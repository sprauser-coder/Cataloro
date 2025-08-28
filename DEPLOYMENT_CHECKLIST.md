# Cataloro Marketplace - Deployment Checklist v1.6.5

## 🔥 **CRITICAL TROUBLESHOOTING SOLUTIONS** 🔥

### **💜 PURPLE MODERN DESIGN DEPLOYMENT ISSUES**

**PROBLEM**: Purple design changes not appearing after deployment  
**ROOT CAUSE**: Deploy script missing GitHub code pulling  
**SOLUTION**: 
```bash
# 1. Fix deploy.sh to include GitHub pull
nano deploy.sh
# Add these lines after directory verification:
echo "📥 Pulling latest code from GitHub..."
git fetch origin
git reset --hard origin/main
```

**PREVENTION**: Always ensure deploy.sh includes git pull step

---

### **🔐 LOGIN/BACKEND CONNECTION ISSUES**

**PROBLEM**: "Internal Server Error" on login attempts  
**ROOT CAUSE**: Backend trying to connect to MongoDB at wrong address  
**SYMPTOMS**: 
- Login form appears but fails with errors
- Backend API returns 500 errors
- `curl -X POST http://217.154.0.82/api/auth/login` fails

**SOLUTION**:
```bash
# Fix backend/.env MongoDB URL
cd /var/www/cataloro/backend
nano .env
# Change: MONGO_URL=mongodb://217.154.0.82:27017
# To:     MONGO_URL=mongodb://localhost:27017
```

**VERIFICATION**:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"email":"admin@marketplace.com","password":"admin123"}' http://217.154.0.82/api/auth/login
# Should return JWT token, not "Internal Server Error"
```

---

### **📁 FILE PERMISSIONS ISSUES**

**PROBLEM**: `./deploy.sh: Permission denied`  
**SOLUTION**:
```bash
chmod +x deploy.sh
```

**PREVENTION**: Always run `chmod +x` after creating/updating shell scripts

---

### **🚀 COMPLETE DEPLOYMENT FIXES**

**ENHANCED deploy.sh** (includes all critical fixes):
```bash
#!/bin/bash

# Cataloro Deployment Script - FOR PRODUCTION ENVIRONMENT (/var/www/cataloro)
echo "🚀 Starting Cataloro deployment..."

PROJECT_ROOT="/var/www/cataloro"
cd "$PROJECT_ROOT"

# Verify directory
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ Error: Not in the correct project directory."
    exit 1
fi

# CRITICAL: Pull latest code from GitHub
echo "📥 Pulling latest code from GitHub..."
git fetch origin
git reset --hard origin/main

if [ $? -ne 0 ]; then
    echo "❌ Git pull failed."
    exit 1
fi

# CRITICAL FIX: Configure backend for production MongoDB
echo "🔧 Configuring backend for production..."
cd "$PROJECT_ROOT/backend"

cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=cataloro_production
JWT_SECRET=cataloro-dev-secret-key
CORS_ORIGINS=http://217.154.0.82,https://217.154.0.82
ENVIRONMENT=production
BACKEND_BASE_URL=http://217.154.0.82
EOF

echo "✅ Backend environment configured"

# Install backend dependencies
cd "$PROJECT_ROOT/backend"
pip3 install -r requirements.txt

# Install frontend dependencies and build
cd "$PROJECT_ROOT/frontend"
yarn install --production=false
yarn build

# Restart services
cd "$PROJECT_ROOT"
pm2 stop cataloro-backend cataloro-frontend 2>/dev/null || true
pm2 delete cataloro-backend cataloro-frontend 2>/dev/null || true
pm2 start ecosystem.config.js

echo "✅ Deployment completed!"
pm2 status
```

---

### **🔍 DIAGNOSTIC COMMANDS**

**Check if services are running**:
```bash
pm2 status
```

**Test backend API**:
```bash
curl http://217.154.0.82/api/
# Should return: {"message":"Marketplace API","version":"v1.6.5"}
```

**Test login endpoint**:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"email":"admin@marketplace.com","password":"admin123"}' http://217.154.0.82/api/auth/login
# Should return JWT token, not "Internal Server Error"
```

**Check if MongoDB is running**:
```bash
systemctl status mongod
# or
ps aux | grep mongo
```

**Check logs**:
```bash
pm2 logs cataloro-backend
pm2 logs cataloro-frontend
```

---

### **🎨 PURPLE DESIGN VERIFICATION**

**Files that contain purple styling**:
- `/frontend/src/index.css` - Core purple variables and styles
- `/frontend/src/App.css` - Purple animations and components  
- `/frontend/tailwind.config.js` - Purple color palette
- `/frontend/src/App.js` - Purple CSS classes

**Verification steps**:
1. Check CSS build contains purple styles: `grep -i purple /var/www/cataloro/frontend/build/static/css/*.css`
2. Visit site and verify purple elements visible
3. Login should show purple gradient background and purple button

---

### **⚠️ COMMON DEPLOYMENT PITFALLS**

1. **Missing Git Pull**: Deploy script rebuilds same old files
   - **Fix**: Always include `git fetch origin && git reset --hard origin/main`

2. **Wrong MongoDB URL**: Backend can't connect to database
   - **Fix**: Use `mongodb://localhost:27017` not external IP

3. **Missing Execute Permission**: Scripts won't run
   - **Fix**: `chmod +x deploy.sh`

4. **CSS Not Updating**: Browser cache or build issues
   - **Fix**: Force rebuild with `yarn build` and clear browser cache

5. **PM2 Process Issues**: Old processes preventing restart
   - **Fix**: `pm2 delete all && pm2 start ecosystem.config.js`

---

### **✅ DEPLOYMENT SUCCESS CHECKLIST**

- [ ] Git pull works (`git fetch origin && git reset --hard origin/main`)
- [ ] Backend .env has `MONGO_URL=mongodb://localhost:27017`
- [ ] Deploy script is executable (`chmod +x deploy.sh`)
- [ ] PM2 services show "online" status
- [ ] API endpoint responds: `curl http://217.154.0.82/api/`
- [ ] Login works: Test with admin@marketplace.com/admin123
- [ ] Purple design visible on website
- [ ] CSS build contains purple styles

---

### **🆘 EMERGENCY RECOVERY**

If deployment completely fails:

1. **Reset to working state**:
   ```bash
   cd /var/www/cataloro
   git reset --hard HEAD~1
   ./deploy.sh
   ```

2. **Manual service restart**:
   ```bash
   pm2 delete all
   pm2 start ecosystem.config.js
   ```

3. **Check all processes**:
   ```bash
   pm2 status
   systemctl status mongod
   ```

---

## 🎯 **DEPLOYMENT RULES COMPLIANCE**

- ✅ **No Ports**: All URLs use standard HTTP without port numbers
- ✅ **No /app paths**: No development path references  
- ✅ **Host is always 217.154.0.82**: All configurations use deployment IP only
- ✅ **MongoDB Local**: Database connects to localhost:27017
- ✅ **GitHub Sync**: Deploy script pulls latest code before building

**Last Updated**: August 28, 2025 - Complete Troubleshooting Guide  
**Version**: 1.6.5 - Purple Modern Edition - BATTLE TESTED ⚔️