"""
Mail Chat Endpoint - Email inbox and conversation management
"""
import json
import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()

# Simple file-based storage
DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data"
THREADS_FILE = DATA_DIR / "email_threads.json"
MESSAGES_FILE = DATA_DIR / "email_messages.json"


class SendMessageRequest(BaseModel):
    thread_id: Optional[str] = None
    to_email: str
    to_name: Optional[str] = None
    subject: str
    body: str


class ReplyRequest(BaseModel):
    body: str


def _ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)
    if not THREADS_FILE.exists():
        THREADS_FILE.write_text("[]")
    if not MESSAGES_FILE.exists():
        MESSAGES_FILE.write_text("[]")


def _load_threads() -> List[dict]:
    _ensure_data_dir()
    try:
        return json.loads(THREADS_FILE.read_text())
    except:
        return []


def _save_threads(threads: List[dict]):
    _ensure_data_dir()
    THREADS_FILE.write_text(json.dumps(threads, indent=2, default=str))


def _load_messages() -> List[dict]:
    _ensure_data_dir()
    try:
        return json.loads(MESSAGES_FILE.read_text())
    except:
        return []


def _save_messages(messages: List[dict]):
    _ensure_data_dir()
    MESSAGES_FILE.write_text(json.dumps(messages, indent=2, default=str))


@router.get("/threads")
async def list_threads(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """
    List all email threads (conversations).
    """
    threads = _load_threads()
    
    if status:
        threads = [t for t in threads if t.get("status") == status]
    
    # Sort by last_message_at descending
    threads.sort(key=lambda x: x.get("last_message_at", ""), reverse=True)
    
    # Pagination
    total = len(threads)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = threads[start:end]
    
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "threads": paginated
    }


@router.get("/threads/{thread_id}")
async def get_thread(thread_id: str):
    """
    Get a specific thread with all messages.
    """
    threads = _load_threads()
    messages = _load_messages()
    
    thread = None
    for t in threads:
        if t.get("id") == thread_id:
            thread = t
            break
    
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Get messages for this thread
    thread_messages = [m for m in messages if m.get("thread_id") == thread_id]
    thread_messages.sort(key=lambda x: x.get("created_at", ""))
    
    return {
        **thread,
        "messages": thread_messages
    }


@router.post("/send")
async def send_message(request: SendMessageRequest):
    """
    Send a new email message.
    Creates a new thread if thread_id is not provided.
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from app.core.config import settings
    
    threads = _load_threads()
    messages = _load_messages()
    
    # Create or get thread
    thread_id = request.thread_id
    if not thread_id:
        thread_id = str(uuid.uuid4())
        new_thread = {
            "id": thread_id,
            "subject": request.subject,
            "recipient_email": request.to_email,
            "recipient_name": request.to_name,
            "status": "active",
            "message_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "last_message_at": datetime.utcnow().isoformat()
        }
        threads.append(new_thread)
    
    # Create message
    message_id = str(uuid.uuid4())
    new_message = {
        "id": message_id,
        "thread_id": thread_id,
        "direction": "outbound",
        "from_email": settings.SMTP_FROM_EMAIL or settings.SMTP_USER,
        "to_email": request.to_email,
        "subject": request.subject,
        "body": request.body,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Try to send via SMTP
    if settings.SMTP_USER and settings.SMTP_PASSWORD:
        try:
            msg = MIMEMultipart()
            msg["Subject"] = request.subject
            msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USER}>"
            msg["To"] = request.to_email
            
            msg.attach(MIMEText(request.body, "plain"))
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            new_message["status"] = "sent"
            new_message["sent_at"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            new_message["status"] = "failed"
            new_message["error"] = str(e)
    else:
        new_message["status"] = "queued"
    
    messages.append(new_message)
    
    # Update thread
    for i, t in enumerate(threads):
        if t.get("id") == thread_id:
            threads[i]["message_count"] = threads[i].get("message_count", 0) + 1
            threads[i]["last_message_at"] = datetime.utcnow().isoformat()
            break
    
    _save_threads(threads)
    _save_messages(messages)
    
    return {
        "thread_id": thread_id,
        "message_id": message_id,
        "status": new_message["status"],
        "error": new_message.get("error")
    }


@router.post("/threads/{thread_id}/reply")
async def reply_to_thread(thread_id: str, request: ReplyRequest):
    """
    Reply to an existing thread.
    """
    threads = _load_threads()
    
    thread = None
    for t in threads:
        if t.get("id") == thread_id:
            thread = t
            break
    
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return await send_message(SendMessageRequest(
        thread_id=thread_id,
        to_email=thread["recipient_email"],
        to_name=thread.get("recipient_name"),
        subject=f"Re: {thread['subject']}",
        body=request.body
    ))


@router.put("/threads/{thread_id}/status")
async def update_thread_status(thread_id: str, status: str):
    """
    Update thread status (active, archived, starred).
    """
    threads = _load_threads()
    
    for i, t in enumerate(threads):
        if t.get("id") == thread_id:
            threads[i]["status"] = status
            threads[i]["updated_at"] = datetime.utcnow().isoformat()
            _save_threads(threads)
            return threads[i]
    
    raise HTTPException(status_code=404, detail="Thread not found")


@router.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    """
    Delete a thread and its messages.
    """
    threads = _load_threads()
    messages = _load_messages()
    
    original_count = len(threads)
    threads = [t for t in threads if t.get("id") != thread_id]
    
    if len(threads) == original_count:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    messages = [m for m in messages if m.get("thread_id") != thread_id]
    
    _save_threads(threads)
    _save_messages(messages)
    
    return {"message": "Thread deleted"}


@router.get("/stats")
async def get_mail_stats():
    """
    Get email statistics.
    """
    threads = _load_threads()
    messages = _load_messages()
    
    outbound = [m for m in messages if m.get("direction") == "outbound"]
    inbound = [m for m in messages if m.get("direction") == "inbound"]
    sent = [m for m in outbound if m.get("status") == "sent"]
    failed = [m for m in outbound if m.get("status") == "failed"]
    
    return {
        "total_threads": len(threads),
        "active_threads": sum(1 for t in threads if t.get("status") == "active"),
        "total_messages": len(messages),
        "outbound_messages": len(outbound),
        "inbound_messages": len(inbound),
        "sent_messages": len(sent),
        "failed_messages": len(failed)
    }
