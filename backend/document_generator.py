"""
Legal Document Auto-Generator
Generates legal notices, complaints, and other legal documents based on user inputs
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from auth_mongo import get_current_user
import logging
from datetime import datetime, timedelta

# Create router
generator_router = APIRouter()

# Request/Response models
class DocumentGenerationRequest(BaseModel):
    document_type: str
    template_data: Dict[str, Any]
    user_details: Dict[str, str]

class DocumentGenerationResponse(BaseModel):
    document_content: str
    document_type: str
    generated_at: str
    download_url: Optional[str] = None

# Legal Document Templates
DOCUMENT_TEMPLATES = {
    "rent_objection_notice": {
        "title": "Legal Notice - Objection to Rent Increase",
        "template": """
LEGAL NOTICE

To,
{landlord_name}
{landlord_address}

Subject: Objection to Unreasonable Rent Increase - Property at {property_address}

Dear Sir/Madam,

I, {tenant_name}, am writing this legal notice to formally object to your demand for rent increase for the above-mentioned property.

FACTS:
1. I am the lawful tenant of the property situated at {property_address} under a rental agreement dated {agreement_date}.
2. The current monthly rent is ₹{current_rent} as per the agreement.
3. You have demanded an increase in rent to ₹{proposed_rent} vide your notice dated {notice_date}.
4. This increase of ₹{increase_amount} ({increase_percentage}%) is unreasonable and not justified under law.

LEGAL POSITION:
1. Under the {state} Rent Control Act, landlords cannot arbitrarily increase rent without valid grounds.
2. Section 108 of the Transfer of Property Act, 1882 governs landlord-tenant relationships.
3. Any rent increase must be reasonable and in accordance with the rental agreement terms.

DEMAND:
I hereby demand that you:
1. Withdraw the unreasonable rent increase demand immediately.
2. Continue to accept the current rent of ₹{current_rent} as per the existing agreement.
3. Refrain from taking any coercive action against me.

CONSEQUENCES:
Please note that if you persist with this unreasonable demand or take any coercive action, I shall be constrained to:
1. File an application before the Rent Controller under the Rent Control Act.
2. Claim damages for harassment and mental agony.
3. Take such other legal action as deemed fit.

This notice is served upon you to give you an opportunity to reconsider your position and act in accordance with law.

Yours faithfully,

{tenant_name}
Date: {current_date}
Place: {place}

Through: Advocate
        """,
        "required_fields": [
            "landlord_name", "landlord_address", "property_address", "tenant_name",
            "agreement_date", "current_rent", "proposed_rent", "notice_date", "state", "place"
        ]
    },
    
    "eviction_reply_notice": {
        "title": "Reply to Eviction Notice",
        "template": """
REPLY TO EVICTION NOTICE

To,
{landlord_name}
{landlord_address}

Subject: Reply to Eviction Notice dated {eviction_notice_date} - Property at {property_address}

Dear Sir/Madam,

I, {tenant_name}, have received your eviction notice dated {eviction_notice_date} regarding the above-mentioned property. I hereby submit my reply as follows:

FACTS:
1. I am the lawful tenant of the property under a valid rental agreement dated {agreement_date}.
2. I have been regularly paying rent and maintaining the property in good condition.
3. Your eviction notice is based on {eviction_grounds} which I deny.

MY RESPONSE:
1. {response_to_grounds}
2. I have not violated any terms of the rental agreement.
3. I am a protected tenant under the {state} Rent Control Act.
4. The eviction notice does not comply with the mandatory requirements under law.

LEGAL POSITION:
1. Under Section 111 of the Transfer of Property Act, 1882, a tenancy can only be terminated on valid grounds.
2. The {state} Rent Control Act provides protection to tenants against arbitrary eviction.
3. Proper procedure must be followed for any eviction proceedings.

PRAYER:
I request you to:
1. Withdraw the illegal eviction notice immediately.
2. Allow me to continue as a lawful tenant.
3. Accept rent regularly as per the agreement.

WARNING:
If you proceed with illegal eviction or harassment, I shall be constrained to:
1. File a complaint before the Rent Controller.
2. Claim damages for illegal eviction attempt.
3. Take appropriate legal action for protection of my tenancy rights.

This reply is served to protect my legal rights and tenancy interests.

Yours faithfully,

{tenant_name}
Date: {current_date}
Place: {place}

Through: Advocate
        """,
        "required_fields": [
            "landlord_name", "landlord_address", "property_address", "tenant_name",
            "eviction_notice_date", "agreement_date", "eviction_grounds", "response_to_grounds", "state", "place"
        ]
    },
    
    "cybercrime_fir_draft": {
        "title": "FIR Draft - Cybercrime/Online Fraud",
        "template": """
FIR DRAFT - CYBERCRIME COMPLAINT

To,
The Station House Officer,
{police_station}
{police_station_address}

Subject: FIR for Cybercrime/Online Fraud under IT Act 2000 and IPC

Respected Sir/Madam,

I, {complainant_name}, aged {age} years, son/daughter of {father_name}, residing at {complainant_address}, hereby lodge this complaint for registration of FIR against unknown fraudsters.

BRIEF FACTS:
1. On {incident_date}, I received a {fraud_method} from an unknown person.
2. The fraudster posed as {fraudster_identity} and convinced me to {fraud_action}.
3. I transferred ₹{fraud_amount} to the account number {account_details}.
4. Later I realized it was a fraud when {realization_details}.
5. I immediately contacted my bank and the transaction could not be reversed.

EVIDENCE:
1. Screenshots of {evidence_type}
2. Bank transaction details showing transfer of ₹{fraud_amount}
3. {additional_evidence}

SECTIONS APPLICABLE:
1. Section 66C of Information Technology Act, 2000 (Identity Theft)
2. Section 66D of Information Technology Act, 2000 (Cheating by personation using computer resource)
3. Section 420 of Indian Penal Code (Cheating and dishonestly inducing delivery of property)
4. Section 468 of Indian Penal Code (Forgery for purpose of cheating)

PRAYER:
I request you to:
1. Register FIR under the above-mentioned sections
2. Investigate the matter thoroughly
3. Trace and freeze the fraudulent accounts
4. Arrest the accused and recover the defrauded amount
5. Take necessary action to prevent such frauds

I am ready to cooperate in the investigation and provide any additional information required.

Yours faithfully,

{complainant_name}
Date: {current_date}
Place: {place}

Attachments:
1. Copy of transaction receipts
2. Screenshots of fraudulent communication
3. Bank statement
4. Identity proof
        """,
        "required_fields": [
            "complainant_name", "age", "father_name", "complainant_address", "police_station",
            "police_station_address", "incident_date", "fraud_method", "fraudster_identity",
            "fraud_action", "fraud_amount", "account_details", "realization_details",
            "evidence_type", "additional_evidence", "place"
        ]
    },
    
    "fraud_recovery_notice": {
        "title": "Legal Notice - Fraud Recovery",
        "template": """
LEGAL NOTICE FOR RECOVERY OF DEFRAUDED AMOUNT

To,
{accused_name}
{accused_address}

Subject: Legal Notice for Recovery of ₹{fraud_amount} - Fraud and Cheating

Dear Sir/Madam,

I, {complainant_name}, through this legal notice, demand immediate refund of ₹{fraud_amount} fraudulently obtained by you.

FACTS:
1. On {transaction_date}, you approached me with a fraudulent scheme of {fraud_scheme}.
2. You induced me to transfer ₹{fraud_amount} by making false representations about {false_representations}.
3. You provided fake documents/proofs including {fake_documents}.
4. After receiving the money, you disappeared and stopped responding to my calls/messages.
5. Your actions constitute fraud, cheating, and criminal breach of trust.

LEGAL POSITION:
1. Your acts fall under Section 420 of IPC (Cheating and dishonestly inducing delivery of property).
2. Section 406 of IPC (Criminal breach of trust) is also applicable.
3. You are liable to refund the entire amount with interest and damages.

DEMAND:
I hereby demand that you:
1. Refund ₹{fraud_amount} immediately within 15 days of this notice.
2. Pay interest @ 18% per annum from {transaction_date}.
3. Compensate ₹{compensation_amount} for mental harassment and legal expenses.

TOTAL DEMAND: ₹{total_demand}

CONSEQUENCES OF NON-COMPLIANCE:
If you fail to comply with this demand within 15 days, I shall be constrained to:
1. File criminal complaint under Sections 420, 406 IPC.
2. File civil suit for recovery with damages and interest.
3. Report the matter to police and relevant authorities.
4. Take such other legal action as deemed appropriate.

This notice is served to give you one final opportunity to settle the matter amicably and avoid legal consequences.

Yours faithfully,

{complainant_name}
Date: {current_date}
Place: {place}

Through: Advocate
        """,
        "required_fields": [
            "accused_name", "accused_address", "complainant_name", "fraud_amount",
            "transaction_date", "fraud_scheme", "false_representations", "fake_documents",
            "compensation_amount", "total_demand", "place"
        ]
    },
    
    "loan_demand_notice": {
        "title": "Legal Notice - Loan Recovery Demand",
        "template": """
LEGAL NOTICE FOR LOAN RECOVERY

To,
{borrower_name}
{borrower_address}

Subject: Demand for Repayment of Loan Amount ₹{loan_amount}

Dear Sir/Madam,

I, {lender_name}, hereby serve this legal notice demanding immediate repayment of the loan amount advanced to you.

LOAN DETAILS:
1. Loan Amount: ₹{loan_amount}
2. Date of Loan: {loan_date}
3. Rate of Interest: {interest_rate}% per annum
4. Repayment Date: {due_date}
5. Purpose: {loan_purpose}

SECURITY/GUARANTEE:
{security_details}

FACTS:
1. You approached me for financial assistance and I advanced ₹{loan_amount} on {loan_date}.
2. You executed {loan_documents} acknowledging the debt.
3. You promised to repay the amount by {due_date} with interest.
4. Despite repeated requests, you have failed to repay the loan amount.
5. The total outstanding amount as on {current_date} is ₹{outstanding_amount}.

CALCULATION:
Principal Amount: ₹{loan_amount}
Interest ({interest_rate}% p.a. for {duration}): ₹{interest_amount}
Total Outstanding: ₹{outstanding_amount}

LEGAL POSITION:
1. This is a clear case of breach of contract under Indian Contract Act, 1872.
2. You are liable to pay the principal amount with interest and costs.
3. Legal action can be initiated for recovery under Order 37 of CPC.

DEMAND:
I hereby demand that you:
1. Pay ₹{outstanding_amount} immediately within 15 days.
2. Clear all dues including interest and legal costs.
3. Honor your commitment and legal obligation.

CONSEQUENCES:
If you fail to comply within 15 days, I shall be constrained to:
1. File civil suit for recovery under Order 37 CPC.
2. Claim interest, costs, and damages.
3. Initiate recovery proceedings against security/guarantor.
4. Take such other legal action as deemed fit.

This notice is served in your interest to avoid legal complications and settle the matter amicably.

Yours faithfully,

{lender_name}
Date: {current_date}
Place: {place}

Through: Advocate
        """,
        "required_fields": [
            "borrower_name", "borrower_address", "lender_name", "loan_amount",
            "loan_date", "interest_rate", "due_date", "loan_purpose", "security_details",
            "loan_documents", "outstanding_amount", "duration", "interest_amount", "place"
        ]
    },
    
    "wrongful_termination_notice": {
        "title": "Legal Notice - Wrongful Termination",
        "template": """
LEGAL NOTICE FOR WRONGFUL TERMINATION

To,
{company_name}
{company_address}

Through: {hr_manager_name}, HR Manager

Subject: Legal Notice for Wrongful Termination and Demand for Dues

Dear Sir/Madam,

I, {employee_name}, former employee of your company, hereby serve this legal notice regarding my wrongful termination.

EMPLOYMENT DETAILS:
1. Employee ID: {employee_id}
2. Designation: {designation}
3. Date of Joining: {joining_date}
4. Date of Termination: {termination_date}
5. Monthly Salary: ₹{monthly_salary}
6. Notice Period: {notice_period}

FACTS:
1. I was employed with your company as {designation} since {joining_date}.
2. My performance was satisfactory and I had no disciplinary issues.
3. On {termination_date}, I was suddenly terminated without proper notice or due process.
4. The termination was in violation of {violation_details}.
5. No opportunity of hearing was provided as required under principles of natural justice.

VIOLATIONS:
1. Termination without {notice_period} notice as per employment contract.
2. No compliance with company's disciplinary policy.
3. Violation of Industrial Disputes Act, 1947.
4. Non-payment of dues and benefits.

OUTSTANDING DUES:
1. Notice Pay: ₹{notice_pay}
2. Pending Salary: ₹{pending_salary}
3. Bonus/Incentives: ₹{bonus_amount}
4. Leave Encashment: ₹{leave_encashment}
5. Gratuity: ₹{gratuity_amount}
6. Other Benefits: ₹{other_benefits}

TOTAL DUES: ₹{total_dues}

LEGAL POSITION:
1. The termination is wrongful and illegal under labor laws.
2. I am entitled to notice pay and all statutory benefits.
3. The company is liable for compensation for illegal termination.

DEMAND:
I hereby demand that you:
1. Reinstate me to my original position immediately.
2. Pay all outstanding dues amounting to ₹{total_dues}.
3. Compensate ₹{compensation_amount} for mental harassment and loss.
4. Provide proper relieving letter and experience certificate.

CONSEQUENCES:
If you fail to comply within 30 days, I shall be constrained to:
1. File complaint before Labor Commissioner.
2. Approach Industrial Tribunal for reinstatement and compensation.
3. File civil suit for recovery of dues and damages.
4. Report the matter to relevant labor authorities.

This notice is served to give you an opportunity to rectify the illegal action and settle the matter amicably.

Yours faithfully,

{employee_name}
Date: {current_date}
Place: {place}

Through: Advocate
        """,
        "required_fields": [
            "company_name", "company_address", "hr_manager_name", "employee_name",
            "employee_id", "designation", "joining_date", "termination_date", "monthly_salary",
            "notice_period", "violation_details", "notice_pay", "pending_salary", "bonus_amount",
            "leave_encashment", "gratuity_amount", "other_benefits", "total_dues",
            "compensation_amount", "place"
        ]
    }
}

@generator_router.post("/generate", response_model=DocumentGenerationResponse)
async def generate_legal_document(
    request: DocumentGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate legal document based on template and user data"""
    
    if request.document_type not in DOCUMENT_TEMPLATES:
        raise HTTPException(
            status_code=400, 
            detail=f"Document type '{request.document_type}' not supported"
        )
    
    template_info = DOCUMENT_TEMPLATES[request.document_type]
    
    # Validate required fields
    missing_fields = []
    for field in template_info["required_fields"]:
        if field not in request.template_data:
            missing_fields.append(field)
    
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )
    
    try:
        # Add current date and calculated fields
        template_data = request.template_data.copy()
        template_data["current_date"] = datetime.now().strftime("%d/%m/%Y")
        
        # Add calculated fields based on document type
        template_data = _add_calculated_fields(request.document_type, template_data)
        
        # Generate document content
        document_content = template_info["template"].format(**template_data)
        
        return DocumentGenerationResponse(
            document_content=document_content,
            document_type=request.document_type,
            generated_at=datetime.now().isoformat()
        )
        
    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Missing template field: {str(e)}"
        )
    except Exception as e:
        logging.error(f"Document generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Document generation failed: {str(e)}"
        )

def _add_calculated_fields(document_type: str, template_data: dict) -> dict:
    """Add calculated fields based on document type and input data"""
    
    if document_type == "rent_objection_notice":
        if "current_rent" in template_data and "proposed_rent" in template_data:
            current_rent = float(template_data["current_rent"])
            proposed_rent = float(template_data["proposed_rent"])
            increase_amount = proposed_rent - current_rent
            increase_percentage = round((increase_amount / current_rent) * 100, 1)
            
            template_data["increase_amount"] = f"{increase_amount:,.0f}"
            template_data["increase_percentage"] = str(increase_percentage)
    
    elif document_type == "loan_demand_notice":
        if all(k in template_data for k in ["loan_amount", "interest_rate", "loan_date"]):
            loan_amount = float(template_data["loan_amount"])
            interest_rate = float(template_data["interest_rate"])
            
            # Calculate duration and interest
            from datetime import datetime
            loan_date = datetime.strptime(template_data["loan_date"], "%d/%m/%Y")
            current_date = datetime.now()
            duration_days = (current_date - loan_date).days
            duration_years = duration_days / 365.25
            
            interest_amount = loan_amount * (interest_rate / 100) * duration_years
            outstanding_amount = loan_amount + interest_amount
            
            template_data["duration"] = f"{duration_days} days"
            template_data["interest_amount"] = f"{interest_amount:,.0f}"
            template_data["outstanding_amount"] = f"{outstanding_amount:,.0f}"
    
    elif document_type == "fraud_recovery_notice":
        if "fraud_amount" in template_data and "compensation_amount" in template_data:
            fraud_amount = float(template_data["fraud_amount"])
            compensation_amount = float(template_data["compensation_amount"])
            total_demand = fraud_amount + compensation_amount
            
            template_data["total_demand"] = f"{total_demand:,.0f}"
    
    elif document_type == "wrongful_termination_notice":
        # Calculate total dues
        due_fields = ["notice_pay", "pending_salary", "bonus_amount", "leave_encashment", "gratuity_amount", "other_benefits"]
        total_dues = 0
        
        for field in due_fields:
            if field in template_data:
                try:
                    amount = float(template_data[field])
                    total_dues += amount
                except (ValueError, TypeError):
                    template_data[field] = "0"
        
        template_data["total_dues"] = f"{total_dues:,.0f}"
    
    return template_data

@generator_router.get("/templates")
async def get_available_templates():
    """Get list of all available document templates"""
    
    templates = []
    for template_id, template_info in DOCUMENT_TEMPLATES.items():
        templates.append({
            "id": template_id,
            "title": template_info["title"],
            "required_fields": template_info["required_fields"]
        })
    
    return {
        "templates": templates,
        "total_count": len(templates)
    }

@generator_router.get("/template/{template_id}")
async def get_template_details(template_id: str):
    """Get detailed information about a specific template"""
    
    if template_id not in DOCUMENT_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template_info = DOCUMENT_TEMPLATES[template_id]
    
    return {
        "id": template_id,
        "title": template_info["title"],
        "required_fields": template_info["required_fields"],
        "sample_template": template_info["template"][:500] + "..." if len(template_info["template"]) > 500 else template_info["template"]
    }

@generator_router.post("/preview")
async def preview_document(request: DocumentGenerationRequest):
    """Preview document without saving (no authentication required)"""
    
    if request.document_type not in DOCUMENT_TEMPLATES:
        raise HTTPException(
            status_code=400, 
            detail=f"Document type '{request.document_type}' not supported"
        )
    
    template_info = DOCUMENT_TEMPLATES[request.document_type]
    
    try:
        # Add current date and calculated fields
        template_data = request.template_data.copy()
        template_data["current_date"] = datetime.now().strftime("%d/%m/%Y")
        
        # Fill missing fields with placeholders
        for field in template_info["required_fields"]:
            if field not in template_data:
                template_data[field] = f"[{field.upper()}]"
        
        # Add calculated fields
        template_data = _add_calculated_fields(request.document_type, template_data)
        
        # Generate preview
        document_content = template_info["template"].format(**template_data)
        
        return {
            "preview": document_content[:1000] + "..." if len(document_content) > 1000 else document_content,
            "document_type": request.document_type,
            "title": template_info["title"],
            "missing_fields": [field for field in template_info["required_fields"] if field not in request.template_data]
        }
        
    except Exception as e:
        logging.error(f"Document preview failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Document preview failed: {str(e)}"
        )
