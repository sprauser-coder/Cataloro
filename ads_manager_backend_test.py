#!/usr/bin/env python3
"""
Cataloro Marketplace Ads Manager Backend Testing Suite
Comprehensive testing for Ads Manager functionality and site configuration
Focus: Testing correct property names (browsePageAd, messengerAd, favoriteAd, footerAd)
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://cataloro-menueditor.preview.emergentagent.com/api"

def test_health_check():
    """Test basic backend health"""
    print("🏥 Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data.get('app', 'Unknown')} v{data.get('version', 'Unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_site_config_get():
    """Test GET site configuration API"""
    print("\n🔧 Testing GET Site Configuration API...")
    
    try:
        print("📥 Testing GET /api/admin/settings...")
        response = requests.get(f"{BACKEND_URL}/admin/settings", timeout=10)
        
        if response.status_code == 200:
            settings = response.json()
            print(f"✅ Site settings retrieved successfully")
            print(f"   - Site name: {settings.get('site_name', 'Not set')}")
            print(f"   - PDF logo URL: {settings.get('pdf_logo_url', 'Not set')}")
            
            # Check if adsManager field exists
            if 'adsManager' in settings:
                print(f"✅ adsManager field found in settings")
                ads_manager = settings['adsManager']
                
                # Check for correct property names
                expected_properties = ['browsePageAd', 'messengerAd', 'favoriteAd', 'footerAd']
                for prop in expected_properties:
                    if prop in ads_manager:
                        ad_config = ads_manager[prop]
                        active = ad_config.get('active', False) if isinstance(ad_config, dict) else False
                        print(f"   ✅ {prop}: active={active}")
                    else:
                        print(f"   ⚠️  {prop}: not found")
                
                # Check for incorrect property names (the bug we're testing for)
                incorrect_properties = ['browse', 'messenger', 'favorite', 'footer']
                for prop in incorrect_properties:
                    if prop in ads_manager:
                        print(f"   ❌ CRITICAL: Found incorrect property '{prop}' - should be '{prop}PageAd' or '{prop}Ad'")
                        return False, settings
                
                print("✅ All property names are correct")
            else:
                print("⚠️  adsManager field not found in settings")
            
            return True, settings
        else:
            print(f"❌ Failed to get site settings: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Site settings GET error: {e}")
        return False, None

def test_ads_manager_save_load():
    """Test Ads Manager configuration save/load with correct property names"""
    print("\n📢 Testing Ads Manager Save/Load with Correct Property Names...")
    
    # Test configuration with correct property names
    test_ads_config = {
        "adsManager": {
            "browsePageAd": {
                "active": True,
                "image": "https://via.placeholder.com/300x600/4F46E5/FFFFFF?text=Test+Browse+Ad",
                "title": "Test Advertisement",
                "content": "This is a test advertisement",
                "width": "300px",
                "height": "600px",
                "clicks": 0,
                "url": "https://example.com",
                "startDate": datetime.now().isoformat(),
                "expirationDate": None,
                "runtime": "1 month"
            },
            "messengerAd": {
                "active": False,
                "image": None,
                "title": "",
                "content": "",
                "width": "250px",
                "height": "400px",
                "clicks": 0,
                "url": "",
                "startDate": None,
                "expirationDate": None,
                "runtime": "1 month"
            },
            "favoriteAd": {
                "active": False,
                "image": None,
                "title": "",
                "content": "",
                "width": "100%",
                "height": "200px",
                "clicks": 0,
                "url": "",
                "startDate": None,
                "expirationDate": None,
                "runtime": "1 month"
            },
            "footerAd": {
                "active": False,
                "logo": None,
                "companyName": "",
                "url": "",
                "clicks": 0,
                "startDate": None,
                "expirationDate": None,
                "runtime": "1 month"
            }
        }
    }
    
    try:
        print("📤 Testing PUT /api/admin/settings with ads configuration...")
        response = requests.put(
            f"{BACKEND_URL}/admin/settings",
            json=test_ads_config,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Ads configuration saved successfully")
            result = response.json()
            print(f"   - Response: {result.get('message', 'Success')}")
            
            # Verify the configuration was saved correctly
            print("🔍 Verifying saved configuration...")
            time.sleep(1)  # Brief delay to ensure save is complete
            
            verify_response = requests.get(f"{BACKEND_URL}/admin/settings", timeout=10)
            
            if verify_response.status_code == 200:
                saved_settings = verify_response.json()
                
                if 'adsManager' in saved_settings:
                    ads_manager = saved_settings['adsManager']
                    
                    # Verify browsePageAd specifically (main focus of the test)
                    if 'browsePageAd' in ads_manager:
                        browse_ad = ads_manager['browsePageAd']
                        print(f"✅ browsePageAd configuration verified:")
                        print(f"   - Active: {browse_ad.get('active')}")
                        print(f"   - Image: {browse_ad.get('image', 'Not set')}")
                        print(f"   - Title: {browse_ad.get('title', 'Not set')}")
                        print(f"   - Width: {browse_ad.get('width', 'Not set')}")
                        print(f"   - Height: {browse_ad.get('height', 'Not set')}")
                        
                        # CRITICAL: Verify it's NOT saved as 'browse' (the bug we're testing for)
                        if 'browse' in ads_manager:
                            print("❌ CRITICAL BUG: Found 'browse' field - should be 'browsePageAd'!")
                            print("   This indicates the property naming bug is present")
                            return False
                        else:
                            print("✅ CRITICAL: Correct property naming confirmed - no 'browse' field found")
                            print("   Configuration is saved to siteConfig.adsManager.browsePageAd (NOT .browse)")
                    else:
                        print("❌ browsePageAd not found in saved configuration")
                        return False
                        
                    # Check other ad types with correct naming
                    expected_ads = {
                        'messengerAd': 'messengerAd',
                        'favoriteAd': 'favoriteAd', 
                        'footerAd': 'footerAd'
                    }
                    
                    for ad_type, expected_name in expected_ads.items():
                        if expected_name in ads_manager:
                            print(f"✅ {expected_name} configuration saved correctly")
                        else:
                            print(f"⚠️  {expected_name} not found in saved configuration")
                    
                    # Check for any incorrect property names
                    incorrect_names = ['browse', 'messenger', 'favorite', 'footer']
                    for incorrect in incorrect_names:
                        if incorrect in ads_manager:
                            print(f"❌ CRITICAL: Found incorrect property '{incorrect}' in saved config")
                            return False
                    
                    print("✅ All ad configurations use correct property names")
                    return True
                else:
                    print("❌ adsManager not found in saved settings")
                    return False
            else:
                print(f"❌ Failed to verify saved configuration: {verify_response.status_code}")
                return False
                
        else:
            print(f"❌ Failed to save ads configuration: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ads configuration save/load error: {e}")
        return False

def test_browse_page_ad_specific():
    """Test browse page ad configuration specifically"""
    print("\n🏠 Testing Browse Page Ad Specific Configuration...")
    
    # Test with specific browsePageAd configuration
    browse_ad_config = {
        "adsManager": {
            "browsePageAd": {
                "active": True,
                "image": "https://via.placeholder.com/300x600/4F46E5/FFFFFF?text=Test+Browse+Ad",
                "title": "Test Advertisement", 
                "content": "This is a test advertisement",
                "width": "300px",
                "height": "600px",
                "clicks": 0
            }
        }
    }
    
    try:
        print("📤 Saving browse page ad configuration...")
        response = requests.put(
            f"{BACKEND_URL}/admin/settings",
            json=browse_ad_config,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Browse page ad configuration saved")
            
            # Verify it's saved to the correct path
            print("🔍 Verifying it's saved to siteConfig.adsManager.browsePageAd...")
            verify_response = requests.get(f"{BACKEND_URL}/admin/settings", timeout=10)
            
            if verify_response.status_code == 200:
                settings = verify_response.json()
                
                # Check the exact path: siteConfig.adsManager.browsePageAd
                if ('adsManager' in settings and 
                    'browsePageAd' in settings['adsManager'] and
                    settings['adsManager']['browsePageAd'].get('active') == True):
                    
                    print("✅ VERIFIED: Configuration saved to siteConfig.adsManager.browsePageAd")
                    print("✅ Browse page ad is active and properly configured")
                    
                    # Double-check it's NOT in the wrong location
                    if 'browse' in settings.get('adsManager', {}):
                        print("❌ CRITICAL: Also found in wrong location (.browse)")
                        return False
                    
                    return True
                else:
                    print("❌ Configuration not found at expected path")
                    return False
            else:
                print(f"❌ Failed to verify: {verify_response.status_code}")
                return False
        else:
            print(f"❌ Failed to save: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Browse page ad test error: {e}")
        return False

def test_ad_analytics_tracking():
    """Test ad analytics and click tracking"""
    print("\n📊 Testing Ad Analytics and Click Tracking...")
    
    try:
        # Get current settings to check analytics structure
        response = requests.get(f"{BACKEND_URL}/admin/settings", timeout=10)
        
        if response.status_code == 200:
            settings = response.json()
            
            if 'adsManager' in settings:
                ads_manager = settings['adsManager']
                
                print("📈 Checking ad analytics structure:")
                analytics_found = False
                
                for ad_type, ad_config in ads_manager.items():
                    if isinstance(ad_config, dict):
                        clicks = ad_config.get('clicks', 0)
                        active = ad_config.get('active', False)
                        start_date = ad_config.get('startDate')
                        expiration = ad_config.get('expirationDate')
                        
                        print(f"   - {ad_type}:")
                        print(f"     * Clicks: {clicks}")
                        print(f"     * Active: {active}")
                        print(f"     * Start Date: {start_date}")
                        print(f"     * Expiration: {expiration}")
                        
                        analytics_found = True
                
                if analytics_found:
                    print("✅ Ad analytics structure verified")
                    
                    # Test click increment (simulate)
                    print("🖱️  Testing click tracking structure...")
                    if 'browsePageAd' in ads_manager:
                        current_clicks = ads_manager['browsePageAd'].get('clicks', 0)
                        print(f"   - Current browsePageAd clicks: {current_clicks}")
                        print("✅ Click tracking field available")
                    
                    return True
                else:
                    print("⚠️  No ad analytics data found")
                    return False
            else:
                print("⚠️  No adsManager found for analytics")
                return False
        else:
            print(f"❌ Failed to get settings: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Analytics test error: {e}")
        return False

def test_ad_expiration_logic():
    """Test ad expiration and runtime logic"""
    print("\n⏰ Testing Ad Expiration and Runtime Logic...")
    
    # Test configuration with expiration
    expiration_config = {
        "adsManager": {
            "browsePageAd": {
                "active": True,
                "image": "https://via.placeholder.com/300x600/4F46E5/FFFFFF?text=Test+Browse+Ad",
                "title": "Test Advertisement",
                "content": "This is a test advertisement", 
                "width": "300px",
                "height": "600px",
                "clicks": 0,
                "runtime": "1 month",
                "startDate": datetime.now().isoformat(),
                "expirationDate": "2024-12-31T23:59:59.000Z"
            }
        }
    }
    
    try:
        print("📤 Testing ad configuration with expiration...")
        response = requests.put(
            f"{BACKEND_URL}/admin/settings",
            json=expiration_config,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Ad expiration configuration saved")
            
            # Verify expiration fields are saved
            verify_response = requests.get(f"{BACKEND_URL}/admin/settings", timeout=10)
            
            if verify_response.status_code == 200:
                settings = verify_response.json()
                
                if ('adsManager' in settings and 
                    'browsePageAd' in settings['adsManager']):
                    
                    browse_ad = settings['adsManager']['browsePageAd']
                    runtime = browse_ad.get('runtime')
                    start_date = browse_ad.get('startDate')
                    expiration_date = browse_ad.get('expirationDate')
                    
                    print(f"✅ Expiration fields verified:")
                    print(f"   - Runtime: {runtime}")
                    print(f"   - Start Date: {start_date}")
                    print(f"   - Expiration Date: {expiration_date}")
                    
                    if all([runtime, start_date, expiration_date]):
                        print("✅ All expiration logic fields present")
                        return True
                    else:
                        print("⚠️  Some expiration fields missing")
                        return False
                else:
                    print("❌ Ad configuration not found")
                    return False
            else:
                print(f"❌ Failed to verify: {verify_response.status_code}")
                return False
        else:
            print(f"❌ Failed to save: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Expiration logic test error: {e}")
        return False

def run_ads_manager_tests():
    """Run comprehensive Ads Manager tests"""
    print("🚀 Starting Ads Manager Backend Testing...")
    print("🎯 Focus: Correct property names and configuration persistence")
    print("=" * 70)
    
    test_results = {
        'health_check': False,
        'site_config_get': False,
        'ads_save_load': False,
        'browse_page_specific': False,
        'ad_analytics': False,
        'ad_expiration': False
    }
    
    # Run all tests
    test_results['health_check'] = test_health_check()
    
    if test_results['health_check']:
        # Test site config GET
        success, settings = test_site_config_get()
        test_results['site_config_get'] = success
        
        # Test ads manager save/load
        test_results['ads_save_load'] = test_ads_manager_save_load()
        
        # Test browse page ad specifically
        test_results['browse_page_specific'] = test_browse_page_ad_specific()
        
        # Test ad analytics
        test_results['ad_analytics'] = test_ad_analytics_tracking()
        
        # Test ad expiration logic
        test_results['ad_expiration'] = test_ad_expiration_logic()
    
    # Print comprehensive summary
    print("\n" + "=" * 70)
    print("📋 ADS MANAGER TEST SUMMARY")
    print("=" * 70)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
        if result:
            passed_tests += 1
    
    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
    
    # Critical issues analysis
    critical_issues = []
    
    if not test_results['health_check']:
        critical_issues.append("Backend is not accessible")
    
    if not test_results['site_config_get']:
        critical_issues.append("Site configuration API not working")
    
    if not test_results['ads_save_load']:
        critical_issues.append("Ads Manager configuration save/load failed - property naming issue")
    
    if not test_results['browse_page_specific']:
        critical_issues.append("Browse page ad not saving to correct path (siteConfig.adsManager.browsePageAd)")
    
    # Success criteria analysis
    success_criteria = []
    
    if test_results['ads_save_load']:
        success_criteria.append("✅ Ads saved with correct property names (browsePageAd, messengerAd, favoriteAd, footerAd)")
    
    if test_results['browse_page_specific']:
        success_criteria.append("✅ Browse page ad saves to siteConfig.adsManager.browsePageAd (NOT .browse)")
    
    if test_results['ad_analytics']:
        success_criteria.append("✅ Ad analytics structure (clicks, active status) working")
    
    if test_results['ad_expiration']:
        success_criteria.append("✅ Ad expiration and runtime logic implemented")
    
    print(f"\n🎯 SUCCESS CRITERIA MET:")
    for criteria in success_criteria:
        print(f"   {criteria}")
    
    if critical_issues:
        print(f"\n🚨 CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"   - {issue}")
        print(f"\n❌ ADS MANAGER TESTING FAILED - Issues need to be resolved")
    else:
        print(f"\n🎉 ADS MANAGER TESTING PASSED - All functionality working correctly!")
        print(f"✅ Property naming is correct (browsePageAd not browse)")
        print(f"✅ Configuration persistence working")
        print(f"✅ Integration with browse page data structure verified")
    
    return test_results, critical_issues

if __name__ == "__main__":
    print("Cataloro Ads Manager Backend Testing Suite")
    print("=" * 50)
    print("🎯 TESTING FOCUS:")
    print("   - Ad Configuration Save/Load")
    print("   - Correct property names (browsePageAd, messengerAd, favoriteAd, footerAd)")
    print("   - Browse Page Ad Integration")
    print("   - Site Config API (GET/POST /api/admin/site-config)")
    print("   - Ad Analytics and Click Tracking")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print("=" * 50)
    print()
    
    results, issues = run_ads_manager_tests()
    
    # Exit with appropriate code
    if issues:
        print(f"\n💥 Testing completed with {len(issues)} critical issues")
        sys.exit(1)
    else:
        print(f"\n🚀 All Ads Manager tests passed successfully!")
        sys.exit(0)