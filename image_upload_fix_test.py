#!/usr/bin/env python3
"""
IMAGE UPLOAD FIX TEST - Testing the corrected endpoint URL
"""

import asyncio
import aiohttp
import time
import base64
from datetime import datetime

# Test Configuration
BACKEND_URL = "https://menu-settings-debug.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@cataloro.com"

class ImageUploadFixTester:
    def __init__(self):
        self.session = None
        self.admin_token = None
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def authenticate_admin(self) -> bool:
        """Authenticate as admin user"""
        print("🔐 Authenticating as admin...")
        
        login_data = {
            "email": ADMIN_EMAIL,
            "password": "admin_password"
        }
        
        async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                self.admin_token = data.get("token", "")
                print(f"  ✅ Admin authentication successful")
                return True
            else:
                print(f"  ❌ Admin authentication failed: {response.status}")
                return False
    
    def create_test_image(self) -> bytes:
        """Create a small test image (PNG format)"""
        # This is a 1x1 red PNG (minimal valid PNG)
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        )
        return png_data
    
    async def test_correct_endpoint(self) -> dict:
        """Test the correct endpoint URL"""
        print("📤 Testing CORRECT endpoint: /api/admin/upload-image")
        
        if not self.admin_token:
            return {"success": False, "error": "No admin token"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        test_image_data = self.create_test_image()
        
        # Create multipart form data
        form_data = aiohttp.FormData()
        form_data.add_field('image', 
                           test_image_data, 
                           filename='test_ad_image.png', 
                           content_type='image/png')
        form_data.add_field('section', 'ads')
        form_data.add_field('field', 'ad_image')
        
        try:
            async with self.session.post(f"{BACKEND_URL}/admin/upload-image", 
                                       headers=headers, 
                                       data=form_data) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print(f"  ✅ Upload successful!")
                    print(f"  🔗 Image URL: {result.get('url', 'No URL returned')}")
                    return {"success": True, "result": result}
                else:
                    error_text = await response.text()
                    print(f"  ❌ Upload failed: {response.status}")
                    print(f"  💬 Error: {error_text}")
                    return {"success": False, "status": response.status, "error": error_text}
                    
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_wrong_endpoint(self) -> dict:
        """Test the wrong endpoint URL (what frontend was calling)"""
        print("📤 Testing WRONG endpoint: /api/api/admin/upload-image (double /api)")
        
        if not self.admin_token:
            return {"success": False, "error": "No admin token"}
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        test_image_data = self.create_test_image()
        
        # Create multipart form data
        form_data = aiohttp.FormData()
        form_data.add_field('image', 
                           test_image_data, 
                           filename='test_ad_image.png', 
                           content_type='image/png')
        form_data.add_field('section', 'ads')
        form_data.add_field('field', 'ad_image')
        
        try:
            # Test the wrong URL with double /api
            wrong_url = f"{BACKEND_URL}/api/admin/upload-image"  # This creates double /api
            async with self.session.post(wrong_url, 
                                       headers=headers, 
                                       data=form_data) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print(f"  ❓ Unexpected success on wrong endpoint")
                    return {"success": True, "result": result}
                else:
                    error_text = await response.text()
                    print(f"  ✅ Expected failure: {response.status}")
                    print(f"  💬 Error: {error_text}")
                    return {"success": False, "status": response.status, "error": error_text}
                    
        except Exception as e:
            print(f"  ✅ Expected exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def run_fix_test(self):
        """Run the image upload fix test"""
        print("🔧 TESTING IMAGE UPLOAD FIX")
        print("=" * 60)
        print("ISSUE: Frontend calling wrong URL due to double /api in config")
        print("TESTING: Correct vs incorrect endpoint URLs")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Authenticate first
            auth_success = await self.authenticate_admin()
            if not auth_success:
                print("❌ Cannot proceed without authentication")
                return
            
            print()
            
            # Test correct endpoint
            correct_result = await self.test_correct_endpoint()
            
            print()
            
            # Test wrong endpoint (what frontend was calling)
            wrong_result = await self.test_wrong_endpoint()
            
            print()
            print("=" * 60)
            print("🔍 TEST RESULTS SUMMARY")
            print("=" * 60)
            
            print(f"✅ Correct endpoint (/api/admin/upload-image): {'SUCCESS' if correct_result['success'] else 'FAILED'}")
            print(f"❌ Wrong endpoint (/api/api/admin/upload-image): {'FAILED (Expected)' if not wrong_result['success'] else 'UNEXPECTED SUCCESS'}")
            
            if correct_result['success']:
                print("\n💡 SOLUTION CONFIRMED:")
                print("   - The backend endpoint /api/admin/upload-image works correctly")
                print("   - Frontend config needs to be fixed to avoid double /api")
                print("   - Remove the extra /api from ENV_CONFIG.API_BASE_URL")
            else:
                print("\n❌ ISSUE PERSISTS:")
                print("   - Even the correct endpoint is failing")
                print("   - Need to investigate backend authentication or permissions")
            
            print("\n🔧 RECOMMENDED FIX:")
            print("   Change frontend config from:")
            print("   API_BASE_URL: `${CURRENT_ENV.BACKEND_URL}/api`")
            print("   To:")
            print("   API_BASE_URL: CURRENT_ENV.BACKEND_URL")
            
        finally:
            await self.cleanup()

async def main():
    tester = ImageUploadFixTester()
    await tester.run_fix_test()

if __name__ == "__main__":
    asyncio.run(main())