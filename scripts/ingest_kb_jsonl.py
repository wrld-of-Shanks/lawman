import os
import sys
import json
import logging
import sqlite3
from typing import List, Dict

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.embed_store import add_chunks_to_db

DB_FILE = "legal_acts.db"
INPUT_FILES_GLOB = [
    os.path.join("data", "processed", "kb_seed.jsonl"),
]


def ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS laws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act TEXT,
            section TEXT,
            title TEXT,
            definition TEXT,
            punishment TEXT,
            keywords TEXT
        )
        """
    )
    conn.commit()


def load_jsonl(path: str) -> List[Dict]:
    records: List[Dict] = []
    if not os.path.exists(path):
        return records
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                # Skip malformed lines
                continue
    return records


def insert_into_sqlite(conn: sqlite3.Connection, records: List[Dict]) -> int:
    cur = conn.cursor()
    inserted = 0
    for r in records:
        act = r.get("instrument") or r.get("act") or ""
        section = r.get("section") or ""
        title = r.get("title") or r.get("marginal_title") or ""
        # Prefer exam-oriented summary for definition column; fallback to chunk_text
        definition = r.get("text_summary") or r.get("chunk_text") or ""
        punishment = (r.get("punishment") or "")
        tags = r.get("tags") or []
        keywords = ", ".join(tags)
        cur.execute(
            "INSERT INTO laws (act, section, title, definition, punishment, keywords) VALUES (?, ?, ?, ?, ?, ?)",
            (act, section, title, definition, punishment, keywords),
        )
        inserted += 1
    conn.commit()
    return inserted


def upsert_embeddings(records: List[Dict]) -> int:
    chunks: List[str] = []
    metadatas: List[Dict] = []
    for r in records:
        text = r.get("chunk_text") or r.get("text_summary")
        if not text:
            continue
        chunks.append(text)
        metadatas.append(
            {
                "act": r.get("instrument"),
                "section": r.get("section"),
                "title": r.get("title"),
                "domain": r.get("domain"),
                "instrument_year": r.get("instrument_year"),
                "source_url": r.get("source_url"),
                "tags": ", ".join(r.get("tags", [])),
            }
        )
    if not chunks:
        return 0
    add_chunks_to_db(chunks, metadatas)
    return len(chunks)


def main() -> None:
    # Gather all input jsonl files
    input_paths: List[str] = []
    for p in INPUT_FILES_GLOB:
        if os.path.exists(p):
            input_paths.append(p)

    if not input_paths:
        print("No input JSONL files found. Place kb_*.jsonl in data/processed/")
        return

    all_records: List[Dict] = []
    for path in input_paths:
        recs = load_jsonl(path)
        print(f"Loaded {len(recs)} records from {path}")
        all_records.extend(recs)

    if not all_records:
        print("No records to ingest.")
        return

    conn = sqlite3.connect(DB_FILE)
    try:
        ensure_schema(conn)
        n_sql = insert_into_sqlite(conn, all_records)
        n_vec = upsert_embeddings(all_records)
        print(f"Inserted into SQLite: {n_sql} rows; added to vector store: {n_vec} chunks.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()


