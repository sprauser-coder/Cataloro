#!/usr/bin/env python3
"""
Field Name Mismatch Analysis Test
Identifying exact field name mismatches between backend and frontend expectations
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://admanager-cataloro.preview.emergentagent.com/api"

class FieldMismatchAnalyzer:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        
    def get_backend_dashboard_fields(self):
        """Get actual field names from backend dashboard"""
        try:
            response = self.session.get(f"{self.backend_url}/admin/dashboard")
            if response.status_code == 200:
                data = response.json()
                return data.get("kpis", {})
            return None
        except Exception as e:
            print(f"Error getting backend data: {e}")
            return None
    
    def analyze_field_mismatches(self):
        """Analyze field name mismatches between backend and frontend"""
        
        # Get actual backend fields
        backend_kpis = self.get_backend_dashboard_fields()
        if not backend_kpis:
            print("❌ Could not retrieve backend dashboard data")
            return
        
        print("=" * 80)
        print("FIELD NAME MISMATCH ANALYSIS")
        print("=" * 80)
        print()
        
        print("BACKEND PROVIDES:")
        print("-" * 40)
        for field, value in backend_kpis.items():
            print(f"  {field}: {value}")
        print()
        
        # Frontend expectations based on code analysis
        frontend_expectations = {
            # Revenue field mismatch
            "total_revenue": {
                "backend_field": "revenue",
                "backend_value": backend_kpis.get("revenue"),
                "usage": "Used in multiple places for revenue display and calculations"
            },
            
            # Active listings field mismatch  
            "active_products": {
                "backend_field": "active_listings", 
                "backend_value": backend_kpis.get("active_listings"),
                "usage": "Used for active listings count display"
            },
            
            # Total products field mismatch
            "total_products": {
                "backend_field": "total_listings",
                "backend_value": backend_kpis.get("total_listings"), 
                "usage": "Used for total listings count and inactive calculation"
            },
            
            # Conversion rate missing
            "conversion_rate": {
                "backend_field": None,
                "backend_value": None,
                "usage": "Expected for conversion rate calculations but not provided by backend"
            }
        }
        
        print("FRONTEND EXPECTS vs BACKEND PROVIDES:")
        print("-" * 60)
        
        critical_mismatches = []
        
        for frontend_field, info in frontend_expectations.items():
            backend_field = info["backend_field"]
            backend_value = info["backend_value"]
            usage = info["usage"]
            
            print(f"\nFrontend expects: '{frontend_field}'")
            
            if backend_field:
                if backend_field in backend_kpis:
                    print(f"  ✅ Backend provides: '{backend_field}' = {backend_value}")
                    print(f"  ❌ FIELD NAME MISMATCH: '{frontend_field}' != '{backend_field}'")
                    critical_mismatches.append({
                        "frontend": frontend_field,
                        "backend": backend_field,
                        "value": backend_value,
                        "type": "name_mismatch"
                    })
                else:
                    print(f"  ❌ Backend field '{backend_field}' not found")
                    critical_mismatches.append({
                        "frontend": frontend_field,
                        "backend": backend_field,
                        "value": None,
                        "type": "missing_backend_field"
                    })
            else:
                print(f"  ❌ NO BACKEND EQUIVALENT FOUND")
                critical_mismatches.append({
                    "frontend": frontend_field,
                    "backend": None,
                    "value": None,
                    "type": "missing_calculation"
                })
            
            print(f"  Usage: {usage}")
        
        print("\n" + "=" * 80)
        print("CRITICAL FIELD MAPPING ISSUES")
        print("=" * 80)
        
        if critical_mismatches:
            for i, mismatch in enumerate(critical_mismatches, 1):
                print(f"\n{i}. ISSUE: {mismatch['type'].upper()}")
                print(f"   Frontend expects: '{mismatch['frontend']}'")
                if mismatch['backend']:
                    print(f"   Backend provides: '{mismatch['backend']}' = {mismatch['value']}")
                else:
                    print(f"   Backend provides: NOTHING")
                
                # Provide fix recommendations
                if mismatch['type'] == 'name_mismatch':
                    print(f"   🔧 FIX: Frontend should use '{mismatch['backend']}' instead of '{mismatch['frontend']}'")
                elif mismatch['type'] == 'missing_backend_field':
                    print(f"   🔧 FIX: Backend needs to provide '{mismatch['frontend']}' field")
                elif mismatch['type'] == 'missing_calculation':
                    print(f"   🔧 FIX: Backend needs to calculate and provide '{mismatch['frontend']}'")
        
        print("\n" + "=" * 80)
        print("IMPACT ANALYSIS")
        print("=" * 80)
        
        print("\n1. REVENUE DISPLAY ISSUE:")
        print(f"   - Frontend looks for 'total_revenue' but backend provides 'revenue'")
        print(f"   - This causes revenue to show as 0 or undefined in frontend")
        print(f"   - Actual revenue value: €{backend_kpis.get('revenue', 0)}")
        
        print("\n2. LISTINGS COUNT ISSUE:")
        print(f"   - Frontend looks for 'active_products' but backend provides 'active_listings'")
        print(f"   - This causes active listings to show incorrectly")
        print(f"   - Actual active listings: {backend_kpis.get('active_listings', 0)}")
        
        print("\n3. TOTAL LISTINGS ISSUE:")
        print(f"   - Frontend looks for 'total_products' but backend provides 'total_listings'")
        print(f"   - This affects inactive listings calculation")
        print(f"   - Actual total listings: {backend_kpis.get('total_listings', 0)}")
        
        print("\n4. CONVERSION RATE MISSING:")
        print(f"   - Frontend expects 'conversion_rate' but backend doesn't provide it")
        print(f"   - Frontend tries to calculate from total_deals/total_users")
        print(f"   - Backend provides 'growth_rate' instead: {backend_kpis.get('growth_rate', 0)}%")
        
        print("\n" + "=" * 80)
        print("RECOMMENDED FIXES")
        print("=" * 80)
        
        print("\nOPTION 1: Fix Frontend (Recommended)")
        print("  Change frontend AdminPanel.js to use correct field names:")
        print("  - Replace 'kpis.total_revenue' with 'kpis.revenue'")
        print("  - Replace 'kpis.active_products' with 'kpis.active_listings'") 
        print("  - Replace 'kpis.total_products' with 'kpis.total_listings'")
        print("  - Use 'kpis.growth_rate' instead of 'conversion_rate'")
        
        print("\nOPTION 2: Fix Backend")
        print("  Add field aliases in backend dashboard response:")
        print("  - Add 'total_revenue': revenue")
        print("  - Add 'active_products': active_listings")
        print("  - Add 'total_products': total_listings")
        print("  - Calculate and add 'conversion_rate'")
        
        print("\n" + "=" * 80)
        print("VERIFICATION TEST")
        print("=" * 80)
        
        # Test what happens when we use correct field names
        print("\nIf frontend used correct field names:")
        print(f"  Revenue would show: €{backend_kpis.get('revenue', 0)}")
        print(f"  Active listings would show: {backend_kpis.get('active_listings', 0)}")
        print(f"  Total listings would show: {backend_kpis.get('total_listings', 0)}")
        print(f"  Growth rate would show: {backend_kpis.get('growth_rate', 0)}%")
        
        # Calculate what conversion rate would be
        total_deals = backend_kpis.get('total_deals', 0)
        total_users = backend_kpis.get('total_users', 1)
        calculated_conversion = (total_deals / max(1, total_users)) * 100
        print(f"  Calculated conversion rate: {calculated_conversion:.1f}%")
        
        return critical_mismatches

if __name__ == "__main__":
    analyzer = FieldMismatchAnalyzer()
    mismatches = analyzer.analyze_field_mismatches()
    
    if mismatches:
        print(f"\n🔍 ANALYSIS COMPLETE: Found {len(mismatches)} field mapping issues")
        print("📋 See detailed analysis above for exact fixes needed")
    else:
        print("\n✅ No field mapping issues found")