from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse
import re

# ==============================
# Configuration
# ==============================

MAX_PAGES = 15
TIMEOUT_MS = 20000
STABILITY_WAIT_MS = 800

ALT_MAX_LENGTH = 125
ALT_MIN_LENGTH = 3

GENERIC_ALTS = {
    "image", "photo", "picture", "pic", "banner",
    "logo", "icon", "graphic", "img", "slider"
}


# ==============================
# Utility Functions
# ==============================

def normalize_url(url):
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def same_domain(url, base_host):
    return urlparse(url).netloc == base_host


def evaluate_alt(src, alt):
    issues = []

    if alt is None:
        issues.append("Missing alt attribute.")
        return issues

    alt = alt.strip()

    if alt == "":
        issues.append("Empty alt text.")

    if len(alt) < ALT_MIN_LENGTH and alt != "":
        issues.append("Alt text too short.")

    if len(alt) > ALT_MAX_LENGTH:
        issues.append("Alt text too long.")

    if alt.lower() in GENERIC_ALTS:
        issues.append("Generic alt text.")

    if re.search(r"\.(jpg|png|jpeg|webp|gif|svg)", alt.lower()):
        issues.append("Alt text looks like filename.")

    words = alt.lower().split()
    if len(words) > 10 and len(set(words)) < len(words) * 0.6:
        issues.append("Possible keyword stuffing.")

    return issues


def rate_score(total_images, images_with_issues):
    if total_images == 0:
        return 3.0

    good = total_images - images_with_issues
    ratio = good / total_images

    if ratio >= 0.95:
        return 5
    if ratio >= 0.85:
        return 4
    if ratio >= 0.70:
        return 3
    if ratio >= 0.50:
        return 2
    if ratio >= 0.30:
        return 1
    return 0


# ==============================
# Main Auditor
# ==============================

def audit_alt_tags(website):

    website = normalize_url(website)
    parsed = urlparse(website)
    base_host = parsed.netloc
    base_origin = f"{parsed.scheme}://{parsed.netloc}"

    total_images = 0
    images_with_issues = 0
    pages_checked = 0
    page_issue_map = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        page = context.new_page()

        try:
            page.goto(website, timeout=TIMEOUT_MS)
            page.wait_for_timeout(STABILITY_WAIT_MS)
        except:
            print("Could not load website.")
            return

        # Collect internal links
        links = page.eval_on_selector_all(
            "a[href]",
            "elements => elements.map(e => e.href)"
        )

        internal_links = []
        for link in links:
            if same_domain(link, base_host):
                internal_links.append(link)

        # Limit pages
        internal_links = list(set(internal_links))[:MAX_PAGES]
        internal_links.insert(0, website)

        # Audit each page
        for url in internal_links:
            try:
                page.goto(url, timeout=TIMEOUT_MS)
                page.wait_for_timeout(STABILITY_WAIT_MS)
            except:
                continue

            pages_checked += 1
            page_issues = 0

            images = page.eval_on_selector_all(
                "img",
                "imgs => imgs.map(img => ({src: img.src, alt: img.getAttribute('alt')}))"
            )

            for img in images:
                total_images += 1
                issues = evaluate_alt(img["src"], img["alt"])
                if issues:
                    images_with_issues += 1
                    page_issues += 1

            if page_issues > 0:
                page_issue_map[url] = page_issues

        browser.close()

    score = rate_score(total_images, images_with_issues)

    # ==========================
    # Print Report
    # ==========================

    print("\n=================================")
    print("IMAGE ALT TAGS AUDIT REPORT")
    print("=================================")

    print(f"Website: {website}")
    print(f"Pages Checked: {pages_checked}")
    print(f"Total Images: {total_images}")
    print(f"Images with Issues: {images_with_issues}")
    print(f"Overall ALT Score (0–5): {score}/5")

    print("\n--- Pages with ALT Issues ---")
    if page_issue_map:
        for page_url, count in page_issue_map.items():
            print(f"{page_url}  →  {count} issues")
    else:
        print("No ALT issues found.")

    print("\n--- Flaws ---")
    if images_with_issues == 0:
        print("All images contain properly structured ALT attributes.")
    else:
        print("Some images are missing ALT text or have weak/non-descriptive ALT attributes.")
        print("This affects SEO and accessibility compliance.")


# ==============================
# Entry Point (Fixed)
# ==============================

if __name__ == "__main__":
    website = input("Enter website link (e.g., example.com): ").strip()

    if not website:
        print("Invalid input.")
    else:
        audit_alt_tags(website)