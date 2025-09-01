import os
import json
import sqlite3
import spacy

DB_FILE = "legal_acts.db"
INPUT_DIR = "data/processed/"

# Load spaCy English model for advanced keyword extraction
nlp = spacy.load("en_core_web_sm")

def extract_keywords(text):
    doc = nlp(text)
    keywords = set()
    for token in doc:
        if token.pos_ in {"NOUN", "PROPN"} and not token.is_stop and len(token.text) > 3:
            keywords.add(token.lemma_.lower())
    for ent in doc.ents:
        keywords.add(ent.text.lower())
    return list(keywords)

def main():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS laws (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        act TEXT,
        section TEXT,
        title TEXT,
        definition TEXT,
        punishment TEXT,
        keywords TEXT
    )
    """)
    for fname in os.listdir(INPUT_DIR):
        if fname.endswith("_structured.json"):
            act = fname.replace("_structured.json", "")
            with open(os.path.join(INPUT_DIR, fname), "r", encoding="utf-8") as f:
                sections = json.load(f)
            for sec in sections:
                # Use advanced keyword extraction
                adv_keywords = extract_keywords(sec.get("definition", ""))
                c.execute(
                    "INSERT INTO laws (act, section, title, definition, punishment, keywords) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        act,
                        sec.get("section", ""),
                        sec.get("title", ""),
                        sec.get("definition", ""),
                        sec.get("punishment", ""),
                        ", ".join(adv_keywords)
                    )
                )
            print(f"Imported {len(sections)} sections from {fname}")
    conn.commit()
    conn.close()
    print(f"All done! Data is in {DB_FILE}")

if __name__ == "__main__":
    main() 