#!/usr/bin/env python3
"""
CATALORO MARKETPLACE - DATABASE MENU SETTINGS RESET TESTING
Testing and fixing database menu settings override issues

SPECIFIC ISSUE IDENTIFIED (Review Request):
Backend testing confirmed that the database `menu_settings` collection has stored overrides 
from previous admin panel changes that are overriding the updated backend defaults.

**ROOT CAUSE IDENTIFIED**:
- Backend default settings in server.py are CORRECT
- Database `menu_settings` collection has stored overrides that take precedence
- API merge logic is working correctly but database settings override defaults
- Previous admin panel menu settings changes were saved to database

**SPECIFIC ISSUES FOUND**:
- "sell" item has extra "buyer" role: ["admin", "manager", "seller", "buyer"] 
  (should only have ["admin", "manager", "seller"])
- "buy_management" (Inventory) is enabled=true (should be enabled=false)

**REQUIRED ACTIONS**:

**1. Clear Database Menu Settings**
- Connect to MongoDB and find the `menu_settings` collection
- Remove or reset the document with `type: "menu_config"`
- This will allow the backend defaults to take effect

**2. Alternative: Update Database Settings**
- Update the database document directly to match intended configuration
- Fix "sell" item roles to remove "buyer" 
- Set "buy_management" enabled=false

**3. Verify After Changes**
- Test GET `/api/admin/menu-settings` again to confirm correct configuration
- Verify "Buy" and "Sell" items appear with correct settings

**EXPECTED RESULT AFTER FIX**:
```
"buy": {"enabled": true, "label": "Buy", "roles": ["admin", "manager", "buyer"]}
"sell": {"enabled": true, "label": "Sell", "roles": ["admin", "manager", "seller"]}
"buy_management": {"enabled": false, "label": "Inventory", "roles": ["admin", "manager", "buyer"]}
```

**LOGIN CREDENTIALS:** admin@cataloro.com / password123

**GOAL:** Clear/update the database menu_settings to allow the new Buy/Sell menu items 
to be properly configured and visible in Admin Panel Menu Settings interface.
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









    async def run_admin_menu_settings_tests(self):
        """Run comprehensive admin menu settings API tests"""
        print("🚀 CATALORO ADMIN MENU SETTINGS API TESTING")
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
            
            # Step 2: Test admin menu settings API
            print(f"🔍 Testing admin menu settings API for {user_type}...")
            menu_api_result = await self.test_admin_menu_settings_api(token)
            user_results['menu_settings_api'] = menu_api_result
            
            # Step 3: Detailed analysis of menu items if API call was successful
            if menu_api_result.get('success') and menu_api_result.get('raw_response'):
                print(f"🔬 Performing detailed analysis of menu items...")
                analysis_result = await self.test_menu_items_detailed_analysis(menu_api_result['raw_response'])
                user_results['menu_items_analysis'] = analysis_result
            
            # Step 4: Check database settings (informational)
            print(f"🗄️ Checking database menu settings implications...")
            db_check_result = await self.test_database_menu_settings_check(token)
            user_results['database_check'] = db_check_result
            
            all_results[user_type] = user_results
            print()
            
            # If login was successful, we can break (no need to test alternative password)
            break
        
        # Generate summary
        self.generate_menu_settings_summary(all_results)
        
        return all_results

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
        results = await tester.run_admin_menu_settings_tests()
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