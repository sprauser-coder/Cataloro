#!/usr/bin/env python3
"""
PHASE 4 BUSINESS INTELLIGENCE & ANALYTICS TESTING
Comprehensive testing of the newly implemented analytics features in Cataloro Marketplace backend
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BACKEND_URL = "https://inventory-fix-1.preview.emergentagent.com/api"

class Phase4AnalyticsTest:
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
        """Login as admin user for analytics access"""
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

    def test_user_analytics(self):
        """Test User Analytics Endpoint"""
        try:
            print("🔍 Testing User Analytics Endpoints...")
            
            # Test default 30 days
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/admin/analytics/users")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                analytics = data.get("analytics", {})
                
                # Verify structure
                required_sections = ["period", "user_registrations", "user_activity", "engagement_metrics", "summary"]
                missing_sections = [section for section in required_sections if section not in analytics]
                
                if not missing_sections:
                    summary = analytics.get("summary", {})
                    self.log_test(
                        "User Analytics (30 days)", 
                        "PASS",
                        f"Complete analytics structure - Total Users: {summary.get('total_users', 0)}, Active Users: {summary.get('active_users', 0)}, Growth Rate: {summary.get('user_growth_rate', 0)}%",
                        response_time
                    )
                else:
                    self.log_test(
                        "User Analytics (30 days)", 
                        "FAIL",
                        f"Missing sections: {missing_sections}",
                        response_time
                    )
            else:
                self.log_test(
                    "User Analytics (30 days)", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
            
            # Test custom period (7 days)
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/admin/analytics/users?days=7")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                analytics = data.get("analytics", {})
                period = analytics.get("period", {})
                
                if period.get("days") == 7:
                    self.log_test(
                        "User Analytics (7 days)", 
                        "PASS",
                        f"Custom period working - Period: {period.get('days')} days",
                        response_time
                    )
                else:
                    self.log_test(
                        "User Analytics (7 days)", 
                        "FAIL",
                        f"Period mismatch - Expected: 7, Got: {period.get('days')}",
                        response_time
                    )
            else:
                self.log_test(
                    "User Analytics (7 days)", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("User Analytics", "FAIL", f"Exception: {str(e)}")

    def test_sales_analytics(self):
        """Test Sales Analytics Endpoint"""
        try:
            print("💰 Testing Sales Analytics Endpoints...")
            
            # Test default 30 days
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/admin/analytics/sales")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                analytics = data.get("analytics", {})
                
                # Verify structure
                required_sections = ["period", "revenue", "transactions", "summary"]
                missing_sections = [section for section in required_sections if section not in analytics]
                
                if not missing_sections:
                    summary = analytics.get("summary", {})
                    self.log_test(
                        "Sales Analytics (30 days)", 
                        "PASS",
                        f"Complete sales structure - Revenue: €{summary.get('total_revenue', 0)}, Transactions: {summary.get('total_transactions', 0)}, Avg Value: €{summary.get('avg_transaction_value', 0)}",
                        response_time
                    )
                else:
                    self.log_test(
                        "Sales Analytics (30 days)", 
                        "FAIL",
                        f"Missing sections: {missing_sections}",
                        response_time
                    )
            else:
                self.log_test(
                    "Sales Analytics (30 days)", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
            
            # Test custom period (14 days)
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/admin/analytics/sales?days=14")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                analytics = data.get("analytics", {})
                period = analytics.get("period", {})
                
                if period.get("days") == 14:
                    self.log_test(
                        "Sales Analytics (14 days)", 
                        "PASS",
                        f"Custom period working - Period: {period.get('days')} days",
                        response_time
                    )
                else:
                    self.log_test(
                        "Sales Analytics (14 days)", 
                        "FAIL",
                        f"Period mismatch - Expected: 14, Got: {period.get('days')}",
                        response_time
                    )
            else:
                self.log_test(
                    "Sales Analytics (14 days)", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("Sales Analytics", "FAIL", f"Exception: {str(e)}")

    def test_marketplace_analytics(self):
        """Test Marketplace Analytics Endpoint"""
        try:
            print("🏪 Testing Marketplace Analytics Endpoints...")
            
            # Test default 30 days
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/admin/analytics/marketplace")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                analytics = data.get("analytics", {})
                
                # Verify structure
                required_sections = ["period", "listings", "categories", "platform_health", "summary"]
                missing_sections = [section for section in required_sections if section not in analytics]
                
                if not missing_sections:
                    summary = analytics.get("summary", {})
                    self.log_test(
                        "Marketplace Analytics (30 days)", 
                        "PASS",
                        f"Complete marketplace structure - Active Listings: {summary.get('total_active_listings', 0)}, New Listings: {summary.get('new_listings', 0)}, Success Rate: {summary.get('listing_success_rate', 0)}%",
                        response_time
                    )
                else:
                    self.log_test(
                        "Marketplace Analytics (30 days)", 
                        "FAIL",
                        f"Missing sections: {missing_sections}",
                        response_time
                    )
            else:
                self.log_test(
                    "Marketplace Analytics (30 days)", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
            
            # Test extended period (60 days)
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/admin/analytics/marketplace?days=60")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                analytics = data.get("analytics", {})
                period = analytics.get("period", {})
                
                if period.get("days") == 60:
                    self.log_test(
                        "Marketplace Analytics (60 days)", 
                        "PASS",
                        f"Extended period working - Period: {period.get('days')} days",
                        response_time
                    )
                else:
                    self.log_test(
                        "Marketplace Analytics (60 days)", 
                        "FAIL",
                        f"Period mismatch - Expected: 60, Got: {period.get('days')}",
                        response_time
                    )
            else:
                self.log_test(
                    "Marketplace Analytics (60 days)", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("Marketplace Analytics", "FAIL", f"Exception: {str(e)}")

    def test_business_intelligence_reporting(self):
        """Test Business Intelligence Reporting"""
        try:
            print("📊 Testing Business Intelligence Reporting...")
            
            # Test comprehensive report
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/admin/analytics/business-report")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                report = data.get("report", {})
                
                # Verify structure
                required_sections = ["executive_summary", "detailed_analytics", "recommendations", "key_insights", "health_scores"]
                missing_sections = [section for section in required_sections if section not in report]
                
                if not missing_sections:
                    exec_summary = report.get("executive_summary", {})
                    insights_count = len(report.get("key_insights", []))
                    recommendations_count = len(report.get("recommendations", []))
                    
                    self.log_test(
                        "Business Intelligence Report", 
                        "PASS",
                        f"Complete BI report - Users: {exec_summary.get('total_users', 0)}, Revenue: €{exec_summary.get('total_revenue', 0)}, Insights: {insights_count}, Recommendations: {recommendations_count}",
                        response_time
                    )
                else:
                    self.log_test(
                        "Business Intelligence Report", 
                        "FAIL",
                        f"Missing sections: {missing_sections}",
                        response_time
                    )
            else:
                self.log_test(
                    "Business Intelligence Report", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
            
            # Test summary report with custom period
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/admin/analytics/business-report?report_type=summary&days=14")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                report = data.get("report", {})
                
                if report.get("report_type") == "summary" and report.get("period_days") == 14:
                    self.log_test(
                        "Business Report (Summary, 14 days)", 
                        "PASS",
                        f"Custom report working - Type: {report.get('report_type')}, Period: {report.get('period_days')} days",
                        response_time
                    )
                else:
                    self.log_test(
                        "Business Report (Summary, 14 days)", 
                        "FAIL",
                        f"Configuration mismatch - Type: {report.get('report_type')}, Period: {report.get('period_days')}",
                        response_time
                    )
            else:
                self.log_test(
                    "Business Report (Summary, 14 days)", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("Business Intelligence Reporting", "FAIL", f"Exception: {str(e)}")

    def test_predictive_analytics(self):
        """Test Predictive Analytics"""
        try:
            print("🔮 Testing Predictive Analytics...")
            
            # Test 30-day forecast
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/admin/analytics/predictive")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                predictions = data.get("predictions", {})
                
                # Verify structure
                required_sections = ["revenue_forecast", "user_growth_forecast", "listing_volume_forecast", "confidence_intervals"]
                missing_sections = [section for section in required_sections if section not in predictions]
                
                if not missing_sections:
                    revenue_forecast = predictions.get("revenue_forecast", {})
                    user_forecast = predictions.get("user_growth_forecast", {})
                    confidence = predictions.get("confidence_intervals", {})
                    
                    self.log_test(
                        "Predictive Analytics (30 days)", 
                        "PASS",
                        f"Complete forecasts - Revenue: €{revenue_forecast.get('forecast', 0)}, Users: {user_forecast.get('forecast', 0)}, Revenue Confidence: {confidence.get('revenue', 0)}",
                        response_time
                    )
                else:
                    self.log_test(
                        "Predictive Analytics (30 days)", 
                        "FAIL",
                        f"Missing sections: {missing_sections}",
                        response_time
                    )
            else:
                self.log_test(
                    "Predictive Analytics (30 days)", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
            
            # Test 60-day forecast
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/admin/analytics/predictive?forecast_days=60")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                predictions = data.get("predictions", {})
                
                if predictions.get("forecast_period_days") == 60:
                    self.log_test(
                        "Predictive Analytics (60 days)", 
                        "PASS",
                        f"Extended forecast working - Period: {predictions.get('forecast_period_days')} days",
                        response_time
                    )
                else:
                    self.log_test(
                        "Predictive Analytics (60 days)", 
                        "FAIL",
                        f"Period mismatch - Expected: 60, Got: {predictions.get('forecast_period_days')}",
                        response_time
                    )
            else:
                self.log_test(
                    "Predictive Analytics (60 days)", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("Predictive Analytics", "FAIL", f"Exception: {str(e)}")

    def test_analytics_dashboard(self):
        """Test Analytics Dashboard"""
        try:
            print("📈 Testing Analytics Dashboard...")
            
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/admin/analytics/dashboard")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify structure
                required_sections = ["overview", "trends", "forecasts", "charts_data", "performance_indicators"]
                missing_sections = [section for section in required_sections if section not in data]
                
                if not missing_sections:
                    overview = data.get("overview", {})
                    trends = data.get("trends", {})
                    forecasts = data.get("forecasts", {})
                    
                    self.log_test(
                        "Analytics Dashboard", 
                        "PASS",
                        f"Complete dashboard - Users: {overview.get('total_users', 0)}, Revenue: €{overview.get('total_revenue', 0)}, Growth Rate: {trends.get('user_growth_rate', 0)}%, Forecasts Available: {len(forecasts)}",
                        response_time
                    )
                else:
                    self.log_test(
                        "Analytics Dashboard", 
                        "FAIL",
                        f"Missing sections: {missing_sections}",
                        response_time
                    )
            else:
                self.log_test(
                    "Analytics Dashboard", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("Analytics Dashboard", "FAIL", f"Exception: {str(e)}")

    def test_key_performance_indicators(self):
        """Test Key Performance Indicators"""
        try:
            print("📊 Testing Key Performance Indicators...")
            
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/admin/analytics/kpis")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify structure
                required_sections = ["business_metrics", "growth_indicators", "health_scores", "recommendations", "overall_health_score"]
                missing_sections = [section for section in required_sections if section not in data]
                
                if not missing_sections:
                    business_metrics = data.get("business_metrics", {})
                    health_scores = data.get("health_scores", {})
                    recommendations = data.get("recommendations", [])
                    overall_health = data.get("overall_health_score", 0)
                    
                    self.log_test(
                        "Key Performance Indicators", 
                        "PASS",
                        f"Complete KPIs - Users: {business_metrics.get('total_users', 0)}, Revenue: €{business_metrics.get('total_revenue', 0)}, Overall Health: {overall_health}%, Recommendations: {len(recommendations)}",
                        response_time
                    )
                else:
                    self.log_test(
                        "Key Performance Indicators", 
                        "FAIL",
                        f"Missing sections: {missing_sections}",
                        response_time
                    )
            else:
                self.log_test(
                    "Key Performance Indicators", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("Key Performance Indicators", "FAIL", f"Exception: {str(e)}")

    def test_custom_report_generation(self):
        """Test Custom Report Generation"""
        try:
            print("📋 Testing Custom Report Generation...")
            
            # Test custom report with different configuration
            report_config = {
                "type": "comprehensive",
                "days": 30,
                "include_predictions": True
            }
            
            start_time = time.time()
            response = self.session.post(f"{self.backend_url}/admin/analytics/reports/generate", json=report_config)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                report = data.get("report", {})
                
                # Verify structure
                required_sections = ["executive_summary", "detailed_analytics", "predictions", "report_config"]
                missing_sections = [section for section in required_sections if section not in report]
                
                if not missing_sections:
                    config = report.get("report_config", {})
                    predictions = report.get("predictions", {})
                    
                    self.log_test(
                        "Custom Report Generation", 
                        "PASS",
                        f"Custom report generated - Type: {config.get('type')}, Days: {config.get('days')}, Predictions: {'Yes' if predictions else 'No'}",
                        response_time
                    )
                else:
                    self.log_test(
                        "Custom Report Generation", 
                        "FAIL",
                        f"Missing sections: {missing_sections}",
                        response_time
                    )
            else:
                self.log_test(
                    "Custom Report Generation", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("Custom Report Generation", "FAIL", f"Exception: {str(e)}")

    def test_performance_integration(self):
        """Test Performance Integration with Analytics"""
        try:
            print("⚡ Testing Performance Integration...")
            
            start_time = time.time()
            response = self.session.get(f"{self.backend_url}/admin/performance")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if analytics service status is included
                analytics_section = data.get("analytics", {})
                
                if analytics_section:
                    service_enabled = analytics_section.get("service_enabled", False)
                    business_intelligence = analytics_section.get("business_intelligence", "")
                    
                    self.log_test(
                        "Performance Analytics Integration", 
                        "PASS",
                        f"Analytics integration verified - Service Enabled: {service_enabled}, BI Status: {business_intelligence}",
                        response_time
                    )
                else:
                    self.log_test(
                        "Performance Analytics Integration", 
                        "FAIL",
                        "Analytics section not found in performance endpoint",
                        response_time
                    )
            else:
                self.log_test(
                    "Performance Analytics Integration", 
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("Performance Integration", "FAIL", f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all Phase 4 analytics tests"""
        print("🚀 PHASE 4 BUSINESS INTELLIGENCE & ANALYTICS TESTING")
        print("=" * 70)
        print()
        
        # Admin authentication
        if not self.admin_login():
            print("❌ Cannot proceed without admin authentication")
            return False
        
        # Run all analytics tests
        self.test_user_analytics()
        self.test_sales_analytics()
        self.test_marketplace_analytics()
        self.test_business_intelligence_reporting()
        self.test_predictive_analytics()
        self.test_analytics_dashboard()
        self.test_key_performance_indicators()
        self.test_custom_report_generation()
        self.test_performance_integration()
        
        # Summary
        print("=" * 70)
        print("📊 PHASE 4 ANALYTICS TESTING SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        # Test specific analytics data quality
        print("📈 ANALYTICS DATA QUALITY VERIFICATION:")
        print("   • User Analytics: Registration, Activity, Engagement metrics")
        print("   • Sales Analytics: Revenue, Transaction, Performance data")
        print("   • Marketplace Analytics: Listing, Category, Platform health")
        print("   • Business Reports: Executive summary, Insights, Recommendations")
        print("   • Predictive Analytics: Revenue, User growth, Listing forecasts")
        print("   • Dashboard: Overview metrics, Trends, Chart data")
        print("   • KPIs: Business metrics, Health scores, Recommendations")
        print()
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = Phase4AnalyticsTest()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL PHASE 4 BUSINESS INTELLIGENCE & ANALYTICS TESTS PASSED!")
        sys.exit(0)
    else:
        print("💥 SOME PHASE 4 ANALYTICS TESTS FAILED!")
        sys.exit(1)