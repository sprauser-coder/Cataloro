import requests
import json
from datetime import datetime

class BiddingSystemTester:
    def __init__(self, base_url="https://marketplace-ready.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.buyer_token = None
        self.seller_token = None
        self.auction_listing_id = None
        
    def register_and_login_user(self, role, suffix):
        """Register and login a user"""
        timestamp = datetime.now().strftime('%H%M%S')
        user_data = {
            "email": f"test_{role}_{timestamp}_{suffix}@example.com",
            "username": f"test{role}_{timestamp}_{suffix}",
            "password": "TestPass123!",
            "full_name": f"Test {role.title()} {timestamp}",
            "role": role,
            "phone": "1234567890",
            "address": "123 Test Street"
        }
        
        # Register
        response = requests.post(f"{self.api_url}/auth/register", json=user_data)
        if response.status_code == 200:
            token = response.json()['access_token']
            user_id = response.json()['user']['id']
            print(f"✅ Registered {role}: {user_id}")
            return token, user_id
        else:
            print(f"❌ Failed to register {role}: {response.text}")
            return None, None
    
    def create_auction_listing(self, token):
        """Create an auction listing"""
        listing_data = {
            "title": "Vintage Watch - Auction",
            "description": "Beautiful vintage watch in excellent condition",
            "category": "Fashion",
            "images": ["https://example.com/watch.jpg"],
            "listing_type": "auction",
            "starting_bid": 25.00,
            "buyout_price": 100.00,
            "condition": "Used",
            "quantity": 1,
            "location": "New York",
            "shipping_cost": 5.99,
            "auction_duration_hours": 24
        }
        
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        response = requests.post(f"{self.api_url}/listings", json=listing_data, headers=headers)
        
        if response.status_code == 200:
            listing_id = response.json()['id']
            print(f"✅ Created auction listing: {listing_id}")
            return listing_id
        else:
            print(f"❌ Failed to create auction: {response.text}")
            return None
    
    def place_bid(self, token, listing_id, amount):
        """Place a bid on an auction"""
        bid_data = {
            "listing_id": listing_id,
            "amount": amount
        }
        
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        response = requests.post(f"{self.api_url}/bids", json=bid_data, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Placed bid of ${amount}")
            return True
        else:
            print(f"❌ Failed to place bid: {response.text}")
            return False
    
    def get_bid_history(self, listing_id):
        """Get bid history for a listing"""
        response = requests.get(f"{self.api_url}/listings/{listing_id}/bids")
        
        if response.status_code == 200:
            bids = response.json()
            print(f"✅ Retrieved {len(bids)} bids")
            for bid in bids:
                print(f"   Bid: ${bid['amount']} at {bid['timestamp']}")
            return bids
        else:
            print(f"❌ Failed to get bid history: {response.text}")
            return []

def main():
    print("🎯 Testing Bidding System")
    print("=" * 40)
    
    tester = BiddingSystemTester()
    
    # Register seller and buyer
    seller_token, seller_id = tester.register_and_login_user("seller", "1")
    buyer_token, buyer_id = tester.register_and_login_user("buyer", "2")
    
    if not seller_token or not buyer_token:
        print("❌ Failed to register users")
        return 1
    
    # Create auction listing
    auction_id = tester.create_auction_listing(seller_token)
    if not auction_id:
        print("❌ Failed to create auction")
        return 1
    
    # Place some bids
    print("\n🔨 Testing Bidding Process")
    success1 = tester.place_bid(buyer_token, auction_id, 30.00)  # First bid
    success2 = tester.place_bid(buyer_token, auction_id, 35.00)  # Higher bid
    
    # Try to place a lower bid (should fail)
    print("\n🚫 Testing Invalid Bid (Lower Amount)")
    success3 = tester.place_bid(buyer_token, auction_id, 25.00)  # Should fail
    
    # Get bid history
    print("\n📊 Getting Bid History")
    bids = tester.get_bid_history(auction_id)
    
    print("\n" + "=" * 40)
    if success1 and success2 and not success3:
        print("🎉 Bidding system working correctly!")
        return 0
    else:
        print("⚠️  Some bidding tests had issues")
        return 1

if __name__ == "__main__":
    main()