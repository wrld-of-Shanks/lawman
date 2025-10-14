#!/bin/bash

# SPECTER Legal Assistant - Email Configuration Setup Script
# This script helps you configure email settings for OTP functionality

echo "🛠️  SPECTER Legal Assistant - Email Configuration Setup"
echo "======================================================"

# Check if .env file exists in backend directory
if [ ! -f "backend/.env" ]; then
    echo "📄 Creating .env file from template..."
    cp backend/.env.example backend/.env
    echo "✅ .env file created successfully!"
fi

echo ""
echo "📧 To enable OTP email sending, you need to configure Gmail SMTP:"
echo ""

echo "1️⃣  Enable 2-Factor Authentication:"
echo "   • Go to: https://myaccount.google.com/security"
echo "   • Enable '2-Step Verification'"

echo ""
echo "2️⃣  Generate App Password:"
echo "   • Go to: https://myaccount.google.com/apppasswords"
echo "   • Select 'Mail' and your device"
echo "   • Copy the 16-character password generated"

echo ""
echo "3️⃣  Update backend/.env file:"
echo "   • Open backend/.env"
echo "   • Replace 'your-gmail@gmail.com' with your Gmail address"
echo "   • Replace 'your-16-char-app-password' with the generated app password"

echo ""
echo "📋 Current .env email configuration:"
grep -E "(LAWYER_SMTP_USER|LAWYER_SMTP_PASS)" backend/.env || echo "   Email configuration not found in .env file"

echo ""
echo "🚀 After configuration:"
echo "   • Restart the backend server"
echo "   • Registration and password reset will send actual emails"
echo "   • Users will receive OTP codes via email"

echo ""
echo "🔧 For Development (no email setup needed):"
echo "   • OTP codes are displayed in server console"
echo "   • Use the development OTP endpoint: /auth/dev/get-otp/{email}"
echo "   • Perfect for testing without email configuration"

echo ""
echo "✨ Setup complete! Your SPECTER Legal Assistant is ready."
