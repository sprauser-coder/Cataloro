#!/usr/bin/env python3
"""
Rate Limiting Test - Focused testing of rate limiting functionality
"""

import requests
import time
import json
from datetime import datetime

BACKEND_URL = "https://marketplace-admin-1.preview.emergentagent.com/api"

def test_login_rate_limiting():
    """Test login rate limiting with different approaches"""
    print("🔒 Testing Login Rate Limiting...")
    
    # Use a fresh session for each test
    session = requests.Session()
    
    # Test with rapid successive requests
    print("Testing rapid successive login attempts...")
    
    for i in range(8):
        try:
            start_time = time.time()
            response = session.post(f"{BACKEND_URL}/auth/login", json={
                "email": f"ratetest{i}@example.com",
                "password": "wrongpassword"
            }, timeout=10)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"Attempt {i+1}: Status {response.status_code}, Duration: {duration:.2f}s")
            
            if response.status_code == 429:
                print(f"✅ Rate limited after {i+1} attempts!")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return True
            
            # Small delay to avoid overwhelming
            time.sleep(0.2)
            
        except Exception as e:
            print(f"Attempt {i+1}: Exception - {e}")
    
    print("❌ No rate limiting detected")
    return False

def test_registration_rate_limiting():
    """Test registration rate limiting"""
    print("\n🔒 Testing Registration Rate Limiting...")
    
    session = requests.Session()
    
    for i in range(6):
        try:
            start_time = time.time()
            response = session.post(f"{BACKEND_URL}/auth/register", json={
                "username": f"ratetest{i}_{int(time.time())}",
                "email": f"ratetest{i}_{int(time.time())}@example.com",
                "full_name": f"Rate Test User {i}",
                "account_type": "buyer"
            }, timeout=10)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"Attempt {i+1}: Status {response.status_code}, Duration: {duration:.2f}s")
            
            if response.status_code == 429:
                print(f"✅ Rate limited after {i+1} attempts!")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                return True
            
            time.sleep(0.2)
            
        except Exception as e:
            print(f"Attempt {i+1}: Exception - {e}")
    
    print("❌ No rate limiting detected")
    return False

def test_rate_limiting_with_same_ip():
    """Test rate limiting behavior with same IP"""
    print("\n🔒 Testing Rate Limiting with Same IP...")
    
    # Test login endpoint with same credentials repeatedly
    for i in range(10):
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": "same.user@example.com",
                "password": "wrongpassword"
            }, timeout=10)
            
            print(f"Attempt {i+1}: Status {response.status_code}")
            
            if response.status_code == 429:
                print(f"✅ Rate limited after {i+1} attempts!")
                return True
            
            # Check for other rate limiting indicators
            if response.status_code == 403 and "too many" in response.text.lower():
                print(f"✅ Rate limited (403) after {i+1} attempts!")
                return True
            
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Attempt {i+1}: Exception - {e}")
    
    print("❌ No rate limiting detected with same IP")
    return False

def main():
    """Run rate limiting tests"""
    print("🚀 RATE LIMITING FOCUSED TESTING")
    print("=" * 50)
    
    tests = [
        test_login_rate_limiting,
        test_registration_rate_limiting,
        test_rate_limiting_with_same_ip
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == 0:
        print("⚠️  Rate limiting may not be properly configured or working")
    elif passed < total:
        print("⚠️  Some rate limiting tests failed")
    else:
        print("✅ All rate limiting tests passed!")

if __name__ == "__main__":
    main()