#!/usr/bin/env python3
"""
SIMPLE LOGO UPLOAD TEST
Quick test of logo upload and image serving functionality
"""

import requests
import json
import sys
import os
import io
from PIL import Image

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cataloro-hub.preview.emergentagent.com') + '/api'
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def create_test_image(format='PNG', size=(100, 100)):
    """Create a simple test image"""
    img = Image.new('RGB', size, color='red')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format=format)
    img_buffer.seek(0)
    return img_buffer

def test_logo_upload():
    """Test logo upload functionality"""
    session = requests.Session()
    
    print("🔐 Authenticating as admin...")
    
    # Step 1: Login
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.status_code}")
        return False
    
    data = response.json()
    admin_token = data["access_token"]
    print("✅ Authentication successful")
    
    # Step 2: Test logo upload
    print("📤 Testing logo upload...")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    png_image = create_test_image('PNG', (200, 200))
    files = {'file': ('test_logo.png', png_image, 'image/png')}
    
    response = session.post(f"{BACKEND_URL}/admin/cms/upload-logo", headers=headers, files=files, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        logo_url = data.get('logo_url')
        print(f"✅ Logo upload successful: {logo_url}")
        
        # Step 3: Test image accessibility
        print("🌐 Testing image accessibility...")
        
        if logo_url.startswith('/uploads/'):
            full_url = BACKEND_URL.replace('/api', '') + logo_url
        else:
            full_url = logo_url
        
        img_response = session.get(full_url, timeout=10)
        
        if img_response.status_code == 200:
            content_type = img_response.headers.get('content-type', '')
            file_size = len(img_response.content)
            print(f"✅ Image accessible: {content_type}, {file_size} bytes")
            
            # Step 4: Test CMS settings integration
            print("⚙️ Testing CMS settings integration...")
            
            settings_response = session.get(f"{BACKEND_URL}/cms/settings", timeout=10)
            
            if settings_response.status_code == 200:
                settings_data = settings_response.json()
                header_logo_url = settings_data.get('header_logo_url')
                
                if header_logo_url:
                    print(f"✅ Logo URL in public settings: {header_logo_url}")
                    return True
                else:
                    print("❌ Logo URL not found in public settings")
                    return False
            else:
                print(f"❌ Failed to get public settings: {settings_response.status_code}")
                return False
        else:
            print(f"❌ Image not accessible: {img_response.status_code}")
            return False
    else:
        print(f"❌ Logo upload failed: {response.status_code} - {response.text}")
        return False

def test_listing_image_upload():
    """Test listing image upload functionality"""
    session = requests.Session()
    
    print("🔐 Authenticating for listing image test...")
    
    # Step 1: Login
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: {response.status_code}")
        return False
    
    data = response.json()
    admin_token = data["access_token"]
    print("✅ Authentication successful")
    
    # Step 2: Test listing image upload
    print("🖼️ Testing listing image upload...")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    png_image = create_test_image('PNG', (300, 300))
    files = {'file': ('test_listing.png', png_image, 'image/png')}
    
    response = session.post(f"{BACKEND_URL}/listings/upload-image", headers=headers, files=files, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        image_url = data.get('image_url')
        print(f"✅ Listing image upload successful: {image_url}")
        
        # Step 3: Test image accessibility
        print("🌐 Testing listing image accessibility...")
        
        if image_url.startswith('/uploads/'):
            full_url = BACKEND_URL.replace('/api', '') + image_url
        else:
            full_url = image_url
        
        img_response = session.get(full_url, timeout=10)
        
        if img_response.status_code == 200:
            content_type = img_response.headers.get('content-type', '')
            file_size = len(img_response.content)
            print(f"✅ Listing image accessible: {content_type}, {file_size} bytes")
            return True
        else:
            print(f"❌ Listing image not accessible: {img_response.status_code}")
            return False
    else:
        print(f"❌ Listing image upload failed: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 SIMPLE LOGO UPLOAD AND IMAGE PREVIEW TEST")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    # Test logo upload
    logo_success = test_logo_upload()
    print()
    
    # Test listing image upload
    listing_success = test_listing_image_upload()
    print()
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if logo_success and listing_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Logo upload and image preview functionality is working correctly.")
        print("🔍 The reported issue may be frontend-specific or user-specific.")
        sys.exit(0)
    elif logo_success or listing_success:
        print("⚠️ PARTIAL SUCCESS")
        print(f"Logo upload: {'✅ Working' if logo_success else '❌ Failed'}")
        print(f"Listing image upload: {'✅ Working' if listing_success else '❌ Failed'}")
        sys.exit(1)
    else:
        print("❌ ALL TESTS FAILED")
        print("🚨 Critical issues with upload functionality detected!")
        sys.exit(1)