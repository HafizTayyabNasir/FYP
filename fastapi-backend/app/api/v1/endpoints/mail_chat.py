"""
Mail endpoints — inbox sync (Gmail API), send, and thread management.
Now supports Resend as the primary email provider.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.db.session import get_db
from app.models.user import User
from app.models.email_account import EmailAccount
from app.core.config import settings
from app.core.encryption import decrypt

router = APIRouter()

DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data"
THREADS_FILE = DATA_DIR / "email_threads.json"
MESSAGES_FILE = DATA_DIR / "email_messages.json"


# ── helpers ──────────────────────────────────────────────────────────────────

def _ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)
    for f in (THREADS_FILE, MESSAGES_FILE):
        if not f.exists():
            f.write_text("[]")


def _load(path: Path) -> list:
    _ensure_data_dir()
    try:
        return json.loads(path.read_text())
    except Exception:
        return []


def _save(path: Path, data: list):
    _ensure_data_dir()
    path.write_text(json.dumps(data, indent=2, default=str))


def _resend_configured() -> bool:
    return bool(settings.RESEND_API_KEY)


def _gmail_configured() -> bool:
    return bool(
        settings.GMAIL_CLIENT_ID
        and settings.GMAIL_CLIENT_SECRET
        and settings.GMAIL_REFRESH_TOKEN
    )


def _smtp_configured() -> bool:
    return bool(settings.SMTP_USER and settings.SMTP_PASSWORD)


def _imap_configured() -> bool:
    return bool(settings.SMTP_USER and settings.SMTP_PASSWORD)


def _any_email_configured() -> bool:
    return _resend_configured() or _gmail_configured() or _smtp_configured()


def _gmail_creds() -> dict:
    return {
        "client_id": settings.GMAIL_CLIENT_ID,
        "client_secret": settings.GMAIL_CLIENT_SECRET,
        "refresh_token": settings.GMAIL_REFRESH_TOKEN,
    }


# ── request models ────────────────────────────────────────────────────────────

class SendRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    reply_to_id: Optional[str] = None
    to_name: Optional[str] = None
    html_body: Optional[str] = None


class SyncRequest(BaseModel):
    imap_host: Optional[str] = None
    imap_port: Optional[int] = 993
    imap_user: Optional[str] = None
    imap_password: Optional[str] = None


class MarkReadRequest(BaseModel):
    contact_email: Optional[str] = None
    email_id: Optional[str] = None


# ── inbox: sync + messages ────────────────────────────────────────────────────

@router.post("/sync")
async def sync_inbox(
    req: Optional[SyncRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Pull latest emails from connected EmailAccounts (Gmail API or IMAP) and store locally."""
    # Fetch all active email accounts for the user
    result = await db.execute(
        select(EmailAccount).where(EmailAccount.user_id == current_user.id, EmailAccount.is_active == True)
    )
    accounts = result.scalars().all()
    
    import asyncio
    import concurrent.futures
    loop = asyncio.get_event_loop()
    results = []

    # Get emails from before sync to compare and find new ones
    INBOX_FILE = DATA_DIR / "inbox_emails.json"
    before_sync = _load(INBOX_FILE)
    before_ids = {e["id"] for e in before_sync}

    for account in accounts:
        if account.provider == "google":
            from app.services.email.gmail_client import sync_inbox as _sync_gmail
            client_id = settings.GOOGLE_CLIENT_ID or settings.GMAIL_CLIENT_ID
            client_secret = settings.GOOGLE_CLIENT_SECRET or settings.GMAIL_CLIENT_SECRET
            refresh_token = decrypt(account.refresh_token)
            
            with concurrent.futures.ThreadPoolExecutor() as ex:
                try:
                    res = await loop.run_in_executor(
                        ex, lambda: _sync_gmail(client_id, client_secret, refresh_token)
                    )
                    results.append(res)
                except Exception as e:
                    pass

        elif account.provider == "smtp":
            from app.services.email.imap_client import sync_inbox as _sync_imap
            imap_host = account.imap_host
            imap_port = account.imap_port or 993
            imap_user = account.email_address
            imap_password = decrypt(account.smtp_password)
            
            if imap_host and imap_user and imap_password:
                with concurrent.futures.ThreadPoolExecutor() as ex:
                    try:
                        res = await loop.run_in_executor(
                            ex, lambda: _sync_imap(
                                host=imap_host,
                                port=imap_port,
                                user=imap_user,
                                password=imap_password,
                            )
                        )
                        results.append(res)
                    except Exception as e:
                        pass

    # Fallback to .env / req for backwards compatibility if no db accounts synced
    if not results:
        imap_host = req.imap_host if req and req.imap_host else settings.IMAP_HOST
        imap_port = req.imap_port if req and req.imap_port else settings.IMAP_PORT
        imap_user = req.imap_user if req and req.imap_user else getattr(settings, "SMTP_USER", None)
        imap_password = req.imap_password if req and req.imap_password else getattr(settings, "SMTP_PASSWORD", None)

        if imap_user and imap_password and imap_host:
            try:
                from app.services.email.imap_client import sync_inbox as _sync_imap
                with concurrent.futures.ThreadPoolExecutor() as ex:
                    res = await loop.run_in_executor(
                        ex, lambda: _sync_imap(
                            host=imap_host,
                            port=imap_port,
                            user=imap_user,
                            password=imap_password,
                        )
                    )
                results.append(res)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"IMAP Sync failed: {e}")

    # ── Always also sync the system sender mailbox (team@elvionsolutions.com) ──
    # Replies to outreach emails go to this mailbox, so we must always fetch them
    sys_imap_user = getattr(settings, "IMAP_USER", None)
    sys_imap_pass = getattr(settings, "IMAP_PASSWORD", None)
    sys_imap_host = getattr(settings, "IMAP_HOST", "imap.hostinger.com")
    sys_imap_port = getattr(settings, "IMAP_PORT", 993)

    # Only sync if configured AND not already synced via one of the account loops above
    already_synced_emails = {acc.email_address.lower() for acc in accounts if acc.email_address}
    print(f"[SYNC] System mailbox: user={sys_imap_user}, host={sys_imap_host}, has_pass={bool(sys_imap_pass)}, already_synced={already_synced_emails}")

    if sys_imap_user and sys_imap_pass and sys_imap_user.lower() not in already_synced_emails:
        try:
            from app.services.email.imap_client import sync_inbox as _sync_imap
            print(f"[SYNC] Syncing system mailbox {sys_imap_user} via {sys_imap_host}:{sys_imap_port}...")
            with concurrent.futures.ThreadPoolExecutor() as ex:
                res = await loop.run_in_executor(
                    ex, lambda: _sync_imap(
                        host=sys_imap_host,
                        port=sys_imap_port,
                        user=sys_imap_user,
                        password=sys_imap_pass,
                    )
                )
            print(f"[SYNC] System mailbox sync result: {res}")
            results.append(res)
        except Exception as e:
            print(f"[SYNC] System mailbox IMAP sync FAILED: {e}")
    elif not sys_imap_user or not sys_imap_pass:
        print(f"[SYNC] System mailbox NOT configured — IMAP_USER or IMAP_PASSWORD missing in env")

    if not results and _resend_configured():
        return {"success": True, "synced": 0, "note": "Resend is send-only. Sent emails are shown in the Sent folder."}
    if not results:
        raise HTTPException(
            status_code=400,
            detail="Please connect an Email Account in Settings first."
        )

    # Cross-reference newly fetched emails with threads
    after_sync = _load(INBOX_FILE)
    new_emails = [e for e in after_sync if e["id"] not in before_ids]

    if new_emails:
        threads = _load(THREADS_FILE)
        messages = _load(MESSAGES_FILE)
        now = datetime.utcnow().isoformat()
        threads_updated = False
        messages_updated = False

        for email in new_emails:
            from_email = (email.get("from_email") or "").strip()
            if not from_email:
                continue

            from_email_lower = from_email.lower()
            # Find if this email belongs to an existing thread (case-insensitive)
            thread = next((t for t in threads if (t.get("contact_email") or "").lower().strip() == from_email_lower), None)
            
            if not thread:
                thread_id = str(uuid.uuid4())
                thread = {
                    "id": thread_id,
                    "contact_email": from_email,
                    "contact_name": email.get("from_name") or from_email.split("@")[0],
                    "subject": email.get("subject", ""),
                    "status": "active",
                    "message_count": 0,
                    "last_message_at": email.get("date", now),
                    "created_at": now,
                    "updated_at": now,
                }
                threads.append(thread)

            thread_id = thread["id"]
            if not any(m.get("id") == email["id"] for m in messages):
                # Add to messages
                messages.append({
                    "id": email["id"],
                    "thread_id": thread_id,
                    "direction": "inbound",
                    "from_email": from_email,
                    "from_name": email.get("from_name", ""),
                    "to_email": email.get("to_email", ""),
                    "to_name": "You",
                    "subject": email.get("subject", ""),
                    "body": email.get("body", ""),
                    "reply_to_id": None,
                    "status": "received",
                    "created_at": email.get("date", now),
                    "read": False,
                })
                # Update thread
                thread["last_message_at"] = email.get("date", now)
                thread["message_count"] = thread.get("message_count", 0) + 1
                thread["updated_at"] = now
                threads_updated = True
                messages_updated = True

        if threads_updated:
            _save(THREADS_FILE, threads)
        if messages_updated:
            _save(MESSAGES_FILE, messages)

    return {"success": True, "details": results, "note": f"Synced successfully. {len(new_emails)} new emails found."}


@router.get("/messages")
async def get_messages(
    folder: str = Query("inbox"),
    imap_user: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Return emails for inbox or sent folder."""
    # Find Google Email Accounts for the user to determine if we should fetch from Gmail
    result = await db.execute(select(EmailAccount).where(EmailAccount.user_id == current_user.id))
    accounts = result.scalars().all()
    has_google = any(acc.provider == "google" and acc.is_active for acc in accounts)
    
    # Use the first account's email as fallback from_email if none in message
    fallback_email = accounts[0].email_address if accounts else "user@example.com"
    fallback_name = accounts[0].display_name or fallback_email if accounts else "You"

    if folder == "sent":
        all_msgs = _load(MESSAGES_FILE)
        sent = [
            {
                "id": m["id"],
                "from_name": m.get("from_name") or fallback_name,
                "from_email": m.get("from_email") or fallback_email,
                "to_email": m.get("to_email", ""),
                "to_name": m.get("to_name", ""),
                "subject": m.get("subject", ""),
                "body": m.get("body", ""),
                "preview": (m.get("body") or "")[:120],
                "date": m.get("sent_at") or m.get("created_at", ""),
                "read": True,
                "folder": "sent",
                "thread_id": m.get("thread_id"),
                "attachments": [],
            }
            for m in all_msgs
            if m.get("direction") == "outbound"
        ]
        sent.sort(key=lambda x: x["date"], reverse=True)
        return {"messages": sent, "total": len(sent)}

    # Inbox: load unconditionally from inbox_emails.json
    INBOX_FILE = DATA_DIR / "inbox_emails.json"
    inbox_raw = _load(INBOX_FILE)

    # Track seen IDs to prevent duplicates across both data sources
    seen_ids = set()
    inbox = []

    for m in inbox_raw:
        mid = m.get("id")
        if mid and mid not in seen_ids:
            seen_ids.add(mid)
            inbox.append(m)

    # Also include any inbound messages stored in our data file (avoid duplicates)
    all_msgs = _load(MESSAGES_FILE)
    for m in all_msgs:
        if m.get("direction") == "inbound":
            mid = m.get("id")
            if mid and mid in seen_ids:
                continue
            seen_ids.add(mid)
            inbox.append({
                "id": mid,
                "from_name": m.get("from_name", ""),
                "from_email": m.get("from_email", ""),
                "to_email": m.get("to_email", ""),
                "subject": m.get("subject", ""),
                "body": m.get("body", ""),
                "preview": (m.get("body") or "")[:120],
                "date": m.get("created_at", ""),
                "read": m.get("read", False),
                "folder": "inbox",
                "thread_id": m.get("thread_id"),
                "attachments": [],
            })

    inbox.sort(key=lambda x: x.get("date", ""), reverse=True)
    return {"messages": inbox, "total": len(inbox)}


# ── send ──────────────────────────────────────────────────────────────────────

@router.post("/send")
async def send_message(
    request: SendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Send an email via Resend (preferred), Gmail API, or SMTP and record it."""
    import asyncio
    import concurrent.futures

    loop = asyncio.get_event_loop()
    result = None

    # ── Pick provider: Resend > Gmail > SMTP ────────────────────────────
    # Find active EmailAccount to use for Reply-To
    reply_to_email = request.reply_to_id
    if not reply_to_email and db and current_user:
        result_accounts = await db.execute(select(EmailAccount).where(EmailAccount.user_id == current_user.id, EmailAccount.is_active == True))
        accounts = result_accounts.scalars().all()
        if accounts:
            reply_to_email = accounts[0].email_address

    if not reply_to_email:
        reply_to_email = getattr(settings, "SMTP_USER", None) or getattr(settings, "IMAP_USER", None)

    if _resend_configured():
        from app.services.email.resend_sender import send_email as resend_send

        with concurrent.futures.ThreadPoolExecutor() as ex:
            result = await loop.run_in_executor(
                ex, lambda: resend_send(
                    to_email=request.to_email,
                    subject=request.subject,
                    body=request.body,
                    html_body=request.html_body,
                    to_name=request.to_name,
                    reply_to=reply_to_email,
                )
            )
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Resend send failed"))

    elif _gmail_configured():
        try:
            from app.services.email.gmail_client import send_email

            with concurrent.futures.ThreadPoolExecutor() as ex:
                result = await loop.run_in_executor(
                    ex, lambda: send_email(
                        **_gmail_creds(),
                        from_name=settings.SMTP_FROM_NAME,
                        to_email=request.to_email,
                        subject=request.subject,
                        body=request.body,
                        html_body=request.html_body,
                        reply_to=reply_to_email,
                    )
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gmail send failed: {e}")

    elif _smtp_configured():
        from app.services.email.smtp_sender import send_email as smtp_send

        with concurrent.futures.ThreadPoolExecutor() as ex:
            result = await loop.run_in_executor(
                ex, lambda: smtp_send(
                    host=settings.SMTP_HOST,
                    port=settings.SMTP_PORT,
                    user=settings.SMTP_USER,
                    password=settings.SMTP_PASSWORD,
                    from_name=settings.SMTP_FROM_NAME,
                    to_email=request.to_email,
                    subject=request.subject,
                    body=request.body,
                    html_body=request.html_body,
                    reply_to=reply_to_email,
                )
            )
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Send failed"))
    else:
        raise HTTPException(
            status_code=400,
            detail="Email not configured. Add RESEND_API_KEY (or Gmail/SMTP creds) to .env"
        )

    # ── Record message + thread ─────────────────────────────────────────
    message_id = result.get("message_id") or str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    from_email = settings.RESEND_FROM_EMAIL or settings.SMTP_FROM_EMAIL or settings.SMTP_USER or ""
    from_name = settings.RESEND_FROM_NAME or settings.SMTP_FROM_NAME or "You"

    # Find or create thread
    threads = _load(THREADS_FILE)
    thread = next(
        (t for t in threads if t.get("contact_email") == request.to_email),
        None
    )
    if not thread:
        thread_id = str(uuid.uuid4())
        thread = {
            "id": thread_id,
            "contact_email": request.to_email,
            "contact_name": request.to_name or request.to_email.split("@")[0],
            "subject": request.subject,
            "status": "active",
            "message_count": 1,
            "last_message_at": now,
            "created_at": now,
            "updated_at": now,
        }
        threads.append(thread)
    else:
        thread_id = thread["id"]
        thread["last_message_at"] = now
        thread["message_count"] = thread.get("message_count", 0) + 1
        thread["updated_at"] = now

    _save(THREADS_FILE, threads)

    # Save message
    messages = _load(MESSAGES_FILE)
    messages.append({
        "id": message_id,
        "thread_id": thread_id,
        "direction": "outbound",
        "from_email": from_email,
        "from_name": from_name,
        "to_email": request.to_email,
        "to_name": request.to_name or "",
        "subject": request.subject,
        "body": request.body,
        "reply_to_id": request.reply_to_id,
        "status": "sent",
        "sent_at": result.get("sent_at") or now,
        "created_at": now,
    })
    _save(MESSAGES_FILE, messages)

    return {
        "success": True,
        "message_id": message_id,
        "thread_id": thread_id,
        "sent_at": result.get("sent_at") or now,
    }


# ── thread management ────────────────────────────────────────────────────────

@router.get("/threads")
async def list_threads(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    threads = _load(THREADS_FILE)
    if status:
        threads = [t for t in threads if t.get("status") == status]
    threads.sort(key=lambda x: x.get("last_message_at", ""), reverse=True)
    total = len(threads)
    start = (page - 1) * per_page
    return {"total": total, "page": page, "per_page": per_page, "threads": threads[start: start + per_page]}


@router.get("/threads/{thread_id}")
async def get_thread(thread_id: str):
    threads = _load(THREADS_FILE)
    thread = next((t for t in threads if t.get("id") == thread_id), None)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    messages = [m for m in _load(MESSAGES_FILE) if m.get("thread_id") == thread_id]
    messages.sort(key=lambda x: x.get("created_at", ""))
    return {**thread, "messages": messages}


@router.post("/read")
async def mark_read_endpoint(req: MarkReadRequest):
    """Mark an email or all emails from a contact_email as read."""
    # 1. Mark in inbox_emails.json
    INBOX_FILE = DATA_DIR / "inbox_emails.json"
    inbox = _load(INBOX_FILE)
    updated_inbox = False
    for msg in inbox:
        if req.email_id and msg.get("id") == req.email_id:
            msg["read"] = True
            updated_inbox = True
        elif req.contact_email:
            msg_from = msg.get("from_email") or ""
            msg_to = msg.get("to_email") or ""
            if msg_from.lower() == req.contact_email.lower() or msg_to.lower() == req.contact_email.lower():
                msg["read"] = True
                updated_inbox = True
    if updated_inbox:
        _save(INBOX_FILE, inbox)

    # 2. Mark in email_messages.json
    messages = _load(MESSAGES_FILE)
    updated_messages = False
    for msg in messages:
        if req.email_id and msg.get("id") == req.email_id:
            msg["read"] = True
            updated_messages = True
        elif req.contact_email:
            msg_from = msg.get("from_email") or ""
            msg_to = msg.get("to_email") or ""
            if msg_from.lower() == req.contact_email.lower() or msg_to.lower() == req.contact_email.lower():
                msg["read"] = True
                updated_messages = True
    if updated_messages:
        _save(MESSAGES_FILE, messages)

    return {"success": True}


@router.put("/threads/{thread_id}/status")
async def update_thread_status(thread_id: str, status: str):
    threads = _load(THREADS_FILE)
    for i, t in enumerate(threads):
        if t.get("id") == thread_id:
            threads[i]["status"] = status
            threads[i]["updated_at"] = datetime.utcnow().isoformat()
            _save(THREADS_FILE, threads)
            return threads[i]
    raise HTTPException(status_code=404, detail="Thread not found")


@router.delete("/conversation")
async def delete_conversation(contact_email: str = Query(...)):
    """Delete an entire conversation (all messages from/to a contact email) from all data stores."""
    contact = contact_email.lower().strip()
    if not contact:
        raise HTTPException(status_code=400, detail="contact_email is required")

    # 1. Remove from inbox_emails.json
    INBOX_FILE = DATA_DIR / "inbox_emails.json"
    inbox = _load(INBOX_FILE)
    inbox_filtered = [
        m for m in inbox
        if (m.get("from_email") or "").lower().strip() != contact
        and (m.get("to_email") or "").lower().strip() != contact
    ]
    _save(INBOX_FILE, inbox_filtered)

    # 2. Remove matching thread(s) from email_threads.json
    threads = _load(THREADS_FILE)
    matching_thread_ids = {
        t["id"] for t in threads
        if (t.get("contact_email") or "").lower().strip() == contact
    }
    threads_filtered = [t for t in threads if t["id"] not in matching_thread_ids]
    _save(THREADS_FILE, threads_filtered)

    # 3. Remove matching messages from email_messages.json
    messages = _load(MESSAGES_FILE)
    messages_filtered = [
        m for m in messages
        if m.get("thread_id") not in matching_thread_ids
        and (m.get("from_email") or "").lower().strip() != contact
        and (m.get("to_email") or "").lower().strip() != contact
    ]
    _save(MESSAGES_FILE, messages_filtered)

    removed_inbox = len(inbox) - len(inbox_filtered)
    removed_threads = len(threads) - len(threads_filtered)
    removed_messages = len(messages) - len(messages_filtered)

    return {
        "success": True,
        "removed_inbox": removed_inbox,
        "removed_threads": removed_threads,
        "removed_messages": removed_messages,
    }


@router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    threads = _load(THREADS_FILE)
    filtered = [t for t in threads if t.get("id") != thread_id]
    if len(filtered) == len(threads):
        raise HTTPException(status_code=404, detail="Thread not found")
    messages = [m for m in _load(MESSAGES_FILE) if m.get("thread_id") != thread_id]
    _save(THREADS_FILE, filtered)
    _save(MESSAGES_FILE, messages)
    return {"message": "Thread deleted"}


@router.get("/stats")
async def get_mail_stats():
    messages = _load(MESSAGES_FILE)

    inbox = []
    if _gmail_configured():
        try:
            from app.services.email.gmail_client import get_stored_inbox
            inbox = get_stored_inbox()
        except Exception:
            inbox = []
    elif _imap_configured():
        try:
            from app.services.email.imap_client import get_stored_inbox
            inbox = get_stored_inbox()
        except Exception:
            inbox = []

    outbound = [m for m in messages if m.get("direction") == "outbound"]
    threads = _load(THREADS_FILE)

    return {
        "inbox_total": len(inbox),
        "inbox_unread": sum(1 for e in inbox if not e.get("read")),
        "sent_total": len(outbound),
        "sent_failed": sum(1 for m in outbound if m.get("status") == "failed"),
        "threads_total": len(threads),
        "resend_configured": _resend_configured(),
        "gmail_configured": _gmail_configured(),
        "smtp_configured": _smtp_configured(),
        "imap_configured": _imap_configured(),
    }
