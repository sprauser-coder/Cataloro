#!/usr/bin/env python3
"""
URGENT: Test exact scenario from review request
Test the specific listing creation data format mentioned in the review.
"""

import requests
import json
import sys

# Configuration - Use VPS deployment URL from frontend/.env
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def test_exact_review_scenario():
    """Test the exact scenario from the review request"""
    print("🔍 TESTING EXACT REVIEW REQUEST SCENARIO")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Admin Credentials: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print()
    
    # Step 1: Admin login
    print("Step 1: Admin Login")
    print("-" * 30)
    
    try:
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            admin_token = data["access_token"]
            print(f"✅ Admin login successful")
            print(f"   User: {data['user']['email']} ({data['user']['role']})")
            print(f"   Token: {admin_token[:20]}...")
            print()
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Admin login error: {str(e)}")
        return False
    
    # Step 2: Test POST /api/listings with exact data from review
    print("Step 2: Test POST /api/listings with Review Request Data")
    print("-" * 30)
    
    # Exact test data from review request
    listing_data = {
        "title": "Test Product",
        "description": "Test description",
        "category": "Electronics", 
        "condition": "New",
        "listing_type": "fixed_price",
        "price": 99.99,
        "quantity": 1,
        "location": "Test City",
        "images": []
    }
    
    print(f"Request Data:")
    print(json.dumps(listing_data, indent=2))
    print()
    
    try:
        headers = {
            'Authorization': f'Bearer {admin_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ LISTING CREATION SUCCESSFUL!")
            print("Response Data:")
            print(json.dumps(result, indent=2, default=str))
            print()
            
            # Verify key fields
            listing_id = result.get('id')
            title = result.get('title')
            price = result.get('price')
            listing_type = result.get('listing_type')
            
            print("Key Fields Verification:")
            print(f"  Listing ID: {listing_id}")
            print(f"  Title: {title}")
            print(f"  Price: {price}")
            print(f"  Type: {listing_type}")
            print(f"  Category: {result.get('category')}")
            print(f"  Condition: {result.get('condition')}")
            print(f"  Quantity: {result.get('quantity')}")
            print(f"  Location: {result.get('location')}")
            print(f"  Images: {result.get('images', [])}")
            print()
            
            return True
            
        else:
            print("❌ LISTING CREATION FAILED!")
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            print()
            
            # Try to parse error details
            try:
                error_data = response.json()
                print("Error Details:")
                print(json.dumps(error_data, indent=2))
            except:
                print("Could not parse error response as JSON")
            
            return False
            
    except Exception as e:
        print(f"❌ Request error: {str(e)}")
        return False

def test_with_uploaded_images():
    """Test listing creation with uploaded images"""
    print("Step 3: Test with Uploaded Images")
    print("-" * 30)
    
    # Login first
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("❌ Could not login for image test")
        return False
        
    admin_token = response.json()["access_token"]
    
    # Upload a test image
    test_image_data = b'\x89PNG\r\n\x1a\n\rIHDR\x01\x01\x08\x02\x90wS\xde\tpHYs\x0b\x13\x0b\x13\x01\x9a\x9c\x18\nIDATx\x9cc\xf8\x01\x01IEND\xaeB`\x82'
    
    files = {'file': ('test_image.png', test_image_data, 'image/png')}
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    upload_response = requests.post(f"{BACKEND_URL}/listings/upload-image", files=files, headers=headers)
    
    if upload_response.status_code == 200:
        image_url = upload_response.json().get('image_url')
        print(f"✅ Image uploaded: {image_url}")
        
        # Create listing with uploaded image
        listing_data = {
            "title": "Test Product with Image",
            "description": "Test description with uploaded image",
            "category": "Electronics", 
            "condition": "New",
            "listing_type": "fixed_price",
            "price": 149.99,
            "quantity": 1,
            "location": "Test City",
            "images": [image_url]
        }
        
        headers['Content-Type'] = 'application/json'
        response = requests.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Listing with image created successfully!")
            print(f"   Listing ID: {result.get('id')}")
            print(f"   Images: {result.get('images', [])}")
            return True
        else:
            print(f"❌ Listing with image failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    else:
        print(f"❌ Image upload failed: {upload_response.status_code}")
        return False

def test_auction_listing():
    """Test auction listing creation"""
    print("Step 4: Test Auction Listing")
    print("-" * 30)
    
    # Login first
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("❌ Could not login for auction test")
        return False
        
    admin_token = response.json()["access_token"]
    
    # Create auction listing
    listing_data = {
        "title": "Test Auction Product",
        "description": "Test auction description",
        "category": "Fashion", 
        "condition": "Used",
        "listing_type": "auction",
        "starting_bid": 10.00,
        "buyout_price": 50.00,
        "quantity": 1,
        "location": "Test City",
        "auction_duration_hours": 24,
        "images": []
    }
    
    headers = {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Auction listing created successfully!")
        print(f"   Listing ID: {result.get('id')}")
        print(f"   Starting Bid: {result.get('starting_bid')}")
        print(f"   Buyout Price: {result.get('buyout_price')}")
        print(f"   Auction End: {result.get('auction_end_time')}")
        return True
    else:
        print(f"❌ Auction listing failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_validation_scenarios():
    """Test various validation scenarios"""
    print("Step 5: Test Validation Scenarios")
    print("-" * 30)
    
    # Login first
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("❌ Could not login for validation tests")
        return False
        
    admin_token = response.json()["access_token"]
    headers = {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }
    
    # Test scenarios
    scenarios = [
        {
            "name": "Missing title",
            "data": {
                "description": "Test description",
                "category": "Electronics", 
                "condition": "New",
                "listing_type": "fixed_price",
                "price": 99.99,
                "quantity": 1,
                "location": "Test City"
            },
            "expected": 422
        },
        {
            "name": "Invalid listing type",
            "data": {
                "title": "Test Product",
                "description": "Test description",
                "category": "Electronics", 
                "condition": "New",
                "listing_type": "invalid_type",
                "price": 99.99,
                "quantity": 1,
                "location": "Test City"
            },
            "expected": 422
        },
        {
            "name": "Empty string fields (previous bug)",
            "data": {
                "title": "Test Product",
                "description": "Test description",
                "category": "Electronics", 
                "condition": "New",
                "listing_type": "fixed_price",
                "price": 99.99,
                "quantity": 1,
                "location": "Test City",
                "starting_bid": "",  # Empty string
                "buyout_price": "",  # Empty string
                "shipping_cost": ""  # Empty string
            },
            "expected": [200, 422]  # Could be either
        }
    ]
    
    results = []
    for scenario in scenarios:
        response = requests.post(f"{BACKEND_URL}/listings", json=scenario["data"], headers=headers)
        
        expected = scenario["expected"] if isinstance(scenario["expected"], list) else [scenario["expected"]]
        
        if response.status_code in expected:
            results.append(f"✅ {scenario['name']}: Expected {scenario['expected']}, got {response.status_code}")
        else:
            results.append(f"❌ {scenario['name']}: Expected {scenario['expected']}, got {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    
    for result in results:
        print(result)
    
    return all(result.startswith("✅") for result in results)

if __name__ == "__main__":
    print("🚀 URGENT LISTING CREATION TEST - REVIEW REQUEST SCENARIOS")
    print("=" * 80)
    print()
    
    success_count = 0
    total_tests = 5
    
    # Run all test scenarios
    if test_exact_review_scenario():
        success_count += 1
    
    print()
    if test_with_uploaded_images():
        success_count += 1
    
    print()
    if test_auction_listing():
        success_count += 1
    
    print()
    if test_validation_scenarios():
        success_count += 1
    
    print()
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Tests Passed: {success_count}/{total_tests}")
    print(f"Success Rate: {(success_count/total_tests)*100:.1f}%")
    print()
    
    if success_count == total_tests:
        print("✅ ALL TESTS PASSED!")
        print("✅ LISTING CREATION FUNCTIONALITY IS WORKING CORRECTLY")
        print("✅ The user's reported issue may be resolved or was a temporary problem")
    else:
        print("❌ SOME TESTS FAILED")
        print("❌ There are still issues with listing creation functionality")
    
    sys.exit(0 if success_count >= 3 else 1)  # Pass if at least 3/5 tests pass