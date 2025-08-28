import requests
import json

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

def check_mongo_data():
    session = requests.Session()
    
    # Login as admin
    login_data = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    response = session.post(f"{BACKEND_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    
    print("=== CHECKING WHAT'S ACTUALLY IN DATABASE ===")
    
    # Get current settings
    response = session.get(f"{BACKEND_URL}/admin/cms/settings")
    if response.status_code == 200:
        current_settings = response.json()
        
        # Try to update with Phase 2 fields
        test_update = {
            "font_color": "#123456",
            "link_color": "#789abc", 
            "link_hover_color": "#def012",
            "hero_image_url": "/test/hero.jpg",
            "hero_background_image_url": "/test/bg.jpg",
            "hero_background_size": "contain"
        }
        
        print("Sending update with Phase 2 fields...")
        response = session.put(f"{BACKEND_URL}/admin/cms/settings", json=test_update)
        print(f"Update response: {response.status_code} - {response.text}")
        
        # Now check what we get back
        response = session.get(f"{BACKEND_URL}/admin/cms/settings")
        if response.status_code == 200:
            updated_settings = response.json()
            print(f"\nTotal fields returned: {len(updated_settings)}")
            
            print("\nPhase 2 fields after update:")
            for field in test_update.keys():
                value = updated_settings.get(field)
                expected = test_update[field]
                status = "✅" if value == expected else "❌"
                print(f"  {status} {field}: {value} (expected: {expected})")
        
        # Let's also try creating a completely new settings document
        print("\n=== TESTING WITH FRESH SETTINGS ===")
        
        # First, let's see what a default SiteSettings looks like
        from pydantic import BaseModel, Field
        from typing import Optional
        from datetime import datetime, timezone
        import uuid
        
        # Recreate the SiteSettings model to see defaults
        class TestSiteSettings(BaseModel):
            id: str = Field(default_factory=lambda: str(uuid.uuid4()))
            site_name: str = Field(default="Cataloro")
            font_color: str = Field(default="#1f2937")
            link_color: str = Field(default="#3b82f6")
            link_hover_color: str = Field(default="#1d4ed8")
            hero_image_url: Optional[str] = Field(default=None)
            hero_background_image_url: Optional[str] = Field(default=None)
            hero_background_size: str = Field(default="cover")
        
        default_test = TestSiteSettings()
        print("Default Phase 2 fields from model:")
        print(f"  font_color: {default_test.font_color}")
        print(f"  link_color: {default_test.link_color}")
        print(f"  link_hover_color: {default_test.link_hover_color}")
        print(f"  hero_image_url: {default_test.hero_image_url}")
        print(f"  hero_background_image_url: {default_test.hero_background_image_url}")
        print(f"  hero_background_size: {default_test.hero_background_size}")

if __name__ == "__main__":
    check_mongo_data()