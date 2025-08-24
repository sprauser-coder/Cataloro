import requests
import json

class AuthEdgeCaseTester:
    def __init__(self, base_url="https://marketplace-fix-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        
    def test_duplicate_registration(self):
        """Test registering with duplicate email/username"""
        print("🔍 Testing duplicate registration...")
        
        user_data = {
            "email": "duplicate@example.com",
            "username": "duplicateuser",
            "password": "TestPass123!",
            "full_name": "Duplicate User",
            "role": "buyer"
        }
        
        # First registration
        response1 = requests.post(f"{self.api_url}/auth/register", json=user_data)
        success1 = response1.status_code == 200
        
        # Second registration (should fail)
        response2 = requests.post(f"{self.api_url}/auth/register", json=user_data)
        success2 = response2.status_code == 400
        
        if success1 and success2:
            print("✅ Duplicate registration properly rejected")
            return True
        else:
            print(f"❌ Duplicate registration test failed: {response2.status_code}")
            return False
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        print("🔍 Testing invalid login...")
        
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = requests.post(f"{self.api_url}/auth/login", json=login_data)
        
        if response.status_code == 401:
            print("✅ Invalid login properly rejected")
            return True
        else:
            print(f"❌ Invalid login test failed: {response.status_code}")
            return False
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        print("🔍 Testing protected endpoint without token...")
        
        listing_data = {
            "title": "Test Product",
            "description": "Test description",
            "category": "Electronics",
            "listing_type": "fixed_price",
            "price": 99.99,
            "condition": "New",
            "quantity": 1,
            "location": "Test City"
        }
        
        response = requests.post(f"{self.api_url}/listings", json=listing_data)
        
        if response.status_code == 403:
            print("✅ Protected endpoint properly secured")
            return True
        else:
            print(f"❌ Protected endpoint test failed: {response.status_code}")
            return False
    
    def test_invalid_token(self):
        """Test using invalid token"""
        print("🔍 Testing invalid token...")
        
        headers = {'Authorization': 'Bearer invalid_token_here'}
        response = requests.get(f"{self.api_url}/cart", headers=headers)
        
        if response.status_code == 401:
            print("✅ Invalid token properly rejected")
            return True
        else:
            print(f"❌ Invalid token test failed: {response.status_code}")
            return False

def main():
    print("🔐 Testing Authentication Edge Cases")
    print("=" * 45)
    
    tester = AuthEdgeCaseTester()
    
    tests = [
        tester.test_duplicate_registration,
        tester.test_invalid_login,
        tester.test_protected_endpoint_without_token,
        tester.test_invalid_token
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 45)
    print(f"📊 Auth Edge Case Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All authentication edge cases handled correctly!")
        return 0
    else:
        print("⚠️  Some authentication tests failed")
        return 1

if __name__ == "__main__":
    main()