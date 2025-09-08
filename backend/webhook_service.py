"""
Webhook Service for Cataloro Marketplace
Handles webhook management, delivery, and monitoring
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import aiohttp
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class WebhookService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.webhooks_collection = db.webhooks
        self.webhook_events_collection = db.webhook_events
        self.webhook_deliveries_collection = db.webhook_deliveries
        
    async def create_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new webhook endpoint"""
        webhook = {
            "id": str(uuid.uuid4()),
            "url": webhook_data["url"],
            "events": webhook_data["events"],
            "name": webhook_data.get("name", "Unnamed Webhook"),
            "description": webhook_data.get("description", ""),
            "active": webhook_data.get("active", True),
            "secret": webhook_data.get("secret", ""),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "retry_attempts": webhook_data.get("retry_attempts", 3),
            "timeout_seconds": webhook_data.get("timeout_seconds", 30)
        }
        
        await self.webhooks_collection.insert_one(webhook)
        return webhook
    
    async def get_webhooks(self) -> List[Dict[str, Any]]:
        """Get all webhooks"""
        webhooks = []
        async for webhook in self.webhooks_collection.find().sort("created_at", -1):
            webhook.pop("_id", None)
            webhooks.append(webhook)
        return webhooks
    
    async def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific webhook by ID"""
        webhook = await self.webhooks_collection.find_one({"id": webhook_id})
        if webhook:
            webhook.pop("_id", None)
        return webhook
    
    async def update_webhook(self, webhook_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a webhook"""
        update_data["updated_at"] = datetime.now(timezone.utc)
        result = await self.webhooks_collection.update_one(
            {"id": webhook_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await self.get_webhook(webhook_id)
        return None
    
    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook"""
        result = await self.webhooks_collection.delete_one({"id": webhook_id})
        return result.deleted_count > 0
    
    async def trigger_event(self, event_type: str, data: Dict[str, Any]):
        """Trigger a webhook event with background processing"""
        # Store the event
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc)
        }
        
        await self.webhook_events_collection.insert_one(event)
        
        # Find all active webhooks that listen to this event
        active_webhooks = []
        async for webhook in self.webhooks_collection.find({
            "active": True,
            "events": {"$in": [event_type, "*"]}
        }):
            active_webhooks.append(webhook)
        
        # Process webhooks in background to avoid blocking the main request
        for webhook in active_webhooks:
            asyncio.create_task(self._deliver_webhook_background(webhook, event))
    
    async def _deliver_webhook_background(self, webhook: Dict[str, Any], event: Dict[str, Any]):
        """Deliver webhook in background with retry logic"""
        delivery_id = str(uuid.uuid4())
        payload = {
            "event_id": event["event_id"],
            "event_type": event["event_type"],
            "timestamp": event["timestamp"].isoformat(),
            "data": event["data"]
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Cataloro-Webhook/1.0",
            "X-Webhook-ID": webhook["id"],
            "X-Event-Type": event["event_type"],
            "X-Delivery-ID": delivery_id
        }
        
        # Add signature if secret is provided
        if webhook.get("secret"):
            headers["X-Webhook-Secret"] = webhook["secret"]
        
        delivery_record = {
            "delivery_id": delivery_id,
            "webhook_id": webhook["id"],
            "event_id": event["event_id"],
            "url": webhook["url"],
            "status": "pending",
            "attempt": 1,
            "max_attempts": webhook.get("retry_attempts", 3),
            "created_at": datetime.now(timezone.utc),
            "next_retry_at": None,
            "response_status": None,
            "response_body": None,
            "error_message": None
        }
        
        await self.webhook_deliveries_collection.insert_one(delivery_record)
        
        # Attempt delivery with retry logic
        max_attempts = webhook.get("retry_attempts", 3)
        for attempt in range(1, max_attempts + 1):
            success = await self._attempt_delivery_with_retry(delivery_record, webhook, payload, headers, attempt)
            if success:
                break
            
            # Calculate exponential backoff for retry
            if attempt < max_attempts:
                backoff_seconds = (2 ** attempt) * 60  # 2, 4, 8 minutes
                await asyncio.sleep(backoff_seconds)
    
    async def _attempt_delivery_with_retry(self, delivery: Dict[str, Any], webhook: Dict[str, Any], 
                                         payload: Dict[str, Any], headers: Dict[str, str], attempt: int) -> bool:
        """Attempt webhook delivery with comprehensive error handling"""
        try:
            timeout = aiohttp.ClientTimeout(total=webhook.get("timeout_seconds", 30))
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    webhook["url"],
                    json=payload,
                    headers=headers
                ) as response:
                    response_body = await response.text()
                    
                    # Update delivery record
                    update_data = {
                        "attempt": attempt,
                        "response_status": response.status,
                        "response_body": response_body[:1000],  # Limit response body size
                        "completed_at": datetime.now(timezone.utc)
                    }
                    
                    if response.status < 400:
                        update_data["status"] = "success"
                        await self.webhook_deliveries_collection.update_one(
                            {"delivery_id": delivery["delivery_id"]},
                            {"$set": update_data}
                        )
                        logger.info(f"Webhook delivered successfully: {webhook['url']} - Status: {response.status}")
                        return True
                    else:
                        update_data["status"] = "failed"
                        update_data["error_message"] = f"HTTP {response.status}: {response_body[:200]}"
                        await self.webhook_deliveries_collection.update_one(
                            {"delivery_id": delivery["delivery_id"]},
                            {"$set": update_data}
                        )
                        logger.warning(f"Webhook delivery failed: {webhook['url']} - Status: {response.status}")
                        return False
                        
        except Exception as e:
            error_message = str(e)
            logger.error(f"Webhook delivery error: {webhook['url']} - {error_message}")
            
            await self.webhook_deliveries_collection.update_one(
                {"delivery_id": delivery["delivery_id"]},
                {
                    "$set": {
                        "attempt": attempt,
                        "status": "failed",
                        "error_message": error_message,
                        "completed_at": datetime.now(timezone.utc)
                    }
                }
            )
            return False
    
    async def get_webhook_deliveries(self, webhook_id: Optional[str] = None, 
                                   limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get webhook delivery history"""
        query = {}
        if webhook_id:
            query["webhook_id"] = webhook_id
        
        deliveries = []
        async for delivery in (self.webhook_deliveries_collection
                             .find(query)
                             .sort("created_at", -1)
                             .skip(offset)
                             .limit(limit)):
            delivery.pop("_id", None)
            deliveries.append(delivery)
        
        return deliveries
    
    async def get_supported_events(self) -> List[Dict[str, str]]:
        """Get list of supported webhook events"""
        return [
            {"event": "user.registered", "description": "User creates an account"},
            {"event": "user.login", "description": "User logs in"},
            {"event": "listing.created", "description": "New listing is created"},
            {"event": "listing.updated", "description": "Listing is updated"},
            {"event": "listing.deleted", "description": "Listing is deleted"},
            {"event": "order.created", "description": "New order is placed"},
            {"event": "order.updated", "description": "Order status is updated"},
            {"event": "order.completed", "description": "Order is completed"},
            {"event": "tender.submitted", "description": "Tender/bid is submitted"},
            {"event": "tender.accepted", "description": "Tender/bid is accepted"},
            {"event": "payment.completed", "description": "Payment is processed"},
            {"event": "payment.failed", "description": "Payment fails"},
            {"event": "escrow.created", "description": "Escrow transaction is created"},
            {"event": "escrow.released", "description": "Escrow funds are released"}
        ]

# Global webhook service instance
_webhook_service = None

async def init_webhook_service(db: AsyncIOMotorDatabase):
    """Initialize the webhook service"""
    global _webhook_service
    _webhook_service = WebhookService(db)
    logger.info("Webhook service initialized")

def get_webhook_service() -> WebhookService:
    """Get the webhook service instance"""
    if _webhook_service is None:
        raise RuntimeError("Webhook service not initialized")
    return _webhook_service