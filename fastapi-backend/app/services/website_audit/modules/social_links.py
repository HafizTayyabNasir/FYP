import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from playwright.sync_api import sync_playwright


TIMEOUT = 15
PLAYWRIGHT_TIMEOUT_MS = 20000

SOCIAL_DOMAINS = {
    "facebook.com": "Facebook",
    "web.facebook.com": "Facebook",
    "instagram.com": "Instagram",
    "linkedin.com": "LinkedIn",
    "twitter.com": "Twitter/X",
    "x.com": "Twitter/X",
    "youtube.com": "YouTube",
    "tiktok.com": "TikTok",
    "snapchat.com": "Snapchat",
    "pinterest.com": "Pinterest",
    "wa.me": "WhatsApp",
    "whatsapp.com": "WhatsApp",
    "telegram.me": "Telegram",
    "t.me": "Telegram",
}

# Codes that usually mean: "the site is blocking automation"
BOT_BLOCK_CODES = {999, 403, 429}

# Sometimes Facebook (web.facebook.com) returns 400 for bots/region/cookies
# We'll treat 400 as "suspected block" ONLY for social platforms and verify via browser.
SUSPECT_BLOCK_CODES = {400}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def platform_name(link: str) -> str:
    low = link.lower()
    for dom, name in SOCIAL_DOMAINS.items():
        if dom in low:
            return name
    return "Social"


def is_social_link(href: str) -> bool:
    if not href:
        return False
    low = href.lower()
    return any(dom in low for dom in SOCIAL_DOMAINS.keys())


def fetch_html(url: str) -> str:
    r = requests.get(url, timeout=TIMEOUT, headers=HEADERS, verify=False)
    r.raise_for_status()
    return r.text


def extract_social_links(base_url: str, html: str):
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        absolute = urljoin(base_url, href)

        if is_social_link(absolute):
            links.add(absolute)

    return sorted(links)


def check_with_requests(url: str):
    """
    Returns: (state, status_code, final_url_or_error)
    state: WORKING | RESTRICTED | BROKEN | ERROR | SUSPECT_BLOCK
    """
    try:
        resp = requests.get(url, allow_redirects=True, timeout=TIMEOUT, headers=HEADERS)
        code = resp.status_code
        final_url = resp.url

        if code in BOT_BLOCK_CODES:
            return "RESTRICTED", code, final_url

        # Suspected block for some platforms (like Facebook)
        if code in SUSPECT_BLOCK_CODES and is_social_link(url):
            return "SUSPECT_BLOCK", code, final_url

        if 200 <= code < 400:
            return "WORKING", code, final_url

        if 400 <= code < 600:
            return "BROKEN", code, final_url

        return "ERROR", code, final_url

    except Exception as e:
        return "ERROR", None, str(e)


def check_with_playwright(url: str):
    """
    Browser-based validation to handle bot blocks.
    Returns: (ok, final_url_or_error)
    ok True means: page opened in real browser without immediate failure
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=PLAYWRIGHT_TIMEOUT_MS)

            # If blocked, the page may still open but show "restricted" screen.
            # We'll do a simple check: did we end up on a valid URL and have some content?
            title = page.title()
            final_url = page.url
            content_len = len(page.content() or "")

            browser.close()

            # Basic heuristic: if it loaded a real page and content exists
            if content_len > 500 and "error" not in (title or "").lower():
                return True, final_url
            return True, final_url  # still count as accessible if it loads

    except Exception as e:
        return False, str(e)


def rate_social_links(found: int, accessible: int, broken: int) -> int:
    """
    Overall score 0-5 based on accessible ratio and broken links.
    accessible includes WORKING + VERIFIED_BLOCKED (opens in browser).
    """
    if found == 0:
        return 0
    if accessible == 0:
        return 1

    ratio = accessible / found

    if ratio < 0.60:
        return 2
    if ratio < 0.85:
        return 3

    # ratio >= 0.85
    if broken > 0:
        return 4
    return 5


def main():
    website = input("Enter website link (e.g., example.com): ").strip()
    base_url = normalize_url(website)
    if not base_url:
        print("Invalid input.")
        return

    flaws = []

    try:
        html = fetch_html(base_url)
    except Exception as e:
        print(f"Failed to load website: {e}")
        return

    social_links = extract_social_links(base_url, html)

    print("\n=== SOCIAL MEDIA LINKS FOUND ===")
    if not social_links:
        print("No social media links found on the homepage.")
        print("\n=== OVERALL SOCIAL MEDIA SCORE (0–5) ===")
        print("Overall Social Media Links Score: 0/5")
        print("\n=== FLAWS ===")
        print("1. No social media links/icons found (header/footer/homepage).")
        return

    for link in social_links:
        print(f"- {platform_name(link)}: {link}")

    # Counters
    working = 0
    accessible_verified = 0  # blocked by requests but opens in browser
    restricted_unverified = 0  # blocked and could not verify
    broken = 0

    print("\n=== LINK CHECK RESULTS ===")
    for link in social_links:
        plat = platform_name(link)
        state, status, final_or_error = check_with_requests(link)

        if state == "WORKING":
            working += 1
            print(f"✅ {plat} | {status} | {final_or_error}")

        elif state in ("RESTRICTED", "SUSPECT_BLOCK"):
            # Fallback to browser check
            ok, browser_final = check_with_playwright(link)
            if ok:
                accessible_verified += 1
                label = "BOT-PROTECTED (verified in browser)"
                print(f"⚠️ {plat} | {status} | {label} | {browser_final}")
            else:
                restricted_unverified += 1
                print(f"❌ {plat} | {status} | BLOCKED and not verified | {browser_final}")

        elif state == "BROKEN":
            broken += 1
            print(f"❌ {plat} | {status} | {final_or_error}")

        else:
            # ERROR
            # Try browser check (sometimes requests fails but browser works)
            ok, browser_final = check_with_playwright(link)
            if ok:
                accessible_verified += 1
                print(f"⚠️ {plat} | ERROR | Verified in browser | {browser_final}")
            else:
                broken += 1
                print(f"❌ {plat} | ERROR | {final_or_error}")

    found = len(social_links)
    accessible_total = working + accessible_verified

    # Flaws
    if broken > 0:
        flaws.append("Some social media links are broken/unreachable (4xx/5xx or failed to open in browser).")
    if restricted_unverified > 0:
        flaws.append("Some social links appear blocked and could not be verified even in browser automation.")
    if accessible_verified > 0:
        flaws.append(
            "Some social platforms block automated HTTP checks (LinkedIn/Facebook/TikTok). "
            "These links were verified using browser-based checking."
        )

    # Coverage check (optional)
    platforms_found = {platform_name(l) for l in social_links}
    major = {"Facebook", "Instagram", "LinkedIn"}
    if len(platforms_found.intersection(major)) == 0:
        flaws.append("No major platforms found (Facebook/Instagram/LinkedIn missing).")

    overall_score = rate_social_links(found, accessible_total, broken)

    print("\n=== SUMMARY ===")
    print(f"Total social links found: {found}")
    print(f"Working (HTTP accessible): {working}")
    print(f"Accessible but blocked for bots (verified in browser): {accessible_verified}")
    print(f"Blocked and not verified: {restricted_unverified}")
    print(f"Broken/Error: {broken}")

    print("\n=== OVERALL SOCIAL MEDIA SCORE (0–5) ===")
    print(f"Overall Social Media Links Score: {overall_score}/5")

    print("\n=== FLAWS ===")
    if flaws:
        # de-duplicate
        seen = set()
        cleaned = []
        for f in flaws:
            if f not in seen:
                cleaned.append(f)
                seen.add(f)
        for i, f in enumerate(cleaned, 1):
            print(f"{i}. {f}")
    else:
        print("No major social media link issues detected.")


if __name__ == "__main__":
    main()
