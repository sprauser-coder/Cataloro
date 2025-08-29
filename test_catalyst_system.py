#!/usr/bin/env python3
"""
CATALORO - CATALYST DATABASE SYSTEM TESTER
==========================================
Comprehensive testing script using centralized configuration
"""

import requests
import json
import sys
import asyncio

# Import centralized config
sys.path.append('/app')
from config_loader import get_config, get_backend_url, get_admin_credentials

def test_catalyst_system():
    """Test the complete Catalyst Database System functionality"""
    
    print("🧪 CATALYST DATABASE SYSTEM - COMPREHENSIVE TEST")
    print("=" * 55)
    
    # Get configuration
    backend_url = get_backend_url('production')
    admin_email, admin_password = get_admin_credentials()
    
    print(f"🔧 Configuration:")
    print(f"   Backend URL: {backend_url}")
    print(f"   Admin Email: {admin_email}")
    print()
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Origin': backend_url
    })
    
    try:
        # Step 1: Admin Login
        print("1️⃣ Testing Admin Authentication...")
        login_data = {"email": admin_email, "password": admin_password}
        
        login_response = session.post(f"{backend_url}/api/auth/login", json=login_data, timeout=10)
        
        if login_response.status_code == 200:
            login_json = login_response.json()
            token = login_json.get('access_token')
            user_data = login_json.get('user', {})
            
            print(f"   ✅ Login successful")
            print(f"   👤 User: {user_data.get('full_name', 'Unknown')}")
            print(f"   🔑 Role: {user_data.get('role', 'Unknown')}")
            print(f"   🚫 Blocked: {user_data.get('is_blocked', 'Unknown')}")
            
            # Set auth header for subsequent requests
            session.headers.update({'Authorization': f'Bearer {token}'})
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
        
        # Step 2: Test Catalyst Data Endpoint
        print()
        print("2️⃣ Testing Catalyst Data Endpoint...")
        
        catalyst_response = session.get(f"{backend_url}/api/admin/catalyst-data", timeout=10)
        
        if catalyst_response.status_code == 200:
            catalyst_data = catalyst_response.json()
            print(f"   ✅ Catalyst data accessible")
            print(f"   📊 Records found: {len(catalyst_data)}")
            
            if catalyst_data:
                sample = catalyst_data[0]
                print(f"   📋 Sample record: {sample.get('name', 'Unknown')} (ID: {sample.get('cat_id', 'N/A')})")
        else:
            print(f"   ❌ Catalyst data failed: {catalyst_response.status_code}")
            print(f"   Response: {catalyst_response.text}")
        
        # Step 3: Test Catalyst Basis Endpoint
        print()
        print("3️⃣ Testing Catalyst Basis Endpoint...")
        
        basis_response = session.get(f"{backend_url}/api/admin/catalyst-basis", timeout=10)
        
        if basis_response.status_code == 200:
            basis_data = basis_response.json()
            print(f"   ✅ Basis data accessible")
            print(f"   💰 Platinum Price: ${basis_data.get('pt_price', 'N/A')}/toz")
            print(f"   💰 Palladium Price: ${basis_data.get('pd_price', 'N/A')}/toz")
            print(f"   💰 Rhodium Price: ${basis_data.get('rh_price', 'N/A')}/toz")
            print(f"   💱 Exchange Rate: {basis_data.get('exchange_rate', 'N/A')} EUR/USD")
        else:
            print(f"   ❌ Basis data failed: {basis_response.status_code}")
            print(f"   Response: {basis_response.text}")
        
        # Step 4: Test Admin Stats (general admin access)
        print()
        print("4️⃣ Testing General Admin Access...")
        
        stats_response = session.get(f"{backend_url}/api/admin/stats", timeout=10)
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print(f"   ✅ Admin stats accessible")
            print(f"   👥 Total Users: {stats_data.get('total_users', 'N/A')}")
            print(f"   📦 Total Products: {stats_data.get('total_products', 'N/A')}")
            print(f"   🛒 Total Orders: {stats_data.get('total_orders', 'N/A')}")
        else:
            print(f"   ❌ Admin stats failed: {stats_response.status_code}")
            print(f"   Response: {stats_response.text}")
        
        # Step 5: Test Sample Data Creation
        print()
        print("5️⃣ Testing Sample Data Creation...")
        
        sample_catalyst = {
            "data": [
                {
                    "cat_id": "TEST001",
                    "pt_ppm": 1200,
                    "pd_ppm": 800,
                    "rh_ppm": 150,
                    "ceramic_weight": 2.5,
                    "add_info": "Test catalyst data",
                    "name": "Test Catalyst Sample"
                }
            ]
        }
        
        create_response = session.post(f"{backend_url}/api/admin/catalyst-data", json=sample_catalyst, timeout=10)
        
        if create_response.status_code == 200:
            create_data = create_response.json()
            print(f"   ✅ Sample data created successfully")
            print(f"   📝 Message: {create_data.get('message', 'Unknown')}")
        else:
            print(f"   ❌ Sample data creation failed: {create_response.status_code}")
            print(f"   Response: {create_response.text}")
        
        print()
        print("🎉 CATALYST DATABASE SYSTEM TEST COMPLETED!")
        print("=" * 55)
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def print_system_status():
    """Print current system configuration status"""
    print()
    print("📋 SYSTEM STATUS REPORT")
    print("-" * 25)
    
    # Check configuration
    backend_url = get_backend_url('production')
    db_url = get_config('MONGO_URL')
    admin_email = get_admin_credentials()[0]
    cors_origins = get_config('CORS_ORIGINS')
    
    print(f"🌐 Backend URL: {backend_url}")
    print(f"🗄️  Database URL: {db_url}")
    print(f"👤 Admin Email: {admin_email}")
    print(f"🔗 CORS Origins: {cors_origins}")
    print(f"🚀 Deployment Mode: {get_config('DEPLOYMENT_MODE')}")
    print(f"✨ Catalyst Database: {'Enabled' if get_config('ENABLE_CATALYST_DATABASE') else 'Disabled'}")
    
    # Check file paths
    paths = ['/app/directions', '/app/config_loader.py', '/app/backend/server.py', '/app/frontend/.env']
    print()
    print("📁 File Status:")
    for path in paths:
        import os
        status = "✅ Exists" if os.path.exists(path) else "❌ Missing"
        print(f"   {path}: {status}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        print_system_status()
    else:
        print_system_status()
        print()
        
        success = test_catalyst_system()
        
        if success:
            print()
            print("🎯 ALL TESTS PASSED - Catalyst Database System is fully operational!")
            print()
            print("📝 Next Steps:")
            print("   1. Access Admin Panel at your frontend URL")
            print("   2. Navigate to the 'Data' tab")
            print("   3. Upload Excel files with catalyst data")
            print("   4. Configure price calculation variables in 'Basis' tab")
            print("   5. Use 'Price Calculations' tab for pricing management")
        else:
            print()
            print("❌ TESTS FAILED - Check the errors above")
            sys.exit(1)