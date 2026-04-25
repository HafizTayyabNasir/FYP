"""
Main FastAPI Application - AI Powered Client Hunt & Outreach
"""
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.api.v1.router import api_router


# Create required directories
TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"
TEMPLATES_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
(STATIC_DIR / "css").mkdir(exist_ok=True)
(STATIC_DIR / "js").mkdir(exist_ok=True)
(STATIC_DIR / "img").mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    # Shutdown
    print(f"👋 Shutting down {settings.APP_NAME}")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered system for hunting potential clients and automated outreach",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include API router
app.include_router(api_router, prefix="/api/v1")


# ==================== WEB ROUTES (Jinja Templates) ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - Dashboard"""
    return templates.TemplateResponse(
        name="pages/dashboard.html",
        request=request,
        context={"title": "Dashboard"}
    )


@app.get("/businesses", response_class=HTMLResponse)
async def businesses_page(request: Request):
    """Business search and listing page"""
    return templates.TemplateResponse(
        name="pages/businesses.html",
        request=request,
        context={"title": "Hunt Businesses"}
    )


@app.get("/audits", response_class=HTMLResponse)
async def audits_page(request: Request):
    """Website audits page"""
    return templates.TemplateResponse(
        name="pages/audits.html",
        request=request,
        context={"title": "Website Audits"}
    )


@app.get("/outreach", response_class=HTMLResponse)
async def outreach_page(request: Request):
    """Email outreach page"""
    return templates.TemplateResponse(
        name="pages/outreach.html",
        request=request,
        context={"title": "Email Outreach"}
    )


@app.get("/campaigns", response_class=HTMLResponse)
async def campaigns_page(request: Request):
    """Campaign management page"""
    return templates.TemplateResponse(
        name="pages/campaigns.html",
        request=request,
        context={"title": "Campaigns"}
    )


@app.get("/inbox", response_class=HTMLResponse)
async def inbox_page(request: Request):
    """Email inbox/chat page"""
    return templates.TemplateResponse(
        name="pages/inbox.html",
        request=request,
        context={"title": "Inbox"}
    )


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page"""
    return templates.TemplateResponse(
        name="pages/settings.html",
        request=request,
        context={"title": "Settings"}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
