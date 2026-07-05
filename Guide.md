# 🚀 A-Z Deployment Guide: AI-Client-Hunting-OutReach

This guide will walk you through the complete deployment process of your project. We will deploy the **Database on Supabase**, the **Backend on Render**, and the **Frontend on Vercel**. 

Follow these steps exactly in order.

---

## 🛠️ Step 1: Set up the Database on Supabase

1. Go to [Supabase](https://supabase.com/) and create an account / login.
2. Click **"New Project"**.
3. Name your project (e.g., `ai-client-hunting`), generate a strong **Database Password**, and select a region close to your users.
4. Click **"Create new project"** and wait a few minutes for the database to provision.
5. Once ready, go to **Project Settings** -> **Database**.
6. Scroll down to **Connection string** -> **URI**.
7. Copy the connection string. It will look like this:
   `postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres`
   *Note: If you are using SQLAlchemy with asyncpg in your FastAPI backend, you should modify it slightly:*
   `postgresql+asyncpg://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres`
8. Keep this URL safe; we will need it for the Backend deployment.

---

## ⚙️ Step 2: Deploy the Backend on Render (FastAPI)

Since the frontend needs to know the backend's URL, we deploy the backend *first*.

1. Push your latest code (including the `fastapi-backend` folder) to your GitHub repository.
2. Go to [Render](https://render.com/) and create an account / login.
3. Click **"New"** -> **"Web Service"**.
4. Connect your GitHub account and select your repository.
5. Configure the Web Service:
   * **Name**: `ai-client-hunting-backend` (or similar)
   * **Root Directory**: `fastapi-backend` *(Very Important!)*
   * **Environment**: `Python`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Scroll down to **Environment Variables** and click **"Add Environment Variable"**. Add all the necessary variables from your `.env.example`:

| Key | Value | Description |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.11.9` | Ensure Render uses the correct Python version. |
| `APP_NAME` | `AI Powered Client Hunt & Outreach` | Your App Name. |
| `DEBUG` | `False` | Turn off debug mode in production. |
| `SECRET_KEY` | `your-very-strong-secret-key` | Generate a secure random string for JWT encryption. |
| `ALLOWED_ORIGINS` | `https://your-frontend.vercel.app` | Update once Vercel gives a URL. |
| `FRONTEND_URL` | `https://your-frontend.vercel.app` | Same as above. |
| `BACKEND_URL` | `https://your-backend.onrender.com` | Your Render backend URL (for OAuth callbacks). |
| `DATABASE_URL` | *[Your Supabase URI from Step 1]* | The Supabase Database connection string. |
| `RESEND_API_KEY` | *[Your Resend API Key]* | Get from resend.com for platform emails. |
| `RESEND_FROM_EMAIL`| `noresponse@elvionsolutions.com` | Or your verified Resend domain email. |
| `RESEND_FROM_NAME` | `Elvion Solutions` | Sender Name. |
| `GROQ_API_KEY` | *[Your Groq API Key]* | Get from console.groq.com. |
| `OPENAI_API_KEY` | *[Your OpenAI Key]* | (Optional if using Groq primarily). |
| `OSM_CONTACT_EMAIL`| `your-email@gmail.com` | Email for OpenStreetMap requests. |
| `GOOGLE_CLIENT_ID` | *[Your Google OAuth Client ID]* | For Gmail email connections (see Email Setup Guide). |
| `GOOGLE_CLIENT_SECRET` | *[Your Google OAuth Client Secret]* | For Gmail email connections. |

7. Choose your instance type (Free tier works, but spins down when inactive) and click **"Create Web Service"**.
8. Wait for the deployment to finish. Once successful, Render will give you a URL (e.g., `https://ai-client-hunting-backend.onrender.com`). 
9. **Copy this Backend URL**. We need it for the frontend.

---

## 🌐 Step 3: Deploy the Frontend on Vercel (Next.js)

1. Go to [Vercel](https://vercel.com/) and login with GitHub.
2. Click **"Add New"** -> **"Project"**.
3. Import your GitHub repository.
4. Configure the Project:
   * **Project Name**: `ai-client-hunting`
   * **Framework Preset**: Vercel should automatically detect **Next.js**.
   * **Root Directory**: `nextjs-frontend` *(Very Important!)*
5. Open the **"Environment Variables"** section and add the following:

| Key | Value | Description |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | `https://ai-client-hunting-backend.onrender.com` | Paste the Render Backend URL you copied from Step 2. Do NOT add a trailing slash `/`. |

6. Click **"Deploy"**.
7. Vercel will build and deploy your Next.js application. Once done, Vercel will provide you with a production URL (e.g., `https://ai-client-hunting.vercel.app`).
8. **Copy this Vercel Frontend URL**.

---

## 🔄 Step 4: Final Connection (Updating Backend with Frontend URL)

Now that we have the Vercel Frontend URL, we need to tell our Render Backend to accept requests from it (CORS).

1. Go back to your [Render Dashboard](https://dashboard.render.com/) and open your Backend Web Service.
2. Go to the **Environment** tab.
3. Update the following Environment Variables with your actual Vercel URL:
   * `ALLOWED_ORIGINS`: `https://ai-client-hunting.vercel.app,http://localhost:3000`
   * `FRONTEND_URL`: `https://ai-client-hunting.vercel.app`
   * `BACKEND_URL`: `https://ai-client-hunting-backend.onrender.com`
4. Click **"Save Changes"**. Render will automatically redeploy the backend with the new variables.

---

## 📧 Step 5: Email Account Setup (Multi-Provider)

Your platform supports 3 email providers for outreach. See **[Email-Setup-Guide.md](./Email-Setup-Guide.md)** for detailed setup instructions.

### Quick Overview

| Provider | Setup | Cost |
|---|---|---|
| **Google (Gmail/Workspace)** | Google Cloud Console → OAuth Client | Free |
| **SMTP (Hostinger/GoDaddy/Zoho)** | User enters SMTP credentials | Free (comes with hosting) |
| **Resend** | Already configured for platform emails | Free (3k/month) |

### For Users (After Deployment)

1. Login to your platform
2. Go to **Settings → Email Accounts** in the sidebar
3. Click **"+ Add Account"**
4. Choose: Google, or SMTP
5. Complete the connection flow
6. Go to **Email Generator** page — your account will appear in the "Send From" dropdown

---

## 🎉 Step 6: Verification & Go Live

Once the Render backend finishes redeploying, your application is completely live!

**To verify:**
1. Open your Vercel URL in the browser.
2. Try signing up / logging in (This tests the Backend + Supabase DB).
3. Check if verification emails are being received (This tests Resend).
4. Go to Settings → Email Accounts and connect a Gmail or SMTP account.
5. Send a test outreach email from the Email Generator page.
6. Perform an action that uses the AI (This tests Groq/OpenAI).

**Congratulations! Your full-stack SaaS is now successfully deployed.**
