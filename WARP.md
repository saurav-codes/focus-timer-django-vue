# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a full-stack productivity application (Sunsama clone) built with Django backend and Vue.js 3 frontend. It features Kanban board and calendar views for task management with drag-and-drop functionality, real-time updates via WebSockets, and background processing with Celery.

## Development Commands

### Backend (Django)
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run tests
pytest

# Run single test file
pytest apps/core/tests.py

# Run specific test
pytest apps/core/tests.py::TestTaskModel::test_task_creation

# Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic
```

### Frontend (Vue.js)
```bash
# Navigate to frontend directory
cd frontend-vue

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Background Services
```bash
# Redis (required for Celery)
redis-server

# Celery worker (from backend directory)
celery -A backend worker --loglevel=info

# Celery beat scheduler (from backend directory)
celery -A backend beat --loglevel=info

# Monitor Celery tasks
celery -A backend flower
```

## Architecture Overview

### Backend Structure
- **`backend/apps/core/`** - Main task management logic and models
- **`backend/apps/authentication/`** - Custom user authentication with timezone support
- **`backend/apps/integrations/`** - External service integrations (Google Calendar, Gmail, GitHub)
- **`backend/backend/`** - Django project configuration, settings, ASGI, and Celery setup

### Frontend Structure
- **`frontend-vue/src/views/`** - Page-level components (KanbanPlanner, CalendarPlanner, Dashboard, Settings)
- **`frontend-vue/src/components/`** - Reusable Vue components (TaskCard, KanbanColumn, CalendarComponent)
- **`frontend-vue/src/stores/`** - Pinia state management stores
- **`frontend-vue/src/composables/`** - Reusable composition functions
- **`frontend-vue/src/router/`** - Vue Router configuration

### Key Models
- **Task** - Central entity with status (BRAINDUMP, ON_BOARD, ON_CAL, COMPLETED), duration, start/end times
- **Project** - Task organization
- **RecurrenceSeries** - Recurring task patterns using RRULE RFC-5545
- **User** - Custom authentication model with timezone support

### State Management Architecture
- **API Stores** - Handle REST API communication (`taskStoreApi`)
- **WebSocket Stores** - Real-time updates (`taskStoreWs`)
- **UI Stores** - Interface state management (`uiStore`)
- **Auth Store** - Authentication state (`authStore`)

## Development Patterns

### Django Backend Patterns
- **Layered Architecture**: models → selectors → services → views
- **File Organization**:
  - `models.py` - Database models only
  - `selectors.py` - Database queries and data retrieval
  - `services.py` - Business logic and data manipulation
  - `views.py` - API endpoints using Django REST Framework
  - `tasks.py` - Celery background tasks
  - `consumers.py` - WebSocket handlers

### Vue Frontend Patterns
- **Composition API** - Use `<script setup>` syntax
- **Component Naming** - PascalCase for components, camelCase for variables/functions
- **State Management** - Pinia stores for centralized state
- **Real-time Updates** - WebSocket integration for live data synchronization

### API Endpoints
- **Tasks**: `/api/tasks/` (full CRUD operations)
- **Authentication**: `/auth/` (login, register, logout)
- **Integrations**: `/api/gcalendar/`, `/api/gmail/`, `/api/github/`

## Environment Setup

### Required Environment Variables
Copy `.env.sample` to `.env` and configure:
- `DATABASE_*` - PostgreSQL connection settings
- `REDIS_CONNECTION_URL` - Redis for Celery message broker
- `GOOGLE_CLIENT_*` - Google API integration credentials
- `CORS_ALLOWED_ORIGINS` - Frontend URL for CORS
- `SECRET_KEY` - Django secret key
- `DEBUG` - Development mode flag

### Services Required
- **PostgreSQL** - Primary database
- **Redis** - Message broker for Celery and caching
- **Celery Worker + Beat** - Background task processing and scheduling

## Key Features Implementation

### Task Management
- **Dual View System**: Kanban-focused and Calendar-focused layouts
- **Drag & Drop**: Between columns and to/from calendar
- **Task Creation**: Popup modal with 'a' keyboard shortcut
- **Real-time Updates**: WebSocket consumers for live synchronization

### Background Processing
- **Celery Tasks**: Recurring task generation, integrations processing
- **Scheduled Jobs**: Celery Beat for periodic tasks
- **Task Storage**: django-celery-results for execution tracking

### Integrations
- **Google Calendar**: Two-way sync with calendar events
- **Gmail**: Email integration for task creation
- **GitHub**: Repository and issue integration

## Testing Strategy
- **Backend**: pytest with Django test framework
- **API Testing**: DRF test cases for endpoints
- **Model Testing**: Unit tests for business logic
- **Integration Testing**: End-to-end workflow testing

## Code Quality Tools
- **Backend**: pre-commit hooks, ruff linting, djlint for templates
- **Frontend**: ESLint, Prettier formatting
- **Type Safety**: JSDoc comments in Vue components

## Cursor AI Rules Integration
Key principles from `.cursorrules`:
- Senior developer expertise in Django and Vue.js 3
- UI/UX focus with conversion-optimized design
- Security and privacy compliance priority
- Simple, optimal solutions over complex implementations
- Thorough codebase scanning before changes
- Comprehensive commenting for learning
- No git commits without explicit request

## Important Notes
- Custom User model with timezone support is required
- WebSocket connections handle real-time task updates
- Celery workers must be running for background tasks
- Redis is required for both Celery and WebSocket channels
- Frontend uses session-based authentication with CSRF protection
- Environment variables must be properly configured for integrations
