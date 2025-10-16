import os
import logging
from typing import List, Dict, Optional

import chromadb
from chromadb.config import Settings

# Lazy init globals to avoid crashing the app at import time on platforms without model/cache access
_chroma_client = None
_collection = None
_embedder = None

BASE_DIR = os.path.join("data", "processed")
CHROMA_PATH = os.path.join(BASE_DIR, "chroma")

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)


def _get_chroma_collection():
    global _chroma_client, _collection
    if _collection is not None:
        return _collection
    try:
        try:
            _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        except Exception:
            _chroma_client = chromadb.Client(Settings(persist_directory=CHROMA_PATH))
        _collection = _chroma_client.get_or_create_collection("law_chunks")
        return _collection
    except Exception as e:
        logging.error(f"Chroma initialization failed: {e}")
        _collection = None
        return None


def _get_embedder():
    global _embedder
    if _embedder is not None:
        return _embedder
    try:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        return _embedder
    except Exception as e:
        logging.error(f"SentenceTransformer init failed: {e}")
        _embedder = None
        return None


def add_chunks_to_db(chunks: List[str], metadata: List[Dict]):
    collection = _get_chroma_collection()
    embedder = _get_embedder()
    if not collection or not embedder:
        logging.warning("Vector store or embedder unavailable; skipping add_chunks_to_db.")
        return
    embeddings = embedder.encode(chunks).tolist()
    ids = [f"chunk_{i}_{os.urandom(4).hex()}" for i in range(len(chunks))]
    try:
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadata,
            ids=ids
        )
        try:
            # Persist if supported
            _chroma_client.persist()  # type: ignore[attr-defined]
        except Exception:
            pass
    except Exception as e:
        logging.error(f"Failed to add chunks to vector store: {e}")


def search_chunks(query: str, top_k: int = 5):
    collection = _get_chroma_collection()
    embedder = _get_embedder()
    if not collection or not embedder:
        logging.warning("Vector search unavailable; returning empty results.")
        return {"documents": [[]], "metadatas": [[]]}
    try:
        query_emb = embedder.encode([query]).tolist()[0]
        results = collection.query(query_embeddings=[query_emb], n_results=top_k)
        return results
    except Exception as e:
        logging.error(f"Vector search failed: {e}")
        return {"documents": [[]], "metadatas": [[]]}
