#!/usr/bin/env python3
"""
Ingest data for the local LLM training.
This script processes legal documents and prepares them for training the local LLM.
"""

import os
import sys
import json
import glob
import logging
import sqlite3
import pandas as pd

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.doc_parser import parse_and_chunk

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = "data"
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
RAW_LAWS_DIR = os.path.join(DATA_DIR, "raw_laws")
OUTPUT_FILE = os.path.join(PROCESSED_DATA_DIR, "legal_training_data.jsonl")

def process_documents():
    """Process all documents in the data directory and extract text for training."""
    logger.info("Processing documents for LLM training...")
    
    # Create processed directory if it doesn't exist
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    # Collect text from various sources
    training_data = []
    
    # 1. Process PDF and DOCX files
    document_files = []
    for ext in ['.pdf', '.docx']:
        document_files.extend(glob.glob(os.path.join(RAW_LAWS_DIR, f"*{ext}")))
        document_files.extend(glob.glob(os.path.join(PROCESSED_DATA_DIR, f"*{ext}")))
    
    for file_path in document_files:
        logger.info(f"Processing document: {file_path}")
        try:
            chunks = parse_and_chunk(file_path)
            for chunk in chunks:
                training_data.append({
                    "text": chunk,
                    "source": os.path.basename(file_path),
                    "type": "document"
                })
        except Exception as e:
            logger.warning(f"Error processing {file_path}: {e}")
    
    # 2. Process JSONL files
    jsonl_files = glob.glob(os.path.join(PROCESSED_DATA_DIR, "*.jsonl")) + glob.glob(os.path.join(RAW_LAWS_DIR, "*.jsonl"))
    for file_path in jsonl_files:
        logger.info(f"Processing JSONL file: {file_path}")
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    # Extract text content from various possible fields
                    if isinstance(data, dict):
                        for field in ['text', 'content', 'description', 'answer', 'question']:
                            if field in data and isinstance(data[field], str):
                                training_data.append({
                                    "text": data[field],
                                    "source": os.path.basename(file_path),
                                    "type": "jsonl",
                                    "field": field
                                })
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse JSON line in {file_path}")
    
    # 3. Process TXT files
    txt_files = glob.glob(os.path.join(RAW_LAWS_DIR, "*.txt"))
    for file_path in txt_files:
        logger.info(f"Processing text file: {file_path}")
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                # Split into paragraphs
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                for paragraph in paragraphs:
                    if len(paragraph) > 50:  # Only include substantial paragraphs
                        training_data.append({
                            "text": paragraph,
                            "source": os.path.basename(file_path),
                            "type": "text"
                        })
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")
    
    # 4. Process SQLite database if it exists
    db_path = "legal_acts.db"
    if os.path.exists(db_path):
        logger.info(f"Processing SQLite database: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            # Query all tables and extract text data
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                
                # Extract text from all string columns
                for col in df.columns:
                    if df[col].dtype == 'object':  # String columns
                        texts = df[col].dropna().astype(str).tolist()
                        for text in texts:
                            if len(text) > 50:  # Only include substantial text
                                training_data.append({
                                    "text": text,
                                    "source": f"database:{table_name}",
                                    "type": "database",
                                    "field": col
                                })
            
            conn.close()
        except Exception as e:
            logger.warning(f"Error processing database {db_path}: {e}")
    
    # Write to output file
    with open(OUTPUT_FILE, 'w') as f:
        for item in training_data:
            f.write(json.dumps(item) + '\n')
    
    logger.info(f"Data ingestion completed: {len(training_data)} items written to {OUTPUT_FILE}")
    return len(training_data)

if __name__ == "__main__":
    count = process_documents()
    print(f"Successfully processed {count} text items for LLM training.")
    print(f"Output saved to {OUTPUT_FILE}")
    print("You can now run train_legal_model.py to train the local LLM on this data.")