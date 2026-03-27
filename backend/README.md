# Backend Directory Structure

This directory contains the Django backend application with a clean, organized structure.

## Directory Structure

```
backend/
├── .env                    # Environment variables
├── .venv/                  # Python virtual environment
├── api/                    # REST API layer (/api/v1/)
├── apps/                   # Django apps (business logic & models)
├── config/                 # Django project settings
├── debug/                  # Debug utilities and scripts
├── LLM_Model/             # Language model files
├── scripts/               # Utility scripts and custom functionalities
├── tests/                 # Test scripts
├── views/                 # Django template views (/employee/)
├── db.sqlite3            # SQLite database (development)
├── manage.py             # Django management script
└── requirements.txt      # Python dependencies
```

## Key Components

- **config/**: Django project configuration (renamed from classifieds/)
- **apps/ads/**: Main Django app with models, business logic, and shared functionality
- **api/v1/**: REST API endpoints using Django REST Framework
- **views/**: Django template views for admin interface
- **scripts/**: Utility scripts for data import, verification, and custom operations
- **tests/**: Test scripts for backend validation
- **debug/**: Debugging utilities for development

## Getting Started

1. Activate virtual environment:
   ```bash
   .venv\Scripts\activate  # Windows
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. Start development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

- REST API: `/api/v1/`
- Admin Views: `/employee/`

## Scripts

Utility scripts are located in `scripts/` and can be run as needed for data operations.