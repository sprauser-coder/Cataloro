#!/usr/bin/env python3
"""
Detailed User Analysis - Deep dive into user data to find potential 156 count source
"""

import requests
import json
from datetime import datetime
from collections import Counter

# Get backend URL from environment
BACKEND_URL = "https://cataloro-ads.preview.emergentagent.com/api"

def detailed_user_analysis():
    """
    Deep analysis of user data to identify potential sources of 156 count
    """
    print("=" * 80)
    print("DETAILED USER DATA ANALYSIS")
    print("=" * 80)
    
    try:
        # Get all users
        admin_users_response = requests.get(f"{BACKEND_URL}/admin/users")
        if admin_users_response.status_code != 200:
            print(f"❌ Failed to get users: {admin_users_response.text}")
            return
        
        users_data = admin_users_response.json()
        print(f"Total users in database: {len(users_data)}")
        
        # Detailed analysis
        print("\n1. USER BREAKDOWN BY CATEGORIES")
        print("-" * 50)
        
        categories = {
            'test_users': [],
            'demo_users': [],
            'admin_users': [],
            'regular_users': [],
            'duplicate_usernames': [],
            'duplicate_emails': []
        }
        
        # Track duplicates
        username_counts = Counter()
        email_counts = Counter()
        
        for user in users_data:
            email = user.get('email', '').lower()
            username = user.get('username', '').lower()
            role = user.get('role', '')
            
            # Count occurrences
            if username:
                username_counts[username] += 1
            if email:
                email_counts[email] += 1
            
            # Categorize users
            if 'test' in email or 'test' in username:
                categories['test_users'].append(user)
            elif 'demo' in email or 'demo' in username:
                categories['demo_users'].append(user)
            elif role == 'admin':
                categories['admin_users'].append(user)
            else:
                categories['regular_users'].append(user)
        
        # Find duplicates
        for username, count in username_counts.items():
            if count > 1:
                duplicate_users = [u for u in users_data if u.get('username', '').lower() == username]
                categories['duplicate_usernames'].extend(duplicate_users)
        
        for email, count in email_counts.items():
            if count > 1:
                duplicate_users = [u for u in users_data if u.get('email', '').lower() == email]
                categories['duplicate_emails'].extend(duplicate_users)
        
        # Print breakdown
        for category, users in categories.items():
            print(f"{category.replace('_', ' ').title()}: {len(users)}")
            if len(users) > 0 and len(users) <= 10:
                for user in users[:5]:  # Show first 5
                    print(f"  - {user.get('username', 'N/A')} ({user.get('email', 'N/A')})")
                if len(users) > 5:
                    print(f"  ... and {len(users) - 5} more")
        
        print("\n2. POTENTIAL SOURCES OF 156 COUNT")
        print("-" * 50)
        
        # Check various combinations that might add up to 156
        total_with_duplicates = len(users_data) + len(categories['duplicate_usernames']) + len(categories['duplicate_emails'])
        print(f"Users + duplicate usernames + duplicate emails: {total_with_duplicates}")
        
        # Check if there might be historical data or other collections
        print(f"Current user count: {len(users_data)}")
        print(f"Test users: {len(categories['test_users'])}")
        print(f"Demo users: {len(categories['demo_users'])}")
        print(f"Regular users: {len(categories['regular_users'])}")
        print(f"Admin users: {len(categories['admin_users'])}")
        
        # Check for patterns that might indicate bulk test data
        print("\n3. BULK DATA ANALYSIS")
        print("-" * 50)
        
        # Group by creation patterns
        creation_dates = {}
        for user in users_data:
            created_at = user.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    date_str = created_at[:10]  # Get just the date part
                else:
                    date_str = str(created_at)[:10]
                
                if date_str not in creation_dates:
                    creation_dates[date_str] = []
                creation_dates[date_str].append(user)
        
        print("Users created by date:")
        for date, users in sorted(creation_dates.items()):
            if len(users) > 5:  # Show dates with bulk creation
                print(f"  {date}: {len(users)} users")
                # Show sample usernames for bulk creation dates
                sample_usernames = [u.get('username', 'N/A') for u in users[:3]]
                print(f"    Sample: {', '.join(sample_usernames)}")
        
        # Check for sequential patterns in usernames/emails
        print("\n4. SEQUENTIAL PATTERN ANALYSIS")
        print("-" * 50)
        
        sequential_patterns = {}
        for user in users_data:
            username = user.get('username', '')
            email = user.get('email', '')
            
            # Look for patterns like testuser_123, user_456, etc.
            import re
            
            # Check username patterns
            username_match = re.search(r'(\w+)_(\d+)', username)
            if username_match:
                base = username_match.group(1)
                if base not in sequential_patterns:
                    sequential_patterns[base] = []
                sequential_patterns[base].append(user)
            
            # Check email patterns
            email_match = re.search(r'(\w+)_(\d+)@', email)
            if email_match:
                base = email_match.group(1)
                if base not in sequential_patterns:
                    sequential_patterns[base] = []
                sequential_patterns[base].append(user)
        
        print("Sequential username/email patterns:")
        for pattern, users in sequential_patterns.items():
            if len(users) > 3:  # Show patterns with multiple users
                print(f"  {pattern}_*: {len(users)} users")
                sample = [u.get('username', u.get('email', 'N/A')) for u in users[:3]]
                print(f"    Sample: {', '.join(sample)}")
        
        # Calculate potential inflated counts
        print("\n5. POTENTIAL INFLATION SOURCES")
        print("-" * 50)
        
        bulk_test_users = sum(len(users) for pattern, users in sequential_patterns.items() if len(users) > 5)
        print(f"Bulk sequential test users: {bulk_test_users}")
        
        # Check if 156 might be from a different calculation
        possible_156_sources = [
            ("Current users + test users", len(users_data) + len(categories['test_users'])),
            ("Users + duplicates", len(users_data) + len(categories['duplicate_usernames'])),
            ("Double counting test users", len(categories['test_users']) * 2 + len(categories['regular_users'])),
            ("Historical peak count", "Unknown - would need to check database history"),
        ]
        
        print("Possible sources of 156 count:")
        for source, count in possible_156_sources:
            if isinstance(count, int):
                if count == 156:
                    print(f"  🎯 {source}: {count} ⭐ EXACT MATCH!")
                elif abs(count - 156) <= 5:
                    print(f"  ⚠️  {source}: {count} (close to 156)")
                else:
                    print(f"  ℹ️  {source}: {count}")
            else:
                print(f"  ❓ {source}: {count}")
        
        return {
            'total_users': len(users_data),
            'categories': {k: len(v) for k, v in categories.items()},
            'sequential_patterns': {k: len(v) for k, v in sequential_patterns.items()},
            'bulk_test_users': bulk_test_users
        }
        
    except Exception as e:
        print(f"❌ Error during detailed analysis: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_other_endpoints():
    """Check other endpoints that might show user counts"""
    print("\n6. CHECKING OTHER ENDPOINTS FOR USER COUNTS")
    print("-" * 50)
    
    endpoints_to_check = [
        "/admin/dashboard",
        "/admin/users", 
        "/marketplace/browse",
    ]
    
    for endpoint in endpoints_to_check:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                
                if endpoint == "/admin/dashboard":
                    kpis = data.get('kpis', {})
                    print(f"Dashboard KPIs:")
                    for key, value in kpis.items():
                        print(f"  {key}: {value}")
                        if isinstance(value, int) and value == 156:
                            print(f"    🎯 FOUND 156 in {key}!")
                
                elif endpoint == "/marketplace/browse":
                    listings = data if isinstance(data, list) else []
                    unique_sellers = set()
                    for listing in listings:
                        seller_id = listing.get('seller_id')
                        if seller_id:
                            unique_sellers.add(seller_id)
                    print(f"Browse endpoint: {len(listings)} listings, {len(unique_sellers)} unique sellers")
                
                elif endpoint == "/admin/users":
                    print(f"Admin users endpoint: {len(data)} users")
            else:
                print(f"❌ {endpoint}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error checking {endpoint}: {e}")

def main():
    """Run detailed user analysis"""
    print(f"Starting Detailed User Analysis at {datetime.now()}")
    print(f"Backend URL: {BACKEND_URL}")
    
    results = detailed_user_analysis()
    check_other_endpoints()
    
    print(f"\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
    if results:
        print(f"Total users found: {results['total_users']}")
        print(f"Test users: {results['categories']['test_users']}")
        print(f"Bulk sequential test users: {results['bulk_test_users']}")
        
        if results['total_users'] != 156:
            print(f"\n❌ Current count ({results['total_users']}) does not match reported 156")
            print("Possible explanations:")
            print("1. The 156 count was from a previous state of the database")
            print("2. The 156 count includes deleted/inactive users")
            print("3. The 156 count is from a different metric or calculation")
            print("4. The user was looking at a cached or outdated dashboard")
        else:
            print(f"\n✅ Found exact match: {results['total_users']} users")
    
    print(f"\nAnalysis completed at {datetime.now()}")

if __name__ == "__main__":
    main()