from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import json
import traceback
import sqlite3
import os
import jwt
import random
import string
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Password hashing context - simplified for compatibility
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Password hashing context - simplified for compatibility
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Database setup
def get_db():
    # Use absolute path to ensure consistency
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "users.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            is_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # OTP table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS otp_verification (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            otp_code TEXT NOT NULL,
            purpose TEXT NOT NULL, -- 'email_verification' or 'password_reset'
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            access_token TEXT NOT NULL,
            refresh_token TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()

# Utility functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access"):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload
    except jwt.PyJWTError:
        return None

def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))

def send_email(to_email: str, subject: str, body: str):
    smtp_user = os.getenv('LAWYER_SMTP_USER')
    smtp_pass = os.getenv('LAWYER_SMTP_PASS')
    smtp_host = os.getenv('LAWYER_SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('LAWYER_SMTP_PORT', '587'))

    if not smtp_user or not smtp_pass:
        raise ValueError("Email credentials not configured")

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        text = msg.as_string()
        server.sendmail(smtp_user, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def get_user_by_email(email: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(email: str, password: str, full_name: str, role: str = "user"):
    conn = get_db()
    cursor = conn.cursor()
    password_hash = hash_password(password)
    cursor.execute(
        "INSERT INTO users (email, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
        (email, password_hash, full_name, role)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def store_otp(user_id: int, otp: str, purpose: str, expiry_minutes: int = 5):
    conn = get_db()
    cursor = conn.cursor()
    expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    cursor.execute(
        "INSERT INTO otp_verification (user_id, otp_code, purpose, expires_at) VALUES (?, ?, ?, ?)",
        (user_id, otp, purpose, expires_at)
    )
    conn.commit()
    conn.close()

def verify_otp(email: str, otp: str, purpose: str):
    conn = get_db()
    cursor = conn.cursor()

    # Get user
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return False

    # Check OTP
    cursor.execute(
        "SELECT * FROM otp_verification WHERE user_id = ? AND otp_code = ? AND purpose = ? AND used = FALSE AND expires_at > ?",
        (user['id'], otp, purpose, datetime.utcnow())
    )
    otp_record = cursor.fetchone()

    if otp_record:
        # Mark OTP as used
        cursor.execute("UPDATE otp_verification SET used = TRUE WHERE id = ?", (otp_record['id'],))
        conn.commit()
        conn.close()
        return True

    conn.close()
    return False

def update_user_verification(email: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_verified = TRUE WHERE email = ?", (email,))
    conn.commit()
    conn.close()

def store_user_session(user_id: int, access_token: str, refresh_token: str):
    conn = get_db()
    cursor = conn.cursor()
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    cursor.execute(
        "INSERT INTO user_sessions (user_id, access_token, refresh_token, expires_at) VALUES (?, ?, ?, ?)",
        (user_id, access_token, refresh_token, expires_at)
    )
    conn.commit()
    conn.close()

def invalidate_user_sessions(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_user_role(email: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user['role'] if user else None

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

# Initialize database tables
create_tables()

# Router and security setup
auth_router = APIRouter()
security = HTTPBearer()

# Helper function to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return {"email": email, "role": get_user_role(email)}

# Helper function to check if user is admin
async def get_current_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Authentication endpoints
@auth_router.post("/register", response_model=dict)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user_id = create_user(
        user_data.email,
        user_data.password,
        user_data.full_name
    )

    # Generate and send verification OTP (optional for now)
    otp = generate_otp()
    store_otp(user_id, otp, "email_verification")

    # For development, auto-verify the user if email sending fails
    try:
        email_body = f"""
        Welcome to SPECTER Legal Assistant!

        Your verification code is: {otp}

        This code will expire in 5 minutes.

        Best regards,
        SPECTER Team
        """

        if send_email(user_data.email, "Verify Your Email - SPECTER", email_body):
            return {"message": "Registration successful. Please check your email for verification code."}
        else:
            # Auto-verify for development if email fails
            update_user_verification(user_data.email)
            return {"message": "Registration successful. Email verification skipped for development."}
    except Exception as e:
        # Auto-verify for development if email fails
        update_user_verification(user_data.email)
        return {"message": "Registration successful. Email verification skipped for development."}

@auth_router.post("/verify-email", response_model=dict)
async def verify_email(otp_data: OTPVerify):
    if verify_otp(otp_data.email, otp_data.otp, "email_verification"):
        update_user_verification(otp_data.email)
        return {"message": "Email verified successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

@auth_router.post("/login")
async def login(user_data: UserLogin):
    try:
        # Get user from database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (user_data.email,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Verify password
        if not verify_password(user_data.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Create tokens
        token_data = {"sub": user_data.email, "role": user['role']}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Store session
        conn = get_db()
        cursor = conn.cursor()
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        cursor.execute(
            "INSERT INTO user_sessions (user_id, access_token, refresh_token, expires_at) VALUES (?, ?, ?, ?)",
            (user['id'], access_token, refresh_token, expires_at)
        )
        conn.commit()
        conn.close()

        # Return response
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@auth_router.post("/refresh-token", response_model=Token)
async def refresh_token(refresh_token: str):
    payload = verify_token(refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # Get user and check if session exists
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Create new tokens
    token_data = {"sub": email, "role": user['role']}
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    # Update session
    store_user_session(user['id'], new_access_token, new_refresh_token)

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@auth_router.post("/forgot-password", response_model=dict)
async def forgot_password(request: PasswordReset):
    user = get_user_by_email(request.email)
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a reset code has been sent"}

    # Generate and send reset OTP
    otp = generate_otp()
    store_otp(user['id'], otp, "password_reset")

    email_body = f"""
    Password Reset Request - SPECTER

    Your password reset code is: {otp}

    This code will expire in 5 minutes.

    If you didn't request this, please ignore this email.

    Best regards,
    SPECTER Team
    """

    if send_email(request.email, "Password Reset - SPECTER", email_body):
        return {"message": "If the email exists, a reset code has been sent"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reset email"
        )

@auth_router.post("/reset-password", response_model=dict)
async def reset_password(request: PasswordResetConfirm):
    if verify_otp(request.email, request.otp, "password_reset"):
        # Update password
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE email = ?",
            (hash_password(request.new_password), request.email)
        )
        conn.commit()
        conn.close()

        return {"message": "Password reset successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

@auth_router.post("/logout", response_model=dict)
async def logout(current_user: dict = Depends(get_current_user)):
    # Invalidate all sessions for this user
    user = get_user_by_email(current_user["email"])
    if user:
        invalidate_user_sessions(user['id'])

    return {"message": "Logged out successfully"}

@auth_router.get("/profile", response_model=dict)
async def get_profile(current_user: dict = Depends(get_current_user)):
    user = get_user_by_email(current_user["email"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "id": user['id'],
        "email": user['email'],
        "full_name": user['full_name'],
        "role": user['role'],
        "is_verified": user['is_verified'],
        "created_at": user['created_at']
    }

@auth_router.put("/profile", response_model=dict)
async def update_profile(
    full_name: str,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET full_name = ?, updated_at = CURRENT_TIMESTAMP WHERE email = ?",
        (full_name, current_user["email"])
    )
    conn.commit()
    conn.close()

    return {"message": "Profile updated successfully"}

# Admin endpoints
@auth_router.get("/admin/users", response_model=list)
async def get_all_users(current_user: dict = Depends(get_current_admin)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, full_name, role, is_verified, created_at FROM users")
    users = cursor.fetchall()
    conn.close()

    return [
        {
            "id": user['id'],
            "email": user['email'],
            "full_name": user['full_name'],
            "role": user['role'],
            "is_verified": user['is_verified'],
            "created_at": user['created_at']
        }
        for user in users
    ]

@auth_router.delete("/admin/users/{user_id}", response_model=dict)
async def delete_user(user_id: int, current_user: dict = Depends(get_current_admin)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    return {"message": "User deleted successfully"}
