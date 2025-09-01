#!/usr/bin/env python3
"""
CRITICAL DATABASE INVESTIGATION - Multiple Collections and Data Inconsistencies
Testing for the reported issue: "items appearing in user listings but not in all listings"
"""

import requests
import json
import sys
import os
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://trade-platform-30.preview.emergentagent.com/api"

class DatabaseInvestigator:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.admin_user = None
        self.regular_user = None
        
    def log_result(self, test_name, status, details):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {details}")
        
    def setup_test_users(self):
        """Setup admin and regular users for testing"""
        try:
            # Login as admin
            admin_response = requests.post(f"{self.backend_url}/auth/login", 
                json={"email": "admin@cataloro.com", "password": "admin123"})
            if admin_response.status_code == 200:
                self.admin_user = admin_response.json()["user"]
                self.log_result("Admin Login", "PASS", f"Admin user ID: {self.admin_user['id']}")
            else:
                self.log_result("Admin Login", "FAIL", f"Status: {admin_response.status_code}")
                return False
                
            # Login as regular user
            user_response = requests.post(f"{self.backend_url}/auth/login", 
                json={"email": "user@cataloro.com", "password": "user123"})
            if user_response.status_code == 200:
                self.regular_user = user_response.json()["user"]
                self.log_result("Regular User Login", "PASS", f"User ID: {self.regular_user['id']}")
            else:
                self.log_result("Regular User Login", "FAIL", f"Status: {user_response.status_code}")
                return False
                
            return True
        except Exception as e:
            self.log_result("User Setup", "FAIL", f"Error: {str(e)}")
            return False
    
    def investigate_database_structure(self):
        """1. Database Structure Analysis - Check for multiple collections"""
        print("\n" + "="*80)
        print("1. DATABASE STRUCTURE ANALYSIS")
        print("="*80)
        
        try:
            # Test different listing endpoints to identify collections
            endpoints_to_test = [
                ("/marketplace/browse", "Browse Listings Collection"),
                ("/listings", "Main Listings Collection"),
                (f"/user/my-listings/{self.admin_user['id']}", "User Listings Collection"),
                (f"/user/my-listings/{self.regular_user['id']}", "Regular User Listings Collection")
            ]
            
            collection_data = {}
            
            for endpoint, description in endpoints_to_test:
                try:
                    response = requests.get(f"{self.backend_url}{endpoint}")
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Analyze response structure
                        if isinstance(data, list):
                            count = len(data)
                            structure = "ARRAY"
                        elif isinstance(data, dict) and 'listings' in data:
                            count = len(data['listings'])
                            structure = "OBJECT_WITH_LISTINGS"
                        else:
                            count = 0
                            structure = "UNKNOWN"
                            
                        collection_data[endpoint] = {
                            "count": count,
                            "structure": structure,
                            "data": data
                        }
                        
                        self.log_result(f"Collection Access: {description}", "PASS", 
                                      f"Structure: {structure}, Count: {count}")
                    else:
                        self.log_result(f"Collection Access: {description}", "FAIL", 
                                      f"Status: {response.status_code}")
                        collection_data[endpoint] = {"error": response.status_code}
                        
                except Exception as e:
                    self.log_result(f"Collection Access: {description}", "FAIL", f"Error: {str(e)}")
                    collection_data[endpoint] = {"error": str(e)}
            
            return collection_data
            
        except Exception as e:
            self.log_result("Database Structure Analysis", "FAIL", f"Error: {str(e)}")
            return {}
    
    def investigate_data_sources(self, collection_data):
        """2. User Listings vs All Listings Investigation"""
        print("\n" + "="*80)
        print("2. USER LISTINGS VS ALL LISTINGS INVESTIGATION")
        print("="*80)
        
        try:
            # Get data from different endpoints
            browse_data = collection_data.get("/marketplace/browse", {}).get("data", [])
            listings_data = collection_data.get("/listings", {}).get("data", [])
            admin_listings = collection_data.get(f"/user/my-listings/{self.admin_user['id']}", {}).get("data", [])
            user_listings = collection_data.get(f"/user/my-listings/{self.regular_user['id']}", {}).get("data", [])
            
            # Extract listings from different structures
            if isinstance(listings_data, dict) and 'listings' in listings_data:
                listings_data = listings_data['listings']
            
            # Analyze data consistency
            browse_ids = set()
            listings_ids = set()
            admin_ids = set()
            user_ids = set()
            
            # Extract IDs from browse data
            if isinstance(browse_data, list):
                browse_ids = {item.get('id', item.get('_id', str(uuid.uuid4()))) for item in browse_data}
                
            # Extract IDs from listings data
            if isinstance(listings_data, list):
                listings_ids = {item.get('id', item.get('_id', str(uuid.uuid4()))) for item in listings_data}
                
            # Extract IDs from admin listings
            if isinstance(admin_listings, list):
                admin_ids = {item.get('id', item.get('_id', str(uuid.uuid4()))) for item in admin_listings}
                
            # Extract IDs from user listings
            if isinstance(user_listings, list):
                user_ids = {item.get('id', item.get('_id', str(uuid.uuid4()))) for item in user_listings}
            
            # Compare collections
            self.log_result("Browse Collection Count", "INFO", f"{len(browse_ids)} unique IDs")
            self.log_result("Listings Collection Count", "INFO", f"{len(listings_ids)} unique IDs")
            self.log_result("Admin Listings Count", "INFO", f"{len(admin_ids)} unique IDs")
            self.log_result("User Listings Count", "INFO", f"{len(user_ids)} unique IDs")
            
            # Check for inconsistencies
            all_user_listings = admin_ids.union(user_ids)
            
            # Critical checks
            missing_from_browse = all_user_listings - browse_ids
            missing_from_listings = all_user_listings - listings_ids
            browse_not_in_listings = browse_ids - listings_ids
            listings_not_in_browse = listings_ids - browse_ids
            
            if missing_from_browse:
                self.log_result("CRITICAL: User listings missing from browse", "FAIL", 
                              f"{len(missing_from_browse)} items: {list(missing_from_browse)[:5]}")
            else:
                self.log_result("User listings in browse", "PASS", "All user listings appear in browse")
                
            if missing_from_listings:
                self.log_result("CRITICAL: User listings missing from /listings", "FAIL", 
                              f"{len(missing_from_listings)} items: {list(missing_from_listings)[:5]}")
            else:
                self.log_result("User listings in /listings", "PASS", "All user listings appear in /listings")
                
            if browse_not_in_listings:
                self.log_result("CRITICAL: Browse items not in /listings", "FAIL", 
                              f"{len(browse_not_in_listings)} items: {list(browse_not_in_listings)[:5]}")
            else:
                self.log_result("Browse-Listings consistency", "PASS", "Browse and listings are consistent")
                
            if listings_not_in_browse:
                self.log_result("CRITICAL: Listings not in browse", "FAIL", 
                              f"{len(listings_not_in_browse)} items: {list(listings_not_in_browse)[:5]}")
            else:
                self.log_result("Listings-Browse consistency", "PASS", "Listings and browse are consistent")
            
            return {
                "browse_ids": browse_ids,
                "listings_ids": listings_ids,
                "admin_ids": admin_ids,
                "user_ids": user_ids,
                "inconsistencies": {
                    "missing_from_browse": missing_from_browse,
                    "missing_from_listings": missing_from_listings,
                    "browse_not_in_listings": browse_not_in_listings,
                    "listings_not_in_browse": listings_not_in_browse
                }
            }
            
        except Exception as e:
            self.log_result("Data Sources Investigation", "FAIL", f"Error: {str(e)}")
            return {}
    
    def investigate_api_endpoints(self):
        """3. API Endpoint Data Source Mapping"""
        print("\n" + "="*80)
        print("3. API ENDPOINT DATA SOURCE MAPPING")
        print("="*80)
        
        try:
            # Create a test listing to trace through system
            test_listing = {
                "title": "DATABASE_INVESTIGATION_TEST_ITEM",
                "description": "Test item for database investigation",
                "price": 999.99,
                "category": "Test",
                "condition": "new",
                "seller_id": self.admin_user['id'],
                "images": []
            }
            
            # Create the test listing
            create_response = requests.post(f"{self.backend_url}/listings", json=test_listing)
            if create_response.status_code == 200:
                test_listing_id = create_response.json().get("listing_id")
                self.log_result("Test Listing Creation", "PASS", f"Created listing ID: {test_listing_id}")
                
                # Wait a moment for database consistency
                import time
                time.sleep(1)
                
                # Check where the listing appears
                endpoints_to_check = [
                    ("/marketplace/browse", "Browse endpoint"),
                    ("/listings", "Listings endpoint"),
                    (f"/user/my-listings/{self.admin_user['id']}", "User listings endpoint"),
                    (f"/listings/{test_listing_id}", "Individual listing endpoint")
                ]
                
                appearance_map = {}
                
                for endpoint, description in endpoints_to_check:
                    try:
                        response = requests.get(f"{self.backend_url}{endpoint}")
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Search for our test listing
                            found = False
                            if isinstance(data, list):
                                found = any(item.get('id') == test_listing_id or 
                                          item.get('title') == 'DATABASE_INVESTIGATION_TEST_ITEM' 
                                          for item in data)
                            elif isinstance(data, dict):
                                if 'listings' in data:
                                    found = any(item.get('id') == test_listing_id or 
                                              item.get('title') == 'DATABASE_INVESTIGATION_TEST_ITEM' 
                                              for item in data['listings'])
                                elif data.get('id') == test_listing_id:
                                    found = True
                            
                            appearance_map[endpoint] = found
                            status = "PASS" if found else "FAIL"
                            self.log_result(f"Test listing in {description}", status, 
                                          f"Found: {found}")
                        else:
                            appearance_map[endpoint] = False
                            self.log_result(f"Test listing in {description}", "FAIL", 
                                          f"HTTP {response.status_code}")
                    except Exception as e:
                        appearance_map[endpoint] = False
                        self.log_result(f"Test listing in {description}", "FAIL", f"Error: {str(e)}")
                
                return test_listing_id, appearance_map
            else:
                self.log_result("Test Listing Creation", "FAIL", f"Status: {create_response.status_code}")
                return None, {}
                
        except Exception as e:
            self.log_result("API Endpoint Mapping", "FAIL", f"Error: {str(e)}")
            return None, {}
    
    def investigate_delete_operations(self, test_listing_id, appearance_map):
        """4. Delete Operation Investigation"""
        print("\n" + "="*80)
        print("4. DELETE OPERATION INVESTIGATION")
        print("="*80)
        
        if not test_listing_id:
            self.log_result("Delete Investigation", "SKIP", "No test listing to delete")
            return
            
        try:
            # Record where the listing appeared before deletion
            appeared_before = [endpoint for endpoint, found in appearance_map.items() if found]
            self.log_result("Pre-delete appearance", "INFO", f"Appeared in: {appeared_before}")
            
            # Delete the test listing
            delete_response = requests.delete(f"{self.backend_url}/listings/{test_listing_id}")
            if delete_response.status_code == 200:
                self.log_result("Test Listing Deletion", "PASS", f"Deleted listing {test_listing_id}")
                
                # Wait for deletion to propagate
                import time
                time.sleep(1)
                
                # Check if listing is removed from all endpoints
                endpoints_to_check = [
                    ("/marketplace/browse", "Browse endpoint"),
                    ("/listings", "Listings endpoint"),
                    (f"/user/my-listings/{self.admin_user['id']}", "User listings endpoint"),
                    (f"/listings/{test_listing_id}", "Individual listing endpoint")
                ]
                
                orphaned_collections = []
                
                for endpoint, description in endpoints_to_check:
                    try:
                        response = requests.get(f"{self.backend_url}{endpoint}")
                        
                        # For individual listing, 404 is expected after deletion
                        if endpoint.endswith(test_listing_id):
                            if response.status_code == 404:
                                self.log_result(f"Post-delete {description}", "PASS", "Correctly returns 404")
                            else:
                                self.log_result(f"Post-delete {description}", "FAIL", 
                                              f"Should be 404, got {response.status_code}")
                                orphaned_collections.append(endpoint)
                            continue
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Search for our deleted test listing
                            found = False
                            if isinstance(data, list):
                                found = any(item.get('id') == test_listing_id or 
                                          item.get('title') == 'DATABASE_INVESTIGATION_TEST_ITEM' 
                                          for item in data)
                            elif isinstance(data, dict) and 'listings' in data:
                                found = any(item.get('id') == test_listing_id or 
                                          item.get('title') == 'DATABASE_INVESTIGATION_TEST_ITEM' 
                                          for item in data['listings'])
                            
                            if found:
                                self.log_result(f"CRITICAL: Orphaned in {description}", "FAIL", 
                                              "Listing still exists after deletion")
                                orphaned_collections.append(endpoint)
                            else:
                                self.log_result(f"Post-delete {description}", "PASS", 
                                              "Listing properly removed")
                        else:
                            self.log_result(f"Post-delete {description}", "FAIL", 
                                          f"HTTP {response.status_code}")
                    except Exception as e:
                        self.log_result(f"Post-delete {description}", "FAIL", f"Error: {str(e)}")
                
                if orphaned_collections:
                    self.log_result("CRITICAL: Orphaned Records Found", "FAIL", 
                                  f"Listing remains in: {orphaned_collections}")
                else:
                    self.log_result("Delete Operation Integrity", "PASS", 
                                  "Listing removed from all collections")
                    
                return orphaned_collections
            else:
                self.log_result("Test Listing Deletion", "FAIL", f"Status: {delete_response.status_code}")
                return []
                
        except Exception as e:
            self.log_result("Delete Operation Investigation", "FAIL", f"Error: {str(e)}")
            return []
    
    def investigate_database_integrity(self):
        """5. Database Integrity Check"""
        print("\n" + "="*80)
        print("5. DATABASE INTEGRITY CHECK")
        print("="*80)
        
        try:
            # Get all listings from different endpoints
            browse_response = requests.get(f"{self.backend_url}/marketplace/browse")
            listings_response = requests.get(f"{self.backend_url}/listings")
            
            browse_data = browse_response.json() if browse_response.status_code == 200 else []
            listings_data = listings_response.json() if listings_response.status_code == 200 else []
            
            # Handle different response structures
            if isinstance(listings_data, dict) and 'listings' in listings_data:
                listings_data = listings_data['listings']
            
            # Check for duplicates within each collection
            browse_titles = {}
            listings_titles = {}
            
            if isinstance(browse_data, list):
                for item in browse_data:
                    title = item.get('title', 'Unknown')
                    item_id = item.get('id', item.get('_id', 'Unknown'))
                    if title in browse_titles:
                        browse_titles[title].append(item_id)
                    else:
                        browse_titles[title] = [item_id]
            
            if isinstance(listings_data, list):
                for item in listings_data:
                    title = item.get('title', 'Unknown')
                    item_id = item.get('id', item.get('_id', 'Unknown'))
                    if title in listings_titles:
                        listings_titles[title].append(item_id)
                    else:
                        listings_titles[title] = [item_id]
            
            # Find duplicates
            browse_duplicates = {title: ids for title, ids in browse_titles.items() if len(ids) > 1}
            listings_duplicates = {title: ids for title, ids in listings_titles.items() if len(ids) > 1}
            
            if browse_duplicates:
                self.log_result("CRITICAL: Duplicates in Browse", "FAIL", 
                              f"Found {len(browse_duplicates)} duplicate titles: {list(browse_duplicates.keys())[:3]}")
            else:
                self.log_result("Browse Collection Duplicates", "PASS", "No duplicate titles found")
            
            if listings_duplicates:
                self.log_result("CRITICAL: Duplicates in Listings", "FAIL", 
                              f"Found {len(listings_duplicates)} duplicate titles: {list(listings_duplicates.keys())[:3]}")
            else:
                self.log_result("Listings Collection Duplicates", "PASS", "No duplicate titles found")
            
            # Check for cross-collection inconsistencies
            browse_items = {item.get('id', item.get('_id')): item for item in browse_data} if isinstance(browse_data, list) else {}
            listings_items = {item.get('id', item.get('_id')): item for item in listings_data} if isinstance(listings_data, list) else {}
            
            # Find items with same ID but different content
            content_mismatches = []
            for item_id in browse_items:
                if item_id in listings_items:
                    browse_item = browse_items[item_id]
                    listings_item = listings_items[item_id]
                    
                    # Compare key fields
                    fields_to_compare = ['title', 'price', 'description', 'category', 'seller_id']
                    mismatched_fields = []
                    
                    for field in fields_to_compare:
                        if browse_item.get(field) != listings_item.get(field):
                            mismatched_fields.append(field)
                    
                    if mismatched_fields:
                        content_mismatches.append({
                            'id': item_id,
                            'mismatched_fields': mismatched_fields
                        })
            
            if content_mismatches:
                self.log_result("CRITICAL: Content Mismatches", "FAIL", 
                              f"Found {len(content_mismatches)} items with different content across collections")
            else:
                self.log_result("Cross-Collection Content Integrity", "PASS", 
                              "No content mismatches found")
            
            return {
                "browse_duplicates": browse_duplicates,
                "listings_duplicates": listings_duplicates,
                "content_mismatches": content_mismatches
            }
            
        except Exception as e:
            self.log_result("Database Integrity Check", "FAIL", f"Error: {str(e)}")
            return {}
    
    def investigate_collection_fragmentation(self):
        """6. Collection Cross-Reference and Fragmentation Check"""
        print("\n" + "="*80)
        print("6. COLLECTION CROSS-REFERENCE AND FRAGMENTATION")
        print("="*80)
        
        try:
            # Test different user scenarios
            users_to_test = [self.admin_user, self.regular_user]
            
            for user in users_to_test:
                user_type = "Admin" if user['email'] == 'admin@cataloro.com' else "Regular"
                
                # Get user's listings
                user_listings_response = requests.get(f"{self.backend_url}/user/my-listings/{user['id']}")
                if user_listings_response.status_code == 200:
                    user_listings = user_listings_response.json()
                    user_listing_ids = {item.get('id', item.get('_id')) for item in user_listings}
                    
                    self.log_result(f"{user_type} User Listings Count", "INFO", 
                                  f"{len(user_listing_ids)} listings")
                    
                    # Check if these listings appear in browse
                    browse_response = requests.get(f"{self.backend_url}/marketplace/browse")
                    if browse_response.status_code == 200:
                        browse_data = browse_response.json()
                        browse_ids = {item.get('id', item.get('_id')) for item in browse_data}
                        
                        missing_from_browse = user_listing_ids - browse_ids
                        if missing_from_browse:
                            self.log_result(f"CRITICAL: {user_type} listings missing from browse", "FAIL", 
                                          f"{len(missing_from_browse)} items not in browse")
                        else:
                            self.log_result(f"{user_type} listings in browse", "PASS", 
                                          "All user listings appear in browse")
                    
                    # Check if these listings appear in main listings
                    listings_response = requests.get(f"{self.backend_url}/listings")
                    if listings_response.status_code == 200:
                        listings_data = listings_response.json()
                        if isinstance(listings_data, dict) and 'listings' in listings_data:
                            listings_data = listings_data['listings']
                        
                        main_listing_ids = {item.get('id', item.get('_id')) for item in listings_data}
                        missing_from_main = user_listing_ids - main_listing_ids
                        
                        if missing_from_main:
                            self.log_result(f"CRITICAL: {user_type} listings missing from main", "FAIL", 
                                          f"{len(missing_from_main)} items not in main listings")
                        else:
                            self.log_result(f"{user_type} listings in main", "PASS", 
                                          "All user listings appear in main listings")
                else:
                    self.log_result(f"{user_type} User Listings Access", "FAIL", 
                                  f"Status: {user_listings_response.status_code}")
            
        except Exception as e:
            self.log_result("Collection Fragmentation Check", "FAIL", f"Error: {str(e)}")
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n" + "="*80)
        print("DATABASE INVESTIGATION SUMMARY REPORT")
        print("="*80)
        
        # Count results by status
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARN'])
        info = len([r for r in self.test_results if r['status'] == 'INFO'])
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"ℹ️  Info: {info}")
        
        # Critical issues
        critical_issues = [r for r in self.test_results if r['status'] == 'FAIL' and 'CRITICAL' in r['test']]
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(critical_issues)}):")
            for issue in critical_issues:
                print(f"   • {issue['test']}: {issue['details']}")
        
        # All failures
        all_failures = [r for r in self.test_results if r['status'] == 'FAIL']
        if all_failures:
            print(f"\n❌ ALL FAILURES ({len(all_failures)}):")
            for failure in all_failures:
                print(f"   • {failure['test']}: {failure['details']}")
        
        return {
            "total_tests": len(self.test_results),
            "passed": passed,
            "failed": failed,
            "critical_issues": len(critical_issues),
            "all_results": self.test_results
        }
    
    def run_investigation(self):
        """Run complete database investigation"""
        print("STARTING CRITICAL DATABASE INVESTIGATION")
        print("Investigating reported issue: 'items appearing in user listings but not in all listings'")
        print("="*80)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to setup test users. Cannot proceed with investigation.")
            return False
        
        # Run investigations
        collection_data = self.investigate_database_structure()
        data_analysis = self.investigate_data_sources(collection_data)
        test_listing_id, appearance_map = self.investigate_api_endpoints()
        orphaned_collections = self.investigate_delete_operations(test_listing_id, appearance_map)
        integrity_results = self.investigate_database_integrity()
        self.investigate_collection_fragmentation()
        
        # Generate report
        summary = self.generate_summary_report()
        
        return summary['failed'] == 0

def main():
    """Main execution function"""
    investigator = DatabaseInvestigator()
    success = investigator.run_investigation()
    
    if success:
        print("\n✅ DATABASE INVESTIGATION COMPLETED - NO CRITICAL ISSUES FOUND")
        sys.exit(0)
    else:
        print("\n❌ DATABASE INVESTIGATION COMPLETED - CRITICAL ISSUES DETECTED")
        sys.exit(1)

if __name__ == "__main__":
    main()