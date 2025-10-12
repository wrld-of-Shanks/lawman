from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, UploadFile, File, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
# Use regular string instead of EmailStr to avoid dependency issues
from typing import Optional
from doc_parser import parse_and_chunk
from embed_store import add_chunks_to_db
from chat_engine import answer_query
import smtplib
from email.mime.text import MIMEText
import sqlite3
import re
from openai import OpenAI
from auth_mongo import auth_router
from mongodb_config import connect_to_mongo, close_mongo_connection, create_indexes, get_legal_acts_collection, get_sync_database

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
MODEL_NAME = "gpt-3.5-turbo"

app = FastAPI()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "SPECTER Legal Assistant API is running"}

@app.get("/")
async def root():
    return {"message": "SPECTER Legal Assistant API", "docs": "/docs"}

# Database events
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    await create_indexes()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Include auth router
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://specter-legal-assistant.netlify.app",  # Production frontend
        "https://*.netlify.app"  # Allow all Netlify preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

def detect_target_language_and_strip(message: str):
    """
    Detect if the message starts with a language directive like 'Respond in Hindi.'
    If so, return (target_language, stripped_message).
    Otherwise, return (None, None).
    """
    pattern = r'^respond in (\w+)\.\s*(.*)$'
    match = re.match(pattern, message, re.IGNORECASE)
    if match:
        target_lang = match.group(1)
        stripped = match.group(2)
        return target_lang, stripped
    return None, None

def format_structured_response(answer: str, legal_reference: str = "", explanation: str = "", steps: list = None):
    """Format response in the structured format expected by the frontend."""
    if steps is None:
        steps = []
    
    response = f"Answer: {answer}\n"
    if legal_reference:
        response += f"Legal Reference: {legal_reference}\n"
    if explanation:
        response += f"Explanation: {explanation}\n"
    if steps:
        response += "Next Steps:\n"
        for step in steps:
            response += f"- {step}\n"
    
    return {"answer": response.strip()}

# Simple FAQ data
FAQ = {
    "bail": "Bail is the temporary release of an accused person awaiting trial. Types include regular bail, anticipatory bail, and default bail.",
    "divorce": "Divorce can be filed under various grounds including cruelty, desertion, adultery, and mutual consent.",
    "property": "Property disputes involve ownership, inheritance, and transfer issues governed by various property laws."
}

KEYWORD_ALIASES = {
    "arrest": "bail",
    "marriage": "divorce",
    "land": "property"
}

@app.post("/chat")
async def chat(request: ChatRequest):
    # Detect language directive, and strip it for intent matching
    target_lang, stripped = detect_target_language_and_strip(request.message)
    user_msg = (stripped or request.message).lower()
    print(f"Received chat message: {user_msg}")
    # Legal solutions request - simplified for memory optimization
    if user_msg.startswith("provide legal solutions for this problem:"):
        return format_structured_response(
            answer="Legal consultation service is temporarily unavailable.",
            legal_reference="Please refer to relevant Indian legal codes",
            explanation="For detailed legal advice, please consult with a qualified lawyer.",
            steps=["Contact a local lawyer with your documents", "Gather relevant case details", "Prepare necessary documentation"]
        )
    # Otherwise, use FAQ first (with structure), then LLM fallback
    for key in list(FAQ.keys()) + list(KEYWORD_ALIASES.keys()):
        if key.lower() in user_msg:
            faq_answer = FAQ.get(key) or FAQ.get(KEYWORD_ALIASES.get(key, ""))
            if faq_answer:
                return {"answer": faq_answer}
    
    # Chat engine disabled for production deployment to save memory
    # Simple fallback without heavy dependencies
    
    # Final fallback with structured response
    return format_structured_response(
        answer="I couldn't find specific information about your query.",
        explanation="Please try rephrasing your question or provide more details.",
        steps=["Be more specific about your legal issue", "Include relevant details like location, dates, amounts", "Try using different keywords"]
    )

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    filename = f"uploads/{file.filename}"
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    # Save the file
    with open(filename, "wb") as f:
        f.write(content)
    return {"filename": file.filename, "status": "uploaded"}

class LawyerContactRequest(BaseModel):
    name: str
    email: str  # Changed from EmailStr to avoid dependency issues
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

@app.get('/law_search')
async def law_search(
    q: str = Query(..., description="Search term"),
    act: str = Query(None, description="Act name (optional)")
):
    legal_acts_collection = get_legal_acts_collection()
    
    # Build search query
    search_query = {
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"definition": {"$regex": q, "$options": "i"}},
            {"keywords": {"$regex": q, "$options": "i"}}
        ]
    }
    
    if act:
        search_query["act"] = act
    
    # Execute search
    cursor = legal_acts_collection.find(
        search_query,
        {"act": 1, "section": 1, "title": 1, "definition": 1, "punishment": 1, "_id": 0}
    ).limit(50)
    
    results = []
    async for doc in cursor:
        results.append({
            "act": doc.get("act", ""),
            "section": doc.get("section", ""),
            "title": doc.get("title", ""),
            "definition": doc.get("definition", ""),
            "punishment": doc.get("punishment", "")
        })
    
    return {"results": results}

@app.get('/law_acts')
async def law_acts():
    legal_acts_collection = get_legal_acts_collection()
    acts = await legal_acts_collection.distinct("act")
    return {"acts": sorted(acts)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8002))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
