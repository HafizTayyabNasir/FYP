"""
Campaigns Endpoint - Manage outreach campaigns
"""
import json
import uuid
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()

# Simple file-based storage
DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data"
CAMPAIGNS_FILE = DATA_DIR / "campaigns.json"


class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    business_type: str
    city: str
    country: str


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


def _ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)
    if not CAMPAIGNS_FILE.exists():
        CAMPAIGNS_FILE.write_text("[]")


def _load_campaigns() -> List[dict]:
    _ensure_data_dir()
    try:
        return json.loads(CAMPAIGNS_FILE.read_text())
    except:
        return []


def _save_campaigns(campaigns: List[dict]):
    _ensure_data_dir()
    CAMPAIGNS_FILE.write_text(json.dumps(campaigns, indent=2, default=str))


@router.get("")
async def list_campaigns(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """
    List all campaigns with optional status filter.
    """
    campaigns = _load_campaigns()
    
    if status:
        campaigns = [c for c in campaigns if c.get("status") == status]
    
    # Sort by created_at descending
    campaigns.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Pagination
    total = len(campaigns)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = campaigns[start:end]
    
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "campaigns": paginated
    }


@router.post("")
async def create_campaign(campaign: CampaignCreate):
    """
    Create a new outreach campaign.
    """
    campaigns = _load_campaigns()
    
    new_campaign = {
        "id": str(uuid.uuid4()),
        "name": campaign.name,
        "description": campaign.description,
        "business_type": campaign.business_type,
        "city": campaign.city,
        "country": campaign.country,
        "status": "draft",
        "total_businesses": 0,
        "emails_sent": 0,
        "emails_opened": 0,
        "emails_replied": 0,
        "emails_bounced": 0,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    campaigns.append(new_campaign)
    _save_campaigns(campaigns)
    
    return new_campaign


@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str):
    """
    Get a specific campaign by ID.
    """
    campaigns = _load_campaigns()
    
    for campaign in campaigns:
        if campaign.get("id") == campaign_id:
            return campaign
    
    raise HTTPException(status_code=404, detail="Campaign not found")


@router.put("/{campaign_id}")
async def update_campaign(campaign_id: str, updates: CampaignUpdate):
    """
    Update a campaign.
    """
    campaigns = _load_campaigns()
    
    for i, campaign in enumerate(campaigns):
        if campaign.get("id") == campaign_id:
            if updates.name:
                campaigns[i]["name"] = updates.name
            if updates.description:
                campaigns[i]["description"] = updates.description
            if updates.status:
                campaigns[i]["status"] = updates.status
            campaigns[i]["updated_at"] = datetime.utcnow().isoformat()
            
            _save_campaigns(campaigns)
            return campaigns[i]
    
    raise HTTPException(status_code=404, detail="Campaign not found")


@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str):
    """
    Delete a campaign.
    """
    campaigns = _load_campaigns()
    original_count = len(campaigns)
    
    campaigns = [c for c in campaigns if c.get("id") != campaign_id]
    
    if len(campaigns) == original_count:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    _save_campaigns(campaigns)
    return {"message": "Campaign deleted"}


@router.post("/{campaign_id}/start")
async def start_campaign(campaign_id: str):
    """
    Start a campaign (change status to active).
    """
    campaigns = _load_campaigns()
    
    for i, campaign in enumerate(campaigns):
        if campaign.get("id") == campaign_id:
            campaigns[i]["status"] = "active"
            campaigns[i]["started_at"] = datetime.utcnow().isoformat()
            campaigns[i]["updated_at"] = datetime.utcnow().isoformat()
            
            _save_campaigns(campaigns)
            return campaigns[i]
    
    raise HTTPException(status_code=404, detail="Campaign not found")


@router.post("/{campaign_id}/pause")
async def pause_campaign(campaign_id: str):
    """
    Pause a campaign.
    """
    campaigns = _load_campaigns()
    
    for i, campaign in enumerate(campaigns):
        if campaign.get("id") == campaign_id:
            campaigns[i]["status"] = "paused"
            campaigns[i]["updated_at"] = datetime.utcnow().isoformat()
            
            _save_campaigns(campaigns)
            return campaigns[i]
    
    raise HTTPException(status_code=404, detail="Campaign not found")


@router.get("/{campaign_id}/stats")
async def get_campaign_stats(campaign_id: str):
    """
    Get detailed statistics for a campaign.
    """
    campaigns = _load_campaigns()
    
    for campaign in campaigns:
        if campaign.get("id") == campaign_id:
            total = campaign.get("total_businesses", 0)
            sent = campaign.get("emails_sent", 0)
            opened = campaign.get("emails_opened", 0)
            replied = campaign.get("emails_replied", 0)
            
            return {
                "campaign_id": campaign_id,
                "total_businesses": total,
                "emails_sent": sent,
                "emails_opened": opened,
                "emails_replied": replied,
                "emails_bounced": campaign.get("emails_bounced", 0),
                "open_rate": round((opened / sent * 100) if sent > 0 else 0, 2),
                "reply_rate": round((replied / sent * 100) if sent > 0 else 0, 2),
                "progress": round((sent / total * 100) if total > 0 else 0, 2)
            }
    
    raise HTTPException(status_code=404, detail="Campaign not found")
