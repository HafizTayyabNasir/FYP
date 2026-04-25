"""
Outreach & Email Schemas for API Request/Response
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from enum import Enum


class EmailStatus(str, Enum):
    """Email status enum"""
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    REPLIED = "replied"
    BOUNCED = "bounced"
    FAILED = "failed"


class EmailGenerationRequest(BaseModel):
    """Request schema for AI email generation"""
    business_name: str = Field(..., description="Name of the target business")
    website_url: str = Field(..., description="Business website URL")
    industry: Optional[str] = Field(None, description="Business industry")
    location: Optional[str] = Field(None, description="Business location")
    target_audience: Optional[str] = Field(None, description="Business target customers")
    business_goal: Optional[str] = Field(None, description="Business main goal")
    
    # Audit scores (0-5)
    seo_score: float = Field(..., ge=0, le=5)
    ssl_score: float = Field(..., ge=0, le=5)
    load_speed_score: float = Field(..., ge=0, le=5)
    responsiveness_score: float = Field(..., ge=0, le=5)
    social_links_score: float = Field(..., ge=0, le=5)
    image_alt_score: float = Field(..., ge=0, le=5)
    
    # Additional context
    specific_issues: Optional[List[str]] = None
    competitor_examples: Optional[List[str]] = None
    additional_notes: Optional[str] = None


class GeneratedEmail(BaseModel):
    """Generated email response"""
    subject_lines: List[str] = Field(..., min_length=1, max_length=3)
    email_body: str
    personalization_note: str
    word_count: int
    generated_at: datetime


class EmailSendRequest(BaseModel):
    """Request to send an email"""
    to_email: EmailStr
    to_name: Optional[str] = None
    subject: str
    body: str
    html_body: Optional[str] = None
    reply_to: Optional[EmailStr] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    business_id: Optional[str] = None


class EmailSendResponse(BaseModel):
    """Response after sending email"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    sent_at: Optional[datetime] = None


class OutreachCampaign(BaseModel):
    """Outreach campaign schema"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    business_type: str
    city: str
    country: str
    status: str = "draft"
    
    # Statistics
    total_businesses: int = 0
    emails_sent: int = 0
    emails_opened: int = 0
    emails_replied: int = 0
    emails_bounced: int = 0
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OutreachEmail(BaseModel):
    """Individual outreach email"""
    id: Optional[str] = None
    campaign_id: Optional[str] = None
    business_id: str
    business_name: str
    to_email: str
    subject: str
    body: str
    status: EmailStatus = EmailStatus.DRAFT
    
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    
    audit_scores: Optional[Dict[str, float]] = None


class BusinessExtractedData(BaseModel):
    """Business data extracted by AI agent"""
    business_name: str
    website_url: str
    
    # Extracted information
    industry: Optional[str] = None
    services: Optional[List[str]] = None
    products: Optional[List[str]] = None
    core_offer: Optional[str] = None
    target_customers: Optional[str] = None
    business_goal: Optional[str] = None
    differentiator: Optional[str] = None
    target_audience: Optional[str] = None
    unique_selling_points: Optional[List[str]] = None
    business_description: Optional[str] = None
    company_size: Optional[str] = None
    years_in_business: Optional[int] = None
    location: Optional[str] = None
    contact_info: Optional[Dict[str, str]] = None
    
    # Extracted at
    extracted_at: datetime
    confidence_score: float = Field(..., ge=0, le=1)


class ExtractBusinessDataRequest(BaseModel):
    """Request to extract business data from website"""
    website_url: str
    business_name: Optional[str] = None
