#!/bin/bash
# Docker PostGIS Setup Script for CIM Wizard Integrated
# This script automates the complete Docker PostGIS setup

set -e  # Exit on any error

echo "🐳 CIM Wizard Integrated - Docker PostGIS Setup"
echo "================================================"

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

# Check if Docker is running
check_docker() {
    print_status "Checking Docker..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    print_success "Docker is running"
}

# Check if docker-compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose not found. Please install Docker Compose."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Stop existing containers
stop_existing() {
    print_status "Stopping existing containers..."
    docker-compose down > /dev/null 2>&1 || true
    print_success "Existing containers stopped"
}

# Build PostGIS container
build_postgis() {
    print_status "Building custom PostGIS container..."
    docker-compose build postgres
    print_success "PostGIS container built"
}

# Start PostGIS container
start_postgis() {
    print_status "Starting PostGIS container..."
    docker-compose up postgres -d
    
    # Wait for container to be healthy
    print_status "Waiting for PostGIS to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps postgres | grep -q "healthy"; then
            print_success "PostGIS container is healthy"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "PostGIS container did not become healthy in time"
    docker-compose logs postgres
    exit 1
}

# Test database connection
test_connection() {
    print_status "Testing database connection..."
    if python scripts/test_docker_connection.py > /dev/null 2>&1; then
        print_success "Database connection test passed"
    else
        print_warning "Database connection test failed - running full test"
        python scripts/test_docker_connection.py
    fi
}

# Populate sample data
populate_data() {
    print_status "Populating sample data..."
    if python scripts/populate_sample_data.py > /dev/null 2>&1; then
        print_success "Sample data populated"
    else
        print_warning "Sample data population failed - running with output"
        python scripts/populate_sample_data.py
    fi
}

# Start pgAdmin
start_pgadmin() {
    print_status "Starting pgAdmin..."
    docker-compose up pgadmin -d
    print_success "pgAdmin started - access at http://localhost:5050"
    print_status "pgAdmin credentials: admin@cimwizard.com / admin"
}

# Create .env file if it doesn't exist
setup_env() {
    if [ ! -f .env ]; then
        print_status "Creating .env file..."
        cp env.example .env
        print_success ".env file created"
    else
        print_status ".env file already exists"
    fi
}

# Test the application
test_application() {
    print_status "Testing application startup..."
    
    # Try to import the application
    if python -c "from app.db.database import engine; print('✅ Application can import database')" 2>/dev/null; then
        print_success "Application imports successful"
    else
        print_warning "Application import test failed"
    fi
}

# Main setup function
main() {
    echo
    print_status "Starting Docker PostGIS setup for CIM Wizard Integrated"
    echo
    
    # Run setup steps
    check_docker
    check_docker_compose
    setup_env
    stop_existing
    build_postgis
    start_postgis
    test_connection
    populate_data
    start_pgadmin
    test_application
    
    echo
    print_success "🎉 Docker PostGIS setup completed!"
    echo
    echo "📊 Service URLs:"
    echo "   • Database: localhost:5432"
    echo "   • pgAdmin: http://localhost:5050"
    echo "   • Application: http://localhost:8000 (after starting)"
    echo
    echo "🚀 Next steps:"
    echo "   1. Start the application: python run.py"
    echo "   2. Test the API: python examples/simple_api_usage.py"
    echo "   3. Access API docs: http://localhost:8000/docs"
    echo
    echo "🔧 Useful commands:"
    echo "   • Check status: docker-compose ps"
    echo "   • View logs: docker-compose logs postgres"
    echo "   • Stop services: docker-compose down"
    echo "   • Restart: docker-compose restart postgres"
    echo
}

# Run main function
main "$@"