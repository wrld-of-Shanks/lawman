# Local LLM Implementation for SPECTER Legal Assistant

This document explains how the SPECTER legal assistant has been modified to use a local language model instead of relying on external API services like OpenAI or OpenRouter.

## Overview

The application now uses Hugging Face's Transformers library to run a local language model for generating responses to legal queries. This approach eliminates the need for API keys and external dependencies, making the application fully self-contained.

## Implementation Details

### Model Selection

- Base model: `distilgpt2`
- Reason: This model is lightweight enough to run on most machines without requiring specialized hardware, while still providing reasonable text generation capabilities.

### Files Modified

1. **chat_engine.py**
   - Replaced OpenAI client with Hugging Face's Transformers pipeline
   - Implemented local text generation with configurable parameters
   - Added fallback to base model if fine-tuned model is not available

### Data Processing

Two new scripts have been added to support the local LLM:

1. **ingest_data_for_llm.py**
   - Processes legal documents from various sources (PDF, DOCX, TXT, JSONL, SQLite)
   - Extracts text content and formats it for training
   - Outputs processed data to `data/processed/legal_training_data.jsonl`

2. **train_legal_model.py**
   - Fine-tunes the base model on legal data
   - Uses the processed data from the ingestion script
   - Saves the fine-tuned model to `backend/models/legal_llm/`

## How It Works

1. When the application starts, it attempts to load a fine-tuned model from the `backend/models/legal_llm/` directory.
2. If a fine-tuned model is not found, it falls back to the base `distilgpt2` model.
3. When a user submits a query:
   - The system searches for relevant document chunks using the embedding store
   - The retrieved chunks are combined with the query to form a prompt
   - The local model generates a response based on the prompt
   - The response is returned to the user along with source information

## Training the Model

To improve the model's performance on legal queries, you can train it on your legal data:

1. Run the data ingestion script:
   ```
   python ingest_data_for_llm.py
   ```

2. Run the training script:
   ```
   python train_legal_model.py
   ```

The training process will fine-tune the model on your legal data and save it to the `backend/models/legal_llm/` directory. The application will automatically use this fine-tuned model the next time it starts.

## Performance Considerations

- The local model may be slower than cloud-based APIs, especially on machines without GPU acceleration.
- Response quality may vary depending on the amount and quality of training data.
- For better performance, consider:
  - Using a machine with GPU support
  - Providing more diverse and high-quality legal training data
  - Adjusting generation parameters in `chat_engine.py` (temperature, top_p, etc.)

## Future Improvements

- Implement more sophisticated training techniques (e.g., RLHF)
- Add support for larger models with better capabilities
- Implement model quantization for better performance on CPU
- Add multilingual support for Indian regional languages