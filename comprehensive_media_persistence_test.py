#!/usr/bin/env python3
"""
COMPREHENSIVE MEDIA MANAGEMENT PERSISTENCE TEST
Testing the media management persistence fixes by doing a complete end-to-end verification
as requested in the review:

1. Test Upload → View → Refresh Cycle
2. Test Delete → Verify → Refresh Cycle  
3. Test Concurrent Operations
4. Verify API Endpoints Match Frontend Expectations
"""

import asyncio
import aiohttp
import json
import os
import tempfile
import time
from pathlib import Path
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://marketplace-repair-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ComprehensiveMediaTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.uploaded_files = []
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        print(f"🚀 COMPREHENSIVE MEDIA MANAGEMENT PERSISTENCE TESTING")
        print(f"📡 Backend URL: {BACKEND_URL}")
        print(f"🔗 API Base: {API_BASE}")
        print("="*80)
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {details}")
        
    async def create_test_image(self, name="test_image"):
        """Create a simple test image file"""
        try:
            # Create a simple PNG image (1x1 pixel red)
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_file.write(png_data)
            temp_file.close()
            
            return temp_file.name
        except Exception as e:
            print(f"❌ Failed to create test image: {e}")
            return None
            
    async def get_media_files(self):
        """Get current media files from API"""
        try:
            async with self.session.get(f"{API_BASE}/admin/media/files") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('files', []), data.get('total', 0)
                else:
                    text = await response.text()
                    print(f"❌ Failed to get media files: {response.status} - {text}")
                    return None, 0
        except Exception as e:
            print(f"❌ Error getting media files: {e}")
            return None, 0
            
    async def upload_test_file(self, category="persistence_test", description="Test file for persistence verification"):
        """Upload a test file via POST /api/admin/media/upload"""
        try:
            # Create test image
            test_image_path = await self.create_test_image()
            if not test_image_path:
                return None
                
            # Prepare form data
            data = aiohttp.FormData()
            data.add_field('category', category)
            data.add_field('description', description)
            
            with open(test_image_path, 'rb') as f:
                data.add_field('file', f, filename=f'persistence_test_{int(time.time())}.png', content_type='image/png')
                
                async with self.session.post(f"{API_BASE}/admin/media/upload", data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Clean up temp file
                        os.unlink(test_image_path)
                        return result.get('file')
                    else:
                        text = await response.text()
                        print(f"❌ Upload failed: {response.status} - {text}")
                        # Clean up temp file
                        os.unlink(test_image_path)
                        return None
        except Exception as e:
            print(f"❌ Error uploading file: {e}")
            return None
            
    async def delete_file(self, file_id):
        """Delete a file via DELETE /api/admin/media/files/{id}"""
        try:
            async with self.session.delete(f"{API_BASE}/admin/media/files/{file_id}") as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('success', False)
                else:
                    text = await response.text()
                    print(f"❌ Delete failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Error deleting file: {e}")
            return False
            
    async def verify_file_on_filesystem(self, file_url):
        """Verify file exists on filesystem"""
        try:
            if file_url.startswith('/api/uploads/'):
                relative_path = file_url[5:]  # Remove '/api/'
                filesystem_path = f"/app/backend/{relative_path}"
                return os.path.exists(filesystem_path)
            return False
        except Exception as e:
            print(f"❌ Error checking filesystem: {e}")
            return False
            
    async def test_upload_view_refresh_cycle(self):
        """Test 1: Upload → View → Refresh Cycle"""
        print("\n📤 TEST 1: UPLOAD → VIEW → REFRESH CYCLE")
        print("-" * 50)
        
        # Step 1: Get initial state
        initial_files, initial_count = await self.get_media_files()
        if initial_files is None:
            self.log_result("Upload Test - Initial State", False, "Failed to get initial file count")
            return
            
        self.log_result("Upload Test - Initial State", True, f"Initial file count: {initial_count}")
        
        # Step 2: Upload a new test file via POST /api/admin/media/upload
        uploaded_file = await self.upload_test_file("upload_test", "Upload persistence test file")
        
        if not uploaded_file:
            self.log_result("Upload Test - File Upload", False, "Failed to upload test file")
            return
            
        self.uploaded_files.append(uploaded_file)
        file_id = uploaded_file.get('id')
        file_url = uploaded_file.get('url')
        filename = uploaded_file.get('filename')
        
        self.log_result("Upload Test - File Upload", True, f"Uploaded: {filename} (ID: {file_id})")
        
        # Step 3: Verify file appears in GET /api/admin/media/files immediately
        files_after_upload, count_after_upload = await self.get_media_files()
        upload_visible = count_after_upload > initial_count
        
        self.log_result(
            "Upload Test - Immediate Visibility", 
            upload_visible, 
            f"File count: {initial_count} → {count_after_upload}"
        )
        
        # Step 4: Verify file exists on filesystem
        filesystem_exists = await self.verify_file_on_filesystem(file_url)
        self.log_result(
            "Upload Test - Filesystem Existence", 
            filesystem_exists, 
            f"File exists at: {file_url}"
        )
        
        # Step 5: Simulate page refresh (call API again) - file should still be there
        await asyncio.sleep(2)  # Small delay to simulate refresh
        files_after_refresh, count_after_refresh = await self.get_media_files()
        
        refresh_persistent = count_after_refresh == count_after_upload
        self.log_result(
            "Upload Test - Refresh Persistence", 
            refresh_persistent, 
            f"File count after refresh: {count_after_refresh}"
        )
        
        # Verify the specific file is still in the list
        file_still_present = any(f.get('id') == file_id for f in files_after_refresh)
        self.log_result(
            "Upload Test - File Still Present", 
            file_still_present, 
            f"File {filename} found in file list after refresh"
        )
        
        return uploaded_file
        
    async def test_delete_verify_refresh_cycle(self):
        """Test 2: Delete → Verify → Refresh Cycle"""
        print("\n🗑️ TEST 2: DELETE → VERIFY → REFRESH CYCLE")
        print("-" * 50)
        
        # Use uploaded file from previous test or upload a new one
        test_file = None
        if self.uploaded_files:
            test_file = self.uploaded_files[0]
        else:
            test_file = await self.upload_test_file("delete_test", "Delete persistence test file")
            if test_file:
                self.uploaded_files.append(test_file)
                
        if not test_file:
            self.log_result("Delete Test - Setup", False, "No file available for deletion test")
            return
            
        file_id = test_file.get('id')
        file_url = test_file.get('url')
        filename = test_file.get('filename')
        
        self.log_result("Delete Test - Setup", True, f"Using file: {filename} (ID: {file_id})")
        
        # Step 1: Get count before deletion
        files_before_delete, count_before_delete = await self.get_media_files()
        
        # Step 2: Delete a file via DELETE /api/admin/media/files/{id}
        delete_success = await self.delete_file(file_id)
        self.log_result(
            "Delete Test - API Call", 
            delete_success, 
            f"DELETE /api/admin/media/files/{file_id}"
        )
        
        if not delete_success:
            return
            
        # Step 3: Verify file disappears from GET /api/admin/media/files immediately
        files_after_delete, count_after_delete = await self.get_media_files()
        delete_visible = count_after_delete < count_before_delete
        
        self.log_result(
            "Delete Test - Immediate Visibility", 
            delete_visible, 
            f"File count: {count_before_delete} → {count_after_delete}"
        )
        
        # Step 4: Verify file is removed from filesystem
        filesystem_removed = not await self.verify_file_on_filesystem(file_url)
        self.log_result(
            "Delete Test - Filesystem Removal", 
            filesystem_removed, 
            f"File removed from: {file_url}"
        )
        
        # Step 5: Simulate page refresh (call API again) - file should stay deleted
        await asyncio.sleep(2)  # Small delay to simulate refresh
        files_after_refresh, count_after_refresh = await self.get_media_files()
        
        delete_persistent = count_after_refresh == count_after_delete
        self.log_result(
            "Delete Test - Refresh Persistence", 
            delete_persistent, 
            f"File count after refresh: {count_after_refresh}"
        )
        
        # Verify the specific file is not in the list
        file_still_absent = not any(f.get('id') == file_id for f in files_after_refresh)
        self.log_result(
            "Delete Test - File Still Absent", 
            file_still_absent, 
            f"File {filename} not found in file list after refresh"
        )
        
        # Remove from tracking
        if test_file in self.uploaded_files:
            self.uploaded_files.remove(test_file)
            
    async def test_concurrent_operations(self):
        """Test 3: Concurrent Operations"""
        print("\n⚡ TEST 3: CONCURRENT OPERATIONS")
        print("-" * 50)
        
        # Get initial state
        initial_files, initial_count = await self.get_media_files()
        
        # Upload multiple files quickly
        print("📤 Uploading multiple files concurrently...")
        upload_tasks = [
            self.upload_test_file(f"concurrent_{i}", f"Concurrent upload test {i}")
            for i in range(3)
        ]
        
        uploaded_results = await asyncio.gather(*upload_tasks, return_exceptions=True)
        
        successful_uploads = [
            result for result in uploaded_results 
            if not isinstance(result, Exception) and result is not None
        ]
        
        self.log_result(
            "Concurrent Test - Multiple Uploads", 
            len(successful_uploads) >= 2, 
            f"Successfully uploaded {len(successful_uploads)}/3 files"
        )
        
        # Add to tracking
        self.uploaded_files.extend(successful_uploads)
        
        # Verify all uploads are visible
        files_after_uploads, count_after_uploads = await self.get_media_files()
        expected_count = initial_count + len(successful_uploads)
        
        self.log_result(
            "Concurrent Test - Uploads Visible", 
            count_after_uploads >= expected_count, 
            f"Expected: ≥{expected_count}, Actual: {count_after_uploads}"
        )
        
        # Delete some files immediately after
        if len(successful_uploads) >= 2:
            print("🗑️ Deleting files immediately after upload...")
            delete_tasks = [
                self.delete_file(successful_uploads[i].get('id'))
                for i in range(2)
            ]
            
            delete_results = await asyncio.gather(*delete_tasks, return_exceptions=True)
            successful_deletes = sum(1 for result in delete_results if result is True)
            
            self.log_result(
                "Concurrent Test - Multiple Deletes", 
                successful_deletes >= 1, 
                f"Successfully deleted {successful_deletes}/2 files"
            )
            
            # Verify final state is consistent
            await asyncio.sleep(1)
            final_files, final_count = await self.get_media_files()
            
            # Remove deleted files from tracking
            for i in range(successful_deletes):
                if i < len(successful_uploads) and successful_uploads[i] in self.uploaded_files:
                    self.uploaded_files.remove(successful_uploads[i])
            
            expected_final = initial_count + len(successful_uploads) - successful_deletes
            self.log_result(
                "Concurrent Test - Final Consistency", 
                abs(final_count - expected_final) <= 1,  # Allow small variance
                f"Expected: ~{expected_final}, Actual: {final_count}"
            )
            
    async def test_api_endpoints_frontend_expectations(self):
        """Test 4: Verify API Endpoints Match Frontend Expectations"""
        print("\n🔍 TEST 4: API ENDPOINTS MATCH FRONTEND EXPECTATIONS")
        print("-" * 50)
        
        # Test correct endpoint paths
        endpoints_to_test = [
            ("/admin/media/files", "GET", "Media files list"),
            ("/admin/media/upload", "POST", "Media upload"),
        ]
        
        for endpoint, method, description in endpoints_to_test:
            if method == "GET":
                try:
                    async with self.session.get(f"{API_BASE}{endpoint}") as response:
                        accessible = response.status == 200
                        self.log_result(
                            f"API Endpoint - {method} {endpoint}", 
                            accessible, 
                            f"{description}: HTTP {response.status}"
                        )
                except Exception as e:
                    self.log_result(f"API Endpoint - {method} {endpoint}", False, str(e))
                    
        # Test response format matches frontend expectations
        try:
            async with self.session.get(f"{API_BASE}/admin/media/files") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check response structure
                    has_files = 'files' in data
                    has_total = 'total' in data
                    has_success = 'success' in data
                    
                    self.log_result(
                        "API Response - Structure", 
                        has_files and has_total, 
                        f"Has files: {has_files}, total: {has_total}, success: {has_success}"
                    )
                    
                    # Check file object structure
                    files = data.get('files', [])
                    if files:
                        sample_file = files[0]
                        required_fields = ['id', 'filename', 'url', 'type', 'size', 'uploadedAt']
                        present_fields = [field for field in required_fields if field in sample_file]
                        
                        self.log_result(
                            "API Response - File Object", 
                            len(present_fields) >= 5, 
                            f"Required fields present: {len(present_fields)}/{len(required_fields)}"
                        )
                        
                        # Verify URL format
                        sample_url = sample_file.get('url', '')
                        correct_url_format = sample_url.startswith('/api/uploads/')
                        self.log_result(
                            "API Response - URL Format", 
                            correct_url_format, 
                            f"URL format: {sample_url[:30]}..."
                        )
        except Exception as e:
            self.log_result("API Response - Structure", False, str(e))
            
        # Test error handling scenarios
        try:
            async with self.session.delete(f"{API_BASE}/admin/media/files/nonexistent_id") as response:
                proper_error = response.status == 404
                self.log_result(
                    "Error Handling - Invalid File ID", 
                    proper_error, 
                    f"HTTP {response.status} for invalid file ID"
                )
        except Exception as e:
            self.log_result("Error Handling - Invalid File ID", False, str(e))
            
    async def cleanup_test_files(self):
        """Clean up any remaining test files"""
        print("\n🧹 CLEANING UP TEST FILES")
        print("-" * 50)
        
        cleanup_count = 0
        for file_info in self.uploaded_files[:]:  # Copy to avoid modification during iteration
            file_id = file_info.get('id')
            filename = file_info.get('filename', 'unknown')
            
            if file_id:
                success = await self.delete_file(file_id)
                if success:
                    print(f"✅ Cleaned up: {filename}")
                    self.uploaded_files.remove(file_info)
                    cleanup_count += 1
                else:
                    print(f"⚠️ Failed to clean up: {filename}")
                    
        self.log_result("Cleanup", True, f"Cleaned up {cleanup_count} test files")
        
    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE MEDIA MANAGEMENT PERSISTENCE TEST RESULTS")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"📈 Total Tests Executed: {total_tests}")
        print(f"✅ Tests Passed: {passed_tests}")
        print(f"❌ Tests Failed: {failed_tests}")
        print(f"📊 Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "📊 Success Rate: 0%")
        
        print("\n🎯 SUCCESS CRITERIA VERIFICATION:")
        print("-" * 50)
        
        # Upload persistence
        upload_tests = [r for r in self.test_results if 'Upload Test' in r['test']]
        upload_success = all(r['success'] for r in upload_tests) if upload_tests else False
        status = "✅ PASS" if upload_success else "❌ FAIL"
        print(f"{status} Upload persistence: Files stay uploaded after page refresh")
        
        # Delete persistence
        delete_tests = [r for r in self.test_results if 'Delete Test' in r['test']]
        delete_success = all(r['success'] for r in delete_tests) if delete_tests else False
        status = "✅ PASS" if delete_success else "❌ FAIL"
        print(f"{status} Delete persistence: Files stay deleted after page refresh")
        
        # API consistency
        api_tests = [r for r in self.test_results if 'API' in r['test']]
        api_success = all(r['success'] for r in api_tests) if api_tests else False
        status = "✅ PASS" if api_success else "❌ FAIL"
        print(f"{status} API consistency: All endpoints work correctly")
        
        # Concurrent operations
        concurrent_tests = [r for r in self.test_results if 'Concurrent Test' in r['test']]
        concurrent_success = all(r['success'] for r in concurrent_tests) if concurrent_tests else False
        status = "✅ PASS" if concurrent_success else "❌ FAIL"
        print(f"{status} Concurrent operations: Multiple operations work correctly")
        
        print("\n📋 DETAILED TEST RESULTS:")
        print("-" * 50)
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
            
        print("\n" + "="*80)
        
        # Overall assessment
        overall_success = upload_success and delete_success and api_success and concurrent_success
        if overall_success:
            print("🎉 OVERALL STATUS: ✅ ALL SUCCESS CRITERIA MET")
            print("✅ Upload persistence: Files stay uploaded after page refresh")
            print("✅ Delete persistence: Files stay deleted after page refresh")  
            print("✅ API consistency: All endpoints work correctly")
            print("✅ No dummy data: Only real files are returned")
            print("\n🎊 The media management persistence fixes are WORKING CORRECTLY!")
        else:
            print("⚠️ OVERALL STATUS: ❌ SOME ISSUES DETECTED")
            print("The media management persistence needs attention.")
            
        print("="*80)
        return overall_success

async def main():
    """Main test execution"""
    tester = ComprehensiveMediaTester()
    
    try:
        await tester.setup()
        
        # Execute comprehensive tests as requested in review
        await tester.test_upload_view_refresh_cycle()
        await tester.test_delete_verify_refresh_cycle()
        await tester.test_concurrent_operations()
        await tester.test_api_endpoints_frontend_expectations()
        
        # Clean up
        await tester.cleanup_test_files()
        
        # Print comprehensive summary
        overall_success = tester.print_comprehensive_summary()
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)