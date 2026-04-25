"""
Website Scraper using Playwright for JavaScript-rendered websites.
Extracts emails, phone numbers, and social media links.
"""
import asyncio
import json
import re
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScrapedContacts:
    """Container for scraped contact information"""
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


# Junk email patterns to filter out
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

# Pages most likely to have contact info
CONTACT_PAGES = [
    "/contact", "/contact-us", "/contactus", "/about", "/about-us", "/aboutus",
    "/location", "/locations", "/our-location", "/find-us", "/visit", "/visit-us",
    "/hours", "/hours-location", "/store", "/stores", "/branches",
    "/reach-us", "/get-in-touch", "/connect", "/info", "/information",
    "/team", "/our-team", "/staff", "/people", "/support", "/help",
    "/footer", "/privacy", "/legal", "/imprint", "/impressum",
]

# Social media patterns
SOCIAL_PATTERNS = {
    "facebook": [
        r'https?://(?:www\.)?facebook\.com/([a-zA-Z0-9._-]+)/?(?:\?[^"\'<>\s]*)?',
        r'https?://(?:www\.)?fb\.com/([a-zA-Z0-9._-]+)/?',
    ],
    "instagram": [
        r'https?://(?:www\.)?instagram\.com/([a-zA-Z0-9._]+)/?(?:\?[^"\'<>\s]*)?',
    ],
    "twitter": [
        r'https?://(?:www\.)?(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)/?(?:\?[^"\'<>\s]*)?',
    ],
    "linkedin": [
        r'https?://(?:www\.)?linkedin\.com/(?:company|in)/([a-zA-Z0-9_-]+)/?',
    ],
    "youtube": [
        r'https?://(?:www\.)?youtube\.com/(?:c/|channel/|@)?([a-zA-Z0-9_-]+)/?',
    ],
    "tiktok": [
        r'https?://(?:www\.)?tiktok\.com/@([a-zA-Z0-9._-]+)/?',
    ],
}

# Skip these social paths (not actual profiles)
SOCIAL_SKIP_PATHS = {
    "facebook": ["tr", "plugins", "share", "login", "dialog", "sharer", "sharer.php"],
    "instagram": ["p", "reel", "explore", "accounts", "tv", "stories"],
    "twitter": ["intent", "share", "home", "search", "login"],
    "linkedin": ["shareArticle", "share"],
    "youtube": ["watch", "embed", "results", "feed"],
    "tiktok": ["embed"],
}


class WebsiteScraperSync:
    """Synchronous website scraper using Playwright for JS rendering.
    Used internally - runs in a thread executor for async compatibility.
    """
    
    def __init__(self, timeout: int = 30000, max_pages: int = 15):
        self.timeout = timeout
        self.max_pages = max_pages
        
    def scrape(self, url: str) -> ScrapedContacts:
        """
        Scrape a website for contact information using sync Playwright.
        """
        from playwright.sync_api import sync_playwright
        
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        contacts = ScrapedContacts()
        visited: Set[str] = set()
        all_emails: Set[str] = set()
        all_phones: Set[str] = set()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            try:
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080},
                )
                
                page = context.new_page()
                
                # Build list of pages to check
                pages_to_check = [url]
                for contact_page in CONTACT_PAGES:
                    page_url = base_url.rstrip('/') + contact_page
                    if page_url not in pages_to_check:
                        pages_to_check.append(page_url)
                
                # Crawl each page
                for page_url in pages_to_check[:self.max_pages]:
                    if page_url in visited:
                        continue
                        
                    try:
                        visited.add(page_url)
                        logger.debug(f"Crawling: {page_url}")
                        response = page.goto(page_url, wait_until="domcontentloaded", timeout=self.timeout)
                        
                        if not response or response.status >= 400:
                            continue
                        
                        # Wait for dynamic content
                        try:
                            page.wait_for_load_state("networkidle", timeout=5000)
                        except:
                            pass  # Some pages never reach network idle
                        
                        # Get page content (including JS-rendered content)
                        content = page.content()
                        
                        # Extract emails
                        page_emails = self._extract_emails(content)
                        all_emails.update(page_emails)
                        
                        # Extract phone numbers
                        page_phones = self._extract_phones(content)
                        all_phones.update(page_phones)
                        
                        # Extract social links
                        self._extract_social_links(content, contacts)
                        
                        contacts.pages_crawled.append(page_url)
                        
                        # If we found an email on homepage, also dynamically find contact links
                        if page_url == url:
                            contact_links = self._find_contact_links_sync(page, base_url)
                            for link in contact_links:
                                if link not in pages_to_check and link not in visited:
                                    pages_to_check.append(link)
                        
                        logger.debug(f"Found {len(page_emails)} emails, {len(page_phones)} phones on {page_url}")
                        
                    except Exception as e:
                        logger.debug(f"Error crawling {page_url}: {e}")
                        continue
                
                context.close()
                
            finally:
                browser.close()
        
        # Finalize results
        contacts.emails = list(all_emails)
        contacts.phones = list(all_phones)
        contacts.best_email = self._pick_best_email(contacts.emails)
        contacts.best_phone = self._pick_best_phone(contacts.phones)
        
        return contacts
    
    def _find_contact_links_sync(self, page, base_url: str) -> List[str]:
        """Find links that might lead to contact info (sync version)"""
        contact_links = []
        try:
            links = page.query_selector_all('a')
            for link in links:
                try:
                    href = link.get_attribute('href')
                    text = (link.text_content() or '').lower()
                    
                    if not href:
                        continue
                    
                    # Look for contact-related links
                    contact_keywords = ['contact', 'about', 'location', 'reach', 'email', 'get in touch', 'find us', 'visit']
                    if any(kw in text for kw in contact_keywords) or any(kw in href.lower() for kw in contact_keywords):
                        full_url = urljoin(base_url, href)
                        if full_url.startswith(base_url) and full_url not in contact_links:
                            contact_links.append(full_url)
                except:
                    continue
        except Exception as e:
            logger.debug(f"Error finding contact links: {e}")
        
        return contact_links[:10]  # Limit to 10 additional links
    
    def _extract_emails(self, content: str) -> Set[str]:
        """Extract emails using multiple methods"""
        emails = set()
        
        # Method 1: Standard regex
        raw_emails = re.findall(
            r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
            content, re.IGNORECASE
        )
        
        # Method 2: mailto links
        mailto_emails = re.findall(
            r'mailto:([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
            content, re.IGNORECASE
        )
        
        # Method 3: JSON-LD / Schema.org
        json_ld_blocks = re.findall(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            content, re.IGNORECASE | re.DOTALL
        )
        for block in json_ld_blocks:
            try:
                data = json.loads(block)
                emails.update(self._extract_emails_from_json(data))
            except:
                # Try to extract from malformed JSON
                email_matches = re.findall(r'"email"\s*:\s*"([^"]+@[^"]+)"', block)
                emails.update(email_matches)
        
        # Method 4: URL-encoded emails
        url_encoded = re.findall(
            r'([a-zA-Z0-9._%+\-]+)%40([a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
            content, re.IGNORECASE
        )
        for local, domain in url_encoded:
            emails.add(f"{local}@{domain}")
        
        # Method 5: data attributes
        data_attr_emails = re.findall(
            r'data-[a-z-]*email[a-z-]*=["\']([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})',
            content, re.IGNORECASE
        )
        
        # Combine all
        all_raw = raw_emails + mailto_emails + data_attr_emails + list(emails)
        
        # Filter and clean
        for email in all_raw:
            email = email.strip().strip('"').strip("'").lower()
            if self._is_valid_email(email):
                emails.add(email)
        
        return emails
    
    def _extract_emails_from_json(self, data, depth=0) -> Set[str]:
        """Recursively extract emails from JSON data"""
        emails = set()
        if depth > 10:
            return emails
        
        if isinstance(data, dict):
            for key, value in data.items():
                key_lower = key.lower()
                if key_lower in ('email', 'contactemail', 'businessemail', 'supportemail', 'mail'):
                    if isinstance(value, str) and '@' in value:
                        emails.add(value.replace('mailto:', '').strip())
                elif isinstance(value, (dict, list)):
                    emails.update(self._extract_emails_from_json(value, depth + 1))
        elif isinstance(data, list):
            for item in data:
                emails.update(self._extract_emails_from_json(item, depth + 1))
        
        return emails
    
    def _is_valid_email(self, email: str) -> bool:
        """Check if email is valid and not junk"""
        if not email or '@' not in email or '.' not in email.split('@')[-1]:
            return False
        
        domain = email.split('@')[-1]
        if domain in JUNK_EMAIL_DOMAINS:
            return False
        
        for pattern in JUNK_EMAIL_PATTERNS:
            if re.search(pattern, email, re.IGNORECASE):
                return False
        
        # Additional validation
        if len(email) < 6 or len(email) > 100:
            return False
        
        return True
    
    def _extract_phones(self, content: str) -> Set[str]:
        """Extract phone numbers from content"""
        phones = set()
        
        # Various phone patterns
        phone_patterns = [
            # US format: (xxx) xxx-xxxx or xxx-xxx-xxxx
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            # International: +1 xxx xxx xxxx
            r'\+\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}',
            # tel: links
            r'tel:([+\d\-.\s()]+)',
            # href="tel:" format
            r'href=["\']tel:([^"\']+)',
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                cleaned = self._clean_phone(match)
                if cleaned and len(cleaned) >= 10:
                    phones.add(cleaned)
        
        # Also check for phone in JSON-LD
        phone_json = re.findall(r'"(?:telephone|phone)":\s*"([^"]+)"', content, re.IGNORECASE)
        for phone in phone_json:
            cleaned = self._clean_phone(phone)
            if cleaned and len(cleaned) >= 10:
                phones.add(cleaned)
        
        return phones
    
    def _clean_phone(self, phone: str) -> str:
        """Clean and format phone number"""
        if not phone:
            return ""
        # Remove all non-digit except + at start
        digits = re.sub(r'[^\d+]', '', phone)
        if digits.startswith('+'):
            return '+' + re.sub(r'\D', '', digits[1:])
        return re.sub(r'\D', '', digits)
    
    def _extract_social_links(self, content: str, contacts: ScrapedContacts):
        """Extract social media links"""
        for platform, patterns in SOCIAL_PATTERNS.items():
            if getattr(contacts, platform):  # Already found
                continue
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Skip known invalid paths
                    if match.lower() in SOCIAL_SKIP_PATHS.get(platform, []):
                        continue
                    
                    # Build full URL
                    if platform == "facebook":
                        url = f"https://www.facebook.com/{match}"
                    elif platform == "instagram":
                        url = f"https://www.instagram.com/{match}"
                    elif platform == "twitter":
                        url = f"https://twitter.com/{match}"
                    elif platform == "linkedin":
                        url = f"https://www.linkedin.com/company/{match}"
                    elif platform == "youtube":
                        url = f"https://www.youtube.com/{match}"
                    elif platform == "tiktok":
                        url = f"https://www.tiktok.com/@{match}"
                    else:
                        url = match
                    
                    setattr(contacts, platform, url)
                    break
                
                if getattr(contacts, platform):
                    break
    
    def _pick_best_email(self, emails: List[str]) -> Optional[str]:
        """Pick the most likely business contact email"""
        if not emails:
            return None
        
        priority_prefixes = [
            "info@", "contact@", "hello@", "reservations@", "booking@",
            "enquiries@", "admin@", "support@", "sales@", "office@"
        ]
        
        for prefix in priority_prefixes:
            for email in emails:
                if email.lower().startswith(prefix):
                    return email
        
        # Prefer non-gmail/yahoo emails
        for email in emails:
            lower = email.lower()
            if "@gmail" not in lower and "@yahoo" not in lower and "@hotmail" not in lower:
                return email
        
        return emails[0] if emails else None
    
    def _pick_best_phone(self, phones: List[str]) -> Optional[str]:
        """Pick the best phone number"""
        if not phones:
            return None
        
        # Prefer numbers with area codes
        for phone in phones:
            if len(phone) >= 11 and (phone.startswith('+') or phone.startswith('1')):
                return phone
        
        return phones[0] if phones else None


async def scrape_website_for_contacts(url: str, timeout: int = 30000, max_pages: int = 15) -> ScrapedContacts:
    """
    Convenience function to scrape a website for contact information.
    
    Uses sync Playwright in a thread executor to avoid Windows async subprocess issues.
    
    Usage:
        contacts = await scrape_website_for_contacts("https://example.com")
        print(contacts.best_email)
        print(contacts.phones)
        print(contacts.facebook)
    """
    import concurrent.futures
    
    def run_sync():
        scraper = WebsiteScraperSync(timeout=timeout, max_pages=max_pages)
        return scraper.scrape(url)
    
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, run_sync)
        return result


# Synchronous wrapper for use in non-async contexts
def scrape_website_sync(url: str, timeout: int = 30000, max_pages: int = 15) -> ScrapedContacts:
    """Synchronous wrapper - runs directly"""
    scraper = WebsiteScraperSync(timeout=timeout, max_pages=max_pages)
    return scraper.scrape(url)


# Alias for backward compatibility
WebsiteScraper = WebsiteScraperSync
