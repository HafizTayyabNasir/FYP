"""
Businesses Endpoint - Manage discovered businesses (per-user, DB-backed)
"""
import asyncio
import uuid
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.models.saved_business import SavedBusiness

router = APIRouter()

executor = ThreadPoolExecutor(max_workers=4)


def _biz_to_dict(b: SavedBusiness) -> dict:
    return {
        "id": str(b.id),
        "business_name": b.business_name,
        "website": b.website,
        "email": b.email,
        "phone": b.phone,
        "address": b.address,
        "city": b.city,
        "country": b.country,
        "category": b.category,
        "notes": b.notes,
        "facebook": b.facebook,
        "instagram": b.instagram,
        "lat": b.lat,
        "lon": b.lon,
        "audit_completed": b.audit_completed,
        "overall_score": b.overall_score,
        "seo_score": b.seo_score,
        "ssl_score": b.ssl_score,
        "load_speed_score": b.load_speed_score,
        "responsiveness_score": b.responsiveness_score,
        "social_links_score": b.social_links_score,
        "image_alt_score": b.image_alt_score,
        "audit_summary": b.audit_summary,
        "audit_recommendations": b.audit_recommendations,
        "created_at": b.created_at.isoformat() if b.created_at else None,
    }


@router.get("")
async def list_businesses(
    page: int = Query(1, ge=1),
    per_page: int = Query(1000, ge=1, le=10000),
    has_email: Optional[bool] = None,
    has_audit: Optional[bool] = None,
    industry: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List all saved businesses for the current user.
    """
    query = select(SavedBusiness).where(SavedBusiness.user_id == current_user.id)

    if has_email is not None:
        if has_email:
            query = query.where(SavedBusiness.email.isnot(None))
        else:
            query = query.where(SavedBusiness.email.is_(None))

    if has_audit is not None:
        query = query.where(SavedBusiness.audit_completed == has_audit)

    if industry:
        query = query.where(SavedBusiness.category.ilike(f"%{industry}%"))

    query = query.order_by(SavedBusiness.created_at.desc())

    result = await db.execute(query)
    all_businesses = result.scalars().all()
    total = len(all_businesses)

    start = (page - 1) * per_page
    end = start + per_page
    paginated = all_businesses[start:end]

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "businesses": [_biz_to_dict(b) for b in paginated],
    }


@router.get("/stats/summary")
async def get_business_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(SavedBusiness).where(SavedBusiness.user_id == current_user.id)
    )
    businesses = result.scalars().all()

    total = len(businesses)
    with_email = sum(1 for b in businesses if b.email)
    with_website = sum(1 for b in businesses if b.website)
    audited = sum(1 for b in businesses if b.audit_completed)
    scores = [b.overall_score for b in businesses if b.audit_completed and b.overall_score]
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
            "poor": sum(1 for s in scores if s < 2),
        },
    }


@router.get("/{business_id}")
async def get_business(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(SavedBusiness).where(
            SavedBusiness.id == uuid.UUID(business_id),
            SavedBusiness.user_id == current_user.id,
        )
    )
    business = result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return _biz_to_dict(business)


@router.post("/save")
async def save_businesses(
    businesses: List[dict],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Save a list of businesses (from OSM search) for the current user.
    """
    added = 0
    for biz in businesses:
        new_biz = SavedBusiness(
            user_id=current_user.id,
            business_name=biz.get("business_name", "") or biz.get("name", "") or biz.get("display_name", ""),
            website=biz.get("website"),
            email=biz.get("email"),
            phone=biz.get("phone"),
            address=biz.get("address"),
            city=biz.get("city"),
            country=biz.get("country"),
            category=biz.get("category"),
            notes=biz.get("notes"),
            lat=biz.get("lat"),
            lon=biz.get("lon"),
        )
        db.add(new_biz)
        added += 1

    await db.commit()

    result = await db.execute(
        select(SavedBusiness).where(SavedBusiness.user_id == current_user.id)
    )
    total = len(result.scalars().all())

    return {"message": f"Saved {added} new businesses", "total": total}


@router.post("")
async def create_business(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Save a single business for the current user.
    """
    new_biz = SavedBusiness(
        user_id=current_user.id,
        business_name=data.get("business_name", "") or data.get("name", "") or data.get("display_name", ""),
        website=data.get("website"),
        email=data.get("email"),
        phone=data.get("phone"),
        address=data.get("address"),
        city=data.get("city"),
        country=data.get("country"),
        category=data.get("category"),
        notes=data.get("notes"),
        lat=data.get("lat"),
        lon=data.get("lon"),
    )
    db.add(new_biz)
    await db.commit()
    await db.refresh(new_biz)
    return _biz_to_dict(new_biz)


@router.put("/{business_id}")
async def update_business(
    business_id: str,
    updates: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(SavedBusiness).where(
            SavedBusiness.id == uuid.UUID(business_id),
            SavedBusiness.user_id == current_user.id,
        )
    )
    business = result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    allowed = {
        "business_name", "website", "email", "phone", "address", "city", "country",
        "category", "notes", "facebook", "instagram", "lat", "lon",
        "audit_completed", "overall_score", "seo_score", "ssl_score",
        "load_speed_score", "responsiveness_score", "social_links_score",
        "image_alt_score", "audit_summary", "audit_recommendations",
    }
    for key, value in updates.items():
        if key in allowed:
            setattr(business, key, value)

    await db.commit()
    await db.refresh(business)
    return _biz_to_dict(business)


@router.delete("/{business_id}")
async def delete_business(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(SavedBusiness).where(
            SavedBusiness.id == uuid.UUID(business_id),
            SavedBusiness.user_id == current_user.id,
        )
    )
    business = result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    await db.delete(business)
    await db.commit()
    return {"message": "Business deleted"}


@router.post("/{business_id}/audit")
async def run_audit_for_business(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from app.services.website_audit.orchestrator import WebsiteAuditOrchestrator

    result = await db.execute(
        select(SavedBusiness).where(
            SavedBusiness.id == uuid.UUID(business_id),
            SavedBusiness.user_id == current_user.id,
        )
    )
    business = result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    if not business.website:
        raise HTTPException(status_code=400, detail="Business has no website")

    try:
        orchestrator = WebsiteAuditOrchestrator()
        loop = asyncio.get_event_loop()
        audit_result = await loop.run_in_executor(
            executor, lambda: orchestrator.run_audit(business.website)
        )

        business.audit_completed = True
        business.overall_score = audit_result.overall_score
        business.seo_score = audit_result.seo.score if audit_result.seo else 0
        business.ssl_score = audit_result.ssl.score if audit_result.ssl else 0
        business.load_speed_score = audit_result.load_speed.score if audit_result.load_speed else 0
        business.responsiveness_score = audit_result.responsiveness.score if audit_result.responsiveness else 0
        business.social_links_score = audit_result.social_links.score if audit_result.social_links else 0
        business.image_alt_score = audit_result.image_alt.score if audit_result.image_alt else 0
        business.audit_summary = audit_result.summary
        business.audit_recommendations = str(audit_result.recommendations)

        await db.commit()
        await db.refresh(business)

        return {
            "business_id": business_id,
            "audit_completed": True,
            "overall_score": audit_result.overall_score,
            "scores": {
                "seo": audit_result.seo.score if audit_result.seo else 0,
                "ssl": audit_result.ssl.score if audit_result.ssl else 0,
                "load_speed": audit_result.load_speed.score if audit_result.load_speed else 0,
                "responsiveness": audit_result.responsiveness.score if audit_result.responsiveness else 0,
                "social_links": audit_result.social_links.score if audit_result.social_links else 0,
                "image_alt": audit_result.image_alt.score if audit_result.image_alt else 0,
            },
            "summary": audit_result.summary,
            "recommendations": audit_result.recommendations,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{business_id}/crawl")
async def crawl_business_website(
    business_id: str,
    use_playwright: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(SavedBusiness).where(
            SavedBusiness.id == uuid.UUID(business_id),
            SavedBusiness.user_id == current_user.id,
        )
    )
    business = result.scalars().first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    if not business.website:
        raise HTTPException(status_code=400, detail="Business has no website")

    url = business.website
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    try:
        from app.services.scraping import scrape_website_for_contacts

        contacts = await scrape_website_for_contacts(url, timeout=30000, max_pages=15)

        if contacts.best_email:
            business.email = contacts.best_email
        if contacts.best_phone and not business.phone:
            business.phone = contacts.best_phone
        if contacts.facebook and not business.facebook:
            business.facebook = contacts.facebook
        if contacts.instagram and not business.instagram:
            business.instagram = contacts.instagram

        await db.commit()
        await db.refresh(business)

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
            "message": f"Found {len(contacts.emails)} emails" if contacts.emails else "No email found",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawl failed: {str(e)}")


@router.post("/crawl-url")
async def crawl_website_url(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    import logging
    import concurrent.futures
    from urllib.parse import urlparse
    logger = logging.getLogger(__name__)

    url = data.get("url")
    use_playwright = data.get("use_playwright", True)

    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    if use_playwright:
        try:
            from app.services.scraping import scrape_website_for_contacts
            contacts = await scrape_website_for_contacts(url, timeout=30000, max_pages=15)
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
                "message": f"Found {len(contacts.emails)} email(s)" if contacts.emails else "No contact info found",
                "method": "playwright",
            }
        except Exception as e:
            logger.warning(f"Playwright failed for {url}: {e}")

    # httpx fallback
    from app.services.scraping.website_scraper import _scrape_with_httpx_async, _ddg_email_search
    from urllib.parse import urlparse

    contacts_data = {
        "email": None, "phone": None, "facebook": None, "instagram": None,
        "twitter": None, "linkedin": None, "url": url,
        "emails_found": 0, "phones_found": 0, "pages_checked": 0,
        "all_emails": [], "all_phones": [],
        "message": "No contacts found", "method": "httpx_fallback",
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
            "message": f"Found {len(contacts.emails)} email(s)",
        })
    except Exception as e:
        contacts_data["message"] = str(e)

    if not contacts_data["email"]:
        parsed = urlparse(url)
        domain = parsed.netloc.lstrip("www.")
        if domain:
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as ex:
                found = await loop.run_in_executor(ex, _ddg_email_search, domain)
            if found:
                contacts_data["email"] = found
                contacts_data["emails_found"] = 1
                contacts_data["all_emails"] = [found]
                contacts_data["message"] = "Found 1 email via search fallback"

    return contacts_data


@router.post("/extract")
async def extract_business_data(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from app.services.agents.business_Data_Extractor_Agent import BusinessDataExtractorAgent

    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        agent = BusinessDataExtractorAgent()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, lambda: agent.extract_business_data(url))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/discover-websites")
async def discover_websites(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from app.services.osm.website_discovery import discover_websites_bulk

    businesses = data.get("businesses", [])
    city = data.get("city", "")
    country = data.get("country", "")

    if not businesses:
        raise HTTPException(status_code=400, detail="No businesses provided")

    without_website = [b for b in businesses if not b.get("website") and b.get("business_name")]
    if not without_website:
        return {"businesses": businesses, "discovered_count": 0, "message": "All have websites"}

    loop = asyncio.get_event_loop()
    updated, discovered_count = await loop.run_in_executor(
        executor, lambda: discover_websites_bulk(businesses, city, country, verify=True)
    )
    return {
        "businesses": updated,
        "discovered_count": discovered_count,
        "total_searched": len(without_website),
        "message": f"Discovered {discovered_count} out of {len(without_website)} websites",
    }


@router.post("/discover-website-single")
async def discover_website_single(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from app.services.osm.website_discovery import discover_website
    from app.services.scraping.website_scraper import _scrape_with_httpx_async

    name = data.get("business_name", "")
    city = data.get("city", "")
    country = data.get("country", "")

    if not name:
        raise HTTPException(status_code=400, detail="business_name is required")

    try:
        loop = asyncio.get_event_loop()
        url = await asyncio.wait_for(
            loop.run_in_executor(executor, lambda: discover_website(name, city, country, verify=True)),
            timeout=30,
        )
    except asyncio.TimeoutError:
        url = None

    contacts = {}
    if url:
        try:
            scraped = await asyncio.wait_for(
                _scrape_with_httpx_async(url, timeout=8), timeout=15
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
