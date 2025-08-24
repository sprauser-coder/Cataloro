# Cataloro Deployment Guide - FIXED

## ✅ Issues Fixed

1. **Created missing deploy.sh script** with proper error handling
2. **Fixed hardcoded URLs** in setupProxy.js and App.js WebSocket connection
3. **Updated backend URL** to point to your production server (217.154.0.82)

## 🚀 Deployment Process

### Step 1: Save to GitHub
Use the "Save to GitHub" feature in the chat interface

### Step 2: Deploy on Production Server
```bash
ssh root@217.154.0.82
cd /var/www/cataloro
./deploy.sh
```

## 📋 What the deploy.sh script does:

1. **Git Pull**: Updates code from GitHub repository
2. **Backend Setup**: Installs Python dependencies from requirements.txt
3. **Frontend Setup**: Installs Node.js dependencies with yarn
4. **Build**: Creates production build of React frontend
5. **Restart**: Restarts services using PM2
6. **Status Check**: Shows current service status

## 🔧 Prerequisites on Production Server

Make sure these are installed on your VPS:
- Git
- Python3 & pip3
- Node.js & yarn
- PM2 process manager

## 🔍 Troubleshooting

If deployment fails:

1. **Check service status**: `pm2 status`
2. **View logs**: `pm2 logs`
3. **Restart specific service**: `pm2 restart [service-name]`
4. **Full restart**: `pm2 restart all`

## 🌐 URLs Configuration

- **Production URL**: http://217.154.0.82
- **Backend API**: http://217.154.0.82/api
- **WebSocket**: ws://217.154.0.82/api (automatically handled)

## ✅ Ready to Deploy!

Your deployment pipeline is now fixed and ready to use:
**Save to GitHub → SSH to server → Run ./deploy.sh**