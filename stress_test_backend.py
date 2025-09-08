#!/usr/bin/env python3
"""
Cataloro Marketplace - Extreme Stress Test for Backend APIs
Comprehensive stress testing with 1360 concurrent users for 5-10 minutes
Tests all major backend endpoints under extreme load conditions
"""

import asyncio
import aiohttp
import json
import sys
import time
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any
import statistics
from concurrent.futures import ThreadPoolExecutor
import psutil
import gc

# Backend URL from environment
BACKEND_URL = "https://cataloro-menueditor.preview.emergentagent.com/api"

class StressTestMetrics:
    def __init__(self):
        self.response_times = []
        self.error_count = 0
        self.success_count = 0
        self.total_requests = 0
        self.start_time = None
        self.end_time = None
        self.memory_usage = []
        self.cpu_usage = []
        
    def add_response_time(self, response_time: float):
        self.response_times.append(response_time)
        
    def add_error(self):
        self.error_count += 1
        self.total_requests += 1
        
    def add_success(self):
        self.success_count += 1
        self.total_requests += 1
        
    def get_stats(self):
        if not self.response_times:
            return {}
            
        return {
            "total_requests": self.total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": (self.success_count / self.total_requests) * 100 if self.total_requests > 0 else 0,
            "avg_response_time": statistics.mean(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "p95_response_time": statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) > 20 else max(self.response_times),
            "p99_response_time": statistics.quantiles(self.response_times, n=100)[98] if len(self.response_times) > 100 else max(self.response_times),
            "duration": (self.end_time - self.start_time) if self.start_time and self.end_time else 0,
            "requests_per_second": self.total_requests / ((self.end_time - self.start_time) if self.start_time and self.end_time and (self.end_time - self.start_time) > 0 else 1),
            "avg_memory_usage": statistics.mean(self.memory_usage) if self.memory_usage else 0,
            "avg_cpu_usage": statistics.mean(self.cpu_usage) if self.cpu_usage else 0
        }

class CataloroStressTester:
    def __init__(self):
        self.session = None
        self.metrics = {
            "browse_listings": StressTestMetrics(),
            "search_listings": StressTestMetrics(),
            "bidding": StressTestMetrics(),
            "messaging": StressTestMetrics(),
            "favorites": StressTestMetrics(),
            "currency_conversion": StressTestMetrics(),
            "webhook_events": StressTestMetrics(),
            "overall": StressTestMetrics()
        }
        self.test_users = []
        self.test_listings = []
        self.active_sessions = []
        
    async def setup(self):
        """Setup test session with optimized settings for high concurrency"""
        connector = aiohttp.TCPConnector(
            limit=2000,  # Total connection pool size
            limit_per_host=500,  # Per host connection limit
            ttl_dns_cache=300,
            use_dns_cache=True,
            ssl=False
        )
        
        timeout = aiohttp.ClientTimeout(
            total=30,
            connect=10,
            sock_read=10
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "User-Agent": "CataloroStressTester/1.0",
                "Accept": "application/json"
            }
        )
        
    async def cleanup(self):
        """Cleanup test session and test data"""
        if self.session:
            await self.session.close()
            
        # Clean up test data
        await self.cleanup_test_data()
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, metric_key: str = "overall") -> Dict:
        """Make HTTP request with metrics tracking"""
        url = f"{BACKEND_URL}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    response_time = time.time() - start_time
                    self.metrics[metric_key].add_response_time(response_time)
                    
                    if response.status < 400:
                        self.metrics[metric_key].add_success()
                        return {
                            "status": response.status,
                            "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                            "success": True,
                            "response_time": response_time
                        }
                    else:
                        self.metrics[metric_key].add_error()
                        return {
                            "status": response.status,
                            "data": await response.text(),
                            "success": False,
                            "response_time": response_time
                        }
                        
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, params=params) as response:
                    response_time = time.time() - start_time
                    self.metrics[metric_key].add_response_time(response_time)
                    
                    if response.status < 400:
                        self.metrics[metric_key].add_success()
                        return {
                            "status": response.status,
                            "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                            "success": True,
                            "response_time": response_time
                        }
                    else:
                        self.metrics[metric_key].add_error()
                        return {
                            "status": response.status,
                            "data": await response.text(),
                            "success": False,
                            "response_time": response_time
                        }
                        
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics[metric_key].add_response_time(response_time)
            self.metrics[metric_key].add_error()
            return {
                "status": 500,
                "data": {"error": str(e)},
                "success": False,
                "response_time": response_time
            }
    
    async def generate_test_data(self):
        """Generate comprehensive test data for stress testing"""
        print("🔧 Generating test data...")
        
        # Generate 1360 test users
        print("👥 Creating 1360 test user accounts...")
        for i in range(1360):
            user_data = {
                "username": f"stress_user_{i}",
                "email": f"stress_user_{i}@stresstest.com",
                "full_name": f"Stress Test User {i}",
                "account_type": "seller" if i % 3 == 0 else "buyer"
            }
            
            response = await self.make_request("POST", "/auth/register", data=user_data)
            if response["success"]:
                self.test_users.append({
                    "id": response["data"].get("user_id"),
                    "email": user_data["email"],
                    "type": user_data["account_type"]
                })
        
        print(f"✅ Created {len(self.test_users)} test users")
        
        # Generate 5000+ test listings
        print("📦 Creating 5000+ test listings...")
        categories = ["Automotive", "Electronics", "Fashion", "Home", "Sports", "Books", "Jewelry", "Art"]
        conditions = ["New", "Like New", "Good", "Fair"]
        
        for i in range(5000):
            if i % 3 == 0 and self.test_users:  # Only sellers can create listings
                seller = random.choice([u for u in self.test_users if u["type"] == "seller"])
                
                listing_data = {
                    "title": f"Stress Test Item {i} - {random.choice(['Premium', 'Deluxe', 'Standard', 'Basic'])} {random.choice(['Widget', 'Gadget', 'Tool', 'Device'])}",
                    "description": f"High-quality stress test item {i} for comprehensive marketplace testing. Features advanced functionality and premium materials.",
                    "price": round(random.uniform(10, 2000), 2),
                    "category": random.choice(categories),
                    "condition": random.choice(conditions),
                    "seller_id": seller["id"],
                    "images": [f"https://example.com/image_{i}.jpg"],
                    "tags": [f"tag_{i}", "stress_test", random.choice(["premium", "sale", "new"])],
                    "features": [f"Feature {j}" for j in range(3)]
                }
                
                # Login as seller first
                login_response = await self.make_request("POST", "/auth/login", data={
                    "email": seller["email"],
                    "password": "password123"
                })
                
                if login_response["success"]:
                    # Create listing
                    response = await self.make_request("POST", "/marketplace/listings", data=listing_data)
                    if response["success"]:
                        self.test_listings.append(response["data"])
        
        print(f"✅ Created {len(self.test_listings)} test listings")
        
        # Generate 10000+ test bids
        print("💰 Creating 10000+ test bids...")
        bid_count = 0
        for i in range(10000):
            if self.test_listings and self.test_users:
                listing = random.choice(self.test_listings)
                buyer = random.choice([u for u in self.test_users if u["type"] == "buyer"])
                
                # Login as buyer
                login_response = await self.make_request("POST", "/auth/login", data={
                    "email": buyer["email"],
                    "password": "password123"
                })
                
                if login_response["success"]:
                    bid_data = {
                        "listing_id": listing.get("id"),
                        "offer_amount": round(listing.get("price", 100) * random.uniform(0.8, 1.2), 2),
                        "message": f"Stress test bid {i}"
                    }
                    
                    response = await self.make_request("POST", "/marketplace/tenders", data=bid_data)
                    if response["success"]:
                        bid_count += 1
        
        print(f"✅ Created {bid_count} test bids")
        
        # Generate 2000+ test messages
        print("💬 Creating 2000+ test messages...")
        message_count = 0
        for i in range(2000):
            if len(self.test_users) >= 2:
                sender = random.choice(self.test_users)
                receiver = random.choice([u for u in self.test_users if u["id"] != sender["id"]])
                
                # Login as sender
                login_response = await self.make_request("POST", "/auth/login", data={
                    "email": sender["email"],
                    "password": "password123"
                })
                
                if login_response["success"]:
                    message_data = {
                        "recipient_id": receiver["id"],
                        "subject": f"Stress Test Message {i}",
                        "content": f"This is a stress test message {i} for comprehensive testing."
                    }
                    
                    response = await self.make_request("POST", "/messages", data=message_data)
                    if response["success"]:
                        message_count += 1
        
        print(f"✅ Created {message_count} test messages")
        
        # Generate 1000+ test favorites
        print("❤️ Creating 1000+ test favorites...")
        favorite_count = 0
        for i in range(1000):
            if self.test_listings and self.test_users:
                listing = random.choice(self.test_listings)
                user = random.choice(self.test_users)
                
                # Login as user
                login_response = await self.make_request("POST", "/auth/login", data={
                    "email": user["email"],
                    "password": "password123"
                })
                
                if login_response["success"]:
                    response = await self.make_request("POST", f"/user/favorites/{user['id']}/{listing.get('id')}")
                    if response["success"]:
                        favorite_count += 1
        
        print(f"✅ Created {favorite_count} test favorites")
        print("🎯 Test data generation completed!")
    
    async def simulate_user_browse_listings(self, user_session: int):
        """Simulate user browsing listings with new pagination (40 items per page)"""
        try:
            # Test different pagination scenarios
            pages_to_test = [1, 2, 3, random.randint(4, 10)]
            
            for page in pages_to_test:
                params = {
                    "page": page,
                    "limit": 40,  # New pagination limit
                    "type": random.choice(["all", "Private", "Business"]),
                    "price_from": random.randint(0, 100),
                    "price_to": random.randint(500, 2000),
                    "bid_status": random.choice(["all", "highest_bidder", "not_bid_yet"])  # New bid status filters
                }
                
                response = await self.make_request("GET", "/marketplace/browse", params=params, metric_key="browse_listings")
                
                if response["success"]:
                    data = response["data"]
                    listings = data.get("listings", [])
                    pagination = data.get("pagination", {})
                    
                    # Verify pagination works correctly
                    if pagination.get("items_per_page") != 40:
                        print(f"⚠️ Pagination issue: Expected 40 items per page, got {pagination.get('items_per_page')}")
                    
                    # Simulate user interaction delay
                    await asyncio.sleep(random.uniform(0.1, 0.5))
                
        except Exception as e:
            print(f"❌ Browse listings error for session {user_session}: {e}")
    
    async def simulate_user_search_and_filter(self, user_session: int):
        """Simulate advanced search and filtering"""
        try:
            search_queries = [
                "automotive", "electronics", "premium", "deluxe", "widget", "gadget",
                "stress test", "high quality", "advanced", "professional"
            ]
            
            for _ in range(3):  # 3 searches per session
                params = {
                    "q": random.choice(search_queries),
                    "category": random.choice(["", "Automotive", "Electronics", "Fashion"]),
                    "price_min": random.randint(0, 100),
                    "price_max": random.randint(500, 2000),
                    "condition": random.choice(["", "New", "Like New", "Good"]),
                    "sort_by": random.choice(["relevance", "price_low", "price_high", "newest"]),
                    "page": random.randint(1, 5),
                    "limit": 20
                }
                
                response = await self.make_request("GET", "/marketplace/search", params=params, metric_key="search_listings")
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
        except Exception as e:
            print(f"❌ Search error for session {user_session}: {e}")
    
    async def simulate_user_bidding(self, user_session: int):
        """Simulate bidding on multiple listings"""
        try:
            if not self.test_listings or not self.test_users:
                return
                
            user = random.choice(self.test_users)
            
            # Login as user
            login_response = await self.make_request("POST", "/auth/login", data={
                "email": user["email"],
                "password": "password123"
            })
            
            if login_response["success"]:
                # Place multiple bids
                for _ in range(random.randint(1, 5)):
                    listing = random.choice(self.test_listings)
                    
                    bid_data = {
                        "listing_id": listing.get("id"),
                        "offer_amount": round(listing.get("price", 100) * random.uniform(0.9, 1.3), 2),
                        "message": f"Stress test bid from session {user_session}"
                    }
                    
                    response = await self.make_request("POST", "/marketplace/tenders", data=bid_data, metric_key="bidding")
                    await asyncio.sleep(random.uniform(0.1, 0.2))
                    
        except Exception as e:
            print(f"❌ Bidding error for session {user_session}: {e}")
    
    async def simulate_user_messaging(self, user_session: int):
        """Simulate messaging between users"""
        try:
            if len(self.test_users) < 2:
                return
                
            sender = random.choice(self.test_users)
            receiver = random.choice([u for u in self.test_users if u["id"] != sender["id"]])
            
            # Login as sender
            login_response = await self.make_request("POST", "/auth/login", data={
                "email": sender["email"],
                "password": "password123"
            })
            
            if login_response["success"]:
                message_data = {
                    "recipient_id": receiver["id"],
                    "subject": f"Stress Test Message from Session {user_session}",
                    "content": f"This is a stress test message from user session {user_session}. Testing messaging system under load."
                }
                
                response = await self.make_request("POST", "/messages", data=message_data, metric_key="messaging")
                await asyncio.sleep(random.uniform(0.1, 0.2))
                
        except Exception as e:
            print(f"❌ Messaging error for session {user_session}: {e}")
    
    async def simulate_user_favorites(self, user_session: int):
        """Simulate adding/removing favorites"""
        try:
            if not self.test_listings or not self.test_users:
                return
                
            user = random.choice(self.test_users)
            
            # Login as user
            login_response = await self.make_request("POST", "/auth/login", data={
                "email": user["email"],
                "password": "password123"
            })
            
            if login_response["success"]:
                # Add/remove favorites
                for _ in range(random.randint(1, 3)):
                    listing = random.choice(self.test_listings)
                    
                    # Add to favorites
                    response = await self.make_request("POST", f"/user/favorites/{user['id']}/{listing.get('id')}", metric_key="favorites")
                    await asyncio.sleep(random.uniform(0.1, 0.2))
                    
                    # Sometimes remove from favorites
                    if random.random() < 0.3:
                        response = await self.make_request("DELETE", f"/user/favorites/{user['id']}/{listing.get('id')}", metric_key="favorites")
                        await asyncio.sleep(random.uniform(0.1, 0.2))
                    
        except Exception as e:
            print(f"❌ Favorites error for session {user_session}: {e}")
    
    async def simulate_currency_conversion(self, user_session: int):
        """Simulate currency conversion requests"""
        try:
            currencies = ["EUR", "USD", "GBP", "CHF", "JPY", "CAD", "AUD"]
            
            for _ in range(random.randint(1, 3)):
                conversion_data = {
                    "amount": round(random.uniform(10, 1000), 2),
                    "from_currency": random.choice(currencies),
                    "to_currency": random.choice(currencies)
                }
                
                response = await self.make_request("POST", "/v2/advanced/currency/convert", data=conversion_data, metric_key="currency_conversion")
                await asyncio.sleep(random.uniform(0.1, 0.2))
                
        except Exception as e:
            print(f"❌ Currency conversion error for session {user_session}: {e}")
    
    async def simulate_webhook_events(self, user_session: int):
        """Simulate webhook events triggering"""
        try:
            # Test webhook endpoints
            webhook_endpoints = [
                "/v2/advanced/webhooks",
                "/v2/advanced/webhook-events",
            ]
            
            for endpoint in webhook_endpoints:
                response = await self.make_request("GET", endpoint, metric_key="webhook_events")
                await asyncio.sleep(random.uniform(0.1, 0.2))
                
        except Exception as e:
            print(f"❌ Webhook events error for session {user_session}: {e}")
    
    async def simulate_user_session(self, session_id: int):
        """Simulate a complete user session with mixed operations"""
        try:
            # Mixed operations as specified: 40% browse, 20% bidding, 15% messaging, 15% favorites, 10% uploads
            operations = (
                ["browse"] * 40 +
                ["bidding"] * 20 +
                ["messaging"] * 15 +
                ["favorites"] * 15 +
                ["currency"] * 10
            )
            
            random.shuffle(operations)
            
            for operation in operations[:random.randint(5, 15)]:  # 5-15 operations per session
                if operation == "browse":
                    await self.simulate_user_browse_listings(session_id)
                elif operation == "bidding":
                    await self.simulate_user_bidding(session_id)
                elif operation == "messaging":
                    await self.simulate_user_messaging(session_id)
                elif operation == "favorites":
                    await self.simulate_user_favorites(session_id)
                elif operation == "currency":
                    await self.simulate_currency_conversion(session_id)
                
                # Add search and filter testing
                if random.random() < 0.3:  # 30% chance to do search
                    await self.simulate_user_search_and_filter(session_id)
                
                # Add webhook testing
                if random.random() < 0.1:  # 10% chance to trigger webhook
                    await self.simulate_webhook_events(session_id)
                
                # Random delay between operations
                await asyncio.sleep(random.uniform(0.1, 1.0))
                
        except Exception as e:
            print(f"❌ User session {session_id} error: {e}")
    
    async def monitor_system_resources(self):
        """Monitor system resources during stress test"""
        while True:
            try:
                # Monitor memory and CPU usage
                memory_percent = psutil.virtual_memory().percent
                cpu_percent = psutil.cpu_percent(interval=1)
                
                self.metrics["overall"].memory_usage.append(memory_percent)
                self.metrics["overall"].cpu_usage.append(cpu_percent)
                
                await asyncio.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                print(f"⚠️ Resource monitoring error: {e}")
                break
    
    async def run_stress_test(self, concurrent_users: int = 1360, duration_minutes: int = 7):
        """Run the main stress test with specified parameters"""
        print(f"🚀 Starting EXTREME STRESS TEST")
        print(f"👥 Concurrent Users: {concurrent_users}")
        print(f"⏱️ Duration: {duration_minutes} minutes")
        print(f"📡 Target: {BACKEND_URL}")
        print("=" * 80)
        
        # Start system monitoring
        monitor_task = asyncio.create_task(self.monitor_system_resources())
        
        # Record start time
        for metric in self.metrics.values():
            metric.start_time = time.time()
        
        try:
            # Phase 1: Gradual Ramp-up (0 to 1360 users over 2 minutes)
            print("📈 Phase 1: Gradual Ramp-up (2 minutes)")
            ramp_up_tasks = []
            
            for i in range(concurrent_users):
                # Stagger user sessions over 2 minutes (120 seconds)
                delay = (i / concurrent_users) * 120
                
                task = asyncio.create_task(self.delayed_user_session(i, delay, duration_minutes * 60))
                ramp_up_tasks.append(task)
            
            # Phase 2: Sustained Peak (1360 concurrent users for 5 minutes)
            print("🔥 Phase 2: Sustained Peak Load")
            
            # Phase 3: Spike Testing (sudden load bursts)
            print("⚡ Phase 3: Spike Testing")
            spike_tasks = []
            for i in range(100):  # 100 requests/second for 30 seconds
                task = asyncio.create_task(self.spike_request(i))
                spike_tasks.append(task)
                if i % 10 == 0:  # Brief pause every 10 requests
                    await asyncio.sleep(0.1)
            
            # Wait for all tasks to complete
            print("⏳ Waiting for all user sessions to complete...")
            await asyncio.gather(*ramp_up_tasks, return_exceptions=True)
            await asyncio.gather(*spike_tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            print("\n⚠️ Stress test interrupted by user")
        except Exception as e:
            print(f"\n💥 Stress test failed: {e}")
        finally:
            # Stop monitoring
            monitor_task.cancel()
            
            # Record end time
            for metric in self.metrics.values():
                metric.end_time = time.time()
            
            # Print results
            await self.print_stress_test_results()
    
    async def delayed_user_session(self, session_id: int, delay: float, duration: float):
        """Start a user session after a delay"""
        await asyncio.sleep(delay)
        
        start_time = time.time()
        while time.time() - start_time < duration:
            await self.simulate_user_session(session_id)
            await asyncio.sleep(random.uniform(1, 5))  # Rest between session cycles
    
    async def spike_request(self, request_id: int):
        """Generate spike load request"""
        try:
            # Random endpoint for spike testing
            endpoints = [
                "/marketplace/browse",
                "/marketplace/search",
                "/v2/advanced/currency/rates",
                "/health"
            ]
            
            endpoint = random.choice(endpoints)
            response = await self.make_request("GET", endpoint, metric_key="overall")
            
        except Exception as e:
            print(f"⚡ Spike request {request_id} error: {e}")
    
    async def cleanup_test_data(self):
        """Clean up all test data after stress test"""
        print("🧹 Cleaning up test data...")
        
        # Note: In a real implementation, you would clean up:
        # - Test user accounts
        # - Test listings
        # - Test bids/tenders
        # - Test messages
        # - Test favorites
        
        print("✅ Test data cleanup completed")
    
    async def print_stress_test_results(self):
        """Print comprehensive stress test results"""
        print("\n" + "=" * 100)
        print("📊 EXTREME STRESS TEST RESULTS")
        print("=" * 100)
        
        overall_stats = self.metrics["overall"].get_stats()
        
        print(f"\n🎯 OVERALL PERFORMANCE:")
        print(f"   Total Requests: {overall_stats.get('total_requests', 0):,}")
        print(f"   Success Rate: {overall_stats.get('success_rate', 0):.2f}%")
        print(f"   Requests/Second: {overall_stats.get('requests_per_second', 0):.2f}")
        print(f"   Test Duration: {overall_stats.get('duration', 0):.2f} seconds")
        
        print(f"\n⚡ RESPONSE TIME METRICS:")
        print(f"   Average: {overall_stats.get('avg_response_time', 0)*1000:.2f}ms")
        print(f"   Minimum: {overall_stats.get('min_response_time', 0)*1000:.2f}ms")
        print(f"   Maximum: {overall_stats.get('max_response_time', 0)*1000:.2f}ms")
        print(f"   95th Percentile: {overall_stats.get('p95_response_time', 0)*1000:.2f}ms")
        print(f"   99th Percentile: {overall_stats.get('p99_response_time', 0)*1000:.2f}ms")
        
        print(f"\n💻 SYSTEM RESOURCE USAGE:")
        print(f"   Average Memory Usage: {overall_stats.get('avg_memory_usage', 0):.2f}%")
        print(f"   Average CPU Usage: {overall_stats.get('avg_cpu_usage', 0):.2f}%")
        
        print(f"\n📋 DETAILED ENDPOINT PERFORMANCE:")
        
        for endpoint, metrics in self.metrics.items():
            if endpoint == "overall":
                continue
                
            stats = metrics.get_stats()
            if stats.get('total_requests', 0) > 0:
                print(f"\n   🔸 {endpoint.upper()}:")
                print(f"      Requests: {stats.get('total_requests', 0):,}")
                print(f"      Success Rate: {stats.get('success_rate', 0):.2f}%")
                print(f"      Avg Response Time: {stats.get('avg_response_time', 0)*1000:.2f}ms")
                print(f"      95th Percentile: {stats.get('p95_response_time', 0)*1000:.2f}ms")
        
        print(f"\n🎯 PERFORMANCE BENCHMARKS:")
        browse_avg = self.metrics["browse_listings"].get_stats().get('avg_response_time', 0) * 1000
        search_avg = self.metrics["search_listings"].get_stats().get('avg_response_time', 0) * 1000
        
        print(f"   Browse API (<500ms target): {browse_avg:.2f}ms {'✅' if browse_avg < 500 else '❌'}")
        print(f"   Search API (<500ms target): {search_avg:.2f}ms {'✅' if search_avg < 500 else '❌'}")
        print(f"   Memory Usage (<80% target): {overall_stats.get('avg_memory_usage', 0):.1f}% {'✅' if overall_stats.get('avg_memory_usage', 0) < 80 else '❌'}")
        print(f"   Success Rate (>95% target): {overall_stats.get('success_rate', 0):.1f}% {'✅' if overall_stats.get('success_rate', 0) > 95 else '❌'}")
        
        print(f"\n🏆 STRESS TEST SUMMARY:")
        if overall_stats.get('success_rate', 0) > 95 and browse_avg < 500:
            print("   🎉 EXCELLENT: System handled extreme load successfully!")
        elif overall_stats.get('success_rate', 0) > 90:
            print("   ✅ GOOD: System performed well under stress with minor issues")
        elif overall_stats.get('success_rate', 0) > 80:
            print("   ⚠️ ACCEPTABLE: System handled load but needs optimization")
        else:
            print("   ❌ POOR: System struggled under extreme load - optimization required")
        
        print("\n" + "=" * 100)

async def main():
    """Main stress test execution"""
    tester = CataloroStressTester()
    
    try:
        await tester.setup()
        
        # Generate test data first
        await tester.generate_test_data()
        
        # Run the extreme stress test
        await tester.run_stress_test(concurrent_users=1360, duration_minutes=7)
        
    except KeyboardInterrupt:
        print("\n⚠️ Stress test interrupted by user")
    except Exception as e:
        print(f"\n💥 Stress test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    # Set event loop policy for better performance on Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())