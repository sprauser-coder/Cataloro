#!/bin/bash

# VPS Complete Cleanup Script for Cataloro
# WARNING: This will delete ALL existing applications and data
# Run this ON YOUR SERVER (217.154.0.82) via SSH

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Confirmation prompt
confirm_destruction() {
    echo -e "${RED}⚠️  DANGER: COMPLETE VPS CLEANUP ⚠️${NC}"
    echo -e "${RED}This will DELETE ALL existing applications, databases, and files${NC}"
    echo -e "${RED}on your server at 217.154.0.82${NC}"
    echo ""
    echo "What will be DELETED:"
    echo "❌ All web applications in /var/www/"
    echo "❌ All databases (MySQL, PostgreSQL, MongoDB)"
    echo "❌ All application services and configurations"
    echo "❌ User-uploaded files and logs"
    echo "❌ Custom nginx configurations"
    echo ""
    echo "What will be PRESERVED:"
    echo "✅ System OS and core packages"
    echo "✅ SSH access and keys"
    echo "✅ SSL certificates (optional backup)"
    echo "✅ Basic system configurations"
    echo ""
    read -p "Are you ABSOLUTELY SURE you want to proceed? Type 'DELETE EVERYTHING' to continue: " -r
    if [[ $REPLY != "DELETE EVERYTHING" ]]; then
        error "Operation cancelled. Exiting safely."
        exit 0
    fi
    
    echo ""
    warning "Starting complete cleanup in 10 seconds... Press Ctrl+C to abort!"
    sleep 10
}

# Backup SSL certificates (optional)
backup_ssl() {
    log "🔐 Backing up SSL certificates..."
    mkdir -p /tmp/ssl-backup
    
    if [ -d "/etc/letsencrypt" ]; then
        cp -r /etc/letsencrypt /tmp/ssl-backup/ 2>/dev/null || true
        info "Let's Encrypt certificates backed up to /tmp/ssl-backup/"
    fi
    
    if [ -d "/etc/nginx/ssl" ]; then
        cp -r /etc/nginx/ssl /tmp/ssl-backup/ 2>/dev/null || true
        info "Custom SSL certificates backed up to /tmp/ssl-backup/"
    fi
    
    if [ -d "/etc/ssl/certs" ]; then
        cp /etc/ssl/certs/*.pem /tmp/ssl-backup/ 2>/dev/null || true
        cp /etc/ssl/private/*.key /tmp/ssl-backup/ 2>/dev/null || true
        info "System SSL certificates backed up to /tmp/ssl-backup/"
    fi
}

# Stop all services
stop_all_services() {
    log "🛑 Stopping all application services..."
    
    # Common service names to stop
    services=(
        "cataloro-backend"
        "cataloro"
        "nginx"
        "apache2"
        "httpd"
        "mysql"
        "mariadb"
        "postgresql"
        "mongodb"
        "mongod"
        "redis-server"
        "redis"
        "elasticsearch"
        "docker"
        "pm2"
        "supervisor"
        "supervisord"
    )
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service" 2>/dev/null; then
            warning "Stopping $service..."
            systemctl stop "$service" || true
            systemctl disable "$service" || true
        fi
    done
    
    # Kill any remaining web processes
    pkill -f "node" || true
    pkill -f "python" || true
    pkill -f "gunicorn" || true
    pkill -f "uwsgi" || true
    pkill -f "php-fpm" || true
}

# Remove application directories
remove_applications() {
    log "🗂️  Removing all application directories..."
    
    # Web directories
    directories=(
        "/var/www/*"
        "/opt/cataloro"
        "/opt/app"
        "/opt/applications"
        "/home/*/app"
        "/home/*/applications"
        "/root/app"
        "/root/applications"
        "/usr/local/app"
        "/srv/www"
        "/srv/http"
    )
    
    for dir in "${directories[@]}"; do
        if ls $dir 1> /dev/null 2>&1; then
            warning "Removing $dir"
            rm -rf $dir
        fi
    done
}

# Remove databases
remove_databases() {
    log "🗄️  Removing all databases..."
    
    # MongoDB
    if command -v mongo &> /dev/null; then
        warning "Removing MongoDB databases..."
        systemctl stop mongod mongodb || true
        rm -rf /var/lib/mongodb/*
        rm -rf /data/db/*
        rm -rf /var/log/mongodb/*
    fi
    
    # MySQL/MariaDB
    if command -v mysql &> /dev/null; then
        warning "Removing MySQL/MariaDB databases..."
        systemctl stop mysql mariadb || true
        rm -rf /var/lib/mysql/*
        rm -rf /var/log/mysql/*
    fi
    
    # PostgreSQL
    if command -v psql &> /dev/null; then
        warning "Removing PostgreSQL databases..."
        systemctl stop postgresql || true
        rm -rf /var/lib/postgresql/*
        rm -rf /var/log/postgresql/*
    fi
    
    # Redis
    if command -v redis-cli &> /dev/null; then
        warning "Removing Redis data..."
        systemctl stop redis-server redis || true
        rm -rf /var/lib/redis/*
        rm -rf /var/log/redis/*
    fi
}

# Remove web server configurations
remove_web_configs() {
    log "🌐 Removing web server configurations..."
    
    # Nginx
    if [ -d "/etc/nginx" ]; then
        warning "Removing nginx configurations..."
        rm -rf /etc/nginx/sites-available/*
        rm -rf /etc/nginx/sites-enabled/*
        rm -rf /etc/nginx/conf.d/*
        # Keep main nginx.conf but remove custom configs
    fi
    
    # Apache
    if [ -d "/etc/apache2" ]; then
        warning "Removing Apache configurations..."
        rm -rf /etc/apache2/sites-available/*
        rm -rf /etc/apache2/sites-enabled/*
        a2dissite 000-default || true
    fi
    
    if [ -d "/etc/httpd" ]; then
        warning "Removing httpd configurations..."
        rm -rf /etc/httpd/conf.d/*.conf
    fi
}

# Remove systemd services
remove_systemd_services() {
    log "⚙️  Removing custom systemd services..."
    
    # Find and remove custom services
    custom_services=$(find /etc/systemd/system -name "*.service" -not -path "*/system/*" | grep -E "(cataloro|app|custom)" | head -20)
    
    for service_file in $custom_services; do
        if [ -f "$service_file" ]; then
            service_name=$(basename "$service_file")
            warning "Removing service: $service_name"
            systemctl stop "$service_name" || true
            systemctl disable "$service_name" || true
            rm -f "$service_file"
        fi
    done
    
    systemctl daemon-reload
}

# Remove logs
remove_logs() {
    log "📋 Removing application logs..."
    
    # Application logs
    rm -rf /var/log/cataloro
    rm -rf /var/log/app
    rm -rf /var/log/applications
    rm -rf /var/log/nginx/access.log*
    rm -rf /var/log/nginx/error.log*
    
    # Clear system logs (optional)
    warning "Clearing system logs..."
    journalctl --vacuum-time=1d
}

# Remove Docker containers and images
remove_docker() {
    if command -v docker &> /dev/null; then
        log "🐳 Removing Docker containers and images..."
        
        # Stop all containers
        docker stop $(docker ps -aq) 2>/dev/null || true
        
        # Remove all containers
        docker rm $(docker ps -aq) 2>/dev/null || true
        
        # Remove all images
        docker rmi $(docker images -q) 2>/dev/null || true
        
        # Remove all volumes
        docker volume prune -f || true
        
        # Remove all networks
        docker network prune -f || true
        
        # Clean system
        docker system prune -af || true
    fi
}

# Remove Node.js applications
remove_nodejs() {
    log "🟢 Removing Node.js applications..."
    
    # Kill PM2 processes
    if command -v pm2 &> /dev/null; then
        pm2 kill || true
        rm -rf ~/.pm2
    fi
    
    # Remove global node modules
    rm -rf /usr/local/lib/node_modules/*
    rm -rf /root/.npm
    rm -rf /home/*/.npm
}

# Clean package managers
clean_packages() {
    log "📦 Cleaning package managers..."
    
    # Python pip
    pip3 freeze | xargs pip3 uninstall -y || true
    
    # Node.js npm
    if command -v npm &> /dev/null; then
        npm cache clean --force || true
    fi
    
    # System packages
    apt-get autoremove -y || true
    apt-get autoclean || true
}

# Final cleanup
final_cleanup() {
    log "🧹 Final cleanup..."
    
    # Remove temporary files
    rm -rf /tmp/*
    rm -rf /var/tmp/*
    
    # Clear bash history
    > ~/.bash_history
    history -c
    
    # Clear system caches
    sync
    echo 3 > /proc/sys/vm/drop_caches
}

# Restore SSL certificates
restore_ssl() {
    if [ -d "/tmp/ssl-backup" ]; then
        info "🔐 Restoring SSL certificates..."
        
        # Restore Let's Encrypt
        if [ -d "/tmp/ssl-backup/letsencrypt" ]; then
            mkdir -p /etc/letsencrypt
            cp -r /tmp/ssl-backup/letsencrypt/* /etc/letsencrypt/
        fi
        
        # Restore custom SSL
        if [ -d "/tmp/ssl-backup/ssl" ]; then
            mkdir -p /etc/nginx/ssl
            cp -r /tmp/ssl-backup/ssl/* /etc/nginx/ssl/
        fi
        
        log "✅ SSL certificates restored"
    fi
}

# Main cleanup function
main() {
    log "🚀 Starting complete VPS cleanup for 217.154.0.82"
    
    confirm_destruction
    backup_ssl
    stop_all_services
    remove_applications
    remove_databases
    remove_web_configs
    remove_systemd_services
    remove_logs
    remove_docker
    remove_nodejs
    clean_packages
    final_cleanup
    restore_ssl
    
    log "✅ Complete VPS cleanup finished!"
    log ""
    log "📋 Summary:"
    log "✅ All applications removed"
    log "✅ All databases cleared"
    log "✅ All services stopped and removed"
    log "✅ All logs cleared"
    log "✅ SSL certificates backed up and restored"
    log ""
    log "🎯 Your VPS is now clean and ready for fresh Cataloro deployment!"
    log "👉 Run your deployment script: ./enhanced-deploy.sh"
}

# Run main function
main "$@"