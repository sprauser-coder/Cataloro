"""
Security Service for Cataloro Marketplace
Implements comprehensive security features including rate limiting, validation, and audit logging
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from passlib.context import CryptContext
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

class SecurityService:
    def __init__(self):
        # Rate limiting configuration
        self.limiter = Limiter(key_func=get_remote_address)
        
        # Password hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # JWT settings
        self.SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'cataloro-secret-key-change-in-production')
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
        
        # Security thresholds
        self.MAX_LOGIN_ATTEMPTS = 5
        self.LOGIN_LOCKOUT_DURATION = 15 * 60  # 15 minutes
        self.SUSPICIOUS_ACTIVITY_THRESHOLD = 10
        
        # In-memory stores (in production, use Redis or database)
        self.failed_login_attempts = {}
        self.blocked_ips = {}
        self.audit_logs = []
        self.security_alerts = []
        
    def setup_rate_limiting(self, app):
        """Setup rate limiting for FastAPI app"""
        app.state.limiter = self.limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        logger.info("✅ Rate limiting configured")
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        result = {
            "valid": True,
            "score": 0,
            "issues": []
        }
        
        if len(password) < 8:
            result["valid"] = False
            result["issues"].append("Password must be at least 8 characters long")
        else:
            result["score"] += 1
        
        if not re.search(r'[A-Z]', password):
            result["issues"].append("Password should contain at least one uppercase letter")
        else:
            result["score"] += 1
        
        if not re.search(r'[a-z]', password):
            result["issues"].append("Password should contain at least one lowercase letter")
        else:
            result["score"] += 1
        
        if not re.search(r'\d', password):
            result["issues"].append("Password should contain at least one digit")
        else:
            result["score"] += 1
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result["issues"].append("Password should contain at least one special character")
        else:
            result["score"] += 1
        
        return result
    
    def sanitize_input(self, input_string: str) -> str:
        """Sanitize user input to prevent XSS and injection attacks"""
        if not input_string:
            return ""
        
        # Basic HTML sanitization
        input_string = re.sub(r'<script[^>]*>.*?</script>', '', input_string, flags=re.IGNORECASE | re.DOTALL)
        input_string = re.sub(r'<[^>]+>', '', input_string)
        
        # Remove potential SQL injection patterns
        dangerous_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
            r'(--|\#|/\*|\*/)',
            r'(\bOR\b.*=.*\bOR\b)',
            r'(\bAND\b.*=.*\bAND\b)',
        ]
        
        for pattern in dangerous_patterns:
            input_string = re.sub(pattern, '', input_string, flags=re.IGNORECASE)
        
        return input_string.strip()
    
    def validate_listing_data(self, listing_data: Dict) -> Dict[str, Any]:
        """Validate listing data for security issues"""
        validation_result = {
            "valid": True,
            "issues": [],
            "sanitized_data": {}
        }
        
        required_fields = ['title', 'description', 'price', 'category', 'condition']
        
        for field in required_fields:
            if field not in listing_data:
                validation_result["valid"] = False
                validation_result["issues"].append(f"Missing required field: {field}")
        
        # Sanitize string fields
        string_fields = ['title', 'description', 'category', 'condition']
        for field in string_fields:
            if field in listing_data:
                sanitized = self.sanitize_input(str(listing_data[field]))
                validation_result["sanitized_data"][field] = sanitized
                
                # Check for suspicious content
                if len(sanitized) != len(str(listing_data[field])):
                    validation_result["issues"].append(f"Suspicious content detected in {field}")
        
        # Validate price
        if 'price' in listing_data:
            try:
                price = float(listing_data['price'])
                if price < 0:
                    validation_result["valid"] = False
                    validation_result["issues"].append("Price cannot be negative")
                elif price > 1000000:  # Max price €1M
                    validation_result["valid"] = False
                    validation_result["issues"].append("Price exceeds maximum allowed")
                validation_result["sanitized_data"]['price'] = price
            except (ValueError, TypeError):
                validation_result["valid"] = False
                validation_result["issues"].append("Invalid price format")
        
        return validation_result
    
    def check_login_attempts(self, identifier: str) -> bool:
        """Check if user/IP has exceeded login attempts"""
        current_time = time.time()
        
        if identifier in self.failed_login_attempts:
            attempts = self.failed_login_attempts[identifier]
            # Clean old attempts
            attempts = [attempt_time for attempt_time in attempts 
                       if current_time - attempt_time < self.LOGIN_LOCKOUT_DURATION]
            self.failed_login_attempts[identifier] = attempts
            
            if len(attempts) >= self.MAX_LOGIN_ATTEMPTS:
                return False  # Blocked
        
        return True  # Allowed
    
    def record_failed_login(self, identifier: str):
        """Record a failed login attempt"""
        current_time = time.time()
        
        if identifier not in self.failed_login_attempts:
            self.failed_login_attempts[identifier] = []
        
        self.failed_login_attempts[identifier].append(current_time)
        
        # Check if this triggers a security alert
        if len(self.failed_login_attempts[identifier]) >= self.MAX_LOGIN_ATTEMPTS:
            self.create_security_alert(
                "Multiple Failed Login Attempts",
                f"Identifier {identifier} has {len(self.failed_login_attempts[identifier])} failed login attempts",
                "high"
            )
    
    def clear_login_attempts(self, identifier: str):
        """Clear failed login attempts after successful login"""
        if identifier in self.failed_login_attempts:
            del self.failed_login_attempts[identifier]
    
    def log_audit_event(
        self,
        user_id: str,
        action: str,
        resource: str,
        details: Dict = None,
        ip_address: str = None,
        user_agent: str = None
    ):
        """Log audit event"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "id": hashlib.md5(f"{user_id}{action}{time.time()}".encode()).hexdigest()
        }
        
        self.audit_logs.append(audit_entry)
        logger.info(f"AUDIT: {user_id} performed {action} on {resource}")
        
        # Keep only last 1000 audit logs in memory
        if len(self.audit_logs) > 1000:
            self.audit_logs = self.audit_logs[-1000:]
    
    def create_security_alert(self, title: str, description: str, severity: str = "medium"):
        """Create a security alert"""
        alert = {
            "id": hashlib.md5(f"{title}{time.time()}".encode()).hexdigest(),
            "timestamp": datetime.utcnow().isoformat(),
            "title": title,
            "description": description,
            "severity": severity,  # low, medium, high, critical
            "status": "active"
        }
        
        self.security_alerts.append(alert)
        logger.warning(f"SECURITY ALERT [{severity.upper()}]: {title} - {description}")
        
        # Keep only last 100 alerts in memory
        if len(self.security_alerts) > 100:
            self.security_alerts = self.security_alerts[-100:]
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics and statistics"""
        current_time = time.time()
        
        # Count recent events
        recent_failed_logins = 0
        for attempts in self.failed_login_attempts.values():
            recent_failed_logins += len([a for a in attempts if current_time - a < 3600])  # Last hour
        
        recent_alerts = len([a for a in self.security_alerts 
                           if (current_time - datetime.fromisoformat(a["timestamp"]).timestamp()) < 3600])
        
        return {
            "failed_login_attempts": {
                "total_unique_identifiers": len(self.failed_login_attempts),
                "recent_attempts_last_hour": recent_failed_logins,
                "blocked_identifiers": len([k for k, v in self.failed_login_attempts.items() 
                                          if len(v) >= self.MAX_LOGIN_ATTEMPTS])
            },
            "security_alerts": {
                "total_alerts": len(self.security_alerts),
                "recent_alerts_last_hour": recent_alerts,
                "active_alerts": len([a for a in self.security_alerts if a["status"] == "active"]),
                "alert_severity_breakdown": self._get_alert_severity_breakdown()
            },
            "audit_logs": {
                "total_entries": len(self.audit_logs),
                "recent_entries_last_hour": len([log for log in self.audit_logs 
                                               if (current_time - datetime.fromisoformat(log["timestamp"]).timestamp()) < 3600])
            },
            "security_status": self._calculate_security_status()
        }
    
    def _get_alert_severity_breakdown(self) -> Dict[str, int]:
        """Get breakdown of alerts by severity"""
        breakdown = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for alert in self.security_alerts:
            severity = alert.get("severity", "medium")
            if severity in breakdown:
                breakdown[severity] += 1
        return breakdown
    
    def _calculate_security_status(self) -> str:
        """Calculate overall security status"""
        recent_time = time.time() - 3600  # Last hour
        
        # Check for critical indicators
        recent_critical_alerts = len([a for a in self.security_alerts 
                                    if a.get("severity") == "critical" and 
                                    datetime.fromisoformat(a["timestamp"]).timestamp() > recent_time])
        
        recent_failed_logins = sum([len([attempt for attempt in attempts if attempt > recent_time]) 
                                  for attempts in self.failed_login_attempts.values()])
        
        if recent_critical_alerts > 0:
            return "critical"
        elif recent_failed_logins > 20:
            return "high_risk"
        elif recent_failed_logins > 5:
            return "medium_risk"
        else:
            return "secure"
    
    def get_recent_audit_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent audit logs"""
        return sorted(self.audit_logs, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_active_security_alerts(self) -> List[Dict]:
        """Get active security alerts"""
        return [alert for alert in self.security_alerts if alert["status"] == "active"]
    
    def resolve_security_alert(self, alert_id: str) -> bool:
        """Mark a security alert as resolved"""
        for alert in self.security_alerts:
            if alert["id"] == alert_id:
                alert["status"] = "resolved"
                alert["resolved_at"] = datetime.utcnow().isoformat()
                return True
        return False

# Global security service instance
security_service = SecurityService()

def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    # Check for forwarded IP first (common in load balancer setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to client host
    return request.client.host if request.client else "unknown"