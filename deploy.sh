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
        git fetch origin $BRANCH
        git reset --hard origin/$BRANCH
        echo "✅ Git force pull completed (local changes overridden)"
    fi
}

# Function to restart supervisor services
restart_services() {
    echo "🔄 Restarting services..."
    sudo supervisorctl restart backend
    sudo supervisorctl restart frontend
    sudo supervisorctl restart mongodb
    echo "✅ Services restarted"
}

# Function to check service status
check_services() {
    echo "📊 Checking service status..."
    sudo supervisorctl status
}

case "$1" in
    "start")
        pull_changes
        echo "🚀 Starting services..."
        sudo supervisorctl start all
        check_services
        echo "✅ Started"
        ;;
    "stop")
        echo "🛑 Stopping services..."
        sudo supervisorctl stop all
        echo "✅ Stopped"
        ;;
    "restart")
        pull_changes
        restart_services
        check_services
        echo "✅ Restarted"
        ;;
    "logs")
        echo "📋 Backend logs:"
        tail -n 50 /var/log/supervisor/backend.*.log
        echo "📋 Frontend logs:"
        tail -n 50 /var/log/supervisor/frontend.*.log
        ;;
    "rebuild")
        pull_changes
        echo "🔧 Installing dependencies and restarting..."
        # Install backend dependencies if requirements.txt changed
        pip install -r backend/requirements.txt
        # Install frontend dependencies if package.json changed
        cd frontend && yarn install && cd ..
        restart_services
        check_services
        echo "✅ Rebuilt and restarted"
        ;;
    *)
        pull_changes
        restart_services
        check_services
        echo "✅ Deploy complete"
        ;;
esac