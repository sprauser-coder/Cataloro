#!/bin/bash

# Cataloro Marketplace Deployment Script
# 
# Usage:
#   ./deploy.sh           - Standard deploy (pull, restart services)
#   ./deploy.sh setup     - Full setup with Nginx, SSL, and build
#   ./deploy.sh restart   - Pull changes and restart services
#   ./deploy.sh rebuild   - Install dependencies and restart
#   ./deploy.sh start     - Start all services
#   ./deploy.sh stop      - Stop all services  
#   ./deploy.sh logs      - View service logs

set -e

# Repository configuration
REPO_URL="https://github.com/sprauser-coder/Cataloro.git"
BRANCH="main"

# Function to backup local config files
backup_configs() {
    echo "💾 Backing up local configuration files..."
    mkdir -p /tmp/cataloro_backup
    
    # Backup supervisor configuration
    if [ -f "/etc/supervisor/conf.d/supervisord.conf" ]; then
        cp /etc/supervisor/conf.d/supervisord.conf /tmp/cataloro_backup/supervisord.conf
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
    if [ -f "/tmp/cataloro_backup/supervisord.conf" ]; then
        sudo cp /tmp/cataloro_backup/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
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
    
    sudo supervisorctl restart backend
    sudo supervisorctl restart frontend
    echo "✅ Services restarted"
}

# Function to check service status
check_services() {
    echo "📊 Checking service status..."
    sudo supervisorctl status
}

# Function to setup Nginx and SSL
setup_nginx() {
    echo "🌐 Setting up Nginx web server..."
    
    # Install Nginx if not present
    if ! command -v nginx &> /dev/null; then
        echo "Installing Nginx..."
        apt update && apt install -y nginx
    fi
    
    # Create SSL certificates if they don't exist
    if [[ ! -f "/etc/ssl/certs/cataloro.pem" ]]; then
        echo "Creating SSL certificates..."
        mkdir -p /etc/ssl/private
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/ssl/private/cataloro.key \
            -out /etc/ssl/certs/cataloro.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=cataloro.com"
    fi
    
    # Copy Nginx configuration
    echo "Configuring Nginx..."
    cp nginx-cataloro.conf /etc/nginx/sites-available/cataloro
    ln -sf /etc/nginx/sites-available/cataloro /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and restart Nginx
    nginx -t
    service nginx restart
    echo "✅ Nginx configured and running"
}

# Function to build frontend
build_frontend() {
    echo "🏗️ Building React frontend..."
    cd frontend
    yarn build
    cd ..
    echo "✅ Frontend built"
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
    "setup")
        pull_changes
        echo "🚀 Full setup with Nginx and SSL..."
        # Install dependencies
        pip install -r backend/requirements.txt
        cd frontend && yarn install && cd ..
        # Build frontend
        build_frontend
        # Setup Nginx
        setup_nginx
        # Restart services
        restart_services
        check_services
        echo "✅ Full setup complete - website should be accessible at https://cataloro.com"
        ;;
    *)
        pull_changes
        restart_services
        check_services
        echo "✅ Deploy complete"
        ;;
esac