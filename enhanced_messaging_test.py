#!/usr/bin/env python3
"""
Enhanced Messaging System Test Suite
Tests the improved messaging functionality with user search and enhanced message data
Focus: sender_name, recipient_name, user search, conversation grouping
"""

import requests
import sys
import json
import uuid
from datetime import datetime

class EnhancedMessagingTester:
    def __init__(self, base_url="https://cat-market-fix.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.test_users = []
        self.test_messages = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if params:
            print(f"   Params: {params}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers, params=params)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if success:
                try:
                    response_data = response.json()
                    details += f", Response: {json.dumps(response_data, indent=2)[:300]}..."
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def create_test_users(self):
        """Create test users for messaging"""
        print("\n🔧 Creating test users for enhanced messaging tests...")
        
        # Create first test user
        user1_data = {
            "username": f"alice_enhanced_{uuid.uuid4().hex[:8]}",
            "email": f"alice_enhanced_{uuid.uuid4().hex[:8]}@example.com",
            "full_name": "Alice Enhanced"
        }
        
        success1, response1 = self.run_test(
            "Create Enhanced Test User 1 (Alice)",
            "POST",
            "api/auth/register",
            200,
            data=user1_data
        )
        
        if success1:
            # Login to get user details
            login_success1, login_response1 = self.run_test(
                "Login Enhanced Test User 1",
                "POST",
                "api/auth/login",
                200,
                data={"email": user1_data["email"], "password": "test123"}
            )
            if login_success1:
                self.test_users.append(login_response1['user'])
        
        # Create second test user
        user2_data = {
            "username": f"bob_enhanced_{uuid.uuid4().hex[:8]}",
            "email": f"bob_enhanced_{uuid.uuid4().hex[:8]}@example.com",
            "full_name": "Bob Enhanced"
        }
        
        success2, response2 = self.run_test(
            "Create Enhanced Test User 2 (Bob)",
            "POST",
            "api/auth/register",
            200,
            data=user2_data
        )
        
        if success2:
            # Login to get user details
            login_success2, login_response2 = self.run_test(
                "Login Enhanced Test User 2",
                "POST",
                "api/auth/login",
                200,
                data={"email": user2_data["email"], "password": "test123"}
            )
            if login_success2:
                self.test_users.append(login_response2['user'])
        
        print(f"   Created {len(self.test_users)} enhanced test users")
        for i, user in enumerate(self.test_users):
            print(f"   User {i+1}: {user['full_name']} ({user['username']}) - ID: {user['id']}")
        
        return len(self.test_users) >= 2

    def test_user_search_endpoint(self):
        """Test the new user search endpoint GET /api/users/search"""
        print("\n🔍 Testing Enhanced User Search Endpoint...")
        
        if len(self.test_users) < 2:
            print("❌ User Search - SKIPPED (Need at least 2 test users)")
            return False
        
        # Test 1: Search by username
        search_term = self.test_users[0]['username'][:6]  # First 6 chars of username
        success1, response1 = self.run_test(
            "User Search by Username",
            "GET",
            "api/users/search",
            200,
            params={"q": search_term}
        )
        
        username_search_valid = False
        if success1:
            print(f"   Found {len(response1)} users for username search '{search_term}'")
            # Verify the search result contains expected user
            found_user = any(user['username'] == self.test_users[0]['username'] for user in response1)
            if found_user:
                print(f"   ✅ Found expected user in username search results")
                username_search_valid = True
            else:
                print(f"   ❌ Expected user not found in username search results")
        
        # Test 2: Search by full name
        search_term = self.test_users[1]['full_name'].split()[0]  # First name
        success2, response2 = self.run_test(
            "User Search by Full Name",
            "GET",
            "api/users/search",
            200,
            params={"q": search_term}
        )
        
        fullname_search_valid = False
        if success2:
            print(f"   Found {len(response2)} users for full name search '{search_term}'")
            # Verify the search result contains expected user
            found_user = any(search_term.lower() in user.get('full_name', '').lower() for user in response2)
            if found_user:
                print(f"   ✅ Found expected user in full name search results")
                fullname_search_valid = True
            else:
                print(f"   ❌ Expected user not found in full name search results")
        
        # Test 3: Minimum character requirement (should return empty for < 2 chars)
        success3, response3 = self.run_test(
            "User Search Minimum Characters (Single Char)",
            "GET",
            "api/users/search",
            200,
            params={"q": "a"}  # Single character
        )
        
        min_char_valid = False
        if success3:
            if len(response3) == 0:
                print(f"   ✅ Correctly returned empty results for single character search")
                min_char_valid = True
            else:
                print(f"   ❌ Should return empty for single character search, got {len(response3)} results")
        
        # Test 4: Verify response structure contains required fields
        response_structure_valid = False
        if success1 and len(response1) > 0:
            user_result = response1[0]
            required_fields = ['id', 'username', 'full_name', 'display_name']
            missing_fields = [field for field in required_fields if field not in user_result]
            if not missing_fields:
                print(f"   ✅ User search response has all required fields: {required_fields}")
                response_structure_valid = True
            else:
                print(f"   ❌ Missing fields in user search response: {missing_fields}")
        
        # Test 5: Test search query handling (2+ characters)
        success5, response5 = self.run_test(
            "User Search Valid Query (2+ Characters)",
            "GET",
            "api/users/search",
            200,
            params={"q": "en"}  # 2 characters
        )
        
        two_char_valid = success5  # Should work with 2+ characters
        
        return all([success1, success2, success3, success5, username_search_valid, 
                   fullname_search_valid, min_char_valid, response_structure_valid, two_char_valid])

    def test_enhanced_message_api(self):
        """Test Enhanced Message API with sender_name and recipient_name"""
        print("\n💬 Testing Enhanced Message API...")
        
        if len(self.test_users) < 2:
            print("❌ Enhanced Message API - SKIPPED (Need at least 2 test users)")
            return False
        
        user1 = self.test_users[0]
        user2 = self.test_users[1]
        
        # Test 1: Send message from user1 to user2
        message1_data = {
            "recipient_id": user2['id'],
            "subject": "Enhanced Message Test 1",
            "content": f"Hello {user2['full_name']}! This is a test message from {user1['full_name']} to verify enhanced messaging."
        }
        
        success1, response1 = self.run_test(
            "Send Enhanced Message (User1 to User2)",
            "POST",
            f"api/user/{user1['id']}/messages",
            200,
            data=message1_data
        )
        
        message1_id = response1.get('id') if success1 else None
        if message1_id:
            self.test_messages.append(message1_id)
        
        # Test 2: Send message from user2 to user1
        message2_data = {
            "recipient_id": user1['id'],
            "subject": "Re: Enhanced Message Test 1",
            "content": f"Hi {user1['full_name']}! Thanks for your message. This is {user2['full_name']} replying to test enhanced messaging."
        }
        
        success2, response2 = self.run_test(
            "Send Enhanced Message (User2 to User1)",
            "POST",
            f"api/user/{user2['id']}/messages",
            200,
            data=message2_data
        )
        
        message2_id = response2.get('id') if success2 else None
        if message2_id:
            self.test_messages.append(message2_id)
        
        # Test 3: Retrieve messages for user1 and verify enhanced fields
        success3, user1_messages = self.run_test(
            "Get Enhanced Messages for User1",
            "GET",
            f"api/user/{user1['id']}/messages",
            200
        )
        
        user1_enhanced_valid = False
        if success3 and len(user1_messages) > 0:
            print(f"   Retrieved {len(user1_messages)} messages for User1")
            
            # Check each message for enhanced fields
            enhanced_messages_count = 0
            for message in user1_messages:
                required_fields = ['sender_name', 'recipient_name', 'sender_id', 'recipient_id', 'content', 'subject']
                missing_fields = [field for field in required_fields if field not in message]
                
                if not missing_fields:
                    enhanced_messages_count += 1
                    print(f"   ✅ Message has sender_name: '{message['sender_name']}', recipient_name: '{message['recipient_name']}'")
                    
                    # Verify sender/recipient names match expected users
                    if message['sender_id'] == user1['id']:
                        expected_sender_name = user1.get('full_name', user1['username'])
                        if message['sender_name'] == expected_sender_name:
                            print(f"   ✅ Sender name correct for User1: '{message['sender_name']}'")
                        else:
                            print(f"   ❌ Sender name mismatch for User1: expected '{expected_sender_name}', got '{message['sender_name']}'")
                    elif message['sender_id'] == user2['id']:
                        expected_sender_name = user2.get('full_name', user2['username'])
                        if message['sender_name'] == expected_sender_name:
                            print(f"   ✅ Sender name correct for User2: '{message['sender_name']}'")
                        else:
                            print(f"   ❌ Sender name mismatch for User2: expected '{expected_sender_name}', got '{message['sender_name']}'")
                else:
                    print(f"   ❌ Message missing enhanced fields: {missing_fields}")
            
            user1_enhanced_valid = enhanced_messages_count > 0
        
        # Test 4: Retrieve messages for user2 and verify enhanced fields
        success4, user2_messages = self.run_test(
            "Get Enhanced Messages for User2",
            "GET",
            f"api/user/{user2['id']}/messages",
            200
        )
        
        user2_enhanced_valid = False
        if success4 and len(user2_messages) > 0:
            print(f"   Retrieved {len(user2_messages)} messages for User2")
            
            # Check each message for enhanced fields
            enhanced_messages_count = 0
            for message in user2_messages:
                required_fields = ['sender_name', 'recipient_name', 'sender_id', 'recipient_id', 'content', 'subject']
                missing_fields = [field for field in required_fields if field not in message]
                
                if not missing_fields:
                    enhanced_messages_count += 1
                    print(f"   ✅ Message has sender_name: '{message['sender_name']}', recipient_name: '{message['recipient_name']}'")
                else:
                    print(f"   ❌ Message missing enhanced fields: {missing_fields}")
            
            user2_enhanced_valid = enhanced_messages_count > 0
        
        return all([success1, success2, success3, success4, user1_enhanced_valid, user2_enhanced_valid])

    def test_conversation_grouping_data(self):
        """Test that conversation grouping works with user names"""
        print("\n🗂️ Testing Conversation Grouping with User Names...")
        
        if len(self.test_users) < 2:
            print("❌ Conversation Grouping - SKIPPED (Need test users)")
            return False
        
        user1 = self.test_users[0]
        user2 = self.test_users[1]
        
        # Send multiple messages to create a conversation
        conversation_messages = []
        
        # Message 1: Alice to Bob
        msg1_data = {
            "recipient_id": user2['id'],
            "subject": "Project Collaboration",
            "content": "Hi Bob! I'd like to discuss our upcoming project collaboration."
        }
        
        success1, response1 = self.run_test(
            "Send Conversation Message 1 (Alice to Bob)",
            "POST",
            f"api/user/{user1['id']}/messages",
            200,
            data=msg1_data
        )
        
        if success1 and response1.get('id'):
            conversation_messages.append(response1['id'])
            self.test_messages.append(response1['id'])
        
        # Message 2: Bob to Alice
        msg2_data = {
            "recipient_id": user1['id'],
            "subject": "Re: Project Collaboration",
            "content": "Hi Alice! Absolutely, I'm excited to work together. What's the timeline?"
        }
        
        success2, response2 = self.run_test(
            "Send Conversation Message 2 (Bob to Alice)",
            "POST",
            f"api/user/{user2['id']}/messages",
            200,
            data=msg2_data
        )
        
        if success2 and response2.get('id'):
            conversation_messages.append(response2['id'])
            self.test_messages.append(response2['id'])
        
        # Message 3: Alice to Bob (follow-up)
        msg3_data = {
            "recipient_id": user2['id'],
            "subject": "Re: Project Collaboration",
            "content": "Great! We have about 2 weeks. Let's schedule a meeting to discuss details."
        }
        
        success3, response3 = self.run_test(
            "Send Conversation Message 3 (Alice to Bob Follow-up)",
            "POST",
            f"api/user/{user1['id']}/messages",
            200,
            data=msg3_data
        )
        
        if success3 and response3.get('id'):
            conversation_messages.append(response3['id'])
            self.test_messages.append(response3['id'])
        
        # Test conversation grouping for Alice
        success4, alice_messages = self.run_test(
            "Get Alice's Messages for Conversation Analysis",
            "GET",
            f"api/user/{user1['id']}/messages",
            200
        )
        
        alice_conversation_valid = False
        if success4 and len(alice_messages) > 0:
            # Analyze conversation grouping potential
            conversations = {}
            for message in alice_messages:
                # Group by the other participant (not Alice)
                other_user_id = message['recipient_id'] if message['sender_id'] == user1['id'] else message['sender_id']
                other_user_name = message['recipient_name'] if message['sender_id'] == user1['id'] else message['sender_name']
                
                if other_user_id not in conversations:
                    conversations[other_user_id] = {
                        'name': other_user_name,
                        'messages': []
                    }
                conversations[other_user_id]['messages'].append(message)
            
            print(f"   ✅ Alice's messages can be grouped into {len(conversations)} conversations")
            for user_id, conv in conversations.items():
                print(f"   - Conversation with {conv['name']}: {len(conv['messages'])} messages")
                
                # Verify conversation with Bob exists and has correct name
                if user_id == user2['id'] and conv['name'] == user2['full_name']:
                    alice_conversation_valid = True
        
        # Test conversation grouping for Bob
        success5, bob_messages = self.run_test(
            "Get Bob's Messages for Conversation Analysis",
            "GET",
            f"api/user/{user2['id']}/messages",
            200
        )
        
        bob_conversation_valid = False
        if success5 and len(bob_messages) > 0:
            # Analyze conversation grouping potential
            conversations = {}
            for message in bob_messages:
                # Group by the other participant (not Bob)
                other_user_id = message['recipient_id'] if message['sender_id'] == user2['id'] else message['sender_id']
                other_user_name = message['recipient_name'] if message['sender_id'] == user2['id'] else message['sender_name']
                
                if other_user_id not in conversations:
                    conversations[other_user_id] = {
                        'name': other_user_name,
                        'messages': []
                    }
                conversations[other_user_id]['messages'].append(message)
            
            print(f"   ✅ Bob's messages can be grouped into {len(conversations)} conversations")
            for user_id, conv in conversations.items():
                print(f"   - Conversation with {conv['name']}: {len(conv['messages'])} messages")
                
                # Verify conversation with Alice exists and has correct name
                if user_id == user1['id'] and conv['name'] == user1['full_name']:
                    bob_conversation_valid = True
        
        return all([success1, success2, success3, success4, success5, 
                   alice_conversation_valid, bob_conversation_valid])

    def test_complete_message_flow(self):
        """Test complete message flow: search users, send messages, retrieve with proper user info"""
        print("\n🔄 Testing Complete Enhanced Message Flow...")
        
        if len(self.test_users) < 2:
            print("❌ Complete Message Flow - SKIPPED (Need test users)")
            return False
        
        user1 = self.test_users[0]
        user2 = self.test_users[1]
        
        # Step 1: Search for users to send messages to
        search_term = user2['username'][:4]  # Search for user2
        success1, search_results = self.run_test(
            "Search Users for Messaging",
            "GET",
            "api/users/search",
            200,
            params={"q": search_term}
        )
        
        user_found_in_search = False
        if success1:
            # Verify user2 is found in search results
            for user in search_results:
                if user['id'] == user2['id']:
                    user_found_in_search = True
                    print(f"   ✅ Found target user in search: {user['display_name']} ({user['username']})")
                    break
        
        # Step 2: Send message to found user
        if user_found_in_search:
            message_data = {
                "recipient_id": user2['id'],
                "subject": "Complete Flow Test",
                "content": f"Hi {user2['full_name']}! I found you through the user search and wanted to send you this test message."
            }
            
            success2, send_response = self.run_test(
                "Send Message to Searched User",
                "POST",
                f"api/user/{user1['id']}/messages",
                200,
                data=message_data
            )
            
            message_id = send_response.get('id') if success2 else None
            if message_id:
                self.test_messages.append(message_id)
        else:
            success2 = False
            message_id = None
        
        # Step 3: Retrieve messages with proper user information
        success3, retrieved_messages = self.run_test(
            "Retrieve Messages with User Information",
            "GET",
            f"api/user/{user2['id']}/messages",
            200
        )
        
        message_with_user_info = False
        if success3 and message_id:
            # Find our test message and verify it has proper user information
            for message in retrieved_messages:
                if message.get('id') == message_id:
                    # Verify enhanced user information is present
                    has_sender_name = 'sender_name' in message and message['sender_name'] == user1['full_name']
                    has_recipient_name = 'recipient_name' in message and message['recipient_name'] == user2['full_name']
                    has_proper_ids = message['sender_id'] == user1['id'] and message['recipient_id'] == user2['id']
                    
                    if has_sender_name and has_recipient_name and has_proper_ids:
                        message_with_user_info = True
                        print(f"   ✅ Message has complete user information:")
                        print(f"      Sender: {message['sender_name']} (ID: {message['sender_id']})")
                        print(f"      Recipient: {message['recipient_name']} (ID: {message['recipient_id']})")
                    else:
                        print(f"   ❌ Message missing proper user information:")
                        print(f"      Sender name: {has_sender_name}, Recipient name: {has_recipient_name}, IDs: {has_proper_ids}")
                    break
        
        # Step 4: Verify conversation grouping works with user names
        success4, all_messages = self.run_test(
            "Verify Conversation Data Structure",
            "GET",
            f"api/user/{user1['id']}/messages",
            200
        )
        
        conversation_data_valid = False
        if success4:
            # Check if we can group messages by conversation partners
            conversation_partners = set()
            for message in all_messages:
                other_user_name = message['recipient_name'] if message['sender_id'] == user1['id'] else message['sender_name']
                conversation_partners.add(other_user_name)
            
            if user2['full_name'] in conversation_partners:
                conversation_data_valid = True
                print(f"   ✅ Conversation grouping data available - found conversation with {user2['full_name']}")
            else:
                print(f"   ❌ Conversation grouping data incomplete - {user2['full_name']} not found in partners")
        
        # Step 5: Test message read functionality in complete flow
        success5 = False
        if message_id:
            success5, read_response = self.run_test(
                "Mark Message as Read (Complete Flow)",
                "PUT",
                f"api/user/{user2['id']}/messages/{message_id}/read",
                200
            )
        
        return all([success1, success2, success3, success4, success5,
                   user_found_in_search, message_with_user_info, conversation_data_valid])

    def run_enhanced_messaging_tests(self):
        """Run all enhanced messaging system tests"""
        print("🚀 Starting Enhanced Messaging System Tests")
        print("=" * 60)
        print("Focus: sender_name, recipient_name, user search, conversation grouping")
        print("=" * 60)
        
        # Step 1: Create test users
        if not self.create_test_users():
            print("\n❌ CRITICAL: Failed to create test users. Cannot proceed with enhanced messaging tests.")
            return False
        
        # Step 2: Test user search functionality
        search_success = self.test_user_search_endpoint()
        
        # Step 3: Test enhanced message API
        api_success = self.test_enhanced_message_api()
        
        # Step 4: Test conversation grouping
        grouping_success = self.test_conversation_grouping_data()
        
        # Step 5: Test complete message flow
        flow_success = self.test_complete_message_flow()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 ENHANCED MESSAGING SYSTEM TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        print("\n🔍 Test Categories:")
        print(f"   User Search Endpoint: {'✅ PASSED' if search_success else '❌ FAILED'}")
        print(f"   Enhanced Message API: {'✅ PASSED' if api_success else '❌ FAILED'}")
        print(f"   Conversation Grouping: {'✅ PASSED' if grouping_success else '❌ FAILED'}")
        print(f"   Complete Message Flow: {'✅ PASSED' if flow_success else '❌ FAILED'}")
        
        overall_success = all([search_success, api_success, grouping_success, flow_success])
        
        print(f"\n🎯 OVERALL ENHANCED MESSAGING STATUS: {'✅ FULLY FUNCTIONAL' if overall_success else '❌ ISSUES DETECTED'}")
        
        if overall_success:
            print("\n✅ All enhanced messaging functionality improvements are working correctly:")
            print("   - GET /api/user/{user_id}/messages includes sender_name and recipient_name")
            print("   - GET /api/users/search provides proper user search functionality")
            print("   - Complete message flow works end-to-end with user information")
            print("   - Conversation grouping works properly with user names")
            print("   - User search handles minimum 2 characters requirement")
            print("   - Message enhancement includes all necessary user information")
        else:
            print("\n❌ Some enhanced messaging functionality issues detected:")
            if not search_success:
                print("   - User search endpoint has issues")
            if not api_success:
                print("   - Enhanced message API missing sender_name/recipient_name")
            if not grouping_success:
                print("   - Conversation grouping with user names not working")
            if not flow_success:
                print("   - Complete message flow has integration issues")
        
        return overall_success

if __name__ == "__main__":
    tester = EnhancedMessagingTester()
    success = tester.run_enhanced_messaging_tests()
    sys.exit(0 if success else 1)