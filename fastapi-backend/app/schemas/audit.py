"""
Website Audit Schemas for API Request/Response
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AuditRequest(BaseModel):
    """Request schema for website audit"""
    website_url: str = Field(..., description="Website URL to audit")
    include_seo: bool = Field(default=True)
    include_ssl: bool = Field(default=True)
    include_speed: bool = Field(default=True)
    include_responsiveness: bool = Field(default=True)
    include_social_links: bool = Field(default=True)
    include_image_alt: bool = Field(default=True)


class SEOAuditResult(BaseModel):
    """SEO audit result"""
    score: float = Field(..., ge=0, le=5)
    flaws: List[str] = []
    metadata: Optional[Dict[str, Any]] = None


class SSLAuditResult(BaseModel):
    """SSL certificate audit result"""
    score: float = Field(..., ge=0, le=5)
    flaws: List[str] = []
    https_accessible: bool = False
    certificate_valid: bool = False
    days_until_expiry: Optional[int] = None
    hsts_enabled: bool = False
    redirects_to_https: bool = False


class LoadSpeedAuditResult(BaseModel):
    """Load speed audit result"""
    score: float = Field(..., ge=0, le=5)
    flaws: List[str] = []
    load_time_ms: Optional[float] = None
    dom_content_loaded_ms: Optional[float] = None
    timing_details: Optional[Dict[str, float]] = None


class ResponsivenessAuditResult(BaseModel):
    """Responsiveness audit result"""
    score: float = Field(..., ge=0, le=5)
    flaws: List[str] = []
    pages_checked: int = 0
    viewport_meta_present: bool = False
    mobile_friendly: bool = False


class SocialLinksAuditResult(BaseModel):
    """Social links audit result"""
    score: float = Field(..., ge=0, le=5)
    flaws: List[str] = []
    links_found: int = 0
    links_accessible: int = 0
    links_broken: int = 0
    social_platforms: List[str] = []


class ImageAltAuditResult(BaseModel):
    """Image alt tags audit result"""
    score: float = Field(..., ge=0, le=5)
    flaws: List[str] = []
    total_images: int = 0
    images_with_issues: int = 0
    pages_checked: int = 0


class WebsiteAuditResponse(BaseModel):
    """Complete website audit response"""
    website_url: str
    audit_timestamp: datetime
    overall_score: float = Field(..., ge=0, le=5)
    
    seo: Optional[SEOAuditResult] = None
    ssl: Optional[SSLAuditResult] = None
    load_speed: Optional[LoadSpeedAuditResult] = None
    responsiveness: Optional[ResponsivenessAuditResult] = None
    social_links: Optional[SocialLinksAuditResult] = None
    image_alt: Optional[ImageAltAuditResult] = None
    
    # Summary for display
    summary: str = ""
    recommendations: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "website_url": "https://example.com",
                "audit_timestamp": "2026-02-27T10:00:00Z",
                "overall_score": 3.5,
                "seo": {"score": 4, "flaws": ["Missing meta description"]},
                "ssl": {"score": 5, "flaws": [], "https_accessible": True},
                "load_speed": {"score": 3, "flaws": ["Slow TTFB"], "load_time_ms": 4500},
                "responsiveness": {"score": 4, "flaws": [], "mobile_friendly": True},
                "social_links": {"score": 2, "flaws": ["Few social links"], "links_found": 2},
                "image_alt": {"score": 3, "flaws": ["Some images missing alt"], "total_images": 20}
            }
        }


class BulkAuditRequest(BaseModel):
    """Request schema for bulk website audits"""
    websites: List[str] = Field(..., min_length=1, max_length=50)
    include_seo: bool = True
    include_ssl: bool = True
    include_speed: bool = True
    include_responsiveness: bool = True
    include_social_links: bool = True
    include_image_alt: bool = True


class BulkAuditResponse(BaseModel):
    """Response schema for bulk audits"""
    total_requested: int
    total_completed: int
    total_failed: int
    results: List[WebsiteAuditResponse]
    errors: List[Dict[str, str]] = []
