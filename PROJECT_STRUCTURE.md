# 🏗️ SPECTER Legal Assistant - Project Structure

## 📁 **Root Directory Structure**

```
lawman/
├── 📄 README.md                    # Main project documentation
├── 📄 CHANGELOG.md                 # Version history and updates
├── 📄 CONTRIBUTING.md              # Contribution guidelines
├── 📄 LICENSE                      # MIT License
├── 📄 PROJECT_STRUCTURE.md         # This file
├── 📄 .gitignore                   # Git ignore rules
├── 📄 requirements.txt             # Python dependencies
├── 📄 netlify.toml                 # Frontend deployment config
├── 🔒 .env                         # Environment variables (local)
├── 📁 backend/                     # FastAPI backend application
├── 📁 frontend/                    # React frontend application
└── 📁 data/                        # Legal documents and datasets
```

## 🔧 **Backend Structure (`/backend/`)**

```
backend/
├── 📄 main.py                      # FastAPI application entry point
├── 📄 auth_mongo.py                # MongoDB-based authentication
├── 📄 mongodb_config.py            # Database configuration
├── 📄 tracing.py                   # System monitoring and logging
├── 📄 chat_engine.py               # Legal query processing engine
├── 📄 doc_parser.py                # Document parsing utilities
├── 📄 embed_store.py               # Vector embeddings and search
├── 📄 legal_solutions.py           # Detailed legal solutions database
├── 📄 comprehensive_legal_db.py    # Complete legal topics database
├── 📄 .env.example                 # Environment template
└── 📄 __init__.py                  # Python package marker
```

### **Backend Components**

#### **🚀 Core Application (`main.py`)**
- FastAPI application setup
- CORS middleware configuration
- Route definitions and API endpoints
- Startup and shutdown event handlers
- Health check and monitoring endpoints

#### **🔐 Authentication (`auth_mongo.py`)**
- User registration and login
- JWT token generation and validation
- Email verification with OTP
- Password reset functionality
- User session management

#### **🗄️ Database (`mongodb_config.py`)**
- MongoDB connection management
- Database and collection initialization
- Index creation for performance
- Connection pooling and error handling

#### **📊 Monitoring (`tracing.py`)**
- System activity logging
- Performance metrics tracking
- User behavior analytics
- Error tracking and debugging
- Admin dashboard data

#### **🤖 Legal Engine (`chat_engine.py`)**
- Natural language query processing
- Legal topic matching
- Response formatting
- Multi-language support preparation

#### **📄 Document Processing (`doc_parser.py`)**
- PDF text extraction (PyMuPDF)
- DOCX document parsing
- Text chunking for analysis
- File format validation

#### **🔍 Vector Search (`embed_store.py`)**
- ChromaDB integration
- Sentence transformer embeddings
- Semantic search capabilities
- Document similarity matching

#### **⚖️ Legal Database (`legal_solutions.py`)**
- Detailed legal procedures
- Case law references
- Step-by-step solutions
- Court fees and documentation

#### **📚 Comprehensive Legal DB (`comprehensive_legal_db.py`)**
- 200+ legal topics coverage
- All major Indian law domains
- Specialized legal areas
- Constitutional to commercial law

## 🎨 **Frontend Structure (`/frontend/react_app/`)**

```
frontend/react_app/
├── 📁 public/                      # Static assets
│   ├── 📄 index.html              # Main HTML template
│   ├── 🖼️ favicon.ico             # Website icon
│   └── 📄 manifest.json           # PWA manifest
├── 📁 src/                         # React source code
│   ├── 📄 index.tsx               # Application entry point
│   ├── 📄 App.tsx                 # Main App component
│   ├── 📄 Auth.tsx                # Authentication components
│   ├── 📄 config.ts               # Configuration settings
│   └── 📁 components/             # Reusable components
├── 📄 package.json                # Node.js dependencies
├── 📄 tsconfig.json               # TypeScript configuration
├── 📄 .env.example                # Environment template
└── 📄 README.md                   # Frontend documentation
```

### **Frontend Components**

#### **⚛️ Core Application**
- React 18 with TypeScript
- Material-UI component library
- Responsive design principles
- Progressive Web App features

#### **🔐 Authentication Flow**
- User registration forms
- Login and logout functionality
- JWT token management
- Protected route handling

#### **💬 Chat Interface**
- Real-time legal query processing
- Message history management
- File upload capabilities
- Response formatting and display

#### **📊 Admin Dashboard**
- System statistics display
- User activity monitoring
- Performance metrics visualization
- Error tracking interface

## 📊 **Data Structure (`/data/`)**

```
data/
├── 📁 raw_laws/                    # Original legal documents
│   ├── 📄 constitution.txt        # Indian Constitution
│   ├── 📄 ipc.txt                 # Indian Penal Code
│   ├── 📄 crpc.txt                # Criminal Procedure Code
│   └── 📄 ...                     # Other legal acts
└── 📁 processed/                   # Processed legal data
    ├── 📁 chroma/                  # ChromaDB vector store
    └── 📄 legal_acts.json          # Structured legal data
```

## 🔧 **Configuration Files**

### **Environment Variables**
```bash
# Backend (.env)
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=specter_legal
JWT_SECRET_KEY=your-secret-key
OPENAI_API_KEY=optional-openai-key

# Frontend (.env)
REACT_APP_API_URL=http://localhost:8002
```

### **Deployment Configuration**
- `netlify.toml` - Frontend deployment settings
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies
- `.gitignore` - Version control exclusions

## 🚀 **API Architecture**

### **RESTful Endpoints**
```
Authentication:
├── POST /auth/register             # User registration
├── POST /auth/login                # User login
└── POST /auth/verify-otp           # Email verification

Legal Services:
├── POST /chat                      # Legal query processing
├── POST /legal-solution            # Detailed legal solutions
├── GET  /legal-topics              # Available topics list
└── POST /upload                    # Document analysis

Admin & Monitoring:
├── GET /admin/traces               # System activity logs
├── GET /admin/stats                # Usage statistics
└── GET /admin/user-activity/{id}   # User analytics

System:
├── GET /health                     # Health check
└── GET /docs                       # API documentation
```

## 🗄️ **Database Schema**

### **MongoDB Collections**
```javascript
// Users Collection
{
  _id: ObjectId,
  email: String,
  password_hash: String,
  full_name: String,
  is_verified: Boolean,
  created_at: Date,
  updated_at: Date
}

// Legal Acts Collection
{
  _id: ObjectId,
  title: String,
  content: String,
  act_type: String,
  sections: Array,
  created_at: Date
}

// Traces Collection
{
  _id: ObjectId,
  timestamp: Date,
  event_type: String,
  user_id: String,
  data: Object,
  request_id: String,
  ip_address: String
}
```

## 🔍 **Key Features Implementation**

### **Legal Query Processing**
1. **Input Processing**: Natural language understanding
2. **Topic Matching**: Keyword and semantic matching
3. **Database Lookup**: Comprehensive legal database search
4. **Response Generation**: Structured legal information
5. **Solution Provision**: Step-by-step legal procedures

### **Document Analysis**
1. **File Upload**: Multi-format support (PDF, DOCX, TXT)
2. **Text Extraction**: Format-specific parsing
3. **Chunking**: Intelligent text segmentation
4. **Embedding**: Vector representation generation
5. **Storage**: ChromaDB vector database

### **User Management**
1. **Registration**: Email-based user creation
2. **Verification**: OTP-based email confirmation
3. **Authentication**: JWT token-based sessions
4. **Authorization**: Role-based access control
5. **Monitoring**: Complete activity tracking

## 📈 **Performance Considerations**

### **Backend Optimizations**
- Async/await for database operations
- Connection pooling for MongoDB
- Efficient vector search with ChromaDB
- Request caching for frequent queries
- Comprehensive error handling

### **Frontend Optimizations**
- React component memoization
- Lazy loading for large components
- Efficient state management
- Responsive design principles
- Progressive Web App features

## 🛡️ **Security Measures**

### **Authentication Security**
- JWT token-based authentication
- Password hashing with bcrypt
- Email verification requirements
- Session timeout management
- CORS protection

### **Data Security**
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Rate limiting for API endpoints
- Comprehensive audit logging

## 🔄 **Development Workflow**

### **Local Development**
1. Clone repository
2. Set up backend environment
3. Install dependencies
4. Configure databases
5. Start development servers

### **Testing Strategy**
- Unit tests for core functions
- Integration tests for API endpoints
- Frontend component testing
- End-to-end user flow testing
- Performance and load testing

### **Deployment Process**
1. Code review and approval
2. Automated testing pipeline
3. Staging environment deployment
4. Production deployment
5. Monitoring and rollback capability

---

This structure provides a scalable, maintainable, and professional legal assistant application with comprehensive Indian law coverage.
