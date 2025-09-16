"""
CATALORO - Enhanced Monitoring Service
Comprehensive system monitoring and performance tracking
"""

import asyncio
import time
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class MonitoringService:
    """Enhanced monitoring service for system and application metrics"""
    
    def __init__(self):
        """Initialize monitoring service"""
        self.metrics = {
            'requests': defaultdict(list),
            'errors': defaultdict(list),
            'performance': defaultdict(list),
            'system': defaultdict(list),
            'database': defaultdict(list)
        }
        
        # Performance tracking
        self.request_times = deque(maxlen=1000)
        self.error_rates = defaultdict(lambda: deque(maxlen=100))
        self.active_connections = 0
        
        # System monitoring
        self.system_alerts = []
        self.monitoring_enabled = True
        self.start_time = datetime.utcnow()
        self._background_task = None
    
    async def start_monitoring(self):
        """Start the background monitoring task"""
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
        timestamp = datetime.utcnow()
        
        # Store request data
        request_data = {
            'timestamp': timestamp,
            'endpoint': endpoint,
            'method': method,
            'response_time': response_time,
            'status_code': status_code,
            'user_id': user_id
        }
        
        self.metrics['requests'][endpoint].append(request_data)
        self.request_times.append(response_time)
        
        # Track errors
        if status_code >= 400:
            self.metrics['errors'][endpoint].append(request_data)
            self.error_rates[endpoint].append(timestamp)
    
    def record_database_operation(
        self,
        operation: str,
        collection: str,
        duration: float,
        success: bool = True
    ):
        """Record database operation metrics"""
        self.metrics['database'][collection].append({
            'timestamp': datetime.utcnow(),
            'operation': operation,
            'duration': duration,
            'success': success
        })
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network
            network = psutil.net_io_counters()
            
            system_data = {
                'timestamp': datetime.utcnow(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used': memory.used,
                'memory_available': memory.available,
                'disk_percent': (disk.used / disk.total) * 100,
                'disk_used': disk.used,
                'disk_free': disk.free,
                'network_sent': network.bytes_sent,
                'network_recv': network.bytes_recv
            }
            
            self.metrics['system']['general'].append(system_data)
            
            # Check for alerts
            await self._check_system_alerts(system_data)
            
        except Exception as e:
            logger.error(f"System metrics collection error: {e}")
    
    async def _check_system_alerts(self, system_data: Dict):
        """Check for system alerts and warnings"""
        alerts = []
        
        # High CPU usage
        if system_data['cpu_percent'] > 90:
            alerts.append({
                'type': 'cpu_high',
                'message': f"High CPU usage: {system_data['cpu_percent']:.1f}%",
                'severity': 'warning',
                'timestamp': datetime.utcnow()
            })
        
        # High memory usage
        if system_data['memory_percent'] > 90:
            alerts.append({
                'type': 'memory_high',
                'message': f"High memory usage: {system_data['memory_percent']:.1f}%",
                'severity': 'warning',
                'timestamp': datetime.utcnow()
            })
        
        # Low disk space
        if system_data['disk_percent'] > 90:
            alerts.append({
                'type': 'disk_high',
                'message': f"Low disk space: {system_data['disk_percent']:.1f}% used",
                'severity': 'critical',
                'timestamp': datetime.utcnow()
            })
        
        if alerts:
            self.system_alerts.extend(alerts)
            # Keep only last 100 alerts
            self.system_alerts = self.system_alerts[-100:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.request_times:
            return {'message': 'No requests recorded yet'}
        
        times = list(self.request_times)
        avg_response_time = sum(times) / len(times)
        
        # Calculate percentiles
        times_sorted = sorted(times)
        n = len(times_sorted)
        p95 = times_sorted[int(n * 0.95)]
        p99 = times_sorted[int(n * 0.99)]
        
        return {
            'total_requests': len(times),
            'avg_response_time': round(avg_response_time, 3),
            'median_response_time': round(times_sorted[n // 2], 3),
            'p95_response_time': round(p95, 3),
            'p99_response_time': round(p99, 3),
            'min_response_time': round(min(times), 3),
            'max_response_time': round(max(times), 3)
        }
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary"""
        total_errors = sum(len(errors) for errors in self.metrics['errors'].values())
        total_requests = len(self.request_times)
        
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        # Get top error endpoints
        error_endpoints = {}
        for endpoint, errors in self.metrics['errors'].items():
            error_endpoints[endpoint] = len(errors)
        
        return {
            'total_errors': total_errors,
            'error_rate': round(error_rate, 2),
            'error_endpoints': dict(sorted(error_endpoints.items(), 
                                         key=lambda x: x[1], reverse=True)[:10])
        }
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get system summary"""
        if not self.metrics['system'].get('general'):
            return {'message': 'No system metrics available'}
        
        latest = self.metrics['system']['general'][-1]
        
        return {
            'uptime_hours': (datetime.utcnow() - self.start_time).total_seconds() / 3600,
            'cpu_percent': latest['cpu_percent'],
            'memory_percent': latest['memory_percent'],
            'disk_percent': latest['disk_percent'],
            'active_alerts': len([a for a in self.system_alerts 
                                if a['timestamp'] > datetime.utcnow() - timedelta(hours=1)])
        }
    
    def get_database_summary(self) -> Dict[str, Any]:
        """Get database summary"""
        if not self.metrics['database']:
            return {'message': 'No database metrics available'}
        
        total_operations = sum(len(ops) for ops in self.metrics['database'].values())
        
        # Calculate average operation times by collection
        collection_stats = {}
        for collection, operations in self.metrics['database'].items():
            if operations:
                avg_duration = sum(op['duration'] for op in operations) / len(operations)
                success_rate = sum(1 for op in operations if op['success']) / len(operations) * 100
                collection_stats[collection] = {
                    'operations': len(operations),
                    'avg_duration': round(avg_duration, 3),
                    'success_rate': round(success_rate, 1)
                }
        
        return {
            'total_operations': total_operations,
            'collections': collection_stats
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        performance = self.get_performance_summary()
        errors = self.get_error_summary()
        system = self.get_system_summary()
        
        # Determine health status
        health_score = 100
        status = "healthy"
        issues = []
        
        # Check performance
        if isinstance(performance, dict) and 'avg_response_time' in performance:
            if performance['avg_response_time'] > 2.0:
                health_score -= 20
                issues.append("High response times")
        
        # Check error rate
        if isinstance(errors, dict) and 'error_rate' in errors:
            if errors['error_rate'] > 5:
                health_score -= 30
                issues.append("High error rate")
        
        # Check system resources
        if isinstance(system, dict):
            if system.get('cpu_percent', 0) > 80:
                health_score -= 15
                issues.append("High CPU usage")
            if system.get('memory_percent', 0) > 80:
                health_score -= 15
                issues.append("High memory usage")
            if system.get('disk_percent', 0) > 90:
                health_score -= 20
                issues.append("Low disk space")
        
        # Determine status
        if health_score >= 90:
            status = "healthy"
        elif health_score >= 70:
            status = "warning"
        else:
            status = "critical"
        
        return {
            'status': status,
            'health_score': max(0, health_score),
            'issues': issues,
            'uptime_hours': (datetime.utcnow() - self.start_time).total_seconds() / 3600,
            'last_check': datetime.utcnow().isoformat()
        }
    
    def clear_old_metrics(self, hours: int = 24):
        """Clear metrics older than specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Clear old request metrics
        for endpoint in list(self.metrics['requests'].keys()):
            self.metrics['requests'][endpoint] = [
                req for req in self.metrics['requests'][endpoint]
                if req['timestamp'] > cutoff_time
            ]
            if not self.metrics['requests'][endpoint]:
                del self.metrics['requests'][endpoint]
        
        # Clear old error metrics
        for endpoint in list(self.metrics['errors'].keys()):
            self.metrics['errors'][endpoint] = [
                err for err in self.metrics['errors'][endpoint]
                if err['timestamp'] > cutoff_time
            ]
            if not self.metrics['errors'][endpoint]:
                del self.metrics['errors'][endpoint]
        
        # Clear old system metrics
        for metric_type in list(self.metrics['system'].keys()):
            self.metrics['system'][metric_type] = [
                metric for metric in self.metrics['system'][metric_type]
                if metric['timestamp'] > cutoff_time
            ]
            if not self.metrics['system'][metric_type]:
                del self.metrics['system'][metric_type]
        
        # Clear old database metrics
        for collection in list(self.metrics['database'].keys()):
            self.metrics['database'][collection] = [
                op for op in self.metrics['database'][collection]
                if op['timestamp'] > cutoff_time
            ]
            if not self.metrics['database'][collection]:
                del self.metrics['database'][collection]
        
        # Clear old alerts
        self.system_alerts = [
            alert for alert in self.system_alerts
            if alert['timestamp'] > cutoff_time
        ]

class MonitoringMiddleware:
    """FastAPI middleware for request monitoring"""
    
    def __init__(self, app, monitoring_service: MonitoringService):
        self.app = app
        self.monitoring_service = monitoring_service
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                process_time = time.time() - start_time
                
                # Record metrics
                self.monitoring_service.record_request(
                    endpoint=scope["path"],
                    method=scope["method"],
                    response_time=process_time,
                    status_code=message["status"],
                    user_id=None  # Could extract from scope if available
                )
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

# Global monitoring service instance
monitoring_service = MonitoringService()