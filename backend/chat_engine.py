from embed_store import search_chunks
from typing import Dict
import os
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENROUTER_BASE_URL)

SYSTEM_PROMPT = "You are a helpful legal assistant. Use the provided law text to answer clearly and cite relevant sections."

# Use OpenRouter to generate an answer from context
def generate_answer(query: str, context_chunks: list) -> str:
    context = "\n---\n".join(context_chunks)
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512,
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

def answer_query(query: str) -> Dict:
    results = search_chunks(query, top_k=3)
    chunks = results.get('documents', [[]])[0]
    metadatas = results.get('metadatas', [[]])[0]
    answer = generate_answer(query, chunks)
    return {
        "answer": answer,
        "sources": [
            {"text": chunk, "metadata": meta}
            for chunk, meta in zip(chunks, metadatas)
        ]
    } 