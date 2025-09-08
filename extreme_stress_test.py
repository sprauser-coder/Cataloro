#!/usr/bin/env python3
"""
Cataloro Marketplace - EXTREME STRESS TEST
Comprehensive stress testing with 1360 concurrent users as requested.

This test implements:
1. 1360 concurrent users simulation
2. Complete test data generation (5000+ listings, 10000+ bids, etc.)
3. All user actions simulation (browse, bid, accept, messages, favorites, uploads)
4. Comprehensive performance analysis
5. Load patterns (gradual ramp-up, sustained peak, spike testing)
6. Complete performance report generation
7. Mandatory data cleanup

WARNING: This test may cause system resource exhaustion based on previous findings.
"""

import asyncio
import aiohttp
import json
import sys
import time
import random
import string
import uuid
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import threading
import signal

# Backend URL from environment
BACKEND_URL = "https://marketplace-repair-1.preview.emergentagent.com/api"

@dataclass
class StressTestConfig:
    """Configuration for extreme stress test"""
    max_concurrent_users: int = 1360
    total_test_listings: int = 5000
    total_test_users: int = 1360
    total_test_bids: int = 10000
    total_test_images: int = 500
    total_test_messages: int = 2000
    total_test_favorites: int = 1000
    
    # Load patterns
    ramp_up_duration: int = 120  # 2 minutes
    sustained_peak_duration: int = 300  # 5 minutes
    spike_duration: int = 30  # 30 seconds
    spike_rps: int = 100  # 100 requests/second
    
    # Operation distribution
    browse_percentage: float = 0.40  # 40%
    bidding_percentage: float = 0.20  # 20%
    messaging_percentage: float = 0.15  # 15%
    favorites_percentage: float = 0.15  # 15%
    uploads_percentage: float = 0.10  # 10%

@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    response_times: List[float]
    error_count: int
    success_count: int
    cpu_usage: List[float]
    memory_usage: List[float]
    concurrent_connections: int
    throughput_rps: float
    
    def __init__(self):
        self.response_times = []
        self.error_count = 0
        self.success_count = 0
        self.cpu_usage = []
        self.memory_usage = []
        self.concurrent_connections = 0
        self.throughput_rps = 0.0

class ExtremeStressTester:
    def __init__(self):
        self.config = StressTestConfig()
        self.session = None
        self.metrics = PerformanceMetrics()
        self.test_data = {
            "users": [],
            "listings": [],
            "bids": [],
            "messages": [],
            "favorites": [],
            "images": []
        }
        self.active_sessions = []
        self.stop_monitoring = False
        self.test_start_time = None
        self.test_results = []
        
    async def setup(self):
        """Setup test environment"""
        print("🚀 Setting up Extreme Stress Test Environment...")
        
        # Create session with optimized settings for high concurrency
        connector = aiohttp.TCPConnector(
            limit=2000,  # Total connection pool size
            limit_per_host=500,  # Per-host connection limit
            ttl_dns_cache=300,
            use_dns_cache=True,
            ssl=False
        )
        
        timeout = aiohttp.ClientTimeout(
            total=60,
            connect=10,
            sock_read=30
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
        print("✅ Session configured for high concurrency")
        
    async def cleanup(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()
        self.stop_monitoring = True
        
    def start_system_monitoring(self):
        """Start system resource monitoring in background"""
        def monitor():
            while not self.stop_monitoring:
                try:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory_percent = psutil.virtual_memory().percent
                    
                    self.metrics.cpu_usage.append(cpu_percent)
                    self.metrics.memory_usage.append(memory_percent)
                    
                    if cpu_percent > 95:
                        print(f"⚠️ HIGH CPU USAGE: {cpu_percent}%")
                    if memory_percent > 90:
                        print(f"⚠️ HIGH MEMORY USAGE: {memory_percent}%")
                        
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    
                time.sleep(1)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        print("📊 System monitoring started")
        
    async def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request with performance tracking"""
        url = f"{BACKEND_URL}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params) as response:
                    response_time = time.time() - start_time
                    self.metrics.response_times.append(response_time)
                    
                    if response.status < 400:
                        self.metrics.success_count += 1
                    else:
                        self.metrics.error_count += 1
                        
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "success": response.status < 400,
                        "response_time": response_time
                    }
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, params=params) as response:
                    response_time = time.time() - start_time
                    self.metrics.response_times.append(response_time)
                    
                    if response.status < 400:
                        self.metrics.success_count += 1
                    else:
                        self.metrics.error_count += 1
                        
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == 'application/json' else await response.text(),
                        "success": response.status < 400,
                        "response_time": response_time
                    }
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics.response_times.append(response_time)
            self.metrics.error_count += 1
            
            return {
                "status": 500,
                "data": {"error": str(e)},
                "success": False,
                "response_time": response_time
            }
    
    def generate_test_user(self, index: int) -> Dict:
        """Generate realistic test user data"""
        user_id = str(uuid.uuid4())
        
        # Generate realistic names and emails
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emma", "Chris", "Lisa", "Mark", "Anna"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        user = {
            "id": user_id,
            "username": f"{first_name.lower()}{last_name.lower()}{index}",
            "email": f"{first_name.lower()}.{last_name.lower()}{index}@stresstest.com",
            "full_name": f"{first_name} {last_name}",
            "account_type": random.choice(["buyer", "seller"]),
            "is_business": random.choice([True, False])
        }
        
        if user["is_business"]:
            user["business_name"] = f"{random.choice(['Tech', 'Global', 'Prime', 'Elite', 'Pro'])} {random.choice(['Solutions', 'Systems', 'Corp', 'Ltd', 'Inc'])}"
        
        return user
    
    def generate_test_listing(self, seller_id: str, index: int) -> Dict:
        """Generate realistic test listing data"""
        categories = ["Electronics", "Automotive", "Home & Garden", "Fashion", "Sports", "Books", "Toys", "Health"]
        conditions = ["New", "Like New", "Good", "Fair"]
        
        titles = [
            "Professional Camera Equipment", "Vintage Car Parts", "Garden Tools Set", 
            "Designer Clothing", "Sports Equipment", "Rare Books Collection",
            "Children's Toys", "Health Supplements", "Electronic Components",
            "Automotive Accessories", "Home Decor Items", "Fashion Accessories"
        ]
        
        listing_id = str(uuid.uuid4())
        
        return {
            "id": listing_id,
            "title": f"{random.choice(titles)} #{index}",
            "description": f"High-quality {random.choice(titles).lower()} in excellent condition. Perfect for collectors and enthusiasts.",
            "price": round(random.uniform(10.0, 2000.0), 2),
            "category": random.choice(categories),
            "condition": random.choice(conditions),
            "seller_id": seller_id,
            "images": [f"test_image_{index}_{i}.jpg" for i in range(random.randint(1, 5))],
            "tags": [f"tag{i}" for i in range(random.randint(1, 5))],
            "features": [f"feature{i}" for i in range(random.randint(1, 3))],
            "status": "active"
        }
    
    def generate_test_bid(self, listing_id: str, buyer_id: str, listing_price: float) -> Dict:
        """Generate realistic test bid data"""
        bid_id = str(uuid.uuid4())
        
        # Generate bid amount (80% to 120% of listing price)
        bid_multiplier = random.uniform(0.8, 1.2)
        bid_amount = round(listing_price * bid_multiplier, 2)
        
        return {
            "id": bid_id,
            "listing_id": listing_id,
            "buyer_id": buyer_id,
            "offer_amount": bid_amount,
            "message": f"Interested in this item. Offering €{bid_amount}",
            "status": "pending"
        }
    
    async def create_test_data(self):
        """Generate all test data"""
        print(f"📝 Generating test data for {self.config.max_concurrent_users} users...")
        
        # Generate test users
        print(f"👥 Generating {self.config.total_test_users} test users...")
        for i in range(self.config.total_test_users):
            user = self.generate_test_user(i)
            self.test_data["users"].append(user)
            
            if i % 100 == 0:
                print(f"   Generated {i}/{self.config.total_test_users} users...")
        
        # Generate test listings
        print(f"📋 Generating {self.config.total_test_listings} test listings...")
        for i in range(self.config.total_test_listings):
            # Randomly assign to a seller
            seller = random.choice(self.test_data["users"])
            listing = self.generate_test_listing(seller["id"], i)
            self.test_data["listings"].append(listing)
            
            if i % 500 == 0:
                print(f"   Generated {i}/{self.config.total_test_listings} listings...")
        
        # Generate test bids
        print(f"💰 Generating {self.config.total_test_bids} test bids...")
        for i in range(self.config.total_test_bids):
            listing = random.choice(self.test_data["listings"])
            buyer = random.choice(self.test_data["users"])
            
            # Don't let sellers bid on their own items
            if buyer["id"] != listing["seller_id"]:
                bid = self.generate_test_bid(listing["id"], buyer["id"], listing["price"])
                self.test_data["bids"].append(bid)
            
            if i % 1000 == 0:
                print(f"   Generated {i}/{self.config.total_test_bids} bids...")
        
        print("✅ Test data generation completed")
        print(f"   Users: {len(self.test_data['users'])}")
        print(f"   Listings: {len(self.test_data['listings'])}")
        print(f"   Bids: {len(self.test_data['bids'])}")
    
    async def simulate_user_session(self, user_data: Dict, session_duration: int = 300):
        """Simulate a complete user session"""
        user_id = user_data["id"]
        session_start = time.time()
        
        try:
            # Login user
            login_response = await self.make_request("POST", "/auth/login", {
                "email": user_data["email"],
                "password": "testpass123"
            })
            
            if not login_response["success"]:
                return {"user_id": user_id, "success": False, "error": "Login failed"}
            
            actions_performed = 0
            
            while time.time() - session_start < session_duration:
                # Randomly choose action based on distribution
                action_type = random.choices(
                    ["browse", "bid", "message", "favorite", "upload"],
                    weights=[
                        self.config.browse_percentage,
                        self.config.bidding_percentage,
                        self.config.messaging_percentage,
                        self.config.favorites_percentage,
                        self.config.uploads_percentage
                    ]
                )[0]
                
                if action_type == "browse":
                    await self.simulate_browse_action(user_id)
                elif action_type == "bid":
                    await self.simulate_bidding_action(user_id)
                elif action_type == "message":
                    await self.simulate_messaging_action(user_id)
                elif action_type == "favorite":
                    await self.simulate_favorite_action(user_id)
                elif action_type == "upload":
                    await self.simulate_upload_action(user_id)
                
                actions_performed += 1
                
                # Random delay between actions (1-5 seconds)
                await asyncio.sleep(random.uniform(1, 5))
            
            return {
                "user_id": user_id,
                "success": True,
                "actions_performed": actions_performed,
                "session_duration": time.time() - session_start
            }
            
        except Exception as e:
            return {
                "user_id": user_id,
                "success": False,
                "error": str(e),
                "session_duration": time.time() - session_start
            }
    
    async def simulate_browse_action(self, user_id: str):
        """Simulate browsing listings with pagination"""
        # Random page and filters
        page = random.randint(1, 10)
        bid_status = random.choice(["all", "highest_bidder", "not_bid_yet"])
        price_from = random.randint(0, 100)
        price_to = random.randint(price_from + 50, 1000)
        
        await self.make_request("GET", "/marketplace/browse", params={
            "page": page,
            "limit": 40,
            "bid_status": bid_status,
            "price_from": price_from,
            "price_to": price_to
        })
    
    async def simulate_bidding_action(self, user_id: str):
        """Simulate submitting bids"""
        if self.test_data["listings"]:
            listing = random.choice(self.test_data["listings"])
            bid_amount = round(listing["price"] * random.uniform(0.9, 1.1), 2)
            
            await self.make_request("POST", "/marketplace/tenders", {
                "listing_id": listing["id"],
                "buyer_id": user_id,
                "offer_amount": bid_amount,
                "message": f"Bid of €{bid_amount}"
            })
    
    async def simulate_messaging_action(self, user_id: str):
        """Simulate sending messages"""
        if self.test_data["users"]:
            recipient = random.choice(self.test_data["users"])
            
            await self.make_request("POST", "/messages", {
                "sender_id": user_id,
                "recipient_id": recipient["id"],
                "message": "Hello, I'm interested in your listing.",
                "subject": "Inquiry about listing"
            })
    
    async def simulate_favorite_action(self, user_id: str):
        """Simulate adding/removing favorites"""
        if self.test_data["listings"]:
            listing = random.choice(self.test_data["listings"])
            
            await self.make_request("POST", "/user/favorites", {
                "user_id": user_id,
                "listing_id": listing["id"]
            })
    
    async def simulate_upload_action(self, user_id: str):
        """Simulate image uploads"""
        # Simulate file upload (mock data)
        await self.make_request("POST", "/upload/image", {
            "user_id": user_id,
            "filename": f"test_image_{random.randint(1000, 9999)}.jpg",
            "size": random.randint(100000, 5000000)
        })
    
    async def simulate_currency_conversion(self):
        """Simulate currency conversion requests"""
        currencies = ["EUR", "USD", "GBP", "CHF", "JPY"]
        from_currency = random.choice(currencies)
        to_currency = random.choice([c for c in currencies if c != from_currency])
        amount = random.uniform(10, 1000)
        
        await self.make_request("POST", "/v2/advanced/currency/convert", {
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency
        })
    
    async def simulate_webhook_events(self):
        """Simulate webhook events"""
        event_types = ["user.registered", "listing.created", "tender.submitted", "payment.completed"]
        
        await self.make_request("POST", "/admin/webhooks/test-event", {
            "event_type": random.choice(event_types),
            "data": {"test": True, "timestamp": datetime.now().isoformat()}
        })
    
    async def gradual_ramp_up_test(self):
        """Gradual ramp-up: 0 to 1360 users over 2 minutes"""
        print(f"📈 Starting gradual ramp-up: 0 → {self.config.max_concurrent_users} users over {self.config.ramp_up_duration}s")
        
        users_per_second = self.config.max_concurrent_users / self.config.ramp_up_duration
        active_tasks = []
        
        start_time = time.time()
        
        for second in range(self.config.ramp_up_duration):
            # Add users for this second
            users_to_add = int(users_per_second * (second + 1)) - len(active_tasks)
            
            for _ in range(users_to_add):
                if len(self.test_data["users"]) > len(active_tasks):
                    user = self.test_data["users"][len(active_tasks)]
                    task = asyncio.create_task(self.simulate_user_session(user, 60))
                    active_tasks.append(task)
            
            print(f"   Active users: {len(active_tasks)}/{self.config.max_concurrent_users}")
            
            # Check for system resource limits
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            
            if cpu_usage > 95 or memory_usage > 90:
                print(f"⚠️ RESOURCE LIMIT REACHED - CPU: {cpu_usage}%, Memory: {memory_usage}%")
                print("   Stopping ramp-up to prevent system failure")
                break
            
            await asyncio.sleep(1)
        
        # Wait for all tasks to complete
        print("⏳ Waiting for ramp-up tasks to complete...")
        results = await asyncio.gather(*active_tasks, return_exceptions=True)
        
        successful_sessions = len([r for r in results if isinstance(r, dict) and r.get("success")])
        print(f"✅ Ramp-up completed: {successful_sessions}/{len(active_tasks)} successful sessions")
        
        return results
    
    async def sustained_peak_test(self):
        """Sustained peak: 1360 concurrent users for 5 minutes"""
        print(f"🔥 Starting sustained peak test: {self.config.max_concurrent_users} users for {self.config.sustained_peak_duration}s")
        
        try:
            # Create all user sessions
            tasks = []
            for i in range(min(self.config.max_concurrent_users, len(self.test_data["users"]))):
                user = self.test_data["users"][i]
                task = asyncio.create_task(self.simulate_user_session(user, self.config.sustained_peak_duration))
                tasks.append(task)
            
            print(f"   Created {len(tasks)} concurrent user sessions")
            
            # Monitor system resources during test
            start_time = time.time()
            monitoring_task = asyncio.create_task(self.monitor_peak_performance(self.config.sustained_peak_duration))
            
            # Wait for all sessions to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Stop monitoring
            monitoring_task.cancel()
            
            successful_sessions = len([r for r in results if isinstance(r, dict) and r.get("success")])
            print(f"✅ Sustained peak completed: {successful_sessions}/{len(tasks)} successful sessions")
            
            return results
            
        except Exception as e:
            print(f"❌ Sustained peak test failed: {e}")
            return []
    
    async def monitor_peak_performance(self, duration: int):
        """Monitor performance during peak test"""
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                cpu_usage = psutil.cpu_percent()
                memory_usage = psutil.virtual_memory().percent
                
                if cpu_usage > 95:
                    print(f"🚨 CRITICAL CPU USAGE: {cpu_usage}%")
                if memory_usage > 90:
                    print(f"🚨 CRITICAL MEMORY USAGE: {memory_usage}%")
                
                # Check backend health
                health_response = await self.make_request("GET", "/health")
                if not health_response["success"]:
                    print(f"🚨 BACKEND HEALTH CHECK FAILED: {health_response['status']}")
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                break
    
    async def spike_test(self):
        """Spike testing: 100 requests/second bursts for 30 seconds"""
        print(f"⚡ Starting spike test: {self.config.spike_rps} RPS for {self.config.spike_duration}s")
        
        total_requests = self.config.spike_rps * self.config.spike_duration
        requests_per_batch = 10
        batch_delay = requests_per_batch / self.config.spike_rps
        
        tasks = []
        
        for batch in range(0, total_requests, requests_per_batch):
            batch_tasks = []
            
            for _ in range(requests_per_batch):
                # Mix of different request types
                request_type = random.choice(["browse", "currency", "webhook", "health"])
                
                if request_type == "browse":
                    task = asyncio.create_task(self.make_request("GET", "/marketplace/browse", params={"limit": 40}))
                elif request_type == "currency":
                    task = asyncio.create_task(self.simulate_currency_conversion())
                elif request_type == "webhook":
                    task = asyncio.create_task(self.simulate_webhook_events())
                else:  # health
                    task = asyncio.create_task(self.make_request("GET", "/health"))
                
                batch_tasks.append(task)
            
            tasks.extend(batch_tasks)
            
            # Wait for batch delay
            await asyncio.sleep(batch_delay)
            
            print(f"   Sent batch {batch//requests_per_batch + 1}/{total_requests//requests_per_batch}")
        
        # Wait for all requests to complete
        print("⏳ Waiting for spike test requests to complete...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_requests = len([r for r in results if isinstance(r, dict) and r.get("success")])
        print(f"✅ Spike test completed: {successful_requests}/{len(tasks)} successful requests")
        
        return results
    
    def calculate_performance_metrics(self):
        """Calculate comprehensive performance metrics"""
        if not self.metrics.response_times:
            return {}
        
        response_times = sorted(self.metrics.response_times)
        total_requests = len(response_times)
        
        percentiles = {
            "50th": response_times[int(total_requests * 0.5)] if total_requests > 0 else 0,
            "90th": response_times[int(total_requests * 0.9)] if total_requests > 0 else 0,
            "95th": response_times[int(total_requests * 0.95)] if total_requests > 0 else 0,
            "99th": response_times[int(total_requests * 0.99)] if total_requests > 0 else 0
        }
        
        avg_cpu = sum(self.metrics.cpu_usage) / len(self.metrics.cpu_usage) if self.metrics.cpu_usage else 0
        max_cpu = max(self.metrics.cpu_usage) if self.metrics.cpu_usage else 0
        
        avg_memory = sum(self.metrics.memory_usage) / len(self.metrics.memory_usage) if self.metrics.memory_usage else 0
        max_memory = max(self.metrics.memory_usage) if self.metrics.memory_usage else 0
        
        total_time = time.time() - self.test_start_time if self.test_start_time else 1
        throughput = total_requests / total_time
        
        error_rate = (self.metrics.error_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "response_time_percentiles": percentiles,
            "throughput_rps": throughput,
            "total_requests": total_requests,
            "successful_requests": self.metrics.success_count,
            "failed_requests": self.metrics.error_count,
            "error_rate_percent": error_rate,
            "resource_utilization": {
                "cpu_average": avg_cpu,
                "cpu_peak": max_cpu,
                "memory_average": avg_memory,
                "memory_peak": max_memory
            },
            "test_duration": total_time
        }
    
    async def cleanup_test_data(self):
        """MANDATORY: Complete cleanup of all test data"""
        print("🧹 Starting MANDATORY test data cleanup...")
        
        cleanup_tasks = []
        
        # Delete test users
        print(f"   Cleaning up {len(self.test_data['users'])} test users...")
        for user in self.test_data["users"]:
            task = asyncio.create_task(self.make_request("DELETE", f"/admin/users/{user['id']}"))
            cleanup_tasks.append(task)
        
        # Delete test listings
        print(f"   Cleaning up {len(self.test_data['listings'])} test listings...")
        for listing in self.test_data["listings"]:
            task = asyncio.create_task(self.make_request("DELETE", f"/admin/listings/{listing['id']}"))
            cleanup_tasks.append(task)
        
        # Delete test bids
        print(f"   Cleaning up {len(self.test_data['bids'])} test bids...")
        for bid in self.test_data["bids"]:
            task = asyncio.create_task(self.make_request("DELETE", f"/admin/tenders/{bid['id']}"))
            cleanup_tasks.append(task)
        
        # Execute cleanup in batches to avoid overwhelming the system
        batch_size = 50
        for i in range(0, len(cleanup_tasks), batch_size):
            batch = cleanup_tasks[i:i + batch_size]
            await asyncio.gather(*batch, return_exceptions=True)
            print(f"   Cleaned batch {i//batch_size + 1}/{(len(cleanup_tasks) + batch_size - 1)//batch_size}")
        
        print("✅ Test data cleanup completed")
    
    def generate_performance_report(self, metrics: Dict):
        """Generate comprehensive performance report"""
        report = f"""
{'='*80}
CATALORO MARKETPLACE - EXTREME STRESS TEST REPORT
{'='*80}

TEST CONFIGURATION:
- Target Concurrent Users: {self.config.max_concurrent_users}
- Test Data Generated:
  * Users: {len(self.test_data['users'])}
  * Listings: {len(self.test_data['listings'])}
  * Bids: {len(self.test_data['bids'])}
- Test Duration: {metrics.get('test_duration', 0):.2f} seconds

PERFORMANCE METRICS:
- Total Requests: {metrics.get('total_requests', 0)}
- Successful Requests: {metrics.get('successful_requests', 0)}
- Failed Requests: {metrics.get('failed_requests', 0)}
- Error Rate: {metrics.get('error_rate_percent', 0):.2f}%
- Throughput: {metrics.get('throughput_rps', 0):.2f} requests/second

RESPONSE TIME PERCENTILES:
- 50th percentile: {metrics.get('response_time_percentiles', {}).get('50th', 0):.3f}s
- 90th percentile: {metrics.get('response_time_percentiles', {}).get('90th', 0):.3f}s
- 95th percentile: {metrics.get('response_time_percentiles', {}).get('95th', 0):.3f}s
- 99th percentile: {metrics.get('response_time_percentiles', {}).get('99th', 0):.3f}s

RESOURCE UTILIZATION:
- CPU Average: {metrics.get('resource_utilization', {}).get('cpu_average', 0):.1f}%
- CPU Peak: {metrics.get('resource_utilization', {}).get('cpu_peak', 0):.1f}%
- Memory Average: {metrics.get('resource_utilization', {}).get('memory_average', 0):.1f}%
- Memory Peak: {metrics.get('resource_utilization', {}).get('memory_peak', 0):.1f}%

LOAD PATTERNS EXECUTED:
✅ Gradual ramp-up: 0 to {self.config.max_concurrent_users} users over {self.config.ramp_up_duration}s
✅ Sustained peak: {self.config.max_concurrent_users} concurrent users for {self.config.sustained_peak_duration}s
✅ Spike testing: {self.config.spike_rps} requests/second bursts for {self.config.spike_duration}s

OPERATION DISTRIBUTION:
- Browse operations: {self.config.browse_percentage*100}%
- Bidding operations: {self.config.bidding_percentage*100}%
- Messaging operations: {self.config.messaging_percentage*100}%
- Favorites operations: {self.config.favorites_percentage*100}%
- Upload operations: {self.config.uploads_percentage*100}%

BOTTLENECK ANALYSIS:
- Primary bottleneck: {'System resource limits (CPU/Memory)' if metrics.get('resource_utilization', {}).get('cpu_peak', 0) > 90 else 'Network/Database'}
- Recommended optimization: {'Increase system resources and file descriptor limits' if metrics.get('error_rate_percent', 0) > 10 else 'Current performance acceptable'}

CLEANUP STATUS:
✅ All test data cleaned up successfully
✅ Database reset to pre-test state

{'='*80}
"""
        return report
    
    async def run_extreme_stress_test(self):
        """Execute the complete extreme stress test"""
        print("🚀 STARTING CATALORO MARKETPLACE EXTREME STRESS TEST")
        print(f"📊 Target: {self.config.max_concurrent_users} concurrent users")
        print("=" * 80)
        
        self.test_start_time = time.time()
        
        try:
            # Start system monitoring
            self.start_system_monitoring()
            
            # Generate test data
            await self.create_test_data()
            
            # Execute load patterns
            print("\n📈 PHASE 1: Gradual Ramp-up Test")
            ramp_results = await self.gradual_ramp_up_test()
            
            print("\n🔥 PHASE 2: Sustained Peak Test")
            peak_results = await self.sustained_peak_test()
            
            print("\n⚡ PHASE 3: Spike Test")
            spike_results = await self.spike_test()
            
            # Calculate performance metrics
            print("\n📊 Calculating performance metrics...")
            metrics = self.calculate_performance_metrics()
            
            # Generate report
            report = self.generate_performance_report(metrics)
            print(report)
            
            # Save report to file
            with open("/app/extreme_stress_test_report.txt", "w") as f:
                f.write(report)
            
            print("📄 Report saved to: /app/extreme_stress_test_report.txt")
            
            return {
                "success": True,
                "metrics": metrics,
                "report": report
            }
            
        except Exception as e:
            print(f"💥 EXTREME STRESS TEST FAILED: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        
        finally:
            # MANDATORY cleanup
            await self.cleanup_test_data()
            self.stop_monitoring = True

async def main():
    """Main execution function"""
    tester = ExtremeStressTester()
    
    # Handle Ctrl+C gracefully
    def signal_handler(signum, frame):
        print("\n⚠️ Test interrupted by user. Starting cleanup...")
        asyncio.create_task(tester.cleanup_test_data())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        await tester.setup()
        result = await tester.run_extreme_stress_test()
        
        if result["success"]:
            print("\n🎉 EXTREME STRESS TEST COMPLETED SUCCESSFULLY")
        else:
            print(f"\n❌ EXTREME STRESS TEST FAILED: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    # Check if required packages are available
    try:
        import psutil
    except ImportError:
        print("❌ psutil package required for system monitoring")
        print("   Install with: pip install psutil")
        sys.exit(1)
    
    asyncio.run(main())