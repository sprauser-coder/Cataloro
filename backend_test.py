#!/usr/bin/env python3
"""
SOLD ITEMS FUNCTIONALITY COMPREHENSIVE TESTING
Testing the enhanced sold items functionality that includes accepted tenders
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "https://market-upgrade-2.preview.emergentagent.com/api"

def test_sold_items_functionality():
    """Test the sold items endpoint with accepted tenders functionality"""
    print("🎯 SOLD ITEMS ENHANCEMENT COMPREHENSIVE TESTING")
    print("=" * 60)
    
    results = {
        "tests_passed": 0,
        "tests_failed": 0,
        "critical_issues": [],
        "test_details": []
    }
    
    try:
        # Test 1: Login and get user ID
        print("\n1. 🔐 USER AUTHENTICATION")
        login_response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "email": "admin@cataloro.com",
            "password": "admin123"
        })
        
        if login_response.status_code == 200:
            user_data = login_response.json()
            user_id = user_data["user"]["id"]
            print(f"   ✅ Login successful - User ID: {user_id}")
            results["tests_passed"] += 1
            results["test_details"].append("✅ User authentication successful")
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            results["tests_failed"] += 1
            results["critical_issues"].append("User authentication failed")
            return results
        
        # Test 2: Test sold items endpoint basic functionality
        print("\n2. 📊 SOLD ITEMS ENDPOINT BASIC TEST")
        sold_items_response = requests.get(f"{BACKEND_URL}/user/{user_id}/sold-items")
        
        if sold_items_response.status_code == 200:
            sold_data = sold_items_response.json()
            print(f"   ✅ Sold items endpoint accessible")
            print(f"   📈 Response structure: {list(sold_data.keys())}")
            
            # Verify response structure
            if "items" in sold_data and "stats" in sold_data:
                print(f"   ✅ Proper response structure with items and stats")
                print(f"   📊 Current sold items count: {len(sold_data['items'])}")
                print(f"   💰 Stats: {sold_data['stats']}")
                results["tests_passed"] += 1
                results["test_details"].append("✅ Sold items endpoint structure correct")
            else:
                print(f"   ❌ Invalid response structure")
                results["tests_failed"] += 1
                results["critical_issues"].append("Sold items endpoint structure invalid")
        else:
            print(f"   ❌ Sold items endpoint failed: {sold_items_response.status_code}")
            results["tests_failed"] += 1
            results["critical_issues"].append("Sold items endpoint not accessible")
        
        # Test 3: Create test listing for tender testing
        print("\n3. 🏷️ CREATE TEST LISTING FOR TENDER TESTING")
        test_listing_data = {
            "title": "Sold Items Test - Premium Headphones",
            "description": "High-quality headphones for testing sold items functionality with accepted tenders",
            "price": 150.0,
            "category": "Electronics",
            "condition": "New",
            "seller_id": user_id,
            "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"],
            "tags": ["headphones", "audio", "premium"],
            "features": ["Noise cancelling", "Wireless", "Premium sound"]
        }
        
        create_response = requests.post(f"{BACKEND_URL}/listings", json=test_listing_data)
        
        if create_response.status_code == 200:
            listing_data = create_response.json()
            test_listing_id = listing_data["listing_id"]
            print(f"   ✅ Test listing created - ID: {test_listing_id}")
            results["tests_passed"] += 1
            results["test_details"].append("✅ Test listing creation successful")
        else:
            print(f"   ❌ Test listing creation failed: {create_response.status_code}")
            results["tests_failed"] += 1
            results["critical_issues"].append("Test listing creation failed")
            return results
        
        # Test 4: Create test buyer and submit tender
        print("\n4. 👤 CREATE TEST BUYER AND SUBMIT TENDER")
        
        # Register test buyer
        buyer_data = {
            "username": "test_buyer_sold_items",
            "email": "buyer_sold_items@test.com",
            "full_name": "Test Buyer for Sold Items",
            "is_business": False
        }
        
        buyer_register_response = requests.post(f"{BACKEND_URL}/auth/register", json=buyer_data)
        
        if buyer_register_response.status_code == 200:
            buyer_response_data = buyer_register_response.json()
            buyer_id = buyer_response_data["user_id"]
            print(f"   ✅ Test buyer created - ID: {buyer_id}")
            results["tests_passed"] += 1
            results["test_details"].append("✅ Test buyer creation successful")
        else:
            print(f"   ❌ Test buyer creation failed: {buyer_register_response.status_code}")
            results["tests_failed"] += 1
            results["critical_issues"].append("Test buyer creation failed")
            return results
        
        # Submit tender offer
        tender_data = {
            "listing_id": test_listing_id,
            "buyer_id": buyer_id,
            "offer_amount": 175.0  # Higher than starting price
        }
        
        tender_response = requests.post(f"{BACKEND_URL}/tenders/submit", json=tender_data)
        
        if tender_response.status_code == 200:
            tender_result = tender_response.json()
            tender_id = tender_result["tender_id"]
            print(f"   ✅ Tender submitted - ID: {tender_id}")
            print(f"   💰 Tender amount: €{tender_data['offer_amount']}")
            results["tests_passed"] += 1
            results["test_details"].append("✅ Tender submission successful")
        else:
            print(f"   ❌ Tender submission failed: {tender_response.status_code}")
            results["tests_failed"] += 1
            results["critical_issues"].append("Tender submission failed")
            return results
        
        # Test 5: Accept the tender
        print("\n5. ✅ ACCEPT TENDER AND TEST SOLD ITEMS UPDATE")
        
        accept_response = requests.put(f"{BACKEND_URL}/tenders/{tender_id}/accept")
        
        if accept_response.status_code == 200:
            print(f"   ✅ Tender accepted successfully")
            results["tests_passed"] += 1
            results["test_details"].append("✅ Tender acceptance successful")
            
            # Wait a moment for database updates
            time.sleep(2)
            
            # Test sold items endpoint after tender acceptance
            print("\n6. 🔍 VERIFY ACCEPTED TENDER IN SOLD ITEMS")
            updated_sold_response = requests.get(f"{BACKEND_URL}/user/{user_id}/sold-items")
            
            if updated_sold_response.status_code == 200:
                updated_sold_data = updated_sold_response.json()
                print(f"   ✅ Updated sold items retrieved")
                print(f"   📊 New sold items count: {len(updated_sold_data['items'])}")
                
                # Check if our accepted tender appears in sold items
                found_tender_item = False
                for item in updated_sold_data["items"]:
                    if item.get("source") == "tender" and item.get("tender_id") == tender_id:
                        found_tender_item = True
                        print(f"   ✅ Accepted tender found in sold items!")
                        print(f"   📋 Item details:")
                        print(f"      - Listing: {item.get('listing', {}).get('title', 'N/A')}")
                        print(f"      - Final price: €{item.get('final_price', 0)}")
                        print(f"      - Buyer: {item.get('buyer', {}).get('full_name', 'N/A')}")
                        print(f"      - Sold date: {item.get('sold_at', 'N/A')}")
                        print(f"      - Source: {item.get('source', 'N/A')}")
                        
                        # Verify data integrity
                        if (item.get('final_price') == 175.0 and 
                            item.get('source') == 'tender' and
                            item.get('listing', {}).get('title') == 'Sold Items Test - Premium Headphones'):
                            print(f"   ✅ Data integrity verified - all fields correct")
                            results["tests_passed"] += 1
                            results["test_details"].append("✅ Accepted tender data integrity verified")
                        else:
                            print(f"   ⚠️ Data integrity issues detected")
                            results["tests_failed"] += 1
                            results["critical_issues"].append("Accepted tender data integrity issues")
                        break
                
                if found_tender_item:
                    results["tests_passed"] += 1
                    results["test_details"].append("✅ Accepted tender appears in sold items")
                else:
                    print(f"   ❌ Accepted tender NOT found in sold items")
                    results["tests_failed"] += 1
                    results["critical_issues"].append("Accepted tender missing from sold items")
                
                # Test statistics update
                stats = updated_sold_data.get("stats", {})
                print(f"\n   📊 SOLD ITEMS STATISTICS:")
                print(f"      - Total sold: {stats.get('totalSold', 0)}")
                print(f"      - Total revenue: €{stats.get('totalRevenue', 0)}")
                print(f"      - Average price: €{stats.get('averagePrice', 0)}")
                print(f"      - This month: {stats.get('thisMonth', 0)}")
                
                if stats.get('totalSold', 0) > 0:
                    print(f"   ✅ Statistics properly calculated")
                    results["tests_passed"] += 1
                    results["test_details"].append("✅ Sold items statistics calculated correctly")
                else:
                    print(f"   ⚠️ Statistics calculation issues")
                    results["tests_failed"] += 1
                    results["critical_issues"].append("Sold items statistics calculation issues")
                    
            else:
                print(f"   ❌ Failed to retrieve updated sold items: {updated_sold_response.status_code}")
                results["tests_failed"] += 1
                results["critical_issues"].append("Failed to retrieve updated sold items")
        else:
            print(f"   ❌ Tender acceptance failed: {accept_response.status_code}")
            results["tests_failed"] += 1
            results["critical_issues"].append("Tender acceptance failed")
        
        # Test 6: Verify listing status changed to sold
        print("\n7. 🏷️ VERIFY LISTING STATUS CHANGED TO SOLD")
        
        listing_check_response = requests.get(f"{BACKEND_URL}/listings/{test_listing_id}")
        
        if listing_check_response.status_code == 200:
            listing_data = listing_check_response.json()
            listing_status = listing_data.get("status", "unknown")
            print(f"   📋 Listing status: {listing_status}")
            
            if listing_status == "sold":
                print(f"   ✅ Listing correctly marked as sold")
                results["tests_passed"] += 1
                results["test_details"].append("✅ Listing status updated to sold")
            else:
                print(f"   ❌ Listing status not updated to sold")
                results["tests_failed"] += 1
                results["critical_issues"].append("Listing status not updated after tender acceptance")
        else:
            print(f"   ❌ Failed to check listing status: {listing_check_response.status_code}")
            results["tests_failed"] += 1
            results["critical_issues"].append("Failed to verify listing status")
        
        # Test 7: Test with existing deals (if any)
        print("\n8. 🔍 TEST SOLD ITEMS WITH MIXED SOURCES")
        
        final_sold_response = requests.get(f"{BACKEND_URL}/user/{user_id}/sold-items")
        
        if final_sold_response.status_code == 200:
            final_sold_data = final_sold_response.json()
            items = final_sold_data.get("items", [])
            
            # Count sources
            tender_sources = len([item for item in items if item.get("source") == "tender"])
            deal_sources = len([item for item in items if item.get("source") == "deal"])
            
            print(f"   📊 SOLD ITEMS SOURCE BREAKDOWN:")
            print(f"      - From accepted tenders: {tender_sources}")
            print(f"      - From completed deals: {deal_sources}")
            print(f"      - Total sold items: {len(items)}")
            
            if tender_sources > 0:
                print(f"   ✅ Accepted tenders properly included in sold items")
                results["tests_passed"] += 1
                results["test_details"].append("✅ Mixed source sold items working correctly")
            else:
                print(f"   ❌ No accepted tenders found in sold items")
                results["tests_failed"] += 1
                results["critical_issues"].append("Accepted tenders not included in sold items")
            
            # Verify sorting (most recent first)
            if len(items) > 1:
                dates = [item.get("sold_at", "") for item in items if item.get("sold_at")]
                if dates == sorted(dates, reverse=True):
                    print(f"   ✅ Sold items properly sorted by date (newest first)")
                    results["tests_passed"] += 1
                    results["test_details"].append("✅ Sold items sorting verified")
                else:
                    print(f"   ⚠️ Sold items sorting may have issues")
                    results["tests_failed"] += 1
                    results["critical_issues"].append("Sold items sorting issues")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        results["tests_failed"] += 1
        results["critical_issues"].append(f"Critical testing error: {str(e)}")
    
    return results

def main():
    """Main testing function"""
    print("🚀 STARTING SOLD ITEMS FUNCTIONALITY TESTING")
    print("Testing enhanced sold items that includes accepted tenders")
    print("=" * 80)
    
    start_time = time.time()
    results = test_sold_items_functionality()
    end_time = time.time()
    
    # Print comprehensive results
    print("\n" + "=" * 80)
    print("📋 COMPREHENSIVE TEST RESULTS")
    print("=" * 80)
    
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Tests Passed: {results['tests_passed']}")
    print(f"   ❌ Tests Failed: {results['tests_failed']}")
    print(f"   ⏱️ Total Time: {end_time - start_time:.2f} seconds")
    
    success_rate = (results['tests_passed'] / (results['tests_passed'] + results['tests_failed']) * 100) if (results['tests_passed'] + results['tests_failed']) > 0 else 0
    print(f"   📈 Success Rate: {success_rate:.1f}%")
    
    print(f"\n✅ SUCCESSFUL TESTS:")
    for detail in results['test_details']:
        print(f"   {detail}")
    
    if results['critical_issues']:
        print(f"\n❌ CRITICAL ISSUES FOUND:")
        for issue in results['critical_issues']:
            print(f"   ❌ {issue}")
    
    # Overall status
    if results['tests_failed'] == 0:
        print(f"\n🎉 SOLD ITEMS FUNCTIONALITY STATUS: ✅ FULLY OPERATIONAL")
        print("   All tests passed - accepted tenders properly integrated into sold items")
    elif results['tests_failed'] <= 2:
        print(f"\n⚠️ SOLD ITEMS FUNCTIONALITY STATUS: ⚠️ MOSTLY WORKING")
        print("   Minor issues detected but core functionality operational")
    else:
        print(f"\n❌ SOLD ITEMS FUNCTIONALITY STATUS: ❌ CRITICAL ISSUES")
        print("   Major problems detected - requires immediate attention")
    
    return results

if __name__ == "__main__":
    main()