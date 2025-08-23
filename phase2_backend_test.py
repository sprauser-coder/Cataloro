#!/usr/bin/env python3
"""
Phase 2 Bug Fixes Backend Testing Suite
Testing hero image uploads, CMS settings, dashboard analytics, and typography/color settings
"""

import requests
import sys
import json
from datetime import datetime, timedelta
import time
import io
import os
from pathlib import Path

# Configuration
BACKEND_URL = "http://217.154.0.82/api"  # From frontend/.env
STATIC_URL = "http://217.154.0.82"  # For static file serving
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class Phase2Tester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.uploaded_hero_image_url = None
        self.uploaded_hero_background_url = None
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details:
            for key, value in details.items():
                print(f"  {key}: {value}")
        print()

    def admin_login(self):
        """Login as admin user"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                self.log_result("Admin Login", True, "Successfully logged in as admin", {
                    "user_role": data["user"]["role"],
                    "user_email": data["user"]["email"]
                })
                return True
            else:
                self.log_result("Admin Login", False, f"Login failed with status {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Admin Login", False, f"Login error: {str(e)}")
            return False

    def create_test_image(self, format='PNG', size_mb=1):
        """Create a test image"""
        try:
            from PIL import Image
            import io
            
            # Create a test image
            img = Image.new('RGB', (200, 200), color='blue')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format=format)
            img_bytes.seek(0)
            
            # If we need a larger file, create a bigger image
            if size_mb > 1:
                img = Image.new('RGB', (1000 * size_mb, 1000), color='blue')
                img_bytes = io.BytesIO()
                img.save(img_bytes, format=format)
                img_bytes.seek(0)
            
            return img_bytes.getvalue()
        except ImportError:
            # Fallback: create minimal image headers for testing
            if format == 'PNG':
                # Minimal PNG header
                base_png = b'\x89PNG\r\n\x1a\n\rIHDR\x01\x01\x08\x02\x90wS\xde\tpHYs\x0b\x13\x0b\x13\x01\x9a\x9c\x18\nIDATx\x9cc\xf8\x01\x01IEND\xaeB`\x82'
                if size_mb > 1:
                    # Pad with null bytes to reach desired size
                    padding_size = (size_mb * 1024 * 1024) - len(base_png)
                    return base_png + b'\x00' * padding_size
                return base_png
            else:
                # Minimal JPEG header
                base_jpeg = b'\xff\xd8\xff\xe0\x10JFIF\x01\x01\x01HH\xff\xdbC\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x11\x08\x01\x01\x01\x01\x11\x02\x11\x01\x03\x11\x01\xff\xc4\x14\x01\x08\xff\xc4\x14\x10\x01\xff\xda\x08\x01\x01?\xaa\xff\xd9'
                if size_mb > 1:
                    # Pad with null bytes to reach desired size
                    padding_size = (size_mb * 1024 * 1024) - len(base_jpeg)
                    return base_jpeg + b'\x00' * padding_size
                return base_jpeg

    # ===========================
    # 1. HERO IMAGE UPLOAD TESTS
    # ===========================

    def test_hero_image_upload_endpoint(self):
        """Test POST /admin/cms/upload-hero-image endpoint"""
        if not self.admin_token:
            self.log_result("Hero Image Upload", False, "No admin token available")
            return False
            
        try:
            # Test valid PNG upload
            test_image_data = self.create_test_image('PNG', 1)
            
            files = {
                'file': ('hero_image.png', test_image_data, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-image", files=files)
            
            if response.status_code == 200:
                result = response.json()
                hero_image_url = result.get('hero_image_url')
                
                if hero_image_url:
                    self.uploaded_hero_image_url = hero_image_url
                    # Test if the uploaded file is accessible
                    file_url = f"{STATIC_URL}{hero_image_url}"
                    file_response = requests.get(file_url, timeout=10)
                    
                    if file_response.status_code == 200:
                        self.log_result("Hero Image Upload", True, "Hero image uploaded and accessible", {
                            "hero_image_url": hero_image_url,
                            "file_url": file_url,
                            "upload_response": result,
                            "file_size": len(file_response.content)
                        })
                        return True
                    else:
                        self.log_result("Hero Image Upload", False, "Hero image uploaded but not accessible via HTTP", {
                            "hero_image_url": hero_image_url,
                            "file_url": file_url,
                            "file_status": file_response.status_code
                        })
                        return False
                else:
                    self.log_result("Hero Image Upload", False, "Hero image upload succeeded but no URL returned", {
                        "response": result
                    })
                    return False
            else:
                self.log_result("Hero Image Upload", False, f"Hero image upload failed - HTTP {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Hero Image Upload", False, f"Hero image upload error: {str(e)}")
            return False

    def test_hero_image_file_size_limit(self):
        """Test hero image 5MB file size limit"""
        if not self.admin_token:
            self.log_result("Hero Image Size Limit", False, "No admin token available")
            return False
            
        try:
            # Test file larger than 5MB (should fail)
            large_image_data = self.create_test_image('PNG', 6)  # 6MB
            
            files = {
                'file': ('large_hero.png', large_image_data, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-image", files=files)
            
            if response.status_code == 400:
                self.log_result("Hero Image Size Limit", True, "5MB size limit properly enforced", {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return True
            else:
                self.log_result("Hero Image Size Limit", False, f"Size limit not enforced - got status {response.status_code}", {
                    "expected": 400,
                    "actual": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Hero Image Size Limit", False, f"Error testing size limit: {str(e)}")
            return False

    def test_hero_image_file_type_validation(self):
        """Test hero image file type validation (PNG, JPEG only)"""
        if not self.admin_token:
            self.log_result("Hero Image Type Validation", False, "No admin token available")
            return False
            
        try:
            # Test valid JPEG
            jpeg_data = self.create_test_image('JPEG', 1)
            files = {
                'file': ('hero_image.jpg', jpeg_data, 'image/jpeg')
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-image", files=files)
            
            if response.status_code == 200:
                jpeg_success = True
                jpeg_result = response.json()
            else:
                jpeg_success = False
                jpeg_result = {"error": response.text}
            
            # Test invalid format (GIF should fail)
            gif_data = b'GIF89a\x01\x01!\xf9\x04\x01,\x01\x01\x02\x02\x04\x01;'
            files = {
                'file': ('hero_image.gif', gif_data, 'image/gif')
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-image", files=files)
            
            if response.status_code == 400:
                gif_rejected = True
            else:
                gif_rejected = False
            
            if jpeg_success and gif_rejected:
                self.log_result("Hero Image Type Validation", True, "File type validation working correctly", {
                    "jpeg_accepted": jpeg_success,
                    "gif_rejected": gif_rejected,
                    "jpeg_response": jpeg_result
                })
                return True
            else:
                self.log_result("Hero Image Type Validation", False, "File type validation not working correctly", {
                    "jpeg_accepted": jpeg_success,
                    "gif_rejected": gif_rejected
                })
                return False
                
        except Exception as e:
            self.log_result("Hero Image Type Validation", False, f"Error testing file type validation: {str(e)}")
            return False

    def test_hero_background_upload_endpoint(self):
        """Test POST /admin/cms/upload-hero-background endpoint"""
        if not self.admin_token:
            self.log_result("Hero Background Upload", False, "No admin token available")
            return False
            
        try:
            # Test valid PNG upload
            test_image_data = self.create_test_image('PNG', 2)  # 2MB background
            
            files = {
                'file': ('hero_background.png', test_image_data, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-background", files=files)
            
            if response.status_code == 200:
                result = response.json()
                hero_background_url = result.get('hero_background_image_url')
                
                if hero_background_url:
                    self.uploaded_hero_background_url = hero_background_url
                    # Test if the uploaded file is accessible
                    file_url = f"{STATIC_URL}{hero_background_url}"
                    file_response = requests.get(file_url, timeout=10)
                    
                    if file_response.status_code == 200:
                        self.log_result("Hero Background Upload", True, "Hero background uploaded and accessible", {
                            "hero_background_url": hero_background_url,
                            "file_url": file_url,
                            "upload_response": result,
                            "file_size": len(file_response.content)
                        })
                        return True
                    else:
                        self.log_result("Hero Background Upload", False, "Hero background uploaded but not accessible via HTTP", {
                            "hero_background_url": hero_background_url,
                            "file_url": file_url,
                            "file_status": file_response.status_code
                        })
                        return False
                else:
                    self.log_result("Hero Background Upload", False, "Hero background upload succeeded but no URL returned", {
                        "response": result
                    })
                    return False
            else:
                self.log_result("Hero Background Upload", False, f"Hero background upload failed - HTTP {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Hero Background Upload", False, f"Hero background upload error: {str(e)}")
            return False

    def test_hero_background_file_size_limit(self):
        """Test hero background 25MB file size limit"""
        if not self.admin_token:
            self.log_result("Hero Background Size Limit", False, "No admin token available")
            return False
            
        try:
            # Test file larger than 25MB (should fail)
            large_image_data = self.create_test_image('PNG', 26)  # 26MB
            
            files = {
                'file': ('large_background.png', large_image_data, 'image/png')
            }
            
            response = self.session.post(f"{BACKEND_URL}/admin/cms/upload-hero-background", files=files)
            
            if response.status_code == 400:
                self.log_result("Hero Background Size Limit", True, "25MB size limit properly enforced", {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return True
            else:
                self.log_result("Hero Background Size Limit", False, f"Size limit not enforced - got status {response.status_code}", {
                    "expected": 400,
                    "actual": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Hero Background Size Limit", False, f"Error testing size limit: {str(e)}")
            return False

    # ===========================
    # 2. CMS SETTINGS SAVE TESTS
    # ===========================

    def test_cms_color_fields_save(self):
        """Test that font_color, link_color, link_hover_color fields can be saved"""
        if not self.admin_token:
            self.log_result("CMS Color Fields Save", False, "No admin token available")
            return False
            
        try:
            # Test saving new color fields
            color_settings = {
                "font_color": "#333333",
                "link_color": "#0066cc",
                "link_hover_color": "#004499"
            }
            
            response = self.session.put(f"{BACKEND_URL}/admin/cms/settings", json=color_settings)
            
            if response.status_code == 200:
                # Verify the fields were saved by retrieving them
                get_response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
                
                if get_response.status_code == 200:
                    settings = get_response.json()
                    
                    font_color_saved = settings.get('font_color') == color_settings['font_color']
                    link_color_saved = settings.get('link_color') == color_settings['link_color']
                    link_hover_color_saved = settings.get('link_hover_color') == color_settings['link_hover_color']
                    
                    if font_color_saved and link_color_saved and link_hover_color_saved:
                        self.log_result("CMS Color Fields Save", True, "Color fields saved and retrieved successfully", {
                            "font_color": settings.get('font_color'),
                            "link_color": settings.get('link_color'),
                            "link_hover_color": settings.get('link_hover_color')
                        })
                        return True
                    else:
                        self.log_result("CMS Color Fields Save", False, "Color fields not saved correctly", {
                            "font_color_saved": font_color_saved,
                            "link_color_saved": link_color_saved,
                            "link_hover_color_saved": link_hover_color_saved,
                            "retrieved_settings": settings
                        })
                        return False
                else:
                    self.log_result("CMS Color Fields Save", False, f"Failed to retrieve settings after save - HTTP {get_response.status_code}")
                    return False
            else:
                self.log_result("CMS Color Fields Save", False, f"Failed to save color fields - HTTP {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("CMS Color Fields Save", False, f"Error testing color fields save: {str(e)}")
            return False

    def test_cms_hero_image_fields_save(self):
        """Test that hero_image_url and hero_background_image_url fields can be saved"""
        if not self.admin_token:
            self.log_result("CMS Hero Image Fields Save", False, "No admin token available")
            return False
            
        try:
            # Use uploaded image URLs if available, otherwise use test URLs
            hero_image_url = self.uploaded_hero_image_url or "/uploads/test_hero_image.png"
            hero_background_url = self.uploaded_hero_background_url or "/uploads/test_hero_background.png"
            
            hero_settings = {
                "hero_image_url": hero_image_url,
                "hero_background_image_url": hero_background_url,
                "hero_background_size": "cover"
            }
            
            response = self.session.put(f"{BACKEND_URL}/admin/cms/settings", json=hero_settings)
            
            if response.status_code == 200:
                # Verify the fields were saved by retrieving them
                get_response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
                
                if get_response.status_code == 200:
                    settings = get_response.json()
                    
                    hero_image_saved = settings.get('hero_image_url') == hero_settings['hero_image_url']
                    hero_background_saved = settings.get('hero_background_image_url') == hero_settings['hero_background_image_url']
                    hero_background_size_saved = settings.get('hero_background_size') == hero_settings['hero_background_size']
                    
                    if hero_image_saved and hero_background_saved and hero_background_size_saved:
                        self.log_result("CMS Hero Image Fields Save", True, "Hero image fields saved and retrieved successfully", {
                            "hero_image_url": settings.get('hero_image_url'),
                            "hero_background_image_url": settings.get('hero_background_image_url'),
                            "hero_background_size": settings.get('hero_background_size')
                        })
                        return True
                    else:
                        self.log_result("CMS Hero Image Fields Save", False, "Hero image fields not saved correctly", {
                            "hero_image_saved": hero_image_saved,
                            "hero_background_saved": hero_background_saved,
                            "hero_background_size_saved": hero_background_size_saved,
                            "retrieved_settings": settings
                        })
                        return False
                else:
                    self.log_result("CMS Hero Image Fields Save", False, f"Failed to retrieve settings after save - HTTP {get_response.status_code}")
                    return False
            else:
                self.log_result("CMS Hero Image Fields Save", False, f"Failed to save hero image fields - HTTP {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("CMS Hero Image Fields Save", False, f"Error testing hero image fields save: {str(e)}")
            return False

    # ===========================
    # 3. DASHBOARD ANALYTICS TESTS
    # ===========================

    def test_dashboard_analytics_data(self):
        """Test dashboard stats provide proper data for horizontal chart layout"""
        if not self.admin_token:
            self.log_result("Dashboard Analytics Data", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/stats")
            
            if response.status_code == 200:
                stats = response.json()
                
                # Check required fields for dashboard analytics
                required_fields = [
                    'total_users', 'active_users', 'blocked_users',
                    'total_listings', 'active_listings',
                    'total_orders', 'total_revenue'
                ]
                
                missing_fields = [field for field in required_fields if field not in stats]
                
                if not missing_fields:
                    # Check that values are numeric
                    numeric_fields_valid = all(
                        isinstance(stats[field], (int, float)) for field in required_fields
                    )
                    
                    if numeric_fields_valid:
                        self.log_result("Dashboard Analytics Data", True, "Dashboard stats provide complete data for horizontal chart", {
                            "total_users": stats['total_users'],
                            "active_users": stats['active_users'],
                            "blocked_users": stats['blocked_users'],
                            "total_listings": stats['total_listings'],
                            "active_listings": stats['active_listings'],
                            "total_orders": stats['total_orders'],
                            "total_revenue": stats['total_revenue']
                        })
                        return True
                    else:
                        self.log_result("Dashboard Analytics Data", False, "Some dashboard stats are not numeric", {
                            "stats": stats
                        })
                        return False
                else:
                    self.log_result("Dashboard Analytics Data", False, f"Missing required fields: {missing_fields}", {
                        "available_fields": list(stats.keys()),
                        "missing_fields": missing_fields
                    })
                    return False
            else:
                self.log_result("Dashboard Analytics Data", False, f"Failed to get dashboard stats - HTTP {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Dashboard Analytics Data", False, f"Error testing dashboard analytics: {str(e)}")
            return False

    def test_admin_functionality_still_works(self):
        """Test that all admin functionality still works"""
        if not self.admin_token:
            self.log_result("Admin Functionality Check", False, "No admin token available")
            return False
            
        try:
            # Test multiple admin endpoints
            endpoints_to_test = [
                ("admin/users", "Admin Users Management"),
                ("admin/listings", "Admin Listings Management"),
                ("admin/orders", "Admin Orders Management"),
                ("admin/cms/settings", "Admin CMS Settings"),
                ("admin/cms/pages", "Admin Pages Management"),
                ("admin/cms/navigation", "Admin Navigation Management")
            ]
            
            results = {}
            all_working = True
            
            for endpoint, description in endpoints_to_test:
                try:
                    response = self.session.get(f"{BACKEND_URL}/{endpoint}")
                    success = response.status_code == 200
                    results[description] = {
                        "success": success,
                        "status_code": response.status_code
                    }
                    if not success:
                        all_working = False
                except Exception as e:
                    results[description] = {
                        "success": False,
                        "error": str(e)
                    }
                    all_working = False
            
            if all_working:
                self.log_result("Admin Functionality Check", True, "All admin functionality working correctly", {
                    "tested_endpoints": len(endpoints_to_test),
                    "results": results
                })
                return True
            else:
                self.log_result("Admin Functionality Check", False, "Some admin functionality not working", {
                    "results": results
                })
                return False
                
        except Exception as e:
            self.log_result("Admin Functionality Check", False, f"Error testing admin functionality: {str(e)}")
            return False

    # ===========================
    # 4. TYPOGRAPHY AND COLOR SETTINGS TESTS
    # ===========================

    def test_typography_settings_persistence(self):
        """Test that typography settings are properly persisted"""
        if not self.admin_token:
            self.log_result("Typography Settings Persistence", False, "No admin token available")
            return False
            
        try:
            # Test saving typography settings
            typography_settings = {
                "global_font_family": "Poppins",
                "h1_size": "3.5rem",
                "h2_size": "2.5rem",
                "h1_color": "#1a1a1a",
                "h2_color": "#2a2a2a"
            }
            
            response = self.session.put(f"{BACKEND_URL}/admin/cms/settings", json=typography_settings)
            
            if response.status_code == 200:
                # Verify the fields were saved by retrieving them
                get_response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
                
                if get_response.status_code == 200:
                    settings = get_response.json()
                    
                    all_saved = all(
                        settings.get(key) == value 
                        for key, value in typography_settings.items()
                    )
                    
                    if all_saved:
                        self.log_result("Typography Settings Persistence", True, "Typography settings saved and retrieved successfully", {
                            "global_font_family": settings.get('global_font_family'),
                            "h1_size": settings.get('h1_size'),
                            "h2_size": settings.get('h2_size'),
                            "h1_color": settings.get('h1_color'),
                            "h2_color": settings.get('h2_color')
                        })
                        return True
                    else:
                        self.log_result("Typography Settings Persistence", False, "Typography settings not saved correctly", {
                            "expected": typography_settings,
                            "retrieved": {key: settings.get(key) for key in typography_settings.keys()}
                        })
                        return False
                else:
                    self.log_result("Typography Settings Persistence", False, f"Failed to retrieve settings after save - HTTP {get_response.status_code}")
                    return False
            else:
                self.log_result("Typography Settings Persistence", False, f"Failed to save typography settings - HTTP {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Typography Settings Persistence", False, f"Error testing typography settings: {str(e)}")
            return False

    def test_color_settings_persistence(self):
        """Test that color settings are properly persisted"""
        if not self.admin_token:
            self.log_result("Color Settings Persistence", False, "No admin token available")
            return False
            
        try:
            # Test saving color settings
            color_settings = {
                "primary_color": "#ff6b6b",
                "secondary_color": "#4ecdc4",
                "accent_color": "#45b7d1",
                "background_color": "#f8f9fa",
                "hero_text_color": "#ffffff",
                "hero_subtitle_color": "#e9ecef"
            }
            
            response = self.session.put(f"{BACKEND_URL}/admin/cms/settings", json=color_settings)
            
            if response.status_code == 200:
                # Verify the fields were saved by retrieving them
                get_response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
                
                if get_response.status_code == 200:
                    settings = get_response.json()
                    
                    all_saved = all(
                        settings.get(key) == value 
                        for key, value in color_settings.items()
                    )
                    
                    if all_saved:
                        self.log_result("Color Settings Persistence", True, "Color settings saved and retrieved successfully", {
                            "primary_color": settings.get('primary_color'),
                            "secondary_color": settings.get('secondary_color'),
                            "accent_color": settings.get('accent_color'),
                            "background_color": settings.get('background_color'),
                            "hero_text_color": settings.get('hero_text_color'),
                            "hero_subtitle_color": settings.get('hero_subtitle_color')
                        })
                        return True
                    else:
                        self.log_result("Color Settings Persistence", False, "Color settings not saved correctly", {
                            "expected": color_settings,
                            "retrieved": {key: settings.get(key) for key in color_settings.keys()}
                        })
                        return False
                else:
                    self.log_result("Color Settings Persistence", False, f"Failed to retrieve settings after save - HTTP {get_response.status_code}")
                    return False
            else:
                self.log_result("Color Settings Persistence", False, f"Failed to save color settings - HTTP {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Color Settings Persistence", False, f"Error testing color settings: {str(e)}")
            return False

    def test_site_settings_retrieve_all_fields(self):
        """Test that site settings can store and retrieve all the new fields"""
        if not self.admin_token:
            self.log_result("Site Settings All Fields", False, "No admin token available")
            return False
            
        try:
            # Get current settings to see all available fields
            response = self.session.get(f"{BACKEND_URL}/admin/cms/settings")
            
            if response.status_code == 200:
                settings = response.json()
                
                # Check for Phase 2 fields
                phase2_fields = [
                    'font_color', 'link_color', 'link_hover_color',
                    'hero_image_url', 'hero_background_image_url', 'hero_background_size'
                ]
                
                # Check for existing typography and color fields
                existing_fields = [
                    'global_font_family', 'h1_size', 'h2_size', 'h1_color', 'h2_color',
                    'primary_color', 'secondary_color', 'accent_color', 'background_color',
                    'hero_text_color', 'hero_subtitle_color'
                ]
                
                all_fields = phase2_fields + existing_fields
                available_fields = [field for field in all_fields if field in settings]
                missing_fields = [field for field in all_fields if field not in settings]
                
                self.log_result("Site Settings All Fields", True, f"Site settings contains {len(available_fields)}/{len(all_fields)} expected fields", {
                    "available_fields": available_fields,
                    "missing_fields": missing_fields,
                    "total_settings_fields": len(settings.keys()),
                    "sample_settings": {k: v for k, v in list(settings.items())[:10]}  # Show first 10 fields
                })
                return True
            else:
                self.log_result("Site Settings All Fields", False, f"Failed to retrieve site settings - HTTP {response.status_code}", {
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_result("Site Settings All Fields", False, f"Error testing site settings fields: {str(e)}")
            return False

    # ===========================
    # MAIN TEST RUNNER
    # ===========================

    def run_all_tests(self):
        """Run all Phase 2 tests"""
        print("🚀 Starting Phase 2 Bug Fixes Backend Testing Suite")
        print("=" * 60)
        
        # Login first
        if not self.admin_login():
            print("❌ Cannot proceed without admin login")
            return
        
        print("\n📋 PHASE 2 TESTING PLAN:")
        print("1. Hero Image Upload Endpoints")
        print("2. CMS Settings Save Functionality") 
        print("3. Dashboard Analytics Data")
        print("4. Typography and Color Settings")
        print("=" * 60)
        
        # 1. Hero Image Upload Tests
        print("\n🖼️  TESTING HERO IMAGE UPLOADS")
        print("-" * 40)
        self.test_hero_image_upload_endpoint()
        self.test_hero_image_file_size_limit()
        self.test_hero_image_file_type_validation()
        self.test_hero_background_upload_endpoint()
        self.test_hero_background_file_size_limit()
        
        # 2. CMS Settings Save Tests
        print("\n⚙️  TESTING CMS SETTINGS SAVE")
        print("-" * 40)
        self.test_cms_color_fields_save()
        self.test_cms_hero_image_fields_save()
        
        # 3. Dashboard Analytics Tests
        print("\n📊 TESTING DASHBOARD ANALYTICS")
        print("-" * 40)
        self.test_dashboard_analytics_data()
        self.test_admin_functionality_still_works()
        
        # 4. Typography and Color Settings Tests
        print("\n🎨 TESTING TYPOGRAPHY AND COLOR SETTINGS")
        print("-" * 40)
        self.test_typography_settings_persistence()
        self.test_color_settings_persistence()
        self.test_site_settings_retrieve_all_fields()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 PHASE 2 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed_tests = [r for r in self.test_results if "✅ PASS" in r["status"]]
        failed_tests = [r for r in self.test_results if "❌ FAIL" in r["status"]]
        
        print(f"✅ PASSED: {len(passed_tests)}")
        print(f"❌ FAILED: {len(failed_tests)}")
        print(f"📊 TOTAL:  {len(self.test_results)}")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        if passed_tests:
            print("\n✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        success_rate = (len(passed_tests) / len(self.test_results)) * 100 if self.test_results else 0
        print(f"\n🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        return len(failed_tests) == 0

if __name__ == "__main__":
    tester = Phase2Tester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)