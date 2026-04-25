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
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(osm_sources.router, prefix="/osm", tags=["OSM Business Search"])
api_router.include_router(audits.router, prefix="/audits", tags=["Website Audits"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["Businesses"])
api_router.include_router(outreach.router, prefix="/outreach", tags=["Email Outreach"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(mail_chat.router, prefix="/mail", tags=["Mail & Chat"])
