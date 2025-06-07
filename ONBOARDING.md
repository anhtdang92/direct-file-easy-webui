# Prism - AI-Powered Tax Assistance Platform

## Project Overview
Prism is an open-source platform that helps users understand and optimize their taxes. It combines AI-powered document analysis with IRS tax code integration to provide accurate and up-to-date tax assistance.

## Prerequisites
- Node.js 18+
- Python 3.8+
- PostgreSQL 15+
- Redis 7+
- Git
- OpenAI API key (for AI features)
- IRS API access (for tax code integration)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/prism.git
cd prism
```

### 2. Install Dependencies

#### Frontend
```bash
cd frontend
npm install
```

#### Backend
```bash
cd backend
npm install
```

#### AI Service
```bash
cd ai_service
pip install -r requirements.txt
```

### 3. Environment Setup

#### Frontend (.env)
```
VITE_API_URL=http://localhost:3000
VITE_WS_URL=ws://localhost:3000
```

#### Backend (.env)
```
PORT=3000
DATABASE_URL=postgresql://user:password@localhost:5432/prism
REDIS_URL=redis://localhost:6379
JWT_SECRET=your_jwt_secret
OPENAI_API_KEY=your_openai_api_key
IRS_API_KEY=your_irs_api_key
```

#### AI Service (.env)
```
OPENAI_API_KEY=your_openai_api_key
IRS_API_KEY=your_irs_api_key
MODEL_PATH=./models
CACHE_DIR=./cache
```

### 4. Database Setup
```bash
cd backend
npm run migrate
```

### 5. IRS Data Setup
```bash
cd ai_service
python scripts/setup_irs_data.py
```

## Development Workflow

### 1. Start Development Servers

#### Frontend
```bash
cd frontend
npm run dev
```

#### Backend
```bash
cd backend
npm run dev
```

#### AI Service
```bash
cd ai_service
python app.py
```

### 2. Running Tests
```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
npm test

# AI service tests
cd ai_service
pytest

# IRS data tests
cd ai_service
pytest tests/test_irs_integration.py
```

### 3. Code Quality
```bash
# Frontend
cd frontend
npm run lint
npm run format

# Backend
cd backend
npm run lint
npm run format

# AI Service
cd ai_service
flake8
black .
```

## Project Structure
```
prism/
├── frontend/           # React frontend
├── backend/           # Node.js backend
├── ai_service/        # Python AI service
│   ├── models/        # ML models
│   ├── utils/         # Utility functions
│   │   ├── tax_code_service.py
│   │   └── irs_publication_service.py
│   └── cache/         # IRS data cache
└── docs/             # Documentation
```

## API Documentation

### Frontend API
- `POST /api/documents/upload` - Upload tax documents
- `GET /api/documents/:id` - Get document details
- `GET /api/analysis/:id` - Get analysis results
- `GET /api/tax-code/:section` - Get tax code section
- `GET /api/publications/:id` - Get IRS publication

### Backend API
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/settings` - Update user settings
- `GET /api/subscription/plans` - Get subscription plans

### AI Service API
- `POST /api/ai/analyze` - Analyze document
- `POST /api/ai/suggest` - Get tax suggestions
- `POST /api/ai/explain` - Explain tax concepts
- `GET /api/ai/tax-code` - Get tax code data
- `GET /api/ai/publications` - Get IRS publications

## IRS Data Integration

### Tax Code Service
```python
from utils.tax_code_service import TaxCodeService

# Initialize service
tax_service = TaxCodeService()

# Fetch specific section
section = tax_service.get_section("26 USC 1")

# Search tax code
results = tax_service.search("capital gains")

# Get updates
updates = tax_service.get_updates_since("2023-01-01")
```

### Publication Service
```python
from utils.irs_publication_service import IRSPublicationService

# Initialize service
pub_service = IRSPublicationService()

# Fetch publication
pub = pub_service.fetch_publication("17")

# Search publications
results = pub_service.search("business expenses")

# Get related publications
related = pub_service.get_related_publications("17")
```

## Troubleshooting

### Common Issues

1. **Database Connection**
   - Check PostgreSQL is running
   - Verify connection string
   - Check user permissions

2. **AI Service Issues**
   - Verify API keys
   - Check model files
   - Monitor memory usage

3. **IRS Data Issues**
   - Check API key validity
   - Verify cache directory
   - Monitor update status

4. **Frontend Issues**
   - Clear browser cache
   - Check API endpoints
   - Verify environment variables

### Debugging Tools

1. **Backend**
   - Node.js debugger
   - PostgreSQL logs
   - Redis monitor

2. **AI Service**
   - Python debugger
   - Model logs
   - IRS data logs

3. **Frontend**
   - React DevTools
   - Network tab
   - Console logs

## Contributing

### Code Style
- Follow ESLint rules
- Use Prettier formatting
- Write unit tests
- Document changes

### Git Workflow
1. Create feature branch
2. Make changes
3. Run tests
4. Submit PR
5. Code review
6. Merge to main

### Documentation
- Update README
- Document API changes
- Add code comments
- Update IRS data docs

## Security

### Best Practices
- Use environment variables
- Encrypt sensitive data
- Validate user input
- Follow IRS guidelines

### API Security
- Rate limiting
- Input validation
- Error handling
- Token management

### Data Security
- Encryption at rest
- Secure transmission
- Regular backups
- Access control

## Performance

### Optimization
- Cache IRS data
- Optimize queries
- Use indexes
- Monitor memory

### Monitoring
- Track API usage
- Monitor errors
- Check performance
- Watch IRS updates

## Deployment

### Production Setup
1. Configure servers
2. Set up databases
3. Deploy services
4. Configure SSL
5. Set up monitoring

### CI/CD
- GitHub Actions
- Automated tests
- Deployment checks
- IRS data updates

## Support

### Getting Help
- Check documentation
- Search issues
- Join community
- Contact support

### Maintenance
- Regular updates
- Security patches
- IRS data sync
- Performance tuning


