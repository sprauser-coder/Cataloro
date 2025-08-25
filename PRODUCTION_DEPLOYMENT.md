# Cataloro Marketplace - Production Deployment Configuration

## Server: 217.154.0.82

### Frontend Configuration (.env)
```
REACT_APP_BACKEND_URL=http://217.154.0.82:8001
WDS_SOCKET_PORT=443
```

### Backend Configuration (.env)
```
MONGO_URL="mongodb://localhost:27017"
DB_NAME="cataloro_production"
JWT_SECRET="cataloro-dev-secret-key"
CORS_ORIGINS="http://217.154.0.82:3000,http://217.154.0.82,https://217.154.0.82:3000,https://217.154.0.82"
ENVIRONMENT="production"
```

### Deployment Steps

1. **Update Frontend .env:**
   ```bash
   echo 'REACT_APP_BACKEND_URL=http://217.154.0.82:8001' > /app/frontend/.env
   echo 'WDS_SOCKET_PORT=443' >> /app/frontend/.env
   ```

2. **Update Backend .env:**
   ```bash
   cat > /app/backend/.env << EOF
   MONGO_URL="mongodb://localhost:27017"
   DB_NAME="cataloro_production"
   JWT_SECRET="cataloro-dev-secret-key"
   CORS_ORIGINS="http://217.154.0.82:3000,http://217.154.0.82,https://217.154.0.82:3000,https://217.154.0.82"
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

- **Frontend:** http://217.154.0.82:3000
- **Backend API:** http://217.154.0.82:8001/api
- **Admin Panel:** http://217.154.0.82:3000/#/admin

### Login Credentials

- **Admin User:** admin@marketplace.com / admin123

### Verified Features

✅ Login system fully functional
✅ Admin panel accessible and working
✅ All images loading correctly (logo, listings, hero)
✅ Backend API connectivity established
✅ Image uploads working
✅ Listings display correctly
✅ Production build completed

### Important Notes

1. Make sure port 3000 and 8001 are open on your server
2. MongoDB should be running on localhost:27017
3. All static assets (images) are served correctly
4. CORS is properly configured for your server IP