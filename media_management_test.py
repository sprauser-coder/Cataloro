#!/usr/bin/env python3
"""
Cataloro Marketplace - Media Management API Testing
Tests the media management API endpoints to identify persistence issues:

SPECIFIC TESTS:
1. DELETE /api/admin/media/files/{file_id} endpoint
2. POST /api/admin/media/upload endpoint  
3. File system verification (count files before/after operations)
4. API response analysis

EXAMPLE TEST FLOW:
1. Get initial file count via API
2. Attempt to delete a specific file
3. Verify file is removed from filesystem
4. Re-fetch file list to confirm removal
5. Upload a new test file
6. Verify file appears in filesystem and API response
"""

import asyncio
import aiohttp
import json
import sys
import time
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Backend URL from environment
BACKEND_URL = "https://marketplace-central.preview.emergentagent.com/api"

class MediaManagementTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        self.uploads_dir = "/app/backend/uploads"
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(ssl=False)
        )
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, files: Dict = None) -> Dict:
        """Make HTTP request to backend"""
        url = f"{BACKEND_URL}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "success": response.status < 400
                    }
            elif method.upper() == "POST":
                if files:
                    # Handle file upload
                    form_data = aiohttp.FormData()
                    for key, value in files.items():
                        if isinstance(value, tuple):
                            filename, file_content, content_type = value
                            form_data.add_field(key, file_content, filename=filename, content_type=content_type)
                        else:
                            form_data.add_field(key, value)
                    
                    # Add other form fields
                    if data:
                        for key, value in data.items():
                            form_data.add_field(key, str(value))
                    
                    async with self.session.post(url, data=form_data, params=params) as response:
                        return {
                            "status": response.status,
                            "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                            "success": response.status < 400
                        }
                else:
                    async with self.session.post(url, json=data, params=params) as response:
                        return {
                            "status": response.status,
                            "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                            "success": response.status < 400
                        }
            elif method.upper() == "DELETE":
                async with self.session.delete(url, params=params) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "success": response.status < 400
                    }
        except Exception as e:
            return {
                "status": 500,
                "data": {"error": str(e)},
                "success": False
            }
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        
        self.test_results.append(result)
        
        if success:
            print(f"✅ {test_name}: {details}")
        else:
            print(f"❌ {test_name}: {details}")
            self.failed_tests.append(result)
    
    def count_files_in_directory(self, directory: str) -> int:
        """Count files in uploads directory"""
        try:
            if not os.path.exists(directory):
                return 0
            
            file_count = 0
            for root, dirs, files in os.walk(directory):
                # Only count image files (matching the API logic)
                import mimetypes
                for file in files:
                    file_path = os.path.join(root, file)
                    mime_type, _ = mimetypes.guess_type(file_path)
                    if mime_type and mime_type.startswith('image/'):
                        file_count += 1
            return file_count
        except Exception as e:
            print(f"Error counting files: {e}")
            return -1
    
    def create_test_image(self) -> bytes:
        """Create a simple test image (PNG format)"""
        # Create a minimal PNG file (1x1 pixel)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
        return png_data
    
    # ==== MEDIA MANAGEMENT API TESTS ====
    
    async def test_get_initial_file_count(self):
        """Test 1: Get initial file count via API (HIGH PRIORITY)"""
        response = await self.make_request("GET", "/admin/media/files")
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "files" in data:
                files = data["files"]
                total = data.get("total", len(files))
                
                # Also count files in filesystem
                fs_count = self.count_files_in_directory(self.uploads_dir)
                
                self.log_test(
                    "Get Initial File Count",
                    True,
                    f"API reports {total} files, Filesystem has {fs_count} files",
                    {"api_count": total, "filesystem_count": fs_count, "files": files[:3]}  # Show first 3 files
                )
                
                # Store for later comparison
                self.initial_api_count = total
                self.initial_fs_count = fs_count
                self.initial_files = files
                
                return files
            else:
                self.log_test("Get Initial File Count", False, "Invalid API response structure", data)
                return []
        else:
            self.log_test("Get Initial File Count", False, f"API request failed: {response['status']}", response["data"])
            return []
    
    async def test_upload_new_file(self):
        """Test 2: Upload a new test file (HIGH PRIORITY)"""
        # Create test image
        test_image_data = self.create_test_image()
        test_filename = f"test_media_{int(time.time())}.png"
        
        # Get filesystem count before upload
        fs_count_before = self.count_files_in_directory(self.uploads_dir)
        
        files = {
            "file": (test_filename, test_image_data, "image/png")
        }
        
        form_data = {
            "category": "test",
            "description": "Test image for media management testing"
        }
        
        response = await self.make_request("POST", "/admin/media/upload", data=form_data, files=files)
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "file" in data:
                uploaded_file = data["file"]
                
                # Get filesystem count after upload
                fs_count_after = self.count_files_in_directory(self.uploads_dir)
                
                # Verify file was actually saved to disk
                file_url = uploaded_file.get("url", "")
                file_path = file_url.replace("/api/", "/app/backend/") if file_url.startswith("/api/") else ""
                file_exists_on_disk = os.path.exists(file_path) if file_path else False
                
                self.log_test(
                    "Upload New File",
                    True,
                    f"File uploaded: {uploaded_file.get('filename', 'unknown')}, FS count: {fs_count_before} → {fs_count_after}, On disk: {file_exists_on_disk}",
                    {
                        "uploaded_file": uploaded_file,
                        "fs_count_before": fs_count_before,
                        "fs_count_after": fs_count_after,
                        "file_exists_on_disk": file_exists_on_disk,
                        "file_path": file_path
                    }
                )
                
                # Store uploaded file info for deletion test
                self.uploaded_file_id = uploaded_file.get("id")
                self.uploaded_file_path = file_path
                
                return uploaded_file
            else:
                self.log_test("Upload New File", False, "Invalid upload response structure", data)
                return None
        else:
            self.log_test("Upload New File", False, f"Upload failed: {response['status']}", response["data"])
            return None
    
    async def test_verify_upload_in_api_list(self):
        """Test 3: Verify uploaded file appears in API file list (HIGH PRIORITY)"""
        response = await self.make_request("GET", "/admin/media/files")
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "files" in data:
                files = data["files"]
                total = data.get("total", len(files))
                
                # Check if our uploaded file is in the list
                uploaded_file_found = False
                if hasattr(self, 'uploaded_file_id') and self.uploaded_file_id:
                    for file in files:
                        if file.get("id") == self.uploaded_file_id:
                            uploaded_file_found = True
                            break
                
                # Compare with initial count
                count_increased = total > getattr(self, 'initial_api_count', 0)
                
                self.log_test(
                    "Verify Upload in API List",
                    uploaded_file_found and count_increased,
                    f"File count: {getattr(self, 'initial_api_count', 0)} → {total}, Uploaded file found: {uploaded_file_found}",
                    {"total_files": total, "uploaded_file_found": uploaded_file_found, "count_increased": count_increased}
                )
                
                return files
            else:
                self.log_test("Verify Upload in API List", False, "Invalid API response structure", data)
                return []
        else:
            self.log_test("Verify Upload in API List", False, f"API request failed: {response['status']}", response["data"])
            return []
    
    async def test_delete_uploaded_file(self):
        """Test 4: Delete the uploaded file (HIGH PRIORITY)"""
        if not hasattr(self, 'uploaded_file_id') or not self.uploaded_file_id:
            self.log_test("Delete Uploaded File", False, "No uploaded file ID available for deletion", None)
            return False
        
        # Get filesystem count before deletion
        fs_count_before = self.count_files_in_directory(self.uploads_dir)
        file_exists_before = os.path.exists(self.uploaded_file_path) if hasattr(self, 'uploaded_file_path') else False
        
        response = await self.make_request("DELETE", f"/admin/media/files/{self.uploaded_file_id}")
        
        if response["success"]:
            data = response["data"]
            if data.get("success"):
                # Get filesystem count after deletion
                fs_count_after = self.count_files_in_directory(self.uploads_dir)
                file_exists_after = os.path.exists(self.uploaded_file_path) if hasattr(self, 'uploaded_file_path') else True
                
                # Check if file was actually deleted from disk
                file_actually_deleted = file_exists_before and not file_exists_after
                count_decreased = fs_count_after < fs_count_before
                
                self.log_test(
                    "Delete Uploaded File",
                    file_actually_deleted and count_decreased,
                    f"API success: {data.get('success')}, FS count: {fs_count_before} → {fs_count_after}, File deleted from disk: {file_actually_deleted}",
                    {
                        "api_response": data,
                        "fs_count_before": fs_count_before,
                        "fs_count_after": fs_count_after,
                        "file_exists_before": file_exists_before,
                        "file_exists_after": file_exists_after,
                        "file_actually_deleted": file_actually_deleted
                    }
                )
                
                return file_actually_deleted
            else:
                self.log_test("Delete Uploaded File", False, "API returned success=false", data)
                return False
        else:
            self.log_test("Delete Uploaded File", False, f"Delete request failed: {response['status']}", response["data"])
            return False
    
    async def test_verify_deletion_in_api_list(self):
        """Test 5: Verify deleted file is removed from API list (HIGH PRIORITY)"""
        response = await self.make_request("GET", "/admin/media/files")
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "files" in data:
                files = data["files"]
                total = data.get("total", len(files))
                
                # Check if our deleted file is still in the list
                deleted_file_still_found = False
                if hasattr(self, 'uploaded_file_id') and self.uploaded_file_id:
                    for file in files:
                        if file.get("id") == self.uploaded_file_id:
                            deleted_file_still_found = True
                            break
                
                # Compare with initial count (should be back to original)
                count_back_to_original = total == getattr(self, 'initial_api_count', 0)
                
                self.log_test(
                    "Verify Deletion in API List",
                    not deleted_file_still_found and count_back_to_original,
                    f"File count: {getattr(self, 'initial_api_count', 0)} → {total}, Deleted file still found: {deleted_file_still_found}",
                    {"total_files": total, "deleted_file_still_found": deleted_file_still_found, "count_back_to_original": count_back_to_original}
                )
                
                return not deleted_file_still_found
            else:
                self.log_test("Verify Deletion in API List", False, "Invalid API response structure", data)
                return False
        else:
            self.log_test("Verify Deletion in API List", False, f"API request failed: {response['status']}", response["data"])
            return False
    
    async def test_delete_existing_file(self):
        """Test 6: Test deleting an existing file (if any) (MEDIUM PRIORITY)"""
        if not hasattr(self, 'initial_files') or not self.initial_files:
            self.log_test("Delete Existing File", True, "No existing files to delete (empty media library)", None)
            return True
        
        # Try to delete the first existing file
        existing_file = self.initial_files[0]
        file_id = existing_file.get("id")
        file_url = existing_file.get("url", "")
        file_path = file_url.replace("/api/", "/app/backend/") if file_url.startswith("/api/") else ""
        
        # Check if file exists on disk before deletion
        file_exists_before = os.path.exists(file_path) if file_path else False
        fs_count_before = self.count_files_in_directory(self.uploads_dir)
        
        response = await self.make_request("DELETE", f"/admin/media/files/{file_id}")
        
        if response["success"]:
            data = response["data"]
            if data.get("success"):
                # Check if file was actually deleted from disk
                file_exists_after = os.path.exists(file_path) if file_path else True
                fs_count_after = self.count_files_in_directory(self.uploads_dir)
                
                file_actually_deleted = file_exists_before and not file_exists_after
                count_decreased = fs_count_after < fs_count_before
                
                self.log_test(
                    "Delete Existing File",
                    file_actually_deleted and count_decreased,
                    f"Deleted existing file: {existing_file.get('filename', 'unknown')}, FS count: {fs_count_before} → {fs_count_after}, Actually deleted: {file_actually_deleted}",
                    {
                        "deleted_file": existing_file,
                        "api_response": data,
                        "file_exists_before": file_exists_before,
                        "file_exists_after": file_exists_after,
                        "file_actually_deleted": file_actually_deleted,
                        "fs_count_before": fs_count_before,
                        "fs_count_after": fs_count_after
                    }
                )
                
                return file_actually_deleted
            else:
                self.log_test("Delete Existing File", False, "API returned success=false", data)
                return False
        else:
            self.log_test("Delete Existing File", False, f"Delete request failed: {response['status']}", response["data"])
            return False
    
    async def test_upload_directory_permissions(self):
        """Test 7: Verify upload directory permissions (MEDIUM PRIORITY)"""
        try:
            # Check if uploads directory exists and is writable
            uploads_exists = os.path.exists(self.uploads_dir)
            uploads_writable = os.access(self.uploads_dir, os.W_OK) if uploads_exists else False
            
            # Try to create a test subdirectory
            test_dir = os.path.join(self.uploads_dir, "permission_test")
            can_create_dir = False
            try:
                os.makedirs(test_dir, exist_ok=True)
                can_create_dir = True
                # Clean up test directory
                if os.path.exists(test_dir):
                    os.rmdir(test_dir)
            except Exception as e:
                can_create_dir = False
            
            all_permissions_ok = uploads_exists and uploads_writable and can_create_dir
            
            self.log_test(
                "Upload Directory Permissions",
                all_permissions_ok,
                f"Directory exists: {uploads_exists}, Writable: {uploads_writable}, Can create subdirs: {can_create_dir}",
                {
                    "uploads_dir": self.uploads_dir,
                    "exists": uploads_exists,
                    "writable": uploads_writable,
                    "can_create_dir": can_create_dir
                }
            )
            
            return all_permissions_ok
            
        except Exception as e:
            self.log_test("Upload Directory Permissions", False, f"Permission check failed: {str(e)}", {"error": str(e)})
            return False
    
    async def test_api_response_consistency(self):
        """Test 8: Test API response consistency (MEDIUM PRIORITY)"""
        # Make multiple requests to check consistency
        responses = []
        
        for i in range(3):
            response = await self.make_request("GET", "/admin/media/files")
            if response["success"]:
                data = response["data"]
                if data.get("success") and "files" in data:
                    responses.append({
                        "total": data.get("total", 0),
                        "file_count": len(data["files"]),
                        "response_time": i
                    })
            
            # Small delay between requests
            await asyncio.sleep(0.5)
        
        # Check if all responses are consistent
        if len(responses) >= 2:
            first_total = responses[0]["total"]
            all_consistent = all(r["total"] == first_total for r in responses)
            
            self.log_test(
                "API Response Consistency",
                all_consistent,
                f"Made {len(responses)} requests, all returned same count: {all_consistent} (count: {first_total})",
                responses
            )
            
            return all_consistent
        else:
            self.log_test("API Response Consistency", False, "Could not get enough responses for consistency check", responses)
            return False
    
    # ==== MAIN TEST EXECUTION ====
    
    async def run_all_tests(self):
        """Run all media management tests"""
        print("🚀 Starting Cataloro Marketplace Media Management API Testing...")
        print(f"📡 Testing against: {BACKEND_URL}")
        print(f"📁 Upload directory: {self.uploads_dir}")
        print("=" * 80)
        
        # HIGH PRIORITY TESTS - Core Media Management Flow
        print("\n📁 HIGH PRIORITY: Core Media Management Flow")
        initial_files = await self.test_get_initial_file_count()
        uploaded_file = await self.test_upload_new_file()
        await self.test_verify_upload_in_api_list()
        deletion_success = await self.test_delete_uploaded_file()
        await self.test_verify_deletion_in_api_list()
        
        # MEDIUM PRIORITY TESTS - Additional Verification
        print("\n🔍 MEDIUM PRIORITY: Additional Verification Tests")
        await self.test_delete_existing_file()
        await self.test_upload_directory_permissions()
        await self.test_api_response_consistency()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📋 MEDIA MANAGEMENT API TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = len(self.failed_tests)
        
        print(f"✅ Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS ({len(self.failed_tests)}):")
            for test in self.failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        print(f"\n🎯 MEDIA MANAGEMENT VERIFICATION:")
        print(f"   • File Upload: {'✅' if any('Upload' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • File Deletion: {'✅' if any('Delete' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • File System Persistence: {'✅' if any('disk' in t['details'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • API Consistency: {'✅' if any('Consistency' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        
        # Identify where persistence is failing
        print(f"\n🔍 PERSISTENCE ANALYSIS:")
        upload_tests = [t for t in self.test_results if 'Upload' in t['test']]
        delete_tests = [t for t in self.test_results if 'Delete' in t['test']]
        
        if upload_tests:
            upload_success = any(t['success'] for t in upload_tests)
            print(f"   • Upload Persistence: {'✅ Working' if upload_success else '❌ Failing'}")
        
        if delete_tests:
            delete_success = any(t['success'] for t in delete_tests)
            print(f"   • Delete Persistence: {'✅ Working' if delete_success else '❌ Failing'}")
        
        # Determine failure level
        if failed_tests == 0:
            print(f"\n🎉 ALL MEDIA MANAGEMENT TESTS PASSED! No persistence issues detected.")
        elif failed_tests <= 2:
            print(f"\n⚠️  MINOR ISSUES DETECTED with {failed_tests} tests failing.")
        else:
            print(f"\n🚨 MAJOR PERSISTENCE ISSUES DETECTED - {failed_tests} tests failed.")
            print(f"   📍 Check: API level, filesystem level, or frontend caching issues")

async def main():
    """Main test execution"""
    tester = MediaManagementTester()
    
    try:
        await tester.setup()
        await tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())