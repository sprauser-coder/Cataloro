"""
Phase 6 - Enhanced User Management Service
Advanced user role management and multi-tenant architecture support
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)

class UserRole(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SELLER = "seller"
    BUYER = "buyer"
    GUEST = "guest"

class Permission(Enum):
    # User management
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"
    EDIT_USER_ROLES = "edit_user_roles"
    
    # Content management
    MANAGE_LISTINGS = "manage_listings"
    MODERATE_CONTENT = "moderate_content"
    APPROVE_LISTINGS = "approve_listings"
    
    # Financial
    VIEW_FINANCIALS = "view_financials"
    MANAGE_TRANSACTIONS = "manage_transactions"
    PROCESS_REFUNDS = "process_refunds"
    
    # System administration
    SYSTEM_CONFIG = "system_config"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_CATEGORIES = "manage_categories"
    
    # Advanced features
    MANAGE_FRAUD_DETECTION = "manage_fraud_detection"
    ACCESS_ADMIN_PANEL = "access_admin_panel"
    EXPORT_DATA = "export_data"

@dataclass
class UserPermissions:
    user_id: str
    role: UserRole
    permissions: Set[Permission]
    custom_permissions: Set[str]  # For custom tenant-specific permissions
    restrictions: Set[str]  # What this user cannot do
    expires_at: Optional[datetime] = None

@dataclass
class Tenant:
    tenant_id: str
    name: str
    domain: str
    settings: Dict[str, Any]
    subscription_tier: str  # 'basic', 'premium', 'enterprise'
    created_at: datetime
    is_active: bool
    user_limit: int
    feature_flags: Set[str]

@dataclass
class UserActivity:
    user_id: str
    action: str
    resource: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    success: bool
    details: Optional[Dict[str, Any]] = None

class EnhancedUserManagementService:
    def __init__(self):
        self.service_name = "Enhanced User Management"
        self.version = "1.0.0"
        self.status = "operational"
        self.last_updated = datetime.now(timezone.utc)
        
        # Data storage
        self.user_permissions: Dict[str, UserPermissions] = {}
        self.tenants: Dict[str, Tenant] = {}
        self.user_activities: List[UserActivity] = []
        
        # Role-permission mappings
        self.role_permissions = self._initialize_role_permissions()
        
        # Session management
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self):
        """Initialize the enhanced user management service"""
        try:
            await self._setup_default_tenants()
            await self._setup_sample_users()
            self.status = "operational"
            logger.info("✅ Enhanced User Management Service initialized successfully")
            return True
        except Exception as e:
            self.status = "error"
            logger.error(f"❌ Enhanced User Management Service initialization failed: {e}")
            return False
    
    def _initialize_role_permissions(self) -> Dict[UserRole, Set[Permission]]:
        """Initialize default role-permission mappings"""
        return {
            UserRole.SUPER_ADMIN: {
                Permission.MANAGE_USERS, Permission.VIEW_USERS, Permission.EDIT_USER_ROLES,
                Permission.MANAGE_LISTINGS, Permission.MODERATE_CONTENT, Permission.APPROVE_LISTINGS,
                Permission.VIEW_FINANCIALS, Permission.MANAGE_TRANSACTIONS, Permission.PROCESS_REFUNDS,
                Permission.SYSTEM_CONFIG, Permission.VIEW_ANALYTICS, Permission.MANAGE_CATEGORIES,
                Permission.MANAGE_FRAUD_DETECTION, Permission.ACCESS_ADMIN_PANEL, Permission.EXPORT_DATA
            },
            UserRole.ADMIN: {
                Permission.VIEW_USERS, Permission.MANAGE_LISTINGS, Permission.MODERATE_CONTENT,
                Permission.APPROVE_LISTINGS, Permission.VIEW_FINANCIALS, Permission.VIEW_ANALYTICS,
                Permission.MANAGE_CATEGORIES, Permission.ACCESS_ADMIN_PANEL
            },
            UserRole.MODERATOR: {
                Permission.VIEW_USERS, Permission.MODERATE_CONTENT, Permission.APPROVE_LISTINGS,
                Permission.ACCESS_ADMIN_PANEL
            },
            UserRole.SELLER: {
                Permission.MANAGE_LISTINGS
            },
            UserRole.BUYER: set(),  # Basic buying permissions
            UserRole.GUEST: set()   # No special permissions
        }
    
    async def _setup_default_tenants(self):
        """Setup default tenants"""
        # Main marketplace tenant
        main_tenant = Tenant(
            tenant_id="main",
            name="Cataloro Marketplace",
            domain="marketplace.cataloro.com",
            settings={
                "theme": "default",
                "features": ["escrow", "ai_recommendations", "multi_currency"],
                "max_listings_per_user": 100,
                "commission_rate": 5.0
            },
            subscription_tier="enterprise",
            created_at=datetime.now(timezone.utc),
            is_active=True,
            user_limit=10000,
            feature_flags={"phase5_features", "phase6_features", "advanced_analytics"}
        )
        self.tenants[main_tenant.tenant_id] = main_tenant
        
        logger.info("🏢 Default tenants setup completed")
    
    async def _setup_sample_users(self):
        """Setup sample user permissions"""
        sample_users = [
            {"id": "admin_001", "role": UserRole.SUPER_ADMIN},
            {"id": "admin_002", "role": UserRole.ADMIN},
            {"id": "mod_001", "role": UserRole.MODERATOR},
            {"id": "seller_001", "role": UserRole.SELLER},
            {"id": "buyer_001", "role": UserRole.BUYER}
        ]
        
        for user_data in sample_users:
            await self.assign_user_role(user_data["id"], user_data["role"])
        
        logger.info("👥 Sample user permissions setup completed")
    
    # Role and Permission Management
    async def assign_user_role(self, user_id: str, role: UserRole, 
                             custom_permissions: Set[str] = None,
                             restrictions: Set[str] = None,
                             expires_at: Optional[datetime] = None) -> bool:
        """Assign a role to a user with optional custom permissions"""
        try:
            base_permissions = self.role_permissions.get(role, set())
            
            user_perms = UserPermissions(
                user_id=user_id,
                role=role,
                permissions=base_permissions.copy(),
                custom_permissions=custom_permissions or set(),
                restrictions=restrictions or set(),
                expires_at=expires_at
            )
            
            self.user_permissions[user_id] = user_perms
            
            # Log activity
            await self._log_user_activity(
                user_id=user_id,
                action="role_assigned",
                resource="user_permissions",
                success=True,
                details={"role": role.value, "permissions_count": len(user_perms.permissions)}
            )
            
            logger.info(f"👤 Role {role.value} assigned to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign role to user {user_id}: {e}")
            return False
    
    async def check_user_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if a user has a specific permission"""
        if user_id not in self.user_permissions:
            return False
        
        user_perms = self.user_permissions[user_id]
        
        # Check if permission is restricted
        if permission.value in user_perms.restrictions:
            return False
        
        # Check if permission expired
        if user_perms.expires_at and user_perms.expires_at < datetime.now(timezone.utc):
            return False
        
        # Check base permissions
        if permission in user_perms.permissions:
            return True
        
        # Check custom permissions
        if permission.value in user_perms.custom_permissions:
            return True
        
        return False
    
    async def get_user_permissions(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive user permissions information"""
        if user_id not in self.user_permissions:
            return None
        
        user_perms = self.user_permissions[user_id]
        
        return {
            "user_id": user_id,
            "role": user_perms.role.value,
            "permissions": [p.value for p in user_perms.permissions],
            "custom_permissions": list(user_perms.custom_permissions),
            "restrictions": list(user_perms.restrictions),
            "expires_at": user_perms.expires_at.isoformat() if user_perms.expires_at else None,
            "is_expired": user_perms.expires_at and user_perms.expires_at < datetime.now(timezone.utc) if user_perms.expires_at else False
        }
    
    async def update_user_permissions(self, user_id: str, 
                                    add_permissions: Set[str] = None,
                                    remove_permissions: Set[str] = None,
                                    add_restrictions: Set[str] = None,
                                    remove_restrictions: Set[str] = None) -> bool:
        """Update user permissions dynamically"""
        try:
            if user_id not in self.user_permissions:
                return False
            
            user_perms = self.user_permissions[user_id]
            
            # Update custom permissions
            if add_permissions:
                user_perms.custom_permissions.update(add_permissions)
            if remove_permissions:
                user_perms.custom_permissions -= remove_permissions
            
            # Update restrictions
            if add_restrictions:
                user_perms.restrictions.update(add_restrictions)
            if remove_restrictions:
                user_perms.restrictions -= remove_restrictions
            
            # Log activity
            await self._log_user_activity(
                user_id=user_id,
                action="permissions_updated",
                resource="user_permissions",
                success=True,
                details={
                    "added_permissions": list(add_permissions) if add_permissions else [],
                    "removed_permissions": list(remove_permissions) if remove_permissions else []
                }
            )
            
            logger.info(f"🔄 Permissions updated for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update permissions for user {user_id}: {e}")
            return False
    
    # Multi-tenant Management
    async def create_tenant(self, name: str, domain: str, subscription_tier: str = "basic",
                          settings: Dict[str, Any] = None) -> str:
        """Create a new tenant"""
        try:
            tenant_id = str(uuid.uuid4())
            
            tenant = Tenant(
                tenant_id=tenant_id,
                name=name,
                domain=domain,
                settings=settings or {},
                subscription_tier=subscription_tier,
                created_at=datetime.now(timezone.utc),
                is_active=True,
                user_limit=self._get_user_limit_for_tier(subscription_tier),
                feature_flags=self._get_features_for_tier(subscription_tier)
            )
            
            self.tenants[tenant_id] = tenant
            
            logger.info(f"🏢 Tenant created: {name} ({tenant_id})")
            return tenant_id
            
        except Exception as e:
            logger.error(f"Failed to create tenant: {e}")
            return ""
    
    def _get_user_limit_for_tier(self, tier: str) -> int:
        """Get user limit based on subscription tier"""
        limits = {
            "basic": 50,
            "premium": 500,
            "enterprise": 10000
        }
        return limits.get(tier, 50)
    
    def _get_features_for_tier(self, tier: str) -> Set[str]:
        """Get feature flags based on subscription tier"""
        features = {
            "basic": {"basic_features"},
            "premium": {"basic_features", "phase5_features"},
            "enterprise": {"basic_features", "phase5_features", "phase6_features", "advanced_analytics"}
        }
        return features.get(tier, {"basic_features"})
    
    async def get_tenant_info(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant information"""
        if tenant_id not in self.tenants:
            return None
        
        tenant = self.tenants[tenant_id]
        return {
            "tenant_id": tenant.tenant_id,
            "name": tenant.name,
            "domain": tenant.domain,
            "subscription_tier": tenant.subscription_tier,
            "is_active": tenant.is_active,
            "user_limit": tenant.user_limit,
            "created_at": tenant.created_at.isoformat(),
            "settings": tenant.settings,
            "feature_flags": list(tenant.feature_flags)
        }
    
    # User Activity Tracking
    async def _log_user_activity(self, user_id: str, action: str, resource: str,
                               success: bool, ip_address: str = "127.0.0.1",
                               user_agent: str = "System", details: Dict[str, Any] = None):
        """Log user activity for audit purposes"""
        activity = UserActivity(
            user_id=user_id,
            action=action,
            resource=resource,
            timestamp=datetime.now(timezone.utc),
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details
        )
        
        self.user_activities.append(activity)
        
        # Keep only last 1000 activities for memory management
        if len(self.user_activities) > 1000:
            self.user_activities = self.user_activities[-1000:]
    
    async def get_user_activity_log(self, user_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user activity log"""
        activities = self.user_activities
        
        if user_id:
            activities = [a for a in activities if a.user_id == user_id]
        
        # Sort by timestamp (newest first) and limit
        activities = sorted(activities, key=lambda x: x.timestamp, reverse=True)[:limit]
        
        return [
            {
                "user_id": activity.user_id,
                "action": activity.action,
                "resource": activity.resource,
                "timestamp": activity.timestamp.isoformat(),
                "ip_address": activity.ip_address,
                "user_agent": activity.user_agent,
                "success": activity.success,
                "details": activity.details
            }
            for activity in activities
        ]
    
    # User Management Analytics
    async def get_user_management_analytics(self) -> Dict[str, Any]:
        """Get comprehensive user management analytics"""
        try:
            # Role distribution
            role_counts = {}
            for user_perms in self.user_permissions.values():
                role = user_perms.role.value
                role_counts[role] = role_counts.get(role, 0) + 1
            
            # Permission usage
            permission_usage = {}
            for user_perms in self.user_permissions.values():
                for permission in user_perms.permissions:
                    perm_name = permission.value
                    permission_usage[perm_name] = permission_usage.get(perm_name, 0) + 1
            
            # Recent activity
            recent_activities = len([
                a for a in self.user_activities 
                if a.timestamp > datetime.now(timezone.utc) - timedelta(hours=24)
            ])
            
            # Tenant statistics
            tenant_stats = {
                "total_tenants": len(self.tenants),
                "active_tenants": len([t for t in self.tenants.values() if t.is_active]),
                "subscription_tiers": {}
            }
            
            for tenant in self.tenants.values():
                tier = tenant.subscription_tier
                tenant_stats["subscription_tiers"][tier] = tenant_stats["subscription_tiers"].get(tier, 0) + 1
            
            analytics = {
                "overview": {
                    "total_users": len(self.user_permissions),
                    "total_roles": len(role_counts),
                    "active_sessions": len(self.active_sessions),
                    "recent_activities_24h": recent_activities
                },
                "roles": role_counts,
                "permissions": permission_usage,
                "tenants": tenant_stats,
                "activity_trends": {
                    "login_trend": "stable",
                    "permission_changes": "increasing",
                    "role_assignments": "stable"
                },
                "recommendations": [
                    "Review users with expired permissions",
                    "Consider role consolidation for efficiency",
                    "Monitor high-privilege user activities"
                ]
            }
            
            logger.info("👥 Generated user management analytics")
            return analytics
            
        except Exception as e:
            logger.error(f"User management analytics generation failed: {e}")
            return {}
    
    # Advanced User Operations
    async def bulk_role_assignment(self, user_role_mappings: List[Dict[str, str]]) -> Dict[str, Any]:
        """Assign roles to multiple users in bulk"""
        results = {"success": 0, "failed": 0, "errors": []}
        
        for mapping in user_role_mappings:
            try:
                user_id = mapping["user_id"]
                role_str = mapping["role"]
                role = UserRole(role_str)
                
                success = await self.assign_user_role(user_id, role)
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Failed to assign role to {user_id}")
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error processing {mapping.get('user_id', 'unknown')}: {str(e)}")
        
        logger.info(f"📋 Bulk role assignment completed: {results['success']} success, {results['failed']} failed")
        return results
    
    async def get_role_hierarchy(self) -> Dict[str, Any]:
        """Get role hierarchy and permission structure"""
        hierarchy = {}
        
        for role, permissions in self.role_permissions.items():
            hierarchy[role.value] = {
                "permissions": [p.value for p in permissions],
                "permission_count": len(permissions),
                "level": self._get_role_level(role)
            }
        
        return {
            "roles": hierarchy,
            "total_permissions": len(Permission),
            "hierarchy_levels": ["guest", "buyer", "seller", "moderator", "admin", "super_admin"]
        }
    
    def _get_role_level(self, role: UserRole) -> int:
        """Get numeric level for role hierarchy"""
        levels = {
            UserRole.GUEST: 0,
            UserRole.BUYER: 1,
            UserRole.SELLER: 2,
            UserRole.MODERATOR: 3,
            UserRole.ADMIN: 4,
            UserRole.SUPER_ADMIN: 5
        }
        return levels.get(role, 0)
    
    # Service Health
    async def get_service_health(self) -> Dict[str, Any]:
        """Get enhanced user management service health information"""
        return {
            "service_name": self.service_name,
            "version": self.version,
            "status": self.status,
            "last_updated": self.last_updated.isoformat(),
            "capabilities": [
                "Advanced Role Management",
                "Multi-tenant Architecture",
                "Permission System",
                "Activity Tracking",
                "Bulk Operations"
            ],
            "managed_users": len(self.user_permissions),
            "active_tenants": len([t for t in self.tenants.values() if t.is_active]),
            "total_roles": len(UserRole),
            "total_permissions": len(Permission),
            "activity_logs": len(self.user_activities)
        }

# Global service instance
_enhanced_user_management_service = None

async def get_enhanced_user_management_service() -> EnhancedUserManagementService:
    """Get or create the global Enhanced User Management service instance"""
    global _enhanced_user_management_service
    
    if _enhanced_user_management_service is None:
        _enhanced_user_management_service = EnhancedUserManagementService()
        await _enhanced_user_management_service.initialize()
    
    return _enhanced_user_management_service