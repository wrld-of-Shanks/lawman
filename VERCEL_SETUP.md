# Vercel Deployment Guide

## Step 1: Import Repository
1. Click "Continue with GitHub"
2. Select repository: `wrld-of-Shanks/lawman`
3. Click "Import"

## Step 2: Configure Project
- **Project Name**: `specter-backend`
- **Framework Preset**: Other
- **Root Directory**: Leave empty (.)
- **Build Command**: Leave empty
- **Output Directory**: Leave empty

## Step 3: Environment Variables
Add these environment variables:

### Required Variables:
```
MONGODB_URL = mongodb+srv://shankardarur0_db_user:qZ8UzZq9p85WPHeC@specter.ucdaabu.mongodb.net/?retryWrites=true&w=majority&appName=specter

DATABASE_NAME = specter_legal

JWT_SECRET_KEY = your-super-secret-jwt-key-for-production-2024
```

### Optional Variables:
```
OPENAI_API_KEY = your-openai-api-key-here

LAWYER_SMTP_USER = your-gmail@gmail.com

LAWYER_SMTP_PASS = your-gmail-app-password
```

## Step 4: Deploy
1. Click "Deploy"
2. Wait for deployment (5-10 minutes)
3. Get your Vercel URL (e.g., https://specter-backend.vercel.app)

## Step 5: Update Netlify
1. Go to Netlify environment variables
2. Update `REACT_APP_API_URL` to your Vercel URL
3. Redeploy Netlify frontend

## Current Status:
✅ ngrok URL: https://7c24dd760260.ngrok-free.app (temporary)
🔄 Vercel URL: (will be permanent)
