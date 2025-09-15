#!/bin/bash
set -e

# Function to pull latest changes from git
pull_changes() {
    echo "📦 Pulling latest changes from GitHub..."
    git pull origin main > /dev/null 2>&1 || {
        echo "⚠️  Git pull failed or no changes to pull"
    }
    echo "✅ Git pull completed"
}

case "$1" in
    "start")
        echo "🚀 Starting..."
        docker-compose up -d > /dev/null
        echo "✅ Started"
        ;;
    "stop")
        echo "🛑 Stopping..."
        docker-compose down > /dev/null
        echo "✅ Stopped"
        ;;
    "restart")
        echo "🔄 Restarting..."
        docker-compose down > /dev/null && docker-compose up -d > /dev/null
        echo "✅ Restarted"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "rebuild")
        echo "🔧 Rebuilding..."
        docker-compose down > /dev/null 2>&1
        docker-compose build --no-cache > /dev/null 2>&1
        docker-compose up -d > /dev/null 2>&1
        echo "✅ Rebuilt and started"
        ;;
    *)
        echo "🚀 Building..."
        docker-compose build --no-cache > /dev/null 2>&1
        docker-compose up -d > /dev/null 2>&1
        echo "✅ Deploy complete"
        ;;
esac