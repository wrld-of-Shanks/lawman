from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Request, UploadFile, File, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel, EmailStr
from backend.doc_parser import parse_and_chunk
from backend.embed_store import add_chunks_to_db
from backend.chat_engine import answer_query
import smtplib
from email.mime.text import MIMEText
import sqlite3
import logging
from openai import OpenAI
from typing import Dict, List

app = FastAPI()

# Allow CORS for frontend domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://specter0.netlify.app",  # Production Netlify
        "https://specter-legal-assistant.netlify.app",  # Alternative/previous Netlify
        "http://localhost:3000",  # Local development
        "http://127.0.0.1:3000",  # Local alternative
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_RAW = "data/raw_laws"

# Initialize OpenAI/OpenRouter client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if OPENROUTER_API_KEY:
    # Use OpenRouter if its key is provided
    client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
else:
    # Fallback to standard OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

# Simple FAQ for demo with keyword-based matching (now includes legal references and steps)
FAQ: Dict[str, Dict] = {
    "theft": {
        "answer": "Punishment for theft is up to 3 years imprisonment, or fine, or both.",
        "legal_reference": "IPC Section 378 (Definition), IPC Section 379 (Punishment)",
        "explanation": "Taking someone else's movable property without consent and with dishonest intention amounts to theft.",
        "steps": [
            "File an FIR at the nearest police station mentioning IPC Section 379.",
            "Provide details, witnesses, and any evidence (CCTV, bills).",
            "Follow up to obtain a copy of the FIR and acknowledgment."
        ]
    },
    "cheating": {
        "answer": "Cheating is punishable with imprisonment up to 3 years, or fine, or both.",
        "legal_reference": "IPC Section 415 (Definition), IPC Section 420 (Punishment)",
        "explanation": "Cheating involves deceiving a person to deliver property or to do/omit an act.",
        "steps": [
            "Collect all communications and documents evidencing deception.",
            "File an FIR for IPC Section 420 at the police station or online e‑FIR portal.",
            "Consider civil remedies for recovery in parallel."
        ]
    },
    "license": {
        "answer": "You can apply online via Parivahan or at your RTO for learner's and driving license.",
        "legal_reference": "Motor Vehicles Act, 1988; Central Motor Vehicles Rules, 1989",
        "explanation": "The MVA and CMVR set eligibility, documents, and test requirements.",
        "steps": [
            "Book an online slot on Parivahan or visit RTO with ID/address/age proof and photos.",
            "Pass learner's test, then schedule driving test after required learning period.",
            "Pay fees and collect the license; ensure PUC and insurance are in order."
        ]
    },
    "ancestral": {
        "answer": "Ancestral property devolves among legal heirs per personal law (e.g., Hindu Succession Act).",
        "legal_reference": "Hindu Succession Act, 1956 (as amended)",
        "explanation": "Shares are determined by class of heirs; daughters have equal rights.",
        "steps": [
            "Obtain legal heir certificate and property documents.",
            "Consider partition deed or suit if dispute persists.",
            "Mutate records post‑partition."
        ]
    }
}

KEYWORD_ALIASES: Dict[str, str] = {
    "bike": "theft",
    "stolen": "theft",
    "property": "ancestral",
    "driving": "license",
}


def format_structured_response(answer: str, legal_reference: str = "", explanation: str = "", steps: List[str] = None) -> Dict[str, str]:
    parts: List[str] = []
    parts.append(f"Answer: {answer}")
    if legal_reference:
        parts.append(f"Legal Reference: {legal_reference}")
    if explanation:
        parts.append(f"Explanation: {explanation}")
    if steps:
        for_steps = "\n".join([f"- {s}" for s in steps])
        parts.append(f"Next Steps:\n{for_steps}")
    return {"answer": "\n".join(parts)}

def detect_target_language_and_strip(msg: str) -> (str, str):
    lower = msg.strip().lower()
    target = None
    prefix = "respond in "
    if lower.startswith(prefix):
        # Expect forms like: Respond in हिंदी. <question>
        rest = msg[len(prefix):].strip()
        # Split on first period or colon
        for sep in [".", ":", "\n"]:
            if sep in rest:
                idx = rest.index(sep)
                target = rest[:idx].strip()
                msg_clean = rest[idx+1:].strip()
                return target, msg_clean
        # If no separator, only language provided
        target = rest.strip()
        return target, ""
    return None, msg

def translate_text(text: str, target_lang: str) -> str:
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": (
                    "You are a translator. Translate the following text into "
                    f"{target_lang} while preserving structure, labels, and bullet points. "
                    "Do not add commentary."
                )},
                {"role": "user", "content": text}
            ],
            temperature=0.2
        )
        return resp.choices[0].message.content
    except Exception:
        return text

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    # Detect language directive, and strip it for intent matching
    target_lang, stripped = detect_target_language_and_strip(request.message)
    user_msg = (stripped or request.message).lower()
    print(f"Received chat message: {user_msg}")
    # If it's a legal solutions request, always use LLM with a detailed system prompt
    if user_msg.startswith("provide legal solutions for this problem:"):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": (
                        "You are SPECTER, a legal assistant chatbot specialized in Indian laws (criminal, civil, traffic). "
                        "Always respond using this exact structure (plain text, no markdown):\n"
                        "Answer: <direct, concise answer>\n"
                        "Legal Reference: <relevant IPC/BNS/BNSS/BSA/MVA/CMVR sections>\n"
                        "Explanation: <simple, layperson terms>\n"
                        "Next Steps:\n- <Step 1>\n- <Step 2>\n- <Step 3>\n"
                        "Do not suggest consulting a lawyer unless the question is outside the dataset or requires human intervention."
                    )},
                    {"role": "user", "content": request.message}
                ]
            )
            answer = response.choices[0].message.content
            return {"answer": answer}
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return format_structured_response(
                answer="No direct solution found.",
                legal_reference="",
                explanation="Please rephrase your question or consult a lawyer.",
                steps=["Contact a local lawyer with your documents."]
            )
    # Otherwise, use FAQ first (with structure), then LLM fallback
    for key in list(FAQ.keys()) + list(KEYWORD_ALIASES.keys()):
        if key in user_msg:
            canonical = KEYWORD_ALIASES.get(key, key)
            if canonical in FAQ:
                item = FAQ[canonical]
                print(f"Matched keyword: {key} -> {canonical}")
                resp_obj = format_structured_response(
                    answer=item.get("answer", ""),
                    legal_reference=item.get("legal_reference", ""),
                    explanation=item.get("explanation", ""),
                    steps=item.get("steps", [])
                )
                # Translate if requested
                if target_lang and target_lang.lower() not in {"english", "en"}:
                    resp_obj = {"answer": translate_text(resp_obj["answer"], target_lang)}
                return resp_obj
    # LLM fallback
    try:
        # Add language instruction if requested
        sys_content = (
            "You are SPECTER, a legal assistant chatbot specialized in Indian laws (criminal, civil, traffic). "
            "Always respond using this exact structure (plain text, no markdown):\n"
            "Answer: <direct, concise answer>\n"
            "Legal Reference: <relevant IPC/BNS/BNSS/BSA/MVA/CMVR sections>\n"
            "Explanation: <simple, layperson terms>\n"
            "Next Steps:\n- <Step 1>\n- <Step 2>\n- <Step 3>\n"
            "Do not suggest consulting a lawyer unless the question is outside the dataset or requires human intervention."
        )
        if target_lang and target_lang.lower() not in {"english", "en"}:
            sys_content = f"Respond in {target_lang}. " + sys_content
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": sys_content},
                {"role": "user", "content": stripped or request.message}
            ]
        )
        answer = response.choices[0].message.content
        return {"answer": answer}
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return format_structured_response(
            answer="No direct solution found.",
            legal_reference="",
            explanation="Please rephrase your question or provide more details.",
            steps=["Specify the Act/section or context.", "Add dates, location, and role (complainant/accused).", "Try a simpler query if the question is very broad."]
        )

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
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

@app.get('/law_search')
def law_search(
    q: str = Query(..., description="Search term"),
    act: str = Query(None, description="Act name (optional)")
):
    conn = sqlite3.connect("legal_acts.db")
    c = conn.cursor()
    if act:
        c.execute(
            "SELECT act, section, title, definition, punishment FROM laws WHERE act=? AND (title LIKE ? OR definition LIKE ? OR keywords LIKE ?)",
            (act, f"%{q}%", f"%{q}%", f"%{q}%")
        )
    else:
        c.execute(
            "SELECT act, section, title, definition, punishment FROM laws WHERE title LIKE ? OR definition LIKE ? OR keywords LIKE ?",
            (f"%{q}%", f"%{q}%", f"%{q}%")
        )
    results = [
        {
            "act": row[0],
            "section": row[1],
            "title": row[2],
            "definition": row[3],
            "punishment": row[4]
        }
        for row in c.fetchall()
    ]
    conn.close()
    return {"results": results}

@app.get('/law_acts')
def law_acts():
    conn = sqlite3.connect("legal_acts.db")
    c = conn.cursor()
    c.execute("SELECT DISTINCT act FROM laws ORDER BY act")
    acts = [row[0] for row in c.fetchall()]
    conn.close()
    return {"acts": acts} 

# --- Translation endpoint ---
class TranslateRequest(BaseModel):
    text: str
    target_lang: str

@app.post('/translate')
def translate(req: TranslateRequest):
    if not req.text.strip():
        return {"translated": ""}
    translated = translate_text(req.text, req.target_lang)
    return {"translated": translated}