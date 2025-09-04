#!/usr/bin/env python3
"""
Enhanced Hero Image CMS Backend Testing
Testing enhanced hero image functionality for About Page CMS
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "https://cataloro-admin-4.preview.emergentagent.com/api"

def test_enhanced_hero_image_cms():
    """Test enhanced hero image functionality for CMS"""
    print("🎯 ENHANCED HERO IMAGE CMS TESTING STARTED")
    print("=" * 60)
    
    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "test_details": []
    }
    
    # Test data with enhanced hero image fields
    enhanced_hero_content = {
        "hero": {
            "title": "Cataloro Marketplace",
            "subtitle": "The Future of Online Commerce",
            "description": "Experience the next generation of online marketplace with advanced features, seamless transactions, and intelligent matching.",
            "heroImage": "https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&h=600&fit=crop&crop=center",
            "showHeroImage": True,
            "heroImagePosition": "right",
            "backgroundImage": "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=1920&h=1080&fit=crop&crop=center",
            "primaryButtonText": "Get Started",
            "secondaryButtonText": "Browse Marketplace"
        },
        "stats": [
            {"label": "Active Users", "value": "25K+", "icon": "users", "color": "#3B82F6"},
            {"label": "Products Listed", "value": "150K+", "icon": "package", "color": "#10B981"},
            {"label": "Successful Deals", "value": "75K+", "icon": "handshake", "color": "#F59E0B"},
            {"label": "User Rating", "value": "4.9★", "icon": "star", "color": "#EF4444"}
        ],
        "features": {
            "title": "Platform Features",
            "description": "Discover all the powerful features that make our marketplace the most advanced platform for buying and selling."
        },
        "cta": {
            "title": "Ready to Get Started?",
            "description": "Join thousands of users who are already experiencing the future of online commerce.",
            "primaryButtonText": "Start Your Journey",
            "secondaryButtonText": "Explore Platform"
        }
    }
    
    # Test 1: Save enhanced hero content with new image fields
    print("\n1. Testing PUT /api/admin/content with enhanced hero image fields...")
    test_results["total_tests"] += 1
    
    try:
        response = requests.put(f"{BACKEND_URL}/admin/content", json=enhanced_hero_content)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Content saved successfully")
            print(f"   📝 Response: {result.get('message', 'No message')}")
            if 'version' in result:
                print(f"   🔢 Version: {result['version']}")
            test_results["passed_tests"] += 1
            test_results["test_details"].append({
                "test": "Save enhanced hero content",
                "status": "PASSED",
                "details": f"Content saved with version {result.get('version', 'unknown')}"
            })
        else:
            print(f"   ❌ Failed to save content: {response.status_code}")
            print(f"   📝 Response: {response.text}")
            test_results["failed_tests"] += 1
            test_results["test_details"].append({
                "test": "Save enhanced hero content",
                "status": "FAILED",
                "details": f"HTTP {response.status_code}: {response.text}"
            })
    except Exception as e:
        print(f"   ❌ Exception during content save: {str(e)}")
        test_results["failed_tests"] += 1
        test_results["test_details"].append({
            "test": "Save enhanced hero content",
            "status": "FAILED",
            "details": f"Exception: {str(e)}"
        })
    
    # Test 2: Retrieve and verify enhanced hero content
    print("\n2. Testing GET /api/admin/content to verify enhanced hero fields...")
    test_results["total_tests"] += 1
    
    try:
        response = requests.get(f"{BACKEND_URL}/admin/content")
        
        if response.status_code == 200:
            content = response.json()
            hero_section = content.get("hero", {})
            
            # Check for enhanced hero image fields
            required_fields = ["heroImage", "showHeroImage", "heroImagePosition", "backgroundImage"]
            missing_fields = []
            present_fields = []
            
            for field in required_fields:
                if field in hero_section:
                    present_fields.append(field)
                else:
                    missing_fields.append(field)
            
            print(f"   📋 Hero section fields found: {list(hero_section.keys())}")
            print(f"   ✅ Enhanced fields present: {present_fields}")
            
            if missing_fields:
                print(f"   ⚠️  Missing enhanced fields: {missing_fields}")
            
            # Verify specific values
            verification_results = []
            if hero_section.get("title") == "Cataloro Marketplace":
                verification_results.append("✅ Title correct")
            else:
                verification_results.append(f"❌ Title mismatch: {hero_section.get('title')}")
            
            if hero_section.get("subtitle") == "The Future of Online Commerce":
                verification_results.append("✅ Subtitle correct")
            else:
                verification_results.append(f"❌ Subtitle mismatch: {hero_section.get('subtitle')}")
            
            if hero_section.get("heroImage") == "https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&h=600&fit=crop&crop=center":
                verification_results.append("✅ Hero image URL correct")
            else:
                verification_results.append(f"❌ Hero image URL mismatch: {hero_section.get('heroImage')}")
            
            if hero_section.get("showHeroImage") == True:
                verification_results.append("✅ Show hero image flag correct")
            else:
                verification_results.append(f"❌ Show hero image flag mismatch: {hero_section.get('showHeroImage')}")
            
            if hero_section.get("heroImagePosition") == "right":
                verification_results.append("✅ Hero image position correct")
            else:
                verification_results.append(f"❌ Hero image position mismatch: {hero_section.get('heroImagePosition')}")
            
            if hero_section.get("backgroundImage") == "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=1920&h=1080&fit=crop&crop=center":
                verification_results.append("✅ Background image URL correct")
            else:
                verification_results.append(f"❌ Background image URL mismatch: {hero_section.get('backgroundImage')}")
            
            for result in verification_results:
                print(f"   {result}")
            
            # Check if all verifications passed
            failed_verifications = [r for r in verification_results if r.startswith("❌")]
            if not failed_verifications and not missing_fields:
                print(f"   ✅ All enhanced hero image fields verified successfully")
                test_results["passed_tests"] += 1
                test_results["test_details"].append({
                    "test": "Verify enhanced hero content",
                    "status": "PASSED",
                    "details": f"All {len(required_fields)} enhanced fields present and correct"
                })
            else:
                print(f"   ⚠️  Some verifications failed or fields missing")
                test_results["failed_tests"] += 1
                test_results["test_details"].append({
                    "test": "Verify enhanced hero content",
                    "status": "FAILED",
                    "details": f"Missing fields: {missing_fields}, Failed verifications: {len(failed_verifications)}"
                })
                
        else:
            print(f"   ❌ Failed to retrieve content: {response.status_code}")
            test_results["failed_tests"] += 1
            test_results["test_details"].append({
                "test": "Verify enhanced hero content",
                "status": "FAILED",
                "details": f"HTTP {response.status_code}: {response.text}"
            })
    except Exception as e:
        print(f"   ❌ Exception during content retrieval: {str(e)}")
        test_results["failed_tests"] += 1
        test_results["test_details"].append({
            "test": "Verify enhanced hero content",
            "status": "FAILED",
            "details": f"Exception: {str(e)}"
        })
    
    # Test 3: Test content structure for admin panel compatibility
    print("\n3. Testing content structure for admin panel PNG upload compatibility...")
    test_results["total_tests"] += 1
    
    try:
        response = requests.get(f"{BACKEND_URL}/admin/content")
        
        if response.status_code == 200:
            content = response.json()
            hero_section = content.get("hero", {})
            
            # Check structure compatibility for admin panel
            admin_compatibility_checks = []
            
            # Check if heroImage field exists (for PNG/JPG uploads)
            if "heroImage" in hero_section:
                admin_compatibility_checks.append("✅ heroImage field ready for PNG/JPG uploads")
            else:
                admin_compatibility_checks.append("❌ heroImage field missing for uploads")
            
            # Check if showHeroImage exists (for visibility toggle)
            if "showHeroImage" in hero_section:
                admin_compatibility_checks.append("✅ showHeroImage field ready for visibility control")
            else:
                admin_compatibility_checks.append("❌ showHeroImage field missing for visibility control")
            
            # Check if heroImagePosition exists (for positioning control)
            if "heroImagePosition" in hero_section:
                admin_compatibility_checks.append("✅ heroImagePosition field ready for position control")
            else:
                admin_compatibility_checks.append("❌ heroImagePosition field missing for position control")
            
            # Check if backgroundImage exists (separate from hero image)
            if "backgroundImage" in hero_section:
                admin_compatibility_checks.append("✅ backgroundImage field ready for background management")
            else:
                admin_compatibility_checks.append("❌ backgroundImage field missing for background management")
            
            for check in admin_compatibility_checks:
                print(f"   {check}")
            
            failed_checks = [c for c in admin_compatibility_checks if c.startswith("❌")]
            if not failed_checks:
                print(f"   ✅ Content structure fully compatible with admin panel image management")
                test_results["passed_tests"] += 1
                test_results["test_details"].append({
                    "test": "Admin panel compatibility",
                    "status": "PASSED",
                    "details": "All required fields present for admin panel image management"
                })
            else:
                print(f"   ⚠️  Some compatibility issues found")
                test_results["failed_tests"] += 1
                test_results["test_details"].append({
                    "test": "Admin panel compatibility",
                    "status": "FAILED",
                    "details": f"{len(failed_checks)} compatibility issues found"
                })
                
        else:
            print(f"   ❌ Failed to check compatibility: {response.status_code}")
            test_results["failed_tests"] += 1
            test_results["test_details"].append({
                "test": "Admin panel compatibility",
                "status": "FAILED",
                "details": f"HTTP {response.status_code}: Could not retrieve content"
            })
    except Exception as e:
        print(f"   ❌ Exception during compatibility check: {str(e)}")
        test_results["failed_tests"] += 1
        test_results["test_details"].append({
            "test": "Admin panel compatibility",
            "status": "FAILED",
            "details": f"Exception: {str(e)}"
        })
    
    # Test 4: Test content persistence across multiple requests
    print("\n4. Testing content persistence across multiple requests...")
    test_results["total_tests"] += 1
    
    try:
        # Make multiple requests to ensure data persists
        persistence_results = []
        for i in range(3):
            response = requests.get(f"{BACKEND_URL}/admin/content")
            if response.status_code == 200:
                content = response.json()
                hero_section = content.get("hero", {})
                
                # Check key fields
                if (hero_section.get("title") == "Cataloro Marketplace" and 
                    hero_section.get("heroImage") and 
                    hero_section.get("showHeroImage") == True):
                    persistence_results.append(f"✅ Request {i+1}: Data persistent")
                else:
                    persistence_results.append(f"❌ Request {i+1}: Data inconsistent")
            else:
                persistence_results.append(f"❌ Request {i+1}: HTTP {response.status_code}")
            
            time.sleep(0.5)  # Small delay between requests
        
        for result in persistence_results:
            print(f"   {result}")
        
        failed_persistence = [r for r in persistence_results if r.startswith("❌")]
        if not failed_persistence:
            print(f"   ✅ Content persistence verified across multiple requests")
            test_results["passed_tests"] += 1
            test_results["test_details"].append({
                "test": "Content persistence",
                "status": "PASSED",
                "details": "Data consistent across 3 requests"
            })
        else:
            print(f"   ⚠️  Persistence issues detected")
            test_results["failed_tests"] += 1
            test_results["test_details"].append({
                "test": "Content persistence",
                "status": "FAILED",
                "details": f"{len(failed_persistence)} requests failed"
            })
            
    except Exception as e:
        print(f"   ❌ Exception during persistence test: {str(e)}")
        test_results["failed_tests"] += 1
        test_results["test_details"].append({
            "test": "Content persistence",
            "status": "FAILED",
            "details": f"Exception: {str(e)}"
        })
    
    # Print final results
    print("\n" + "=" * 60)
    print("🎯 ENHANCED HERO IMAGE CMS TESTING COMPLETED")
    print("=" * 60)
    
    print(f"\n📊 TEST SUMMARY:")
    print(f"   Total Tests: {test_results['total_tests']}")
    print(f"   Passed: {test_results['passed_tests']} ✅")
    print(f"   Failed: {test_results['failed_tests']} ❌")
    
    success_rate = (test_results['passed_tests'] / test_results['total_tests']) * 100 if test_results['total_tests'] > 0 else 0
    print(f"   Success Rate: {success_rate:.1f}%")
    
    print(f"\n📋 DETAILED RESULTS:")
    for detail in test_results['test_details']:
        status_icon = "✅" if detail['status'] == "PASSED" else "❌"
        print(f"   {status_icon} {detail['test']}: {detail['status']}")
        print(f"      {detail['details']}")
    
    # Determine overall status
    if test_results['failed_tests'] == 0:
        print(f"\n🎉 OVERALL STATUS: ALL TESTS PASSED - Enhanced Hero Image CMS functionality is FULLY OPERATIONAL")
        return True
    else:
        print(f"\n⚠️  OVERALL STATUS: {test_results['failed_tests']} TESTS FAILED - Some issues need attention")
        return False

if __name__ == "__main__":
    test_enhanced_hero_image_cms()