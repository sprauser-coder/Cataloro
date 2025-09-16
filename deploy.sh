#!/bin/bash

# Enhanced Cataloro Marketplace Deployment Script with Protection
# 
# Usage:
#   ./deploy.sh           - Standard protected deploy
#   ./deploy.sh setup     - Full initial setup with protection
#   ./deploy.sh restore   - Restore from backup
#   ./deploy.sh status    - Check system status
#   ./deploy.sh logs      - View service logs

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/sprauser-coder/Cataloro.git"
BRANCH="main"
BACKUP_DIR="/tmp/cataloro_backup_$(date +%Y%m%d_%H%M%S)"
LATEST_BACKUP_LINK="/tmp/cataloro_backup_latest"
APP_DIR="/root/cataloro-marketplace"

# Protected files list
PROTECTED_FILES=(
    "/etc/nginx/conf.d/cataloro.conf"
    "/etc/supervisord.d/cataloro.conf"
    "/etc/supervisor/conf.d/supervisord.conf"
    "frontend/.env"
    "backend/.env"
    "/etc/letsencrypt"
    "/etc/ssl/certs/cataloro.pem"
    "/etc/ssl/private/cataloro.key"
)

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Pre-flight checks
preflight_checks() {
    log "🔍 Running pre-flight checks..."
    
    # Check if we're in the right directory
    if [ ! -f "package.json" ] && [ ! -f "frontend/package.json" ]; then
        if [ -d "$APP_DIR" ]; then
            cd "$APP_DIR"
            log "Changed to application directory: $APP_DIR"
        else
            error "Not in application directory and $APP_DIR not found"
            exit 1
        fi
    fi
    
    # Check git status
    if [ -d ".git" ]; then
        if ! git status >/dev/null 2>&1; then
            error "Git repository is corrupted"
            exit 1
        fi
    fi
    
    # Check disk space (need at least 1GB free)
    FREE_SPACE=$(df / | awk 'NR==2 {print $4}')
    if [ "$FREE_SPACE" -lt 1048576 ]; then
        error "Insufficient disk space (need at least 1GB free)"
        exit 1
    fi
    
    # Check if ports are available
    if ! command -v ss >/dev/null 2>&1; then
        warning "ss command not available, skipping port checks"
    else
        if ss -tlnp | grep -q ":80 "; then
            info "Port 80 is in use (expected for nginx)"
        fi
        if ss -tlnp | grep -q ":443 "; then
            info "Port 443 is in use (expected for nginx)"
        fi
    fi
    
    log "✅ Pre-flight checks completed"
}

# Backup protected files
backup_protected_files() {
    log "💾 Backing up protected files..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Backup each protected file/directory
    for protected_file in "${PROTECTED_FILES[@]}"; do
        if [ -e "$protected_file" ]; then
            # Create directory structure in backup
            backup_path="$BACKUP_DIR$(dirname "$protected_file")"
            mkdir -p "$backup_path"
            
            # Copy file/directory
            if [ -d "$protected_file" ]; then
                cp -r "$protected_file" "$backup_path/"
                log "✅ Backed up directory: $protected_file"
            else
                cp "$protected_file" "$backup_path/"
                log "✅ Backed up file: $protected_file"
            fi
        else
            info "Protected file not found (will be created from template): $protected_file"
        fi
    done
    
    # Create symlink to latest backup
    rm -f "$LATEST_BACKUP_LINK"
    ln -s "$BACKUP_DIR" "$LATEST_BACKUP_LINK"
    
    log "✅ Backup completed: $BACKUP_DIR"
}

# Restore protected files
restore_protected_files() {
    local backup_source="${1:-$LATEST_BACKUP_LINK}"
    
    log "🔄 Restoring protected files from: $backup_source"
    
    if [ ! -d "$backup_source" ]; then
        error "Backup directory not found: $backup_source"
        return 1
    fi
    
    # Restore each protected file
    for protected_file in "${PROTECTED_FILES[@]}"; do
        backup_file="$backup_source$protected_file"
        
        if [ -e "$backup_file" ]; then
            # Ensure target directory exists
            target_dir=$(dirname "$protected_file")
            mkdir -p "$target_dir"
            
            # Restore file/directory
            if [ -d "$backup_file" ]; then
                cp -r "$backup_file" "$target_dir/"
                log "✅ Restored directory: $protected_file"
            else
                cp "$backup_file" "$protected_file"
                log "✅ Restored file: $protected_file"
            fi
        else
            info "No backup found for: $protected_file"
        fi
    done
    
    log "✅ Restore completed"
}

# Setup environment files from templates
setup_environment_files() {
    log "🔧 Setting up environment files..."
    
    # Frontend environment
    if [ ! -f "frontend/.env" ] && [ -f "frontend/.env.example" ]; then
        cp "frontend/.env.example" "frontend/.env"
        log "✅ Created frontend/.env from template"
    fi
    
    # Backend environment
    if [ ! -f "backend/.env" ] && [ -f "backend/.env.example" ]; then
        cp "backend/.env.example" "backend/.env"
        log "✅ Created backend/.env from template"
    fi
}

# Pull latest changes from GitHub
pull_changes() {
    log "📦 Pulling latest changes from GitHub..."
    
    # Initialize git if needed
    if [ ! -d ".git" ]; then
        git init
        git remote add origin "$REPO_URL"
    fi
    
    # Fetch and reset to latest
    git fetch origin "$BRANCH"
    git reset --hard "origin/$BRANCH"
    
    log "✅ Git pull completed"
}

# Install dependencies
install_dependencies() {
    log "📚 Installing dependencies..."
    
    # Backend dependencies
    if [ -f "backend/requirements.txt" ]; then
        log "Installing Python dependencies..."
        pip install -r backend/requirements.txt
    fi
    
    # Frontend dependencies
    if [ -f "frontend/package.json" ]; then
        log "Installing Node.js dependencies..."
        cd frontend
        yarn install
        cd ..
    fi
    
    log "✅ Dependencies installed"
}

# Build frontend
build_frontend() {
    log "🏗️ Building React frontend..."
    
    if [ -f "frontend/package.json" ]; then
        cd frontend
        yarn build
        cd ..
        log "✅ Frontend built successfully"
    else
        warning "Frontend package.json not found, skipping build"
    fi
}

# Setup system services
setup_services() {
    log "🌐 Setting up system services..."
    
    # Install nginx if not present
    if ! command -v nginx >/dev/null 2>&1; then
        log "Installing Nginx..."
        yum update -y
        yum install -y nginx
    fi
    
    # Create SSL certificates if they don't exist
    if [ ! -f "/etc/letsencrypt/live/cataloro.com/fullchain.pem" ] && [ ! -f "/etc/ssl/certs/cataloro.pem" ]; then
        log "Creating self-signed SSL certificates..."
        mkdir -p /etc/ssl/private
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/ssl/private/cataloro.key \
            -out /etc/ssl/certs/cataloro.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=cataloro.com"
        log "✅ SSL certificates created"
    fi
    
    # Setup Nginx configuration if it doesn't exist
    if [ ! -f "/etc/nginx/conf.d/cataloro.conf" ] && [ -f "nginx-cataloro.conf" ]; then
        log "Setting up Nginx configuration..."
        cp nginx-cataloro.conf /etc/nginx/conf.d/cataloro.conf
        log "✅ Nginx configuration installed"
    fi
    
    # Setup Supervisor configuration if it doesn't exist  
    if [ ! -f "/etc/supervisord.d/cataloro.conf" ] && [ -f "supervisor-cataloro.conf" ]; then
        log "Setting up Supervisor configuration..."
        cp supervisor-cataloro.conf /etc/supervisord.d/cataloro.conf
        log "✅ Supervisor configuration installed"
    fi
}

# Restart services
restart_services() {
    log "🔄 Restarting services..."
    
    # Test nginx configuration
    if nginx -t >/dev/null 2>&1; then
        systemctl restart nginx
        log "✅ Nginx restarted"
    else
        error "Nginx configuration test failed"
        nginx -t
        return 1
    fi
    
    # Restart supervisor services
    if command -v supervisorctl >/dev/null 2>&1; then
        supervisorctl reread
        supervisorctl update
        supervisorctl restart all
        log "✅ Supervisor services restarted"
    else
        warning "Supervisor not available"
    fi
}

# Health checks
health_checks() {
    log "🔍 Running health checks..."
    
    local failed=0
    
    # Check Nginx
    if systemctl is-active nginx >/dev/null 2>&1; then
        log "✅ Nginx is running"
    else
        error "❌ Nginx is not running"
        failed=1
    fi
    
    # Check backend API
    if curl -s http://localhost:8001/api/health >/dev/null 2>&1; then
        log "✅ Backend API is responding"
    else
        error "❌ Backend API is not responding"
        failed=1
    fi
    
    # Check website
    if curl -s -k https://localhost >/dev/null 2>&1; then
        log "✅ Website is accessible"
    else
        error "❌ Website is not accessible"
        failed=1
    fi
    
    # Check supervisor services
    if command -v supervisorctl >/dev/null 2>&1; then
        local services_status=$(supervisorctl status | grep -v RUNNING | wc -l)
        if [ "$services_status" -eq 0 ]; then
            log "✅ All Supervisor services are running"
        else
            error "❌ Some Supervisor services are not running"
            supervisorctl status
            failed=1
        fi
    fi
    
    return $failed
}

# Rollback function
rollback() {
    error "💥 Deployment failed! Starting rollback..."
    
    if [ -d "$LATEST_BACKUP_LINK" ]; then
        restore_protected_files "$LATEST_BACKUP_LINK"
        restart_services
        log "🔄 Rollback completed"
    else
        error "No backup found for rollback"
        exit 1
    fi
}

# Main deployment function
deploy() {
    log "🚀 Starting protected deployment..."
    
    # Set up error handling
    trap rollback ERR
    
    preflight_checks
    backup_protected_files
    pull_changes
    setup_environment_files
    restore_protected_files
    install_dependencies
    build_frontend
    restart_services
    
    # Disable error trap for health checks
    trap - ERR
    
    if health_checks; then
        log "🎉 Deployment successful!"
        log "🌐 Website: https://cataloro.com"
        log "🔧 API: https://cataloro.com/api/health"
        
        # Clean up old backups (keep last 5)
        find /tmp -name "cataloro_backup_*" -type d | sort | head -n -5 | xargs rm -rf 2>/dev/null || true
    else
        warning "⚠️  Deployment completed but health checks failed"
        log "Check the status with: ./deploy.sh status"
        return 1
    fi
}

# Show service status
show_status() {
    log "📊 System Status"
    echo ""
    
    echo "=== Nginx Status ==="
    systemctl status nginx --no-pager -l || true
    echo ""
    
    echo "=== Supervisor Status ==="
    supervisorctl status || true
    echo ""
    
    echo "=== Disk Usage ==="
    df -h / || true
    echo ""
    
    echo "=== Port Usage ==="
    ss -tlnp | grep -E ":(80|443|8001|3000|3001)" || true
    echo ""
    
    echo "=== Recent Logs ==="
    echo "Backend logs:"
    tail -5 /var/log/supervisor/backend.log 2>/dev/null || echo "No backend logs found"
    echo ""
    echo "Frontend logs:"
    tail -5 /var/log/supervisor/frontend.log 2>/dev/null || echo "No frontend logs found"
}

# Show logs
show_logs() {
    log "📋 Service Logs"
    echo ""
    
    echo "=== Backend Logs (last 50 lines) ==="
    tail -50 /var/log/supervisor/backend.log 2>/dev/null || echo "No backend logs found"
    echo ""
    
    echo "=== Frontend Logs (last 50 lines) ==="
    tail -50 /var/log/supervisor/frontend.log 2>/dev/null || echo "No frontend logs found"
    echo ""
    
    echo "=== Nginx Error Logs (last 20 lines) ==="
    tail -20 /var/log/nginx/error.log 2>/dev/null || echo "No nginx error logs found"
}

# Main script logic
case "${1:-deploy}" in
    "deploy"|"")
        deploy
        ;;
    "setup")
        log "🚀 Running full setup with protection..."
        preflight_checks
        backup_protected_files
        pull_changes
        setup_environment_files
        install_dependencies
        build_frontend
        setup_services
        restore_protected_files
        restart_services
        health_checks && log "🎉 Setup completed successfully!" || warning "⚠️ Setup completed with warnings"
        ;;
    "restore")
        if [ -n "$2" ]; then
            restore_protected_files "$2"
        else
            restore_protected_files
        fi
        restart_services
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "backup")
        backup_protected_files
        ;;
    "health")
        health_checks && log "✅ All health checks passed" || error "❌ Health checks failed"
        ;;
    *)
        echo "Usage: $0 {deploy|setup|restore|status|logs|backup|health}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Standard protected deployment (default)"
        echo "  setup   - Full initial setup with service configuration"
        echo "  restore - Restore protected files from backup"
        echo "  status  - Show system and service status"
        echo "  logs    - Show service logs"
        echo "  backup  - Create backup of protected files"
        echo "  health  - Run health checks only"
        exit 1
        ;;
esac