#!/bin/bash

# CIM Wizard Integrated - Application Startup Script
# This script provides different ways to start the FastAPI application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker container is running
check_database() {
    print_status "Checking database connection..."
    
    if ! sudo docker ps | grep -q "integrateddb"; then
        print_warning "Database container not running. Starting it..."
        sudo docker-compose -f docker-compose.db.yml up -d
        sleep 5
    else
        print_success "Database container is running"
    fi
    
    # Test database connection
    if python -c "import psycopg2; conn = psycopg2.connect('postgresql://cim_wizard_user:cim_wizard_password@localhost:5433/cim_wizard_integrated'); print('Database connection successful'); conn.close()" 2>/dev/null; then
        print_success "Database connection verified"
    else
        print_error "Database connection failed"
        exit 1
    fi
}

# Function to start application in development mode
start_development() {
    print_status "Starting application in development mode..."
    
    # Set development environment
    export ENV_FILE="env.development"
    
    # Start with auto-reload
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 --reload-exclude pgdata
}

# Function to start application in production mode
start_production() {
    print_status "Starting application in production mode..."
    
    # Set production environment
    export ENV_FILE="env.production"
    
    # Start without reload for production
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
}

# Function to start application in background
start_background() {
    print_status "Starting application in background..."
    
    # Kill any existing uvicorn processes
    pkill -f uvicorn 2>/dev/null || true
    
    # Start in background
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
    
    print_success "Application started in background. PID: $!"
    print_status "Logs are being written to app.log"
    print_status "You can check the logs with: tail -f app.log"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  dev, development    Start in development mode with auto-reload"
    echo "  prod, production    Start in production mode with multiple workers"
    echo "  bg, background      Start in background mode"
    echo "  stop                Stop the application"
    echo "  status              Show application status"
    echo "  logs                Show application logs"
    echo "  help                Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  You can override settings by setting environment variables:"
    echo "  - DATABASE_URL: Override database connection URL"
    echo "  - POSTGRES_HOST, POSTGRES_PORT, etc.: Individual database settings"
    echo "  - HOST, PORT: Server host and port"
    echo "  - DEBUG: Enable/disable debug mode"
    echo ""
    echo "Examples:"
    echo "  $0 dev                    # Start in development mode"
    echo "  $0 prod                   # Start in production mode"
    echo "  DATABASE_URL=... $0 dev   # Override database URL"
    echo "  PORT=9000 $0 dev          # Run on different port"
}

# Function to stop application
stop_application() {
    print_status "Stopping application..."
    
    if pkill -f uvicorn; then
        print_success "Application stopped"
    else
        print_warning "No application was running"
    fi
}

# Function to show status
show_status() {
    print_status "Application status:"
    
    if pgrep -f uvicorn > /dev/null; then
        print_success "Application is running"
        echo "Processes:"
        ps aux | grep uvicorn | grep -v grep
    else
        print_warning "Application is not running"
    fi
    
    echo ""
    print_status "Database status:"
    if sudo docker ps | grep -q "integrateddb"; then
        print_success "Database container is running"
    else
        print_warning "Database container is not running"
    fi
}

# Function to show logs
show_logs() {
    if [ -f "app.log" ]; then
        print_status "Showing application logs (last 50 lines):"
        tail -50 app.log
    else
        print_warning "No log file found"
    fi
}

# Main script logic
main() {
    case "${1:-dev}" in
        "dev"|"development")
            check_database
            start_development
            ;;
        "prod"|"production")
            check_database
            start_production
            ;;
        "bg"|"background")
            check_database
            start_background
            ;;
        "stop")
            stop_application
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"


