import requests
import json

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def check_raw_db():
    session = requests.Session()
    
    # Login as admin
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    print("=== CHECKING RAW DATABASE CONTENT ===")
    
    # Get current settings
    response = session.get(f"{BACKEND_URL}/admin/cms/settings")
    if response.status_code == 200:
        settings = response.json()
        
        # Check if Phase 2 fields exist and what their values are
        phase2_fields = ["font_color", "link_color", "link_hover_color", 
                        "hero_image_url", "hero_background_image_url", "hero_background_size"]
        
        print("Phase 2 fields in database:")
        for field in phase2_fields:
            if field in settings:
                value = settings[field]
                print(f"  {field}: {value} (type: {type(value).__name__})")
            else:
                print(f"  {field}: NOT PRESENT")
        
        # Let's try to remove these fields entirely and see if defaults kick in
        print(f"\n=== TESTING FIELD REMOVAL ===")
        
        # Create a copy without the Phase 2 fields
        clean_settings = {k: v for k, v in settings.items() if k not in phase2_fields}
        print(f"Removed {len(settings) - len(clean_settings)} Phase 2 fields")
        
        # Update with clean settings
        response = session.put(f"{BACKEND_URL}/admin/cms/settings", json=clean_settings)
        print(f"Clean update response: {response.status_code}")
        
        # Check what we get back
        response = session.get(f"{BACKEND_URL}/admin/cms/settings")
        if response.status_code == 200:
            clean_result = response.json()
            print("\nAfter removing Phase 2 fields:")
            for field in phase2_fields:
                if field in clean_result:
                    value = clean_result[field]
                    print(f"  {field}: {value} (type: {type(value).__name__})")
                else:
                    print(f"  {field}: NOT PRESENT")

if __name__ == "__main__":
    check_raw_db()