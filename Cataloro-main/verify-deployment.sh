#!/bin/bash

echo "🔍 Verifying Cataloro Marketplace Deployment..."

# Check if services are running
echo "📊 Checking service status..."
sudo supervisorctl status

# Test backend API connectivity
echo "🧪 Testing backend API..."
BACKEND_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://217.154.0.82/api/)
if [ "$BACKEND_TEST" = "200" ]; then
    echo "   ✅ Backend API is responding (HTTP $BACKEND_TEST)"
else
    echo "   ❌ Backend API is not responding (HTTP $BACKEND_TEST)"
fi

# Test admin authentication
echo "🔐 Testing admin authentication..."
AUTH_TEST=$(curl -s -X POST -H "Content-Type: application/json" -d '{"email":"admin@marketplace.com","password":"admin123"}' http://217.154.0.82/api/auth/login | grep -o '"access_token"')
if [ "$AUTH_TEST" = '"access_token"' ]; then
    echo "   ✅ Admin authentication is working"
else
    echo "   ❌ Admin authentication failed"
fi

# Test frontend accessibility
echo "🌐 Testing frontend accessibility..."
FRONTEND_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://217.154.0.82/)
if [ "$FRONTEND_TEST" = "200" ]; then
    echo "   ✅ Frontend is accessible (HTTP $FRONTEND_TEST)"
else
    echo "   ❌ Frontend is not accessible (HTTP $FRONTEND_TEST)"
fi

echo ""
echo "📱 Application URLs:"
echo "   Frontend: http://217.154.0.82"
echo "   Backend API: http://217.154.0.82/api"
echo ""
echo "👤 Admin Login Credentials:"
echo "   Email: admin@marketplace.com"
echo "   Password: admin123"
echo ""
echo "✅ Deployment verification completed!"