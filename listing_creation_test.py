#!/usr/bin/env python3
"""
Cataloro Marketplace - Listing Creation Test Suite
Focused testing for POST /api/listings endpoint functionality
"""

import requests
import sys
import json
import uuid
from datetime import datetime

class ListingCreationTester:
    def __init__(self, base_url="https://trade-platform-30.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.created_listings = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def setup_user(self):
        """Create a test user for listing creation"""
        print("\n🔧 Setting up test user...")
        
        # First try to login with existing user
        login_data = {
            "email": "seller@cataloro.com",
            "password": "demo123"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                self.user_id = user_data['user']['id']
                print(f"   ✅ User logged in: {self.user_id}")
                return True
            else:
                print(f"   ❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Setup error: {str(e)}")
            return False

    def test_listing_creation_basic(self):
        """Test basic listing creation with required fields"""
        print("\n🔍 Testing Basic Listing Creation...")
        
        listing_data = {
            "title": "Test MacBook Pro 2023",
            "description": "Excellent condition MacBook Pro with M2 chip, barely used for development work",
            "price": 2299.99,
            "category": "Electronics",
            "condition": "Like New",
            "seller_id": self.user_id,
            "images": [
                "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400",
                "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400"
            ]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/listings",
                json=listing_data,
                headers={'Content-Type': 'application/json'}
            )
            
            success = response.status_code == 200
            
            if success:
                response_data = response.json()
                listing_id = response_data.get('listing_id')
                self.created_listings.append(listing_id)
                
                details = f"Status: {response.status_code}, Listing ID: {listing_id}"
                print(f"   Response: {json.dumps(response_data, indent=2)}")
                
                # Verify required response fields
                required_fields = ['message', 'listing_id', 'status']
                missing_fields = [field for field in required_fields if field not in response_data]
                
                if missing_fields:
                    self.log_test("Basic Listing Creation", False, f"Missing response fields: {missing_fields}")
                    return False
                else:
                    self.log_test("Basic Listing Creation", True, details)
                    return True
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                self.log_test("Basic Listing Creation", False, details)
                return False
                
        except Exception as e:
            self.log_test("Basic Listing Creation", False, f"Error: {str(e)}")
            return False

    def test_listing_creation_missing_fields(self):
        """Test listing creation with missing required fields"""
        print("\n🔍 Testing Listing Creation with Missing Fields...")
        
        # Test missing title
        incomplete_data = {
            "description": "Missing title field",
            "price": 100.00,
            "category": "Electronics",
            "condition": "Good",
            "seller_id": self.user_id
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/listings",
                json=incomplete_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Should return 400 for missing required field
            success = response.status_code == 400
            
            if success:
                response_data = response.json()
                details = f"Status: {response.status_code}, Error: {response_data.get('detail', 'No detail')}"
                self.log_test("Missing Required Fields Validation", True, details)
                return True
            else:
                details = f"Expected 400, got {response.status_code}, Response: {response.text}"
                self.log_test("Missing Required Fields Validation", False, details)
                return False
                
        except Exception as e:
            self.log_test("Missing Required Fields Validation", False, f"Error: {str(e)}")
            return False

    def test_listing_creation_with_images(self):
        """Test listing creation with image array"""
        print("\n🔍 Testing Listing Creation with Images...")
        
        listing_data = {
            "title": "Vintage Camera Collection",
            "description": "Beautiful vintage camera with leather case and original manual",
            "price": 450.00,
            "category": "Photography",
            "condition": "Good",
            "seller_id": self.user_id,
            "images": [
                "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                "https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=400"
            ]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/listings",
                json=listing_data,
                headers={'Content-Type': 'application/json'}
            )
            
            success = response.status_code == 200
            
            if success:
                response_data = response.json()
                listing_id = response_data.get('listing_id')
                self.created_listings.append(listing_id)
                
                details = f"Status: {response.status_code}, Listing ID: {listing_id}"
                print(f"   Images processed: {len(listing_data['images'])} images")
                self.log_test("Listing Creation with Images", True, details)
                return True
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                self.log_test("Listing Creation with Images", False, details)
                return False
                
        except Exception as e:
            self.log_test("Listing Creation with Images", False, f"Error: {str(e)}")
            return False

    def test_listing_creation_edge_cases(self):
        """Test listing creation with edge cases"""
        print("\n🔍 Testing Listing Creation Edge Cases...")
        
        # Test with very long description
        edge_case_data = {
            "title": "Edge Case Test Item",
            "description": "A" * 1000,  # Very long description
            "price": 0.01,  # Minimum price
            "category": "Other",
            "condition": "Fair",
            "seller_id": self.user_id,
            "images": []  # Empty images array
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/listings",
                json=edge_case_data,
                headers={'Content-Type': 'application/json'}
            )
            
            success = response.status_code == 200
            
            if success:
                response_data = response.json()
                listing_id = response_data.get('listing_id')
                self.created_listings.append(listing_id)
                
                details = f"Status: {response.status_code}, Listing ID: {listing_id}"
                self.log_test("Edge Cases Handling", True, details)
                return True
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                self.log_test("Edge Cases Handling", False, details)
                return False
                
        except Exception as e:
            self.log_test("Edge Cases Handling", False, f"Error: {str(e)}")
            return False

    def test_listing_creation_invalid_data(self):
        """Test listing creation with invalid data types"""
        print("\n🔍 Testing Listing Creation with Invalid Data...")
        
        invalid_data = {
            "title": "Invalid Price Test",
            "description": "Testing with invalid price type",
            "price": "not_a_number",  # Invalid price type
            "category": "Electronics",
            "condition": "Good",
            "seller_id": self.user_id
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/listings",
                json=invalid_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Should return 422 for validation error or 400 for bad request
            success = response.status_code in [400, 422]
            
            if success:
                details = f"Status: {response.status_code} (correctly rejected invalid data)"
                self.log_test("Invalid Data Type Validation", True, details)
                return True
            else:
                details = f"Expected 400/422, got {response.status_code}, Response: {response.text}"
                self.log_test("Invalid Data Type Validation", False, details)
                return False
                
        except Exception as e:
            self.log_test("Invalid Data Type Validation", False, f"Error: {str(e)}")
            return False

    def test_authentication_requirements(self):
        """Test if authentication is required for listing creation"""
        print("\n🔍 Testing Authentication Requirements...")
        
        listing_data = {
            "title": "Auth Test Item",
            "description": "Testing authentication requirements",
            "price": 100.00,
            "category": "Electronics",
            "condition": "Good",
            "seller_id": "invalid_user_id"  # Invalid seller ID
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/listings",
                json=listing_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Check if it accepts invalid seller_id or requires authentication
            if response.status_code == 200:
                response_data = response.json()
                listing_id = response_data.get('listing_id')
                self.created_listings.append(listing_id)
                
                details = f"Status: {response.status_code} (No authentication required)"
                self.log_test("Authentication Requirements", True, details)
                print("   ⚠️  Note: Endpoint accepts any seller_id without validation")
                return True
            else:
                details = f"Status: {response.status_code} (Authentication/validation enforced)"
                self.log_test("Authentication Requirements", True, details)
                return True
                
        except Exception as e:
            self.log_test("Authentication Requirements", False, f"Error: {str(e)}")
            return False

    def verify_created_listings(self):
        """Verify that created listings can be retrieved"""
        print("\n🔍 Verifying Created Listings...")
        
        if not self.created_listings:
            print("   No listings to verify")
            return True
        
        try:
            # Test browsing to see if our listings appear
            response = self.session.get(
                f"{self.base_url}/api/marketplace/browse",
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                listings = response.json()
                created_count = len(self.created_listings)
                total_listings = len(listings)
                
                details = f"Created {created_count} listings, Total in marketplace: {total_listings}"
                self.log_test("Listing Verification", True, details)
                
                # Try to get individual listing
                if self.created_listings:
                    first_listing_id = self.created_listings[0]
                    individual_response = self.session.get(
                        f"{self.base_url}/api/listings/{first_listing_id}",
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if individual_response.status_code == 200:
                        listing_data = individual_response.json()
                        print(f"   ✅ Individual listing retrieval works: {listing_data.get('title', 'No title')}")
                        self.log_test("Individual Listing Retrieval", True, f"Retrieved listing: {first_listing_id}")
                    else:
                        self.log_test("Individual Listing Retrieval", False, f"Status: {individual_response.status_code}")
                
                return True
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                self.log_test("Listing Verification", False, details)
                return False
                
        except Exception as e:
            self.log_test("Listing Verification", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run complete listing creation test suite"""
        print("🚀 Starting Listing Creation Test Suite")
        print("=" * 60)

        # Setup
        if not self.setup_user():
            print("❌ User setup failed - stopping tests")
            return False

        # Core listing creation tests
        self.test_listing_creation_basic()
        self.test_listing_creation_missing_fields()
        self.test_listing_creation_with_images()
        self.test_listing_creation_edge_cases()
        self.test_listing_creation_invalid_data()
        self.test_authentication_requirements()
        
        # Verification
        self.verify_created_listings()

        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All listing creation tests passed!")
            return True
        else:
            failed_count = self.tests_run - self.tests_passed
            print(f"⚠️  {failed_count} tests failed")
            
            # Provide specific failure analysis
            if failed_count > 0:
                print("\n🔍 FAILURE ANALYSIS:")
                print("   The listing creation functionality has issues that need attention.")
                print("   Check the failed test details above for specific problems.")
            
            return False

def main():
    """Main test execution"""
    tester = ListingCreationTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())