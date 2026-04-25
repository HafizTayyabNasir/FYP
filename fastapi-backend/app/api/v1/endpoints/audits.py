"""
Website Audit Endpoints
"""
import asyncio
from typing import List
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.schemas.audit import (
    AuditRequest,
    WebsiteAuditResponse,
    BulkAuditRequest,
    BulkAuditResponse
)
from app.services.website_audit.orchestrator import WebsiteAuditOrchestrator

router = APIRouter()

# Thread pool for running sync audit operations
executor = ThreadPoolExecutor(max_workers=4)


@router.post("/run", response_model=WebsiteAuditResponse)
async def run_audit(request: AuditRequest):
    """
    Run a complete website audit.
    
    Audits the following aspects:
    - **SEO**: Meta tags, Open Graph, Twitter Cards, canonical links
    - **SSL**: HTTPS, certificate validity, HSTS, redirects
    - **Load Speed**: Page load time, TTFB, DNS lookup
    - **Responsiveness**: Mobile-friendly, viewport meta, overflow
    - **Social Links**: Social media presence and accessibility
    - **Image Alt Tags**: Accessibility and SEO compliance
    """
    try:
        orchestrator = WebsiteAuditOrchestrator()
        
        # Run the synchronous audit in a thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            lambda: orchestrator.run_audit(
                website_url=request.website_url,
                include_seo=request.include_seo,
                include_ssl=request.include_ssl,
                include_speed=request.include_speed,
                include_responsiveness=request.include_responsiveness,
                include_social_links=request.include_social_links,
                include_image_alt=request.include_image_alt
            )
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk", response_model=BulkAuditResponse)
async def run_bulk_audit(request: BulkAuditRequest):
    """
    Run audits on multiple websites.
    Maximum 50 websites per request.
    """
    try:
        orchestrator = WebsiteAuditOrchestrator()
        results = []
        errors = []
        
        loop = asyncio.get_event_loop()
        
        for website in request.websites:
            try:
                result = await loop.run_in_executor(
                    executor,
                    lambda w=website: orchestrator.run_audit(
                        website_url=w,
                        include_seo=request.include_seo,
                        include_ssl=request.include_ssl,
                        include_speed=request.include_speed,
                        include_responsiveness=request.include_responsiveness,
                        include_social_links=request.include_social_links,
                        include_image_alt=request.include_image_alt
                    )
                )
                results.append(result)
            except Exception as e:
                errors.append({"website": website, "error": str(e)})
        
        return BulkAuditResponse(
            total_requested=len(request.websites),
            total_completed=len(results),
            total_failed=len(errors),
            results=results,
            errors=errors
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quick/{url:path}")
async def quick_audit(url: str):
    """
    Run a quick audit on a single URL.
    Returns simplified results suitable for display.
    """
    from datetime import datetime
    
    try:
        # Decode URL if needed
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        orchestrator = WebsiteAuditOrchestrator()
        
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            lambda: orchestrator.run_audit(
                website_url=url,
                include_seo=True,
                include_ssl=True,
                include_speed=True,
                include_responsiveness=True,
                include_social_links=True,
                include_image_alt=True
            )
        )
        
        # Build response matching template expectations
        seo = result.seo
        ssl = result.ssl
        speed = result.load_speed
        resp = result.responsiveness
        social = result.social_links
        images = result.image_alt
        
        # Get SEO metadata dict if available
        seo_meta = seo.metadata if seo and seo.metadata else {}
        seo_flaws = seo.flaws if seo else []
        seo_flaws_str = str(seo_flaws).lower()
        
        # Determine SEO field presence from metadata or flaws
        has_title = bool(seo_meta.get("title")) if seo_meta else ("missing title" not in seo_flaws_str)
        has_description = bool(seo_meta.get("description")) if seo_meta else ("missing meta description" not in seo_flaws_str)
        has_h1 = bool(seo_meta.get("h1")) if seo_meta else ("missing h1" not in seo_flaws_str)
        has_canonical = bool(seo_meta.get("canonical")) if seo_meta else ("missing canonical" not in seo_flaws_str)
        
        return {
            "url": result.website_url,
            "website_url": result.website_url,
            "timestamp": datetime.now().isoformat(),
            "overall_score": result.overall_score,
            "summary": result.summary,
            "recommendations": result.recommendations,
            
            # SEO Metadata - template expects seo_metadata
            "seo_metadata": {
                "score": seo.score if seo else 0,
                "flaws": seo_flaws,
                "has_title": has_title,
                "has_meta_description": has_description,
                "has_h1": has_h1,
                "has_canonical": has_canonical,
            },
            
            # SSL Certificate - template expects ssl_certificate
            "ssl_certificate": {
                "score": ssl.score if ssl else 0,
                "flaws": ssl.flaws if ssl else [],
                "is_valid": ssl.certificate_valid if ssl else False,
                "days_until_expiry": ssl.days_until_expiry if ssl else None,
                "issuer": "Valid SSL" if ssl and ssl.certificate_valid else "N/A",
                "https_accessible": ssl.https_accessible if ssl else False,
                "hsts_enabled": ssl.hsts_enabled if ssl else False,
            },
            
            # Load Speed - template expects load_speed
            "load_speed": {
                "score": speed.score if speed else 0,
                "flaws": speed.flaws if speed else [],
                "load_time_ms": round(speed.load_time_ms, 2) if speed and speed.load_time_ms else 0,
                "load_time_seconds": round(speed.load_time_ms / 1000, 2) if speed and speed.load_time_ms else 0,
                "dom_content_loaded_ms": round(speed.dom_content_loaded_ms, 2) if speed and speed.dom_content_loaded_ms else 0,
                "dom_content_loaded": round(speed.dom_content_loaded_ms / 1000, 2) if speed and speed.dom_content_loaded_ms else 0,
                "page_size": speed.timing_details.get("page_size", 0) if speed and speed.timing_details else 0,
                "total_size_bytes": speed.timing_details.get("page_size", 0) if speed and speed.timing_details else 0,
            },
            
            # Responsiveness - template expects responsiveness
            "responsiveness": {
                "score": resp.score if resp else 0,
                "flaws": resp.flaws if resp else [],
                "mobile_friendly": resp.mobile_friendly if resp else False,
                "viewport_meta": resp.viewport_meta_present if resp else False,
                "media_queries": "media query" not in str(resp.flaws).lower() if resp else False,
            },
            
            # Social Links - template expects social_links
            "social_links": {
                "score": social.score if social else 0,
                "flaws": social.flaws if social else [],
                "total_links_found": social.links_found if social else 0,
                "links_accessible": social.links_accessible if social else 0,
                "platforms": social.social_platforms if social else [],
            },
            
            # Image Alt Tags - template expects image_alt_tags
            "image_alt_tags": {
                "score": images.score if images else 0,
                "flaws": images.flaws if images else [],
                "total_images": images.total_images if images else 0,
                "with_alt_text": (images.total_images - images.images_with_issues) if images else 0,
                "missing_alt": images.images_with_issues if images else 0,
                "coverage": round((images.total_images - images.images_with_issues) / images.total_images * 100) if images and images.total_images > 0 else 0,
            },
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
