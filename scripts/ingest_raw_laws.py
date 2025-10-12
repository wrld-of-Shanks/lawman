import os
import sys
import json
import logging
import sqlite3

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.doc_parser import parse_and_chunk
from backend.embed_store import add_chunks_to_db

RAW_DIR = os.path.join("data", "raw_laws")
DB_FILE = "legal_acts.db"


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


def summarize_text(text: str, limit: int = 1000) -> str:
    text = " ".join(text.split())
    return text[:limit]


def ingest_file(conn: sqlite3.Connection, path: str) -> Dict[str, int]:
    filename = os.path.basename(path)
    act_name = os.path.splitext(filename)[0]
    chunks: List[str] = parse_and_chunk(path)

    # Insert a coarse summary row to SQLite so /law_search has something
    definition = summarize_text(" ".join(chunks[:5])) if chunks else ""
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO laws (act, section, title, definition, punishment, keywords) VALUES (?, ?, ?, ?, ?, ?)",
        (act_name, "", act_name, definition, "", ""),
    )
    conn.commit()

    # Add chunks to vector store with metadata
    metadatas = [{"act": act_name, "filename": filename, "source": "raw_laws"} for _ in chunks]
    if chunks:
        add_chunks_to_db(chunks, metadatas)

    return {"sqlite_rows": 1, "vector_chunks": len(chunks)}


def main() -> None:
    if not os.path.isdir(RAW_DIR):
        print(f"No directory: {RAW_DIR}")
        return
    files = [os.path.join(RAW_DIR, f) for f in os.listdir(RAW_DIR) if os.path.isfile(os.path.join(RAW_DIR, f))]
    if not files:
        print("No files to ingest in data/raw_laws/")
        return
    conn = sqlite3.connect(DB_FILE)
    try:
        ensure_schema(conn)
        total_sql = 0
        total_vec = 0
        for fp in files:
            try:
                stats = ingest_file(conn, fp)
                total_sql += stats["sqlite_rows"]
                total_vec += stats["vector_chunks"]
                print(f"Ingested {os.path.basename(fp)} -> SQLite +{stats['sqlite_rows']}, vectors +{stats['vector_chunks']}")
            except Exception as e:
                print(f"Failed to ingest {fp}: {e}")
        print(f"Done. SQLite rows added: {total_sql}; vector chunks added: {total_vec}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()


