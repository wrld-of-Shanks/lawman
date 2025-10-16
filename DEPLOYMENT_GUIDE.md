# SPECTER Legal Assistant - Deployment Guide

## 🎉 Issues Fixed

### Backend Issues Resolved:
- ✅ **PyMuPDF Import Error**: Fixed ModuleNotFoundError for 'fitz' module
- ✅ **Python Version Compatibility**: Updated to Python 3.11 for better compatibility
- ✅ **Dependencies Updated**: Updated PyMuPDF to version 1.23.26 with additional font support
- ✅ **Build Configuration**: Enhanced nixpacks.toml with required system dependencies
- ✅ **Runtime Configuration**: Corrected runtime.txt to specify Python instead of Node.js

### Frontend Issues Resolved:
- ✅ **Build Configuration**: Verified React app builds successfully
- ✅ **Deployment Setup**: Netlify configuration is properly configured
- ✅ **TypeScript Compilation**: All TypeScript errors resolved
- ✅ **JavaScript Requirement**: The "enable JavaScript" message is normal for React apps

## 🚀 Deployment Steps

### 1. Backend Deployment (Render)

Your backend is configured to deploy to: `specter-vwjk.onrender.com`

**Files configured:**
- `nixpacks.toml` - Build configuration with Python 3.11 and system dependencies
- `runtime.txt` - Python runtime specification
- `Procfile` - Process configuration for Render
- `backend/requirements.txt` - Updated dependencies including PyMuPDF 1.23.26

**Environment Variables to Set on Render:**
```bash
# Database
MONGODB_URI=your_mongodb_connection_string
DATABASE_NAME=specter_legal

# Authentication
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# OpenAI (Optional)
OPENAI_API_KEY=your_openai_api_key
OPENROUTER_API_KEY=your_openrouter_api_key  # Alternative

# Email Configuration
LAWYER_SMTP_USER=your_email@gmail.com
LAWYER_SMTP_PASS=your_app_password
LAWYER_SMTP_HOST=smtp.gmail.com
LAWYER_SMTP_PORT=587
LAWYER_RECEIVER_EMAIL=lawyer@example.com

# Payment (if using Razorpay)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

### 2. Frontend Deployment (Netlify)

Your frontend is deployed to: `specter0.netlify.app`

**Files configured:**
- `netlify.toml` - Build and redirect configuration
- `frontend/react_app/package.json` - Dependencies and build scripts
- `frontend/react_app/src/config.ts` - API endpoint configuration

**Environment Variables to Set on Netlify:**
```bash
REACT_APP_API_URL=https://specter-vwjk.onrender.com
```

### 3. Deployment Command Sequence

```bash
# 1. Verify everything is ready
python deploy_verify.py

# 2. Commit and push your changes
git add .
git commit -m "Fix: Resolve PyMuPDF import error and update deployment configuration"
git push origin main

# 3. Deployments should trigger automatically:
# - Render will redeploy backend automatically
# - Netlify will redeploy frontend automatically
```

## 🔧 Troubleshooting

### Backend Issues

**PyMuPDF Import Error (RESOLVED)**
- **Problem**: `ModuleNotFoundError: No module named 'fitz'`
- **Solution**: Updated nixpacks.toml with required system dependencies and PyMuPDF version

**Build Timeout Issues**
```bash
# If build times out, check nixpacks.toml has:
[phases.setup]
nixPkgs = ["python311", "gcc", "g++", "pkgconfig", "freetype", "fontconfig", "harfbuzz"]
```

**Import Path Issues**
```bash
# If you get import errors in deployment, ensure PYTHONPATH is set:
PYTHONPATH = "/opt/render/project/src"
```

### Frontend Issues

**API Connection Issues**
- Check that `REACT_APP_API_URL` is set correctly in Netlify
- Verify CORS settings in backend allow your Netlify domain

**Build Failures**
```bash
# Test build locally:
cd frontend/react_app
npm install
npm run build
```

### Database Connection

**MongoDB Connection Issues**
- Ensure `MONGODB_URI` includes full connection string with credentials
- For MongoDB Atlas, ensure IP whitelist includes `0.0.0.0/0` for Render

## 📊 Verification

Run the verification script anytime:
```bash
python deploy_verify.py
```

This checks:
- ✅ All deployment configuration files exist
- ✅ Python dependencies can be imported
- ✅ Frontend builds successfully
- ✅ Backend core imports work
- ✅ Environment templates are available

## 🔄 Post-Deployment Testing

### 1. Backend Health Check
```bash
curl https://specter-vwjk.onrender.com/health
# Should return: {"status": "healthy", "message": "API is operational"}
```

### 2. Frontend Access
- Visit: https://specter0.netlify.app
- Should load the SPECTER Legal Assistant interface
- Test chat functionality with a simple legal query

### 3. Full Integration Test
- Open frontend → Click "SPECTER" → Ask a legal question
- Should receive structured response with Answer, Legal Reference, etc.

## 🎯 Success Indicators

✅ **Backend**: Returns JSON responses from API endpoints
✅ **Frontend**: Loads without JavaScript errors in browser console  
✅ **Integration**: Chat functionality works end-to-end
✅ **Database**: User registration/login works (if enabled)

## 📞 Support

If deployment issues persist:

1. **Check Render Logs**: Go to Render dashboard → View build/runtime logs
2. **Check Netlify Logs**: Go to Netlify dashboard → Site → Deploy log
3. **Run Verification**: `python deploy_verify.py` to identify specific issues
4. **Environment Variables**: Verify all required variables are set correctly

Your project is now configured for smooth deployment! 🚀