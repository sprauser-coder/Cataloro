# CRITICAL DEPLOYMENT RULES - MUST FOLLOW TO PREVENT BACKEND CRASHES

## 🚨 MANDATORY RULES FOR ALL VERSION UPDATES

### Rule #1: NEVER Change Deployment Paths
- **Current Environment**: Development environment using `/app/*` paths
- **Service Manager**: Supervisor (NOT PM2)
- **NEVER** change any paths in deployment files to `/var/www/cataloro` or other production paths
- **NEVER** assume PM2 is available - this environment uses Supervisor

### Rule #2: Path Consistency Check
Before ANY version update, verify these files use CORRECT paths:

**deploy.sh**: Must use `/app` as PROJECT_ROOT
```bash
PROJECT_ROOT="/app"  # ✅ CORRECT
PROJECT_ROOT="/var/www/cataloro"  # ❌ WRONG - WILL CRASH
```

**ecosystem.config.js**: Must use `/app/*` paths
```javascript
cwd: '/app/backend'  // ✅ CORRECT
cwd: '/var/www/cataloro/backend'  // ❌ WRONG - WILL CRASH
```

### Rule #3: Service Management
- **USE**: `sudo supervisorctl restart backend` and `sudo supervisorctl restart frontend`
- **NEVER USE**: `pm2 restart` or `pm2 start` commands
- **CHECK STATUS**: `sudo supervisorctl status`

### Rule #4: Version Update Process
When updating versions (e.g., 1.6.4 → 1.6.5):

1. **ONLY** update version numbers in:
   - `/app/backend/server.py` (version string)
   - `/app/frontend/package.json` (version field)
   - `/app/frontend/src/App.js` (console.log version)

2. **NEVER** modify:
   - `/app/deploy.sh` (unless fixing bugs)
   - `/app/ecosystem.config.js` (unless fixing bugs)
   - Any file paths or deployment configurations

3. **ALWAYS** test locally first:
   ```bash
   sudo supervisorctl status  # Check services are running
   curl -s http://localhost:8001/api/ | jq .  # Check version
   ```

### Rule #5: Environment Awareness
- **Development Environment**: `/app/*` paths, Supervisor service manager
- **User's Production**: May use different paths like `/var/www/cataloro/*`, PM2
- **NEVER** assume user's production environment matches development

### Rule #6: Crisis Prevention Checklist
Before declaring any version update complete:

✅ Both backend and frontend services show "RUNNING" status
✅ Version endpoint returns correct version (e.g., v1.6.5)
✅ No path references to `/var/www/cataloro` in any deployment files
✅ All deployment scripts use Supervisor commands, not PM2
✅ Services restart successfully after version update
✅ URLs are configured for production: http://217.154.0.82 (NO PORTS)
✅ CORS allows http://217.154.0.82 and https://217.154.0.82
✅ No localhost references in production configs
✅ **IMAGE UPLOADS WORK**: Test logo, profile pictures, and general uploads
✅ **NO HARDCODED URLS**: All image paths use environment variables
✅ **VERSION DISPLAYS CORRECTLY**: Frontend shows updated version number

## 🔧 RECOVERY PROCESS
If backend crashes after deployment:

1. Check service status: `sudo supervisorctl status`
2. Check logs: `sudo supervisorctl tail -f backend stderr`
3. Verify paths in deployment files match actual environment (`/app/*`)
4. Verify URLs use production format: `http://217.154.0.82` (no ports)
5. Restart services: `sudo supervisorctl restart all`
6. Test version endpoint: `curl http://217.154.0.82/api/` (NOT localhost)

## 📝 APPROVED URL PATTERNS

### Current Production URLs - DO NOT CHANGE:
```bash
# Frontend Environment (/app/frontend/.env)
REACT_APP_BACKEND_URL=https://marketplace-fix-6.preview.emergentagent.com

# Backend Environment (/app/backend/.env)  
CORS_ORIGINS="http://217.154.0.82,https://217.154.0.82,http://localhost:3000"

# User Access
Frontend Access: http://217.154.0.82
```

### Development URLs - FOR LOCAL TESTING ONLY:
```
Frontend: http://localhost:3000
Backend API: http://localhost:8001/api/
```

## 📝 APPROVED FILE PATTERNS

### deploy.sh - CORRECT PATTERN:
```bash
PROJECT_ROOT="/app"
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

### ecosystem.config.js - CORRECT PATTERN:
```javascript
cwd: '/app/backend'
interpreter: '/usr/bin/python3.11'
error_file: '/var/log/supervisor/backend-error.log'
```

### Rule #8: IMAGE UPLOAD PATHS - CRITICAL ISSUE
**CRITICAL**: Never hardcode domain-specific URLs for image uploads - this creates deployment confusion

**FORBIDDEN APPROACHES**:
- ❌ Hardcoding `https://marketplace-fix-6.preview.emergentagent.com/api/uploads/`
- ❌ Using specific domain URLs in image upload code
- ❌ Absolute URLs that don't work across environments

**CORRECT APPROACH**:
- ✅ Use environment variables: `BACKEND_BASE_URL` from .env
- ✅ Use relative paths that work in all environments
- ✅ Dynamic URL construction based on environment
- ✅ Always test image uploads after any deployment changes

**MANDATORY CHECK**: After every version update, verify:
- Logo uploads work correctly
- Image uploads work correctly  
- Profile picture uploads work correctly
- All image URLs are accessible

**Why This Rule Exists**:
Image upload paths have been a recurring issue that breaks functionality after deployments. Hardcoded URLs create environment-specific problems that require manual fixes every time.

### Rule #7: CORRECT URL CONFIGURATION - NEVER USE LOCALHOST IN PRODUCTION
**CRITICAL**: Production environment URLs must match actual deployment setup

**CURRENT PRODUCTION CONFIGURATION**:
- Frontend URL: `http://217.154.0.82` (NO PORT)
- Backend URL: `https://marketplace-fix-6.preview.emergentagent.com` (as configured in frontend/.env)
- Backend CORS: `http://217.154.0.82,https://217.154.0.82,http://localhost:3000`

**NEVER CHANGE** these URLs without explicit user confirmation:
- ❌ Don't modify `/app/frontend/.env` REACT_APP_BACKEND_URL 
- ❌ Don't modify `/app/backend/.env` CORS_ORIGINS
- ❌ Don't use localhost URLs in production context
- ❌ Don't add port numbers to production URLs (217.154.0.82)

**FORBIDDEN URLs IN PRODUCTION**:
- ❌ `http://localhost:3000` 
- ❌ `http://localhost:8001`
- ❌ `http://217.154.0.82:3000`
- ❌ `http://217.154.0.82:8001`

## ❌ FORBIDDEN CHANGES
- Changing `/app` to `/var/www/cataloro` in any file
- Adding PM2 commands to deploy.sh
- Modifying deployment configurations during version updates
- Assuming production environment matches development
- Using localhost URLs in any production context
- Adding port numbers to production URLs (217.154.0.82)
- **HARDCODING IMAGE UPLOAD DOMAINS** (creates recurring deployment issues)
- Using `https://marketplace-fix-6.preview.emergentagent.com/api/uploads/` directly in code

---
**Remember**: The user is frustrated with this recurring cycle. Following these rules prevents the "works in dev, crashes in production" pattern that has been occurring.**