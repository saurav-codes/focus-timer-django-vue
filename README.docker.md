# Docker Setup for Focus Timer

This Docker setup simulates the production environment locally with all the required services.

## Prerequisites

1. **Docker & Docker Compose**: Make sure you have Docker and Docker Compose installed
2. **Environment File**: You must have a `.env` file in the root directory

## Quick Start

### 1. Create Environment File

```bash
# Copy the sample environment file
cp .env.docker .env

# Or if you already have .env.sample
cp .env.sample .env
```

**Important**: The Docker setup will NOT run without a `.env` file in the root directory.

### 2. Development Mode (Backend + Frontend Dev Server)

```bash
# Start backend services + frontend development server
docker-compose --profile dev up

# Or run in detached mode
docker-compose --profile dev up -d
```

This will start:
- ✅ PostgreSQL database (port 5432)
- ✅ Redis (port 6379)
- ✅ Django backend with Uvicorn (port 8000)
- ✅ Celery worker
- ✅ Celery beat scheduler
- ✅ Frontend dev server with hot reload (port 5173)

Access the application:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin (admin@example.com / admin123)

### 3. Production Mode (Full Production Simulation)

```bash
# Build and start all services including Nginx
docker-compose --profile prod up --build

# Or run in detached mode
docker-compose --profile prod up -d --build
```

This will start:
- ✅ PostgreSQL database
- ✅ Redis
- ✅ Django backend with Uvicorn
- ✅ Celery worker
- ✅ Celery beat scheduler
- ✅ Frontend production build
- ✅ Nginx reverse proxy (port 80)

Access the application:
- **Full Application**: http://localhost (served by Nginx)
- **Backend API**: http://localhost/api/
- **Django Admin**: http://localhost/admin/

## Useful Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f postgres

# Follow logs for development
docker-compose --profile dev logs -f
```

### Database Operations
```bash
# Run Django migrations
docker-compose exec backend python manage.py migrate

# Create Django superuser
docker-compose exec backend python manage.py createsuperuser

# Access Django shell
docker-compose exec backend python manage.py shell

# Access PostgreSQL
docker-compose exec postgres psql -U focus_timer_user -d focus_timer_db
```

### Rebuild Services
```bash
# Rebuild specific service
docker-compose build backend

# Rebuild and restart
docker-compose up --build backend

# Force rebuild without cache
docker-compose build --no-cache backend
```

### Clean Up
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ this will delete your database data)
docker-compose down -v

# Clean up Docker system
docker system prune -a
```

## Service Details

### Backend (Django + Uvicorn)
- **Port**: 8000
- **Features**: Auto-migrations, static file collection, auto-superuser creation
- **WebSocket**: Enabled for real-time features
- **Package Manager**: Uses `uv` for fast Python package installation

### Database (PostgreSQL)
- **Port**: 5432
- **Persistence**: Data persists in Docker volume `postgres_data`
- **Credentials**: See `.env` file

### Redis
- **Port**: 6379
- **Usage**: Celery broker and result backend
- **Persistence**: Data persists in Docker volume `redis_data`

### Frontend Development
- **Port**: 5173
- **Features**: Hot reload, volume mounting for real-time changes
- **API URL**: Configured to connect to backend at `http://localhost:8000`

### Frontend Production
- **Served by**: Nginx
- **Build**: Optimized production build
- **Features**: Gzip compression, caching headers

### Nginx (Production Mode Only)
- **Port**: 80
- **Features**:
  - Reverse proxy to Django backend
  - WebSocket proxy for Django Channels
  - Static file serving
  - Security headers
  - Gzip compression

## Environment Variables

Key environment variables for Docker:

```bash
# Database
DATABASE_HOST=postgres          # Uses Docker service name
DATABASE_NAME=focus_timer_db
DATABASE_USER=focus_timer_user
DATABASE_PASSWORD=focus_timer_password

# Redis
REDIS_CONNECTION_URL=redis://:StrongRedisPassw0rd@redis:6379/0

# Django
ALLOWED_HOSTS=localhost,127.0.0.1,backend
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:80
```

## Troubleshooting

### "No .env file found"
Make sure you have a `.env` file in the root directory:
```bash
cp .env.docker .env
```

### Database Connection Issues
```bash
# Check if PostgreSQL is healthy
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Permission Issues
```bash
# Fix permission issues (if any)
sudo chown -R $USER:$USER .
```

### Port Conflicts
If you have services running on the same ports:
```bash
# Check what's using the port
lsof -i :8000
lsof -i :5432

# Stop conflicting services or change ports in docker-compose.yml
```

## Development Workflow

1. **Start Development Environment**:
   ```bash
   docker-compose --profile dev up -d
   ```

2. **Make Changes**: Edit your code normally - changes will be reflected immediately
   - Backend: Auto-reload enabled in uvicorn
   - Frontend: Hot reload enabled in Vite

3. **Run Tests** (when implemented):
   ```bash
   docker-compose exec backend python manage.py test
   ```

4. **Test Production Build**:
   ```bash
   docker-compose --profile prod up --build
   ```

5. **Clean Up**:
   ```bash
   docker-compose down
   ```

## Performance Tips

- **Use `uv`**: Python packages install much faster with `uv`
- **Layer Caching**: Requirements are copied before source code for better Docker layer caching
- **Volume Mounting**: Source code is mounted for development, so no rebuilds needed for code changes
- **Health Checks**: Services wait for dependencies to be healthy before starting
