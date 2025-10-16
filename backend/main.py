from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
from typing import Optional

# Simplified imports for debugging
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Core modules only
from auth_mongo import auth_router
from mongodb_config import connect_to_mongo, close_mongo_connection, create_indexes

# Import comprehensive legal database
from comprehensive_legal_db import COMPREHENSIVE_LEGAL_FAQ, get_comprehensive_legal_info, SPECIALIZED_LEGAL_AREAS

# Import legal solutions
from legal_solutions import get_legal_solution, format_legal_solution, TOPIC_TO_SOLUTION

# Optional imports with fallbacks
try:
    from tracing import tracing, TraceEvents, log_system_event, log_chat_event
except ImportError:
    # Create dummy tracing objects if import fails
    class TraceEvents:
        SYSTEM_START = "system_start"
        CHAT_MESSAGE = "chat_message"
        DOC_UPLOAD = "doc_upload"
        DOC_ERROR = "doc_error"
    
    class DummyTracing:
        async def initialize(self): pass
        async def log_trace(self, *args, **kwargs): pass
        async def get_traces(self, **kwargs): return []
        async def get_system_stats(self): return {}
        async def get_user_activity(self, user_id, days): return {}
    
    tracing = DummyTracing()
    log_system_event = lambda *args, **kwargs: None
    log_chat_event = lambda *args, **kwargs: None

# Simplified payment imports
try:
    from payment_razorpay import PaymentRequest, PaymentVerification, SubscriptionStatus
except ImportError:
    # Create dummy payment classes if import fails
    class PaymentRequest(BaseModel):
        amount: int
        currency: str = "INR"
    
    class PaymentVerification(BaseModel):
        razorpay_payment_id: str
        razorpay_order_id: str
        razorpay_signature: str
    
    class SubscriptionStatus(BaseModel):
        user_id: str
        subscription_tier: str
        expires_at: Optional[str] = None
import uuid
import time
import re

# Initialize OpenAI client (optional)
if OpenAI:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    MODEL_NAME = "gpt-3.5-turbo"
else:
    client = None
    MODEL_NAME = None

app = FastAPI()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check that doesn't depend on external services"""
    try:
        # Basic connectivity check
        return {
            "status": "healthy",
            "message": "SPECTER Legal Assistant API is running",
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

@app.get("/debug")
async def debug_endpoint():
    """Debug endpoint to check database connection and environment"""
    try:
        # Test database connection
        db = get_database()
        if db is None:
            return {"error": "Database connection failed", "mongodb_url": os.getenv("MONGODB_URL"), "database_name": os.getenv("DATABASE_NAME")}

        # Test collections
        users_collection = get_users_collection()
        test_user = await users_collection.find_one({"email": "test@example.com"})

        return {
            "status": "ok",
            "mongodb_url": os.getenv("MONGODB_URL")[:20] + "..." if os.getenv("MONGODB_URL") else "Not set",
            "database_name": os.getenv("DATABASE_NAME"),
            "jwt_secret_set": bool(os.getenv("JWT_SECRET_KEY")),
            "test_query_result": "User found" if test_user else "No test user"
        }
    except Exception as e:
        return {"error": str(e)}

# Database events
@app.on_event("startup")
async def startup_event():
    """Initialize database connections and tracing on startup"""
    try:
        await connect_to_mongo()
        await create_indexes()
        await tracing.initialize()
        await log_system_event(TraceEvents.SYSTEM_START, {
            "message": "Application started successfully"
        })
        print("✅ Application startup completed successfully")
    except Exception as e:
        print(f"⚠️  Startup warning (app will still run): {str(e)}")
        # Don't crash the app if optional services fail

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup connections on shutdown"""
    try:
        await close_mongo_connection()
    except Exception as e:
        print(f"Shutdown error: {str(e)}")

@app.get("/debug")
async def debug_endpoint():
    """Debug endpoint to check database connection and environment"""
    try:
        # Test database connection
        db = get_database()
        if db is None:
            return {"error": "Database connection failed", "mongodb_url": os.getenv("MONGODB_URL"), "database_name": os.getenv("DATABASE_NAME")}

        # Test collections
        users_collection = get_users_collection()
        test_user = await users_collection.find_one({"email": "test@example.com"})

        return {
            "status": "ok",
            "mongodb_url": os.getenv("MONGODB_URL")[:20] + "..." if os.getenv("MONGODB_URL") else "Not set",
            "database_name": os.getenv("DATABASE_NAME"),
            "jwt_secret_set": bool(os.getenv("JWT_SECRET_KEY")),
            "test_query_result": "User found" if test_user else "No test user"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
async def root():
    return {"message": "SPECTER Legal Assistant API", "docs": "/docs"}

@app.get("/test")
async def test():
    return {"message": "Test endpoint working"}

# Temporarily comment out complex routers for debugging
# from legal_api import legal_router
# app.include_router(legal_router, prefix="/legal", tags=["legal-analysis"])

# from legal_solutions_flow import solutions_router
# app.include_router(solutions_router, prefix="/solutions", tags=["legal-solutions"])

# from document_generator import generator_router
# app.include_router(generator_router, prefix="/generate", tags=["document-generator"])

# Include authentication router
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Temporarily comment out complex middleware for debugging
# @app.middleware("http")
# async def trace_requests(request: Request, call_next):
#     # Simplified middleware for debugging
#     response = await call_next(request)
#     return response

# Add CORS middleware - updated for production with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://specter-legal-assistant.netlify.app",  # Production Netlify domain
        "http://localhost:3000",  # Local development (React dev server)
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

# Comprehensive Legal FAQ Database
FAQ = {
    # Criminal Law
    "bail": "Bail is the temporary release of an accused person awaiting trial. Types include regular bail (Section 437), anticipatory bail (Section 438), and default bail (Section 167). Bail is generally granted except for serious offenses.",
    "murder": "Murder under IPC Section 302 is punishable by death or life imprisonment. It requires proving intention to cause death or knowledge that the act is likely to cause death.",
    "theft": "Theft under IPC Section 378 involves dishonestly taking movable property without consent. Punishment includes imprisonment up to 3 years or fine or both.",
    "fraud": "Fraud involves intentional deception for unlawful gain. Under IPC Section 420 (cheating), punishment includes imprisonment up to 7 years and fine.",
    "assault": "Assault under IPC Section 351 is making gestures or preparations to use criminal force. Simple assault is punishable with imprisonment up to 3 months or fine up to ₹500.",
    "kidnapping": "Kidnapping under IPC Sections 359-369 involves taking a person without consent. Punishment varies from 7 years to life imprisonment depending on circumstances.",
    "dowry": "Dowry harassment under Section 498A IPC and Dowry Prohibition Act 1961 is punishable with imprisonment up to 3 years and fine.",
    
    # Family Law
    "divorce": "Divorce can be filed under Hindu Marriage Act 1955, Special Marriage Act 1954, or personal laws. Grounds include cruelty, desertion, adultery, conversion, mental disorder, and mutual consent.",
    "marriage": "Marriage registration is mandatory under respective personal laws. Requirements include age (21 for men, 18 for women), consent, and prohibited relationship checks.",
    "custody": "Child custody is decided based on child's welfare. Types include physical custody, legal custody, joint custody, and sole custody. Courts consider child's age, preference, and parent's capability.",
    "maintenance": "Maintenance under Section 125 CrPC can be claimed by wife, children, and parents. Amount depends on income, lifestyle, and needs of the dependent.",
    "adoption": "Adoption is governed by Hindu Adoption and Maintenance Act 1956 for Hindus and Juvenile Justice Act 2015 for others. Legal formalities include court approval.",
    
    # Property Law
    "property": "Property disputes involve ownership, inheritance, partition, and transfer issues. Types include movable and immovable property governed by Transfer of Property Act 1882.",
    "inheritance": "Inheritance follows personal laws - Hindu Succession Act 1956 for Hindus, Indian Succession Act 1925 for Christians, and Muslim Personal Law for Muslims.",
    "registration": "Property registration under Registration Act 1908 is mandatory for immovable property above ₹100. Required documents include sale deed, NOC, and tax receipts.",
    "landlord": "Landlord-tenant disputes are governed by Rent Control Acts. Issues include rent increase, eviction, maintenance, and security deposit.",
    "partition": "Property partition can be done by mutual consent or court decree. Each co-owner has right to demand partition under Hindu Succession Act.",
    
    # Consumer Law
    "consumer": "Consumer protection under Consumer Protection Act 2019 covers defective goods, deficient services, unfair trade practices, and misleading advertisements.",
    "refund": "Refund rights depend on purchase terms, warranty, and consumer protection laws. E-commerce purchases have additional return/refund policies.",
    "warranty": "Warranty is manufacturer's guarantee for product quality. Breach of warranty entitles consumer to replacement, repair, or refund.",
    
    # Employment Law
    "employment": "Employment rights include fair wages, working hours, leave, termination notice, and workplace safety under various labor laws.",
    "termination": "Employment termination requires proper notice, due process, and compliance with Industrial Disputes Act 1947 and labor laws.",
    "salary": "Salary disputes involve non-payment, delayed payment, or wrongful deductions. Remedies available under Payment of Wages Act 1936.",
    
    # Contract Law
    "contract": "Contracts under Indian Contract Act 1872 require offer, acceptance, consideration, and legal capacity. Breach of contract attracts damages or specific performance.",
    "agreement": "Agreements become contracts when legally enforceable. Essential elements include free consent, lawful object, and certainty of terms.",
    
    # Cyber Law
    "cyber": "Cyber crimes under IT Act 2000 include hacking, identity theft, cyberstalking, and online fraud. Penalties range from fines to imprisonment.",
    "privacy": "Privacy rights under IT Act and Personal Data Protection Bill include data protection, consent requirements, and right to be forgotten.",
    
    # Constitutional Law
    "rights": "Fundamental rights under Constitution Articles 14-32 include equality, freedom, religion, culture, and constitutional remedies.",
    "writ": "Writ petitions under Article 32 (Supreme Court) and 226 (High Court) include habeas corpus, mandamus, prohibition, certiorari, and quo-warranto.",
    
    # Tax Law
    "tax": "Tax disputes involve income tax, GST, property tax, and customs duty. Remedies include appeals, revisions, and tribunal proceedings.",
    "gst": "GST (Goods and Services Tax) is levied on supply of goods and services. Rates vary from 0% to 28% based on product category.",
    
    # Banking Law
    "loan": "Loan disputes involve EMI defaults, foreclosure, and recovery proceedings. Banks can initiate SARFAESI Act proceedings for secured loans above ₹1 lakh.",
    "cheque": "Cheque bounce under Section 138 Negotiable Instruments Act is punishable with fine up to twice the cheque amount or imprisonment up to 2 years.",
    
    # Motor Vehicle Law
    "accident": "Motor vehicle accidents are covered under Motor Vehicles Act 1988. Compensation depends on injury severity, income loss, and negligence.",
    "insurance": "Motor insurance is mandatory under Motor Vehicles Act. Third-party insurance covers liability, while comprehensive covers own damage too.",
    
    # Real Estate Law
    "rera": "RERA (Real Estate Regulation Act) 2016 protects homebuyers' interests. Builders must register projects and provide timely possession.",
    
    # Intellectual Property
    "copyright": "Copyright under Copyright Act 1957 protects original literary, artistic, and musical works for author's lifetime plus 60 years.",
    "trademark": "Trademark registration under Trade Marks Act 1999 protects brand names, logos, and slogans for 10 years (renewable).",
    
    # Environmental Law
    "environment": "Environmental protection under Environment Protection Act 1986 and pollution control laws. Violations attract penalties and closure orders.",
    
    # Medical Law
    "medical": "Medical negligence involves breach of duty of care by healthcare professionals. Compensation available under Consumer Protection Act.",
    
    # Education Law
    "education": "Right to Education under Article 21A provides free and compulsory education to children aged 6-14 years.",
    
    # Senior Citizens
    "elderly": "Senior citizens' rights under Maintenance and Welfare of Parents and Senior Citizens Act 2007 include maintenance, medical care, and protection from abuse.",
    
    # Women's Rights & Gender Laws
    "domestic violence": "Domestic Violence Act 2005 protects women from physical, sexual, verbal, emotional, and economic abuse. Provides for protection orders, residence orders, and monetary relief.",
    "sexual harassment": "Sexual Harassment of Women at Workplace Act 2013 mandates Internal Complaints Committee (ICC) in organizations. Penalties include compensation and disciplinary action.",
    "dowry death": "Dowry death under IPC Section 304B presumes culpability if woman dies within 7 years of marriage due to dowry demands. Punishment is imprisonment for minimum 7 years.",
    "rape": "Rape under IPC Sections 375-376 includes various forms of sexual assault. Punishment ranges from 7 years to life imprisonment or death penalty in aggravated cases.",
    "acid attack": "Acid attack under IPC Section 326A/B is punishable with imprisonment for minimum 10 years extending to life. Free medical treatment and compensation provided to victims.",
    
    # Child Rights & Juvenile Laws
    "child abuse": "Child abuse is covered under POCSO Act 2012 for sexual offenses and JJ Act 2015 for other crimes. Special courts ensure speedy trials and victim protection.",
    "child marriage": "Child marriage is prohibited under Prohibition of Child Marriage Act 2006. Marriage of girl below 18 and boy below 21 is voidable and punishable.",
    "child custody": "Child custody prioritizes child's welfare under Guardians and Wards Act 1890. Courts consider child's age, preference, parent's financial stability and moral character.",
    "adoption laws": "Adoption is governed by Hindu Adoption and Maintenance Act 1956 for Hindus and JJ Act 2015 for others. Central Adoption Resource Authority (CARA) regulates adoptions.",
    
    # Labour & Industrial Laws
    "minimum wage": "Minimum Wages Act 1948 ensures minimum wage rates for scheduled employments. Rates vary by state and are revised periodically by government notification.",
    "provident fund": "Employees' Provident Fund Act 1952 mandates 12% contribution from employee and employer salary. Withdrawal allowed for specific purposes like house purchase, marriage.",
    "gratuity": "Payment of Gratuity Act 1972 provides lump sum payment to employees completing 5 years of service. Current rate is 15 days wages for each completed year.",
    "maternity leave": "Maternity Benefit Act 2017 provides 26 weeks paid leave to women employees. Includes 8 weeks pre-natal and 18 weeks post-natal leave.",
    "sexual harassment workplace": "Vishaka Guidelines and Sexual Harassment Act 2013 mandate zero tolerance policy. Every workplace must have Internal Complaints Committee (ICC).",
    "industrial dispute": "Industrial Disputes Act 1947 provides machinery for investigation and settlement of disputes between employers and workmen through conciliation and arbitration.",
    
    # Commercial & Business Laws
    "company law": "Companies Act 2013 governs incorporation, management, and winding up of companies. Provides for various types of companies and compliance requirements.",
    "partnership": "Partnership Act 1932 governs partnership firms. Partners have unlimited liability and joint responsibility for firm's debts and obligations.",
    "insolvency": "Insolvency and Bankruptcy Code 2016 provides time-bound resolution of insolvency. Corporate Insolvency Resolution Process (CIRP) must be completed within 330 days.",
    "arbitration": "Arbitration and Conciliation Act 2015 provides alternative dispute resolution mechanism. Awards are binding and enforceable like court decrees.",
    "competition law": "Competition Act 2002 prohibits anti-competitive practices, abuse of dominant position, and regulates combinations. Competition Commission of India (CCI) enforces the Act.",
    
    # Financial & Securities Laws
    "securities law": "Securities and Exchange Board of India (SEBI) Act 1992 regulates securities market. Protects investor interests and promotes development of securities market.",
    "mutual funds": "Mutual funds are regulated by SEBI. Provide diversified investment options with professional fund management. Subject to market risks and regulatory compliance.",
    "insider trading": "Insider trading is prohibited under SEBI Act. Trading on material non-public information attracts penalties including disgorgement of profits and imprisonment.",
    
    # Agricultural & Land Laws
    "land acquisition": "Land Acquisition Act 2013 provides fair compensation and rehabilitation for land acquisition. Requires social impact assessment and consent of affected families.",
    "agricultural laws": "Agricultural laws vary by state. Cover land ceiling, tenancy, marketing, and cooperative societies. Recent farm laws aimed at agricultural reforms.",
    "water rights": "Water rights are governed by state laws and Easements Act. Riparian rights, prior appropriation, and beneficial use principles determine water allocation.",
    
    # Information Technology Laws
    "data protection": "Personal Data Protection Bill (proposed) aims to protect personal data and privacy rights. Provides for data localization and consent requirements.",
    "e-commerce": "E-commerce is regulated by Consumer Protection Act 2019 and IT Act 2000. Covers online transactions, digital signatures, and consumer grievances.",
    "digital signature": "Digital signatures under IT Act 2000 have legal validity. Certified by Controller of Certifying Authorities (CCA) for secure electronic transactions.",
    
    # Administrative & Public Laws
    "rti": "Right to Information Act 2005 empowers citizens to seek information from public authorities. Promotes transparency and accountability in governance.",
    "pil": "Public Interest Litigation allows any citizen to approach courts for public causes. Relaxed standing requirements enable access to justice for marginalized sections.",
    "administrative law": "Administrative law governs functioning of administrative agencies. Principles include natural justice, reasonableness, and procedural fairness.",
    
    # Miscellaneous Laws
    "arms license": "Arms Act 1959 regulates manufacture, sale, and possession of arms and ammunition. License required from District Magistrate with strict verification process.",
    "passport": "Passport Act 1967 governs issuance of passports for international travel. Passport Seva Kendra provides online application and tracking facilities.",
    "driving license": "Motor Vehicles Act 1988 mandates driving license for vehicle operation. Different categories for different vehicle types with validity periods.",
    "food safety": "Food Safety and Standards Act 2006 ensures safe and wholesome food. FSSAI regulates food business operators and sets food safety standards.",
    "drugs control": "Drugs and Cosmetics Act 1940 regulates manufacture, sale, and distribution of drugs and cosmetics. Central and state drug controllers ensure compliance.",
    
    # Tribal & Minority Rights
    "tribal rights": "Scheduled Tribes and Other Traditional Forest Dwellers Act 2006 recognizes forest rights of tribal communities. Provides for community forest resource rights.",
    "minority rights": "National Commission for Minorities Act 1992 protects interests of religious and linguistic minorities. Investigates complaints and recommends measures.",
    
    # Disability Rights
    "disability rights": "Rights of Persons with Disabilities Act 2016 ensures equal opportunities and non-discrimination. Provides for accessibility, education, and employment rights.",
    
    # Sports & Entertainment Laws
    "sports law": "Sports laws cover doping, match-fixing, and sports governance. National Anti-Doping Agency (NADA) implements anti-doping measures in Indian sports."
}

KEYWORD_ALIASES = {
    # Criminal Law Aliases
    "arrest": "bail",
    "detention": "bail", 
    "custody": "bail",
    "killing": "murder",
    "homicide": "murder",
    "stealing": "theft",
    "robbery": "theft",
    "cheating": "fraud",
    "scam": "fraud",
    "beating": "assault",
    "violence": "assault",
    "abduction": "kidnapping",
    
    # Family Law Aliases
    "separation": "divorce",
    "alimony": "maintenance",
    "child support": "maintenance",
    "spousal support": "maintenance",
    
    # Women's Rights Aliases
    "domestic abuse": "domestic violence",
    "wife beating": "domestic violence",
    "workplace harassment": "sexual harassment",
    "eve teasing": "sexual harassment",
    "dowry torture": "dowry death",
    "sexual assault": "rape",
    "molestation": "rape",
    "acid throwing": "acid attack",
    
    # Child Rights Aliases
    "child sexual abuse": "child abuse",
    "pocso": "child abuse",
    "underage marriage": "child marriage",
    "child adoption": "adoption laws",
    
    # Property Law Aliases
    "land": "property",
    "house": "property",
    "real estate": "property",
    "will": "inheritance",
    "succession": "inheritance",
    "tenant": "landlord",
    "rent": "landlord",
    "property dispute": "property",
    
    # Employment Law Aliases
    "job": "employment",
    "work": "employment",
    "firing": "termination",
    "dismissal": "termination",
    "wages": "salary",
    "payment": "salary",
    "pf": "provident fund",
    "epf": "provident fund",
    "pregnancy leave": "maternity leave",
    "workplace sexual harassment": "sexual harassment workplace",
    
    # Business Law Aliases
    "business": "company law",
    "corporation": "company law",
    "firm": "partnership",
    "bankruptcy": "insolvency",
    "adr": "arbitration",
    "monopoly": "competition law",
    
    # Financial Law Aliases
    "stock market": "securities law",
    "share trading": "securities law",
    "sip": "mutual funds",
    "investment": "mutual funds",
    
    # Technology Law Aliases
    "hacking": "cyber",
    "online fraud": "cyber",
    "privacy": "data protection",
    "online shopping": "e-commerce",
    "digital certificate": "digital signature",
    
    # Constitutional Law Aliases
    "fundamental rights": "rights",
    "right to information": "rti",
    "public interest": "pil",
    
    # Tax Law Aliases
    "income tax": "tax",
    "goods and services tax": "gst",
    
    # Motor Vehicle Aliases
    "car accident": "accident",
    "vehicle": "accident",
    "motor insurance": "insurance",
    "dl": "driving license",
    
    # Real Estate Aliases
    "builder": "rera",
    "flat": "rera",
    "apartment": "rera",
    "home buyer": "rera",
    
    # IP Law Aliases
    "patent": "copyright",
    "brand": "trademark",
    "logo": "trademark",
    
    # Environmental Aliases
    "pollution": "environment",
    "green tribunal": "environment",
    
    # Medical Aliases
    "doctor": "medical",
    "hospital": "medical",
    "medical malpractice": "medical",
    
    # Education Aliases
    "school": "education",
    "rte": "education",
    
    # Senior Citizens Aliases
    "parents": "elderly",
    "senior": "elderly",
    "old age": "elderly",
    
    # Administrative Aliases
    "government information": "rti",
    "transparency": "rti",
    "social cause": "pil",
    
    # Miscellaneous Aliases
    "gun license": "arms license",
    "weapon": "arms license",
    "travel document": "passport",
    "international travel": "passport",
    "vehicle license": "driving license",
    "food adulteration": "food safety",
    "medicine": "drugs control",
    "pharmaceutical": "drugs control",
    
    # Rights Aliases
    "adivasi": "tribal rights",
    "forest dwellers": "tribal rights",
    "religious minority": "minority rights",
    "linguistic minority": "minority rights",
    "handicapped": "disability rights",
    "differently abled": "disability rights",
    "pwd": "disability rights",
    
    # Sports Aliases
    "doping": "sports law",
    "match fixing": "sports law",
    "athletics": "sports law"
}

# Define missing variables for legal topics
SPECIALIZED_LEGAL_AREAS = {
    # This can be expanded with more specialized legal areas as needed
    "detailed_solutions": "Legal solutions with step-by-step procedures",
    "case_law": "Legal precedents and landmark judgments",
    "procedural_law": "Court procedures and legal processes"
}

# Map topics to solution IDs for detailed solutions

@app.post("/chat")
async def chat(request: ChatRequest):
    start_time = time.time()
    
    # Detect language directive, and strip it for intent matching
    target_lang, stripped = detect_target_language_and_strip(request.message)
    user_msg = (stripped or request.message).lower()
    print(f"Received chat message: {user_msg}")
    
    # Log chat request
    await log_chat_event("anonymous", request.message)
    # Legal solutions request - simplified for memory optimization
    if user_msg.startswith("provide legal solutions for this problem:"):
        return format_structured_response(
            answer="Legal consultation service is temporarily unavailable.",
            legal_reference="Please refer to relevant Indian legal codes",
            explanation="For detailed legal advice, please consult with a qualified lawyer.",
            steps=["Contact a local lawyer with your documents", "Gather relevant case details", "Prepare necessary documentation"]
        )
    # First check comprehensive legal database
    comprehensive_answer = get_comprehensive_legal_info(user_msg)
    if comprehensive_answer:
        # Check if detailed legal solution is available
        solution_key = None
        for topic, solution_id in TOPIC_TO_SOLUTION.items():
            if topic.lower() in user_msg:
                solution_key = solution_id
                break
        
        if solution_key:
            solution_data = get_legal_solution(solution_key)
            if solution_data:
                detailed_solution = format_legal_solution(solution_data)
                return {"answer": f"{comprehensive_answer}\n\n--- DETAILED LEGAL SOLUTION ---\n{detailed_solution}"}
        
        return {"answer": comprehensive_answer}
    
    # Fallback to original FAQ system
    for key in list(FAQ.keys()) + list(KEYWORD_ALIASES.keys()):
        if key.lower() in user_msg:
            faq_answer = FAQ.get(key) or FAQ.get(KEYWORD_ALIASES.get(key, ""))
            if faq_answer:
                # Check if detailed solution available for this topic
                solution_key = TOPIC_TO_SOLUTION.get(key) or TOPIC_TO_SOLUTION.get(KEYWORD_ALIASES.get(key, ""))
                if solution_key:
                    solution_data = get_legal_solution(solution_key)
                    if solution_data:
                        detailed_solution = format_legal_solution(solution_data)
                        return {"answer": f"{faq_answer}\n\n--- DETAILED LEGAL SOLUTION ---\n{detailed_solution}"}
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
    temp_file_path = None
    try:
        # Validate file type
        allowed_extensions = {'.txt', '.pdf', '.docx'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise ValueError(f"Unsupported file type: {file_ext}. Allowed: {', '.join(allowed_extensions)}")
        
        # Save the uploaded file temporarily
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        print(f"📄 Processing file: {file.filename} ({len(content)} bytes)")
        
        # Parse and chunk the document
        chunks = parse_and_chunk(temp_file_path)
        print(f"📝 Created {len(chunks)} chunks")
        
        if not chunks:
            raise ValueError("No content could be extracted from the file")
        
        # Add chunks to the database with proper metadata
        metadata = [{"source": file.filename, "chunk_index": i, "file_type": file_ext} for i in range(len(chunks))]
        print(f"💾 Adding {len(chunks)} chunks to ChromaDB...")
        
        add_chunks_to_db(chunks, metadata)
        print("✅ Successfully added to ChromaDB")
        
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        
        # Log document upload
        await tracing.log_trace(
            TraceEvents.DOC_UPLOAD,
            {
                "filename": file.filename,
                "file_size": len(content),
                "file_type": file_ext,
                "chunks_created": len(chunks),
                "success": True
            }
        )
        
        return {
            "message": f"File '{file.filename}' uploaded and processed successfully.",
            "chunks_created": len(chunks),
            "file_size": len(content)
        }
        
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        
        # Clean up the temporary file on error
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass
        
        # Log upload error
        await tracing.log_trace(
            TraceEvents.DOC_ERROR,
            {
                "filename": file.filename if file else "unknown",
                "error": str(e),
                "success": False
            }
        )
        return {"error": f"Failed to process file: {str(e)}"}

@app.post("/legal-solution")
async def get_legal_solution_endpoint(request: ChatRequest):
    """Get detailed legal solution for a specific legal problem"""
    user_msg = request.message.lower()
    
    # Log the legal solution request
    await tracing.log_trace(
        "legal.solution_request",
        {
            "query": request.message,
            "timestamp": time.time()
        }
    )
    
    # Check if specific solution is available
    solution_key = None
    for topic, solution_id in TOPIC_TO_SOLUTION.items():
        if topic.lower() in user_msg:
            solution_key = solution_id
            break
    
    if solution_key:
        solution_data = get_legal_solution(solution_key)
        if solution_data:
            formatted_solution = format_legal_solution(solution_data)
            return {
                "solution_available": True,
                "topic": solution_data["topic"],
                "detailed_solution": formatted_solution,
                "solution_type": "comprehensive"
            }
    
    # Check comprehensive legal database
    comprehensive_answer = get_comprehensive_legal_info(user_msg)
    if comprehensive_answer:
        return {
            "solution_available": True,
            "topic": "General Legal Information",
            "detailed_solution": comprehensive_answer,
            "solution_type": "informational"
        }
    
    # Check original FAQ
    for key in list(FAQ.keys()) + list(KEYWORD_ALIASES.keys()):
        if key.lower() in user_msg:
            faq_answer = FAQ.get(key) or FAQ.get(KEYWORD_ALIASES.get(key, ""))
            if faq_answer:
                return {
                    "solution_available": True,
                    "topic": key.replace("_", " ").title(),
                    "detailed_solution": faq_answer,
                    "solution_type": "basic"
                }
    
    return {
        "solution_available": False,
        "message": "No specific legal solution found for your query. Please consult a qualified lawyer for personalized legal advice.",
        "suggestions": [
            "Try using more specific legal terms",
            "Mention the specific law or act you're asking about",
            "Include the type of legal issue (criminal, civil, family, etc.)",
            "Contact a local lawyer for detailed consultation"
        ]
    }

@app.get("/legal-topics")
async def get_all_legal_topics():
    """Get list of all available legal topics"""
    topics = {
        "comprehensive_topics": list(COMPREHENSIVE_LEGAL_FAQ.keys()),
        "specialized_areas": list(SPECIALIZED_LEGAL_AREAS.keys()),
        "detailed_solutions": list(TOPIC_TO_SOLUTION.keys()),
        "faq_topics": list(FAQ.keys()),
        "total_topics": len(COMPREHENSIVE_LEGAL_FAQ) + len(SPECIALIZED_LEGAL_AREAS) + len(FAQ)
    }
    return topics

@app.get("/admin/traces")
async def get_traces(
    event_type: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 50
):
    """Get system traces for monitoring and debugging"""
    traces = await tracing.get_traces(
        event_type=event_type,
        user_id=user_id,
        limit=limit
    )
    return {
        "traces": traces,
        "count": len(traces),
        "filters": {
            "event_type": event_type,
            "user_id": user_id,
            "limit": limit
        }
    }

@app.get("/admin/stats")
async def get_system_stats():
    """Get overall system statistics"""
    stats = await tracing.get_system_stats()
    return stats

@app.get("/admin/user-activity/{user_id}")
async def get_user_activity(user_id: str, days: int = 7):
    """Get user activity summary"""
    activity = await tracing.get_user_activity(user_id, days)
    return activity

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

# ==================== PAYMENT ENDPOINTS ====================

@app.post("/api/create-payment-order")
async def create_payment_order_endpoint(payment_request: PaymentRequest):
    """
    Create a Razorpay order for subscription payment
    """
    try:
        order_data = create_payment_order(
            plan=payment_request.plan,
            user_id=payment_request.user_id,
            user_email=payment_request.user_email,
            user_name=payment_request.user_name
        )
        return {"success": True, "data": order_data}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/verify-payment")
async def verify_payment_endpoint(verification: PaymentVerification):
    """
    Verify payment and update user subscription
    """
    try:
        # Verify payment signature
        is_valid = verify_payment_signature(
            verification.razorpay_order_id,
            verification.razorpay_payment_id,
            verification.razorpay_signature
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid payment signature")
        
        # Process successful payment
        subscription = process_successful_payment(
            verification.razorpay_order_id,
            verification.razorpay_payment_id,
            verification.user_id
        )
        
        # Store subscription in database
        users_collection = get_users_collection()
        await users_collection.update_one(
            {"_id": verification.user_id},
            {
                "$set": {
                    "subscription": {
                        "plan": subscription.plan,
                        "status": subscription.status,
                        "expires_at": subscription.expires_at,
                        "payment_id": subscription.payment_id,
                        "order_id": subscription.order_id,
                        "updated_at": datetime.now()
                    }
                }
            }
        )
        
        return {
            "success": True,
            "message": "Payment verified and subscription activated",
            "subscription": subscription.dict()
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/subscription-status/{user_id}")
async def get_subscription_status(user_id: str):
    """
    Get current subscription status for a user
    """
    try:
        users_collection = get_users_collection()
        user = await users_collection.find_one({"_id": user_id})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        subscription_data = user.get("subscription", {})
        
        if not subscription_data:
            # Return free tier defaults
            return {
                "plan": "free",
                "status": "active",
                "limits": get_subscription_limits("free"),
                "expires_at": None
            }
        
        # Check if subscription is still active
        subscription = SubscriptionStatus(**subscription_data)
        active = is_subscription_active(subscription)
        
        return {
            "plan": subscription.plan,
            "status": "active" if active else "expired",
            "limits": get_subscription_limits(subscription.plan),
            "expires_at": subscription.expires_at,
            "payment_id": subscription.payment_id
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhook/razorpay")
async def razorpay_webhook(request: Request):
    """
    Handle Razorpay webhooks for payment events
    """
    try:
        payload = await request.body()
        signature = request.headers.get("X-Razorpay-Signature")
        
        # Verify webhook signature (implement webhook secret verification)
        webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
        
        if webhook_secret:
            # Verify webhook signature here if needed
            pass
        
        # Parse webhook payload
        webhook_data = json.loads(payload.decode('utf-8'))
        event = webhook_data.get("event")
        
        if event == "payment.captured":
            # Handle successful payment
            payment_entity = webhook_data.get("payload", {}).get("payment", {}).get("entity", {})
            order_id = payment_entity.get("order_id")
            payment_id = payment_entity.get("id")
            
            # Additional processing can be added here
            log_system_event(f"Payment captured: {payment_id} for order: {order_id}")
        
        return {"status": "ok"}
        
    except Exception as e:
        log_system_event(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # Use Render's PORT or default to 8000 for local dev
    uvicorn.run(app, host="0.0.0.0", port=port)