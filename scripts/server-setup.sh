#!/bin/bash

# Server Setup Script for Cataloro Deployment
# Run this on your server (217.154.0.82) to prepare it for deployment

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

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

log "🔧 Setting up server for Cataloro deployment..."

# Update system
log "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install required packages
log "📦 Installing required packages..."
apt-get install -y \
    nginx \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    mongodb \
    redis-server \
    curl \
    wget \
    git \
    unzip \
    supervisor \
    certbot \
    python3-certbot-nginx

# Install yarn
log "📦 Installing Yarn..."
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
apt-get update && apt-get install -y yarn

# Create application directory
log "📁 Creating application directories..."
mkdir -p /var/www/cataloro/{current,backups,logs}
mkdir -p /var/log/cataloro

# Create www-data user if it doesn't exist
if ! id "www-data" &>/dev/null; then
    useradd -r -s /bin/false www-data
fi

# Set permissions
chown -R www-data:www-data /var/www/cataloro
chown -R www-data:www-data /var/log/cataloro

# Configure MongoDB
log "🍃 Configuring MongoDB..."
systemctl enable mongodb
systemctl start mongodb

# Create MongoDB database and user
mongo << 'EOF'
use cataloro_marketplace
db.createUser({
  user: "cataloro_user",
  pwd: "cataloro_password_change_this",
  roles: [{role: "readWrite", db: "cataloro_marketplace"}]
})
EOF

# Configure Redis
log "📮 Configuring Redis..."
systemctl enable redis-server
systemctl start redis-server

# Configure Nginx
log "🌐 Configuring Nginx..."
# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Create basic nginx configuration
cat > /etc/nginx/sites-available/cataloro << 'EOF'
server {
    listen 80;
    server_name 217.154.0.82 cataloro.com www.cataloro.com;
    
    location / {
        root /var/www/cataloro/current/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/cataloro /etc/nginx/sites-enabled/
nginx -t
systemctl enable nginx
systemctl reload nginx

# Configure firewall
log "🔥 Configuring firewall..."
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 27017  # MongoDB
ufw --force enable

# Create log rotation
log "📋 Setting up log rotation..."
cat > /etc/logrotate.d/cataloro << 'EOF'
/var/log/cataloro/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload cataloro-backend
    endscript
}
EOF

# Set up SSL certificate (Let's Encrypt)
setup_ssl() {
    log "🔐 Setting up SSL certificate..."
    info "This will set up Let's Encrypt SSL for cataloro.com"
    read -p "Do you want to set up SSL now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        certbot --nginx -d cataloro.com -d www.cataloro.com
        
        # Set up auto-renewal
        crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | crontab -
    else
        info "SSL setup skipped. You can run 'certbot --nginx -d cataloro.com -d www.cataloro.com' later."
    fi
}

# Create environment file template
log "⚙️  Creating environment template..."
cat > /var/www/cataloro/.env.template << 'EOF'
# Production Environment Variables
MONGO_URL=mongodb://cataloro_user:cataloro_password_change_this@localhost:27017/cataloro_marketplace
REDIS_URL=redis://localhost:6379
NODE_ENV=production
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
SESSION_SECRET=your-session-secret-change-this
LOG_LEVEL=INFO
LOG_FILE=/var/log/cataloro/application.log
EOF

log "✅ Server setup completed!"
log ""
log "📋 Next steps:"
log "1. Copy /var/www/cataloro/.env.template to /var/www/cataloro/.env and configure it"
log "2. Change MongoDB password: mongo cataloro_marketplace -u cataloro_user -p"
log "3. Run your deployment script from your local machine"
log "4. Optionally set up SSL certificate"
log ""
log "🔧 Useful commands:"
log "• Check service status: systemctl status cataloro-backend"
log "• View logs: journalctl -u cataloro-backend -f"
log "• Check nginx status: systemctl status nginx"
log "• Test nginx config: nginx -t"

# Offer to set up SSL
setup_ssl