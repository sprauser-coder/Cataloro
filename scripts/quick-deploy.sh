#!/bin/bash

# Quick Deploy Script for Cataloro
# For rapid deployments and updates

set -e

SSH_HOST="217.154.0.82"
SSH_USER="root"
DEPLOY_PATH="/var/www/cataloro"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Quick frontend-only deploy
deploy_frontend() {
    log "⚡ Quick frontend deployment..."
    
    cd /app/frontend
    yarn build
    
    # Create tarball of build files
    tar -czf /tmp/frontend-build.tar.gz build/
    
    # Upload and deploy
    scp /tmp/frontend-build.tar.gz ${SSH_USER}@${SSH_HOST}:/tmp/
    
    ssh ${SSH_USER}@${SSH_HOST} << 'ENDSSH'
    cd /var/www/cataloro/current
    sudo rm -rf frontend/
    sudo tar -xzf /tmp/frontend-build.tar.gz
    sudo mv build frontend
    sudo chown -R www-data:www-data frontend/
    sudo systemctl reload nginx
    rm -f /tmp/frontend-build.tar.gz
    echo "✅ Frontend deployed successfully!"
ENDSSH
    
    rm -f /tmp/frontend-build.tar.gz
    log "✅ Quick frontend deployment completed!"
}

# Quick backend-only deploy
deploy_backend() {
    log "⚡ Quick backend deployment..."
    
    cd /app/backend
    tar -czf /tmp/backend.tar.gz --exclude=__pycache__ --exclude=uploads .
    
    # Upload and deploy
    scp /tmp/backend.tar.gz ${SSH_USER}@${SSH_HOST}:/tmp/
    
    ssh ${SSH_USER}@${SSH_HOST} << 'ENDSSH'
    cd /var/www/cataloro/current
    sudo systemctl stop cataloro-backend
    sudo rm -rf backend.old
    sudo mv backend backend.old
    sudo mkdir backend
    sudo tar -xzf /tmp/backend.tar.gz -C backend/
    sudo chown -R www-data:www-data backend/
    sudo pip3 install -r backend/requirements.txt
    sudo systemctl start cataloro-backend
    rm -f /tmp/backend.tar.gz
    echo "✅ Backend deployed successfully!"
ENDSSH
    
    rm -f /tmp/backend.tar.gz
    log "✅ Quick backend deployment completed!"
}

# Check deployment status
check_status() {
    log "📊 Checking deployment status..."
    
    ssh ${SSH_USER}@${SSH_HOST} << 'ENDSSH'
    echo "=== Service Status ==="
    systemctl status cataloro-backend --no-pager -l
    echo ""
    systemctl status nginx --no-pager -l
    echo ""
    echo "=== Recent Logs ==="
    journalctl -u cataloro-backend --no-pager -n 10
ENDSSH
}

# Show usage
usage() {
    echo "Usage: $0 [frontend|backend|status|full]"
    echo ""
    echo "Commands:"
    echo "  frontend  - Deploy only frontend changes"
    echo "  backend   - Deploy only backend changes"
    echo "  status    - Check deployment status"
    echo "  full      - Run full deployment (same as enhanced-deploy.sh)"
    echo ""
}

# Main logic
case "${1:-status}" in
    frontend)
        deploy_frontend
        ;;
    backend)
        deploy_backend
        ;;
    status)
        check_status
        ;;
    full)
        log "🚀 Running full deployment..."
        ./enhanced-deploy.sh
        ;;
    *)
        usage
        exit 1
        ;;
esac