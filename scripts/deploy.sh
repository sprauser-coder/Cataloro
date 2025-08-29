#!/bin/bash

# CATALORO - Deployment Script
# Automated deployment to SSH server at 217.154.0.82

set -e  # Exit on any error

# Configuration
SSH_HOST="217.154.0.82"
SSH_USER="root"  # Change this to your SSH user
DEPLOY_PATH="/var/www/cataloro"
APP_NAME="cataloro"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Cataloro Deployment...${NC}"

# Step 1: Build the application
echo -e "${YELLOW}📦 Building application...${NC}"
cd /app/frontend
yarn build

cd /app/backend
pip freeze > requirements.txt

# Step 2: Create deployment package
echo -e "${YELLOW}📁 Creating deployment package...${NC}"
cd /app
tar -czf cataloro-deploy.tar.gz \
  --exclude=node_modules \
  --exclude=__pycache__ \
  --exclude=.git \
  --exclude=.emergent \
  frontend/build \
  backend \
  config \
  scripts

# Step 3: Upload to server
echo -e "${YELLOW}🌐 Uploading to server...${NC}"
scp cataloro-deploy.tar.gz ${SSH_USER}@${SSH_HOST}:/tmp/

# Step 4: Deploy on server
echo -e "${YELLOW}🔧 Deploying on server...${NC}"
ssh ${SSH_USER}@${SSH_HOST} << 'ENDSSH'
set -e

# Create deployment directory
sudo mkdir -p /var/www/cataloro
cd /var/www/cataloro

# Backup existing deployment (if any)
if [ -d "current" ]; then
  sudo mv current backup-$(date +%Y%m%d-%H%M%S)
fi

# Extract new deployment
sudo tar -xzf /tmp/cataloro-deploy.tar.gz
sudo mv cataloro-deploy current

# Set permissions
sudo chown -R www-data:www-data current/
sudo chmod -R 755 current/

# Install backend dependencies
cd current/backend
sudo pip3 install -r requirements.txt

# Configure Nginx (if needed)
sudo tee /etc/nginx/sites-available/cataloro > /dev/null <<EOL
server {
    listen 80;
    server_name 217.154.0.82;
    root /var/www/cataloro/current/frontend/build;
    index index.html;

    # Frontend routes
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API routes
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOL

# Enable site
sudo ln -sf /etc/nginx/sites-available/cataloro /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Configure systemd service for backend
sudo tee /etc/systemd/system/cataloro-backend.service > /dev/null <<EOL
[Unit]
Description=Cataloro Backend API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/cataloro/current/backend
Environment=PATH=/usr/bin:/usr/local/bin
Environment=MONGO_URL=mongodb://localhost:27017
ExecStart=/usr/bin/python3 -m uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Start backend service
sudo systemctl daemon-reload
sudo systemctl enable cataloro-backend
sudo systemctl restart cataloro-backend

# Clean up
rm -f /tmp/cataloro-deploy.tar.gz

echo "✅ Deployment completed successfully!"
echo "🌐 Frontend: http://217.154.0.82"
echo "🔌 Backend API: http://217.154.0.82/api"

ENDSSH

# Step 5: Cleanup local files
echo -e "${YELLOW}🧹 Cleaning up...${NC}"
rm -f cataloro-deploy.tar.gz

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Your application is now live at: http://217.154.0.82${NC}"
echo -e "${GREEN}🔌 API endpoints available at: http://217.154.0.82/api${NC}"

# Step 6: Health check
echo -e "${YELLOW}🏥 Running health check...${NC}"
sleep 5
if curl -s http://217.154.0.82/api/health > /dev/null; then
  echo -e "${GREEN}✅ Backend is healthy and responding${NC}"
else
  echo -e "${RED}❌ Backend health check failed${NC}"
fi

echo -e "${GREEN}🎉 Cataloro deployment complete!${NC}"