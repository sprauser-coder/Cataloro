#!/bin/bash
set -e

echo "🚀 Cataloro Marketplace Deploy"

case "$1" in
    "start")
        echo "Starting services..."
        docker-compose up -d
        ;;
    "stop")
        echo "Stopping services..."
        docker-compose down
        ;;
    "restart")
        echo "Restarting services..."
        docker-compose down && docker-compose up -d
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "rebuild")
        echo "Rebuilding..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        ;;
    *)
        echo "Building and starting..."
        docker-compose build --no-cache
        docker-compose up -d
        echo "✅ Deployment completed!"
        echo "Frontend: http://localhost:3000"
        echo "Backend: http://localhost:8001"
        ;;
esac