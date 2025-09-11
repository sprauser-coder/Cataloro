#!/usr/bin/env python3
"""
CRITICAL DATABASE INVESTIGATION - CATS DATABASE MISSING
Investigating reported data loss: "Cats database is completely gone!"
Testing MongoDB collections and catalyst-related data
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Test Configuration
BACKEND_URL = "https://dynamic-marketplace.preview.emergentagent.com/api"

# Admin User Configuration
ADMIN_EMAIL = "admin@cataloro.com"
ADMIN_USERNAME = "sash_admin"
ADMIN_ROLE = "admin"
ADMIN_ID = "admin_user_1"

class CriticalDatabaseInvestigator:
    """
    URGENT: Critical data investigation for missing cats/catalyst database
    User reports: "Cats database is completely gone!"
    """
    def __init__(self):
        self.session = None
        self.admin_token = None
        self.investigation_results = {}
        
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
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin for database investigation...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        result = await self.make_request("/auth/login", "POST", data=login_data)
        
        if result["success"]:
            self.admin_token = result["data"].get("token", "")
            print(f"  ✅ Admin authentication successful")
            return True
        else:
            print(f"  ❌ Admin authentication failed: {result.get('error', 'Unknown error')}")
            return False
    
    async def investigate_database_collections(self) -> Dict:
        """
        CRITICAL: Investigate what collections exist in MongoDB
        Check for cats, catalyst_data, catalyst_prices, catalyst_overrides
        """
        print("🔍 CRITICAL: Investigating MongoDB collections for missing cats/catalyst data...")
        
        if not self.admin_token:
            return {"test_name": "Database Collections Investigation", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        investigation_results = {
            "collections_found": [],
            "catalyst_related_collections": [],
            "document_counts": {},
            "missing_collections": [],
            "potential_data_loss": False
        }
        
        # Check for catalyst-related endpoints that might indicate collection existence
        catalyst_endpoints_to_check = [
            "/admin/catalyst-data",
            "/admin/catalyst-prices", 
            "/admin/catalyst-overrides",
            "/admin/cats",
            "/catalyst-data",
            "/catalyst-prices",
            "/cats",
            "/admin/database-status",
            "/admin/collections"
        ]
        
        print("  🔍 Checking catalyst-related API endpoints...")
        for endpoint in catalyst_endpoints_to_check:
            result = await self.make_request(endpoint, headers=headers)
            
            if result["success"]:
                investigation_results["collections_found"].append({
                    "endpoint": endpoint,
                    "status": "ACCESSIBLE",
                    "data_present": bool(result.get("data")),
                    "response_size": len(str(result.get("data", "")))
                })
                
                if "catalyst" in endpoint.lower() or "cat" in endpoint.lower():
                    investigation_results["catalyst_related_collections"].append(endpoint)
                    
                    # Try to count documents if data is returned
                    data = result.get("data", {})
                    if isinstance(data, list):
                        investigation_results["document_counts"][endpoint] = len(data)
                    elif isinstance(data, dict) and "count" in data:
                        investigation_results["document_counts"][endpoint] = data["count"]
                    elif isinstance(data, dict) and "data" in data:
                        if isinstance(data["data"], list):
                            investigation_results["document_counts"][endpoint] = len(data["data"])
                        
            else:
                investigation_results["missing_collections"].append({
                    "endpoint": endpoint,
                    "status": "NOT_ACCESSIBLE",
                    "error": result.get("error", "Unknown error"),
                    "status_code": result.get("status", 0)
                })
        
        # Check general database/admin endpoints for collection info
        admin_endpoints = [
            "/admin/performance",
            "/admin/database-stats", 
            "/admin/system-info"
        ]
        
        print("  📊 Checking admin endpoints for database information...")
        for endpoint in admin_endpoints:
            result = await self.make_request(endpoint, headers=headers)
            if result["success"]:
                data = result.get("data", {})
                
                # Look for collection information in the response
                if "collections" in data:
                    investigation_results["collections_found"].append({
                        "endpoint": endpoint,
                        "collections_info": data["collections"],
                        "status": "FOUND_COLLECTION_INFO"
                    })
                
                # Look for database statistics
                if "database" in data:
                    investigation_results["database_stats"] = data["database"]
        
        # Determine if there's potential data loss
        catalyst_accessible = len(investigation_results["catalyst_related_collections"]) > 0
        total_missing = len(investigation_results["missing_collections"])
        
        investigation_results["potential_data_loss"] = not catalyst_accessible and total_missing > 3
        investigation_results["summary"] = {
            "catalyst_endpoints_accessible": len(investigation_results["catalyst_related_collections"]),
            "total_endpoints_checked": len(catalyst_endpoints_to_check),
            "missing_endpoints": total_missing,
            "data_loss_likely": investigation_results["potential_data_loss"]
        }
        
        print(f"  📊 Collections investigation complete:")
        print(f"    - Catalyst endpoints accessible: {len(investigation_results['catalyst_related_collections'])}")
        print(f"    - Total endpoints missing: {total_missing}")
        print(f"    - Potential data loss: {investigation_results['potential_data_loss']}")
        
        return {
            "test_name": "Database Collections Investigation",
            "success": True,
            "investigation_results": investigation_results,
            "critical_finding": investigation_results["potential_data_loss"],
            "accessible_catalyst_endpoints": investigation_results["catalyst_related_collections"],
            "document_counts": investigation_results["document_counts"]
        }
    
    async def check_catalyst_data_endpoints(self) -> Dict:
        """
        Check specific catalyst data endpoints for data presence
        """
        print("🧪 Checking catalyst data endpoints for actual data...")
        
        if not self.admin_token:
            return {"test_name": "Catalyst Data Check", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        catalyst_data_results = {
            "catalyst_data": {"exists": False, "count": 0, "sample": None},
            "catalyst_prices": {"exists": False, "count": 0, "sample": None},
            "catalyst_overrides": {"exists": False, "count": 0, "sample": None},
            "cats_collection": {"exists": False, "count": 0, "sample": None}
        }
        
        # Check catalyst data endpoint
        print("  🔍 Checking catalyst data...")
        catalyst_result = await self.make_request("/admin/catalyst-data", headers=headers)
        if catalyst_result["success"]:
            data = catalyst_result.get("data", {})
            if isinstance(data, list):
                catalyst_data_results["catalyst_data"]["exists"] = True
                catalyst_data_results["catalyst_data"]["count"] = len(data)
                catalyst_data_results["catalyst_data"]["sample"] = data[:3] if data else None
            elif isinstance(data, dict) and "catalyst_data" in data:
                catalyst_list = data["catalyst_data"]
                catalyst_data_results["catalyst_data"]["exists"] = True
                catalyst_data_results["catalyst_data"]["count"] = len(catalyst_list) if isinstance(catalyst_list, list) else 0
                catalyst_data_results["catalyst_data"]["sample"] = catalyst_list[:3] if isinstance(catalyst_list, list) and catalyst_list else None
        
        # Check catalyst prices endpoint
        print("  💰 Checking catalyst prices...")
        prices_result = await self.make_request("/admin/catalyst-prices", headers=headers)
        if prices_result["success"]:
            data = prices_result.get("data", {})
            if isinstance(data, dict):
                catalyst_data_results["catalyst_prices"]["exists"] = True
                catalyst_data_results["catalyst_prices"]["sample"] = data
                # Count price settings
                price_fields = ["pt_price", "pd_price", "rh_price"]
                catalyst_data_results["catalyst_prices"]["count"] = sum(1 for field in price_fields if field in data)
        
        # Check catalyst overrides endpoint  
        print("  🔧 Checking catalyst overrides...")
        overrides_result = await self.make_request("/admin/catalyst-overrides", headers=headers)
        if overrides_result["success"]:
            data = overrides_result.get("data", {})
            if isinstance(data, list):
                catalyst_data_results["catalyst_overrides"]["exists"] = True
                catalyst_data_results["catalyst_overrides"]["count"] = len(data)
                catalyst_data_results["catalyst_overrides"]["sample"] = data[:3] if data else None
            elif isinstance(data, dict) and "overrides" in data:
                overrides_list = data["overrides"]
                catalyst_data_results["catalyst_overrides"]["exists"] = True
                catalyst_data_results["catalyst_overrides"]["count"] = len(overrides_list) if isinstance(overrides_list, list) else 0
                catalyst_data_results["catalyst_overrides"]["sample"] = overrides_list[:3] if isinstance(overrides_list, list) and overrides_list else None
        
        # Try alternative endpoints for cats data
        cats_endpoints = ["/cats", "/admin/cats", "/catalyst/cats", "/admin/catalyst/cats"]
        print("  🐱 Checking cats collection endpoints...")
        for endpoint in cats_endpoints:
            cats_result = await self.make_request(endpoint, headers=headers)
            if cats_result["success"]:
                data = cats_result.get("data", {})
                if data:
                    catalyst_data_results["cats_collection"]["exists"] = True
                    if isinstance(data, list):
                        catalyst_data_results["cats_collection"]["count"] = len(data)
                        catalyst_data_results["cats_collection"]["sample"] = data[:3] if data else None
                    break
        
        # Calculate summary
        total_collections = len(catalyst_data_results)
        existing_collections = sum(1 for result in catalyst_data_results.values() if result["exists"])
        total_documents = sum(result["count"] for result in catalyst_data_results.values())
        
        data_loss_confirmed = existing_collections == 0 and total_documents == 0
        
        print(f"  📊 Catalyst data check complete:")
        print(f"    - Collections existing: {existing_collections}/{total_collections}")
        print(f"    - Total documents found: {total_documents}")
        print(f"    - Data loss confirmed: {data_loss_confirmed}")
        
        return {
            "test_name": "Catalyst Data Check",
            "success": True,
            "catalyst_data_results": catalyst_data_results,
            "summary": {
                "total_collections_checked": total_collections,
                "existing_collections": existing_collections,
                "total_documents": total_documents,
                "data_loss_confirmed": data_loss_confirmed
            },
            "critical_finding": data_loss_confirmed
        }
    
    async def check_listings_for_catalyst_fields(self) -> Dict:
        """
        Check existing listings for catalyst-related fields
        This might indicate if catalyst data was integrated into listings
        """
        print("📋 Checking listings for catalyst-related fields...")
        
        # Get some listings to check for catalyst fields
        listings_result = await self.make_request("/marketplace/browse")
        
        catalyst_fields_found = {
            "listings_checked": 0,
            "listings_with_catalyst_fields": 0,
            "catalyst_fields_present": [],
            "sample_catalyst_data": []
        }
        
        if listings_result["success"]:
            listings = listings_result.get("data", [])
            catalyst_fields_found["listings_checked"] = len(listings)
            
            # Check for catalyst-related fields in listings
            catalyst_field_names = [
                "ceramic_weight", "pt_ppm", "pd_ppm", "rh_ppm",
                "catalyst_id", "cat_id", "catalyst_data",
                "pt_price", "pd_price", "rh_price"
            ]
            
            for listing in listings[:10]:  # Check first 10 listings
                listing_has_catalyst = False
                listing_catalyst_fields = []
                
                for field in catalyst_field_names:
                    if field in listing and listing[field] is not None:
                        listing_has_catalyst = True
                        listing_catalyst_fields.append(field)
                        
                        if field not in catalyst_fields_found["catalyst_fields_present"]:
                            catalyst_fields_found["catalyst_fields_present"].append(field)
                
                if listing_has_catalyst:
                    catalyst_fields_found["listings_with_catalyst_fields"] += 1
                    catalyst_fields_found["sample_catalyst_data"].append({
                        "listing_id": listing.get("id", "unknown"),
                        "catalyst_fields": listing_catalyst_fields,
                        "sample_values": {field: listing.get(field) for field in listing_catalyst_fields[:3]}
                    })
        
        catalyst_integration_exists = len(catalyst_fields_found["catalyst_fields_present"]) > 0
        
        print(f"  📊 Listings catalyst check complete:")
        print(f"    - Listings checked: {catalyst_fields_found['listings_checked']}")
        print(f"    - Listings with catalyst fields: {catalyst_fields_found['listings_with_catalyst_fields']}")
        print(f"    - Catalyst fields found: {catalyst_fields_found['catalyst_fields_present']}")
        print(f"    - Catalyst integration exists: {catalyst_integration_exists}")
        
        return {
            "test_name": "Listings Catalyst Fields Check",
            "success": True,
            "catalyst_fields_found": catalyst_fields_found,
            "catalyst_integration_exists": catalyst_integration_exists,
            "potential_data_migration": catalyst_integration_exists and catalyst_fields_found["listings_with_catalyst_fields"] > 0
        }
    
    async def check_database_backup_collections(self) -> Dict:
        """
        Check for potential backup or renamed collections
        """
        print("💾 Checking for backup or renamed catalyst collections...")
        
        if not self.admin_token:
            return {"test_name": "Backup Collections Check", "error": "No admin token available"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Try various backup/renamed collection patterns
        backup_patterns = [
            "/admin/catalyst-data-backup",
            "/admin/catalyst_data_backup", 
            "/admin/cats-backup",
            "/admin/cats_backup",
            "/admin/catalyst-data-old",
            "/admin/catalyst_data_old",
            "/admin/catalyst-archive",
            "/admin/catalyst_archive",
            "/admin/catalyst-data-v1",
            "/admin/catalyst-data-v2",
            "/admin/catalyst-migration",
            "/admin/old-catalyst-data",
            "/admin/legacy-catalyst-data"
        ]
        
        backup_results = {
            "backup_collections_found": [],
            "backup_collections_missing": [],
            "total_backup_documents": 0
        }
        
        for pattern in backup_patterns:
            result = await self.make_request(pattern, headers=headers)
            
            if result["success"]:
                data = result.get("data", {})
                if data:
                    doc_count = 0
                    if isinstance(data, list):
                        doc_count = len(data)
                    elif isinstance(data, dict) and "count" in data:
                        doc_count = data["count"]
                    
                    backup_results["backup_collections_found"].append({
                        "endpoint": pattern,
                        "document_count": doc_count,
                        "sample_data": str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
                    })
                    backup_results["total_backup_documents"] += doc_count
            else:
                backup_results["backup_collections_missing"].append(pattern)
        
        backups_exist = len(backup_results["backup_collections_found"]) > 0
        
        print(f"  📊 Backup collections check complete:")
        print(f"    - Backup collections found: {len(backup_results['backup_collections_found'])}")
        print(f"    - Total backup documents: {backup_results['total_backup_documents']}")
        print(f"    - Backups exist: {backups_exist}")
        
        return {
            "test_name": "Backup Collections Check", 
            "success": True,
            "backup_results": backup_results,
            "backups_exist": backups_exist,
            "recovery_possible": backups_exist and backup_results["total_backup_documents"] > 0
        }
    
    async def run_critical_database_investigation(self) -> Dict:
        """
        Run complete critical database investigation for missing cats/catalyst data
        """
        print("🚨 STARTING CRITICAL DATABASE INVESTIGATION")
        print("=" * 80)
        print("USER REPORT: 'Cats database is completely gone!'")
        print("INVESTIGATING: MongoDB collections and catalyst-related data")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Authenticate first
            auth_success = await self.authenticate_admin()
            if not auth_success:
                return {
                    "investigation_timestamp": datetime.now().isoformat(),
                    "error": "Admin authentication failed - cannot proceed with investigation"
                }
            
            # Run all investigation tests
            collections_investigation = await self.investigate_database_collections()
            catalyst_data_check = await self.check_catalyst_data_endpoints()
            listings_catalyst_check = await self.check_listings_for_catalyst_fields()
            backup_collections_check = await self.check_database_backup_collections()
            
            # Compile comprehensive investigation results
            investigation_results = {
                "investigation_timestamp": datetime.now().isoformat(),
                "user_report": "Cats database is completely gone!",
                "collections_investigation": collections_investigation,
                "catalyst_data_check": catalyst_data_check,
                "listings_catalyst_check": listings_catalyst_check,
                "backup_collections_check": backup_collections_check
            }
            
            # Determine critical findings
            data_loss_confirmed = (
                catalyst_data_check.get("critical_finding", False) and
                not listings_catalyst_check.get("catalyst_integration_exists", False) and
                not backup_collections_check.get("backups_exist", False)
            )
            
            recovery_options = []
            if backup_collections_check.get("recovery_possible", False):
                recovery_options.append("Backup collections found - data recovery possible")
            if listings_catalyst_check.get("potential_data_migration", False):
                recovery_options.append("Catalyst data may have been migrated to listings")
            if not data_loss_confirmed:
                recovery_options.append("Some catalyst endpoints still accessible")
            
            investigation_results["critical_summary"] = {
                "data_loss_confirmed": data_loss_confirmed,
                "catalyst_endpoints_accessible": len(collections_investigation.get("accessible_catalyst_endpoints", [])),
                "total_catalyst_documents": catalyst_data_check.get("summary", {}).get("total_documents", 0),
                "backup_collections_found": len(backup_collections_check.get("backup_results", {}).get("backup_collections_found", [])),
                "recovery_options_available": len(recovery_options),
                "recovery_options": recovery_options,
                "investigation_status": "COMPLETE",
                "urgent_action_required": data_loss_confirmed and len(recovery_options) == 0
            }
            
            return investigation_results
            
        finally:
            await self.cleanup()


async def main():
    """Run CRITICAL DATABASE INVESTIGATION for missing cats/catalyst data"""
    print("🚨 STARTING CRITICAL DATABASE INVESTIGATION")
    print("=" * 80)
    print("USER REPORT: 'Cats database is completely gone!'")
    print("MISSION: Investigate MongoDB collections and catalyst-related data loss")
    print("=" * 80)
    
    # Run Critical Database Investigation
    investigator = CriticalDatabaseInvestigator()
    investigation_results = await investigator.run_critical_database_investigation()
    
    print("\n" + "=" * 80)
    print("🚨 CRITICAL DATABASE INVESTIGATION RESULTS")
    print("=" * 80)
    
    critical_summary = investigation_results.get("critical_summary", {})
    print(f"Data Loss Confirmed: {'🚨 YES' if critical_summary.get('data_loss_confirmed') else '✅ NO'}")
    print(f"Catalyst Endpoints Accessible: {critical_summary.get('catalyst_endpoints_accessible', 0)}")
    print(f"Total Catalyst Documents: {critical_summary.get('total_catalyst_documents', 0)}")
    print(f"Backup Collections Found: {critical_summary.get('backup_collections_found', 0)}")
    print(f"Recovery Options Available: {critical_summary.get('recovery_options_available', 0)}")
    print(f"Urgent Action Required: {'🚨 YES' if critical_summary.get('urgent_action_required') else '✅ NO'}")
    
    if critical_summary.get("recovery_options"):
        print("\n🔧 RECOVERY OPTIONS:")
        for option in critical_summary["recovery_options"]:
            print(f"  - {option}")
    
    # Save critical investigation results
    with open('/app/critical_database_investigation.json', 'w') as f:
        json.dump(investigation_results, f, indent=2)
    
    print(f"\n📄 Critical investigation results saved to: /app/critical_database_investigation.json")
    
    return investigation_results


if __name__ == "__main__":
    asyncio.run(main())