import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional
import jwt
import random
import string
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

# Database helper functions
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
