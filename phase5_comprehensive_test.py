#!/usr/bin/env python3
"""
PHASE 5 BACKEND TESTING - Advanced Marketplace Features
Comprehensive testing of Phase 5 services as requested in review
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "https://marketplace-repair-1.preview.emergentagent.com/api"

class Phase5BackendTest:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        
    def log_test(self, test_name, status, details="", response_time=0):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": f"{response_time:.2f}ms",
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if response_time > 0:
            print(f"   Response Time: {response_time:.2f}ms")
        print()

    def admin_login(self):
        """Login as admin user for Phase 5 access"""
        try:
            start_time = time.time()
            
            response = self.session.post(f"{self.backend_url}/auth/login", json={
                "email": "admin@cataloro.com",
                "password": "admin123"
            })
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                user_info = data.get("user", {})
                
                self.log_test(
                    "Admin Authentication", 
                    "PASS",
                    f"Admin login successful - Role: {user_info.get('user_role', 'Unknown')}, ID: {user_info.get('id', 'Unknown')}",
                    response_time
                )
                return True
            else:
                self.log_test(
                    "Admin Authentication", 
                    "FAIL", 
                    f"Login failed - Status: {response.status_code}, Response: {response.text}",
                    response_time
                )
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", "FAIL", f"Exception: {str(e)}")
            return False

    def test_websocket_services(self):
        """Test Real-time WebSocket services"""
        try:
            print("🔄 Testing Phase 5A - Real-Time WebSocket Services...")
            
            # Test WebSocket connection statistics
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/v2/websocket/stats")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stats = data.get("stats", {})
                    
                    # Verify WebSocket stats structure
                    required_fields = ["total_connections", "unique_users", "active_rooms", "active_auctions"]
                    missing_fields = [field for field in required_fields if field not in stats]
                    
                    if not missing_fields:
                        self.log_test(
                            "WebSocket Connection Statistics", 
                            "PASS",
                            f"WebSocket stats available - Connections: {stats.get('total_connections', 0)}, Users: {stats.get('unique_users', 0)}, Rooms: {stats.get('active_rooms', 0)}",
                            response_time
                        )
                    else:
                        self.log_test(
                            "WebSocket Connection Statistics", 
                            "FAIL",
                            f"Missing WebSocket stats fields: {missing_fields}",
                            response_time
                        )
                else:
                    self.log_test(
                        "WebSocket Connection Statistics", 
                        "FAIL",
                        f"WebSocket service returned success=false",
                        response_time
                    )
            else:
                self.log_test(
                    "WebSocket Connection Statistics", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
            
            # Test WebSocket broadcast functionality
            start_time = time.time()
            broadcast_data = {
                "message": "Phase 5 Test Notification",
                "type": "system_update",
                "target": "all_users"
            }
            response = self.session.post(f"{self.backend_url}/v2/websocket/broadcast", json=broadcast_data)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test(
                        "WebSocket Notification Broadcasting", 
                        "PASS",
                        f"Broadcast successful - Recipients: {data.get('recipients', 0)}, Message: {broadcast_data['message']}",
                        response_time
                    )
                else:
                    self.log_test(
                        "WebSocket Notification Broadcasting", 
                        "FAIL",
                        f"Broadcast failed: {data.get('error', 'Unknown error')}",
                        response_time
                    )
            else:
                self.log_test(
                    "WebSocket Notification Broadcasting", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("WebSocket Services", "FAIL", f"Exception: {str(e)}")

    def test_multicurrency_system(self):
        """Test Multi-currency system"""
        try:
            print("💱 Testing Phase 5B - Multi-Currency System...")
            
            # Test supported currencies endpoint
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/v2/currency/supported")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    currencies = data.get("currencies", [])
                    
                    if len(currencies) >= 10:  # Should support 10+ currencies
                        currency_codes = [curr.get("code") for curr in currencies]
                        self.log_test(
                            "Supported Currencies Endpoint", 
                            "PASS",
                            f"Found {len(currencies)} currencies: {', '.join(currency_codes[:5])}{'...' if len(currency_codes) > 5 else ''}",
                            response_time
                        )
                    else:
                        self.log_test(
                            "Supported Currencies Endpoint", 
                            "FAIL",
                            f"Expected 10+ currencies, found {len(currencies)}",
                            response_time
                        )
                else:
                    self.log_test(
                        "Supported Currencies Endpoint", 
                        "FAIL",
                        f"Currency service returned success=false",
                        response_time
                    )
            else:
                self.log_test(
                    "Supported Currencies Endpoint", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
            
            # Test exchange rates endpoint
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/v2/currency/rates")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    rates = data.get("rates", {})
                    
                    if "USD" in rates and "GBP" in rates and "EUR" in rates:
                        self.log_test(
                            "Exchange Rates Endpoint", 
                            "PASS",
                            f"Live rates available - USD: {rates.get('USD', 0)}, GBP: {rates.get('GBP', 0)}, EUR: {rates.get('EUR', 1)}",
                            response_time
                        )
                    else:
                        self.log_test(
                            "Exchange Rates Endpoint", 
                            "FAIL",
                            f"Missing major currency rates in response",
                            response_time
                        )
                else:
                    self.log_test(
                        "Exchange Rates Endpoint", 
                        "FAIL",
                        f"Exchange rates service returned success=false",
                        response_time
                    )
            else:
                self.log_test(
                    "Exchange Rates Endpoint", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
            
            # Test currency conversion endpoint
            start_time = time.time()
            conversion_data = {
                "amount": 100.0,
                "from_currency": "EUR",
                "to_currency": "USD"
            }
            response = self.session.post(f"{self.backend_url}/v2/currency/convert", json=conversion_data)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    conversion = data.get("conversion", {})
                    
                    if "converted_amount" in conversion and "exchange_rate" in conversion:
                        self.log_test(
                            "Currency Conversion", 
                            "PASS",
                            f"Converted €{conversion_data['amount']} to ${conversion.get('converted_amount', 0)} (Rate: {conversion.get('exchange_rate', 0)})",
                            response_time
                        )
                    else:
                        self.log_test(
                            "Currency Conversion", 
                            "FAIL",
                            f"Missing conversion data in response",
                            response_time
                        )
                else:
                    self.log_test(
                        "Currency Conversion", 
                        "FAIL",
                        f"Currency conversion returned success=false: {data.get('error', 'Unknown error')}",
                        response_time
                    )
            else:
                self.log_test(
                    "Currency Conversion", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("Multi-Currency System", "FAIL", f"Exception: {str(e)}")

    def test_escrow_system(self):
        """Test Escrow system"""
        try:
            print("🔒 Testing Phase 5B - Escrow System...")
            
            # Test escrow creation endpoint
            start_time = time.time()
            escrow_data = {
                "buyer_id": "test_buyer_123",
                "seller_id": "test_seller_456",
                "listing_id": "test_listing_789",
                "amount": 250.00,
                "currency": "EUR",
                "payment_method": "bank_transfer"
            }
            response = self.session.post(f"{self.backend_url}/v2/escrow/create", json=escrow_data)
            response_time = (time.time() - start_time) * 1000
            
            escrow_id = None
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    escrow_id = data.get("escrow_id")
                    
                    if escrow_id:
                        self.log_test(
                            "Escrow Creation", 
                            "PASS",
                            f"Escrow created successfully - ID: {escrow_id}, Amount: €{escrow_data['amount']}",
                            response_time
                        )
                    else:
                        self.log_test(
                            "Escrow Creation", 
                            "FAIL",
                            f"No escrow ID returned in response",
                            response_time
                        )
                else:
                    self.log_test(
                        "Escrow Creation", 
                        "FAIL",
                        f"Escrow creation failed: {data.get('error', 'Unknown error')}",
                        response_time
                    )
            else:
                self.log_test(
                    "Escrow Creation", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
            
            # Test escrow funding (if escrow was created)
            if escrow_id:
                start_time = time.time()
                funding_data = {
                    "payment_reference": f"PAY-{escrow_id[:8]}",
                    "amount": escrow_data["amount"]
                }
                response = self.session.post(f"{self.backend_url}/v2/escrow/{escrow_id}/fund", json=funding_data)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        self.log_test(
                            "Escrow Funding", 
                            "PASS",
                            f"Escrow funded successfully - Reference: {funding_data['payment_reference']}",
                            response_time
                        )
                    else:
                        self.log_test(
                            "Escrow Funding", 
                            "FAIL",
                            f"Escrow funding failed: {data.get('error', 'Unknown error')}",
                            response_time
                        )
                else:
                    self.log_test(
                        "Escrow Funding", 
                        "FAIL",
                        f"HTTP {response.status_code}: {response.text}",
                        response_time
                    )
                
                # Test escrow status management
                start_time = time.time()
                response = self.session.get(f"{self.backend_url}/v2/escrow/{escrow_id}")
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        escrow_details = data.get("escrow", {})
                        
                        if "status" in escrow_details and "amount" in escrow_details:
                            self.log_test(
                                "Escrow Status Management", 
                                "PASS",
                                f"Escrow details retrieved - Status: {escrow_details.get('status')}, Amount: €{escrow_details.get('amount')}",
                                response_time
                            )
                        else:
                            self.log_test(
                                "Escrow Status Management", 
                                "FAIL",
                                f"Missing escrow details in response",
                                response_time
                            )
                    else:
                        self.log_test(
                            "Escrow Status Management", 
                            "FAIL",
                            f"Escrow status retrieval failed: {data.get('error', 'Unknown error')}",
                            response_time
                        )
                else:
                    self.log_test(
                        "Escrow Status Management", 
                        "FAIL",
                        f"HTTP {response.status_code}: {response.text}",
                        response_time
                    )
                
        except Exception as e:
            self.log_test("Escrow System", "FAIL", f"Exception: {str(e)}")

    def test_ai_recommendations(self):
        """Test AI Recommendations"""
        try:
            print("🤖 Testing Phase 5C - AI Recommendations...")
            
            # Test user interaction tracking
            start_time = time.time()
            interaction_data = {
                "user_id": "test_user_123",
                "listing_id": "test_listing_789",
                "interaction_type": "view",
                "context": {
                    "page": "listing_detail",
                    "duration": 45,
                    "source": "search_results"
                }
            }
            response = self.session.post(f"{self.backend_url}/v2/ai/interaction", json=interaction_data)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test(
                        "User Interaction Tracking", 
                        "PASS",
                        f"Interaction tracked - User: {interaction_data['user_id']}, Type: {interaction_data['interaction_type']}, Duration: {interaction_data['context']['duration']}s",
                        response_time
                    )
                else:
                    self.log_test(
                        "User Interaction Tracking", 
                        "FAIL",
                        f"Interaction tracking failed: {data.get('error', 'Unknown error')}",
                        response_time
                    )
            else:
                self.log_test(
                    "User Interaction Tracking", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
            
            # Test personalized recommendations
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/v2/ai/recommendations/test_user_123?limit=10")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    recommendations = data.get("recommendations", [])
                    
                    if len(recommendations) > 0:
                        self.log_test(
                            "Personalized Recommendations", 
                            "PASS",
                            f"Generated {len(recommendations)} personalized recommendations for user",
                            response_time
                        )
                    else:
                        self.log_test(
                            "Personalized Recommendations", 
                            "WARN",
                            f"No recommendations generated (may be expected for new user)",
                            response_time
                        )
                else:
                    self.log_test(
                        "Personalized Recommendations", 
                        "FAIL",
                        f"Recommendations failed: {data.get('error', 'Unknown error')}",
                        response_time
                    )
            else:
                self.log_test(
                    "Personalized Recommendations", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
            
            # Test similar items recommendations
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/v2/ai/similar/test_listing_789?limit=5")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    similar_items = data.get("similar_items", [])
                    
                    self.log_test(
                        "Similar Items Recommendations", 
                        "PASS",
                        f"Found {len(similar_items)} similar items for listing",
                        response_time
                    )
                else:
                    self.log_test(
                        "Similar Items Recommendations", 
                        "FAIL",
                        f"Similar items failed: {data.get('error', 'Unknown error')}",
                        response_time
                    )
            else:
                self.log_test(
                    "Similar Items Recommendations", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
            
            # Test trending items
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/v2/ai/trending?limit=10")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    trending_items = data.get("trending_items", [])
                    
                    self.log_test(
                        "Trending Items", 
                        "PASS",
                        f"Retrieved {len(trending_items)} trending items based on AI analysis",
                        response_time
                    )
                else:
                    self.log_test(
                        "Trending Items", 
                        "FAIL",
                        f"Trending items failed: {data.get('error', 'Unknown error')}",
                        response_time
                    )
            else:
                self.log_test(
                    "Trending Items", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("AI Recommendations", "FAIL", f"Exception: {str(e)}")

    def test_phase5_status_endpoint(self):
        """Test Phase 5 comprehensive status endpoint"""
        try:
            print("📊 Testing Phase 5 Status Endpoint...")
            
            # Test comprehensive Phase 5 status
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/v2/status")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    
                    # Verify Phase 5 services status
                    required_services = ["websocket", "multicurrency", "escrow", "ai_recommendations"]
                    services_status = data.get("services", {})
                    
                    operational_services = []
                    failed_services = []
                    
                    for service in required_services:
                        service_data = services_status.get(service, {})
                        if service_data.get("status") == "operational":
                            operational_services.append(service)
                        else:
                            failed_services.append(service)
                    
                    if len(operational_services) == len(required_services):
                        self.log_test(
                            "Phase 5 Status Endpoint", 
                            "PASS",
                            f"All Phase 5 services operational: {', '.join(operational_services)}",
                            response_time
                        )
                    else:
                        self.log_test(
                            "Phase 5 Status Endpoint", 
                            "FAIL",
                            f"Services not operational: {', '.join(failed_services)}. Operational: {', '.join(operational_services)}",
                            response_time
                        )
                else:
                    self.log_test(
                        "Phase 5 Status Endpoint", 
                        "FAIL",
                        f"Status endpoint returned success=false: {data.get('error', 'Unknown error')}",
                        response_time
                    )
            else:
                self.log_test(
                    "Phase 5 Status Endpoint", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("Phase 5 Status Endpoint", "FAIL", f"Exception: {str(e)}")

    def test_data_flows(self):
        """Test that data flows properly between services"""
        try:
            print("🔄 Testing Data Flows Between Services...")
            
            # Test that services are integrated correctly
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/admin/performance")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                phase5_services = data.get("phase5_services", {})
                
                if phase5_services:
                    enabled_services = [k for k, v in phase5_services.items() if v == "enabled"]
                    if len(enabled_services) >= 4:  # All 4 Phase 5 services
                        self.log_test(
                            "Service Integration", 
                            "PASS",
                            f"Phase 5 services integrated in performance monitoring: {', '.join(enabled_services)}",
                            response_time
                        )
                    else:
                        self.log_test(
                            "Service Integration", 
                            "FAIL",
                            f"Not all Phase 5 services integrated. Found: {', '.join(enabled_services)}",
                            response_time
                        )
                else:
                    self.log_test(
                        "Service Integration", 
                        "FAIL",
                        f"Phase 5 services not found in performance endpoint",
                        response_time
                    )
            else:
                self.log_test(
                    "Service Integration", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("Data Flows", "FAIL", f"Exception: {str(e)}")

    def test_error_handling(self):
        """Test error handling works as expected"""
        try:
            print("⚠️ Testing Error Handling...")
            
            # Test invalid currency conversion
            start_time = time.time()
            invalid_conversion = {
                "amount": -100.0,  # Invalid negative amount
                "from_currency": "INVALID",
                "to_currency": "USD"
            }
            response = self.session.post(f"{self.backend_url}/v2/currency/convert", json=invalid_conversion)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code in [400, 422]:  # Expected error codes
                self.log_test(
                    "Currency Conversion Error Handling", 
                    "PASS",
                    f"Properly rejected invalid conversion request (HTTP {response.status_code})",
                    response_time
                )
            elif response.status_code == 200:
                data = response.json()
                if not data.get("success"):
                    self.log_test(
                        "Currency Conversion Error Handling", 
                        "PASS",
                        f"Properly returned error in response: {data.get('error', 'Unknown error')}",
                        response_time
                    )
                else:
                    self.log_test(
                        "Currency Conversion Error Handling", 
                        "FAIL",
                        f"Accepted invalid conversion request",
                        response_time
                    )
            else:
                self.log_test(
                    "Currency Conversion Error Handling", 
                    "WARN",
                    f"Unexpected response code: {response.status_code}",
                    response_time
                )
            
            # Test invalid escrow creation
            start_time = time.time()
            invalid_escrow = {
                "amount": -50.0,  # Invalid negative amount
                "currency": "INVALID"
            }
            response = self.session.post(f"{self.backend_url}/v2/escrow/create", json=invalid_escrow)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code in [400, 422]:  # Expected error codes
                self.log_test(
                    "Escrow Creation Error Handling", 
                    "PASS",
                    f"Properly rejected invalid escrow request (HTTP {response.status_code})",
                    response_time
                )
            elif response.status_code == 200:
                data = response.json()
                if not data.get("success"):
                    self.log_test(
                        "Escrow Creation Error Handling", 
                        "PASS",
                        f"Properly returned error in response: {data.get('error', 'Unknown error')}",
                        response_time
                    )
                else:
                    self.log_test(
                        "Escrow Creation Error Handling", 
                        "FAIL",
                        f"Accepted invalid escrow request",
                        response_time
                    )
            else:
                self.log_test(
                    "Escrow Creation Error Handling", 
                    "WARN",
                    f"Unexpected response code: {response.status_code}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("Error Handling", "FAIL", f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all Phase 5 backend tests"""
        print("🚀 PHASE 5 BACKEND TESTING - Advanced Marketplace Features")
        print("=" * 80)
        print("Testing Phase 5 services as requested in review:")
        print("1. Real-time WebSocket services")
        print("2. Multi-currency system") 
        print("3. Escrow system")
        print("4. AI Recommendations")
        print("5. Phase 5 status endpoint")
        print("=" * 80)
        print()
        
        # Admin authentication
        if not self.admin_login():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Run Phase 5 tests as requested in review
        print("🔄 PHASE 5A - REAL-TIME WEBSOCKET SERVICES")
        print("-" * 50)
        self.test_websocket_services()
        
        print("💱 PHASE 5B - MULTI-CURRENCY SYSTEM")
        print("-" * 50)
        self.test_multicurrency_system()
        
        print("🔒 PHASE 5B - ESCROW SYSTEM")
        print("-" * 50)
        self.test_escrow_system()
        
        print("🤖 PHASE 5C - AI RECOMMENDATIONS")
        print("-" * 50)
        self.test_ai_recommendations()
        
        print("📊 PHASE 5 STATUS ENDPOINT")
        print("-" * 50)
        self.test_phase5_status_endpoint()
        
        print("🔄 DATA FLOWS & INTEGRATION")
        print("-" * 50)
        self.test_data_flows()
        
        print("⚠️ ERROR HANDLING")
        print("-" * 50)
        self.test_error_handling()
        
        # Summary
        print("=" * 80)
        print("📊 PHASE 5 BACKEND TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warning_tests = len([r for r in self.test_results if r["status"] == "WARN"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Warnings: {warning_tests} ⚠️")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        if warning_tests > 0:
            print("⚠️ WARNING TESTS:")
            for result in self.test_results:
                if result["status"] == "WARN":
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        # Phase 5 Feature Summary
        print("🎯 PHASE 5 FEATURES TESTED (as requested in review):")
        print("   1. Real-time WebSocket Services:")
        print("     • WebSocket connection statistics and tracking")
        print("     • Real-time notification broadcasting")
        print("   2. Multi-Currency System:")
        print("     • Supported currencies endpoint")
        print("     • Exchange rates retrieval")
        print("     • Currency conversion functionality")
        print("   3. Escrow System:")
        print("     • Escrow creation and funding")
        print("     • Status management")
        print("   4. AI Recommendations:")
        print("     • User interaction tracking")
        print("     • Personalized recommendations")
        print("     • Similar items and trending analysis")
        print("   5. Phase 5 Status Endpoint:")
        print("     • Comprehensive service status monitoring")
        print("   6. Integration & Error Handling:")
        print("     • Data flows between services")
        print("     • Proper error handling")
        print()
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = Phase5BackendTest()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL PHASE 5 BACKEND TESTS PASSED!")
        print("✨ Advanced marketplace features are fully operational!")
        sys.exit(0)
    else:
        print("💥 SOME PHASE 5 TESTS FAILED!")
        print("🔧 Phase 5 services may need implementation or configuration.")
        sys.exit(1)