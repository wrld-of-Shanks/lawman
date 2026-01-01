"""
Legal Analysis Module
Handles Summarization, Translation, and Verification of legal documents using LLM.
"""

import logging
from typing import Dict, List, Optional
from local_llm import generate_with_context

logger = logging.getLogger(__name__)

class LegalAnalyzer:
    def __init__(self):
        pass

    def identify_document_type(self, text: str) -> str:
        """Identify the type of legal document using pattern matching and LLM"""
        # First try pattern matching for common document types
        text_lower = text.lower()
        
        # Pattern-based identification for faster and more accurate results
        if "first information report" in text_lower or ("fir" in text_lower[:200] and "police" in text_lower[:500]):
            return "First Information Report (FIR)"
        elif "rent agreement" in text_lower or "lease agreement" in text_lower:
            return "Rent/Lease Agreement"
        elif "sale deed" in text_lower or "conveyance deed" in text_lower:
            return "Sale Deed"
        elif "affidavit" in text_lower[:200]:
            return "Affidavit"
        elif "power of attorney" in text_lower:
            return "Power of Attorney"
        elif "marriage certificate" in text_lower:
            return "Marriage Certificate"
        elif "birth certificate" in text_lower:
            return "Birth Certificate"
        elif "cheque" in text_lower and "bounce" in text_lower:
            return "Cheque Bounce Notice"
        elif "legal notice" in text_lower[:200]:
            return "Legal Notice"
        elif "employment contract" in text_lower or "appointment letter" in text_lower:
            return "Employment Contract"
        elif "non-disclosure agreement" in text_lower or ("nda" in text_lower[:200] and "confidential" in text_lower):
            return "Non-Disclosure Agreement (NDA)"
        elif "memorandum of understanding" in text_lower or ("mou" in text_lower[:200] and "parties" in text_lower):
            return "Memorandum of Understanding (MOU)"
        elif "will" in text_lower[:100] and ("testament" in text_lower or "bequeath" in text_lower):
            return "Last Will and Testament"
        elif "petition" in text_lower[:200] and "court" in text_lower[:500]:
            return "Court Petition"
        
        # If pattern matching fails, use LLM
        prompt = f"""
        Analyze the following legal document text and identify its type.
        Examples: Contract, FIR, Affidavit, Rent Agreement, Sale Deed, Marriage Certificate, 
        Cheque Bounce Notice, Legal Notice, Employment Contract, NDA, MOU, Court Order, 
        Petition, Will, Trust Deed, Property Agreement, etc.
        
        Return ONLY the document type name. If unsure, return "Legal Document".
        
        Document Text (first 500 chars):
        {text[:500]}...
        """
        try:
            response = generate_with_context("You are a legal document classifier.", prompt, temperature=0.1)
            return response.strip() or "Legal Document"
        except Exception as e:
            logger.error(f"LLM document classification failed: {e}")
            return "Legal Document"

    def summarize_document(self, text: str, doc_type: str) -> Dict:
        """
        Generate a legal summary with extracted entities.
        """
        system_prompt = """
        You are an expert legal AI assistant. Your task is to summarize legal documents accurately and conservatively.
        Do not hallucinate facts. If a detail is missing, do not invent it.
        Focus on extracting key information, parties involved, dates, obligations, and critical clauses.
        """
        
        user_prompt = f"""
        Document Type: {doc_type}
        
        Please provide a highly detailed and professional legal summary of the following document. 
        Your goal is to provide a summary that is so clear and comprehensive that a person could understand the entire legal situation without reading the full text.
        
        Structure your response with these exact headers:
        
        **1. EXECUTIVE SUMMARY**
        Provide a 3-4 paragraph overview of the document's purpose, the parties involved, and the overall legal context.
        
        **2. KEY PARTIES & ROLES**
        - [Party Name]: [Detailed Role and Identification]
        - [Party Name]: [Detailed Role and Identification]
        
        **3. CRITICAL DATES & DEADLINES**
        - [Date]: [Significance of this date]
        - [Date]: [Significance of this date]
        
        **4. FINANCIAL TERMS & OBLIGATIONS**
        - [Amount]: [Description of payment, penalty, or consideration]
        - [Terms]: [Payment schedules or financial conditions]
        
        **5. IMPORTANT CLAUSES & LEGAL PROVISIONS**
        - [Clause Name]: [Detailed explanation of the clause and its impact]
        - [Clause Name]: [Detailed explanation of the clause and its impact]
        
        **6. RIGHTS & OBLIGATIONS**
        - [Party A's Rights]: [List of rights]
        - [Party A's Obligations]: [List of obligations]
        - [Party B's Rights]: [List of rights]
        - [Party B's Obligations]: [List of obligations]
        
        **7. VALIDITY, RENEWAL & TERMINATION**
        - [Validity]: [How long is this document valid?]
        - [Renewal]: [Terms for renewal]
        - [Termination]: [How can this be ended?]
        
        **8. LEGAL COMPLIANCE & FORMALITIES**
        - [Compliance]: [Does it meet legal standards?]
        - [Formalities]: [Are signatures, stamps, or notarization present/required?]
        
        Document Text:
        {text[:12000]} 
        """
        
        try:
            summary = generate_with_context(system_prompt, user_prompt, temperature=0.2)
            
            return {
                "summary": summary,
                "doc_type": doc_type
            }
        except Exception as e:
            logger.error(f"Document summarization failed: {e}")
            return {
                "summary": f"Error generating summary: {str(e)}. Please ensure the LLM service is running.",
                "doc_type": doc_type
            }

    def translate_document(self, text: str, target_lang: str) -> str:
        """
        Translate legal document preserving legal meaning.
        """
        system_prompt = f"""
        You are an expert legal translator. Translate the following legal document into {target_lang}.
        Maintain strict legal accuracy. Preserve Latin terms or specific legal terminology where appropriate, 
        or provide the standard equivalent in the target language.
        Do not summarize; translate the full meaning while maintaining legal precision.
        """
        
        user_prompt = f"""
        Translate this legal text to {target_lang}:
        
        {text[:8000]}
        """
        
        try:
            translation = generate_with_context(system_prompt, user_prompt, temperature=0.1)
            return translation
        except Exception as e:
            logger.error(f"Document translation failed: {e}")
            return f"Error translating document: {str(e)}. Please ensure the LLM service is running."

    def verify_legality(self, text: str, doc_type: str) -> Dict:
        """
        Verify the legality and completeness of the document.
        """
        system_prompt = """
        You are a senior legal compliance officer. Review the document for legal validity, 
        completeness, and admissibility under Indian law.
        Be thorough but conservative in your assessment.
        """
        
        user_prompt = f"""
        Document Type: {doc_type}
        
        Analyze this document for the following:
        
        **CHECKLIST ITEMS TO VERIFY:**
        1. **Parties Identified**: Are all parties clearly named and identified with complete details?
        2. **Date & Jurisdiction**: Is the date and place of execution clearly mentioned?
        3. **Signatures**: Does it indicate where signatures should be? (Note: OCR might miss handwritten signatures, so check for signature blocks)
        4. **Witnesses**: Are witness clauses present if required for this document type?
        5. **Stamp Paper**: Is there mention of stamp paper value if required?
        6. **Notarization**: Is notarization mentioned if required for this document type?
        7. **Legal Formalities**: Are all legal formalities appropriate for this document type present?
        8. **Clarity**: Is the language clear and unambiguous?
        9. **Completeness**: Are all standard clauses for this document type present?
        10. **Compliance**: Does it comply with relevant Indian laws?
        
        Output your analysis in this specific format:
        
        **CHECKLIST:**
        [✓/✗] Parties Identified: [Brief note]
        [✓/✗] Date & Jurisdiction: [Brief note]
        [✓/✗] Signatures: [Brief note]
        [✓/✗] Witnesses: [Brief note]
        [✓/✗] Stamp Paper: [Brief note]
        [✓/✗] Notarization: [Brief note]
        [✓/✗] Legal Formalities: [Brief note]
        [✓/✗] Clarity: [Brief note]
        [✓/✗] Completeness: [Brief note]
        [✓/✗] Compliance: [Brief note]
        
        **DETAILED ANALYSIS:**
        [Provide a detailed explanation of your findings, highlighting any issues or concerns]
        
        **RECOMMENDATIONS:**
        [List specific recommendations for improvement if any issues were found]
        
        **VERDICT:**
        [Choose exactly one: "Legally correct and ready for submission", "Needs modification before submission", "Likely invalid / inadmissible"]
        
        **CONFIDENCE:**
        [Provide confidence level: 0-100%]
        
        Document Text:
        {text[:10000]}
        """
        
        try:
            analysis = generate_with_context(system_prompt, user_prompt, temperature=0.1)
            
            # Try to extract confidence percentage
            import re
            conf_match = re.search(r"CONFIDENCE:\s*(\d+)", analysis, re.IGNORECASE)
            conf_value = 85
            if conf_match:
                conf_value = int(conf_match.group(1))
                confidence = f"{conf_value}%"
            else:
                confidence = "85%"
            
            # Determine verdict (User request: 95+ is valid)
            if conf_value >= 95:
                verdict = "Legally correct and ready for submission. You can proceed to submit it to the needed office."
            elif "Legally correct and ready for submission" in analysis:
                verdict = "Legally correct and ready for submission. You can proceed to submit it to the needed office."
            elif "Likely invalid" in analysis or "inadmissible" in analysis:
                verdict = "Likely invalid / inadmissible. This document needs to be examined and remade."
            elif "Needs modification" in analysis:
                verdict = "Needs modification before submission. Please examine the recommendations and update the document."
            else:
                verdict = "Needs modification before submission"
                
            return {
                "full_analysis": analysis,
                "verdict": verdict,
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Document verification failed: {e}")
            return {
                "full_analysis": f"Error verifying document: {str(e)}. Please ensure the LLM service is running.",
                "verdict": "Unable to verify - service error"
            }

legal_analyzer = LegalAnalyzer()
