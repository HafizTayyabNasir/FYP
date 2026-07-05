"""
Resend Email Sender — sends emails via the Resend API.
Supports both transactional and outreach emails.
"""
import uuid
import logging
from datetime import datetime
from typing import Optional, List

import resend

from app.core.config import settings

logger = logging.getLogger(__name__)


def _configure():
    """Set the Resend API key from settings."""
    resend.api_key = settings.RESEND_API_KEY


def is_configured() -> bool:
    """Check whether Resend is properly configured."""
    return bool(settings.RESEND_API_KEY)


def get_from_address() -> str:
    """Return the configured 'from' address string."""
    name = settings.RESEND_FROM_NAME or settings.SMTP_FROM_NAME or "Elvion Solutions"
    email = settings.RESEND_FROM_EMAIL or "onboarding@resend.dev"
    return f"{name} <{email}>"


def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    from_name: Optional[str] = None,
    from_email: Optional[str] = None,
    reply_to: Optional[str] = None,
    to_name: Optional[str] = None,
) -> dict:
    """
    Send an email via Resend API.

    Returns a dict with success, message_id, sent_at, and optional error.
    """
    _configure()

    sender_name = from_name or settings.RESEND_FROM_NAME or settings.SMTP_FROM_NAME or "Elvion Solutions"
    sender_email = from_email or settings.RESEND_FROM_EMAIL or "onboarding@resend.dev"
    from_address = f"{sender_name} <{sender_email}>"

    # Build the email body — prefer HTML, fall back to plain text wrapped in <pre>
    email_html = html_body or f"<div style='white-space: pre-wrap; font-family: Arial, sans-serif; line-height: 1.6;'>{body}</div>"

    params: dict = {
        "from": from_address,
        "to": [to_email],
        "subject": subject,
        "html": email_html,
        "text": body,
    }

    if reply_to:
        params["reply_to"] = [reply_to]

    try:
        result = resend.Emails.send(params)
        message_id = result.get("id", str(uuid.uuid4()))
        logger.info(f" Email sent via Resend to {to_email} | id: {message_id}")
        return {
            "success": True,
            "message_id": message_id,
            "sent_at": datetime.utcnow().isoformat(),
        }
    except resend.exceptions.ResendError as e:
        err = str(e)
        logger.error(f"❌ Resend API error: {err}")
        return {"success": False, "error": err}
    except Exception as e:
        err = str(e)
        logger.error(f"❌ Resend send error: {err}")
        return {"success": False, "error": err}
