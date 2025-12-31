import os
import logging
from typing import List, Dict, Optional
import requests
import google.generativeai as genai

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "lawman-legal")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini if key is available
if GOOGLE_API_KEY:
    logger.info(f"Gemini API Key detected (starts with: {GOOGLE_API_KEY[:4]}...)")
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    logger.warning("GOOGLE_API_KEY not found. Gemini will be disabled.")

def _build_ollama_url(path: str) -> str:
    base = OLLAMA_BASE_URL.rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    return base + path

def chat_with_gemini(messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
    """Call Google Gemini API"""
    try:
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is missing")
            
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Convert messages to Gemini format
        system_instruction = ""
        last_user_msg = ""
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                last_user_msg = msg["content"]

        # Re-initialize model with system instruction if present
        if system_instruction:
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
        
        if not last_user_msg:
            return "Error: No user message provided."
            
        response = model.generate_content(
            last_user_msg,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
            )
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini API request failed: {e}")
        raise e

def chat_with_ollama(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> str:
    """Call local Ollama chat API"""
    payload = {
        "model": model or OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    try:
        resp = requests.post(
            _build_ollama_url("/api/chat"), json=payload, timeout=120
        )
        resp.raise_for_status()
        data = resp.json()
        message = data.get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content
        return ""
    except Exception as e:
        logger.error(f"Ollama chat request failed: {e}")
        raise e

def generate_with_context(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """Convenience wrapper for single-turn question answering."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    
    # 1. Try Gemini first if API key is present
    if GOOGLE_API_KEY:
        try:
            logger.info("Attempting to use Gemini...")
            return chat_with_gemini(messages, temperature=temperature)
        except Exception as e:
            logger.warning(f"Gemini failed: {e}. Falling back to Ollama...")
    
    # 2. Fallback to Ollama
    try:
        logger.info(f"Attempting to use Ollama at {OLLAMA_BASE_URL}...")
        return chat_with_ollama(messages, temperature=temperature)
    except Exception as e:
        logger.error(f"All LLM providers failed. Last error: {e}")
        if not GOOGLE_API_KEY:
            return "Error: GOOGLE_API_KEY is not set in Render environment variables. Please add it to your Render dashboard to enable AI features."
        return f"Error: LLM service unavailable. {str(e)}"
