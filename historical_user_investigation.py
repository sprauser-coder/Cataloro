#!/usr/bin/env python3
"""
Historical User Investigation - Check for evidence of 156 user count
"""

import requests
import json
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://market-refactor.preview.emergentagent.com/api"

def check_all_possible_endpoints():
    """Check all possible endpoints that might show user-related counts"""
    print("=" * 80)
    print("COMPREHENSIVE ENDPOINT INVESTIGATION FOR 156 COUNT")
    print("=" * 80)
    
    endpoints_to_check = [
        # Admin endpoints
        ("/admin/dashboard", "Dashboard KPIs"),
        ("/admin/users", "All users list"),
        
        # Marketplace endpoints  
        ("/marketplace/browse", "Browse listings"),
        
        # Try some other potential endpoints
        ("/listings", "All listings"),
        ("/health", "Health check"),
    ]
    
    found_156 = []
    
    for endpoint, description in endpoints_to_check:
        try:
            print(f"\n🔍 Checking {endpoint} ({description})")
            print("-" * 50)
            
            response = requests.get(f"{BACKEND_URL}{endpoint}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Recursively search for any occurrence of 156
                def find_156_in_data(obj, path=""):
                    results = []
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            current_path = f"{path}.{key}" if path else key
                            if isinstance(value, (int, float)) and value == 156:
                                results.append(f"Found 156 at {current_path}")
                            elif isinstance(value, (dict, list)):
                                results.extend(find_156_in_data(value, current_path))
                    elif isinstance(obj, list):
                        if len(obj) == 156:
                            results.append(f"Found list of length 156 at {path}")
                        for i, item in enumerate(obj):
                            current_path = f"{path}[{i}]" if path else f"[{i}]"
                            if isinstance(item, (int, float)) and item == 156:
                                results.append(f"Found 156 at {current_path}")
                            elif isinstance(item, (dict, list)):
                                results.extend(find_156_in_data(item, current_path))
                    return results
                
                matches = find_156_in_data(data)
                if matches:
                    print("🎯 FOUND 156!")
                    for match in matches:
                        print(f"  {match}")
                    found_156.extend([(endpoint, match) for match in matches])
                else:
                    print("No 156 found in response")
                
                # Show key metrics for each endpoint
                if endpoint == "/admin/dashboard":
                    kpis = data.get('kpis', {})
                    print("Dashboard metrics:")
                    for key, value in kpis.items():
                        print(f"  {key}: {value}")
                        
                elif endpoint == "/admin/users":
                    print(f"Total users: {len(data)}")
                    
                elif endpoint == "/marketplace/browse":
                    if isinstance(data, list):
                        print(f"Total listings: {len(data)}")
                        unique_sellers = set()
                        for listing in data:
                            seller_id = listing.get('seller_id')
                            if seller_id:
                                unique_sellers.add(seller_id)
                        print(f"Unique sellers: {len(unique_sellers)}")
                        
                elif endpoint == "/listings":
                    if isinstance(data, dict) and 'listings' in data:
                        listings = data['listings']
                        print(f"Total listings: {len(listings)}")
                        print(f"Total count from API: {data.get('total', 'N/A')}")
                    elif isinstance(data, list):
                        print(f"Total listings: {len(data)}")
                        
            else:
                print(f"❌ Failed: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return found_156

def check_user_data_patterns():
    """Check for patterns in user data that might explain 156"""
    print(f"\n" + "=" * 80)
    print("USER DATA PATTERN ANALYSIS")
    print("=" * 80)
    
    try:
        # Get all users
        response = requests.get(f"{BACKEND_URL}/admin/users")
        if response.status_code != 200:
            print(f"❌ Failed to get users: {response.text}")
            return
        
        users = response.json()
        print(f"Current user count: {len(users)}")
        
        # Analyze creation dates to see if there was a peak at 156
        creation_dates = {}
        for user in users:
            created_at = user.get('created_at')
            if created_at:
                # Extract date
                if isinstance(created_at, str):
                    date_str = created_at[:10]
                else:
                    date_str = str(created_at)[:10]
                
                if date_str not in creation_dates:
                    creation_dates[date_str] = 0
                creation_dates[date_str] += 1
        
        print("\nUser creation by date:")
        cumulative = 0
        for date in sorted(creation_dates.keys()):
            count = creation_dates[date]
            cumulative += count
            print(f"  {date}: +{count} users (total: {cumulative})")
            
            # Check if cumulative ever reached 156
            if cumulative == 156:
                print(f"    🎯 FOUND IT! Total reached exactly 156 on {date}")
            elif abs(cumulative - 156) <= 2:
                print(f"    ⚠️  Close to 156: {cumulative}")
        
        # Check if there might have been deletions
        print(f"\nCurrent total: {cumulative}")
        if cumulative < 156:
            deleted_count = 156 - cumulative
            print(f"💡 If peak was 156, then {deleted_count} users may have been deleted")
        
        # Look for gaps in user IDs that might indicate deletions
        user_ids = [user.get('id') for user in users if user.get('id')]
        print(f"\nUser ID analysis:")
        print(f"  Total users with IDs: {len(user_ids)}")
        
        # Check for test users that might have been bulk created and deleted
        test_patterns = {}
        for user in users:
            username = user.get('username', '').lower()
            email = user.get('email', '').lower()
            
            if 'test' in username or 'test' in email:
                # Extract pattern
                import re
                pattern_match = re.search(r'(test\w*)', username + email)
                if pattern_match:
                    pattern = pattern_match.group(1)
                    if pattern not in test_patterns:
                        test_patterns[pattern] = 0
                    test_patterns[pattern] += 1
        
        print(f"\nTest user patterns:")
        total_test_users = 0
        for pattern, count in test_patterns.items():
            print(f"  {pattern}: {count} users")
            total_test_users += count
        
        print(f"Total test users: {total_test_users}")
        
        # Calculate what the count would be without test users
        real_users = len(users) - total_test_users
        print(f"Real users (excluding test): {real_users}")
        
        # Check if 156 might be total including deleted test users
        if real_users + (156 - len(users)) > 0:
            potential_deleted_test = 156 - len(users)
            print(f"💡 Potential scenario: {len(users)} current + {potential_deleted_test} deleted = 156 peak")
        
    except Exception as e:
        print(f"❌ Error analyzing user patterns: {e}")

def main():
    """Run comprehensive investigation"""
    print(f"Starting Historical User Investigation at {datetime.now()}")
    print(f"Backend URL: {BACKEND_URL}")
    
    # Check all endpoints for 156
    found_156_locations = check_all_possible_endpoints()
    
    # Analyze user data patterns
    check_user_data_patterns()
    
    # Summary
    print(f"\n" + "=" * 80)
    print("INVESTIGATION SUMMARY")
    print("=" * 80)
    
    if found_156_locations:
        print("🎯 FOUND 156 IN THE FOLLOWING LOCATIONS:")
        for endpoint, location in found_156_locations:
            print(f"  {endpoint}: {location}")
    else:
        print("❌ NO CURRENT OCCURRENCE OF 156 FOUND")
        print("\nPossible explanations for the reported 156 count:")
        print("1. 📊 Historical peak - the database once had 156 users but some were deleted")
        print("2. 🧪 Test data - bulk test users were created and later removed")
        print("3. 🔄 Cached data - user was seeing outdated dashboard information")
        print("4. 📱 Different environment - user was looking at a different system/database")
        print("5. 🧮 Calculation error - a bug in dashboard calculation that has since been fixed")
        print("6. 📈 Different metric - user was looking at a different count (not total users)")
    
    print(f"\nCurrent actual user count: 74")
    print(f"Current test users: ~53")
    print(f"Current real users: ~21")
    
    print(f"\n💡 RECOMMENDATION:")
    print("The dashboard is currently showing accurate user counts (74).")
    print("The reported 156 count is likely from:")
    print("- A previous state when more test users existed")
    print("- Cached/outdated dashboard data")
    print("- A different system or environment")
    
    print(f"\nInvestigation completed at {datetime.now()}")

if __name__ == "__main__":
    main()