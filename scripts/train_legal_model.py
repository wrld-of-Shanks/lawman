#!/usr/bin/env python3
"""
Train a local LLM on legal data for the lawman project.
This script fine-tunes a small language model on the legal data in the data directory.
"""

import os
import json
import torch
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    TextDataset, 
    DataCollatorForLanguageModeling,
    Trainer, 
    TrainingArguments
)
import glob
import logging
import sqlite3
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BASE_MODEL = "distilgpt2"  # A smaller model that can run locally
MODEL_DIR = os.path.join("backend", "models", "legal_llm")
DATA_DIR = "data"
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
RAW_LAWS_DIR = os.path.join(DATA_DIR, "raw_laws")
TRAIN_FILE = os.path.join(PROCESSED_DATA_DIR, "legal_train.txt")
MAX_LENGTH = 512
BATCH_SIZE = 4
EPOCHS = 3

def prepare_training_data():
    """Prepare training data from various sources in the data directory."""
    logger.info("Preparing training data...")
    
    # Create processed directory if it doesn't exist
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    # Collect text from various sources
    all_texts = []
    
    # 1. Process JSONL files
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
                                all_texts.append(data[field])
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse JSON line in {file_path}")
    
    # 2. Process TXT files
    txt_files = glob.glob(os.path.join(RAW_LAWS_DIR, "*.txt"))
    for file_path in txt_files:
        logger.info(f"Processing text file: {file_path}")
        try:
            with open(file_path, 'r') as f:
                all_texts.append(f.read())
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")
    
    # 3. Process SQLite database if it exists
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
                        all_texts.extend(texts)
            
            conn.close()
        except Exception as e:
            logger.warning(f"Error processing database {db_path}: {e}")
    
    # Format the texts for training
    formatted_texts = []
    for text in all_texts:
        if text and len(text.strip()) > 50:  # Only include substantial text
            # Format as instruction-response pairs for better fine-tuning
            formatted_text = f"<|system|>You are a legal assistant trained on Indian laws.</|system|>\n"
            formatted_text += f"<|user|>Explain this legal concept: {text[:100]}</|user|>\n"
            formatted_text += f"<|assistant|>{text}</|assistant|>\n\n"
            formatted_texts.append(formatted_text)
    
    # Write to training file
    with open(TRAIN_FILE, 'w') as f:
        f.write('\n'.join(formatted_texts))
    
    logger.info(f"Training data prepared: {len(formatted_texts)} examples written to {TRAIN_FILE}")
    return TRAIN_FILE

def train_model():
    """Fine-tune the model on legal data."""
    logger.info(f"Starting model training using {BASE_MODEL}...")
    
    # Prepare training data
    train_file = prepare_training_data()
    
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL)
    
    # Special tokens for instruction format
    special_tokens = {
        "additional_special_tokens": [
            "<|system|>", "</|system|>", 
            "<|user|>", "</|user|>", 
            "<|assistant|>", "</|assistant|>"
        ]
    }
    tokenizer.add_special_tokens(special_tokens)
    model.resize_token_embeddings(len(tokenizer))
    
    # Create dataset
    dataset = TextDataset(
        tokenizer=tokenizer,
        file_path=train_file,
        block_size=MAX_LENGTH
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False  # We're not using masked language modeling
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=MODEL_DIR,
        overwrite_output_dir=True,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        save_steps=500,
        save_total_limit=2,
        logging_steps=100,
        logging_dir=os.path.join(MODEL_DIR, "logs"),
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=dataset,
    )
    
    # Train the model
    trainer.train()
    
    # Save the model and tokenizer
    model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)
    
    logger.info(f"Model training completed. Model saved to {MODEL_DIR}")

if __name__ == "__main__":
    # Check if CUDA is available
    if torch.cuda.is_available():
        logger.info("CUDA is available. Training on GPU.")
    else:
        logger.info("CUDA is not available. Training on CPU (this will be slow).")
    
    # Train the model
    train_model()