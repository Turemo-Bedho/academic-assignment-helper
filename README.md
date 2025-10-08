# Academic Assignment Helper & Plagiarism Detector (RAG-Powered)

A comprehensive backend system that helps students with academic assignments by providing RAG-based research source suggestions and AI-powered plagiarism detection.

## 🚀 Features

- 🔐 **JWT-based Authentication** - Secure student registration and login
- 📄 **File Upload & Processing** - Support for PDF, DOCX, DOC, and TXT files
- 🔍 **RAG-Powered Source Suggestions** - Semantic search across academic papers
- 🤖 **AI-Powered Analysis** - Automatic topic detection and research suggestions
- ⚖️ **Plagiarism Detection** - Vector similarity analysis against academic database
- 🐳 **Dockerized Deployment** - Easy setup with Docker Compose
- 🔄 **Workflow Automation** - n8n workflow orchestration
- 📊 **Comprehensive Analytics** - Detailed assignment analysis and recommendations

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend API** | FastAPI (Python 3.11) |
| **Database** | PostgreSQL 16 + pgvector |
| **Vector Search** | OpenAI Embeddings (text-embedding-ada-002) |
| **Workflow Engine** | n8n |
| **Authentication** | JWT Tokens |
| **Containerization** | Docker & Docker Compose |
| **File Processing** | PyPDF2, python-docx |

## 📋 Prerequisites

- Docker and Docker Compose
- OpenAI API Key
- 4GB RAM minimum

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/academic-assignment-helper.git
cd academic-assignment-helper
```

### 2. Environment Configuration
```bash
cp .env.example .env
```
Edit `.env` file and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
JWT_SECRET_KEY=your-super-secret-jwt-key
```

### 3. Start Services
```bash
docker-compose up -d
```

### 4. Access the Application
- **API Documentation**: http://localhost:8000/docs
- **n8n Workflow UI**: http://localhost:5678
- **pgAdmin (Database)**: http://localhost:5050

## 🏗️ Project Structure

```
academic-assignment-helper/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── auth.py              # JWT authentication
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── rag_service.py       # RAG and vector search
│   │   ├── schemas.py           # Pydantic schemas
│   │   └── config.py            # Configuration
│   ├── requirements.txt
│   └── Dockerfile
├── data/
│   └── init.sql                 # Database initialization
├── workflows/
│   └── assignment_analysis_workflow.json  # n8n workflow
├── docker-compose.yml
└── README.md
```

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Register new student
- `POST /auth/login` - Login and get JWT token

### Assignment Management
- `POST /upload` - Upload assignment file (secured)
- `GET /analysis/{id}` - Get analysis results
- `GET /sources` - Search academic sources

## 🗃️ Database Schema

### Core Tables
- **students** - User accounts and profiles
- **assignments** - Uploaded assignment files and metadata
- **analysis_results** - AI analysis and plagiarism detection results
- **academic_sources** - Research papers with vector embeddings

## 🔍 RAG Pipeline

The system implements a sophisticated RAG (Retrieval Augmented Generation) pipeline:

1. **Document Ingestion** - Academic papers processed and embedded
2. **Query Processing** - Assignment text converted to embeddings
3. **Semantic Search** - Vector similarity search across papers
4. **Context Retrieval** - Most relevant sources returned
5. **AI Analysis** - Structured analysis using retrieved context

## 🔒 Security Features

- JWT-based authentication with 30-minute expiration
- BCrypt password hashing
- File type validation (PDF, DOCX, DOC, TXT)
- Student-specific data access control
- Secure environment variable management

## 🚀 Deployment

### Production Deployment
```bash
# Build and start all services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Development Mode
```bash
# Start with hot reload
docker-compose up -d postgres n8n
cd backend && uvicorn app.main:app --reload
```

## 🧪 Testing

### 1. Register a Student
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@university.edu",
    "password": "test123",
    "full_name": "Test Student",
    "student_id": "TEST001"
  }'
```

### 2. Login and Get Token
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=test@university.edu&password=test123"
```

### 3. Upload Assignment
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@sample_assignment.txt"
```

## 📊 n8n Workflow

The system includes an automated n8n workflow that processes assignments through:

1. **Webhook Trigger** - Receives assignment data from FastAPI
2. **Text Extraction** - Simulates PDF/DOCX content extraction
3. **RAG Source Search** - Queries vector database for relevant papers
4. **AI Analysis** - Analyzes content and generates recommendations
5. **Plagiarism Detection** - Checks for similarity with academic sources
6. **Results Storage** - Saves analysis to database
7. **Notifications** - Simulates email and Slack alerts

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings | Required |
| `JWT_SECRET_KEY` | Secret for JWT token signing | Required |
| `DATABASE_URL` | PostgreSQL connection string | Auto-generated |
| `N8N_WEBHOOK_URL` | n8n webhook endpoint | http://n8n:5678/webhook/assignment |

### Database Initialization
The database is automatically initialized with:
- Sample academic papers on education technology
- Vector embeddings for semantic search
- Optimized indexes for performance

## 🐛 Troubleshooting

### Common Issues

1. **n8n workflow not triggering**
   - Check if workflow is active in n8n UI
   - Verify webhook URL in environment variables

2. **Database connection issues**
   - Ensure PostgreSQL container is running
   - Check database logs: `docker-compose logs postgres`

3. **OpenAI API errors**
   - Verify API key in .env file
   - Check quota and billing status

### Logs and Monitoring
```bash
# View all service logs
docker-compose logs -f

# Check specific service
docker-compose logs -f backend
docker-compose logs -f n8n

# Database status
docker-compose exec postgres psql -U student -d academic_helper -c "\dt"
```

## 📈 Performance

- Vector similarity search optimized with IVFFlat indexing
- Async request handling in FastAPI
- Connection pooling for database
- Efficient embedding generation and caching


## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check API documentation at http://localhost:8000/docs
- Review n8n workflow at http://localhost:5678

## 🎯 Demo Video

A 5-minute demo video is available demonstrating:
- Student registration and authentication
- Assignment upload and processing
- RAG-based source suggestions
- Plagiarism detection results
- n8n workflow execution
- Database storage verification

---
