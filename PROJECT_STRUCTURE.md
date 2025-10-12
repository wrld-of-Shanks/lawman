# SPECTER Legal Assistant - Project Structure

## 📁 Project Organization

```
lawman/
├── 📂 backend/                 # FastAPI Backend Server
│   ├── __init__.py
│   ├── main.py                # Main FastAPI application
│   ├── auth.py                # Authentication & user management
│   ├── chat_engine.py         # AI chat functionality
│   ├── database.py            # Database operations
│   ├── doc_parser.py          # Document parsing utilities
│   ├── embed_store.py         # Vector embeddings & search
│   └── .env                   # Environment variables
│
├── 📂 frontend/               # React Frontend Application
│   └── react_app/
│       ├── public/            # Static assets
│       ├── src/               # React source code
│       │   ├── App.tsx        # Main application component
│       │   ├── Auth.tsx       # Authentication component
│       │   ├── Dashboard.tsx  # User dashboard
│       │   └── App.css        # Styling
│       ├── package.json       # Frontend dependencies
│       └── build/             # Production build (auto-generated)
│
├── 📂 data/                   # Legal Data & Knowledge Base
│   ├── processed/             # Processed legal documents
│   │   ├── chroma/           # Vector database
│   │   ├── kb_seed.jsonl     # Knowledge base seed data
│   │   └── legal_training_data.jsonl
│   └── raw_laws/             # Raw legal documents
│       ├── constitution.pdf
│       ├── comprehensive_legal_faq.txt
│       └── legal_knowledge_sources.txt
│
├── 📂 scripts/               # Utility Scripts
│   ├── ingest_data_for_llm.py    # Data ingestion for LLM training
│   ├── train_legal_model.py      # Local LLM training script
│   ├── ingest_kb_jsonl.py        # Knowledge base ingestion
│   ├── ingest_raw_laws.py        # Raw legal document processing
│   ├── batch_upload.py           # Batch document upload
│   ├── import_acts_json_to_sql.py # Import legal acts to database
│   ├── parse_all_acts_to_json.py # Parse legal acts to JSON
│   └── parse_ipc_to_json.py      # Parse IPC to JSON
│
├── 📄 Configuration Files
│   ├── requirements.txt       # Python dependencies
│   ├── .env                  # Environment variables (create from .env.example)
│   ├── .gitignore           # Git ignore rules
│   └── README.md            # Main project documentation
│
├── 📄 Documentation
│   ├── LEGAL_AI_MODEL_GUIDE.md  # AI model guide
│   ├── LOCAL_LLM_README.md      # Local LLM setup
│   └── PROJECT_STRUCTURE.md     # This file
│
└── 📄 Database Files
    ├── users.db             # User authentication database
    └── legal_acts.db        # Legal knowledge database
```

## 🚀 Core Components

### Backend Services
- **FastAPI Server** (`backend/main.py`) - Main API server
- **Authentication** (`backend/auth.py`) - JWT-based user auth
- **AI Chat Engine** (`backend/chat_engine.py`) - Legal Q&A system
- **Document Parser** (`backend/doc_parser.py`) - PDF/text processing
- **Vector Store** (`backend/embed_store.py`) - Semantic search

### Frontend Application
- **React App** - Modern web interface with Material-UI
- **Authentication UI** - Login/register with themed design
- **Main Interface** - SPECTER legal assistant interface
- **Dashboard** - User management and statistics

### Data Management
- **Raw Legal Documents** - Source legal texts and PDFs
- **Processed Data** - Chunked and embedded documents
- **Vector Database** - ChromaDB for semantic search
- **SQLite Databases** - User data and legal acts

### Utility Scripts
- **Data Ingestion** - Process and import legal documents
- **Model Training** - Train local legal LLM
- **Database Management** - Import/export legal data

## 🔧 Development Workflow

### Running the Application
1. **Backend**: `cd backend && python main.py`
2. **Frontend**: `cd frontend/react_app && npm start`

### Data Processing
1. **Ingest Raw Laws**: `python scripts/ingest_raw_laws.py`
2. **Process Knowledge Base**: `python scripts/ingest_kb_jsonl.py`
3. **Train Local Model**: `python scripts/train_legal_model.py`

### Database Management
- User authentication data: `users.db`
- Legal knowledge base: `legal_acts.db`
- Vector embeddings: `data/processed/chroma/`

## 📝 File Naming Conventions

- **Python files**: `snake_case.py`
- **React components**: `PascalCase.tsx`
- **Configuration**: `lowercase.extension`
- **Documentation**: `UPPERCASE.md`
- **Data files**: `descriptive_name.extension`

## 🧹 Maintenance

### Auto-Generated Files (Ignored)
- `__pycache__/` - Python bytecode
- `node_modules/` - Node.js dependencies
- `build/` - React production build
- `.DS_Store` - macOS system files

### Regular Cleanup
- Remove unused dependencies
- Update documentation
- Clean temporary files
- Optimize database indexes

## 🔒 Security Notes

- Environment variables in `.env` files
- JWT secrets for authentication
- Database files excluded from version control
- API keys stored securely

This structure ensures maintainability, scalability, and clear separation of concerns.
