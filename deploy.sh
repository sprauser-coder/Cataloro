#!/bin/bash

# Cataloro Deployment Script - FOR PRODUCTION ENVIRONMENT (/var/www/cataloro)
echo "🚀 Starting Cataloro deployment..."

# PRODUCTION: Use actual production project root path
PROJECT_ROOT="/var/www/cataloro"
cd "$PROJECT_ROOT"

# Verify we're in the right directory
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ Error: Not in the correct project directory. Expected frontend/ and backend/ folders."
    echo "Current directory: $(pwd)"
    exit 1
fi

# CRITICAL: Pull latest code from GitHub
echo "📥 Pulling latest code from GitHub..."
git fetch origin
git reset --hard origin/main

# Check if git pull was successful
if [ $? -ne 0 ]; then
    echo "❌ Git pull failed. Please check GitHub connection and repository status."
    exit 1
fi

echo "✅ Latest code pulled successfully from GitHub"

# CRITICAL FIX: Update backend .env for production MongoDB
echo "🔧 Configuring backend for production..."
cd "$PROJECT_ROOT/backend"

# Ensure .env exists and has correct MongoDB URL for production
cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=cataloro_production
JWT_SECRET=cataloro-dev-secret-key
CORS_ORIGINS=http://217.154.0.82,https://217.154.0.82
ENVIRONMENT=production
BACKEND_BASE_URL=http://217.154.0.82
EOF

echo "✅ Backend environment configured for production"

# Show current version info
echo "📋 Version Info:"
if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
    grep -n "version" "$PROJECT_ROOT/frontend/package.json" | head -1
fi
if [ -f "$PROJECT_ROOT/backend/server.py" ]; then
    grep -n "version.*v1" "$PROJECT_ROOT/backend/server.py"
fi

# Navigate to backend and install Python dependencies
echo "🐍 Installing backend dependencies..."
cd "$PROJECT_ROOT/backend"

# Verify we're in backend directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found in $(pwd)"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Check if backend install was successful
if [ $? -ne 0 ]; then
    echo "❌ Backend dependency installation failed."
    exit 1
fi

# Navigate to frontend and install Node dependencies  
echo "📦 Installing frontend dependencies..."
cd "$PROJECT_ROOT/frontend"

# Verify we're in frontend directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found in $(pwd)"
    exit 1
fi

yarn install --production=false

# Build the frontend
echo "🏗️ Building frontend..."
yarn build

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed. Please check for build errors."
    exit 1
fi

# PRODUCTION: Use PM2 for service management
echo "🔄 Restarting services using PM2..."
cd "$PROJECT_ROOT"

# Create logs directory if it doesn't exist
mkdir -p logs

# Verify ecosystem.config.js exists
if [ ! -f "ecosystem.config.js" ]; then
    echo "❌ Error: ecosystem.config.js not found in $(pwd)"
    exit 1
fi

# Stop errored processes first
pm2 stop cataloro-backend 2>/dev/null || true
pm2 delete cataloro-backend 2>/dev/null || true

# Restart services
pm2 start ecosystem.config.js

# Check PM2 status
echo "📊 Checking service status..."
pm2 status

echo "✅ Deployment completed successfully!"
echo "🌐 Your application should now be updated at http://217.154.0.82"

# Show final version confirmation
echo "🎯 Deployed Version:"
if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
    grep "version" "$PROJECT_ROOT/frontend/package.json" | head -1
fi