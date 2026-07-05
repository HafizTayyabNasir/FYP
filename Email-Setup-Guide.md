# 📧 Email Setup Guide — User & Admin Reference

> How to connect and verify email accounts in AI Client Hunting & OutReach Platform

---

## 📋 Table of Contents

1. [Overview — How Email Works in This Platform](#overview)
2. [For Users: Connecting Your Email](#for-users)
3. [Option A: Connect Gmail / Google Workspace](#option-a-google)
4. [Option B: Connect Business Email (SMTP)](#option-b-smtp)
5. [Sending Outreach Emails](#sending-outreach)
6. [For Admins: Setting Up OAuth Providers](#for-admins)
7. [Admin Setup A: Google Cloud Console](#admin-google)
8. [Troubleshooting](#troubleshooting)

---

## Overview

Is platform mein **do tarah ki emails** hain:

| Email Type | Kahan se jati hai | Kaun set karta hai |
|---|---|---|
| **Platform Emails** (verification, reset) | Resend API se → `noresponse@elvionsolutions.com` | Admin (.env mein configured) |
| **Outreach Emails** (client emails) | User ke apne email account se | User khud connect karta hai |

### Supported Providers

| Provider | Email Examples | Connection Method |
|---|---|---|
| Gmail | `user@gmail.com` | Google OAuth (1 click) |
| Google Workspace | `ceo@company.com` (G Suite) | Google OAuth (1 click) |
| Hostinger | `info@company.com` | SMTP credentials |
| GoDaddy | `contact@business.com` | SMTP credentials |
| Zoho Mail | `admin@company.com` | SMTP credentials |
| cPanel / Custom | `hello@mydomain.com` | SMTP credentials |

---

## For Users

### Step 1: Navigate to Email Accounts

1. Login to your account
2. Click **"Email Accounts"** in the left sidebar (under System)
3. Or go to **Settings → Email Accounts**

### Step 2: Click "+ Add Account"

You will see 2 options:
- 🔵 **Continue with Google** — Gmail, Google Workspace
- ⚙️ **Other Email Provider (SMTP)** — Hostinger, GoDaddy, Zoho, cPanel

---

## Option A: Google

### Personal Gmail (`user@gmail.com`)

1. Click **"Continue with Google"**
2. Google login popup open hoga
3. Apna Gmail account select karein
4. Permission allow karein:
   - "View your email messages" ✅
   - "Send email on your behalf" ✅
5. Automatically redirect ho jayega aur account connected show hoga ✅

### Google Workspace (`ceo@company.com`)

Same process — sirf Google Workspace email se login karein. Agar aapke domain ka email Google par hosted hai to ye kaam karega.

> **Note:** Google Workspace admin ko pehle OAuth consent screen mein is app ko approve karna padega.

### Verification

Koi alag verification nahi chahiye. Google OAuth **automatically verify** karta hai k ye email aapki hai. Token securely encrypted ho kar database mein save hota hai.

---


### Ye Kab Use Karein

Agar aapki email **Hostinger, GoDaddy, Zoho, Namecheap, cPanel** ya kisi aur hosting provider se hai, to SMTP connection use hoga.

### Step-by-Step Setup

1. Click **"Other Email Provider (SMTP)"**

2. **Provider Select Karein** — preset buttons mein se choose karein:
   - Hostinger, GoDaddy, Zoho, Namecheap, cPanel, Gmail (SMTP)
   - Ye automatically SMTP host aur port fill kar dega

3. **Email Address** daalein — e.g. `info@company.com`

4. **Password** daalein — ye aapke email ka password hai
   > **Gmail ke liye:** Normal password kaam nahi karega. Aapko [App Password](https://myaccount.google.com/apppasswords) generate karna hoga.

5. **Display Name** daalein (optional) — e.g. "John from Company"

6. **"Test Connection"** click karein — ye verify karega k credentials sahi hain

7. Agar test successful ho to **"Connect Account"** click karein

### Common SMTP Settings (Auto-filled by Presets)

| Provider | SMTP Host | Port | IMAP Host | Port |
|---|---|---|---|---|
| Hostinger | `smtp.hostinger.com` | 587 | `imap.hostinger.com` | 993 |
| GoDaddy | `smtpout.secureserver.net` | 587 | `imap.secureserver.net` | 993 |
| Zoho | `smtp.zoho.com` | 587 | `imap.zoho.com` | 993 |
| Namecheap | `mail.privateemail.com` | 587 | `mail.privateemail.com` | 993 |
| cPanel | `mail.yourdomain.com` | 587 | `mail.yourdomain.com` | 993 |

### Advanced Settings

Agar preset kaam nahi kare to **"Advanced Settings"** expand karein aur manually daalein:
- SMTP Host & Port
- IMAP Host & Port

### SMTP Verification

SMTP mein **Test Connection** button verification ka kaam karta hai:
- Ye actual SMTP server se connect hota hai
- Login attempt karta hai aapke credentials ke saath
- Agar success ✅ → credentials sahi hain, account connect ho jayega
- Agar fail ❌ → password galat hai ya host/port incorrect hai

> **Important:** SMTP mein sirf email verify karna kafi nahi. Aapko email ka actual password chahiye. Bina password ke outreach email nahi ja sakti.

---

## Sending Outreach

### Step 1: Go to Email Generator

Left sidebar mein **"Email Generator"** click karein.

### Step 2: Select "Send From"

Compose Email section mein sab se pehle **"Send From"** dropdown hai:
- Agar accounts connected hain → dropdown mein show honge
- Default account pe ★ star hoga
- Koi bhi account select kar sakte hain

### Step 3: Generate & Send

1. Business details fill karein (ya audit se auto-fill hoga)
2. **"Generate Outreach Email"** click karein
3. AI email generate karega
4. Recipient email daalein (ya Find Email use karein)
5. Subject line select karein
6. Email edit karein (agar zaroorat ho)
7. **"Send Email"** click karein

Email **aapke selected account se** jayegi — recipient ko email exactly aapke email address se milegi.

---

## For Admins

### Admin Responsibilities

Admin ko **ek dafa** ye setup karna hota hai. Users ko in steps ki zaroorat nahi.

| Task | Where | Cost |
|---|---|---|
| Google OAuth App | Google Cloud Console | Free |
| Environment Variables | Render / .env | Free |

---

## Admin Google

### Google Cloud Console Setup

1. **Go to** [Google Cloud Console](https://console.cloud.google.com/)

2. **Create a new project** (ya existing select karein)

3. **Enable Gmail API:**
   - APIs & Services → Library → Search "Gmail API" → Enable

4. **Configure OAuth Consent Screen:**
   - APIs & Services → OAuth consent screen
   - User Type: **External**
   - App name: `AI Client Hunting`
   - Support email: your email
   - Scopes: Add these:
     - `https://www.googleapis.com/auth/gmail.send`
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/userinfo.email`
     - `https://www.googleapis.com/auth/userinfo.profile`
   - Test users: Add your test Gmail addresses
   - Save

5. **Create OAuth Credentials:**
   - APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID
   - Application type: **Web application**
   - Name: `AI Client Hunt Web`
   - Authorized redirect URIs: Add:
     ```
     http://localhost:8000/api/v1/email-accounts/google/callback
     https://your-backend.onrender.com/api/v1/email-accounts/google/callback
     ```
   - Click Create → Copy **Client ID** and **Client Secret**

6. **Add to .env:**
   ```env
   GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-your_secret
   ```

> **Production Note:** Jab tak OAuth app "Testing" mode mein hai, sirf test users hi connect kar sakte hain. Production mein Google verification submit karni padegi (1-3 weeks lagta hai).


### Google OAuth Errors

| Error | Solution |
|---|---|
| "Access blocked: App not verified" | Google Console → OAuth consent screen → Add user as test user |
| "redirect_uri_mismatch" | Check Authorized redirect URIs match exactly in Google Console |
| "invalid_grant" | User needs to re-connect (token expired) |

### SMTP Errors

| Error | Solution |
|---|---|
| "Authentication failed" | Check email and password. For Gmail use App Password |
| "Connection timed out" | Check SMTP host and port. Try port 465 (SSL) instead of 587 |
| "Connection refused" | Firewall blocking port. Contact hosting provider |
| "Certificate verify failed" | Some hosts need SSL instead of TLS. Try port 465 |

### General

| Issue | Solution |
|---|---|
| No accounts showing in dropdown | Go to Settings → Email Accounts and connect one |
| "Email not configured" error | Connect an account or set up .env credentials |
| Emails going to spam | Set up SPF, DKIM, DMARC records on your domain |

---

## Daily Sending Limits (Free)

| Provider | Free Limit |
|---|---|
| Gmail (personal) | 500 emails/day |
| Google Workspace | 2,000 emails/day |
| Hostinger SMTP | 500 emails/hour |
| Resend (platform) | 100 emails/day, 3,000/month |

---

> **Yaad rakhein:** Outreach emails user ke apne email account se jaati hain. Platform (Resend) sirf verification/notification ke liye hai. Is se deliverability behtar hoti hai aur emails spam mein nahi jaatein.
