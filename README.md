# 🏛️ SPECTER Legal Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-47A248.svg)](https://www.mongodb.com/)

> **Comprehensive AI-Powered Legal Assistant for Indian Law**  
> Providing accessible legal information, document analysis, and procedural guidance with 200+ legal topics coverage.

## 🌟 **Features**

### 🤖 **Intelligent Legal Assistant**
- **Natural Language Processing**: Advanced chat interface for legal queries
- **200+ Legal Topics**: Comprehensive coverage of all major Indian law domains
- **Case Law References**: 50+ landmark case citations with legal precedents
- **Step-by-Step Solutions**: Detailed procedures for 12+ common legal issues
- **Multi-Domain Coverage**: Constitutional, Criminal, Civil, Commercial, Labour, Tax, Environmental law

### 📄 **Document Processing**
- **Multi-Format Support**: PDF, DOCX, TXT file analysis
- **Vector Search**: ChromaDB-powered semantic search
- **Document Chunking**: Intelligent text segmentation for better analysis
- **Upload Tracking**: Complete audit trail for document processing

### 🔐 **Security & Authentication**
- **JWT-Based Auth**: Secure token-based authentication
- **Email Verification**: OTP-based email verification system
- **User Management**: Complete user registration and profile management
- **Session Tracking**: Comprehensive user activity monitoring

### 📊 **Monitoring & Analytics**
- **Real-Time Tracing**: Complete system activity logging
- **Performance Metrics**: API response times and usage statistics
- **Admin Dashboard**: System health monitoring and user analytics
- **Error Tracking**: Comprehensive error logging and debugging

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │   MongoDB Atlas │
│                 │    │                 │    │                 │
│  • Material-UI  │◄──►│  • 200+ Topics  │◄──►│  • User Data    │
│  • TypeScript   │    │  • Legal Solutions│   │  • Legal Acts   │
│  • Auth System  │    │  • Document AI  │    │  • Audit Logs   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   ChromaDB      │◄─────────────┘
                        │  Vector Store   │
                        │  • Embeddings   │
                        │  • Semantic     │
                        │    Search       │
                        └─────────────────┘
```

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+ 🐍
- Node.js 16+ 📦
- MongoDB (local or Atlas) 🍃
- Git 📝

### **1. Clone Repository**
```bash
git clone https://github.com/wrld-of-Shanks/lawman.git
cd lawman
```

### **2. Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start backend server
python main.py
```

### **3. Frontend Setup**
```bash
cd frontend/react_app

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Set REACT_APP_API_URL=http://localhost:8002

# Start development server
npm start
```

### **4. Access Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8002
- **API Docs**: http://localhost:8002/docs

## 📚 **Legal Coverage**

### **🏛️ Constitutional Law (15+ Topics)**
- Fundamental Rights & Duties
- Directive Principles of State Policy
- Emergency Provisions & Constitutional Amendments
- Judicial Review & Separation of Powers

### **⚖️ Criminal Law (25+ Topics)**
- Indian Penal Code (IPC) - Complete coverage
- Criminal Procedure Code (CrPC)
- Evidence Act & Cyber Crimes
- Terrorism, Narcotics & Corruption Laws

### **👨‍👩‍👧‍👦 Civil & Family Law (20+ Topics)**
- Contract Law & Tort Law
- Property & Succession Laws
- Marriage, Divorce & Child Custody
- Maintenance & Adoption Laws

### **🏢 Commercial Law (15+ Topics)**
- Company Law & Partnership
- Insolvency & Bankruptcy Code
- Securities Law & Banking Regulation
- Competition Law & Arbitration

### **👷 Labour Law (12+ Topics)**
- Industrial Relations & Wages
- Social Security & Working Conditions
- Employment Rights & Trade Unions
- Maternity Benefits & Sexual Harassment

### **💰 Tax Law (8+ Topics)**
- Income Tax & GST
- Customs & Central Excise
- Service Tax & Tax Procedures

### **🌍 Environmental Law (8+ Topics)**
- Environment Protection Act
- Pollution Control & Forest Conservation
- Wildlife Protection & Green Tribunal

### **🏛️ Administrative Law (10+ Topics)**
- Right to Information (RTI)
- Public Interest Litigation (PIL)
- Ombudsman & Central Vigilance

### **💻 Information Technology (8+ Topics)**
- IT Act 2000 & Data Protection
- Cyber Security & E-commerce Laws

### **🚗 Specialized Areas (30+ Topics)**
- Motor Vehicle Law
- Consumer Protection
- Real Estate (RERA)
- Banking & Finance
- Agricultural Law
- Health & Medical Law
- Media & Entertainment
- Sports Law
- International Law

## 🔧 **API Reference**

### **Authentication**
```http
POST /auth/register
POST /auth/login  
POST /auth/verify-otp
```

### **Legal Services**
```http
POST /chat                 # Legal query processing
POST /legal-solution      # Detailed legal solutions
GET  /legal-topics        # List all available topics
POST /upload              # Document analysis
```

### **Admin & Monitoring**
```http
GET /admin/traces         # System activity logs
GET /admin/stats          # Usage statistics
GET /admin/user-activity/{user_id}  # User analytics
```

## 💡 **Usage Examples**

### **Legal Query**
```bash
curl -X POST "http://localhost:8002/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are fundamental rights under Indian Constitution?"}'
```

### **Detailed Legal Solution**
```bash
curl -X POST "http://localhost:8002/legal-solution" \
  -H "Content-Type: application/json" \
  -d '{"message": "bail application procedure"}'
```

### **Document Upload**
```bash
curl -X POST "http://localhost:8002/upload" \
  -F "file=@legal_document.pdf"
```

## 📊 **System Statistics**

- **📖 Total Legal Topics**: 213
- **⚖️ Detailed Legal Solutions**: 12 comprehensive procedures
- **📚 Case Law References**: 50+ landmark cases
- **🏛️ Law Domains Covered**: 15+ major areas
- **🔍 Search Capabilities**: Semantic vector search
- **📈 Response Time**: <100ms for FAQ queries
- **🛡️ Security Features**: JWT auth + audit logging

## 🚀 **Deployment**

### **Production Deployment**
- **Frontend**: Deployed on Netlify
- **Backend**: Cloud deployment ready (Railway, Heroku, AWS)
- **Database**: MongoDB Atlas
- **Monitoring**: Built-in tracing and analytics

### **Environment Configuration**
```bash
# Production Backend
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/
DATABASE_NAME=specter_legal
JWT_SECRET_KEY=your-production-secret

# Production Frontend  
REACT_APP_API_URL=https://your-backend-url.com
```

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

## 📄 **Legal Disclaimer**

⚠️ **Important**: SPECTER Legal Assistant provides general legal information for educational purposes only. This is **NOT** a substitute for professional legal advice. Users should consult qualified lawyers for specific legal matters and representation.

## 📞 **Support**

- 🐛 **Bug Reports**: [Create an Issue](https://github.com/wrld-of-Shanks/lawman/issues)
- 💡 **Feature Requests**: [Discussions](https://github.com/wrld-of-Shanks/lawman/discussions)
- 📧 **Contact**: [Email Support](mailto:support@specter-legal.com)

## 🗺️ **Roadmap**

- [ ] 🤖 Advanced AI integration with local LLMs
- [ ] 🌐 Multi-language interface (Hindi, Tamil, Bengali)
- [ ] 📱 Mobile application (React Native)
- [ ] 📋 Legal document templates
- [ ] 👩‍⚖️ Lawyer directory integration
- [ ] 🔍 Advanced case law search engine
- [ ] 📊 Legal analytics dashboard
- [ ] 🎯 Specialized domain modules

## 📜 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Indian Legal System** for comprehensive law coverage
- **Open Source Community** for amazing tools and libraries
- **Legal Professionals** for domain expertise and guidance

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

[🏠 Homepage](https://specter-legal-assistant.netlify.app) • [📖 Documentation](https://github.com/wrld-of-Shanks/lawman/wiki) • [🐛 Report Bug](https://github.com/wrld-of-Shanks/lawman/issues) • [💡 Request Feature](https://github.com/wrld-of-Shanks/lawman/discussions)

</div>

### For Developers
1. **Data Ingestion** - Use scripts to process legal documents
2. **Model Training** - Train custom legal models
3. **API Integration** - Integrate with the FastAPI backend
4. **Frontend Customization** - Modify the React interface

## 📧 Contact Lawyer Feature Setup

### Gmail Configuration for Email Service

**Step 1: Enable 2-Factor Authentication**
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification if not already enabled
3. Verify your phone number or authenticator app

**Step 2: Generate App Password**
1. In Google Account Security, go to "App passwords"
2. Select "Mail" as the app type
3. Generate a 16-character app password
4. Use this password as `LAWYER_SMTP_PASS` (not your regular Gmail password)

**Step 3: Configure Environment Variables**
```env
# Sender email (your Gmail account)
LAWYER_SMTP_USER=your-gmail@gmail.com

# App password (16-character code from Step 2)
LAWYER_SMTP_PASS=abcd-efgh-ijkl-mnop

# Destination email (where lawyer requests go)
LAWYER_RECEIVER_EMAIL=legal-team@lawfirm.com

# SMTP settings (default for Gmail)
LAWYER_SMTP_HOST=smtp.gmail.com
LAWYER_SMTP_PORT=587
```

**Step 4: Test Email Configuration**
```bash
# Method 1: Use the provided test script
cd backend
python test_email_config.py

# Method 2: Test via API endpoint
curl -X POST "http://localhost:8002/contact-lawyer" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "phone": "123-456-7890",
    "caseType": "Contract Dispute",
    "description": "Test message for email configuration"
  }'
```

### Email Flow
1. **User submits** contact form on frontend
2. **Backend processes** request via `/contact-lawyer` endpoint
3. **Email sent** from `LAWYER_SMTP_USER` to `LAWYER_RECEIVER_EMAIL`
4. **Lawyer receives** formatted inquiry with user details

### Configuration Files
- **`.env.example`** - Template for environment variables
- **`test_email_config.py`** - Email configuration test script

## 🛠️ Development

### Running in Development Mode

**Backend:**
```bash
cd backend
python main.py
```

**Frontend:**
```bash
cd frontend/react_app
npm start
```

### Building for Production

**Frontend:**
```bash
cd frontend/react_app
npm run build
```

### Data Processing

**Ingest Legal Documents:**
```bash
python scripts/ingest_raw_laws.py
```

**Process Knowledge Base:**
```bash
python scripts/ingest_kb_jsonl.py
```

## 📚 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8002/docs
- **ReDoc Documentation**: http://localhost:8002/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

## 🙏 Acknowledgments

- OpenAI for GPT models
- FastAPI for the excellent web framework
- React and Material-UI for the frontend
- ChromaDB for vector storage
- All contributors and legal experts who helped with the knowledge base

---

**Built with ❤️ for the legal community**