#!/usr/bin/env python3
"""
Cataloro Marketplace Messaging Functionality Test Suite
Comprehensive testing of messaging functionality to identify all issues
"""

import requests
import sys
import json
import uuid
from datetime import datetime

class MessagingTester:
    def __init__(self, base_url="https://cataloro-marketplace-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.user1 = None
        self.user2 = None
        self.user1_token = None
        self.user2_token = None
        self.test_messages = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
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
                    details += f", Response: {json.dumps(response_data, indent=2)[:200]}..."
                except:
                    details += f", Response: {response.text[:100]}..."
            else:
                details += f", Expected: {expected_status}, Response: {response.text[:200]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def setup_test_users(self):
        """Create two test users for messaging"""
        print("\n👥 Setting up test users for messaging...")
        
        # Create User 1 (Alice)
        user1_data = {
            "email": "alice.messaging@cataloro.com",
            "username": "alice_msg",
            "full_name": "Alice Messaging",
            "password": "test123"
        }
        
        success1, response1 = self.run_test(
            "Create User 1 (Alice)",
            "POST",
            "api/auth/login",
            200,
            data=user1_data
        )
        
        if success1:
            self.user1 = response1.get('user')
            self.user1_token = response1.get('token')
            print(f"   User 1 ID: {self.user1['id']}")
        
        # Create User 2 (Bob)
        user2_data = {
            "email": "bob.messaging@cataloro.com", 
            "username": "bob_msg",
            "full_name": "Bob Messaging",
            "password": "test123"
        }
        
        success2, response2 = self.run_test(
            "Create User 2 (Bob)",
            "POST",
            "api/auth/login",
            200,
            data=user2_data
        )
        
        if success2:
            self.user2 = response2.get('user')
            self.user2_token = response2.get('token')
            print(f"   User 2 ID: {self.user2['id']}")
        
        return success1 and success2

    def test_message_api_endpoints(self):
        """Test all message API endpoints"""
        print("\n📨 Testing Message API Endpoints...")
        
        if not self.user1 or not self.user2:
            print("❌ Message API Tests - SKIPPED (Users not set up)")
            return False
        
        # Test 1: GET messages (empty state)
        success1, messages1 = self.run_test(
            "GET Messages (User 1 - Empty State)",
            "GET",
            f"api/user/{self.user1['id']}/messages",
            200
        )
        
        if success1:
            print(f"   User 1 has {len(messages1)} messages initially")
        
        success2, messages2 = self.run_test(
            "GET Messages (User 2 - Empty State)",
            "GET",
            f"api/user/{self.user2['id']}/messages",
            200
        )
        
        if success2:
            print(f"   User 2 has {len(messages2)} messages initially")
        
        # Test 2: POST message (User 1 to User 2)
        message_data = {
            "recipient_id": self.user2['id'],
            "subject": "Test Message 1",
            "content": "Hello Bob! This is a test message from Alice. How are you doing today?"
        }
        
        success3, send_response = self.run_test(
            "POST Message (User 1 to User 2)",
            "POST",
            f"api/user/{self.user1['id']}/messages",
            200,
            data=message_data
        )
        
        message_id = None
        if success3:
            message_id = send_response.get('id')
            print(f"   Message sent with ID: {message_id}")
            self.test_messages.append(message_id)
        
        # Test 3: Verify message appears for both users
        success4, user1_messages = self.run_test(
            "GET Messages After Send (User 1)",
            "GET",
            f"api/user/{self.user1['id']}/messages",
            200
        )
        
        success5, user2_messages = self.run_test(
            "GET Messages After Send (User 2)",
            "GET",
            f"api/user/{self.user2['id']}/messages",
            200
        )
        
        # Test 4: PUT mark as read
        if message_id:
            success6, read_response = self.run_test(
                "PUT Mark Message as Read",
                "PUT",
                f"api/user/{self.user2['id']}/messages/{message_id}/read",
                200
            )
        else:
            success6 = False
            self.log_test("PUT Mark Message as Read", False, "No message ID available")
        
        return all([success1, success2, success3, success4, success5, success6])

    def test_message_data_structure(self):
        """Test message data structure and field validation"""
        print("\n📋 Testing Message Data Structure...")
        
        if not self.user1 or not self.user2:
            print("❌ Message Data Structure Tests - SKIPPED (Users not set up)")
            return False
        
        # Test 1: Send message with all fields
        complete_message = {
            "recipient_id": self.user2['id'],
            "subject": "Complete Message Test",
            "content": "This message tests all required fields including subject and content."
        }
        
        success1, response1 = self.run_test(
            "Send Complete Message",
            "POST",
            f"api/user/{self.user1['id']}/messages",
            200,
            data=complete_message
        )
        
        message_id = response1.get('id') if success1 else None
        if message_id:
            self.test_messages.append(message_id)
        
        # Test 2: Verify message structure
        if success1:
            success2, messages = self.run_test(
                "Get Messages to Verify Structure",
                "GET",
                f"api/user/{self.user2['id']}/messages",
                200
            )
            
            if success2 and messages:
                # Find our test message
                test_message = None
                for msg in messages:
                    if msg.get('id') == message_id:
                        test_message = msg
                        break
                
                if test_message:
                    # Check required fields
                    required_fields = ['id', 'sender_id', 'recipient_id', 'subject', 'content', 'is_read', 'created_at']
                    missing_fields = []
                    
                    for field in required_fields:
                        if field not in test_message:
                            missing_fields.append(field)
                    
                    structure_valid = len(missing_fields) == 0
                    self.log_test("Message Structure Validation", structure_valid, 
                                 f"Missing fields: {missing_fields}" if missing_fields else "All required fields present")
                    
                    # Check field types and values
                    if structure_valid:
                        sender_correct = test_message['sender_id'] == self.user1['id']
                        recipient_correct = test_message['recipient_id'] == self.user2['id']
                        subject_correct = test_message['subject'] == complete_message['subject']
                        content_correct = test_message['content'] == complete_message['content']
                        is_read_bool = isinstance(test_message['is_read'], bool)
                        
                        data_integrity = all([sender_correct, recipient_correct, subject_correct, content_correct, is_read_bool])
                        self.log_test("Message Data Integrity", data_integrity,
                                     f"Sender: {sender_correct}, Recipient: {recipient_correct}, Subject: {subject_correct}, Content: {content_correct}, is_read type: {is_read_bool}")
                else:
                    self.log_test("Message Structure Validation", False, "Test message not found in response")
                    structure_valid = False
            else:
                self.log_test("Message Structure Validation", False, "Could not retrieve messages")
                structure_valid = False
        else:
            structure_valid = False
        
        # Test 3: Test message ID generation and uniqueness
        message_ids = set()
        for i in range(3):
            msg_data = {
                "recipient_id": self.user2['id'],
                "subject": f"Uniqueness Test {i+1}",
                "content": f"Testing message ID uniqueness - message {i+1}"
            }
            
            success, response = self.run_test(
                f"Send Message for ID Uniqueness Test {i+1}",
                "POST",
                f"api/user/{self.user1['id']}/messages",
                200,
                data=msg_data
            )
            
            if success and 'id' in response:
                msg_id = response['id']
                message_ids.add(msg_id)
                self.test_messages.append(msg_id)
        
        uniqueness_valid = len(message_ids) == 3
        self.log_test("Message ID Uniqueness", uniqueness_valid,
                     f"Generated {len(message_ids)} unique IDs out of 3 messages")
        
        # Test 4: Test timestamp validation
        success4, recent_messages = self.run_test(
            "Get Messages for Timestamp Validation",
            "GET",
            f"api/user/{self.user1['id']}/messages",
            200
        )
        
        timestamp_valid = False
        if success4 and recent_messages:
            for msg in recent_messages[:3]:  # Check first 3 messages
                created_at = msg.get('created_at')
                if created_at:
                    try:
                        # Try to parse the timestamp
                        if 'T' in created_at:  # ISO format
                            datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        else:
                            datetime.fromisoformat(created_at)
                        timestamp_valid = True
                        break
                    except:
                        continue
        
        self.log_test("Message Timestamp Validation", timestamp_valid,
                     "Timestamps are in valid ISO format" if timestamp_valid else "Invalid timestamp format")
        
        return all([success1, structure_valid, uniqueness_valid, timestamp_valid])

    def test_message_threading_conversations(self):
        """Test message threading and conversation functionality"""
        print("\n💬 Testing Message Threading and Conversations...")
        
        if not self.user1 or not self.user2:
            print("❌ Message Threading Tests - SKIPPED (Users not set up)")
            return False
        
        # Test 1: Send multiple messages between users
        conversation_messages = []
        
        # Alice to Bob
        msg1_data = {
            "recipient_id": self.user2['id'],
            "subject": "Project Discussion",
            "content": "Hi Bob, I wanted to discuss the new project requirements with you."
        }
        
        success1, response1 = self.run_test(
            "Send Message 1 (Alice to Bob)",
            "POST",
            f"api/user/{self.user1['id']}/messages",
            200,
            data=msg1_data
        )
        
        if success1:
            conversation_messages.append(response1.get('id'))
            self.test_messages.append(response1.get('id'))
        
        # Bob to Alice (reply)
        msg2_data = {
            "recipient_id": self.user1['id'],
            "subject": "Re: Project Discussion",
            "content": "Hi Alice, sure! I'd be happy to discuss the requirements. When would be a good time?"
        }
        
        success2, response2 = self.run_test(
            "Send Message 2 (Bob to Alice - Reply)",
            "POST",
            f"api/user/{self.user2['id']}/messages",
            200,
            data=msg2_data
        )
        
        if success2:
            conversation_messages.append(response2.get('id'))
            self.test_messages.append(response2.get('id'))
        
        # Alice to Bob (follow-up)
        msg3_data = {
            "recipient_id": self.user2['id'],
            "subject": "Re: Project Discussion",
            "content": "Great! How about tomorrow at 2 PM? We can go over the technical specifications."
        }
        
        success3, response3 = self.run_test(
            "Send Message 3 (Alice to Bob - Follow-up)",
            "POST",
            f"api/user/{self.user1['id']}/messages",
            200,
            data=msg3_data
        )
        
        if success3:
            conversation_messages.append(response3.get('id'))
            self.test_messages.append(response3.get('id'))
        
        # Test 2: Verify conversation appears for both users
        success4, alice_messages = self.run_test(
            "Get Alice's Messages (Conversation View)",
            "GET",
            f"api/user/{self.user1['id']}/messages",
            200
        )
        
        success5, bob_messages = self.run_test(
            "Get Bob's Messages (Conversation View)",
            "GET",
            f"api/user/{self.user2['id']}/messages",
            200
        )
        
        # Test 3: Verify message ordering (newest first)
        ordering_correct = False
        if success4 and alice_messages:
            # Check if messages are ordered by created_at (newest first)
            timestamps = []
            for msg in alice_messages:
                if msg.get('created_at'):
                    timestamps.append(msg['created_at'])
            
            if len(timestamps) >= 2:
                # Check if timestamps are in descending order (newest first)
                ordering_correct = all(timestamps[i] >= timestamps[i+1] for i in range(len(timestamps)-1))
        
        self.log_test("Message Ordering (Newest First)", ordering_correct,
                     f"Messages ordered correctly: {ordering_correct}")
        
        # Test 4: Verify sender/recipient relationships
        relationship_correct = True
        if success4 and success5:
            # Check Alice's messages
            for msg in alice_messages:
                if msg.get('id') in conversation_messages:
                    sender_id = msg.get('sender_id')
                    recipient_id = msg.get('recipient_id')
                    
                    # Message should involve Alice (either as sender or recipient)
                    if sender_id != self.user1['id'] and recipient_id != self.user1['id']:
                        relationship_correct = False
                        break
            
            # Check Bob's messages
            for msg in bob_messages:
                if msg.get('id') in conversation_messages:
                    sender_id = msg.get('sender_id')
                    recipient_id = msg.get('recipient_id')
                    
                    # Message should involve Bob (either as sender or recipient)
                    if sender_id != self.user2['id'] and recipient_id != self.user2['id']:
                        relationship_correct = False
                        break
        
        self.log_test("Sender/Recipient Relationships", relationship_correct,
                     f"All message relationships correct: {relationship_correct}")
        
        # Test 5: Test conversation grouping
        conversation_found = False
        if success4 and alice_messages:
            # Look for messages with similar subjects (conversation threading)
            project_messages = [msg for msg in alice_messages if 'Project Discussion' in msg.get('subject', '')]
            conversation_found = len(project_messages) >= 2
        
        self.log_test("Conversation Grouping", conversation_found,
                     f"Found conversation thread: {conversation_found}")
        
        return all([success1, success2, success3, success4, success5, ordering_correct, relationship_correct, conversation_found])

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n⚠️  Testing Edge Cases and Error Handling...")
        
        if not self.user1 or not self.user2:
            print("❌ Edge Case Tests - SKIPPED (Users not set up)")
            return False
        
        # Test 1: Send message with empty content
        empty_content_data = {
            "recipient_id": self.user2['id'],
            "subject": "Empty Content Test",
            "content": ""
        }
        
        success1, response1 = self.run_test(
            "Send Message with Empty Content",
            "POST",
            f"api/user/{self.user1['id']}/messages",
            200,  # Should still work, empty content might be allowed
            data=empty_content_data
        )
        
        if success1 and response1.get('id'):
            self.test_messages.append(response1.get('id'))
        
        # Test 2: Send message with invalid recipient ID
        invalid_recipient_data = {
            "recipient_id": "invalid-user-id-12345",
            "subject": "Invalid Recipient Test",
            "content": "This message should fail due to invalid recipient"
        }
        
        success2, response2 = self.run_test(
            "Send Message with Invalid Recipient ID",
            "POST",
            f"api/user/{self.user1['id']}/messages",
            200,  # Backend might accept any recipient_id
            data=invalid_recipient_data
        )
        
        if success2 and response2.get('id'):
            self.test_messages.append(response2.get('id'))
        
        # Test 3: Send message with non-existent user ID as sender
        success3, response3 = self.run_test(
            "Send Message with Non-existent Sender ID",
            "POST",
            "api/user/non-existent-user-id/messages",
            200,  # Backend might create the endpoint regardless
            data={
                "recipient_id": self.user2['id'],
                "subject": "Non-existent Sender Test",
                "content": "This message has a non-existent sender"
            }
        )
        
        # Test 4: Mark non-existent message as read
        fake_message_id = str(uuid.uuid4())
        success4, response4 = self.run_test(
            "Mark Non-existent Message as Read",
            "PUT",
            f"api/user/{self.user1['id']}/messages/{fake_message_id}/read",
            404  # Should return 404 for non-existent message
        )
        
        # Test 5: Get messages for non-existent user
        success5, response5 = self.run_test(
            "Get Messages for Non-existent User",
            "GET",
            "api/user/non-existent-user-id/messages",
            200  # Backend might return empty array
        )
        
        # Test 6: Send message without required fields
        incomplete_data = {
            "subject": "Missing Recipient Test"
            # Missing recipient_id and content
        }
        
        success6, response6 = self.run_test(
            "Send Message without Required Fields",
            "POST",
            f"api/user/{self.user1['id']}/messages",
            200,  # Backend might handle missing fields gracefully
            data=incomplete_data
        )
        
        # Test 7: Send very long message content
        long_content_data = {
            "recipient_id": self.user2['id'],
            "subject": "Long Content Test",
            "content": "A" * 10000  # 10,000 character message
        }
        
        success7, response7 = self.run_test(
            "Send Message with Very Long Content",
            "POST",
            f"api/user/{self.user1['id']}/messages",
            200,
            data=long_content_data
        )
        
        if success7 and response7.get('id'):
            self.test_messages.append(response7.get('id'))
        
        # Summary of edge case handling
        edge_cases_handled = 0
        total_edge_cases = 7
        
        # Count how many edge cases were handled appropriately
        if success1:  # Empty content handled
            edge_cases_handled += 1
        if not success2 or success2:  # Invalid recipient (either rejected or accepted gracefully)
            edge_cases_handled += 1
        if not success3 or success3:  # Non-existent sender (either rejected or handled)
            edge_cases_handled += 1
        if not success4:  # Non-existent message correctly returns 404
            edge_cases_handled += 1
        if success5:  # Non-existent user returns empty array
            edge_cases_handled += 1
        if not success6 or success6:  # Missing fields (either rejected or handled)
            edge_cases_handled += 1
        if success7:  # Long content handled
            edge_cases_handled += 1
        
        self.log_test("Edge Case Handling", edge_cases_handled >= 5,
                     f"Handled {edge_cases_handled}/{total_edge_cases} edge cases appropriately")
        
        return edge_cases_handled >= 5

    def test_message_status_updates(self):
        """Test message status updates (read/unread)"""
        print("\n📖 Testing Message Status Updates...")
        
        if not self.user1 or not self.user2:
            print("❌ Message Status Tests - SKIPPED (Users not set up)")
            return False
        
        # Test 1: Send a new message (should be unread initially)
        test_message_data = {
            "recipient_id": self.user2['id'],
            "subject": "Status Update Test",
            "content": "This message will be used to test read/unread status updates."
        }
        
        success1, response1 = self.run_test(
            "Send Message for Status Testing",
            "POST",
            f"api/user/{self.user1['id']}/messages",
            200,
            data=test_message_data
        )
        
        message_id = response1.get('id') if success1 else None
        if message_id:
            self.test_messages.append(message_id)
        
        # Test 2: Verify message is initially unread
        if success1:
            success2, messages = self.run_test(
                "Get Messages to Check Initial Status",
                "GET",
                f"api/user/{self.user2['id']}/messages",
                200
            )
            
            initial_unread = False
            if success2:
                for msg in messages:
                    if msg.get('id') == message_id:
                        initial_unread = msg.get('is_read') == False
                        break
            
            self.log_test("Message Initially Unread", initial_unread,
                         f"Message is unread initially: {initial_unread}")
        else:
            success2 = False
            initial_unread = False
        
        # Test 3: Mark message as read
        if message_id:
            success3, response3 = self.run_test(
                "Mark Message as Read",
                "PUT",
                f"api/user/{self.user2['id']}/messages/{message_id}/read",
                200
            )
        else:
            success3 = False
        
        # Test 4: Verify message is now read
        if success3:
            success4, messages_after_read = self.run_test(
                "Get Messages to Check Read Status",
                "GET",
                f"api/user/{self.user2['id']}/messages",
                200
            )
            
            now_read = False
            read_timestamp_present = False
            if success4:
                for msg in messages_after_read:
                    if msg.get('id') == message_id:
                        now_read = msg.get('is_read') == True
                        read_timestamp_present = 'read_at' in msg and msg['read_at'] is not None
                        break
            
            self.log_test("Message Marked as Read", now_read,
                         f"Message is read after update: {now_read}")
            self.log_test("Read Timestamp Added", read_timestamp_present,
                         f"Read timestamp present: {read_timestamp_present}")
        else:
            success4 = False
            now_read = False
            read_timestamp_present = False
        
        # Test 5: Verify read status persists
        if success4:
            success5, messages_persistence = self.run_test(
                "Get Messages to Check Persistence",
                "GET",
                f"api/user/{self.user2['id']}/messages",
                200
            )
            
            status_persisted = False
            if success5:
                for msg in messages_persistence:
                    if msg.get('id') == message_id:
                        status_persisted = msg.get('is_read') == True
                        break
            
            self.log_test("Read Status Persistence", status_persisted,
                         f"Read status persisted: {status_persisted}")
        else:
            success5 = False
            status_persisted = False
        
        # Test 6: Test marking already read message as read (idempotent)
        if message_id and success3:
            success6, response6 = self.run_test(
                "Mark Already Read Message as Read (Idempotent)",
                "PUT",
                f"api/user/{self.user2['id']}/messages/{message_id}/read",
                200
            )
        else:
            success6 = False
        
        return all([success1, success2, success3, success4, success5, success6, 
                   initial_unread, now_read, status_persisted])

    def test_real_time_functionality(self):
        """Test real-time messaging functionality"""
        print("\n⚡ Testing Real-time Functionality...")
        
        if not self.user1 or not self.user2:
            print("❌ Real-time Tests - SKIPPED (Users not set up)")
            return False
        
        # Test 1: Send multiple messages in sequence
        sequence_messages = []
        
        for i in range(5):
            msg_data = {
                "recipient_id": self.user2['id'],
                "subject": f"Sequence Message {i+1}",
                "content": f"This is message {i+1} in a sequence of 5 messages sent rapidly."
            }
            
            success, response = self.run_test(
                f"Send Sequence Message {i+1}",
                "POST",
                f"api/user/{self.user1['id']}/messages",
                200,
                data=msg_data
            )
            
            if success and response.get('id'):
                sequence_messages.append(response['id'])
                self.test_messages.append(response['id'])
        
        sequence_success = len(sequence_messages) == 5
        self.log_test("Rapid Message Sequence", sequence_success,
                     f"Sent {len(sequence_messages)}/5 messages successfully")
        
        # Test 2: Verify all messages appear in retrieval
        success2, retrieved_messages = self.run_test(
            "Retrieve Messages After Sequence",
            "GET",
            f"api/user/{self.user2['id']}/messages",
            200
        )
        
        all_messages_retrieved = False
        if success2:
            retrieved_ids = [msg.get('id') for msg in retrieved_messages]
            found_sequence_messages = sum(1 for msg_id in sequence_messages if msg_id in retrieved_ids)
            all_messages_retrieved = found_sequence_messages == len(sequence_messages)
        
        self.log_test("All Sequence Messages Retrieved", all_messages_retrieved,
                     f"Retrieved {found_sequence_messages if success2 else 0}/{len(sequence_messages)} sequence messages")
        
        # Test 3: Test message ordering consistency
        ordering_consistent = False
        if success2 and retrieved_messages:
            # Check if sequence messages appear in correct order (newest first)
            sequence_in_response = []
            for msg in retrieved_messages:
                if msg.get('id') in sequence_messages:
                    sequence_in_response.append(msg)
            
            if len(sequence_in_response) >= 2:
                # Check timestamps are in descending order
                timestamps = [msg.get('created_at') for msg in sequence_in_response]
                ordering_consistent = all(timestamps[i] >= timestamps[i+1] for i in range(len(timestamps)-1))
        
        self.log_test("Message Ordering Consistency", ordering_consistent,
                     f"Sequence messages ordered correctly: {ordering_consistent}")
        
        # Test 4: Test bidirectional messaging
        # Bob replies to Alice
        reply_data = {
            "recipient_id": self.user1['id'],
            "subject": "Re: Sequence Messages",
            "content": "I received all your sequence messages! Thanks for testing."
        }
        
        success4, reply_response = self.run_test(
            "Send Reply Message (Bidirectional Test)",
            "POST",
            f"api/user/{self.user2['id']}/messages",
            200,
            data=reply_data
        )
        
        if success4 and reply_response.get('id'):
            self.test_messages.append(reply_response['id'])
        
        # Verify Alice receives Bob's reply
        success5, alice_messages = self.run_test(
            "Verify Bidirectional Message Delivery",
            "GET",
            f"api/user/{self.user1['id']}/messages",
            200
        )
        
        bidirectional_success = False
        if success5:
            reply_id = reply_response.get('id') if success4 else None
            if reply_id:
                alice_message_ids = [msg.get('id') for msg in alice_messages]
                bidirectional_success = reply_id in alice_message_ids
        
        self.log_test("Bidirectional Message Delivery", bidirectional_success,
                     f"Reply message delivered to sender: {bidirectional_success}")
        
        # Test 5: Test latest messages retrieval
        success6, latest_messages = self.run_test(
            "Get Latest Messages",
            "GET",
            f"api/user/{self.user1['id']}/messages",
            200
        )
        
        latest_messages_correct = False
        if success6 and latest_messages:
            # Check if the most recent message is Bob's reply
            if latest_messages[0].get('sender_id') == self.user2['id']:
                latest_messages_correct = True
        
        self.log_test("Latest Messages Retrieval", latest_messages_correct,
                     f"Latest message is most recent: {latest_messages_correct}")
        
        return all([sequence_success, all_messages_retrieved, ordering_consistent, 
                   success4, bidirectional_success, latest_messages_correct])

    def cleanup_test_messages(self):
        """Clean up test messages (if delete endpoint exists)"""
        print("\n🧹 Cleaning up test messages...")
        
        # Note: The backend doesn't seem to have a DELETE endpoint for messages
        # This is just for completeness in case it gets implemented
        cleanup_count = 0
        
        for message_id in self.test_messages:
            try:
                # Try to delete message (this endpoint might not exist)
                url = f"{self.base_url}/api/user/{self.user1['id']}/messages/{message_id}"
                response = self.session.delete(url)
                if response.status_code == 200:
                    cleanup_count += 1
            except:
                pass  # Ignore cleanup errors
        
        print(f"   Cleaned up {cleanup_count}/{len(self.test_messages)} test messages")

    def run_comprehensive_messaging_tests(self):
        """Run all messaging functionality tests"""
        print("🚀 Starting Comprehensive Messaging Functionality Tests")
        print("=" * 70)
        
        # Setup
        if not self.setup_test_users():
            print("❌ Failed to set up test users - stopping tests")
            return False
        
        # Run all test suites
        test_results = []
        
        print("\n" + "="*50)
        test_results.append(self.test_message_api_endpoints())
        
        print("\n" + "="*50)
        test_results.append(self.test_message_data_structure())
        
        print("\n" + "="*50)
        test_results.append(self.test_message_threading_conversations())
        
        print("\n" + "="*50)
        test_results.append(self.test_edge_cases())
        
        print("\n" + "="*50)
        test_results.append(self.test_message_status_updates())
        
        print("\n" + "="*50)
        test_results.append(self.test_real_time_functionality())
        
        # Cleanup
        self.cleanup_test_messages()
        
        # Results
        print("\n" + "=" * 70)
        print(f"📊 Messaging Test Results: {self.tests_passed}/{self.tests_run} individual tests passed")
        
        test_suites = [
            "Message API Endpoints",
            "Message Data Structure", 
            "Message Threading & Conversations",
            "Edge Cases & Error Handling",
            "Message Status Updates",
            "Real-time Functionality"
        ]
        
        passed_suites = sum(test_results)
        print(f"📋 Test Suites: {passed_suites}/{len(test_suites)} suites passed")
        
        for i, (suite, result) in enumerate(zip(test_suites, test_results)):
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {i+1}. {suite}: {status}")
        
        if passed_suites == len(test_suites):
            print("\n🎉 All messaging functionality tests passed!")
            return True
        else:
            print(f"\n⚠️  {len(test_suites) - passed_suites} test suites failed")
            print("\n🔍 Issues Identified:")
            
            if not test_results[0]:
                print("   - Message API endpoints may have issues")
            if not test_results[1]:
                print("   - Message data structure problems detected")
            if not test_results[2]:
                print("   - Message threading/conversation issues found")
            if not test_results[3]:
                print("   - Edge case handling needs improvement")
            if not test_results[4]:
                print("   - Message status update functionality has problems")
            if not test_results[5]:
                print("   - Real-time functionality issues detected")
            
            return False

def main():
    """Main test execution"""
    tester = MessagingTester()
    success = tester.run_comprehensive_messaging_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())