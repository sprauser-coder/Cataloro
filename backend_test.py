#!/usr/bin/env python3
"""
Cataloro Marketplace - Consolidated Backend Services Testing
Tests the newly consolidated Phase 1-6 backend services with focus on:
1. Unified Analytics Service (consolidated analytics + advanced analytics)
2. Unified Security Service (consolidated security + enterprise security)  
3. Advanced Features Status (consolidated endpoints)
4. Currency & Escrow (Phase 5 services)
5. AI & Chatbot (Phase 6 services)
"""

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://mega-dashboard.preview.emergentagent.com/api"

class ConsolidatedBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.failed_tests = []
        
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
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
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
                async with self.session.post(url, json=data, params=params) as response:
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
    
    # ==== UNIFIED ANALYTICS SERVICE TESTS ====
    
    async def test_unified_analytics_dashboard(self):
        """Test unified analytics dashboard (HIGH PRIORITY)"""
        response = await self.make_request("GET", "/v2/advanced/analytics/dashboard")
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "dashboard_data" in data:
                dashboard = data["dashboard_data"]
                overview = dashboard.get("overview", {})
                
                # Verify real data structure
                users = overview.get("total_users", 0)
                revenue = overview.get("total_revenue", 0)
                listings = overview.get("active_listings", 0)
                
                self.log_test(
                    "Unified Analytics Dashboard",
                    True,
                    f"Dashboard loaded with Users: {users}, Revenue: €{revenue}, Listings: {listings}",
                    dashboard
                )
            else:
                self.log_test("Unified Analytics Dashboard", False, "Invalid dashboard data structure", data)
        else:
            self.log_test("Unified Analytics Dashboard", False, f"Request failed: {response['status']}", response["data"])
    
    async def test_user_analytics_real_data(self):
        """Test user analytics with real data (HIGH PRIORITY)"""
        response = await self.make_request("GET", "/v2/advanced/analytics/user", params={"days": 30})
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "analytics" in data:
                analytics = data["analytics"]
                summary = analytics.get("summary", {})
                
                total_users = summary.get("total_users", 0)
                new_users = summary.get("new_users", 0)
                growth_rate = summary.get("user_growth_rate", 0)
                
                self.log_test(
                    "User Analytics (Real Data)",
                    True,
                    f"Total Users: {total_users}, New Users (30d): {new_users}, Growth: {growth_rate}%",
                    analytics
                )
            else:
                self.log_test("User Analytics (Real Data)", False, "Invalid analytics data", data)
        else:
            self.log_test("User Analytics (Real Data)", False, f"Request failed: {response['status']}", response["data"])
    
    async def test_sales_analytics_real_data(self):
        """Test sales analytics with real data (HIGH PRIORITY)"""
        response = await self.make_request("GET", "/v2/advanced/analytics/sales", params={"days": 30})
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "analytics" in data:
                analytics = data["analytics"]
                summary = analytics.get("summary", {})
                
                revenue = summary.get("total_revenue", 0)
                transactions = summary.get("total_transactions", 0)
                avg_value = summary.get("avg_transaction_value", 0)
                
                self.log_test(
                    "Sales Analytics (Real Data)",
                    True,
                    f"Revenue: €{revenue}, Transactions: {transactions}, Avg Value: €{avg_value}",
                    analytics
                )
            else:
                self.log_test("Sales Analytics (Real Data)", False, "Invalid sales analytics data", data)
        else:
            self.log_test("Sales Analytics (Real Data)", False, f"Request failed: {response['status']}", response["data"])
    
    async def test_marketplace_analytics_real_data(self):
        """Test marketplace analytics with real data (HIGH PRIORITY)"""
        response = await self.make_request("GET", "/v2/advanced/analytics/marketplace", params={"days": 30})
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "analytics" in data:
                analytics = data["analytics"]
                summary = analytics.get("summary", {})
                
                active_listings = summary.get("total_active_listings", 0)
                new_listings = summary.get("new_listings", 0)
                success_rate = summary.get("listing_success_rate", 0)
                
                self.log_test(
                    "Marketplace Analytics (Real Data)",
                    True,
                    f"Active Listings: {active_listings}, New: {new_listings}, Success Rate: {success_rate}%",
                    analytics
                )
            else:
                self.log_test("Marketplace Analytics (Real Data)", False, "Invalid marketplace analytics", data)
        else:
            self.log_test("Marketplace Analytics (Real Data)", False, f"Request failed: {response['status']}", response["data"])
    
    async def test_predictive_analytics(self):
        """Test predictive analytics (MEDIUM PRIORITY)"""
        response = await self.make_request("GET", "/v2/advanced/analytics/predictive", params={"forecast_days": 30})
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "predictions" in data:
                predictions = data["predictions"]
                
                revenue_forecast = predictions.get("revenue_forecast", {})
                user_forecast = predictions.get("user_growth_forecast", {})
                
                self.log_test(
                    "Predictive Analytics",
                    True,
                    f"Revenue Forecast: {revenue_forecast.get('forecast', 0)}, User Growth: {user_forecast.get('forecast', 0)}",
                    predictions
                )
            else:
                self.log_test("Predictive Analytics", False, "Invalid predictions data", data)
        else:
            self.log_test("Predictive Analytics", False, f"Request failed: {response['status']}", response["data"])
    
    async def test_market_trends_analysis(self):
        """Test market trends with real data (MEDIUM PRIORITY)"""
        response = await self.make_request("GET", "/v2/advanced/analytics/market-trends", params={"time_period": "30d"})
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "trends" in data:
                trends = data["trends"]
                
                if trends:
                    trend_count = len(trends)
                    top_trend = trends[0] if trends else {}
                    
                    self.log_test(
                        "Market Trends Analysis",
                        True,
                        f"Found {trend_count} trends, Top: {top_trend.get('category', 'N/A')} ({top_trend.get('trend_direction', 'N/A')})",
                        trends[:3]  # Show top 3 trends
                    )
                else:
                    self.log_test("Market Trends Analysis", True, "No trends found (empty database)", trends)
            else:
                self.log_test("Market Trends Analysis", False, "Invalid trends data", data)
        else:
            self.log_test("Market Trends Analysis", False, f"Request failed: {response['status']}", response["data"])
    
    async def test_seller_performance_forecasting(self):
        """Test seller performance forecasting (MEDIUM PRIORITY)"""
        response = await self.make_request("GET", "/v2/advanced/analytics/seller-performance")
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "seller_performance" in data:
                performance = data["seller_performance"]
                
                if performance:
                    seller_count = len(performance)
                    top_seller = performance[0] if performance else {}
                    
                    self.log_test(
                        "Seller Performance Forecasting",
                        True,
                        f"Analyzed {seller_count} sellers, Top: {top_seller.get('seller_name', 'N/A')} (Rating: {top_seller.get('current_rating', 0)})",
                        performance[:2]  # Show top 2 sellers
                    )
                else:
                    self.log_test("Seller Performance Forecasting", True, "No sellers found (empty database)", performance)
            else:
                self.log_test("Seller Performance Forecasting", False, "Invalid performance data", data)
        else:
            self.log_test("Seller Performance Forecasting", False, f"Request failed: {response['status']}", response["data"])
    
    # ==== UNIFIED SECURITY SERVICE TESTS ====
    
    async def test_security_dashboard(self):
        """Test unified security dashboard (HIGH PRIORITY)"""
        response = await self.make_request("GET", "/v2/advanced/security/dashboard")
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "security_data" in data:
                security_data = data["security_data"]
                
                total_events = security_data.get("total_events", 0)
                critical_events = security_data.get("critical_events", 0)
                security_score = security_data.get("security_score", 0)
                
                self.log_test(
                    "Unified Security Dashboard",
                    True,
                    f"Events: {total_events}, Critical: {critical_events}, Score: {security_score}",
                    security_data
                )
            else:
                self.log_test("Unified Security Dashboard", False, "Invalid security data", data)
        else:
            self.log_test("Unified Security Dashboard", False, f"Request failed: {response['status']}", response["data"])
    
    async def test_security_event_logging(self):
        """Test security event logging (HIGH PRIORITY)"""
        event_data = {
            "event_type": "test_event",
            "severity": "medium",
            "user_id": "test_user_123",
            "ip_address": "192.168.1.100",
            "description": "Test security event for consolidation testing"
        }
        
        response = await self.make_request("POST", "/v2/advanced/security/log-event", data=event_data)
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "event_id" in data:
                event_id = data["event_id"]
                
                self.log_test(
                    "Security Event Logging",
                    True,
                    f"Event logged with ID: {event_id}",
                    data
                )
            else:
                self.log_test("Security Event Logging", False, "Invalid event logging response", data)
        else:
            self.log_test("Security Event Logging", False, f"Request failed: {response['status']}", response["data"])
    
    async def test_compliance_status(self):
        """Test compliance status (HIGH PRIORITY)"""
        response = await self.make_request("GET", "/v2/advanced/security/compliance")
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "compliance" in data:
                compliance = data["compliance"]
                
                total_checks = compliance.get("total_checks", 0)
                passing_checks = compliance.get("passing_checks", 0)
                compliance_score = compliance.get("compliance_score", 0)
                
                self.log_test(
                    "Compliance Status",
                    True,
                    f"Checks: {total_checks}, Passing: {passing_checks}, Score: {compliance_score}%",
                    compliance
                )
            else:
                self.log_test("Compliance Status", False, "Invalid compliance data", data)
        else:
            self.log_test("Compliance Status", False, f"Request failed: {response['status']}", response["data"])
    
    async def test_user_security_insights(self):
        """Test user security insights (HIGH PRIORITY)"""
        response = await self.make_request("GET", "/v2/advanced/security/user-insights", params={"limit": 10})
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "user_insights" in data:
                insights = data["user_insights"]
                
                if insights:
                    user_count = len(insights)
                    high_risk_users = len([u for u in insights if u.get("risk_score", 0) > 0.7])
                    
                    self.log_test(
                        "User Security Insights",
                        True,
                        f"Analyzed {user_count} users, High Risk: {high_risk_users}",
                        insights[:2]  # Show first 2 users
                    )
                else:
                    self.log_test("User Security Insights", True, "No user insights available", insights)
            else:
                self.log_test("User Security Insights", False, "Invalid insights data", data)
        else:
            self.log_test("User Security Insights", False, f"Request failed: {response['status']}", response["data"])
    
    # ==== ADVANCED FEATURES STATUS TESTS ====
    
    async def test_advanced_features_status(self):
        """Test consolidated services status (MEDIUM PRIORITY)"""
        response = await self.make_request("GET", "/v2/advanced/status")
        
        if response["success"]:
            data = response["data"]
            if "services" in data and "consolidation_info" in data:
                services = data["services"]
                consolidation = data["consolidation_info"]
                
                operational_services = [name for name, info in services.items() if info.get("status") == "operational"]
                
                self.log_test(
                    "Advanced Features Status",
                    True,
                    f"Operational Services: {len(operational_services)}/{len(services)}, Consolidated: {consolidation.get('dummy_data_removed', False)}",
                    {
                        "services": list(services.keys()),
                        "consolidation": consolidation
                    }
                )
            else:
                self.log_test("Advanced Features Status", False, "Invalid status data structure", data)
        else:
            self.log_test("Advanced Features Status", False, f"Request failed: {response['status']}", response["data"])
    
    # ==== CURRENCY & ESCROW TESTS ====
    
    async def test_supported_currencies(self):
        """Test currency support still works (MEDIUM PRIORITY)"""
        response = await self.make_request("GET", "/v2/advanced/currency/supported")
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "currencies" in data:
                currencies = data["currencies"]
                
                currency_count = len(currencies)
                currency_codes = [c.get("code", "N/A") for c in currencies[:5]]
                
                self.log_test(
                    "Supported Currencies",
                    True,
                    f"Found {currency_count} currencies: {', '.join(currency_codes)}",
                    currencies[:3]
                )
            else:
                self.log_test("Supported Currencies", False, "Invalid currencies data", data)
        else:
            self.log_test("Supported Currencies", False, f"Request failed: {response['status']}", response["data"])
    
    async def test_exchange_rates(self):
        """Test exchange rates still work (MEDIUM PRIORITY)"""
        response = await self.make_request("GET", "/v2/advanced/currency/rates")
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "rates" in data:
                rates = data["rates"]
                base_currency = data.get("base_currency", "EUR")
                
                rate_count = len(rates)
                sample_rates = list(rates.items())[:3]
                
                self.log_test(
                    "Exchange Rates",
                    True,
                    f"Base: {base_currency}, {rate_count} rates, Sample: {sample_rates}",
                    rates
                )
            else:
                self.log_test("Exchange Rates", False, "Invalid rates data", data)
        else:
            self.log_test("Exchange Rates", False, f"Request failed: {response['status']}", response["data"])
    
    async def test_currency_conversion(self):
        """Test currency conversion still works (MEDIUM PRIORITY)"""
        conversion_data = {
            "amount": 100,
            "from_currency": "EUR",
            "to_currency": "USD"
        }
        
        response = await self.make_request("POST", "/v2/advanced/currency/convert", data=conversion_data)
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "conversion" in data:
                conversion = data["conversion"]
                
                converted_amount = conversion.get("converted_amount", 0)
                exchange_rate = conversion.get("exchange_rate", 0)
                
                self.log_test(
                    "Currency Conversion",
                    True,
                    f"€100 → ${converted_amount} (Rate: {exchange_rate})",
                    conversion
                )
            else:
                self.log_test("Currency Conversion", False, "Invalid conversion data", data)
        else:
            self.log_test("Currency Conversion", False, f"Request failed: {response['status']}", response["data"])
    
    # ==== AI & CHATBOT TESTS ====
    
    async def test_ai_trending_items(self):
        """Test AI trending items (LOW PRIORITY)"""
        response = await self.make_request("GET", "/v2/advanced/ai/trending", params={"limit": 5})
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "trending_items" in data:
                trending = data["trending_items"]
                
                if trending:
                    item_count = len(trending)
                    top_item = trending[0] if trending else {}
                    
                    self.log_test(
                        "AI Trending Items",
                        True,
                        f"Found {item_count} trending items, Top: {top_item.get('title', 'N/A')}",
                        trending[:2]
                    )
                else:
                    self.log_test("AI Trending Items", True, "No trending items (empty database)", trending)
            else:
                self.log_test("AI Trending Items", False, "Invalid trending data", data)
        else:
            self.log_test("AI Trending Items", False, f"Request failed: {response['status']}", response["data"])
    
    async def test_chatbot_start_session(self):
        """Test chatbot session start (LOW PRIORITY)"""
        session_data = {
            "user_id": "test_user_123"
        }
        
        response = await self.make_request("POST", "/v2/advanced/chatbot/start-session", data=session_data)
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "session_id" in data:
                session_id = data["session_id"]
                
                self.log_test(
                    "Chatbot Start Session",
                    True,
                    f"Session started: {session_id}",
                    data
                )
                
                # Store session ID for potential follow-up tests
                self.chatbot_session_id = session_id
            else:
                self.log_test("Chatbot Start Session", False, "Invalid session data", data)
        else:
            self.log_test("Chatbot Start Session", False, f"Request failed: {response['status']}", response["data"])
    
    async def test_chatbot_analytics(self):
        """Test chatbot analytics (LOW PRIORITY)"""
        response = await self.make_request("GET", "/v2/advanced/chatbot/analytics")
        
        if response["success"]:
            data = response["data"]
            if data.get("success") and "analytics" in data:
                analytics = data["analytics"]
                
                total_sessions = analytics.get("total_sessions", 0)
                active_sessions = analytics.get("active_sessions", 0)
                
                self.log_test(
                    "Chatbot Analytics",
                    True,
                    f"Sessions: {total_sessions}, Active: {active_sessions}",
                    analytics
                )
            else:
                self.log_test("Chatbot Analytics", False, "Invalid analytics data", data)
        else:
            self.log_test("Chatbot Analytics", False, f"Request failed: {response['status']}", response["data"])
    
    # ==== MAIN TEST EXECUTION ====
    
    async def run_all_tests(self):
        """Run all consolidation tests"""
        print("🚀 Starting Cataloro Marketplace Consolidated Backend Testing...")
        print(f"📡 Testing against: {BACKEND_URL}")
        print("=" * 80)
        
        # HIGH PRIORITY TESTS - Unified Analytics
        print("\n🔍 HIGH PRIORITY: Unified Analytics Service Tests")
        await self.test_unified_analytics_dashboard()
        await self.test_user_analytics_real_data()
        await self.test_sales_analytics_real_data()
        await self.test_marketplace_analytics_real_data()
        
        # HIGH PRIORITY TESTS - Unified Security
        print("\n🔒 HIGH PRIORITY: Unified Security Service Tests")
        await self.test_security_dashboard()
        await self.test_security_event_logging()
        await self.test_compliance_status()
        await self.test_user_security_insights()
        
        # MEDIUM PRIORITY TESTS
        print("\n📊 MEDIUM PRIORITY: Advanced Features & Predictive Analytics")
        await self.test_predictive_analytics()
        await self.test_market_trends_analysis()
        await self.test_seller_performance_forecasting()
        await self.test_advanced_features_status()
        
        # MEDIUM PRIORITY TESTS - Currency & Escrow
        print("\n💰 MEDIUM PRIORITY: Currency & Escrow Services")
        await self.test_supported_currencies()
        await self.test_exchange_rates()
        await self.test_currency_conversion()
        
        # LOW PRIORITY TESTS - AI & Chatbot
        print("\n🤖 LOW PRIORITY: AI & Chatbot Services")
        await self.test_ai_trending_items()
        await self.test_chatbot_start_session()
        await self.test_chatbot_analytics()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📋 CONSOLIDATED BACKEND TESTING SUMMARY")
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
        
        print(f"\n🎯 CONSOLIDATION VERIFICATION:")
        print(f"   • Unified Analytics Service: {'✅' if any('Analytics' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • Unified Security Service: {'✅' if any('Security' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • Advanced Features Status: {'✅' if any('Status' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • Currency & Escrow: {'✅' if any('Currency' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        print(f"   • AI & Chatbot: {'✅' if any('Chatbot' in t['test'] and t['success'] for t in self.test_results) else '❌'}")
        
        if failed_tests == 0:
            print(f"\n🎉 ALL CONSOLIDATION TESTS PASSED! The unified services are working correctly.")
        elif failed_tests <= 2:
            print(f"\n⚠️  MOSTLY SUCCESSFUL with {failed_tests} minor issues.")
        else:
            print(f"\n🚨 CONSOLIDATION ISSUES DETECTED - {failed_tests} tests failed.")

async def main():
    """Main test execution"""
    tester = ConsolidatedBackendTester()
    
    try:
        await tester.setup()
        await tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n💥 Testing failed with error: {e}")
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())