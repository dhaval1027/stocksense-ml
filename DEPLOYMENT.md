# StockSense — Live Deployment Guide (Vercel & Render)

This project can be deployed live in two ways:

---

## Option 1: Direct Vercel All-In-One Deployment (Using `vercel.json`)

We have already configured `vercel.json` and `api/index.py` for direct deployment.

### Step 1: Initialize Git and Push to GitHub
Open your terminal in the project root (`c:\Users\Admin\Desktop\dhaval\sem-5\ML\Final`) and run:

```bash
git init
git add .
git commit -m "Deploy StockSense with 70%+ accuracy model to Vercel"
git branch -M main
```

Now create a new repository on [GitHub](https://github.com/new) (e.g., `stocksense-ml`) and push:
```bash
git remote add origin https://github.com/<YOUR_USERNAME>/stocksense-ml.git
git push -u origin main
```

### Step 2: Deploy on Vercel
1. Go to [https://vercel.com](https://vercel.com) and log in.
2. Click **"Add New..."** → **"Project"**.
3. Import your GitHub repository (`stocksense-ml`).
4. Keep the default settings (Vercel will detect `vercel.json` automatically).
5. Click **"Deploy"**.
6. Once deployed, you will get your live URL: `https://your-stocksense.vercel.app`!

---

## Option 2: The Recommended ML Architecture (Vercel Frontend + Render Backend)

> **Why this is recommended for ML apps**:
> Vercel Serverless Functions have a strict **250MB uncompressed limit**. Heavy Python ML packages (`xgboost`, `scikit-learn`, `scipy`, `pandas`) together can exceed 400MB. Hosting the FastAPI backend on **Render** (free, no size limit) and the frontend on **Vercel** guarantees 100% uptime without serverless timeouts.

### Step 1: Deploy Backend on Render (100% Free)
1. Sign up / Log in to [Render.com](https://render.com).
2. Click **"New +"** → **"Web Service"**.
3. Connect your GitHub repository.
4. Fill in the service details:
   - **Name**: `stocksense-api`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. Click **"Create Web Service"**.
6. Once deployed, copy your backend URL (e.g., `https://stocksense-api.onrender.com`).

### Step 2: Deploy Frontend on Vercel
1. Go to [Vercel.com](https://vercel.com) → **"Add New..."** → **"Project"**.
2. Select your repository.
3. Configure Project Settings:
   - **Root Directory**: Click `Edit` and select `frontend`.
   - **Framework Preset**: `Vite` (auto-detected).
   - **Environment Variables**:
     - Key: `VITE_API_BASE_URL`
     - Value: `https://stocksense-api.onrender.com/api` (your Render URL + `/api`)
4. Click **"Deploy"**.

Your frontend is now live on Vercel with high-speed CDN and connected to your live ML backend!
