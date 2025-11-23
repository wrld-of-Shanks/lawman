"""
Enhanced Chat Engine with Production-Grade Vector RAG
Integrates the trained vector database for semantic search
"""

import logging
from typing import Dict
from vector_rag_trainer import VectorRAGTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Vector RAG system (singleton)
_rag_system = None

def get_rag_system():
    """Get or create the RAG system singleton"""
    global _rag_system
    if _rag_system is None:
        logger.info("Initializing Vector RAG system...")
        _rag_system = VectorRAGTrainer(
            model_name="all-mpnet-base-v2",
            similarity_threshold=0.70  # Lowered to 70% for better coverage
        )
    return _rag_system

def answer_query_with_rag(query: str, user_id: str = None, mode: str = "default") -> Dict:
    """
    Enhanced answer function using Hybrid Search (Keyword Expansion + Vector RAG)
    
    Args:
        query: User's question
        user_id: Optional user ID
        mode: Query mode
        
    Returns:
        Dict with answer and metadata
    """
    try:
        # Pre-process query to expand abbreviations
        # This fixes issues where "DL" doesn't match "Driving License" well in vector space
        from comprehensive_legal_db import get_comprehensive_legal_info
        
        # Simple keyword expansion
        expanded_query = query
        lower_query = query.lower()
        
        # Map common abbreviations
        abbreviations = {
            "dl": "driving license",
            "fir": "first information report",
            "pil": "public interest litigation",
            "rti": "right to information",
            "pf": "provident fund",
            "gst": "goods and services tax",
            "posh": "prevention of sexual harassment",
            "ipc": "indian penal code",
            "crpc": "criminal procedure code"
        }
        
        for abbr, full_form in abbreviations.items():
            # Check for standalone abbreviation (surrounded by spaces or start/end)
            import re
            pattern = r'\b' + re.escape(abbr) + r'\b'
            if re.search(pattern, query, re.IGNORECASE):
                expanded_query = re.sub(pattern, full_form, expanded_query, flags=re.IGNORECASE)
                logger.info(f"Expanded query: '{query}' -> '{expanded_query}'")
        
        # Get RAG system
        rag = get_rag_system()
        
        # Get answer using vector similarity search with expanded query
        result = rag.get_answer(expanded_query, top_k=3)
        
        # Format response
        response = {
            "answer": result['answer'],
            "sources": result['sources'],
            "confidence": result['similarity'],
            "matched_question": result.get('matched_question')
        }
        
        logger.info(f"Query: '{query}' (Expanded: '{expanded_query}') | Confidence: {result['similarity']:.2%}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in RAG query: {str(e)}")
        
        # Fallback to comprehensive legal database
        try:
            from comprehensive_legal_db import get_comprehensive_legal_info
            legal_info = get_comprehensive_legal_info(query)
            if legal_info:
                return {
                    "answer": legal_info,
                    "sources": ["Comprehensive Legal Database"],
                    "confidence": 0.8
                }
        except:
            pass
        
        # Final fallback
        return {
            "answer": "I encountered an error processing your question. Please try rephrasing or ask about specific Indian legal topics like bail, divorce, FIR, driving license, property, employment, or consumer rights.",
            "sources": [],
            "confidence": 0.0
        }
