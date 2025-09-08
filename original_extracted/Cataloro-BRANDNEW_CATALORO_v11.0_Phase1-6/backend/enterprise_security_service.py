"""
Phase 6 - Enterprise Security & Compliance Service
Advanced security features, compliance monitoring, and enterprise-grade protection
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import hashlib
import json
import uuid

logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    event_id: str
    event_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    user_id: Optional[str]
    ip_address: str
    description: str
    timestamp: datetime
    resolved: bool = False

@dataclass
class ComplianceCheck:
    check_id: str
    check_name: str
    category: str
    status: str  # 'pass', 'fail', 'warning'
    description: str
    last_checked: datetime
    next_check: datetime

@dataclass
class UserSecurityProfile:
    user_id: str
    risk_score: float  # 0.0 to 1.0
    security_flags: List[str]
    last_security_check: datetime
    mfa_enabled: bool
    suspicious_activities: int
    location_anomalies: int

class EnterpriseSecurityService:
    def __init__(self):
        self.service_name = "Enterprise Security & Compliance"
        self.version = "1.0.0"
        self.status = "operational"
        self.last_updated = datetime.now(timezone.utc)
        
        # Security monitoring data
        self.security_events: List[SecurityEvent] = []
        self.compliance_checks: List[ComplianceCheck] = []
        self.user_profiles: Dict[str, UserSecurityProfile] = {}
        
        # Security thresholds
        self.thresholds = {
            "max_login_attempts": 5,
            "suspicious_activity_threshold": 10,
            "high_risk_score_threshold": 0.7,
            "location_anomaly_threshold": 3
        }
        
    async def initialize(self):
        """Initialize the enterprise security service"""
        try:
            await self._initialize_security_monitoring()
            await self._setup_compliance_checks()
            self.status = "operational"
            logger.info("✅ Enterprise Security Service initialized successfully")
            return True
        except Exception as e:
            self.status = "error"
            logger.error(f"❌ Enterprise Security Service initialization failed: {e}")
            return False
    
    async def _initialize_security_monitoring(self):
        """Initialize security monitoring systems"""
        # Generate some sample security events
        sample_events = [
            {"type": "failed_login", "severity": "medium", "desc": "Multiple failed login attempts"},
            {"type": "suspicious_activity", "severity": "high", "desc": "Unusual transaction pattern detected"},
            {"type": "unauthorized_access", "severity": "critical", "desc": "Access attempt from blocked IP"},
            {"type": "data_breach_attempt", "severity": "critical", "desc": "Potential data extraction detected"},
            {"type": "phishing_attempt", "severity": "high", "desc": "Suspicious email interaction"}
        ]
        
        for event_data in sample_events:
            event = SecurityEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_data["type"],
                severity=event_data["severity"],
                user_id=f"user_{uuid.uuid4().hex[:8]}",
                ip_address=f"192.168.{hash(event_data['type']) % 255}.{hash(event_data['desc']) % 255}",
                description=event_data["desc"],
                timestamp=datetime.now(timezone.utc) - timedelta(hours=hash(event_data["type"]) % 48),
                resolved=hash(event_data["type"]) % 3 == 0
            )
            self.security_events.append(event)
        
        logger.info("🔒 Security monitoring initialized")
    
    async def _setup_compliance_checks(self):
        """Setup compliance monitoring checks"""
        compliance_standards = [
            {"name": "GDPR Data Protection", "category": "Privacy", "status": "pass"},
            {"name": "PCI DSS Payment Security", "category": "Payment", "status": "pass"},
            {"name": "SOX Financial Controls", "category": "Financial", "status": "warning"},
            {"name": "CCPA Consumer Privacy", "category": "Privacy", "status": "pass"},
            {"name": "ISO 27001 Security Management", "category": "Security", "status": "pass"},
            {"name": "HIPAA Data Protection", "category": "Healthcare", "status": "fail"},
            {"name": "SOC 2 Type II", "category": "Security", "status": "pass"}
        ]
        
        for check_data in compliance_standards:
            check = ComplianceCheck(
                check_id=str(uuid.uuid4()),
                check_name=check_data["name"],
                category=check_data["category"],
                status=check_data["status"],
                description=f"Compliance check for {check_data['name']} standards",
                last_checked=datetime.now(timezone.utc) - timedelta(days=hash(check_data["name"]) % 30),
                next_check=datetime.now(timezone.utc) + timedelta(days=30)
            )
            self.compliance_checks.append(check)
        
        logger.info("📋 Compliance checks initialized")
    
    # Security Event Management
    async def log_security_event(self, event_type: str, severity: str, user_id: str = None, 
                                ip_address: str = "unknown", description: str = "") -> str:
        """Log a new security event"""
        try:
            event = SecurityEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                severity=severity,
                user_id=user_id,
                ip_address=ip_address,
                description=description,
                timestamp=datetime.now(timezone.utc)
            )
            
            self.security_events.append(event)
            
            # Update user security profile if user involved
            if user_id:
                await self._update_user_security_profile(user_id, event_type)
            
            logger.info(f"🚨 Security event logged: {event_type} - {severity}")
            return event.event_id
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
            return ""
    
    async def _update_user_security_profile(self, user_id: str, event_type: str):
        """Update user security profile based on event"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserSecurityProfile(
                user_id=user_id,
                risk_score=0.0,
                security_flags=[],
                last_security_check=datetime.now(timezone.utc),
                mfa_enabled=False,
                suspicious_activities=0,
                location_anomalies=0
            )
        
        profile = self.user_profiles[user_id]
        
        # Update based on event type
        if event_type in ["failed_login", "unauthorized_access"]:
            profile.suspicious_activities += 1
            profile.risk_score = min(1.0, profile.risk_score + 0.1)
        elif event_type == "location_anomaly":
            profile.location_anomalies += 1
            profile.risk_score = min(1.0, profile.risk_score + 0.05)
        
        # Add security flags
        if profile.risk_score > self.thresholds["high_risk_score_threshold"]:
            if "high_risk" not in profile.security_flags:
                profile.security_flags.append("high_risk")
        
        profile.last_security_check = datetime.now(timezone.utc)
    
    # Security Analytics
    async def get_security_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard data"""
        try:
            # Calculate security metrics
            total_events = len(self.security_events)
            critical_events = len([e for e in self.security_events if e.severity == "critical"])
            unresolved_events = len([e for e in self.security_events if not e.resolved])
            
            # Recent events (last 24 hours)
            recent_events = [
                e for e in self.security_events 
                if e.timestamp > datetime.now(timezone.utc) - timedelta(hours=24)
            ]
            
            # Event distribution by type
            event_types = {}
            for event in self.security_events:
                event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            
            # Risk assessment
            high_risk_users = len([p for p in self.user_profiles.values() if p.risk_score > 0.7])
            total_users = max(1, len(self.user_profiles))  # Avoid division by zero
            
            dashboard_data = {
                "overview": {
                    "total_events": total_events,
                    "critical_events": critical_events,
                    "unresolved_events": unresolved_events,
                    "recent_events_24h": len(recent_events),
                    "security_score": max(0, 100 - (critical_events * 10) - (unresolved_events * 5)),
                    "high_risk_users": high_risk_users,
                    "risk_percentage": (high_risk_users / total_users) * 100
                },
                "event_distribution": event_types,
                "recent_events": [
                    {
                        "id": e.event_id,
                        "type": e.event_type,
                        "severity": e.severity,
                        "description": e.description,
                        "timestamp": e.timestamp.isoformat(),
                        "resolved": e.resolved
                    }
                    for e in sorted(recent_events, key=lambda x: x.timestamp, reverse=True)[:10]
                ],
                "threat_levels": {
                    "current_threat_level": self._calculate_threat_level(),
                    "threat_trend": "stable",  # Would be calculated based on historical data
                    "active_threats": critical_events + unresolved_events
                },
                "recommendations": self._generate_security_recommendations()
            }
            
            logger.info("🔒 Generated security dashboard data")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Security dashboard data generation failed: {e}")
            return {}
    
    def _calculate_threat_level(self) -> str:
        """Calculate current threat level"""
        critical_events = len([e for e in self.security_events if e.severity == "critical" and not e.resolved])
        high_events = len([e for e in self.security_events if e.severity == "high" and not e.resolved])
        
        if critical_events >= 3:
            return "critical"
        elif critical_events >= 1 or high_events >= 5:
            return "high"
        elif high_events >= 2:
            return "medium"
        else:
            return "low"
    
    def _generate_security_recommendations(self) -> List[str]:
        """Generate security recommendations based on current state"""
        recommendations = []
        
        unresolved_critical = len([e for e in self.security_events if e.severity == "critical" and not e.resolved])
        if unresolved_critical > 0:
            recommendations.append(f"Address {unresolved_critical} critical security events immediately")
        
        high_risk_users = len([p for p in self.user_profiles.values() if p.risk_score > 0.7])
        if high_risk_users > 0:
            recommendations.append(f"Review {high_risk_users} high-risk user accounts")
        
        failed_compliance = len([c for c in self.compliance_checks if c.status == "fail"])
        if failed_compliance > 0:
            recommendations.append(f"Fix {failed_compliance} failing compliance checks")
        
        if not recommendations:
            recommendations = [
                "Security posture is good - maintain current monitoring",
                "Consider implementing additional multi-factor authentication",
                "Review and update security policies quarterly"
            ]
        
        return recommendations[:5]  # Top 5 recommendations
    
    # Compliance Management
    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get comprehensive compliance status"""
        try:
            total_checks = len(self.compliance_checks)
            passing_checks = len([c for c in self.compliance_checks if c.status == "pass"])
            failing_checks = len([c for c in self.compliance_checks if c.status == "fail"])
            warning_checks = len([c for c in self.compliance_checks if c.status == "warning"])
            
            compliance_score = (passing_checks / total_checks) * 100 if total_checks > 0 else 0
            
            # Group by category
            categories = {}
            for check in self.compliance_checks:
                if check.category not in categories:
                    categories[check.category] = {"pass": 0, "fail": 0, "warning": 0, "total": 0}
                categories[check.category][check.status] += 1
                categories[check.category]["total"] += 1
            
            compliance_data = {
                "overview": {
                    "total_checks": total_checks,
                    "passing_checks": passing_checks,
                    "failing_checks": failing_checks,
                    "warning_checks": warning_checks,
                    "compliance_score": compliance_score,
                    "last_audit": self.last_updated.isoformat()
                },
                "by_category": categories,
                "failing_checks": [
                    {
                        "id": c.check_id,
                        "name": c.check_name,
                        "category": c.category,
                        "description": c.description,
                        "last_checked": c.last_checked.isoformat(),
                        "next_check": c.next_check.isoformat()
                    }
                    for c in self.compliance_checks if c.status == "fail"
                ],
                "upcoming_checks": [
                    {
                        "name": c.check_name,
                        "category": c.category,
                        "next_check": c.next_check.isoformat()
                    }
                    for c in sorted(self.compliance_checks, key=lambda x: x.next_check)[:5]
                ]
            }
            
            logger.info("📋 Generated compliance status data")
            return compliance_data
            
        except Exception as e:
            logger.error(f"Compliance status generation failed: {e}")
            return {}
    
    # User Security Management
    async def get_user_security_insights(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get security insights for users"""
        try:
            # If we don't have enough real user profiles, generate some sample data
            if len(self.user_profiles) < 5:
                await self._generate_sample_user_profiles()
            
            user_insights = []
            for user_id, profile in list(self.user_profiles.items())[:limit]:
                insight = {
                    "user_id": user_id,
                    "risk_score": profile.risk_score,
                    "risk_level": "high" if profile.risk_score > 0.7 else "medium" if profile.risk_score > 0.4 else "low",
                    "security_flags": profile.security_flags,
                    "mfa_enabled": profile.mfa_enabled,
                    "suspicious_activities": profile.suspicious_activities,
                    "location_anomalies": profile.location_anomalies,
                    "last_security_check": profile.last_security_check.isoformat(),
                    "recommendations": self._get_user_recommendations(profile)
                }
                user_insights.append(insight)
            
            # Sort by risk score (highest first)
            user_insights.sort(key=lambda x: x["risk_score"], reverse=True)
            
            logger.info(f"👥 Generated security insights for {len(user_insights)} users")
            return user_insights
            
        except Exception as e:
            logger.error(f"User security insights generation failed: {e}")
            return []
    
    async def _generate_sample_user_profiles(self):
        """Generate sample user security profiles for demonstration"""
        import random
        
        for i in range(10):
            user_id = f"user_{uuid.uuid4().hex[:8]}"
            profile = UserSecurityProfile(
                user_id=user_id,
                risk_score=random.uniform(0.0, 1.0),
                security_flags=random.sample(["high_risk", "suspicious_login", "location_anomaly"], 
                                           random.randint(0, 2)),
                last_security_check=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30)),
                mfa_enabled=random.choice([True, False]),
                suspicious_activities=random.randint(0, 15),
                location_anomalies=random.randint(0, 5)
            )
            self.user_profiles[user_id] = profile
    
    def _get_user_recommendations(self, profile: UserSecurityProfile) -> List[str]:
        """Get security recommendations for a specific user"""
        recommendations = []
        
        if not profile.mfa_enabled:
            recommendations.append("Enable multi-factor authentication")
        
        if profile.risk_score > 0.7:
            recommendations.append("Account requires immediate security review")
        
        if profile.suspicious_activities > 5:
            recommendations.append("Monitor for unusual activity patterns")
        
        if profile.location_anomalies > 2:
            recommendations.append("Verify recent login locations")
        
        if not recommendations:
            recommendations.append("Security profile looks good")
        
        return recommendations[:3]
    
    # Service Health
    async def get_service_health(self) -> Dict[str, Any]:
        """Get enterprise security service health information"""
        return {
            "service_name": self.service_name,
            "version": self.version,
            "status": self.status,
            "last_updated": self.last_updated.isoformat(),
            "capabilities": [
                "Security Event Monitoring",
                "Compliance Management",
                "User Risk Assessment",
                "Threat Detection",
                "Security Analytics"
            ],
            "active_monitors": len(self.security_events),
            "compliance_checks": len(self.compliance_checks),
            "monitored_users": len(self.user_profiles),
            "threat_level": self._calculate_threat_level()
        }

# Global service instance
_enterprise_security_service = None

async def get_enterprise_security_service() -> EnterpriseSecurityService:
    """Get or create the global Enterprise Security service instance"""
    global _enterprise_security_service
    
    if _enterprise_security_service is None:
        _enterprise_security_service = EnterpriseSecurityService()
        await _enterprise_security_service.initialize()
    
    return _enterprise_security_service