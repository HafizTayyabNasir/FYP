"""
API v1 Router - Combines all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    osm_sources,
    audits,
    businesses,
    outreach,
    campaigns,
    mail_chat,
    health,
    auth,
    admin,
    pricing,
    email_accounts,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(pricing.router, prefix="/pricing", tags=["Pricing"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(osm_sources.router, prefix="/osm", tags=["OSM Business Search"])
api_router.include_router(audits.router, prefix="/audits", tags=["Website Audits"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["Businesses"])
api_router.include_router(outreach.router, prefix="/outreach", tags=["Email Outreach"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(mail_chat.router, prefix="/mail", tags=["Mail & Chat"])
api_router.include_router(email_accounts.router, prefix="/email-accounts", tags=["Email Accounts"])
