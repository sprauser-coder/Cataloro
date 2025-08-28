from pydantic import BaseModel, Field
from typing import Optional
import uuid

# Recreate the SiteSettings model to test defaults
class TestSiteSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    site_name: str = Field(default="Cataloro")
    font_color: str = Field(default="#1f2937")
    link_color: str = Field(default="#3b82f6")
    link_hover_color: str = Field(default="#1d4ed8")
    hero_image_url: Optional[str] = Field(default=None)
    hero_background_image_url: Optional[str] = Field(default=None)
    hero_background_size: str = Field(default="cover")

def test_defaults():
    print("=== TESTING PYDANTIC DEFAULTS ===")
    
    # Create a default instance
    default_instance = TestSiteSettings()
    print("Default instance values:")
    print(f"  font_color: {default_instance.font_color}")
    print(f"  link_color: {default_instance.link_color}")
    print(f"  link_hover_color: {default_instance.link_hover_color}")
    print(f"  hero_background_size: {default_instance.hero_background_size}")
    
    # Test creating from partial data (simulating database)
    partial_data = {
        "id": "test-id",
        "site_name": "Test Site"
        # Missing Phase 2 fields
    }
    
    print(f"\nCreating from partial data: {partial_data}")
    try:
        partial_instance = TestSiteSettings(**partial_data)
        print("Partial instance values:")
        print(f"  font_color: {partial_instance.font_color}")
        print(f"  link_color: {partial_instance.link_color}")
        print(f"  link_hover_color: {partial_instance.link_hover_color}")
        print(f"  hero_background_size: {partial_instance.hero_background_size}")
    except Exception as e:
        print(f"Error creating partial instance: {e}")
    
    # Test merging approach
    print(f"\n=== TESTING MERGE APPROACH ===")
    default_dict = default_instance.dict()
    print(f"Default dict has {len(default_dict)} fields")
    
    merged = default_dict.copy()
    merged.update(partial_data)
    print(f"Merged dict has {len(merged)} fields")
    
    try:
        merged_instance = TestSiteSettings(**merged)
        print("Merged instance values:")
        print(f"  font_color: {merged_instance.font_color}")
        print(f"  link_color: {merged_instance.link_color}")
        print(f"  link_hover_color: {merged_instance.link_hover_color}")
        print(f"  hero_background_size: {merged_instance.hero_background_size}")
    except Exception as e:
        print(f"Error creating merged instance: {e}")

if __name__ == "__main__":
    test_defaults()