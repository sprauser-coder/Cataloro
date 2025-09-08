#!/usr/bin/env python3
"""
Phase 6 Backend Services Testing Suite
Comprehensive testing for Phase 6 Enterprise Intelligence & Global Expansion features
"""

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://marketplace-repair-1.preview.emergentagent.com"

class Phase6BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
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
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None) -> tuple[bool, Any]:
        """Make HTTP request and return success status and response data"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data
            else:
                return False, {"error": f"Unsupported method: {method}"}
                
        except Exception as e:
            return False, {"error": str(e)}
    
    # Advanced Analytics Service Tests
    async def test_advanced_analytics_dashboard(self):
        """Test Advanced Analytics dashboard data endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/analytics/dashboard")
        
        if success and response.get("success"):
            dashboard_data = response.get("dashboard_data", {})
            has_overview = "overview" in dashboard_data
            has_predictions = "predictions" in dashboard_data
            has_trends = "trends" in dashboard_data
            has_recommendations = "recommendations" in dashboard_data
            
            if has_overview and has_predictions and has_trends and has_recommendations:
                overview = dashboard_data["overview"]
                self.log_test(
                    "Advanced Analytics Dashboard", 
                    True, 
                    f"Dashboard loaded with overview (Users: {overview.get('total_users', 0)}, Revenue: €{overview.get('monthly_revenue', 0):.2f}), predictions, trends, and recommendations"
                )
            else:
                self.log_test("Advanced Analytics Dashboard", False, "Missing required dashboard sections", response)
        else:
            self.log_test("Advanced Analytics Dashboard", False, "Failed to load dashboard", response)
    
    async def test_market_trends_analysis(self):
        """Test market trends analysis endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/analytics/market-trends?time_period=30d")
        
        if success and response.get("success"):
            trends = response.get("trends", [])
            if trends and len(trends) > 0:
                trend_sample = trends[0]
                required_fields = ["category", "trend_direction", "trend_strength", "predicted_growth", "confidence_score"]
                has_all_fields = all(field in trend_sample for field in required_fields)
                
                if has_all_fields:
                    self.log_test(
                        "Market Trends Analysis", 
                        True, 
                        f"Analyzed {len(trends)} categories. Top trend: {trend_sample['category']} ({trend_sample['trend_direction']}, {trend_sample['predicted_growth']:.1f}% growth)"
                    )
                else:
                    self.log_test("Market Trends Analysis", False, "Missing required trend fields", response)
            else:
                self.log_test("Market Trends Analysis", False, "No trends data returned", response)
        else:
            self.log_test("Market Trends Analysis", False, "Failed to get market trends", response)
    
    async def test_seller_performance_forecasting(self):
        """Test seller performance forecasting endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/analytics/seller-performance")
        
        if success and response.get("success"):
            performance_data = response.get("seller_performance", [])
            if performance_data and len(performance_data) > 0:
                seller_sample = performance_data[0]
                required_fields = ["seller_id", "seller_name", "current_rating", "predicted_rating", "revenue_forecast", "recommendations"]
                has_all_fields = all(field in seller_sample for field in required_fields)
                
                if has_all_fields:
                    self.log_test(
                        "Seller Performance Forecasting", 
                        True, 
                        f"Forecasted performance for {len(performance_data)} sellers. Sample: {seller_sample['seller_name']} (Rating: {seller_sample['current_rating']:.1f} → {seller_sample['predicted_rating']:.1f}, Revenue forecast: €{seller_sample['revenue_forecast']:.0f})"
                    )
                else:
                    self.log_test("Seller Performance Forecasting", False, "Missing required performance fields", response)
            else:
                self.log_test("Seller Performance Forecasting", False, "No performance data returned", response)
        else:
            self.log_test("Seller Performance Forecasting", False, "Failed to get seller performance", response)
    
    async def test_revenue_insights(self):
        """Test revenue optimization insights endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/analytics/revenue-insights?period=monthly")
        
        if success and response.get("success"):
            insights = response.get("revenue_insights", [])
            if insights and len(insights) > 0:
                insight_sample = insights[0]
                required_fields = ["period", "actual_revenue", "predicted_revenue", "growth_rate", "key_drivers", "optimization_opportunities"]
                has_all_fields = all(field in insight_sample for field in required_fields)
                
                if has_all_fields:
                    self.log_test(
                        "Revenue Optimization Insights", 
                        True, 
                        f"Generated insights for {len(insights)} periods. Sample: {insight_sample['period']} (Actual: €{insight_sample['actual_revenue']:.0f}, Predicted: €{insight_sample['predicted_revenue']:.0f}, Growth: {insight_sample['growth_rate']:.1f}%)"
                    )
                else:
                    self.log_test("Revenue Optimization Insights", False, "Missing required insight fields", response)
            else:
                self.log_test("Revenue Optimization Insights", False, "No insights data returned", response)
        else:
            self.log_test("Revenue Optimization Insights", False, "Failed to get revenue insights", response)
    
    async def test_category_performance_analysis(self):
        """Test category performance analysis endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/analytics/category-performance")
        
        if success and response.get("success"):
            categories = response.get("categories", [])
            if categories and len(categories) > 0:
                category_sample = categories[0]
                required_fields = ["name", "sales", "growth", "profit_margin", "customer_rating"]
                has_all_fields = all(field in category_sample for field in required_fields)
                
                if has_all_fields:
                    self.log_test(
                        "Category Performance Analysis", 
                        True, 
                        f"Analyzed {len(categories)} categories. Top category: {category_sample['name']} (Sales: €{category_sample['sales']:,}, Growth: {category_sample['growth']:.1f}%, Rating: {category_sample['customer_rating']:.1f})"
                    )
                else:
                    self.log_test("Category Performance Analysis", False, "Missing required category fields", response)
            else:
                self.log_test("Category Performance Analysis", False, "No categories data returned", response)
        else:
            self.log_test("Category Performance Analysis", False, "Failed to get category performance", response)
    
    # Enterprise Security Service Tests
    async def test_enterprise_security_dashboard(self):
        """Test Enterprise Security dashboard endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/security/dashboard")
        
        if success and response.get("success"):
            security_data = response.get("security_data", {})
            has_overview = "overview" in security_data
            has_events = "recent_events" in security_data
            has_threat_levels = "threat_levels" in security_data
            has_recommendations = "recommendations" in security_data
            
            if has_overview and has_events and has_threat_levels and has_recommendations:
                overview = security_data["overview"]
                self.log_test(
                    "Enterprise Security Dashboard", 
                    True, 
                    f"Security dashboard loaded with overview (Total events: {overview.get('total_events', 0)}, Critical: {overview.get('critical_events', 0)}, Security score: {overview.get('security_score', 0)}), threat levels, and recommendations"
                )
            else:
                self.log_test("Enterprise Security Dashboard", False, "Missing required security sections", response)
        else:
            self.log_test("Enterprise Security Dashboard", False, "Failed to load security dashboard", response)
    
    async def test_security_event_logging(self):
        """Test security event logging endpoint"""
        test_event = {
            "event_type": "test_event",
            "severity": "medium",
            "user_id": "test_user_123",
            "ip_address": "192.168.1.100",
            "description": "Test security event for Phase 6 testing"
        }
        
        success, response = await self.make_request("POST", "/api/v2/phase6/security/log-event", test_event)
        
        if success and response.get("success"):
            event_id = response.get("event_id")
            if event_id:
                self.log_test(
                    "Security Event Logging", 
                    True, 
                    f"Security event logged successfully with ID: {event_id}"
                )
            else:
                self.log_test("Security Event Logging", False, "No event ID returned", response)
        else:
            self.log_test("Security Event Logging", False, "Failed to log security event", response)
    
    async def test_compliance_status(self):
        """Test compliance status endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/security/compliance")
        
        if success and response.get("success"):
            compliance_data = response.get("compliance", {})
            has_overview = "overview" in compliance_data
            has_categories = "by_category" in compliance_data
            has_failing_checks = "failing_checks" in compliance_data
            
            if has_overview and has_categories:
                overview = compliance_data["overview"]
                self.log_test(
                    "Compliance Status", 
                    True, 
                    f"Compliance status retrieved (Total checks: {overview.get('total_checks', 0)}, Passing: {overview.get('passing_checks', 0)}, Score: {overview.get('compliance_score', 0):.1f}%)"
                )
            else:
                self.log_test("Compliance Status", False, "Missing required compliance sections", response)
        else:
            self.log_test("Compliance Status", False, "Failed to get compliance status", response)
    
    async def test_user_security_insights(self):
        """Test user security insights endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/security/user-insights?limit=10")
        
        if success and response.get("success"):
            insights = response.get("user_insights", [])
            if insights and len(insights) > 0:
                insight_sample = insights[0]
                required_fields = ["user_id", "risk_score", "risk_level", "security_flags", "recommendations"]
                has_all_fields = all(field in insight_sample for field in required_fields)
                
                if has_all_fields:
                    self.log_test(
                        "User Security Insights", 
                        True, 
                        f"Retrieved security insights for {len(insights)} users. Sample: User {insight_sample['user_id']} (Risk: {insight_sample['risk_level']}, Score: {insight_sample['risk_score']:.2f})"
                    )
                else:
                    self.log_test("User Security Insights", False, "Missing required insight fields", response)
            else:
                self.log_test("User Security Insights", False, "No security insights returned", response)
        else:
            self.log_test("User Security Insights", False, "Failed to get user security insights", response)
    
    # Fraud Detection Service Tests
    async def test_fraud_detection_dashboard(self):
        """Test Fraud Detection dashboard endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/fraud/dashboard")
        
        if success and response.get("success"):
            fraud_data = response.get("fraud_data", {})
            has_overview = "overview" in fraud_data
            has_risk_metrics = "risk_metrics" in fraud_data
            has_transaction_metrics = "transaction_metrics" in fraud_data
            has_recent_alerts = "recent_alerts" in fraud_data
            
            if has_overview and has_risk_metrics and has_transaction_metrics:
                overview = fraud_data["overview"]
                self.log_test(
                    "Fraud Detection Dashboard", 
                    True, 
                    f"Fraud dashboard loaded (Total alerts: {overview.get('total_alerts', 0)}, Active: {overview.get('active_alerts', 0)}, Detection accuracy: {overview.get('detection_accuracy', 0):.1f}%)"
                )
            else:
                self.log_test("Fraud Detection Dashboard", False, "Missing required fraud sections", response)
        else:
            self.log_test("Fraud Detection Dashboard", False, "Failed to load fraud dashboard", response)
    
    async def test_transaction_analysis(self):
        """Test transaction fraud analysis endpoint"""
        test_transaction = {
            "user_id": "test_user_456",
            "amount": 1500.00,
            "transaction_id": "tx_test_123",
            "payment_method": "credit_card",
            "unusual_location": False
        }
        
        success, response = await self.make_request("POST", "/api/v2/phase6/fraud/analyze-transaction", test_transaction)
        
        if success and response.get("success"):
            analysis = response.get("analysis", {})
            required_fields = ["transaction_id", "fraud_probability", "risk_factors", "recommendation"]
            has_all_fields = all(field in analysis for field in required_fields)
            
            if has_all_fields:
                self.log_test(
                    "Transaction Fraud Analysis", 
                    True, 
                    f"Transaction analyzed (ID: {analysis['transaction_id']}, Fraud probability: {analysis['fraud_probability']:.2f}, Recommendation: {analysis['recommendation']})"
                )
            else:
                self.log_test("Transaction Fraud Analysis", False, "Missing required analysis fields", response)
        else:
            self.log_test("Transaction Fraud Analysis", False, "Failed to analyze transaction", response)
    
    # AI Chatbot Service Tests
    async def test_chatbot_session_management(self):
        """Test AI Chatbot session start endpoint"""
        session_data = {"user_id": "test_user_789"}
        
        success, response = await self.make_request("POST", "/api/v2/phase6/chatbot/start-session", session_data)
        
        if success and response.get("success"):
            session_id = response.get("session_id")
            if session_id:
                self.log_test(
                    "AI Chatbot Session Management", 
                    True, 
                    f"Chat session started successfully with ID: {session_id}"
                )
                return session_id
            else:
                self.log_test("AI Chatbot Session Management", False, "No session ID returned", response)
                return None
        else:
            self.log_test("AI Chatbot Session Management", False, "Failed to start chat session", response)
            return None
    
    async def test_chatbot_message_processing(self):
        """Test AI Chatbot message processing endpoint"""
        # First start a session
        session_id = await self.test_chatbot_session_management()
        
        if session_id:
            message_data = {
                "session_id": session_id,
                "message": "I need help with my order status",
                "user_id": "test_user_789"
            }
            
            success, response = await self.make_request("POST", "/api/v2/phase6/chatbot/message", message_data)
            
            if success and response.get("success"):
                chat_response = response.get("chat_response", {})
                required_fields = ["response", "intent", "confidence"]
                has_all_fields = all(field in chat_response for field in required_fields)
                
                if has_all_fields:
                    self.log_test(
                        "AI Chatbot Message Processing", 
                        True, 
                        f"Message processed (Intent: {chat_response['intent']}, Confidence: {chat_response['confidence']:.2f}, Response generated)"
                    )
                else:
                    self.log_test("AI Chatbot Message Processing", False, "Missing required response fields", response)
            else:
                self.log_test("AI Chatbot Message Processing", False, "Failed to process message", response)
        else:
            self.log_test("AI Chatbot Message Processing", False, "Cannot test without valid session", {})
    
    async def test_chatbot_analytics(self):
        """Test AI Chatbot analytics endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/chatbot/analytics")
        
        if success and response.get("success"):
            analytics = response.get("analytics", {})
            has_overview = "overview" in analytics
            has_performance = "performance" in analytics
            has_intents = "intents" in analytics
            
            if has_overview and has_performance:
                overview = analytics["overview"]
                performance = analytics["performance"]
                self.log_test(
                    "AI Chatbot Analytics", 
                    True, 
                    f"Chat analytics retrieved (Total sessions: {overview.get('total_sessions', 0)}, Resolution rate: {overview.get('resolution_rate', 0):.1f}%, Avg confidence: {performance.get('avg_confidence', 0):.2f})"
                )
            else:
                self.log_test("AI Chatbot Analytics", False, "Missing required analytics sections", response)
        else:
            self.log_test("AI Chatbot Analytics", False, "Failed to get chat analytics", response)
    
    # Internationalization Service Tests
    async def test_supported_languages(self):
        """Test supported languages endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/i18n/languages")
        
        if success and response.get("success"):
            languages = response.get("languages", [])
            if languages and len(languages) > 0:
                lang_sample = languages[0]
                required_fields = ["code", "name", "native_name", "enabled", "completion_percentage"]
                has_all_fields = all(field in lang_sample for field in required_fields)
                
                if has_all_fields:
                    enabled_count = len([lang for lang in languages if lang.get("enabled", False)])
                    self.log_test(
                        "Internationalization - Supported Languages", 
                        True, 
                        f"Retrieved {len(languages)} languages ({enabled_count} enabled). Sample: {lang_sample['name']} ({lang_sample['code']}) - {lang_sample['completion_percentage']:.1f}% complete"
                    )
                else:
                    self.log_test("Internationalization - Supported Languages", False, "Missing required language fields", response)
            else:
                self.log_test("Internationalization - Supported Languages", False, "No languages returned", response)
        else:
            self.log_test("Internationalization - Supported Languages", False, "Failed to get supported languages", response)
    
    async def test_supported_regions(self):
        """Test supported regions endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/i18n/regions")
        
        if success and response.get("success"):
            regions = response.get("regions", [])
            if regions and len(regions) > 0:
                region_sample = regions[0]
                required_fields = ["code", "name", "currency", "tax_rate", "compliance_requirements", "supported_languages"]
                has_all_fields = all(field in region_sample for field in required_fields)
                
                if has_all_fields:
                    self.log_test(
                        "Internationalization - Supported Regions", 
                        True, 
                        f"Retrieved {len(regions)} regions. Sample: {region_sample['name']} ({region_sample['code']}) - Currency: {region_sample['currency']}, Tax: {region_sample['tax_rate']}%, Compliance: {len(region_sample['compliance_requirements'])} requirements"
                    )
                else:
                    self.log_test("Internationalization - Supported Regions", False, "Missing required region fields", response)
            else:
                self.log_test("Internationalization - Supported Regions", False, "No regions returned", response)
        else:
            self.log_test("Internationalization - Supported Regions", False, "Failed to get supported regions", response)
    
    async def test_translations(self):
        """Test translations endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/i18n/translations/es")
        
        if success and response.get("success"):
            translations = response.get("translations", {})
            language_code = response.get("language_code")
            
            if translations and language_code == "es":
                sample_keys = list(translations.keys())[:3]
                self.log_test(
                    "Internationalization - Translations", 
                    True, 
                    f"Retrieved {len(translations)} translations for Spanish. Sample keys: {', '.join(sample_keys)}"
                )
            else:
                self.log_test("Internationalization - Translations", False, "No translations or incorrect language", response)
        else:
            self.log_test("Internationalization - Translations", False, "Failed to get translations", response)
    
    async def test_compliance_requirements(self):
        """Test regional compliance requirements endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/i18n/compliance/DE")
        
        if success and response.get("success"):
            compliance_status = response.get("compliance_status", {})
            has_region_code = "region_code" in compliance_status
            has_requirements = "requirements" in compliance_status
            has_overall_status = "overall_status" in compliance_status
            
            if has_region_code and has_requirements and has_overall_status:
                requirements = compliance_status["requirements"]
                self.log_test(
                    "Internationalization - Compliance Requirements", 
                    True, 
                    f"Retrieved compliance status for {compliance_status['region_code']} ({len(requirements)} requirements, Overall status: {compliance_status['overall_status']})"
                )
            else:
                self.log_test("Internationalization - Compliance Requirements", False, "Missing required compliance fields", response)
        else:
            self.log_test("Internationalization - Compliance Requirements", False, "Failed to get compliance requirements", response)
    
    async def test_localization_analytics(self):
        """Test localization analytics endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/i18n/analytics")
        
        if success and response.get("success"):
            analytics = response.get("analytics", {})
            has_overview = "overview" in analytics
            has_languages = "languages" in analytics
            has_regions = "regions" in analytics
            
            if has_overview and has_languages and has_regions:
                overview = analytics["overview"]
                self.log_test(
                    "Internationalization - Localization Analytics", 
                    True, 
                    f"Localization analytics retrieved (Languages: {overview.get('enabled_languages', 0)}/{overview.get('total_languages', 0)}, Regions: {overview.get('enabled_regions', 0)}/{overview.get('total_regions', 0)})"
                )
            else:
                self.log_test("Internationalization - Localization Analytics", False, "Missing required analytics sections", response)
        else:
            self.log_test("Internationalization - Localization Analytics", False, "Failed to get localization analytics", response)
    
    # Enhanced User Management Service Tests
    async def test_user_management_analytics(self):
        """Test user management analytics endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/users/analytics")
        
        if success and response.get("success"):
            analytics = response.get("analytics", {})
            has_overview = "overview" in analytics
            has_roles = "roles" in analytics
            has_permissions = "permissions" in analytics
            has_tenants = "tenants" in analytics
            
            if has_overview and has_roles and has_permissions:
                overview = analytics["overview"]
                self.log_test(
                    "Enhanced User Management - Analytics", 
                    True, 
                    f"User management analytics retrieved (Total users: {overview.get('total_users', 0)}, Roles: {overview.get('total_roles', 0)}, Active sessions: {overview.get('active_sessions', 0)})"
                )
            else:
                self.log_test("Enhanced User Management - Analytics", False, "Missing required analytics sections", response)
        else:
            self.log_test("Enhanced User Management - Analytics", False, "Failed to get user management analytics", response)
    
    async def test_user_permissions(self):
        """Test user permissions endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/users/permissions/admin_001")
        
        if success and response.get("success"):
            permissions = response.get("permissions", {})
            required_fields = ["user_id", "role", "permissions", "custom_permissions"]
            has_all_fields = all(field in permissions for field in required_fields)
            
            if has_all_fields:
                self.log_test(
                    "Enhanced User Management - User Permissions", 
                    True, 
                    f"User permissions retrieved for {permissions['user_id']} (Role: {permissions['role']}, Permissions: {len(permissions['permissions'])}, Custom: {len(permissions['custom_permissions'])})"
                )
            else:
                self.log_test("Enhanced User Management - User Permissions", False, "Missing required permission fields", response)
        else:
            self.log_test("Enhanced User Management - User Permissions", False, "Failed to get user permissions", response)
    
    async def test_role_hierarchy(self):
        """Test role hierarchy endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/users/role-hierarchy")
        
        if success and response.get("success"):
            hierarchy = response.get("hierarchy", {})
            has_roles = "roles" in hierarchy
            has_total_permissions = "total_permissions" in hierarchy
            has_hierarchy_levels = "hierarchy_levels" in hierarchy
            
            if has_roles and has_total_permissions and has_hierarchy_levels:
                roles = hierarchy["roles"]
                self.log_test(
                    "Enhanced User Management - Role Hierarchy", 
                    True, 
                    f"Role hierarchy retrieved ({len(roles)} roles, {hierarchy['total_permissions']} total permissions, {len(hierarchy['hierarchy_levels'])} levels)"
                )
            else:
                self.log_test("Enhanced User Management - Role Hierarchy", False, "Missing required hierarchy fields", response)
        else:
            self.log_test("Enhanced User Management - Role Hierarchy", False, "Failed to get role hierarchy", response)
    
    async def test_user_activity_tracking(self):
        """Test user activity tracking endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/users/activity?limit=10")
        
        if success and response.get("success"):
            activities = response.get("activities", [])
            if activities and len(activities) > 0:
                activity_sample = activities[0]
                required_fields = ["user_id", "action", "resource", "timestamp", "success"]
                has_all_fields = all(field in activity_sample for field in required_fields)
                
                if has_all_fields:
                    self.log_test(
                        "Enhanced User Management - Activity Tracking", 
                        True, 
                        f"Retrieved {len(activities)} user activities. Sample: User {activity_sample['user_id']} performed {activity_sample['action']} on {activity_sample['resource']}"
                    )
                else:
                    self.log_test("Enhanced User Management - Activity Tracking", False, "Missing required activity fields", response)
            else:
                self.log_test("Enhanced User Management - Activity Tracking", False, "No activities returned", response)
        else:
            self.log_test("Enhanced User Management - Activity Tracking", False, "Failed to get user activities", response)
    
    # Phase 6 Status Endpoint Test
    async def test_phase6_status(self):
        """Test comprehensive Phase 6 status endpoint"""
        success, response = await self.make_request("GET", "/api/v2/phase6/status")
        
        if success:
            required_services = [
                "advanced_analytics", 
                "enterprise_security", 
                "fraud_detection", 
                "ai_chatbot", 
                "internationalization", 
                "enhanced_user_management"
            ]
            
            services = response.get("services", {})
            overall_status = response.get("overall_status", "unknown")
            
            operational_services = []
            error_services = []
            
            for service_name in required_services:
                if service_name in services:
                    service_status = services[service_name].get("status", "unknown")
                    if service_status == "operational":
                        operational_services.append(service_name)
                    else:
                        error_services.append(service_name)
                else:
                    error_services.append(f"{service_name} (missing)")
            
            if len(operational_services) == len(required_services):
                self.log_test(
                    "Phase 6 Comprehensive Status", 
                    True, 
                    f"All {len(required_services)} Phase 6 services operational (Overall status: {overall_status})"
                )
            else:
                self.log_test(
                    "Phase 6 Comprehensive Status", 
                    False, 
                    f"Some services not operational. Working: {len(operational_services)}/{len(required_services)}. Issues: {', '.join(error_services)}", 
                    response
                )
        else:
            self.log_test("Phase 6 Comprehensive Status", False, "Failed to get Phase 6 status", response)
    
    async def run_all_tests(self):
        """Run all Phase 6 backend tests"""
        print("🚀 Starting Phase 6 Backend Services Testing Suite")
        print("=" * 80)
        print()
        
        # Advanced Analytics Service Tests
        print("📊 ADVANCED ANALYTICS SERVICE TESTS")
        print("-" * 50)
        await self.test_advanced_analytics_dashboard()
        await self.test_market_trends_analysis()
        await self.test_seller_performance_forecasting()
        await self.test_revenue_insights()
        await self.test_category_performance_analysis()
        print()
        
        # Enterprise Security Service Tests
        print("🔒 ENTERPRISE SECURITY SERVICE TESTS")
        print("-" * 50)
        await self.test_enterprise_security_dashboard()
        await self.test_security_event_logging()
        await self.test_compliance_status()
        await self.test_user_security_insights()
        print()
        
        # Fraud Detection Service Tests
        print("🕵️ FRAUD DETECTION SERVICE TESTS")
        print("-" * 50)
        await self.test_fraud_detection_dashboard()
        await self.test_transaction_analysis()
        print()
        
        # AI Chatbot Service Tests
        print("🤖 AI CHATBOT SERVICE TESTS")
        print("-" * 50)
        await self.test_chatbot_message_processing()  # This includes session management
        await self.test_chatbot_analytics()
        print()
        
        # Internationalization Service Tests
        print("🌍 INTERNATIONALIZATION SERVICE TESTS")
        print("-" * 50)
        await self.test_supported_languages()
        await self.test_supported_regions()
        await self.test_translations()
        await self.test_compliance_requirements()
        await self.test_localization_analytics()
        print()
        
        # Enhanced User Management Service Tests
        print("👥 ENHANCED USER MANAGEMENT SERVICE TESTS")
        print("-" * 50)
        await self.test_user_management_analytics()
        await self.test_user_permissions()
        await self.test_role_hierarchy()
        await self.test_user_activity_tracking()
        print()
        
        # Phase 6 Status Test
        print("📋 PHASE 6 COMPREHENSIVE STATUS TEST")
        print("-" * 50)
        await self.test_phase6_status()
        print()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print("=" * 80)
        print("📊 PHASE 6 BACKEND TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
            print()
        
        # Service-wise summary
        service_results = {}
        for result in self.test_results:
            service = result["test"].split(" - ")[0] if " - " in result["test"] else "General"
            if service not in service_results:
                service_results[service] = {"total": 0, "passed": 0}
            service_results[service]["total"] += 1
            if result["success"]:
                service_results[service]["passed"] += 1
        
        print("📋 SERVICE-WISE RESULTS:")
        for service, stats in service_results.items():
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            status = "✅" if rate == 100 else "⚠️" if rate >= 50 else "❌"
            print(f"  {status} {service}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
        
        print()
        print("🎯 PHASE 6 ENTERPRISE FEATURES STATUS:")
        if success_rate >= 90:
            print("✅ EXCELLENT - Phase 6 services are working exceptionally well")
        elif success_rate >= 75:
            print("✅ GOOD - Phase 6 services are mostly operational with minor issues")
        elif success_rate >= 50:
            print("⚠️ PARTIAL - Phase 6 services have significant issues requiring attention")
        else:
            print("❌ CRITICAL - Phase 6 services have major problems requiring immediate fixes")
        
        print("=" * 80)

async def main():
    """Main test execution function"""
    async with Phase6BackendTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())