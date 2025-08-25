# Cataloro Marketplace - Production Deployment Configuration

## Server: 217.154.0.82

### ✅ CORRECT CONFIGURATION (Based on Previous Working Solutions)

**Frontend Configuration (.env):**
```
REACT_APP_BACKEND_URL=http://217.154.0.82
WDS_SOCKET_PORT=443
```

**Backend Configuration (.env):**
```
MONGO_URL="mongodb://localhost:27017"
DB_NAME="cataloro_production"
JWT_SECRET="cataloro-dev-secret-key"
CORS_ORIGINS="http://217.154.0.82,https://217.154.0.82"
ENVIRONMENT="production"
```

### 🔄 KEY INSIGHT FROM TEST RESULTS

**CRITICAL:** The backend runs on port 8001 internally but is accessible externally on the default HTTP port (80/443). This is why the frontend URL should be `http://217.154.0.82` **WITHOUT** the port number.

### Deployment Steps

1. **Update Frontend .env:**
   ```bash
   echo 'REACT_APP_BACKEND_URL=http://217.154.0.82' > /app/frontend/.env
   echo 'WDS_SOCKET_PORT=443' >> /app/frontend/.env
   ```

2. **Update Backend .env:**
   ```bash
   cat > /app/backend/.env << EOF
   MONGO_URL="mongodb://localhost:27017"
   DB_NAME="cataloro_production"
   JWT_SECRET="cataloro-dev-secret-key"
   CORS_ORIGINS="http://217.154.0.82,https://217.154.0.82"
   ENVIRONMENT="production"
   EOF
   ```

3. **Build Frontend for Production:**
   ```bash
   cd /app/frontend && yarn build
   ```

4. **Restart All Services:**
   ```bash
   sudo supervisorctl restart all
   ```

### Access URLs After Deployment

- **Frontend:** http://217.154.0.82 (not :3000)
- **Backend API:** http://217.154.0.82/api (not :8001/api)  
- **Admin Panel:** http://217.154.0.82/#/admin

### ❌ COMMON MISTAKES TO AVOID

1. **DO NOT** add port numbers to frontend URLs
2. **DO NOT** use :8001 in REACT_APP_BACKEND_URL
3. **DO NOT** use :3000 in CORS_ORIGINS
4. **DO NOT** use localhost or emergent URLs for production

### ✅ VERIFIED WORKING CONFIGURATION

This configuration is based on successful test results from `test_result.md` showing:
- Authentication working with `http://217.154.0.82`
- Image uploads successful
- All API endpoints accessible 
- CORS properly configured

### Login Credentials

- **Admin User:** admin@marketplace.com / admin123