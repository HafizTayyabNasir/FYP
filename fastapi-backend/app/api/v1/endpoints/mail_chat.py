"""
Mail endpoints — inbox sync (Gmail API), send, and thread management.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.config import settings

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


# ── inbox: sync + messages ────────────────────────────────────────────────────

@router.post("/sync")
async def sync_inbox():
    """Pull latest emails from Gmail API and store locally."""
    if _gmail_configured():
        try:
            import asyncio
            import concurrent.futures
            from app.services.email.gmail_client import sync_inbox as _sync

            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as ex:
                result = await loop.run_in_executor(
                    ex, lambda: _sync(**_gmail_creds())
                )
            return {"success": True, **result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gmail sync failed: {e}")

    if not _imap_configured():
        raise HTTPException(
            status_code=400,
            detail="Email not configured. Add GMAIL_CLIENT_ID/SECRET/REFRESH_TOKEN (or SMTP_USER/PASSWORD + IMAP_HOST) to .env"
        )

    try:
        from app.services.email.imap_client import sync_inbox as _sync
        import asyncio
        import concurrent.futures

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as ex:
            result = await loop.run_in_executor(
                ex, lambda: _sync(
                    host=settings.IMAP_HOST,
                    port=settings.IMAP_PORT,
                    user=settings.SMTP_USER,
                    password=settings.SMTP_PASSWORD,
                )
            )
        return {"success": True, **result}
    except ConnectionError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {e}")


@router.get("/messages")
async def get_messages(folder: str = Query("inbox")):
    """Return emails for inbox or sent folder."""
    if folder == "sent":
        all_msgs = _load(MESSAGES_FILE)
        sent = [
            {
                "id": m["id"],
                "from_name": settings.SMTP_FROM_NAME,
                "from_email": m.get("from_email") or settings.SMTP_USER or "",
                "to_email": m.get("to_email", ""),
                "subject": m.get("subject", ""),
                "body": m.get("body", ""),
                "preview": (m.get("body") or "")[:120],
                "date": m.get("sent_at") or m.get("created_at", ""),
                "read": True,
                "folder": "sent",
                "attachments": [],
            }
            for m in all_msgs
            if m.get("direction") == "outbound"
        ]
        sent.sort(key=lambda x: x["date"], reverse=True)
        return {"messages": sent, "total": len(sent)}

    if _gmail_configured():
        from app.services.email.gmail_client import get_stored_inbox
        inbox = get_stored_inbox()
    else:
        from app.services.email.imap_client import get_stored_inbox
        inbox = get_stored_inbox()

    inbox.sort(key=lambda x: x.get("date", ""), reverse=True)
    return {"messages": inbox, "total": len(inbox)}


# ── send ──────────────────────────────────────────────────────────────────────

@router.post("/send")
async def send_message(request: SendRequest):
    """Send an email and record it in the sent store."""
    import asyncio
    import concurrent.futures

    loop = asyncio.get_event_loop()

    if _gmail_configured():
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
                    )
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gmail send failed: {e}")
    elif _smtp_configured():
        from app.services.email.smtp_sender import send_email

        with concurrent.futures.ThreadPoolExecutor() as ex:
            result = await loop.run_in_executor(
                ex, lambda: send_email(
                    host=settings.SMTP_HOST,
                    port=settings.SMTP_PORT,
                    user=settings.SMTP_USER,
                    password=settings.SMTP_PASSWORD,
                    from_name=settings.SMTP_FROM_NAME,
                    to_email=request.to_email,
                    subject=request.subject,
                    body=request.body,
                    html_body=request.html_body,
                )
            )
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Send failed"))
    else:
        raise HTTPException(
            status_code=400,
            detail="Email not configured. Add GMAIL_CLIENT_ID/SECRET/REFRESH_TOKEN to .env"
        )

    messages = _load(MESSAGES_FILE)
    message_id = result.get("message_id") or str(uuid.uuid4())
    messages.append({
        "id": message_id,
        "direction": "outbound",
        "from_email": settings.SMTP_FROM_EMAIL or settings.SMTP_USER or "",
        "to_email": request.to_email,
        "to_name": request.to_name,
        "subject": request.subject,
        "body": request.body,
        "reply_to_id": request.reply_to_id,
        "status": "sent",
        "sent_at": result.get("sent_at") or datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat(),
    })
    _save(MESSAGES_FILE, messages)

    return {"success": True, "message_id": message_id, "sent_at": result.get("sent_at")}


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

    if _gmail_configured():
        from app.services.email.gmail_client import get_stored_inbox
    else:
        from app.services.email.imap_client import get_stored_inbox

    inbox = get_stored_inbox()
    outbound = [m for m in messages if m.get("direction") == "outbound"]
    return {
        "inbox_total": len(inbox),
        "inbox_unread": sum(1 for e in inbox if not e.get("read")),
        "sent_total": len(outbound),
        "sent_failed": sum(1 for m in outbound if m.get("status") == "failed"),
        "gmail_configured": _gmail_configured(),
        "smtp_configured": _smtp_configured(),
        "imap_configured": _imap_configured(),
    }
