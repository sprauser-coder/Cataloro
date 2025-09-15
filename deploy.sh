#!/bin/bash
set -e

# Repository configuration
REPO_URL="https://github.com/sprauser-coder/Cataloro.git"
BRANCH="main"

# Function to force pull latest changes from git
pull_changes() {
    echo "📦 Force pulling latest changes from GitHub..."
    
    # Check if .git directory exists
    if [ ! -d ".git" ]; then
        echo "🔄 No git repository found. Cloning from $REPO_URL..."
        git clone $REPO_URL .
        echo "✅ Repository cloned"
    else
        # Ensure origin is set to correct repo
        git remote set-url origin $REPO_URL 2>/dev/null || git remote add origin $REPO_URL
        
        # Force pull from specified repo and branch
        git fetch origin $BRANCH > /dev/null 2>&1
        git reset --hard origin/$BRANCH > /dev/null 2>&1
        echo "✅ Git force pull completed (local changes overridden)"
    fi
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