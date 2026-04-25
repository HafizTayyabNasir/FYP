"""
IMAP client — fetches emails from the configured mail server.
Stores fetched emails in data/inbox_emails.json for fast retrieval.
"""
import email
import imaplib
import json
import uuid
import re
from datetime import datetime
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
INBOX_FILE = DATA_DIR / "inbox_emails.json"


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


def _decode_str(value: str) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(str(part))
    return " ".join(decoded)


def _get_body(msg) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            cd = str(part.get("Content-Disposition", ""))
            if ct == "text/plain" and "attachment" not in cd:
                charset = part.get_content_charset() or "utf-8"
                body = part.get_payload(decode=True).decode(charset, errors="replace")
                break
            elif ct == "text/html" and "attachment" not in cd and not body:
                charset = part.get_content_charset() or "utf-8"
                raw_html = part.get_payload(decode=True).decode(charset, errors="replace")
                body = re.sub(r"<[^>]+>", " ", raw_html)
                body = re.sub(r"\s+", " ", body).strip()
    else:
        charset = msg.get_content_charset() or "utf-8"
        payload = msg.get_payload(decode=True)
        if payload:
            body = payload.decode(charset, errors="replace")
    return body.strip()


def _parse_date(msg) -> str:
    try:
        return parsedate_to_datetime(msg["Date"]).isoformat()
    except Exception:
        return datetime.utcnow().isoformat()


def fetch_inbox(host: str, port: int, user: str, password: str, max_emails: int = 50) -> List[dict]:
    """Connect via IMAP SSL, fetch the latest emails."""
    try:
        mail = imaplib.IMAP4_SSL(host, port)
        mail.login(user, password)
        mail.select("INBOX", readonly=True)

        _, data = mail.search(None, "ALL")
        uid_list = data[0].split()
        uid_list = uid_list[-max_emails:]

        emails = []
        for uid in reversed(uid_list):
            try:
                _, msg_data = mail.fetch(uid, "(RFC822)")
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)

                from_name, from_email = parseaddr(msg.get("From", ""))
                from_name = _decode_str(from_name) or from_email
                _, to_email = parseaddr(msg.get("To", ""))

                subject = _decode_str(msg.get("Subject", "(no subject)"))
                body = _get_body(msg)
                date_str = _parse_date(msg)

                emails.append({
                    "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{from_email}:{subject}:{date_str}")),
                    "from_name": from_name,
                    "from_email": from_email,
                    "to_email": to_email or user,
                    "subject": subject,
                    "body": body,
                    "preview": body[:120].replace("\n", " "),
                    "date": date_str,
                    "read": False,
                    "folder": "inbox",
                    "attachments": [],
                })
            except Exception as e:
                logger.debug(f"Failed to parse email uid {uid}: {e}")

        mail.logout()
        return emails

    except imaplib.IMAP4.error as e:
        raise ConnectionError(f"IMAP login failed: {e}")
    except Exception as e:
        raise RuntimeError(f"IMAP error: {e}")


def sync_inbox(host: str, port: int, user: str, password: str, max_emails: int = 50) -> dict:
    """Fetch from IMAP and merge into local store, preserving read status."""
    fetched = fetch_inbox(host, port, user, password, max_emails)
    existing = _load_inbox()

    # Build lookup of existing read status
    read_status = {e["id"]: e.get("read", False) for e in existing}
    existing_ids = set(read_status.keys())

    new_emails = [e for e in fetched if e["id"] not in existing_ids]
    # Apply preserved read status to re-fetched emails
    for e in fetched:
        if e["id"] in read_status:
            e["read"] = read_status[e["id"]]

    merged = fetched + [e for e in existing if e["id"] not in {x["id"] for x in fetched}]
    merged = merged[: max_emails * 2]

    _save_inbox(merged)
    return {"total": len(merged), "new": len(new_emails), "synced_at": datetime.utcnow().isoformat()}


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
