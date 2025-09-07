#!/usr/bin/env python3
"""
Detailed Rate Limiting Test - Understanding the rate limiting behavior
"""

import requests
import time
import json

BACKEND_URL = "https://marketplace-central.preview.emergentagent.com/api"

def test_same_email_rate_limiting():
    """Test rate limiting with same email"""
    print("🔒 Testing Rate Limiting with Same Email...")
    
    email = "same.email.test@example.com"
    
    for i in range(8):
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": email,
                "password": f"wrongpassword{i}"  # Different passwords
            }, timeout=10)
            
            print(f"Attempt {i+1}: Status {response.status_code}")
            
            if response.status_code == 429:
                print(f"✅ Rate limited after {i+1} attempts with same email!")
                return True
            
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Attempt {i+1}: Exception - {e}")
    
    print("❌ No rate limiting detected with same email")
    return False

def test_different_emails_same_session():
    """Test rate limiting with different emails in same session"""
    print("\n🔒 Testing Rate Limiting with Different Emails (Same Session)...")
    
    session = requests.Session()
    
    for i in range(8):
        try:
            response = session.post(f"{BACKEND_URL}/auth/login", json={
                "email": f"different{i}@example.com",
                "password": "wrongpassword"
            }, timeout=10)
            
            print(f"Attempt {i+1}: Status {response.status_code}")
            
            if response.status_code == 429:
                print(f"✅ Rate limited after {i+1} attempts with different emails!")
                return True
            
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Attempt {i+1}: Exception - {e}")
    
    print("❌ No rate limiting detected with different emails")
    return False

def test_registration_same_session():
    """Test registration rate limiting in same session"""
    print("\n🔒 Testing Registration Rate Limiting (Same Session)...")
    
    session = requests.Session()
    
    for i in range(6):
        try:
            timestamp = int(time.time() * 1000)  # More unique timestamps
            response = session.post(f"{BACKEND_URL}/auth/register", json={
                "username": f"regtest{i}_{timestamp}",
                "email": f"regtest{i}_{timestamp}@example.com",
                "full_name": f"Registration Test {i}",
                "account_type": "buyer"
            }, timeout=10)
            
            print(f"Attempt {i+1}: Status {response.status_code}")
            
            if response.status_code == 429:
                print(f"✅ Rate limited after {i+1} registration attempts!")
                return True
            
            time.sleep(0.1)
            
        except Exception as e:
            print(f"Attempt {i+1}: Exception - {e}")
    
    print("❌ No registration rate limiting detected")
    return False

def test_rapid_fire_same_credentials():
    """Test rapid fire with exact same credentials"""
    print("\n🔒 Testing Rapid Fire with Same Credentials...")
    
    email = "rapidfire@example.com"
    password = "wrongpassword"
    
    for i in range(10):
        try:
            start = time.time()
            response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": email,
                "password": password
            }, timeout=10)
            
            duration = time.time() - start
            print(f"Attempt {i+1}: Status {response.status_code}, Duration: {duration:.3f}s")
            
            if response.status_code == 429:
                print(f"✅ Rate limited after {i+1} rapid attempts!")
                try:
                    error_data = response.json()
                    print(f"   Rate limit error: {error_data}")
                except:
                    print(f"   Rate limit text: {response.text}")
                return True
            
            # No delay for rapid fire test
            
        except Exception as e:
            print(f"Attempt {i+1}: Exception - {e}")
    
    print("❌ No rate limiting detected in rapid fire test")
    return False

def main():
    """Run detailed rate limiting tests"""
    print("🚀 DETAILED RATE LIMITING TESTING")
    print("=" * 50)
    
    tests = [
        test_same_email_rate_limiting,
        test_different_emails_same_session,
        test_registration_same_session,
        test_rapid_fire_same_credentials
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
    
    if passed > 0:
        print("✅ Rate limiting is working in some scenarios")
    else:
        print("⚠️  Rate limiting may need configuration adjustment")

if __name__ == "__main__":
    main()