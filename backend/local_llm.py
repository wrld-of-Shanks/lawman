import os
import logging
from typing import List, Dict, Optional
import requests

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "lawman-legal")

def _build_ollama_url(path: str) -> str:
    base = OLLAMA_BASE_URL.rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    return base + path

def chat_with_ollama(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> str:
    """Call local Ollama chat API and return assistant content as plain text.
    Messages must be a list of {"role": "system"|"user"|"assistant", "content": str}.
    """
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
        # Ollama chat responses contain a top-level "message" with "content"
        message = data.get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content
        # Some versions stream chunks into a list under "messages"; handle defensively
        if "messages" in data and isinstance(data["messages"], list):
            texts = [m.get("content", "") for m in data["messages"]]
            return "".join(texts).strip()
        return ""
    except Exception as e:
        logging.error(f"Ollama chat request failed: {e}")
        return ""

def generate_with_context(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """Convenience wrapper for single-turn question answering with a system prompt."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    return chat_with_ollama(messages, temperature=temperature)
