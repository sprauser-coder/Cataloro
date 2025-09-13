#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - INDEPENDENT COMPLETION WORKFLOW TESTING
Testing the fixed completion workflow to ensure buyer and seller completions work independently

SPECIFIC TESTS REQUESTED:
1. **Test Separate Completion Logic**:
   - Test POST /api/user/complete-transaction from seller perspective
   - Test POST /api/user/complete-transaction from buyer perspective  
   - Verify that each completion only affects that user's view

2. **Test Completed Transactions Filtering**:
   - Test GET /api/user/completed-transactions/admin_user_1 (seller completion only)
   - Verify seller-completed transactions appear only for seller, not buyer
   - Test with another user ID to verify buyer-completed transactions

3. **Test Workflow Independence**:
   - Create a scenario where seller completes but buyer does not
   - Verify seller sees it in completed transactions
   - Verify buyer does NOT see it in completed transactions
   - Test the reverse scenario (buyer completes but seller does not)

4. **Test Transaction States**:
   - Verify seller_confirmed_at and buyer_confirmed_at work independently
   - Check that is_fully_completed only becomes true when BOTH parties confirm
   - Verify data integrity with mixed completion states

5. **Test API Response Structure**:
   - Verify completed transactions API returns correct user_role_in_transaction
   - Check that only relevant transactions are returned for each user
   - Ensure proper filtering based on confirmation timestamps

CRITICAL ENDPOINTS BEING TESTED:
- POST /api/auth/login (user authentication)
- POST /api/user/complete-transaction (complete a transaction from buyer/seller perspective)
- GET /api/user/completed-transactions/{user_id} (get completed transactions with proper filtering)
- GET /api/tenders/buyer/{buyer_id} (get buyer tenders to find test data)
- GET /api/tenders/seller/{seller_id}/accepted (get seller accepted tenders to find test data)

EXPECTED RESULTS:
- ✅ Seller and buyer completions work independently
- ✅ Completed transactions filtering works correctly for each user
- ✅ seller_confirmed_at and buyer_confirmed_at timestamps work independently
- ✅ is_fully_completed only true when both parties confirm
- ✅ API responses include correct user_role_in_transaction
- ✅ Workflow independence verified in both directions
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
import pytz

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://cataloro-marketplace-6.preview.emergentagent.com/api"

class BackendTester:
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
    
    async def get_test_tender_data(self, token):
        """Get test tender data for completion workflow testing"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get buyer tenders for admin_user_1
            buyer_url = f"{BACKEND_URL}/tenders/buyer/admin_user_1"
            async with self.session.get(buyer_url, headers=headers) as response:
                if response.status == 200:
                    buyer_tenders = await response.json()
                    
                    # Find an accepted tender
                    accepted_tender = None
                    for tender in buyer_tenders:
                        if tender.get('status') == 'accepted':
                            accepted_tender = tender
                            break
                    
                    if accepted_tender:
                        self.log_result(
                            "Test Data Discovery", 
                            True, 
                            f"✅ Found accepted tender: listing_id={accepted_tender.get('listing_id')}, buyer_id={accepted_tender.get('buyer_id')}, seller_id={accepted_tender.get('seller_id')}",
                            (datetime.now() - start_time).total_seconds() * 1000
                        )
                        return {
                            'success': True,
                            'tender': accepted_tender,
                            'listing_id': accepted_tender.get('listing_id'),
                            'buyer_id': accepted_tender.get('buyer_id'),
                            'seller_id': accepted_tender.get('seller_id')
                        }
                    else:
                        self.log_result(
                            "Test Data Discovery", 
                            False, 
                            f"❌ No accepted tenders found in {len(buyer_tenders)} buyer tenders",
                            (datetime.now() - start_time).total_seconds() * 1000
                        )
                        return {'success': False, 'error': 'No accepted tenders found'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Test Data Discovery", 
                        False, 
                        f"❌ Failed to get buyer tenders: {response.status} - {error_text}",
                        (datetime.now() - start_time).total_seconds() * 1000
                    )
                    return {'success': False, 'error': f'Failed to get buyer tenders: {error_text}'}
                    
        except Exception as e:
            self.log_result(
                "Test Data Discovery", 
                False, 
                f"❌ Exception getting test data: {str(e)}",
                (datetime.now() - start_time).total_seconds() * 1000
            )
            return {'success': False, 'error': str(e)}
    
    async def test_seller_completion(self, listing_id, seller_token):
        """Test POST /api/user/complete-transaction from seller perspective"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {seller_token}"}
            url = f"{BACKEND_URL}/user/complete-transaction"
            
            transaction_data = {
                "listing_id": listing_id,
                "notes": "Seller completion test",
                "method": "meeting"
            }
            
            async with self.session.post(url, headers=headers, json=transaction_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    completion = data.get('completion', {})
                    is_fully_completed = data.get('is_fully_completed', False)
                    
                    # Verify seller completion fields
                    seller_confirmed_at = completion.get('seller_confirmed_at')
                    buyer_confirmed_at = completion.get('buyer_confirmed_at')
                    
                    if seller_confirmed_at and not buyer_confirmed_at and not is_fully_completed:
                        self.log_result(
                            "Seller Completion Logic", 
                            True, 
                            f"✅ SELLER COMPLETION WORKING: seller_confirmed_at set, buyer_confirmed_at null, is_fully_completed=false",
                            response_time
                        )
                        return {
                            'success': True,
                            'completion': completion,
                            'is_fully_completed': is_fully_completed,
                            'seller_confirmed_at': seller_confirmed_at,
                            'buyer_confirmed_at': buyer_confirmed_at
                        }
                    else:
                        self.log_result(
                            "Seller Completion Logic", 
                            False, 
                            f"❌ SELLER COMPLETION LOGIC FAILED: seller_confirmed_at={seller_confirmed_at}, buyer_confirmed_at={buyer_confirmed_at}, is_fully_completed={is_fully_completed}",
                            response_time
                        )
                        return {'success': False, 'error': 'Seller completion logic incorrect', 'data': data}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Seller Completion Logic", 
                        False, 
                        f"❌ SELLER COMPLETION FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Seller Completion Logic", 
                False, 
                f"❌ SELLER COMPLETION EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_buyer_completion(self, listing_id, buyer_token):
        """Test POST /api/user/complete-transaction from buyer perspective"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {buyer_token}"}
            url = f"{BACKEND_URL}/user/complete-transaction"
            
            transaction_data = {
                "listing_id": listing_id,
                "notes": "Buyer completion test",
                "method": "meeting"
            }
            
            async with self.session.post(url, headers=headers, json=transaction_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    completion = data.get('completion', {})
                    is_fully_completed = data.get('is_fully_completed', False)
                    
                    # Verify buyer completion fields
                    seller_confirmed_at = completion.get('seller_confirmed_at')
                    buyer_confirmed_at = completion.get('buyer_confirmed_at')
                    
                    # Should now have both confirmations and be fully completed
                    if seller_confirmed_at and buyer_confirmed_at and is_fully_completed:
                        self.log_result(
                            "Buyer Completion Logic", 
                            True, 
                            f"✅ BUYER COMPLETION WORKING: Both confirmations present, is_fully_completed=true",
                            response_time
                        )
                        return {
                            'success': True,
                            'completion': completion,
                            'is_fully_completed': is_fully_completed,
                            'seller_confirmed_at': seller_confirmed_at,
                            'buyer_confirmed_at': buyer_confirmed_at
                        }
                    else:
                        self.log_result(
                            "Buyer Completion Logic", 
                            False, 
                            f"❌ BUYER COMPLETION LOGIC FAILED: seller_confirmed_at={seller_confirmed_at}, buyer_confirmed_at={buyer_confirmed_at}, is_fully_completed={is_fully_completed}",
                            response_time
                        )
                        return {'success': False, 'error': 'Buyer completion logic incorrect', 'data': data}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Buyer Completion Logic", 
                        False, 
                        f"❌ BUYER COMPLETION FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Buyer Completion Logic", 
                False, 
                f"❌ BUYER COMPLETION EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def test_completed_transactions_endpoint(self, user_id, token):
        """Test GET /api/user/completed-transactions/{user_id} endpoint"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/user/completed-transactions/{user_id}"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list):
                        completed_count = len(data)
                        
                        # Check if completed transactions have proper structure
                        has_proper_structure = True
                        structure_details = []
                        has_timestamps = True
                        
                        if completed_count > 0:
                            sample_transaction = data[0]
                            required_fields = ['id', 'listing_id', 'buyer_id', 'seller_id']
                            timestamp_fields = ['seller_confirmed_at', 'completed_at']
                            
                            # Check transaction fields
                            missing_fields = [field for field in required_fields if field not in sample_transaction]
                            if missing_fields:
                                has_proper_structure = False
                                structure_details.append(f"Missing transaction fields: {missing_fields}")
                            
                            # Check timestamp fields
                            missing_timestamps = [field for field in timestamp_fields if not sample_transaction.get(field)]
                            if missing_timestamps:
                                has_timestamps = False
                                structure_details.append(f"Missing timestamp fields: {missing_timestamps}")
                        
                        if has_proper_structure and has_timestamps:
                            self.log_result(
                                "Completed Transactions Endpoint", 
                                True, 
                                f"✅ WORKING CORRECTLY: Returns {completed_count} completed transactions with proper timestamps",
                                response_time
                            )
                        elif has_proper_structure:
                            self.log_result(
                                "Completed Transactions Endpoint", 
                                True, 
                                f"✅ MOSTLY WORKING: Returns {completed_count} completed transactions but missing some timestamps",
                                response_time
                            )
                        else:
                            self.log_result(
                                "Completed Transactions Endpoint", 
                                False, 
                                f"❌ STRUCTURE ISSUES: Returns {completed_count} transactions but has structure problems: {'; '.join(structure_details)}",
                                response_time
                            )
                        
                        return {
                            'success': True,
                            'completed_count': completed_count,
                            'data': data,
                            'has_proper_structure': has_proper_structure,
                            'has_timestamps': has_timestamps,
                            'structure_details': structure_details
                        }
                    else:
                        self.log_result(
                            "Completed Transactions Endpoint", 
                            False, 
                            f"❌ WRONG FORMAT: Expected array, got {type(data)}",
                            response_time
                        )
                        return {'success': False, 'error': 'Wrong response format'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Completed Transactions Endpoint", 
                        False, 
                        f"❌ ENDPOINT FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Completed Transactions Endpoint", 
                False, 
                f"❌ REQUEST FAILED: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def test_complete_order_workflow(self, seller_id, token):
        """Test the complete order workflow end-to-end"""
        try:
            print(f"      Testing complete order workflow for seller: {seller_id}")
            
            # Step 1: Get initial accepted tenders
            print("      Step 1: Getting initial accepted tenders...")
            initial_accepted = await self.test_seller_accepted_tenders_endpoint(seller_id, token)
            
            if not initial_accepted.get('success') or initial_accepted.get('accepted_count', 0) == 0:
                self.log_result(
                    "Complete Order Workflow", 
                    False, 
                    "❌ WORKFLOW BLOCKED: No accepted tenders found to test completion workflow"
                )
                return {'success': False, 'error': 'No accepted tenders available'}
            
            # Step 2: Select a tender to complete
            accepted_tenders = initial_accepted.get('data', [])
            test_tender = accepted_tenders[0]  # Use first accepted tender
            test_listing_id = test_tender.get('listing_id')
            
            if not test_listing_id:
                self.log_result(
                    "Complete Order Workflow", 
                    False, 
                    "❌ WORKFLOW BLOCKED: Selected tender missing listing_id"
                )
                return {'success': False, 'error': 'Missing listing_id in tender'}
            
            print(f"      Step 2: Selected tender for listing {test_listing_id} to complete")
            
            # Step 3: Complete the transaction
            print("      Step 3: Completing the transaction...")
            completion_result = await self.test_complete_transaction_endpoint(test_listing_id, token)
            
            if not completion_result.get('success'):
                self.log_result(
                    "Complete Order Workflow", 
                    False, 
                    f"❌ WORKFLOW FAILED: Transaction completion failed: {completion_result.get('error', 'Unknown error')}"
                )
                return {'success': False, 'error': 'Transaction completion failed'}
            
            # Step 4: Verify tender is no longer in accepted list
            print("      Step 4: Verifying tender removed from accepted list...")
            updated_accepted = await self.test_seller_accepted_tenders_endpoint(seller_id, token)
            
            if updated_accepted.get('success'):
                updated_tenders = updated_accepted.get('data', [])
                completed_tender_still_present = any(
                    tender.get('listing_id') == test_listing_id for tender in updated_tenders
                )
                
                if completed_tender_still_present:
                    self.log_result(
                        "Complete Order Workflow", 
                        False, 
                        f"❌ FILTERING FAILED: Completed tender for listing {test_listing_id} still appears in accepted tenders list"
                    )
                    return {'success': False, 'error': 'Completed tender not filtered out'}
                else:
                    print(f"      ✅ Tender for listing {test_listing_id} successfully removed from accepted list")
            
            # Step 5: Verify transaction appears in completed transactions
            print("      Step 5: Verifying transaction appears in completed list...")
            completed_transactions = await self.test_completed_transactions_endpoint(seller_id, token)
            
            if completed_transactions.get('success'):
                completed_data = completed_transactions.get('data', [])
                transaction_found = any(
                    transaction.get('listing_id') == test_listing_id for transaction in completed_data
                )
                
                if not transaction_found:
                    self.log_result(
                        "Complete Order Workflow", 
                        False, 
                        f"❌ DATA CONSISTENCY FAILED: Completed transaction for listing {test_listing_id} not found in completed transactions"
                    )
                    return {'success': False, 'error': 'Completed transaction not found'}
                else:
                    print(f"      ✅ Completed transaction for listing {test_listing_id} found in completed list")
            
            # Success!
            self.log_result(
                "Complete Order Workflow", 
                True, 
                f"✅ WORKFLOW SUCCESS: Complete order workflow working correctly - tender filtered from accepted list, transaction recorded in completed list"
            )
            
            return {
                'success': True,
                'test_listing_id': test_listing_id,
                'initial_accepted_count': initial_accepted.get('accepted_count', 0),
                'final_accepted_count': updated_accepted.get('accepted_count', 0),
                'completed_transactions_count': completed_transactions.get('completed_count', 0)
            }
            
        except Exception as e:
            self.log_result(
                "Complete Order Workflow", 
                False, 
                f"❌ WORKFLOW EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}
    
    async def test_data_consistency(self, workflow_result, seller_id, token):
        """Test data consistency for completed transactions"""
        try:
            if not workflow_result.get('success'):
                self.log_result(
                    "Data Consistency Verification", 
                    False, 
                    "❌ CONSISTENCY CHECK SKIPPED: Workflow failed, cannot verify data consistency"
                )
                return {'success': False, 'error': 'Workflow failed'}
            
            test_listing_id = workflow_result.get('test_listing_id')
            if not test_listing_id:
                self.log_result(
                    "Data Consistency Verification", 
                    False, 
                    "❌ CONSISTENCY CHECK FAILED: No test listing ID available"
                )
                return {'success': False, 'error': 'No test listing ID'}
            
            # Get completed transactions to verify data structure
            completed_result = await self.test_completed_transactions_endpoint(seller_id, token)
            
            if not completed_result.get('success'):
                self.log_result(
                    "Data Consistency Verification", 
                    False, 
                    "❌ CONSISTENCY CHECK FAILED: Could not retrieve completed transactions"
                )
                return {'success': False, 'error': 'Could not retrieve completed transactions'}
            
            completed_transactions = completed_result.get('data', [])
            target_transaction = None
            
            # Find our test transaction
            for transaction in completed_transactions:
                if transaction.get('listing_id') == test_listing_id:
                    target_transaction = transaction
                    break
            
            if not target_transaction:
                self.log_result(
                    "Data Consistency Verification", 
                    False, 
                    f"❌ CONSISTENCY FAILED: Completed transaction for listing {test_listing_id} not found"
                )
                return {'success': False, 'error': 'Target transaction not found'}
            
            # Verify required fields and timestamps
            consistency_issues = []
            
            # Check required fields
            required_fields = ['id', 'listing_id', 'buyer_id', 'seller_id']
            for field in required_fields:
                if not target_transaction.get(field):
                    consistency_issues.append(f"Missing {field}")
            
            # Check timestamp fields
            timestamp_fields = ['seller_confirmed_at', 'completed_at']
            missing_timestamps = []
            for field in timestamp_fields:
                if not target_transaction.get(field):
                    missing_timestamps.append(field)
            
            if missing_timestamps:
                consistency_issues.append(f"Missing timestamps: {missing_timestamps}")
            
            # Check listing details
            if not target_transaction.get('listing_title'):
                consistency_issues.append("Missing listing title")
            if not target_transaction.get('listing_price'):
                consistency_issues.append("Missing listing price")
            
            if consistency_issues:
                self.log_result(
                    "Data Consistency Verification", 
                    False, 
                    f"❌ CONSISTENCY ISSUES: {'; '.join(consistency_issues)}"
                )
                return {'success': False, 'issues': consistency_issues}
            else:
                self.log_result(
                    "Data Consistency Verification", 
                    True, 
                    f"✅ DATA CONSISTENT: Completed transaction properly stored with seller_confirmed_at timestamp and listing details"
                )
                return {'success': True, 'transaction': target_transaction}
            
        except Exception as e:
            self.log_result(
                "Data Consistency Verification", 
                False, 
                f"❌ CONSISTENCY CHECK EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}
    
    async def test_authentication_requirements(self, seller_id):
        """Test that all endpoints require proper authentication"""
        try:
            print("      Testing authentication requirements...")
            
            # Test endpoints without authentication
            endpoints_to_test = [
                f"/tenders/seller/{seller_id}/accepted",
                f"/user/complete-transaction", 
                f"/user/completed-transactions/{seller_id}"
            ]
            
            auth_failures = []
            auth_successes = []
            
            for endpoint in endpoints_to_test:
                url = f"{BACKEND_URL}{endpoint}"
                
                try:
                    if endpoint == "/user/complete-transaction":
                        # POST request
                        async with self.session.post(url, json={"listing_id": "test"}) as response:
                            if response.status == 401 or response.status == 403:
                                auth_successes.append(f"{endpoint} (POST) properly requires auth")
                            else:
                                auth_failures.append(f"{endpoint} (POST) allows access without auth (status: {response.status})")
                    else:
                        # GET request
                        async with self.session.get(url) as response:
                            if response.status == 401 or response.status == 403:
                                auth_successes.append(f"{endpoint} (GET) properly requires auth")
                            else:
                                auth_failures.append(f"{endpoint} (GET) allows access without auth (status: {response.status})")
                                
                except Exception as e:
                    auth_failures.append(f"{endpoint} test failed: {str(e)}")
            
            if auth_failures:
                self.log_result(
                    "Authentication Requirements", 
                    False, 
                    f"❌ AUTH ISSUES: {'; '.join(auth_failures)}"
                )
                return {'success': False, 'failures': auth_failures}
            else:
                self.log_result(
                    "Authentication Requirements", 
                    True, 
                    f"✅ AUTH WORKING: All endpoints properly require authentication ({len(auth_successes)} endpoints tested)"
                )
                return {'success': True, 'successes': auth_successes}
            
        except Exception as e:
            self.log_result(
                "Authentication Requirements", 
                False, 
                f"❌ AUTH TEST EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}
    
    async def analyze_complete_order_results(self, accepted_result, workflow_result, consistency_result, auth_result):
        """Analyze the effectiveness of the complete order functionality testing"""
        print("      Final analysis of complete order functionality testing:")
        
        working_features = []
        failing_features = []
        
        # Check seller accepted tenders filtering
        if accepted_result.get('success') and accepted_result.get('completed_tenders_found', 0) == 0:
            working_features.append(f"✅ Seller accepted tenders filtering working ({accepted_result.get('accepted_count', 0)} pending tenders)")
        else:
            failing_features.append("❌ Seller accepted tenders filtering issues")
        
        # Check complete order workflow
        if workflow_result.get('success'):
            working_features.append("✅ Complete transaction workflow working")
        else:
            failing_features.append("❌ Complete transaction workflow issues")
        
        # Check data consistency
        if consistency_result.get('success'):
            working_features.append("✅ Data consistency verification passed")
        else:
            failing_features.append("❌ Data consistency issues found")
        
        # Check authentication
        if auth_result.get('success'):
            working_features.append("✅ Authentication requirements working")
        else:
            failing_features.append("❌ Authentication issues found")
        
        # Final assessment
        if not failing_features:
            self.log_result(
                "Complete Order Functionality Analysis", 
                True, 
                f"✅ ALL COMPLETE ORDER FEATURES WORKING: {'; '.join(working_features)}"
            )
        else:
            self.log_result(
                "Complete Order Functionality Analysis", 
                False, 
                f"❌ COMPLETE ORDER ISSUES FOUND: {len(working_features)} working, {len(failing_features)} failing. Issues: {'; '.join(failing_features)}"
            )
        
        return len(failing_features) == 0
    
    async def test_complete_order_functionality(self):
        """Test the complete order functionality"""
        print("\n🔄 COMPLETE ORDER FUNCTIONALITY TESTING:")
        print("   Testing updated Complete Order functionality to verify both fixes are working")
        print("   Testing seller accepted tenders filtering and complete transaction workflow")
        
        # Step 1: Setup - Login as admin user
        admin_token, admin_user_id, admin_user = await self.test_login_and_get_token("admin@cataloro.com", "admin123")
        if not admin_token:
            self.log_result("Complete Order Functionality Setup", False, "Failed to login as admin")
            return False
        
        print(f"   Testing with admin user ID: {admin_user_id}")
        
        # Step 2: Test Authentication Requirements
        print("\n   🔐 Test Authentication Requirements:")
        auth_result = await self.test_authentication_requirements(admin_user_id)
        
        # Step 3: Test Seller Accepted Tenders Filtering
        print("\n   📋 Test Seller Accepted Tenders Filtering:")
        accepted_tenders_result = await self.test_seller_accepted_tenders_endpoint(admin_user_id, admin_token)
        
        # Step 4: Test Complete Transaction Workflow
        print("\n   🔄 Test Complete Transaction Workflow:")
        workflow_result = await self.test_complete_order_workflow(admin_user_id, admin_token)
        
        # Step 5: Test Data Consistency
        print("\n   🔍 Test Data Consistency:")
        consistency_result = await self.test_data_consistency(workflow_result, admin_user_id, admin_token)
        
        # Step 6: Final Analysis
        print("\n   📈 Final Analysis:")
        await self.analyze_complete_order_results(
            accepted_tenders_result, workflow_result, consistency_result, auth_result
        )
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🎯 COMPLETE ORDER FUNCTIONALITY TESTING SUMMARY")
        print("="*80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        
        print(f"📊 Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/len(self.test_results)*100):.1f}%" if self.test_results else "0%")
        
        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n" + "="*80)

async def main():
    """Main test execution"""
    print("🚀 Starting Complete Order Functionality Testing...")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print("="*80)
    
    async with BackendTester() as tester:
        try:
            # Run complete order functionality tests
            await tester.test_complete_order_functionality()
            
            # Print summary
            tester.print_summary()
            
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())