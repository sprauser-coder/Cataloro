#!/usr/bin/env python3
"""
Dynamic Price Range Configuration Testing
Testing the Cat Database & Basis section price range functionality
"""

import requests
import json
import sys
import time
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cataloro-admin-4.preview.emergentagent.com/api"

class PriceRangeConfigTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, success, details="", expected="", actual=""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "expected": expected,
            "actual": actual,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and expected:
            print(f"   Expected: {expected}")
            print(f"   Actual: {actual}")
        print()
        
    def test_price_range_settings_get_endpoint(self):
        """Test 1: Price Range Settings GET Endpoint"""
        try:
            response = self.session.get(f"{self.backend_url}/marketplace/price-range-settings")
            
            if response.status_code != 200:
                self.log_test(
                    "Price Range Settings GET Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200 OK",
                    f"{response.status_code}"
                )
                return False
                
            data = response.json()
            
            # Check if default values are returned
            expected_min = 10.0
            expected_max = 10.0
            
            actual_min = data.get("price_range_min_percent")
            actual_max = data.get("price_range_max_percent")
            
            if actual_min == expected_min and actual_max == expected_max:
                self.log_test(
                    "Price Range Settings GET Endpoint",
                    True,
                    f"Returns correct default values: min={actual_min}%, max={actual_max}%"
                )
                return True
            else:
                self.log_test(
                    "Price Range Settings GET Endpoint",
                    False,
                    "Default values incorrect",
                    f"min={expected_min}%, max={expected_max}%",
                    f"min={actual_min}%, max={actual_max}%"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Price Range Settings GET Endpoint",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_price_settings_retrieval(self):
        """Test 2: Price Settings Retrieval"""
        try:
            response = self.session.get(f"{self.backend_url}/admin/catalyst/price-settings")
            
            if response.status_code != 200:
                self.log_test(
                    "Price Settings Retrieval",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200 OK",
                    f"{response.status_code}"
                )
                return False
                
            data = response.json()
            
            # Check if all required fields are present
            required_fields = [
                "pt_price", "pd_price", "rh_price",
                "renumeration_pt", "renumeration_pd", "renumeration_rh",
                "price_range_min_percent", "price_range_max_percent"
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
            
            if not missing_fields:
                self.log_test(
                    "Price Settings Retrieval",
                    True,
                    f"All required fields present: {', '.join(required_fields)}"
                )
                return data
            else:
                self.log_test(
                    "Price Settings Retrieval",
                    False,
                    f"Missing fields: {', '.join(missing_fields)}",
                    f"All fields: {', '.join(required_fields)}",
                    f"Present fields: {', '.join(data.keys())}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Price Settings Retrieval",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_price_range_update(self):
        """Test 3: Price Range Update"""
        try:
            # Test data with different price range values
            test_settings = {
                "pt_price": 40.0,
                "pd_price": 40.0,
                "rh_price": 200.0,
                "renumeration_pt": 0.95,
                "renumeration_pd": 0.92,
                "renumeration_rh": 0.88,
                "price_range_min_percent": 15.0,  # Test with 15%
                "price_range_max_percent": 20.0   # Test with 20%
            }
            
            response = self.session.put(
                f"{self.backend_url}/admin/catalyst/price-settings",
                json=test_settings,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code not in [200, 201]:
                self.log_test(
                    "Price Range Update",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    "200/201 OK",
                    f"{response.status_code}"
                )
                return False
                
            result = response.json()
            
            if "message" in result and "success" in result.get("message", "").lower():
                self.log_test(
                    "Price Range Update",
                    True,
                    f"Successfully updated price settings with min={test_settings['price_range_min_percent']}%, max={test_settings['price_range_max_percent']}%"
                )
                return test_settings
            else:
                self.log_test(
                    "Price Range Update",
                    False,
                    f"Unexpected response: {result}",
                    "Success message",
                    str(result)
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Price Range Update",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_persistence_verification(self, expected_settings):
        """Test 4: Persistence Verification"""
        try:
            # Test both endpoints to verify persistence
            
            # Test 1: Check admin endpoint
            response1 = self.session.get(f"{self.backend_url}/admin/catalyst/price-settings")
            if response1.status_code != 200:
                self.log_test(
                    "Persistence Verification (Admin Endpoint)",
                    False,
                    f"HTTP {response1.status_code}: {response1.text}"
                )
                return False
                
            admin_data = response1.json()
            
            # Test 2: Check marketplace endpoint
            response2 = self.session.get(f"{self.backend_url}/marketplace/price-range-settings")
            if response2.status_code != 200:
                self.log_test(
                    "Persistence Verification (Marketplace Endpoint)",
                    False,
                    f"HTTP {response2.status_code}: {response2.text}"
                )
                return False
                
            marketplace_data = response2.json()
            
            # Verify admin endpoint has updated values
            admin_min = admin_data.get("price_range_min_percent")
            admin_max = admin_data.get("price_range_max_percent")
            
            # Verify marketplace endpoint has updated values
            market_min = marketplace_data.get("price_range_min_percent")
            market_max = marketplace_data.get("price_range_max_percent")
            
            expected_min = expected_settings["price_range_min_percent"]
            expected_max = expected_settings["price_range_max_percent"]
            
            admin_correct = (admin_min == expected_min and admin_max == expected_max)
            market_correct = (market_min == expected_min and market_max == expected_max)
            
            if admin_correct and market_correct:
                self.log_test(
                    "Persistence Verification",
                    True,
                    f"Both endpoints return updated values: min={expected_min}%, max={expected_max}%"
                )
                return True
            else:
                details = []
                if not admin_correct:
                    details.append(f"Admin endpoint: min={admin_min}%, max={admin_max}%")
                if not market_correct:
                    details.append(f"Marketplace endpoint: min={market_min}%, max={market_max}%")
                
                self.log_test(
                    "Persistence Verification",
                    False,
                    f"Values not persisted correctly. {'; '.join(details)}",
                    f"min={expected_min}%, max={expected_max}%",
                    "; ".join(details)
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Persistence Verification",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_database_storage_verification(self):
        """Test 5: Database Storage Verification"""
        try:
            # This test verifies the data structure by checking the admin endpoint
            # which should return the complete stored document
            response = self.session.get(f"{self.backend_url}/admin/catalyst/price-settings")
            
            if response.status_code != 200:
                self.log_test(
                    "Database Storage Verification",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
            data = response.json()
            
            # Check if the response indicates proper database storage
            # The presence of all fields suggests proper storage in catalyst_price_settings collection
            storage_indicators = [
                "pt_price", "pd_price", "rh_price",
                "price_range_min_percent", "price_range_max_percent"
            ]
            
            all_present = all(field in data for field in storage_indicators)
            
            if all_present:
                self.log_test(
                    "Database Storage Verification",
                    True,
                    "Price range settings properly stored with complete data structure"
                )
                return True
            else:
                missing = [field for field in storage_indicators if field not in data]
                self.log_test(
                    "Database Storage Verification",
                    False,
                    f"Incomplete data structure, missing: {', '.join(missing)}",
                    "Complete price settings structure",
                    f"Missing fields: {', '.join(missing)}"
                )
                return False
                
        except Exception as e:
            self.log_test(
                "Database Storage Verification",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all price range configuration tests"""
        print("=" * 80)
        print("DYNAMIC PRICE RANGE CONFIGURATION TESTING")
        print("Testing Cat Database & Basis section functionality")
        print("=" * 80)
        print()
        
        # Test 1: Price Range Settings GET Endpoint
        test1_success = self.test_price_range_settings_get_endpoint()
        
        # Test 2: Price Settings Retrieval
        test2_result = self.test_price_settings_retrieval()
        test2_success = bool(test2_result)
        
        # Test 3: Price Range Update
        test3_result = self.test_price_range_update()
        test3_success = bool(test3_result)
        
        # Test 4: Persistence Verification (only if update succeeded)
        test4_success = False
        if test3_success and test3_result:
            test4_success = self.test_persistence_verification(test3_result)
        else:
            self.log_test(
                "Persistence Verification",
                False,
                "Skipped due to failed price range update"
            )
        
        # Test 5: Database Storage Verification
        test5_success = self.test_database_storage_verification()
        
        # Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = 5
        passed_tests = sum([test1_success, test2_success, test3_success, test4_success, test5_success])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        # Individual test results
        tests = [
            ("Price Range Settings GET Endpoint", test1_success),
            ("Price Settings Retrieval", test2_success),
            ("Price Range Update", test3_success),
            ("Persistence Verification", test4_success),
            ("Database Storage Verification", test5_success)
        ]
        
        for test_name, success in tests:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print()
        
        # Critical issues
        critical_failures = []
        if not test1_success:
            critical_failures.append("Price range settings endpoint not working")
        if not test2_success:
            critical_failures.append("Price settings retrieval failing")
        if not test3_success:
            critical_failures.append("Price range update not working")
        if not test4_success and test3_success:
            critical_failures.append("Price range values not persisting")
        
        if critical_failures:
            print("CRITICAL ISSUES FOUND:")
            for issue in critical_failures:
                print(f"❌ {issue}")
        else:
            print("✅ ALL CRITICAL FUNCTIONALITY WORKING")
        
        print()
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = PriceRangeConfigTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL TESTS PASSED - Dynamic price range configuration is working correctly!")
        sys.exit(0)
    else:
        print("⚠️  SOME TESTS FAILED - Check the issues above")
        sys.exit(1)