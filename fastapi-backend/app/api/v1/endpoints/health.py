"""
Health Check Endpoint
"""
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with service status"""
    health_status = {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "services": {
            "groq_api": "configured" if settings.GROQ_API_KEY else "not_configured",
            "grok_api": "configured" if settings.GROK_API_KEY else "not_configured",
            "smtp": "configured" if settings.SMTP_USER else "not_configured",
        }
    }
    return health_status
