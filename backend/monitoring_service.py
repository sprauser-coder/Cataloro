"""
Monitoring Service for Cataloro Marketplace
Implements comprehensive application monitoring, performance tracking, and alerting
"""

import asyncio
import logging
import os
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class MonitoringService:
    def __init__(self):
        # Performance metrics storage
        self.response_times = deque(maxlen=1000)  # Last 1000 requests
        self.error_counts = defaultdict(int)
        self.endpoint_metrics = defaultdict(lambda: {"count": 0, "total_time": 0, "errors": 0})
        self.system_metrics = deque(maxlen=100)  # Last 100 system snapshots
        
        # Health check configuration
        self.health_checks = {}
        self.service_status = {}
        
        # Alert configuration
        self.alerts = []
        self.alert_thresholds = {
            "response_time": 5000,  # 5 seconds
            "error_rate": 0.05,     # 5%
            "cpu_usage": 80,        # 80%
            "memory_usage": 85,     # 85%
            "disk_usage": 90        # 90%
        }
        
        # Monitoring state
        self.monitoring_enabled = True
        self.start_time = datetime.utcnow()
        self._background_task = None
        
        # Background monitoring will be started in startup event
    
    def start_background_monitoring(self):
        """Start background monitoring task"""
        if self._background_task is None:
            self._background_task = asyncio.create_task(self._start_background_monitoring())
    
    async def _start_background_monitoring(self):
        """Start background monitoring tasks"""
        while self.monitoring_enabled:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(60)  # Collect every minute
            except Exception as e:
                logger.error(f"Background monitoring error: {e}")
                await asyncio.sleep(60)
    
    def record_request(
        self,
        endpoint: str,
        method: str,
        response_time: float,
        status_code: int,
        user_id: str = None
    ):
        """Record request metrics"""
        try:
            # Record overall response time
            self.response_times.append({
                "timestamp": time.time(),
                "response_time": response_time,
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "user_id": user_id
            })
            
            # Record endpoint-specific metrics
            endpoint_key = f"{method} {endpoint}"
            self.endpoint_metrics[endpoint_key]["count"] += 1
            self.endpoint_metrics[endpoint_key]["total_time"] += response_time
            
            # Record errors
            if status_code >= 400:
                self.endpoint_metrics[endpoint_key]["errors"] += 1
                self.error_counts[status_code] += 1
                
                # Create alert for high error rates
                if status_code >= 500:
                    self._check_error_rate_alerts(endpoint_key)
            
            # Check response time alerts
            if response_time > self.alert_thresholds["response_time"]:
                self._create_alert(
                    "High Response Time",
                    f"Endpoint {endpoint_key} took {response_time:.2f}ms",
                    "medium"
                )
            
        except Exception as e:
            logger.error(f"Failed to record request metrics: {e}")
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available
            memory_total = memory.total
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free
            disk_total = disk.total
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            metrics = {
                "timestamp": time.time(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "process_percent": process_cpu
                },
                "memory": {
                    "percent": memory_percent,
                    "available": memory_available,
                    "total": memory_total,
                    "process_rss": process_memory.rss,
                    "process_vms": process_memory.vms
                },
                "disk": {
                    "percent": disk_percent,
                    "free": disk_free,
                    "total": disk_total
                }
            }
            
            self.system_metrics.append(metrics)
            
            # Check for system alerts
            await self._check_system_alerts(metrics)
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    async def _check_system_alerts(self, metrics: Dict):
        """Check system metrics against alert thresholds"""
        # CPU usage alert
        if metrics["cpu"]["percent"] > self.alert_thresholds["cpu_usage"]:
            self._create_alert(
                "High CPU Usage",
                f"CPU usage at {metrics['cpu']['percent']:.1f}%",
                "high"
            )
        
        # Memory usage alert
        if metrics["memory"]["percent"] > self.alert_thresholds["memory_usage"]:
            self._create_alert(
                "High Memory Usage",
                f"Memory usage at {metrics['memory']['percent']:.1f}%",
                "high"
            )
        
        # Disk usage alert
        if metrics["disk"]["percent"] > self.alert_thresholds["disk_usage"]:
            self._create_alert(
                "High Disk Usage",
                f"Disk usage at {metrics['disk']['percent']:.1f}%",
                "critical"
            )
    
    def _check_error_rate_alerts(self, endpoint: str):
        """Check if error rate exceeds threshold"""
        metrics = self.endpoint_metrics[endpoint]
        if metrics["count"] > 10:  # Only check after 10+ requests
            error_rate = metrics["errors"] / metrics["count"]
            if error_rate > self.alert_thresholds["error_rate"]:
                self._create_alert(
                    "High Error Rate",
                    f"Endpoint {endpoint} has {error_rate:.1%} error rate",
                    "high"
                )
    
    def _create_alert(self, title: str, description: str, severity: str = "medium"):
        """Create a monitoring alert"""
        alert = {
            "id": f"alert_{len(self.alerts)}_{int(time.time())}",
            "timestamp": datetime.utcnow().isoformat(),
            "title": title,
            "description": description,
            "severity": severity,
            "status": "active",
            "type": "system"
        }
        
        self.alerts.append(alert)
        logger.warning(f"MONITORING ALERT [{severity.upper()}]: {title} - {description}")
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def register_health_check(self, name: str, check_function):
        """Register a health check function"""
        self.health_checks[name] = check_function
        logger.info(f"Registered health check: {name}")
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = {}
        overall_healthy = True
        
        for name, check_function in self.health_checks.items():
            try:
                start_time = time.time()
                result = await check_function() if asyncio.iscoroutinefunction(check_function) else check_function()
                duration = (time.time() - start_time) * 1000
                
                results[name] = {
                    "healthy": result.get("healthy", True),
                    "message": result.get("message", "OK"),
                    "duration_ms": round(duration, 2),
                    "details": result.get("details", {})
                }
                
                if not results[name]["healthy"]:
                    overall_healthy = False
                    
            except Exception as e:
                results[name] = {
                    "healthy": False,
                    "message": f"Health check failed: {str(e)}",
                    "duration_ms": 0,
                    "details": {}
                }
                overall_healthy = False
        
        return {
            "overall_healthy": overall_healthy,
            "checks": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        current_time = time.time()
        
        # Calculate response time statistics
        recent_responses = [r for r in self.response_times if current_time - r["timestamp"] < 3600]
        
        if recent_responses:
            response_times = [r["response_time"] for r in recent_responses]
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        # Get endpoint statistics
        endpoint_stats = {}
        for endpoint, metrics in self.endpoint_metrics.items():
            if metrics["count"] > 0:
                endpoint_stats[endpoint] = {
                    "request_count": metrics["count"],
                    "avg_response_time": metrics["total_time"] / metrics["count"],
                    "error_count": metrics["errors"],
                    "error_rate": metrics["errors"] / metrics["count"]
                }
        
        # Get system metrics
        latest_system_metrics = self.system_metrics[-1] if self.system_metrics else {}
        
        return {
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "request_metrics": {
                "total_requests": len(self.response_times),
                "recent_requests_last_hour": len(recent_responses),
                "avg_response_time_ms": round(avg_response_time, 2),
                "max_response_time_ms": round(max_response_time, 2),
                "min_response_time_ms": round(min_response_time, 2)
            },
            "error_metrics": {
                "total_errors": sum(self.error_counts.values()),
                "error_breakdown": dict(self.error_counts),
                "recent_error_rate": self._calculate_recent_error_rate()
            },
            "endpoint_performance": endpoint_stats,
            "system_metrics": latest_system_metrics,
            "alert_summary": {
                "total_alerts": len(self.alerts),
                "active_alerts": len([a for a in self.alerts if a["status"] == "active"]),
                "recent_alerts": len([a for a in self.alerts 
                                    if (current_time - datetime.fromisoformat(a["timestamp"]).timestamp()) < 3600])
            }
        }
    
    def _calculate_recent_error_rate(self) -> float:
        """Calculate error rate for recent requests"""
        current_time = time.time()
        recent_responses = [r for r in self.response_times if current_time - r["timestamp"] < 3600]
        
        if not recent_responses:
            return 0.0
        
        error_count = len([r for r in recent_responses if r["status_code"] >= 400])
        return error_count / len(recent_responses)
    
    def get_system_health_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        latest_metrics = self.system_metrics[-1] if self.system_metrics else {}
        
        if not latest_metrics:
            return {"status": "unknown", "message": "No system metrics available"}
        
        # Determine health status
        cpu_ok = latest_metrics.get("cpu", {}).get("percent", 0) < 80
        memory_ok = latest_metrics.get("memory", {}).get("percent", 0) < 85
        disk_ok = latest_metrics.get("disk", {}).get("percent", 0) < 90
        
        active_alerts = len([a for a in self.alerts if a["status"] == "active"])
        error_rate = self._calculate_recent_error_rate()
        
        if not cpu_ok or not memory_ok or not disk_ok or active_alerts > 5:
            status = "critical"
            message = "System resources under stress or multiple active alerts"
        elif error_rate > 0.1 or active_alerts > 2:
            status = "warning"
            message = "Elevated error rate or active alerts detected"
        else:
            status = "healthy"
            message = "All systems operating normally"
        
        return {
            "status": status,
            "message": message,
            "details": {
                "cpu_healthy": cpu_ok,
                "memory_healthy": memory_ok,
                "disk_healthy": disk_ok,
                "active_alerts": active_alerts,
                "error_rate": error_rate
            }
        }
    
    def get_recent_alerts(self, limit: int = 20) -> List[Dict]:
        """Get recent monitoring alerts"""
        return sorted(self.alerts, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved"""
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["status"] = "resolved"
                alert["resolved_at"] = datetime.utcnow().isoformat()
                return True
        return False
    
    def get_monitoring_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive monitoring dashboard data"""
        return {
            "system_health": self.get_system_health_status(),
            "performance_metrics": self.get_performance_metrics(),
            "recent_alerts": self.get_recent_alerts(10),
            "uptime": {
                "start_time": self.start_time.isoformat(),
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "uptime_formatted": self._format_uptime()
            }
        }
    
    def _format_uptime(self) -> str:
        """Format uptime in human readable format"""
        uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

# Global monitoring service instance
monitoring_service = MonitoringService()

# Middleware for automatic request monitoring
class MonitoringMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            # Wrap send to capture response status
            response_status = 200
            
            async def send_wrapper(message):
                nonlocal response_status
                if message["type"] == "http.response.start":
                    response_status = message["status"]
                await send(message)
            
            # Process request
            await self.app(scope, receive, send_wrapper)
            
            # Record metrics
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            path = scope.get("path", "unknown")
            method = scope.get("method", "unknown")
            
            monitoring_service.record_request(
                endpoint=path,
                method=method,
                response_time=response_time,
                status_code=response_status
            )
        else:
            await self.app(scope, receive, send)