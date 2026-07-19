"""
Gmail API client — send and fetch emails using the Gmail REST API.
Requires GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN in .env.
Run scripts/gmail_auth.py once to obtain the refresh token.
"""
import base64
import json
import re
import uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
INBOX_FILE = DATA_DIR / "inbox_emails.json"


# ── credential helpers ────────────────────────────────────────────────────────

def _build_service(client_id: str, client_secret: str, refresh_token: str):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
    )
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


# ── local storage helpers ─────────────────────────────────────────────────────

def _ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)
    if not INBOX_FILE.exists():
        INBOX_FILE.write_text("[]")


def _load_inbox() -> List[dict]:
    _ensure_data_dir()
    try:
        return json.loads(INBOX_FILE.read_text())
    except Exception:
        return []


def _save_inbox(emails: List[dict]):
    _ensure_data_dir()
    INBOX_FILE.write_text(json.dumps(emails, indent=2, default=str))


# ── message parsing ───────────────────────────────────────────────────────────

def _header(headers: list, name: str) -> str:
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _decode_part(data: str) -> str:
    try:
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
    except Exception:
        return ""


def _extract_body(payload: dict) -> str:
    mime = payload.get("mimeType", "")
    if mime == "text/plain":
        return _decode_part(payload.get("body", {}).get("data", ""))
    if mime == "text/html":
        raw = _decode_part(payload.get("body", {}).get("data", ""))
        return re.sub(r"<[^>]+>", " ", raw)

    # multipart — prefer text/plain
    parts = payload.get("parts", [])
    plain = next((p for p in parts if p.get("mimeType") == "text/plain"), None)
    if plain:
        return _decode_part(plain.get("body", {}).get("data", ""))
    html = next((p for p in parts if p.get("mimeType") == "text/html"), None)
    if html:
        raw = _decode_part(html.get("body", {}).get("data", ""))
        return re.sub(r"<[^>]+>", " ", raw)

    # nested multipart
    for part in parts:
        body = _extract_body(part)
        if body:
            return body
    return ""


def _parse_message(msg: dict, user_email: str) -> dict:
    headers = msg.get("payload", {}).get("headers", [])
    body = _extract_body(msg.get("payload", {})).strip()

    from_raw = _header(headers, "From")
    # "Name <email>" or just "email"
    m = re.match(r"^(.*?)\s*<(.+?)>$", from_raw.strip())
    if m:
        from_name, from_email = m.group(1).strip(' "'), m.group(2)
    else:
        from_name = from_email = from_raw.strip()

    date_raw = _header(headers, "Date")
    try:
        from email.utils import parsedate_to_datetime
        date_str = parsedate_to_datetime(date_raw).isoformat()
    except Exception:
        date_str = datetime.utcnow().isoformat()

    labels = msg.get("labelIds", [])

    return {
        "id": msg["id"],
        "thread_id": msg.get("threadId", ""),
        "from_name": from_name or from_email,
        "from_email": from_email,
        "to_email": _header(headers, "To") or user_email,
        "subject": _header(headers, "Subject") or "(no subject)",
        "body": body,
        "preview": body[:120].replace("\n", " "),
        "date": date_str,
        "read": "UNREAD" not in labels,
        "folder": "inbox",
        "attachments": [],
    }


# ── public API ────────────────────────────────────────────────────────────────

def fetch_inbox(
    client_id: str,
    client_secret: str,
    refresh_token: str,
    max_emails: int = 50,
) -> List[dict]:
    service = _build_service(client_id, client_secret, refresh_token)

    profile = service.users().getProfile(userId="me").execute()
    user_email = profile.get("emailAddress", "")

    result = service.users().messages().list(
        userId="me", labelIds=["INBOX"], maxResults=max_emails
    ).execute()

    message_refs = result.get("messages", [])
    emails = []
    for ref in message_refs:
        try:
            msg = service.users().messages().get(
                userId="me", id=ref["id"], format="full"
            ).execute()
            emails.append(_parse_message(msg, user_email))
        except Exception as e:
            logger.debug(f"Failed to fetch message {ref['id']}: {e}")

    return emails


def sync_inbox(
    client_id: str,
    client_secret: str,
    refresh_token: str,
    max_emails: int = 50,
) -> dict:
    fetched = fetch_inbox(client_id, client_secret, refresh_token, max_emails)
    existing = _load_inbox()

    read_status = {e["id"]: e.get("read", False) for e in existing}
    existing_ids = set(read_status.keys())

    new_emails = [e for e in fetched if e["id"] not in existing_ids]
    for e in fetched:
        if e["id"] in read_status:
            e["read"] = read_status[e["id"]]

    merged = fetched + [e for e in existing if e["id"] not in {x["id"] for x in fetched}]
    merged = merged[: max_emails * 2]

    _save_inbox(merged)
    return {"total": len(merged), "new": len(new_emails), "synced_at": datetime.utcnow().isoformat()}


def send_email(
    client_id: str,
    client_secret: str,
    refresh_token: str,
    from_name: str,
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> dict:
    service = _build_service(client_id, client_secret, refresh_token)

    profile = service.users().getProfile(userId="me").execute()
    from_email = profile.get("emailAddress", "")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email
    if reply_to:
        msg["Reply-To"] = reply_to

    msg.attach(MIMEText(body, "plain", "utf-8"))
    if html_body:
        msg.attach(MIMEText(html_body, "html", "utf-8"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    result = service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()

    message_id = result.get("id", str(uuid.uuid4()))
    logger.info(f"Gmail sent to {to_email} | subject: {subject} | id: {message_id}")
    return {"success": True, "message_id": message_id, "sent_at": datetime.utcnow().isoformat()}


def get_stored_inbox() -> List[dict]:
    return _load_inbox()


def mark_read(email_id: str):
    emails = _load_inbox()
    for e in emails:
        if e["id"] == email_id:
            e["read"] = True
            break
    _save_inbox(emails)


def delete_stored_email(email_id: str):
    emails = _load_inbox()
    _save_inbox([e for e in emails if e["id"] != email_id])
