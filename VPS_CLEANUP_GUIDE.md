# Complete VPS Cleanup Guide for 217.154.0.82

⚠️ **WARNING: This will DELETE everything on your VPS** ⚠️

## 🎯 What This Will Do

**DELETED:**
- ❌ All web applications in `/var/www/`
- ❌ All databases (MySQL, PostgreSQL, MongoDB)
- ❌ All custom services and configurations
- ❌ User-uploaded files and application logs
- ❌ Custom nginx/apache configurations
- ❌ Docker containers and images
- ❌ Node.js applications and PM2 processes

**PRESERVED:**
- ✅ System OS (Ubuntu/Debian/CentOS)
- ✅ SSH access and authorized keys
- ✅ SSL certificates (backed up and restored)
- ✅ Basic system packages and configurations
- ✅ Network settings

## 📋 Step-by-Step Cleanup Process

### Step 1: Upload Cleanup Script to Your Server

**From your local machine or Emergent environment:**

```bash
# Make script executable
chmod +x /app/scripts/vps-complete-cleanup.sh

# Upload to your server
scp /app/scripts/vps-complete-cleanup.sh root@217.154.0.82:/tmp/
```

### Step 2: Connect to Your Server

```bash
ssh root@217.154.0.82
```

### Step 3: Review What Will Be Deleted (Optional)

**Check current applications:**
```bash
# Check web directories
ls -la /var/www/
ls -la /opt/

# Check running services
systemctl list-units --state=running | grep -E "(nginx|apache|mysql|mongo|redis|node|python)"

# Check databases
ps aux | grep -E "(mysql|mongo|postgres|redis)"
```

### Step 4: Run the Complete Cleanup

```bash
cd /tmp
chmod +x vps-complete-cleanup.sh
./vps-complete-cleanup.sh
```

**You will be prompted to:**
1. ⚠️ Read the warning about what will be deleted
2. 🔑 Type `DELETE EVERYTHING` to confirm
3. ⏰ Wait 10 seconds (last chance to cancel with Ctrl+C)

### Step 5: Monitor the Cleanup Process

The script will show you each step:
```
🔐 Backing up SSL certificates...
🛑 Stopping all application services...
🗂️  Removing all application directories...
🗄️  Removing all databases...
🌐 Removing web server configurations...
⚙️  Removing custom systemd services...
📋 Removing application logs...
🐳 Removing Docker containers and images...
🟢 Removing Node.js applications...
📦 Cleaning package managers...
🧹 Final cleanup...
🔐 Restoring SSL certificates...
```

### Step 6: Verify Cleanup Completion

**After cleanup, verify:**
```bash
# Check that applications are removed
ls -la /var/www/  # Should be empty or only contain basic files

# Check services are stopped
systemctl list-units --state=running | grep -v "system"

# Check databases are cleared
ps aux | grep -E "(mysql|mongo|postgres|redis)"  # Should show no results

# Verify SSL backup
ls -la /tmp/ssl-backup/  # Should contain your certificates
```

## 🔧 After Cleanup: Prepare for Fresh Deployment

### Step 7: Basic System Update

```bash
# Update package lists
apt-get update

# Upgrade system packages
apt-get upgrade -y

# Install basic requirements
apt-get install -y curl wget git unzip
```

### Step 8: Verify SSH Access Still Works

```bash
# Test SSH from another terminal
ssh root@217.154.0.82 "echo 'SSH working!'"
```

### Step 9: Ready for Fresh Cataloro Deployment

Your server is now clean and ready. You can proceed with:

```bash
# Upload and run server setup
scp /app/scripts/server-setup.sh root@217.154.0.82:/tmp/
ssh root@217.154.0.82 "bash /tmp/server-setup.sh"

# Then run deployment
./app/scripts/enhanced-deploy.sh
```

## 🆘 Emergency Recovery

If something goes wrong during cleanup:

### Restore SSL Certificates
```bash
# SSL certificates are backed up to /tmp/ssl-backup/
# They are automatically restored at the end, but if needed:
cp -r /tmp/ssl-backup/letsencrypt/* /etc/letsencrypt/
cp -r /tmp/ssl-backup/ssl/* /etc/nginx/ssl/
```

### Basic SSH Access Issues
```bash
# If SSH becomes inaccessible, use your hosting provider's console
# The script preserves SSH configurations, but if issues occur:
systemctl restart ssh
systemctl enable ssh
```

### Rollback Not Possible
⚠️ **IMPORTANT**: This cleanup is **irreversible**. Make sure you have:
- ✅ Backups of any important data
- ✅ Access to your hosting provider's console
- ✅ Your SSH keys available

## 📞 Final Confirmation

Before proceeding, confirm you have:
- [ ] ✅ Backed up any important data manually
- [ ] ✅ SSH access to your server
- [ ] ✅ Access to your hosting provider's console (as backup)
- [ ] ✅ Your domain DNS pointing to 217.154.0.82
- [ ] ✅ SSL certificates will be preserved automatically

**Ready to proceed?** Run the cleanup script and then deploy fresh Cataloro!

---

**Need Help?** If you encounter any issues during cleanup, stop the process and ask for assistance before continuing.