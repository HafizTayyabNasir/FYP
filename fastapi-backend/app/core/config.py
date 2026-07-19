"""
Application configuration using Pydantic Settings
"""
import os
from pathlib import Path
from functools import lru_cache
from typing import Optional, List

from pydantic_settings import BaseSettings
from pydantic import Field, model_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "AI Powered Client Hunt & Outreach"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database (Supabase PostgreSQL)
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/ai_client_hunt")
    
    # Redis (for caching/celery)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # OSM Configuration
    OSM_CONTACT_EMAIL: str = Field(default="your_email@gmail.com")
    OSM_DEFAULT_RADIUS: int = 8000
    OSM_MAX_RESULTS: int = 200
    
    # Groq API (for AI agents)
    GROQ_API_KEY: Optional[str] = Field(default=None)
    
    # OpenAI API (alternative)
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    
    # Grok API (X.AI - for business data extraction)
    GROK_API_KEY: Optional[str] = Field(default=None)
    GROK_API_BASE_URL: str = "https://api.x.ai/v1"
    
    # Resend API (email sending)
    RESEND_API_KEY: Optional[str] = Field(default=None)
    RESEND_FROM_EMAIL: str = Field(default="team@elvionsolutions.com")
    RESEND_FROM_NAME: str = Field(default="Elvion Solutions")
    
    # Gmail API Configuration (preferred over SMTP/IMAP)
    # Run scripts/gmail_auth.py once to get GMAIL_REFRESH_TOKEN
    GMAIL_CLIENT_ID: Optional[str] = Field(default=None)
    GMAIL_CLIENT_SECRET: Optional[str] = Field(default=None)
    GMAIL_REFRESH_TOKEN: Optional[str] = Field(default=None)

    # SMTP Configuration (fallback when Gmail API is not configured)
    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = Field(default=None)
    SMTP_PASSWORD: Optional[str] = Field(default=None)
    SMTP_FROM_EMAIL: Optional[str] = Field(default=None)
    SMTP_FROM_NAME: str = "AI Client Hunt"
    
    # IMAP Configuration
    IMAP_HOST: str = Field(default="imap.gmail.com")
    IMAP_PORT: int = 993

    # Google OAuth (for per-user email connections)
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None)
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None)


    # Encryption key for storing tokens/passwords at rest (Fernet)
    # If not set, a key is derived from SECRET_KEY automatically
    ENCRYPTION_KEY: Optional[str] = Field(default=None)

    # URLs (for OAuth callbacks and redirects)
    BACKEND_URL: str = Field(default="http://localhost:8000")
    FRONTEND_URL: str = Field(default="http://localhost:3000")

    # Admin Portal Credentials
    ADMIN_EMAIL: str = Field(default="admin@example.com")
    ADMIN_PASSWORD: str = Field(default="admin123")

    # Templates
    TEMPLATES_DIR: Path = Path(__file__).parent.parent / "templates"
    STATIC_DIR: Path = Path(__file__).parent.parent / "static"
    
    @model_validator(mode="after")
    def _remap_groq_key(self):
        # If user put their Groq key (gsk_...) under GROK_API_KEY by mistake,
        # move it to GROQ_API_KEY automatically.
        if not self.GROQ_API_KEY and self.GROK_API_KEY and self.GROK_API_KEY.startswith("gsk_"):
            self.GROQ_API_KEY = self.GROK_API_KEY
            self.GROK_API_KEY = None
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
