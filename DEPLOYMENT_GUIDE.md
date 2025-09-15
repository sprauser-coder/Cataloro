# 🚀 Cataloro Marketplace Deployment Guide

This guide will help you deploy your Cataloro Marketplace application to your own server using Docker and Docker Compose.

## 📋 Prerequisites

- A server running Ubuntu 20.04+ (or similar Linux distribution)
- Root or sudo access
- At least 2GB RAM and 20GB disk space
- A domain name (optional, but recommended for SSL)

## 🛠️ Quick Start (Recommended)

### Step 1: Server Setup (First Time Only)

1. **Connect to your server:**
   ```bash
   ssh your-username@your-server-ip
   ```

2. **Download and run the server setup script:**
   ```bash
   curl -sSL https://raw.githubusercontent.com/your-repo/cataloro-marketplace/main/server-setup.sh | bash
   ```
   
   Or manually:
   ```bash
   wget https://your-deployment-files/server-setup.sh
   chmod +x server-setup.sh
   ./server-setup.sh
   ```

3. **Log out and back in** (required for Docker group changes):
   ```bash
   exit
   ssh your-username@your-server-ip
   ```

### Step 2: Deploy Application

1. **Upload your application files to the server:**
   ```bash
   # Using SCP
   scp -r ./cataloro-marketplace/ your-username@your-server-ip:~/
   
   # Or using Git (if you've pushed to GitHub)
   cd ~/cataloro-marketplace
   git clone https://github.com/your-username/cataloro-marketplace.git .
   ```

2. **Navigate to application directory:**
   ```bash
   cd ~/cataloro-marketplace
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.production .env
   nano .env  # Edit with your settings
   ```

4. **Deploy the application:**
   ```bash
   ./deploy.sh
   ```

## ⚙️ Manual Setup (Alternative)

### Step 1: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in
exit
```

### Step 2: Configure Application

1. **Create and edit environment file:**
   ```bash
   cp .env.production .env
   ```

2. **Update the following variables in `.env`:**
   ```bash
   # Database
   MONGO_ROOT_PASSWORD=your_secure_mongodb_password
   
   # Security
   JWT_SECRET=your_very_secure_jwt_secret_key
   
   # Frontend URL
   REACT_APP_BACKEND_URL=http://your-domain.com
   # Or for HTTPS: https://your-domain.com
   ```

### Step 3: Deploy

```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 🔧 Configuration Details

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_ROOT_PASSWORD` | MongoDB admin password | `my_secure_password123` |
| `JWT_SECRET` | JWT secret key for authentication | `super_secret_jwt_key_xyz789` |
| `REACT_APP_BACKEND_URL` | Backend URL for frontend | `https://api.yourdomain.com` |
| `MONGO_DB_NAME` | Database name | `cataloro_marketplace` |

### Port Configuration

- **Frontend:** Port 3000 (mapped to 80 in container)
- **Backend:** Port 8001
- **MongoDB:** Port 27017
- **Nginx:** Port 80 (HTTP), 443 (HTTPS)

## 🔒 SSL Setup (HTTPS)

### Option 1: Let's Encrypt (Free)

```bash
# Install Certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates for Docker
sudo mkdir -p ./ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./ssl/key.pem
sudo chown -R $USER:$USER ./ssl
```

### Option 2: Custom SSL Certificate

Place your SSL files in `./ssl/`:
- `cert.pem` - Your SSL certificate
- `key.pem` - Your private key

### Enable HTTPS in Nginx

Edit `nginx.conf` and uncomment the HTTPS server block, then restart:
```bash
docker-compose restart nginx
```

## 🎯 Domain Configuration

### DNS Setup

Point your domain to your server IP:
```
A Record: @ -> your-server-ip
A Record: www -> your-server-ip
```

### Update Backend URL

Update `.env` file:
```bash
REACT_APP_BACKEND_URL=https://yourdomain.com
```

Restart frontend:
```bash
docker-compose restart frontend
```

## 📊 Management Commands

### Basic Operations
```bash
# Start all services
./deploy.sh start

# Stop all services
./deploy.sh stop

# Restart services
./deploy.sh restart

# View logs
./deploy.sh logs

# Rebuild and restart
./deploy.sh rebuild
```

### Database Management
```bash
# Connect to MongoDB
docker exec -it cataloro_mongodb mongo -u admin -p your_password

# Backup database
docker exec cataloro_mongodb mongodump --uri="mongodb://admin:password@localhost:27017/cataloro_marketplace?authSource=admin" --out=/backup
docker cp cataloro_mongodb:/backup ./backup

# Restore database
docker cp ./backup cataloro_mongodb:/backup
docker exec cataloro_mongodb mongorestore --uri="mongodb://admin:password@localhost:27017/cataloro_marketplace?authSource=admin" /backup/cataloro_marketplace
```

### Application Updates
```bash
# Update code (if using Git)
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🔍 Troubleshooting

### Common Issues

1. **Services won't start:**
   ```bash
   docker-compose logs
   ```

2. **Permission denied errors:**
   ```bash
   sudo chown -R $USER:$USER .
   ```

3. **Port already in use:**
   ```bash
   sudo netstat -tulpn | grep :80
   sudo killall -9 apache2  # If Apache is running
   ```

4. **MongoDB connection issues:**
   ```bash
   docker-compose logs mongodb
   ```

### Performance Optimization

1. **Add swap space (if less than 4GB RAM):**
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

2. **Configure log rotation:**
   ```bash
   echo '{"log-driver":"json-file","log-opts":{"max-size":"10m","max-file":"3"}}' | sudo tee /etc/docker/daemon.json
   sudo systemctl restart docker
   ```

## 🔄 Updates and Maintenance

### Regular Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d

# Clean unused Docker resources
docker system prune -a
```

### Monitoring
```bash
# Check resource usage
docker stats

# Check disk usage
df -h
docker system df
```

## 🆘 Support

If you encounter issues:

1. Check logs: `docker-compose logs`
2. Verify configuration: `cat .env`
3. Check service status: `docker-compose ps`
4. Test connectivity: `curl http://localhost:3000`

## 🎉 Success!

Once deployed, your Cataloro Marketplace will be available at:
- **Frontend:** `http://your-domain.com` (or your server IP)
- **Backend API:** `http://your-domain.com/api`

Default admin credentials (remember to change):
- Email: `admin@cataloro.com`
- Password: `password123`

---

**Important Security Notes:**
- Change default passwords immediately
- Keep your system updated
- Use strong JWT secrets
- Enable firewall
- Set up SSL/HTTPS for production
- Regular backups of database and uploads