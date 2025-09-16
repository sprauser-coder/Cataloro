# Cataloro Marketplace Deployment Guide

This guide will help you deploy the Cataloro Marketplace application to your server at `217.154.0.82` with the domain `cataloro.com`.

## 📋 Prerequisites

1. **Server Access**: SSH access to your server at `217.154.0.82`
2. **Domain Setup**: DNS A-record pointing `cataloro.com` to `217.154.0.82`
3. **SSL Certificate**: Existing SSL certificate or Let's Encrypt setup

## 🚀 Deployment Methods

### Method 1: Full Automated Deployment (Recommended)

**Step 1: Prepare Your Server**
```bash
# Run this ON YOUR SERVER (217.154.0.82)
chmod +x /app/scripts/server-setup.sh
scp /app/scripts/server-setup.sh root@217.154.0.82:/tmp/
ssh root@217.154.0.82 "bash /tmp/server-setup.sh"
```

**Step 2: Deploy the Application**
```bash
# Run this FROM YOUR LOCAL MACHINE (or Emergent environment)
chmod +x /app/scripts/enhanced-deploy.sh
./app/scripts/enhanced-deploy.sh
```

### Method 2: Docker Deployment

**Step 1: Copy Files to Server**
```bash
scp -r /app/* root@217.154.0.82:/var/www/cataloro/
```

**Step 2: Deploy with Docker**
```bash
ssh root@217.154.0.82
cd /var/www/cataloro
docker-compose up -d
```

### Method 3: Quick Updates

For rapid deployments after initial setup:
```bash
# Frontend only
./app/scripts/quick-deploy.sh frontend

# Backend only  
./app/scripts/quick-deploy.sh backend

# Check status
./app/scripts/quick-deploy.sh status
```

## 🔧 Configuration Files

### Protected Files (Won't be overwritten in deployments)
- `/var/www/cataloro/.env` - Environment variables
- `/etc/nginx/conf.d/cataloro.conf` - Nginx configuration
- `/etc/systemd/system/cataloro-backend.service` - Backend service
- SSL certificates in `/etc/nginx/ssl/`

### Environment Configuration
Copy and modify `.env.production` to your server:
```bash
scp /app/.env.production root@217.154.0.82:/var/www/cataloro/.env
```

Edit the file on your server:
```bash
ssh root@217.154.0.82
nano /var/www/cataloro/.env
```

Required changes:
- Set strong `JWT_SECRET_KEY`
- Set strong `SESSION_SECRET`
- Configure MongoDB credentials
- Set proper `CORS_ORIGINS`

## 🗄️ Database Setup

### MongoDB Configuration
The deployment includes automatic MongoDB setup with:
- Database: `cataloro_marketplace`
- Collections with proper indexes
- User authentication

### Initial Data
If you need to migrate data from your current database:
```bash
# Export from current database
mongodump --uri="mongodb://localhost:27017/cataloro_marketplace" --out=/tmp/cataloro-backup

# Import to production
scp -r /tmp/cataloro-backup root@217.154.0.82:/tmp/
ssh root@217.154.0.82 "mongorestore --uri='mongodb://localhost:27017' /tmp/cataloro-backup"
```

## 🔐 SSL/HTTPS Setup

### Option 1: Let's Encrypt (Automatic)
```bash
ssh root@217.154.0.82
certbot --nginx -d cataloro.com -d www.cataloro.com
```

### Option 2: Existing SSL Certificate
Place your certificates in:
- `/etc/nginx/ssl/cataloro.com.crt`
- `/etc/nginx/ssl/cataloro.com.key`

## 📊 Monitoring & Maintenance

### Service Management
```bash
# Check backend status
sudo systemctl status cataloro-backend

# View logs
sudo journalctl -u cataloro-backend -f

# Restart services
sudo systemctl restart cataloro-backend
sudo systemctl reload nginx
```

### Health Checks
- Frontend: `https://cataloro.com`
- Backend API: `https://cataloro.com/api/health`
- Database: `sudo systemctl status mongodb`

### Backup & Restore

**Create Backup:**
```bash
./app/scripts/enhanced-deploy.sh  # Automatically creates backup before deployment
```

**Manual Restore:**
```bash
ssh root@217.154.0.82
cd /var/www/cataloro
sudo systemctl stop cataloro-backend
sudo mv current current.failed
sudo cp -r backups/backup-YYYYMMDD-HHMMSS current
sudo systemctl start cataloro-backend
```

## 🚨 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
sudo journalctl -u cataloro-backend -n 50
```

**Frontend not loading:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

**Database connection issues:**
```bash
sudo systemctl status mongodb
mongo cataloro_marketplace -u cataloro_user -p
```

**SSL certificate issues:**
```bash
sudo certbot certificates
sudo nginx -t
```

### Log Locations
- Application logs: `/var/log/cataloro/application.log`
- Nginx logs: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`
- System logs: `journalctl -u cataloro-backend`

## 🔄 Rollback Procedure

If deployment fails, the enhanced deploy script automatically attempts rollback:
```bash
# Manual rollback
ssh root@217.154.0.82
cd /var/www/cataloro
sudo systemctl stop cataloro-backend
sudo mv current current.failed
sudo mv current.old current  # or copy from backups/
sudo systemctl start cataloro-backend
```

## 📁 File Structure on Server

```
/var/www/cataloro/
├── current/                 # Active deployment
│   ├── frontend/           # Built React app
│   ├── backend/            # Python FastAPI app
│   └── .env               # Environment variables
├── backups/                # Automatic backups
│   ├── backup-20250916-120000/
│   └── backup-20250916-180000/
└── logs/                   # Application logs
```

## 🎯 Next Steps After Deployment

1. **Verify SSL**: Ensure `https://cataloro.com` loads correctly
2. **Test API**: Check `https://cataloro.com/api/health`
3. **Admin Access**: Log in to admin panel and verify functionality
4. **Monitor Logs**: Watch logs for any errors
5. **Performance**: Monitor server resources (CPU, memory, disk)

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review service logs using provided commands
3. Ensure all prerequisites are met
4. Contact support with specific error messages

---

**Deployment completed successfully!** 🎉

Your Cataloro Marketplace should now be accessible at:
- **Frontend**: https://cataloro.com
- **API**: https://cataloro.com/api