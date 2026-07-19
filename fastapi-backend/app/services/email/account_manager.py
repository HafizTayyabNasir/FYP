"""
Unified Email Account Manager — routes email operations through the correct
provider (Google, Microsoft, or SMTP) based on the user's connected account.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from app.core.config import settings
from app.core.encryption import decrypt, encrypt
from app.models.email_account import EmailAccount

logger = logging.getLogger(__name__)


async def send_via_account(
    account: EmailAccount,
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    db_session=None,
) -> dict:
    """
    Send an email using the specified account.
    Automatically routes through the correct provider.
    """
    if account.provider == "google":
        return await _send_google(account, to_email, subject, body, html_body)

    elif account.provider == "smtp":
        return await _send_smtp(account, to_email, subject, body, html_body)

    else:
        return {"success": False, "error": f"Unknown provider: {account.provider}"}


async def _send_google(
    account: EmailAccount,
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
) -> dict:
    """Send via Gmail API using per-user OAuth tokens."""
    from app.services.email.gmail_client import send_email

    try:
        # Use per-user OAuth credentials stored in the account
        # Fall back to global config for client_id/secret (shared app credentials)
        client_id = settings.GOOGLE_CLIENT_ID or settings.GMAIL_CLIENT_ID
        client_secret = settings.GOOGLE_CLIENT_SECRET or settings.GMAIL_CLIENT_SECRET
        refresh_token = decrypt(account.refresh_token)

        result = send_email(
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            from_email=account.email_address,
            from_name=account.display_name or account.email_address,
            to_email=to_email,
            subject=subject,
            body=body,
            html_body=html_body,
        )
        return result
    except Exception as e:
        logger.error(f"Google send failed for {account.email_address}: {e}")
        return {"success": False, "error": str(e)}




async def _send_smtp(
    account: EmailAccount,
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
) -> dict:
    """Send via SMTP using stored credentials."""
    from app.services.email.smtp_sender import send_email

    try:
        result = send_email(
            host=account.smtp_host,
            port=account.smtp_port,
            user=account.smtp_username or account.email_address,
            password=decrypt(account.smtp_password),
            from_name=account.display_name or account.email_address,
            to_email=to_email,
            subject=subject,
            body=body,
            html_body=html_body,
        )
        return result
    except Exception as e:
        logger.error(f"SMTP send failed for {account.email_address}: {e}")
        return {"success": False, "error": str(e)}


def test_smtp_connection(
    smtp_host: str,
    smtp_port: int,
    email_address: str,
    smtp_password: str,
) -> dict:
    """Test SMTP connection without sending an email."""
    import smtplib

    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            server.ehlo()
            server.starttls()
            server.ehlo()

        server.login(email_address, smtp_password)
        server.quit()
        return {
            "success": True,
            "message": f"Successfully connected to {smtp_host}:{smtp_port}",
            "email_address": email_address,
        }
    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "message": "Authentication failed. Check your email and password.",
        }
    except smtplib.SMTPConnectError:
        return {
            "success": False,
            "message": f"Could not connect to {smtp_host}:{smtp_port}. Check host and port.",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection error: {str(e)}",
        }
