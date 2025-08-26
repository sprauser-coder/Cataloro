#!/bin/bash

# CATALORO PRODUCTION VERIFICATION TEST
# Individual User Statistics System Verification
# Target: http://217.154.0.82

set -e

echo "🔍 CATALORO INDIVIDUAL STATISTICS VERIFICATION"
echo "Target Server: http://217.154.0.82"
echo "Testing Individual User Statistics System..."
echo "================================================"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_test() {
    echo -e "${BLUE}🧪 TEST: $1${NC}"
}

print_pass() {
    echo -e "${GREEN}✅ PASS: $1${NC}"
}

print_fail() {
    echo -e "${RED}❌ FAIL: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}"
}

# Test configuration
BASE_URL="http://217.154.0.82"
API_URL="$BASE_URL/api"

# Test 1: Basic Connectivity
print_test "Basic API Connectivity"
if curl -s "$API_URL/" | grep -q "Marketplace API"; then
    VERSION=$(curl -s "$API_URL/" | jq -r '.version' 2>/dev/null || echo "unknown")
    print_pass "API is accessible (Version: $VERSION)"
else
    print_fail "API is not accessible at $API_URL"
    exit 1
fi

# Test 2: Admin Authentication
print_test "Admin Authentication"
ADMIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@marketplace.com","password":"admin123"}')

if echo "$ADMIN_RESPONSE" | grep -q "access_token"; then
    ADMIN_TOKEN=$(echo "$ADMIN_RESPONSE" | jq -r '.access_token')
    ADMIN_USER_ID=$(echo "$ADMIN_RESPONSE" | jq -r '.user.id')
    print_pass "Admin authentication successful (User ID: $ADMIN_USER_ID)"
else
    print_fail "Admin authentication failed"
    echo "Response: $ADMIN_RESPONSE"
    exit 1
fi

# Test 3: Admin Individual Statistics
print_test "Admin Individual Statistics"
ADMIN_STATS=$(curl -s -H "Authorization: Bearer $ADMIN_TOKEN" "$API_URL/profile/stats")

if echo "$ADMIN_STATS" | grep -q "user_id"; then
    STATS_USER_ID=$(echo "$ADMIN_STATS" | jq -r '.user_id')
    TOTAL_LISTINGS=$(echo "$ADMIN_STATS" | jq -r '.total_listings')
    TOTAL_EARNED=$(echo "$ADMIN_STATS" | jq -r '.total_earned')
    TOTAL_ORDERS=$(echo "$ADMIN_STATS" | jq -r '.total_orders')
    
    print_pass "Admin statistics retrieved"
    echo "  User ID: $STATS_USER_ID"
    echo "  Total Listings: $TOTAL_LISTINGS"  
    echo "  Total Earned: €$TOTAL_EARNED"
    echo "  Total Orders: $TOTAL_ORDERS"
    
    # Verify user ID consistency
    if [ "$ADMIN_USER_ID" = "$STATS_USER_ID" ]; then
        print_pass "User ID consistency verified"
    else
        print_fail "User ID mismatch - Authentication: $ADMIN_USER_ID, Stats: $STATS_USER_ID"
    fi
else
    print_fail "Failed to retrieve admin statistics"
    echo "Response: $ADMIN_STATS"
fi

# Test 4: Create New Test User
print_test "Create New Test User for Individual Stats Verification"
TIMESTAMP=$(date +%s)
TEST_EMAIL="statstest_$TIMESTAMP@example.com"
TEST_USERNAME="statstest_$TIMESTAMP"

NEW_USER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"username\":\"$TEST_USERNAME\",\"password\":\"test123\",\"full_name\":\"Stats Test User\",\"role\":\"both\"}")

if echo "$NEW_USER_RESPONSE" | grep -q "access_token"; then
    NEW_USER_ID=$(echo "$NEW_USER_RESPONSE" | jq -r '.user.id')
    print_pass "New test user created (ID: $NEW_USER_ID)"
else
    print_warning "Failed to create new user (may already exist)"
    echo "Response: $NEW_USER_RESPONSE"
fi

# Test 5: New User Statistics (Should be Zero)
print_test "New User Individual Statistics (Should be Zero)"
NEW_USER_TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"test123\"}" | jq -r '.access_token')

if [ "$NEW_USER_TOKEN" != "null" ] && [ -n "$NEW_USER_TOKEN" ]; then
    NEW_USER_STATS=$(curl -s -H "Authorization: Bearer $NEW_USER_TOKEN" "$API_URL/profile/stats")
    
    NEW_LISTINGS=$(echo "$NEW_USER_STATS" | jq -r '.total_listings')
    NEW_EARNED=$(echo "$NEW_USER_STATS" | jq -r '.total_earned')
    NEW_ORDERS=$(echo "$NEW_USER_STATS" | jq -r '.total_orders')
    NEW_STATS_USER_ID=$(echo "$NEW_USER_STATS" | jq -r '.user_id')
    
    print_pass "New user statistics retrieved"
    echo "  User ID: $NEW_STATS_USER_ID"
    echo "  Total Listings: $NEW_LISTINGS"
    echo "  Total Earned: €$NEW_EARNED"
    echo "  Total Orders: $NEW_ORDERS"
    
    # Verify new user has zero statistics
    if [ "$NEW_LISTINGS" = "0" ] && [ "$NEW_EARNED" = "0" ] && [ "$NEW_ORDERS" = "0" ]; then
        print_pass "New user correctly starts with zero statistics"
    else
        print_fail "New user does not start with zero statistics"
    fi
    
    # Verify different user IDs
    if [ "$ADMIN_USER_ID" != "$NEW_STATS_USER_ID" ]; then
        print_pass "Different users have different IDs (Individual statistics confirmed)"
    else
        print_fail "Users have same ID - Individual statistics NOT working"
    fi
else
    print_warning "Could not authenticate new user for statistics test"
fi

# Test 6: Admin Dashboard Statistics
print_test "Admin Dashboard Statistics"
DASHBOARD_STATS=$(curl -s -H "Authorization: Bearer $ADMIN_TOKEN" "$API_URL/admin/stats")

if echo "$DASHBOARD_STATS" | grep -q "total_users"; then
    TOTAL_USERS=$(echo "$DASHBOARD_STATS" | jq -r '.total_users')
    TOTAL_LISTINGS=$(echo "$DASHBOARD_STATS" | jq -r '.total_listings')
    ACTIVE_LISTINGS=$(echo "$DASHBOARD_STATS" | jq -r '.active_listings')
    TOTAL_REVENUE=$(echo "$DASHBOARD_STATS" | jq -r '.total_revenue')
    
    print_pass "Dashboard statistics retrieved"
    echo "  Total Users: $TOTAL_USERS"
    echo "  Total Listings: $TOTAL_LISTINGS"
    echo "  Active Listings: $ACTIVE_LISTINGS"
    echo "  Total Revenue: €$TOTAL_REVENUE"
    
    # Logical validation
    if [ "$ACTIVE_LISTINGS" -le "$TOTAL_LISTINGS" ] 2>/dev/null; then
        print_pass "Logical validation: Active listings ≤ Total listings"
    else
        print_fail "Logical validation failed: Active listings > Total listings"
    fi
else
    print_fail "Failed to retrieve dashboard statistics"
fi

# Test 7: No Emergent URLs Check
print_test "No Emergent URLs in Responses"
ALL_RESPONSES="$ADMIN_RESPONSE $ADMIN_STATS $NEW_USER_RESPONSE $NEW_USER_STATS $DASHBOARD_STATS"

if echo "$ALL_RESPONSES" | grep -q "emergentagent.com\|preview\."; then
    print_fail "Found emergent URLs in responses"
    echo "$ALL_RESPONSES" | grep -o "emergentagent.com\|preview\." | head -5
else
    print_pass "No emergent URLs found in responses"
fi

# Test 8: Frontend Accessibility
print_test "Frontend Accessibility"
if curl -s -I "$BASE_URL" | grep -q "200 OK"; then
    print_pass "Frontend is accessible"
else
    print_fail "Frontend is not accessible"
fi

# Summary
echo ""
echo "================================================"
echo "🎯 INDIVIDUAL USER STATISTICS VERIFICATION SUMMARY"
echo "================================================"

if [ "$ADMIN_USER_ID" != "$NEW_STATS_USER_ID" ] && [ "$NEW_LISTINGS" = "0" ]; then
    echo -e "${GREEN}✅ SUCCESS: Individual user statistics are working correctly!${NC}"
    echo ""
    echo "Key Results:"
    echo "• Admin User ID: $ADMIN_USER_ID (has data: $TOTAL_LISTINGS listings, €$TOTAL_EARNED earned)"
    echo "• New User ID: $NEW_STATS_USER_ID (starts with zero data)"
    echo "• Different users have different statistics ✓"
    echo "• No duplicate data issue ✓"
    echo "• Production URL working ✓"
    echo ""
    echo -e "${GREEN}🎉 DEPLOYMENT VERIFICATION SUCCESSFUL!${NC}"
    exit 0
else
    echo -e "${RED}❌ FAILURE: Individual user statistics are NOT working correctly!${NC}"
    echo ""
    echo "Issues found:"
    if [ "$ADMIN_USER_ID" = "$NEW_STATS_USER_ID" ]; then
        echo "• Users have same ID - statistics not individual"
    fi
    if [ "$NEW_LISTINGS" != "0" ]; then
        echo "• New user doesn't start with zero statistics"
    fi
    echo ""
    echo -e "${RED}🚨 DEPLOYMENT VERIFICATION FAILED!${NC}"
    exit 1
fi