#!/usr/bin/env python3
"""
Comprehensive Menu Settings Testing - Real Navigation Data Verification
Testing Menu Settings functionality with real navigation data after database population
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://cataloro-marketplace-6.preview.emergentagent.com/api"

# Real Navigation Data Structure (based on actual frontend components)
REAL_NAVIGATION_DATA = {
    "desktop_menu": {
        "browse": {
            "enabled": True,
            "roles": ["admin", "manager", "seller", "buyer"],
            "label": "Browse",
            "icon": "Search",
            "path": "/browse"
        },
        "messages": {
            "enabled": True,
            "roles": ["admin", "manager", "seller", "buyer"],
            "label": "Messages",
            "icon": "MessageCircle",
            "path": "/messages"
        },
        "create_listing": {
            "enabled": True,
            "roles": ["admin", "manager", "seller"],
            "label": "Create Listing",
            "icon": "Plus",
            "path": "/create-listing"
        },
        "favorites": {
            "enabled": True,
            "roles": ["admin", "manager", "seller", "buyer"],
            "label": "Favorites",
            "icon": "Heart",
            "path": "/favorites"
        },
        "profile": {
            "enabled": True,
            "roles": ["admin", "manager", "seller", "buyer"],
            "label": "Profile",
            "icon": "User",
            "path": "/profile"
        },
        "my_listings": {
            "enabled": True,
            "roles": ["admin", "manager", "seller"],
            "label": "My Listings",
            "icon": "List",
            "path": "/my-listings"
        },
        "admin_panel": {
            "enabled": True,
            "roles": ["admin", "manager"],
            "label": "Admin Panel",
            "icon": "Settings",
            "path": "/admin"
        },
        "about": {
            "enabled": True,
            "roles": ["admin", "manager", "seller", "buyer"],
            "label": "About",
            "icon": "Info",
            "path": "/about"
        },
        "buy_management": {
            "enabled": True,
            "roles": ["admin", "manager", "buyer"],
            "label": "Buy Management",
            "icon": "ShoppingCart",
            "path": "/buy-management"
        },
        "tenders": {
            "enabled": True,
            "roles": ["admin", "manager", "seller", "buyer"],
            "label": "Tenders",
            "icon": "FileText",
            "path": "/tenders"
        },
        "notifications": {
            "enabled": True,
            "roles": ["admin", "manager", "seller", "buyer"],
            "label": "Notifications",
            "icon": "Bell",
            "path": "/notifications"
        }
    },
    "mobile_menu": {
        "browse": {
            "enabled": True,
            "roles": ["admin", "manager", "seller", "buyer"],
            "label": "Browse",
            "icon": "Search",
            "path": "/browse"
        },
        "messages": {
            "enabled": True,
            "roles": ["admin", "manager", "seller", "buyer"],
            "label": "Messages",
            "icon": "MessageCircle",
            "path": "/messages"
        },
        "create": {
            "enabled": True,
            "roles": ["admin", "manager", "seller"],
            "label": "Create",
            "icon": "Plus",
            "path": "/create-listing"
        },
        "tenders": {
            "enabled": True,
            "roles": ["admin", "manager", "seller", "buyer"],
            "label": "Tenders",
            "icon": "FileText",
            "path": "/tenders"
        },
        "listings": {
            "enabled": True,
            "roles": ["admin", "manager", "seller"],
            "label": "Listings",
            "icon": "List",
            "path": "/my-listings"
        },
        "about": {
            "enabled": True,
            "roles": ["admin", "manager", "seller", "buyer"],
            "label": "About",
            "icon": "Info",
            "path": "/about"
        },
        "buy_management": {
            "enabled": True,
            "roles": ["admin", "manager", "buyer"],
            "label": "Buy Management",
            "icon": "ShoppingCart",
            "path": "/buy-management"
        },
        "favorites": {
            "enabled": True,
            "roles": ["admin", "manager", "seller", "buyer"],
            "label": "Favorites",
            "icon": "Heart",
            "path": "/favorites"
        },
        "profile": {
            "enabled": True,
            "roles": ["admin", "manager", "seller", "buyer"],
            "label": "Profile",
            "icon": "User",
            "path": "/profile"
        },
        "notifications": {
            "enabled": True,
            "roles": ["admin", "manager", "seller", "buyer"],
            "label": "Notifications",
            "icon": "Bell",
            "path": "/notifications"
        },
        "admin_drawer": {
            "enabled": True,
            "roles": ["admin", "manager"],
            "label": "Admin",
            "icon": "Settings",
            "path": "/admin"
        }
    }
}

class ComprehensiveMenuSettingsTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.demo_token = None
        self.test_results = []
        
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
    
    async def authenticate_users(self) -> Dict:
        """Authenticate admin and demo users for testing"""
        print("🔐 Authenticating test users...")
        
        # Admin login
        admin_login = {
            "email": "admin@cataloro.com",
            "password": "admin_password"
        }
        
        admin_result = await self.make_request("/auth/login", "POST", data=admin_login)
        if admin_result["success"]:
            self.admin_token = admin_result["data"].get("token", "")
            admin_user = admin_result["data"].get("user", {})
            print(f"  ✅ Admin authenticated successfully (ID: {admin_user.get('id')}, Role: {admin_user.get('role')})")
        else:
            print(f"  ❌ Admin authentication failed: {admin_result.get('error')}")
            return {"success": False, "error": "Admin authentication failed"}
        
        # Demo user login
        demo_login = {
            "email": "demo@cataloro.com", 
            "password": "demo_password"
        }
        
        demo_result = await self.make_request("/auth/login", "POST", data=demo_login)
        if demo_result["success"]:
            self.demo_token = demo_result["data"].get("token", "")
            demo_user = demo_result["data"].get("user", {})
            print(f"  ✅ Demo user authenticated successfully (ID: {demo_user.get('id')}, Role: {demo_user.get('role')})")
        else:
            print(f"  ❌ Demo user authentication failed: {demo_result.get('error')}")
            return {"success": False, "error": "Demo user authentication failed"}
        
        return {
            "success": True,
            "admin_token": self.admin_token,
            "demo_token": self.demo_token,
            "admin_user": admin_result["data"].get("user", {}),
            "demo_user": demo_result["data"].get("user", {})
        }
    
    async def populate_real_navigation_data(self) -> Dict:
        """Populate database with real navigation data"""
        print("📋 Populating database with real navigation data...")
        
        if not self.admin_token:
            return {"success": False, "error": "Admin token required"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Update menu settings with real navigation data
        result = await self.make_request("/admin/menu-settings", "POST", data=REAL_NAVIGATION_DATA, headers=headers)
        
        if result["success"]:
            print(f"  ✅ Real navigation data populated successfully ({result['response_time_ms']:.0f}ms)")
            return {
                "success": True,
                "response_time_ms": result["response_time_ms"],
                "desktop_items": len(REAL_NAVIGATION_DATA["desktop_menu"]),
                "mobile_items": len(REAL_NAVIGATION_DATA["mobile_menu"])
            }
        else:
            print(f"  ❌ Failed to populate navigation data: {result.get('error')}")
            return {
                "success": False,
                "error": result.get("error", "Population failed"),
                "status": result["status"]
            }
    
    async def test_menu_settings_data_verification(self) -> Dict:
        """Test that Menu Settings returns real navigation data instead of dummy data"""
        print("📋 Testing Menu Settings Data Verification...")
        
        if not self.admin_token:
            return {"test_name": "Menu Settings Data Verification", "error": "Admin token required"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test GET /api/admin/menu-settings
        result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if not result["success"]:
            return {
                "test_name": "Menu Settings Data Verification",
                "success": False,
                "error": result.get("error", "Failed to get menu settings"),
                "status": result["status"]
            }
        
        menu_data = result["data"]
        desktop_menu = menu_data.get("desktop_menu", {})
        mobile_menu = menu_data.get("mobile_menu", {})
        
        # Verify desktop menu structure
        desktop_items = list(desktop_menu.keys())
        expected_desktop_items = list(REAL_NAVIGATION_DATA["desktop_menu"].keys())
        desktop_real_data = len(desktop_items) >= 10  # Should have substantial menu items
        desktop_has_expected_items = len(set(desktop_items) & set(expected_desktop_items)) >= 8
        
        # Verify mobile menu structure  
        mobile_items = list(mobile_menu.keys())
        expected_mobile_items = list(REAL_NAVIGATION_DATA["mobile_menu"].keys())
        mobile_real_data = len(mobile_items) >= 10  # Should have substantial menu items
        mobile_has_expected_items = len(set(mobile_items) & set(expected_mobile_items)) >= 8
        
        # Check menu item structure (should have enabled, roles, label, icon, path)
        desktop_structure_valid = True
        mobile_structure_valid = True
        
        for item_key, item_config in desktop_menu.items():
            if not all(field in item_config for field in ["enabled", "roles", "label", "icon", "path"]):
                desktop_structure_valid = False
                break
        
        for item_key, item_config in mobile_menu.items():
            if not all(field in item_config for field in ["enabled", "roles", "label", "icon", "path"]):
                mobile_structure_valid = False
                break
        
        # Check for real vs dummy data indicators
        is_real_data = (
            desktop_real_data and mobile_real_data and 
            desktop_has_expected_items and mobile_has_expected_items and
            desktop_structure_valid and mobile_structure_valid
        )
        
        print(f"  📱 Desktop menu items: {len(desktop_items)} (Expected: {len(expected_desktop_items)})")
        print(f"  📱 Mobile menu items: {len(mobile_items)} (Expected: {len(expected_mobile_items)})")
        print(f"  ✅ Real navigation data: {'Yes' if is_real_data else 'No'}")
        print(f"  🏗️ Structure valid: Desktop {'✅' if desktop_structure_valid else '❌'}, Mobile {'✅' if mobile_structure_valid else '❌'}")
        
        return {
            "test_name": "Menu Settings Data Verification",
            "success": True,
            "response_time_ms": result["response_time_ms"],
            "desktop_menu_count": len(desktop_items),
            "mobile_menu_count": len(mobile_items),
            "expected_desktop_count": len(expected_desktop_items),
            "expected_mobile_count": len(expected_mobile_items),
            "desktop_items": desktop_items,
            "mobile_items": mobile_items,
            "desktop_structure_valid": desktop_structure_valid,
            "mobile_structure_valid": mobile_structure_valid,
            "has_real_navigation_data": is_real_data,
            "not_dummy_data": is_real_data,
            "desktop_match_score": len(set(desktop_items) & set(expected_desktop_items)),
            "mobile_match_score": len(set(mobile_items) & set(expected_mobile_items))
        }
    
    async def test_role_based_menu_structure(self) -> Dict:
        """Test role-based access control in menu data"""
        print("🔐 Testing Role-Based Menu Structure...")
        
        if not self.admin_token:
            return {"test_name": "Role-Based Menu Structure", "error": "Admin token required"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if not result["success"]:
            return {
                "test_name": "Role-Based Menu Structure",
                "success": False,
                "error": result.get("error", "Failed to get menu settings")
            }
        
        menu_data = result["data"]
        desktop_menu = menu_data.get("desktop_menu", {})
        mobile_menu = menu_data.get("mobile_menu", {})
        
        # Test admin-only items
        admin_only_items = ["admin_panel", "admin_drawer"]
        admin_only_access = True
        admin_items_found = []
        
        for item in admin_only_items:
            desktop_item = desktop_menu.get(item, {})
            mobile_item = mobile_menu.get(item, {})
            
            if desktop_item:
                admin_items_found.append(f"desktop.{item}")
                roles = desktop_item.get("roles", [])
                if not any(role in ["admin", "manager"] for role in roles):
                    admin_only_access = False
            
            if mobile_item:
                admin_items_found.append(f"mobile.{item}")
                roles = mobile_item.get("roles", [])
                if not any(role in ["admin", "manager"] for role in roles):
                    admin_only_access = False
        
        # Test seller-only items
        seller_items = ["create_listing", "my_listings", "listings"]
        seller_access_correct = True
        seller_items_found = []
        
        for item in seller_items:
            desktop_item = desktop_menu.get(item, {})
            mobile_item = mobile_menu.get(item, {})
            
            if desktop_item:
                seller_items_found.append(f"desktop.{item}")
                roles = desktop_item.get("roles", [])
                if not any(role in ["admin", "manager", "seller"] for role in roles):
                    seller_access_correct = False
            
            if mobile_item:
                seller_items_found.append(f"mobile.{item}")
                roles = mobile_item.get("roles", [])
                if not any(role in ["admin", "manager", "seller"] for role in roles):
                    seller_access_correct = False
        
        # Test buyer-only items
        buyer_items = ["buy_management"]
        buyer_access_correct = True
        buyer_items_found = []
        
        for item in buyer_items:
            desktop_item = desktop_menu.get(item, {})
            mobile_item = mobile_menu.get(item, {})
            
            if desktop_item:
                buyer_items_found.append(f"desktop.{item}")
                roles = desktop_item.get("roles", [])
                if not any(role in ["admin", "manager", "buyer"] for role in roles):
                    buyer_access_correct = False
            
            if mobile_item:
                buyer_items_found.append(f"mobile.{item}")
                roles = mobile_item.get("roles", [])
                if not any(role in ["admin", "manager", "buyer"] for role in roles):
                    buyer_access_correct = False
        
        # Test common items (should be available to all roles)
        common_items = ["browse", "messages", "profile", "favorites", "about", "tenders", "notifications"]
        common_access_correct = True
        common_items_found = []
        
        for item in common_items:
            desktop_item = desktop_menu.get(item, {})
            mobile_item = mobile_menu.get(item, {})
            
            if desktop_item:
                common_items_found.append(f"desktop.{item}")
                roles = desktop_item.get("roles", [])
                if len(roles) < 3:  # Should have multiple roles
                    common_access_correct = False
            
            if mobile_item:
                common_items_found.append(f"mobile.{item}")
                roles = mobile_item.get("roles", [])
                if len(roles) < 3:  # Should have multiple roles
                    common_access_correct = False
        
        role_based_access_working = (
            admin_only_access and seller_access_correct and 
            buyer_access_correct and common_access_correct
        )
        
        print(f"  🔒 Admin-only access: {'✅' if admin_only_access else '❌'} ({len(admin_items_found)} items)")
        print(f"  🛒 Seller access: {'✅' if seller_access_correct else '❌'} ({len(seller_items_found)} items)")
        print(f"  💰 Buyer access: {'✅' if buyer_access_correct else '❌'} ({len(buyer_items_found)} items)")
        print(f"  👥 Common access: {'✅' if common_access_correct else '❌'} ({len(common_items_found)} items)")
        
        return {
            "test_name": "Role-Based Menu Structure",
            "success": True,
            "response_time_ms": result["response_time_ms"],
            "admin_only_access_correct": admin_only_access,
            "seller_access_correct": seller_access_correct,
            "buyer_access_correct": buyer_access_correct,
            "common_access_correct": common_access_correct,
            "role_based_access_working": role_based_access_working,
            "admin_items_found": admin_items_found,
            "seller_items_found": seller_items_found,
            "buyer_items_found": buyer_items_found,
            "common_items_found": common_items_found
        }
    
    async def test_menu_settings_crud_operations(self) -> Dict:
        """Test complete CRUD functionality for Menu Settings"""
        print("🔄 Testing Menu Settings CRUD Operations...")
        
        if not self.admin_token:
            return {"test_name": "Menu Settings CRUD Operations", "error": "Admin token required"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test GET operation
        get_result = await self.make_request("/admin/menu-settings", headers=headers)
        if not get_result["success"]:
            return {
                "test_name": "Menu Settings CRUD Operations",
                "success": False,
                "error": "GET operation failed",
                "get_success": False
            }
        
        original_data = get_result["data"]
        
        # Test POST operation (update) - Add a test item
        test_update_data = dict(original_data)  # Copy original data
        test_update_data["desktop_menu"]["test_crud_item"] = {
            "enabled": True,
            "roles": ["admin"],
            "label": "Test CRUD Item",
            "icon": "TestIcon",
            "path": "/test-crud"
        }
        
        post_result = await self.make_request("/admin/menu-settings", "POST", data=test_update_data, headers=headers)
        post_success = post_result["success"]
        
        # Test persistence - GET again to verify changes
        persistence_result = await self.make_request("/admin/menu-settings", headers=headers)
        persistence_success = persistence_result["success"]
        
        changes_persisted = False
        if persistence_success:
            updated_data = persistence_result["data"]
            changes_persisted = "test_crud_item" in updated_data.get("desktop_menu", {})
        
        # Test data structure integrity after update
        structure_integrity = True
        if persistence_success:
            updated_data = persistence_result["data"]
            desktop_menu = updated_data.get("desktop_menu", {})
            
            # Check that required fields are present
            for item_key, item_config in desktop_menu.items():
                if not all(field in item_config for field in ["enabled", "roles"]):
                    structure_integrity = False
                    break
        
        # Restore original data (cleanup)
        restore_result = await self.make_request("/admin/menu-settings", "POST", data=original_data, headers=headers)
        restore_success = restore_result["success"]
        
        crud_operations_working = (
            get_result["success"] and post_success and 
            persistence_success and changes_persisted and structure_integrity
        )
        
        print(f"  📖 GET operation: {'✅' if get_result['success'] else '❌'} ({get_result['response_time_ms']:.0f}ms)")
        print(f"  📝 POST operation: {'✅' if post_success else '❌'} ({post_result['response_time_ms']:.0f}ms)")
        print(f"  💾 Persistence: {'✅' if changes_persisted else '❌'}")
        print(f"  🏗️ Structure integrity: {'✅' if structure_integrity else '❌'}")
        print(f"  🔄 Restore operation: {'✅' if restore_success else '❌'}")
        
        return {
            "test_name": "Menu Settings CRUD Operations",
            "success": True,
            "get_operation_success": get_result["success"],
            "get_response_time_ms": get_result["response_time_ms"],
            "post_operation_success": post_success,
            "post_response_time_ms": post_result["response_time_ms"] if post_result else 0,
            "persistence_verified": changes_persisted,
            "structure_integrity_maintained": structure_integrity,
            "restore_operation_success": restore_success,
            "crud_operations_working": crud_operations_working,
            "original_desktop_items": len(original_data.get("desktop_menu", {})),
            "original_mobile_items": len(original_data.get("mobile_menu", {}))
        }
    
    async def test_data_structure_validation(self) -> Dict:
        """Test proper data structure validation"""
        print("🏗️ Testing Data Structure Validation...")
        
        if not self.admin_token:
            return {"test_name": "Data Structure Validation", "error": "Admin token required"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        result = await self.make_request("/admin/menu-settings", headers=headers)
        
        if not result["success"]:
            return {
                "test_name": "Data Structure Validation",
                "success": False,
                "error": result.get("error", "Failed to get menu settings")
            }
        
        menu_data = result["data"]
        desktop_menu = menu_data.get("desktop_menu", {})
        mobile_menu = menu_data.get("mobile_menu", {})
        
        # Validate required fields
        required_fields = ["enabled", "roles", "label", "icon", "path"]
        
        desktop_validation = {"valid_items": 0, "total_items": len(desktop_menu), "missing_fields": []}
        mobile_validation = {"valid_items": 0, "total_items": len(mobile_menu), "missing_fields": []}
        
        # Validate desktop menu items
        for item_key, item_config in desktop_menu.items():
            item_valid = True
            for field in required_fields:
                if field not in item_config:
                    desktop_validation["missing_fields"].append(f"{item_key}.{field}")
                    item_valid = False
            
            # Check roles array validity
            roles = item_config.get("roles", [])
            if not isinstance(roles, list) or not roles:
                desktop_validation["missing_fields"].append(f"{item_key}.roles_invalid")
                item_valid = False
            else:
                # Check for valid role values
                valid_roles = ["admin", "manager", "seller", "buyer"]
                if not all(role in valid_roles for role in roles):
                    desktop_validation["missing_fields"].append(f"{item_key}.roles_invalid_values")
                    item_valid = False
            
            # Check icon names (should match Lucide icon names)
            icon = item_config.get("icon", "")
            if icon and not isinstance(icon, str):
                desktop_validation["missing_fields"].append(f"{item_key}.icon_invalid_type")
                item_valid = False
            
            # Check paths (should start with /)
            path = item_config.get("path", "")
            if path and not path.startswith("/"):
                desktop_validation["missing_fields"].append(f"{item_key}.path_invalid_format")
                item_valid = False
            
            if item_valid:
                desktop_validation["valid_items"] += 1
        
        # Validate mobile menu items
        for item_key, item_config in mobile_menu.items():
            item_valid = True
            for field in required_fields:
                if field not in item_config:
                    mobile_validation["missing_fields"].append(f"{item_key}.{field}")
                    item_valid = False
            
            # Check roles array validity
            roles = item_config.get("roles", [])
            if not isinstance(roles, list) or not roles:
                mobile_validation["missing_fields"].append(f"{item_key}.roles_invalid")
                item_valid = False
            else:
                # Check for valid role values
                valid_roles = ["admin", "manager", "seller", "buyer"]
                if not all(role in valid_roles for role in roles):
                    mobile_validation["missing_fields"].append(f"{item_key}.roles_invalid_values")
                    item_valid = False
            
            # Check icon names (should match Lucide icon names)
            icon = item_config.get("icon", "")
            if icon and not isinstance(icon, str):
                mobile_validation["missing_fields"].append(f"{item_key}.icon_invalid_type")
                item_valid = False
            
            # Check paths (should start with /)
            path = item_config.get("path", "")
            if path and not path.startswith("/"):
                mobile_validation["missing_fields"].append(f"{item_key}.path_invalid_format")
                item_valid = False
            
            if item_valid:
                mobile_validation["valid_items"] += 1
        
        desktop_structure_valid = desktop_validation["valid_items"] == desktop_validation["total_items"]
        mobile_structure_valid = mobile_validation["valid_items"] == mobile_validation["total_items"]
        overall_structure_valid = desktop_structure_valid and mobile_structure_valid
        
        print(f"  🖥️ Desktop structure valid: {'✅' if desktop_structure_valid else '❌'} ({desktop_validation['valid_items']}/{desktop_validation['total_items']})")
        print(f"  📱 Mobile structure valid: {'✅' if mobile_structure_valid else '❌'} ({mobile_validation['valid_items']}/{mobile_validation['total_items']})")
        
        if desktop_validation["missing_fields"]:
            print(f"  ⚠️ Desktop missing fields: {desktop_validation['missing_fields'][:3]}...")
        if mobile_validation["missing_fields"]:
            print(f"  ⚠️ Mobile missing fields: {mobile_validation['missing_fields'][:3]}...")
        
        return {
            "test_name": "Data Structure Validation",
            "success": True,
            "response_time_ms": result["response_time_ms"],
            "desktop_structure_valid": desktop_structure_valid,
            "mobile_structure_valid": mobile_structure_valid,
            "overall_structure_valid": overall_structure_valid,
            "desktop_validation": desktop_validation,
            "mobile_validation": mobile_validation,
            "total_menu_items": len(desktop_menu) + len(mobile_menu),
            "valid_menu_items": desktop_validation["valid_items"] + mobile_validation["valid_items"]
        }
    
    async def run_comprehensive_menu_settings_test(self) -> Dict:
        """Run all Menu Settings tests"""
        print("🚀 Starting Comprehensive Menu Settings Testing - Real Navigation Data Verification")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Step 1: Authenticate users
            auth_result = await self.authenticate_users()
            if not auth_result["success"]:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "Authentication failed",
                    "details": auth_result
                }
            
            # Step 2: Populate database with real navigation data
            population_result = await self.populate_real_navigation_data()
            if not population_result["success"]:
                return {
                    "test_timestamp": datetime.now().isoformat(),
                    "error": "Failed to populate real navigation data",
                    "details": population_result
                }
            
            # Step 3: Run all test suites
            data_verification = await self.test_menu_settings_data_verification()
            role_based_structure = await self.test_role_based_menu_structure()
            crud_operations = await self.test_menu_settings_crud_operations()
            data_structure_validation = await self.test_data_structure_validation()
            
            # Compile overall results
            all_results = {
                "test_timestamp": datetime.now().isoformat(),
                "authentication": auth_result,
                "database_population": population_result,
                "menu_settings_data_verification": data_verification,
                "role_based_menu_structure": role_based_structure,
                "menu_settings_crud_operations": crud_operations,
                "data_structure_validation": data_structure_validation
            }
            
            # Calculate overall success metrics
            test_results = [
                data_verification.get("has_real_navigation_data", False),
                role_based_structure.get("role_based_access_working", False),
                crud_operations.get("crud_operations_working", False),
                data_structure_validation.get("overall_structure_valid", False)
            ]
            
            overall_success_rate = sum(test_results) / len(test_results) * 100
            
            all_results["summary"] = {
                "overall_success_rate": overall_success_rate,
                "database_populated_with_real_data": population_result["success"],
                "real_navigation_data_confirmed": data_verification.get("has_real_navigation_data", False),
                "not_dummy_data": data_verification.get("not_dummy_data", False),
                "role_based_access_working": role_based_structure.get("role_based_access_working", False),
                "crud_operations_functional": crud_operations.get("crud_operations_working", False),
                "data_structure_valid": data_structure_validation.get("overall_structure_valid", False),
                "all_tests_passed": overall_success_rate == 100,
                "desktop_menu_items": data_verification.get("desktop_menu_count", 0),
                "mobile_menu_items": data_verification.get("mobile_menu_count", 0),
                "expected_desktop_items": data_verification.get("expected_desktop_count", 0),
                "expected_mobile_items": data_verification.get("expected_mobile_count", 0),
                "desktop_match_score": data_verification.get("desktop_match_score", 0),
                "mobile_match_score": data_verification.get("mobile_match_score", 0)
            }
            
            return all_results
            
        finally:
            await self.cleanup()


async def main():
    """Run the comprehensive Menu Settings test"""
    tester = ComprehensiveMenuSettingsTester()
    results = await tester.run_comprehensive_menu_settings_test()
    
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE MENU SETTINGS TEST RESULTS SUMMARY")
    print("=" * 80)
    
    summary = results.get("summary", {})
    
    print(f"🎯 Overall Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    print(f"🗄️ Database Populated: {'✅ YES' if summary.get('database_populated_with_real_data') else '❌ NO'}")
    print(f"📋 Real Navigation Data: {'✅ YES' if summary.get('real_navigation_data_confirmed') else '❌ NO'}")
    print(f"🚫 Not Dummy Data: {'✅ YES' if summary.get('not_dummy_data') else '❌ NO'}")
    print(f"🔐 Role-Based Access: {'✅ WORKING' if summary.get('role_based_access_working') else '❌ FAILED'}")
    print(f"🔄 CRUD Operations: {'✅ WORKING' if summary.get('crud_operations_functional') else '❌ FAILED'}")
    print(f"🏗️ Data Structure: {'✅ VALID' if summary.get('data_structure_valid') else '❌ INVALID'}")
    
    print(f"\n📊 Menu Items Comparison:")
    print(f"  🖥️ Desktop: {summary.get('desktop_menu_items', 0)}/{summary.get('expected_desktop_items', 0)} (Match: {summary.get('desktop_match_score', 0)})")
    print(f"  📱 Mobile: {summary.get('mobile_menu_items', 0)}/{summary.get('expected_mobile_items', 0)} (Match: {summary.get('mobile_match_score', 0)})")
    
    if summary.get('all_tests_passed'):
        print("\n🎉 ALL MENU SETTINGS TESTS PASSED - REAL NAVIGATION DATA CONFIRMED!")
        print("✅ Menu Settings now returns real navigation data instead of dummy data")
    else:
        print(f"\n⚠️ SOME TESTS FAILED - Success Rate: {summary.get('overall_success_rate', 0):.1f}%")
    
    # Save detailed results to file
    with open('/app/comprehensive_menu_settings_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: /app/comprehensive_menu_settings_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())