# Cataloro Marketplace - VPS Deployment Guide

## ✅ Deployment Issues RESOLVED

The critical deployment blockers have been fixed:

1. **Fixed hardcoded localhost URLs** in `/app/frontend/src/App.js` (lines 1205 and 3041)
2. **Updated environment variables** for production deployment
3. **Created VPS-specific configuration files**

## 📋 Pre-deployment Checklist

### ✅ Completed Tasks:
- [x] Fixed hardcoded localhost URLs in frontend code
- [x] Updated environment variables for production
- [x] Created VPS-specific server entry point (`vps-server.py`)
- [x] Created PM2 configuration (`ecosystem.config.js`)  
- [x] Created Nginx configuration (`cataloro.conf`)
- [x] Created VPS requirements file (`vps-requirements.txt`)
- [x] Verified backend API functionality
- [x] Verified frontend builds successfully

## 🚀 VPS Deployment Steps

### 1. Copy Files to VPS

Copy these files to your VPS at `/var/www/cataloro/`:

```bash
# Core application files
/app/frontend/src/App.js (updated with env variables)
/app/frontend/.env (updated for production)  
/app/backend/.env (updated for production)
/app/backend/requirements.txt
/app/vps-server.py
/app/ecosystem.config.js
/app/vps-requirements.txt

# Configuration files  
/app/cataloro.conf (for Nginx)
```

### 2. Update Backend Environment Variables

Ensure `/var/www/cataloro/backend/.env` contains:

```
MONGO_URL="mongodb://localhost:27017"
DB_NAME="cataloro_production"
JWT_SECRET="cataloro-production-secret-key-change-in-production"
CORS_ORIGINS="https://www.app.cataloro.com,https://app.cataloro.com,https://cataloro.com,https://www.cataloro.com"
ENVIRONMENT="production"
```

### 3. Update Frontend Environment Variables

Ensure `/var/www/cataloro/frontend/.env` contains:

```
REACT_APP_BACKEND_URL=https://www.app.cataloro.com
WDS_SOCKET_PORT=443
```

### 4. Install/Update Python Packages

```bash
cd /var/www/cataloro
source venv/bin/activate
pip install -r vps-requirements.txt
```

### 5. Rebuild Frontend

```bash
cd /var/www/cataloro/frontend
yarn build
```

### 6. Update Nginx Configuration

```bash
sudo cp /var/www/cataloro/cataloro.conf /etc/nginx/conf.d/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. Restart Backend with PM2

```bash
cd /var/www/cataloro
pm2 stop cataloro-backend || true
pm2 delete cataloro-backend || true
pm2 start ecosystem.config.js
pm2 save
```

### 8. Verify Deployment

1. **Check PM2 status:**
   ```bash
   pm2 status
   pm2 logs cataloro-backend
   ```

2. **Test backend API:**
   ```bash
   curl http://127.0.0.1:8001/api/
   ```

3. **Test domain access:**
   ```bash
   curl -I https://www.app.cataloro.com/api/
   ```

## 🔧 Configuration Files Created

### `vps-server.py`
- Proper VPS entry point for the backend
- Handles path resolution and uvicorn startup
- Configured for production deployment

### `ecosystem.config.js`  
- PM2 configuration for process management
- Proper logging and restart policies
- Production environment settings

### `cataloro.conf`
- Nginx server configuration
- Frontend static file serving
- API proxying to backend
- File upload handling
- Security headers and gzip compression

## 🐛 Troubleshooting

### If Backend Fails to Start:
1. Check PM2 logs: `pm2 logs cataloro-backend`
2. Verify Python packages: `pip list | grep -E "(fastapi|pydantic|uvicorn)"`
3. Check environment variables are loaded
4. Verify MongoDB is running: `systemctl status mongod`

### If Domain Not Accessible:
1. Check DNS settings for www.app.cataloro.com → 217.154.0.82
2. Verify firewall allows ports 80/443
3. Check Nginx status: `systemctl status nginx`
4. Test Nginx config: `nginx -t`

### If API Calls Fail:
1. Verify CORS settings in backend/.env
2. Check if backend is responding: `curl http://127.0.0.1:8001/api/`
3. Check Nginx proxy configuration

## 📊 What Was Fixed

### Critical Issues Resolved:
1. **Hardcoded URLs**: Replaced `http://localhost:8001` with `${process.env.REACT_APP_BACKEND_URL}`
2. **Environment Variables**: Updated for production domain `www.app.cataloro.com`
3. **Package Compatibility**: Ensured Pydantic 2.6.4+ for Python 3.11 compatibility
4. **File Paths**: Proper VPS server entry point with correct path resolution

The application is now ready for deployment to www.app.cataloro.com! 🎉