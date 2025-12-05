#!/bin/bash

# WagmiWars Deployment Script
# This script deploys the complete WagmiWars platform

set -e

echo "🚀 WagmiWars Platform Deployment"
echo "================================"

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

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env files exist
    if [ ! -f "backend/.env" ]; then
        print_warning "Backend .env file not found. Creating from example..."
        cp backend/.env.example backend/.env 2>/dev/null || print_warning "No .env.example found"
    fi
    
    if [ ! -f "frontend/.env.local" ]; then
        print_warning "Frontend .env.local file not found. Creating from example..."
        cp frontend/.env.example frontend/.env.local 2>/dev/null || print_warning "No .env.example found"
    fi
    
    print_success "Prerequisites check completed"
}

# Build and start services
start_services() {
    print_status "Building and starting services..."
    
    # Pull latest images
    docker-compose pull
    
    # Build custom images
    docker-compose build
    
    # Start services
    docker-compose up -d
    
    print_success "Services started successfully"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    print_status "Waiting for PostgreSQL..."
    while ! docker-compose exec postgres pg_isready -U wagmi -d wagmiwars_db &> /dev/null; do
        sleep 2
    done
    print_success "PostgreSQL is ready"
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    while ! docker-compose exec redis redis-cli ping &> /dev/null; do
        sleep 2
    done
    print_success "Redis is ready"
    
    # Wait for Backend API
    print_status "Waiting for Backend API..."
    while ! curl -f http://localhost:8000/health &> /dev/null; do
        sleep 2
    done
    print_success "Backend API is ready"
    
    # Wait for Frontend
    print_status "Waiting for Frontend..."
    while ! curl -f http://localhost:3000 &> /dev/null; do
        sleep 2
    done
    print_success "Frontend is ready"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Create database tables
    docker-compose exec backend python -c "
from app.core.database import create_tables
create_tables()
print('Database tables created successfully')
"
    
    print_success "Database migrations completed"
}

# Display access information
display_access_info() {
    print_success "🎉 WagmiWars Platform Deployed Successfully!"
    echo ""
    echo "Access URLs:"
    echo "============"
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo "API Health Check: http://localhost:8000/health"
    echo ""
    echo "Services:"
    echo "========="
    echo "PostgreSQL: localhost:5432"
    echo "Redis: localhost:6379"
    echo ""
    echo "Default Credentials:"
    echo "==================="
    echo "Database: wagmi/wagmi123"
    echo ""
    echo "Next Steps:"
    echo "==========="
    echo "1. Open http://localhost:3000 in your browser"
    echo "2. Connect your Web3 wallet (MetaMask, etc.)"
    echo "3. Create your first AI trading agent"
    echo "4. Join a match and start competing!"
    echo ""
    echo "For development:"
    echo "docker-compose logs -f backend  # View backend logs"
    echo "docker-compose logs -f frontend # View frontend logs"
    echo ""
}

# Main deployment function
main() {
    echo "Starting WagmiWars deployment..."
    echo "================================"
    echo ""
    
    check_prerequisites
    start_services
    wait_for_services
    run_migrations
    display_access_info
}

# Handle script arguments
case "${1:-deploy}" in
    deploy)
        main
        ;;
    start)
        docker-compose start
        ;;
    stop)
        docker-compose stop
        ;;
    restart)
        docker-compose restart
        ;;
    logs)
        docker-compose logs -f
        ;;
    status)
        docker-compose ps
        ;;
    cleanup)
        print_status "Cleaning up Docker resources..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        print_success "Cleanup completed"
        ;;
    *)
        echo "Usage: $0 {deploy|start|stop|restart|logs|status|cleanup}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy the complete platform (default)"
        echo "  start   - Start existing services"
        echo "  stop    - Stop services"
        echo "  restart - Restart services"
        echo "  logs    - View logs"
        echo "  status  - Check service status"
        echo "  cleanup - Remove all containers and volumes"
        exit 1
        ;;
esac