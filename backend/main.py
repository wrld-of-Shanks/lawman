from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request, UploadFile, File, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
import sqlite3
import logging

# Robust intra-package imports (works with both `backend.main` and `main` entrypoints)
try:
    from .doc_parser import parse_and_chunk
    from .embed_store import add_chunks_to_db
    from .auth_mongo import auth_router
    from .legal_api import legal_router
except ImportError:
    from doc_parser import parse_and_chunk
    from embed_store import add_chunks_to_db
    from auth_mongo import auth_router
    from legal_api import legal_router

app = FastAPI(title="SPECTER Legal Assistant API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    from mongodb_config import connect_to_mongo
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    from mongodb_config import close_mongo_connection
    await close_mongo_connection()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(legal_router, prefix="/legal", tags=["legal"])



# Health check endpoint
@app.get("/")
async def root():
    return {"message": "SPECTER Legal Assistant API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Basic chat endpoint
@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message", "")
        user_id = data.get("user_id", None)
        target_lang = data.get("target_lang", "english")
        
        if not user_message.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Message cannot be empty"}
            )
        
        
        # Use the Vector RAG system for semantic search
        from chat_engine_rag import answer_query_with_rag
        response = answer_query_with_rag(user_message, user_id=user_id)
        
        return response
        
    except Exception as e:
        logging.error(f"Chat endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

# File upload endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    import os
    os.makedirs("data/processed", exist_ok=True)
    content = await file.read()
    with open(f"data/processed/{file.filename}", "wb") as f:
        f.write(content)
    return {"filename": file.filename, "status": "uploaded"}

class LawyerContactRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str = ''
    caseType: str
    description: str = ''

@app.post('/contact-lawyer')
def contact_lawyer(request: LawyerContactRequest):
    smtp_user = os.getenv('LAWYER_SMTP_USER')
    smtp_pass = os.getenv('LAWYER_SMTP_PASS')
    smtp_to = os.getenv('LAWYER_RECEIVER_EMAIL')
    smtp_host = os.getenv('LAWYER_SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('LAWYER_SMTP_PORT', '587'))
    
    if not (smtp_user and smtp_pass and smtp_to):
        return {"status": "error", "message": "Email credentials not set in .env"}
    
    subject = f"New SPECTER Contact Request: {request.caseType}"
    body = f"""
Name: {request.name}
Email: {request.email}
Phone: {request.phone}
Case Type: {request.caseType}
Description: {request.description}
"""
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = smtp_to
    
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, smtp_to, msg.as_string())
        return {"status": "success", "message": "Request sent to lawyer network."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to send email: {e}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
