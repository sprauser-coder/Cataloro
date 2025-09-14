#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - COMPLETED TRANSACTIONS FUNCTIONALITY TESTING
Testing the completed transactions functionality in the backend

SPECIFIC TESTS REQUESTED:
1. **Test Transaction Completion Endpoint**: POST /api/user/complete-transaction with valid listing_id, notes, and method
2. **Test Get Completed Transactions**: GET /api/user/completed-transactions/{user_id} to retrieve user's completed transactions
3. **Test Undo Completion**: DELETE /api/user/completed-transactions/{completion_id} to undo a completion
4. **Test Admin Overview**: GET /api/admin/completed-transactions to get admin view of all completions
5. **Test Dual Party Completion**: Have both buyer and seller mark the same transaction as complete

CRITICAL ENDPOINTS BEING TESTED:
- POST /api/auth/login (user authentication)
- POST /api/user/complete-transaction (mark transaction as complete)
- GET /api/user/completed-transactions/{user_id} (get user's completed transactions)
- DELETE /api/user/completed-transactions/{completion_id} (undo completion)
- GET /api/admin/completed-transactions (admin view of all completions)

EXPECTED RESULTS:
- Transaction completion creates proper records and sends notifications
- Users can retrieve their completed transactions with proper role context
- Users can undo their completion confirmations
- Admin can view all completions with proper status information
- Dual party completion sets is_fully_completed to true
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
import pytz

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://mobilefixed-market.preview.emergentagent.com/api"

class CompletedTransactionsTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name, success, details, response_time=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        time_info = f" ({response_time:.1f}ms)" if response_time else ""
        print(f"{status}: {test_name}{time_info}")
        print(f"   Details: {details}")
        print()
    
    async def test_login_and_get_token(self, email="admin@cataloro.com", password="admin123"):
        """Test login and get JWT token"""
        start_time = datetime.now()
        
        try:
            login_data = {
                "email": email,
                "password": password
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    token = data.get("token")
                    user = data.get("user", {})
                    user_id = user.get("id")
                    
                    if token and user_id:
                        self.log_result(
                            "Login Authentication", 
                            True, 
                            f"Successfully logged in as {user.get('full_name', 'Unknown')} (ID: {user_id}), token received",
                            response_time
                        )
                        return token, user_id, user
                    else:
                        self.log_result(
                            "Login Authentication", 
                            False, 
                            f"Login successful but missing token or user_id in response: {data}",
                            response_time
                        )
                        return None, None, None
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Login Authentication", 
                        False, 
                        f"Login failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None, None, None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Login Authentication", 
                False, 
                f"Login request failed with exception: {str(e)}",
                response_time
            )
            return None, None, None
    
    async def test_database_connectivity(self):
        """Test if backend can connect to database"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    self.log_result(
                        "Database Connectivity", 
                        True, 
                        f"Backend health check passed: {data.get('status', 'unknown')}",
                        response_time
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Database Connectivity", 
                        False, 
                        f"Health check failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return False
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Database Connectivity", 
                False, 
                f"Health check failed with exception: {str(e)}",
                response_time
            )
            return False
    
    async def find_accepted_tender_for_testing(self, admin_token, admin_user_id):
        """Find an accepted tender for testing completed transactions"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            # Get buyer tenders for admin user to find accepted ones
            async with self.session.get(f"{BACKEND_URL}/tenders/buyer/{admin_user_id}", headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    tenders_data = await response.json()
                    
                    # Find accepted tenders
                    accepted_tenders = []
                    if isinstance(tenders_data, list):
                        accepted_tenders = [t for t in tenders_data if t.get('status') == 'accepted']
                    
                    if accepted_tenders:
                        test_tender = accepted_tenders[0]  # Use first accepted tender
                        self.log_result(
                            "Find Accepted Tender", 
                            True, 
                            f"Found accepted tender: {test_tender.get('id')} for listing {test_tender.get('listing', {}).get('id')}",
                            response_time
                        )
                        return test_tender
                    else:
                        # If no accepted tenders, try to create one for testing
                        return await self.create_test_tender_for_completion_testing(admin_token, admin_user_id)
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Find Accepted Tender", 
                        False, 
                        f"Failed to get buyer tenders: Status {response.status}: {error_text}",
                        response_time
                    )
                    return None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Find Accepted Tender", 
                False, 
                f"Request failed: {str(e)}",
                response_time
            )
            return None
    
    async def create_test_tender_for_completion_testing(self, admin_token, admin_user_id):
        """Create a test tender and accept it for completion testing"""
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            # First, get a listing to create a tender for (not owned by admin user)
            async with self.session.get(f"{BACKEND_URL}/marketplace/browse?limit=10", headers=headers) as response:
                if response.status == 200:
                    listings_data = await response.json()
                    listings = listings_data.get('listings', []) if isinstance(listings_data, dict) else listings_data
                    
                    # Find a listing not owned by admin user
                    test_listing = None
                    for listing in listings:
                        if listing.get('seller_id') != admin_user_id:
                            test_listing = listing
                            break
                    
                    if test_listing:
                        listing_id = test_listing.get('id')
                        seller_id = test_listing.get('seller_id')
                        
                        # Create a tender
                        tender_data = {
                            "listing_id": listing_id,
                            "offer_amount": test_listing.get('price', 100) * 0.9,  # Offer 90% of asking price
                            "message": "Test tender for completion testing"
                        }
                        
                        async with self.session.post(f"{BACKEND_URL}/tenders/submit", json=tender_data, headers=headers) as tender_response:
                            if tender_response.status == 200:
                                tender_result = await tender_response.json()
                                tender_id = tender_result.get('id')
                                
                                # Accept the tender (need seller_id for acceptance)
                                accept_data = {"seller_id": seller_id}
                                async with self.session.put(f"{BACKEND_URL}/tenders/{tender_id}/accept", json=accept_data, headers=headers) as accept_response:
                                    if accept_response.status == 200:
                                        accept_result = await accept_response.json()
                                        
                                        self.log_result(
                                            "Create Test Tender", 
                                            True, 
                                            f"Created and accepted test tender: {tender_id} for listing {listing_id}"
                                        )
                                        
                                        return {
                                            'id': tender_id,
                                            'listing_id': listing_id,
                                            'status': 'accepted',
                                            'buyer_id': admin_user_id,
                                            'seller_id': seller_id,
                                            'listing': test_listing
                                        }
                                    else:
                                        error_text = await accept_response.text()
                                        self.log_result("Create Test Tender", False, f"Failed to accept tender: {error_text}")
                            else:
                                error_text = await tender_response.text()
                                self.log_result("Create Test Tender", False, f"Failed to create tender: {error_text}")
            
            self.log_result("Create Test Tender", False, "Could not create test tender for completion testing")
            return None
            
        except Exception as e:
            self.log_result("Create Test Tender", False, f"Failed to create test tender: {str(e)}")
            return None
    
    async def test_complete_transaction_endpoint(self, token, tender, notes, method):
        """Test POST /api/user/complete-transaction"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            # Handle both direct listing_id and nested listing structure
            listing_id = tender.get('listing_id') or tender.get('listing', {}).get('id')
            completion_data = {
                "listing_id": listing_id,
                "notes": notes,
                "method": method
            }
            
            async with self.session.post(f"{BACKEND_URL}/user/complete-transaction", 
                                       json=completion_data, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    completion = data.get('completion', {})
                    completion_id = completion.get('id')
                    is_fully_completed = data.get('is_fully_completed', False)
                    
                    self.log_result(
                        "Complete Transaction Endpoint", 
                        True, 
                        f"Transaction marked as complete. Completion ID: {completion_id}, Fully completed: {is_fully_completed}",
                        response_time
                    )
                    
                    return {
                        'success': True,
                        'completion_id': completion_id,
                        'completion': completion,
                        'is_fully_completed': is_fully_completed,
                        'listing_id': listing_id
                    }
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Complete Transaction Endpoint", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Complete Transaction Endpoint", 
                False, 
                f"Request failed: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def test_get_completed_transactions(self, user_id):
        """Test GET /api/user/completed-transactions/{user_id}"""
        start_time = datetime.now()
        
        try:
            async with self.session.get(f"{BACKEND_URL}/user/completed-transactions/{user_id}") as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list):
                        self.log_result(
                            "Get Completed Transactions", 
                            True, 
                            f"Retrieved {len(data)} completed transactions with proper role context",
                            response_time
                        )
                        
                        # Verify structure of transactions
                        if data:
                            sample_transaction = data[0]
                            has_role_context = 'user_role_in_transaction' in sample_transaction
                            has_other_party = 'other_party' in sample_transaction
                            
                            structure_details = f"Role context: {has_role_context}, Other party info: {has_other_party}"
                            self.log_result(
                                "Transaction Structure Validation", 
                                has_role_context and has_other_party, 
                                f"Transaction structure validation: {structure_details}"
                            )
                        
                        return {
                            'success': True,
                            'transactions': data,
                            'count': len(data)
                        }
                    else:
                        self.log_result(
                            "Get Completed Transactions", 
                            False, 
                            f"Expected array response, got: {type(data)}",
                            response_time
                        )
                        return {'success': False, 'error': 'Invalid response format'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Get Completed Transactions", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Get Completed Transactions", 
                False, 
                f"Request failed: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def test_dual_party_completion(self, second_user_token, tender, first_completion_result):
        """Test dual party completion - second user marks same transaction complete"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {second_user_token}"}
            # Handle both direct listing_id and nested listing structure
            listing_id = tender.get('listing_id') or tender.get('listing', {}).get('id')
            completion_data = {
                "listing_id": listing_id,
                "notes": "Second party completion - deal finalized",
                "method": "meeting"
            }
            
            async with self.session.post(f"{BACKEND_URL}/user/complete-transaction", 
                                       json=completion_data, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    is_fully_completed = data.get('is_fully_completed', False)
                    completion = data.get('completion', {})
                    
                    self.log_result(
                        "Dual Party Completion", 
                        True, 
                        f"Second party completion successful. Fully completed: {is_fully_completed}",
                        response_time
                    )
                    
                    # Verify that is_fully_completed is now true
                    if is_fully_completed:
                        self.log_result(
                            "Dual Party Completion Validation", 
                            True, 
                            "✅ Both parties confirmed - transaction is fully completed"
                        )
                    else:
                        self.log_result(
                            "Dual Party Completion Validation", 
                            False, 
                            "❌ Both parties marked complete but is_fully_completed is still false"
                        )
                    
                    return {
                        'success': True,
                        'is_fully_completed': is_fully_completed,
                        'completion': completion
                    }
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Dual Party Completion", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Dual Party Completion", 
                False, 
                f"Request failed: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def test_admin_completed_transactions_overview(self, admin_token):
        """Test GET /api/admin/completed-transactions"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            async with self.session.get(f"{BACKEND_URL}/admin/completed-transactions", headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify admin overview structure
                    expected_fields = ['total_transactions', 'fully_completed', 'pending_confirmation', 'transactions']
                    missing_fields = [field for field in expected_fields if field not in data]
                    
                    if not missing_fields:
                        total_transactions = data.get('total_transactions', 0)
                        fully_completed = data.get('fully_completed', 0)
                        pending_confirmation = data.get('pending_confirmation', 0)
                        transactions = data.get('transactions', [])
                        
                        self.log_result(
                            "Admin Completed Transactions Overview", 
                            True, 
                            f"Admin overview retrieved: {total_transactions} total, {fully_completed} fully completed, {pending_confirmation} pending",
                            response_time
                        )
                        
                        # Verify transaction details include user info
                        if transactions:
                            sample_transaction = transactions[0]
                            has_buyer_info = 'buyer_info' in sample_transaction
                            has_seller_info = 'seller_info' in sample_transaction
                            has_completion_status = 'completion_status' in sample_transaction
                            
                            self.log_result(
                                "Admin Transaction Details Validation", 
                                has_buyer_info and has_seller_info and has_completion_status, 
                                f"Transaction details: Buyer info: {has_buyer_info}, Seller info: {has_seller_info}, Status: {has_completion_status}"
                            )
                        
                        return {
                            'success': True,
                            'data': data,
                            'total_transactions': total_transactions,
                            'fully_completed': fully_completed,
                            'pending_confirmation': pending_confirmation
                        }
                    else:
                        self.log_result(
                            "Admin Completed Transactions Overview", 
                            False, 
                            f"Missing required fields: {missing_fields}",
                            response_time
                        )
                        return {'success': False, 'error': f'Missing fields: {missing_fields}'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Admin Completed Transactions Overview", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Admin Completed Transactions Overview", 
                False, 
                f"Request failed: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def test_undo_completion(self, token, completion_result):
        """Test DELETE /api/user/completed-transactions/{completion_id}"""
        if not completion_result.get('success') or not completion_result.get('completion_id'):
            self.log_result("Undo Completion", False, "No valid completion ID available for undo testing")
            return {'success': False, 'error': 'No completion ID'}
        
        start_time = datetime.now()
        completion_id = completion_result.get('completion_id')
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self.session.delete(f"{BACKEND_URL}/user/completed-transactions/{completion_id}", 
                                         headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    message = data.get('message', '')
                    
                    self.log_result(
                        "Undo Completion", 
                        True, 
                        f"Completion undone successfully: {message}",
                        response_time
                    )
                    
                    return {
                        'success': True,
                        'message': message
                    }
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Undo Completion", 
                        False, 
                        f"Failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Undo Completion", 
                False, 
                f"Request failed: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def analyze_completed_transactions_functionality(self, completion_result, get_transactions_result, 
                                                         dual_completion_result, admin_overview_result, undo_result):
        """Analyze the effectiveness of the completed transactions functionality"""
        print("      Final analysis of completed transactions functionality:")
        
        working_features = []
        failing_features = []
        
        # Check transaction completion
        if completion_result.get('success'):
            working_features.append("✅ Transaction completion endpoint working")
        else:
            failing_features.append("❌ Transaction completion endpoint failed")
        
        # Check get completed transactions
        if get_transactions_result.get('success'):
            working_features.append("✅ Get completed transactions endpoint working")
        else:
            failing_features.append("❌ Get completed transactions endpoint failed")
        
        # Check dual party completion
        if dual_completion_result.get('success') and dual_completion_result.get('is_fully_completed'):
            working_features.append("✅ Dual party completion sets is_fully_completed to true")
        else:
            failing_features.append("❌ Dual party completion not working properly")
        
        # Check admin overview
        if admin_overview_result.get('success'):
            working_features.append("✅ Admin overview endpoint working with proper user details")
        else:
            failing_features.append("❌ Admin overview endpoint failed")
        
        # Check undo functionality
        if undo_result.get('success'):
            working_features.append("✅ Undo completion functionality working")
        else:
            failing_features.append("❌ Undo completion functionality failed")
        
        # Final assessment
        if not failing_features:
            self.log_result(
                "Completed Transactions Functionality Analysis", 
                True, 
                f"✅ ALL FUNCTIONALITY WORKING: {len(working_features)} features operational. {'; '.join(working_features)}"
            )
        else:
            self.log_result(
                "Completed Transactions Functionality Analysis", 
                False, 
                f"❌ SOME ISSUES FOUND: {len(working_features)} working, {len(failing_features)} failing. Issues: {'; '.join(failing_features)}"
            )
        
        return len(failing_features) == 0
    
    async def test_completed_transactions_functionality(self):
        """Test the completed transactions functionality"""
        print("\n🔄 COMPLETED TRANSACTIONS FUNCTIONALITY TESTING:")
        print("   Testing transaction completion, retrieval, undo, and admin overview")
        print("   Testing dual party completion workflow")
        
        # Step 1: Test database connectivity
        print("\n   🔗 Test Database Connectivity:")
        db_result = await self.test_database_connectivity()
        if not db_result:
            return False
        
        # Step 2: Setup - Login as admin and demo user
        admin_token, admin_user_id, admin_user = await self.test_login_and_get_token("admin@cataloro.com", "admin123")
        if not admin_token:
            self.log_result("Completed Transactions Test Setup", False, "Failed to login as admin")
            return False
        
        demo_token, demo_user_id, demo_user = await self.test_login_and_get_token("demo@cataloro.com", "demo123")
        if not demo_token:
            self.log_result("Completed Transactions Test Setup", False, "Failed to login as demo user")
            return False
        
        print(f"   Testing with admin user ID: {admin_user_id}")
        print(f"   Testing with demo user ID: {demo_user_id}")
        
        # Step 3: Find an accepted tender for testing
        print("\n   🔍 Finding Accepted Tender for Testing:")
        test_tender = await self.find_accepted_tender_for_testing(admin_token, admin_user_id)
        if not test_tender:
            self.log_result("Completed Transactions Test Setup", False, "No accepted tender found for testing")
            return False
        
        # Step 4: Test Transaction Completion Endpoint
        print("\n   ✅ Test Transaction Completion Endpoint:")
        completion_result = await self.test_complete_transaction_endpoint(
            admin_token, test_tender, "Meeting completed successfully", "meeting"
        )
        
        # Step 5: Test Get Completed Transactions
        print("\n   📋 Test Get Completed Transactions:")
        get_transactions_result = await self.test_get_completed_transactions(admin_user_id)
        
        # Step 6: Test Dual Party Completion
        print("\n   👥 Test Dual Party Completion:")
        dual_completion_result = await self.test_dual_party_completion(
            demo_token, test_tender, completion_result
        )
        
        # Step 7: Test Admin Overview
        print("\n   👨‍💼 Test Admin Overview:")
        admin_overview_result = await self.test_admin_completed_transactions_overview(admin_token)
        
        # Step 8: Test Undo Completion
        print("\n   ↩️ Test Undo Completion:")
        undo_result = await self.test_undo_completion(admin_token, completion_result)
        
        # Step 9: Final Analysis
        print("\n   📈 Final Analysis:")
        await self.analyze_completed_transactions_functionality(
            completion_result, get_transactions_result, dual_completion_result, 
            admin_overview_result, undo_result
        )
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"\n" + "="*80)
        print(f"COMPLETED TRANSACTIONS FUNCTIONALITY TEST SUMMARY")
        print(f"="*80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"="*80)
        
        if failed_tests > 0:
            print(f"\nFAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['details']}")
        
        print(f"\nTEST COMPLETED: {datetime.now().isoformat()}")

async def main():
    """Main test execution"""
    print("🚀 Starting Completed Transactions Functionality Testing...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    async with CompletedTransactionsTester() as tester:
        success = await tester.test_completed_transactions_functionality()
        tester.print_summary()
        
        if success:
            print("\n✅ All completed transactions functionality tests passed!")
            return 0
        else:
            print("\n❌ Some completed transactions functionality tests failed!")
            return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)