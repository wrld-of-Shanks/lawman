"""
Legal Solutions Guided Flow System
Provides step-by-step legal problem solving with category selection and follow-up questions
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from auth_mongo import get_current_user
import logging

# Create router
solutions_router = APIRouter()

# Request/Response models
class CategorySelectionRequest(BaseModel):
    user_id: Optional[str] = None

class CategorySelectionResponse(BaseModel):
    categories: List[Dict[str, Any]]
    session_id: str

class FollowUpRequest(BaseModel):
    session_id: str
    category_id: str
    answers: Optional[Dict[str, str]] = None

class FollowUpResponse(BaseModel):
    questions: List[Dict[str, Any]]
    session_id: str
    step: int

class SolutionRequest(BaseModel):
    session_id: str
    category_id: str
    answers: Dict[str, str]

class SolutionResponse(BaseModel):
    legal_rights: str
    applicable_laws: List[str]
    action_plan: List[Dict[str, Any]]
    auto_generate_options: List[str]
    session_id: str

# Legal Problem Categories
LEGAL_CATEGORIES = {
    "property_rent": {
        "id": "property_rent",
        "title": "🏠 Property / Rent Dispute",
        "description": "Issues related to property ownership, rent disputes, landlord-tenant problems",
        "icon": "🏠",
        "questions": [
            {
                "id": "dispute_type",
                "question": "What type of property dispute are you facing?",
                "type": "select",
                "options": [
                    "Rent increase dispute",
                    "Eviction notice received", 
                    "Security deposit not returned",
                    "Property damage claims",
                    "Illegal occupation",
                    "Maintenance issues"
                ]
            },
            {
                "id": "property_details",
                "question": "Please provide property details (location, rent amount, lease duration)",
                "type": "text",
                "placeholder": "e.g., 2BHK in Mumbai, ₹25,000/month, 11-month lease"
            },
            {
                "id": "timeline",
                "question": "When did this issue start? Any notices served?",
                "type": "text",
                "placeholder": "e.g., Issue started 2 months ago, received eviction notice last week"
            }
        ]
    },
    "fraud_recovery": {
        "id": "fraud_recovery", 
        "title": "💰 Cheating / Fraud / Loan Recovery",
        "description": "Financial fraud, cheating, loan defaults, recovery issues",
        "icon": "💰",
        "questions": [
            {
                "id": "fraud_type",
                "question": "What type of financial issue are you facing?",
                "type": "select",
                "options": [
                    "Online fraud / UPI fraud",
                    "Investment scam",
                    "Loan not repaid",
                    "Cheque bounce",
                    "Credit card fraud",
                    "Business partnership fraud"
                ]
            },
            {
                "id": "amount_details",
                "question": "What is the amount involved and transaction details?",
                "type": "text",
                "placeholder": "e.g., ₹50,000 transferred via UPI on 15th Jan 2024"
            },
            {
                "id": "evidence",
                "question": "What evidence do you have? (WhatsApp chats, receipts, bank statements)",
                "type": "text",
                "placeholder": "e.g., WhatsApp messages, bank transfer receipts, signed agreement"
            }
        ]
    },
    "family_marriage": {
        "id": "family_marriage",
        "title": "❤️ Divorce / Marriage / Maintenance", 
        "description": "Family disputes, divorce proceedings, maintenance issues",
        "icon": "❤️",
        "questions": [
            {
                "id": "issue_type",
                "question": "What family law issue are you facing?",
                "type": "select",
                "options": [
                    "Want to file for divorce",
                    "Maintenance/alimony dispute",
                    "Child custody issue",
                    "Domestic violence",
                    "Property settlement",
                    "Marriage registration"
                ]
            },
            {
                "id": "marriage_details",
                "question": "Marriage details (date, type of marriage, children if any)",
                "type": "text",
                "placeholder": "e.g., Hindu marriage in 2018, one child aged 4 years"
            },
            {
                "id": "current_situation",
                "question": "Current living situation and main issues",
                "type": "text",
                "placeholder": "e.g., Living separately for 6 months, husband not paying maintenance"
            }
        ]
    },
    "criminal_fir": {
        "id": "criminal_fir",
        "title": "⚖️ FIR / Police Complaint / Criminal Case",
        "description": "Criminal complaints, FIR filing, police cases",
        "icon": "⚖️",
        "questions": [
            {
                "id": "crime_type",
                "question": "What type of criminal issue are you facing?",
                "type": "select",
                "options": [
                    "Theft / Robbery",
                    "Assault / Physical violence",
                    "Harassment / Stalking",
                    "Fraud / Cheating",
                    "Cybercrime",
                    "Domestic violence"
                ]
            },
            {
                "id": "incident_details",
                "question": "When and where did the incident occur?",
                "type": "text",
                "placeholder": "e.g., On 10th March 2024 at 8 PM near City Mall, Mumbai"
            },
            {
                "id": "complaint_status",
                "question": "Have you filed a police complaint? If yes, what's the status?",
                "type": "text",
                "placeholder": "e.g., Filed FIR No. 123/2024 at XYZ Police Station, under investigation"
            }
        ]
    },
    "employment_contract": {
        "id": "employment_contract",
        "title": "📜 Contract Breach / Employment Issue",
        "description": "Employment disputes, contract violations, workplace issues",
        "icon": "📜",
        "questions": [
            {
                "id": "employment_issue",
                "question": "What employment or contract issue are you facing?",
                "type": "select",
                "options": [
                    "Wrongful termination",
                    "Salary not paid",
                    "Contract breach by employer",
                    "Workplace harassment",
                    "Non-compete violation",
                    "Service agreement dispute"
                ]
            },
            {
                "id": "employment_details",
                "question": "Employment details (company, position, salary, duration)",
                "type": "text",
                "placeholder": "e.g., Software Engineer at ABC Corp, ₹8 LPA, worked for 2 years"
            },
            {
                "id": "contract_terms",
                "question": "Key contract terms and what was violated?",
                "type": "text",
                "placeholder": "e.g., 3-month notice period, terminated without notice, 2 months salary pending"
            }
        ]
    }
}

# Legal Solutions Database
LEGAL_SOLUTIONS = {
    "property_rent": {
        "rent_increase": {
            "legal_rights": "Under the Rent Control Act, landlords cannot arbitrarily increase rent. Tenants have the right to challenge unreasonable rent increases before the Rent Controller.",
            "applicable_laws": [
                "State Rent Control Act",
                "Transfer of Property Act, 1882 - Section 108", 
                "Indian Contract Act, 1872"
            ],
            "action_plan": [
                {
                    "step": 1,
                    "action": "Review your rent agreement for rent revision clauses",
                    "details": "Check if the agreement specifies conditions for rent increase"
                },
                {
                    "step": 2, 
                    "action": "Send legal notice to landlord",
                    "details": "Object to unreasonable rent increase citing legal provisions",
                    "auto_generate": "rent_objection_notice"
                },
                {
                    "step": 3,
                    "action": "File application before Rent Controller",
                    "details": "If landlord persists, approach Rent Controller for fair rent fixation"
                },
                {
                    "step": 4,
                    "action": "Continue paying current rent",
                    "details": "Keep paying existing rent to avoid eviction proceedings"
                }
            ]
        },
        "eviction_notice": {
            "legal_rights": "Tenants cannot be evicted without proper legal grounds and due process. Landlords must follow procedure under Rent Control Act.",
            "applicable_laws": [
                "State Rent Control Act - Eviction provisions",
                "Transfer of Property Act, 1882 - Section 111",
                "Code of Civil Procedure, 1908"
            ],
            "action_plan": [
                {
                    "step": 1,
                    "action": "Examine eviction notice for legal grounds",
                    "details": "Check if notice cites valid reasons like non-payment, subletting, etc."
                },
                {
                    "step": 2,
                    "action": "Send reply to eviction notice",
                    "details": "Contest invalid grounds and assert your tenancy rights",
                    "auto_generate": "eviction_reply_notice"
                },
                {
                    "step": 3,
                    "action": "File counter-application if needed",
                    "details": "Approach Rent Controller to challenge wrongful eviction"
                }
            ]
        }
    },
    "fraud_recovery": {
        "online_fraud": {
            "legal_rights": "Victims of online fraud can file complaints under IT Act and IPC. Banks are liable to reverse fraudulent transactions in many cases.",
            "applicable_laws": [
                "Information Technology Act, 2000 - Section 66C, 66D",
                "Indian Penal Code - Section 420 (Cheating)",
                "Indian Penal Code - Section 468 (Forgery)"
            ],
            "action_plan": [
                {
                    "step": 1,
                    "action": "Immediately report to bank/payment gateway",
                    "details": "Contact customer care and request transaction reversal"
                },
                {
                    "step": 2,
                    "action": "File cybercrime complaint online",
                    "details": "Register complaint on cybercrime.gov.in portal with evidence"
                },
                {
                    "step": 3,
                    "action": "File FIR at local police station",
                    "details": "Lodge FIR under IPC Section 420 and IT Act provisions",
                    "auto_generate": "cybercrime_fir_draft"
                },
                {
                    "step": 4,
                    "action": "Send legal notice to fraudster (if known)",
                    "details": "Demand refund and threaten legal action",
                    "auto_generate": "fraud_recovery_notice"
                }
            ]
        },
        "loan_recovery": {
            "legal_rights": "Lenders have right to recover loans through legal means. Can file civil suit or criminal case depending on circumstances.",
            "applicable_laws": [
                "Indian Contract Act, 1872 - Sections 124-147",
                "Negotiable Instruments Act, 1881 - Section 138",
                "Code of Civil Procedure, 1908 - Order 37"
            ],
            "action_plan": [
                {
                    "step": 1,
                    "action": "Send demand notice to borrower",
                    "details": "Formal demand for loan repayment with interest calculation",
                    "auto_generate": "loan_demand_notice"
                },
                {
                    "step": 2,
                    "action": "File civil suit for recovery",
                    "details": "File suit under Order 37 CPC for summary judgment"
                },
                {
                    "step": 3,
                    "action": "If cheque given, file Section 138 case",
                    "details": "Criminal case for cheque bounce with penalty"
                }
            ]
        }
    },
    "family_marriage": {
        "divorce": {
            "legal_rights": "Both spouses have equal rights in divorce proceedings. Grounds for divorce are specified under respective personal laws.",
            "applicable_laws": [
                "Hindu Marriage Act, 1955 - Section 13",
                "Special Marriage Act, 1954 - Section 27", 
                "Indian Divorce Act, 1869",
                "Code of Civil Procedure, 1908"
            ],
            "action_plan": [
                {
                    "step": 1,
                    "action": "Attempt mediation/counselling",
                    "details": "Try family counselling or mediation before legal proceedings"
                },
                {
                    "step": 2,
                    "action": "Gather evidence for divorce grounds",
                    "details": "Collect proof of cruelty, desertion, or other valid grounds"
                },
                {
                    "step": 3,
                    "action": "File divorce petition in family court",
                    "details": "Submit petition with evidence and seek appropriate relief",
                    "auto_generate": "divorce_petition_draft"
                },
                {
                    "step": 4,
                    "action": "Negotiate settlement terms",
                    "details": "Discuss alimony, child custody, and property division"
                }
            ]
        }
    },
    "criminal_fir": {
        "theft": {
            "legal_rights": "Victims of theft can file FIR and claim compensation. Police are duty-bound to investigate and recover stolen property.",
            "applicable_laws": [
                "Indian Penal Code - Sections 378-382 (Theft)",
                "Code of Criminal Procedure, 1973 - Section 154",
                "Indian Evidence Act, 1872"
            ],
            "action_plan": [
                {
                    "step": 1,
                    "action": "File FIR immediately at nearest police station",
                    "details": "Report theft with detailed description of stolen items",
                    "auto_generate": "theft_fir_draft"
                },
                {
                    "step": 2,
                    "action": "Provide evidence to police",
                    "details": "Submit CCTV footage, witness statements, purchase receipts"
                },
                {
                    "step": 3,
                    "action": "Follow up on investigation",
                    "details": "Regular follow-up with investigating officer for progress"
                },
                {
                    "step": 4,
                    "action": "File insurance claim if applicable",
                    "details": "Claim insurance for stolen items with FIR copy"
                }
            ]
        }
    },
    "employment_contract": {
        "wrongful_termination": {
            "legal_rights": "Employees have right to proper notice, due process, and compensation for wrongful termination under labor laws.",
            "applicable_laws": [
                "Industrial Disputes Act, 1947",
                "Payment of Wages Act, 1936",
                "Indian Contract Act, 1872",
                "Shops and Establishments Act (State-specific)"
            ],
            "action_plan": [
                {
                    "step": 1,
                    "action": "Review employment contract and company policy",
                    "details": "Check termination clauses, notice period, and disciplinary procedure"
                },
                {
                    "step": 2,
                    "action": "Send legal notice to employer",
                    "details": "Demand proper notice pay, pending salary, and reinstatement",
                    "auto_generate": "wrongful_termination_notice"
                },
                {
                    "step": 3,
                    "action": "File complaint with Labor Commissioner",
                    "details": "Approach labor authorities for conciliation and settlement"
                },
                {
                    "step": 4,
                    "action": "File civil suit for damages",
                    "details": "Claim compensation for wrongful termination and mental harassment"
                }
            ]
        }
    }
}

# Session storage (in production, use Redis or database)
active_sessions = {}

import uuid
import time

@solutions_router.get("/categories", response_model=CategorySelectionResponse)
async def get_legal_categories():
    """Get all available legal problem categories"""
    
    session_id = str(uuid.uuid4())
    
    categories = []
    for cat_id, cat_data in LEGAL_CATEGORIES.items():
        categories.append({
            "id": cat_id,
            "title": cat_data["title"],
            "description": cat_data["description"], 
            "icon": cat_data["icon"]
        })
    
    # Store session
    active_sessions[session_id] = {
        "created_at": time.time(),
        "step": 1,
        "category_id": None,
        "answers": {}
    }
    
    return CategorySelectionResponse(
        categories=categories,
        session_id=session_id
    )

@solutions_router.post("/questions", response_model=FollowUpResponse)
async def get_follow_up_questions(request: FollowUpRequest):
    """Get follow-up questions for selected category"""
    
    if request.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if request.category_id not in LEGAL_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    category = LEGAL_CATEGORIES[request.category_id]
    
    # Update session
    active_sessions[request.session_id].update({
        "category_id": request.category_id,
        "step": 2
    })
    
    return FollowUpResponse(
        questions=category["questions"],
        session_id=request.session_id,
        step=2
    )

@solutions_router.post("/solution", response_model=SolutionResponse)
async def generate_legal_solution(
    request: SolutionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate comprehensive legal solution based on user inputs"""
    
    if request.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[request.session_id]
    
    if not request.category_id or request.category_id not in LEGAL_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # Update session with answers
    session["answers"] = request.answers
    session["step"] = 3
    
    # Generate solution based on category and answers
    solution = _generate_solution(request.category_id, request.answers)
    
    return SolutionResponse(
        legal_rights=solution["legal_rights"],
        applicable_laws=solution["applicable_laws"],
        action_plan=solution["action_plan"],
        auto_generate_options=solution["auto_generate_options"],
        session_id=request.session_id
    )

def _generate_solution(category_id: str, answers: Dict[str, str]) -> Dict[str, Any]:
    """Generate legal solution based on category and user answers"""
    
    # Get base solution template
    category_solutions = LEGAL_SOLUTIONS.get(category_id, {})
    
    # Determine specific solution based on answers
    solution_key = _determine_solution_key(category_id, answers)
    
    if solution_key and solution_key in category_solutions:
        base_solution = category_solutions[solution_key]
    else:
        # Fallback to generic solution
        base_solution = _create_generic_solution(category_id, answers)
    
    # Customize solution based on user inputs
    customized_solution = _customize_solution(base_solution, answers)
    
    return customized_solution

def _determine_solution_key(category_id: str, answers: Dict[str, str]) -> str:
    """Determine which specific solution to use based on user answers"""
    
    if category_id == "property_rent":
        dispute_type = answers.get("dispute_type", "").lower()
        if "rent increase" in dispute_type:
            return "rent_increase"
        elif "eviction" in dispute_type:
            return "eviction_notice"
    
    elif category_id == "fraud_recovery":
        fraud_type = answers.get("fraud_type", "").lower()
        if "online fraud" in fraud_type or "upi fraud" in fraud_type:
            return "online_fraud"
        elif "loan" in fraud_type:
            return "loan_recovery"
    
    elif category_id == "family_marriage":
        issue_type = answers.get("issue_type", "").lower()
        if "divorce" in issue_type:
            return "divorce"
    
    elif category_id == "criminal_fir":
        crime_type = answers.get("crime_type", "").lower()
        if "theft" in crime_type or "robbery" in crime_type:
            return "theft"
    
    elif category_id == "employment_contract":
        employment_issue = answers.get("employment_issue", "").lower()
        if "termination" in employment_issue:
            return "wrongful_termination"
    
    return None

def _create_generic_solution(category_id: str, answers: Dict[str, str]) -> Dict[str, Any]:
    """Create generic solution when specific solution not found"""
    
    generic_solutions = {
        "property_rent": {
            "legal_rights": "Tenants and landlords have specific rights under Rent Control Acts and Transfer of Property Act. Disputes should be resolved through proper legal channels.",
            "applicable_laws": ["State Rent Control Act", "Transfer of Property Act, 1882", "Indian Contract Act, 1872"],
            "action_plan": [
                {"step": 1, "action": "Review your rental agreement", "details": "Understand your rights and obligations"},
                {"step": 2, "action": "Attempt amicable resolution", "details": "Try to resolve through discussion"},
                {"step": 3, "action": "Send legal notice", "details": "Formal notice stating your position"},
                {"step": 4, "action": "Approach Rent Controller", "details": "File application for legal remedy"}
            ]
        },
        "fraud_recovery": {
            "legal_rights": "Fraud victims can pursue both civil and criminal remedies. File complaints with police and approach courts for recovery.",
            "applicable_laws": ["Indian Penal Code - Section 420", "Indian Contract Act, 1872", "Information Technology Act, 2000"],
            "action_plan": [
                {"step": 1, "action": "Collect all evidence", "details": "Gather documents, communications, transaction records"},
                {"step": 2, "action": "File police complaint", "details": "Lodge FIR for fraud under relevant sections"},
                {"step": 3, "action": "Send legal notice", "details": "Demand recovery of defrauded amount"},
                {"step": 4, "action": "File civil suit", "details": "Claim damages and recovery through court"}
            ]
        }
    }
    
    return generic_solutions.get(category_id, {
        "legal_rights": "You have legal rights under Indian law. Consult a lawyer for specific advice.",
        "applicable_laws": ["Indian Constitution", "Relevant statutory provisions"],
        "action_plan": [
            {"step": 1, "action": "Consult a lawyer", "details": "Get professional legal advice"},
            {"step": 2, "action": "Gather evidence", "details": "Collect all relevant documents"},
            {"step": 3, "action": "Explore legal remedies", "details": "Consider available legal options"}
        ]
    })

def _customize_solution(base_solution: Dict[str, Any], answers: Dict[str, str]) -> Dict[str, Any]:
    """Customize solution based on user-specific inputs"""
    
    customized = base_solution.copy()
    
    # Add auto-generation options based on action plan
    auto_generate_options = []
    for step in customized.get("action_plan", []):
        if step.get("auto_generate"):
            auto_generate_options.append(step["auto_generate"])
    
    customized["auto_generate_options"] = auto_generate_options
    
    # Customize legal rights based on specific details
    if "amount_details" in answers:
        amount_info = answers["amount_details"]
        customized["legal_rights"] += f" In your case involving {amount_info}, you have additional rights to claim interest and compensation."
    
    return customized

@solutions_router.get("/session/{session_id}")
async def get_session_status(session_id: str):
    """Get current session status and progress"""
    
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    return {
        "session_id": session_id,
        "step": session["step"],
        "category_id": session.get("category_id"),
        "answers": session.get("answers", {}),
        "created_at": session["created_at"]
    }

@solutions_router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear/delete a session"""
    
    if session_id in active_sessions:
        del active_sessions[session_id]
        return {"message": "Session cleared successfully"}
    
    raise HTTPException(status_code=404, detail="Session not found")
