# Setup Guide

## PostgreSQL Setup

Ensure PostgreSQL is installed and running.

1. Connect to the default `postgres` database:

```bash
psql -U postgres
# on ubuntu
sudo -u postgres psql
```

2. Create the project database and user:

```sql
CREATE ROLE focus_timer_user
  WITH LOGIN
       PASSWORD 'your_strong_password'
       CREATEDB    -- needed so test runner can CREATE/DROP the test DB
       NOCREATEROLE  -- this user will not be able to create another user
       NOSUPERUSER;
CREATE DATABASE focus_timer_django_vue_db 
  OWNER = focus_timer_user;

-- Grant the minimal CONNECT/TEMP/USAGE/CREATE rights on that DB & schema:
\c focus_timer_django_vue_db focus_timer_user

GRANT CONNECT
  ON DATABASE focus_timer_django_vue_db 
  TO focus_timer_user;

GRANT TEMP
  ON DATABASE focus_timer_django_vue_db 
  TO focus_timer_user;

GRANT USAGE
  ON SCHEMA public
  TO focus_timer_user;

GRANT CREATE
  ON SCHEMA public
  TO focus_timer_user;
```

3. Exit the shell:

```bash
\q
```

## Test Connection

```bash
psql -h 127.0.0.1 -p 5432 -U focus_timer_user -d focus_timer_django_vue_db 
