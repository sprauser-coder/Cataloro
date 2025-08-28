#!/bin/bash

# Clean Architecture Deployment Verification Script
echo "🧪 Verifying Clean Architecture Deployment..."
echo "============================================="

# Test 1: Basic API connectivity
echo "1. Testing API connectivity..."
API_RESPONSE=$(curl -s http://217.154.0.82/api/)
if echo "$API_RESPONSE" | grep -q "Marketplace API"; then
    echo "   ✅ API is responding correctly"
else
    echo "   ❌ API test failed: $API_RESPONSE"
fi

# Test 2: Check if frontend build contains clean architecture
echo "2. Checking frontend build for clean architecture..."
if [ -d "/var/www/cataloro/frontend/build" ]; then
    # Check if build contains our new components
    if [ -d "/var/www/cataloro/frontend/src/features" ] && [ -d "/var/www/cataloro/frontend/src/components" ]; then
        echo "   ✅ Clean architecture folder structure found"
    else
        echo "   ❌ Clean architecture folders missing"
    fi
    
    # Check if CSS contains purple theme
    if grep -r "8b5cf6\|purple" /var/www/cataloro/frontend/build/static/css/ 2>/dev/null; then
        echo "   ✅ Purple theme found in CSS build"
    else
        echo "   ❌ Purple theme missing from CSS build"
    fi
else
    echo "   ❌ Frontend build directory not found"
fi

# Test 3: Check PM2 services
echo "3. Checking PM2 services..."
PM2_STATUS=$(pm2 jlist 2>/dev/null)
if echo "$PM2_STATUS" | grep -q "cataloro-backend.*online" && echo "$PM2_STATUS" | grep -q "cataloro-frontend.*online"; then
    echo "   ✅ Both frontend and backend services are online"
else
    echo "   ❌ Services not running properly"
    pm2 status
fi

# Test 4: Test admin login endpoint
echo "4. Testing admin login endpoint..."
LOGIN_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" \
    -d '{"email":"admin@marketplace.com","password":"admin123"}' \
    http://217.154.0.82/api/auth/login)

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "   ✅ Admin login working correctly"
else
    echo "   ❌ Admin login failed: $LOGIN_RESPONSE"
fi

# Test 5: Check environment configuration
echo "5. Checking environment configuration..."
if [ -f "/var/www/cataloro/frontend/.env" ]; then
    FRONTEND_URL=$(grep "REACT_APP_BACKEND_URL" /var/www/cataloro/frontend/.env | cut -d'=' -f2)
    if [ "$FRONTEND_URL" = "http://217.154.0.82" ]; then
        echo "   ✅ Frontend environment configured correctly"
    else
        echo "   ❌ Frontend environment misconfigured: $FRONTEND_URL"
    fi
else
    echo "   ❌ Frontend .env file not found"
fi

if [ -f "/var/www/cataloro/backend/.env" ]; then
    MONGO_URL=$(grep "MONGO_URL" /var/www/cataloro/backend/.env | cut -d'=' -f2)
    if [ "$MONGO_URL" = "mongodb://localhost:27017" ]; then
        echo "   ✅ Backend environment configured correctly"
    else
        echo "   ❌ Backend environment misconfigured: $MONGO_URL"
    fi
else
    echo "   ❌ Backend .env file not found"
fi

echo ""
echo "============================================="
echo "🎯 Deployment Verification Complete!"
echo ""
echo "🌐 Access your application at:"
echo "   • Main Site: http://217.154.0.82"
echo "   • Login Page: http://217.154.0.82/#/auth"
echo "   • Admin Panel: http://217.154.0.82/#/admin"
echo ""