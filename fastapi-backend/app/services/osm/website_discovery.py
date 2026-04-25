"""
Website Discovery Service
─────────────────────────
Discovers official websites for businesses that OSM doesn't have data for.
Uses DuckDuckGo search via the `ddgs` library (handles rate limits, browser
impersonation, etc. out of the box — no API key needed).
"""
import time
from typing import Optional, List, Dict
from urllib.parse import urlparse

import re

from ddgs import DDGS


# Domains to skip — social media, directories, food delivery, review sites, etc.
SKIP_DOMAINS = frozenset({
    # Social media
    "facebook.com", "instagram.com", "twitter.com", "x.com",
    "youtube.com", "linkedin.com", "tiktok.com", "pinterest.com",
    # Review / directory sites
    "yelp.com", "tripadvisor.com", "zomato.com", "foursquare.com",
    "yellowpages.com", "bbb.org", "trustpilot.com", "glassdoor.com",
    "justdial.com", "sulekha.com", "manta.com",
    # Wikis
    "wikipedia.org", "wikidata.org", "wikimedia.org",
    # Search engines / maps
    "google.com", "maps.google.com", "bing.com", "duckduckgo.com",
    "openstreetmap.org", "waze.com",
    # Food delivery
    "foodpanda.pk", "foodpanda.com", "uber.com", "deliveroo.com",
    "grubhub.com", "doordash.com", "justeat.com",
    # Classifieds / e-commerce
    "zameen.com", "olx.com", "daraz.pk",
    # Food/restaurant directory aggregators
    "peekaboo.guru", "cybo.com", "place123.net",
    "wanderlog.com", "restaurantmenu.com.pk", "menucard.pk",
    "kfoods.com", "restaurantguru.com", "menuism.com",
    "allmenus.com", "menupages.com", "menu.com.pk",
    "mughal.pk", "pakpedia.pk",
    # Travel aggregators
    "booking.com", "agoda.com", "expedia.com", "hotels.com",
    "trivago.com", "kayak.com", "makemytrip.com",
    # Generic/blog/hosting platforms (not the business's own domain)
    "blogspot.com", "wordpress.com", "medium.com", "tumblr.com",
    "tossdown.website", "wixsite.com", "weebly.com",
    "squarespace.com", "godaddysites.com", "sites.google.com",
    # Ordering / menu platforms (subdomains like businessname.ordrz.com)
    "ordrz.com", "order.online", "gloriafood.com",
    "cloudwaitress.com", "getbento.com",
    # Food blogs / review blogs
    "lahoresnob.com", "foodfusion.com", "foodpakistan.com",
    "lahorefoodies.com", "reviewit.pk", "mashion.pk",
    "dailytimes.com.pk", "dawn.com", "geo.tv", "arynews.tv",
    "thenews.com.pk", "tribune.com.pk", "samaa.tv",
})

# Generic words that shouldn't count as a name match
GENERIC_WORDS = frozenset({
    "restaurant", "hotel", "cafe", "shop", "store", "food",
    "grill", "kitchen", "bar", "bakery", "the", "and",
    "family", "new", "old", "sweet", "sweets", "bakers",
    # Pakistani / South-Asian cuisine terms (too generic for name matching)
    "karahi", "tikka", "biryani", "nihari", "haleem", "kebab",
    "kabab", "tandoori", "naan", "chai", "lassi", "paratha",
    "dhaba", "handi", "chapli", "seekh", "boti", "pulao",
    "chaat", "samosa", "paye", "sajji", "shinwari",
    # Common generic business words
    "foods", "cuisine", "dine", "dining", "eatery",
    "lahore", "karachi", "islamabad", "rawalpindi",  # city names
})


def _is_skip_domain(url: str) -> bool:
    """Check if the URL belongs to a domain we want to skip."""
    try:
        netloc = urlparse(url).netloc.lower().lstrip("www.")
        # Check both full domain and root domain (last 2 parts)
        # e.g. for "bundukhan.ordrz.com" check both that AND "ordrz.com"
        parts = netloc.split(".")
        root = ".".join(parts[-2:]) if len(parts) >= 2 else netloc
        return any(skip in netloc or skip == root for skip in SKIP_DOMAINS)
    except Exception:
        return True


def _get_base_url(url: str) -> str:
    """Normalize a URL to just the homepage (scheme + netloc)."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _score_result(url: str, title: str, business_name: str) -> int:
    """
    Score a search result's relevance to the business.
    Higher = better match.  0 = definitely not relevant.
    
    Scoring:
        - Concatenated name in domain (e.g. "bundukhan" in bundukhan.pk): +25
        - Individual name word in domain: +10 each
        - Individual name word in title:  +3 each
    
    Minimum threshold to accept: 5 (requires domain match or 2+ title matches).
    """
    name_lower = business_name.lower()
    # Significant name words (non-generic, >= 3 chars)
    name_words = [w for w in re.split(r'\W+', name_lower)
                  if len(w) >= 3 and w not in GENERIC_WORDS]
    if not name_words:
        return 1  # Can't validate — weak accept

    domain = urlparse(url).netloc.lower().replace("www.", "")
    title_lower = (title or "").lower()
    score = 0

    # Strongest signal: concatenated name appears in domain
    # e.g. "bundukhan" in "bundukhan.pk" or "saltandpepper" style
    concat_name = "".join(name_words)
    if len(concat_name) >= 5 and concat_name in domain.replace(".", "").replace("-", ""):
        score += 25

    # Individual domain word matches
    for word in name_words:
        if word in domain:
            score += 10

    # Title/snippet match (weaker signal)
    for word in name_words:
        if word in title_lower:
            score += 3

    return score

# Minimum score threshold to accept a result
MIN_SCORE = 5


def discover_website(
    business_name: str,
    city: str,
    country: str = "",
    verify: bool = False,
) -> Optional[str]:
    """
    Search DuckDuckGo to discover the official website of a business.

    Args:
        business_name: Name of the business (e.g. "Bundu Khan")
        city: City where the business is located
        country: Country (optional)
        verify: Unused (kept for API compat)

    Returns:
        Website URL string or None
    """
    query = f"{business_name} {city} {country} official website".strip()

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=10))

        # Score all results and pick the best match
        best_url = None
        best_score = 0

        for r in results:
            url = r.get("href", "")
            title = r.get("title", "")
            if not url or _is_skip_domain(url):
                continue

            score = _score_result(url, title, business_name)
            if score > best_score:
                best_score = score
                best_url = _get_base_url(url)

        # Only return if we have a reasonable match
        if best_url and best_score >= MIN_SCORE:
            return best_url

    except Exception as e:
        print(f"  ⚠️ Search failed for '{business_name}': {e}")

    return None


def discover_websites_bulk(
    records: List[Dict],
    city: str,
    country: str = "",
    verify: bool = False,
) -> tuple[List[Dict], int]:
    """
    Discover websites for all businesses that don't already have one.

    Returns:
        (updated_records, discovered_count)
    """
    discovered = 0
    total_without = sum(1 for r in records if not r.get("website") and r.get("business_name"))

    print(f"\n🔍 Discovering websites for {total_without} businesses in {city}, {country}...")

    for i, rec in enumerate(records):
        if rec.get("website") or not rec.get("business_name"):
            continue

        name = rec["business_name"]
        print(f"  [{i+1}] Searching for: {name}...", end=" ", flush=True)

        url = discover_website(name, city, country)

        if url:
            rec["website"] = url
            rec["website_discovered"] = True
            discovered += 1
            print(f"✅ {url}")
        else:
            print("❌ not found")

        # Small delay to avoid rate-limit (ddgs handles most of this internally)
        time.sleep(0.3)

    print(f"\n📊 Website Discovery Complete: {discovered}/{total_without} websites found\n")
    return records, discovered
