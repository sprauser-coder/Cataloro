#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - COMPREHENSIVE PARTNER BADGE TESTING
Extended testing for Partner Badge display functionality including visibility filtering

COMPREHENSIVE TEST SCENARIOS:
1. **Admin Authentication** - Login as admin@cataloro.com / admin123
2. **Partner-only Listing Creation** - Create listing with partner visibility
3. **Database Verification** - Verify partner fields are saved correctly
4. **Authenticated Browse** - Test browse endpoint with admin authentication
5. **Anonymous Browse** - Test browse endpoint without authentication (should not see partner-only listing)
6. **Partner Data Structure** - Verify all fields needed for badge display
7. **Badge Logic Validation** - Confirm badge should display based on frontend logic

This comprehensive test ensures the complete partner badge workflow is functioning correctly.
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone, timedelta
import pytz

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://cataloro-uxfixes.preview.emergentagent.com/api"

class ComprehensivePartnerBadgeTester:
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
    
    async def test_admin_login(self):
        """Test admin login with admin@cataloro.com / admin123"""
        start_time = datetime.now()
        
        try:
            login_data = {
                "email": "admin@cataloro.com",
                "password": "admin123"
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
                            "Admin Login Authentication", 
                            True, 
                            f"Successfully logged in as {user.get('full_name', 'Admin')} (ID: {user_id}), token received",
                            response_time
                        )
                        return token, user_id, user
                    else:
                        self.log_result(
                            "Admin Login Authentication", 
                            False, 
                            f"Login successful but missing token or user_id in response: {data}",
                            response_time
                        )
                        return None, None, None
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Admin Login Authentication", 
                        False, 
                        f"Login failed with status {response.status}: {error_text}",
                        response_time
                    )
                    return None, None, None
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Admin Login Authentication", 
                False, 
                f"Login request failed with exception: {str(e)}",
                response_time
            )
            return None, None, None
    
    async def create_partner_badge_test_listing(self, token, seller_id):
        """Create a new partner-only listing for badge testing"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/listings"
            
            listing_data = {
                "title": "Partner Badge Test",
                "description": "Testing badge display",
                "price": 100.0,
                "category": "Electronics",
                "condition": "New",
                "seller_id": seller_id,
                "show_partners_first": True,
                "partners_visibility_hours": 24,
                "images": [],
                "tags": ["partner-test", "badge-display"],
                "features": []
            }
            
            async with self.session.post(url, headers=headers, json=listing_data) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status in [200, 201]:
                    data = await response.json()
                    listing_id = data.get('id') or data.get('listing_id')
                    
                    if listing_id:
                        self.log_result(
                            "Create Partner Badge Test Listing", 
                            True, 
                            f"✅ PARTNER LISTING CREATED: ID {listing_id}, creation successful",
                            response_time
                        )
                        return {'success': True, 'listing_id': listing_id, 'creation_response': data}
                    else:
                        self.log_result(
                            "Create Partner Badge Test Listing", 
                            False, 
                            f"❌ NO LISTING ID: Response missing listing ID: {data}",
                            response_time
                        )
                        return {'success': False, 'error': 'No listing ID in response'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Create Partner Badge Test Listing", 
                        False, 
                        f"❌ CREATION FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Create Partner Badge Test Listing", 
                False, 
                f"❌ CREATION EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def verify_listing_in_database(self, token, listing_id):
        """Verify the listing was created with correct partner data in database"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/listings/{listing_id}"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    listing = data.get('listing') or data
                    
                    # Verify all required partner fields
                    required_fields = ['is_partners_only', 'public_at', 'show_partners_first']
                    missing_fields = [field for field in required_fields if field not in listing]
                    
                    if not missing_fields:
                        is_partners_only = listing.get('is_partners_only')
                        public_at = listing.get('public_at')
                        show_partners_first = listing.get('show_partners_first')
                        
                        # Verify values are correct
                        if is_partners_only is True and show_partners_first is True and public_at:
                            self.log_result(
                                "Verify Listing in Database", 
                                True, 
                                f"✅ DATABASE VERIFICATION PASSED: All partner fields correct - is_partners_only={is_partners_only}, public_at={public_at}, show_partners_first={show_partners_first}",
                                response_time
                            )
                            return {'success': True, 'listing': listing, 'partner_fields_verified': True}
                        else:
                            self.log_result(
                                "Verify Listing in Database", 
                                False, 
                                f"❌ INCORRECT PARTNER VALUES: is_partners_only={is_partners_only}, show_partners_first={show_partners_first}, public_at={public_at}",
                                response_time
                            )
                            return {'success': False, 'error': 'Incorrect partner field values'}
                    else:
                        self.log_result(
                            "Verify Listing in Database", 
                            False, 
                            f"❌ MISSING PARTNER FIELDS: {missing_fields}",
                            response_time
                        )
                        return {'success': False, 'error': f'Missing fields: {missing_fields}'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Verify Listing in Database", 
                        False, 
                        f"❌ VERIFICATION FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Verify Listing in Database", 
                False, 
                f"❌ VERIFICATION EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def test_authenticated_browse(self, token, listing_id):
        """Test browse endpoint with authentication (admin should see partner-only listing)"""
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
                        partner_fields = ['is_partners_only', 'public_at', 'show_partners_first']
                        present_fields = [field for field in partner_fields if field in test_listing]
                        
                        if len(present_fields) == len(partner_fields):
                            is_partners_only = test_listing.get('is_partners_only')
                            public_at = test_listing.get('public_at')
                            show_partners_first = test_listing.get('show_partners_first')
                            
                            self.log_result(
                                "Test Authenticated Browse", 
                                True, 
                                f"✅ AUTHENTICATED BROWSE WORKING: Admin can see partner-only listing with all fields - is_partners_only={is_partners_only}, public_at={public_at}, show_partners_first={show_partners_first}",
                                response_time
                            )
                            return {'success': True, 'test_listing': test_listing, 'admin_can_see': True}
                        else:
                            missing_fields = [field for field in partner_fields if field not in test_listing]
                            self.log_result(
                                "Test Authenticated Browse", 
                                False, 
                                f"❌ MISSING PARTNER FIELDS IN BROWSE: {missing_fields}",
                                response_time
                            )
                            return {'success': False, 'error': f'Missing partner fields: {missing_fields}'}
                    else:
                        self.log_result(
                            "Test Authenticated Browse", 
                            False, 
                            f"❌ ADMIN CANNOT SEE LISTING: Partner-only listing {listing_id} not found in authenticated browse ({len(listings)} listings total)",
                            response_time
                        )
                        return {'success': False, 'error': 'Admin cannot see partner-only listing'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Test Authenticated Browse", 
                        False, 
                        f"❌ AUTHENTICATED BROWSE FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Test Authenticated Browse", 
                False, 
                f"❌ AUTHENTICATED BROWSE EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def test_anonymous_browse(self, listing_id):
        """Test browse endpoint without authentication (should NOT see partner-only listing)"""
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
                    test_listing_found = any(listing.get('id') == listing_id for listing in listings)
                    
                    if not test_listing_found:
                        self.log_result(
                            "Test Anonymous Browse", 
                            True, 
                            f"✅ ANONYMOUS FILTERING WORKING: Anonymous user cannot see partner-only listing ({len(listings)} public listings visible)",
                            response_time
                        )
                        return {'success': True, 'anonymous_cannot_see': True, 'public_listings_count': len(listings)}
                    else:
                        self.log_result(
                            "Test Anonymous Browse", 
                            False, 
                            f"❌ ANONYMOUS FILTERING FAILED: Anonymous user can see partner-only listing {listing_id}",
                            response_time
                        )
                        return {'success': False, 'error': 'Anonymous can see partner-only listing'}
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Test Anonymous Browse", 
                        False, 
                        f"❌ ANONYMOUS BROWSE FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {'success': False, 'error': error_text}
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Test Anonymous Browse", 
                False, 
                f"❌ ANONYMOUS BROWSE EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}
    
    async def verify_partner_data_structure(self, test_listing):
        """Verify partner data structure is correct for frontend badge display"""
        try:
            # Check all required fields for partner badge display
            required_for_badge = {
                'is_partners_only': bool,
                'public_at': str,
                'show_partners_first': bool,
                'title': str,
                'id': str
            }
            
            missing_fields = []
            incorrect_types = []
            
            for field, expected_type in required_for_badge.items():
                if field not in test_listing:
                    missing_fields.append(field)
                elif not isinstance(test_listing[field], expected_type):
                    incorrect_types.append(f"{field} (expected {expected_type.__name__}, got {type(test_listing[field]).__name__})")
            
            if not missing_fields and not incorrect_types:
                # Verify the badge logic condition: item.is_partners_only && item.public_at && new Date(item.public_at) > new Date()
                is_partners_only = test_listing.get('is_partners_only')
                public_at = test_listing.get('public_at')
                
                try:
                    # Handle both timezone-aware and naive datetime strings
                    if public_at.endswith('Z'):
                        public_at_dt = datetime.fromisoformat(public_at.replace('Z', '+00:00'))
                    elif '+' in public_at or public_at.endswith('00:00'):
                        public_at_dt = datetime.fromisoformat(public_at)
                    else:
                        # Assume UTC if no timezone info
                        public_at_dt = datetime.fromisoformat(public_at).replace(tzinfo=timezone.utc)
                    
                    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
                    is_future = public_at_dt > current_time
                    
                    badge_should_show = is_partners_only and public_at and is_future
                    
                    if badge_should_show:
                        time_until_public = (public_at_dt - current_time).total_seconds() / 3600  # hours
                        self.log_result(
                            "Verify Partner Data Structure", 
                            True, 
                            f"✅ PARTNER DATA STRUCTURE CORRECT: Badge logic condition met - is_partners_only={is_partners_only}, public_at={public_at} (~{time_until_public:.1f}h future), badge should display=True"
                        )
                        return {
                            'success': True,
                            'badge_should_show': True,
                            'data_structure_valid': True,
                            'is_partners_only': is_partners_only,
                            'public_at': public_at,
                            'public_at_is_future': is_future,
                            'hours_until_public': time_until_public
                        }
                    else:
                        self.log_result(
                            "Verify Partner Data Structure", 
                            False, 
                            f"❌ BADGE LOGIC CONDITION NOT MET: is_partners_only={is_partners_only}, public_at={public_at}, future={is_future}"
                        )
                        return {'success': False, 'error': 'Badge logic condition not met'}
                except Exception as dt_error:
                    self.log_result(
                        "Verify Partner Data Structure", 
                        False, 
                        f"❌ INVALID PUBLIC_AT FORMAT: {public_at}, error: {str(dt_error)}"
                    )
                    return {'success': False, 'error': f'Invalid public_at format: {str(dt_error)}'}
            else:
                issues = []
                if missing_fields:
                    issues.append(f"Missing fields: {missing_fields}")
                if incorrect_types:
                    issues.append(f"Incorrect types: {incorrect_types}")
                
                self.log_result(
                    "Verify Partner Data Structure", 
                    False, 
                    f"❌ DATA STRUCTURE INVALID: {'; '.join(issues)}"
                )
                return {'success': False, 'error': '; '.join(issues)}
                
        except Exception as e:
            self.log_result(
                "Verify Partner Data Structure", 
                False, 
                f"❌ STRUCTURE VERIFICATION EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}
    
    async def validate_badge_logic(self, test_listing):
        """Validate the frontend badge logic: item.is_partners_only && item.public_at && new Date(item.public_at) > new Date()"""
        try:
            is_partners_only = test_listing.get('is_partners_only')
            public_at = test_listing.get('public_at')
            
            # Frontend badge logic conditions
            condition1 = is_partners_only is True
            condition2 = public_at is not None and public_at != ""
            
            # Check if public_at is in the future
            condition3 = False
            if condition2:
                try:
                    if public_at.endswith('Z'):
                        public_at_dt = datetime.fromisoformat(public_at.replace('Z', '+00:00'))
                    elif '+' in public_at or public_at.endswith('00:00'):
                        public_at_dt = datetime.fromisoformat(public_at)
                    else:
                        public_at_dt = datetime.fromisoformat(public_at).replace(tzinfo=timezone.utc)
                    
                    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
                    condition3 = public_at_dt > current_time
                except:
                    condition3 = False
            
            badge_should_show = condition1 and condition2 and condition3
            
            self.log_result(
                "Validate Badge Logic", 
                True, 
                f"✅ BADGE LOGIC VALIDATION: is_partners_only={condition1}, public_at_exists={condition2}, public_at_future={condition3} → Badge should show: {badge_should_show}"
            )
            
            return {
                'success': True,
                'badge_should_show': badge_should_show,
                'condition1_is_partners_only': condition1,
                'condition2_public_at_exists': condition2,
                'condition3_public_at_future': condition3
            }
            
        except Exception as e:
            self.log_result(
                "Validate Badge Logic", 
                False, 
                f"❌ BADGE LOGIC VALIDATION EXCEPTION: {str(e)}"
            )
            return {'success': False, 'error': str(e)}
    
    async def run_comprehensive_tests(self):
        """Run all comprehensive partner badge tests"""
        print("🚀 STARTING COMPREHENSIVE PARTNER BADGE TESTING")
        print("=" * 70)
        
        try:
            # Step 1: Login as admin user
            print("Step 1: Testing admin authentication...")
            token, user_id, user = await self.test_admin_login()
            
            if not token:
                print("❌ CRITICAL FAILURE: Admin login failed - cannot proceed with tests")
                return False
            
            # Step 2: Create partner-only listing
            print("\nStep 2: Creating partner-only listing...")
            listing_result = await self.create_partner_badge_test_listing(token, user_id)
            
            if not listing_result.get('success'):
                print("❌ CRITICAL FAILURE: Partner listing creation failed - cannot proceed with tests")
                return False
            
            listing_id = listing_result.get('listing_id')
            
            # Step 3: Verify listing in database
            print(f"\nStep 3: Verifying listing {listing_id} in database...")
            db_verification = await self.verify_listing_in_database(token, listing_id)
            
            if not db_verification.get('success'):
                print("❌ CRITICAL FAILURE: Database verification failed")
                return False
            
            # Step 4: Test authenticated browse (admin should see listing)
            print(f"\nStep 4: Testing authenticated browse (admin should see partner-only listing)...")
            auth_browse_result = await self.test_authenticated_browse(token, listing_id)
            
            if not auth_browse_result.get('success'):
                print("❌ CRITICAL FAILURE: Authenticated browse test failed")
                return False
            
            test_listing = auth_browse_result.get('test_listing')
            
            # Step 5: Test anonymous browse (should NOT see listing)
            print(f"\nStep 5: Testing anonymous browse (should NOT see partner-only listing)...")
            anon_browse_result = await self.test_anonymous_browse(listing_id)
            
            if not anon_browse_result.get('success'):
                print("❌ CRITICAL FAILURE: Anonymous browse filtering failed")
                return False
            
            # Step 6: Verify partner data structure
            print(f"\nStep 6: Verifying partner data structure for badge display...")
            structure_result = await self.verify_partner_data_structure(test_listing)
            
            if not structure_result.get('success'):
                print("❌ CRITICAL FAILURE: Partner data structure verification failed")
                return False
            
            # Step 7: Validate badge logic
            print(f"\nStep 7: Validating frontend badge logic...")
            badge_logic_result = await self.validate_badge_logic(test_listing)
            
            # Final assessment
            print("\n" + "=" * 70)
            print("🏁 COMPREHENSIVE PARTNER BADGE TESTING COMPLETE")
            print("=" * 70)
            
            successful_tests = sum(1 for result in self.test_results if result['success'])
            total_tests = len(self.test_results)
            
            print(f"📊 RESULTS: {successful_tests}/{total_tests} tests passed ({(successful_tests/total_tests)*100:.1f}%)")
            
            if successful_tests == total_tests:
                print("✅ ALL TESTS PASSED - Partner badge functionality is working correctly")
                print(f"✅ Partner-only listing created with ID: {listing_id}")
                print(f"✅ Admin can see partner-only listing: {auth_browse_result.get('admin_can_see', False)}")
                print(f"✅ Anonymous users cannot see partner-only listing: {anon_browse_result.get('anonymous_cannot_see', False)}")
                print(f"✅ Badge should display: {badge_logic_result.get('badge_should_show', False)}")
                print(f"✅ Hours until public: {structure_result.get('hours_until_public', 0):.1f}")
                return True
            else:
                failed_tests = [result for result in self.test_results if not result['success']]
                print(f"❌ {len(failed_tests)} TESTS FAILED:")
                for failed_test in failed_tests:
                    print(f"   - {failed_test['test']}: {failed_test['details']}")
                return False
                
        except Exception as e:
            print(f"❌ TESTING FRAMEWORK ERROR: {str(e)}")
            return False

async def main():
    """Main test execution"""
    async with ComprehensivePartnerBadgeTester() as tester:
        success = await tester.run_comprehensive_tests()
        
        if success:
            print("\n🎉 COMPREHENSIVE PARTNER BADGE TESTING SUCCESSFUL")
            sys.exit(0)
        else:
            print("\n💥 COMPREHENSIVE PARTNER BADGE TESTING FAILED")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())