#!/bin/bash
set -e

# Repository configuration
REPO_URL="https://github.com/sprauser-coder/Cataloro.git"
BRANCH="main"

# Function to backup local config files
backup_configs() {
    echo "💾 Backing up local configuration files..."
    mkdir -p /tmp/cataloro_backup
    
    # Backup supervisor configuration
    if [ -f "/etc/supervisord.d/cataloro.conf" ]; then
        cp /etc/supervisord.d/cataloro.conf /tmp/cataloro_backup/
        echo "✅ Supervisor config backed up"
    fi
    
    # Backup frontend .env if it exists
    if [ -f "frontend/.env" ]; then
        cp frontend/.env /tmp/cataloro_backup/frontend.env
        echo "✅ Frontend .env backed up"
    fi
    
    # Backup backend .env if it exists  
    if [ -f "backend/.env" ]; then
        cp backend/.env /tmp/cataloro_backup/backend.env
        echo "✅ Backend .env backed up"
    fi
}

# Function to restore local config files
restore_configs() {
    echo "🔄 Restoring local configuration files..."
    
    # Restore supervisor configuration
    if [ -f "/tmp/cataloro_backup/cataloro.conf" ]; then
        sudo cp /tmp/cataloro_backup/cataloro.conf /etc/supervisord.d/
        echo "✅ Supervisor config restored"
    fi
    
    # Restore frontend .env
    if [ -f "/tmp/cataloro_backup/frontend.env" ]; then
        cp /tmp/cataloro_backup/frontend.env frontend/.env
        echo "✅ Frontend .env restored"
    fi
    
    # Restore backend .env
    if [ -f "/tmp/cataloro_backup/backend.env" ]; then
        cp /tmp/cataloro_backup/backend.env backend/.env
        echo "✅ Backend .env restored"
    fi
    
    # Clean up backup
    rm -rf /tmp/cataloro_backup
}

# Function to force pull latest changes from git
pull_changes() {
    echo "📦 Force pulling latest changes from GitHub..."
    
    # Check if .git directory exists
    if [ ! -d ".git" ]; then
        echo "🔄 No git repository found. Cloning from $REPO_URL..."
        git clone $REPO_URL .
        echo "✅ Repository cloned"
    else
        # Backup local configs before git operations
        backup_configs
        
        # Ensure origin is set to correct repo
        git remote set-url origin $REPO_URL 2>/dev/null || git remote add origin $REPO_URL
        
        # Force pull from specified repo and branch
        git fetch origin $BRANCH
        git reset --hard origin/$BRANCH
        echo "✅ Git force pull completed (local changes overridden)"
        
        # Restore local configs after git operations
        restore_configs
    fi
}

# Function to restart supervisor services
restart_services() {
    echo "🔄 Restarting services..."
    
    # Reload supervisor config in case it was restored
    sudo supervisorctl reread
    sudo supervisorctl update
    
    sudo supervisorctl restart cataloro-backend
    sudo supervisorctl restart cataloro-frontend
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