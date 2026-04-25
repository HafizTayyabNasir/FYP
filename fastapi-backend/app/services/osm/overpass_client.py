import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==============================
# REQUIRED: Put real email here
# ==============================
CONTACT_EMAIL = "your_real_email@gmail.com"
USER_AGENT = f"FYP-Global-OSM-Extractor/2.0 ({CONTACT_EMAIL})"

OUTPUT_FILE = "business_data.json"

# Search behavior
DEFAULT_RADIUS_METERS = 8000
MAX_RESULTS = 500
OVERPASS_INTERNAL_TIMEOUT = 180

# Reliability — two separate timeout profiles:
# Overpass can take 60-120s for large radius queries; website crawl should be fast
OVERPASS_READ_TIMEOUT = 120  # seconds — large radius queries need time
CRAWL_READ_TIMEOUT    = 20   # seconds — website pages should load fast
CONNECT_TIMEOUT       = 8    # seconds — fail fast on dead connections
RETRIES               = 3
BACKOFF_BASE          = 2

# Website crawl enrichment
ENABLE_WEBSITE_CRAWL   = True
CRAWL_MAX_PAGES_PER_SITE = 5   # kept for API compat but concurrent probing ignores sequential limit
CRAWL_MAX_WORKERS      = 20    # more workers = more sites processed at once

# Nominatim fallback endpoints
NOMINATIM_SERVERS = [
    "https://nominatim.openstreetmap.org/search",
    "https://nominatim.openstreetmap.fr/search",
    "https://nominatim.geocoding.ai/search",
]

# Overpass fallback endpoints
OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter",
]

# ──────────────────────────────────────────────────────────
# Junk email filters
# These domains / patterns appear in HTML source but are NOT
# real business contact emails.
# ──────────────────────────────────────────────────────────
JUNK_EMAIL_DOMAINS = {
    # Error tracking / analytics
    "sentry.io", "sentry.wixpress.com", "sentry-next.wixpress.com",
    # Placeholder / template emails
    "example.com", "domain.com", "yourdomain.com", "test.com",
    "placeholder.com", "email.com",
    # Image filenames falsely matched as emails (e.g. sprite@2x.png)
}

JUNK_EMAIL_PATTERNS = [
    r"[a-f0-9]{32}@",          # 32-char hex hash (Sentry DSNs)
    r"@sentry",                  # any sentry domain
    r"\.png$", r"\.jpg$", r"\.gif$", r"\.svg$", r"\.webp$",  # image filenames
    r"\.css$", r"\.js$",         # asset filenames
    r"noemail@",                 # placeholder
    r"user@domain",              # template
    r"your_real_email@",         # the script's own config email
    r"hi@mystore",               # template
    r"@flowdtx\.com",            # 3rd-party platform leak
    r"@flowcode\.com",
    r"@thedtxcompany\.com",
    r"@corcoran\.com",           # realtor site leaked on restaurant page
    r"@meetsoci\.com",           # SaaS platform email
    r"datastudio\d*@",
]

_JUNK_COMPILED = [re.compile(p, flags=re.IGNORECASE) for p in JUNK_EMAIL_PATTERNS]


def is_junk_email(email: str) -> bool:
    email_lower = email.lower()
    # Check domain blocklist
    domain = email_lower.split("@")[-1] if "@" in email_lower else ""
    if domain in JUNK_EMAIL_DOMAINS:
        return True
    # Check pattern blocklist
    for pat in _JUNK_COMPILED:
        if pat.search(email_lower):
            return True
    return False


def extract_emails(text: str) -> list[str]:
    """
    Extract real-looking business contact emails from HTML/text.
    Filters out junk: Sentry DSNs, placeholder emails, image filenames, etc.
    
    Enhanced to also extract from:
    - mailto: links
    - JSON-LD structured data
    - data- attributes
    - URL-encoded emails
    """
    seen = set()
    result = []
    
    # Method 1: Standard email regex pattern
    standard_emails = re.findall(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", text, flags=re.IGNORECASE)
    
    # Method 2: Extract from mailto: links (handles HTML entity encoding too)
    # Pattern: mailto:email@domain.com or href="mailto:email"
    mailto_patterns = [
        r'mailto:([A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,})',
        r'href=["\']mailto:([A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,})',
    ]
    mailto_emails = []
    for pattern in mailto_patterns:
        mailto_emails.extend(re.findall(pattern, text, flags=re.IGNORECASE))
    
    # Method 3: Extract from JSON-LD structured data
    # Look for "email" fields in JSON blocks
    json_ld_emails = []
    json_ld_blocks = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, flags=re.IGNORECASE | re.DOTALL)
    for block in json_ld_blocks:
        try:
            # Handle multiple JSON objects in one block
            data = json.loads(block)
            json_ld_emails.extend(_extract_emails_from_json(data))
        except json.JSONDecodeError:
            # Try to extract emails from malformed JSON
            email_matches = re.findall(r'"email"\s*:\s*"([^"]+)"', block, flags=re.IGNORECASE)
            json_ld_emails.extend(email_matches)
    
    # Method 4: Extract from data attributes
    # e.g., data-email="contact@example.com"
    data_attr_emails = re.findall(r'data-[a-z-]*email[a-z-]*=["\']([A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,})', text, flags=re.IGNORECASE)
    
    # Method 5: Extract URL-encoded emails (e.g., contact%40example.com)
    url_encoded = re.findall(r'([A-Z0-9._%+\-]+)%40([A-Z0-9.\-]+\.[A-Z]{2,})', text, flags=re.IGNORECASE)
    url_decoded_emails = [f"{local}@{domain}" for local, domain in url_encoded]
    
    # Method 6: Extract from common contact JSON patterns
    # e.g., "contactEmail": "...", "businessEmail": "..."
    json_field_patterns = [
        r'"(?:contact_?)?email"\s*:\s*"([^"@]+@[^"]+)"',
        r'"business_?email"\s*:\s*"([^"@]+@[^"]+)"',
        r'"support_?email"\s*:\s*"([^"@]+@[^"]+)"',
        r'"info_?email"\s*:\s*"([^"@]+@[^"]+)"',
    ]
    json_field_emails = []
    for pattern in json_field_patterns:
        json_field_emails.extend(re.findall(pattern, text, flags=re.IGNORECASE))
    
    # Combine all found emails
    all_emails = standard_emails + mailto_emails + json_ld_emails + data_attr_emails + url_decoded_emails + json_field_emails
    
    for e in all_emails:
        # Clean up the email
        e = e.strip().strip('"').strip("'").strip()
        e_lower = e.lower()
        if e_lower in seen:
            continue
        seen.add(e_lower)
        # Validate it looks like an email
        if '@' in e and '.' in e.split('@')[-1] and not is_junk_email(e):
            result.append(e)
    
    # Prefer lowercase, sort for determinism
    return sorted(result, key=lambda x: x.lower())


def _extract_emails_from_json(data, depth=0) -> list[str]:
    """Recursively extract emails from JSON-LD data."""
    if depth > 10:  # Prevent infinite recursion
        return []
    
    emails = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            if key.lower() in ('email', 'contactemail', 'businessemail', 'supportemail'):
                if isinstance(value, str) and '@' in value:
                    emails.append(value)
            elif isinstance(value, (dict, list)):
                emails.extend(_extract_emails_from_json(value, depth + 1))
    elif isinstance(data, list):
        for item in data:
            emails.extend(_extract_emails_from_json(item, depth + 1))
    
    return emails


def pick_best_email(emails: list[str]) -> str | None:
    """
    From a list of valid emails, pick the most likely business contact.
    Priority: info@ > contact@ > hello@ > other gmail/generic > rest
    """
    if not emails:
        return None

    priority_prefixes = ["info@", "contact@", "hello@", "reservations@",
                         "booking@", "enquiries@", "admin@", "support@"]

    for prefix in priority_prefixes:
        for e in emails:
            if e.lower().startswith(prefix):
                return e

    # Prefer non-gmail addresses (more likely to be official)
    non_gmail = [e for e in emails if "@gmail" not in e.lower() and "@yahoo" not in e.lower()]
    if non_gmail:
        return non_gmail[0]

    return emails[0]


# ──────────────────────────────────────────────────────────
# Social link extraction (cleaner regex — avoids tracking pixels)
# ──────────────────────────────────────────────────────────
def extract_social_links(text: str) -> dict:
    # Facebook: must be a profile/page path, not a pixel/tracking URL
    fb_matches = re.findall(
        r"https?://(www\.)?(facebook\.com|fb\.com)/([\w.\-]+/?)",
        text, flags=re.I
    )
    facebook = None
    for _, domain, path in fb_matches:
        # Skip tracking pixel paths
        if re.match(r"^(tr|plugins|share|login|dialog)/", path, re.I):
            continue
        # Skip numeric-only IDs that look like pixel IDs (not page IDs)
        if re.match(r"^\d{10,}/?$", path):
            continue
        facebook = f"https://www.{domain}/{path}".rstrip("?&")
        break

    # Instagram: simple profile URL
    ig = re.search(r"https?://(www\.)?instagram\.com/([\w.\-]+)/?", text, flags=re.I)
    instagram = None
    if ig:
        profile = ig.group(2)
        # skip non-profile paths
        if profile.lower() not in ("p", "reel", "explore", "accounts", "tv"):
            instagram = f"https://www.instagram.com/{profile}/"

    return {"facebook": facebook, "instagram": instagram}


# ──────────────────────────────────────────────────────────
# Session factory
# ──────────────────────────────────────────────────────────
def make_session(pool_size: int = 20, browser_ua: bool = False) -> requests.Session:
    s = requests.Session()
    if browser_ua:
        # Used for crawling business websites — looks like a real browser
        # so sites don't block us
        s.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        })
    else:
        # Used for Nominatim / Overpass — these APIs REQUIRE a legitimate
        # bot User-Agent string. A fake browser UA causes them to return
        # empty responses or block the request entirely.
        s.headers.update({
            "User-Agent": USER_AGENT,   # e.g. "FYP-Global-OSM-Extractor/2.0 (email)"
            "Accept": "application/json",
            "Accept-Language": "en",
        })
    retry = Retry(
        total=RETRIES,
        backoff_factor=BACKOFF_BASE,
        status_forcelist=[429, 502, 503, 504],
        allowed_methods=["GET", "POST"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=pool_size,
        pool_maxsize=pool_size,
    )
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s


# Shared session for Nominatim + Overpass (bot UA — required by OSM policy)
session = make_session(browser_ua=False)


# ──────────────────────────────────────────────────────────
# Utils
# ──────────────────────────────────────────────────────────
def normalize_url(u: str | None) -> str | None:
    if not u:
        return None
    u = u.strip()
    if u and not re.match(r"^https?://", u, flags=re.I):
        u = "https://" + u
    return u


def safe_get(tags: dict, *keys, default=None):
    for k in keys:
        v = tags.get(k)
        if v:
            return v
    return default


# ──────────────────────────────────────────────────────────
# Resilient GET/POST
# ──────────────────────────────────────────────────────────
def resilient_get(url: str, params=None, use_session=None):
    s = use_session or session
    for attempt in range(1, RETRIES + 1):
        try:
            r = s.get(url, params=params, timeout=(CONNECT_TIMEOUT, CRAWL_READ_TIMEOUT))
            r.raise_for_status()
            return r
        except Exception as e:
            if attempt == RETRIES:
                raise RuntimeError(f"GET failed after {RETRIES} retries: {url} | {e}") from e
            time.sleep(BACKOFF_BASE ** attempt)


def resilient_post(url: str, data: bytes):
    for attempt in range(1, RETRIES + 1):
        try:
            r = session.post(url, data=data, timeout=(CONNECT_TIMEOUT, OVERPASS_READ_TIMEOUT))
            r.raise_for_status()
            return r
        except Exception as e:
            if attempt == RETRIES:
                raise RuntimeError(f"POST failed after {RETRIES} retries: {url} | {e}") from e
            wait = BACKOFF_BASE ** attempt
            print(f"   ↻ Retry {attempt}/{RETRIES} for Overpass in {wait}s...")
            time.sleep(wait)


# ──────────────────────────────────────────────────────────
# Geocoding
# ──────────────────────────────────────────────────────────
def geocode_city_center(city: str, country: str):
    query = f"{city}, {country}".strip()
    params = {
        "q": query,
        "format": "json",
        "limit": 10,
        "addressdetails": 1,
        "email": CONTACT_EMAIL,
    }

    last_err = None
    for base in NOMINATIM_SERVERS:
        try:
            r = resilient_get(base, params=params)
            data = r.json()
            if not data:
                last_err = f"No results from {base}"
                continue

            country_l = country.strip().lower()
            best = None
            for item in data:
                addr = item.get("address", {}) or {}
                display = (item.get("display_name") or "").lower()
                cc = (addr.get("country_code") or "").lower()

                if len(country_l) == 2 and cc == country_l:
                    best = item; break
                if country_l in display:
                    best = item; break
                if country_l in ["usa", "us", "united states"] and (cc == "us" or "united states" in display):
                    best = item; break
                if country_l in ["uae", "united arab emirates"] and (cc == "ae" or "united arab emirates" in display):
                    best = item; break

            if best is None:
                best = data[0]

            lat = float(best["lat"])
            lon = float(best["lon"])
            display_name = best.get("display_name")
            cc = ((best.get("address") or {}).get("country_code") or "").upper()

            print("\n✅ Geocoding selected:")
            print("   Input:", query)
            print("   Match:", display_name)
            print("   Country code:", cc)
            print("   Center:", lat, lon, "\n")
            return lat, lon, display_name, cc

        except Exception as e:
            last_err = e
            print(f"➡️ Geocoding server failed: {base} | {e}")

    raise RuntimeError(
        f"Geocoding failed on all servers. Last error: {last_err}\n"
        "Tips:\n"
        "  1) Use a specific city name e.g. 'New York City' + 'USA'\n"
        "  2) Turn off VPN/proxy\n"
        "  3) Try again in a few minutes\n"
    )


# ──────────────────────────────────────────────────────────
# Business type mapping + Overpass
# ──────────────────────────────────────────────────────────
def osm_tag_candidates(business_type: str):
    t = business_type.strip().lower()

    # ── Full mapping: key = canonical OSM term, value = OSM tags ──
    mapping = {
        # Food & drink
        "restaurant":       [("amenity", "restaurant"), ("amenity", "fast_food"), ("amenity", "food_court")],
        "cafe":             [("amenity", "cafe"), ("amenity", "coffee_shop"), ("cuisine", "coffee")],
        "coffee":           [("amenity", "cafe"), ("amenity", "coffee_shop"), ("cuisine", "coffee")],
        "fast_food":        [("amenity", "fast_food")],
        "fast food":        [("amenity", "fast_food")],
        "bar":              [("amenity", "bar")],
        "pub":              [("amenity", "pub")],
        "food court":       [("amenity", "food_court")],
        "food_court":       [("amenity", "food_court")],
        "ice cream":        [("amenity", "ice_cream")],
        "bakery":           [("shop", "bakery")],
        "pizza":            [("amenity", "restaurant"), ("cuisine", "pizza")],
        # Health
        "dentist":          [("healthcare", "dentist"), ("amenity", "dentist")],
        "doctor":           [("amenity", "doctors"), ("healthcare", "doctor")],
        "doctors":          [("amenity", "doctors"), ("healthcare", "doctor")],
        "clinic":           [("amenity", "clinic"), ("healthcare", "clinic")],
        "hospital":         [("amenity", "hospital")],
        "pharmacy":         [("amenity", "pharmacy")],
        "chemist":          [("shop", "chemist")],
        "optician":         [("shop", "optician")],
        "physiotherapy":    [("healthcare", "physiotherapist")],
        # Accommodation
        "hotel":            [("tourism", "hotel")],
        "hostel":           [("tourism", "hostel")],
        "motel":            [("tourism", "motel")],
        "guest house":      [("tourism", "guest_house")],
        "guesthouse":       [("tourism", "guest_house")],
        # Finance
        "bank":             [("amenity", "bank")],
        "atm":              [("amenity", "atm")],
        "money exchange":   [("amenity", "bureau_de_change")],
        # Fitness & beauty
        "gym":              [("leisure", "fitness_centre")],
        "fitness":          [("leisure", "fitness_centre")],
        "fitness centre":   [("leisure", "fitness_centre")],
        "fitness center":   [("leisure", "fitness_centre")],
        "salon":            [("shop", "hairdresser"), ("shop", "beauty")],
        "hair salon":       [("shop", "hairdresser")],
        "hairdresser":      [("shop", "hairdresser")],
        "beauty salon":     [("shop", "beauty")],
        "spa":              [("leisure", "spa"), ("shop", "beauty")],
        "nail salon":       [("shop", "nail_salon")],
        "barbershop":       [("shop", "hairdresser")],
        "barber":           [("shop", "hairdresser")],
        # Retail
        "supermarket":      [("shop", "supermarket")],
        "grocery":          [("shop", "supermarket"), ("shop", "grocery")],
        "convenience":      [("shop", "convenience")],
        "convenience store":[("shop", "convenience")],
        "clothing":         [("shop", "clothes")],
        "clothes":          [("shop", "clothes")],
        "shoes":            [("shop", "shoes")],
        "electronics":      [("shop", "electronics")],
        "mobile phone":     [("shop", "mobile_phone")],
        "jewellery":        [("shop", "jewellery")],
        "jewelry":          [("shop", "jewellery")],
        "bookstore":        [("shop", "books")],
        "books":            [("shop", "books")],
        "florist":          [("shop", "florist")],
        # Education
        "school":           [("amenity", "school")],
        "university":       [("amenity", "university")],
        "college":          [("amenity", "college")],
        "kindergarten":     [("amenity", "kindergarten")],
        "nursery":          [("amenity", "kindergarten")],
        "language school":  [("amenity", "language_school")],
        "driving school":   [("amenity", "driving_school")],
        # Services
        "laundry":          [("shop", "laundry"), ("amenity", "laundry")],
        "dry cleaning":     [("shop", "dry_cleaning")],
        "car wash":         [("amenity", "car_wash")],
        "car repair":       [("shop", "car_repair")],
        "mechanic":         [("shop", "car_repair")],
        "petrol":           [("amenity", "fuel")],
        "gas station":      [("amenity", "fuel")],
        "fuel":             [("amenity", "fuel")],
        "parking":          [("amenity", "parking")],
        "post office":      [("amenity", "post_office")],
        "library":          [("amenity", "library")],
        "place of worship": [("amenity", "place_of_worship")],
        "mosque":           [("amenity", "place_of_worship"), ("religion", "muslim")],
        "church":           [("amenity", "place_of_worship"), ("religion", "christian")],
        # Leisure
        "cinema":           [("amenity", "cinema")],
        "theatre":          [("amenity", "theatre")],
        "theater":          [("amenity", "theatre")],
        "museum":           [("tourism", "museum")],
        "park":             [("leisure", "park")],
        "playground":       [("leisure", "playground")],
        "swimming pool":    [("leisure", "swimming_pool")],
    }

    # ── Step 1: direct match ──────────────────────────────────
    if t in mapping:
        return mapping[t]

    # ── Step 2: strip common plural/suffix variants ───────────
    for suffix in ("s", "es", "ies"):
        stripped = t[:-len(suffix)] if t.endswith(suffix) else None
        if stripped and stripped in mapping:
            return mapping[stripped]
        if suffix == "ies" and stripped:
            y_form = stripped + "y"
            if y_form in mapping:
                return mapping[y_form]

    # ── Step 3: substring match ───────────────────────────────
    for key in mapping:
        if key in t or t in key:
            return mapping[key]

    # ── Step 4: typo/fuzzy correction via difflib ─────────────
    # Catches misspellings like "reataurants" → "restaurant"
    import difflib
    all_keys = list(mapping.keys())
    # Try matching against the input AND the de-pluralised input
    candidates_to_try = [t]
    if t.endswith("s"):
        candidates_to_try.append(t[:-1])   # simple de-plural before fuzzy
    for candidate in candidates_to_try:
        close = difflib.get_close_matches(candidate, all_keys, n=1, cutoff=0.72)
        if close:
            matched_key = close[0]
            return mapping[matched_key], matched_key  # return match info for logging

    # ── Step 5: no match at all ───────────────────────────────
    return [], None


def _resolve_business_type(business_type: str):
    """
    Returns (tags, matched_key, corrected_input).
    Steps 1-3 return (tags, key, original_input).
    Step 4 (fuzzy) returns (tags, key, corrected_input) so caller can warn user.
    Step 5 returns ([], None, original_input).
    """
    result = osm_tag_candidates(business_type)
    # osm_tag_candidates returns either:
    #   list           — steps 1-3 (direct/plural/substring match)
    #   (list, str)    — step 4 (fuzzy match, includes matched key)
    #   ([], None)     — step 5 (no match)
    if isinstance(result, tuple):
        tags, matched_key = result
        corrected = matched_key if matched_key else business_type
        return tags, matched_key, corrected
    else:
        # Steps 1-3: plain list returned, no correction needed
        return result, None, business_type


def build_overpass_query(lat, lon, radius_m, business_type: str) -> str:
    tags, _, corrected = _resolve_business_type(business_type)
    if tags:
        parts = [f'nwr["{k}"="{v}"](around:{radius_m},{lat},{lon});' for k, v in tags]
        joined = "\n      ".join(parts)
        return f"""
        [out:json][timeout:{OVERPASS_INTERNAL_TIMEOUT}];
        (
          {joined}
        );
        out center tags {MAX_RESULTS};
        """
    # Fallback: search by business name text
    # Note: OSM stores business *categories*, not service descriptions like
    # "heating system". This may return 0 results for non-standard types.
    escaped = (corrected or business_type).replace('"', '\\"')
    return f"""
    [out:json][timeout:{OVERPASS_INTERNAL_TIMEOUT}];
    (
      nwr["name"~"{escaped}",i](around:{radius_m},{lat},{lon});
    );
    out center tags {MAX_RESULTS};
    """


def overpass_fetch(query: str) -> dict:
    last_err = None
    for server in OVERPASS_SERVERS:
        try:
            r = resilient_post(server, query.encode("utf-8"))
            return r.json()
        except Exception as e:
            last_err = e
            print(f"➡️ Overpass server failed: {server} | {e}")
    raise RuntimeError(f"All Overpass servers failed. Last error: {last_err}")


def osm_element_to_record(el: dict) -> dict:
    tags = el.get("tags", {}) or {}

    website  = normalize_url(safe_get(tags, "website", "contact:website", "url"))
    phone    = safe_get(tags, "phone", "contact:phone", "mobile", "contact:mobile")
    email    = safe_get(tags, "email", "contact:email")
    facebook = safe_get(tags, "contact:facebook", "facebook")
    instagram= safe_get(tags, "contact:instagram", "instagram")

    # Validate OSM email — strip junk right away
    if email and is_junk_email(email):
        email = None

    if facebook and not facebook.lower().startswith("http"):
        facebook = "https://www.facebook.com/" + facebook.strip().lstrip("@/")
    if instagram and not instagram.lower().startswith("http"):
        instagram = "https://www.instagram.com/" + instagram.strip().lstrip("@/")

    lat = el.get("lat")
    lon = el.get("lon")
    if lat is None:
        center = el.get("center") or {}
        lat = center.get("lat")
        lon = center.get("lon")

    # Build address from OSM addr:* tags
    addr_parts = []
    house = tags.get("addr:housenumber", "")
    street = tags.get("addr:street", "")
    if house and street:
        addr_parts.append(f"{house} {street}")
    elif street:
        addr_parts.append(street)
    
    addr_city = tags.get("addr:city", "")
    addr_state = tags.get("addr:state", "")
    addr_postcode = tags.get("addr:postcode", "")
    
    if addr_city:
        addr_parts.append(addr_city)
    if addr_state:
        addr_parts.append(addr_state)
    if addr_postcode:
        addr_parts.append(addr_postcode)
    
    address = ", ".join(addr_parts) if addr_parts else None

    return {
        "business_name": tags.get("name"),
        "website":   website,
        "email":     email,
        "phone":     phone,
        "facebook":  facebook,
        "instagram": instagram,
        "latitude":  lat,
        "longitude": lon,
        "address":   address,
    }


# ──────────────────────────────────────────────────────────
# Website crawl — fast concurrent probing
# ──────────────────────────────────────────────────────────

SKIP_EXTENSIONS = re.compile(
    r"\.(css|js|json|xml|ico|png|jpg|jpeg|gif|svg|webp|pdf|woff|woff2|ttf|eot|mp4|zip)(\?.*)?$",
    flags=re.I
)

# Trimmed to highest-yield paths (covers ~95% of real contact pages)
PROBE_PATHS = [
    "/contact", "/contact-us", "/about", "/about-us",
    "/contactus", "/our-story", "/location", "/impressum",
    "/locations", "/our-location", "/find-us", "/visit",
    "/reach-us", "/get-in-touch", "/info", "/hours",
]

CONTACT_KEYWORDS = [
    "contact", "about", "about-us", "reach", "enquir",
    "info", "team", "location", "impressum",
]


def _is_contact_href(href: str) -> bool:
    h = href.lower()
    return any(kw in h for kw in CONTACT_KEYWORDS)


def _fetch_page(url: str, crawl_session: requests.Session) -> str | None:
    """Fetch a single page, return first 200KB of HTML or None on failure."""
    try:
        r = crawl_session.get(
            url,
            timeout=(CONNECT_TIMEOUT, CRAWL_READ_TIMEOUT),
            allow_redirects=True,
        )
        if r.status_code in (404, 403, 410):
            return None
        r.raise_for_status()
        ct = (r.headers.get("Content-Type") or "").lower()
        if "html" not in ct and "text" not in ct:
            return None
        return r.text[:200_000] or ""   # cap at 200KB — emails are near top
    except Exception:
        return None


def _probe_concurrently(urls: list, crawl_session: requests.Session) -> dict:
    """Fetch multiple URLs simultaneously. Returns {url: html}."""
    results = {}
    with ThreadPoolExecutor(max_workers=min(len(urls), 6)) as pool:
        future_to_url = {pool.submit(_fetch_page, u, crawl_session): u for u in urls}
        for fut in as_completed(future_to_url):
            url = future_to_url[fut]
            try:
                html = fut.result()
                if html:
                    results[url] = html
            except Exception:
                pass
    return results


def crawl_website_for_contacts(website_url: str, max_pages: int, crawl_session: requests.Session):
    website_url = normalize_url(website_url)
    if not website_url:
        return {"emails": [], "facebook": None, "instagram": None, "crawled_pages": []}

    parsed   = urlparse(website_url)
    base     = f"{parsed.scheme}://{parsed.netloc}"
    href_re  = re.compile(r'href=["\'](/?[^\s"\'<>#][^\s"\'<>]*)', flags=re.IGNORECASE)

    # ── ROUND 1: Homepage + all probe paths fired simultaneously ──
    # e.g. 9 URLs fetched in parallel instead of 9 sequential requests.
    # For a 300ms avg page load, this cuts per-site time from ~2.7s → ~0.3s.
    probe_urls = list(dict.fromkeys([website_url] + [base + p for p in PROBE_PATHS]))
    batch      = _probe_concurrently(probe_urls, crawl_session)

    visited  = set(batch.keys())
    all_text = "\n".join(batch.values())

    # ── EARLY EXIT: if emails found already, stop here ────────
    emails = extract_emails(all_text)
    if emails:
        socials = extract_social_links(all_text)
        return {"emails": emails, "facebook": socials["facebook"],
                "instagram": socials["instagram"], "crawled_pages": sorted(visited)}

    # ── ROUND 2: Scan homepage links for extra contact pages ──
    # Only runs if Round 1 found no emails (rare fallback).
    homepage_html = batch.get(website_url, "")
    extra = []
    seen  = set(visited)
    for href in href_re.findall(homepage_html)[:300]:
        if not href or SKIP_EXTENSIONS.search(href):
            continue
        full  = urljoin(base, href.strip())
        pu    = urlparse(full)
        if pu.netloc != parsed.netloc:
            continue
        clean = f"{pu.scheme}://{pu.netloc}{pu.path}".rstrip("/") or full
        if clean not in seen and _is_contact_href(href):
            extra.append(clean)
            seen.add(clean)

    if extra:
        extra_batch = _probe_concurrently(extra[:4], crawl_session)
        visited.update(extra_batch.keys())
        all_text += "\n".join(extra_batch.values())

    emails  = extract_emails(all_text)
    socials = extract_social_links(all_text)
    return {
        "emails":        emails,
        "facebook":      socials["facebook"],
        "instagram":     socials["instagram"],
        "crawled_pages": sorted(visited),
    }



# ──────────────────────────────────────────────────────────
# Record enrichment (runs in a thread)
# ──────────────────────────────────────────────────────────
def enrich_record(rec: dict) -> dict:
    site = rec.get("website")
    if not site:
        return rec

    # Each thread gets its own session with browser UA — thread-safe
    # Browser UA needed so restaurant websites don't block the crawler
    crawl_session = make_session(pool_size=4, browser_ua=True)

    try:
        crawl = crawl_website_for_contacts(site, CRAWL_MAX_PAGES_PER_SITE, crawl_session)
    except Exception as e:
        print(f"  ⚠️ Crawl failed for {site}: {e}")
        return rec
    finally:
        crawl_session.close()

    # ── EMAIL ──
    if crawl["emails"]:
        best = pick_best_email(crawl["emails"])
        if not rec.get("email") and best:
            rec["email"] = best
        # Always record the full list so researchers can pick
        if len(crawl["emails"]) > 1:
            rec["all_emails_found"] = crawl["emails"]
        elif crawl["emails"]:
            rec["all_emails_found"] = crawl["emails"]

    # ── SOCIAL ──
    if not rec.get("facebook") and crawl.get("facebook"):
        rec["facebook"] = crawl["facebook"]
    if not rec.get("instagram") and crawl.get("instagram"):
        rec["instagram"] = crawl["instagram"]

    rec["website_crawl"] = {"crawled_pages": crawl["crawled_pages"]}
    return rec


# ──────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────
def main():
    print("=== Global Business Directory Extractor v2.0 (OSM + Overpass) ===\n")
    business_type = input("Enter business type (e.g. dentist, restaurant, cafe): ").strip()
    city          = input("Enter city (e.g. New York City): ").strip()
    country       = input("Enter country (e.g. USA or Pakistan or 'us'/'pk'): ").strip()

    radius_in = input(f"Enter radius meters (default {DEFAULT_RADIUS_METERS}): ").strip()
    radius_m  = int(radius_in) if radius_in.isdigit() else DEFAULT_RADIUS_METERS

    lat, lon, display_name, cc = geocode_city_center(city, country)

    print("🔍 Querying OSM directory via Overpass...")
    tags, matched_key, corrected = _resolve_business_type(business_type)
    if tags and corrected != business_type:
        print(f"   ✏️  Typo corrected: '{business_type}' → '{corrected}'")
        print(f"   Matched OSM tags: {tags}")
    elif tags:
        print(f"   Matched OSM tags: {tags}")
    else:
        print(f"   ⚠️  No OSM tag match for '{business_type}'")
        print(f"   ℹ️  OSM stores business categories (restaurant, gym, pharmacy…),")
        print(f"       not service descriptions. Falling back to name search — results may be 0.")
        print(f"       Try a standard type like: restaurant, cafe, dentist, gym, hotel, pharmacy")
    t0 = time.time()
    query = build_overpass_query(lat, lon, radius_m, business_type)
    data  = overpass_fetch(query)
    print(f"   Overpass query done in {time.time()-t0:.1f}s")

    elements = data.get("elements", []) or []
    records  = [osm_element_to_record(el) for el in elements]
    records  = [r for r in records if r.get("business_name")]

    print(f"   Found {len(records)} named businesses")

    if ENABLE_WEBSITE_CRAWL:
        with_sites = [r for r in records if r.get("website")]
        without    = [r for r in records if not r.get("website")]

        print(f"\n🌐 Crawling {len(with_sites)} websites in parallel (workers={CRAWL_MAX_WORKERS})...")
        print("   Prioritising contact/about pages for email extraction...\n")
        t1 = time.time()

        enriched = []
        with ThreadPoolExecutor(max_workers=CRAWL_MAX_WORKERS) as pool:
            futures = {pool.submit(enrich_record, rec): rec for rec in with_sites}
            done = 0
            for fut in as_completed(futures):
                done += 1
                try:
                    result = fut.result()
                    enriched.append(result)
                    status = "✅" if result.get("email") else "—"
                    print(f"  {status} [{done}/{len(with_sites)}] "
                          f"{result.get('business_name', '?')[:40]}"
                          + (f"  → {result['email']}" if result.get("email") else ""))
                except Exception as e:
                    enriched.append(futures[fut])
                    print(f"  ⚠️ Enrichment error: {e}")

        records = enriched + without
        found_email = sum(1 for r in records if r.get("email"))
        print(f"\n   Done in {time.time()-t1:.1f}s  |  Emails found: {found_email}/{len(records)}")

    output = {
        "query": {
            "business_type":     business_type,
            "city":              city,
            "country":           country,
            "resolved_location": display_name,
            "country_code":      cc,
            "radius_meters":     radius_m,
        },
        "result_count":        len(records),
        "emails_found_count":  sum(1 for r in records if r.get("email")),
        "results":             records,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Done! Saved {len(records)} businesses to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()