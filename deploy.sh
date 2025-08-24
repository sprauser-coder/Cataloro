#!/bin/bash

# Cataloro Deployment Script
echo "🚀 Starting Cataloro deployment..."

# Update from git
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Check if git pull was successful
if [ $? -ne 0 ]; then
    echo "❌ Git pull failed. Please check your repository setup."
    exit 1
fi

# Navigate to backend and install Python dependencies
echo "🐍 Installing backend dependencies..."
cd /var/www/cataloro/backend
pip3 install -r requirements.txt

# Navigate to frontend and install Node dependencies  
echo "📦 Installing frontend dependencies..."
cd /var/www/cataloro/frontend
yarn install --production=false

# Build the frontend
echo "🏗️ Building frontend..."
yarn build

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed. Please check for build errors."
    exit 1
fi

# Restart services using PM2
echo "🔄 Restarting services..."
cd /var/www/cataloro
pm2 restart ecosystem.config.js

# Check PM2 status
echo "📊 Checking service status..."
pm2 status

echo "✅ Deployment completed successfully!"
echo "🌐 Your application should now be updated at http://217.154.0.82"