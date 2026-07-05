import re

with open('fastapi-backend/app/api/v1/endpoints/businesses.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace _crawl_with_httpx
new_crawl_with_httpx = """async def _crawl_with_httpx(url: str, businesses: list, business_idx: int) -> dict:
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
"""

content = re.sub(r'async def _crawl_with_httpx\(url: str, businesses: list, business_idx: int\) -> dict:.*?return \{(.*?)\}', new_crawl_with_httpx, content, flags=re.DOTALL)

# Replace _crawl_url_with_httpx
new_crawl_url_with_httpx = """async def _crawl_url_with_httpx(url: str) -> dict:
    from app.services.scraping.website_scraper import _scrape_with_httpx_async
    try:
        contacts = await _scrape_with_httpx_async(url, timeout=10)
        return {
            "email": contacts.best_email,
            "phone": contacts.best_phone,
            "facebook": contacts.facebook,
            "instagram": contacts.instagram,
            "twitter": contacts.twitter,
            "linkedin": contacts.linkedin,
            "url": url,
            "emails_found": len(contacts.emails),
            "phones_found": len(contacts.phones),
            "pages_checked": len(contacts.pages_crawled),
            "all_emails": contacts.emails[:5],
            "all_phones": contacts.phones[:5],
            "message": f"Found {len(contacts.emails)} email(s), {len(contacts.phones)} phone(s)",
            "method": "httpx_fallback"
        }
    except Exception as e:
        return {"email": None, "url": url, "message": str(e), "emails_found": 0}
"""

content = re.sub(r'async def _crawl_url_with_httpx\(url: str\) -> dict:.*?return \{(.*?)\}', new_crawl_url_with_httpx, content, flags=re.DOTALL)

with open('fastapi-backend/app/api/v1/endpoints/businesses.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated successfully")
