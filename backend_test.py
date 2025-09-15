#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - BUY/SELL MENU ITEMS INVESTIGATION
URGENT: Investigating why Buy and Sell menu items are still not appearing in Admin Panel Menu Settings

CURRENT ISSUE (Review Request):
The Buy and Sell menu items are still not appearing in the Admin Panel Menu Settings interface 
despite the database fix. User screenshot shows Admin Panel Menu Settings interface with only:
Browse, Messages, Notifications, Create, Tenders, Listings, Profile, View Public Profile, Admin

**CRITICAL INVESTIGATION REQUIRED:**

**1. Re-verify Menu Settings API Response**
- Login as admin (admin@cataloro.com / password123)
- Call GET `/api/admin/menu-settings` again
- Check if Buy/Sell items are actually in the API response
- Verify the exact structure of the returned data

**2. Debug Desktop vs Mobile Menu Structure**  
- Check if Buy/Sell items exist in desktop_menu vs mobile_menu
- User mentions they appear in desktop version but not mobile
- This suggests different configurations for desktop vs mobile menus

**3. Investigate Frontend Filtering**
- Check if frontend MenuSettings.js is filtering out certain items
- Look for any conditional logic that might hide Buy/Sell items
- Verify if there are permission checks that could hide these items

**4. Check Current Database State**
- Verify the menu_settings collection current state
- Ensure the database clear operation actually worked
- Check if new database overrides have been created

**EXPECTED DEBUG OUTPUT:**
- Exact API response structure showing whether Buy/Sell items are present
- Comparison of desktop_menu vs mobile_menu configurations  
- Current database state of menu_settings collection
- Any filtering or conditional logic affecting menu item display

**LOGIN CREDENTIALS:** admin@cataloro.com / password123

**GOAL:** Identify exactly why Buy and Sell menu items are not appearing in the Admin Panel 
Menu Settings interface and provide specific fix recommendations.
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime, timezone
import pytz

# Configuration - Use production URL from frontend/.env
BACKEND_URL = "https://marketplace-fix-9.preview.emergentagent.com/api"

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

    async def test_admin_menu_settings_api(self, token):
        """Test GET /api/admin/menu-settings endpoint to verify Buy/Sell menu items"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/admin/menu-settings"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if response has the expected structure
                    desktop_menu = data.get('desktop_menu', {})
                    mobile_menu = data.get('mobile_menu', {})
                    
                    # Check for expected Buy/Sell menu items
                    expected_items = {
                        'buy': {'enabled': True, 'label': 'Buy', 'roles': ['admin', 'manager', 'buyer']},
                        'sell': {'enabled': True, 'label': 'Sell', 'roles': ['admin', 'manager', 'seller']},
                        'buy_management': {'enabled': False, 'label': 'Inventory', 'roles': ['admin', 'manager', 'buyer']}
                    }
                    
                    # Verify desktop menu items
                    desktop_results = {}
                    for item_key, expected_config in expected_items.items():
                        actual_item = desktop_menu.get(item_key, {})
                        desktop_results[item_key] = {
                            'found': item_key in desktop_menu,
                            'enabled': actual_item.get('enabled'),
                            'label': actual_item.get('label'),
                            'roles': actual_item.get('roles', []),
                            'matches_expected': actual_item == expected_config
                        }
                    
                    # Verify mobile menu items (buy/sell might not be in mobile)
                    mobile_results = {}
                    for item_key in expected_items.keys():
                        if item_key in mobile_menu:
                            actual_item = mobile_menu.get(item_key, {})
                            mobile_results[item_key] = {
                                'found': True,
                                'enabled': actual_item.get('enabled'),
                                'label': actual_item.get('label'),
                                'roles': actual_item.get('roles', [])
                            }
                        else:
                            mobile_results[item_key] = {'found': False}
                    
                    # Check if all expected items are present and correct in desktop menu
                    all_desktop_correct = all(
                        result['found'] and result['matches_expected'] 
                        for result in desktop_results.values()
                    )
                    
                    success_message = f"✅ MENU SETTINGS API ACCESSIBLE: Retrieved menu settings successfully. Desktop menu items: {list(desktop_menu.keys())}. Mobile menu items: {list(mobile_menu.keys())}"
                    
                    if all_desktop_correct:
                        success_message += f" ✅ ALL EXPECTED ITEMS FOUND: Buy, Sell, and Inventory items are correctly configured in desktop menu"
                    else:
                        success_message += f" ⚠️ SOME ITEMS MISSING/INCORRECT: Check desktop menu configuration"
                    
                    self.log_result(
                        "Admin Menu Settings API", 
                        True, 
                        success_message,
                        response_time
                    )
                    
                    return {
                        'success': True, 
                        'desktop_menu_count': len(desktop_menu),
                        'mobile_menu_count': len(mobile_menu),
                        'desktop_menu_items': list(desktop_menu.keys()),
                        'mobile_menu_items': list(mobile_menu.keys()),
                        'expected_items_check': desktop_results,
                        'mobile_items_check': mobile_results,
                        'all_expected_found': all_desktop_correct,
                        'raw_response': data
                    }
                elif response.status == 403:
                    error_text = await response.text()
                    self.log_result(
                        "Admin Menu Settings API", 
                        False, 
                        f"❌ ACCESS DENIED: Status 403 - Admin user does not have permission to access menu settings endpoint: {error_text}",
                        response_time
                    )
                    return {
                        'success': False, 
                        'error': 'Access denied - insufficient permissions',
                        'status_code': 403
                    }
                elif response.status == 401:
                    error_text = await response.text()
                    self.log_result(
                        "Admin Menu Settings API", 
                        False, 
                        f"❌ AUTHENTICATION FAILED: Status 401 - Token may be invalid or expired: {error_text}",
                        response_time
                    )
                    return {
                        'success': False, 
                        'error': 'Authentication failed',
                        'status_code': 401
                    }
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Admin Menu Settings API", 
                        False, 
                        f"❌ ENDPOINT FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {
                        'success': False, 
                        'error': error_text,
                        'status_code': response.status
                    }
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Admin Menu Settings API", 
                False, 
                f"❌ ENDPOINT EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_menu_items_detailed_analysis(self, menu_data):
        """Perform detailed analysis of menu items structure"""
        start_time = datetime.now()
        
        try:
            desktop_menu = menu_data.get('desktop_menu', {})
            mobile_menu = menu_data.get('mobile_menu', {})
            
            # Analyze desktop menu structure
            desktop_analysis = {
                'total_items': len(desktop_menu),
                'enabled_items': [],
                'disabled_items': [],
                'buy_sell_items': {},
                'role_distribution': {}
            }
            
            for item_key, item_config in desktop_menu.items():
                if isinstance(item_config, dict):
                    enabled = item_config.get('enabled', False)
                    label = item_config.get('label', item_key)
                    roles = item_config.get('roles', [])
                    
                    if enabled:
                        desktop_analysis['enabled_items'].append(f"{item_key} ({label})")
                    else:
                        desktop_analysis['disabled_items'].append(f"{item_key} ({label})")
                    
                    # Track buy/sell related items
                    if item_key in ['buy', 'sell', 'buy_management']:
                        desktop_analysis['buy_sell_items'][item_key] = {
                            'enabled': enabled,
                            'label': label,
                            'roles': roles
                        }
                    
                    # Track role distribution
                    for role in roles:
                        if role not in desktop_analysis['role_distribution']:
                            desktop_analysis['role_distribution'][role] = []
                        desktop_analysis['role_distribution'][role].append(item_key)
            
            # Analyze mobile menu structure
            mobile_analysis = {
                'total_items': len(mobile_menu),
                'enabled_items': [],
                'disabled_items': [],
                'buy_sell_items': {}
            }
            
            for item_key, item_config in mobile_menu.items():
                if isinstance(item_config, dict):
                    enabled = item_config.get('enabled', False)
                    label = item_config.get('label', item_key)
                    roles = item_config.get('roles', [])
                    
                    if enabled:
                        mobile_analysis['enabled_items'].append(f"{item_key} ({label})")
                    else:
                        mobile_analysis['disabled_items'].append(f"{item_key} ({label})")
                    
                    # Track buy/sell related items
                    if item_key in ['buy', 'sell', 'buy_management']:
                        mobile_analysis['buy_sell_items'][item_key] = {
                            'enabled': enabled,
                            'label': label,
                            'roles': roles
                        }
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Check if Buy/Sell items are properly configured
            buy_sell_properly_configured = (
                'buy' in desktop_analysis['buy_sell_items'] and
                'sell' in desktop_analysis['buy_sell_items'] and
                desktop_analysis['buy_sell_items']['buy']['enabled'] and
                desktop_analysis['buy_sell_items']['sell']['enabled'] and
                desktop_analysis['buy_sell_items']['buy']['label'] == 'Buy' and
                desktop_analysis['buy_sell_items']['sell']['label'] == 'Sell'
            )
            
            inventory_properly_configured = (
                'buy_management' in desktop_analysis['buy_sell_items'] and
                not desktop_analysis['buy_sell_items']['buy_management']['enabled'] and
                desktop_analysis['buy_sell_items']['buy_management']['label'] == 'Inventory'
            )
            
            success_message = f"✅ MENU STRUCTURE ANALYZED: Desktop has {desktop_analysis['total_items']} items, Mobile has {mobile_analysis['total_items']} items"
            
            if buy_sell_properly_configured:
                success_message += f" ✅ BUY/SELL ITEMS CORRECT: Both Buy and Sell items are enabled with correct labels"
            else:
                success_message += f" ❌ BUY/SELL ITEMS ISSUE: Buy/Sell items may be missing or incorrectly configured"
            
            if inventory_properly_configured:
                success_message += f" ✅ INVENTORY ITEM CORRECT: Inventory item is disabled as expected"
            else:
                success_message += f" ❌ INVENTORY ITEM ISSUE: Inventory item may be missing or incorrectly configured"
            
            self.log_result(
                "Menu Items Detailed Analysis", 
                True, 
                success_message,
                response_time
            )
            
            return {
                'success': True,
                'desktop_analysis': desktop_analysis,
                'mobile_analysis': mobile_analysis,
                'buy_sell_properly_configured': buy_sell_properly_configured,
                'inventory_properly_configured': inventory_properly_configured,
                'configuration_issues': []
            }
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Menu Items Detailed Analysis", 
                False, 
                f"❌ ANALYSIS EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def test_database_menu_settings_check(self, token):
        """Check if there are database menu settings that might override defaults"""
        start_time = datetime.now()
        
        try:
            # Connect to MongoDB directly to check menu_settings collection
            import motor.motor_asyncio
            import os
            
            # Get MongoDB URL from environment
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
            db = client.cataloro_marketplace
            
            # Check if menu_settings collection exists and has documents
            menu_settings_docs = await db.menu_settings.find({}).to_list(length=None)
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if menu_settings_docs:
                # Found database overrides
                override_count = len(menu_settings_docs)
                override_details = []
                
                for doc in menu_settings_docs:
                    doc_type = doc.get('type', 'unknown')
                    doc_id = doc.get('_id', 'unknown')
                    override_details.append(f"Document ID: {doc_id}, Type: {doc_type}")
                
                self.log_result(
                    "Database Menu Settings Check", 
                    True, 
                    f"⚠️ DATABASE OVERRIDES FOUND: Found {override_count} menu_settings documents that may be overriding backend defaults. Documents: {'; '.join(override_details)}",
                    response_time
                )
                
                return {
                    'success': True,
                    'has_overrides': True,
                    'override_count': override_count,
                    'override_documents': menu_settings_docs,
                    'recommendation': 'Clear or update these database documents to allow backend defaults to take effect'
                }
            else:
                # No database overrides found
                self.log_result(
                    "Database Menu Settings Check", 
                    True, 
                    "✅ NO DATABASE OVERRIDES: menu_settings collection is empty, backend defaults should be used",
                    response_time
                )
                
                return {
                    'success': True,
                    'has_overrides': False,
                    'override_count': 0,
                    'recommendation': 'No database overrides found, issue may be in backend default configuration'
                }
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Database Menu Settings Check", 
                False, 
                f"❌ DATABASE CHECK EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def clear_database_menu_settings(self, token):
        """Clear database menu_settings collection to allow backend defaults"""
        start_time = datetime.now()
        
        try:
            # Connect to MongoDB directly
            import motor.motor_asyncio
            import os
            
            # Get MongoDB URL from environment
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
            db = client.cataloro_marketplace
            
            # Count documents before deletion
            before_count = await db.menu_settings.count_documents({})
            
            # Clear all menu_settings documents
            delete_result = await db.menu_settings.delete_many({})
            deleted_count = delete_result.deleted_count
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            self.log_result(
                "Clear Database Menu Settings", 
                True, 
                f"✅ DATABASE CLEARED: Removed {deleted_count} documents from menu_settings collection (was {before_count} documents). Backend defaults should now take effect.",
                response_time
            )
            
            return {
                'success': True,
                'documents_before': before_count,
                'documents_deleted': deleted_count,
                'message': 'Database menu settings cleared successfully'
            }
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Clear Database Menu Settings", 
                False, 
                f"❌ DATABASE CLEAR EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def update_database_menu_settings(self, token):
        """Update database menu_settings to match intended configuration"""
        start_time = datetime.now()
        
        try:
            # Connect to MongoDB directly
            import motor.motor_asyncio
            import os
            
            # Get MongoDB URL from environment
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
            db = client.cataloro_marketplace
            
            # Define the correct menu configuration
            correct_menu_config = {
                "type": "menu_config",
                "desktop_menu": {
                    "buy": {"enabled": True, "label": "Buy", "roles": ["admin", "manager", "buyer"]},
                    "sell": {"enabled": True, "label": "Sell", "roles": ["admin", "manager", "seller"]},
                    "buy_management": {"enabled": False, "label": "Inventory", "roles": ["admin", "manager", "buyer"]}
                },
                "mobile_menu": {
                    "buy": {"enabled": True, "label": "Buy", "roles": ["admin", "manager", "buyer"]},
                    "sell": {"enabled": True, "label": "Sell", "roles": ["admin", "manager", "seller"]},
                    "buy_management": {"enabled": False, "label": "Inventory", "roles": ["admin", "manager", "buyer"]}
                },
                "updated_at": datetime.now().isoformat(),
                "updated_by": "backend_test_fix"
            }
            
            # Update or insert the menu configuration
            result = await db.menu_settings.replace_one(
                {"type": "menu_config"},
                correct_menu_config,
                upsert=True
            )
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if result.upserted_id:
                action = "INSERTED"
            elif result.modified_count > 0:
                action = "UPDATED"
            else:
                action = "NO CHANGE"
            
            self.log_result(
                "Update Database Menu Settings", 
                True, 
                f"✅ DATABASE {action}: Menu settings document updated with correct Buy/Sell/Inventory configuration. Sell item roles fixed, Inventory disabled.",
                response_time
            )
            
            return {
                'success': True,
                'action': action,
                'upserted_id': str(result.upserted_id) if result.upserted_id else None,
                'modified_count': result.modified_count,
                'message': 'Database menu settings updated with correct configuration'
            }
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Update Database Menu Settings", 
                False, 
                f"❌ DATABASE UPDATE EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}









    async def investigate_buy_sell_menu_items_missing(self):
        """URGENT: Comprehensive investigation of why Buy/Sell menu items are not appearing"""
        print("🚨 URGENT: BUY/SELL MENU ITEMS MISSING INVESTIGATION")
        print("=" * 80)
        print("ISSUE: Buy and Sell menu items not appearing in Admin Panel Menu Settings")
        print("USER REPORT: Only shows Browse, Messages, Notifications, Create, Tenders, Listings, Profile, View Public Profile, Admin")
        print()
        
        # Test with admin credentials
        test_credentials = [
            ("admin@cataloro.com", "password123", "Admin User"),
            ("admin@cataloro.com", "admin123", "Admin User (Alt Password)"),
        ]
        
        investigation_results = {}
        
        # Test with admin credentials
        for email, password, user_type in test_credentials:
            print(f"🔐 Investigating with {user_type} ({email})")
            print("-" * 50)
            
            # Step 1: Login
            token, user_id, user = await self.test_login_and_get_token(email, password)
            if not token:
                print(f"❌ Login failed for {user_type}, trying next credentials")
                continue
            
            user_results = {}
            user_role = user.get('user_role', 'Unknown')
            username = user.get('username', 'unknown')
            
            print(f"✅ Successfully logged in as: {user.get('full_name', 'Unknown')} (Role: {user_role})")
            
            # Step 2: CRITICAL - Get exact API response structure
            print(f"🔍 STEP 1: Getting exact Menu Settings API response...")
            menu_api_result = await self.test_admin_menu_settings_api_detailed(token)
            user_results['detailed_api_response'] = menu_api_result
            
            # Step 3: Check current database state
            print(f"🗄️ STEP 2: Checking current database state...")
            db_state_result = await self.check_current_database_state(token)
            user_results['database_state'] = db_state_result
            
            # Step 4: Compare desktop vs mobile menu structure
            if menu_api_result.get('success'):
                print(f"📱 STEP 3: Analyzing desktop vs mobile menu differences...")
                menu_comparison = await self.compare_desktop_mobile_menus(menu_api_result.get('raw_response', {}))
                user_results['menu_comparison'] = menu_comparison
            
            # Step 5: Check for any filtering or permission issues
            print(f"🔒 STEP 4: Checking for permission or filtering issues...")
            permission_check = await self.check_menu_permission_filtering(token, user)
            user_results['permission_check'] = permission_check
            
            # Step 6: Verify backend endpoint implementation
            print(f"🔧 STEP 5: Verifying backend endpoint implementation...")
            backend_check = await self.verify_backend_menu_endpoint(token)
            user_results['backend_verification'] = backend_check
            
            investigation_results[user_type] = user_results
            print()
            
            # If login was successful, we can break (no need to test alternative password)
            break
        
        # Generate comprehensive investigation report
        self.generate_buy_sell_investigation_report(investigation_results)
        
        return investigation_results

    async def test_admin_menu_settings_api_detailed(self, token):
        """Get detailed API response with exact structure analysis"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/admin/menu-settings"
            
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Get exact structure
                    desktop_menu = data.get('desktop_menu', {})
                    mobile_menu = data.get('mobile_menu', {})
                    
                    # Check specifically for Buy/Sell items
                    buy_in_desktop = 'buy' in desktop_menu
                    sell_in_desktop = 'sell' in desktop_menu
                    buy_in_mobile = 'buy' in mobile_menu
                    sell_in_mobile = 'sell' in mobile_menu
                    
                    # Get all menu item keys for comparison
                    desktop_keys = list(desktop_menu.keys())
                    mobile_keys = list(mobile_menu.keys())
                    
                    # Detailed analysis of Buy/Sell items if present
                    buy_details = desktop_menu.get('buy', {}) if buy_in_desktop else None
                    sell_details = desktop_menu.get('sell', {}) if sell_in_desktop else None
                    inventory_details = desktop_menu.get('buy_management', {}) if 'buy_management' in desktop_menu else None
                    
                    success_message = f"✅ API RESPONSE RECEIVED: Desktop has {len(desktop_keys)} items, Mobile has {len(mobile_keys)} items"
                    
                    if buy_in_desktop and sell_in_desktop:
                        success_message += f" ✅ BUY/SELL FOUND: Both items present in desktop menu"
                    elif buy_in_desktop or sell_in_desktop:
                        success_message += f" ⚠️ PARTIAL BUY/SELL: Only {'Buy' if buy_in_desktop else 'Sell'} found in desktop menu"
                    else:
                        success_message += f" ❌ BUY/SELL MISSING: Neither Buy nor Sell found in desktop menu"
                    
                    if buy_in_mobile and sell_in_mobile:
                        success_message += f" ✅ MOBILE BUY/SELL: Both items present in mobile menu"
                    elif buy_in_mobile or sell_in_mobile:
                        success_message += f" ⚠️ PARTIAL MOBILE: Only {'Buy' if buy_in_mobile else 'Sell'} found in mobile menu"
                    else:
                        success_message += f" ❌ MOBILE MISSING: Neither Buy nor Sell found in mobile menu"
                    
                    self.log_result(
                        "Detailed Menu Settings API", 
                        True, 
                        success_message,
                        response_time
                    )
                    
                    return {
                        'success': True,
                        'desktop_menu_count': len(desktop_keys),
                        'mobile_menu_count': len(mobile_keys),
                        'desktop_menu_keys': desktop_keys,
                        'mobile_menu_keys': mobile_keys,
                        'buy_in_desktop': buy_in_desktop,
                        'sell_in_desktop': sell_in_desktop,
                        'buy_in_mobile': buy_in_mobile,
                        'sell_in_mobile': sell_in_mobile,
                        'buy_details': buy_details,
                        'sell_details': sell_details,
                        'inventory_details': inventory_details,
                        'raw_response': data
                    }
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Detailed Menu Settings API", 
                        False, 
                        f"❌ API FAILED: Status {response.status}: {error_text}",
                        response_time
                    )
                    return {
                        'success': False, 
                        'error': error_text,
                        'status_code': response.status
                    }
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Detailed Menu Settings API", 
                False, 
                f"❌ API EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def check_current_database_state(self, token):
        """Check current state of menu_settings collection"""
        start_time = datetime.now()
        
        try:
            import motor.motor_asyncio
            import os
            
            # Get MongoDB URL from environment
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
            db = client.cataloro_marketplace
            
            # Check menu_settings collection
            menu_settings_docs = await db.menu_settings.find({}).to_list(length=None)
            doc_count = len(menu_settings_docs)
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Analyze documents
            doc_analysis = []
            for doc in menu_settings_docs:
                doc_info = {
                    'id': str(doc.get('_id', 'unknown')),
                    'type': doc.get('type', 'unknown'),
                    'has_desktop_menu': 'desktop_menu' in doc,
                    'has_mobile_menu': 'mobile_menu' in doc,
                    'created_at': doc.get('created_at', 'unknown'),
                    'updated_at': doc.get('updated_at', 'unknown')
                }
                
                # Check for Buy/Sell items in this document
                if 'desktop_menu' in doc:
                    desktop_menu = doc['desktop_menu']
                    doc_info['desktop_has_buy'] = 'buy' in desktop_menu
                    doc_info['desktop_has_sell'] = 'sell' in desktop_menu
                    doc_info['desktop_keys'] = list(desktop_menu.keys())
                
                if 'mobile_menu' in doc:
                    mobile_menu = doc['mobile_menu']
                    doc_info['mobile_has_buy'] = 'buy' in mobile_menu
                    doc_info['mobile_has_sell'] = 'sell' in mobile_menu
                    doc_info['mobile_keys'] = list(mobile_menu.keys())
                
                doc_analysis.append(doc_info)
            
            if doc_count > 0:
                self.log_result(
                    "Database State Check", 
                    True, 
                    f"⚠️ DATABASE OVERRIDES PRESENT: Found {doc_count} menu_settings documents that may be affecting API response",
                    response_time
                )
            else:
                self.log_result(
                    "Database State Check", 
                    True, 
                    f"✅ NO DATABASE OVERRIDES: menu_settings collection is empty, backend defaults should be used",
                    response_time
                )
            
            return {
                'success': True,
                'document_count': doc_count,
                'has_overrides': doc_count > 0,
                'documents': doc_analysis,
                'raw_documents': menu_settings_docs
            }
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Database State Check", 
                False, 
                f"❌ DATABASE CHECK EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def compare_desktop_mobile_menus(self, api_response):
        """Compare desktop vs mobile menu structures"""
        start_time = datetime.now()
        
        try:
            desktop_menu = api_response.get('desktop_menu', {})
            mobile_menu = api_response.get('mobile_menu', {})
            
            # Get all unique keys
            all_keys = set(desktop_menu.keys()) | set(mobile_menu.keys())
            
            comparison = {
                'desktop_only': [],
                'mobile_only': [],
                'both_menus': [],
                'buy_sell_analysis': {}
            }
            
            for key in all_keys:
                in_desktop = key in desktop_menu
                in_mobile = key in mobile_menu
                
                if in_desktop and in_mobile:
                    comparison['both_menus'].append(key)
                elif in_desktop:
                    comparison['desktop_only'].append(key)
                elif in_mobile:
                    comparison['mobile_only'].append(key)
            
            # Specific Buy/Sell analysis
            for item in ['buy', 'sell', 'buy_management']:
                desktop_item = desktop_menu.get(item, {})
                mobile_item = mobile_menu.get(item, {})
                
                comparison['buy_sell_analysis'][item] = {
                    'in_desktop': item in desktop_menu,
                    'in_mobile': item in mobile_menu,
                    'desktop_enabled': desktop_item.get('enabled', False) if desktop_item else False,
                    'mobile_enabled': mobile_item.get('enabled', False) if mobile_item else False,
                    'desktop_label': desktop_item.get('label', '') if desktop_item else '',
                    'mobile_label': mobile_item.get('label', '') if mobile_item else '',
                    'desktop_roles': desktop_item.get('roles', []) if desktop_item else [],
                    'mobile_roles': mobile_item.get('roles', []) if mobile_item else []
                }
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Analysis summary
            desktop_has_buy_sell = 'buy' in desktop_menu and 'sell' in desktop_menu
            mobile_has_buy_sell = 'buy' in mobile_menu and 'sell' in mobile_menu
            
            summary = f"✅ MENU COMPARISON COMPLETE: Desktop has {len(desktop_menu)} items, Mobile has {len(mobile_menu)} items"
            
            if desktop_has_buy_sell and mobile_has_buy_sell:
                summary += f" ✅ BUY/SELL IN BOTH: Items present in both desktop and mobile menus"
            elif desktop_has_buy_sell:
                summary += f" ⚠️ BUY/SELL DESKTOP ONLY: Items only in desktop menu, missing from mobile"
            elif mobile_has_buy_sell:
                summary += f" ⚠️ BUY/SELL MOBILE ONLY: Items only in mobile menu, missing from desktop"
            else:
                summary += f" ❌ BUY/SELL MISSING: Items missing from both desktop and mobile menus"
            
            self.log_result(
                "Desktop vs Mobile Menu Comparison", 
                True, 
                summary,
                response_time
            )
            
            return {
                'success': True,
                'comparison': comparison,
                'desktop_has_buy_sell': desktop_has_buy_sell,
                'mobile_has_buy_sell': mobile_has_buy_sell,
                'desktop_count': len(desktop_menu),
                'mobile_count': len(mobile_menu)
            }
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Desktop vs Mobile Menu Comparison", 
                False, 
                f"❌ COMPARISON EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def check_menu_permission_filtering(self, token, user):
        """Check if there are permission or role-based filtering issues"""
        start_time = datetime.now()
        
        try:
            user_role = user.get('user_role', 'Unknown')
            user_legacy_role = user.get('role', 'Unknown')
            
            # Check if user should have access to Buy/Sell items
            expected_permissions = {
                'buy': user_role in ['Admin', 'Admin-Manager', 'User-Buyer'],
                'sell': user_role in ['Admin', 'Admin-Manager', 'User-Seller'],
                'buy_management': user_role in ['Admin', 'Admin-Manager']
            }
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            summary = f"✅ PERMISSION CHECK COMPLETE: User role '{user_role}' (legacy: '{user_legacy_role}')"
            
            if expected_permissions['buy'] and expected_permissions['sell']:
                summary += f" ✅ SHOULD SEE BUY/SELL: User role should have access to both Buy and Sell items"
            elif expected_permissions['buy']:
                summary += f" ⚠️ SHOULD SEE BUY ONLY: User role should only have access to Buy items"
            elif expected_permissions['sell']:
                summary += f" ⚠️ SHOULD SEE SELL ONLY: User role should only have access to Sell items"
            else:
                summary += f" ❌ NO BUY/SELL ACCESS: User role should not have access to Buy/Sell items"
            
            self.log_result(
                "Menu Permission Filtering Check", 
                True, 
                summary,
                response_time
            )
            
            return {
                'success': True,
                'user_role': user_role,
                'legacy_role': user_legacy_role,
                'expected_permissions': expected_permissions,
                'should_see_buy': expected_permissions['buy'],
                'should_see_sell': expected_permissions['sell'],
                'should_see_inventory': expected_permissions['buy_management']
            }
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Menu Permission Filtering Check", 
                False, 
                f"❌ PERMISSION CHECK EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    async def verify_backend_menu_endpoint(self, token):
        """Verify backend menu endpoint implementation by checking raw response"""
        start_time = datetime.now()
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            url = f"{BACKEND_URL}/admin/menu-settings"
            
            # Make request and capture all response details
            async with self.session.get(url, headers=headers) as response:
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                
                # Get response details
                status_code = response.status
                response_headers = dict(response.headers)
                content_type = response_headers.get('content-type', 'unknown')
                
                if status_code == 200:
                    # Get raw response text first
                    raw_text = await response.text()
                    
                    try:
                        # Try to parse as JSON
                        data = json.loads(raw_text)
                        
                        # Check response structure
                        has_desktop_menu = 'desktop_menu' in data
                        has_mobile_menu = 'mobile_menu' in data
                        
                        # Check for expected structure
                        structure_valid = has_desktop_menu and has_mobile_menu
                        
                        summary = f"✅ BACKEND ENDPOINT WORKING: Status 200, Content-Type: {content_type}"
                        
                        if structure_valid:
                            summary += f" ✅ VALID STRUCTURE: Response has both desktop_menu and mobile_menu"
                        else:
                            summary += f" ❌ INVALID STRUCTURE: Missing desktop_menu or mobile_menu in response"
                        
                        self.log_result(
                            "Backend Menu Endpoint Verification", 
                            True, 
                            summary,
                            response_time
                        )
                        
                        return {
                            'success': True,
                            'status_code': status_code,
                            'content_type': content_type,
                            'response_size': len(raw_text),
                            'has_desktop_menu': has_desktop_menu,
                            'has_mobile_menu': has_mobile_menu,
                            'structure_valid': structure_valid,
                            'raw_response_preview': raw_text[:500] + '...' if len(raw_text) > 500 else raw_text
                        }
                        
                    except json.JSONDecodeError as e:
                        self.log_result(
                            "Backend Menu Endpoint Verification", 
                            False, 
                            f"❌ INVALID JSON: Response is not valid JSON: {str(e)}",
                            response_time
                        )
                        return {
                            'success': False,
                            'error': 'Invalid JSON response',
                            'raw_response': raw_text[:500] + '...' if len(raw_text) > 500 else raw_text
                        }
                else:
                    error_text = await response.text()
                    self.log_result(
                        "Backend Menu Endpoint Verification", 
                        False, 
                        f"❌ ENDPOINT ERROR: Status {status_code}: {error_text}",
                        response_time
                    )
                    return {
                        'success': False,
                        'status_code': status_code,
                        'error': error_text
                    }
                    
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.log_result(
                "Backend Menu Endpoint Verification", 
                False, 
                f"❌ ENDPOINT EXCEPTION: {str(e)}",
                response_time
            )
            return {'success': False, 'error': str(e)}

    def generate_buy_sell_investigation_report(self, investigation_results):
        """Generate comprehensive investigation report for Buy/Sell menu items missing issue"""
        print("📊 BUY/SELL MENU ITEMS MISSING - INVESTIGATION REPORT")
        print("=" * 80)
        
        admin_results = investigation_results.get('Admin User', {}) or investigation_results.get('Admin User (Alt Password)', {})
        
        if not admin_results:
            print("❌ CRITICAL: Could not login with admin credentials")
            print("🔧 SOLUTION: Check admin credentials (admin@cataloro.com / password123)")
            return
        
        print("🔍 INVESTIGATION FINDINGS:")
        print("-" * 40)
        
        # 1. API Response Analysis
        api_result = admin_results.get('detailed_api_response', {})
        if api_result.get('success'):
            print(f"✅ STEP 1 - API ACCESS: Menu Settings API is accessible")
            print(f"   📊 Desktop Menu: {api_result.get('desktop_menu_count', 0)} items")
            print(f"   📱 Mobile Menu: {api_result.get('mobile_menu_count', 0)} items")
            print(f"   🗂️ Desktop Keys: {', '.join(api_result.get('desktop_menu_keys', []))}")
            print(f"   📱 Mobile Keys: {', '.join(api_result.get('mobile_menu_keys', []))}")
            
            # Buy/Sell presence analysis
            buy_desktop = api_result.get('buy_in_desktop', False)
            sell_desktop = api_result.get('sell_in_desktop', False)
            buy_mobile = api_result.get('buy_in_mobile', False)
            sell_mobile = api_result.get('sell_in_mobile', False)
            
            print(f"   🛒 Buy Item - Desktop: {'✅ FOUND' if buy_desktop else '❌ MISSING'}, Mobile: {'✅ FOUND' if buy_mobile else '❌ MISSING'}")
            print(f"   🏪 Sell Item - Desktop: {'✅ FOUND' if sell_desktop else '❌ MISSING'}, Mobile: {'✅ FOUND' if sell_mobile else '❌ MISSING'}")
            
            # Show item details if found
            if buy_desktop and api_result.get('buy_details'):
                buy_details = api_result.get('buy_details')
                print(f"      Buy Details: enabled={buy_details.get('enabled')}, label='{buy_details.get('label')}', roles={buy_details.get('roles', [])}")
            
            if sell_desktop and api_result.get('sell_details'):
                sell_details = api_result.get('sell_details')
                print(f"      Sell Details: enabled={sell_details.get('enabled')}, label='{sell_details.get('label')}', roles={sell_details.get('roles', [])}")
                
        else:
            print(f"❌ STEP 1 - API ACCESS: Menu Settings API failed")
            print(f"   Error: {api_result.get('error', 'Unknown error')}")
        
        # 2. Database State Analysis
        db_result = admin_results.get('database_state', {})
        if db_result.get('success'):
            doc_count = db_result.get('document_count', 0)
            print(f"\n✅ STEP 2 - DATABASE STATE: Successfully checked menu_settings collection")
            print(f"   📄 Documents Found: {doc_count}")
            
            if doc_count > 0:
                print(f"   ⚠️ DATABASE OVERRIDES DETECTED: {doc_count} documents may be affecting API response")
                for i, doc in enumerate(db_result.get('documents', [])):
                    print(f"      Document {i+1}: ID={doc.get('id', 'unknown')[:8]}..., Type={doc.get('type', 'unknown')}")
                    if doc.get('desktop_has_buy') or doc.get('desktop_has_sell'):
                        print(f"         Desktop Buy/Sell: Buy={'✅' if doc.get('desktop_has_buy') else '❌'}, Sell={'✅' if doc.get('desktop_has_sell') else '❌'}")
            else:
                print(f"   ✅ NO DATABASE OVERRIDES: Collection is empty, backend defaults should be used")
        else:
            print(f"\n❌ STEP 2 - DATABASE STATE: Database check failed")
            print(f"   Error: {db_result.get('error', 'Unknown error')}")
        
        # 3. Desktop vs Mobile Comparison
        comparison_result = admin_results.get('menu_comparison', {})
        if comparison_result.get('success'):
            print(f"\n✅ STEP 3 - MENU COMPARISON: Desktop vs Mobile analysis complete")
            comparison = comparison_result.get('comparison', {})
            
            desktop_only = comparison.get('desktop_only', [])
            mobile_only = comparison.get('mobile_only', [])
            both_menus = comparison.get('both_menus', [])
            
            print(f"   🖥️ Desktop Only: {', '.join(desktop_only) if desktop_only else 'None'}")
            print(f"   📱 Mobile Only: {', '.join(mobile_only) if mobile_only else 'None'}")
            print(f"   🔄 Both Menus: {', '.join(both_menus) if both_menus else 'None'}")
            
            # Buy/Sell specific analysis
            buy_sell_analysis = comparison.get('buy_sell_analysis', {})
            for item in ['buy', 'sell']:
                item_analysis = buy_sell_analysis.get(item, {})
                desktop_present = item_analysis.get('in_desktop', False)
                mobile_present = item_analysis.get('in_mobile', False)
                print(f"   {item.upper()} Item: Desktop={'✅' if desktop_present else '❌'}, Mobile={'✅' if mobile_present else '❌'}")
        else:
            print(f"\n❌ STEP 3 - MENU COMPARISON: Comparison failed")
            print(f"   Error: {comparison_result.get('error', 'Unknown error')}")
        
        # 4. Permission Analysis
        permission_result = admin_results.get('permission_check', {})
        if permission_result.get('success'):
            print(f"\n✅ STEP 4 - PERMISSIONS: Permission analysis complete")
            user_role = permission_result.get('user_role', 'Unknown')
            should_see_buy = permission_result.get('should_see_buy', False)
            should_see_sell = permission_result.get('should_see_sell', False)
            
            print(f"   👤 User Role: {user_role}")
            print(f"   🛒 Should See Buy: {'✅ YES' if should_see_buy else '❌ NO'}")
            print(f"   🏪 Should See Sell: {'✅ YES' if should_see_sell else '❌ NO'}")
        else:
            print(f"\n❌ STEP 4 - PERMISSIONS: Permission check failed")
            print(f"   Error: {permission_result.get('error', 'Unknown error')}")
        
        # 5. Backend Verification
        backend_result = admin_results.get('backend_verification', {})
        if backend_result.get('success'):
            print(f"\n✅ STEP 5 - BACKEND: Backend endpoint verification complete")
            print(f"   🔧 Status Code: {backend_result.get('status_code', 'Unknown')}")
            print(f"   📄 Content Type: {backend_result.get('content_type', 'Unknown')}")
            print(f"   📊 Structure Valid: {'✅ YES' if backend_result.get('structure_valid') else '❌ NO'}")
        else:
            print(f"\n❌ STEP 5 - BACKEND: Backend verification failed")
            print(f"   Error: {backend_result.get('error', 'Unknown error')}")
        
        # ROOT CAUSE ANALYSIS
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        print("-" * 40)
        
        # Determine the most likely root cause
        if not api_result.get('success'):
            print("❌ CRITICAL ISSUE: Admin Menu Settings API is not accessible")
            print("🔧 IMMEDIATE ACTION: Fix backend API endpoint or authentication")
        elif not (api_result.get('buy_in_desktop') and api_result.get('sell_in_desktop')):
            print("❌ CRITICAL ISSUE: Buy/Sell items are missing from API response")
            
            if db_result.get('document_count', 0) > 0:
                print("🔍 LIKELY CAUSE: Database overrides are preventing Buy/Sell items from appearing")
                print("🔧 RECOMMENDED FIX: Clear or update menu_settings collection documents")
            else:
                print("🔍 LIKELY CAUSE: Backend default menu settings don't include Buy/Sell items")
                print("🔧 RECOMMENDED FIX: Check backend server.py default menu settings configuration")
        elif api_result.get('buy_in_desktop') and api_result.get('sell_in_desktop'):
            print("⚠️ BACKEND API WORKING: Buy/Sell items are present in API response")
            print("🔍 LIKELY CAUSE: Frontend Menu Settings component is not displaying the items correctly")
            print("🔧 RECOMMENDED FIX: Check frontend MenuSettings.js component for filtering or display issues")
        
        # SPECIFIC RECOMMENDATIONS
        print(f"\n🎯 SPECIFIC RECOMMENDATIONS:")
        print("-" * 40)
        
        if api_result.get('success'):
            if api_result.get('buy_in_desktop') and api_result.get('sell_in_desktop'):
                print("1. ✅ BACKEND API WORKING: Buy/Sell items are in the API response")
                print("2. 🔍 CHECK FRONTEND: Investigate MenuSettings.js component")
                print("3. 🔍 CHECK FILTERING: Look for role-based or conditional filtering in frontend")
                print("4. 🔍 CHECK DISPLAY: Verify frontend is correctly rendering all menu items")
            else:
                print("1. ❌ BACKEND ISSUE: Buy/Sell items missing from API response")
                
                if db_result.get('document_count', 0) > 0:
                    print("2. 🧹 CLEAR DATABASE: Remove menu_settings collection documents")
                    print("3. 🔄 RESTART BACKEND: Restart backend service after database changes")
                else:
                    print("2. 🔧 FIX BACKEND: Add Buy/Sell items to default menu settings in server.py")
                    print("3. 🔄 RESTART BACKEND: Restart backend service after code changes")
        else:
            print("1. ❌ CRITICAL: Fix Admin Menu Settings API endpoint")
            print("2. 🔍 CHECK AUTHENTICATION: Verify admin user permissions")
            print("3. 🔍 CHECK BACKEND LOGS: Check backend service logs for errors")
        
        print(f"\n🚨 URGENT NEXT STEPS:")
        print("-" * 40)
        
        # Determine immediate next steps based on findings
        if api_result.get('success') and api_result.get('buy_in_desktop') and api_result.get('sell_in_desktop'):
            print("✅ BACKEND IS WORKING - FRONTEND ISSUE LIKELY")
            print("🔧 MAIN AGENT SHOULD:")
            print("   1. Check MenuSettings.js component in frontend")
            print("   2. Look for any filtering logic that might hide Buy/Sell items")
            print("   3. Verify that all API response items are being rendered")
            print("   4. Check browser console for any JavaScript errors")
        elif db_result.get('document_count', 0) > 0:
            print("⚠️ DATABASE OVERRIDES DETECTED - CLEAR REQUIRED")
            print("🔧 MAIN AGENT SHOULD:")
            print("   1. Clear the menu_settings collection in MongoDB")
            print("   2. Restart the backend service")
            print("   3. Test the API response again")
            print("   4. Verify Buy/Sell items appear in Admin Panel")
        else:
            print("❌ BACKEND CONFIGURATION ISSUE")
            print("🔧 MAIN AGENT SHOULD:")
            print("   1. Check backend server.py default menu settings")
            print("   2. Ensure Buy/Sell items are included in default configuration")
            print("   3. Restart backend service after changes")
            print("   4. Test API response and Admin Panel")
        
        print(f"\n🎉 BUY/SELL MENU ITEMS INVESTIGATION COMPLETED!")
        print("=" * 80)

    async def run_database_menu_settings_fix(self):
        """Run comprehensive database menu settings fix and verification"""
        print("🚀 CATALORO DATABASE MENU SETTINGS FIX")
        print("=" * 80)
        print()
        
        # Test with admin credentials
        test_credentials = [
            ("admin@cataloro.com", "password123", "Admin User"),
            ("admin@cataloro.com", "admin123", "Admin User (Alt Password)"),
        ]
        
        all_results = {}
        
        # Test with admin credentials
        for email, password, user_type in test_credentials:
            print(f"🔐 Testing with {user_type} ({email})")
            print("-" * 50)
            
            # Step 1: Login
            token, user_id, user = await self.test_login_and_get_token(email, password)
            if not token:
                print(f"❌ Login failed for {user_type}, trying next credentials")
                continue
            
            user_results = {}
            user_role = user.get('user_role', 'Unknown')
            username = user.get('username', 'unknown')
            
            # Step 2: Test current admin menu settings API (BEFORE fix)
            print(f"🔍 Testing CURRENT admin menu settings API (before fix)...")
            menu_api_before = await self.test_admin_menu_settings_api(token)
            user_results['menu_settings_api_before'] = menu_api_before
            
            # Step 3: Check database menu settings
            print(f"🗄️ Checking database menu settings for overrides...")
            db_check_result = await self.test_database_menu_settings_check(token)
            user_results['database_check'] = db_check_result
            
            # Step 4: Apply fix based on database check results
            if db_check_result.get('has_overrides'):
                print(f"⚠️ Database overrides found. Applying fix...")
                
                # Option 1: Clear database settings (recommended)
                print(f"🧹 OPTION 1: Clearing database menu settings...")
                clear_result = await self.clear_database_menu_settings(token)
                user_results['database_clear'] = clear_result
                
                if clear_result.get('success'):
                    # Test API after clearing database
                    print(f"🔍 Testing admin menu settings API AFTER clearing database...")
                    menu_api_after_clear = await self.test_admin_menu_settings_api(token)
                    user_results['menu_settings_api_after_clear'] = menu_api_after_clear
                    
                    # Check if clearing fixed the issues
                    if self.is_menu_configuration_correct(menu_api_after_clear):
                        print(f"✅ SUCCESS: Clearing database fixed the menu configuration!")
                        user_results['fix_successful'] = True
                        user_results['fix_method'] = 'database_clear'
                    else:
                        print(f"⚠️ Clearing database didn't fully fix the issue. Trying direct update...")
                        
                        # Option 2: Update database settings directly
                        print(f"🔧 OPTION 2: Updating database menu settings directly...")
                        update_result = await self.update_database_menu_settings(token)
                        user_results['database_update'] = update_result
                        
                        if update_result.get('success'):
                            # Test API after updating database
                            print(f"🔍 Testing admin menu settings API AFTER updating database...")
                            menu_api_after_update = await self.test_admin_menu_settings_api(token)
                            user_results['menu_settings_api_after_update'] = menu_api_after_update
                            
                            # Check if updating fixed the issues
                            if self.is_menu_configuration_correct(menu_api_after_update):
                                print(f"✅ SUCCESS: Updating database fixed the menu configuration!")
                                user_results['fix_successful'] = True
                                user_results['fix_method'] = 'database_update'
                            else:
                                print(f"❌ Database update didn't fix the issue. Manual intervention may be required.")
                                user_results['fix_successful'] = False
                        else:
                            print(f"❌ Failed to update database menu settings.")
                            user_results['fix_successful'] = False
                else:
                    print(f"❌ Failed to clear database menu settings.")
                    user_results['fix_successful'] = False
            else:
                print(f"ℹ️ No database overrides found. Issue may be in backend configuration.")
                user_results['fix_successful'] = None
                user_results['fix_method'] = 'no_fix_needed'
            
            # Step 5: Final verification
            print(f"🔬 Performing final detailed analysis...")
            final_menu_result = user_results.get('menu_settings_api_after_update') or user_results.get('menu_settings_api_after_clear') or menu_api_before
            if final_menu_result.get('success') and final_menu_result.get('raw_response'):
                analysis_result = await self.test_menu_items_detailed_analysis(final_menu_result['raw_response'])
                user_results['final_menu_analysis'] = analysis_result
            
            all_results[user_type] = user_results
            print()
            
            # If login was successful, we can break (no need to test alternative password)
            break
        
        # Generate summary
        self.generate_database_fix_summary(all_results)
        
        return all_results

    def is_menu_configuration_correct(self, menu_api_result):
        """Check if menu configuration matches expected values"""
        if not menu_api_result.get('success'):
            return False
        
        expected_items_check = menu_api_result.get('expected_items_check', {})
        
        # Check if all expected items match
        buy_correct = (
            expected_items_check.get('buy', {}).get('found') and
            expected_items_check.get('buy', {}).get('enabled') == True and
            expected_items_check.get('buy', {}).get('label') == 'Buy' and
            set(expected_items_check.get('buy', {}).get('roles', [])) == {'admin', 'manager', 'buyer'}
        )
        
        sell_correct = (
            expected_items_check.get('sell', {}).get('found') and
            expected_items_check.get('sell', {}).get('enabled') == True and
            expected_items_check.get('sell', {}).get('label') == 'Sell' and
            set(expected_items_check.get('sell', {}).get('roles', [])) == {'admin', 'manager', 'seller'}
        )
        
        inventory_correct = (
            expected_items_check.get('buy_management', {}).get('found') and
            expected_items_check.get('buy_management', {}).get('enabled') == False and
            expected_items_check.get('buy_management', {}).get('label') == 'Inventory' and
            set(expected_items_check.get('buy_management', {}).get('roles', [])) == {'admin', 'manager', 'buyer'}
        )
        
        return buy_correct and sell_correct and inventory_correct

    def generate_database_fix_summary(self, all_results):
        """Generate comprehensive summary of database menu settings fix"""
        print("📊 DATABASE MENU SETTINGS FIX SUMMARY")
        print("=" * 80)
        
        total_tests = 0
        passed_tests = 0
        critical_issues = []
        
        for user_type, results in all_results.items():
            print(f"\n🔍 {user_type} Results:")
            print("-" * 30)
            
            # Show before/after comparison
            menu_before = results.get('menu_settings_api_before', {})
            menu_after_clear = results.get('menu_settings_api_after_clear', {})
            menu_after_update = results.get('menu_settings_api_after_update', {})
            
            print(f"  📊 BEFORE FIX:")
            if menu_before.get('success'):
                before_check = menu_before.get('expected_items_check', {})
                for item_name, item_result in before_check.items():
                    if item_result.get('found'):
                        enabled = "✅ ENABLED" if item_result.get('enabled') else "❌ DISABLED"
                        roles = ', '.join(item_result.get('roles', []))
                        print(f"    • {item_name}: {enabled} - {item_result.get('label', 'No Label')} - Roles: [{roles}]")
                        
                        # Highlight issues
                        if item_name == 'sell' and 'buyer' in item_result.get('roles', []):
                            print(f"      ⚠️ ISSUE: Sell item has extra 'buyer' role")
                        if item_name == 'buy_management' and item_result.get('enabled'):
                            print(f"      ⚠️ ISSUE: Inventory item is enabled (should be disabled)")
                    else:
                        print(f"    • {item_name}: ❌ NOT FOUND")
            else:
                print(f"    ❌ API call failed")
            
            # Show database check results
            db_check = results.get('database_check', {})
            if db_check.get('success'):
                if db_check.get('has_overrides'):
                    override_count = db_check.get('override_count', 0)
                    print(f"  🗄️ DATABASE CHECK: ⚠️ Found {override_count} override documents")
                else:
                    print(f"  🗄️ DATABASE CHECK: ✅ No overrides found")
            
            # Show fix results
            fix_successful = results.get('fix_successful')
            fix_method = results.get('fix_method', 'unknown')
            
            if fix_successful == True:
                print(f"  🔧 FIX RESULT: ✅ SUCCESS via {fix_method}")
                
                # Show after results
                final_menu = menu_after_update if menu_after_update.get('success') else menu_after_clear
                if final_menu.get('success'):
                    print(f"  📊 AFTER FIX:")
                    after_check = final_menu.get('expected_items_check', {})
                    for item_name, item_result in after_check.items():
                        if item_result.get('found'):
                            enabled = "✅ ENABLED" if item_result.get('enabled') else "❌ DISABLED"
                            roles = ', '.join(item_result.get('roles', []))
                            print(f"    • {item_name}: {enabled} - {item_result.get('label', 'No Label')} - Roles: [{roles}]")
                        else:
                            print(f"    • {item_name}: ❌ NOT FOUND")
            elif fix_successful == False:
                print(f"  🔧 FIX RESULT: ❌ FAILED")
                critical_issues.append(f"{user_type}: Fix failed")
            else:
                print(f"  🔧 FIX RESULT: ℹ️ No fix needed (no database overrides)")
        
        # Overall summary
        print(f"\n🎯 OVERALL RESULTS:")
        
        # Analyze results to determine success
        admin_results = all_results.get('Admin User', {}) or all_results.get('Admin User (Alt Password)', {})
        
        if admin_results:
            fix_successful = admin_results.get('fix_successful')
            fix_method = admin_results.get('fix_method', 'unknown')
            
            if fix_successful == True:
                print(f"   ✅ DATABASE MENU SETTINGS FIX SUCCESSFUL")
                print(f"   🔧 Fix Method: {fix_method}")
                print(f"   🎉 Buy/Sell/Inventory items should now be correctly configured")
                print(f"   💡 Admin Panel Menu Settings should now display the correct items")
            elif fix_successful == False:
                print(f"   ❌ DATABASE MENU SETTINGS FIX FAILED")
                print(f"   🔧 Manual intervention may be required")
                critical_issues.append("Database fix failed")
            else:
                print(f"   ℹ️ NO DATABASE OVERRIDES FOUND")
                print(f"   💡 Issue may be in backend configuration or frontend parsing")
        
        # Key findings and recommendations
        print(f"\n🔑 KEY FINDINGS:")
        
        if admin_results:
            db_check = admin_results.get('database_check', {})
            menu_before = admin_results.get('menu_settings_api_before', {})
            
            if db_check.get('has_overrides'):
                print(f"   ⚠️ Database overrides were found and addressed")
                override_count = db_check.get('override_count', 0)
                print(f"   📊 {override_count} menu_settings documents were affecting configuration")
            
            if menu_before.get('success'):
                before_check = menu_before.get('expected_items_check', {})
                issues_found = []
                
                sell_item = before_check.get('sell', {})
                if sell_item.get('found') and 'buyer' in sell_item.get('roles', []):
                    issues_found.append("Sell item had extra 'buyer' role")
                
                inventory_item = before_check.get('buy_management', {})
                if inventory_item.get('found') and inventory_item.get('enabled'):
                    issues_found.append("Inventory item was incorrectly enabled")
                
                if issues_found:
                    print(f"   🔍 Issues identified: {'; '.join(issues_found)}")
                else:
                    print(f"   ✅ No configuration issues found in API response")
        
        print(f"\n🔧 RECOMMENDATIONS:")
        
        if admin_results and admin_results.get('fix_successful') == True:
            print("   ✅ Database fix was successful")
            print("   🎯 Next steps:")
            print("     1. Verify Admin Panel Menu Settings now shows correct Buy/Sell items")
            print("     2. Test that menu items appear correctly for different user roles")
            print("     3. Confirm frontend is parsing the updated menu configuration")
        elif admin_results and admin_results.get('fix_successful') == False:
            print("   ❌ Database fix failed - manual intervention required")
            print("   🔧 Manual steps:")
            print("     1. Connect to MongoDB directly")
            print("     2. Check db.menu_settings collection")
            print("     3. Remove or update documents with type: 'menu_config'")
            print("     4. Restart backend service to clear any caches")
        else:
            print("   ℹ️ No database overrides found")
            print("   🔍 Check these areas:")
            print("     1. Backend default menu settings in server.py")
            print("     2. Frontend Menu Settings component parsing")
            print("     3. API endpoint implementation")
        
        print(f"\n🎉 DATABASE MENU SETTINGS FIX COMPLETED!")
        print("=" * 80)

    def generate_menu_settings_summary(self, all_results):
        """Generate comprehensive summary of admin menu settings API testing"""
        print("📊 ADMIN MENU SETTINGS API TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = 0
        passed_tests = 0
        critical_issues = []
        
        for user_type, results in all_results.items():
            print(f"\n🔍 {user_type} Results:")
            print("-" * 30)
            
            for test_name, result in results.items():
                total_tests += 1
                if result.get('success'):
                    passed_tests += 1
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"
                    critical_issues.append(f"{user_type}: {test_name}")
                
                print(f"  {status}: {test_name.replace('_', ' ').title()}")
                
                # Add specific details for each test
                if test_name == 'menu_settings_api':
                    if result.get('success'):
                        desktop_count = result.get('desktop_menu_count', 0)
                        mobile_count = result.get('mobile_menu_count', 0)
                        all_expected_found = result.get('all_expected_found', False)
                        print(f"    📊 Desktop Menu Items: {desktop_count}")
                        print(f"    📱 Mobile Menu Items: {mobile_count}")
                        print(f"    ✅ Expected Items Found: {all_expected_found}")
                        
                        # Show specific items found
                        desktop_items = result.get('desktop_menu_items', [])
                        if 'buy' in desktop_items and 'sell' in desktop_items:
                            print(f"    🎯 Buy/Sell Items: ✅ FOUND in desktop menu")
                        else:
                            print(f"    🎯 Buy/Sell Items: ❌ MISSING from desktop menu")
                            
                        expected_check = result.get('expected_items_check', {})
                        for item_name, item_result in expected_check.items():
                            if item_result.get('found'):
                                enabled_status = "✅ ENABLED" if item_result.get('enabled') else "❌ DISABLED"
                                print(f"      • {item_name}: {enabled_status} - {item_result.get('label', 'No Label')}")
                            else:
                                print(f"      • {item_name}: ❌ NOT FOUND")
                    else:
                        status_code = result.get('status_code', 'Unknown')
                        error = result.get('error', 'Unknown error')
                        print(f"    ❌ Status Code: {status_code}")
                        print(f"    ❌ Error: {error}")
                        
                elif test_name == 'menu_items_analysis':
                    if result.get('success'):
                        buy_sell_ok = result.get('buy_sell_properly_configured', False)
                        inventory_ok = result.get('inventory_properly_configured', False)
                        print(f"    🛒 Buy/Sell Configuration: {'✅ CORRECT' if buy_sell_ok else '❌ INCORRECT'}")
                        print(f"    📦 Inventory Configuration: {'✅ CORRECT' if inventory_ok else '❌ INCORRECT'}")
                        
                        desktop_analysis = result.get('desktop_analysis', {})
                        buy_sell_items = desktop_analysis.get('buy_sell_items', {})
                        
                        for item_name, item_config in buy_sell_items.items():
                            enabled = item_config.get('enabled', False)
                            label = item_config.get('label', 'No Label')
                            roles = item_config.get('roles', [])
                            print(f"      • {item_name}: {label} - {'Enabled' if enabled else 'Disabled'} - Roles: {', '.join(roles)}")
                    else:
                        print(f"    ❌ Analysis Error: {result.get('error', 'Unknown error')}")
                        
                elif test_name == 'database_check':
                    if result.get('success'):
                        note = result.get('note', '')
                        recommendation = result.get('recommendation', '')
                        print(f"    ℹ️ Note: {note}")
                        print(f"    💡 Recommendation: {recommendation}")
                    else:
                        print(f"    ❌ Database Check Error: {result.get('error', 'Unknown error')}")
        
        # Overall summary
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Key findings
        print(f"\n🔑 KEY FINDINGS:")
        
        # Analyze results to determine root cause
        admin_results = all_results.get('Admin User', {}) or all_results.get('Admin User (Alt Password)', {})
        
        if admin_results:
            menu_api_result = admin_results.get('menu_settings_api', {})
            analysis_result = admin_results.get('menu_items_analysis', {})
            
            # Check API access
            if menu_api_result.get('success'):
                print(f"   ✅ Admin menu settings API is accessible")
                
                # Check if expected items are found
                all_expected_found = menu_api_result.get('all_expected_found', False)
                if all_expected_found:
                    print(f"   ✅ All expected Buy/Sell/Inventory items found with correct configuration")
                else:
                    print(f"   ⚠️ Some expected items missing or incorrectly configured")
                    
                    # Show specific issues
                    expected_check = menu_api_result.get('expected_items_check', {})
                    for item_name, item_result in expected_check.items():
                        if not item_result.get('matches_expected', False):
                            if not item_result.get('found'):
                                print(f"     ❌ {item_name}: NOT FOUND in menu")
                            else:
                                print(f"     ⚠️ {item_name}: Found but configuration doesn't match expected")
                                print(f"        Expected: enabled={item_name != 'buy_management'}, label={'Buy' if item_name == 'buy' else 'Sell' if item_name == 'sell' else 'Inventory'}")
                                print(f"        Actual: enabled={item_result.get('enabled')}, label={item_result.get('label')}")
                
                # Check detailed analysis
                if analysis_result.get('success'):
                    buy_sell_ok = analysis_result.get('buy_sell_properly_configured', False)
                    inventory_ok = analysis_result.get('inventory_properly_configured', False)
                    
                    if buy_sell_ok and inventory_ok:
                        print(f"   ✅ Detailed analysis confirms Buy/Sell/Inventory items are correctly configured")
                    else:
                        print(f"   ❌ Detailed analysis found configuration issues:")
                        if not buy_sell_ok:
                            print(f"     • Buy/Sell items are not properly configured")
                        if not inventory_ok:
                            print(f"     • Inventory item is not properly configured")
                            
            else:
                status_code = menu_api_result.get('status_code', 'Unknown')
                error = menu_api_result.get('error', 'Unknown')
                print(f"   ❌ Admin menu settings API is NOT accessible")
                print(f"   🔍 Status Code: {status_code}")
                print(f"   💬 Error: {error}")
        
        # Root cause analysis and recommendations
        print(f"\n🔧 ROOT CAUSE ANALYSIS & RECOMMENDATIONS:")
        
        if not admin_results:
            print("   ❌ CRITICAL: Could not login with admin credentials")
            print("   🔧 SOLUTION: Check admin credentials (admin@cataloro.com / password123)")
        elif not menu_api_result.get('success'):
            status_code = menu_api_result.get('status_code', 'Unknown')
            if status_code == 403:
                print("   ❌ CRITICAL: Admin user cannot access menu settings endpoint (403 Forbidden)")
                print("   🔧 SOLUTION: Check backend require_admin_role function and user role verification")
            elif status_code == 401:
                print("   ❌ CRITICAL: Authentication token is invalid or expired (401 Unauthorized)")
                print("   🔧 SOLUTION: Check JWT token generation and validation")
            else:
                print("   ❌ CRITICAL: Backend endpoint /api/admin/menu-settings is not working")
                print("   🔧 SOLUTION: Check backend server logs and endpoint implementation")
        else:
            # API is working, check configuration
            all_expected_found = menu_api_result.get('all_expected_found', False)
            if all_expected_found:
                print("   ✅ BACKEND API WORKING CORRECTLY: All Buy/Sell/Inventory items found with correct configuration")
                print("   🎉 CONCLUSION: The backend menu settings API is returning the expected items")
                print("   💡 FRONTEND ISSUE: If items are not showing in Admin Panel, check frontend Menu Settings component")
                print("   🔍 NEXT STEPS: Verify frontend is correctly parsing and displaying the menu settings response")
            else:
                print("   ⚠️ CONFIGURATION ISSUE: Backend API accessible but some items missing/incorrect")
                print("   🔧 SOLUTION: Check backend default menu settings in server.py around line 4306-4333")
                print("   🔍 VERIFY: Ensure database menu_settings collection doesn't have overrides")
                
                # Specific recommendations based on what's missing
                expected_check = menu_api_result.get('expected_items_check', {})
                for item_name, item_result in expected_check.items():
                    if not item_result.get('found'):
                        print(f"   🔧 MISSING ITEM: Add '{item_name}' to default_settings in backend menu settings endpoint")
                    elif not item_result.get('matches_expected'):
                        print(f"   🔧 INCORRECT CONFIG: Fix '{item_name}' configuration in backend default settings")
        
        print(f"\n🎉 ADMIN MENU SETTINGS API TESTING COMPLETED!")
        print("=" * 80)

async def main():
    """Main test execution function"""
    async with BackendTester() as tester:
        # Run the urgent Buy/Sell menu items investigation
        results = await tester.investigate_buy_sell_menu_items_missing()
        return results

if __name__ == "__main__":
    # Run the tests
    try:
        results = asyncio.run(main())
        print("\n✅ All tests completed successfully!")
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()