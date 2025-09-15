#!/bin/bash

# Cataloro Marketplace Deployment Script
# This script helps deploy the application to your server

set -e  # Exit on any error

echo "🚀 Cataloro Marketplace Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed ✓"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        cp .env.production .env
        print_warning "Please edit .env file with your configuration before continuing!"
        echo "Required changes:"
        echo "  - MONGO_ROOT_PASSWORD: Set a secure MongoDB password"
        echo "  - JWT_SECRET: Set a secure JWT secret key"
        echo "  - REACT_APP_BACKEND_URL: Set your domain/IP"
        echo ""
        read -p "Press Enter when you've updated the .env file..."
    fi
    print_status ".env file exists ✓"
}

# Build and start services
deploy() {
    print_status "Building Docker images..."
    docker-compose build --no-cache
    
    print_status "Starting services..."
    docker-compose up -d
    
    print_status "Waiting for services to start..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        print_status "Services started successfully! ✓"
        echo ""
        echo "🎉 Deployment completed!"
        echo ""
        echo "Services running:"
        docker-compose ps
        echo ""
        echo "Access your application at:"
        echo "  Frontend: http://localhost:3000"
        echo "  Backend API: http://localhost:8001"
        echo "  MongoDB: localhost:27017"
        echo ""
        echo "To view logs: docker-compose logs -f"
        echo "To stop: docker-compose down"
    else
        print_error "Some services failed to start. Check logs: docker-compose logs"
        exit 1
    fi
}

# Main deployment process
main() {
    echo "Starting deployment process..."
    echo ""
    
    check_docker
    check_env
    deploy
    
    echo ""
    print_status "Deployment script completed!"
}

# Handle script arguments
case "$1" in
    "start")
        print_status "Starting existing services..."
        docker-compose up -d
        ;;
    "stop")
        print_status "Stopping services..."
        docker-compose down
        ;;
    "restart")
        print_status "Restarting services..."
        docker-compose down
        docker-compose up -d
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "rebuild")
        print_status "Rebuilding and restarting..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        ;;
    *)
        main
        ;;
esac