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
    "yourdomain.com", "test.com", "email.com", "mail.com", "sample.com",
    "hub.biz", "form.google.com", "docs.google.com", "sheets.google.com",
    "drive.google.com", "calendar.google.com",
}

JUNK_EMAIL_PATTERNS = [
    r"@.*\.png", r"@.*\.jpg", r"@.*\.gif", r"@.*\.svg", r"@.*\.webp",
    r"@.*\.js", r"@.*\.css", r"@.*\.jsx", r"@.*\.ts", r"@.*\.tsx",
    r"noreply@", r"no-reply@", r"donotreply@", r"mailer-daemon@",
    r"example@", r"test@", r"admin@admin", r"user@user", r"sample@",
    r"support@wix", r"@wixpress\.com", r"@sentry\.io", r"@cloudflareinsights\.com",
]

JUNK_EMAIL_PARTS = {
    "body", "container", "css", "hover", "icon", "icons", "image", "img",
    "ion", "ions", "ionids", "loc", "many", "mut", "script", "sprite",
    "src", "str", "style", "this", "write",
}

# All common contact/about page URL variations
CONTACT_PAGES = [
    "/contact", "/contact-us", "/contactus", "/contact_us", "/contact%20us",
    "/contact-me", "/contacts", "/contact-info", "/contact-information",
    "/get-in-touch", "/getintouch", "/reach-us", "/reach-out",
    "/connect", "/connect-with-us", "/find-us", "/visit-us",
    "/about", "/about-us", "/aboutus", "/about_us", "/about%20us",
    "/about-me", "/our-story", "/our-team", "/who-we-are",
    "/location", "/locations", "/our-location", "/store", "/stores",
    "/info", "/information", "/impressum", "/imprint",
]

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


def _decode_html_entities(text: str) -> str:
    """Decode common HTML entities used to obfuscate emails."""
    return (text
        .replace('&#64;', '@').replace('&#x40;', '@').replace('&amp;#64;', '@')
        .replace('&#46;', '.').replace('&#x2e;', '.')
        .replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        .replace('\u0040', '@').replace('\u002e', '.')
    )


def _decode_cf_email(encoded: str) -> str:
    """Decode Cloudflare email obfuscation (/cdn-cgi/l/email-protection#HEX)."""
    try:
        r = int(encoded[:2], 16)
        return ''.join(chr(int(encoded[i:i+2], 16) ^ r) for i in range(2, len(encoded), 2))
    except Exception:
        return ''


def _extract_emails(content: str) -> Set[str]:
    emails: Set[str] = set()

    # Decode HTML entities before scanning
    decoded = _decode_html_entities(content)
    no_scripts = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', decoded, flags=re.IGNORECASE | re.DOTALL)
    text_only = re.sub(r'<[^>]+>', ' ', no_scripts)

    # 1. Explicit email-bearing HTML attributes. Avoid broad raw-HTML scanning
    # because CSS/JS fragments can accidentally look like emails.
    raw_patterns = [
        r'mailto:\s*([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
        r'data-[a-z-]*(?:email|mail|cfemail)[a-z-]*=["\']([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
    ]
    for i, pattern in enumerate(raw_patterns):
        for match in re.findall(pattern, decoded, re.IGNORECASE):
            e = (match if isinstance(match, str) else match[0]).strip().strip('"\'').lower().replace('mailto:', '')
            if _is_valid_email(e):
                emails.add(e)

    # 2. URL-encoded @ (%40)
    for local, domain in re.findall(r'([a-zA-Z0-9._%+\-]+)%40([a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', content, re.IGNORECASE):
        e = f"{local}@{domain}".lower()
        if _is_valid_email(e):
            emails.add(e)

    # 3. Cloudflare email protection — multiple patterns
    # 3a. data-cfemail attribute
    for cf_hex in re.findall(r'data-cfemail=["\']([0-9a-fA-F]+)["\']', content):
        e = _decode_cf_email(cf_hex).lower()
        if _is_valid_email(e):
            emails.add(e)
    # 3b. /cdn-cgi/l/email-protection#HEX in href or anywhere
    for cf_hex in re.findall(r'/cdn-cgi/l/email-protection#([0-9a-fA-F]+)', content):
        e = _decode_cf_email(cf_hex).lower()
        if _is_valid_email(e):
            emails.add(e)
    # 3c. __cf_email__ data attribute (alternate CF pattern)
    for cf_hex in re.findall(r'data-__cf_email__=["\']([0-9a-fA-F]+)["\']', content):
        e = _decode_cf_email(cf_hex).lower()
        if _is_valid_email(e):
            emails.add(e)
    # 3d. CF email link with hex in anchor tag (full tag scan)
    for cf_hex in re.findall(r'<a[^>]+href=["\'][^"\']*/cdn-cgi/l/email-protection#([0-9a-fA-F]+)["\'][^>]*>', content, re.IGNORECASE):
        e = _decode_cf_email(cf_hex).lower()
        if _is_valid_email(e):
            emails.add(e)

    # 4. Obfuscated text: name [at] domain.com / name (at) domain / name AT domain DOT com
    obfuscated = re.findall(
        r'([a-zA-Z0-9._%+\-]+)\s*[\[\({\s]?(?:at|AT|@)\s*[\]\)}\s]?\s*([a-zA-Z0-9.\-]+)\s*[\[\({\s]?(?:dot|DOT|\.)\s*[\]\)}\s]?\s*([a-zA-Z]{2,})',
        decoded
    )
    for local, domain_part, tld in obfuscated:
        e = f"{local}@{domain_part}.{tld}".lower()
        if _is_valid_email(e):
            emails.add(e)

    # 5. Meta tags: <meta name="email" content="...">
    for m in re.findall(r'<meta[^>]+name=["\'](?:email|contact)["\'][^>]+content=["\']([^"\']+)["\']', content, re.IGNORECASE):
        if _is_valid_email(m.lower()):
            emails.add(m.lower())
    for m in re.findall(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\'](?:email|contact)["\']', content, re.IGNORECASE):
        if _is_valid_email(m.lower()):
            emails.add(m.lower())

    # 6. JSON-LD / Schema.org structured data
    for block in re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', content, re.IGNORECASE | re.DOTALL):
        try:
            data = json.loads(block)
            emails.update(_emails_from_json(data))
        except Exception:
            for m in re.findall(r'"email"\s*:\s*"([^"]+@[^"]+)"', block):
                if _is_valid_email(m):
                    emails.add(m.lower())

    # 7. Plain text after stripping tags (catches emails rendered as text nodes)
    for m in re.findall(r'\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b', text_only):
        if _is_valid_email(m.lower()):
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

    email = email.strip().strip('.,;:()[]{}<>"\'').lower()
    
    local_part = email.split('@')[0]
    domain = email.split('@')[-1]
    domain_labels = domain.split('.')
    
    if len(local_part) < 2 or local_part.startswith('.') or local_part.endswith('.'):
        return False

    if '..' in email or '_' in domain or len(domain_labels) < 2:
        return False

    if any(not label or label.startswith('-') or label.endswith('-') for label in domain_labels):
        return False

    if any(re.search(r'\d{3,}[-.]?\d{3,}', label) for label in domain_labels):
        return False

    local_tokens = {token for token in re.split(r'[^a-z0-9]+', local_part) if token}
    domain_tokens = {token for token in re.split(r'[^a-z0-9]+', domain) if token}
    if local_tokens & JUNK_EMAIL_PARTS and domain_tokens & JUNK_EMAIL_PARTS:
        return False

    if domain_labels[-1] in JUNK_EMAIL_PARTS:
        return False
        
    invalid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.js', '.css', '.mui', '.ts', '.tsx', '.json', '.xml', '.find', '.min.js')
    if domain.endswith(invalid_extensions):
        return False

    # Reject fake TLDs — only accept well-known TLDs
    VALID_TLDS = {
        'com', 'org', 'net', 'edu', 'gov', 'mil', 'int', 'io', 'co', 'us',
        'uk', 'ca', 'au', 'de', 'fr', 'es', 'it', 'nl', 'be', 'at', 'ch',
        'se', 'no', 'dk', 'fi', 'pl', 'cz', 'sk', 'hu', 'ro', 'bg', 'hr',
        'si', 'lt', 'lv', 'ee', 'pt', 'gr', 'ie', 'lu', 'mt', 'cy',
        'jp', 'cn', 'kr', 'in', 'sg', 'hk', 'tw', 'th', 'my', 'ph', 'vn',
        'id', 'pk', 'bd', 'lk', 'np',
        'br', 'mx', 'ar', 'cl', 'co', 'pe', 've', 'ec', 'uy', 'py',
        'za', 'ng', 'ke', 'eg', 'ma', 'tz', 'gh', 'et',
        'ru', 'ua', 'tr', 'il', 'ae', 'sa', 'qa', 'kw', 'bh', 'om',
        'nz', 'info', 'biz', 'me', 'pro', 'name', 'mobi', 'tel',
        'asia', 'cat', 'jobs', 'travel', 'museum', 'aero', 'coop',
        'online', 'store', 'shop', 'site', 'website', 'tech', 'app',
        'dev', 'cloud', 'agency', 'digital', 'media', 'design', 'studio',
        'solutions', 'services', 'consulting', 'group', 'team', 'company',
        'global', 'world', 'center', 'network', 'systems', 'works',
        'ai', 'xyz', 'gg', 'cc', 'tv', 'fm', 'am', 'ly', 'to', 'so',
        'ac', 'space', 'page', 'link', 'click', 'live', 'news', 'blog',
        'email', 'marketing', 'social', 'plus', 'one', 'top', 'icu',
    }
    tld = domain_labels[-1]
    if tld not in VALID_TLDS:
        return False

    # Reject domains where the name part (before TLD) is suspiciously short (<=2 chars)
    # e.g., "el.com", "ars.com" — these are almost always CSS/JS false positives
    domain_name = '.'.join(domain_labels[:-1])
    if len(domain_name) <= 2:
        return False

    # Reject emails where local part looks like a truncated word (ends/starts mid-word
    # with common CSS/code suffixes)
    CODE_FRAGMENTS = {
        'ation', 'tion', 'sion', 'ions', 'ment', 'ness', 'ible', 'able',
        'ling', 'ally', 'ould', 'ight', 'ween', 'ject', 'pect',
    }
    if any(local_part.endswith(frag) for frag in CODE_FRAGMENTS):
        # But allow if domain looks like a real business domain (has 6+ char domain name)
        if len(domain_name) < 6:
            return False

    if any(domain == junk_domain or domain.endswith(f".{junk_domain}") for junk_domain in JUNK_EMAIL_DOMAINS):
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


def _pick_best_email(emails: List[str], site_domain: Optional[str] = None) -> Optional[str]:
    if not emails:
        return None
    
    # First priority: emails whose domain matches the website being crawled
    if site_domain:
        clean_domain = site_domain.lstrip('www.').lower()
        domain_emails = [e for e in emails if e.endswith('@' + clean_domain)]
        if domain_emails:
            # Among domain-matching emails, prefer common prefixes
            priority = ["info@", "contact@", "hello@", "team@", "reservations@", "booking@",
                        "enquiries@", "admin@", "support@", "sales@", "office@"]
            for prefix in priority:
                for e in domain_emails:
                    if e.startswith(prefix):
                        return e
            return domain_emails[0]
    
    # Second priority: common business email prefixes
    priority = ["info@", "contact@", "hello@", "team@", "reservations@", "booking@",
                "enquiries@", "admin@", "support@", "sales@", "office@"]
    for prefix in priority:
        for e in emails:
            if e.startswith(prefix):
                return e
    # Third: non-free-mail addresses
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


async def _scrape_with_httpx_async(base_url: str, timeout: int = 10) -> ScrapedContacts:
    """
    Fast async scraper — fetches pages concurrently.
    Raises ValueError if site is JS-heavy or if homepage could not be fetched.
    """
    import httpx

    if not base_url.startswith(("http://", "https://")):
        base_url = f"https://{base_url}"

    parsed = urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    contacts = ScrapedContacts()
    all_emails: Set[str] = set()
    all_phones: Set[str] = set()

    async with httpx.AsyncClient(
        headers=HEADERS,
        timeout=httpx.Timeout(timeout),
        follow_redirects=True,
        verify=False,
    ) as client:
        try:
            r = await client.get(base_url)
            homepage_html = r.text if r.status_code < 400 else None
        except Exception as e:
            logger.debug(f"httpx error on {base_url}: {e}")
            homepage_html = None

        if not homepage_html:
            raise ValueError("Homepage unreachable — needs Playwright")
        if _is_js_heavy(homepage_html):
            raise ValueError("JS-heavy site — needs Playwright")

        # Extract from homepage immediately
        all_emails.update(_extract_emails(homepage_html))
        all_phones.update(_extract_phones(homepage_html))
        _extract_social(homepage_html, contacts)
        contacts.pages_crawled.append(base_url)

        # Find internal links dynamically
        internal_links = set()
        for match in re.findall(r'href=["\']([^"\']+)["\']', homepage_html):
            if any(kw in match.lower() for kw in ['contact', 'about', 'team', 'location', 'info', 'store']):
                full_url = urljoin(base_url, match)
                if full_url.startswith(origin):
                    internal_links.add(full_url)
                    
        # Always add default contact pages for comprehensive coverage
        for p in CONTACT_PAGES[:12]:
            internal_links.add(origin.rstrip('/') + p)
                
        # Limit to max 15 pages for detailed crawling
        pages_to_fetch = list(internal_links)[:15]
        
        # We already fetched base_url
        if base_url in pages_to_fetch:
            pages_to_fetch.remove(base_url)

        semaphore = asyncio.Semaphore(10)  # max 10 concurrent requests

        async def fetch(url: str):
            async with semaphore:
                try:
                    res = await client.get(url)
                    if res.status_code < 400:
                        return url, res.text
                except Exception:
                    pass
                return url, None

        results = await asyncio.gather(*[fetch(u) for u in pages_to_fetch])

        for url, html in results:
            if not html:
                continue
            all_emails.update(_extract_emails(html))
            all_phones.update(_extract_phones(html))
            _extract_social(html, contacts)
            contacts.pages_crawled.append(url)

    contacts.emails = list(all_emails)
    contacts.phones = list(all_phones)
    site_domain = urlparse(base_url).netloc.lstrip('www.')
    contacts.best_email = _pick_best_email(contacts.emails, site_domain)
    contacts.best_phone = _pick_best_phone(contacts.phones)
    return contacts


def _scrape_with_httpx(base_url: str, timeout: int = 10) -> ScrapedContacts:
    """Sync wrapper — spawns a fresh event loop in a worker thread."""
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(asyncio.run, _scrape_with_httpx_async(base_url, timeout))
        return future.result()


class WebsiteScraperSync:
    """Playwright-based scraper — fallback for JS-rendered sites."""

    def __init__(self, timeout: int = 15000, max_pages: int = 10):
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

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
            try:
                context = browser.new_context(
                    user_agent=HEADERS["User-Agent"],
                    viewport={"width": 1920, "height": 1080},
                )
                pw_page = context.new_page()

                # Fetch homepage first
                try:
                    resp = pw_page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
                    if not resp or resp.status >= 400:
                        context.close()
                        browser.close()
                        return contacts
                    html = pw_page.content()
                except Exception as e:
                    logger.debug(f"Playwright error on homepage {url}: {e}")
                    context.close()
                    browser.close()
                    return contacts

                all_emails.update(_extract_emails(html))
                all_phones.update(_extract_phones(html))
                _extract_social(html, contacts)
                contacts.pages_crawled.append(url)

                # Extract internal links dynamically
                internal_links = set()
                for match in re.findall(r'href=["\']([^"\']+)["\']', html):
                    if any(kw in match.lower() for kw in ['contact', 'about', 'team', 'location', 'info', 'store']):
                        full_url = urljoin(url, match)
                        if full_url.startswith(base_url):
                            internal_links.add(full_url)
                            
                if len(internal_links) < 3:
                    for page_path in CONTACT_PAGES[:10]:
                        internal_links.add(base_url.rstrip('/') + page_path)
                        
                pages_to_fetch = list(internal_links)[:self.max_pages - 1]
                if url in pages_to_fetch:
                    pages_to_fetch.remove(url)

                for page_url in pages_to_fetch:
                    try:
                        resp = pw_page.goto(page_url, wait_until="domcontentloaded", timeout=self.timeout)
                        if not resp or resp.status >= 400:
                            continue
                        html = pw_page.content()
                        all_emails.update(_extract_emails(html))
                        all_phones.update(_extract_phones(html))
                        _extract_social(html, contacts)
                        contacts.pages_crawled.append(page_url)
                    except Exception as e:
                        logger.debug(f"Playwright error on {page_url}: {e}")
                        continue

                context.close()
            finally:
                browser.close()

        contacts.emails = list(all_emails)
        contacts.phones = list(all_phones)
        site_domain = urlparse(url).netloc.lstrip('www.')
        contacts.best_email = _pick_best_email(contacts.emails, site_domain)
        contacts.best_phone = _pick_best_phone(contacts.phones)
        return contacts


def scrape_website_sync(url: str, timeout: int = 15000, max_pages: int = 20) -> ScrapedContacts:
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


def _ddg_email_search(domain: str) -> Optional[str]:
    """Search DuckDuckGo for a business email when crawl finds nothing."""
    try:
        from ddgs import DDGS
        query = f'email contact "@{domain}"'
        with DDGS() as ddgs:
            for result in ddgs.text(query, max_results=5):
                text = (result.get('body', '') + ' ' + result.get('title', ''))
                for m in re.findall(r'[a-zA-Z0-9._%+\-]+@' + re.escape(domain), text, re.IGNORECASE):
                    if _is_valid_email(m.lower()):
                        return m.lower()
    except Exception as e:
        logger.debug(f"DDG email search failed: {e}")
    return None


async def scrape_website_for_contacts(url: str, timeout: int = 15000, max_pages: int = 20) -> ScrapedContacts:
    """Async entry point — tries concurrent httpx first, Playwright fallback, DDG email fallback."""
    contacts = None
    try:
        contacts = await _scrape_with_httpx_async(url, timeout=min(timeout // 1000, 10))
    except Exception as e:
        if not isinstance(e, ValueError):
            logger.debug(f"async httpx failed ({e}), falling back to Playwright")
        import concurrent.futures
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as ex:
            scraper = WebsiteScraperSync(timeout=timeout, max_pages=max_pages)
            contacts = await loop.run_in_executor(ex, scraper.scrape, url)

    # If still no email, try DuckDuckGo search for domain email
    if contacts and not contacts.best_email:
        parsed = urlparse(url)
        domain = parsed.netloc.lstrip('www.')
        if domain:
            loop = asyncio.get_event_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as ex:
                found = await loop.run_in_executor(ex, _ddg_email_search, domain)
            if found:
                contacts.best_email = found
                contacts.emails = [found]

    return contacts


# Alias for backward compatibility
WebsiteScraper = WebsiteScraperSync
