#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_error() {
    echo -e "${RED}❌ Error: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found!"
    echo
    print_info "You need to create a .env file before running Docker Compose."
    echo
    echo "Options:"
    echo "1. Copy from sample: cp .env.docker .env"
    echo "2. Copy from existing: cp .env.sample .env"
    echo
    print_warning "Please create .env file and try again."
    exit 1
fi

print_success ".env file found!"

# Parse command line arguments
PROFILE="dev"
DETACHED=""
BUILD=""
EXTRA_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --prod|--production)
            PROFILE="prod"
            shift
            ;;
        -d|--detach)
            DETACHED="-d"
            shift
            ;;
        --build)
            BUILD="--build"
            shift
            ;;
        *)
            EXTRA_ARGS="$EXTRA_ARGS $1"
            shift
            ;;
    esac
done

# Display what we're about to run
echo
if [ "$PROFILE" = "prod" ]; then
    print_info "Starting PRODUCTION mode (with Nginx reverse proxy)"
    print_info "Access: http://localhost"
else
    print_info "Starting DEVELOPMENT mode (frontend dev server)"
    print_info "Frontend: http://localhost:5173"
    print_info "Backend: http://localhost:8000"
fi

echo
print_info "Profile: $PROFILE"
[ ! -z "$DETACHED" ] && print_info "Mode: Detached (background)"
[ ! -z "$BUILD" ] && print_info "Build: Rebuilding images"

echo
print_warning "Starting Docker Compose..."

# Run Docker Compose
docker-compose --profile $PROFILE up $DETACHED $BUILD $EXTRA_ARGS

# If not detached, show helpful info when it exits
if [ -z "$DETACHED" ]; then
    echo
    print_info "Docker Compose stopped."
    print_info "To clean up: docker-compose down"
    print_info "To clean up with volumes: docker-compose down -v"
fi
