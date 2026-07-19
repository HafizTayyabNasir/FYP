# FastAPI Backend - Run Guide
## Prerequisites
- Python 3.8+ installed
- Git

## Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers (first time only)
```bash
playwright install chromium
```

### 5. Setup Environment Variables
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` and fill in your values:
- `GROQ_API_KEY` — get from https://console.groq.com
- `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN` — see Gmail API setup below
- `SMTP_FROM_NAME` — your name or company name

## Running the Application

### Development Mode (auto-reload)
```bash
uvicorn app.main:app --host 127.0.0.1 --port 5000 --reload
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Access the Application
- **App**: http://127.0.0.1:5000
- **Swagger API Docs**: http://127.0.0.1:5000/docs
- **ReDoc**: http://127.0.0.1:5000/redoc

## Gmail API Setup (for Email Dashboard)

Run this once to get your refresh token:
```bash
python scripts/gmail_auth.py --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
```

Steps:
1. Go to https://console.cloud.google.com → New Project → Enable **Gmail API**
2. OAuth consent screen → External → add your Gmail as a test user
3. Credentials → Create **OAuth 2.0 Client ID** → Desktop app
4. Run the command above — a browser window will open
5. Sign in and allow access
6. Copy the printed `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN` into `.env`

## Troubleshooting

### Port already in use
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### Missing package errors
```bash
pip install -r requirements.txt --upgrade
```

### `ddgs` module not found
```bash
pip install ddgs
```

### Groq API key not working
Make sure the key is set as `GROQ_API_KEY` in `.env` (not `GROK_API_KEY`). Keys starting with `gsk_` are Groq keys.



cd "d:\FYP\AI-Client-Hunting-OutReach-main\AI-Client-Hunting-OutReach-main\fastapi-backend"
venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 5000 --reload


cd "d:\FYP\AI-Client-Hunting-OutReach-main\AI-Client-Hunting-OutReach-main\nextjs-frontend"
npm run dev