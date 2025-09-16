# 🚀 Initial Deployment Guide for Cataloro Marketplace

## Overview
This guide will help you perform the initial deployment of Cataloro Marketplace to your VPS at `217.154.0.82` with domain `https://cataloro.com`.

## Prerequisites
- VPS access via SSH to 217.154.0.82
- Domain cataloro.com pointing to 217.154.0.82 (A record)
- Root or sudo access on the VPS

## Step 1: Initial Setup on VPS

### Connect to your VPS
```bash
ssh root@217.154.0.82
```

### Install Required System Dependencies
```bash
# Update system
yum update -y

# Install essential packages
yum install -y git curl wget nginx python3.11 python3.11-pip nodejs npm

# Install yarn globally
npm install -g yarn

# Install supervisor
yum install -y supervisor || pip3.11 install supervisor
```

### Create Application Directory
```bash
# Create the application directory
mkdir -p /root/cataloro-marketplace
cd /root/cataloro-marketplace
```

## Step 2: Clone Repository and Deploy Files

### Clone your GitHub repository
```bash
# Clone the repository
git clone https://github.com/sprauser-coder/Cataloro.git .

# Make deploy script executable
chmod +x deploy.sh
```

### Manually Copy Deployment Files (First Time Only)
Since this is the initial setup, you need to manually transfer the deployment files:

```bash
# Create nginx config
cat > nginx-cataloro.conf << 'EOF'
[Copy the content from /app/nginx-cataloro.conf here]
EOF

# Create supervisor config
cat > supervisor-cataloro.conf << 'EOF'
[Copy the content from /app/supervisor-cataloro.conf here]
EOF

# Create deploy script
cat > deploy.sh << 'EOF'
[Copy the content from /app/deploy.sh here]
EOF

# Create .deployignore
cat > .deployignore << 'EOF'
[Copy the content from /app/.deployignore here]
EOF

# Make deploy script executable
chmod +x deploy.sh
```

## Step 3: Initial Deployment

### Run the Initial Setup
```bash
# Run the full setup command
./deploy.sh setup
```

This will:
- ✅ Install all dependencies
- ✅ Create SSL certificates (self-signed initially)
- ✅ Configure Nginx for https://cataloro.com
- ✅ Set up Supervisor services
- ✅ Build the React frontend
- ✅ Start all services

## Step 4: Verification

### Check System Status
```bash
# Check overall status
./deploy.sh status

# Check specific health
./deploy.sh health

# View logs if needed
./deploy.sh logs
```

### Test the Website
```bash
# Test API
curl https://cataloro.com/api/health

# Test website
curl -I https://cataloro.com
```

## Step 5: Set Up Let's Encrypt SSL (Recommended)

### Install Certbot
```bash
# Install certbot
yum install -y certbot python3-certbot-nginx

# Stop nginx temporarily
systemctl stop nginx

# Get SSL certificate
certbot certonly --standalone -d cataloro.com -d www.cataloro.com

# Update nginx config to use Let's Encrypt
# Edit /etc/nginx/conf.d/cataloro.conf and uncomment the Let's Encrypt lines

# Start nginx
systemctl start nginx

# Test SSL renewal
certbot renew --dry-run
```

## Step 6: Future Deployments

After the initial setup, all future deployments are simple:

```bash
# Standard deployment (updates code, protects configs)
./deploy.sh

# Or with specific command
./deploy.sh deploy
```

## Protected Files System

The deployment system protects these files from being overridden:

### ✅ Protected Files (Never Changed by Deployment)
- `/etc/nginx/conf.d/cataloro.conf`
- `/etc/supervisord.d/cataloro.conf`
- `frontend/.env`
- `backend/.env`
- SSL certificates

### 🔄 Updated Files (Changed by Deployment)
- All source code
- package.json, requirements.txt
- React components, API routes
- Everything else in the repository

## Troubleshooting

### If deployment fails:
```bash
# Check status
./deploy.sh status

# View logs
./deploy.sh logs

# Restore from backup
./deploy.sh restore
```

### If services won't start:
```bash
# Check supervisor
supervisorctl status

# Restart services manually
supervisorctl restart all

# Check nginx
nginx -t
systemctl restart nginx
```

### Common Issues:

1. **Port conflicts**: Check what's using ports 80, 443, 8001
   ```bash
   ss -tlnp | grep -E ":(80|443|8001)"
   ```

2. **Permission issues**: Ensure files are owned by root
   ```bash
   chown -R root:root /root/cataloro-marketplace
   ```

3. **SSL certificate issues**: Check certificate paths in nginx config
   ```bash
   ls -la /etc/letsencrypt/live/cataloro.com/
   ```

## Service Management Commands

```bash
# Deployment commands
./deploy.sh          # Standard deployment
./deploy.sh setup    # Full setup
./deploy.sh status   # Check status
./deploy.sh logs     # View logs
./deploy.sh health   # Health checks
./deploy.sh backup   # Create backup
./deploy.sh restore  # Restore from backup

# Manual service commands
systemctl restart nginx
supervisorctl restart all
supervisorctl status
```

## Success Indicators

✅ **Deployment Successful When:**
- `./deploy.sh health` shows all green checkmarks
- `https://cataloro.com` loads the React app
- `https://cataloro.com/api/health` returns JSON response
- `supervisorctl status` shows all services RUNNING

## Next Steps After Successful Deployment

1. Set up automated SSL renewal
2. Configure monitoring and alerts
3. Set up database backups
4. Configure firewall rules
5. Set up log rotation

Your Cataloro Marketplace should now be live at https://cataloro.com! 🎉