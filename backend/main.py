from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request, UploadFile, File, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
import sqlite3
import logging

# Standard imports for Docker/Gunicorn execution
from doc_parser import parse_and_chunk
from embed_store import add_chunks_to_db
from auth_mongo import auth_router
from legal_api import legal_router
from contact_service import contact_router
from payment_api import payment_router

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
app.include_router(contact_router, prefix="/api", tags=["contact"])
app.include_router(payment_router, prefix="/payment", tags=["payment"])

# Fallback routes for document analysis (to support older frontend versions)
@app.post("/upload_doc")
async def upload_doc_fallback(request: Request, file: UploadFile = File(...)):
    from legal_api import upload_document
    return await upload_document(request, file)

@app.post("/analyze_doc")
async def analyze_doc_fallback(request: Request):
    from legal_api import analyze_document, AnalysisRequest
    data = await request.json()
    analysis_request = AnalysisRequest(**data)
    return await analyze_document(analysis_request)



# Health check endpoint
@app.get("/")
async def root():
    return {"message": "SPECTER Legal Assistant API is running"}

@app.get("/health")
async def health_check():
    from local_llm import get_google_api_key
    api_key = get_google_api_key()
    return {
        "status": "healthy",
        "google_api_key_detected": api_key is not None and len(api_key) > 0,
        "env_keys": [k for k in os.environ.keys() if "API" in k or "KEY" in k or "URL" in k or "MONGODB" in k]
    }

# Usage stats endpoint
@app.get("/usage")
async def get_usage(request: Request):
    try:
        from auth_mongo import get_current_user
        from usage_tracker import get_usage_stats
        from fastapi.security import HTTPAuthorizationCredentials
        
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        # Get current user
        token = auth_header.replace("Bearer ", "")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        user = await get_current_user(credentials)
        
        # Get usage stats
        stats = await get_usage_stats(user)
        
        return stats
        
    except HTTPException as he:
        return JSONResponse(
            status_code=he.status_code,
            content={"error": he.detail}
        )
    except Exception as e:
        logging.error(f"Usage stats error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )


# Basic chat endpoint
@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        from auth_mongo import get_current_user
        from usage_tracker import enforce_question_limit, increment_question_count
        from fastapi.security import HTTPAuthorizationCredentials
        
        data = await request.json()
        user_message = data.get("message", "")
        target_lang = data.get("target_lang", "english")
        
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        # Get current user
        token = auth_header.replace("Bearer ", "")
        from fastapi.security import HTTPAuthorizationCredentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        user = await get_current_user(credentials)
        
        # Check usage limits
        await enforce_question_limit(user)
        
        if not user_message.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Message cannot be empty"}
            )
        
        # Use the Vector RAG system for semantic search
        from chat_engine_rag import answer_query_with_rag
        response = answer_query_with_rag(user_message, user_id=str(user["_id"]))
        
        # Increment usage count
        await increment_question_count(str(user["_id"]))
        
        return response
        
    except HTTPException as he:
        return JSONResponse(
            status_code=he.status_code,
            content={"error": he.detail}
        )
    except Exception as e:
        logging.error(f"Chat endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

# File upload endpoint
@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        from auth_mongo import get_current_user
        from usage_tracker import enforce_upload_limit, increment_upload_count
        from fastapi.security import HTTPAuthorizationCredentials
        
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        # Get current user
        token = auth_header.replace("Bearer ", "")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        user = await get_current_user(credentials)
        
        # Check upload limits
        await enforce_upload_limit(user)
        
        # Process upload
        import os
        os.makedirs("data/processed", exist_ok=True)
        content = await file.read()
        with open(f"data/processed/{file.filename}", "wb") as f:
            f.write(content)
        
        # Increment usage count
        await increment_upload_count(str(user["_id"]))
        
        return {"filename": file.filename, "status": "uploaded"}
        
    except HTTPException as he:
        return JSONResponse(
            status_code=he.status_code,
            content={"error": he.detail}
        )
    except Exception as e:
        logging.error(f"Upload endpoint error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

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
