import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import os

# Initialize ChromaDB persistent client and collection
base_dir = os.path.join("data", "processed")
os.makedirs(base_dir, exist_ok=True)
chroma_path = os.path.join(base_dir, "chroma")
os.makedirs(chroma_path, exist_ok=True)

# Prefer PersistentClient to ensure data survives between runs
try:
    chroma_client = chromadb.PersistentClient(path=chroma_path)
except Exception:
    # Fallback for older versions using Settings
    chroma_client = chromadb.Client(Settings(persist_directory=chroma_path))

collection = chroma_client.get_or_create_collection("law_chunks")

# Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def add_chunks_to_db(chunks: List[str], metadata: List[Dict]):
    embeddings = embedder.encode(chunks).tolist()
    ids = [f"chunk_{i}_{os.urandom(4).hex()}" for i in range(len(chunks))]
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadata,
        ids=ids
    )
    # Ensure data is persisted to disk so future processes can access it
    try:
        chroma_client.persist()
    except Exception:
        pass

def search_chunks(query: str, top_k: int = 5):
    query_emb = embedder.encode([query]).tolist()[0]
    results = collection.query(query_embeddings=[query_emb], n_results=top_k)
    return results 