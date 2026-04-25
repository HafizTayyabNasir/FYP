import time
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

TIMEOUT_MS = 30000

def normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def rate_load(load_ms: float) -> int:
    # Simple 0–5 rating (you can mention this in FYP)
    # < 2000ms: 5
    # 2000-4000: 4
    # 4000-6000: 3
    # 6000-9000: 2
    # 9000-12000: 1
    # > 12000: 0
    if load_ms < 2000: return 5
    if load_ms < 4000: return 4
    if load_ms < 6000: return 3
    if load_ms < 9000: return 2
    if load_ms < 12000: return 1
    return 0

def main():
    website = input("Enter website link (e.g., example.com): ").strip()
    url = normalize_url(website)
    if not url:
        print("Invalid input.")
        return

    flaws = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Track timing using Performance API
        start = time.perf_counter()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)
            dom_loaded = (time.perf_counter() - start) * 1000

            # Wait full load
            page.wait_for_load_state("load", timeout=TIMEOUT_MS)
            fully_loaded = (time.perf_counter() - start) * 1000

            # Grab detailed timing from browser
            timing = page.evaluate("""() => {
                const nav = performance.getEntriesByType('navigation')[0];
                if (!nav) return null;
                return {
                    dns: nav.domainLookupEnd - nav.domainLookupStart,
                    tcp: nav.connectEnd - nav.connectStart,
                    ttfb: nav.responseStart - nav.requestStart,
                    response_download: nav.responseEnd - nav.responseStart,
                    dom_content_loaded: nav.domContentLoadedEventEnd - nav.startTime,
                    load_event: nav.loadEventEnd - nav.startTime
                };
            }""")

        except Exception as e:
            print(f"Page load failed: {e}")
            browser.close()
            return

        browser.close()

    # Use load_event as “load time”
    load_ms = timing["load_event"] if timing else fully_loaded
    score = rate_load(load_ms)

    # Flaws based on thresholds
    if timing:
        if timing["ttfb"] > 800:
            flaws.append(f"High TTFB (server response is slow): {timing['ttfb']:.0f} ms")
        if timing["dns"] > 300:
            flaws.append(f"Slow DNS lookup: {timing['dns']:.0f} ms")
        if timing["tcp"] > 400:
            flaws.append(f"Slow TCP connection: {timing['tcp']:.0f} ms")

    if dom_loaded > 4000:
        flaws.append(f"DOM content loads slowly: {dom_loaded:.0f} ms")
    if load_ms > 6000:
        flaws.append(f"Full page load is slow: {load_ms:.0f} ms")

    host = urlparse(url).netloc

    print("\n=== WEBSITE LOAD TIME REPORT ===")
    print(f"Website: {host}")
    print(f"DOMContentLoaded: {dom_loaded:.0f} ms")
    print(f"Full Load (Load Event): {load_ms:.0f} ms")

    if timing:
        print("\n--- Detailed Timing (ms) ---")
        print(f"DNS: {timing['dns']:.0f}")
        print(f"TCP Connect: {timing['tcp']:.0f}")
        print(f"TTFB: {timing['ttfb']:.0f}")
        print(f"Response Download: {timing['response_download']:.0f}")

    print("\n=== RATING (0–5) ===")
    print(f"Load Speed Score: {score}/5")

    print("\n=== FLAWS ===")
    if flaws:
        for i, f in enumerate(flaws, 1):
            print(f"{i}. {f}")
    else:
        print("No major load-time issues detected.")

if __name__ == "__main__":
    main()
