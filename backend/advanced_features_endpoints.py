"""
Advanced Features Endpoints for Cataloro Marketplace
Consolidated Phase 5 + Phase 6 endpoints into unified advanced features API
Includes: Real-time, Multi-currency, Escrow, AI, Analytics, Security, Fraud Detection, Chatbot, i18n, User Management
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Create router for Advanced Features endpoints
advanced_features_router = APIRouter(prefix="/api/v2/advanced", tags=["Advanced Marketplace Features"])

# ==== REAL-TIME WEBSOCKET ENDPOINTS ====

@advanced_features_router.get("/websocket/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    try:
        from websocket_service import get_websocket_service
        ws_service = get_websocket_service()
        if ws_service:
            stats = await ws_service.get_connection_stats()
            return {"success": True, "stats": stats}
        return {"success": False, "error": "WebSocket service not available"}
    except Exception as e:
        logger.error(f"WebSocket stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.post("/websocket/broadcast")
async def broadcast_notification(notification_data: dict):
    """Broadcast notification to specific user or all users"""
    try:
        from websocket_service import get_websocket_service
        ws_service = get_websocket_service()
        if not ws_service:
            return {"success": False, "error": "WebSocket service not available"}
        
        user_id = notification_data.get("user_id")
        message = notification_data.get("message", {})
        
        if user_id:
            await ws_service.send_notification(user_id, message)
        
        return {"success": True, "message": "Notification sent"}
    except Exception as e:
        logger.error(f"Broadcast notification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==== MULTI-CURRENCY ENDPOINTS ====

@advanced_features_router.get("/currency/supported")
async def get_supported_currencies():
    """Get list of supported currencies"""
    try:
        from multicurrency_service import get_multicurrency_service
        currency_service = get_multicurrency_service()
        currencies = await currency_service.get_supported_currencies()
        return {"success": True, "currencies": currencies}
    except Exception as e:
        logger.error(f"Get supported currencies failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.get("/currency/rates")
async def get_exchange_rates():
    """Get current exchange rates"""
    try:
        from multicurrency_service import get_multicurrency_service
        currency_service = get_multicurrency_service()
        rates = await currency_service.get_exchange_rates()
        return {"success": True, "rates": rates, "base_currency": "EUR"}
    except Exception as e:
        logger.error(f"Get exchange rates failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.post("/currency/convert")
async def convert_currency(conversion_data: dict):
    """Convert amount between currencies"""
    try:
        from multicurrency_service import get_multicurrency_service
        currency_service = get_multicurrency_service()
        
        amount = conversion_data.get("amount")
        from_currency = conversion_data.get("from_currency")
        to_currency = conversion_data.get("to_currency")
        
        if not all([amount, from_currency, to_currency]):
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        result = await currency_service.convert_currency(amount, from_currency, to_currency)
        return {"success": True, "conversion": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Currency conversion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.post("/currency/user/preference")
async def set_user_currency_preference(preference_data: dict):
    """Set user's preferred currency"""
    try:
        from multicurrency_service import get_multicurrency_service
        currency_service = get_multicurrency_service()
        
        user_id = preference_data.get("user_id")
        currency_code = preference_data.get("currency_code")
        
        if not user_id or not currency_code:
            raise HTTPException(status_code=400, detail="Missing user_id or currency_code")
        
        success = await currency_service.set_user_preferred_currency(user_id, currency_code)
        
        if success:
            return {"success": True, "message": "Currency preference updated"}
        else:
            return {"success": False, "error": "Invalid currency or update failed"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set currency preference failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==== ESCROW ENDPOINTS ====

@advanced_features_router.post("/escrow/create")
async def create_escrow_transaction(escrow_data: dict):
    """Create a new escrow transaction"""
    try:
        from escrow_service import get_escrow_service
        escrow_service_instance = get_escrow_service()
        
        result = await escrow_service_instance.create_escrow(
            listing_id=escrow_data.get("listing_id"),
            buyer_id=escrow_data.get("buyer_id"),
            seller_id=escrow_data.get("seller_id"),
            amount=escrow_data.get("amount"),
            currency=escrow_data.get("currency", "EUR"),
            payment_method=escrow_data.get("payment_method", "bank_transfer")
        )
        
        return result
    except Exception as e:
        logger.error(f"Create escrow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.get("/escrow/{escrow_id}")
async def get_escrow_details(escrow_id: str):
    """Get escrow transaction details"""
    try:
        from escrow_service import get_escrow_service
        escrow_service_instance = get_escrow_service()
        
        result = await escrow_service_instance.get_escrow_details(escrow_id)
        return result
    except Exception as e:
        logger.error(f"Get escrow details failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.get("/escrow/user/{user_id}")
async def get_user_escrows(user_id: str, status: str = None, limit: int = 50):
    """Get user's escrow transactions"""
    try:
        from escrow_service import get_escrow_service
        escrow_service_instance = get_escrow_service()
        
        escrows = await escrow_service_instance.get_user_escrows(user_id, status, limit)
        return {"success": True, "escrows": escrows}
    except Exception as e:
        logger.error(f"Get user escrows failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==== AI RECOMMENDATION ENDPOINTS ====

@advanced_features_router.post("/ai/interaction")
async def track_user_interaction(interaction_data: dict):
    """Track user interaction for AI learning"""
    try:
        from ai_recommendation_service import get_ai_recommendation_service
        ai_service = get_ai_recommendation_service()
        
        await ai_service.track_user_interaction(
            user_id=interaction_data.get("user_id"),
            listing_id=interaction_data.get("listing_id"),
            interaction_type=interaction_data.get("interaction_type"),
            context=interaction_data.get("context", {})
        )
        
        return {"success": True, "message": "Interaction tracked"}
    except Exception as e:
        logger.error(f"Track interaction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.get("/ai/recommendations/{user_id}")
async def get_personalized_recommendations(user_id: str, limit: int = 10):
    """Get personalized recommendations for user"""
    try:
        from ai_recommendation_service import get_ai_recommendation_service
        ai_service = get_ai_recommendation_service()
        
        recommendations = await ai_service.get_personalized_recommendations(user_id, limit)
        return {"success": True, "recommendations": recommendations}
    except Exception as e:
        logger.error(f"Get recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.get("/ai/similar/{listing_id}")
async def get_similar_items(listing_id: str, limit: int = 5):
    """Get items similar to a specific listing"""
    try:
        from ai_recommendation_service import get_ai_recommendation_service
        ai_service = get_ai_recommendation_service()
        
        similar_items = await ai_service.get_similar_items(listing_id, limit)
        return {"success": True, "similar_items": similar_items}
    except Exception as e:
        logger.error(f"Get similar items failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.get("/ai/trending")
async def get_trending_items(category: str = None, timeframe_hours: int = 24, limit: int = 10):
    """Get trending items"""
    try:
        from ai_recommendation_service import get_ai_recommendation_service
        ai_service = get_ai_recommendation_service()
        
        trending_items = await ai_service.get_trending_items(category, timeframe_hours, limit)
        return {"success": True, "trending_items": trending_items}
    except Exception as e:
        logger.error(f"Get trending items failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==== UNIFIED ANALYTICS ENDPOINTS ====

@advanced_features_router.get("/analytics/dashboard")
async def get_unified_analytics_dashboard():
    """Get comprehensive unified analytics dashboard"""
    try:
        from unified_analytics_service import get_unified_analytics_service
        analytics_service = await get_unified_analytics_service()
        
        dashboard_data = await analytics_service.get_unified_dashboard_data()
        
        return {
            "success": True,
            "dashboard_data": dashboard_data
        }
    except Exception as e:
        logger.error(f"Unified analytics dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.get("/analytics/user")
async def get_user_analytics(days: int = 30):
    """Get user analytics"""
    try:
        from unified_analytics_service import get_unified_analytics_service
        analytics_service = await get_unified_analytics_service()
        
        user_analytics = await analytics_service.get_user_analytics(days)
        
        return {
            "success": True,
            "analytics": user_analytics
        }
    except Exception as e:
        logger.error(f"User analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.get("/analytics/sales")
async def get_sales_analytics(days: int = 30):
    """Get sales analytics"""
    try:
        from unified_analytics_service import get_unified_analytics_service
        analytics_service = await get_unified_analytics_service()
        
        sales_analytics = await analytics_service.get_sales_analytics(days)
        
        return {
            "success": True,
            "analytics": sales_analytics
        }
    except Exception as e:
        logger.error(f"Sales analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.get("/analytics/marketplace")
async def get_marketplace_analytics(days: int = 30):
    """Get marketplace analytics"""
    try:
        from unified_analytics_service import get_unified_analytics_service
        analytics_service = await get_unified_analytics_service()
        
        marketplace_analytics = await analytics_service.get_marketplace_analytics(days)
        
        return {
            "success": True,
            "analytics": marketplace_analytics
        }
    except Exception as e:
        logger.error(f"Marketplace analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.get("/analytics/predictive")
async def get_predictive_analytics(forecast_days: int = 30):
    """Get predictive analytics"""
    try:
        from unified_analytics_service import get_unified_analytics_service
        analytics_service = await get_unified_analytics_service()
        
        predictions = await analytics_service.get_predictive_analytics(forecast_days)
        
        return {
            "success": True,
            "predictions": predictions
        }
    except Exception as e:
        logger.error(f"Predictive analytics failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.get("/analytics/market-trends")
async def get_market_trends(time_period: str = "30d"):
    """Get market trend analysis"""
    try:
        from unified_analytics_service import get_unified_analytics_service
        analytics_service = await get_unified_analytics_service()
        
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

@advanced_features_router.get("/analytics/seller-performance")
async def get_seller_performance(seller_id: Optional[str] = None):
    """Get seller performance forecasting"""
    try:
        from unified_analytics_service import get_unified_analytics_service
        analytics_service = await get_unified_analytics_service()
        
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

@advanced_features_router.get("/analytics/revenue-insights")
async def get_revenue_insights(period: str = "monthly"):
    """Get revenue optimization insights"""
    try:
        from unified_analytics_service import get_unified_analytics_service
        analytics_service = await get_unified_analytics_service()
        
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

# ==== UNIFIED SECURITY ENDPOINTS ====

@advanced_features_router.get("/security/dashboard")
async def get_security_dashboard():
    """Get comprehensive security dashboard data"""
    try:
        from unified_security_service import get_unified_security_service
        security_service = get_unified_security_service()
        
        dashboard_data = await security_service.get_security_dashboard_data()
        
        return {
            "success": True,
            "security_data": dashboard_data
        }
    except Exception as e:
        logger.error(f"Security dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.post("/security/log-event")
async def log_security_event(event_data: Dict[str, Any]):
    """Log a security event"""
    try:
        from unified_security_service import get_unified_security_service
        security_service = get_unified_security_service()
        
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

@advanced_features_router.get("/security/compliance")
async def get_compliance_status():
    """Get compliance status"""
    try:
        from unified_security_service import get_unified_security_service
        security_service = get_unified_security_service()
        
        compliance_data = await security_service.get_compliance_status()
        
        return {
            "success": True,
            "compliance": compliance_data
        }
    except Exception as e:
        logger.error(f"Compliance status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@advanced_features_router.get("/security/user-insights")
async def get_user_security_insights(limit: int = 20):
    """Get user security insights"""
    try:
        from unified_security_service import get_unified_security_service
        security_service = get_unified_security_service()
        
        insights = await security_service.get_user_security_insights(limit)
        
        return {
            "success": True,
            "user_insights": insights
        }
    except Exception as e:
        logger.error(f"User security insights failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==== FRAUD DETECTION ENDPOINTS ====

@advanced_features_router.get("/fraud/dashboard")
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

@advanced_features_router.post("/fraud/analyze-transaction")
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

# ==== AI CHATBOT ENDPOINTS ====

@advanced_features_router.post("/chatbot/start-session")
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

@advanced_features_router.post("/chatbot/message")
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

@advanced_features_router.get("/chatbot/analytics")
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

# ==== INTERNATIONALIZATION ENDPOINTS ====

@advanced_features_router.get("/i18n/languages")
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

@advanced_features_router.get("/i18n/regions")
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

# ==== ENHANCED USER MANAGEMENT ENDPOINTS ====

@advanced_features_router.get("/users/analytics")
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

@advanced_features_router.get("/users/permissions/{user_id}")
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

# ==== ADVANCED FEATURES STATUS ENDPOINT ====

@advanced_features_router.get("/status")
async def get_advanced_features_status():
    """Get comprehensive status of all advanced features"""
    try:
        status = {
            "service": "Advanced Marketplace Features",
            "version": "2.0.0 - Consolidated",
            "services": {},
            "timestamp": "2025-01-01T00:00:00Z"
        }
        
        # WebSocket service status
        try:
            from websocket_service import get_websocket_service
            ws_service = get_websocket_service()
            if ws_service:
                ws_stats = await ws_service.get_connection_stats()
                status["services"]["websocket"] = {
                    "status": "operational",
                    "connections": ws_stats.get("total_connections", 0),
                    "users": ws_stats.get("unique_users", 0)
                }
            else:
                status["services"]["websocket"] = {"status": "not_initialized"}
        except Exception as e:
            status["services"]["websocket"] = {"status": "error", "error": str(e)}
        
        # Multi-currency service status
        try:
            from multicurrency_service import get_multicurrency_service
            currency_service = get_multicurrency_service()
            if currency_service:
                currency_stats = await currency_service.get_currency_stats()
                status["services"]["multicurrency"] = {
                    "status": currency_stats.get("service_status", "unknown"),
                    "supported_currencies": currency_stats.get("supported_currencies", 0),
                    "base_currency": currency_stats.get("base_currency", "EUR")
                }
            else:
                status["services"]["multicurrency"] = {"status": "not_initialized"}
        except Exception as e:
            status["services"]["multicurrency"] = {"status": "error", "error": str(e)}
        
        # Unified Analytics service status
        try:
            from unified_analytics_service import get_unified_analytics_service
            analytics_service = await get_unified_analytics_service()
            if analytics_service:
                status["services"]["unified_analytics"] = await analytics_service.get_service_health()
            else:
                status["services"]["unified_analytics"] = {"status": "not_initialized"}
        except Exception as e:
            status["services"]["unified_analytics"] = {"status": "error", "error": str(e)}
        
        # Unified Security service status
        try:
            from unified_security_service import get_unified_security_service
            security_service = get_unified_security_service()
            if security_service:
                status["services"]["unified_security"] = await security_service.get_service_health()
            else:
                status["services"]["unified_security"] = {"status": "not_initialized"}
        except Exception as e:
            status["services"]["unified_security"] = {"status": "error", "error": str(e)}
        
        # AI services status
        try:
            from ai_recommendation_service import get_ai_recommendation_service
            ai_service = get_ai_recommendation_service()
            if ai_service:
                ai_stats = await ai_service.get_recommendation_analytics()
                status["services"]["ai_recommendations"] = {
                    "status": ai_stats.get("service_status", "unknown"),
                    "total_interactions": ai_stats.get("total_interactions", 0),
                    "unique_users": ai_stats.get("unique_users", 0)
                }
            else:
                status["services"]["ai_recommendations"] = {"status": "not_initialized"}
        except Exception as e:
            status["services"]["ai_recommendations"] = {"status": "error", "error": str(e)}
        
        # Overall status
        operational_services = sum(1 for service in status["services"].values() if service.get("status") == "operational")
        total_services = len(status["services"])
        
        if operational_services == total_services:
            status["overall_status"] = "fully_operational"
        elif operational_services > total_services / 2:
            status["overall_status"] = "mostly_operational"
        else:
            status["overall_status"] = "degraded"
        
        status["consolidation_info"] = {
            "merged_services": [
                "analytics_service.py + advanced_analytics_service.py → unified_analytics_service.py",
                "security_service.py + enterprise_security_service.py → unified_security_service.py",
                "phase5_endpoints.py + phase6_endpoints.py → advanced_features_endpoints.py"
            ],
            "dummy_data_removed": True,
            "real_database_queries": True
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Advanced features status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))