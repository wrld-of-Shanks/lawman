"""
Comprehensive Indian Legal Solutions Database
Contains detailed legal remedies, procedures, and case law references
"""

from typing import Dict, List, Any

class LegalSolution:
    def __init__(self, topic: str, description: str, legal_remedy: str, 
                 procedure: List[str], documents_required: List[str], 
                 time_limit: str, court_fees: str, case_references: List[str],
                 practical_tips: List[str]):
        self.topic = topic
        self.description = description
        self.legal_remedy = legal_remedy
        self.procedure = procedure
        self.documents_required = documents_required
        self.time_limit = time_limit
        self.court_fees = court_fees
        self.case_references = case_references
        self.practical_tips = practical_tips

# Comprehensive Legal Solutions Database
LEGAL_SOLUTIONS = {
    
    # CRIMINAL LAW SOLUTIONS
    "bail_application": LegalSolution(
        topic="Bail Application",
        description="Securing temporary release of accused person during trial",
        legal_remedy="File bail application under Section 437/438 CrPC",
        procedure=[
            "1. File bail application in appropriate court (Magistrate/Sessions/High Court)",
            "2. Submit personal bond and surety bond",
            "3. Attend court hearings regularly",
            "4. Comply with bail conditions",
            "5. Surrender passport if required"
        ],
        documents_required=[
            "Bail application with grounds",
            "Personal bond and surety bond",
            "Identity proof of accused and surety",
            "Address proof of surety",
            "Property documents of surety",
            "Character certificate",
            "Medical certificate (if applicable)"
        ],
        time_limit="No specific time limit, but urgency preferred",
        court_fees="₹50-500 depending on court",
        case_references=[
            "Gurbaksh Singh Sibbia v. State of Punjab (1980) - Liberal bail policy",
            "Sanjay Chandra v. CBI (2012) - Economic offenses bail guidelines",
            "Arnesh Kumar v. State of Bihar (2014) - Arrest guidelines"
        ],
        practical_tips=[
            "Engage experienced criminal lawyer",
            "Arrange reliable surety with property",
            "Prepare strong grounds for bail",
            "Show roots in community",
            "Demonstrate no flight risk"
        ]
    ),
    
    "domestic_violence_remedy": LegalSolution(
        topic="Domestic Violence Protection",
        description="Legal protection for women against domestic abuse",
        legal_remedy="File complaint under Domestic Violence Act 2005",
        procedure=[
            "1. File complaint with Magistrate or Protection Officer",
            "2. Obtain protection order from court",
            "3. Get residence order if needed",
            "4. Apply for monetary relief",
            "5. Seek custody order for children"
        ],
        documents_required=[
            "Written complaint with details of violence",
            "Medical reports of injuries",
            "Photographs of injuries",
            "Witness statements",
            "Marriage certificate",
            "Income proof for maintenance",
            "Property documents"
        ],
        time_limit="No limitation period for filing complaint",
        court_fees="No court fees required",
        case_references=[
            "Indra Sarma v. V.K.V. Sarma (2013) - Definition of domestic relationship",
            "Hiral P. Harsora v. Kusum Narottamdas (2016) - Irretrievable breakdown",
            "Rajesh Sharma v. State of UP (2017) - Misuse prevention guidelines"
        ],
        practical_tips=[
            "Document all incidents of violence",
            "Seek immediate medical attention",
            "Inform trusted family/friends",
            "Keep emergency contact numbers",
            "Know location of nearest police station"
        ]
    ),
    
    # FAMILY LAW SOLUTIONS
    "divorce_mutual_consent": LegalSolution(
        topic="Mutual Consent Divorce",
        description="Divorce by mutual agreement of both spouses",
        legal_remedy="File joint petition under Section 13B Hindu Marriage Act",
        procedure=[
            "1. File joint petition in family court",
            "2. Wait for 6-month cooling period",
            "3. File second motion after 6 months",
            "4. Court grants divorce decree",
            "5. Obtain certified copy of decree"
        ],
        documents_required=[
            "Joint petition signed by both parties",
            "Marriage certificate",
            "Settlement agreement",
            "Income certificates of both parties",
            "Property documents",
            "Children's birth certificates",
            "Passport size photographs"
        ],
        time_limit="Minimum 6 months from filing to decree",
        court_fees="₹1000-5000 depending on state",
        case_references=[
            "Amardeep Singh v. Harveen Kaur (2017) - Waiver of 6-month period",
            "Sureshta Devi v. Om Prakash (2008) - Mutual consent essentials",
            "Naveen Kohli v. Neelu Kohli (2006) - Irretrievable breakdown"
        ],
        practical_tips=[
            "Prepare comprehensive settlement agreement",
            "Decide child custody and maintenance",
            "Divide assets and liabilities clearly",
            "Consider tax implications",
            "Maintain cordial relationship during process"
        ]
    ),
    
    "child_custody_dispute": LegalSolution(
        topic="Child Custody Dispute",
        description="Legal custody determination for minor children",
        legal_remedy="File petition under Guardians and Wards Act 1890",
        procedure=[
            "1. File custody petition in family court",
            "2. Submit welfare report by court officer",
            "3. Attend mediation sessions",
            "4. Present evidence of child's best interest",
            "5. Obtain custody order from court"
        ],
        documents_required=[
            "Custody petition with grounds",
            "Child's birth certificate",
            "School records and medical records",
            "Income proof and accommodation details",
            "Character certificates",
            "Photographs of living conditions",
            "Witness statements"
        ],
        time_limit="No specific limitation, but urgency for child welfare",
        court_fees="₹500-2000 depending on court",
        case_references=[
            "Roxann Sharma v. Arun Sharma (2015) - Child's welfare paramount",
            "Nil Ratan Kundu v. Abhijit Kundu (2008) - Tender years doctrine",
            "Gaurav Nagpal v. Sumedha Nagpal (2009) - Joint custody guidelines"
        ],
        practical_tips=[
            "Focus on child's best interests",
            "Maintain stable living environment",
            "Document quality time with child",
            "Avoid negative comments about other parent",
            "Consider child's preference if mature"
        ]
    ),
    
    # PROPERTY LAW SOLUTIONS
    "property_dispute_resolution": LegalSolution(
        topic="Property Title Dispute",
        description="Resolving ownership disputes over immovable property",
        legal_remedy="File suit for declaration of title and possession",
        procedure=[
            "1. File title suit in civil court",
            "2. Obtain temporary injunction if needed",
            "3. Complete pleadings and discovery",
            "4. Examine witnesses and documents",
            "5. Obtain decree and execute if needed"
        ],
        documents_required=[
            "Sale deed or title documents",
            "Property tax receipts",
            "Survey settlement records",
            "Mutation records",
            "Possession certificates",
            "Boundary demarcation documents",
            "Witness statements"
        ],
        time_limit="12 years from dispossession (Article 65 Limitation Act)",
        court_fees="Based on property value as per Court Fees Act",
        case_references=[
            "Sarla Verma v. Delhi Development Authority (2009) - Adverse possession",
            "Karnataka Board v. Ranganatha Reddy (1977) - Title by possession",
            "Hemaji Waghaji v. Bhikhabhai Khengarbhai (2009) - Burden of proof"
        ],
        practical_tips=[
            "Maintain continuous possession records",
            "Pay property taxes regularly",
            "Keep all original documents safe",
            "Conduct proper due diligence before purchase",
            "Register property transactions promptly"
        ]
    ),
    
    "landlord_tenant_dispute": LegalSolution(
        topic="Landlord-Tenant Dispute",
        description="Resolving rental disputes and eviction matters",
        legal_remedy="File suit under Rent Control Act or specific state laws",
        procedure=[
            "1. Send legal notice for rent/eviction",
            "2. File suit in rent controller court",
            "3. Deposit rent in court if tenant",
            "4. Present evidence of grounds for eviction",
            "5. Obtain eviction order if successful"
        ],
        documents_required=[
            "Rent agreement or lease deed",
            "Rent receipts and payment records",
            "Legal notice served",
            "Property ownership documents",
            "Electricity and water bills",
            "Witness statements",
            "Photographs of property condition"
        ],
        time_limit="Varies by state Rent Control Acts",
        court_fees="₹100-1000 depending on monthly rent",
        case_references=[
            "Prativa Devi v. T.V. Krishnan (1996) - Bonafide need for eviction",
            "Hasmat Rai v. Raghunath Prasad (1981) - Default in rent payment",
            "Gian Devi Anand v. Jeevan Kumar (1985) - Subletting without consent"
        ],
        practical_tips=[
            "Maintain proper rent agreement",
            "Keep records of all rent payments",
            "Give proper notice before eviction",
            "Document property condition regularly",
            "Follow state-specific rent control laws"
        ]
    ),
    
    # CONSUMER LAW SOLUTIONS
    "consumer_complaint_remedy": LegalSolution(
        topic="Consumer Complaint",
        description="Redressal for defective goods or deficient services",
        legal_remedy="File complaint under Consumer Protection Act 2019",
        procedure=[
            "1. File complaint in appropriate consumer forum",
            "2. Serve notice to opposite party",
            "3. Attend hearings and present evidence",
            "4. Obtain order for compensation/replacement",
            "5. Execute order if not complied voluntarily"
        ],
        documents_required=[
            "Purchase receipt or invoice",
            "Warranty/guarantee card",
            "Correspondence with seller/manufacturer",
            "Expert opinion/test reports",
            "Photographs of defective product",
            "Medical reports (if health affected)",
            "Witness statements"
        ],
        time_limit="2 years from cause of action",
        court_fees="No fees up to ₹5 lakhs, minimal fees above",
        case_references=[
            "Spring Meadows Hospital v. Harjol Ahluwalia (1998) - Medical negligence",
            "Indian Medical Association v. V.P. Shantha (1995) - Service definition",
            "Lucknow Development Authority v. M.K. Gupta (1994) - Deficiency in service"
        ],
        practical_tips=[
            "Keep all purchase documents safe",
            "Document defects with photographs",
            "First approach seller for resolution",
            "File complaint within limitation period",
            "Engage lawyer for complex cases"
        ]
    ),
    
    # EMPLOYMENT LAW SOLUTIONS
    "wrongful_termination_remedy": LegalSolution(
        topic="Wrongful Termination",
        description="Legal remedy for illegal dismissal from employment",
        legal_remedy="File complaint under Industrial Disputes Act 1947",
        procedure=[
            "1. Raise dispute through union or directly",
            "2. Approach conciliation officer",
            "3. File reference to labour court/tribunal",
            "4. Present case with evidence",
            "5. Obtain reinstatement or compensation order"
        ],
        documents_required=[
            "Appointment letter and service records",
            "Termination notice and reasons",
            "Salary slips and provident fund records",
            "Performance appraisals",
            "Correspondence with management",
            "Witness statements from colleagues",
            "Union membership records"
        ],
        time_limit="1 year from termination for raising dispute",
        court_fees="Minimal fees as per state rules",
        case_references=[
            "Workmen of Motipur Sugar Factory v. State of UP (1965) - Natural justice",
            "Managing Director ECIL v. B. Karunakar (1993) - Domestic enquiry",
            "State Bank of India v. N. Sundara Money (1976) - Punishment proportionate"
        ],
        practical_tips=[
            "Maintain employment records properly",
            "Follow grievance procedure first",
            "Document all communications",
            "Seek union support if available",
            "Consider settlement negotiations"
        ]
    ),
    
    # CYBER LAW SOLUTIONS
    "cyber_crime_remedy": LegalSolution(
        topic="Cyber Crime Complaint",
        description="Legal remedy for online fraud, hacking, and cyber crimes",
        legal_remedy="File FIR under IT Act 2000 and IPC provisions",
        procedure=[
            "1. File complaint with cyber crime cell",
            "2. Preserve digital evidence immediately",
            "3. Cooperate with police investigation",
            "4. File civil suit for damages if needed",
            "5. Follow up on investigation progress"
        ],
        documents_required=[
            "Screenshots of fraudulent messages/websites",
            "Bank statements showing unauthorized transactions",
            "Email headers and digital communications",
            "System logs and IP address records",
            "Identity documents",
            "Loss/damage assessment report",
            "Expert technical opinion"
        ],
        time_limit="No specific limitation for FIR, but immediate reporting preferred",
        court_fees="No fees for FIR, court fees for civil suit",
        case_references=[
            "Shreya Singhal v. Union of India (2015) - Section 66A struck down",
            "Avnish Bajaj v. State (2005) - Intermediary liability",
            "SMC Pneumatics v. Jogesh Kwatra (2014) - Email evidence"
        ],
        practical_tips=[
            "Report cyber crime immediately",
            "Preserve all digital evidence",
            "Don't share personal information online",
            "Use strong passwords and 2FA",
            "Keep software updated regularly"
        ]
    ),
    
    # CONSTITUTIONAL LAW SOLUTIONS
    "fundamental_rights_violation": LegalSolution(
        topic="Fundamental Rights Violation",
        description="Constitutional remedy for violation of fundamental rights",
        legal_remedy="File writ petition under Article 32 (SC) or 226 (HC)",
        procedure=[
            "1. File writ petition in High Court or Supreme Court",
            "2. Seek interim relief if urgent",
            "3. Serve notice to respondent authorities",
            "4. Present constitutional arguments",
            "5. Obtain writ order for enforcement"
        ],
        documents_required=[
            "Writ petition with constitutional grounds",
            "Affidavit with facts and evidence",
            "Relevant government orders/notifications",
            "Newspaper reports or media coverage",
            "Expert opinions on constitutional law",
            "Precedent case citations",
            "Vakalatnama of advocate"
        ],
        time_limit="No limitation period for constitutional remedies",
        court_fees="₹500-2000 depending on court and relief sought",
        case_references=[
            "Maneka Gandhi v. Union of India (1978) - Right to life and liberty",
            "Vishaka v. State of Rajasthan (1997) - Workplace sexual harassment",
            "K.S. Puttaswamy v. Union of India (2017) - Right to privacy"
        ],
        practical_tips=[
            "Engage constitutional law expert",
            "Document rights violation clearly",
            "Cite relevant constitutional provisions",
            "Show locus standi for petition",
            "Consider public interest angle"
        ]
    ),
    
    # BANKING AND FINANCE SOLUTIONS
    "loan_recovery_defense": LegalSolution(
        topic="Loan Recovery Defense",
        description="Defense against bank recovery proceedings under SARFAESI",
        legal_remedy="File objection under SARFAESI Act 2002",
        procedure=[
            "1. File objection with DRT within 30 days",
            "2. Challenge classification as NPA if disputed",
            "3. Seek stay on recovery proceedings",
            "4. Present defense on merits",
            "5. Negotiate one-time settlement if viable"
        ],
        documents_required=[
            "Loan agreement and all amendments",
            "Payment records and acknowledgments",
            "Correspondence with bank",
            "Valuation reports of secured assets",
            "Financial statements and tax returns",
            "Notice under Section 13(2) received",
            "Legal opinion on bank's action"
        ],
        time_limit="30 days from receipt of Section 13(4) notice",
        court_fees="₹2500 for DRT application",
        case_references=[
            "Mardia Chemicals v. Union of India (2004) - SARFAESI validity",
            "United Bank of India v. Satyawati Tondon (2010) - Notice requirements",
            "Transcore v. Union of India (2008) - Security interest enforcement"
        ],
        practical_tips=[
            "Respond to bank notices promptly",
            "Maintain loan payment records",
            "Challenge incorrect NPA classification",
            "Explore settlement options early",
            "Engage banking law specialist"
        ]
    ),
    
    # MOTOR VEHICLE ACCIDENT SOLUTIONS
    "motor_accident_claim": LegalSolution(
        topic="Motor Vehicle Accident Compensation",
        description="Claiming compensation for motor vehicle accident injuries",
        legal_remedy="File claim petition under Motor Vehicles Act 1988",
        procedure=[
            "1. File claim petition in Motor Accident Claims Tribunal",
            "2. Serve notice to insurance company and vehicle owner",
            "3. Submit medical evidence and expert opinions",
            "4. Attend tribunal hearings regularly",
            "5. Obtain award and execute if not paid"
        ],
        documents_required=[
            "FIR copy and police investigation report",
            "Medical reports and treatment records",
            "Income proof of victim/deceased",
            "Death certificate (in fatal accidents)",
            "Insurance policy details",
            "Driving license and vehicle registration",
            "Expert opinion on disability percentage"
        ],
        time_limit="2 years from accident date (extendable)",
        court_fees="₹100-500 depending on claim amount",
        case_references=[
            "Sarla Verma v. Delhi Transport Corporation (2009) - Compensation guidelines",
            "National Insurance Co. v. Pranay Sethi (2017) - Updated multiplier method",
            "Rajesh Tyagi v. Jaibir Singh (2004) - No-fault liability"
        ],
        practical_tips=[
            "Report accident to police immediately",
            "Preserve all medical records",
            "Don't accept quick settlements",
            "Calculate compensation scientifically",
            "Engage experienced motor accident lawyer"
        ]
    )
}

def get_legal_solution(topic_key: str) -> Dict[str, Any]:
    """Get comprehensive legal solution for a topic"""
    if topic_key in LEGAL_SOLUTIONS:
        solution = LEGAL_SOLUTIONS[topic_key]
        return {
            "topic": solution.topic,
            "description": solution.description,
            "legal_remedy": solution.legal_remedy,
            "procedure": solution.procedure,
            "documents_required": solution.documents_required,
            "time_limit": solution.time_limit,
            "court_fees": solution.court_fees,
            "case_references": solution.case_references,
            "practical_tips": solution.practical_tips
        }
    return None

def format_legal_solution(solution_data: Dict[str, Any]) -> str:
    """Format legal solution for user display"""
    if not solution_data:
        return "No specific legal solution available for this query."
    
    formatted = f"**{solution_data['topic']}**\n\n"
    formatted += f"**Description:** {solution_data['description']}\n\n"
    formatted += f"**Legal Remedy:** {solution_data['legal_remedy']}\n\n"
    
    formatted += "**Procedure:**\n"
    for step in solution_data['procedure']:
        formatted += f"{step}\n"
    formatted += "\n"
    
    formatted += "**Documents Required:**\n"
    for doc in solution_data['documents_required']:
        formatted += f"• {doc}\n"
    formatted += "\n"
    
    formatted += f"**Time Limit:** {solution_data['time_limit']}\n"
    formatted += f"**Court Fees:** {solution_data['court_fees']}\n\n"
    
    formatted += "**Important Case References:**\n"
    for case in solution_data['case_references']:
        formatted += f"• {case}\n"
    formatted += "\n"
    
    formatted += "**Practical Tips:**\n"
    for tip in solution_data['practical_tips']:
        formatted += f"• {tip}\n"
    
    return formatted

# Topic to solution mapping
TOPIC_TO_SOLUTION = {
    "bail": "bail_application",
    "domestic violence": "domestic_violence_remedy",
    "divorce": "divorce_mutual_consent",
    "custody": "child_custody_dispute",
    "property": "property_dispute_resolution",
    "landlord": "landlord_tenant_dispute",
    "consumer": "consumer_complaint_remedy",
    "termination": "wrongful_termination_remedy",
    "cyber": "cyber_crime_remedy",
    "rights": "fundamental_rights_violation",
    "loan": "loan_recovery_defense",
    "accident": "motor_accident_claim"
}
