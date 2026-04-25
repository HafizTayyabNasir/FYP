"""
Website Scraper - extracts emails, phone numbers, and social media links.
Strategy: httpx (fast, no browser) first; Playwright fallback for JS-heavy sites.
"""
import asyncio
import json
import re
from typing import List, Optional, Set
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScrapedContacts:
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    youtube: Optional[str] = None
    tiktok: Optional[str] = None
    pages_crawled: List[str] = field(default_factory=list)
    best_email: Optional[str] = None
    best_phone: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "emails": self.emails,
            "phones": self.phones,
            "facebook": self.facebook,
            "instagram": self.instagram,
            "twitter": self.twitter,
            "linkedin": self.linkedin,
            "youtube": self.youtube,
            "tiktok": self.tiktok,
            "pages_crawled": self.pages_crawled,
            "best_email": self.best_email,
            "best_phone": self.best_phone,
        }


JUNK_EMAIL_DOMAINS = {
    "sentry.io", "sentry.wixpress.com", "example.com", "domain.com",
    "yourdomain.com", "test.com", "email.com", "mail.com", "sample.com"
}

JUNK_EMAIL_PATTERNS = [
    r"@.*\.png", r"@.*\.jpg", r"@.*\.gif", r"@.*\.svg", r"@.*\.webp",
    r"noreply@", r"no-reply@", r"donotreply@", r"mailer-daemon@",
    r"example@", r"test@", r"admin@admin", r"user@user", r"sample@",
    r"support@wix", r"@wixpress", r"@sentry", r"@cloudflare",
]

# Only check the 3 most valuable pages — homepage, contact, about
CONTACT_PAGES = ["/contact", "/contact-us", "/about", "/about-us"]

SOCIAL_PATTERNS = {
    "facebook": r'https?://(?:www\.)?(?:facebook\.com|fb\.com)/(?!(?:tr|plugins|share|login|dialog|sharer|photo|video|groups|events|pages/create)(?:/|$))([a-zA-Z0-9._%-]+)/?(?:\?[^"\'<>\s]*)?',
    "instagram": r'https?://(?:www\.)?instagram\.com/(?!(?:p|reel|explore|accounts|tv|stories)(?:/|$))([a-zA-Z0-9._]+)/?(?:\?[^"\'<>\s]*)?',
    "twitter": r'https?://(?:www\.)?(?:twitter\.com|x\.com)/(?!(?:intent|share|home|search|login|i/)(?:/|$))([a-zA-Z0-9_]+)/?(?:\?[^"\'<>\s]*)?',
    "linkedin": r'https?://(?:www\.)?linkedin\.com/((?:company|in)/[a-zA-Z0-9_-]+)/?',
    "youtube": r'https?://(?:www\.)?youtube\.com/(?:c/|channel/|@)([a-zA-Z0-9_-]+)/?',
    "tiktok": r'https?://(?:www\.)?tiktok\.com/@([a-zA-Z0-9._-]+)/?',
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def _is_js_heavy(html: str) -> bool:
    """Heuristic: page is mostly a JS bundle with little real HTML content."""
    text_content = re.sub(r'<[^>]+>', '', html)
    text_content = text_content.strip()
    if len(text_content) < 200 and ('<div id="root"' in html or '<div id="app"' in html):
        return True
    return False


def _extract_emails(content: str) -> Set[str]:
    emails: Set[str] = set()

    patterns = [
        r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
        r'mailto:([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
        r'data-[a-z-]*email[a-z-]*=["\']([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
        r'([a-zA-Z0-9._%+\-]+)%40([a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
    ]

    for i, pattern in enumerate(patterns):
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if i == 3:  # URL-encoded: tuple (local, domain)
                email = f"{match[0]}@{match[1]}"
            else:
                email = match if isinstance(match, str) else match[0]
            email = email.strip().strip('"').strip("'").lower().replace('mailto:', '')
            if _is_valid_email(email):
                emails.add(email)

    # JSON-LD structured data
    for block in re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', content, re.IGNORECASE | re.DOTALL):
        try:
            data = json.loads(block)
            emails.update(_emails_from_json(data))
        except Exception:
            for m in re.findall(r'"email"\s*:\s*"([^"]+@[^"]+)"', block):
                if _is_valid_email(m):
                    emails.add(m.lower())

    return emails


def _emails_from_json(data, depth=0) -> Set[str]:
    emails: Set[str] = set()
    if depth > 8:
        return emails
    if isinstance(data, dict):
        for k, v in data.items():
            if k.lower() in ('email', 'contactemail', 'businessemail', 'mail') and isinstance(v, str) and '@' in v:
                e = v.replace('mailto:', '').strip().lower()
                if _is_valid_email(e):
                    emails.add(e)
            elif isinstance(v, (dict, list)):
                emails.update(_emails_from_json(v, depth + 1))
    elif isinstance(data, list):
        for item in data:
            emails.update(_emails_from_json(item, depth + 1))
    return emails


def _is_valid_email(email: str) -> bool:
    if not email or '@' not in email or '.' not in email.split('@')[-1]:
        return False
    domain = email.split('@')[-1]
    if domain in JUNK_EMAIL_DOMAINS:
        return False
    for pattern in JUNK_EMAIL_PATTERNS:
        if re.search(pattern, email, re.IGNORECASE):
            return False
    return 6 <= len(email) <= 100


def _extract_phones(content: str) -> Set[str]:
    phones: Set[str] = set()
    patterns = [
        r'href=["\']tel:([^"\']+)',
        r'"(?:telephone|phone)"\s*:\s*"([^"]+)"',
        r'\+\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}',
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    ]
    for pattern in patterns:
        for match in re.findall(pattern, content):
            cleaned = re.sub(r'[^\d+]', '', match)
            if len(cleaned) >= 10:
                phones.add(cleaned)
    return phones


def _extract_social(content: str, contacts: ScrapedContacts):
    for platform, pattern in SOCIAL_PATTERNS.items():
        if getattr(contacts, platform):
            continue
        match = re.search(pattern, content, re.IGNORECASE)
        if not match:
            continue
        slug = match.group(1)
        if platform == "facebook":
            url = f"https://www.facebook.com/{slug}"
        elif platform == "instagram":
            url = f"https://www.instagram.com/{slug}"
        elif platform == "twitter":
            url = f"https://twitter.com/{slug}"
        elif platform == "linkedin":
            url = f"https://www.linkedin.com/{slug}"
        elif platform == "youtube":
            url = f"https://www.youtube.com/{slug}"
        elif platform == "tiktok":
            url = f"https://www.tiktok.com/@{slug}"
        else:
            continue
        setattr(contacts, platform, url)


def _pick_best_email(emails: List[str]) -> Optional[str]:
    if not emails:
        return None
    priority = ["info@", "contact@", "hello@", "reservations@", "booking@",
                "enquiries@", "admin@", "support@", "sales@", "office@"]
    for prefix in priority:
        for e in emails:
            if e.startswith(prefix):
                return e
    for e in emails:
        if not any(s in e for s in ["@gmail", "@yahoo", "@hotmail", "@outlook"]):
            return e
    return emails[0]


def _pick_best_phone(phones: List[str]) -> Optional[str]:
    if not phones:
        return None
    for p in phones:
        if len(p) >= 11 and (p.startswith('+') or p.startswith('1')):
            return p
    return phones[0]


def _scrape_with_httpx(base_url: str, timeout: int = 8) -> ScrapedContacts:
    """Fast scraper using httpx — no browser startup cost."""
    import httpx

    if not base_url.startswith(("http://", "https://")):
        base_url = f"https://{base_url}"

    parsed = urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    contacts = ScrapedContacts()
    all_emails: Set[str] = set()
    all_phones: Set[str] = set()

    pages = [base_url] + [origin.rstrip('/') + p for p in CONTACT_PAGES]

    with httpx.Client(headers=HEADERS, timeout=timeout, follow_redirects=True, verify=False) as client:
        js_heavy = False
        for url in pages:
            try:
                r = client.get(url)
                if r.status_code >= 400:
                    continue
                html = r.text
                if url == base_url and _is_js_heavy(html):
                    js_heavy = True
                    break
                all_emails.update(_extract_emails(html))
                all_phones.update(_extract_phones(html))
                _extract_social(html, contacts)
                contacts.pages_crawled.append(url)
                # Stop early if we have everything
                if all_emails and contacts.facebook or contacts.instagram:
                    break
            except Exception as e:
                logger.debug(f"httpx error on {url}: {e}")
                continue

    if js_heavy:
        raise ValueError("JS-heavy site — needs Playwright")

    contacts.emails = list(all_emails)
    contacts.phones = list(all_phones)
    contacts.best_email = _pick_best_email(contacts.emails)
    contacts.best_phone = _pick_best_phone(contacts.phones)
    return contacts


class WebsiteScraperSync:
    """Playwright-based scraper — fallback for JS-rendered sites."""

    def __init__(self, timeout: int = 15000, max_pages: int = 3):
        self.timeout = timeout
        self.max_pages = max_pages

    def scrape(self, url: str) -> ScrapedContacts:
        from playwright.sync_api import sync_playwright

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        contacts = ScrapedContacts()
        all_emails: Set[str] = set()
        all_phones: Set[str] = set()

        pages = [url] + [base_url.rstrip('/') + p for p in CONTACT_PAGES]

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
            try:
                context = browser.new_context(
                    user_agent=HEADERS["User-Agent"],
                    viewport={"width": 1920, "height": 1080},
                )
                pw_page = context.new_page()

                for page_url in pages[:self.max_pages]:
                    try:
                        resp = pw_page.goto(page_url, wait_until="domcontentloaded", timeout=self.timeout)
                        if not resp or resp.status >= 400:
                            continue
                        html = pw_page.content()
                        all_emails.update(_extract_emails(html))
                        all_phones.update(_extract_phones(html))
                        _extract_social(html, contacts)
                        contacts.pages_crawled.append(page_url)
                        if all_emails and (contacts.facebook or contacts.instagram):
                            break
                    except Exception as e:
                        logger.debug(f"Playwright error on {page_url}: {e}")
                        continue

                context.close()
            finally:
                browser.close()

        contacts.emails = list(all_emails)
        contacts.phones = list(all_phones)
        contacts.best_email = _pick_best_email(contacts.emails)
        contacts.best_phone = _pick_best_phone(contacts.phones)
        return contacts


def scrape_website_sync(url: str, timeout: int = 15000, max_pages: int = 3) -> ScrapedContacts:
    """
    Scrape a website for contacts.
    Tries fast httpx first; falls back to Playwright for JS-heavy sites.
    """
    try:
        return _scrape_with_httpx(url, timeout=8)
    except ValueError:
        # JS-heavy site — use Playwright
        scraper = WebsiteScraperSync(timeout=timeout, max_pages=max_pages)
        return scraper.scrape(url)
    except Exception as e:
        logger.debug(f"httpx scrape failed ({e}), falling back to Playwright")
        scraper = WebsiteScraperSync(timeout=timeout, max_pages=max_pages)
        return scraper.scrape(url)


async def scrape_website_for_contacts(url: str, timeout: int = 15000, max_pages: int = 3) -> ScrapedContacts:
    import concurrent.futures
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, lambda: scrape_website_sync(url, timeout, max_pages))


# Alias for backward compatibility
WebsiteScraper = WebsiteScraperSync
