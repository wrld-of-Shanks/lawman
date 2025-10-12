from embed_store import search_chunks
from typing import Dict
import os
import torch
import re
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
except ImportError:
    AutoTokenizer = None
    AutoModelForCausalLM = None
    pipeline = None

# Simple text generation function that doesn't require external models
def simple_text_generator(prompt, max_length=150):
    """
    A simple text generation function that uses pattern matching and templates
    to generate responses without requiring a complex language model.
    """
    # Extract the question from the prompt
    question_match = re.search(r"Question: (.*?)\nAnswer:", prompt)
    question = question_match.group(1) if question_match else "your question"
    
    # Extract context snippets
    context_match = re.search(r"Context:\n(.*?)\n\nQuestion:", prompt, re.DOTALL)
    context = context_match.group(1) if context_match else ""
    
    # Look for key legal terms in the question and context
    key_terms = ["theft", "property", "rights", "law", "legal", "court", "crime", 
                "punishment", "section", "act", "constitution", "contract", "marriage", 
                "divorce", "compensation", "damages", "liability"]
    
    found_terms = []
    for term in key_terms:
        if term.lower() in question.lower() or term.lower() in context.lower():
            found_terms.append(term)
    
    # Generate a response based on found terms and context
    if found_terms:
        response = f"Based on Indian law regarding {', '.join(found_terms)}, "
        
        # Extract relevant sentences from context
        relevant_sentences = []
        if context:
            sentences = re.split(r'[.!?]+', context)
            for sentence in sentences:
                for term in found_terms:
                    if term.lower() in sentence.lower():
                        relevant_sentences.append(sentence.strip())
                        break
        
        if relevant_sentences:
            response += "the relevant legal provisions state that: " + " ".join(relevant_sentences[:3])
            if len(relevant_sentences) > 3:
                response += " Additionally, " + " ".join(relevant_sentences[3:5])
        else:
            response += "you should consult with a legal professional for specific advice on this matter."
            
        response += " This information is provided for educational purposes only and should not be considered legal advice."
    else:
        response = "I don't have specific information about this legal query. Please consult with a qualified legal professional for advice on your specific situation."
    
    return response

# Function to simulate a text generation pipeline
def generate_text(prompt, max_length=150, **kwargs):
    response = simple_text_generator(prompt, max_length)
    return [{"generated_text": prompt + response}]

# Create a simple generator function that doesn't require external models
def _load_local_llm_pipeline():
    if AutoTokenizer is None or AutoModelForCausalLM is None or pipeline is None:
        return None
    # Prefer fine-tuned model if present
    ft_path = os.path.join("backend", "models", "legal_llm")
    model_id = ft_path if os.path.isdir(ft_path) else "distilgpt2"
    try:
        tok = AutoTokenizer.from_pretrained(model_id)
        mdl = AutoModelForCausalLM.from_pretrained(model_id)
        gen = pipeline("text-generation", model=mdl, tokenizer=tok, device=0 if torch.cuda.is_available() else -1)
        return gen
    except Exception:
        return None

_LOCAL_GEN = _load_local_llm_pipeline()

def generator(prompt, max_length=150, num_return_sequences=1, temperature=0.7, top_p=0.9, do_sample=True):
    if _LOCAL_GEN is not None:
        # Use HF pipeline; control with max_new_tokens to avoid exploding lengths
        max_new = max(16, min(256, max_length))
        outs = _LOCAL_GEN(
            prompt,
            max_new_tokens=max_new,
            num_return_sequences=num_return_sequences,
            temperature=temperature,
            top_p=top_p,
            do_sample=do_sample,
            return_full_text=True,
        )
        return outs
    # Fallback to simple template-based generator
    return generate_text(prompt, max_length=max_length)

SYSTEM_PROMPT = "You are a helpful legal assistant. Use the provided law text to answer clearly and cite relevant sections."

def generate_answer(query: str, context_chunks: list) -> str:
    # First, try to extract direct Q&A matches
    qa_matches = []
    for chunk in context_chunks:
        # Look for Q&A patterns in the text
        if 'Q:' in chunk and 'A:' in chunk:
            # Split by Q: to find questions
            parts = chunk.split('Q:')
            for part in parts[1:]:  # Skip first empty part
                if 'A:' in part:
                    question_part, answer_part = part.split('A:', 1)
                    question = question_part.strip()
                    answer = answer_part.strip()

                    # Check if this Q&A is relevant to the query
                    if any(term in question.lower() for term in query.lower().split()):
                        qa_matches.append(f"A: {answer}")

    if qa_matches:
        return " ".join(qa_matches[:2])  # Return top 2 matches

    # If no direct Q&A found, try to extract relevant sentences
    relevant_sentences = []
    for chunk in context_chunks:
        sentences = chunk.replace('. ', '.\n').split('\n')
        for sentence in sentences:
            if any(term in sentence.lower() for term in query.lower().split()):
                relevant_sentences.append(sentence.strip())

    if relevant_sentences:
        return " ".join(relevant_sentences[:3])  # Return top 3 relevant sentences

    # Fallback to template approach
    context = "\n---\n".join(context_chunks)
    prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"

    response = generator(
        prompt,
        max_length=len(prompt.split()) + 150,
        num_return_sequences=1,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )

    generated_text = response[0]['generated_text']
    answer = generated_text[len(prompt):].strip()

    return answer

def answer_query(query: str) -> Dict:
    results = search_chunks(query, top_k=3)
    chunks = results.get('documents', [[]])[0]
    metadatas = results.get('metadatas', [[]])[0]
    if not chunks:
        return {
            "answer": "No relevant context found in the knowledge base for your query. Please try rephrasing or upload relevant documents.",
            "sources": []
        }
    answer = generate_answer(query, chunks)
    return {
        "answer": answer,
        "sources": [
            {"text": chunk, "metadata": meta}
            for chunk, meta in zip(chunks, metadatas)
        ]
    }