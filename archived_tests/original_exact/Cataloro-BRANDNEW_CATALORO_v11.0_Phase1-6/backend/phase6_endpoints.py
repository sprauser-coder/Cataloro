"""
Phase 6 - Enterprise Intelligence & Global Expansion Endpoints
Comprehensive API endpoints for Phase 6 advanced features
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Create router for Phase 6 endpoints
phase6_router = APIRouter(prefix="/api/v2/phase6", tags=["Phase 6 Enterprise Features"])

# Advanced Analytics Endpoints
@phase6_router.get("/analytics/dashboard")
async def get_analytics_dashboard():
    """Get comprehensive analytics dashboard data"""
    try:
        from advanced_analytics_service import get_advanced_analytics_service
        analytics_service = await get_advanced_analytics_service()
        
        dashboard_data = await analytics_service.get_predictive_dashboard_data()
        
        return {
            "success": True,
            "dashboard_data": dashboard_data
        }
    except Exception as e:
        logger.error(f"Analytics dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.get("/analytics/market-trends")
async def get_market_trends(time_period: str = "30d"):
    """Get market trend analysis"""
    try:
        from advanced_analytics_service import get_advanced_analytics_service
        analytics_service = await get_advanced_analytics_service()
        
        trends = await analytics_service.analyze_market_trends(time_period)
        
        return {
            "success": True,
            "trends": [
                {
                    "category": trend.category,
                    "trend_direction": trend.trend_direction,
                    "trend_strength": trend.trend_strength,
                    "predicted_growth": trend.predicted_growth,
                    "confidence_score": trend.confidence_score,
                    "time_period": trend.time_period
                }
                for trend in trends
            ]
        }
    except Exception as e:
        logger.error(f"Market trends analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.get("/analytics/seller-performance")
async def get_seller_performance(seller_id: Optional[str] = None):
    """Get seller performance forecasting"""
    try:
        from advanced_analytics_service import get_advanced_analytics_service
        analytics_service = await get_advanced_analytics_service()
        
        performance = await analytics_service.forecast_seller_performance(seller_id)
        
        return {
            "success": True,
            "seller_performance": [
                {
                    "seller_id": perf.seller_id,
                    "seller_name": perf.seller_name,
                    "current_rating": perf.current_rating,
                    "predicted_rating": perf.predicted_rating,
                    "sales_trend": perf.sales_trend,
                    "revenue_forecast": perf.revenue_forecast,
                    "risk_score": perf.risk_score,
                    "recommendations": perf.recommendations
                }
                for perf in performance
            ]
        }
    except Exception as e:
        logger.error(f"Seller performance forecasting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.get("/analytics/revenue-insights")
async def get_revenue_insights(period: str = "monthly"):
    """Get revenue optimization insights"""
    try:
        from advanced_analytics_service import get_advanced_analytics_service
        analytics_service = await get_advanced_analytics_service()
        
        insights = await analytics_service.generate_revenue_insights(period)
        
        return {
            "success": True,
            "revenue_insights": [
                {
                    "period": insight.period,
                    "actual_revenue": insight.actual_revenue,
                    "predicted_revenue": insight.predicted_revenue,
                    "growth_rate": insight.growth_rate,
                    "key_drivers": insight.key_drivers,
                    "optimization_opportunities": insight.optimization_opportunities
                }
                for insight in insights
            ]
        }
    except Exception as e:
        logger.error(f"Revenue insights generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.get("/analytics/category-performance")
async def get_category_performance():
    """Get category performance analysis"""
    try:
        from advanced_analytics_service import get_advanced_analytics_service
        analytics_service = await get_advanced_analytics_service()
        
        categories = await analytics_service.analyze_category_performance()
        
        return {
            "success": True,
            "categories": categories
        }
    except Exception as e:
        logger.error(f"Category performance analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enterprise Security Endpoints
@phase6_router.get("/security/dashboard")
async def get_security_dashboard():
    """Get comprehensive security dashboard data"""
    try:
        from enterprise_security_service import get_enterprise_security_service
        security_service = await get_enterprise_security_service()
        
        dashboard_data = await security_service.get_security_dashboard_data()
        
        return {
            "success": True,
            "security_data": dashboard_data
        }
    except Exception as e:
        logger.error(f"Security dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.post("/security/log-event")
async def log_security_event(event_data: Dict[str, Any]):
    """Log a security event"""
    try:
        from enterprise_security_service import get_enterprise_security_service
        security_service = await get_enterprise_security_service()
        
        event_id = await security_service.log_security_event(
            event_type=event_data.get("event_type", "unknown"),
            severity=event_data.get("severity", "medium"),
            user_id=event_data.get("user_id"),
            ip_address=event_data.get("ip_address", "unknown"),
            description=event_data.get("description", "")
        )
        
        return {
            "success": True,
            "event_id": event_id
        }
    except Exception as e:
        logger.error(f"Security event logging failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.get("/security/compliance")
async def get_compliance_status():
    """Get compliance status"""
    try:
        from enterprise_security_service import get_enterprise_security_service
        security_service = await get_enterprise_security_service()
        
        compliance_data = await security_service.get_compliance_status()
        
        return {
            "success": True,
            "compliance": compliance_data
        }
    except Exception as e:
        logger.error(f"Compliance status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.get("/security/user-insights")
async def get_user_security_insights(limit: int = 20):
    """Get user security insights"""
    try:
        from enterprise_security_service import get_enterprise_security_service
        security_service = await get_enterprise_security_service()
        
        insights = await security_service.get_user_security_insights(limit)
        
        return {
            "success": True,
            "user_insights": insights
        }
    except Exception as e:
        logger.error(f"User security insights failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Fraud Detection Endpoints
@phase6_router.get("/fraud/dashboard")
async def get_fraud_dashboard():
    """Get fraud detection dashboard data"""
    try:
        from fraud_detection_service import get_fraud_detection_service
        fraud_service = await get_fraud_detection_service()
        
        dashboard_data = await fraud_service.get_fraud_dashboard_data()
        
        return {
            "success": True,
            "fraud_data": dashboard_data
        }
    except Exception as e:
        logger.error(f"Fraud dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.post("/fraud/analyze-transaction")
async def analyze_transaction(transaction_data: Dict[str, Any]):
    """Analyze a transaction for fraud risk"""
    try:
        from fraud_detection_service import get_fraud_detection_service
        fraud_service = await get_fraud_detection_service()
        
        analysis = await fraud_service.analyze_transaction(
            user_id=transaction_data.get("user_id", ""),
            amount=float(transaction_data.get("amount", 0)),
            transaction_data=transaction_data
        )
        
        return {
            "success": True,
            "analysis": {
                "transaction_id": analysis.transaction_id,
                "fraud_probability": analysis.fraud_probability,
                "risk_factors": analysis.risk_factors,
                "anomaly_score": analysis.anomaly_score,
                "recommendation": analysis.recommendation,
                "analyzed_at": analysis.analyzed_at.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Transaction analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.post("/fraud/resolve-alert/{alert_id}")
async def resolve_fraud_alert(alert_id: str, resolution_data: Dict[str, Any]):
    """Resolve a fraud alert"""
    try:
        from fraud_detection_service import get_fraud_detection_service
        fraud_service = await get_fraud_detection_service()
        
        success = await fraud_service.resolve_fraud_alert(
            alert_id=alert_id,
            resolution=resolution_data.get("resolution", "resolved"),
            notes=resolution_data.get("notes", "")
        )
        
        return {
            "success": success,
            "message": "Alert resolved successfully" if success else "Alert not found"
        }
    except Exception as e:
        logger.error(f"Fraud alert resolution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Chatbot Endpoints
@phase6_router.post("/chatbot/start-session")
async def start_chat_session(session_data: Dict[str, Any] = None):
    """Start a new chat session"""
    try:
        from ai_chatbot_service import get_ai_chatbot_service
        chatbot_service = await get_ai_chatbot_service()
        
        user_id = session_data.get("user_id") if session_data else None
        session_id = await chatbot_service.start_chat_session(user_id)
        
        return {
            "success": True,
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Chat session start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.post("/chatbot/message")
async def process_chat_message(message_data: Dict[str, Any]):
    """Process a chat message"""
    try:
        from ai_chatbot_service import get_ai_chatbot_service
        chatbot_service = await get_ai_chatbot_service()
        
        result = await chatbot_service.process_message(
            session_id=message_data.get("session_id", ""),
            message=message_data.get("message", ""),
            user_id=message_data.get("user_id")
        )
        
        return {
            "success": True,
            "chat_response": result
        }
    except Exception as e:
        logger.error(f"Chat message processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.get("/chatbot/analytics")
async def get_chat_analytics():
    """Get chat analytics"""
    try:
        from ai_chatbot_service import get_ai_chatbot_service
        chatbot_service = await get_ai_chatbot_service()
        
        analytics = await chatbot_service.get_chat_analytics()
        
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        logger.error(f"Chat analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.post("/chatbot/end-session/{session_id}")
async def end_chat_session(session_id: str, feedback_data: Dict[str, Any] = None):
    """End a chat session"""
    try:
        from ai_chatbot_service import get_ai_chatbot_service
        chatbot_service = await get_ai_chatbot_service()
        
        satisfaction_rating = None
        if feedback_data:
            satisfaction_rating = feedback_data.get("satisfaction_rating")
        
        success = await chatbot_service.end_chat_session(session_id, satisfaction_rating)
        
        return {
            "success": success,
            "message": "Session ended successfully" if success else "Session not found"
        }
    except Exception as e:
        logger.error(f"Chat session end failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Internationalization Endpoints
@phase6_router.get("/i18n/languages")
async def get_supported_languages():
    """Get supported languages"""
    try:
        from internationalization_service import get_internationalization_service
        i18n_service = await get_internationalization_service()
        
        languages = await i18n_service.get_supported_languages()
        
        return {
            "success": True,
            "languages": languages
        }
    except Exception as e:
        logger.error(f"Languages retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.get("/i18n/regions")
async def get_supported_regions():
    """Get supported regions"""
    try:
        from internationalization_service import get_internationalization_service
        i18n_service = await get_internationalization_service()
        
        regions = await i18n_service.get_supported_regions()
        
        return {
            "success": True,
            "regions": regions
        }
    except Exception as e:
        logger.error(f"Regions retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.get("/i18n/translations/{language_code}")
async def get_translations(language_code: str):
    """Get translations for a specific language"""
    try:
        from internationalization_service import get_internationalization_service
        i18n_service = await get_internationalization_service()
        
        translations = await i18n_service.get_translations_for_language(language_code)
        
        return {
            "success": True,
            "language_code": language_code,
            "translations": translations
        }
    except Exception as e:
        logger.error(f"Translations retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.get("/i18n/compliance/{region_code}")
async def get_compliance_requirements(region_code: str):
    """Get compliance requirements for a region"""
    try:
        from internationalization_service import get_internationalization_service
        i18n_service = await get_internationalization_service()
        
        compliance_status = await i18n_service.check_compliance_status(region_code)
        
        return {
            "success": True,
            "compliance_status": compliance_status
        }
    except Exception as e:
        logger.error(f"Compliance requirements failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.get("/i18n/analytics")
async def get_localization_analytics():
    """Get localization analytics"""
    try:
        from internationalization_service import get_internationalization_service
        i18n_service = await get_internationalization_service()
        
        analytics = await i18n_service.get_localization_analytics()
        
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        logger.error(f"Localization analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced User Management Endpoints
@phase6_router.get("/users/analytics")
async def get_user_management_analytics():
    """Get user management analytics"""
    try:
        from enhanced_user_management_service import get_enhanced_user_management_service
        user_service = await get_enhanced_user_management_service()
        
        analytics = await user_service.get_user_management_analytics()
        
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        logger.error(f"User management analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.get("/users/permissions/{user_id}")
async def get_user_permissions(user_id: str):
    """Get user permissions"""
    try:
        from enhanced_user_management_service import get_enhanced_user_management_service
        user_service = await get_enhanced_user_management_service()
        
        permissions = await user_service.get_user_permissions(user_id)
        
        if not permissions:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "permissions": permissions
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User permissions retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.get("/users/role-hierarchy")
async def get_role_hierarchy():
    """Get role hierarchy information"""
    try:
        from enhanced_user_management_service import get_enhanced_user_management_service
        user_service = await get_enhanced_user_management_service()
        
        hierarchy = await user_service.get_role_hierarchy()
        
        return {
            "success": True,
            "hierarchy": hierarchy
        }
    except Exception as e:
        logger.error(f"Role hierarchy retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase6_router.get("/users/activity")
async def get_user_activity_log(user_id: Optional[str] = None, limit: int = 50):
    """Get user activity log"""
    try:
        from enhanced_user_management_service import get_enhanced_user_management_service
        user_service = await get_enhanced_user_management_service()
        
        activities = await user_service.get_user_activity_log(user_id, limit)
        
        return {
            "success": True,
            "activities": activities
        }
    except Exception as e:
        logger.error(f"User activity log failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Phase 6 Status Endpoint
@phase6_router.get("/status")
async def get_phase6_status():
    """Get comprehensive Phase 6 services status"""
    try:
        status = {
            "phase": "6 - Enterprise Intelligence & Global Expansion",
            "services": {},
            "timestamp": "2025-01-01T00:00:00Z"
        }
        
        # Advanced Analytics service status
        try:
            from advanced_analytics_service import get_advanced_analytics_service
            analytics_service = await get_advanced_analytics_service()
            status["services"]["advanced_analytics"] = await analytics_service.get_service_health()
        except Exception as e:
            status["services"]["advanced_analytics"] = {"status": "error", "error": str(e)}
        
        # Enterprise Security service status
        try:
            from enterprise_security_service import get_enterprise_security_service
            security_service = await get_enterprise_security_service()
            status["services"]["enterprise_security"] = await security_service.get_service_health()
        except Exception as e:
            status["services"]["enterprise_security"] = {"status": "error", "error": str(e)}
        
        # Fraud Detection service status
        try:
            from fraud_detection_service import get_fraud_detection_service
            fraud_service = await get_fraud_detection_service()
            status["services"]["fraud_detection"] = await fraud_service.get_service_health()
        except Exception as e:
            status["services"]["fraud_detection"] = {"status": "error", "error": str(e)}
        
        # AI Chatbot service status
        try:
            from ai_chatbot_service import get_ai_chatbot_service
            chatbot_service = await get_ai_chatbot_service()
            status["services"]["ai_chatbot"] = await chatbot_service.get_service_health()
        except Exception as e:
            status["services"]["ai_chatbot"] = {"status": "error", "error": str(e)}
        
        # Internationalization service status
        try:
            from internationalization_service import get_internationalization_service
            i18n_service = await get_internationalization_service()
            status["services"]["internationalization"] = await i18n_service.get_service_health()
        except Exception as e:
            status["services"]["internationalization"] = {"status": "error", "error": str(e)}
        
        # Enhanced User Management service status
        try:
            from enhanced_user_management_service import get_enhanced_user_management_service
            user_service = await get_enhanced_user_management_service()
            status["services"]["enhanced_user_management"] = await user_service.get_service_health()
        except Exception as e:
            status["services"]["enhanced_user_management"] = {"status": "error", "error": str(e)}
        
        # Determine overall status
        service_statuses = [s.get("status", "error") for s in status["services"].values()]
        if all(s == "operational" for s in service_statuses):
            status["overall_status"] = "operational"
        elif any(s == "operational" for s in service_statuses):
            status["overall_status"] = "partial"
        else:
            status["overall_status"] = "error"
        
        return status
        
    except Exception as e:
        logger.error(f"Phase 6 status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))