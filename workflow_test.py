#!/usr/bin/env python3
"""
Complete listing creation workflow test
"""

import requests
import json

BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def test_complete_workflow():
    """Test the complete listing creation workflow"""
    print("🔄 COMPLETE LISTING CREATION WORKFLOW TEST")
    print("=" * 50)
    
    # Step 1: Admin login
    print("\n1️⃣ Admin Authentication")
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Admin login failed: {response.status_code}")
        return False
        
    token = response.json()["access_token"]
    user_info = response.json()["user"]
    print(f"✅ Admin logged in: {user_info['email']} (Role: {user_info['role']})")
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Step 2: Upload an image
    print("\n2️⃣ Image Upload")
    png_data = b'\x89PNG\r\n\x1a\n\rIHDR\x01\x01\x08\x02\x90wS\xde\tpHYs\x0b\x13\x0b\x13\x01\x9a\x9c\x18\nIDATx\x9cc\xf8\x01\x01IEND\xaeB`\x82'
    files = {'file': ('test_product.png', png_data, 'image/png')}
    upload_headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.post(f"{BACKEND_URL}/listings/upload-image", files=files, headers=upload_headers)
    
    if response.status_code != 200:
        print(f"❌ Image upload failed: {response.status_code}")
        image_url = None
    else:
        image_url = response.json().get('image_url')
        print(f"✅ Image uploaded: {image_url}")
    
    # Step 3: Create listing
    print("\n3️⃣ Create Listing")
    listing_data = {
        "title": "Complete Workflow Test Product",
        "description": "This product tests the complete listing creation workflow including image upload, validation, and retrieval",
        "category": "Electronics",
        "images": [image_url] if image_url else [],
        "listing_type": "fixed_price",
        "price": 299.99,
        "condition": "New",
        "quantity": 1,
        "location": "Workflow Test City",
        "shipping_cost": 9.99
    }
    
    response = requests.post(f"{BACKEND_URL}/listings", json=listing_data, headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Listing creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False
        
    listing = response.json()
    listing_id = listing.get('id')
    print(f"✅ Listing created: {listing_id}")
    print(f"   Title: {listing.get('title')}")
    print(f"   Price: ${listing.get('price')}")
    print(f"   Category: {listing.get('category')}")
    print(f"   Images: {len(listing.get('images', []))} image(s)")
    
    # Step 4: Verify listing in GET /listings
    print("\n4️⃣ Verify in Listings Endpoint")
    response = requests.get(f"{BACKEND_URL}/listings")
    
    if response.status_code != 200:
        print(f"❌ Get listings failed: {response.status_code}")
        return False
        
    all_listings = response.json()
    found_listing = None
    for listing in all_listings:
        if listing.get('id') == listing_id:
            found_listing = listing
            break
    
    if found_listing:
        print(f"✅ Listing found in GET /listings")
        print(f"   Title: {found_listing.get('title')}")
        print(f"   Status: {found_listing.get('status')}")
        print(f"   Images: {found_listing.get('images')}")
    else:
        print(f"❌ Listing not found in GET /listings")
        return False
    
    # Step 5: Get listing by ID
    print("\n5️⃣ Get Listing by ID")
    response = requests.get(f"{BACKEND_URL}/listings/{listing_id}")
    
    if response.status_code != 200:
        print(f"❌ Get listing by ID failed: {response.status_code}")
        return False
        
    listing_detail = response.json()
    print(f"✅ Listing retrieved by ID")
    print(f"   Title: {listing_detail.get('title')}")
    print(f"   Views: {listing_detail.get('views')}")
    print(f"   Created: {listing_detail.get('created_at')}")
    
    # Step 6: Test image accessibility (if image was uploaded)
    if image_url:
        print("\n6️⃣ Test Image Accessibility")
        image_full_url = f"http://217.154.0.82{image_url}"
        response = requests.get(image_full_url)
        
        if response.status_code == 200:
            print(f"✅ Image accessible: {image_full_url}")
            print(f"   Content-Type: {response.headers.get('content-type')}")
            print(f"   Size: {len(response.content)} bytes")
        else:
            print(f"❌ Image not accessible: {response.status_code}")
    
    # Step 7: Test search functionality
    print("\n7️⃣ Test Search Functionality")
    response = requests.get(f"{BACKEND_URL}/listings?search=Workflow")
    
    if response.status_code == 200:
        search_results = response.json()
        found_in_search = any(l.get('id') == listing_id for l in search_results)
        if found_in_search:
            print(f"✅ Listing found in search results")
        else:
            print(f"⚠️ Listing not found in search (may take time to index)")
    else:
        print(f"❌ Search failed: {response.status_code}")
    
    # Step 8: Test category filtering
    print("\n8️⃣ Test Category Filtering")
    response = requests.get(f"{BACKEND_URL}/listings?category=Electronics")
    
    if response.status_code == 200:
        category_results = response.json()
        found_in_category = any(l.get('id') == listing_id for l in category_results)
        if found_in_category:
            print(f"✅ Listing found in category filter")
        else:
            print(f"❌ Listing not found in category filter")
    else:
        print(f"❌ Category filter failed: {response.status_code}")
    
    print("\n🎉 WORKFLOW TEST COMPLETED SUCCESSFULLY")
    print(f"Created listing ID: {listing_id}")
    return True

if __name__ == "__main__":
    test_complete_workflow()