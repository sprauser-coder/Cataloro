#!/bin/bash

# CATALORO PRODUCTION DEPLOYMENT SCRIPT
# Target Server: 217.154.0.82
# Individual User Statistics System - Version 1.5.1

set -e  # Exit on any error

echo "🚀 CATALORO PRODUCTION DEPLOYMENT STARTING..."
echo "Target: http://217.154.0.82"
echo "Version: 1.5.1 (Individual User Statistics Fix)"
echo "Date: $(date)"
echo "=========================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Create backup directory
BACKUP_DIR="/backup/cataloro-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

print_info "Created backup directory: $BACKUP_DIR"

# Step 1: Backup existing data
print_info "STEP 1: Backing up existing data..."

if [ -d "/app" ]; then
    print_info "Backing up application files..."
    tar -czf "$BACKUP_DIR/app-backup.tar.gz" /app/ 2>/dev/null || print_warning "App backup failed (may not exist)"
fi

if command -v mongodump &> /dev/null; then
    print_info "Backing up MongoDB database..."
    mongodump --db cataloro_production --out "$BACKUP_DIR/mongodb-backup" 2>/dev/null || print_warning "MongoDB backup failed (may not exist)"
fi

print_status "Backup completed in $BACKUP_DIR"

# Step 2: Stop existing services
print_info "STEP 2: Stopping existing services..."

systemctl stop nginx 2>/dev/null || print_warning "Nginx not running"
systemctl stop cataloro-backend 2>/dev/null || print_warning "Backend service not found"
systemctl stop cataloro-frontend 2>/dev/null || print_warning "Frontend service not found"

# Kill any existing processes on ports 8001 and 3000
pkill -f "uvicorn.*8001" 2>/dev/null || true
pkill -f "serve.*3000" 2>/dev/null || true

print_status "Services stopped"

# Step 3: Install system dependencies
print_info "STEP 3: Installing system dependencies..."

# Update package list
apt-get update -qq

# Install required packages
apt-get install -y \
    nginx \
    mongodb-server \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    curl \
    jq \
    openssl 2>/dev/null

# Install Node.js 18+ if needed
if ! node --version | grep -q "v1[8-9]\|v[2-9][0-9]"; then
    print_info "Installing Node.js 18..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
fi

print_status "System dependencies installed"

# Step 4: Setup Python virtual environment
print_info "STEP 4: Setting up Python environment..."

if [ ! -d "/root/.venv" ]; then
    python3 -m venv /root/.venv
fi

source /root/.venv/bin/activate
pip install --upgrade pip

print_status "Python environment ready"

# Step 5: Create directory structure
print_info "STEP 5: Creating application structure..."

mkdir -p /app/{backend,frontend}
mkdir -p /app/backend/uploads
mkdir -p /var/log/cataloro

print_status "Directory structure created"

# Step 6: Install backend dependencies
print_info "STEP 6: Installing backend dependencies..."

cd /app/backend

# Create requirements.txt if not present
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
motor==3.3.2
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic==2.5.0
python-decouple==3.8
pillow==10.1.0
aiofiles==23.2.1
pymongo==4.6.0
bcrypt==4.1.2
python-dotenv==1.0.0
EOF

pip install -r requirements.txt

print_status "Backend dependencies installed"

# Step 7: Configure backend environment
print_info "STEP 7: Configuring backend environment..."

# Generate secure JWT secret
JWT_SECRET=$(openssl rand -hex 32)

cat > /app/backend/.env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="cataloro_production"
JWT_SECRET="$JWT_SECRET"
CORS_ORIGINS="http://217.154.0.82,https://217.154.0.82"
ENVIRONMENT="production"
EOF

print_status "Backend environment configured"

# Step 8: Install frontend dependencies
print_info "STEP 8: Installing frontend dependencies..."

cd /app/frontend

# Create package.json if not present
cat > package.json << 'EOF'
{
  "name": "cataloro-frontend",
  "version": "1.5.1",
  "private": true,
  "dependencies": {
    "@craco/craco": "^7.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.0",
    "lucide-react": "^0.294.0",
    "serve": "^14.2.1"
  },
  "scripts": {
    "start": "craco start",
    "build": "craco build",
    "test": "craco test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF

npm install

print_status "Frontend dependencies installed"

# Step 9: Configure frontend environment
print_info "STEP 9: Configuring frontend environment..."

cat > /app/frontend/.env << 'EOF'
REACT_APP_BACKEND_URL=http://217.154.0.82
WDS_SOCKET_PORT=443
EOF

print_status "Frontend environment configured"

# Step 10: Start MongoDB
print_info "STEP 10: Starting MongoDB..."

systemctl start mongod
systemctl enable mongod

# Wait for MongoDB to start
sleep 5

# Test MongoDB connection
if mongosh --eval "db.runCommand({ping: 1})" > /dev/null 2>&1; then
    print_status "MongoDB is running"
else
    print_error "MongoDB failed to start"
    exit 1
fi

# Step 11: Create systemd services
print_info "STEP 11: Creating system services..."

# Backend service
cat > /etc/systemd/system/cataloro-backend.service << 'EOF'
[Unit]
Description=Cataloro Backend API
After=network.target mongod.service

[Service]
Type=simple
User=root
WorkingDirectory=/app/backend
Environment=PATH=/root/.venv/bin
ExecStart=/root/.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1
Restart=always
RestartSec=3
StandardOutput=append:/var/log/cataloro/backend.log
StandardError=append:/var/log/cataloro/backend-error.log

[Install]
WantedBy=multi-user.target
EOF

# Frontend service
cat > /etc/systemd/system/cataloro-frontend.service << 'EOF'
[Unit]
Description=Cataloro Frontend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/app/frontend
ExecStart=/app/frontend/node_modules/.bin/serve -s build -p 3000 -n
Restart=always
RestartSec=3
StandardOutput=append:/var/log/cataloro/frontend.log
StandardError=append:/var/log/cataloro/frontend-error.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

print_status "System services created"

# Step 12: Configure Nginx
print_info "STEP 12: Configuring Nginx..."

cat > /etc/nginx/sites-available/cataloro << 'EOF'
server {
    listen 80;
    server_name 217.154.0.82;

    client_max_body_size 100M;

    # Frontend (React app)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Disable caching for HTML files
        location ~* \.(html|htm)$ {
            proxy_pass http://localhost:3000;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
            add_header Pragma "no-cache";
            add_header Expires "0";
        }
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Disable caching for API endpoints
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

    # Static files (uploads)
    location /uploads {
        proxy_pass http://localhost:8001/uploads;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
EOF

# Remove default nginx site
rm -f /etc/nginx/sites-enabled/default

# Enable Cataloro site
ln -sf /etc/nginx/sites-available/cataloro /etc/nginx/sites-enabled/

# Test nginx configuration
if nginx -t; then
    print_status "Nginx configuration is valid"
else
    print_error "Nginx configuration is invalid"
    exit 1
fi

# Step 13: Deploy message
print_info "STEP 13: Ready for application deployment..."

cat << 'EOF'

=================================================================
🎯 DEPLOYMENT INFRASTRUCTURE READY!

Next steps:
1. Copy your application files to:
   - Backend files → /app/backend/
   - Frontend files → /app/frontend/

2. Build frontend:
   cd /app/frontend && npm run build

3. Start services:
   systemctl enable cataloro-backend cataloro-frontend
   systemctl start cataloro-backend cataloro-frontend nginx

4. Test deployment:
   curl http://217.154.0.82/api/

=================================================================
EOF

print_status "Deployment infrastructure setup completed!"
print_info "Backup location: $BACKUP_DIR"
print_info "Log files: /var/log/cataloro/"

echo "🎉 Ready for application deployment!"