"""
Outreach Endpoints - Email generation, sending via Resend, and full pipeline.

The frontend calls:
    GET  /smtp-status          → check if email sending is configured
    POST /generate             → AI-generate an outreach email
    POST /send                 → send email via Resend + create inbox thread
    POST /generate-email       → (legacy) generate email with audit scores
    POST /extract-business-data→ extract business info from website
    POST /send-email           → (legacy) send via SMTP
    POST /full-pipeline        → audit → extract → generate in one shot
"""
import asyncio
import json
import uuid
from typing import List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.config import settings
from app.api import deps
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.email_account import EmailAccount
from app.models.user import User
from app.schemas.outreach import (
    EmailGenerationRequest,
    GeneratedEmail,
    EmailSendRequest,
    EmailSendResponse,
    ExtractBusinessDataRequest,
    BusinessExtractedData
)
from app.services.agents.email_writing_service import EmailWritingAgent
from app.services.agents.business_Data_Extractor_Agent import BusinessDataExtractorAgent
from app.core.config import settings

router = APIRouter()

# Thread pool for running sync operations
executor = ThreadPoolExecutor(max_workers=4)

# Data files (shared with mail_chat)
DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data"
THREADS_FILE = DATA_DIR / "email_threads.json"
MESSAGES_FILE = DATA_DIR / "email_messages.json"


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


def _smtp_configured() -> bool:
    return bool(settings.SMTP_USER and settings.SMTP_PASSWORD)


def _gmail_configured() -> bool:
    return bool(
        settings.GMAIL_CLIENT_ID
        and settings.GMAIL_CLIENT_SECRET
        and settings.GMAIL_REFRESH_TOKEN
    )


def _any_email_configured() -> bool:
    return _resend_configured() or _gmail_configured() or _smtp_configured()


# ── Quick request models ─────────────────────────────────────────────────────

class QuickGenerateRequest(BaseModel):
    business_name: str
    business_email: Optional[str] = None
    business_website: Optional[str] = None
    business_industry: Optional[str] = None
    audit_data: Optional[dict] = None
    sender_name: Optional[str] = "Your Name"
    sender_company: Optional[str] = "Your Company"
    services_offered: Optional[str] = "Web development, SEO optimization, digital marketing"
    tone: Optional[str] = "professional"


class QuickSendRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    to_name: Optional[str] = None
    business_name: Optional[str] = None
    html_body: Optional[str] = None
    account_id: Optional[str] = None  # UUID of connected email account to send from


class GenerateReplyRequest(BaseModel):
    chat_history: list
    prompt_instruction: str


class PipelineRequest(BaseModel):
    website_url: str
    sender_name: Optional[str] = None
    sender_company: Optional[str] = None
    services_offered: Optional[str] = None


# ── smtp-status (used by outreach page to enable/disable Send button) ────────

@router.get("/smtp-status")
async def smtp_status():
    """Return whether email sending is configured (Resend, Gmail, or SMTP)."""
    return {
        "configured": _any_email_configured(),
        "provider": (
            "resend" if _resend_configured()
            else "gmail" if _gmail_configured()
            else "smtp" if _smtp_configured()
            else "none"
        ),
    }


# ── generate (AI email generation from outreach page) ────────────────────────

@router.post("/generate")
async def generate_outreach_email(request: QuickGenerateRequest):
    """Generate a personalized outreach email using AI."""
    try:
        agent = EmailWritingAgent()

        # Extract audit scores if provided
        audit = request.audit_data or {}
        seo = audit.get("seo_metadata", audit.get("seo", {}))
        ssl = audit.get("ssl_certificate", audit.get("ssl", {}))
        speed = audit.get("load_speed", {})
        mobile = audit.get("responsiveness", {})
        social = audit.get("social_links", {})
        images = audit.get("image_alt_tags", audit.get("image_alt", {}))

        seo_score = seo.get("score", 3.0) if isinstance(seo, dict) else 3.0
        ssl_score = ssl.get("score", 3.0) if isinstance(ssl, dict) else 3.0
        speed_score = speed.get("score", 3.0) if isinstance(speed, dict) else 3.0
        mobile_score = mobile.get("score", 3.0) if isinstance(mobile, dict) else 3.0
        social_score = social.get("score", 3.0) if isinstance(social, dict) else 3.0
        images_score = images.get("score", 3.0) if isinstance(images, dict) else 3.0

        # Collect specific issues from audit
        specific_issues = []
        for section in [seo, ssl, speed, mobile, social, images]:
            if isinstance(section, dict):
                specific_issues.extend(section.get("flaws", [])[:2])

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            lambda: agent.generate_email(
                business_name=request.business_name,
                website_url=request.business_website or "",
                seo_score=seo_score,
                ssl_score=ssl_score,
                load_speed_score=speed_score,
                responsiveness_score=mobile_score,
                social_links_score=social_score,
                image_alt_score=images_score,
                industry=request.business_industry,
                specific_issues=specific_issues[:6] if specific_issues else None,
                additional_notes=f"Tone: {request.tone}. Sender: {request.sender_name} from {request.sender_company}. Services: {request.services_offered}"
            )
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-reply")
async def generate_reply_email(request: GenerateReplyRequest):
    """Generate an email reply using AI context."""
    try:
        agent = EmailWritingAgent()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            lambda: agent.generate_reply(
                chat_history=request.chat_history,
                prompt_instruction=request.prompt_instruction
            )
        )
        return {"reply_body": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── send (send email + create inbox thread) ──────────────────────────────────

@router.post("/send")
async def send_outreach_email(
    request: QuickSendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Send outreach email directly via system email sender (team@elvionsolutions.com)."""
    loop = asyncio.get_event_loop()

    from app.services.email.resend_sender import send_email as resend_send

    reply_to_email = None
    if db and current_user:
        result_accounts = await db.execute(
            select(EmailAccount).where(EmailAccount.user_id == current_user.id, EmailAccount.is_active == True)
        )
        accounts = result_accounts.scalars().all()
        if accounts:
            reply_to_email = accounts[0].email_address

    if not reply_to_email:
        reply_to_email = getattr(settings, "SMTP_USER", None) or getattr(settings, "IMAP_USER", None)

    result = await loop.run_in_executor(
        executor,
        lambda: resend_send(
            to_email=request.to_email,
            subject=request.subject,
            body=request.body,
            html_body=request.html_body,
            from_name=settings.RESEND_FROM_NAME or "Elvion Solutions",
            from_email=settings.RESEND_FROM_EMAIL or "team@elvionsolutions.com",
            to_name=request.to_name,
            reply_to=reply_to_email,
        )
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Send failed"))

    from_email = settings.RESEND_FROM_EMAIL or "team@elvionsolutions.com"
    from_name = settings.RESEND_FROM_NAME or "Elvion Solutions"

    # ── Create / update inbox thread ─────────────────────────────────────
    message_id = result.get("message_id") or str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    # Determine sender info
    # (from_email and from_name were set above from the account)

    # Find or create thread for this email address
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
            "contact_name": request.to_name or request.business_name or request.to_email.split("@")[0],
            "subject": request.subject,
            "status": "active",
            "message_count": 0,
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

    # Save the outbound message
    messages = _load(MESSAGES_FILE)
    messages.append({
        "id": message_id,
        "thread_id": thread_id,
        "direction": "outbound",
        "from_email": from_email,
        "from_name": from_name,
        "to_email": request.to_email,
        "to_name": request.to_name or request.business_name or "",
        "subject": request.subject,
        "body": request.body,
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


# ── Legacy endpoints (kept for backward compatibility) ───────────────────────

@router.post("/generate-email", response_model=dict)
async def generate_email(request: EmailGenerationRequest):
    """
    Generate a personalized outreach email using AI.

    Requires audit scores and business information to generate
    a targeted, professional email.
    """
    try:
        agent = EmailWritingAgent()

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            lambda: agent.generate_email(
                business_name=request.business_name,
                website_url=request.website_url,
                seo_score=request.seo_score,
                ssl_score=request.ssl_score,
                load_speed_score=request.load_speed_score,
                responsiveness_score=request.responsiveness_score,
                social_links_score=request.social_links_score,
                image_alt_score=request.image_alt_score,
                industry=request.industry,
                location=request.location,
                target_audience=request.target_audience,
                business_goal=request.business_goal,
                specific_issues=request.specific_issues,
                additional_notes=request.additional_notes
            )
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-business-data", response_model=dict)
async def extract_business_data(request: ExtractBusinessDataRequest):
    """
    Extract business information from a website using AI.
    """
    try:
        agent = BusinessDataExtractorAgent()

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            lambda: agent.extract_business_data(
                website_url=request.website_url,
                business_name=request.business_name
            )
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/full-pipeline")
async def run_full_pipeline(request: PipelineRequest):
    """
    Run the complete pipeline:
    1. Audit the website
    2. Extract business data
    3. Generate personalized email
    """
    try:
        from app.services.website_audit.orchestrator import WebsiteAuditOrchestrator

        loop = asyncio.get_event_loop()

        # Step 1: Run website audit
        audit_orchestrator = WebsiteAuditOrchestrator()
        audit_result = await loop.run_in_executor(
            executor,
            lambda: audit_orchestrator.run_audit(request.website_url)
        )

        # Step 2: Extract business data
        extractor = BusinessDataExtractorAgent()
        business_data = await loop.run_in_executor(
            executor,
            lambda: extractor.extract_business_data(request.website_url)
        )

        # Step 3: Generate email
        email_agent = EmailWritingAgent()

        # Prepare scores
        scores = {
            "seo": audit_result.seo.score if audit_result.seo else 0,
            "ssl": audit_result.ssl.score if audit_result.ssl else 0,
            "load_speed": audit_result.load_speed.score if audit_result.load_speed else 0,
            "responsiveness": audit_result.responsiveness.score if audit_result.responsiveness else 0,
            "social_links": audit_result.social_links.score if audit_result.social_links else 0,
            "image_alt": audit_result.image_alt.score if audit_result.image_alt else 0
        }

        # Collect specific issues
        specific_issues = []
        if audit_result.seo:
            specific_issues.extend(audit_result.seo.flaws[:2])
        if audit_result.ssl:
            specific_issues.extend(audit_result.ssl.flaws[:2])
        if audit_result.load_speed:
            specific_issues.extend(audit_result.load_speed.flaws[:2])

        additional_notes = None
        if request.sender_name or request.sender_company:
            additional_notes = f"Sender: {request.sender_name or 'N/A'} from {request.sender_company or 'N/A'}. Services: {request.services_offered or 'Web development, SEO'}"

        email_result = await loop.run_in_executor(
            executor,
            lambda: email_agent.generate_email(
                business_name=business_data.get("business_name", "Unknown"),
                website_url=request.website_url,
                seo_score=scores["seo"],
                ssl_score=scores["ssl"],
                load_speed_score=scores["load_speed"],
                responsiveness_score=scores["responsiveness"],
                social_links_score=scores["social_links"],
                image_alt_score=scores["image_alt"],
                industry=business_data.get("industry"),
                location=business_data.get("location"),
                target_audience=business_data.get("target_audience"),
                specific_issues=specific_issues[:6] if specific_issues else None,
                additional_notes=additional_notes,
            )
        )

        return {
            "pipeline_status": "completed",
            "website_url": request.website_url,
            "audit": {
                "overall_score": audit_result.overall_score,
                "scores": scores,
                "summary": audit_result.summary,
                "recommendations": audit_result.recommendations
            },
            "business": business_data,
            "email": email_result,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-email", response_model=EmailSendResponse)
async def send_email_legacy(
    request: EmailSendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Send an email via configured provider (Resend preferred, SMTP fallback).
    """
    loop = asyncio.get_event_loop()
    
    reply_to_email = request.reply_to
    if not reply_to_email:
        result_accounts = await db.execute(select(EmailAccount).where(EmailAccount.user_id == current_user.id, EmailAccount.is_active == True))
        accounts = result_accounts.scalars().all()
        if accounts:
            reply_to_email = accounts[0].email_address

    if _resend_configured():
        from app.services.email.resend_sender import send_email as resend_send
        result = await loop.run_in_executor(
            executor,
            lambda: resend_send(
                to_email=request.to_email,
                subject=request.subject,
                body=request.body,
                html_body=request.html_body,
                to_name=request.to_name,
                reply_to=reply_to_email,
            )
        )
        return EmailSendResponse(
            success=result["success"],
            message_id=result.get("message_id"),
            error=result.get("error"),
            sent_at=datetime.utcnow() if result["success"] else None,
        )

    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        raise HTTPException(
            status_code=400,
            detail="Email not configured. Set RESEND_API_KEY or SMTP_USER/PASSWORD in .env"
        )

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart("alternative")
        msg["Subject"] = request.subject
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USER}>"
        msg["To"] = f"{request.to_name} <{request.to_email}>" if request.to_name else request.to_email

        if request.reply_to:
            msg["Reply-To"] = request.reply_to

        msg.attach(MIMEText(request.body, "plain"))
        if request.html_body:
            msg.attach(MIMEText(request.html_body, "html"))

        def send():
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
                return True

        await loop.run_in_executor(executor, send)

        return EmailSendResponse(
            success=True,
            message_id=None,
            sent_at=datetime.utcnow()
        )

    except Exception as e:
        return EmailSendResponse(
            success=False,
            error=str(e)
        )
