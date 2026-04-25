import os
import re
from urllib.parse import urlparse, urljoin

from playwright.sync_api import sync_playwright

# -------------------------
# Config
# -------------------------
MOBILE_VIEWPORT = {"width": 390, "height": 844}       # phone-like
DESKTOP_VIEWPORT = {"width": 1366, "height": 768}     # laptop-like

STABILITY_WAIT_MS = 1000
TIMEOUT_MS = 25000

MAX_PAGES_TO_CHECK = 15
CRAWL_LIMIT_LINKS = 80
MEDIA_QUERY = "(max-width: 768px)"

# ✅ Screenshots: always save OK screenshots + save issue screenshots if issues exist
ALWAYS_SAVE_SCREENSHOTS = True


# -------------------------
# Utilities
# -------------------------
def normalize_url(user_input: str) -> str:
    user_input = user_input.strip()
    if not user_input:
        return ""
    if not user_input.startswith(("http://", "https://")):
        user_input = "https://" + user_input
    return user_input


def safe_name(text: str) -> str:
    text = text.replace(":", "_")
    text = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", text)
    return text[:140] if text else "site"


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def clean_url(url: str) -> str:
    return url.split("#")[0]


def same_domain(url: str, base_host: str) -> bool:
    return (urlparse(url).netloc or "") == base_host


# -------------------------
# Playwright checks
# -------------------------
def has_viewport_meta(page) -> bool:
    return page.evaluate("""() => !!document.querySelector('meta[name="viewport"]')""")


def horizontal_overflow(page) -> bool:
    return page.evaluate(
        """() => {
            const doc = document.documentElement;
            const body = document.body;
            const scrollW = Math.max(doc.scrollWidth, body ? body.scrollWidth : 0);
            const clientW = doc.clientWidth;
            return scrollW > clientW + 2; // tolerance
        }"""
    )


def media_query_match(page, query: str) -> bool:
    return page.evaluate("""(q) => window.matchMedia(q).matches""", query)


def save_screenshot(page, path: str):
    try:
        page.screenshot(path=path, full_page=True)
        print(f"📸 Saved screenshot: {path}")
    except Exception as e:
        print(f"❌ Screenshot failed: {path} | Error: {e}")


# -------------------------
# Rating logic
# -------------------------
def rate_page(mobile_ok: bool, desktop_ok: bool, viewport_ok: bool, mq_ok: bool) -> int:
    """
    Page rating (0–5)
    """
    if not mobile_ok and not desktop_ok:
        return 0
    if (not mobile_ok and desktop_ok) or (mobile_ok and not desktop_ok):
        return 2
    # both ok by load+overflow
    if not viewport_ok or not mq_ok:
        return 3
    return 5


def overall_rating_from_average(page_results):
    if not page_results:
        return 0
    avg = sum(r["rating"] for r in page_results) / len(page_results)
    score = int(round(avg))
    return max(0, min(5, score))


# -------------------------
# Crawl internal pages
# -------------------------
def crawl_internal_pages(page, base_url: str, max_links: int = 80):
    parsed = urlparse(base_url)
    base_host = parsed.netloc
    base_origin = f"{parsed.scheme}://{base_host}"

    page.goto(base_url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)
    page.wait_for_timeout(STABILITY_WAIT_MS)

    hrefs = page.evaluate(
        """() => Array.from(document.querySelectorAll('a[href]'))
            .map(a => a.getAttribute('href'))
            .filter(Boolean)
        """
    )

    urls = []
    seen = set()

    base_clean = clean_url(base_url)
    seen.add(base_clean)
    urls.append(base_clean)

    for href in hrefs:
        if len(urls) >= max_links:
            break

        abs_url = clean_url(urljoin(base_origin + "/", href))

        if not abs_url.startswith(("http://", "https://")):
            continue
        if not same_domain(abs_url, base_host):
            continue

        low = abs_url.lower()
        if any(x in low for x in ["logout", "cart", "checkout", "wp-admin", "signin", "login"]):
            continue

        if abs_url not in seen:
            seen.add(abs_url)
            urls.append(abs_url)

    return urls


# -------------------------
# Test view for one page
# -------------------------
def test_view(page, url: str, expected_mobile: bool, screenshots_dir: str, prefix: str):
    """
    Returns dict: loaded, overflow, viewport_meta, mq_match, issues(list)
    Saves screenshots:
      - prefix_ok.png always (if loaded)
      - prefix_issue.png if issues exist
      - prefix_load_error.png if load fails
    """
    issues = []
    out = {
        "loaded": False,
        "overflow": False,
        "viewport_meta": False,
        "mq_match": False,
        "issues": issues,
    }

    ok_path = os.path.join(screenshots_dir, f"{prefix}_ok.png")
    issue_path = os.path.join(screenshots_dir, f"{prefix}_issue.png")
    error_path = os.path.join(screenshots_dir, f"{prefix}_load_error.png")

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)
        page.wait_for_timeout(STABILITY_WAIT_MS)

        out["loaded"] = True
        out["viewport_meta"] = has_viewport_meta(page)
        out["overflow"] = horizontal_overflow(page)
        out["mq_match"] = media_query_match(page, MEDIA_QUERY)

        if out["overflow"]:
            issues.append("Horizontal overflow detected (content wider than screen).")

        if not out["viewport_meta"]:
            issues.append("Viewport meta tag missing (weak mobile scaling).")

        if expected_mobile and not out["mq_match"]:
            issues.append(f'Media query "{MEDIA_QUERY}" did not match on mobile viewport (breakpoints may be missing).')
        if (not expected_mobile) and out["mq_match"]:
            issues.append(f'Media query "{MEDIA_QUERY}" matched on desktop viewport (unexpected breakpoint behavior).')

        # Always save OK screenshot if requested
        if ALWAYS_SAVE_SCREENSHOTS:
            save_screenshot(page, ok_path)

        # Save issue screenshot if issues found
        if issues:
            save_screenshot(page, issue_path)

    except Exception as e:
        issues.append(f"Page failed to load: {e}")
        save_screenshot(page, error_path)

    return out


# -------------------------
# Overall Responsiveness Points (summary)
# -------------------------
def compute_overall_points(results):
    """
    Builds overall point-based responsiveness summary:
      1) Mobile layout fit (no overflow on mobile)
      2) Desktop layout fit (no overflow on desktop)
      3) Viewport meta presence
      4) Breakpoints/media query behaves correctly
    """
    total = len(results)
    if total == 0:
        return {}

    mobile_fit_pass = sum(1 for r in results if r["mobile_loaded"] and not r["mobile_overflow"])
    desktop_fit_pass = sum(1 for r in results if r["desktop_loaded"] and not r["desktop_overflow"])
    viewport_pass = sum(1 for r in results if r["viewport_ok"])
    breakpoints_pass = sum(1 for r in results if r["mq_ok"] and r["mobile_loaded"] and r["desktop_loaded"])

    # Convert to percentage
    def pct(x): return round((x / total) * 100, 1)

    return {
        "total_pages_checked": total,
        "mobile_layout_fit": (mobile_fit_pass, total, pct(mobile_fit_pass)),
        "desktop_layout_fit": (desktop_fit_pass, total, pct(desktop_fit_pass)),
        "viewport_meta": (viewport_pass, total, pct(viewport_pass)),
        "responsive_breakpoints": (breakpoints_pass, total, pct(breakpoints_pass)),
    }


# -------------------------
# Main
# -------------------------
def main():
    website = input("Enter website link (e.g., example.com): ").strip()
    base_url = normalize_url(website)
    if not base_url:
        print("Invalid input.")
        return

    parsed = urlparse(base_url)
    base_host = parsed.netloc
    domain_folder = safe_name(base_host or base_url)

    root_screens_dir = os.path.join(os.getcwd(), f"screenshots_{domain_folder}")
    ensure_dir(root_screens_dir)
    print(f"\n📁 Screenshots root folder: {root_screens_dir}")

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Crawl
        crawl_ctx = browser.new_context(viewport=DESKTOP_VIEWPORT)
        crawl_page = crawl_ctx.new_page()

        try:
            found_pages = crawl_internal_pages(crawl_page, base_url, max_links=CRAWL_LIMIT_LINKS)
        except Exception as e:
            print(f"Could not crawl pages: {e}")
            found_pages = [base_url]

        crawl_ctx.close()

        pages_to_check = found_pages[:MAX_PAGES_TO_CHECK]

        # Contexts for checking
        desktop_ctx = browser.new_context(viewport=DESKTOP_VIEWPORT)
        desktop_page = desktop_ctx.new_page()

        mobile_ctx = browser.new_context(
            viewport=MOBILE_VIEWPORT,
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
            ),
            is_mobile=True,
            has_touch=True,
        )
        mobile_page = mobile_ctx.new_page()

        print("\nPages being checked:")
        for i, u in enumerate(pages_to_check, 1):
            print(f"{i}. {u}")

        for idx, url in enumerate(pages_to_check, 1):
            page_folder = safe_name(url.replace("https://", "").replace("http://", ""))
            page_screens_dir = os.path.join(root_screens_dir, f"page_{idx}_{page_folder}")
            ensure_dir(page_screens_dir)

            print(f"\n--- Checking page {idx}/{len(pages_to_check)} ---")
            print(f"URL: {url}")
            print(f"📁 Page screenshots folder: {page_screens_dir}")

            desktop_res = test_view(desktop_page, url, expected_mobile=False, screenshots_dir=page_screens_dir, prefix="desktop")
            mobile_res = test_view(mobile_page, url, expected_mobile=True, screenshots_dir=page_screens_dir, prefix="mobile")

            desktop_loaded = desktop_res["loaded"]
            mobile_loaded = mobile_res["loaded"]

            desktop_overflow = desktop_res["overflow"]
            mobile_overflow = mobile_res["overflow"]

            desktop_ok = desktop_loaded and not desktop_overflow
            mobile_ok = mobile_loaded and not mobile_overflow

            viewport_ok = mobile_res["viewport_meta"] or desktop_res["viewport_meta"]
            mq_ok = (mobile_res["mq_match"] is True) and (desktop_res["mq_match"] is False)

            rating = rate_page(mobile_ok, desktop_ok, viewport_ok, mq_ok)

            issues = []
            if mobile_loaded and mobile_overflow:
                issues.append("Page is not responsive on mobile (horizontal scrolling / overflow).")
            if desktop_loaded and desktop_overflow:
                issues.append("Page is not responsive on PC screen (horizontal scrolling / overflow).")
            if (mobile_loaded or desktop_loaded) and not viewport_ok:
                issues.append("Viewport meta tag missing (weak mobile scaling).")
            if (mobile_loaded and desktop_loaded) and not mq_ok:
                issues.append(f'Responsive breakpoints may be incorrect (media query "{MEDIA_QUERY}" behavior unexpected).')

            # Add detailed issues from views
            for it in desktop_res["issues"]:
                issues.append(f"Desktop: {it}")
            for it in mobile_res["issues"]:
                issues.append(f"Mobile: {it}")

            # De-duplicate issues
            seen = set()
            cleaned = []
            for it in issues:
                if it not in seen:
                    cleaned.append(it)
                    seen.add(it)

            results.append({
                "url": url,
                "rating": rating,
                "issues": cleaned,
                "screenshots_dir": page_screens_dir,

                # store these for overall points
                "mobile_loaded": mobile_loaded,
                "desktop_loaded": desktop_loaded,
                "mobile_overflow": mobile_overflow,
                "desktop_overflow": desktop_overflow,
                "viewport_ok": viewport_ok,
                "mq_ok": mq_ok,
            })

        mobile_ctx.close()
        desktop_ctx.close()
        browser.close()

    # Overall rating
    overall_rating = overall_rating_from_average(results)

    # Overall points summary
    points = compute_overall_points(results)

    pages_with_issues = [r for r in results if r["rating"] < 4 or any("not responsive" in x.lower() for x in r["issues"])]

    # Output report
    print("\n\n==============================")
    print("ALL-PAGES RESPONSIVENESS REPORT")
    print("==============================")
    print(f"Website: {base_host or base_url}")
    print(f"Pages checked: {len(results)} (limit: {MAX_PAGES_TO_CHECK})")
    print(f"📁 Screenshots root folder: {root_screens_dir}")

    print("\n=== OVERALL RATING (0–5) ===")
    print(f"Overall Responsiveness Score: {overall_rating}/5")

    print("\n=== OVERALL RESPONSIVENESS POINTS (SUMMARY) ===")
    if points:
        mf = points["mobile_layout_fit"]
        df = points["desktop_layout_fit"]
        vp = points["viewport_meta"]
        bp = points["responsive_breakpoints"]

        print(f"1) Mobile Layout Fit (no overflow): {mf[0]}/{mf[1]} pages PASS  ({mf[2]}%)")
        print(f"2) Desktop Layout Fit (no overflow): {df[0]}/{df[1]} pages PASS ({df[2]}%)")
        print(f"3) Viewport Meta Tag Present: {vp[0]}/{vp[1]} pages PASS ({vp[2]}%)")
        print(f"4) Responsive Breakpoints Working (media query): {bp[0]}/{bp[1]} pages PASS ({bp[2]}%)")
    else:
        print("No pages could be tested, so overall points cannot be computed.")

    print("\n=== PAGE-BY-PAGE SCORES ===")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['rating']}/5  -  {r['url']}")

    print("\n=== PAGES WITH RESPONSIVENESS ISSUES ===")
    if not pages_with_issues:
        print("No major responsiveness issues detected across checked pages.")
    else:
        for i, r in enumerate(pages_with_issues, 1):
            print(f"\n{i}) Page: {r['url']}")
            print(f"   Score: {r['rating']}/5")
            print(f"   Screenshots: {r['screenshots_dir']}")
            for j, issue in enumerate(r["issues"], 1):
                print(f"   {j}. {issue}")

    print("\n=== FINAL VERDICT ===")
    if overall_rating >= 4:
        print("Responsive: YES (overall good responsiveness across pages)")
    elif overall_rating >= 2:
        print("Responsive: PARTIALLY (some pages have responsiveness issues)")
    else:
        print("Responsive: NO (major responsiveness issues across pages)")


if __name__ == "__main__":
    main()