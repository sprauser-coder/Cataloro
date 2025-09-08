#!/usr/bin/env python3
"""
Webhook Management System Backend Testing
Tests the newly implemented webhook management system and related features
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://listing-repair-4.preview.emergentagent.com/api"

class WebhookBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.webhook_id = None
        self.test_webhook_url = "https://webhook.site/test-endpoint"  # Mock webhook endpoint
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print("🔧 Test session initialized")
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
        print("🧹 Test session cleaned up")
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status} {test_name}: {details}")
        
    async def test_webhook_service_initialization(self):
        """Test 1: Verify webhook service is properly initialized"""
        try:
            # Test webhook events endpoint to verify service is running
            async with self.session.get(f"{BACKEND_URL}/admin/webhook-events") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("events"):
                        events = data["events"]
                        self.log_result(
                            "Webhook Service Initialization",
                            True,
                            f"Service initialized with {len(events)} supported events"
                        )
                        return True
                    else:
                        self.log_result("Webhook Service Initialization", False, "Service response invalid")
                        return False
                else:
                    self.log_result("Webhook Service Initialization", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Webhook Service Initialization", False, f"Error: {str(e)}")
            return False
            
    async def test_webhook_events_endpoint(self):
        """Test 2: Test supported webhook events endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/admin/webhook-events") as response:
                if response.status == 200:
                    data = await response.json()
                    events = data.get("events", [])
                    
                    # Verify expected events exist
                    expected_events = [
                        "user.registered", "user.login", "listing.created", 
                        "order.created", "tender.submitted", "payment.completed"
                    ]
                    
                    found_events = [event["event"] for event in events]
                    missing_events = [e for e in expected_events if e not in found_events]
                    
                    if not missing_events:
                        self.log_result(
                            "Webhook Events Endpoint",
                            True,
                            f"All {len(events)} expected events available"
                        )
                        return True
                    else:
                        self.log_result(
                            "Webhook Events Endpoint",
                            False,
                            f"Missing events: {missing_events}"
                        )
                        return False
                else:
                    self.log_result("Webhook Events Endpoint", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Webhook Events Endpoint", False, f"Error: {str(e)}")
            return False
            
    async def test_create_webhook(self):
        """Test 3: Test creating a new webhook"""
        try:
            webhook_data = {
                "url": self.test_webhook_url,
                "events": ["user.login", "listing.created", "order.created"],
                "name": "Test Webhook",
                "description": "Test webhook for backend testing",
                "active": True,
                "secret": "test_secret_123",
                "retry_attempts": 3,
                "timeout_seconds": 30
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/admin/webhooks",
                json=webhook_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("webhook"):
                        webhook = data["webhook"]
                        self.webhook_id = webhook["id"]
                        self.log_result(
                            "Create Webhook",
                            True,
                            f"Webhook created with ID: {self.webhook_id}"
                        )
                        return True
                    else:
                        self.log_result("Create Webhook", False, "Invalid response format")
                        return False
                else:
                    error_text = await response.text()
                    self.log_result("Create Webhook", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_result("Create Webhook", False, f"Error: {str(e)}")
            return False
            
    async def test_get_webhooks(self):
        """Test 4: Test listing all webhooks"""
        try:
            async with self.session.get(f"{BACKEND_URL}/admin/webhooks") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "webhooks" in data:
                        webhooks = data["webhooks"]
                        self.log_result(
                            "Get Webhooks",
                            True,
                            f"Retrieved {len(webhooks)} webhooks"
                        )
                        return True
                    else:
                        self.log_result("Get Webhooks", False, "Invalid response format")
                        return False
                else:
                    self.log_result("Get Webhooks", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Get Webhooks", False, f"Error: {str(e)}")
            return False
            
    async def test_get_specific_webhook(self):
        """Test 5: Test getting a specific webhook"""
        if not self.webhook_id:
            self.log_result("Get Specific Webhook", False, "No webhook ID available")
            return False
            
        try:
            async with self.session.get(f"{BACKEND_URL}/admin/webhooks/{self.webhook_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("webhook"):
                        webhook = data["webhook"]
                        self.log_result(
                            "Get Specific Webhook",
                            True,
                            f"Retrieved webhook: {webhook['name']}"
                        )
                        return True
                    else:
                        self.log_result("Get Specific Webhook", False, "Invalid response format")
                        return False
                else:
                    self.log_result("Get Specific Webhook", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Get Specific Webhook", False, f"Error: {str(e)}")
            return False
            
    async def test_update_webhook(self):
        """Test 6: Test updating a webhook"""
        if not self.webhook_id:
            self.log_result("Update Webhook", False, "No webhook ID available")
            return False
            
        try:
            update_data = {
                "name": "Updated Test Webhook",
                "description": "Updated description for testing",
                "events": ["user.login", "listing.created", "order.created", "tender.submitted"],
                "active": True
            }
            
            async with self.session.put(
                f"{BACKEND_URL}/admin/webhooks/{self.webhook_id}",
                json=update_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("webhook"):
                        webhook = data["webhook"]
                        self.log_result(
                            "Update Webhook",
                            True,
                            f"Updated webhook: {webhook['name']}"
                        )
                        return True
                    else:
                        self.log_result("Update Webhook", False, "Invalid response format")
                        return False
                else:
                    self.log_result("Update Webhook", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Update Webhook", False, f"Error: {str(e)}")
            return False
            
    async def test_webhook_test_functionality(self):
        """Test 7: Test webhook test functionality"""
        if not self.webhook_id:
            self.log_result("Webhook Test Functionality", False, "No webhook ID available")
            return False
            
        try:
            async with self.session.post(f"{BACKEND_URL}/admin/webhooks/{self.webhook_id}/test") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_result(
                            "Webhook Test Functionality",
                            True,
                            "Test webhook sent successfully"
                        )
                        return True
                    else:
                        self.log_result("Webhook Test Functionality", False, "Test failed")
                        return False
                else:
                    self.log_result("Webhook Test Functionality", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Webhook Test Functionality", False, f"Error: {str(e)}")
            return False
            
    async def test_webhook_deliveries(self):
        """Test 8: Test webhook delivery history"""
        if not self.webhook_id:
            self.log_result("Webhook Deliveries", False, "No webhook ID available")
            return False
            
        try:
            async with self.session.get(f"{BACKEND_URL}/admin/webhooks/{self.webhook_id}/deliveries") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "deliveries" in data:
                        deliveries = data["deliveries"]
                        self.log_result(
                            "Webhook Deliveries",
                            True,
                            f"Retrieved {len(deliveries)} delivery records"
                        )
                        return True
                    else:
                        self.log_result("Webhook Deliveries", False, "Invalid response format")
                        return False
                else:
                    self.log_result("Webhook Deliveries", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Webhook Deliveries", False, f"Error: {str(e)}")
            return False
            
    async def test_currency_integration(self):
        """Test 9: Test currency endpoints for CurrencyPriceDisplay component"""
        try:
            # Test supported currencies endpoint
            async with self.session.get(f"{BACKEND_URL}/v2/advanced/currency/supported") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("currencies"):
                        currencies = data["currencies"]
                        self.log_result(
                            "Currency Integration - Supported Currencies",
                            True,
                            f"Retrieved {len(currencies)} supported currencies"
                        )
                        
                        # Test exchange rates endpoint
                        async with self.session.get(f"{BACKEND_URL}/v2/advanced/currency/rates") as rates_response:
                            if rates_response.status == 200:
                                rates_data = await rates_response.json()
                                if rates_data.get("success") and rates_data.get("rates"):
                                    rates = rates_data["rates"]
                                    self.log_result(
                                        "Currency Integration - Exchange Rates",
                                        True,
                                        f"Retrieved {len(rates)} exchange rates"
                                    )
                                    
                                    # Test currency conversion
                                    conversion_data = {
                                        "amount": 100,
                                        "from_currency": "EUR",
                                        "to_currency": "USD"
                                    }
                                    
                                    async with self.session.post(
                                        f"{BACKEND_URL}/v2/advanced/currency/convert",
                                        json=conversion_data
                                    ) as convert_response:
                                        if convert_response.status == 200:
                                            convert_data = await convert_response.json()
                                            if convert_data.get("success"):
                                                conversion = convert_data["conversion"]
                                                self.log_result(
                                                    "Currency Integration - Conversion",
                                                    True,
                                                    f"€100 → ${conversion['converted_amount']}"
                                                )
                                                return True
                                            else:
                                                self.log_result("Currency Integration - Conversion", False, "Conversion failed")
                                                return False
                                        else:
                                            self.log_result("Currency Integration - Conversion", False, f"HTTP {convert_response.status}")
                                            return False
                                else:
                                    self.log_result("Currency Integration - Exchange Rates", False, "Invalid rates response")
                                    return False
                            else:
                                self.log_result("Currency Integration - Exchange Rates", False, f"HTTP {rates_response.status}")
                                return False
                    else:
                        self.log_result("Currency Integration - Supported Currencies", False, "Invalid currencies response")
                        return False
                else:
                    self.log_result("Currency Integration - Supported Currencies", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Currency Integration", False, f"Error: {str(e)}")
            return False
            
    async def test_language_integration(self):
        """Test 10: Test language endpoints for LanguageSwitcher component"""
        try:
            async with self.session.get(f"{BACKEND_URL}/v2/advanced/i18n/languages") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("languages"):
                        languages = data["languages"]
                        self.log_result(
                            "Language Integration - Supported Languages",
                            True,
                            f"Retrieved {len(languages)} supported languages"
                        )
                        
                        # Test regions endpoint
                        async with self.session.get(f"{BACKEND_URL}/v2/advanced/i18n/regions") as regions_response:
                            if regions_response.status == 200:
                                regions_data = await regions_response.json()
                                if regions_data.get("success") and regions_data.get("regions"):
                                    regions = regions_data["regions"]
                                    self.log_result(
                                        "Language Integration - Supported Regions",
                                        True,
                                        f"Retrieved {len(regions)} supported regions"
                                    )
                                    return True
                                else:
                                    self.log_result("Language Integration - Supported Regions", False, "Invalid regions response")
                                    return False
                            else:
                                self.log_result("Language Integration - Supported Regions", False, f"HTTP {regions_response.status}")
                                return False
                    else:
                        self.log_result("Language Integration - Supported Languages", False, "Invalid languages response")
                        return False
                else:
                    self.log_result("Language Integration - Supported Languages", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Language Integration", False, f"Error: {str(e)}")
            return False
            
    async def test_listings_limit(self):
        """Test 11: Check that browse page returns more than 20 listings (should be 100)"""
        try:
            async with self.session.get(f"{BACKEND_URL}/marketplace/browse?limit=100") as response:
                if response.status == 200:
                    listings = await response.json()
                    if isinstance(listings, list):
                        count = len(listings)
                        if count > 20:
                            self.log_result(
                                "Listings Limit Check",
                                True,
                                f"Browse returns {count} listings (more than 20)"
                            )
                            return True
                        else:
                            self.log_result(
                                "Listings Limit Check",
                                False,
                                f"Browse returns only {count} listings (should be more than 20)"
                            )
                            return False
                    else:
                        self.log_result("Listings Limit Check", False, "Invalid response format")
                        return False
                else:
                    self.log_result("Listings Limit Check", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Listings Limit Check", False, f"Error: {str(e)}")
            return False
            
    async def test_delete_webhook(self):
        """Test 12: Test deleting a webhook (cleanup)"""
        if not self.webhook_id:
            self.log_result("Delete Webhook", False, "No webhook ID available")
            return False
            
        try:
            async with self.session.delete(f"{BACKEND_URL}/admin/webhooks/{self.webhook_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_result(
                            "Delete Webhook",
                            True,
                            f"Webhook {self.webhook_id} deleted successfully"
                        )
                        return True
                    else:
                        self.log_result("Delete Webhook", False, "Delete failed")
                        return False
                else:
                    self.log_result("Delete Webhook", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_result("Delete Webhook", False, f"Error: {str(e)}")
            return False
            
    async def run_all_tests(self):
        """Run all webhook and integration tests"""
        print("🚀 Starting Webhook Management System Backend Testing")
        print("=" * 60)
        
        await self.setup()
        
        # Run tests in sequence
        tests = [
            self.test_webhook_service_initialization,
            self.test_webhook_events_endpoint,
            self.test_create_webhook,
            self.test_get_webhooks,
            self.test_get_specific_webhook,
            self.test_update_webhook,
            self.test_webhook_test_functionality,
            self.test_webhook_deliveries,
            self.test_currency_integration,
            self.test_language_integration,
            self.test_listings_limit,
            self.test_delete_webhook
        ]
        
        for test in tests:
            await test()
            await asyncio.sleep(0.5)  # Small delay between tests
            
        await self.cleanup()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 WEBHOOK MANAGEMENT SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL WEBHOOK TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️  {total - passed} TESTS FAILED")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}: {result['details']}")
            return False

async def main():
    """Main test execution"""
    tester = WebhookBackendTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ Webhook management system is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Some webhook tests failed. Check the details above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())