"""
Business Schemas for API Request/Response
"""
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime


class BusinessSearchRequest(BaseModel):
    """Request schema for business search via OSM"""
    business_type: str = Field(..., description="Type of business (e.g., restaurant, dentist, cafe)")
    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country name or code")
    radius_meters: int = Field(default=8000, ge=500, le=50000, description="Search radius in meters")
    enable_website_crawl: bool = Field(default=False, description="Enable website crawling for emails")


class BusinessData(BaseModel):
    """Business data from OSM"""
    id: Optional[str] = None
    business_name: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    all_emails_found: Optional[List[str]] = None
    website_crawl: Optional[dict] = None
    
    # Audit scores (added after audit)
    audit_completed: bool = False
    seo_score: Optional[float] = None
    ssl_score: Optional[float] = None
    load_speed_score: Optional[float] = None
    responsiveness_score: Optional[float] = None
    social_links_score: Optional[float] = None
    image_alt_score: Optional[float] = None
    overall_score: Optional[float] = None
    
    # Business details (extracted by AI)
    industry: Optional[str] = None
    services: Optional[List[str]] = None
    target_audience: Optional[str] = None
    unique_selling_points: Optional[List[str]] = None
    business_description: Optional[str] = None
    
    class Config:
        extra = "allow"


class BusinessSearchResponse(BaseModel):
    """Response schema for business search"""
    query: dict
    result_count: int
    emails_found_count: int
    results: List[BusinessData]


class BusinessListResponse(BaseModel):
    """Response for listing businesses"""
    total: int
    page: int
    per_page: int
    businesses: List[Any]  # Allow any dict-like data
