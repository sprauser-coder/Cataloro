#!/usr/bin/env python3
"""
Comprehensive Backend Testing for New User Rating System and Enhanced Messaging Endpoints
Testing Agent: Focused testing of newly implemented features
"""

import asyncio
import aiohttp
import json
import uuid
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except:
        pass
    return "https://marketplace-admin-1.preview.emergentagent.com"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

class BackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_users = []
        self.test_transactions = []
        self.test_messages = []
        
    async def setup_session(self):
        """Setup HTTP session"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if error:
            print(f"   Error: {error}")
            
    async def make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request with error handling"""
        try:
            url = f"{API_BASE}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    return await response.json(), response.status
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, params=params) as response:
                    return await response.json(), response.status
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, params=params) as response:
                    return await response.json(), response.status
            elif method.upper() == "DELETE":
                async with self.session.delete(url, params=params) as response:
                    return await response.json(), response.status
                    
        except Exception as e:
            return {"error": str(e)}, 500
            
    async def setup_test_data(self):
        """Setup test users and transactions for rating system testing"""
        print("\n🔧 Setting up test data...")
        
        # Use admin user for testing
        admin_login_response, admin_status = await self.make_request("POST", "/auth/login", {
            "email": "admin@cataloro.com",
            "password": "admin123"
        })
        
        if admin_status == 200 and "user" in admin_login_response:
            admin_user = admin_login_response["user"]
            self.test_users.append(admin_user)
            print(f"✅ Admin user logged in: {admin_user.get('username', 'admin')}")
        
        # Create a demo user for testing
        demo_login_response, demo_status = await self.make_request("POST", "/auth/login", {
            "email": "demo@test.com",
            "password": "demo123"
        })
        
        if demo_status == 200 and "user" in demo_login_response:
            demo_user = demo_login_response["user"]
            self.test_users.append(demo_user)
            print(f"✅ Demo user logged in: {demo_user.get('username', 'demo')}")
        
        print(f"✅ Setup {len(self.test_users)} test users")
        
        # Create mock transaction data for testing
        if len(self.test_users) >= 1:
            user = self.test_users[0]
            
            # Create mock transaction for rating system testing
            mock_transaction = {
                "id": str(uuid.uuid4()),
                "buyer_id": user["id"],
                "seller_id": user["id"],  # Same user for simplicity
                "listing_id": str(uuid.uuid4()),
                "status": "completed"
            }
            
            self.test_transactions.append(mock_transaction)
            print(f"✅ Created mock transaction: {mock_transaction['id']}")
                
    async def test_user_rating_system(self):
        """Test all user rating system endpoints"""
        print("\n🔍 Testing User Rating System Endpoints...")
        
        if len(self.test_users) < 2 or len(self.test_transactions) < 1:
            self.log_result("User Rating System Setup", False, "Insufficient test data", "Need at least 2 users and 1 transaction")
            return
            
        buyer = self.test_users[0]
        seller = self.test_users[1]
        transaction = self.test_transactions[0]
        
        # Test 1: POST /api/user-ratings/create
        await self.test_create_user_rating(buyer["id"], seller["id"], transaction["id"])
        
        # Test 2: GET /api/user-ratings/{user_id}
        await self.test_get_user_ratings(seller["id"])
        
        # Test 3: GET /api/user-ratings/{user_id}/stats
        await self.test_get_user_rating_stats(seller["id"])
        
        # Test 4: GET /api/user-ratings/can-rate/{user_id}/{target_user_id}
        await self.test_can_rate_user(buyer["id"], seller["id"])
        
    async def test_create_user_rating(self, rater_id, rated_user_id, transaction_id):
        """Test creating a user rating"""
        rating_data = {
            "rater_id": rater_id,
            "rated_user_id": rated_user_id,
            "transaction_id": transaction_id,
            "rating": 5,
            "comment": "Excellent seller, fast shipping and great communication!"
        }
        
        response, status = await self.make_request("POST", "/user-ratings/create", rating_data)
        
        if status == 200:
            self.log_result("Create User Rating", True, f"Rating created successfully: {response.get('rating_id')}")
        else:
            self.log_result("Create User Rating", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
        # Test invalid rating (should fail)
        invalid_rating_data = rating_data.copy()
        invalid_rating_data["rating"] = 6  # Invalid rating > 5
        
        response, status = await self.make_request("POST", "/user-ratings/create", invalid_rating_data)
        
        if status == 400:
            self.log_result("Create User Rating - Invalid Data", True, "Correctly rejected invalid rating")
        else:
            self.log_result("Create User Rating - Invalid Data", False, f"Should reject invalid rating, got status: {status}")
            
    async def test_get_user_ratings(self, user_id):
        """Test fetching user ratings"""
        response, status = await self.make_request("GET", f"/user-ratings/{user_id}")
        
        if status == 200:
            ratings = response if isinstance(response, list) else []
            self.log_result("Get User Ratings", True, f"Retrieved {len(ratings)} ratings")
            
            # Test with filter parameters
            response, status = await self.make_request("GET", f"/user-ratings/{user_id}", params={"as_seller": True, "limit": 10})
            if status == 200:
                self.log_result("Get User Ratings - Filtered", True, f"Retrieved seller ratings with filters")
            else:
                self.log_result("Get User Ratings - Filtered", False, f"Status: {status}")
        else:
            self.log_result("Get User Ratings", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
    async def test_get_user_rating_stats(self, user_id):
        """Test fetching user rating statistics"""
        response, status = await self.make_request("GET", f"/user-ratings/{user_id}/stats")
        
        if status == 200:
            required_fields = ["total_ratings", "average_rating", "seller_rating", "buyer_rating", "rating_distribution"]
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                self.log_result("Get User Rating Stats", True, f"Stats: {response['total_ratings']} ratings, avg: {response['average_rating']}")
            else:
                self.log_result("Get User Rating Stats", False, f"Missing fields: {missing_fields}")
        else:
            self.log_result("Get User Rating Stats", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
    async def test_can_rate_user(self, user_id, target_user_id):
        """Test checking if user can rate another user"""
        response, status = await self.make_request("GET", f"/user-ratings/can-rate/{user_id}/{target_user_id}")
        
        if status == 200:
            can_rate = response.get("can_rate", False)
            reason = response.get("reason", "")
            self.log_result("Can Rate User Check", True, f"Can rate: {can_rate}, Reason: {reason}")
        else:
            self.log_result("Can Rate User Check", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
    async def test_enhanced_messaging_system(self):
        """Test all enhanced messaging system endpoints"""
        print("\n💬 Testing Enhanced Messaging System Endpoints...")
        
        if len(self.test_users) < 2:
            self.log_result("Enhanced Messaging Setup", False, "Insufficient test data", "Need at least 2 users")
            return
            
        user1 = self.test_users[0]
        user2 = self.test_users[1]
        
        # Test 1: POST /api/messages/send
        message_id = await self.test_send_enhanced_message(user1["id"], user2["id"])
        
        # Test 2: GET /api/messages/conversations/{user_id}
        await self.test_get_user_conversations(user1["id"])
        
        # Test 3: GET /api/messages/conversation/{user_id}/{other_user_id}
        await self.test_get_conversation_messages(user1["id"], user2["id"])
        
        # Test 4: DELETE /api/messages/{message_id}
        if message_id:
            await self.test_delete_message(message_id, user1["id"])
            
        # Test 5: GET /api/messages/search/{user_id}
        await self.test_search_messages(user1["id"])
        
    async def test_send_enhanced_message(self, sender_id, recipient_id):
        """Test sending enhanced messages"""
        message_data = {
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "content": "Hello! This is a test message for the enhanced messaging system.",
            "message_type": "text",
            "metadata": {"test": True}
        }
        
        response, status = await self.make_request("POST", "/messages/send", message_data)
        
        if status == 200:
            message_id = response.get("message_id")
            self.test_messages.append(message_id)
            self.log_result("Send Enhanced Message", True, f"Message sent successfully: {message_id}")
            return message_id
        else:
            self.log_result("Send Enhanced Message", False, f"Status: {status}", response.get("detail", "Unknown error"))
            return None
            
        # Test invalid message (empty content)
        invalid_message = message_data.copy()
        invalid_message["content"] = ""
        
        response, status = await self.make_request("POST", "/messages/send", invalid_message)
        
        if status == 400:
            self.log_result("Send Enhanced Message - Invalid Data", True, "Correctly rejected empty message")
        else:
            self.log_result("Send Enhanced Message - Invalid Data", False, f"Should reject empty message, got status: {status}")
            
    async def test_get_user_conversations(self, user_id):
        """Test fetching user conversations"""
        response, status = await self.make_request("GET", f"/messages/conversations/{user_id}")
        
        if status == 200:
            conversations = response.get("conversations", [])
            total_conversations = response.get("total_conversations", 0)
            total_unread = response.get("total_unread", 0)
            
            self.log_result("Get User Conversations", True, f"Retrieved {total_conversations} conversations, {total_unread} unread")
        else:
            self.log_result("Get User Conversations", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
    async def test_get_conversation_messages(self, user_id, other_user_id):
        """Test fetching specific conversation messages"""
        response, status = await self.make_request("GET", f"/messages/conversation/{user_id}/{other_user_id}")
        
        if status == 200:
            messages = response.get("messages", [])
            has_more = response.get("has_more", False)
            
            self.log_result("Get Conversation Messages", True, f"Retrieved {len(messages)} messages, has_more: {has_more}")
        else:
            self.log_result("Get Conversation Messages", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
        # Test with pagination parameters
        response, status = await self.make_request("GET", f"/messages/conversation/{user_id}/{other_user_id}", params={"limit": 10, "offset": 0})
        
        if status == 200:
            self.log_result("Get Conversation Messages - Paginated", True, "Pagination parameters accepted")
        else:
            self.log_result("Get Conversation Messages - Paginated", False, f"Status: {status}")
            
    async def test_delete_message(self, message_id, user_id):
        """Test deleting messages"""
        response, status = await self.make_request("DELETE", f"/messages/{message_id}", params={"user_id": user_id})
        
        if status == 200:
            self.log_result("Delete Message", True, "Message deleted successfully")
        else:
            self.log_result("Delete Message", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
        # Test deleting non-existent message
        fake_message_id = str(uuid.uuid4())
        response, status = await self.make_request("DELETE", f"/messages/{fake_message_id}", params={"user_id": user_id})
        
        if status == 404:
            self.log_result("Delete Message - Not Found", True, "Correctly handled non-existent message")
        else:
            self.log_result("Delete Message - Not Found", False, f"Should return 404, got status: {status}")
            
    async def test_search_messages(self, user_id):
        """Test searching messages"""
        # Test with search query
        response, status = await self.make_request("GET", f"/messages/search/{user_id}", params={"q": "test", "limit": 10})
        
        if status == 200:
            results = response.get("results", [])
            self.log_result("Search Messages", True, f"Search returned {len(results)} results")
        else:
            self.log_result("Search Messages", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
        # Test empty search query
        response, status = await self.make_request("GET", f"/messages/search/{user_id}", params={"q": ""})
        
        if status == 200:
            results = response.get("results", [])
            if len(results) == 0:
                self.log_result("Search Messages - Empty Query", True, "Empty query returned no results")
            else:
                self.log_result("Search Messages - Empty Query", False, "Empty query should return no results")
        else:
            self.log_result("Search Messages - Empty Query", False, f"Status: {status}")
            
    async def test_enhanced_profile_endpoints(self):
        """Test enhanced profile endpoints"""
        print("\n👤 Testing Enhanced Profile Endpoints...")
        
        if len(self.test_users) < 1:
            self.log_result("Enhanced Profile Setup", False, "Insufficient test data", "Need at least 1 user")
            return
            
        user = self.test_users[0]
        user_id = user["id"]
        
        # Test 1: GET /api/auth/profile/{user_id}/stats
        await self.test_get_profile_statistics(user_id)
        
        # Test 2: POST /api/auth/profile/{user_id}/export
        await self.test_export_user_data(user_id)
        
        # Test 3: GET /api/profile/{user_id}/public
        await self.test_get_public_profile(user_id)
        
    async def test_get_profile_statistics(self, user_id):
        """Test fetching comprehensive profile statistics"""
        response, status = await self.make_request("GET", f"/auth/profile/{user_id}/stats")
        
        if status == 200:
            required_sections = ["user_info", "statistics", "ratings", "activity"]
            missing_sections = [section for section in required_sections if section not in response]
            
            if not missing_sections:
                user_info = response["user_info"]
                stats = response["statistics"]
                self.log_result("Get Profile Statistics", True, f"User: {user_info.get('username')}, Listings: {stats.get('total_listings', 0)}")
            else:
                self.log_result("Get Profile Statistics", False, f"Missing sections: {missing_sections}")
        else:
            self.log_result("Get Profile Statistics", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
    async def test_export_user_data(self, user_id):
        """Test PDF data export functionality"""
        response, status = await self.make_request("POST", f"/auth/profile/{user_id}/export")
        
        if status == 200:
            pdf_data = response.get("pdf_data")
            filename = response.get("filename")
            
            if pdf_data and filename:
                # Verify PDF data is base64 encoded
                try:
                    import base64
                    decoded = base64.b64decode(pdf_data)
                    if decoded.startswith(b'%PDF'):
                        self.log_result("Export User Data", True, f"PDF export successful: {filename}")
                    else:
                        self.log_result("Export User Data", False, "PDF data is not valid PDF format")
                except Exception as e:
                    self.log_result("Export User Data", False, f"PDF data validation failed: {str(e)}")
            else:
                self.log_result("Export User Data", False, "Missing pdf_data or filename in response")
        else:
            self.log_result("Export User Data", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
    async def test_get_public_profile(self, user_id):
        """Test public profile endpoint"""
        response, status = await self.make_request("GET", f"/profile/{user_id}/public")
        
        if status == 200:
            is_public = response.get("public", False)
            
            if is_public:
                required_fields = ["user", "statistics", "ratings"]
                missing_fields = [field for field in required_fields if field not in response]
                
                if not missing_fields:
                    user_data = response["user"]
                    self.log_result("Get Public Profile", True, f"Public profile for: {user_data.get('username')}")
                else:
                    self.log_result("Get Public Profile", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("Get Public Profile", True, "Profile is private (correctly handled)")
        else:
            self.log_result("Get Public Profile", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
    async def test_backend_health(self):
        """Test backend health and connectivity"""
        print("\n🏥 Testing Backend Health...")
        
        response, status = await self.make_request("GET", "/health")
        
        if status == 200:
            app_name = response.get("app", "")
            version = response.get("version", "")
            self.log_result("Backend Health Check", True, f"App: {app_name}, Version: {version}")
        else:
            self.log_result("Backend Health Check", False, f"Status: {status}", response.get("detail", "Unknown error"))
            
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🧪 BACKEND TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['error']}")
                    
        print(f"\n🎯 TESTING FOCUS AREAS:")
        print(f"   • User Rating System: 4 endpoints tested")
        print(f"   • Enhanced Messaging: 5 endpoints tested") 
        print(f"   • Enhanced Profile: 3 endpoints tested")
        print(f"   • Backend Health: 1 endpoint tested")
        
        print(f"\n📊 ENDPOINT COVERAGE:")
        rating_tests = [r for r in self.test_results if "Rating" in r["test"]]
        messaging_tests = [r for r in self.test_results if "Message" in r["test"] or "Conversation" in r["test"]]
        profile_tests = [r for r in self.test_results if "Profile" in r["test"]]
        
        print(f"   • Rating System: {sum(1 for t in rating_tests if t['success'])}/{len(rating_tests)} passed")
        print(f"   • Messaging System: {sum(1 for t in messaging_tests if t['success'])}/{len(messaging_tests)} passed")
        print(f"   • Profile System: {sum(1 for t in profile_tests if t['success'])}/{len(profile_tests)} passed")
        
async def main():
    """Main test execution"""
    print("🚀 Starting Comprehensive Backend Testing")
    print(f"🌐 Backend URL: {BASE_URL}")
    print("="*80)
    
    tester = BackendTester()
    
    try:
        await tester.setup_session()
        
        # Test backend health first
        await tester.test_backend_health()
        
        # Setup test data
        await tester.setup_test_data()
        
        # Run all test suites
        await tester.test_user_rating_system()
        await tester.test_enhanced_messaging_system()
        await tester.test_enhanced_profile_endpoints()
        
        # Print summary
        tester.print_summary()
        
    except Exception as e:
        print(f"❌ Testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        await tester.cleanup_session()

if __name__ == "__main__":
    asyncio.run(main())