"""
One-time script to obtain a Gmail API refresh token.

Steps:
  1. Go to https://console.cloud.google.com/
  2. Create a project → Enable Gmail API
  3. OAuth consent screen → External → add your email as test user
  4. Credentials → Create → OAuth 2.0 Client ID → Desktop app
  5. Download the JSON → paste client_id and client_secret below (or pass as args)
  6. Run:  python scripts/gmail_auth.py
  7. A browser window opens — sign in and grant access
  8. Copy the GMAIL_REFRESH_TOKEN printed at the end into your .env

Usage:
    python scripts/gmail_auth.py --client-id YOUR_ID --client-secret YOUR_SECRET
"""
import argparse
import sys
import os

# Allow running from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

SCOPES = ["https://mail.google.com/"]


def main():
    parser = argparse.ArgumentParser(description="Obtain Gmail API refresh token")
    parser.add_argument("--client-id", help="OAuth2 Client ID")
    parser.add_argument("--client-secret", help="OAuth2 Client Secret")
    args = parser.parse_args()

    client_id = args.client_id
    client_secret = args.client_secret

    # Fall back to .env values if available
    if not client_id or not client_secret:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            client_id = client_id or os.getenv("GMAIL_CLIENT_ID")
            client_secret = client_secret or os.getenv("GMAIL_CLIENT_SECRET")
        except ImportError:
            pass

    if not client_id or not client_secret:
        print("ERROR: Provide --client-id and --client-secret, or set GMAIL_CLIENT_ID/SECRET in .env")
        sys.exit(1)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("ERROR: Run: pip install google-auth-oauthlib")
        sys.exit(1)

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)

    print("\n" + "=" * 60)
    print("SUCCESS! Add these to your .env file:")
    print("=" * 60)
    print(f"GMAIL_CLIENT_ID={client_id}")
    print(f"GMAIL_CLIENT_SECRET={client_secret}")
    print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
