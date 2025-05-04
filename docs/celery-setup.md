# Celery and Celery Beat Setup

## Overview

This document outlines the Celery and Celery Beat configuration in the Focus Timer project. Celery is used for handling asynchronous tasks and scheduled jobs, which is essential for features like recurring task generation.

## Dependencies

The project uses the following Celery-related packages:

- `celery`: The core Celery package for task processing
- `django-celery-results`: For storing task results in the Django database
- `django-celery-beat`: For managing periodic tasks through the Django admin interface
- `redis`: Used as the message broker for Celery

These dependencies are listed in the `backend/requirements.txt` file.

## Configuration

### Celery Initialization

Celery is initialized in the `backend/backend/celery.py` file:

```python
import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
```

This configuration is imported in the `backend/backend/__init__.py` file to ensure Celery is loaded when Django starts:

```python
from .celery import app as celery_app

__all__ = ("celery_app",)
```

### Django Settings

The Celery-specific settings are defined in `backend/backend/settings.py`:

```python
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
```

The required apps are also included in the `INSTALLED_APPS` setting:

```python
THIRD_PARTY_APPS = [
    # ... other apps
    "django_celery_results",
    "django_celery_beat",
    # ... other apps
]
```

## Tasks

The project currently has the following Celery tasks defined:

### Recurring Task Generation

Located in `backend/apps/core/tasks.py`, this task generates recurring tasks based on recurrence rules:

```python
@app.task(name="generate_recurring_tasks")
def generate_recurring_tasks():
    """
    Runs every 12 hours. For each "template" task (recurrence_rule set,
    recurrence_parent is null), parse the rule, find the next up-to-5
    occurrences after now (that haven't already been cloned), and create them.
    """
    print("Generating recurring tasks...")

    # 1) Grab only the *original* recurring tasks (no parents, with an RRULE)
    templates_tasks = Task.objects.filter(
        recurrence_rule__isnull=False,
        recurrence_parent__isnull=True,
    )

    for parent in templates_tasks:
        gen_rec_tasks_for_parent(parent)
    return "done"
```

This task uses helper functions to generate child tasks based on recurrence rules defined in parent tasks.

## Running Celery

To run Celery workers and beat scheduler in development:

1. Start Redis (message broker):
   ```
   redis-server
   ```

2. Start Celery worker:
   ```
   cd backend
   celery -A backend worker -l info
   ```

3. Start Celery beat scheduler:
   ```
   cd backend
    celery -A backend beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
   ```

## Scheduling Tasks

Tasks can be scheduled in two ways:

1. **Django Admin Interface**: Using the django-celery-beat admin interface to create and manage periodic tasks.

2. **Programmatically**: By creating `PeriodicTask` objects in the database.

## Monitoring

Celery task results are stored in the database using the django-celery-results backend, which allows for monitoring task execution through the Django admin interface.

## Best Practices

1. Keep tasks small and focused on a single responsibility
2. Use proper error handling in tasks
3. Avoid sharing state between tasks
4. Use task timeouts to prevent hanging tasks
5. Monitor task execution and performance

## Future Improvements

- Implement task monitoring with Flower or similar tools
- Add task retries with exponential backoff
- add more debug info like logging

