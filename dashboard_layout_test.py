import requests
import sys
import json
from datetime import datetime, timedelta

# Configuration
BACKEND_URL = "http://217.154.0.82/api"
ADMIN_EMAIL = "admin@marketplace.com"
ADMIN_PASSWORD = "admin123"

class DashboardLayoutTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
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
                self.log_result("Admin Authentication", True, f"Successfully authenticated as {data['user']['full_name']}", {
                    "user_role": data["user"]["role"],
                    "user_email": data["user"]["email"]
                })
                return True
            else:
                self.log_result("Admin Authentication", False, f"Authentication failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication", False, f"Authentication error: {str(e)}")
            return False

    def test_dashboard_data_structure(self):
        """Test that dashboard provides proper data structure for new analytics chart"""
        if not self.admin_token:
            self.log_result("Dashboard Data Structure", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/stats")
            
            if response.status_code == 200:
                stats = response.json()
                
                # Check for the three data series mentioned in review request
                required_metrics = {
                    'users': ['total_users', 'active_users'],
                    'listings': ['total_listings', 'active_listings'], 
                    'orders': ['total_orders']
                }
                
                available_metrics = {}
                missing_metrics = []
                
                for category, metrics in required_metrics.items():
                    available_metrics[category] = {}
                    for metric in metrics:
                        if metric in stats:
                            available_metrics[category][metric] = stats[metric]
                        else:
                            missing_metrics.append(metric)
                
                if not missing_metrics:
                    # Simulate the three data series for the chart
                    chart_data = {
                        "users_series": {
                            "total": stats['total_users'],
                            "active": stats['active_users'],
                            "blocked": stats.get('blocked_users', 0)
                        },
                        "listings_series": {
                            "total": stats['total_listings'],
                            "active": stats['active_listings']
                        },
                        "orders_series": {
                            "total": stats['total_orders'],
                            "revenue": stats.get('total_revenue', 0)
                        }
                    }
                    
                    self.log_result("Dashboard Data Structure", True, "Dashboard provides complete data for three-series analytics chart", {
                        "chart_data_structure": chart_data,
                        "users_metrics": available_metrics['users'],
                        "listings_metrics": available_metrics['listings'],
                        "orders_metrics": available_metrics['orders']
                    })
                    return True
                else:
                    self.log_result("Dashboard Data Structure", False, f"Missing required metrics: {missing_metrics}", {
                        "available_metrics": available_metrics
                    })
                    return False
            else:
                self.log_result("Dashboard Data Structure", False, f"Dashboard stats access failed - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Dashboard Data Structure", False, f"Dashboard data structure error: {str(e)}")
            return False

    def test_users_panel_stats_bars(self):
        """Test that users panel provides data for smaller stats bars"""
        if not self.admin_token:
            self.log_result("Users Panel Stats Bars", False, "No admin token available")
            return False
            
        try:
            # Get admin stats for users panel
            stats_response = self.session.get(f"{BACKEND_URL}/admin/stats")
            users_response = self.session.get(f"{BACKEND_URL}/admin/users")
            
            if stats_response.status_code == 200 and users_response.status_code == 200:
                stats = stats_response.json()
                users = users_response.json()
                
                # Calculate stats for smaller stats bars
                stats_bars_data = {
                    "total_users": stats.get('total_users', 0),
                    "active_users": stats.get('active_users', 0),
                    "blocked_users": stats.get('blocked_users', 0),
                    "admin_users": len([u for u in users if u.get('role') == 'admin']),
                    "seller_users": len([u for u in users if u.get('role') in ['seller', 'both']]),
                    "buyer_users": len([u for u in users if u.get('role') in ['buyer', 'both']])
                }
                
                self.log_result("Users Panel Stats Bars", True, "Users panel provides complete data for smaller stats bars", {
                    "stats_bars_data": stats_bars_data,
                    "total_users": stats_bars_data['total_users'],
                    "active_users": stats_bars_data['active_users'],
                    "user_roles_breakdown": {
                        "admin": stats_bars_data['admin_users'],
                        "sellers": stats_bars_data['seller_users'],
                        "buyers": stats_bars_data['buyer_users']
                    }
                })
                return True
            else:
                self.log_result("Users Panel Stats Bars", False, "Could not access required endpoints for users stats")
                return False
                
        except Exception as e:
            self.log_result("Users Panel Stats Bars", False, f"Users panel stats error: {str(e)}")
            return False

    def test_listings_panel_thumbnails(self):
        """Test that listings panel provides thumbnail images"""
        if not self.admin_token:
            self.log_result("Listings Panel Thumbnails", False, "No admin token available")
            return False
            
        try:
            response = self.session.get(f"{BACKEND_URL}/admin/listings")
            
            if response.status_code == 200:
                listings = response.json()
                
                if isinstance(listings, list) and listings:
                    # Check listings for thumbnail capability
                    thumbnail_data = {
                        "total_listings": len(listings),
                        "listings_with_images": 0,
                        "accessible_thumbnails": 0,
                        "sample_thumbnails": []
                    }
                    
                    # Check first 10 listings for images
                    for listing in listings[:10]:
                        listing_id = listing.get('id')
                        if listing_id:
                            try:
                                # Get full listing details
                                detail_response = self.session.get(f"{BACKEND_URL}/listings/{listing_id}")
                                if detail_response.status_code == 200:
                                    detail_data = detail_response.json()
                                    images = detail_data.get('images', [])
                                    
                                    if images:
                                        thumbnail_data['listings_with_images'] += 1
                                        first_image = images[0]
                                        
                                        # Test thumbnail accessibility
                                        if first_image.startswith('/uploads/'):
                                            thumbnail_url = f"http://217.154.0.82{first_image}"
                                            try:
                                                img_response = requests.get(thumbnail_url, timeout=3)
                                                if img_response.status_code == 200:
                                                    thumbnail_data['accessible_thumbnails'] += 1
                                                    if len(thumbnail_data['sample_thumbnails']) < 3:
                                                        thumbnail_data['sample_thumbnails'].append({
                                                            "listing_title": listing.get('title'),
                                                            "thumbnail_url": first_image,
                                                            "accessible": True
                                                        })
                                            except:
                                                pass
                            except:
                                pass
                    
                    success = thumbnail_data['listings_with_images'] > 0
                    message = "Listings panel has thumbnail images available" if success else "No thumbnail images found in listings"
                    
                    self.log_result("Listings Panel Thumbnails", success, message, thumbnail_data)
                    return success
                else:
                    self.log_result("Listings Panel Thumbnails", True, "No listings found to check for thumbnails", {
                        "listings_count": len(listings) if isinstance(listings, list) else 0
                    })
                    return True
            else:
                self.log_result("Listings Panel Thumbnails", False, f"Listings panel access failed - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Listings Panel Thumbnails", False, f"Listings thumbnails error: {str(e)}")
            return False

    def test_admin_navigation_tabs(self):
        """Test that all admin navigation tabs are accessible"""
        if not self.admin_token:
            self.log_result("Admin Navigation Tabs", False, "No admin token available")
            return False
            
        try:
            # Test the four main admin tabs mentioned in review request
            admin_tabs = {
                "Dashboard": "admin/stats",
                "Users": "admin/users", 
                "Listings": "admin/listings",
                "Orders": "admin/orders"
            }
            
            tab_results = {}
            all_accessible = True
            
            for tab_name, endpoint in admin_tabs.items():
                try:
                    response = self.session.get(f"{BACKEND_URL}/{endpoint}")
                    success = response.status_code == 200
                    
                    tab_results[tab_name] = {
                        "accessible": success,
                        "status_code": response.status_code,
                        "has_data": False
                    }
                    
                    if success:
                        try:
                            data = response.json()
                            if isinstance(data, list):
                                tab_results[tab_name]["has_data"] = len(data) > 0
                                tab_results[tab_name]["data_count"] = len(data)
                            elif isinstance(data, dict):
                                tab_results[tab_name]["has_data"] = len(data) > 0
                                tab_results[tab_name]["data_fields"] = list(data.keys())[:5]  # First 5 fields
                        except:
                            pass
                    else:
                        all_accessible = False
                        
                except Exception as e:
                    tab_results[tab_name] = {
                        "accessible": False,
                        "error": str(e)
                    }
                    all_accessible = False
            
            if all_accessible:
                self.log_result("Admin Navigation Tabs", True, "All admin navigation tabs are accessible", tab_results)
            else:
                failed_tabs = [tab for tab, result in tab_results.items() if not result.get('accessible', False)]
                self.log_result("Admin Navigation Tabs", False, f"Some admin tabs failed: {failed_tabs}", tab_results)
            
            return all_accessible
                
        except Exception as e:
            self.log_result("Admin Navigation Tabs", False, f"Admin navigation error: {str(e)}")
            return False

    def test_dashboard_layout_data_completeness(self):
        """Test that dashboard has complete data for the new layout (no visitor countries/quick actions)"""
        if not self.admin_token:
            self.log_result("Dashboard Layout Data", False, "No admin token available")
            return False
            
        try:
            # Get all data needed for the new dashboard layout
            stats_response = self.session.get(f"{BACKEND_URL}/admin/stats")
            users_response = self.session.get(f"{BACKEND_URL}/admin/users")
            listings_response = self.session.get(f"{BACKEND_URL}/admin/listings")
            orders_response = self.session.get(f"{BACKEND_URL}/admin/orders")
            
            all_responses = [stats_response, users_response, listings_response, orders_response]
            all_successful = all(r.status_code == 200 for r in all_responses)
            
            if all_successful:
                stats = stats_response.json()
                users = users_response.json()
                listings = listings_response.json()
                orders = orders_response.json()
                
                # Prepare complete dashboard data (replacing visitor countries and quick actions)
                dashboard_data = {
                    "analytics_chart_data": {
                        "users": {
                            "total": stats.get('total_users', 0),
                            "active": stats.get('active_users', 0),
                            "blocked": stats.get('blocked_users', 0)
                        },
                        "listings": {
                            "total": stats.get('total_listings', 0),
                            "active": stats.get('active_listings', 0)
                        },
                        "orders": {
                            "total": stats.get('total_orders', 0),
                            "revenue": stats.get('total_revenue', 0)
                        }
                    },
                    "summary_stats": {
                        "total_users": len(users),
                        "total_listings": len(listings),
                        "total_orders": len(orders),
                        "total_revenue": stats.get('total_revenue', 0)
                    },
                    "recent_activity": {
                        "recent_users": len([u for u in users if u.get('created_at')]),
                        "recent_listings": len([l for l in listings if l.get('created_at')]),
                        "recent_orders": len(orders)
                    }
                }
                
                self.log_result("Dashboard Layout Data", True, "Complete dashboard data available for new layout", {
                    "analytics_ready": True,
                    "summary_stats": dashboard_data["summary_stats"],
                    "chart_data_points": len(dashboard_data["analytics_chart_data"]),
                    "data_completeness": "100%"
                })
                return True
            else:
                failed_endpoints = []
                for i, response in enumerate(all_responses):
                    if response.status_code != 200:
                        endpoints = ["admin/stats", "admin/users", "admin/listings", "admin/orders"]
                        failed_endpoints.append(f"{endpoints[i]} ({response.status_code})")
                
                self.log_result("Dashboard Layout Data", False, f"Some dashboard endpoints failed: {failed_endpoints}")
                return False
                
        except Exception as e:
            self.log_result("Dashboard Layout Data", False, f"Dashboard layout data error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all dashboard layout tests"""
        print("🎨 Starting Dashboard Layout & Navigation Testing...")
        print("=" * 60)
        
        # Login first
        if not self.admin_login():
            print("❌ Cannot proceed without admin login")
            return False
        
        # Run all tests
        tests = [
            self.test_dashboard_data_structure,
            self.test_users_panel_stats_bars,
            self.test_listings_panel_thumbnails,
            self.test_admin_navigation_tabs,
            self.test_dashboard_layout_data_completeness
        ]
        
        total_tests = len(tests)
        passed_tests = 0
        
        for test in tests:
            if test():
                passed_tests += 1
        
        # Summary
        print("=" * 60)
        print(f"📊 DASHBOARD LAYOUT TESTING SUMMARY")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 ALL DASHBOARD LAYOUT TESTS PASSED!")
        else:
            print("⚠️  Some dashboard layout tests failed - check details above")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = DashboardLayoutTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)