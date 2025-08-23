#!/usr/bin/env python3
"""
Debug upload functionality
"""

import requests
import json
import time

# Test admin login
print("Testing admin login...")
admin_credentials = {
    "email": "admin@marketplace.com",
    "password": "admin123"
}

response = requests.post("http://217.154.0.82/api/auth/login", json=admin_credentials)
print(f"Login status: {response.status_code}")

if response.status_code == 200:
    token = response.json()['access_token']
    print(f"Token obtained successfully")
    
    # Test logo upload with debugging
    print("\nTesting logo upload...")
    headers = {'Authorization': f'Bearer {token}'}
    
    # Create a simple PNG file
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02\xac\xea\x05\x1b\x00\x00\x00\x00IEND\xaeB`\x82'
    
    print(f"PNG data size: {len(png_data)} bytes")
    
    files = {'file': ('debug_logo.png', png_data, 'image/png')}
    data = {'logo_type': 'header'}
    
    # Record time before upload
    before_upload = time.time()
    
    upload_response = requests.post("http://217.154.0.82/api/admin/cms/upload-logo", 
                                   files=files, data=data, headers=headers)
    
    after_upload = time.time()
    
    print(f"Upload status: {upload_response.status_code}")
    print(f"Upload time: {after_upload - before_upload:.2f} seconds")
    print(f"Upload response: {upload_response.text}")
    
    if upload_response.status_code == 200:
        logo_url = upload_response.json().get('logo_url')
        print(f"Logo URL: {logo_url}")
        
        # Check if file was created
        if logo_url:
            filename = logo_url.split('/')[-1]
            print(f"Expected filename: {filename}")
            
            # Wait a moment for file system
            time.sleep(1)
            
            # Check if file exists
            import subprocess
            result = subprocess.run(['find', '/app/backend/uploads/', '-name', filename], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip():
                print(f"✅ File found: {result.stdout.strip()}")
                
                # Test internal access
                internal_url = f"http://localhost:8001{logo_url}"
                print(f"Testing internal access: {internal_url}")
                internal_response = requests.get(internal_url)
                print(f"Internal access status: {internal_response.status_code}")
                
            else:
                print(f"❌ File NOT found in uploads directory")
                print("Files in uploads directory:")
                result = subprocess.run(['ls', '-la', '/app/backend/uploads/'], 
                                      capture_output=True, text=True)
                print(result.stdout)
    else:
        print(f"Upload failed with status {upload_response.status_code}")
        print(f"Error response: {upload_response.text}")
else:
    print(f"Login failed: {response.text}")