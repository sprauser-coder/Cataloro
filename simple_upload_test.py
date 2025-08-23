#!/usr/bin/env python3
"""
Simple upload test to verify file upload functionality
"""

import requests
import json

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
    print(f"Token obtained: {token[:20]}...")
    
    # Test logo upload
    print("\nTesting logo upload...")
    headers = {'Authorization': f'Bearer {token}'}
    
    # Create a simple PNG file
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02\xac\xea\x05\x1b\x00\x00\x00\x00IEND\xaeB`\x82'
    
    files = {'file': ('test_logo.png', png_data, 'image/png')}
    data = {'logo_type': 'header'}
    
    upload_response = requests.post("http://217.154.0.82/api/admin/cms/upload-logo", 
                                   files=files, data=data, headers=headers)
    
    print(f"Upload status: {upload_response.status_code}")
    print(f"Upload response: {upload_response.text}")
    
    if upload_response.status_code == 200:
        logo_url = upload_response.json().get('logo_url')
        print(f"Logo URL: {logo_url}")
        
        # Test file accessibility via internal backend
        if logo_url:
            internal_url = f"http://localhost:8001{logo_url}"
            external_url = f"http://217.154.0.82{logo_url}"
            
            print(f"\nTesting internal access: {internal_url}")
            internal_response = requests.get(internal_url)
            print(f"Internal access status: {internal_response.status_code}")
            
            print(f"\nTesting external access: {external_url}")
            external_response = requests.get(external_url)
            print(f"External access status: {external_response.status_code}")
else:
    print(f"Login failed: {response.text}")