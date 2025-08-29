import requests
import json
from config_loader import get_config, get_backend_url, get_admin_credentials, get_paths, get_database_url

# Configuration
BACKEND_URL = "get_backend_url()/api"

def check_public_api():
    print("=== CHECKING PUBLIC CMS API ===")
    
    # Check public settings endpoint
    response = requests.get(f"{BACKEND_URL}/cms/settings")
    
    if response.status_code == 200:
        settings = response.json()
        print(f"Public API returned {len(settings)} fields")
        
        # Check Phase 2 fields
        phase2_fields = ["font_color", "link_color", "link_hover_color", 
                        "hero_image_url", "hero_background_image_url", "hero_background_size"]
        
        print("\nPhase 2 fields in public API:")
        for field in phase2_fields:
            if field in settings:
                value = settings[field]
                print(f"  {field}: {value} (type: {type(value).__name__})")
            else:
                print(f"  {field}: NOT PRESENT")
        
        # Check if any fields are missing compared to admin API
        print(f"\nAll fields in public API:")
        for key in sorted(settings.keys()):
            print(f"  {key}")
    else:
        print(f"Public API failed: {response.status_code}")

if __name__ == "__main__":
    check_public_api()