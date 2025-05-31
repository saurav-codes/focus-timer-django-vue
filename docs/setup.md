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
-- above cmd only for mac local setup. -- for ubuntu, use the following cmd:
-- sudo vi /etc/postgresql/16/main/pg_hba.conf
-- and add the following line:
-- host    focus_timer_django_vue_db             focus_timer_user       127.0.0.1/32            md5
-- host    focus_timer_django_vue_db             focus_timer_user             ::1/128           md5
-- then restart the postgres service:
-- sudo service postgresql restart
-- then you will be able to connect to the database using the following command:
-- psql -h 127.0.0.1 -U focus_timer_user -d focus_timer_django_vue_db
-- now after connecting, let's grant the necessary permissions:
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
