import requests
import json
from datetime import datetime

class MarketplaceEdgeCaseTester:
    def __init__(self, base_url="https://localmart-app.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.buyer_token = None
        self.seller_token = None
        
    def setup_users(self):
        """Setup buyer and seller users"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        # Register seller
        seller_data = {
            "email": f"seller_edge_{timestamp}@example.com",
            "username": f"seller_edge_{timestamp}",
            "password": "TestPass123!",
            "full_name": f"Seller Edge {timestamp}",
            "role": "seller"
        }
        
        response = requests.post(f"{self.api_url}/auth/register", json=seller_data)
        if response.status_code == 200:
            self.seller_token = response.json()['access_token']
            print("✅ Seller registered")
        
        # Register buyer
        buyer_data = {
            "email": f"buyer_edge_{timestamp}@example.com",
            "username": f"buyer_edge_{timestamp}",
            "password": "TestPass123!",
            "full_name": f"Buyer Edge {timestamp}",
            "role": "buyer"
        }
        
        response = requests.post(f"{self.api_url}/auth/register", json=buyer_data)
        if response.status_code == 200:
            self.buyer_token = response.json()['access_token']
            print("✅ Buyer registered")
    
    def test_buyer_cannot_create_listing(self):
        """Test that buyer role cannot create listings"""
        print("🔍 Testing buyer cannot create listing...")
        
        listing_data = {
            "title": "Unauthorized Listing",
            "description": "This should fail",
            "category": "Electronics",
            "listing_type": "fixed_price",
            "price": 99.99,
            "condition": "New",
            "quantity": 1,
            "location": "Test City"
        }
        
        headers = {'Authorization': f'Bearer {self.buyer_token}', 'Content-Type': 'application/json'}
        response = requests.post(f"{self.api_url}/listings", json=listing_data, headers=headers)
        
        if response.status_code == 403:
            print("✅ Buyer properly prevented from creating listings")
            return True
        else:
            print(f"❌ Buyer restriction test failed: {response.status_code}")
            return False
    
    def test_seller_cannot_bid(self):
        """Test that seller role cannot place bids"""
        print("🔍 Testing seller cannot place bids...")
        
        bid_data = {
            "listing_id": "dummy_id",
            "amount": 50.00
        }
        
        headers = {'Authorization': f'Bearer {self.seller_token}', 'Content-Type': 'application/json'}
        response = requests.post(f"{self.api_url}/bids", json=bid_data, headers=headers)
        
        if response.status_code == 403:
            print("✅ Seller properly prevented from placing bids")
            return True
        else:
            print(f"❌ Seller bidding restriction test failed: {response.status_code}")
            return False
    
    def test_nonexistent_listing(self):
        """Test accessing non-existent listing"""
        print("🔍 Testing non-existent listing access...")
        
        response = requests.get(f"{self.api_url}/listings/nonexistent-id")
        
        if response.status_code == 404:
            print("✅ Non-existent listing properly handled")
            return True
        else:
            print(f"❌ Non-existent listing test failed: {response.status_code}")
            return False
    
    def test_add_auction_to_cart(self):
        """Test adding auction item to cart (should fail)"""
        print("🔍 Testing adding auction item to cart...")
        
        # First create an auction listing
        listing_data = {
            "title": "Auction Item",
            "description": "This is an auction item",
            "category": "Electronics",
            "listing_type": "auction",
            "starting_bid": 10.00,
            "condition": "New",
            "quantity": 1,
            "location": "Test City",
            "auction_duration_hours": 24
        }
        
        headers = {'Authorization': f'Bearer {self.seller_token}', 'Content-Type': 'application/json'}
        response = requests.post(f"{self.api_url}/listings", json=listing_data, headers=headers)
        
        if response.status_code == 200:
            auction_id = response.json()['id']
            
            # Try to add auction to cart
            cart_data = {
                "listing_id": auction_id,
                "quantity": 1
            }
            
            headers = {'Authorization': f'Bearer {self.buyer_token}', 'Content-Type': 'application/json'}
            response = requests.post(f"{self.api_url}/cart", json=cart_data, headers=headers)
            
            if response.status_code == 400:
                print("✅ Auction items properly prevented from being added to cart")
                return True
            else:
                print(f"❌ Auction cart restriction test failed: {response.status_code}")
                return False
        else:
            print("❌ Failed to create auction for cart test")
            return False
    
    def test_remove_nonexistent_cart_item(self):
        """Test removing non-existent cart item"""
        print("🔍 Testing removing non-existent cart item...")
        
        headers = {'Authorization': f'Bearer {self.buyer_token}'}
        response = requests.delete(f"{self.api_url}/cart/nonexistent-id", headers=headers)
        
        if response.status_code == 404:
            print("✅ Non-existent cart item removal properly handled")
            return True
        else:
            print(f"❌ Non-existent cart item test failed: {response.status_code}")
            return False

def main():
    print("🧪 Testing Marketplace Edge Cases")
    print("=" * 40)
    
    tester = MarketplaceEdgeCaseTester()
    tester.setup_users()
    
    if not tester.buyer_token or not tester.seller_token:
        print("❌ Failed to setup test users")
        return 1
    
    tests = [
        tester.test_buyer_cannot_create_listing,
        tester.test_seller_cannot_bid,
        tester.test_nonexistent_listing,
        tester.test_add_auction_to_cart,
        tester.test_remove_nonexistent_cart_item
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Edge Case Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All marketplace edge cases handled correctly!")
        return 0
    else:
        print("⚠️  Some marketplace edge case tests failed")
        return 1

if __name__ == "__main__":
    main()