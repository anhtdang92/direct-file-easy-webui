# AI Tax Filer - Onboarding Guide

## Prerequisites
- Node.js (v18 or higher)
- npm (v8 or higher)
- Git

## Project Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd direct-file-easy-webui
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The frontend will be available at http://localhost:5173

### 3. Backend Setup
```bash
cd backend
npm install
node src/index.js
```
The backend will be available at http://localhost:3001

## Project Structure
```
direct-file-easy-webui/
├── frontend/               # React frontend application
│   ├── src/               # Source files
│   ├── public/            # Static files
│   └── package.json       # Frontend dependencies
├── backend/               # Express backend application
│   ├── src/              # Source files
│   ├── logs/             # Log files
│   └── package.json      # Backend dependencies
└── docs/                 # Documentation
```

## Development Workflow

### Frontend Development
1. Start the development server:
   ```bash
   cd frontend
   npm run dev
   ```
2. The application will be available at http://localhost:5173
3. Changes will be hot-reloaded

### Backend Development
1. Start the backend server:
   ```bash
   cd backend
   node src/index.js
   ```
2. The API will be available at http://localhost:3001
3. Logs will be written to `backend/logs/tax-filer.log`

## Testing
- Frontend tests: `npm test` in the frontend directory
- Backend tests: `npm test` in the backend directory

## Available Scripts

### Frontend
- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run test`: Run tests
- `npm run lint`: Run linter
- `npm run format`: Format code

### Backend
- `node src/index.js`: Start server
- `npm test`: Run tests
- `npm run lint`: Run linter

## API Endpoints

### POST /api/logs
- Purpose: Log form submissions
- Request Body:
  ```json
  {
    "message": "Form submitted: {...}",
    "level": "info"
  }
  ```
- Response:
  ```json
  {
    "status": "logged",
    "entry": {
      "timestamp": "2025-06-07T16:34:08.206Z",
      "level": "info",
      "message": "Form submitted: {...}"
    }
  }
  ```

## Troubleshooting

### Common Issues
1. Port already in use:
   - Frontend: Change port in vite.config.ts
   - Backend: Change port in src/index.js

2. CORS issues:
   - Check backend CORS configuration
   - Verify frontend API URL

3. Logging issues:
   - Check logs directory permissions
   - Verify log file path

## Contributing
1. Create a new branch
2. Make changes
3. Run tests
4. Submit pull request

## Resources
- [React Documentation](https://reactjs.org/)
- [Express Documentation](https://expressjs.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [TypeScript Documentation](https://www.typescriptlang.org/)


