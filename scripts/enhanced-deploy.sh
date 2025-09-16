#!/bin/bash

# CATALORO - Enhanced Deployment Script with Backup/Restore
# Automated deployment to SSH server at 217.154.0.82

set -e  # Exit on any error

# Configuration
SSH_HOST="217.154.0.82"
SSH_USER="root"  # Change this to your SSH user
DEPLOY_PATH="/var/www/cataloro"
APP_NAME="cataloro"
BACKUP_RETENTION_DAYS=7

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Pre-flight checks
preflight_checks() {
    log "🔍 Running pre-flight checks..."
    
    # Check if SSH key is configured
    if ! ssh -o BatchMode=yes -o ConnectTimeout=5 ${SSH_USER}@${SSH_HOST} exit 2>/dev/null; then
        error "SSH connection failed. Please ensure SSH key is configured."
        exit 1
    fi
    
    # Check if required directories exist locally
    if [ ! -d "/app/frontend" ] || [ ! -d "/app/backend" ]; then
        error "Frontend or backend directories not found."
        exit 1
    fi
    
    # Check if Node.js and yarn are available
    if ! command -v yarn &> /dev/null; then
        error "yarn could not be found. Please install yarn."
        exit 1
    fi
    
    log "✅ Pre-flight checks passed"
}

# Backup current deployment
backup_deployment() {
    log "💾 Creating backup of current deployment..."
    
    ssh ${SSH_USER}@${SSH_HOST} << 'ENDSSH'
    set -e
    
    if [ -d "/var/www/cataloro/current" ]; then
        BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
        sudo mkdir -p /var/www/cataloro/backups
        sudo cp -r /var/www/cataloro/current /var/www/cataloro/backups/$BACKUP_NAME
        
        # Remove old backups (keep last 7 days)
        sudo find /var/www/cataloro/backups -type d -name "backup-*" -mtime +7 -exec rm -rf {} + 2>/dev/null || true
        
        echo "✅ Backup created: $BACKUP_NAME"
    else
        echo "ℹ️  No existing deployment to backup"
    fi
ENDSSH
}

# Build application
build_application() {
    log "📦 Building application..."
    
    # Build frontend
    info "Building React frontend..."
    cd /app/frontend
    yarn install --frozen-lockfile
    yarn build
    
    # Prepare backend
    info "Preparing Python backend..."
    cd /app/backend
    pip freeze > requirements.txt
    
    log "✅ Application build completed"
}

# Create deployment package
create_deployment_package() {
    log "📁 Creating deployment package..."
    
    cd /app
    
    # Create temporary directory for deployment files
    mkdir -p /tmp/cataloro-deploy
    
    # Copy files to deployment directory
    cp -r frontend/build /tmp/cataloro-deploy/frontend
    cp -r backend /tmp/cataloro-deploy/
    cp -r config /tmp/cataloro-deploy/ 2>/dev/null || true
    cp -r scripts /tmp/cataloro-deploy/
    cp -r nginx /tmp/cataloro-deploy/ 2>/dev/null || true
    cp docker-compose.yml /tmp/cataloro-deploy/ 2>/dev/null || true
    cp .env.production /tmp/cataloro-deploy/.env 2>/dev/null || true
    
    # Create tarball
    cd /tmp
    tar -czf cataloro-deploy.tar.gz cataloro-deploy/
    
    # Cleanup temporary directory
    rm -rf /tmp/cataloro-deploy
    
    log "✅ Deployment package created"
}

# Upload and deploy
upload_and_deploy() {
    log "🌐 Uploading and deploying to server..."
    
    # Upload deployment package
    scp /tmp/cataloro-deploy.tar.gz ${SSH_USER}@${SSH_HOST}:/tmp/
    
    # Deploy on server
    ssh ${SSH_USER}@${SSH_HOST} << 'ENDSSH'
    set -e
    
    # Create deployment directory
    sudo mkdir -p /var/www/cataloro
    cd /var/www/cataloro
    
    # Extract new deployment
    sudo tar -xzf /tmp/cataloro-deploy.tar.gz
    
    # Stop services before deployment
    sudo systemctl stop cataloro-backend 2>/dev/null || true
    sudo systemctl stop nginx 2>/dev/null || true
    
    # Move current to new
    if [ -d "current" ]; then
        sudo rm -rf current.old 2>/dev/null || true
        sudo mv current current.old
    fi
    sudo mv cataloro-deploy current
    
    # Set permissions
    sudo chown -R www-data:www-data current/
    sudo chmod -R 755 current/
    
    # Install backend dependencies
    info "Installing backend dependencies..."
    cd current/backend
    sudo pip3 install -r requirements.txt
    
    # Copy environment file
    if [ -f "../.env" ]; then
        sudo cp ../.env .env
    fi
    
    # Configure Nginx
    info "Configuring Nginx..."
    if [ -f "../nginx/cataloro.conf" ]; then
        sudo cp ../nginx/cataloro.conf /etc/nginx/sites-available/cataloro
        sudo ln -sf /etc/nginx/sites-available/cataloro /etc/nginx/sites-enabled/
    fi
    
    # Test Nginx configuration
    sudo nginx -t
    
    # Configure systemd service for backend
    sudo tee /etc/systemd/system/cataloro-backend.service > /dev/null <<EOL
[Unit]
Description=Cataloro Backend API
After=network.target mongodb.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/cataloro/current/backend
Environment=PATH=/usr/bin:/usr/local/bin
EnvironmentFile=/var/www/cataloro/current/backend/.env
ExecStart=/usr/bin/python3 -m uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL
    
    # Reload systemd and start services
    sudo systemctl daemon-reload
    sudo systemctl enable cataloro-backend
    sudo systemctl start cataloro-backend
    sudo systemctl start nginx
    
    # Clean up
    rm -f /tmp/cataloro-deploy.tar.gz
    
    echo "✅ Deployment completed successfully!"
    
ENDSSH
}

# Health checks
health_checks() {
    log "🏥 Running health checks..."
    
    sleep 10  # Give services time to start
    
    # Check backend health
    info "Checking backend health..."
    if curl -s -f "http://${SSH_HOST}/api/health" > /dev/null; then
        log "✅ Backend is healthy and responding"
    else
        error "❌ Backend health check failed"
        return 1
    fi
    
    # Check frontend
    info "Checking frontend..."
    if curl -s -f "http://${SSH_HOST}/" > /dev/null; then
        log "✅ Frontend is accessible"
    else
        warning "⚠️  Frontend check failed (might be normal if SSL redirect is configured)"
    fi
    
    # Check HTTPS if SSL is configured
    if curl -s -f "https://cataloro.com/" > /dev/null 2>&1; then
        log "✅ HTTPS is working"
    else
        info "ℹ️  HTTPS check skipped (SSL might not be configured yet)"
    fi
}

# Rollback function
rollback() {
    error "🔄 Deployment failed. Initiating rollback..."
    
    ssh ${SSH_USER}@${SSH_HOST} << 'ENDSSH'
    set -e
    
    cd /var/www/cataloro
    
    # Stop services
    sudo systemctl stop cataloro-backend 2>/dev/null || true
    
    # Restore from backup
    if [ -d "current.old" ]; then
        sudo rm -rf current
        sudo mv current.old current
        sudo systemctl start cataloro-backend
        sudo systemctl reload nginx
        echo "✅ Rollback completed successfully"
    else
        # Try to restore from latest backup
        LATEST_BACKUP=$(sudo find backups -type d -name "backup-*" -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
        if [ -n "$LATEST_BACKUP" ]; then
            sudo rm -rf current
            sudo cp -r "$LATEST_BACKUP" current
            sudo systemctl start cataloro-backend
            sudo systemctl reload nginx
            echo "✅ Rollback completed from backup: $LATEST_BACKUP"
        else
            echo "❌ No backup available for rollback"
            exit 1
        fi
    fi
ENDSSH
}

# Cleanup
cleanup() {
    log "🧹 Cleaning up local files..."
    rm -f /tmp/cataloro-deploy.tar.gz
}

# Main deployment function
main() {
    log "🚀 Starting Cataloro Enhanced Deployment..."
    log "📍 Target server: ${SSH_HOST}"
    log "📁 Deploy path: ${DEPLOY_PATH}"
    
    # Set trap for cleanup and rollback on error
    trap 'error "Deployment failed"; rollback; cleanup; exit 1' ERR
    
    preflight_checks
    backup_deployment
    build_application
    create_deployment_package
    upload_and_deploy
    
    # Remove error trap before health checks
    trap - ERR
    
    # Run health checks (non-fatal)
    if ! health_checks; then
        warning "Health checks failed, but deployment completed. Please check manually."
    fi
    
    cleanup
    
    log "✅ Cataloro deployment completed successfully!"
    log "🌐 Frontend: https://cataloro.com (or http://${SSH_HOST})"
    log "🔌 Backend API: https://cataloro.com/api (or http://${SSH_HOST}/api)"
    log "📊 Service status: sudo systemctl status cataloro-backend"
    log "📋 Logs: sudo journalctl -u cataloro-backend -f"
}

# Run main function
main "$@"