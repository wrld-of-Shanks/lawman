# Email Configuration for SPECTER Legal Assistant

## Quick Setup for Gmail

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification if not already enabled
3. Verify your phone number or authenticator app

### Step 2: Generate App Password
1. In Google Account Security, go to "App passwords"
2. Select "Mail" as the app type
3. Generate a 16-character app password
4. Copy this password (it looks like: `abcd efgh ijkl mnop`)

### Step 3: Set Environment Variables

Run these commands in your terminal (replace with your actual values):

```bash
export LAWYER_SMTP_USER="your-gmail@gmail.com"
export LAWYER_SMTP_PASS="your-16-char-app-password"
export LAWYER_RECEIVER_EMAIL="your-gmail@gmail.com"
```

### Step 4: Restart the Backend

```bash
cd backend
MONGODB_URL="mongodb://localhost:27017" DATABASE_NAME="specter_legal" JWT_SECRET_KEY="your-super-secret-jwt-key-for-development" LAWYER_SMTP_USER="your-gmail@gmail.com" LAWYER_SMTP_PASS="your-app-password" python main.py
```

## Alternative: Development Mode (No Email Setup)

If you don't want to set up email, the system will show the OTP in the server console for development purposes.

## Test Password Reset

1. Go to the login page
2. Click "Forgot Password?"
3. Enter your email address
4. Check the server console for the OTP (if email not configured)
5. Use the OTP to reset your password
