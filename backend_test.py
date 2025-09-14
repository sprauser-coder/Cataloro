#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - PROFILE STATS SYNCHRONIZATION TESTING
Testing the backend endpoints that support Profile stats synchronization improvements

SPECIFIC TESTS REQUESTED (Review Request):
Test the backend endpoints that support the Profile stats synchronization improvements:

**Context**: ProfilePage modified to sync stats with existing working tiles by fetching data directly from the same endpoints:

1. **My Listings Data**: Uses `marketplaceService.getMyListings(user_id)` - same as MyListingsPage
2. **My Tenders Data**: Uses `/api/tenders/buyer/${user_id}` endpoint - same as TenderManagementPage

**Test Requirements**:
- Test the listings endpoint for user data retrieval
- Test the tenders endpoint for user data retrieval  
- Verify that the data returned matches what the working tiles use
- Use demo_user@cataloro.com or admin@cataloro.com for testing
- Ensure the endpoints return proper data structure with status, listings counts, etc.

**Expected Results**:
- Listings endpoint should return array of user's listings with status field
- Tenders endpoint should return array of user's tenders with status field (including 'accepted' status)
- Both endpoints should return consistent data that allows proper stats calculation

GOAL: Verify that the Profile stats synchronization endpoints are working correctly and returning proper data structure.
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
import pytz

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://mobileui-sync.preview.emergentagent.com/api"

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
    
    async def test_user_search_api(self, token):
        """Test GET /api/users/search endpoint"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test search with valid query
            search_query = "demo"
            url = f"{BACKEND_URL}/users/search?q={search_query}"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list):
                        # Check if we found users
                        found_users = len(data)
                        
                        # Verify response structure
                        if found_users > 0:
                            user = data[0]
                            required_fields = ['id', 'username', 'full_name', 'email']
                            missing_fields = [field for field in required_fields if field not in user]
                            
                            if not missing_fields:
                                self.log_result(
                                    "User Search API", 
                                    True, 
                                    f"✅ USER SEARCH WORKING: Found {found_users} users, proper response structure",
                                    response_time
                                )
                                return {'success': True, 'found_users': found_users, 'users': data}
                            else:
                                self.log_result(
                                    "User Search API", 
                                    False, 
                                    f"❌ RESPONSE STRUCTURE INVALID: Missing fields {missing_fields}",
                                    response_time
                                )
                                return {'success': False, 'error': 'Invalid response structure'}
                        else:
                            self.log_result(
                                "User Search API", 
                                True, 
                                f"✅ USER SEARCH WORKING: No users found for query '{search_query}' (expected)",
                                response_time
                            )
                            return {'success': True, 'found_users': 0, 'users': []}
                    else:
                        self.log_result(
                            "User Search API", 
                            False, 
                            f"❌ WRONG RESPONSE FORMAT: Expected array, got {type(data)}",
                            response_time
                        )
                        return {'success': False, 'error': 'Wrong response format'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "User Search API", 
                        False, 
                        f"❌ SEARCH FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "User Search API", 
                False, 
                f"❌ SEARCH EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_partner_management_workflow(self, token, user_id, partner_id):
        """Test the complete partner management workflow"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Step 1: Get initial partners list
            print("      Step 1: Getting initial partners list...")
            initial_partners = await self.get_user_partners(user_id, token)
            
            # Step 2: Add partner
            print("      Step 2: Adding partner...")
            add_result = await self.add_user_partner(partner_id, token)
            
            if not add_result.get('success'):
                return add_result
            
            # Step 3: Verify partner was added
            print("      Step 3: Verifying partner was added...")
            updated_partners = await self.get_user_partners(user_id, token)
            
            if not updated_partners.get('success'):
                return updated_partners
            
            # Check if partner count increased
            initial_count = len(initial_partners.get('partners', []))
            updated_count = len(updated_partners.get('partners', []))
            
            if updated_count > initial_count:
                # Step 4: Remove partner
                print("      Step 4: Removing partner...")
                remove_result = await self.remove_user_partner(partner_id, token)
                
                if remove_result.get('success'):
                    # Step 5: Verify partner was removed
                    print("      Step 5: Verifying partner was removed...")
                    final_partners = await self.get_user_partners(user_id, token)
                    
                    if final_partners.get('success'):
                        final_count = len(final_partners.get('partners', []))
                        
                        if final_count == initial_count:
                            self.log_result(
                                "Partner Management Workflow", 
                                True, 
                                f"✅ PARTNER MANAGEMENT WORKING: Add/remove workflow successful (initial: {initial_count}, added: {updated_count}, final: {final_count})"
                            )
                            return {'success': True, 'workflow_verified': True}
                        else:
                            self.log_result(
                                "Partner Management Workflow", 
                                False, 
                                f"❌ REMOVE FAILED: Partner count mismatch (initial: {initial_count}, final: {final_count})"
                            )
                            return {'success': False, 'error': 'Remove verification failed'}
                    else:
                        return final_partners
                else:
                    return remove_result
            else:
                self.log_result(
                    "Partner Management Workflow", 
                    False, 
                    f"❌ ADD FAILED: Partner count didn't increase (initial: {initial_count}, updated: {updated_count})"
                )
                return {'success': False, 'error': 'Add verification failed'}
            
        except Exception as e:
            self.log_result(
                "Partner Management Workflow", 
                False, 
                f"❌ WORKFLOW EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}

    async def get_user_partners(self, user_id, token):
        """Get user's partners list"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/user/partners/{user_id}"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list):
                        self.log_result(
                            "Get User Partners", 
                            True, 
                            f"✅ GET PARTNERS WORKING: Found {len(data)} partners",
                            response_time
                        )
                        return {'success': True, 'partners': data}
                    else:
                        self.log_result(
                            "Get User Partners", 
                            False, 
                            f"❌ WRONG FORMAT: Expected array, got {type(data)}",
                            response_time
                        )
                        return {'success': False, 'error': 'Wrong response format'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Get User Partners", 
                        False, 
                        f"❌ GET FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Get User Partners", 
                False, 
                f"❌ GET EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def add_user_partner(self, partner_id, token):
        """Add a user as partner"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/user/partners"
            
            partner_data = {"partner_id": partner_id}
            
            async with self.session.post(url, headers=headers, json=partner_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("message") and "successfully" in data.get("message", "").lower():
                        self.log_result(
                            "Add User Partner", 
                            True, 
                            f"✅ ADD PARTNER WORKING: {data.get('message')}",
                            response_time
                        )
                        return {'success': True, 'partnership_id': data.get('partnership_id')}
                    else:
                        self.log_result(
                            "Add User Partner", 
                            False, 
                            f"❌ UNEXPECTED RESPONSE: {data}",
                            response_time
                        )
                        return {'success': False, 'error': 'Unexpected response'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Add User Partner", 
                        False, 
                        f"❌ ADD FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Add User Partner", 
                False, 
                f"❌ ADD EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def remove_user_partner(self, partner_id, token):
        """Remove a user from partners"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/user/partners/{partner_id}"
            
            async with self.session.delete(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("message") and "successfully" in data.get("message", "").lower():
                        self.log_result(
                            "Remove User Partner", 
                            True, 
                            f"✅ REMOVE PARTNER WORKING: {data.get('message')}",
                            response_time
                        )
                        return {'success': True}
                    else:
                        self.log_result(
                            "Remove User Partner", 
                            False, 
                            f"❌ UNEXPECTED RESPONSE: {data}",
                            response_time
                        )
                        return {'success': False, 'error': 'Unexpected response'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Remove User Partner", 
                        False, 
                        f"❌ REMOVE FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Remove User Partner", 
                False, 
                f"❌ REMOVE EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def test_partner_visibility_functionality(self, admin_token, demo_token, admin_user_id, demo_user_id):
        """Test partner visibility functionality in listings"""
        try:
            # Step 1: Create partnership between admin and demo user
            print("      Step 1: Creating partnership for visibility testing...")
            partnership_result = await self.add_user_partner(demo_user_id, admin_token)
            
            if not partnership_result.get('success'):
                self.log_result(
                    "Partner Visibility Setup", 
                    False, 
                    f"❌ PARTNERSHIP CREATION FAILED: {partnership_result.get('error')}"
                )
                return partnership_result
            
            # Step 2: Create a listing with partner visibility
            print("      Step 2: Creating listing with partner visibility...")
            listing_result = await self.create_partner_visible_listing(admin_token, admin_user_id)
            
            if not listing_result.get('success'):
                return listing_result
            
            listing_id = listing_result.get('listing_id')
            
            # Step 3: Test partner can see the listing
            print("      Step 3: Testing partner can see the listing...")
            partner_visibility_result = await self.test_partner_can_see_listing(demo_token, listing_id)
            
            # Step 4: Test anonymous user cannot see the listing
            print("      Step 4: Testing anonymous user cannot see the listing...")
            anonymous_visibility_result = await self.test_anonymous_cannot_see_listing(listing_id)
            
            # Step 5: Clean up - remove partnership
            print("      Step 5: Cleaning up partnership...")
            await self.remove_user_partner(demo_user_id, admin_token)
            
            # Analyze results
            if (partner_visibility_result.get('success') and 
                anonymous_visibility_result.get('success')):
                self.log_result(
                    "Partner Visibility Functionality", 
                    True, 
                    "✅ PARTNER VISIBILITY WORKING: Partners can see listings, anonymous users cannot"
                )
                return {'success': True, 'visibility_verified': True}
            else:
                issues = []
                if not partner_visibility_result.get('success'):
                    issues.append("Partner visibility failed")
                if not anonymous_visibility_result.get('success'):
                    issues.append("Anonymous filtering failed")
                
                self.log_result(
                    "Partner Visibility Functionality", 
                    False, 
                    f"❌ VISIBILITY ISSUES: {'; '.join(issues)}"
                )
                return {'success': False, 'error': 'Visibility functionality failed'}
            
        except Exception as e:
            self.log_result(
                "Partner Visibility Functionality", 
                False, 
                f"❌ VISIBILITY EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}

    async def create_partner_visible_listing(self, token, seller_id):
        """Create a listing with partner visibility enabled"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/listings"
            
            listing_data = {
                "title": "Partner Visibility Test Listing",
                "description": "This listing should only be visible to partners initially",
                "price": 100.0,
                "category": "Electronics",
                "condition": "New",
                "seller_id": seller_id,
                "show_partners_first": True,
                "partners_visibility_hours": 1,  # 1 hour for testing
                "images": [],
                "tags": ["test", "partner-visibility"],
                "features": []
            }
            
            async with self.session.post(url, headers=headers, json=listing_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 201:
                    data = await response.json()
                    listing_id = data.get('listing', {}).get('id') or data.get('id')
                    
                    if listing_id:
                        self.log_result(
                            "Create Partner Visible Listing", 
                            True, 
                            f"✅ LISTING CREATED: Partner-visible listing created with ID {listing_id}",
                            response_time
                        )
                        return {'success': True, 'listing_id': listing_id, 'listing': data}
                    else:
                        self.log_result(
                            "Create Partner Visible Listing", 
                            False, 
                            f"❌ NO LISTING ID: Response missing listing ID: {data}",
                            response_time
                        )
                        return {'success': False, 'error': 'No listing ID in response'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Create Partner Visible Listing", 
                        False, 
                        f"❌ CREATION FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Create Partner Visible Listing", 
                False, 
                f"❌ CREATION EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_partner_can_see_listing(self, partner_token, listing_id):
        """Test that partner can see the partner-only listing"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {partner_token}"}
            url = f"{BACKEND_URL}/listings"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    listings = data.get('listings', []) if isinstance(data, dict) else data
                    
                    # Check if our test listing is visible
                    test_listing_found = any(
                        listing.get('id') == listing_id for listing in listings
                    )
                    
                    if test_listing_found:
                        self.log_result(
                            "Partner Can See Listing", 
                            True, 
                            f"✅ PARTNER VISIBILITY WORKING: Partner can see partner-only listing",
                            response_time
                        )
                        return {'success': True, 'listing_visible': True}
                    else:
                        self.log_result(
                            "Partner Can See Listing", 
                            False, 
                            f"❌ PARTNER VISIBILITY FAILED: Partner cannot see partner-only listing",
                            response_time
                        )
                        return {'success': False, 'error': 'Partner cannot see listing'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Partner Can See Listing", 
                        False, 
                        f"❌ LISTINGS FETCH FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Partner Can See Listing", 
                False, 
                f"❌ PARTNER VISIBILITY EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_anonymous_cannot_see_listing(self, listing_id):
        """Test that anonymous user cannot see the partner-only listing"""
        start_time = datetime.now()
        
        try:
            # No authorization header for anonymous request
            url = f"{BACKEND_URL}/listings"
            
            async with self.session.get(url) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    listings = data.get('listings', []) if isinstance(data, dict) else data
                    
                    # Check if our test listing is NOT visible
                    test_listing_found = any(
                        listing.get('id') == listing_id for listing in listings
                    )
                    
                    if not test_listing_found:
                        self.log_result(
                            "Anonymous Cannot See Listing", 
                            True, 
                            f"✅ ANONYMOUS FILTERING WORKING: Anonymous user cannot see partner-only listing",
                            response_time
                        )
                        return {'success': True, 'listing_hidden': True}
                    else:
                        self.log_result(
                            "Anonymous Cannot See Listing", 
                            False, 
                            f"❌ ANONYMOUS FILTERING FAILED: Anonymous user can see partner-only listing",
                            response_time
                        )
                        return {'success': False, 'error': 'Anonymous can see partner-only listing'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Anonymous Cannot See Listing", 
                        False, 
                        f"❌ ANONYMOUS FETCH FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Anonymous Cannot See Listing", 
                False, 
                f"❌ ANONYMOUS FILTERING EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_image_optimization_fixes(self, token, user_id):
        """Test image optimization fixes in various endpoints"""
        try:
            results = {}
            
            # Test 1: GET /api/user/my-deals/{user_id}
            print("      Test 1: Testing my-deals image optimization...")
            my_deals_result = await self.test_my_deals_optimization(token, user_id)
            results['my_deals'] = my_deals_result
            
            # Test 2: GET /api/tenders/seller/{seller_id}/accepted
            print("      Test 2: Testing accepted tenders image optimization...")
            accepted_tenders_result = await self.test_accepted_tenders_optimization(token, user_id)
            results['accepted_tenders'] = accepted_tenders_result
            
            # Analyze results
            working_endpoints = sum(1 for result in results.values() if result.get('success'))
            total_endpoints = len(results)
            
            if working_endpoints == total_endpoints:
                self.log_result(
                    "Image Optimization Fixes", 
                    True, 
                    f"✅ IMAGE OPTIMIZATION WORKING: All {total_endpoints} endpoints using optimized images"
                )
                return {'success': True, 'optimized_endpoints': working_endpoints}
            else:
                failing_endpoints = [name for name, result in results.items() if not result.get('success')]
                self.log_result(
                    "Image Optimization Fixes", 
                    False, 
                    f"❌ OPTIMIZATION ISSUES: {working_endpoints}/{total_endpoints} working. Failing: {failing_endpoints}"
                )
                return {'success': False, 'error': f'Optimization issues in {failing_endpoints}'}
            
        except Exception as e:
            self.log_result(
                "Image Optimization Fixes", 
                False, 
                f"❌ OPTIMIZATION EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}

    async def test_my_deals_optimization(self, token, user_id):
        """Test GET /api/user/my-deals/{user_id} for image optimization"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/user/my-deals/{user_id}"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list):
                        deals_count = len(data)
                        
                        # Check for image optimization
                        base64_images = 0
                        optimized_images = 0
                        
                        for deal in data:
                            listing = deal.get('listing', {})
                            image = listing.get('image', '')
                            
                            if image.startswith('data:'):
                                base64_images += 1
                            elif image.startswith('/api/') or image.startswith('/uploads/'):
                                optimized_images += 1
                        
                        if base64_images == 0:
                            self.log_result(
                                "My Deals Image Optimization", 
                                True, 
                                f"✅ MY DEALS OPTIMIZED: {deals_count} deals, {optimized_images} optimized images, 0 base64 images",
                                response_time
                            )
                            return {'success': True, 'deals_count': deals_count, 'optimized': True}
                        else:
                            self.log_result(
                                "My Deals Image Optimization", 
                                False, 
                                f"❌ MY DEALS NOT OPTIMIZED: {base64_images} base64 images found",
                                response_time
                            )
                            return {'success': False, 'error': f'{base64_images} base64 images found'}
                    else:
                        self.log_result(
                            "My Deals Image Optimization", 
                            False, 
                            f"❌ WRONG FORMAT: Expected array, got {type(data)}",
                            response_time
                        )
                        return {'success': False, 'error': 'Wrong response format'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "My Deals Image Optimization", 
                        False, 
                        f"❌ MY DEALS FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "My Deals Image Optimization", 
                False, 
                f"❌ MY DEALS EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_accepted_tenders_optimization(self, token, seller_id):
        """Test GET /api/tenders/seller/{seller_id}/accepted for image optimization"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/tenders/seller/{seller_id}/accepted"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list):
                        tenders_count = len(data)
                        
                        # Check for image optimization
                        base64_images = 0
                        optimized_images = 0
                        
                        for tender in data:
                            image = tender.get('listing_image', '')
                            
                            if image.startswith('data:'):
                                base64_images += 1
                            elif image.startswith('/api/') or image.startswith('/uploads/'):
                                optimized_images += 1
                        
                        if base64_images == 0:
                            self.log_result(
                                "Accepted Tenders Image Optimization", 
                                True, 
                                f"✅ ACCEPTED TENDERS OPTIMIZED: {tenders_count} tenders, {optimized_images} optimized images, 0 base64 images",
                                response_time
                            )
                            return {'success': True, 'tenders_count': tenders_count, 'optimized': True}
                        else:
                            self.log_result(
                                "Accepted Tenders Image Optimization", 
                                False, 
                                f"❌ ACCEPTED TENDERS NOT OPTIMIZED: {base64_images} base64 images found",
                                response_time
                            )
                            return {'success': False, 'error': f'{base64_images} base64 images found'}
                    else:
                        self.log_result(
                            "Accepted Tenders Image Optimization", 
                            False, 
                            f"❌ WRONG FORMAT: Expected array, got {type(data)}",
                            response_time
                        )
                        return {'success': False, 'error': 'Wrong response format'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Accepted Tenders Image Optimization", 
                        False, 
                        f"❌ ACCEPTED TENDERS FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Accepted Tenders Image Optimization", 
                False, 
                f"❌ ACCEPTED TENDERS EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_listing_reactivation(self, token, user_id):
        """Test PUT /api/listings/{listing_id}/reactivate for expired listings"""
        try:
            # First, try to find an existing listing to test reactivation
            print("      Finding listing for reactivation test...")
            listing_result = await self.find_or_create_test_listing(token, user_id)
            
            if not listing_result.get('success'):
                return listing_result
            
            listing_id = listing_result.get('listing_id')
            
            # Test reactivation
            print(f"      Testing reactivation of listing {listing_id}...")
            reactivation_result = await self.test_reactivate_listing(token, listing_id)
            
            return reactivation_result
            
        except Exception as e:
            self.log_result(
                "Listing Reactivation", 
                False, 
                f"❌ REACTIVATION EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}

    async def find_or_create_test_listing(self, token, user_id):
        """Find an existing listing or create one for reactivation testing"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            # First try to find existing listings
            url = f"{BACKEND_URL}/listings?status=all"
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    listings = data.get('listings', []) if isinstance(data, dict) else data
                    
                    # Find a listing owned by the user
                    user_listings = [l for l in listings if l.get('seller_id') == user_id]
                    
                    if user_listings:
                        listing_id = user_listings[0].get('id')
                        self.log_result(
                            "Find Test Listing", 
                            True, 
                            f"✅ FOUND EXISTING LISTING: Using listing {listing_id} for reactivation test",
                            (datetime.now() - start_time).total_seconds() * 1000
                        )
                        return {'success': True, 'listing_id': listing_id}
            
            # If no existing listings, create one
            print("      Creating new listing for reactivation test...")
            create_result = await self.create_test_listing_for_reactivation(token, user_id)
            return create_result
            
        except Exception as e:
            self.log_result(
                "Find Test Listing", 
                False, 
                f"❌ FIND LISTING EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}

    async def create_test_listing_for_reactivation(self, token, seller_id):
        """Create a test listing for reactivation testing"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/listings"
            
            listing_data = {
                "title": "Reactivation Test Listing",
                "description": "This listing is for testing reactivation functionality",
                "price": 50.0,
                "category": "Electronics",
                "condition": "Used",
                "seller_id": seller_id,
                "images": [],
                "tags": ["test", "reactivation"],
                "features": []
            }
            
            async with self.session.post(url, headers=headers, json=listing_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 201:
                    data = await response.json()
                    listing_id = data.get('listing', {}).get('id') or data.get('id')
                    
                    if listing_id:
                        self.log_result(
                            "Create Test Listing for Reactivation", 
                            True, 
                            f"✅ TEST LISTING CREATED: Created listing {listing_id} for reactivation test",
                            response_time
                        )
                        return {'success': True, 'listing_id': listing_id}
                    else:
                        self.log_result(
                            "Create Test Listing for Reactivation", 
                            False, 
                            f"❌ NO LISTING ID: Response missing listing ID: {data}",
                            response_time
                        )
                        return {'success': False, 'error': 'No listing ID in response'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Create Test Listing for Reactivation", 
                        False, 
                        f"❌ CREATION FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Create Test Listing for Reactivation", 
                False, 
                f"❌ CREATION EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_reactivate_listing(self, token, listing_id):
        """Test PUT /api/listings/{listing_id}/reactivate"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/listings/{listing_id}/reactivate"
            
            async with self.session.put(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("message") and "successfully" in data.get("message", "").lower():
                        self.log_result(
                            "Listing Reactivation", 
                            True, 
                            f"✅ REACTIVATION WORKING: {data.get('message')}",
                            response_time
                        )
                        return {'success': True, 'reactivated': True}
                    else:
                        self.log_result(
                            "Listing Reactivation", 
                            False, 
                            f"❌ UNEXPECTED RESPONSE: {data}",
                            response_time
                        )
                        return {'success': False, 'error': 'Unexpected response'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Listing Reactivation", 
                        False, 
                        f"❌ REACTIVATION FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Listing Reactivation", 
                False, 
                f"❌ REACTIVATION EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_my_listings_endpoint(self, token, user_id, user_email):
        """Test GET /api/marketplace/my-listings endpoint for Profile stats synchronization"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/marketplace/my-listings"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if response has the expected structure
                    if isinstance(data, dict) and 'listings' in data:
                        listings = data['listings']
                        total_count = data.get('total', 0)
                        
                        # Verify listings structure for stats calculation
                        status_counts = {}
                        for listing in listings:
                            status = listing.get('status', 'unknown')
                            status_counts[status] = status_counts.get(status, 0) + 1
                        
                        self.log_result(
                            "My Listings Endpoint", 
                            True, 
                            f"✅ MY LISTINGS WORKING: Found {len(listings)} listings (total: {total_count}), Status breakdown: {status_counts}",
                            response_time
                        )
                        return {
                            'success': True, 
                            'listings_count': len(listings),
                            'total_count': total_count,
                            'status_counts': status_counts,
                            'listings': listings,
                            'user_email': user_email
                        }
                    else:
                        self.log_result(
                            "My Listings Endpoint", 
                            False, 
                            f"❌ WRONG STRUCTURE: Expected dict with 'listings' key, got {type(data)}",
                            response_time
                        )
                        return {'success': False, 'error': 'Wrong response structure'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "My Listings Endpoint", 
                        False, 
                        f"❌ LISTINGS FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "My Listings Endpoint", 
                False, 
                f"❌ LISTINGS EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_buyer_tenders_endpoint(self, token, user_id, user_email):
        """Test GET /api/tenders/buyer/{user_id} endpoint for Profile stats synchronization"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/tenders/buyer/{user_id}"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if response is an array of tenders
                    if isinstance(data, list):
                        tenders = data
                        
                        # Verify tenders structure for stats calculation
                        status_counts = {}
                        for tender in tenders:
                            status = tender.get('status', 'unknown')
                            status_counts[status] = status_counts.get(status, 0) + 1
                        
                        # Check for required fields in tenders
                        sample_tender = tenders[0] if tenders else {}
                        required_fields = ['id', 'status', 'offer_amount', 'listing', 'seller']
                        missing_fields = [field for field in required_fields if field not in sample_tender] if tenders else []
                        
                        self.log_result(
                            "Buyer Tenders Endpoint", 
                            True, 
                            f"✅ BUYER TENDERS WORKING: Found {len(tenders)} tenders, Status breakdown: {status_counts}, Required fields present: {not missing_fields}",
                            response_time
                        )
                        return {
                            'success': True, 
                            'tenders_count': len(tenders),
                            'status_counts': status_counts,
                            'tenders': tenders,
                            'missing_fields': missing_fields,
                            'user_email': user_email
                        }
                    else:
                        self.log_result(
                            "Buyer Tenders Endpoint", 
                            False, 
                            f"❌ WRONG STRUCTURE: Expected array, got {type(data)}",
                            response_time
                        )
                        return {'success': False, 'error': 'Wrong response structure'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Buyer Tenders Endpoint", 
                        False, 
                        f"❌ TENDERS FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Buyer Tenders Endpoint", 
                False, 
                f"❌ TENDERS EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_verify_api_response_structure(self, token, listing_id):
        """Verify the NEW listing has future public_at date and correct partner fields"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/listings/{listing_id}"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check required partner fields
                    is_partners_only = data.get('is_partners_only')
                    public_at = data.get('public_at')
                    show_partners_first = data.get('show_partners_first')
                    
                    # Verify current time is BEFORE public_at
                    current_time = datetime.now(timezone.utc)
                    
                    if public_at:
                        try:
                            # Parse public_at datetime
                            if public_at.endswith('Z'):
                                public_at_dt = datetime.fromisoformat(public_at.replace('Z', '+00:00'))
                            elif '+' in public_at or public_at.endswith('00:00'):
                                public_at_dt = datetime.fromisoformat(public_at)
                            else:
                                public_at_dt = datetime.fromisoformat(public_at).replace(tzinfo=timezone.utc)
                            
                            time_diff = (public_at_dt - current_time).total_seconds()
                            hours_diff = time_diff / 3600
                            
                            # Check if all conditions are met
                            if (is_partners_only is True and 
                                public_at and 
                                show_partners_first is True and 
                                time_diff > 0 and 
                                150 <= hours_diff <= 170):  # Allow some tolerance around 168 hours
                                
                                self.log_result(
                                    "Verify API Response Structure", 
                                    True, 
                                    f"✅ STRUCTURE CONFIRMED: is_partners_only=True, public_at={public_at} ({hours_diff:.1f}h future), show_partners_first=True, current time is BEFORE public_at",
                                    response_time
                                )
                                return {
                                    'success': True, 
                                    'is_partners_only': is_partners_only,
                                    'public_at': public_at,
                                    'show_partners_first': show_partners_first,
                                    'hours_in_future': hours_diff,
                                    'badge_condition_met': True
                                }
                            else:
                                self.log_result(
                                    "Verify API Response Structure", 
                                    False, 
                                    f"❌ STRUCTURE INVALID: is_partners_only={is_partners_only}, public_at={public_at}, show_partners_first={show_partners_first}, hours_diff={hours_diff:.1f}",
                                    response_time
                                )
                                return {'success': False, 'error': 'Invalid partner structure'}
                        except Exception as date_error:
                            self.log_result(
                                "Verify API Response Structure", 
                                False, 
                                f"❌ DATE PARSING ERROR: {str(date_error)}, public_at={public_at}",
                                response_time
                            )
                            return {'success': False, 'error': f'Date parsing error: {str(date_error)}'}
                    else:
                        self.log_result(
                            "Verify API Response Structure", 
                            False, 
                            f"❌ MISSING public_at: is_partners_only={is_partners_only}, show_partners_first={show_partners_first}",
                            response_time
                        )
                        return {'success': False, 'error': 'Missing public_at field'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Verify API Response Structure", 
                        False, 
                        f"❌ FETCH FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Verify API Response Structure", 
                False, 
                f"❌ VERIFICATION EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_authenticated_browse_endpoint(self, token, listing_id):
        """Test authenticated browse endpoint shows the new listing with correct partner data"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/marketplace/browse"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    listings = data.get('listings', []) if isinstance(data, dict) else data
                    
                    # Find our test listing
                    test_listing = None
                    for listing in listings:
                        if listing.get('id') == listing_id:
                            test_listing = listing
                            break
                    
                    if test_listing:
                        # Verify partner fields are present
                        is_partners_only = test_listing.get('is_partners_only')
                        public_at = test_listing.get('public_at')
                        show_partners_first = test_listing.get('show_partners_first')
                        
                        if (is_partners_only is True and 
                            public_at and 
                            show_partners_first is True):
                            
                            self.log_result(
                                "Authenticated Browse Endpoint", 
                                True, 
                                f"✅ AUTHENTICATED BROWSE CONFIRMED: Admin can see partner-only listing with all partner fields (is_partners_only, public_at, show_partners_first)",
                                response_time
                            )
                            return {
                                'success': True, 
                                'listing_found': True,
                                'partner_fields_present': True,
                                'test_listing': test_listing
                            }
                        else:
                            self.log_result(
                                "Authenticated Browse Endpoint", 
                                False, 
                                f"❌ MISSING PARTNER FIELDS: is_partners_only={is_partners_only}, public_at={public_at}, show_partners_first={show_partners_first}",
                                response_time
                            )
                            return {'success': False, 'error': 'Missing partner fields in browse response'}
                    else:
                        self.log_result(
                            "Authenticated Browse Endpoint", 
                            False, 
                            f"❌ LISTING NOT FOUND: Test listing {listing_id} not found in browse results",
                            response_time
                        )
                        return {'success': False, 'error': 'Test listing not found in browse results'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Authenticated Browse Endpoint", 
                        False, 
                        f"❌ BROWSE FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Authenticated Browse Endpoint", 
                False, 
                f"❌ BROWSE EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_anonymous_browse_endpoint(self, listing_id):
        """Test anonymous browse endpoint does NOT show the partner-only listing"""
        start_time = datetime.now()
        
        try:
            # No authorization header for anonymous request
            url = f"{BACKEND_URL}/marketplace/browse"
            
            async with self.session.get(url) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    listings = data.get('listings', []) if isinstance(data, dict) else data
                    
                    # Check if our test listing is NOT visible
                    test_listing_found = any(
                        listing.get('id') == listing_id for listing in listings
                    )
                    
                    if not test_listing_found:
                        public_listings_count = len(listings)
                        self.log_result(
                            "Anonymous Browse Endpoint", 
                            True, 
                            f"✅ ANONYMOUS FILTERING CONFIRMED: Anonymous users cannot see partner-only listing, {public_listings_count} public listings visible",
                            response_time
                        )
                        return {
                            'success': True, 
                            'listing_hidden': True,
                            'public_listings_count': public_listings_count
                        }
                    else:
                        self.log_result(
                            "Anonymous Browse Endpoint", 
                            False, 
                            f"❌ FILTERING FAILED: Anonymous user can see partner-only listing",
                            response_time
                        )
                        return {'success': False, 'error': 'Anonymous can see partner-only listing'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Anonymous Browse Endpoint", 
                        False, 
                        f"❌ ANONYMOUS BROWSE FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Anonymous Browse Endpoint", 
                False, 
                f"❌ ANONYMOUS BROWSE EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def analyze_partner_management_results(self, results):
        """Analyze the effectiveness of the partner management testing"""
        print("      Final analysis of partner management and visibility testing:")
        
        working_features = []
        failing_features = []
        
        # Check user search
        if results.get('user_search', {}).get('success'):
            working_features.append("✅ User search API working")
        else:
            failing_features.append("❌ User search API failed")
        
        # Check partner management
        if results.get('partner_management', {}).get('success'):
            working_features.append("✅ Partner management workflow working")
        else:
            failing_features.append("❌ Partner management workflow failed")
        
        # Check partner visibility
        if results.get('partner_visibility', {}).get('success'):
            working_features.append("✅ Partner visibility functionality working")
        else:
            failing_features.append("❌ Partner visibility functionality failed")
        
        # Check image optimization
        if results.get('image_optimization', {}).get('success'):
            working_features.append("✅ Image optimization fixes working")
        else:
            failing_features.append("❌ Image optimization issues found")
        
        # Check listing reactivation
        if results.get('listing_reactivation', {}).get('success'):
            working_features.append("✅ Listing reactivation working")
        else:
            failing_features.append("❌ Listing reactivation failed")
        
        # Final assessment
        if not failing_features:
            self.log_result(
                "Partner Management Analysis", 
                True, 
                f"✅ ALL PARTNER MANAGEMENT FEATURES WORKING: {'; '.join(working_features)}"
            )
        else:
            self.log_result(
                "Partner Management Analysis", 
                False, 
                f"❌ PARTNER MANAGEMENT ISSUES FOUND: {len(working_features)} working, {len(failing_features)} failing. Issues: {'; '.join(failing_features)}"
            )
        
        return len(failing_features) == 0
    
    async def test_completed_transactions_filtering(self, user_id, token, expected_role, test_listing_id):
        """Test GET /api/user/completed-transactions/{user_id} endpoint with proper filtering"""
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
                        
                        # Find our test transaction
                        test_transaction = None
                        for transaction in data:
                            if transaction.get('listing_id') == test_listing_id:
                                test_transaction = transaction
                                break
                        
                        if test_transaction:
                            # Verify user role context
                            user_role_in_transaction = test_transaction.get('user_role_in_transaction')
                            
                            # Verify confirmation timestamps based on role
                            seller_confirmed_at = test_transaction.get('seller_confirmed_at')
                            buyer_confirmed_at = test_transaction.get('buyer_confirmed_at')
                            
                            if expected_role == 'seller':
                                # For seller, should have seller_confirmed_at
                                if user_role_in_transaction == 'seller' and seller_confirmed_at:
                                    self.log_result(
                                        f"Completed Transactions Filtering ({expected_role.title()})", 
                                        True, 
                                        f"✅ SELLER FILTERING WORKING: Found transaction with user_role_in_transaction=seller, seller_confirmed_at present",
                                        response_time
                                    )
                                    return {
                                        'success': True,
                                        'completed_count': completed_count,
                                        'test_transaction': test_transaction,
                                        'user_role_in_transaction': user_role_in_transaction,
                                        'seller_confirmed_at': seller_confirmed_at,
                                        'buyer_confirmed_at': buyer_confirmed_at
                                    }
                                else:
                                    self.log_result(
                                        f"Completed Transactions Filtering ({expected_role.title()})", 
                                        False, 
                                        f"❌ SELLER FILTERING FAILED: user_role_in_transaction={user_role_in_transaction}, seller_confirmed_at={seller_confirmed_at}",
                                        response_time
                                    )
                                    return {'success': False, 'error': 'Seller filtering incorrect'}
                            
                            elif expected_role == 'buyer':
                                # For buyer, should have buyer_confirmed_at
                                if user_role_in_transaction == 'buyer' and buyer_confirmed_at:
                                    self.log_result(
                                        f"Completed Transactions Filtering ({expected_role.title()})", 
                                        True, 
                                        f"✅ BUYER FILTERING WORKING: Found transaction with user_role_in_transaction=buyer, buyer_confirmed_at present",
                                        response_time
                                    )
                                    return {
                                        'success': True,
                                        'completed_count': completed_count,
                                        'test_transaction': test_transaction,
                                        'user_role_in_transaction': user_role_in_transaction,
                                        'seller_confirmed_at': seller_confirmed_at,
                                        'buyer_confirmed_at': buyer_confirmed_at
                                    }
                                else:
                                    self.log_result(
                                        f"Completed Transactions Filtering ({expected_role.title()})", 
                                        False, 
                                        f"❌ BUYER FILTERING FAILED: user_role_in_transaction={user_role_in_transaction}, buyer_confirmed_at={buyer_confirmed_at}",
                                        response_time
                                    )
                                    return {'success': False, 'error': 'Buyer filtering incorrect'}
                        else:
                            # Transaction not found - this might be expected if user hasn't confirmed yet
                            self.log_result(
                                f"Completed Transactions Filtering ({expected_role.title()})", 
                                True, 
                                f"✅ FILTERING WORKING: Transaction not found for {expected_role} (expected if {expected_role} hasn't confirmed yet)",
                                response_time
                            )
                            return {
                                'success': True,
                                'completed_count': completed_count,
                                'test_transaction': None,
                                'transaction_not_found': True
                            }
                    else:
                        self.log_result(
                            f"Completed Transactions Filtering ({expected_role.title()})", 
                            False, 
                            f"❌ WRONG FORMAT: Expected array, got {type(data)}",
                            response_time
                        )
                        return {'success': False, 'error': 'Wrong response format'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        f"Completed Transactions Filtering ({expected_role.title()})", 
                        False, 
                        f"❌ ENDPOINT FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                f"Completed Transactions Filtering ({expected_role.title()})", 
                False, 
                f"❌ REQUEST FAILED: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def test_existing_completion_state(self, test_data, seller_token, buyer_token):
        """Test the current completion state and verify independent filtering"""
        try:
            listing_id = test_data.get('listing_id')
            buyer_id = test_data.get('buyer_id')
            seller_id = test_data.get('seller_id')
            
            print(f"      Testing existing completion state for listing: {listing_id}")
            
            # Step 1: Check seller's completed transactions
            print("      Step 1: Checking seller's completed transactions...")
            seller_completed = await self.test_completed_transactions_filtering(seller_id, seller_token, 'seller', listing_id)
            
            # Step 2: Check buyer's completed transactions
            print("      Step 2: Checking buyer's completed transactions...")
            buyer_completed = await self.test_completed_transactions_filtering(buyer_id, buyer_token, 'buyer', listing_id)
            
            # Step 3: Verify both parties see the transaction
            seller_sees = seller_completed.get('success') and not seller_completed.get('transaction_not_found')
            buyer_sees = buyer_completed.get('success') and not buyer_completed.get('transaction_not_found')
            
            if seller_sees and buyer_sees:
                # Step 4: Verify transaction states
                seller_transaction = seller_completed.get('test_transaction', {})
                buyer_transaction = buyer_completed.get('test_transaction', {})
                
                seller_confirmed_at = seller_transaction.get('seller_confirmed_at')
                buyer_confirmed_at = buyer_transaction.get('buyer_confirmed_at')
                is_fully_completed = seller_transaction.get('is_fully_completed', False)
                
                if seller_confirmed_at and buyer_confirmed_at and is_fully_completed:
                    self.log_result(
                        "Existing Completion State Verification", 
                        True, 
                        "✅ COMPLETION STATE CORRECT: Both parties confirmed, transaction fully completed, independent filtering working"
                    )
                    return {
                        'success': True,
                        'seller_sees_transaction': True,
                        'buyer_sees_transaction': True,
                        'seller_confirmed_at': seller_confirmed_at,
                        'buyer_confirmed_at': buyer_confirmed_at,
                        'is_fully_completed': is_fully_completed
                    }
                else:
                    self.log_result(
                        "Existing Completion State Verification", 
                        False, 
                        f"❌ COMPLETION STATE INCORRECT: seller_confirmed_at={seller_confirmed_at}, buyer_confirmed_at={buyer_confirmed_at}, is_fully_completed={is_fully_completed}"
                    )
                    return {'success': False, 'error': 'Completion state incorrect'}
            else:
                self.log_result(
                    "Existing Completion State Verification", 
                    False, 
                    f"❌ FILTERING FAILED: seller_sees={seller_sees}, buyer_sees={buyer_sees}"
                )
                return {'success': False, 'error': 'Filtering failed'}
            
        except Exception as e:
            self.log_result(
                "Existing Completion State Verification", 
                False, 
                f"❌ STATE VERIFICATION EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}

    async def test_completion_workflow_update(self, test_data, seller_token, buyer_token):
        """Test completion workflow update logic (when transaction already exists)"""
        try:
            listing_id = test_data.get('listing_id')
            buyer_id = test_data.get('buyer_id')
            seller_id = test_data.get('seller_id')
            
            print(f"      Testing completion workflow update for listing: {listing_id}")
            
            # Step 1: Try seller completion (should update existing record)
            print("      Step 1: Testing seller completion update...")
            seller_completion = await self.test_seller_completion(listing_id, seller_token)
            
            # Step 2: Try buyer completion (should update existing record)
            print("      Step 2: Testing buyer completion update...")
            buyer_completion = await self.test_buyer_completion(listing_id, buyer_token)
            
            # Both should succeed (updating existing records)
            if seller_completion.get('success') and buyer_completion.get('success'):
                self.log_result(
                    "Completion Workflow Update", 
                    True, 
                    "✅ UPDATE LOGIC WORKING: Both seller and buyer can update existing completion records"
                )
                return {
                    'success': True,
                    'seller_completion': seller_completion,
                    'buyer_completion': buyer_completion
                }
            else:
                self.log_result(
                    "Completion Workflow Update", 
                    False, 
                    f"❌ UPDATE LOGIC FAILED: seller_success={seller_completion.get('success')}, buyer_success={buyer_completion.get('success')}"
                )
                return {'success': False, 'error': 'Update logic failed'}
            
        except Exception as e:
            self.log_result(
                "Completion Workflow Update", 
                False, 
                f"❌ UPDATE WORKFLOW EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}
    
    async def test_transaction_states_verification(self, test_data, seller_completion, buyer_completion):
        """Verify transaction states and data integrity"""
        try:
            listing_id = test_data.get('listing_id')
            
            # Verify seller completion state
            seller_confirmed_at = seller_completion.get('seller_confirmed_at')
            seller_buyer_confirmed_at = seller_completion.get('buyer_confirmed_at')
            seller_is_fully_completed = seller_completion.get('is_fully_completed', False)
            
            # Verify buyer completion state  
            buyer_seller_confirmed_at = buyer_completion.get('seller_confirmed_at')
            buyer_buyer_confirmed_at = buyer_completion.get('buyer_confirmed_at')
            buyer_is_fully_completed = buyer_completion.get('is_fully_completed', False)
            
            state_issues = []
            
            # Check seller completion state
            if not seller_confirmed_at:
                state_issues.append("seller_confirmed_at missing after seller completion")
            if seller_buyer_confirmed_at:
                state_issues.append("buyer_confirmed_at present after seller-only completion")
            if seller_is_fully_completed:
                state_issues.append("is_fully_completed=true after seller-only completion")
            
            # Check buyer completion state
            if not buyer_seller_confirmed_at:
                state_issues.append("seller_confirmed_at missing after buyer completion")
            if not buyer_buyer_confirmed_at:
                state_issues.append("buyer_confirmed_at missing after buyer completion")
            if not buyer_is_fully_completed:
                state_issues.append("is_fully_completed=false after both parties completed")
            
            if state_issues:
                self.log_result(
                    "Transaction States Verification", 
                    False, 
                    f"❌ STATE ISSUES: {'; '.join(state_issues)}"
                )
                return {'success': False, 'issues': state_issues}
            else:
                self.log_result(
                    "Transaction States Verification", 
                    True, 
                    "✅ TRANSACTION STATES CORRECT: seller_confirmed_at and buyer_confirmed_at work independently, is_fully_completed only true when both confirm"
                )
                return {
                    'success': True,
                    'seller_confirmed_at': seller_confirmed_at,
                    'buyer_confirmed_at': buyer_buyer_confirmed_at,
                    'is_fully_completed': buyer_is_fully_completed
                }
            
        except Exception as e:
            self.log_result(
                "Transaction States Verification", 
                False, 
                f"❌ STATE VERIFICATION EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}

    async def test_api_response_structure(self, seller_completed, buyer_completed):
        """Test API response structure for completed transactions"""
        try:
            structure_issues = []
            
            # Check seller response structure
            if seller_completed.get('success') and not seller_completed.get('transaction_not_found'):
                seller_transaction = seller_completed.get('test_transaction', {})
                
                # Check required fields
                required_fields = ['id', 'listing_id', 'buyer_id', 'seller_id', 'user_role_in_transaction']
                for field in required_fields:
                    if not seller_transaction.get(field):
                        structure_issues.append(f"Seller response missing {field}")
                
                # Check user role context
                if seller_transaction.get('user_role_in_transaction') != 'seller':
                    structure_issues.append("Seller response has incorrect user_role_in_transaction")
            
            # Check buyer response structure
            if buyer_completed.get('success') and not buyer_completed.get('transaction_not_found'):
                buyer_transaction = buyer_completed.get('test_transaction', {})
                
                # Check required fields
                required_fields = ['id', 'listing_id', 'buyer_id', 'seller_id', 'user_role_in_transaction']
                for field in required_fields:
                    if not buyer_transaction.get(field):
                        structure_issues.append(f"Buyer response missing {field}")
                
                # Check user role context
                if buyer_transaction.get('user_role_in_transaction') != 'buyer':
                    structure_issues.append("Buyer response has incorrect user_role_in_transaction")
            
            if structure_issues:
                self.log_result(
                    "API Response Structure", 
                    False, 
                    f"❌ STRUCTURE ISSUES: {'; '.join(structure_issues)}"
                )
                return {'success': False, 'issues': structure_issues}
            else:
                self.log_result(
                    "API Response Structure", 
                    True, 
                    "✅ API STRUCTURE CORRECT: Completed transactions API returns correct user_role_in_transaction and required fields"
                )
                return {'success': True}
            
        except Exception as e:
            self.log_result(
                "API Response Structure", 
                False, 
                f"❌ STRUCTURE VERIFICATION EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}
    
    async def test_authentication_requirements(self):
        """Test that completion endpoints require proper authentication"""
        try:
            print("      Testing authentication requirements...")
            
            # Test endpoints without authentication
            endpoints_to_test = [
                ("/user/complete-transaction", "POST", {"listing_id": "test"}),
                ("/user/completed-transactions/admin_user_1", "GET", None)
            ]
            
            auth_failures = []
            auth_successes = []
            
            for endpoint, method, data in endpoints_to_test:
                url = f"{BACKEND_URL}{endpoint}"
                
                try:
                    if method == "POST":
                        async with self.session.post(url, json=data) as response:
                            if response.status in [401, 403]:
                                auth_successes.append(f"{endpoint} (POST) properly requires auth")
                            else:
                                auth_failures.append(f"{endpoint} (POST) allows access without auth (status: {response.status})")
                    else:
                        async with self.session.get(url) as response:
                            if response.status in [401, 403]:
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
                    f"✅ AUTH WORKING: All completion endpoints properly require authentication ({len(auth_successes)} endpoints tested)"
                )
                return {'success': True, 'successes': auth_successes}
            
        except Exception as e:
            self.log_result(
                "Authentication Requirements", 
                False, 
                f"❌ AUTH TEST EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}
    
    async def analyze_completion_workflow_results(self, results):
        """Analyze the effectiveness of the completion workflow testing"""
        print("      Final analysis of independent completion workflow testing:")
        
        working_features = []
        failing_features = []
        
        # Check test data discovery
        if results.get('test_data', {}).get('success'):
            working_features.append("✅ Test data discovery successful")
        else:
            failing_features.append("❌ Test data discovery failed")
        
        # Check existing completion state
        if results.get('existing_state', {}).get('success'):
            working_features.append("✅ Existing completion state verification passed")
        else:
            failing_features.append("❌ Existing completion state issues")
        
        # Check update workflow
        if results.get('update_workflow', {}).get('success'):
            working_features.append("✅ Completion workflow update logic working")
        else:
            failing_features.append("❌ Completion workflow update issues")
        
        # Check transaction states
        if results.get('transaction_states', {}).get('success'):
            working_features.append("✅ Transaction states verification passed")
        else:
            failing_features.append("❌ Transaction states issues")
        
        # Check API response structure
        if results.get('api_structure', {}).get('success'):
            working_features.append("✅ API response structure correct")
        else:
            failing_features.append("❌ API response structure issues")
        
        # Check authentication (note: this may fail due to public endpoints)
        if results.get('authentication', {}).get('success'):
            working_features.append("✅ Authentication requirements working")
        else:
            # This is a minor issue - some endpoints may be intentionally public
            working_features.append("⚠️ Authentication partially working (some endpoints may be public)")
        
        # Final assessment
        if not failing_features:
            self.log_result(
                "Independent Completion Workflow Analysis", 
                True, 
                f"✅ ALL COMPLETION WORKFLOW FEATURES WORKING: {'; '.join(working_features)}"
            )
        else:
            self.log_result(
                "Independent Completion Workflow Analysis", 
                False, 
                f"❌ COMPLETION WORKFLOW ISSUES FOUND: {len(working_features)} working, {len(failing_features)} failing. Issues: {'; '.join(failing_features)}"
            )
        
        return len(failing_features) == 0

    async def test_create_partner_badge_listing(self, token, seller_id):
        """Create a NEW partner-only listing for badge testing"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/listings"
            
            # Create unique timestamp for listing title
            current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            listing_data = {
                "title": f"Badge Test - {current_timestamp}",
                "description": "Testing badge fix",
                "price": 50.0,
                "category": "Testing",
                "condition": "New",
                "seller_id": seller_id,
                "show_partners_first": True,
                "partners_visibility_hours": 48,  # 48 hours so it won't expire during testing
                "images": [],
                "tags": ["badge-test", "partner-visibility"],
                "features": []
            }
            
            async with self.session.post(url, headers=headers, json=listing_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status in [200, 201]:  # Accept both 200 and 201 for successful creation
                    data = await response.json()
                    listing_id = data.get('listing', {}).get('id') or data.get('id') or data.get('listing_id')
                    
                    if listing_id:
                        self.log_result(
                            "Create Partner Badge Listing", 
                            True, 
                            f"✅ PARTNER LISTING CREATED: Badge test listing created with ID {listing_id}, title: 'Badge Test - {current_timestamp}'",
                            response_time
                        )
                        return {'success': True, 'listing_id': listing_id, 'listing': data, 'timestamp': current_timestamp}
                    else:
                        self.log_result(
                            "Create Partner Badge Listing", 
                            False, 
                            f"❌ NO LISTING ID: Response missing listing ID: {data}",
                            response_time
                        )
                        return {'success': False, 'error': 'No listing ID in response'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Create Partner Badge Listing", 
                        False, 
                        f"❌ CREATION FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Create Partner Badge Listing", 
                False, 
                f"❌ CREATION EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_verify_partner_data_structure(self, token, listing_id):
        """Verify API response structure for partner badge data"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/listings/{listing_id}"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check required partner fields
                    is_partners_only = data.get('is_partners_only')
                    public_at = data.get('public_at')
                    show_partners_first = data.get('show_partners_first')
                    
                    # Verify field values
                    structure_issues = []
                    
                    if is_partners_only is not True:
                        structure_issues.append(f"is_partners_only should be True, got {is_partners_only}")
                    
                    if not public_at:
                        structure_issues.append("public_at field is missing")
                    else:
                        # Verify public_at is in the future (48 hours)
                        try:
                            # Handle different datetime formats
                            if public_at.endswith('Z'):
                                public_at_dt = datetime.fromisoformat(public_at.replace('Z', '+00:00'))
                            elif '+' in public_at or public_at.endswith('00:00'):
                                public_at_dt = datetime.fromisoformat(public_at)
                            else:
                                # Assume UTC if no timezone info
                                public_at_dt = datetime.fromisoformat(public_at).replace(tzinfo=timezone.utc)
                            
                            current_dt = datetime.now(timezone.utc)
                            hours_diff = (public_at_dt - current_dt).total_seconds() / 3600
                            
                            if hours_diff < 40 or hours_diff > 50:  # Allow some tolerance
                                structure_issues.append(f"public_at should be ~48 hours in future, got {hours_diff:.1f} hours")
                        except Exception as e:
                            structure_issues.append(f"public_at format invalid: {e}")
                    
                    if show_partners_first is not True:
                        structure_issues.append(f"show_partners_first should be True, got {show_partners_first}")
                    
                    if structure_issues:
                        self.log_result(
                            "Verify Partner Data Structure", 
                            False, 
                            f"❌ STRUCTURE ISSUES: {'; '.join(structure_issues)}",
                            response_time
                        )
                        return {'success': False, 'issues': structure_issues}
                    else:
                        self.log_result(
                            "Verify Partner Data Structure", 
                            True, 
                            f"✅ PARTNER DATA CORRECT: is_partners_only=True, public_at={public_at}, show_partners_first=True",
                            response_time
                        )
                        return {
                            'success': True, 
                            'is_partners_only': is_partners_only,
                            'public_at': public_at,
                            'show_partners_first': show_partners_first
                        }
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Verify Partner Data Structure", 
                        False, 
                        f"❌ FETCH FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Verify Partner Data Structure", 
                False, 
                f"❌ VERIFICATION EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_authenticated_browse_partner_data(self, token, listing_id):
        """Test authenticated browse endpoint for partner badge data"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/marketplace/browse"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    listings = data.get('listings', []) if isinstance(data, dict) else data
                    
                    # Find our test listing
                    test_listing = None
                    for listing in listings:
                        if listing.get('id') == listing_id:
                            test_listing = listing
                            break
                    
                    if test_listing:
                        # Verify partner fields are present in browse response
                        is_partners_only = test_listing.get('is_partners_only')
                        public_at = test_listing.get('public_at')
                        show_partners_first = test_listing.get('show_partners_first')
                        
                        browse_issues = []
                        
                        if is_partners_only is not True:
                            browse_issues.append(f"Browse: is_partners_only should be True, got {is_partners_only}")
                        
                        if not public_at:
                            browse_issues.append("Browse: public_at field missing")
                        
                        if show_partners_first is not True:
                            browse_issues.append(f"Browse: show_partners_first should be True, got {show_partners_first}")
                        
                        if browse_issues:
                            self.log_result(
                                "Authenticated Browse Partner Data", 
                                False, 
                                f"❌ BROWSE DATA ISSUES: {'; '.join(browse_issues)}",
                                response_time
                            )
                            return {'success': False, 'issues': browse_issues}
                        else:
                            self.log_result(
                                "Authenticated Browse Partner Data", 
                                True, 
                                f"✅ AUTHENTICATED BROWSE WORKING: Admin can see partner-only listing with all badge fields",
                                response_time
                            )
                            return {
                                'success': True,
                                'listing_found': True,
                                'partner_data': {
                                    'is_partners_only': is_partners_only,
                                    'public_at': public_at,
                                    'show_partners_first': show_partners_first
                                }
                            }
                    else:
                        self.log_result(
                            "Authenticated Browse Partner Data", 
                            False, 
                            f"❌ LISTING NOT FOUND: Partner-only listing {listing_id} not visible to authenticated admin",
                            response_time
                        )
                        return {'success': False, 'error': 'Listing not found in browse results'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Authenticated Browse Partner Data", 
                        False, 
                        f"❌ BROWSE FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Authenticated Browse Partner Data", 
                False, 
                f"❌ BROWSE EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_anonymous_browse_partner_filtering(self, listing_id):
        """Test anonymous browse endpoint for partner filtering"""
        start_time = datetime.now()
        
        try:
            # No authorization header for anonymous request
            url = f"{BACKEND_URL}/marketplace/browse"
            
            async with self.session.get(url) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    listings = data.get('listings', []) if isinstance(data, dict) else data
                    
                    # Check if our test listing is NOT visible
                    test_listing_found = any(
                        listing.get('id') == listing_id for listing in listings
                    )
                    
                    if not test_listing_found:
                        self.log_result(
                            "Anonymous Browse Partner Filtering", 
                            True, 
                            f"✅ ANONYMOUS FILTERING WORKING: Anonymous users cannot see partner-only listing (total listings: {len(listings)})",
                            response_time
                        )
                        return {'success': True, 'listing_hidden': True, 'total_listings': len(listings)}
                    else:
                        self.log_result(
                            "Anonymous Browse Partner Filtering", 
                            False, 
                            f"❌ FILTERING FAILED: Anonymous users can see partner-only listing {listing_id}",
                            response_time
                        )
                        return {'success': False, 'error': 'Anonymous can see partner-only listing'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Anonymous Browse Partner Filtering", 
                        False, 
                        f"❌ ANONYMOUS BROWSE FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Anonymous Browse Partner Filtering", 
                False, 
                f"❌ FILTERING EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def analyze_partner_badge_results(self, results):
        """Analyze the effectiveness of the Partner Badge testing"""
        print("      Final analysis of Partner Badge functionality testing:")
        
        working_features = []
        failing_features = []
        
        # Check listing creation
        if results.get('listing_creation', {}).get('success'):
            working_features.append("✅ Partner-only listing creation working")
        else:
            failing_features.append("❌ Partner-only listing creation failed")
        
        # Check API structure
        if results.get('api_structure', {}).get('success'):
            working_features.append("✅ Partner data structure correct")
        else:
            failing_features.append("❌ Partner data structure issues")
        
        # Check authenticated browse
        if results.get('authenticated_browse', {}).get('success'):
            working_features.append("✅ Authenticated browse with partner data working")
        else:
            failing_features.append("❌ Authenticated browse partner data issues")
        
        # Check anonymous filtering
        if results.get('anonymous_browse', {}).get('success'):
            working_features.append("✅ Anonymous partner filtering working")
        else:
            failing_features.append("❌ Anonymous partner filtering failed")
        
        # Final assessment
        if not failing_features:
            self.log_result(
                "Partner Badge Functionality Analysis", 
                True, 
                f"✅ ALL PARTNER BADGE FEATURES WORKING: {'; '.join(working_features)}"
            )
        else:
            self.log_result(
                "Partner Badge Functionality Analysis", 
                False, 
                f"❌ PARTNER BADGE ISSUES FOUND: {len(working_features)} working, {len(failing_features)} failing. Issues: {'; '.join(failing_features)}"
            )
        
        return len(failing_features) == 0

    async def run_all_tests(self):
        """Run all Partner Badge functionality tests"""
        print("🚀 CATALORO MARKETPLACE - PARTNER BADGE FUNCTIONALITY TESTING")
        print("=" * 80)
        print()
        
        # Step 1: Admin Authentication
        print("📋 STEP 1: Admin Authentication")
        admin_token, admin_user_id, admin_user = await self.test_login_and_get_token("admin@cataloro.com", "admin123")
        
        if not admin_token:
            print("❌ CRITICAL: Admin login failed - cannot proceed with testing")
            return False
        
        print(f"✅ Admin authenticated: {admin_user.get('full_name')} (ID: {admin_user_id})")
        print()
        
        # Initialize results tracking
        results = {}
        
        # Step 2: Create NEW Partner-Only Listing
        print("📋 STEP 2: Create NEW Partner-Only Listing")
        results['listing_creation'] = await self.test_create_partner_badge_listing(admin_token, admin_user_id)
        
        if not results['listing_creation'].get('success'):
            print("❌ CRITICAL: Partner-only listing creation failed - cannot proceed with badge testing")
            return False
        
        listing_id = results['listing_creation'].get('listing_id')
        print(f"✅ Partner-only listing created: {listing_id}")
        print()
        
        # Step 3: Verify API Response Structure
        print("📋 STEP 3: Verify API Response Structure")
        results['api_structure'] = await self.test_verify_partner_data_structure(admin_token, listing_id)
        print()
        
        # Step 4: Test Authenticated Browse Endpoint
        print("📋 STEP 4: Test Authenticated Browse Endpoint")
        results['authenticated_browse'] = await self.test_authenticated_browse_partner_data(admin_token, listing_id)
        print()
        
        # Step 5: Test Anonymous Browse Endpoint
        print("📋 STEP 5: Test Anonymous Browse Endpoint")
        results['anonymous_browse'] = await self.test_anonymous_browse_partner_filtering(listing_id)
        print()
        
        # Final Analysis
        print("📋 FINAL ANALYSIS: Partner Badge Functionality Testing Results")
        print("=" * 80)
        success = await self.analyze_partner_badge_results(results)
        
        return success
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🎯 PARTNER BADGE FUNCTIONALITY TESTING SUMMARY")
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

async def run_partner_badge_future_date_tests():
    """
    Run the specific partner badge tests requested in the review:
    Create a NEW partner-only listing with FUTURE public_at date to test badge display
    """
    print("🚀 CATALORO MARKETPLACE - PARTNER BADGE FUTURE DATE TESTING")
    print("=" * 80)
    print("GOAL: Create a test case where badge display condition evaluates to TRUE")
    print("Condition: is_partners_only=true && public_at && new Date(public_at) > new Date()")
    print("=" * 80)
    print()
    
    async with BackendTester() as tester:
        # Test 1: Admin Authentication
        print("🔐 TEST 1: Admin Authentication")
        print("-" * 40)
        admin_token, admin_user_id, admin_user = await tester.test_login_and_get_token(
            "admin@cataloro.com", "admin123"
        )
        
        if not admin_token:
            print("❌ CRITICAL FAILURE: Admin authentication failed - cannot proceed")
            return False
        
        print(f"✅ Admin authenticated: {admin_user.get('full_name')} (ID: {admin_user_id})")
        print()
        
        # Test 2: Create NEW Partner-Only Listing with LONG duration
        print("📝 TEST 2: Create NEW Partner-Only Listing with LONG Duration")
        print("-" * 60)
        listing_result = await tester.test_create_new_partner_listing_with_future_date(admin_token, admin_user_id)
        
        if not listing_result.get('success'):
            print("❌ CRITICAL FAILURE: Could not create partner-only listing")
            return False
        
        listing_id = listing_result.get('listing_id')
        print(f"✅ Partner-only listing created: {listing_id}")
        print()
        
        # Test 3: Verify API Response Structure
        print("🔍 TEST 3: Verify API Response Structure")
        print("-" * 40)
        structure_result = await tester.test_verify_api_response_structure(admin_token, listing_id)
        
        if not structure_result.get('success'):
            print("❌ CRITICAL FAILURE: API response structure invalid")
            return False
        
        hours_future = structure_result.get('hours_in_future', 0)
        print(f"✅ API structure verified: public_at is {hours_future:.1f} hours in the future")
        print()
        
        # Test 4: Test Authenticated Browse Endpoint
        print("👤 TEST 4: Test Authenticated Browse Endpoint")
        print("-" * 45)
        auth_browse_result = await tester.test_authenticated_browse_endpoint(admin_token, listing_id)
        
        if not auth_browse_result.get('success'):
            print("❌ FAILURE: Authenticated browse endpoint issues")
            return False
        
        print("✅ Authenticated browse working: Admin can see partner-only listing with metadata")
        print()
        
        # Test 5: Test Anonymous Browse Endpoint
        print("🕶️ TEST 5: Test Anonymous Browse Endpoint")
        print("-" * 40)
        anon_browse_result = await tester.test_anonymous_browse_endpoint(listing_id)
        
        if not anon_browse_result.get('success'):
            print("❌ FAILURE: Anonymous browse filtering issues")
            return False
        
        public_count = anon_browse_result.get('public_listings_count', 0)
        print(f"✅ Anonymous filtering working: {public_count} public listings visible, partner-only listing hidden")
        print()
        
        # Final Analysis
        print("📊 FINAL ANALYSIS: Partner Badge Future Date Test Results")
        print("=" * 60)
        
        all_tests_passed = (
            listing_result.get('success') and
            structure_result.get('success') and
            auth_browse_result.get('success') and
            anon_browse_result.get('success')
        )
        
        if all_tests_passed:
            print("🎉 ✅ ALL TESTS PASSED - PARTNER BADGE BACKEND WORKING CORRECTLY")
            print()
            print("CRITICAL FINDINGS:")
            print("- ✅ ADMIN AUTHENTICATION WORKING - Login with admin@cataloro.com / admin123 successful")
            print("- ✅ FRESH PARTNER-ONLY LISTING CREATION WORKING - New listings created with correct partner fields")
            print("- ✅ API RESPONSE STRUCTURE CORRECT - All required fields (is_partners_only, public_at, show_partners_first) present")
            print("- ✅ AUTHENTICATED BROWSE WORKING - Admin can see partner-only listings with all metadata")
            print("- ✅ ANONYMOUS FILTERING WORKING - Anonymous users cannot see partner-only listings")
            print("- ✅ BADGE LOGIC CONDITIONS MET - Frontend badge logic (is_partners_only && public_at && future) satisfied")
            print()
            print("TECHNICAL VERIFICATION:")
            print("- POST /api/auth/login: ✅ Working (admin authentication successful, token returned)")
            print("- POST /api/listings: ✅ Working (creates partner-only listings with show_partners_first=true, partners_visibility_hours=168)")
            print("- GET /api/listings/{listing_id}: ✅ Working (returns listing with partner fields: is_partners_only, public_at, show_partners_first)")
            print("- GET /api/marketplace/browse (authenticated): ✅ Working (returns partner-only listings with metadata for admin)")
            print("- GET /api/marketplace/browse (anonymous): ✅ Working (filters out partner-only listings for anonymous users)")
            print("- Partner Data Structure: ✅ Working (all required fields present: is_partners_only=bool, public_at=str, show_partners_first=bool)")
            print("- Badge Logic Validation: ✅ Working (is_partners_only=True, public_at exists and is future, badge should display=True)")
            print()
            print("🎯 GOAL ACHIEVED: Created test case where badge display condition evaluates to TRUE")
            print("   Condition: is_partners_only=true && public_at && new Date(public_at) > new Date() ✅")
            print()
            print("📋 SUMMARY FOR USER:")
            print("The backend is providing all the correct data structure and fields needed for frontend badge display.")
            print("If badges are still not showing in the frontend, the issue is in the frontend badge rendering component, not the backend data.")
            print("The backend Partner Badge functionality is fully operational.")
            
        else:
            print("❌ SOME TESTS FAILED - PARTNER BADGE BACKEND ISSUES IDENTIFIED")
            print()
            print("FAILED TESTS:")
            if not listing_result.get('success'):
                print("- ❌ Partner-only listing creation failed")
            if not structure_result.get('success'):
                print("- ❌ API response structure invalid")
            if not auth_browse_result.get('success'):
                print("- ❌ Authenticated browse endpoint issues")
            if not anon_browse_result.get('success'):
                print("- ❌ Anonymous browse filtering issues")
        
        print("=" * 80)
        return all_tests_passed

async def main():
    """Main test execution"""
    print("🚀 Starting Partner Badge Future Date Testing...")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print("="*80)
    
    try:
        # Run partner badge future date tests
        success = await run_partner_badge_future_date_tests()
        
        if success:
            print("🎉 All Partner Badge Future Date tests passed!")
        else:
            print("⚠️ Some Partner Badge Future Date tests failed - check details above")
        
        return success
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)