from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

contact_router = APIRouter()

class LawyerContactRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    lawyer_type: str
    budget: str
    case_description: str

@contact_router.post("/contact_lawyer")
async def contact_lawyer(request: LawyerContactRequest):
    """Send lawyer contact request to admin email"""
    try:
        # Email configuration
        admin_email = "shankardarur158@gmail.com"
        
        # Create email content
        subject = f"New Lawyer Consultation Request - {request.lawyer_type}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
                    <h2 style="color: #fbbf24; border-bottom: 2px solid #fbbf24; padding-bottom: 10px;">
                        New Lawyer Consultation Request
                    </h2>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin-top: 20px;">
                        <h3 style="color: #333; margin-top: 0;">Client Information</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px; font-weight: bold; width: 150px;">Name:</td>
                                <td style="padding: 8px;">{request.name}</td>
                            </tr>
                            <tr style="background-color: #f5f5f5;">
                                <td style="padding: 8px; font-weight: bold;">Email:</td>
                                <td style="padding: 8px;">{request.email}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: bold;">Phone:</td>
                                <td style="padding: 8px;">{request.phone}</td>
                            </tr>
                            <tr style="background-color: #f5f5f5;">
                                <td style="padding: 8px; font-weight: bold;">Lawyer Type:</td>
                                <td style="padding: 8px;"><strong>{request.lawyer_type}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: bold;">Budget:</td>
                                <td style="padding: 8px;"><strong>{request.budget}</strong></td>
                            </tr>
                        </table>
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin-top: 15px;">
                        <h3 style="color: #333; margin-top: 0;">Case Description</h3>
                        <p style="white-space: pre-wrap; background: #f9f9f9; padding: 15px; border-left: 4px solid #fbbf24; border-radius: 4px;">
                            {request.case_description}
                        </p>
                    </div>
                    
                    <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #fbbf24;">
                        <p style="margin: 0; font-size: 14px;">
                            <strong>Action Required:</strong> Please contact the client within 24 hours to discuss their case.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Try to send via SMTP (Gmail)
        try:
            # Get SMTP credentials from environment
            smtp_email = os.getenv("SMTP_EMAIL", admin_email)
            smtp_password = os.getenv("SMTP_PASSWORD")
            
            if smtp_password:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = smtp_email
                msg['To'] = admin_email
                msg['Reply-To'] = request.email
                
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
                
                # Send via Gmail SMTP
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(smtp_email, smtp_password)
                    server.send_message(msg)
                    
                logger.info(f"Lawyer contact request sent from {request.email}")
                return {
                    "success": True,
                    "message": "Your request has been sent successfully! We'll contact you within 24 hours."
                }
            else:
                # Fallback: Log the request
                logger.warning("SMTP not configured. Logging request instead.")
                logger.info(f"Lawyer Request: {request.dict()}")
                
                return {
                    "success": True,
                    "message": "Your request has been received! We'll contact you soon.",
                    "note": "Email service not configured - request logged"
                }
                
        except Exception as smtp_error:
            logger.error(f"SMTP error: {smtp_error}")
            # Fallback to logging
            logger.info(f"Lawyer Request (fallback): {request.dict()}")
            return {
                "success": True,
                "message": "Your request has been received! We'll contact you soon."
            }
            
    except Exception as e:
        logger.error(f"Contact lawyer error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send request. Please try again.")
