# FastAPI Backend - Run Guide

## Prerequisites
Ensure Python 3.8+ is installed on your system.

## Installation

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Copy the example environment file and configure it:
```bash
cp .env.example .env
```
Edit `.env` with your configuration values (API keys, database URLs, etc.)

## Running the Application

### Development Mode (with auto-reload)
```bash
uvicorn app.main:app --host 127.0.0.1 --port 5000 --reload
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Using Makefile (if configured)
```bash
make run
```

## Access the Application
- **API**: http://127.0.0.1:5000
- **Interactive API Docs (Swagger)**: http://127.0.0.1:5000/docs
- **Alternative API Docs (ReDoc)**: http://127.0.0.1:5000/redoc

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, specify a different port:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### Database Connection Issues
Verify your database credentials in `.env` file and ensure the database service is running.

### Missing Dependencies
If you encounter missing package errors, reinstall dependencies:
```bash
pip install -r requirements.txt --upgrade
```