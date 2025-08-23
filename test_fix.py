import requests
import json

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def test_fix():
    session = requests.Session()
    
    # Login as admin
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    print("=== TESTING POTENTIAL FIX ===")
    
    # Get current settings
    response = session.get(f"{BACKEND_URL}/admin/cms/settings")
    if response.status_code == 200:
        current_settings = response.json()
        
        # Add the Phase 2 fields with their default values to the existing settings
        phase2_defaults = {
            "font_color": "#1f2937",
            "link_color": "#3b82f6", 
            "link_hover_color": "#1d4ed8",
            "hero_image_url": None,
            "hero_background_image_url": None,
            "hero_background_size": "cover"
        }
        
        # Merge current settings with Phase 2 defaults
        updated_settings = current_settings.copy()
        for field, default_value in phase2_defaults.items():
            if field not in updated_settings or updated_settings[field] is None:
                updated_settings[field] = default_value
        
        print("Adding Phase 2 fields with defaults to existing settings...")
        response = session.put(f"{BACKEND_URL}/admin/cms/settings", json=updated_settings)
        print(f"Update response: {response.status_code} - {response.text}")
        
        # Check if they're now present
        response = session.get(f"{BACKEND_URL}/admin/cms/settings")
        if response.status_code == 200:
            final_settings = response.json()
            
            print("\nPhase 2 fields after adding defaults:")
            for field, expected in phase2_defaults.items():
                actual = final_settings.get(field)
                status = "✅" if actual == expected else "❌"
                print(f"  {status} {field}: {actual} (expected: {expected})")
                
            # Now test if we can update them with custom values
            print("\n=== TESTING CUSTOM VALUES ===")
            custom_values = {
                "font_color": "#ff0000",
                "link_color": "#00ff00",
                "link_hover_color": "#0000ff"
            }
            
            test_settings = final_settings.copy()
            test_settings.update(custom_values)
            
            response = session.put(f"{BACKEND_URL}/admin/cms/settings", json=test_settings)
            print(f"Custom update response: {response.status_code}")
            
            # Verify custom values
            response = session.get(f"{BACKEND_URL}/admin/cms/settings")
            if response.status_code == 200:
                custom_result = response.json()
                print("\nCustom values test:")
                for field, expected in custom_values.items():
                    actual = custom_result.get(field)
                    status = "✅" if actual == expected else "❌"
                    print(f"  {status} {field}: {actual} (expected: {expected})")

if __name__ == "__main__":
    test_fix()