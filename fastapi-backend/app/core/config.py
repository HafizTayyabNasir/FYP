"""
Application configuration using Pydantic Settings
"""
import os
from pathlib import Path
from functools import lru_cache
from typing import Optional, List

from pydantic_settings import BaseSettings
from pydantic import Field


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
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./app.db")
    
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
    
    # SMTP Configuration
    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = Field(default=None)
    SMTP_PASSWORD: Optional[str] = Field(default=None)
    SMTP_FROM_EMAIL: Optional[str] = Field(default=None)
    SMTP_FROM_NAME: str = "Elvion Solutions"
    
    # IMAP Configuration
    IMAP_HOST: str = Field(default="imap.gmail.com")
    IMAP_PORT: int = 993
    
    # Templates
    TEMPLATES_DIR: Path = Path(__file__).parent.parent / "templates"
    STATIC_DIR: Path = Path(__file__).parent.parent / "static"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
