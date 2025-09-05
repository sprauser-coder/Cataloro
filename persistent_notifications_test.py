#!/usr/bin/env python3
"""
Persistent Notifications Investigation and Cleanup Test
Testing to identify and permanently delete persistent "Order Completed!" notifications
"""

import requests
import json
import time
import uuid
from datetime import datetime
import pymongo
from pymongo import MongoClient

# Get backend URL from environment
BACKEND_URL = "https://market-refactor.preview.emergentagent.com/api"
MONGO_URL = "mongodb://localhost:27017"

class PersistentNotificationTester:
    def __init__(self):
        self.test_results = []
        self.mongo_client = None
        self.db = None
        self.persistent_notifications = []
        
    def setup_database_connection(self):
        """Setup direct MongoDB connection for investigation"""
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client.cataloro_marketplace
            print("✅ Connected to MongoDB for direct investigation")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            return False
        
    def log_test(self, test_name, passed, details=""):
        """Log test results"""
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
    
    def investigate_notification_collections(self):
        """Test 1: Investigate all notification-related collections"""
        print("\n=== TEST 1: Notification Collections Investigation ===")
        
        try:
            if not self.setup_database_connection():
                self.log_test("Database connection", False, "Could not connect to MongoDB")
                return
            
            # Get all collection names
            collections = self.db.list_collection_names()
            notification_collections = [col for col in collections if 'notification' in col.lower()]
            
            print(f"Found notification-related collections: {notification_collections}")
            
            collection_data = {}
            for collection_name in notification_collections:
                collection = self.db[collection_name]
                count = collection.count_documents({})
                collection_data[collection_name] = count
                print(f"  - {collection_name}: {count} documents")
            
            self.log_test(
                "Notification collections discovery", 
                True, 
                f"Found {len(notification_collections)} notification collections: {notification_collections}"
            )
            
            return collection_data
            
        except Exception as e:
            self.log_test("Notification collections discovery", False, f"Exception: {str(e)}")
            return {}
    
    def search_persistent_notifications(self):
        """Test 2: Search for the specific persistent notifications"""
        print("\n=== TEST 2: Search for Persistent 'Order Completed!' Notifications ===")
        
        try:
            target_notifications = [
                "Your sale of 'Workflow Test - Tablet' has been completed!",
                "Your sale of 'Completion Test - Premium Headphones' has been completed!"
            ]
            
            found_notifications = []
            
            # Search in all notification collections
            notification_collections = ['notifications', 'user_notifications', 'system_notifications']
            
            for collection_name in notification_collections:
                try:
                    collection = self.db[collection_name]
                    
                    for target_message in target_notifications:
                        # Search for exact message match
                        exact_matches = list(collection.find({"message": target_message}))
                        
                        # Search for partial matches
                        partial_matches = list(collection.find({
                            "message": {"$regex": "Workflow Test - Tablet|Completion Test - Premium Headphones", "$options": "i"}
                        }))
                        
                        # Search for "Order Completed" pattern
                        order_completed_matches = list(collection.find({
                            "message": {"$regex": "Order Completed|sale.*completed", "$options": "i"}
                        }))
                        
                        if exact_matches:
                            print(f"  Found {len(exact_matches)} exact matches in {collection_name}")
                            found_notifications.extend([(collection_name, "exact", doc) for doc in exact_matches])
                        
                        if partial_matches:
                            print(f"  Found {len(partial_matches)} partial matches in {collection_name}")
                            found_notifications.extend([(collection_name, "partial", doc) for doc in partial_matches])
                        
                        if order_completed_matches:
                            print(f"  Found {len(order_completed_matches)} 'order completed' pattern matches in {collection_name}")
                            found_notifications.extend([(collection_name, "pattern", doc) for doc in order_completed_matches])
                
                except Exception as e:
                    print(f"  Error searching {collection_name}: {e}")
            
            self.persistent_notifications = found_notifications
            
            if found_notifications:
                self.log_test(
                    "Persistent notifications found", 
                    True, 
                    f"Found {len(found_notifications)} matching notifications across collections"
                )
                
                # Print details of found notifications
                for collection_name, match_type, doc in found_notifications:
                    print(f"    [{collection_name}] ({match_type}): {doc.get('message', 'No message')[:100]}...")
                    print(f"      ID: {doc.get('id', doc.get('_id', 'No ID'))}")
                    print(f"      User ID: {doc.get('user_id', 'No user_id')}")
                    print(f"      Created: {doc.get('created_at', 'No timestamp')}")
                    
            else:
                self.log_test(
                    "Persistent notifications found", 
                    False, 
                    "No matching persistent notifications found in any collection"
                )
            
            return found_notifications
            
        except Exception as e:
            self.log_test("Persistent notifications search", False, f"Exception: {str(e)}")
            return []
    
    def analyze_notification_timestamps(self):
        """Test 3: Analyze timestamps to identify the specific notifications"""
        print("\n=== TEST 3: Timestamp Analysis for Target Notifications ===")
        
        try:
            # Target timestamps from the review request
            target_timestamps = [
                "1.9.2025, 21:28:19",  # Workflow Test - Tablet
                "1.9.2025, 21:28:18"   # Completion Test - Premium Headphones
            ]
            
            # Convert to various possible formats
            possible_formats = [
                "2025-01-09T21:28:19",
                "2025-01-09T21:28:18",
                "2025-09-01T21:28:19",  # In case date format is different
                "2025-09-01T21:28:18"
            ]
            
            timestamp_matches = []
            
            for collection_name in ['notifications', 'user_notifications', 'system_notifications']:
                try:
                    collection = self.db[collection_name]
                    
                    # Search by timestamp patterns
                    for timestamp_pattern in possible_formats:
                        matches = list(collection.find({
                            "created_at": {"$regex": timestamp_pattern[:16]}  # Match up to minute
                        }))
                        
                        if matches:
                            timestamp_matches.extend([(collection_name, timestamp_pattern, doc) for doc in matches])
                            print(f"  Found {len(matches)} notifications with timestamp pattern {timestamp_pattern} in {collection_name}")
                
                except Exception as e:
                    print(f"  Error searching timestamps in {collection_name}: {e}")
            
            if timestamp_matches:
                self.log_test(
                    "Timestamp analysis", 
                    True, 
                    f"Found {len(timestamp_matches)} notifications with matching timestamps"
                )
                
                for collection_name, timestamp, doc in timestamp_matches:
                    print(f"    [{collection_name}] {timestamp}: {doc.get('message', 'No message')[:80]}...")
            else:
                self.log_test(
                    "Timestamp analysis", 
                    False, 
                    "No notifications found with matching timestamps"
                )
            
            return timestamp_matches
            
        except Exception as e:
            self.log_test("Timestamp analysis", False, f"Exception: {str(e)}")
            return []
    
    def check_notification_regeneration_sources(self):
        """Test 4: Check for potential sources of notification regeneration"""
        print("\n=== TEST 4: Check for Notification Regeneration Sources ===")
        
        try:
            regeneration_sources = []
            
            # Check for automated processes or background jobs
            collections_to_check = [
                'orders', 'deals', 'tenders', 'listings', 'system_notifications',
                'scheduled_tasks', 'background_jobs', 'notification_templates'
            ]
            
            for collection_name in collections_to_check:
                try:
                    if collection_name in self.db.list_collection_names():
                        collection = self.db[collection_name]
                        
                        # Look for documents that might trigger notifications
                        if collection_name == 'orders':
                            completed_orders = list(collection.find({"status": "completed"}))
                            if completed_orders:
                                regeneration_sources.append(f"Found {len(completed_orders)} completed orders")
                        
                        elif collection_name == 'deals':
                            completed_deals = list(collection.find({"status": "completed"}))
                            if completed_deals:
                                regeneration_sources.append(f"Found {len(completed_deals)} completed deals")
                        
                        elif collection_name == 'system_notifications':
                            active_system_notifs = list(collection.find({"is_active": True}))
                            if active_system_notifs:
                                regeneration_sources.append(f"Found {len(active_system_notifs)} active system notifications")
                        
                        elif collection_name == 'notification_templates':
                            templates = list(collection.find({}))
                            if templates:
                                regeneration_sources.append(f"Found {len(templates)} notification templates")
                
                except Exception as e:
                    print(f"  Error checking {collection_name}: {e}")
            
            self.log_test(
                "Regeneration sources check", 
                True, 
                f"Potential regeneration sources: {regeneration_sources}"
            )
            
            return regeneration_sources
            
        except Exception as e:
            self.log_test("Regeneration sources check", False, f"Exception: {str(e)}")
            return []
    
    def delete_persistent_notifications(self):
        """Test 5: Delete the identified persistent notifications"""
        print("\n=== TEST 5: Delete Persistent Notifications ===")
        
        try:
            if not self.persistent_notifications:
                self.log_test(
                    "Delete persistent notifications", 
                    False, 
                    "No persistent notifications found to delete"
                )
                return False
            
            deleted_count = 0
            deletion_results = []
            
            # Group by collection for efficient deletion
            collections_to_clean = {}
            for collection_name, match_type, doc in self.persistent_notifications:
                if collection_name not in collections_to_clean:
                    collections_to_clean[collection_name] = []
                collections_to_clean[collection_name].append(doc)
            
            # Delete from each collection
            for collection_name, docs in collections_to_clean.items():
                try:
                    collection = self.db[collection_name]
                    
                    for doc in docs:
                        # Try to delete by ID (both 'id' field and '_id' field)
                        doc_id = doc.get('id') or doc.get('_id')
                        
                        if doc_id:
                            # Try deleting by 'id' field first
                            result = collection.delete_one({"id": doc_id})
                            if result.deleted_count == 0:
                                # Try deleting by '_id' field
                                result = collection.delete_one({"_id": doc_id})
                            
                            if result.deleted_count > 0:
                                deleted_count += 1
                                deletion_results.append(f"Deleted from {collection_name}: {doc.get('message', 'No message')[:50]}...")
                                print(f"    ✅ Deleted notification from {collection_name}")
                            else:
                                deletion_results.append(f"Failed to delete from {collection_name}: {doc_id}")
                                print(f"    ❌ Failed to delete notification from {collection_name}")
                
                except Exception as e:
                    deletion_results.append(f"Error deleting from {collection_name}: {e}")
                    print(f"    ❌ Error deleting from {collection_name}: {e}")
            
            if deleted_count > 0:
                self.log_test(
                    "Delete persistent notifications", 
                    True, 
                    f"Successfully deleted {deleted_count} persistent notifications"
                )
            else:
                self.log_test(
                    "Delete persistent notifications", 
                    False, 
                    "Failed to delete any persistent notifications"
                )
            
            return deleted_count > 0
            
        except Exception as e:
            self.log_test("Delete persistent notifications", False, f"Exception: {str(e)}")
            return False
    
    def verify_deletion_and_prevent_regeneration(self):
        """Test 6: Verify deletion and check for regeneration prevention"""
        print("\n=== TEST 6: Verify Deletion and Prevent Regeneration ===")
        
        try:
            # Wait a moment and then re-search for the notifications
            time.sleep(2)
            
            # Re-run the search to verify deletion
            remaining_notifications = self.search_persistent_notifications()
            
            if not remaining_notifications:
                self.log_test(
                    "Verify deletion", 
                    True, 
                    "No persistent notifications found after deletion - successfully removed"
                )
            else:
                self.log_test(
                    "Verify deletion", 
                    False, 
                    f"Still found {len(remaining_notifications)} persistent notifications after deletion attempt"
                )
            
            # Check for any automated processes that might recreate notifications
            # Look for scheduled tasks, cron jobs, or background processes
            potential_regenerators = []
            
            # Check system_notifications for auto-generating rules
            try:
                system_notifs = list(self.db.system_notifications.find({
                    "is_active": True,
                    "$or": [
                        {"message": {"$regex": "completed", "$options": "i"}},
                        {"event_type": "order_completed"},
                        {"event_type": "sale_completed"}
                    ]
                }))
                
                if system_notifs:
                    potential_regenerators.append(f"Found {len(system_notifs)} active system notifications for completion events")
            
            except Exception as e:
                print(f"  Error checking system notifications: {e}")
            
            # Provide recommendations for preventing regeneration
            recommendations = [
                "Disable any automated notification systems for 'order completed' events",
                "Check for background jobs or scheduled tasks that create notifications",
                "Review notification templates for 'sale completed' patterns",
                "Monitor the collections for 24-48 hours to ensure no regeneration"
            ]
            
            self.log_test(
                "Regeneration prevention analysis", 
                True, 
                f"Potential regenerators: {potential_regenerators}. Recommendations: {recommendations}"
            )
            
            return len(remaining_notifications) == 0
            
        except Exception as e:
            self.log_test("Verify deletion and prevent regeneration", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_cleanup(self):
        """Run comprehensive cleanup of persistent notifications"""
        print("🔍 PERSISTENT NOTIFICATIONS CLEANUP")
        print("=" * 60)
        
        # Run all tests in sequence
        self.investigate_notification_collections()
        self.search_persistent_notifications()
        self.analyze_notification_timestamps()
        self.check_notification_regeneration_sources()
        self.delete_persistent_notifications()
        self.verify_deletion_and_prevent_regeneration()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 CLEANUP SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        total_tests = len(self.test_results)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        # Cleanup recommendations
        print("\n" + "=" * 60)
        print("🔧 CLEANUP RECOMMENDATIONS")
        print("=" * 60)
        
        if self.persistent_notifications:
            print("1. ✅ Identified persistent notifications in the database")
            print("2. 🔄 Attempted deletion of persistent notifications")
            print("3. ⚠️  Monitor for regeneration over next 24-48 hours")
            print("4. 🛠️  Consider disabling automated notification systems temporarily")
        else:
            print("1. ✅ No persistent notifications found in current search")
            print("2. 🔍 Notifications may have been previously cleaned or use different patterns")
            print("3. 📊 Continue monitoring notification collections for patterns")
        
        # Close database connection
        if self.mongo_client:
            self.mongo_client.close()
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = PersistentNotificationTester()
    success = tester.run_comprehensive_cleanup()
    
    if success:
        print("\n✅ PERSISTENT NOTIFICATIONS CLEANUP: COMPLETED")
    else:
        print("\n⚠️  PERSISTENT NOTIFICATIONS CLEANUP: NEEDS ATTENTION")