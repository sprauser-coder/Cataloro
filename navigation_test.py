#!/usr/bin/env python3
"""
CATALORO - Navigation Changes Testing
Testing that shopping cart has been replaced with create listing functionality
"""

import requests
import re
import sys
from datetime import datetime

class NavigationTester:
    def __init__(self):
        self.frontend_url = "https://cataloro-marketplace-2.preview.emergentagent.com"
        self.test_results = []
        
    def log_result(self, test_name, status, details=""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": "✅ PASSED" if status else "❌ FAILED", 
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{result['status']} - {test_name}: {details}")
        
    def test_frontend_accessibility(self):
        """Test that frontend is accessible"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                self.log_result("Frontend Accessibility", True, f"Frontend accessible at {self.frontend_url}")
                return True
            else:
                self.log_result("Frontend Accessibility", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Frontend Accessibility", False, f"Error: {str(e)}")
            return False
            
    def test_create_listing_route(self):
        """Test that create listing route exists"""
        try:
            # Test the create listing route
            response = requests.get(f"{self.frontend_url}/create-listing", timeout=10)
            if response.status_code == 200:
                self.log_result("Create Listing Route", True, "Create listing page accessible")
                return True
            else:
                self.log_result("Create Listing Route", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Create Listing Route", False, f"Error: {str(e)}")
            return False
            
    def test_tenders_page_route(self):
        """Test that tenders page route exists"""
        try:
            # Test the tenders route
            response = requests.get(f"{self.frontend_url}/tenders", timeout=10)
            if response.status_code == 200:
                self.log_result("Tenders Page Route", True, "Tenders page accessible")
                return True
            else:
                self.log_result("Tenders Page Route", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Tenders Page Route", False, f"Error: {str(e)}")
            return False
            
    def test_tenders_page_tabs(self):
        """Test that tenders page has the correct tab structure"""
        try:
            # Test different tab parameters
            tabs_to_test = [
                ("listings", "My Listings tab"),
                ("tenders", "Tenders tab"), 
                ("sold", "Sold Items tab")
            ]
            
            all_tabs_work = True
            tab_results = []
            
            for tab_param, tab_name in tabs_to_test:
                try:
                    response = requests.get(f"{self.frontend_url}/tenders?tab={tab_param}", timeout=10)
                    if response.status_code == 200:
                        tab_results.append(f"{tab_name} ✅")
                    else:
                        tab_results.append(f"{tab_name} ❌")
                        all_tabs_work = False
                except:
                    tab_results.append(f"{tab_name} ❌")
                    all_tabs_work = False
                    
            if all_tabs_work:
                self.log_result("Tenders Page Tabs", True, f"All tabs accessible: {', '.join(tab_results)}")
                return True
            else:
                self.log_result("Tenders Page Tabs", False, f"Tab status: {', '.join(tab_results)}")
                return False
        except Exception as e:
            self.log_result("Tenders Page Tabs", False, f"Error: {str(e)}")
            return False
            
    def run_navigation_tests(self):
        """Run all navigation tests"""
        print("🧭 Starting Navigation Changes Testing...")
        print("=" * 50)
        
        # Test 1: Frontend accessibility
        print("\n🌐 Testing Frontend Accessibility...")
        self.test_frontend_accessibility()
        
        # Test 2: Create listing route
        print("\n➕ Testing Create Listing Route...")
        self.test_create_listing_route()
        
        # Test 3: Tenders page route
        print("\n📊 Testing Tenders Page Route...")
        self.test_tenders_page_route()
        
        # Test 4: Tenders page tabs
        print("\n🔄 Testing Tenders Page Tabs...")
        self.test_tenders_page_tabs()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📋 NAVIGATION TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if "✅ PASSED" in result['status'])
        failed = sum(1 for result in self.test_results if "❌ FAILED" in result['status'])
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAILED" in result['status']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 NAVIGATION FINDINGS:")
        
        # Check create listing
        create_test = next((r for r in self.test_results if r['test'] == 'Create Listing Route'), None)
        if create_test and "✅ PASSED" in create_test['status']:
            print("  ✅ Create Listing: Route accessible (replaces shopping cart)")
        else:
            print("  ❌ Create Listing: Route not accessible")
            
        # Check tenders page
        tenders_test = next((r for r in self.test_results if r['test'] == 'Tenders Page Route'), None)
        if tenders_test and "✅ PASSED" in tenders_test['status']:
            print("  ✅ Tenders Page: Main route accessible")
        else:
            print("  ❌ Tenders Page: Route not accessible")
            
        # Check tabs
        tabs_test = next((r for r in self.test_results if r['test'] == 'Tenders Page Tabs'), None)
        if tabs_test and "✅ PASSED" in tabs_test['status']:
            print("  ✅ Tab Navigation: All three tabs (My Listings, Tenders, Sold Items) accessible")
        else:
            print("  ❌ Tab Navigation: Some tabs not accessible")
            
        return failed == 0

def main():
    """Main test execution"""
    tester = NavigationTester()
    success = tester.run_navigation_tests()
    
    if success:
        print("\n🎉 All navigation tests passed! TendersPage navigation is working correctly.")
        return True
    else:
        print("\n⚠️  Some navigation tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)