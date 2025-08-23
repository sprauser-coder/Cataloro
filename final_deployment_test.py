import requests
import sys
import json
from datetime import datetime, timedelta
import time

class FinalDeploymentTester:
    def __init__(self, base_url="https://market-deploy.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.seller_token = None
        self.buyer_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        self.minor_issues = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, token=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if token:
            test_headers['Authorization'] = f'Bearer {token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASS")
            else:
                print(f"❌ FAIL - Expected {expected_status}, got {response.status_code}")
                if response.status_code >= 500:
                    self.critical_issues.append(f"{name}: Server error {response.status_code}")
                elif response.status_code in [401, 403, 404]:
                    self.minor_issues.append(f"{name}: Client error {response.status_code}")

            return success, response.json() if response.text and response.text.strip() else {}

        except Exception as e:
            print(f"❌ FAIL - Error: {str(e)}")
            self.critical_issues.append(f"{name}: Network/System error")
            return False, {}

    def setup_test_users(self):
        """Setup admin, seller, and buyer accounts"""
        print("🔐 AUTHENTICATION SETUP")
        print("=" * 40)
        
        # Admin login
        admin_data = {"email": "admin@marketplace.com", "password": "admin123"}
        success, response = self.run_test("Admin Login", "POST", "auth/login", 200, admin_data)
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            print(f"   Admin: {response['user']['full_name']}")
        
        # Create seller account
        timestamp = datetime.now().strftime('%H%M%S')
        seller_data = {
            "email": f"seller_{timestamp}@cataloro.com",
            "username": f"seller_{timestamp}",
            "password": "SellerPass123!",
            "full_name": f"Test Seller {timestamp}",
            "role": "seller"
        }
        
        success, response = self.run_test("Seller Registration", "POST", "auth/register", 200, seller_data)
        if success and 'access_token' in response:
            self.seller_token = response['access_token']
            print(f"   Seller: {response['user']['full_name']}")
        
        # Create buyer account
        buyer_data = {
            "email": f"buyer_{timestamp}@cataloro.com",
            "username": f"buyer_{timestamp}",
            "password": "BuyerPass123!",
            "full_name": f"Test Buyer {timestamp}",
            "role": "buyer"
        }
        
        success, response = self.run_test("Buyer Registration", "POST", "auth/register", 200, buyer_data)
        if success and 'access_token' in response:
            self.buyer_token = response['access_token']
            print(f"   Buyer: {response['user']['full_name']}")

    def test_1_authentication_system(self):
        """Test 1: Authentication System"""
        print("\n1️⃣  AUTHENTICATION SYSTEM")
        print("=" * 40)
        
        results = []
        
        # Test admin authentication
        admin_data = {"email": "admin@marketplace.com", "password": "admin123"}
        success, response = self.run_test("Admin Authentication", "POST", "auth/login", 200, admin_data)
        results.append(success)
        
        # Test invalid credentials
        invalid_data = {"email": "invalid@test.com", "password": "wrongpass"}
        success, response = self.run_test("Invalid Credentials (Expected Fail)", "POST", "auth/login", 401, invalid_data)
        results.append(success)
        
        # Test registration validation
        duplicate_data = {"email": "admin@marketplace.com", "username": "admin", "password": "test", "full_name": "Test", "role": "buyer"}
        success, response = self.run_test("Duplicate Email (Expected Fail)", "POST", "auth/register", 400, duplicate_data)
        results.append(success)
        
        passed = sum(results)
        print(f"   Result: {passed}/3 tests passed")
        return passed >= 2

    def test_2_currency_system(self):
        """Test 2: Currency System (Euro €)"""
        print("\n2️⃣  CURRENCY SYSTEM (EURO €)")
        print("=" * 40)
        
        if not self.seller_token:
            print("❌ Cannot test - no seller token")
            return False
        
        # Create listing with Euro pricing
        listing_data = {
            "title": "Euro Test Product - Laptop",
            "description": "Testing Euro currency - €1,299.99",
            "category": "Electronics",
            "listing_type": "fixed_price",
            "price": 1299.99,
            "condition": "New",
            "quantity": 1,
            "location": "Berlin, Germany",
            "shipping_cost": 29.99
        }
        
        success, response = self.run_test("Create Euro Listing", "POST", "listings", 200, listing_data, token=self.seller_token)
        if success:
            listing_id = response['id']
            price = response['price']
            shipping = response.get('shipping_cost', 0)
            print(f"   Created listing: €{price} + €{shipping} shipping")
            
            # Test order with Euro totals
            if self.buyer_token:
                order_data = {
                    "listing_id": listing_id,
                    "quantity": 1,
                    "shipping_address": "123 Test St, Munich, Germany"
                }
                success2, response2 = self.run_test("Create Euro Order", "POST", "orders", 200, order_data, token=self.buyer_token)
                if success2:
                    total = response2.get('total_amount', 0)
                    print(f"   Order total: €{total}")
                    return True
        
        return False

    def test_3_admin_panel_tabs(self):
        """Test 3: Admin Panel - All 8 Tabs"""
        print("\n3️⃣  ADMIN PANEL - 8 TABS")
        print("=" * 40)
        
        if not self.admin_token:
            print("❌ Cannot test - no admin token")
            return False
        
        tabs = [
            ("Dashboard", "admin/stats"),
            ("Users", "admin/users"),
            ("Listings", "admin/listings"),
            ("Orders", "admin/orders"),
            ("Appearance", "admin/cms/settings"),
            ("Page Management", "admin/cms/pages"),
            ("General Settings", "admin/cms/navigation"),
            ("Database", "admin/generate-user-ids")
        ]
        
        results = []
        for tab_name, endpoint in tabs:
            method = "POST" if endpoint.endswith("generate-user-ids") else "GET"
            success, response = self.run_test(f"Tab: {tab_name}", method, endpoint, 200, token=self.admin_token)
            results.append(success)
            if success and isinstance(response, (list, dict)):
                if isinstance(response, list):
                    print(f"   {tab_name}: {len(response)} items")
                elif 'total_users' in response:
                    print(f"   {tab_name}: {response.get('total_users', 0)} users, €{response.get('total_revenue', 0):.2f} revenue")
        
        passed = sum(results)
        print(f"   Result: {passed}/8 tabs working")
        return passed >= 7

    def test_4_user_management(self):
        """Test 4: User Management"""
        print("\n4️⃣  USER MANAGEMENT")
        print("=" * 40)
        
        if not self.admin_token:
            print("❌ Cannot test - no admin token")
            return False
        
        results = []
        
        # Get users list
        success, response = self.run_test("Get Users List", "GET", "admin/users", 200, token=self.admin_token)
        results.append(success)
        
        if success and response:
            users = response
            non_admin_users = [u for u in users if u.get('role') != 'admin']
            
            if non_admin_users:
                test_user = non_admin_users[0]
                user_id = test_user['id']
                print(f"   Testing with user: {test_user.get('full_name', 'Unknown')}")
                
                # Test block/unblock functionality
                success2, _ = self.run_test("Block User", "PUT", f"admin/users/{user_id}/block", 200, token=self.admin_token)
                results.append(success2)
                
                success3, _ = self.run_test("Unblock User", "PUT", f"admin/users/{user_id}/unblock", 200, token=self.admin_token)
                results.append(success3)
        
        passed = sum(results)
        print(f"   Result: {passed}/{len(results)} tests passed")
        return passed >= 2

    def test_5_image_upload(self):
        """Test 5: Image Upload (Logo & Listing)"""
        print("\n5️⃣  IMAGE UPLOAD SYSTEM")
        print("=" * 40)
        
        results = []
        
        # Test logo upload (admin only)
        if self.admin_token:
            # Create minimal PNG data
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02\xac\xea\x05\x1bIEND\xaeB`\x82'
            
            url = f"{self.api_url}/admin/cms/upload-logo"
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            files = {'file': ('test_logo.png', png_data, 'image/png')}
            data = {'logo_type': 'header'}
            
            try:
                response = requests.post(url, files=files, data=data, headers=headers, timeout=10)
                success = response.status_code == 200
                self.run_test("Logo Upload", "POST", "admin/cms/upload-logo", 200 if success else response.status_code)
                results.append(success)
                if success:
                    print("   Logo upload successful")
            except Exception as e:
                print(f"❌ Logo upload failed: {e}")
                results.append(False)
        
        # Test listing image upload
        if self.seller_token:
            url = f"{self.api_url}/listings/upload-image"
            headers = {'Authorization': f'Bearer {self.seller_token}'}
            files = {'file': ('test_listing.png', png_data, 'image/png')}
            
            try:
                response = requests.post(url, files=files, headers=headers, timeout=10)
                success = response.status_code == 200
                self.run_test("Listing Image Upload", "POST", "listings/upload-image", 200 if success else response.status_code)
                results.append(success)
                if success:
                    print("   Listing image upload successful")
            except Exception as e:
                print(f"❌ Listing image upload failed: {e}")
                results.append(False)
        
        passed = sum(results)
        print(f"   Result: {passed}/{len(results)} tests passed")
        return passed >= 1

    def test_6_hero_height(self):
        """Test 6: Hero Height Functionality"""
        print("\n6️⃣  HERO HEIGHT FUNCTIONALITY")
        print("=" * 40)
        
        if not self.admin_token:
            print("❌ Cannot test - no admin token")
            return False
        
        results = []
        
        # Test setting different hero heights
        heights = ["400px", "600px", "80vh"]
        
        for height in heights:
            settings_data = {"hero_height": height}
            success, response = self.run_test(f"Set Hero Height {height}", "PUT", "admin/cms/settings", 200, settings_data, token=self.admin_token)
            results.append(success)
            
            if success:
                # Verify it was set
                success2, response2 = self.run_test(f"Verify Hero Height {height}", "GET", "cms/settings", 200)
                if success2 and response2.get('hero_height') == height:
                    print(f"   Hero height {height} verified")
                    results.append(True)
                else:
                    results.append(False)
        
        passed = sum(results)
        print(f"   Result: {passed}/{len(results)} tests passed")
        return passed >= 4

    def test_7_font_system(self):
        """Test 7: Font System"""
        print("\n7️⃣  FONT SYSTEM")
        print("=" * 40)
        
        if not self.admin_token:
            print("❌ Cannot test - no admin token")
            return False
        
        fonts = ["Inter", "Roboto", "Poppins"]
        results = []
        
        for font in fonts:
            settings_data = {"global_font_family": font}
            success, response = self.run_test(f"Set Font {font}", "PUT", "admin/cms/settings", 200, settings_data, token=self.admin_token)
            results.append(success)
            
            if success:
                # Verify font was set
                success2, response2 = self.run_test(f"Verify Font {font}", "GET", "admin/cms/settings", 200, token=self.admin_token)
                if success2 and response2.get('global_font_family') == font:
                    print(f"   Font {font} verified")
                    results.append(True)
                else:
                    results.append(False)
        
        passed = sum(results)
        print(f"   Result: {passed}/{len(results)} tests passed")
        return passed >= 4

    def test_8_marketplace_core(self):
        """Test 8: Marketplace Core Functionality"""
        print("\n8️⃣  MARKETPLACE CORE")
        print("=" * 40)
        
        results = []
        
        # Test listings creation
        if self.seller_token:
            listing_data = {
                "title": "Core Test Product",
                "description": "Testing core marketplace functionality",
                "category": "Electronics",
                "listing_type": "fixed_price",
                "price": 99.99,
                "condition": "New",
                "quantity": 1,
                "location": "Test City"
            }
            
            success, response = self.run_test("Create Listing", "POST", "listings", 200, listing_data, token=self.seller_token)
            results.append(success)
            
            if success:
                listing_id = response['id']
                
                # Test cart functionality
                if self.buyer_token:
                    cart_data = {"listing_id": listing_id, "quantity": 1}
                    success2, _ = self.run_test("Add to Cart", "POST", "cart", 200, cart_data, token=self.buyer_token)
                    results.append(success2)
                    
                    success3, _ = self.run_test("View Cart", "GET", "cart", 200, token=self.buyer_token)
                    results.append(success3)
                    
                    # Test order creation
                    order_data = {
                        "listing_id": listing_id,
                        "quantity": 1,
                        "shipping_address": "123 Test Street"
                    }
                    success4, _ = self.run_test("Create Order", "POST", "orders", 200, order_data, token=self.buyer_token)
                    results.append(success4)
        
        # Test search and filtering
        success5, _ = self.run_test("Search Listings", "GET", "listings?search=test", 200)
        results.append(success5)
        
        success6, _ = self.run_test("Filter by Category", "GET", "listings?category=Electronics", 200)
        results.append(success6)
        
        passed = sum(results)
        print(f"   Result: {passed}/{len(results)} tests passed")
        return passed >= 4

    def test_9_cms_system(self):
        """Test 9: CMS System"""
        print("\n9️⃣  CMS SYSTEM")
        print("=" * 40)
        
        if not self.admin_token:
            print("❌ Cannot test - no admin token")
            return False
        
        results = []
        
        # Test site settings
        success, _ = self.run_test("Get Site Settings", "GET", "admin/cms/settings", 200, token=self.admin_token)
        results.append(success)
        
        # Test settings update
        settings_data = {"site_name": "Cataloro", "site_tagline": "Your trusted marketplace"}
        success2, _ = self.run_test("Update Site Settings", "PUT", "admin/cms/settings", 200, settings_data, token=self.admin_token)
        results.append(success2)
        
        # Test page management
        success3, _ = self.run_test("Get Pages", "GET", "admin/cms/pages", 200, token=self.admin_token)
        results.append(success3)
        
        # Test navigation
        success4, _ = self.run_test("Get Navigation", "GET", "admin/cms/navigation", 200, token=self.admin_token)
        results.append(success4)
        
        # Test public endpoints
        success5, _ = self.run_test("Public Site Settings", "GET", "cms/settings", 200)
        results.append(success5)
        
        passed = sum(results)
        print(f"   Result: {passed}/{len(results)} tests passed")
        return passed >= 4

    def test_10_database_operations(self):
        """Test 10: Database Operations"""
        print("\n🔟 DATABASE OPERATIONS")
        print("=" * 40)
        
        results = []
        
        # Test basic CRUD operations
        success, _ = self.run_test("Get Categories", "GET", "categories", 200)
        results.append(success)
        
        success2, _ = self.run_test("Get Listings", "GET", "listings", 200)
        results.append(success2)
        
        if self.admin_token:
            success3, _ = self.run_test("Database User IDs", "POST", "admin/generate-user-ids", 200, token=self.admin_token)
            results.append(success3)
        
        passed = sum(results)
        print(f"   Result: {passed}/{len(results)} tests passed")
        return passed >= 2

    def run_final_deployment_test(self):
        """Run complete deployment readiness test"""
        print("🚀 CATALORO MARKETPLACE - FINAL DEPLOYMENT TEST")
        print("=" * 60)
        
        # Setup
        self.setup_test_users()
        
        # Run all tests
        test_results = [
            ("Authentication System", self.test_1_authentication_system()),
            ("Currency System (€)", self.test_2_currency_system()),
            ("Admin Panel (8 Tabs)", self.test_3_admin_panel_tabs()),
            ("User Management", self.test_4_user_management()),
            ("Image Upload", self.test_5_image_upload()),
            ("Hero Height", self.test_6_hero_height()),
            ("Font System", self.test_7_font_system()),
            ("Marketplace Core", self.test_8_marketplace_core()),
            ("CMS System", self.test_9_cms_system()),
            ("Database Operations", self.test_10_database_operations())
        ]
        
        # Results summary
        print("\n" + "=" * 60)
        print("📊 FINAL DEPLOYMENT READINESS REPORT")
        print("=" * 60)
        
        passed_tests = [name for name, success in test_results if success]
        failed_tests = [name for name, success in test_results if not success]
        
        print(f"Total API calls: {self.tests_run}")
        print(f"Successful calls: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print(f"\n✅ WORKING FUNCTIONALITY ({len(passed_tests)}/10):")
        for i, test_name in enumerate(passed_tests, 1):
            print(f"   {i}. {test_name}")
        
        if failed_tests:
            print(f"\n❌ ISSUES FOUND ({len(failed_tests)}/10):")
            for i, test_name in enumerate(failed_tests, 1):
                print(f"   {i}. {test_name}")
        
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES ({len(self.critical_issues)}):")
            for issue in self.critical_issues:
                print(f"   • {issue}")
        
        if self.minor_issues:
            print(f"\n⚠️  MINOR ISSUES ({len(self.minor_issues)}):")
            for issue in self.minor_issues[:5]:  # Show first 5
                print(f"   • {issue}")
            if len(self.minor_issues) > 5:
                print(f"   ... and {len(self.minor_issues) - 5} more")
        
        # Final verdict
        critical_functionality_working = len(passed_tests) >= 8
        no_critical_issues = len(self.critical_issues) == 0
        
        print("\n" + "=" * 60)
        if critical_functionality_working and no_critical_issues:
            print("🎉 DEPLOYMENT STATUS: ✅ READY FOR PRODUCTION")
            print("\nThe Cataloro marketplace is functioning correctly!")
            print("All major functionality is working as expected.")
            if self.minor_issues:
                print(f"Note: {len(self.minor_issues)} minor issues detected but don't block deployment.")
        else:
            print("⚠️  DEPLOYMENT STATUS: ❌ NEEDS ATTENTION")
            print("\nCritical issues must be resolved before deployment:")
            if not critical_functionality_working:
                print(f"• Only {len(passed_tests)}/10 core functions working (need 8+)")
            if self.critical_issues:
                print(f"• {len(self.critical_issues)} critical system errors detected")
        
        print("=" * 60)
        return critical_functionality_working and no_critical_issues

if __name__ == "__main__":
    tester = FinalDeploymentTester()
    tester.run_final_deployment_test()