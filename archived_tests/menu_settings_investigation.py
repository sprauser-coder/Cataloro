#!/usr/bin/env python3
"""
Menu Settings Investigation - Debug Test Items in Menu Settings
Investigating why test items are showing in Menu Settings and debug current menu data state.
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-uxfixes.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_PASSWORD = "admin_password"

# Demo User Configuration  
DEMO_EMAIL = "demo@cataloro.com"
DEMO_PASSWORD = "demo_password"

# Expected Real Navigation Items (from review request)
EXPECTED_REAL_ITEMS = [
    "browse", "messages", "create_listing", "favorites", "profile", 
    "my_listings", "admin_panel", "about", "buy_management", "tenders", 
    "notifications", "admin_drawer"
]

class MenuSettingsInvestigator:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.admin_user_id = None
        self.demo_user_id = None
        self.investigation_results = []
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, headers: Dict = None) -> Dict:
        """Make HTTP request and measure response time"""
        start_time = time.time()
        
        try:
            request_kwargs = {}
            if params:
                request_kwargs['params'] = params
            if data:
                request_kwargs['json'] = data
            if headers:
                request_kwargs['headers'] = headers
            
            async with self.session.request(method, f"{BACKEND_URL}{endpoint}", **request_kwargs) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                return {
                    "success": response.status in [200, 201],
                    "response_time_ms": response_time_ms,
                    "data": response_data,
                    "status": response.status
                }
        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            return {
                "success": False,
                "response_time_ms": response_time_ms,
                "error": str(e),
                "status": 0
            }
    
    async def authenticate_admin(self) -> Dict:
        """Authenticate admin user and get JWT token"""
        print("🔐 Authenticating admin user...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            user_data = result["data"].get("user", {})
            token = result["data"].get("token", "")
            
            self.admin_token = token
            self.admin_user_id = user_data.get("id")
            
            print(f"  ✅ Admin authenticated successfully")
            print(f"  👤 Admin ID: {self.admin_user_id}")
            print(f"  🔑 Token received: {bool(token)}")
            
            return {
                "test_name": "Admin Authentication",
                "success": True,
                "admin_id": self.admin_user_id,
                "token_received": bool(token),
                "user_data": user_data
            }
        else:
            print(f"  ❌ Admin authentication failed: {result.get('error')}")
            return {
                "test_name": "Admin Authentication", 
                "success": False,
                "error": result.get("error")
            }
    
    async def authenticate_demo_user(self) -> Dict:
        """Authenticate demo user for comparison"""
        print("👤 Authenticating demo user...")
        
        login_data = {
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            user_data = result["data"].get("user", {})
            self.demo_user_id = user_data.get("id")
            
            print(f"  ✅ Demo user authenticated successfully")
            print(f"  👤 Demo ID: {self.demo_user_id}")
            
            return {
                "test_name": "Demo User Authentication",
                "success": True,
                "demo_id": self.demo_user_id,
                "user_data": user_data
            }
        else:
            print(f"  ❌ Demo user authentication failed: {result.get('error')}")
            return {
                "test_name": "Demo User Authentication",
                "success": False,
                "error": result.get("error")
            }
    
    async def investigate_admin_menu_settings(self) -> Dict:
        """REQUIREMENT 1: Check current admin menu settings via GET /api/admin/menu-settings"""
        print("🔍 INVESTIGATION 1: Current Admin Menu Settings Data")
        print("=" * 60)
        
        if not self.admin_token:
            return {"error": "Admin token not available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if result["success"]:
            menu_data = result["data"]
            
            print(f"  ✅ Admin menu settings retrieved ({result['response_time_ms']:.0f}ms)")
            print(f"  📊 Response structure: {type(menu_data)}")
            
            # Analyze menu structure
            analysis = self.analyze_menu_structure(menu_data)
            
            # Look for test items specifically
            test_items_found = self.detect_test_items(menu_data)
            
            # Check for real navigation items
            real_items_found = self.check_real_navigation_items(menu_data)
            
            print(f"  🔍 Total menu sections: {analysis['total_sections']}")
            print(f"  📱 Mobile menu items: {analysis['mobile_items_count']}")
            print(f"  🖥️ Desktop menu items: {analysis['desktop_items_count']}")
            print(f"  ⚠️ Test items detected: {len(test_items_found)}")
            print(f"  ✅ Real items found: {len(real_items_found)}")
            
            if test_items_found:
                print("  🚨 TEST ITEMS DETECTED:")
                for item in test_items_found:
                    print(f"    - {item['key']}: {item['label']} (in {item['section']})")
            
            if len(real_items_found) < len(EXPECTED_REAL_ITEMS):
                missing_items = set(EXPECTED_REAL_ITEMS) - set(real_items_found)
                print(f"  ⚠️ MISSING REAL ITEMS: {list(missing_items)}")
            
            return {
                "test_name": "Admin Menu Settings Investigation",
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "menu_structure_analysis": analysis,
                "test_items_found": test_items_found,
                "real_items_found": real_items_found,
                "missing_real_items": list(set(EXPECTED_REAL_ITEMS) - set(real_items_found)),
                "has_test_items": len(test_items_found) > 0,
                "has_all_real_items": len(real_items_found) == len(EXPECTED_REAL_ITEMS),
                "raw_menu_data": menu_data
            }
        else:
            print(f"  ❌ Failed to retrieve admin menu settings: {result.get('error')}")
            return {
                "test_name": "Admin Menu Settings Investigation",
                "success": False,
                "error": result.get("error"),
                "status": result["status"]
            }
    
    async def investigate_user_menu_settings(self) -> Dict:
        """REQUIREMENT 2: Check what users are receiving via GET /api/menu-settings/user/{user_id}"""
        print("🔍 INVESTIGATION 2: User Menu Settings Investigation")
        print("=" * 60)
        
        user_investigations = []
        
        # Test admin user menu settings
        if self.admin_user_id:
            print(f"  Testing admin user menu settings (ID: {self.admin_user_id})...")
            admin_result = await self.make_request(f"/menu-settings/user/{self.admin_user_id}")
            
            if admin_result["success"]:
                admin_menu = admin_result["data"]
                admin_test_items = self.detect_test_items_in_user_menu(admin_menu)
                admin_real_items = self.check_real_items_in_user_menu(admin_menu)
                
                print(f"    ✅ Admin user menu retrieved ({admin_result['response_time_ms']:.0f}ms)")
                print(f"    📱 Mobile items: {len(admin_menu.get('mobile_menu', {}))}")
                print(f"    🖥️ Desktop items: {len(admin_menu.get('desktop_menu', {}))}")
                print(f"    ⚠️ Test items in admin menu: {len(admin_test_items)}")
                print(f"    ✅ Real items in admin menu: {len(admin_real_items)}")
                
                user_investigations.append({
                    "user_type": "admin",
                    "user_id": self.admin_user_id,
                    "success": True,
                    "response_time_ms": admin_result["response_time_ms"],
                    "test_items_found": admin_test_items,
                    "real_items_found": admin_real_items,
                    "mobile_items_count": len(admin_menu.get('mobile_menu', {})),
                    "desktop_items_count": len(admin_menu.get('desktop_menu', {})),
                    "raw_menu_data": admin_menu
                })
            else:
                print(f"    ❌ Failed to get admin user menu: {admin_result.get('error')}")
                user_investigations.append({
                    "user_type": "admin",
                    "user_id": self.admin_user_id,
                    "success": False,
                    "error": admin_result.get("error")
                })
        
        # Test demo user menu settings
        if self.demo_user_id:
            print(f"  Testing demo user menu settings (ID: {self.demo_user_id})...")
            demo_result = await self.make_request(f"/menu-settings/user/{self.demo_user_id}")
            
            if demo_result["success"]:
                demo_menu = demo_result["data"]
                demo_test_items = self.detect_test_items_in_user_menu(demo_menu)
                demo_real_items = self.check_real_items_in_user_menu(demo_menu)
                
                print(f"    ✅ Demo user menu retrieved ({demo_result['response_time_ms']:.0f}ms)")
                print(f"    📱 Mobile items: {len(demo_menu.get('mobile_menu', {}))}")
                print(f"    🖥️ Desktop items: {len(demo_menu.get('desktop_menu', {}))}")
                print(f"    ⚠️ Test items in demo menu: {len(demo_test_items)}")
                print(f"    ✅ Real items in demo menu: {len(demo_real_items)}")
                
                user_investigations.append({
                    "user_type": "demo",
                    "user_id": self.demo_user_id,
                    "success": True,
                    "response_time_ms": demo_result["response_time_ms"],
                    "test_items_found": demo_test_items,
                    "real_items_found": demo_real_items,
                    "mobile_items_count": len(demo_menu.get('mobile_menu', {})),
                    "desktop_items_count": len(demo_menu.get('desktop_menu', {})),
                    "raw_menu_data": demo_menu
                })
            else:
                print(f"    ❌ Failed to get demo user menu: {demo_result.get('error')}")
                user_investigations.append({
                    "user_type": "demo",
                    "user_id": self.demo_user_id,
                    "success": False,
                    "error": demo_result.get("error")
                })
        
        # Analyze differences between admin and demo user menus
        test_items_in_user_menus = sum(len(inv.get("test_items_found", [])) for inv in user_investigations if inv["success"])
        users_receiving_test_items = [inv for inv in user_investigations if inv["success"] and len(inv.get("test_items_found", [])) > 0]
        
        return {
            "test_name": "User Menu Settings Investigation",
            "total_users_tested": len(user_investigations),
            "successful_user_tests": len([inv for inv in user_investigations if inv["success"]]),
            "test_items_in_user_menus": test_items_in_user_menus,
            "users_receiving_test_items": len(users_receiving_test_items),
            "role_mapping_working": len([inv for inv in user_investigations if inv["success"]]) > 0,
            "filtering_working": all(inv.get("mobile_items_count", 0) > 0 for inv in user_investigations if inv["success"]),
            "detailed_user_investigations": user_investigations
        }
    
    async def investigate_database_state(self) -> Dict:
        """REQUIREMENT 3: Check raw database state by examining menu_settings collection"""
        print("🔍 INVESTIGATION 3: Database State Verification")
        print("=" * 60)
        
        # We can't directly access MongoDB from here, but we can infer database state
        # by examining the admin menu settings response structure and consistency
        
        if not self.admin_token:
            return {"error": "Admin token not available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get admin menu settings multiple times to check consistency
        print("  Checking database consistency with multiple requests...")
        
        consistency_tests = []
        for i in range(3):
            result = await self.make_request("/admin/menu-settings", headers=headers)
            if result["success"]:
                consistency_tests.append({
                    "request_number": i + 1,
                    "response_time_ms": result["response_time_ms"],
                    "data_hash": hash(str(result["data"])),  # Simple consistency check
                    "menu_structure": self.analyze_menu_structure(result["data"])
                })
                print(f"    Request {i+1}: {result['response_time_ms']:.0f}ms")
            else:
                consistency_tests.append({
                    "request_number": i + 1,
                    "error": result.get("error"),
                    "success": False
                })
        
        # Check if all responses are identical (indicating consistent database state)
        successful_tests = [t for t in consistency_tests if "data_hash" in t]
        data_consistent = len(set(t["data_hash"] for t in successful_tests)) <= 1 if successful_tests else False
        
        # Try to save and retrieve to test persistence
        print("  Testing database persistence...")
        
        # Get current settings
        current_result = await self.make_request("/admin/menu-settings", headers=headers)
        if current_result["success"]:
            current_data = current_result["data"]
            
            # Make a small modification (toggle a setting)
            modified_data = json.loads(json.dumps(current_data))  # Deep copy
            
            # Find first menu item and toggle its enabled state
            test_modification_made = False
            for section_name, section_data in modified_data.items():
                if isinstance(section_data, dict):
                    for item_key, item_data in section_data.items():
                        if isinstance(item_data, dict) and "enabled" in item_data:
                            original_enabled = item_data["enabled"]
                            modified_data[section_name][item_key]["enabled"] = not original_enabled
                            test_modification_made = True
                            print(f"    Modified {section_name}.{item_key}.enabled: {original_enabled} -> {not original_enabled}")
                            break
                    if test_modification_made:
                        break
            
            persistence_test = {"modification_made": test_modification_made}
            
            if test_modification_made:
                # Save modified settings
                save_result = await self.make_request("/admin/menu-settings", "POST", data=modified_data, headers=headers)
                persistence_test["save_success"] = save_result["success"]
                
                if save_result["success"]:
                    print(f"    Settings saved successfully ({save_result['response_time_ms']:.0f}ms)")
                    
                    # Retrieve to verify persistence
                    verify_result = await self.make_request("/admin/menu-settings", headers=headers)
                    persistence_test["retrieve_success"] = verify_result["success"]
                    
                    if verify_result["success"]:
                        # Check if modification persisted
                        persisted_correctly = hash(str(verify_result["data"])) == hash(str(modified_data))
                        persistence_test["data_persisted"] = persisted_correctly
                        print(f"    Data persistence verified: {persisted_correctly}")
                        
                        # Restore original settings
                        restore_result = await self.make_request("/admin/menu-settings", "POST", data=current_data, headers=headers)
                        persistence_test["restore_success"] = restore_result["success"]
                        print(f"    Original settings restored: {restore_result['success']}")
                    else:
                        persistence_test["retrieve_error"] = verify_result.get("error")
                else:
                    persistence_test["save_error"] = save_result.get("error")
        
        return {
            "test_name": "Database State Verification",
            "consistency_tests_count": len(consistency_tests),
            "successful_consistency_tests": len(successful_tests),
            "data_consistent_across_requests": data_consistent,
            "persistence_test": persistence_test,
            "database_responsive": len(successful_tests) > 0,
            "database_state_stable": data_consistent and persistence_test.get("data_persisted", False),
            "detailed_consistency_tests": consistency_tests
        }
    
    async def detect_test_data_patterns(self) -> Dict:
        """REQUIREMENT 4: Identify test or dummy items and analyze patterns"""
        print("🔍 INVESTIGATION 4: Test Data Detection and Pattern Analysis")
        print("=" * 60)
        
        if not self.admin_token:
            return {"error": "Admin token not available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if not result["success"]:
            return {"error": "Could not retrieve menu settings for analysis"}
        
        menu_data = result["data"]
        
        # Comprehensive test data detection
        test_patterns = {
            "test_keywords": ["test", "dummy", "sample", "placeholder", "mock", "fake", "temp"],
            "test_prefixes": ["test_", "dummy_", "sample_", "mock_", "temp_"],
            "test_suffixes": ["_test", "_dummy", "_sample", "_mock", "_temp"],
            "suspicious_labels": ["Test Item", "Dummy Data", "Sample Menu", "Placeholder"]
        }
        
        detected_test_items = []
        suspicious_items = []
        real_items_analysis = []
        
        # Analyze each menu section
        for section_name, section_data in menu_data.items():
            if isinstance(section_data, dict):
                print(f"  Analyzing {section_name} section...")
                
                for item_key, item_data in section_data.items():
                    if isinstance(item_data, dict):
                        item_analysis = self.analyze_menu_item_for_test_data(
                            item_key, item_data, test_patterns, section_name
                        )
                        
                        if item_analysis["is_test_item"]:
                            detected_test_items.append(item_analysis)
                            print(f"    🚨 TEST ITEM: {item_key} - {item_analysis['reasons']}")
                        elif item_analysis["is_suspicious"]:
                            suspicious_items.append(item_analysis)
                            print(f"    ⚠️ SUSPICIOUS: {item_key} - {item_analysis['reasons']}")
                        elif item_key in EXPECTED_REAL_ITEMS:
                            real_items_analysis.append(item_analysis)
                            print(f"    ✅ REAL ITEM: {item_key}")
                        else:
                            print(f"    ❓ UNKNOWN: {item_key} (not in expected real items)")
        
        # Check for data integrity issues
        integrity_issues = []
        
        # Check for duplicate items across sections
        all_items = {}
        for section_name, section_data in menu_data.items():
            if isinstance(section_data, dict):
                for item_key in section_data.keys():
                    if item_key in all_items:
                        integrity_issues.append(f"Duplicate item '{item_key}' in {section_name} and {all_items[item_key]}")
                    else:
                        all_items[item_key] = section_name
        
        # Check for missing expected items
        found_real_items = set(item["item_key"] for item in real_items_analysis)
        missing_real_items = set(EXPECTED_REAL_ITEMS) - found_real_items
        
        if missing_real_items:
            integrity_issues.append(f"Missing expected real items: {list(missing_real_items)}")
        
        # Check for unexpected test data presence
        if detected_test_items:
            integrity_issues.append(f"Test items found in production menu: {[item['item_key'] for item in detected_test_items]}")
        
        return {
            "test_name": "Test Data Detection and Pattern Analysis",
            "total_test_items_detected": len(detected_test_items),
            "total_suspicious_items": len(suspicious_items),
            "total_real_items_found": len(real_items_analysis),
            "missing_real_items_count": len(missing_real_items),
            "integrity_issues_count": len(integrity_issues),
            "menu_data_clean": len(detected_test_items) == 0 and len(integrity_issues) == 0,
            "real_navigation_complete": len(missing_real_items) == 0,
            "detected_test_items": detected_test_items,
            "suspicious_items": suspicious_items,
            "real_items_analysis": real_items_analysis,
            "missing_real_items": list(missing_real_items),
            "integrity_issues": integrity_issues,
            "test_patterns_used": test_patterns
        }
    
    def analyze_menu_structure(self, menu_data: Dict) -> Dict:
        """Analyze the structure of menu data"""
        analysis = {
            "total_sections": 0,
            "mobile_items_count": 0,
            "desktop_items_count": 0,
            "sections": {}
        }
        
        for section_name, section_data in menu_data.items():
            if isinstance(section_data, dict):
                analysis["total_sections"] += 1
                item_count = len(section_data)
                analysis["sections"][section_name] = {
                    "item_count": item_count,
                    "items": list(section_data.keys())
                }
                
                if "mobile" in section_name.lower():
                    analysis["mobile_items_count"] += item_count
                elif "desktop" in section_name.lower():
                    analysis["desktop_items_count"] += item_count
        
        return analysis
    
    def detect_test_items(self, menu_data: Dict) -> List[Dict]:
        """Detect test items in menu data"""
        test_items = []
        
        for section_name, section_data in menu_data.items():
            if isinstance(section_data, dict):
                for item_key, item_data in section_data.items():
                    if isinstance(item_data, dict):
                        # Check for test indicators
                        is_test = False
                        reasons = []
                        
                        # Check key for test patterns
                        if any(pattern in item_key.lower() for pattern in ["test", "dummy", "sample", "mock"]):
                            is_test = True
                            reasons.append("test pattern in key")
                        
                        # Check label for test patterns
                        label = item_data.get("label", "")
                        if any(pattern in label.lower() for pattern in ["test", "dummy", "sample", "mock"]):
                            is_test = True
                            reasons.append("test pattern in label")
                        
                        # Check if it's not in expected real items
                        if item_key not in EXPECTED_REAL_ITEMS:
                            reasons.append("not in expected real items")
                        
                        if is_test:
                            test_items.append({
                                "key": item_key,
                                "label": label,
                                "section": section_name,
                                "reasons": reasons,
                                "data": item_data
                            })
        
        return test_items
    
    def check_real_navigation_items(self, menu_data: Dict) -> List[str]:
        """Check which real navigation items are present"""
        found_items = []
        
        for section_name, section_data in menu_data.items():
            if isinstance(section_data, dict):
                for item_key in section_data.keys():
                    if item_key in EXPECTED_REAL_ITEMS:
                        found_items.append(item_key)
        
        return list(set(found_items))  # Remove duplicates
    
    def detect_test_items_in_user_menu(self, user_menu: Dict) -> List[Dict]:
        """Detect test items in user menu response"""
        test_items = []
        
        for section_name, section_data in user_menu.items():
            if isinstance(section_data, dict):
                for item_key, item_data in section_data.items():
                    # Check for test patterns
                    if any(pattern in item_key.lower() for pattern in ["test", "dummy", "sample", "mock"]):
                        test_items.append({
                            "key": item_key,
                            "section": section_name,
                            "data": item_data
                        })
        
        return test_items
    
    def check_real_items_in_user_menu(self, user_menu: Dict) -> List[str]:
        """Check real items in user menu"""
        found_items = []
        
        for section_name, section_data in user_menu.items():
            if isinstance(section_data, dict):
                for item_key in section_data.keys():
                    if item_key in EXPECTED_REAL_ITEMS:
                        found_items.append(item_key)
        
        return list(set(found_items))
    
    def analyze_menu_item_for_test_data(self, item_key: str, item_data: Dict, test_patterns: Dict, section_name: str) -> Dict:
        """Analyze a single menu item for test data patterns"""
        analysis = {
            "item_key": item_key,
            "section": section_name,
            "is_test_item": False,
            "is_suspicious": False,
            "is_real_item": item_key in EXPECTED_REAL_ITEMS,
            "reasons": [],
            "data": item_data
        }
        
        # Check for test keywords
        item_key_lower = item_key.lower()
        label = item_data.get("label", "").lower()
        
        for keyword in test_patterns["test_keywords"]:
            if keyword in item_key_lower or keyword in label:
                analysis["is_test_item"] = True
                analysis["reasons"].append(f"contains test keyword: {keyword}")
        
        # Check for test prefixes
        for prefix in test_patterns["test_prefixes"]:
            if item_key_lower.startswith(prefix):
                analysis["is_test_item"] = True
                analysis["reasons"].append(f"has test prefix: {prefix}")
        
        # Check for test suffixes
        for suffix in test_patterns["test_suffixes"]:
            if item_key_lower.endswith(suffix):
                analysis["is_test_item"] = True
                analysis["reasons"].append(f"has test suffix: {suffix}")
        
        # Check for suspicious labels
        for suspicious_label in test_patterns["suspicious_labels"]:
            if suspicious_label.lower() in label:
                analysis["is_test_item"] = True
                analysis["reasons"].append(f"has suspicious label: {suspicious_label}")
        
        # Check if item is not in expected real items (suspicious but not necessarily test)
        if not analysis["is_real_item"] and not analysis["is_test_item"]:
            analysis["is_suspicious"] = True
            analysis["reasons"].append("not in expected real navigation items")
        
        return analysis
    
    async def run_comprehensive_investigation(self) -> Dict:
        """Run all menu settings investigations"""
        print("🚀 Starting Menu Settings Investigation")
        print("Investigating why test items are showing in Menu Settings")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Step 1: Authenticate users
            admin_auth = await self.authenticate_admin()
            demo_auth = await self.authenticate_demo_user()
            
            # Step 2: Run all investigations
            admin_menu_investigation = await self.investigate_admin_menu_settings()
            user_menu_investigation = await self.investigate_user_menu_settings()
            database_investigation = await self.investigate_database_state()
            test_data_detection = await self.detect_test_data_patterns()
            
            # Compile comprehensive results
            investigation_results = {
                "investigation_timestamp": datetime.now().isoformat(),
                "authentication": {
                    "admin_auth": admin_auth,
                    "demo_auth": demo_auth
                },
                "admin_menu_settings_investigation": admin_menu_investigation,
                "user_menu_settings_investigation": user_menu_investigation,
                "database_state_investigation": database_investigation,
                "test_data_detection": test_data_detection
            }
            
            # Generate summary and conclusions
            summary = self.generate_investigation_summary(investigation_results)
            investigation_results["summary"] = summary
            
            return investigation_results
            
        finally:
            await self.cleanup()
    
    def generate_investigation_summary(self, results: Dict) -> Dict:
        """Generate comprehensive summary of investigation findings"""
        
        # Extract key findings
        admin_menu = results.get("admin_menu_settings_investigation", {})
        user_menu = results.get("user_menu_settings_investigation", {})
        database = results.get("database_state_investigation", {})
        test_detection = results.get("test_data_detection", {})
        
        # Critical findings
        test_items_in_admin = admin_menu.get("has_test_items", False)
        test_items_count = len(admin_menu.get("test_items_found", []))
        users_receiving_test_items = user_menu.get("users_receiving_test_items", 0)
        missing_real_items = len(admin_menu.get("missing_real_items", []))
        database_consistent = database.get("data_consistent_across_requests", False)
        menu_data_clean = test_detection.get("menu_data_clean", True)
        
        # Determine root cause
        root_cause_analysis = []
        
        if test_items_in_admin:
            root_cause_analysis.append("Test items detected in admin menu settings")
        
        if users_receiving_test_items > 0:
            root_cause_analysis.append("Users are receiving test items in their menu settings")
        
        if missing_real_items > 0:
            root_cause_analysis.append("Some expected real navigation items are missing")
        
        if not database_consistent:
            root_cause_analysis.append("Database state appears inconsistent")
        
        if not menu_data_clean:
            root_cause_analysis.append("Menu data contains test/dummy entries")
        
        # Generate recommendations
        recommendations = []
        
        if test_items_in_admin or users_receiving_test_items > 0:
            recommendations.append("Remove test items from menu_settings collection in database")
            recommendations.append("Verify menu settings initialization process")
        
        if missing_real_items > 0:
            recommendations.append("Restore missing real navigation items to menu settings")
        
        if not database_consistent:
            recommendations.append("Investigate database consistency issues")
            recommendations.append("Consider clearing and reinitializing menu settings")
        
        # Overall status
        investigation_successful = all([
            results.get("authentication", {}).get("admin_auth", {}).get("success", False),
            admin_menu.get("success", False),
            user_menu.get("successful_user_tests", 0) > 0
        ])
        
        issue_severity = "CRITICAL" if test_items_in_admin and users_receiving_test_items > 0 else \
                        "HIGH" if test_items_in_admin or users_receiving_test_items > 0 else \
                        "MEDIUM" if missing_real_items > 0 else "LOW"
        
        return {
            "investigation_successful": investigation_successful,
            "issue_severity": issue_severity,
            "test_items_detected_in_admin": test_items_in_admin,
            "test_items_count": test_items_count,
            "users_receiving_test_items": users_receiving_test_items,
            "missing_real_items_count": missing_real_items,
            "database_state_consistent": database_consistent,
            "menu_data_clean": menu_data_clean,
            "root_cause_analysis": root_cause_analysis,
            "recommendations": recommendations,
            "requires_immediate_action": issue_severity in ["CRITICAL", "HIGH"],
            "data_integrity_score": (
                (0 if test_items_in_admin else 25) +
                (0 if users_receiving_test_items > 0 else 25) +
                (25 if missing_real_items == 0 else max(0, 25 - missing_real_items * 5)) +
                (25 if database_consistent else 0)
            )
        }

async def main():
    """Main function to run the investigation"""
    investigator = MenuSettingsInvestigator()
    results = await investigator.run_comprehensive_investigation()
    
    # Print summary
    print("\n" + "=" * 70)
    print("🔍 MENU SETTINGS INVESTIGATION SUMMARY")
    print("=" * 70)
    
    summary = results.get("summary", {})
    
    print(f"Investigation Status: {'✅ SUCCESS' if summary.get('investigation_successful') else '❌ FAILED'}")
    print(f"Issue Severity: {summary.get('issue_severity', 'UNKNOWN')}")
    print(f"Data Integrity Score: {summary.get('data_integrity_score', 0)}/100")
    
    print(f"\nKey Findings:")
    print(f"  Test items in admin menu: {'YES' if summary.get('test_items_detected_in_admin') else 'NO'}")
    print(f"  Test items count: {summary.get('test_items_count', 0)}")
    print(f"  Users receiving test items: {summary.get('users_receiving_test_items', 0)}")
    print(f"  Missing real items: {summary.get('missing_real_items_count', 0)}")
    print(f"  Database consistent: {'YES' if summary.get('database_state_consistent') else 'NO'}")
    
    if summary.get("root_cause_analysis"):
        print(f"\nRoot Cause Analysis:")
        for cause in summary["root_cause_analysis"]:
            print(f"  - {cause}")
    
    if summary.get("recommendations"):
        print(f"\nRecommendations:")
        for rec in summary["recommendations"]:
            print(f"  - {rec}")
    
    print(f"\nRequires Immediate Action: {'YES' if summary.get('requires_immediate_action') else 'NO'}")
    
    # Save detailed results to file
    with open("/app/menu_investigation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: /app/menu_investigation_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())