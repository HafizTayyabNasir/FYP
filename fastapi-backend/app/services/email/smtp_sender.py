"""
SMTP sender — sends emails via the configured SMTP server.
"""
import smtplib
import uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def send_email(
    host: str,
    port: int,
    user: str,
    password: str,
    from_name: str,
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> dict:
    """
    Send an email via SMTP STARTTLS.
    Returns a dict with success, message_id, sent_at, and optional error.
    """
    message_id = str(uuid.uuid4())
    from_address = f"{from_name} <{user}>"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = to_email
    msg["Message-ID"] = f"<{message_id}@mail>"
    if reply_to:
        msg["Reply-To"] = reply_to

    msg.attach(MIMEText(body, "plain", "utf-8"))
    if html_body:
        msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user, password)
            server.send_message(msg)

        logger.info(f"Email sent to {to_email} | subject: {subject}")
        return {"success": True, "message_id": message_id, "sent_at": datetime.utcnow().isoformat()}

    except smtplib.SMTPAuthenticationError:
        err = "Authentication failed. Check SMTP_USER and SMTP_PASSWORD in .env"
        logger.error(err)
        return {"success": False, "error": err}
    except smtplib.SMTPRecipientsRefused:
        err = f"Recipient refused: {to_email}"
        logger.error(err)
        return {"success": False, "error": err}
    except Exception as e:
        err = str(e)
        logger.error(f"SMTP error: {err}")
        return {"success": False, "error": err}
