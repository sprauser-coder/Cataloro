import requests
import json

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def reset_settings():
    session = requests.Session()
    
    # Login as admin
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    print("=== RESETTING SETTINGS WITH PHASE 2 FIELDS ===")
    
    # Create a complete settings object with all Phase 2 fields
    complete_settings = {
        "site_name": "Cataloro",
        "site_tagline": "Your trusted marketplace for amazing deals",
        "hero_title": "Discover Amazing Deals",
        "hero_subtitle": "Buy and sell with confidence on Cataloro - your trusted marketplace for amazing deals",
        "header_logo_url": None,
        "header_logo_alt": "Cataloro Logo",
        "primary_color": "#6366f1",
        "secondary_color": "#8b5cf6",
        "accent_color": "#ef4444",
        "background_color": "#f8fafc",
        "hero_background_type": "gradient",
        "hero_background_color": "#6366f1",
        "hero_background_gradient_start": "#667eea",
        "hero_background_gradient_end": "#764ba2",
        "hero_text_color": "#ffffff",
        "hero_subtitle_color": "#f1f5f9",
        "hero_height": "600px",
        "global_font_family": "Inter",
        "h1_size": "3rem",
        "h2_size": "2.25rem",
        "h3_size": "1.875rem",
        "h4_size": "1.5rem",
        "h5_size": "1.25rem",
        "h1_color": "#1f2937",
        "h2_color": "#374151",
        "h3_color": "#4b5563",
        "h4_color": "#6b7280",
        "h5_color": "#9ca3af",
        # Phase 2 fields with explicit values
        "font_color": "#1f2937",
        "link_color": "#3b82f6",
        "link_hover_color": "#1d4ed8",
        "hero_image_url": None,
        "hero_background_image_url": None,
        "hero_background_size": "cover",
        # Feature toggles
        "show_hero_section": True,
        "show_categories": True,
        "show_auctions": True,
        "show_buy_now": True,
        "allow_user_registration": True,
        "enable_reviews": True,
        "enable_cart": True,
        "max_images_per_listing": 5,
        "auto_add_pages_to_menu": True
    }
    
    print(f"Sending complete settings with {len(complete_settings)} fields...")
    response = session.put(f"{BACKEND_URL}/admin/cms/settings", json=complete_settings)
    print(f"Update response: {response.status_code} - {response.text}")
    
    if response.status_code == 200:
        # Check what we get back
        response = session.get(f"{BACKEND_URL}/admin/cms/settings")
        if response.status_code == 200:
            result_settings = response.json()
            print(f"\nResult has {len(result_settings)} fields")
            
            # Check Phase 2 fields specifically
            phase2_fields = ["font_color", "link_color", "link_hover_color", 
                            "hero_image_url", "hero_background_image_url", "hero_background_size"]
            
            print("\nPhase 2 fields after reset:")
            all_present = True
            for field in phase2_fields:
                expected = complete_settings[field]
                actual = result_settings.get(field)
                status = "✅" if actual == expected else "❌"
                print(f"  {status} {field}: {actual} (expected: {expected})")
                if actual != expected:
                    all_present = False
            
            if all_present:
                print("\n🎉 SUCCESS: All Phase 2 fields are now working!")
                
                # Test updating one field
                print("\n=== TESTING FIELD UPDATE ===")
                test_settings = result_settings.copy()
                test_settings["font_color"] = "#ff0000"  # Red
                
                response = session.put(f"{BACKEND_URL}/admin/cms/settings", json=test_settings)
                print(f"Test update response: {response.status_code}")
                
                # Verify the update
                response = session.get(f"{BACKEND_URL}/admin/cms/settings")
                if response.status_code == 200:
                    updated_result = response.json()
                    font_color = updated_result.get("font_color")
                    if font_color == "#ff0000":
                        print("✅ Field update test PASSED!")
                    else:
                        print(f"❌ Field update test FAILED: got {font_color}")
            else:
                print("\n❌ Some Phase 2 fields are still not working correctly")

if __name__ == "__main__":
    reset_settings()