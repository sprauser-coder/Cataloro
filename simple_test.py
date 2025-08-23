import requests
import json

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def simple_test():
    session = requests.Session()
    
    # Login as admin
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    print("=== SIMPLE TEST ===")
    
    # Get current settings and see what we have
    response = session.get(f"{BACKEND_URL}/admin/cms/settings")
    if response.status_code == 200:
        settings = response.json()
        print(f"Current settings has {len(settings)} fields")
        
        # Check if Phase 2 fields are now present after the fix
        phase2_fields = ["font_color", "link_color", "link_hover_color", 
                        "hero_image_url", "hero_background_image_url", "hero_background_size"]
        
        print("\nPhase 2 fields after backend fix:")
        for field in phase2_fields:
            value = settings.get(field)
            print(f"  {field}: {value}")
        
        # If they're present with defaults, try updating one
        if settings.get("font_color") is not None:
            print("\n✅ Phase 2 fields are now present! Testing update...")
            
            # Update just the font_color
            settings["font_color"] = "#test123"
            response = session.put(f"{BACKEND_URL}/admin/cms/settings", json=settings)
            print(f"Update response: {response.status_code}")
            
            # Check if it was saved
            response = session.get(f"{BACKEND_URL}/admin/cms/settings")
            if response.status_code == 200:
                updated = response.json()
                font_color = updated.get("font_color")
                print(f"After update, font_color is: {font_color}")
                
                if font_color == "#test123":
                    print("✅ SUCCESS: Phase 2 field update works!")
                else:
                    print("❌ FAILED: Phase 2 field update doesn't work")
        else:
            print("❌ Phase 2 fields are still not present after backend fix")

if __name__ == "__main__":
    simple_test()