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

    def _fetch_website_content(self, url: str) -> str:
        """Fetch and clean website content using Playwright for JS rendering"""
        if not url.startswith("https://"):
            url = "https://" + url

        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox"],
                )
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080},
                )
                page = context.new_page()

                try:
                    response = page.goto(url, timeout=30000, wait_until="domcontentloaded")
                except Exception:
                    response = None

                if not response:
                    raise Exception("No response received for url: " + url)

                if response.status >= 400:
                    raise Exception(str(response.status) + " Client Error for url: " + url)

                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    pass

                html = page.content()
                browser.close()

            soup = BeautifulSoup(html, "html.parser")
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            lines = text.splitlines()
            lines = [line.strip() for line in lines if line.strip()]
            text = "\n".join(lines)

            return text

        except Exception as e:
            return "Failed to fetch website: " + str(e)

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
