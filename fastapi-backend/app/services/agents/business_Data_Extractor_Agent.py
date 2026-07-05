"""
Business Data Extractor Agent - Uses Grok API to extract business details from websites
"""

import json
import re
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from app.core.config import settings

BUSINESS_EXTRACTOR_SYSTEM_PROMPT = """You are a Business Intelligence Analyst specializing in extracting and analyzing business information from website content.

Your task is to analyze the provided website content and extract structured business information.

EXTRACTION REQUIREMENTS:
1. Business Name - The official name of the business
2. Industry - The primary industry/sector (e.g., restaurant, healthcare, retail, technology)
3. Services - List of main services offered
4. Products - List of main products (if applicable)
5. Core Offer - What they primarily sell or provide (their main value proposition)
6. Target Customers - Who are their ideal customers (be specific: demographics, needs, types)
7. Business Goal - What the business is trying to achieve (e.g., more calls, bookings, orders, walk-ins, inquiries, online sales)
8. Differentiator - What makes them different from competitors (e.g., premium, budget-friendly, fast delivery, halal, vegan, organic, family-owned, etc.)
9. Unique Selling Points (USPs) - List of key differentiators
10. Business Description - A concise 2-3 sentence description
11. Company Size - Small, Medium, Large, or Enterprise (estimate based on content)
12. Location - Primary location/service area
13. Contact Information - Phone, email, address if found

RULES:
- Only extract information that is explicitly stated or strongly implied in the content
- If information is not available, return null for that field
- Do not invent or assume information
- Keep descriptions concise and professional
- For services/products, list the main 5-10 items maximum
- For core_offer, summarize their main product/service offering in one sentence
- For target_customers, be specific about who they serve
- For business_goal, infer from the website what they want customers to do (book, buy, call, visit, etc.)
- For differentiator, identify what makes this business unique or special

OUTPUT FORMAT (JSON):
{
    "business_name": "string or null",
    "industry": "string or null",
    "services": ["list of strings"] or null,
    "products": ["list of strings"] or null,
    "core_offer": "string or null",
    "target_customers": "string or null",
    "business_goal": "string or null",
    "differentiator": "string or null",
    "target_audience": "string or null",
    "unique_selling_points": ["list of strings"] or null,
    "business_description": "string or null",
    "company_size": "Small|Medium|Large|Enterprise or null",
    "location": "string or null",
    "contact_info": {
        "phone": "string or null",
        "email": "string or null",
        "address": "string or null"
    },
    "confidence_score": 0.0-1.0
}

Confidence score should reflect how much information you were able to extract (1.0 = all fields, 0.5 = half, etc.)
"""


class BusinessDataExtractorAgent:
    """Agent that extracts business information from websites using Grok API"""

    def __init__(self):
        self.api_key = settings.GROK_API_KEY
        self.api_base_url = settings.GROK_API_BASE_URL
        self.groq_api_key = settings.GROQ_API_KEY

    def _is_cloudflare_challenge(self, text: str) -> bool:
        """Detect Cloudflare challenge / bot-block pages."""
        cf_markers = [
            "one moment, please",
            "checking your browser",
            "enable javascript and cookies",
            "cloudflare",
            "just a moment",
            "verify you are human",
            "ray id",
        ]
        lower = text.lower()
        hits = sum(1 for m in cf_markers if m in lower)
        # If the page is very short AND contains multiple CF markers → blocked
        return hits >= 2 or (len(text.strip()) < 500 and hits >= 1)

    def _clean_html_to_text(self, html: str) -> str:
        """Strip scripts/styles and return readable text from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "iframe"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def _fetch_with_requests(self, url: str) -> Optional[str]:
        """Fast fetch with requests — works for most static sites and often bypasses Cloudflare."""
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Try with full browser-like headers first (no brotli — it triggers CF)
        headers_list = [
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            },
            # Minimal fallback headers
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            },
        ]

        for headers in headers_list:
            try:
                resp = requests.get(url, headers=headers, timeout=15, verify=False, allow_redirects=True)
                text = self._clean_html_to_text(resp.text)
                if self._is_cloudflare_challenge(text):
                    continue  # Try next header set
                if len(text.strip()) < 100:
                    continue  # Too little content
                return text
            except Exception:
                continue

        return None  # All header sets failed

    def _fetch_with_playwright(self, url: str) -> str:
        """Playwright fetch with stealth-like settings for JS-heavy or CF-protected sites."""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                ],
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
            )
            # Hide webdriver flag
            context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            page = context.new_page()

            try:
                response = page.goto(url, timeout=30000, wait_until="domcontentloaded")
            except Exception:
                response = None

            if not response:
                browser.close()
                raise Exception("No response received for url: " + url)

            # Wait longer for CF challenge to resolve
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass

            html = page.content()
            browser.close()

        return self._clean_html_to_text(html)

    def _fetch_website_content(self, url: str) -> str:
        """Fetch website content — tries requests first, falls back to Playwright.
        Also scrapes /about and /contact subpages for richer business data."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        subpages = ["/about", "/about-us", "/contact", "/contact-us", "/services", "/menu"]

        all_text_parts = []

        # --- Strategy 1: requests (fast, often bypasses CF) ---
        try:
            text = self._fetch_with_requests(url)
            if text and len(text) > 200:
                all_text_parts.append(text)
                # Also try subpages with requests
                for sp in subpages:
                    try:
                        sp_text = self._fetch_with_requests(base.rstrip("/") + sp)
                        if sp_text and len(sp_text) > 100:
                            all_text_parts.append(f"\n--- PAGE: {sp} ---\n" + sp_text)
                    except Exception:
                        continue
                combined = "\n".join(all_text_parts)
                # Truncate to avoid token limits
                return combined[:15000] if len(combined) > 15000 else combined
        except Exception:
            pass

        # --- Strategy 2: Playwright (for JS-heavy or CF-protected sites) ---
        try:
            text = self._fetch_with_playwright(url)
            if text and not self._is_cloudflare_challenge(text) and len(text) > 200:
                all_text_parts.append(text)
                combined = "\n".join(all_text_parts)
                return combined[:15000] if len(combined) > 15000 else combined
        except Exception as e:
            if not all_text_parts:
                return "Failed to fetch website: " + str(e)

        if all_text_parts:
            combined = "\n".join(all_text_parts)
            return combined[:15000] if len(combined) > 15000 else combined

        return "Failed to fetch website: All strategies failed (possibly Cloudflare-protected)"

    def _call_grok_api(self, content: str, business_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Call Grok API to extract business data"""
        if not self.api_key:
            raise Exception("Grok API key not configured")

        user_prompt = (
            "Analyze this website content and extract business information:\n\n"
            "Business Name (if known): " + (business_name or "Unknown")
            + "\n\nWEBSITE CONTENT:\n" + content
            + "\n\nExtract the business information following the specified format. Return ONLY valid JSON."
        )

        response = requests.post(
            self.api_base_url + "/chat/completions",
            headers={
                "Authorization": "Bearer " + self.api_key,
                "Content-Type": "application/json",
            },
            json={
                "model": "grok-beta",
                "messages": [
                    {"role": "system", "content": BUSINESS_EXTRACTOR_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 2000,
            },
        )
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]

        # Extract JSON from response
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            return json.loads(json_match.group())
        return None

    def _call_groq_api(self, content: str, business_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fallback to Groq API if Grok is not available"""
        if not self.groq_api_key:
            raise Exception("Neither Grok nor Groq API key is configured")

        from groq import Groq

        client = Groq(api_key=self.groq_api_key)

        user_prompt = (
            "Analyze this website content and extract business information:\n\n"
            "Business Name (if known): " + (business_name or "Unknown")
            + "\n\nWEBSITE CONTENT:\n" + content
            + "\n\nExtract the business information following the specified format. Return ONLY valid JSON."
        )

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": BUSINESS_EXTRACTOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        response_content = completion.choices[0].message.content

        # Extract JSON from response
        json_match = re.search(r"\{[\s\S]*\}", response_content)
        if json_match:
            return json.loads(json_match.group())
        return None

    def extract_business_data(self, website_url: str, business_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract business data from a website.

        Args:
            website_url: URL of the business website
            business_name: Optional known business name
            
        Returns:
            Dictionary with extracted business information
        """
        content = self._fetch_website_content(website_url)

        try:
            if self.api_key:
                result = self._call_grok_api(content, business_name)
            else:
                result = self._call_groq_api(content, business_name)
        except Exception as e:
            try:
                result = self._call_groq_api(content, business_name)
            except Exception as e2:
                raise Exception("All API calls failed: " + str(e) + ", " + str(e2))

        if result is None:
            result = {}

        result["website_url"] = website_url
        result["extracted_at"] = datetime.utcnow().isoformat()

        # Calculate confidence based on filled fields
        fields = [
            "business_name", "industry", "services", "products", "core_offer",
            "target_customers", "business_goal", "differentiator", "target_audience",
            "unique_selling_points", "business_description", "company_size",
            "location", "contact_info",
        ]
        filled = sum(1 for f in fields if result.get(f))
        result["confidence_score"] = filled / len(fields)

        return result

    def extract_batch(self, businesses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract business data for multiple businesses.

        Args:
            businesses: List of dicts with 'website_url' and optional 'business_name'
            
        Returns:
            List of extracted business data
        """
        results = []
        for business in businesses:
            website_url = business.get("website_url") or business.get("website", "")
            if not website_url:
                results.append({
                    "error": "No website URL provided",
                    "extracted_at": datetime.utcnow().isoformat(),
                    "business_name": business.get("business_name", ""),
                })
                continue

            try:
                data = self.extract_business_data(
                    website_url=website_url,
                    business_name=business.get("business_name"),
                )
                results.append(data)
            except Exception as e:
                results.append({
                    "website_url": website_url,
                    "error": str(e),
                    "extracted_at": datetime.utcnow().isoformat(),
                    "business_name": business.get("business_name", ""),
                })

        return results
