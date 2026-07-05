"""
Email Accounts Endpoints — Connect, manage, and test email accounts.

Supports:
  - Google OAuth (Gmail / Google Workspace)
  - Microsoft OAuth (Outlook / Microsoft 365)
  - SMTP (Hostinger, GoDaddy, Zoho, cPanel, etc.)
"""
import uuid
import logging
from datetime import datetime, timedelta
from typing import Annotated
from urllib.parse import urlencode

import requests as http_requests
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.encryption import encrypt, decrypt
from app.db.session import get_db
from app.models.email_account import EmailAccount
from app.models.user import User
from app.schemas.email_account import (
    SMTPTestRequest,
    SMTPConnectRequest,
    EmailAccountResponse,
    EmailAccountListResponse,
    SMTPTestResponse,
    OAuthURLResponse,
    SMTPPresetsResponse,
    SMTP_PRESETS,
)
from app.services.email.account_manager import test_smtp_connection

router = APIRouter()
logger = logging.getLogger(__name__)


# ── List Connected Accounts ──────────────────────────────────────────────────

@router.get("/", response_model=EmailAccountListResponse)
async def list_email_accounts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all email accounts connected by the current user."""
    result = await db.execute(
        select(EmailAccount)
        .where(EmailAccount.user_id == current_user.id)
        .order_by(EmailAccount.is_default.desc(), EmailAccount.created_at.desc())
    )
    accounts = result.scalars().all()

    return EmailAccountListResponse(
        accounts=[EmailAccountResponse.model_validate(a) for a in accounts],
        total=len(accounts),
    )


# ── SMTP Presets ─────────────────────────────────────────────────────────────

@router.get("/smtp-presets", response_model=SMTPPresetsResponse)
async def get_smtp_presets():
    """Return available SMTP provider presets (Hostinger, GoDaddy, etc.)."""
    return SMTPPresetsResponse(presets=SMTP_PRESETS)


# ── SMTP Test Connection ────────────────────────────────────────────────────

@router.post("/test-smtp", response_model=SMTPTestResponse)
async def test_smtp(
    request: SMTPTestRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Test an SMTP connection before saving the account."""
    result = test_smtp_connection(
        smtp_host=request.smtp_host,
        smtp_port=request.smtp_port,
        email_address=request.email_address,
        smtp_password=request.smtp_password,
    )
    return SMTPTestResponse(**result)


# ── SMTP Connect (Save Account) ─────────────────────────────────────────────

@router.post("/connect-smtp", response_model=EmailAccountResponse)
async def connect_smtp(
    request: SMTPConnectRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Save an SMTP email account after successful connection test."""
    # Check if already connected
    existing = await db.execute(
        select(EmailAccount).where(
            EmailAccount.user_id == current_user.id,
            EmailAccount.email_address == request.email_address,
        )
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=400,
            detail=f"{request.email_address} is already connected.",
        )

    # Test connection first
    test_result = test_smtp_connection(
        smtp_host=request.smtp_host,
        smtp_port=request.smtp_port,
        email_address=request.email_address,
        smtp_password=request.smtp_password,
    )
    if not test_result["success"]:
        raise HTTPException(status_code=400, detail=test_result["message"])

    # Check if this should be the default (first account)
    count_result = await db.execute(
        select(EmailAccount).where(EmailAccount.user_id == current_user.id)
    )
    is_first = len(count_result.scalars().all()) == 0

    account = EmailAccount(
        user_id=current_user.id,
        provider="smtp",
        email_address=request.email_address,
        display_name=request.display_name or request.email_address.split("@")[0],
        smtp_host=request.smtp_host,
        smtp_port=request.smtp_port,
        smtp_username=request.email_address,
        smtp_password=encrypt(request.smtp_password),
        imap_host=request.imap_host or request.smtp_host.replace("smtp", "imap"),
        imap_port=request.imap_port or 993,
        connection_status="connected",
        is_default=is_first,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)

    logger.info(f"SMTP account connected: {request.email_address} for user {current_user.id}")
    return EmailAccountResponse.model_validate(account)


# ── Google OAuth ─────────────────────────────────────────────────────────────

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_SCOPES = " ".join([
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
])


@router.get("/google/auth-url", response_model=OAuthURLResponse)
async def google_auth_url(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Generate Google OAuth authorization URL."""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=400,
            detail="Google OAuth not configured. Set GOOGLE_CLIENT_ID in .env",
        )

    redirect_uri = f"{settings.BACKEND_URL}/api/v1/email-accounts/google/callback"
    params = urlencode({
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": GOOGLE_SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": str(current_user.id),
    })
    return OAuthURLResponse(auth_url=f"{GOOGLE_AUTH_URL}?{params}")


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Handle Google OAuth callback — exchange code for tokens and save account."""
    redirect_uri = f"{settings.BACKEND_URL}/api/v1/email-accounts/google/callback"

    # Exchange authorization code for tokens
    token_resp = http_requests.post(GOOGLE_TOKEN_URL, data={
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }, timeout=15)

    if token_resp.status_code != 200:
        logger.error(f"Google token exchange failed: {token_resp.text}")
        return RedirectResponse(
            f"{settings.FRONTEND_URL}/settings/email-accounts?error=google_token_failed"
        )

    tokens = token_resp.json()

    # Get user info (email, name)
    userinfo_resp = http_requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        timeout=10,
    )
    if userinfo_resp.status_code != 200:
        return RedirectResponse(
            f"{settings.FRONTEND_URL}/settings/email-accounts?error=google_userinfo_failed"
        )

    userinfo = userinfo_resp.json()
    email = userinfo.get("email", "")
    name = userinfo.get("name", email.split("@")[0])
    user_id = uuid.UUID(state)

    # Check if already connected
    existing = await db.execute(
        select(EmailAccount).where(
            EmailAccount.user_id == user_id,
            EmailAccount.email_address == email,
        )
    )
    existing_account = existing.scalars().first()

    if existing_account:
        # Update tokens
        existing_account.access_token = encrypt(tokens["access_token"])
        existing_account.refresh_token = encrypt(tokens.get("refresh_token", ""))
        existing_account.token_expires_at = datetime.utcnow() + timedelta(
            seconds=tokens.get("expires_in", 3600)
        )
        existing_account.connection_status = "connected"
        existing_account.display_name = name
    else:
        # Check if first account
        count_result = await db.execute(
            select(EmailAccount).where(EmailAccount.user_id == user_id)
        )
        is_first = len(count_result.scalars().all()) == 0

        account = EmailAccount(
            user_id=user_id,
            provider="google",
            email_address=email,
            display_name=name,
            access_token=encrypt(tokens["access_token"]),
            refresh_token=encrypt(tokens.get("refresh_token", "")),
            token_expires_at=datetime.utcnow() + timedelta(
                seconds=tokens.get("expires_in", 3600)
            ),
            connection_status="connected",
            is_default=is_first,
        )
        db.add(account)

    await db.commit()
    logger.info(f"Google account connected: {email} for user {user_id}")

    return RedirectResponse(
        f"{settings.FRONTEND_URL}/settings/email-accounts?connected=google&email={email}"
    )





# ── Delete Account ───────────────────────────────────────────────────────────

@router.delete("/{account_id}")
async def delete_email_account(
    account_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Remove a connected email account."""
    result = await db.execute(
        select(EmailAccount).where(
            EmailAccount.id == account_id,
            EmailAccount.user_id == current_user.id,
        )
    )
    account = result.scalars().first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    was_default = account.is_default
    await db.delete(account)
    await db.commit()

    # If deleted account was default, set the next one as default
    if was_default:
        next_result = await db.execute(
            select(EmailAccount)
            .where(EmailAccount.user_id == current_user.id)
            .order_by(EmailAccount.created_at.asc())
            .limit(1)
        )
        next_account = next_result.scalars().first()
        if next_account:
            next_account.is_default = True
            await db.commit()

    return {"success": True, "message": "Account disconnected"}


# ── Set Default Account ──────────────────────────────────────────────────────

@router.patch("/{account_id}/default")
async def set_default_account(
    account_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Set an email account as the default for outreach."""
    # Verify ownership
    result = await db.execute(
        select(EmailAccount).where(
            EmailAccount.id == account_id,
            EmailAccount.user_id == current_user.id,
        )
    )
    account = result.scalars().first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Unset all defaults for this user
    await db.execute(
        update(EmailAccount)
        .where(EmailAccount.user_id == current_user.id)
        .values(is_default=False)
    )

    # Set the selected one as default
    account.is_default = True
    await db.commit()

    return {"success": True, "message": f"{account.email_address} set as default"}
