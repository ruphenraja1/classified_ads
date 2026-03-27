# Varivilambarangal - Classifieds Platform

A full-stack classifieds platform built with Django REST Framework backend and Next.js React frontend.

## Project Structure

```
varivilambarangal-dev/
├── backend/                # Django REST API backend
│   ├── config/            # Django project settings
│   ├── apps/              # Django apps (business logic)
│   ├── api/               # REST API layer (/api/v1/)
│   ├── views/             # Django template views (/employee/)
│   ├── scripts/           # Utility scripts
│   ├── tests/             # Test scripts
│   ├── debug/             # Debug utilities
│   └── ...
├── frontend/              # Next.js React frontend
│   ├── src/               # React source code
│   ├── public/            # Static assets
│   ├── package.json       # Frontend dependencies
│   └── ...
├── .env                   # Environment variables
├── .env.prod.example      # Production env template
└── README.md              # This file
```

## Tech Stack

### Backend
- **Framework**: Django 4.2
- **API**: Django REST Framework
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Authentication**: Django auth
- **File Uploads**: Django media handling

### Frontend
- **Framework**: Next.js 16.1.1
- **React**: 19.2.3
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Linting**: ESLint

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (for production)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Start development server**:
   ```bash
   python manage.py runserver
   ```

Backend will be available at: http://localhost:8000

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

Frontend will be available at: http://localhost:3000

## API Endpoints

- **REST API**: `http://localhost:8000/api/v1/`
- **Admin Interface**: `http://localhost:8000/employee/`

## Development

### Running Tests
```bash
# Backend tests
cd backend && python manage.py test

# Frontend linting
cd frontend && npm run lint
```

### Building for Production
```bash
# Backend
cd backend && python manage.py collectstatic

# Frontend
cd frontend && npm run build
```

## Environment Variables

Copy `.env.prod.example` to `.env` and configure:

- Database settings
- Secret keys
- API endpoints
- File upload paths

## Deployment

The application is designed to work with:
- Docker containers
- Cloud platforms (AWS, GCP, Azure)
- Traditional web servers

## Contributing

1. Follow the established project structure
2. Write tests for new features
3. Update documentation as needed
4. Ensure code passes linting

## License

This project is private and proprietary.
