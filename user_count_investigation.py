#!/usr/bin/env python3
"""
User Count Discrepancy Investigation Test
Testing dashboard vs actual user count to identify inflated numbers
"""

import requests
import json
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-upgrade.preview.emergentagent.com/api"

def test_user_count_discrepancy():
    """
    Comprehensive investigation of user count discrepancy issue
    Dashboard shows 156 users but should show much lower number
    """
    print("=" * 80)
    print("USER COUNT DISCREPANCY INVESTIGATION")
    print("=" * 80)
    
    results = {
        "dashboard_user_count": None,
        "admin_users_count": None,
        "admin_users_actual_list": [],
        "discrepancy_found": False,
        "duplicate_analysis": {},
        "test_data_analysis": {},
        "recommendations": []
    }
    
    try:
        # 1. Test GET /api/admin/dashboard endpoint
        print("\n1. TESTING DASHBOARD USER COUNT")
        print("-" * 50)
        
        dashboard_response = requests.get(f"{BACKEND_URL}/admin/dashboard")
        print(f"Dashboard endpoint status: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            dashboard_user_count = dashboard_data.get("kpis", {}).get("total_users", 0)
            results["dashboard_user_count"] = dashboard_user_count
            
            print(f"✅ Dashboard reports: {dashboard_user_count} users")
            print(f"Dashboard KPIs: {dashboard_data.get('kpis', {})}")
        else:
            print(f"❌ Dashboard endpoint failed: {dashboard_response.text}")
            return results
        
        # 2. Test GET /api/admin/users endpoint
        print("\n2. TESTING ADMIN USERS ENDPOINT")
        print("-" * 50)
        
        admin_users_response = requests.get(f"{BACKEND_URL}/admin/users")
        print(f"Admin users endpoint status: {admin_users_response.status_code}")
        
        if admin_users_response.status_code == 200:
            admin_users_data = admin_users_response.json()
            admin_users_count = len(admin_users_data)
            results["admin_users_count"] = admin_users_count
            results["admin_users_actual_list"] = admin_users_data
            
            print(f"✅ Admin users endpoint returns: {admin_users_count} users")
            
            # Analyze user data for patterns
            print(f"\nUser Analysis:")
            print(f"- Total users in database: {admin_users_count}")
            
            # Check for duplicate emails
            emails = [user.get('email', '') for user in admin_users_data if user.get('email')]
            unique_emails = set(emails)
            duplicate_emails = len(emails) - len(unique_emails)
            results["duplicate_analysis"]["duplicate_emails"] = duplicate_emails
            
            # Check for duplicate usernames
            usernames = [user.get('username', '') for user in admin_users_data if user.get('username')]
            unique_usernames = set(usernames)
            duplicate_usernames = len(usernames) - len(unique_usernames)
            results["duplicate_analysis"]["duplicate_usernames"] = duplicate_usernames
            
            # Check for test/demo users
            test_users = []
            demo_users = []
            admin_users = []
            
            for user in admin_users_data:
                email = user.get('email', '').lower()
                username = user.get('username', '').lower()
                role = user.get('role', '')
                
                if 'test' in email or 'test' in username:
                    test_users.append(user)
                elif 'demo' in email or 'demo' in username:
                    demo_users.append(user)
                elif role == 'admin':
                    admin_users.append(user)
            
            results["test_data_analysis"] = {
                "test_users_count": len(test_users),
                "demo_users_count": len(demo_users),
                "admin_users_count": len(admin_users),
                "regular_users_count": admin_users_count - len(test_users) - len(demo_users) - len(admin_users)
            }
            
            print(f"- Duplicate emails: {duplicate_emails}")
            print(f"- Duplicate usernames: {duplicate_usernames}")
            print(f"- Test users: {len(test_users)}")
            print(f"- Demo users: {len(demo_users)}")
            print(f"- Admin users: {len(admin_users)}")
            print(f"- Regular users: {admin_users_count - len(test_users) - len(demo_users) - len(admin_users)}")
            
            # Show sample users for verification
            print(f"\nSample users (first 5):")
            for i, user in enumerate(admin_users_data[:5]):
                print(f"  {i+1}. {user.get('username', 'N/A')} ({user.get('email', 'N/A')}) - Role: {user.get('role', 'N/A')}")
            
            if len(admin_users_data) > 5:
                print(f"  ... and {len(admin_users_data) - 5} more users")
                
        else:
            print(f"❌ Admin users endpoint failed: {admin_users_response.text}")
            return results
        
        # 3. Compare dashboard vs actual count
        print("\n3. DISCREPANCY ANALYSIS")
        print("-" * 50)
        
        if results["dashboard_user_count"] and results["admin_users_count"]:
            discrepancy = results["dashboard_user_count"] - results["admin_users_count"]
            results["discrepancy_found"] = discrepancy != 0
            
            print(f"Dashboard count: {results['dashboard_user_count']}")
            print(f"Actual database count: {results['admin_users_count']}")
            print(f"Discrepancy: {discrepancy}")
            
            if discrepancy > 0:
                print(f"❌ ISSUE CONFIRMED: Dashboard shows {discrepancy} more users than actually exist")
                results["recommendations"].append(f"Dashboard calculation includes {discrepancy} non-existent users")
            elif discrepancy < 0:
                print(f"⚠️  Dashboard shows {abs(discrepancy)} fewer users than actually exist")
                results["recommendations"].append(f"Dashboard calculation missing {abs(discrepancy)} users")
            else:
                print(f"✅ User counts match perfectly")
        
        # 4. Additional verification - check if there are other user endpoints
        print("\n4. ADDITIONAL USER ENDPOINT VERIFICATION")
        print("-" * 50)
        
        # Try to access browse endpoint to see if it reveals user information
        try:
            browse_response = requests.get(f"{BACKEND_URL}/marketplace/browse")
            if browse_response.status_code == 200:
                browse_data = browse_response.json()
                unique_sellers = set()
                
                for listing in browse_data:
                    seller_id = listing.get('seller_id')
                    if seller_id:
                        unique_sellers.add(seller_id)
                
                print(f"✅ Browse endpoint accessible")
                print(f"- Found {len(browse_data)} listings")
                print(f"- Unique sellers in listings: {len(unique_sellers)}")
                
                # Cross-reference sellers with user database
                seller_ids_in_db = [user.get('id') for user in results["admin_users_actual_list"]]
                sellers_not_in_db = [seller_id for seller_id in unique_sellers if seller_id not in seller_ids_in_db]
                
                if sellers_not_in_db:
                    print(f"⚠️  Found {len(sellers_not_in_db)} seller IDs in listings that don't exist in users database")
                    results["recommendations"].append(f"Clean up orphaned listings with non-existent seller IDs")
                else:
                    print(f"✅ All sellers in listings exist in users database")
                    
        except Exception as e:
            print(f"⚠️  Could not verify browse endpoint: {e}")
        
        # 5. Generate recommendations
        print("\n5. RECOMMENDATIONS")
        print("-" * 50)
        
        if results["discrepancy_found"]:
            if results["dashboard_user_count"] > results["admin_users_count"]:
                results["recommendations"].extend([
                    "Check dashboard calculation logic in /api/admin/dashboard endpoint",
                    "Verify if dashboard is counting deleted or inactive users",
                    "Review database query in get_admin_dashboard() function",
                    "Ensure dashboard uses same collection and filters as admin/users endpoint"
                ])
            
        if results["duplicate_analysis"]["duplicate_emails"] > 0:
            results["recommendations"].append("Remove duplicate email entries from users collection")
            
        if results["duplicate_analysis"]["duplicate_usernames"] > 0:
            results["recommendations"].append("Remove duplicate username entries from users collection")
            
        if results["test_data_analysis"]["test_users_count"] > 10:
            results["recommendations"].append(f"Consider removing {results['test_data_analysis']['test_users_count']} test users from production database")
            
        if results["test_data_analysis"]["demo_users_count"] > 5:
            results["recommendations"].append(f"Consider removing {results['test_data_analysis']['demo_users_count']} demo users from production database")
        
        for recommendation in results["recommendations"]:
            print(f"• {recommendation}")
        
        if not results["recommendations"]:
            print("✅ No issues found - user counts are accurate")
        
        print(f"\n" + "=" * 80)
        print("USER COUNT DISCREPANCY INVESTIGATION COMPLETE")
        print("=" * 80)
        
        return results
        
    except Exception as e:
        print(f"❌ Error during user count investigation: {e}")
        import traceback
        traceback.print_exc()
        return results

def main():
    """Run user count discrepancy investigation"""
    print(f"Starting User Count Discrepancy Investigation at {datetime.now()}")
    print(f"Backend URL: {BACKEND_URL}")
    
    results = test_user_count_discrepancy()
    
    # Summary
    print(f"\n" + "=" * 80)
    print("INVESTIGATION SUMMARY")
    print("=" * 80)
    
    if results["dashboard_user_count"] and results["admin_users_count"]:
        print(f"Dashboard User Count: {results['dashboard_user_count']}")
        print(f"Actual Database Count: {results['admin_users_count']}")
        
        if results["discrepancy_found"]:
            discrepancy = results["dashboard_user_count"] - results["admin_users_count"]
            print(f"❌ DISCREPANCY CONFIRMED: {discrepancy} user difference")
        else:
            print(f"✅ NO DISCREPANCY: Counts match")
            
        # Data quality summary
        test_analysis = results["test_data_analysis"]
        print(f"\nData Quality Analysis:")
        print(f"- Regular users: {test_analysis.get('regular_users_count', 0)}")
        print(f"- Test users: {test_analysis.get('test_users_count', 0)}")
        print(f"- Demo users: {test_analysis.get('demo_users_count', 0)}")
        print(f"- Admin users: {test_analysis.get('admin_users_count', 0)}")
        
        duplicate_analysis = results["duplicate_analysis"]
        if duplicate_analysis.get("duplicate_emails", 0) > 0 or duplicate_analysis.get("duplicate_usernames", 0) > 0:
            print(f"⚠️  Data Quality Issues:")
            print(f"- Duplicate emails: {duplicate_analysis.get('duplicate_emails', 0)}")
            print(f"- Duplicate usernames: {duplicate_analysis.get('duplicate_usernames', 0)}")
    else:
        print("❌ INVESTIGATION FAILED: Could not retrieve user counts")
    
    print(f"\nInvestigation completed at {datetime.now()}")

if __name__ == "__main__":
    main()