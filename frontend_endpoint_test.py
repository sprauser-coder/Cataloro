#!/usr/bin/env python3
"""
Test the exact endpoints that the frontend is calling for delete operations
"""

import requests
import json

def test_frontend_delete_endpoints():
    """Test the endpoints that frontend is configured to call"""
    
    base_url = "https://bizcat-market.preview.emergentagent.com"
    
    # From the frontend config, API_ENDPOINTS.MARKETPLACE.LISTINGS resolves to:
    # `${CURRENT_ENV.BACKEND_URL}/api/listings`
    # Which should be: https://bizcat-market.preview.emergentagent.com/api/listings
    
    print("🔍 Testing Frontend Delete Endpoint Configuration")
    print("=" * 60)
    
    # First, let's create a test listing to delete
    print("\n1️⃣ Creating test listing...")
    
    # Login as admin first
    login_response = requests.post(f"{base_url}/api/auth/login", 
                                 json={"email": "admin@cataloro.com", "password": "demo123"})
    
    if login_response.status_code != 200:
        print("❌ Failed to login")
        return False
    
    admin_user = login_response.json()['user']
    print(f"✅ Logged in as: {admin_user['full_name']}")
    
    # Create test listing
    test_listing = {
        "title": "Frontend Endpoint Test - Smartwatch",
        "description": "Test listing for frontend endpoint verification",
        "price": 299.99,
        "category": "Electronics",
        "condition": "New",
        "seller_id": admin_user['id'],
        "images": ["https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400"]
    }
    
    create_response = requests.post(f"{base_url}/api/listings", json=test_listing)
    
    if create_response.status_code != 200:
        print(f"❌ Failed to create test listing: {create_response.status_code}")
        return False
    
    listing_id = create_response.json()['listing_id']
    print(f"✅ Created test listing: {listing_id}")
    
    # Test the exact endpoint that frontend calls
    print(f"\n2️⃣ Testing frontend delete endpoint...")
    frontend_delete_url = f"{base_url}/api/listings/{listing_id}"
    print(f"   Frontend calls: {frontend_delete_url}")
    
    delete_response = requests.delete(frontend_delete_url)
    
    print(f"   Status Code: {delete_response.status_code}")
    print(f"   Response Headers: {dict(delete_response.headers)}")
    
    if delete_response.text:
        try:
            response_json = delete_response.json()
            print(f"   Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"   Response Text: {delete_response.text}")
    
    # Check if delete was successful
    if delete_response.status_code == 200:
        print("✅ Frontend delete endpoint works correctly")
        
        # Verify deletion by checking browse
        browse_response = requests.get(f"{base_url}/api/marketplace/browse")
        if browse_response.status_code == 200:
            listings = browse_response.json()
            still_exists = any(listing.get('id') == listing_id for listing in listings)
            
            if not still_exists:
                print("✅ Listing successfully removed from browse")
                return True
            else:
                print("❌ Listing still exists in browse after delete")
                return False
        else:
            print("⚠️ Could not verify deletion via browse endpoint")
            return True  # Delete endpoint worked, assume success
    else:
        print(f"❌ Frontend delete endpoint failed: {delete_response.status_code}")
        print(f"   Error: {delete_response.text}")
        return False

def test_bulk_delete_simulation():
    """Simulate exactly what the frontend bulk delete would do"""
    
    base_url = "https://bizcat-market.preview.emergentagent.com"
    
    print("\n3️⃣ Simulating Frontend Bulk Delete Process...")
    print("=" * 60)
    
    # Login as admin
    login_response = requests.post(f"{base_url}/api/auth/login", 
                                 json={"email": "admin@cataloro.com", "password": "demo123"})
    
    if login_response.status_code != 200:
        print("❌ Failed to login for bulk test")
        return False
    
    admin_user = login_response.json()['user']
    
    # Create multiple test listings
    print("   Creating 3 test listings for bulk delete...")
    listing_ids = []
    
    for i in range(3):
        test_listing = {
            "title": f"Bulk Delete Frontend Test #{i+1} - Headphones",
            "description": f"Test listing #{i+1} for frontend bulk delete simulation",
            "price": 150.00 + (i * 50),
            "category": "Electronics",
            "condition": "Used - Good",
            "seller_id": admin_user['id'],
            "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"]
        }
        
        create_response = requests.post(f"{base_url}/api/listings", json=test_listing)
        if create_response.status_code == 200:
            listing_id = create_response.json()['listing_id']
            listing_ids.append(listing_id)
            print(f"   ✅ Created listing {i+1}: {listing_id[:8]}...")
        else:
            print(f"   ❌ Failed to create listing {i+1}")
    
    if not listing_ids:
        print("❌ No listings created for bulk delete test")
        return False
    
    print(f"\n   Simulating bulk delete of {len(listing_ids)} listings...")
    
    # Simulate frontend bulk delete: multiple DELETE requests
    successful_deletes = 0
    failed_deletes = 0
    
    for i, listing_id in enumerate(listing_ids):
        print(f"   Deleting {i+1}/{len(listing_ids)}: {listing_id[:8]}...")
        
        # This is exactly what the frontend does
        delete_url = f"{base_url}/api/listings/{listing_id}"
        delete_response = requests.delete(delete_url)
        
        if delete_response.status_code == 200:
            successful_deletes += 1
            print(f"     ✅ Success")
        else:
            failed_deletes += 1
            print(f"     ❌ Failed: {delete_response.status_code}")
    
    print(f"\n   📊 Bulk Delete Results:")
    print(f"     Successful: {successful_deletes}")
    print(f"     Failed: {failed_deletes}")
    
    # Verify all listings are gone
    browse_response = requests.get(f"{base_url}/api/marketplace/browse")
    if browse_response.status_code == 200:
        listings = browse_response.json()
        remaining_count = 0
        
        for listing_id in listing_ids:
            still_exists = any(listing.get('id') == listing_id for listing in listings)
            if still_exists:
                remaining_count += 1
                print(f"     ⚠️ Listing {listing_id[:8]}... still exists")
        
        if remaining_count == 0:
            print(f"   ✅ All {len(listing_ids)} listings successfully removed from browse")
            return True
        else:
            print(f"   ❌ {remaining_count} listings still exist after bulk delete")
            return False
    else:
        print("   ⚠️ Could not verify bulk delete results")
        return successful_deletes == len(listing_ids)

if __name__ == "__main__":
    print("🚀 Frontend Delete Endpoint Testing")
    print("Testing the exact endpoints and process that frontend uses")
    
    # Test individual delete
    individual_success = test_frontend_delete_endpoints()
    
    # Test bulk delete simulation
    bulk_success = test_bulk_delete_simulation()
    
    print("\n" + "=" * 60)
    print("📊 FRONTEND ENDPOINT TEST RESULTS")
    print("=" * 60)
    print(f"Individual Delete: {'✅ PASSED' if individual_success else '❌ FAILED'}")
    print(f"Bulk Delete Simulation: {'✅ PASSED' if bulk_success else '❌ FAILED'}")
    
    if individual_success and bulk_success:
        print("\n🎉 CONCLUSION: Frontend delete endpoints work correctly!")
        print("💡 The issue is likely in the frontend UI/notification logic, not the API calls")
    elif individual_success and not bulk_success:
        print("\n⚠️ CONCLUSION: Individual delete works but bulk delete has issues")
        print("💡 Check frontend bulk delete implementation")
    else:
        print("\n❌ CONCLUSION: Delete endpoints have issues")
        print("💡 Check API endpoint configuration")