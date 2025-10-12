#!/usr/bin/env python3
"""
Test script for SPECTER Contact Lawyer email configuration
Run this to verify your email settings are working correctly.
"""

import os
import smtplib
from email.mime.text import MIMEText

try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    load_dotenv = lambda: None

def test_email_configuration():
    """Test the email configuration for the Contact Lawyer feature."""
    
    # Load environment variables
    load_dotenv()
    
    # Get email configuration
    smtp_user = os.getenv('LAWYER_SMTP_USER')
    smtp_pass = os.getenv('LAWYER_SMTP_PASS')
    smtp_to = os.getenv('LAWYER_RECEIVER_EMAIL')
    smtp_host = os.getenv('LAWYER_SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('LAWYER_SMTP_PORT', '587'))
    
    print("🧪 SPECTER Email Configuration Test")
    print("=" * 40)
    
    # Check if all required variables are set
    missing_vars = []
    if not smtp_user:
        missing_vars.append('LAWYER_SMTP_USER')
    if not smtp_pass:
        missing_vars.append('LAWYER_SMTP_PASS')
    if not smtp_to:
        missing_vars.append('LAWYER_RECEIVER_EMAIL')
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please check your .env file and ensure all variables are set.")
        return False
    
    print(f"📧 Sender: {smtp_user}")
    print(f"📨 Receiver: {smtp_to}")
    print(f"🌐 SMTP Host: {smtp_host}:{smtp_port}")
    print()
    
    # Create test email
    subject = "SPECTER Email Configuration Test"
    body = """
This is a test email from the SPECTER Legal Assistant system.

If you receive this email, your Contact Lawyer feature is configured correctly!

Test Details:
- Sender: {sender}
- Receiver: {receiver}
- SMTP Host: {host}:{port}
- Timestamp: {timestamp}

You can now receive legal consultation requests through the SPECTER platform.
""".format(
        sender=smtp_user,
        receiver=smtp_to,
        host=smtp_host,
        port=smtp_port,
        timestamp=__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = smtp_to
    
    try:
        print("🔄 Connecting to SMTP server...")
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            print("🔐 Starting TLS encryption...")
            server.starttls()
            
            print("🔑 Authenticating...")
            server.login(smtp_user, smtp_pass)
            
            print("📤 Sending test email...")
            server.sendmail(smtp_user, smtp_to, msg.as_string())
            
        print("✅ SUCCESS! Test email sent successfully.")
        print(f"📬 Check {smtp_to} for the test message.")
        print("\n🎉 Your Contact Lawyer feature is ready to use!")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ AUTHENTICATION FAILED")
        print("💡 Possible solutions:")
        print("   1. Verify LAWYER_SMTP_USER is correct")
        print("   2. Ensure you're using an App Password (not regular password)")
        print("   3. Check that 2FA is enabled on your Gmail account")
        print("   4. Generate a new App Password if needed")
        return False
        
    except smtplib.SMTPRecipientsRefused:
        print("❌ RECIPIENT EMAIL REFUSED")
        print("💡 Check that LAWYER_RECEIVER_EMAIL is a valid email address")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("💡 Check your network connection and email settings")
        return False

if __name__ == "__main__":
    success = test_email_configuration()
    exit(0 if success else 1)
