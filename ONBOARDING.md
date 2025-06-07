# Onboarding
__Table of Contents__

1. [Quickstart](#quickstart)
2. [Codebase Overview](#codebase-overview)
3. [Local Environment Setup](#local-environment-setup)
4. [Development Workflow](#development-workflow)
5. [Testing](#testing)

# Quickstart
To run the application:

1. Start the backend server:
```bash
cd backend
npm install
npm run dev
```

2. Start the frontend development server:
```bash
cd frontend
npm install
npm run dev
```

The backend application is available at http://localhost:3001 and the frontend application is available at http://localhost:5173.

# Codebase Overview
The project consists of a React frontend and an Express.js backend. Here's a breakdown of the main components:

#### Frontend (`/frontend`)
- React application with TypeScript
- Vite for fast development
- Tailwind CSS for styling
- Form components for tax filing
- Wizard-based navigation

#### Backend (`/backend`)
- Express.js server
- RESTful API endpoints
- Winston logger for logging
- Data validation middleware

## Local Environment Setup

### Required Software

* Node.js (v18 or higher)
* npm (v8 or higher)
* Git

### Optional Software

* Visual Studio Code
* Postman (for API testing)

### Environment Variables

1. Backend (`.env` in `/backend`):
```
PORT=3001
NODE_ENV=development
```

2. Frontend (`.env` in `/frontend`):
```
VITE_API_URL=http://localhost:3001
```

## Development Workflow

1. **Starting Development**
   - Clone the repository
   - Install dependencies for both frontend and backend
   - Start both servers in development mode

2. **Making Changes**
   - Frontend changes will hot-reload
   - Backend changes will restart the server
   - Follow the coding standards in the project

3. **Testing**
   - Run frontend tests: `npm test` in `/frontend`
   - Run backend tests: `npm test` in `/backend`

4. **Building for Production**
   - Frontend: `npm run build` in `/frontend`
   - Backend: `npm run build` in `/backend`

## Testing

### Frontend Tests
- Unit tests for components
- Integration tests for forms
- E2E tests for user flows

### Backend Tests
- API endpoint tests
- Validation tests
- Logging tests

### Running Tests
```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
npm test
```

### Code Coverage
- Frontend coverage report: `npm run test:coverage` in `/frontend`
- Backend coverage report: `npm run test:coverage` in `/backend`


