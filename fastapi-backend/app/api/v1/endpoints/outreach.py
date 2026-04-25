"""
Outreach Endpoints - Email generation and sending
"""
import asyncio
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

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

router = APIRouter()

# Thread pool for running sync operations
executor = ThreadPoolExecutor(max_workers=4)


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
    
    The AI agent analyzes the website content to identify:
    - Industry
    - Services/Products
    - Target audience
    - Unique selling points
    - Contact information
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
async def run_full_pipeline(
    website_url: str,
    business_name: Optional[str] = None,
    to_email: Optional[str] = None
):
    """
    Run the complete pipeline:
    1. Audit the website
    2. Extract business data
    3. Generate personalized email
    4. Optionally send the email
    
    This is the main workflow combining all agents.
    """
    try:
        from app.services.website_audit.orchestrator import WebsiteAuditOrchestrator
        
        loop = asyncio.get_event_loop()
        
        # Step 1: Run website audit
        audit_orchestrator = WebsiteAuditOrchestrator()
        audit_result = await loop.run_in_executor(
            executor,
            lambda: audit_orchestrator.run_audit(website_url)
        )
        
        # Step 2: Extract business data
        extractor = BusinessDataExtractorAgent()
        business_data = await loop.run_in_executor(
            executor,
            lambda: extractor.extract_business_data(website_url, business_name)
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
        
        email_result = await loop.run_in_executor(
            executor,
            lambda: email_agent.generate_email(
                business_name=business_data.get("business_name", business_name or "Unknown"),
                website_url=website_url,
                seo_score=scores["seo"],
                ssl_score=scores["ssl"],
                load_speed_score=scores["load_speed"],
                responsiveness_score=scores["responsiveness"],
                social_links_score=scores["social_links"],
                image_alt_score=scores["image_alt"],
                industry=business_data.get("industry"),
                location=business_data.get("location"),
                target_audience=business_data.get("target_audience"),
                specific_issues=specific_issues[:6] if specific_issues else None
            )
        )
        
        return {
            "pipeline_status": "completed",
            "website_url": website_url,
            "audit": {
                "overall_score": audit_result.overall_score,
                "scores": scores,
                "summary": audit_result.summary,
                "recommendations": audit_result.recommendations
            },
            "business_data": business_data,
            "generated_email": email_result,
            "ready_to_send": to_email is not None,
            "target_email": to_email
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-email", response_model=EmailSendResponse)
async def send_email(request: EmailSendRequest):
    """
    Send an email via SMTP.
    
    Requires SMTP configuration in environment variables.
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from datetime import datetime
    
    from app.core.config import settings
    
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        raise HTTPException(
            status_code=400,
            detail="SMTP not configured. Set SMTP_USER and SMTP_PASSWORD."
        )
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = request.subject
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USER}>"
        msg["To"] = f"{request.to_name} <{request.to_email}>" if request.to_name else request.to_email
        
        if request.reply_to:
            msg["Reply-To"] = request.reply_to
        
        # Add body
        text_part = MIMEText(request.body, "plain")
        msg.attach(text_part)
        
        if request.html_body:
            html_part = MIMEText(request.html_body, "html")
            msg.attach(html_part)
        
        # Send email
        def send():
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
                return True
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, send)
        
        return EmailSendResponse(
            success=True,
            message_id=None,  # Would need to parse from SMTP response
            sent_at=datetime.utcnow()
        )
        
    except Exception as e:
        return EmailSendResponse(
            success=False,
            error=str(e)
        )
