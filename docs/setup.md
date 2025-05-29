# Setup Guide

## PostgreSQL Setup

Ensure PostgreSQL is installed and running.

1. Connect to the default `postgres` database:

```bash
psql -U postgres
```

2. Create the project database and user:

```sql
CREATE DATABASE focus_timer_django_vue;
CREATE USER focus_timer_user WITH PASSWORD '7d2003ead892-any-uuid-str';
GRANT ALL PRIVILEGES ON DATABASE focus_timer_django_vue TO focus_timer_user;
```

3. Exit the shell:

```bash
\q
```

## Test Connection

```bash
psql -h 127.0.0.1 -p 5432 -U focus_timer_user -d focus_timer_django_vue
