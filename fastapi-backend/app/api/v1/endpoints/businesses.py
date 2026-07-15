"""
Businesses Endpoint - Manage discovered businesses
"""
import asyncio
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from app.schemas.business import (
    BusinessData,
    BusinessListResponse
)

router = APIRouter()

# Simple file-based storage for demo purposes
# In production, use a proper database
DATA_DIR = Path(__file__).parent.parent.parent.parent.parent / "data"
BUSINESSES_FILE = DATA_DIR / "businesses.json"

executor = ThreadPoolExecutor(max_workers=4)


def _ensure_data_dir():
    """Ensure data directory exists"""
    DATA_DIR.mkdir(exist_ok=True)
    if not BUSINESSES_FILE.exists():
        BUSINESSES_FILE.write_text("[]")


def _load_businesses() -> List[dict]:
    """Load businesses from storage"""
    _ensure_data_dir()
    try:
        return json.loads(BUSINESSES_FILE.read_text())
    except:
        return []


def _save_businesses(businesses: List[dict]):
    """Save businesses to storage"""
    _ensure_data_dir()
    BUSINESSES_FILE.write_text(json.dumps(businesses, indent=2, default=str))


@router.get("", response_model=BusinessListResponse)
async def list_businesses(
    page: int = Query(1, ge=1),
    per_page: int = Query(1000, ge=1, le=10000),
    has_email: Optional[bool] = None,
    has_audit: Optional[bool] = None,
    industry: Optional[str] = None
):
    """
    List all discovered businesses with pagination and filtering.
    """
    businesses = _load_businesses()
    
    # Apply filters
    if has_email is not None:
        businesses = [b for b in businesses if bool(b.get("email")) == has_email]
    
    if has_audit is not None:
        businesses = [b for b in businesses if b.get("audit_completed", False) == has_audit]
    
    if industry:
        businesses = [b for b in businesses if industry.lower() in (b.get("industry") or "").lower()]
    
    # Pagination
    total = len(businesses)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = businesses[start:end]
    
    return BusinessListResponse(
        total=total,
        page=page,
        per_page=per_page,
        businesses=paginated
    )


@router.get("/{business_id}")
async def get_business(business_id: str):
    """
    Get a specific business by ID.
    """
    businesses = _load_businesses()
    
    for business in businesses:
        if business.get("id") == business_id:
            return business
    
    raise HTTPException(status_code=404, detail="Business not found")


@router.post("/save")
async def save_businesses(businesses: List[dict]):
    """
    Save a list of businesses (from OSM search).
    """
    existing = _load_businesses()
    existing_ids = {b.get("id") for b in existing}
    
    added = 0
    for business in businesses:
        if business.get("id") not in existing_ids:
            existing.append(business)
            added += 1
    
    _save_businesses(existing)
    
    return {
        "message": f"Saved {added} new businesses",
        "total": len(existing)
    }


@router.put("/{business_id}")
async def update_business(business_id: str, updates: dict):
    """
    Update a business record.
    """
    businesses = _load_businesses()
    
    for i, business in enumerate(businesses):
        if business.get("id") == business_id:
            businesses[i].update(updates)
            _save_businesses(businesses)
            return businesses[i]
    
    raise HTTPException(status_code=404, detail="Business not found")


@router.delete("/{business_id}")
async def delete_business(business_id: str):
    """
    Delete a business record.
    """
    businesses = _load_businesses()
    original_count = len(businesses)
    
    businesses = [b for b in businesses if b.get("id") != business_id]
    
    if len(businesses) == original_count:
        raise HTTPException(status_code=404, detail="Business not found")
    
    _save_businesses(businesses)
    return {"message": "Business deleted"}


@router.post("/{business_id}/audit")
async def run_audit_for_business(business_id: str):
    """
    Run a website audit for a specific business.
    """
    from app.services.website_audit.orchestrator import WebsiteAuditOrchestrator
    
    businesses = _load_businesses()
    business = None
    business_idx: int = -1
    
    for i, b in enumerate(businesses):
        if b.get("id") == business_id:
            business = b
            business_idx = i
            break
    
    if not business or business_idx < 0:
        raise HTTPException(status_code=404, detail="Business not found")
    
    if not business.get("website"):
        raise HTTPException(status_code=400, detail="Business has no website")
    
    try:
        orchestrator = WebsiteAuditOrchestrator()
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            lambda: orchestrator.run_audit(business["website"])
        )
        
        # Update business with audit results - cast to list of dicts for proper indexing
        biz_list = list(businesses)
        biz_list[business_idx]["audit_completed"] = True
        biz_list[business_idx]["seo_score"] = result.seo.score if result.seo else 0
        biz_list[business_idx]["ssl_score"] = result.ssl.score if result.ssl else 0
        biz_list[business_idx]["load_speed_score"] = result.load_speed.score if result.load_speed else 0
        biz_list[business_idx]["responsiveness_score"] = result.responsiveness.score if result.responsiveness else 0
        biz_list[business_idx]["social_links_score"] = result.social_links.score if result.social_links else 0
        biz_list[business_idx]["image_alt_score"] = result.image_alt.score if result.image_alt else 0
        biz_list[business_idx]["overall_score"] = result.overall_score
        biz_list[business_idx]["audit_summary"] = result.summary
        biz_list[business_idx]["audit_recommendations"] = result.recommendations
        
        _save_businesses(biz_list)
        
        return {
            "business_id": business_id,
            "audit_completed": True,
            "overall_score": result.overall_score,
            "scores": {
                "seo": result.seo.score if result.seo else 0,
                "ssl": result.ssl.score if result.ssl else 0,
                "load_speed": result.load_speed.score if result.load_speed else 0,
                "responsiveness": result.responsiveness.score if result.responsiveness else 0,
                "social_links": result.social_links.score if result.social_links else 0,
                "image_alt": result.image_alt.score if result.image_alt else 0
            },
            "summary": result.summary,
            "recommendations": result.recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_business_stats():
    """
    Get summary statistics for all businesses.
    """
    businesses = _load_businesses()
    
    total = len(businesses)
    with_email = sum(1 for b in businesses if b.get("email"))
    with_website = sum(1 for b in businesses if b.get("website"))
    audited = sum(1 for b in businesses if b.get("audit_completed"))
    
    # Score distribution
    scores = [b.get("overall_score", 0) for b in businesses if b.get("audit_completed")]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    return {
        "total_businesses": total,
        "with_email": with_email,
        "with_website": with_website,
        "audited": audited,
        "average_score": round(avg_score, 2),
        "score_distribution": {
            "excellent": sum(1 for s in scores if s >= 4),
            "good": sum(1 for s in scores if 3 <= s < 4),
            "fair": sum(1 for s in scores if 2 <= s < 3),
            "poor": sum(1 for s in scores if s < 2)
        }
    }


@router.post("/{business_id}/crawl")
async def crawl_business_website(business_id: str, use_playwright: bool = True):
    """
    Advanced crawl for saved business website to extract email, phone, and social media.
    Uses Playwright for JavaScript-rendered websites when use_playwright=True.
    """
    businesses = _load_businesses()
    business = None
    business_idx: int = -1
    
    for i, b in enumerate(businesses):
        if b.get("id") == business_id:
            business = b
            business_idx = i
            break
    
    if not business or business_idx < 0:
        raise HTTPException(status_code=404, detail="Business not found")
    
    if not business.get("website"):
        raise HTTPException(status_code=400, detail="Business has no website")
    
    # Allow re-crawl even if email exists (to find/update Facebook, Instagram, phone)
    
    url = business["website"]
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    
    try:
        if use_playwright:
            # Use Playwright for JS-rendered websites
            from app.services.scraping import scrape_website_for_contacts
            
            contacts = await scrape_website_for_contacts(url, timeout=30000, max_pages=15)
            
            # Update business with found data
            updated = False
            biz_list = list(businesses)
            
            if contacts.best_email:
                biz_list[business_idx]["email"] = contacts.best_email
                updated = True
                
            if contacts.best_phone and not biz_list[business_idx].get("phone"):
                biz_list[business_idx]["phone"] = contacts.best_phone
                updated = True
                
            if contacts.facebook and not biz_list[business_idx].get("facebook"):
                biz_list[business_idx]["facebook"] = contacts.facebook
                updated = True
                
            if contacts.instagram and not biz_list[business_idx].get("instagram"):
                biz_list[business_idx]["instagram"] = contacts.instagram
                updated = True
            
            if updated:
                _save_businesses(biz_list)
            
            return {
                "email": contacts.best_email,
                "phone": contacts.best_phone,
                "facebook": contacts.facebook,
                "instagram": contacts.instagram,
                "twitter": contacts.twitter,
                "linkedin": contacts.linkedin,
                "all_emails": contacts.emails,
                "all_phones": contacts.phones,
                "pages_crawled": len(contacts.pages_crawled),
                "message": f"Found {len(contacts.emails)} emails, {len(contacts.phones)} phones" if contacts.emails else "No email found after comprehensive search"
            }
        else:
            # Fallback to httpx-based scraping
            return await _crawl_with_httpx(url, businesses, business_idx)
            
    except Exception as e:
        # Try httpx fallback if Playwright fails
        try:
            return await _crawl_with_httpx(url, businesses, business_idx)
        except Exception as e2:
            raise HTTPException(status_code=500, detail=f"Crawl failed: {str(e)}. Fallback also failed: {str(e2)}")


async def _crawl_with_httpx(url: str, businesses: list, business_idx: int) -> dict:
    from app.services.scraping.website_scraper import _scrape_with_httpx_async
    try:
        contacts = await _scrape_with_httpx_async(url, timeout=10)
        if contacts.best_email or contacts.best_phone or contacts.facebook or contacts.instagram:
            businesses[business_idx]["email"] = contacts.best_email or businesses[business_idx].get("email")
            businesses[business_idx]["phone"] = contacts.best_phone or businesses[business_idx].get("phone")
            businesses[business_idx]["facebook"] = contacts.facebook or businesses[business_idx].get("facebook")
            businesses[business_idx]["instagram"] = contacts.instagram or businesses[business_idx].get("instagram")
            _save_businesses(businesses)
            return {
                "email": contacts.best_email, 
                "phone": contacts.best_phone,
                "facebook": contacts.facebook,
                "instagram": contacts.instagram,
                "message": "Extracted contacts via fallback", 
                "pages_checked": len(contacts.pages_crawled)
            }
        return {"email": None, "message": "No contacts found", "pages_checked": len(contacts.pages_crawled)}
    except Exception as e:
        return {"email": None, "message": str(e), "pages_checked": 0}



@router.post("/crawl-url")
async def crawl_website_url(data: dict):
    """
    Advanced website scraping to extract email, phone, and social media.
    Uses Playwright for JavaScript-rendered websites with httpx fallback.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    url = data.get("url")
    use_playwright = data.get("use_playwright", True)
    
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    
    playwright_error = None
    
    if use_playwright:
        try:
            # Use Playwright for JS-rendered websites
            from app.services.scraping import scrape_website_for_contacts
            
            logger.info(f"Starting Playwright crawl for {url}")
            contacts = await scrape_website_for_contacts(url, timeout=30000, max_pages=15)
            logger.info(f"Playwright found: {len(contacts.emails)} emails, {len(contacts.phones)} phones")
            
            return {
                "email": contacts.best_email,
                "phone": contacts.best_phone,
                "facebook": contacts.facebook,
                "instagram": contacts.instagram,
                "twitter": contacts.twitter,
                "linkedin": contacts.linkedin,
                "youtube": contacts.youtube,
                "tiktok": contacts.tiktok,
                "url": url,
                "emails_found": len(contacts.emails),
                "phones_found": len(contacts.phones),
                "pages_checked": len(contacts.pages_crawled),
                "all_emails": contacts.emails[:10],
                "all_phones": contacts.phones[:10],
                "message": f"Found {len(contacts.emails)} email(s), {len(contacts.phones)} phone(s)" if contacts.emails or contacts.phones else "No contact info found",
                "method": "playwright"
            }
        except Exception as e:
            playwright_error = str(e)
            logger.warning(f"Playwright failed for {url}: {e}, falling back to httpx")
    
    # Fallback to httpx-based scraping
    try:
        result = await _crawl_url_with_httpx(url)
        result["method"] = "httpx_fallback"
        if playwright_error:
            result["playwright_error"] = playwright_error
        return result
    except Exception as e2:
        raise HTTPException(status_code=500, detail=f"Crawl failed. Playwright: {playwright_error}. Httpx: {str(e2)}")


async def _crawl_url_with_httpx(url: str) -> dict:
    from app.services.scraping.website_scraper import _scrape_with_httpx_async, _ddg_email_search
    from urllib.parse import urlparse
    import asyncio
    import concurrent.futures
    
    contacts_data = {
        "email": None, "phone": None, "facebook": None, "instagram": None,
        "twitter": None, "linkedin": None, "url": url,
        "emails_found": 0, "phones_found": 0, "pages_checked": 0,
        "all_emails": [], "all_phones": [],
        "message": "No contacts found", "method": "httpx_fallback"
    }

    try:
        contacts = await _scrape_with_httpx_async(url, timeout=10)
        contacts_data.update({
            "email": contacts.best_email,
            "phone": contacts.best_phone,
            "facebook": contacts.facebook,
            "instagram": contacts.instagram,
            "twitter": contacts.twitter,
            "linkedin": contacts.linkedin,
            "emails_found": len(contacts.emails),
            "phones_found": len(contacts.phones),
            "pages_checked": len(contacts.pages_crawled),
            "all_emails": contacts.emails[:5],
            "all_phones": contacts.phones[:5],
            "message": f"Found {len(contacts.emails)} email(s), {len(contacts.phones)} phone(s)"
        })
    except Exception as e:
        contacts_data["message"] = str(e)

    # Fast DDG Search Fallback if no email found (bypasses Playwright/Cloudflare)
    if not contacts_data["email"]:
        parsed = urlparse(url)
        domain = parsed.netloc.lstrip('www.')
        if domain:
            try:
                loop = asyncio.get_event_loop()
                with concurrent.futures.ThreadPoolExecutor() as ex:
                    found = await loop.run_in_executor(ex, _ddg_email_search, domain)
                if found:
                    contacts_data["email"] = found
                    contacts_data["emails_found"] = 1
                    contacts_data["all_emails"] = [found]
                    contacts_data["message"] = "Found 1 email(s) via search fallback"
            except Exception:
                pass

    return contacts_data



@router.post("/extract")
async def extract_business_data(data: dict):
    """
    Extract business data from a website URL using AI.
    """
    from app.services.agents.business_Data_Extractor_Agent import BusinessDataExtractorAgent
    
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    try:
        agent = BusinessDataExtractorAgent()
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            lambda: agent.extract_business_data(url)
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/discover-websites")
async def discover_websites(data: dict):
    """
    Discover official websites for businesses using DuckDuckGo search.
    Useful for OSM records that don't include website URLs.
    """
    from app.services.osm.website_discovery import discover_websites_bulk

    businesses = data.get("businesses", [])
    city = data.get("city", "")
    country = data.get("country", "")

    if not businesses:
        raise HTTPException(status_code=400, detail="No businesses provided")

    without_website = [b for b in businesses if not b.get("website") and b.get("business_name")]
    if not without_website:
        return {
            "businesses": businesses,
            "discovered_count": 0,
            "message": "All businesses already have websites",
        }

    loop = asyncio.get_event_loop()
    updated, discovered_count = await loop.run_in_executor(
        executor,
        lambda: discover_websites_bulk(businesses, city, country, verify=True),
    )

    return {
        "businesses": updated,
        "discovered_count": discovered_count,
        "total_searched": len(without_website),
        "message": f"Discovered {discovered_count} out of {len(without_website)} websites",
    }


@router.post("/discover-website-single")
async def discover_website_single(data: dict):
    """
    Discover the website for a single business via DuckDuckGo search,
    then immediately scrape it for email, phone, and social media.
    Uses httpx-only scraping (no Playwright) for speed.
    Used for progressive row-by-row discovery from the UI.
    """
    from app.services.osm.website_discovery import discover_website
    from app.services.scraping.website_scraper import _scrape_with_httpx_async

    name = data.get("business_name", "")
    city = data.get("city", "")
    country = data.get("country", "")

    if not name:
        raise HTTPException(status_code=400, detail="business_name is required")

    # Discover website URL via DuckDuckGo (with timeout guard)
    try:
        loop = asyncio.get_event_loop()
        url = await asyncio.wait_for(
            loop.run_in_executor(
                executor,
                lambda: discover_website(name, city, country, verify=True),
            ),
            timeout=30  # 30 second max for DuckDuckGo search
        )
    except asyncio.TimeoutError:
        url = None

    contacts = {}
    if url:
        try:
            # Use httpx-only scraping (fast, no Playwright) — 8s timeout
            scraped = await asyncio.wait_for(
                _scrape_with_httpx_async(url, timeout=8),
                timeout=15  # hard cap at 15s for the scrape
            )
            contacts = {
                "email": scraped.best_email,
                "phone": scraped.best_phone,
                "all_emails_found": scraped.emails,
                "all_phones_found": scraped.phones,
                "facebook": scraped.facebook,
                "instagram": scraped.instagram,
                "twitter": scraped.twitter,
                "linkedin": scraped.linkedin,
                "youtube": scraped.youtube,
                "tiktok": scraped.tiktok,
            }
        except Exception:
            pass

    return {
        "business_name": name,
        "website": url,
        "discovered": url is not None,
        **contacts,
    }
