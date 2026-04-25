import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import urllib3

# Disable SSL warnings for audit purposes
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_html_with_playwright(url: str) -> str:
    """Fetch HTML using Playwright for sites that block basic requests"""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()
        response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
        
        if not response:
            raise Exception(f"No response for {url}")
        if response.status >= 400:
            raise Exception(f"HTTP {response.status} for {url}")
        
        # Wait for dynamic content
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass
        
        html = page.content()
        context.close()
        browser.close()
        return html


# Check function to get the metadata
def fetch_html(url: str):
    """Fetch HTML content of the URL, fallback to Playwright if blocked"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    
    try:
        # Try basic requests first (faster)
        r = requests.get(url, timeout=15, headers=headers, verify=False, allow_redirects=True)
        r.raise_for_status()
        return r.text
    except requests.exceptions.RequestException as e:
        # Fallback to Playwright for blocked sites
        print(f"Basic request failed ({e}), trying Playwright...")
        return fetch_html_with_playwright(url)

# Function to normalize and format URL
def normalize_url(url: str) -> str:
    """Ensure the URL is valid and starts with http(s)"""
    url = url.strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

# Function to check SEO metadata tags
def check_seo_metadata(url: str):
    """Check the SEO metadata of a webpage"""
    try:
        html = fetch_html(url)
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None

    soup = BeautifulSoup(html, "html.parser")

    # Extract common SEO metadata
    metadata = {
        "title": soup.title.string if soup.title else None,
        "description": None,
        "keywords": None,
        "canonical": None,
        "og_title": None,
        "og_description": None,
        "og_image": None,
        "og_url": None,
        "twitter_title": None,
        "twitter_description": None,
        "twitter_image": None,
        "canonical_link": None,
    }

    # Title tag
    metadata["title"] = soup.title.string if soup.title else None

    # Meta Description
    description_tag = soup.find("meta", attrs={"name": "description"})
    if description_tag:
        metadata["description"] = description_tag.get("content")

    # Meta Keywords
    keywords_tag = soup.find("meta", attrs={"name": "keywords"})
    if keywords_tag:
        metadata["keywords"] = keywords_tag.get("content")

    # Open Graph Metadata (Facebook, LinkedIn)
    og_title_tag = soup.find("meta", attrs={"property": "og:title"})
    if og_title_tag:
        metadata["og_title"] = og_title_tag.get("content")

    og_description_tag = soup.find("meta", attrs={"property": "og:description"})
    if og_description_tag:
        metadata["og_description"] = og_description_tag.get("content")

    og_image_tag = soup.find("meta", attrs={"property": "og:image"})
    if og_image_tag:
        metadata["og_image"] = og_image_tag.get("content")

    og_url_tag = soup.find("meta", attrs={"property": "og:url"})
    if og_url_tag:
        metadata["og_url"] = og_url_tag.get("content")

    # Twitter Card Metadata
    twitter_title_tag = soup.find("meta", attrs={"name": "twitter:title"})
    if twitter_title_tag:
        metadata["twitter_title"] = twitter_title_tag.get("content")

    twitter_description_tag = soup.find("meta", attrs={"name": "twitter:description"})
    if twitter_description_tag:
        metadata["twitter_description"] = twitter_description_tag.get("content")

    twitter_image_tag = soup.find("meta", attrs={"name": "twitter:image"})
    if twitter_image_tag:
        metadata["twitter_image"] = twitter_image_tag.get("content")

    # Canonical link
    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    if canonical_tag:
        metadata["canonical"] = canonical_tag.get("href")

    # H1 tag
    h1_tag = soup.find("h1")
    metadata["h1"] = h1_tag.get_text(strip=True) if h1_tag else None

    return metadata

# Function to rate SEO metadata completeness (0-5)
def rate_seo_metadata(metadata):
    """
    Rate SEO Metadata based on:
    - Presence of key tags
    - Correctness of metadata
    """
    score = 0
    flaws = []

    # Check if key SEO elements are present
    if metadata["title"]:
        score += 0.5
    else:
        flaws.append("Missing title tag.")

    if metadata["description"]:
        score += 0.5
    else:
        flaws.append("Missing meta description.")

    if metadata["keywords"]:
        score += 0.5
    else:
        flaws.append("Missing meta keywords.")

    if metadata["og_title"]:
        score += 0.5
    else:
        flaws.append("Missing Open Graph title (og:title).")

    if metadata["og_description"]:
        score += 0.5
    else:
        flaws.append("Missing Open Graph description (og:description).")

    if metadata["og_image"]:
        score += 0.5
    else:
        flaws.append("Missing Open Graph image (og:image).")

    if metadata["og_url"]:
        score += 0.5
    else:
        flaws.append("Missing Open Graph URL (og:url).")

    if metadata["twitter_title"]:
        score += 0.5
    else:
        flaws.append("Missing Twitter card title (twitter:title).")

    if metadata["twitter_description"]:
        score += 0.5
    else:
        flaws.append("Missing Twitter card description (twitter:description).")

    if metadata["twitter_image"]:
        score += 0.5
    else:
        flaws.append("Missing Twitter card image (twitter:image).")

    if metadata["canonical"]:
        score += 0.5
    else:
        flaws.append("Missing canonical link.")

    # H1 tag check
    if metadata.get("h1"):
        score += 0.5
    else:
        flaws.append("Missing H1 tag.")

    # Penalize if the meta keywords are missing (they still matter, even if not as much)
    if not metadata["keywords"]:
        score -= 0.5  # Penalize for missing keywords

    # Cap the score at 5 and ensure it's not negative
    score = max(0, min(score, 5))

    return score, flaws

# Main function
def main():
    website = input("Enter website link (e.g., example.com): ").strip()
    url = normalize_url(website)

    if not url:
        print("Invalid URL input.")
        return

    # Check SEO metadata
    metadata = check_seo_metadata(url)

    if metadata is None:
        print("Could not fetch SEO metadata from the website.")
        return

    # Print SEO Metadata
    print("\n=== SEO META DATA FOUND ===")
    for key, value in metadata.items():
        print(f"{key}: {value}")

    # Rate the SEO metadata
    score, flaws = rate_seo_metadata(metadata)

    # Print rating and flaws
    print("\n=== RATING (0–5) ===")
    print(f"SEO Metadata Score: {score}/5")

    if flaws:
        print("\n=== FLAWS ===")
        for idx, flaw in enumerate(flaws, 1):
            print(f"{idx}. {flaw}")
    else:
        print("No major SEO flaws detected.")

if __name__ == "__main__":
    main()
