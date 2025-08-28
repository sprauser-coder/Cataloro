#!/usr/bin/env python3
"""
Debug CMS Settings Issue
"""

import requests
import json

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def test_cms_debug():
    # Login as admin
    login_data = {'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}
    response = requests.post(f'{BACKEND_URL}/auth/login', json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    print("=== STEP 1: Get current settings ===")
    response = requests.get(f'{BACKEND_URL}/admin/cms/settings', headers=headers)
    if response.status_code == 200:
        settings = response.json()
        print(f"Current settings has {len(settings)} fields")
        print("Phase 2 fields in current settings:")
        for field in ['font_color', 'link_color', 'link_hover_color', 'hero_image_url', 'hero_background_image_url', 'hero_background_size']:
            value = settings.get(field, 'MISSING')
            print(f"  {field}: {value}")
        
        # Show all field names to debug
        print(f"\nAll field names in response: {sorted(settings.keys())}")
    else:
        print(f"Failed to get settings: {response.status_code}")
        return
    
    print("\n=== STEP 2: Update with Phase 2 fields ===")
    update_data = {
        'font_color': '#ff0000',
        'link_color': '#00ff00', 
        'link_hover_color': '#0000ff',
        'hero_image_url': '/uploads/test.jpg',
        'hero_background_image_url': '/uploads/test_bg.jpg',
        'hero_background_size': 'contain'
    }
    
    print(f"Updating with: {update_data}")
    response = requests.put(f'{BACKEND_URL}/admin/cms/settings', json=update_data, headers=headers)
    print(f"Update response: {response.status_code} - {response.text}")
    
    print("\n=== STEP 3: Get settings after update ===")
    response = requests.get(f'{BACKEND_URL}/admin/cms/settings', headers=headers)
    if response.status_code == 200:
        settings = response.json()
        print("Phase 2 fields after update:")
        for field in ['font_color', 'link_color', 'link_hover_color', 'hero_image_url', 'hero_background_image_url', 'hero_background_size']:
            expected = update_data.get(field)
            actual = settings.get(field, 'MISSING')
            status = "✅" if actual == expected else "❌"
            print(f"  {status} {field}: expected={expected}, actual={actual}")
    else:
        print(f"Failed to get settings after update: {response.status_code}")
    
    print("\n=== STEP 4: Check public API ===")
    response = requests.get(f'{BACKEND_URL}/cms/settings')
    if response.status_code == 200:
        settings = response.json()
        print("Phase 2 fields in public API:")
        for field in ['font_color', 'link_color', 'link_hover_color', 'hero_image_url', 'hero_background_image_url', 'hero_background_size']:
            expected = update_data.get(field)
            actual = settings.get(field, 'MISSING')
            status = "✅" if actual == expected else "❌"
            print(f"  {status} {field}: expected={expected}, actual={actual}")
    else:
        print(f"Failed to get public settings: {response.status_code}")

if __name__ == "__main__":
    test_cms_debug()