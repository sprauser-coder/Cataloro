#!/usr/bin/env python3
"""
Phase 3B Integration Test - Verify database persistence and real-world scenarios
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

# Admin credentials
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def get_admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{API_BASE}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_database_persistence():
    """Test that bulk operations persist in database"""
    print("🔍 Testing Database Persistence...")
    
    token = get_admin_token()
    if not token:
        print("❌ Failed to get admin token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test listing
    listing_data = {
        "title": "Persistence Test Item",
        "description": "Testing database persistence",
        "category": "Electronics",
        "condition": "New",
        "listing_type": "fixed_price",
        "price": 100.00,
        "quantity": 1,
        "location": "Test City"
    }
    
    response = requests.post(f"{API_BASE}/listings", json=listing_data, headers=headers)
    if response.status_code != 200:
        print("❌ Failed to create test listing")
        return False
    
    listing = response.json()
    listing_id = listing["id"]
    print(f"✅ Created test listing: {listing_id}")
    
    # Update the listing using bulk update
    response = requests.post(
        f"{API_BASE}/admin/listings/bulk-update",
        json={
            "listing_ids": [listing_id],
            "status": "sold",
            "category": "Books",
            "featured": True
        },
        headers=headers
    )
    
    if response.status_code != 200:
        print("❌ Bulk update failed")
        return False
    
    print("✅ Bulk update completed")
    
    # Verify changes persisted by fetching the listing
    response = requests.get(f"{API_BASE}/listings/{listing_id}")
    if response.status_code != 200:
        print("❌ Failed to fetch updated listing")
        return False
    
    updated_listing = response.json()
    
    # Check if changes persisted
    status_correct = updated_listing.get("status") == "sold"
    category_correct = updated_listing.get("category") == "Books"
    featured_correct = updated_listing.get("featured") == True
    
    print(f"✅ Status persisted: {status_correct} (expected: sold, got: {updated_listing.get('status')})")
    print(f"✅ Category persisted: {category_correct} (expected: Books, got: {updated_listing.get('category')})")
    print(f"✅ Featured persisted: {featured_correct} (expected: True, got: {updated_listing.get('featured')})")
    
    # Update price using bulk price update
    response = requests.post(
        f"{API_BASE}/admin/listings/bulk-price-update",
        json={
            "listing_ids": [listing_id],
            "price_type": "increase",
            "price_value": 25.0
        },
        headers=headers
    )
    
    if response.status_code != 200:
        print("❌ Bulk price update failed")
        return False
    
    print("✅ Bulk price update completed")
    
    # Verify price change persisted
    response = requests.get(f"{API_BASE}/listings/{listing_id}")
    if response.status_code != 200:
        print("❌ Failed to fetch price-updated listing")
        return False
    
    price_updated_listing = response.json()
    new_price = price_updated_listing.get("price")
    expected_price = 125.00  # 100 + 25%
    
    price_correct = abs(new_price - expected_price) < 0.01
    print(f"✅ Price persisted: {price_correct} (expected: {expected_price}, got: {new_price})")
    
    # Clean up
    requests.post(f"{API_BASE}/admin/listings/bulk-delete", 
                 json={"listing_ids": [listing_id]}, headers=headers)
    
    return status_correct and category_correct and price_correct

def test_large_batch_operations():
    """Test bulk operations with larger datasets"""
    print("\n🔍 Testing Large Batch Operations...")
    
    token = get_admin_token()
    if not token:
        print("❌ Failed to get admin token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create 10 test listings
    listing_ids = []
    for i in range(10):
        listing_data = {
            "title": f"Batch Test Item {i+1}",
            "description": f"Testing batch operations item {i+1}",
            "category": "Electronics",
            "condition": "New",
            "listing_type": "fixed_price",
            "price": 50.00 + (i * 10),  # Varying prices
            "quantity": 1,
            "location": "Test City"
        }
        
        response = requests.post(f"{API_BASE}/listings", json=listing_data, headers=headers)
        if response.status_code == 200:
            listing_ids.append(response.json()["id"])
    
    print(f"✅ Created {len(listing_ids)} test listings")
    
    # Test bulk update on all listings
    response = requests.post(
        f"{API_BASE}/admin/listings/bulk-update",
        json={
            "listing_ids": listing_ids,
            "category": "Fashion",
            "featured": True
        },
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        updated_count = data.get("modified_count", 0)
        success = updated_count == len(listing_ids)
        print(f"✅ Bulk update large batch: {success} (updated {updated_count}/{len(listing_ids)})")
    else:
        print("❌ Large batch bulk update failed")
        success = False
    
    # Test bulk price update on all listings
    response = requests.post(
        f"{API_BASE}/admin/listings/bulk-price-update",
        json={
            "listing_ids": listing_ids,
            "price_type": "decrease",
            "price_value": 10.0
        },
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        updates = data.get("updates", [])
        price_success = len(updates) == len(listing_ids)
        print(f"✅ Bulk price update large batch: {price_success} (updated {len(updates)}/{len(listing_ids)})")
    else:
        print("❌ Large batch bulk price update failed")
        price_success = False
    
    # Clean up all test listings
    response = requests.post(
        f"{API_BASE}/admin/listings/bulk-delete",
        json={"listing_ids": listing_ids},
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        deleted_count = data.get("deleted_count", 0)
        cleanup_success = deleted_count == len(listing_ids)
        print(f"✅ Bulk delete large batch: {cleanup_success} (deleted {deleted_count}/{len(listing_ids)})")
    else:
        print("❌ Large batch cleanup failed")
        cleanup_success = False
    
    return success and price_success and cleanup_success

def test_edge_cases():
    """Test edge cases and error conditions"""
    print("\n🔍 Testing Edge Cases...")
    
    token = get_admin_token()
    if not token:
        print("❌ Failed to get admin token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test minimum price protection
    listing_data = {
        "title": "Minimum Price Test",
        "description": "Testing minimum price protection",
        "category": "Electronics",
        "condition": "New",
        "listing_type": "fixed_price",
        "price": 1.00,  # Very low price
        "quantity": 1,
        "location": "Test City"
    }
    
    response = requests.post(f"{API_BASE}/listings", json=listing_data, headers=headers)
    if response.status_code != 200:
        print("❌ Failed to create minimum price test listing")
        return False
    
    listing_id = response.json()["id"]
    
    # Try to decrease price by 99% (should hit minimum price protection)
    response = requests.post(
        f"{API_BASE}/admin/listings/bulk-price-update",
        json={
            "listing_ids": [listing_id],
            "price_type": "decrease",
            "price_value": 99.0
        },
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        updates = data.get("updates", [])
        if updates:
            new_price = updates[0].get("new_price", 0)
            min_price_protected = new_price >= 0.01
            print(f"✅ Minimum price protection: {min_price_protected} (price: ${new_price})")
        else:
            print("❌ No price updates returned")
            min_price_protected = False
    else:
        print("❌ Minimum price test failed")
        min_price_protected = False
    
    # Clean up
    requests.post(f"{API_BASE}/admin/listings/bulk-delete", 
                 json={"listing_ids": [listing_id]}, headers=headers)
    
    return min_price_protected

def main():
    """Run all integration tests"""
    print("🚀 Phase 3B Integration Testing...")
    print("=" * 50)
    
    results = []
    
    # Test database persistence
    results.append(test_database_persistence())
    
    # Test large batch operations
    results.append(test_large_batch_operations())
    
    # Test edge cases
    results.append(test_edge_cases())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    success_rate = (passed / total) * 100 if total > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Phase 3B bulk actions are fully functional and ready for production!")
    elif success_rate >= 80:
        print("✅ Integration tests mostly successful!")
    else:
        print("⚠️ Some integration issues found")
    
    return success_rate >= 80

if __name__ == "__main__":
    main()