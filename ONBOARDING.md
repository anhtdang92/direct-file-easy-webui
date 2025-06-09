# Prism Tax Assistant - Onboarding Guide

## Project Overview
Prism Tax Assistant is an AI-powered tax preparation platform that helps users file their taxes accurately and efficiently. The platform uses advanced AI models to analyze tax documents, provide personalized tax advice, and ensure compliance with tax regulations.

## Project Structure
```
direct-file-easy-webui/
├── frontend/           # React frontend application
│   ├── src/           # Source code
│   │   ├── components/    # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   ├── utils/        # Utility functions
│   │   └── styles/       # CSS/SCSS files
│   ├── public/        # Static assets
│   └── package.json   # Frontend dependencies
├── backend/           # Express.js backend server
│   ├── src/          # Source code
│   │   ├── controllers/  # Route controllers
│   │   ├── models/       # Data models
│   │   ├── routes/       # API routes
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utility functions
│   ├── tests/        # Backend tests
│   └── package.json  # Backend dependencies
├── ai_service/        # AI service implementation
│   ├── src/          # Source code
│   │   ├── models/       # AI models
│   │   ├── processors/   # Document processors
│   │   ├── services/     # AI services
│   │   └── utils/        # Utility functions
│   ├── tests/        # AI service tests
│   └── requirements.txt # Python dependencies
├── ai-tax-filer/      # Tax filing AI components
│   ├── src/          # Source code
│   │   ├── analyzers/    # Tax analyzers
│   │   ├── validators/   # Tax validators
│   │   └── processors/   # Tax processors
│   └── tests/        # AI tax filer tests
├── direct-file/       # Core tax filing components
│   ├── src/          # Source code
│   │   ├── forms/        # Tax forms
│   │   ├── validators/   # Form validators
│   │   └── processors/   # Form processors
│   └── tests/        # Core component tests
├── docs/             # Project documentation
│   ├── api/          # API documentation
│   ├── guides/       # User guides
│   └── architecture/ # Architecture diagrams
├── venv/             # Python virtual environment
├── .pytest_cache/    # Python test cache
├── .git/             # Version control
├── .gitignore        # Git ignore rules
├── LICENSE           # MIT License
├── ONBOARDING.md     # Setup and development guide
├── PROJECT_PLAN.md   # Project roadmap and architecture
└── README.md         # Project overview
```

## Prerequisites
- Python 3.8+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Git
- Docker (optional)

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/prism-tax-assistant.git
cd prism-tax-assistant
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. AI Service Setup
```bash
cd ai_service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Setup

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/prism
REDIS_URL=redis://localhost:6379
JWT_SECRET=your_jwt_secret
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### AI Service (.env)
```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/prism
```

## Database Setup
```bash
cd backend
alembic upgrade head
```

## IRS Data Setup
```bash
cd ai_service
python scripts/setup_irs_data.py
```

## API Documentation

### Frontend API
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/documents` - List user documents
- `POST /api/documents/upload` - Upload tax document
- `GET /api/documents/{id}` - Get document details
- `POST /api/analysis` - Analyze tax documents
- `GET /api/export/formats` - Get supported export formats
- `POST /api/export/{format}` - Export tax data
- `GET /api/usage` - Get current usage statistics
- `POST /api/chat/start` - Start tax filing conversation
- `POST /api/chat/message` - Send message to tax assistant
- `GET /api/chat/history` - Get conversation history

### Backend API
- `GET /api/tax-code` - Get tax code sections
- `GET /api/publications` - Get IRS publications
- `POST /api/validate` - Validate tax data
- `GET /api/export/history` - Get export history
- `POST /api/export/validate` - Validate export format
- `GET /api/chat/state` - Get conversation state
- `POST /api/chat/process` - Process user response

### AI Service API
- `POST /api/ai/analyze` - Analyze tax documents
- `POST /api/ai/validate` - Validate tax data
- `POST /api/ai/export/validate` - Validate export data
- `POST /api/ai/export/optimize` - Optimize export format
- `POST /api/ai/chat/process` - Process chat message
- `POST /api/ai/chat/validate` - Validate chat input

## Security Best Practices
1. **API Key Management**
   - Store API keys securely
   - Rotate keys regularly
   - Monitor key usage
   - Implement rate limiting

2. **Data Security**
   - Encrypt sensitive data
   - Implement access controls
   - Regular security audits
   - Monitor data access

3. **User Authentication**
   - Implement JWT authentication
   - Use secure password hashing
   - Enable MFA
   - Session management

4. **Compliance**
   - Follow tax regulations
   - Implement data retention
   - Privacy policy
   - Terms of service

## Development Workflow
1. Create feature branch
2. Implement changes
3. Write tests
4. Submit PR
5. Code review
6. Merge to main

## Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# AI Service tests
cd ai_service
pytest
```

## Deployment
```bash
# Backend deployment
cd backend
docker build -t prism-backend .
docker run -p 8000:8000 prism-backend

# Frontend deployment
cd frontend
npm run build
docker build -t prism-frontend .
docker run -p 3000:3000 prism-frontend

# AI Service deployment
cd ai_service
docker build -t prism-ai .
docker run -p 8001:8001 prism-ai
```

## Monitoring
- API usage tracking
- Error monitoring
- Performance metrics
- User analytics
- Cost monitoring
- Export statistics
- Chat metrics

## Support
- Documentation
- FAQ
- Issue tracking
- Feature requests
- Bug reports
- Chat support
- Email support

## Export Options
- TurboTax export
- H&R Block export
- TaxAct export
- IRS e-file format
- Printable tax forms
- Custom reports

## Chat Interface
- Natural language processing
- Context tracking
- Form collection
- Real-time validation
- Progress tracking
- Voice input
- Accessibility features

## Next Steps
1. Set up development environment
2. Configure API keys
3. Initialize database
4. Start development server
5. Begin implementation
6. Test features
7. Deploy changes
8. Monitor performance
9. Gather feedback
10. Iterate improvements


