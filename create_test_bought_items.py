#!/usr/bin/env python3
"""
Create Test Bought Items Data
Create test tenders and accept them to generate bought items for testing
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
BASE_URL = "https://cataloro-marketplace-4.preview.emergentagent.com/api"

class TestDataCreator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.demo_user_id = None
        self.seller_user_id = None
        
    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def get_demo_user_id(self):
        """Get demo user ID"""
        try:
            login_data = {
                "email": "demo@cataloro.com",
                "username": "demo_user"
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                user_data = response.json()
                self.demo_user_id = user_data.get('user', {}).get('id')
                self.log(f"✅ Demo user ID: {self.demo_user_id}")
                return self.demo_user_id
            else:
                self.log(f"❌ Failed to get demo user: {response.status_code}")
                return None
        except Exception as e:
            self.log(f"❌ Error getting demo user: {e}")
            return None

    def get_seller_user_id(self):
        """Get a seller user ID (different from demo user)"""
        try:
            # Get all users and find a seller
            response = self.session.get(f"{BASE_URL}/admin/users")
            if response.status_code == 200:
                users = response.json()
                for user in users:
                    if user.get('id') != self.demo_user_id and user.get('email') != 'demo@cataloro.com':
                        self.seller_user_id = user.get('id')
                        self.log(f"✅ Found seller user: {user.get('username')} ({self.seller_user_id})")
                        return self.seller_user_id
                
                # If no other user found, create one
                self.log("🔧 Creating test seller user...")
                seller_data = {
                    "username": f"test_seller_{str(uuid.uuid4())[:8]}",
                    "email": f"seller_{str(uuid.uuid4())[:8]}@test.com",
                    "password": "test123",
                    "user_role": "User-Seller",
                    "registration_status": "Approved",
                    "full_name": "Test Seller"
                }
                
                create_response = self.session.post(f"{BASE_URL}/admin/users", json=seller_data)
                if create_response.status_code == 200:
                    created_user = create_response.json().get('user', {})
                    self.seller_user_id = created_user.get('id')
                    self.log(f"✅ Created seller user: {self.seller_user_id}")
                    return self.seller_user_id
                else:
                    self.log(f"❌ Failed to create seller user: {create_response.status_code}")
                    return None
            else:
                self.log(f"❌ Failed to get users: {response.status_code}")
                return None
        except Exception as e:
            self.log(f"❌ Error getting seller user: {e}")
            return None

    def create_test_listing(self):
        """Create a test listing for the seller"""
        try:
            listing_data = {
                "title": "Test Item for Buy Management",
                "description": "Test item created for Buy Management testing - will be used to create bought items",
                "price": 150.0,
                "category": "Electronics",
                "condition": "New",
                "seller_id": self.seller_user_id,
                "status": "active",
                "images": [],
                "tags": ["test", "buy-management"]
            }
            
            response = self.session.post(f"{BASE_URL}/listings", json=listing_data)
            if response.status_code == 200:
                result = response.json()
                listing_id = result.get('listing_id')
                self.log(f"✅ Created test listing: {listing_id}")
                return listing_id
            else:
                self.log(f"❌ Failed to create listing: {response.status_code}")
                if response.content:
                    self.log(f"   Error: {response.json().get('detail', 'Unknown error')}")
                return None
        except Exception as e:
            self.log(f"❌ Error creating listing: {e}")
            return None

    def submit_tender(self, listing_id):
        """Submit a tender for the listing"""
        try:
            tender_data = {
                "listing_id": listing_id,
                "buyer_id": self.demo_user_id,
                "offer_amount": 160.0,  # Offer slightly more than listing price
                "message": "Test tender for Buy Management testing"
            }
            
            response = self.session.post(f"{BASE_URL}/tenders/submit", json=tender_data)
            if response.status_code == 200:
                result = response.json()
                tender_id = result.get('tender_id')
                self.log(f"✅ Submitted tender: {tender_id} for €{tender_data['offer_amount']}")
                return tender_id
            else:
                self.log(f"❌ Failed to submit tender: {response.status_code}")
                if response.content:
                    self.log(f"   Error: {response.json().get('detail', 'Unknown error')}")
                return None
        except Exception as e:
            self.log(f"❌ Error submitting tender: {e}")
            return None

    def accept_tender(self, tender_id):
        """Accept the tender to create a bought item"""
        try:
            response = self.session.put(f"{BASE_URL}/tenders/{tender_id}/accept")
            if response.status_code == 200:
                result = response.json()
                self.log(f"✅ Accepted tender: {tender_id}")
                return True
            else:
                self.log(f"❌ Failed to accept tender: {response.status_code}")
                if response.content:
                    self.log(f"   Error: {response.json().get('detail', 'Unknown error')}")
                return False
        except Exception as e:
            self.log(f"❌ Error accepting tender: {e}")
            return False

    def verify_bought_items(self):
        """Verify that bought items now appear"""
        try:
            response = self.session.get(f"{BASE_URL}/user/bought-items/{self.demo_user_id}")
            if response.status_code == 200:
                bought_items = response.json()
                self.log(f"📊 Bought items after test: {len(bought_items)} items")
                
                if len(bought_items) > 0:
                    self.log("✅ SUCCESS: Bought items now appear!")
                    for item in bought_items:
                        self.log(f"   - {item.get('title')} - €{item.get('price')} from {item.get('seller_name')}")
                    return True
                else:
                    self.log("❌ Still no bought items found")
                    return False
            else:
                self.log(f"❌ Failed to check bought items: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Error verifying bought items: {e}")
            return False

    def create_test_data(self):
        """Main method to create test data"""
        self.log("🚀 Creating Test Data for Buy Management")
        self.log("=" * 60)
        
        # 1. Get demo user ID
        if not self.get_demo_user_id():
            self.log("❌ Cannot proceed without demo user ID")
            return False
        
        # 2. Get seller user ID
        if not self.get_seller_user_id():
            self.log("❌ Cannot proceed without seller user ID")
            return False
        
        # 3. Create test listing
        listing_id = self.create_test_listing()
        if not listing_id:
            self.log("❌ Cannot proceed without test listing")
            return False
        
        # 4. Submit tender
        tender_id = self.submit_tender(listing_id)
        if not tender_id:
            self.log("❌ Cannot proceed without tender")
            return False
        
        # 5. Accept tender
        if not self.accept_tender(tender_id):
            self.log("❌ Failed to accept tender")
            return False
        
        # 6. Verify bought items
        success = self.verify_bought_items()
        
        self.log("=" * 60)
        if success:
            self.log("🎉 SUCCESS: Test data created and bought items now appear!")
            self.log("✅ The Buy Management frontend should now show the test item")
        else:
            self.log("❌ FAILED: Test data creation did not resolve the issue")
        
        return success

if __name__ == "__main__":
    creator = TestDataCreator()
    creator.create_test_data()