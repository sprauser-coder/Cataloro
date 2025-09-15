#!/bin/bash
set -e

# Function to force pull latest changes from git
pull_changes() {
    echo "📦 Force pulling latest changes from GitHub..."
    git fetch origin main > /dev/null 2>&1
    git pull origin main > /dev/null 2>&1
    echo "✅ Git pull completed"
}

case "$1" in
    "start")
        pull_changes
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
        pull_changes
        echo "🔄 Restarting..."
        docker-compose down > /dev/null && docker-compose up -d > /dev/null
        echo "✅ Restarted"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "rebuild")
        pull_changes
        echo "🔧 Rebuilding..."
        docker-compose down > /dev/null 2>&1
        docker-compose build --no-cache > /dev/null 2>&1
        docker-compose up -d > /dev/null 2>&1
        echo "✅ Rebuilt and started"
        ;;
    *)
        pull_changes
        echo "🚀 Building..."
        docker-compose build --no-cache > /dev/null 2>&1
        docker-compose up -d > /dev/null 2>&1
        echo "✅ Deploy complete"
        ;;
esac