---
inclusion: always
---

# Project Structure & Architecture Patterns

## Architecture Overview

This is a Django + Vue.js productivity application with clear separation between backend API and frontend SPA. Follow these patterns when working with the codebase.

## Directory Structure

### Backend (`backend/`)
- `apps/core/` - Main task management logic
- `apps/authentication/` - Custom user auth with timezone support
- `apps/integrations/` - External service integrations (Google Calendar)
- `backend/` - Django project configuration (settings, ASGI, Celery)

### Frontend (`frontend-vue/`)
- `src/components/` - Reusable Vue components (PascalCase naming)
- `src/views/` - Page-level components for routing
- `src/stores/` - Pinia state management (separate API and WebSocket stores)
- `src/composables/` - Reusable composition functions
- `src/utils/` - Pure utility functions

## Code Organization Patterns

### Django Backend
- **Layered Architecture**: models → selectors → services → views
- **models.py**: Database models only
- **selectors.py**: Database queries and data retrieval
- **services.py**: Business logic and data manipulation
- **views.py**: API endpoints using DRF
- **serializers.py**: Data serialization for API responses
- **tasks.py**: Celery background tasks
- **consumers.py**: WebSocket handlers

### Vue Frontend
- **Component Architecture**: Single-file components with Composition API
- **State Management**: Pinia stores for centralized state
- **Real-time Updates**: Separate WebSocket store for live data
- **Composables**: Reusable logic (useRecurrenceRule, useStartAt)

## Naming Conventions

- **Python**: snake_case for files, functions, variables
- **Vue.js**: PascalCase for components, camelCase for variables/functions
- **API URLs**: kebab-case endpoints
- **Database**: snake_case table and column names

## Import Patterns

### Django
```python
# Relative imports within same app
from .models import Task
from .selectors import get_user_tasks

# Absolute imports across apps
from apps.authentication.models import User
```

### Vue.js
```javascript
// Relative imports for local files
import TaskCard from '../components/TaskCard.vue'
import { useTaskStore } from '@/stores/taskStoreApi'
```

## Key Architecture Rules

1. **Backend**: Keep business logic in services, not views
2. **Frontend**: Use composables for reusable logic across components
3. **State**: Separate API calls (taskStoreApi) from WebSocket updates (taskStoreWs)
4. **Real-time**: Use WebSocket consumers for live updates, not polling
5. **Authentication**: Custom User model with timezone support required
6. **Tasks**: Use Celery for background processing (recurring tasks, integrations)
