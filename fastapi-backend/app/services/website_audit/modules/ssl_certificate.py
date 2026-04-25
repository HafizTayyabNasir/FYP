import socket
import ssl
import datetime
from urllib.parse import urlparse
import urllib3

import requests

# Disable SSL warnings for audit purposes
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ----------------------------
# Helpers
# ----------------------------
def normalize_input_url(user_input: str):
    user_input = user_input.strip()
    if not user_input:
        return None, None, None

    if not user_input.startswith(("http://", "https://")):
        user_input = "https://" + user_input

    parsed = urlparse(user_input)
    host = parsed.netloc or parsed.path
    host = host.split("/")[0].strip()

    if not host:
        return None, None, None

    http_url = f"http://{host}"
    https_url = f"https://{host}"
    return host, http_url, https_url


def parse_cert_time(date_str: str) -> datetime.datetime:
    # e.g. 'Jun  5 12:00:00 2026 GMT'
    return datetime.datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z")


def classify_ssl_error(err: Exception) -> str:
    """
    Gives a readable category for common SSL failures.
    """
    msg = str(err).lower()

    if isinstance(err, ssl.SSLCertVerificationError):
        # Common cert verification failures
        if "self signed" in msg:
            return "self_signed_certificate"
        if "hostname" in msg or "doesn't match" in msg:
            return "hostname_mismatch"
        if "expired" in msg:
            return "certificate_expired"
        return "certificate_verification_failed"

    if isinstance(err, ssl.SSLError):
        if "wrong version number" in msg or "protocol version" in msg:
            return "tls_protocol_error"
        if "handshake failure" in msg:
            return "handshake_failure"
        return "ssl_error"

    if isinstance(err, socket.timeout):
        return "timeout"

    return "connection_error"


# ----------------------------
# Checks
# ----------------------------
def check_https_access(https_url: str, timeout: int = 10):
    """
    Attempts to access HTTPS URL using requests.
    Returns: (ok, status_code, error_str)
    """
    try:
        # First try with SSL verification
        r = requests.get(https_url, timeout=timeout, headers=DEFAULT_HEADERS, verify=True, allow_redirects=True)
        return True, r.status_code, None
    except requests.exceptions.SSLError as e:
        # SSL verification failed - still HTTPS works but cert issue
        try:
            r = requests.get(https_url, timeout=timeout, headers=DEFAULT_HEADERS, verify=False, allow_redirects=True)
            return True, r.status_code, "SSL verification failed but HTTPS accessible"
        except Exception as e2:
            return False, None, f"SSL error: {e}"
    except Exception as e:
        return False, None, str(e)


def fetch_certificate(host: str, port: int = 443, timeout: int = 6):
    """
    Fetch certificate with verification enabled and SNI set,
    which helps detect hostname mismatch & self-signed certs.
    Returns: (cert_dict, error_category, error_message)
    """
    try:
        context = ssl.create_default_context()  # verification ON
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                return cert, None, None
    except Exception as e:
        return None, classify_ssl_error(e), str(e)


def evaluate_certificate_dates(cert: dict):
    """
    Correct certificate validity logic:
    cert is valid only if now is within [notBefore, notAfter].
    Returns: (cert_ok, not_before, not_after, days_left, flaws)
    """
    flaws = []
    now = datetime.datetime.utcnow()

    try:
        not_before = parse_cert_time(cert["notBefore"])
        not_after = parse_cert_time(cert["notAfter"])
    except Exception as e:
        return False, None, None, None, [f"Could not parse certificate validity dates ({e})."]

    # Correct validity check
    cert_ok = True
    if now < not_before:
        cert_ok = False
        flaws.append("Certificate is not valid yet (start date is in the future).")
    if now > not_after:
        cert_ok = False
        flaws.append("Certificate is expired.")

    days_left = (not_after - now).days

    if cert_ok:
        if days_left < 30:
            flaws.append(f"Certificate expires soon (in {days_left} days).")

    return cert_ok, not_before, not_after, days_left, flaws


def check_http_redirect(http_url: str, timeout: int = 10):
    """
    Checks whether HTTP redirects to HTTPS.
    Returns: (redirects_to_https, final_url, first_redirect_code, hsts_present, flaws)
    """
    flaws = []
    try:
        r = requests.get(http_url, allow_redirects=True, timeout=timeout, headers=DEFAULT_HEADERS, verify=False)

        final_url = r.url
        redirects_to_https = final_url.startswith("https://")

        # Find first redirect response code (if any)
        first_redirect_code = None
        if r.history:
            first_redirect_code = r.history[0].status_code

        # Check HSTS header on final HTTPS response (best practice)
        hsts_present = "strict-transport-security" in {k.lower(): v for k, v in r.headers.items()}

        if not redirects_to_https:
            flaws.append(f"HTTP does not redirect to HTTPS (final URL: {final_url}).")
        else:
            # extra insight: 301 is preferred for permanent redirect
            if first_redirect_code and first_redirect_code != 301:
                flaws.append(f"HTTP→HTTPS redirect is not permanent (first redirect code: {first_redirect_code}).")

        return redirects_to_https, final_url, first_redirect_code, hsts_present, flaws

    except Exception as e:
        return False, None, None, False, [f"Could not test HTTP redirect ({e})."]


# ----------------------------
# Rating Logic (0–5)
# ----------------------------
def rate_ssl(has_https: bool, cert_ok: bool, days_left, redirects_https: bool, hsts_present: bool):
    """
    Updated scoring:
    0 = HTTPS not accessible
    1 = HTTPS accessible but certificate invalid (expired/not-yet-valid/self-signed/mismatch)
    2 = Cert OK but no HTTP->HTTPS redirect
    3 = Redirect OK but no HSTS OR expiry soon (<15 days)
    4 = Good: redirect OK, HSTS ok or missing minor, expiry <30 days
    5 = Great: cert valid, redirect ok, HSTS present, expiry >=30 days
    """
    if not has_https:
        return 0
    if not cert_ok:
        return 1
    if not redirects_https:
        return 2

    # from here: HTTPS + cert valid + redirect ok
    if days_left is not None and days_left < 15:
        return 3

    if not hsts_present:
        # still okay but not best practice
        return 4 if (days_left is None or days_left >= 30) else 3

    if days_left is not None and days_left < 30:
        return 4

    return 5


# ----------------------------
# Main
# ----------------------------
def main():
    website = input("Enter website link (e.g., example.com): ").strip()
    host, http_url, https_url = normalize_input_url(website)

    if not host:
        print("Invalid input.")
        return

    flaws = []
    ssl_state = "unknown"

    # 1) HTTPS availability
    https_ok, status_code, https_err = check_https_access(https_url)
    if not https_ok:
        ssl_state = "no_https_or_ssl_failure"
        flaws.append(f"HTTPS is not accessible ({https_err}).")
    else:
        if status_code is not None and status_code >= 400:
            flaws.append(f"HTTPS returns HTTP status {status_code} (site may be misconfigured).")

    # 2) Certificate fetch + verify
    cert_ok = False
    days_left = None
    cert_type_issue = None

    cert, cert_err_type, cert_err_msg = fetch_certificate(host)
    if cert is None:
        # When verification fails, categorize the failure
        ssl_state = "invalid_certificate"
        cert_type_issue = cert_err_type

        if cert_err_type == "self_signed_certificate":
            flaws.append("Certificate is self-signed (not trusted by browsers).")
        elif cert_err_type == "hostname_mismatch":
            flaws.append("Certificate hostname mismatch (domain does not match certificate).")
        elif cert_err_type == "certificate_expired":
            flaws.append("Certificate is expired.")
        elif cert_err_type == "certificate_verification_failed":
            flaws.append("Certificate verification failed (untrusted/invalid certificate chain).")
        else:
            flaws.append(f"Could not verify SSL certificate ({cert_err_type}: {cert_err_msg}).")
    else:
        cert_ok, nb, na, days_left, cert_flaws = evaluate_certificate_dates(cert)
        flaws.extend(cert_flaws)
        ssl_state = "valid_certificate" if cert_ok else "invalid_certificate"

    # 3) HTTP -> HTTPS redirect + HSTS
    redirects_https, final_url, first_code, hsts_present, redirect_flaws = check_http_redirect(http_url)
    flaws.extend(redirect_flaws)

    if https_ok and cert_ok and redirects_https:
        if not hsts_present:
            flaws.append("HSTS header is missing (browser not forced to use HTTPS after first visit).")

    # Rating
    rating = rate_ssl(https_ok, cert_ok, days_left, redirects_https, hsts_present)

    # Output
    print("\n=== SSL CHECK RESULT ===")
    print(f"Website: {host}")
    print(f"HTTPS accessible: {'YES' if https_ok else 'NO'}")
    print(f"SSL state: {ssl_state}")

    if cert_type_issue:
        print(f"Certificate issue type: {cert_type_issue}")

    print(f"Certificate valid: {'YES' if cert_ok else 'NO'}")
    if days_left is not None:
        print(f"Certificate days left: {days_left}")

    print(f"HTTP -> HTTPS redirect: {'YES' if redirects_https else 'NO'}")
    if final_url:
        print(f"Final URL after redirect test: {final_url}")
    print(f"HSTS present: {'YES' if hsts_present else 'NO'}")

    print("\n=== RATING (0–5) ===")
    print(f"SSL Score: {rating}/5")

    print("\n=== FLAWS ===")
    if flaws:
        # de-duplicate while preserving order
        seen = set()
        cleaned = []
        for f in flaws:
            if f not in seen:
                cleaned.append(f)
                seen.add(f)

        for i, f in enumerate(cleaned, 1):
            print(f"{i}. {f}")
    else:
        print("No major SSL flaws found.")


if __name__ == "__main__":
    main()
