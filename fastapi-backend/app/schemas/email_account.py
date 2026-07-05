"""
Pydantic schemas for Email Account management.
"""
import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr


# ── SMTP Provider Presets ─────────────────────────────────────────────────────

SMTP_PRESETS = {
    "hostinger": {
        "label": "Hostinger",
        "smtp_host": "smtp.hostinger.com",
        "smtp_port": 587,
        "imap_host": "imap.hostinger.com",
        "imap_port": 993,
    },
    "godaddy": {
        "label": "GoDaddy",
        "smtp_host": "smtpout.secureserver.net",
        "smtp_port": 587,
        "imap_host": "imap.secureserver.net",
        "imap_port": 993,
    },
    "zoho": {
        "label": "Zoho Mail",
        "smtp_host": "smtp.zoho.com",
        "smtp_port": 587,
        "imap_host": "imap.zoho.com",
        "imap_port": 993,
    },
    "namecheap": {
        "label": "Namecheap (Private Email)",
        "smtp_host": "mail.privateemail.com",
        "smtp_port": 587,
        "imap_host": "mail.privateemail.com",
        "imap_port": 993,
    },
    "cpanel": {
        "label": "cPanel / Custom Domain",
        "smtp_host": "",
        "smtp_port": 587,
        "imap_host": "",
        "imap_port": 993,
    },
    "gmail": {
        "label": "Gmail (SMTP)",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "imap_host": "imap.gmail.com",
        "imap_port": 993,
    },
}


# ── Request Schemas ───────────────────────────────────────────────────────────

class SMTPTestRequest(BaseModel):
    """Test an SMTP connection before saving."""
    smtp_host: str = Field(..., description="SMTP server hostname")
    smtp_port: int = Field(587, description="SMTP server port")
    email_address: str = Field(..., description="Email address")
    smtp_password: str = Field(..., description="Email password or app password")
    display_name: Optional[str] = Field(None, description="Sender display name")


class SMTPConnectRequest(BaseModel):
    """Connect an SMTP/IMAP email account."""
    smtp_host: str
    smtp_port: int = 587
    email_address: str
    smtp_password: str
    display_name: Optional[str] = None
    imap_host: Optional[str] = None
    imap_port: Optional[int] = 993


class SetDefaultRequest(BaseModel):
    """Mark an account as default."""
    pass  # No body needed, account_id comes from path


# ── Response Schemas ──────────────────────────────────────────────────────────

class EmailAccountResponse(BaseModel):
    """Public representation of a connected email account."""
    id: uuid.UUID
    provider: str
    email_address: str
    display_name: Optional[str] = None
    is_active: bool = True
    is_default: bool = False
    connection_status: str = "pending"
    last_synced_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmailAccountListResponse(BaseModel):
    """List of connected accounts."""
    accounts: List[EmailAccountResponse]
    total: int


class SMTPTestResponse(BaseModel):
    """Result of SMTP connection test."""
    success: bool
    message: str
    email_address: Optional[str] = None


class OAuthURLResponse(BaseModel):
    """OAuth authorization URL."""
    auth_url: str


class SMTPPresetsResponse(BaseModel):
    """Available SMTP provider presets."""
    presets: dict
