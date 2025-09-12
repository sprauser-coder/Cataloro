"""
Phase 5 Advanced Marketplace Endpoints - Real-time, Multi-currency, Escrow, AI Features
Comprehensive endpoints for all Phase 5 functionality
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Create router for Phase 5 endpoints
phase5_router = APIRouter(prefix="/api/v2", tags=["Phase 5 Advanced Features"])

# Real-time WebSocket endpoints
@phase5_router.get("/websocket/stats")
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

@phase5_router.post("/websocket/broadcast")
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

# Multi-currency endpoints
@phase5_router.get("/currency/supported")
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

@phase5_router.get("/currency/rates")
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

@phase5_router.post("/currency/convert")
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

@phase5_router.post("/currency/user/preference")
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

# Escrow endpoints
@phase5_router.post("/escrow/create")
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

@phase5_router.post("/escrow/{escrow_id}/fund")
async def fund_escrow_transaction(escrow_id: str, funding_data: dict):
    """Fund an escrow transaction"""
    try:
        from escrow_service import get_escrow_service
        escrow_service_instance = get_escrow_service()
        
        result = await escrow_service_instance.fund_escrow(
            escrow_id=escrow_id,
            payment_proof=funding_data.get("payment_proof", {}),
            funded_by=funding_data.get("funded_by")
        )
        
        return result
    except Exception as e:
        logger.error(f"Fund escrow failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase5_router.post("/escrow/{escrow_id}/release")
async def request_escrow_release(escrow_id: str, release_data: dict):
    """Request release of escrow funds"""
    try:
        from escrow_service import get_escrow_service
        escrow_service_instance = get_escrow_service()
        
        result = await escrow_service_instance.request_release(
            escrow_id=escrow_id,
            requested_by=release_data.get("requested_by"),
            release_reason=release_data.get("reason", "Transaction completed")
        )
        
        return result
    except Exception as e:
        logger.error(f"Request escrow release failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase5_router.post("/escrow/{escrow_id}/approve")
async def approve_escrow_release(escrow_id: str, approval_data: dict):
    """Approve escrow release"""
    try:
        from escrow_service import get_escrow_service
        escrow_service_instance = get_escrow_service()
        
        result = await escrow_service_instance.approve_release(
            escrow_id=escrow_id,
            approved_by=approval_data.get("approved_by")
        )
        
        return result
    except Exception as e:
        logger.error(f"Approve escrow release failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase5_router.post("/escrow/{escrow_id}/dispute")
async def create_escrow_dispute(escrow_id: str, dispute_data: dict):
    """Create a dispute for an escrow transaction"""
    try:
        from escrow_service import get_escrow_service
        escrow_service_instance = get_escrow_service()
        
        result = await escrow_service_instance.create_dispute(
            escrow_id=escrow_id,
            disputed_by=dispute_data.get("disputed_by"),
            dispute_reason=dispute_data.get("reason"),
            evidence=dispute_data.get("evidence", [])
        )
        
        return result
    except Exception as e:
        logger.error(f"Create escrow dispute failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@phase5_router.get("/escrow/{escrow_id}")
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

@phase5_router.get("/escrow/user/{user_id}")
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

# AI Recommendation endpoints
@phase5_router.post("/ai/interaction")
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

@phase5_router.get("/ai/recommendations/{user_id}")
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

@phase5_router.get("/ai/similar/{listing_id}")
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

@phase5_router.get("/ai/trending")
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

@phase5_router.get("/ai/category/{user_id}/{category}")
async def get_category_recommendations(user_id: str, category: str, limit: int = 10):
    """Get recommendations within a specific category"""
    try:
        from ai_recommendation_service import get_ai_recommendation_service
        ai_service = get_ai_recommendation_service()
        
        recommendations = await ai_service.get_category_recommendations(user_id, category, limit)
        return {"success": True, "recommendations": recommendations}
    except Exception as e:
        logger.error(f"Get category recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Phase 5 comprehensive status endpoint
@phase5_router.get("/status")
async def get_phase5_status():
    """Get comprehensive Phase 5 services status"""
    try:
        status = {
            "phase": "5 - Advanced Marketplace Features",
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
        
        # Escrow service status
        try:
            from escrow_service import get_escrow_service
            escrow_service_instance = get_escrow_service()
            if escrow_service_instance:
                escrow_stats = await escrow_service_instance.get_escrow_statistics()
                status["services"]["escrow"] = {
                    "status": "operational",
                    "total_escrows": escrow_stats.get("total_escrows", 0),
                    "active_escrows": escrow_stats.get("active_escrows", 0),
                    "total_volume": escrow_stats.get("total_volume", 0)
                }
            else:
                status["services"]["escrow"] = {"status": "not_initialized"}
        except Exception as e:
            status["services"]["escrow"] = {"status": "error", "error": str(e)}
        
        # AI Recommendation service status
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
        all_operational = all(
            service.get("status") == "operational" 
            for service in status["services"].values()
        )
        
        status["overall_status"] = "operational" if all_operational else "partial"
        
        return status
        
    except Exception as e:
        logger.error(f"Get Phase 5 status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))