# SPECTER Legal Assistant 🏛️

> **Your AI-Powered Legal Companion**

SPECTER is a comprehensive legal assistant application that combines modern web technologies with advanced AI to provide accurate legal information, document analysis, and intelligent legal guidance.

## ✨ Features

- **🤖 AI Legal Chat** - Get instant answers to legal questions with source citations
- **📄 Document Analysis** - Upload and analyze legal documents
- **🔐 User Authentication** - Secure JWT-based authentication system
- **📊 User Dashboard** - Personal legal query history and statistics
- **🌐 Multi-language Support** - Available in English, Hindi, Kannada, Tamil, Telugu, and Malayalam
- **📱 Responsive Design** - Beautiful, modern interface that works on all devices

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lawman
   ```

2. **Set up the backend**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration
   
   # Start the backend server
   cd backend
   python main.py
   ```

3. **Set up the frontend**
   ```bash
   # Install Node.js dependencies
   cd frontend/react_app
   npm install
   
   # Start the development server
   npm start
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8002

## 📁 Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed information about the project organization.

```
lawman/
├── backend/          # FastAPI backend server
├── frontend/         # React frontend application
├── data/            # Legal documents and knowledge base
├── scripts/         # Utility scripts for data processing
└── docs/           # Documentation files
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Email Service Configuration (Contact Lawyer Feature)
LAWYER_SMTP_USER=your-email@gmail.com
LAWYER_SMTP_PASS=your-app-password
LAWYER_SMTP_HOST=smtp.gmail.com
LAWYER_SMTP_PORT=587
LAWYER_RECEIVER_EMAIL=lawyer@lawfirm.com

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key
```

## 🎯 Usage

### For Users
1. **Register/Login** - Create an account or sign in
2. **Ask Questions** - Use the chat interface to ask legal questions
3. **Upload Documents** - Analyze legal documents for insights
4. **View Dashboard** - Track your legal queries and account information

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