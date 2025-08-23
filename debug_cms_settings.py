import requests
import json

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def debug_cms_settings():
    session = requests.Session()
    
    # Login as admin
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    print("=== DEBUGGING CMS SETTINGS ===")
    
    # Get current settings
    response = session.get(f"{BACKEND_URL}/admin/cms/settings")
    if response.status_code == 200:
        current_settings = response.json()
        print("Current settings keys:", list(current_settings.keys()))
        
        # Check if Phase 2 fields exist
        phase2_fields = ["font_color", "link_color", "link_hover_color", 
                        "hero_image_url", "hero_background_image_url", "hero_background_size"]
        
        print("\nPhase 2 fields in current settings:")
        for field in phase2_fields:
            value = current_settings.get(field)
            print(f"  {field}: {value}")
        
        # Try to update with just one Phase 2 field
        test_update = current_settings.copy()
        test_update["font_color"] = "#ff0000"  # Red color for testing
        
        print(f"\nTrying to update font_color to #ff0000...")
        response = session.put(f"{BACKEND_URL}/admin/cms/settings", json=test_update)
        print(f"Update response status: {response.status_code}")
        print(f"Update response: {response.text}")
        
        # Check if it was saved
        response = session.get(f"{BACKEND_URL}/admin/cms/settings")
        if response.status_code == 200:
            updated_settings = response.json()
            font_color = updated_settings.get("font_color")
            print(f"After update, font_color is: {font_color}")
            
            if font_color == "#ff0000":
                print("✅ Phase 2 field was saved successfully!")
            else:
                print("❌ Phase 2 field was NOT saved")
                
                # Let's see what fields are actually being saved
                print("\nComparing before and after:")
                for key in test_update:
                    before = current_settings.get(key)
                    after = updated_settings.get(key)
                    if before != after:
                        print(f"  {key}: {before} -> {after}")
        else:
            print(f"Failed to get updated settings: {response.status_code}")
    else:
        print(f"Failed to get current settings: {response.status_code}")

if __name__ == "__main__":
    debug_cms_settings()