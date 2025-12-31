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
    genai.configure(api_key=GOOGLE_API_KEY)

def _build_ollama_url(path: str) -> str:
    base = OLLAMA_BASE_URL.rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    return base + path

def chat_with_gemini(messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
    """Call Google Gemini API"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Convert messages to Gemini format
        # System prompt is handled separately in Gemini 1.5
        system_instruction = ""
        history = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                history.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                history.append({"role": "model", "parts": [msg["content"]]})

        # Re-initialize model with system instruction
        if system_instruction:
            model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
        
        # For single turn, we just use the last user message
        last_msg = history[-1]["parts"][0] if history else ""
        
        response = model.generate_content(
            last_msg,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
            )
        )
        return response.text
    except Exception as e:
        logging.error(f"Gemini API request failed: {e}")
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
        if "messages" in data and isinstance(data["messages"], list):
            texts = [m.get("content", "") for m in data["messages"]]
            return "".join(texts).strip()
        return ""
    except Exception as e:
        logging.error(f"Ollama chat request failed: {e}")
        raise e

def generate_with_context(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """Convenience wrapper for single-turn question answering."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    
    # 1. Try Gemini if API key is present
    if GOOGLE_API_KEY:
        try:
            return chat_with_gemini(messages, temperature=temperature)
        except Exception as e:
            logging.warning(f"Gemini failed, falling back to Ollama if available: {e}")
    
    # 2. Fallback to Ollama
    try:
        return chat_with_ollama(messages, temperature=temperature)
    except Exception as e:
        logging.error(f"All LLM providers failed: {e}")
        return f"Error: LLM service unavailable. {str(e)}"
