from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
import os
import random
import string
import smtplib
from email.mime.text import MIMEText
try:
    from .mongodb_config import get_users_collection, get_otps_collection, get_user_sessions_collection
    from .tracing import TraceEvents, log_auth_event, tracing
except ImportError:
    from mongodb_config import get_users_collection, get_otps_collection, get_user_sessions_collection
    from tracing import TraceEvents, log_auth_event, tracing
from dotenv import load_dotenv
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

# Load environment variables
load_dotenv()

# Password hashing context - using bcrypt for compatibility
pwd_context = CryptContext(schemes=["bcrypt", "pbkdf2_sha256"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Pydantic models
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class OTPVerify(BaseModel):
    email: str
    otp: str

class PasswordReset(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    email: str
    otp: str
    new_password: str

# Helper functions
def hash_password(password: str) -> str:
    # Truncate password to 72 bytes to avoid bcrypt error
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # Truncate password to 72 bytes to avoid bcrypt error
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access"):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

# Database operations
async def get_user_by_email(email: str):
    users_collection = get_users_collection()
    user = await users_collection.find_one({"email": email})
    return user

async def create_user(user_data: UserCreate):
    users_collection = get_users_collection()
    user_dict = {
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "is_verified": False,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    try:
        result = await users_collection.insert_one(user_dict)
        print(f"User created successfully: {user_data.email}")
        return result.inserted_id
    except DuplicateKeyError as e:
        print(f"Duplicate key error for email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        print(f"Error creating user {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )

async def store_otp(email: str, otp: str, otp_type: str):
    otps_collection = get_otps_collection()
    otp_data = {
        "email": email,
        "otp": otp,
        "type": otp_type,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=10)
    }
    await otps_collection.insert_one(otp_data)

async def verify_otp(email: str, otp: str, otp_type: str) -> bool:
    otps_collection = get_otps_collection()
    otp_doc = await otps_collection.find_one({
        "email": email,
        "otp": otp,
        "type": otp_type,
        "expires_at": {"$gt": datetime.utcnow()}
    })
    
    if otp_doc:
        # Delete used OTP
        await otps_collection.delete_one({"_id": otp_doc["_id"]})
        return True
    return False

async def update_user_verification(email: str):
    users_collection = get_users_collection()
    await users_collection.update_one(
        {"email": email},
        {"$set": {"is_verified": True, "updated_at": datetime.utcnow()}}
    )

async def update_user_password(email: str, new_password: str):
    users_collection = get_users_collection()
    await users_collection.update_one(
        {"email": email},
        {"$set": {"password_hash": hash_password(new_password), "updated_at": datetime.utcnow()}}
    )

async def invalidate_user_sessions(user_id: str):
    """Invalidate all sessions for a user"""
    try:
        sessions_collection = get_user_sessions_collection()
        result = await sessions_collection.delete_many({"user_id": user_id})
        print(f"Invalidated {result.deleted_count} sessions for user {user_id}")
    except Exception as e:
        print(f"Error invalidating sessions for user {user_id}: {str(e)}")
        # Don't fail the password reset if session invalidation fails

def send_otp_email(to_email: str, otp: str, otp_type: str):
    """Send OTP via email to user"""
    smtp_user = os.getenv('LAWYER_SMTP_USER')
    smtp_pass = os.getenv('LAWYER_SMTP_PASS')
    smtp_host = os.getenv('LAWYER_SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('LAWYER_SMTP_PORT', '587'))

    if not (smtp_user and smtp_pass):
        # For development without email config, return the OTP
        print(f"DEVELOPMENT MODE - OTP for {to_email}: {otp}")
        return {"sent": False, "otp": otp, "reason": "email_not_configured"}

    try:
        # Email content based on OTP type
        if otp_type == "email_verification":
            subject = "SPECTER - Email Verification"
            body = f"""
Welcome to SPECTER Legal Assistant!

Your email verification code is: {otp}

This code will expire in 10 minutes.

If you didn't request this verification, please ignore this email.

Thank you for choosing SPECTER!
"""
        elif otp_type == "password_reset":
            subject = "SPECTER - Password Reset"
            body = f"""
SPECTER Legal Assistant - Password Reset

Your password reset code is: {otp}

This code will expire in 10 minutes.

If you didn't request this password reset, please ignore this email.

Thank you for using SPECTER!
"""
        else:
            subject = "SPECTER - Verification Code"
            body = f"Your verification code is: {otp}\n\nThis code will expire in 10 minutes."

        msg = MIMEText(body)
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        print(f"OTP email sent successfully to {to_email}")
        return {"sent": True, "message": "OTP sent successfully"}

    except Exception as e:
        print(f"Failed to send OTP email to {to_email}: {str(e)}")
        # Fallback to console for development
        print(f"DEVELOPMENT MODE - OTP for {to_email}: {otp}")
        return {"sent": False, "otp": otp, "reason": "email_send_failed"}

# Router and security setup
auth_router = APIRouter()
security = HTTPBearer()

# Handle CORS preflight requests for auth endpoints
@auth_router.options("/{path:path}")
async def auth_options_handler(path: str):
    """Handle CORS preflight requests for auth endpoints"""
    return {"message": "OK"}

# Helper function to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_user_by_email(payload.get("sub"))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Authentication endpoints
@auth_router.post("/register", response_model=dict)
async def register(user_data: UserCreate):
    try:
        # Validate password length before processing
        if len(user_data.password.encode('utf-8')) > 72:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be 72 characters or fewer to ensure compatibility."
            )

        # Check if user already exists
        existing_user = await get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        user_id = await create_user(user_data)

        # Generate and send OTP for email verification
        otp = generate_otp()
        await store_otp(user_data.email, otp, "email_verification")

        # Send OTP email
        email_result = send_otp_email(user_data.email, otp, "email_verification")

        # For development, skip email verification automatically
        print(f"Development mode: Skipping email verification for {user_data.email}")
        await update_user_verification(user_data.email)

        # Return appropriate message based on email sending result
        if email_result["sent"]:
            return {"message": "Registration successful. Please check your email for verification code."}
        else:
            return {"message": f"Registration successful. Email verification completed automatically for development. OTP: {email_result['otp']}"}

    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        # Handle any other unexpected errors
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@auth_router.post("/verify-email", response_model=dict)
async def verify_email(otp_data: OTPVerify):
    if await verify_otp(otp_data.email, otp_data.otp, "email_verification"):
        await update_user_verification(otp_data.email)
        return {"message": "Email verified successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

@auth_router.post("/login")
async def login(user_data: UserLogin):
    user = await get_user_by_email(user_data.email)
    
    if not user or not verify_password(user_data.password, user["password_hash"]):
        await log_auth_event(TraceEvents.AUTH_LOGIN, user_data.email, False, {"reason": "invalid_credentials"})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.get("is_verified", False):
        await log_auth_event(TraceEvents.AUTH_LOGIN, user_data.email, False, {"reason": "email_not_verified"})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your email first"
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user["email"]})
    refresh_token = create_refresh_token(data={"sub": user["email"]})
    
    # Log successful login
    await log_auth_event(TraceEvents.AUTH_LOGIN, user_data.email, True, {
        "user_id": str(user["_id"]),
        "login_time": datetime.utcnow().isoformat()
    })
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@auth_router.post("/refresh-token", response_model=Token)
async def refresh_token(refresh_token: str):
    payload = verify_token(refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = await get_user_by_email(payload.get("sub"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": user["email"]})
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@auth_router.post("/forgot-password", response_model=dict)
async def forgot_password(request: PasswordReset):
    user = await get_user_by_email(request.email)
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a reset code has been sent."}

    # Generate and send OTP
    otp = generate_otp()
    await store_otp(request.email, otp, "password_reset")

    # Send OTP email
    email_result = send_otp_email(request.email, otp, "password_reset")

    if email_result["sent"]:
        return {"message": "If the email exists, a reset code has been sent."}
    else:
        # For development, show the OTP
        return {"message": f"Email not configured. For development, use OTP: {email_result['otp']}"}

@auth_router.post("/reset-password", response_model=dict)
async def reset_password(request: PasswordResetConfirm):
    try:
        if await verify_otp(request.email, request.otp, "password_reset"):
            # Update password
            await update_user_password(request.email, request.new_password)

            # Invalidate all sessions for this user
            user = await get_user_by_email(request.email)
            if user:
                await invalidate_user_sessions(str(user["_id"]))

            return {"message": "Password reset successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed. Please try again."
        )

@auth_router.post("/logout", response_model=dict)
async def logout(current_user: dict = Depends(get_current_user)):
    # Invalidate all sessions for this user
    await invalidate_user_sessions(str(current_user["_id"]))
    return {"message": "Logged out successfully"}

@auth_router.get("/profile", response_model=dict)
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "full_name": current_user["full_name"],
        "is_verified": current_user.get("is_verified", False),
        "is_active": current_user.get("is_active", True),
        "created_at": current_user["created_at"].isoformat()
    }

@auth_router.put("/profile", response_model=dict)
async def update_profile(
    full_name: str,
    current_user: dict = Depends(get_current_user)
):
    users_collection = get_users_collection()
    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"full_name": full_name, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Profile updated successfully"}

# Development helper endpoint
@auth_router.get("/dev/get-otp/{email}")
async def get_otp_for_development(email: str):
    """Development endpoint to get the latest OTP for an email"""
    otps_collection = get_otps_collection()
    otp_doc = await otps_collection.find_one(
        {"email": email, "expires_at": {"$gt": datetime.utcnow()}},
        sort=[("created_at", -1)]
    )
    
    if otp_doc:
        return {
            "email": email,
            "otp": otp_doc["otp"],
            "type": otp_doc["type"],
            "expires_at": otp_doc["expires_at"].isoformat()
        }
    else:
        return {"message": "No valid OTP found for this email"}
