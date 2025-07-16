# Technology Stack

## Backend

- **Framework**: Django 5.2 with Django REST Framework 3.15.2
- **Database**: PostgreSQL with psycopg2-binary
- **Authentication**: Django's built-in auth with custom User model
- **API**: RESTful APIs with DRF, CORS enabled for frontend communication
- **WebSockets**: Django Channels with Redis for real-time features
- **Background Tasks**: Celery 5.5.3 with Redis broker and django-celery-beat for scheduling
- **Package Management**: uv for fast Python package installation

## Frontend

- **Framework**: Vue.js 3.5.13 with Composition API
- **State Management**: Pinia 2.3.1 for centralized store
- **Routing**: Vue Router 4.5.0
- **Build Tool**: Vite 6.0.11 with hot reload
- **UI Components**: Custom components with Lucide Vue Next icons
- **Drag & Drop**: vuedraggable 4.1.0
- **Calendar**: FullCalendar 6.1.17 for calendar views
- **HTTP Client**: Axios 1.4.0 for API communication

## Infrastructure

- **Web Server**: Uvicorn ASGI server for development
- **Cache/Message Broker**: Redis for Celery and Django Channels
- **Development**: Hot reload for both frontend and backend

## Development Tools

- **Code Quality**: ESLint, Prettier, Ruff (Python linter)
- **Testing**: pytest with pytest-django and pytest-cov
- **Debugging**: ipdb for Python debugging
- **Monitoring**: Sentry SDK for error tracking

## Common Commands

### Development Setup

```bash
# Start backend server (from root directory)
cd backend
uvicorn backend.asgi:application --reload --env-file ../.env --log-level info

# Start frontend development server (from root directory)
cd frontend-vue
npm run dev
```

### Backend Commands

```bash
# Run Django migrations (from backend/ directory)
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Run tests
python manage.py test

# Start Celery worker (from backend/ directory)
celery -A backend worker --loglevel=info

# Start Celery beat scheduler (from backend/ directory)
celery -A backend beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Frontend Commands

```bash
# Development server (from frontend-vue/ directory)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Database Operations

```bash
# Access PostgreSQL (requires local PostgreSQL installation)
psql -U [username] -d [database_name]
```
