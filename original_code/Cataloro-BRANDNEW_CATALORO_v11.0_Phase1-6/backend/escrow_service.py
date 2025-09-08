"""
Escrow Service for Cataloro Marketplace - Phase 5B
Secure payment holding and release system for high-value transactions
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)

class EscrowStatus(Enum):
    PENDING = "pending"
    FUNDED = "funded"
    IN_DISPUTE = "in_dispute"
    RELEASED = "released" 
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class DisputeStatus(Enum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class EscrowService:
    def __init__(self, db):
        self.db = db
        
        # Configuration
        self.escrow_fee_percentage = 2.5  # 2.5% platform fee
        self.minimum_escrow_amount = 100.0  # Minimum €100 for escrow
        self.automatic_release_days = 7  # Auto-release after 7 days if no dispute
        self.dispute_resolution_days = 14  # Time limit for dispute resolution
        
        # Escrow account (in production, this would be a real payment processor)
        self.escrow_balance = {}  # escrow_id -> balance
        
        logger.info("✅ Escrow service initialized")
    
    async def create_escrow(
        self,
        listing_id: str,
        buyer_id: str,
        seller_id: str,
        amount: float,
        currency: str = "EUR",
        payment_method: str = "bank_transfer"
    ) -> Dict[str, Any]:
        """Create a new escrow transaction"""
        try:
            # Validate inputs
            if amount < self.minimum_escrow_amount:
                return {
                    "success": False,
                    "error": f"Amount must be at least {self.minimum_escrow_amount} {currency}"
                }
            
            # Verify listing exists
            listing = await self.db.listings.find_one({"id": listing_id})
            if not listing:
                return {"success": False, "error": "Listing not found"}
            
            if listing.get("seller_id") != seller_id:
                return {"success": False, "error": "Seller ID mismatch"}
            
            # Calculate fees
            platform_fee = amount * (self.escrow_fee_percentage / 100)
            net_amount = amount - platform_fee
            
            # Create escrow record
            escrow_id = str(uuid.uuid4())
            escrow_data = {
                "id": escrow_id,
                "listing_id": listing_id,
                "buyer_id": buyer_id,
                "seller_id": seller_id,
                "amount": amount,
                "currency": currency,
                "platform_fee": platform_fee,
                "net_amount": net_amount,
                "payment_method": payment_method,
                "status": EscrowStatus.PENDING.value,
                "created_at": datetime.utcnow().isoformat(),
                "funded_at": None,
                "release_date": None,
                "auto_release_at": None,
                "terms": {
                    "auto_release_days": self.automatic_release_days,
                    "dispute_deadline": (datetime.utcnow() + timedelta(days=self.dispute_resolution_days)).isoformat()
                },
                "payment_details": {},
                "transaction_history": [
                    {
                        "action": "created",
                        "timestamp": datetime.utcnow().isoformat(),
                        "actor": "system",
                        "details": {"amount": amount, "currency": currency}
                    }
                ]
            }
            
            # Store in database
            await self.db.escrow_transactions.insert_one(escrow_data)
            
            # Generate payment instructions
            payment_instructions = await self._generate_payment_instructions(escrow_data)
            
            return {
                "success": True,
                "escrow_id": escrow_id,
                "status": EscrowStatus.PENDING.value,
                "amount": amount,
                "currency": currency,
                "platform_fee": platform_fee,
                "net_amount": net_amount,
                "payment_instructions": payment_instructions,
                "auto_release_at": (datetime.utcnow() + timedelta(days=self.automatic_release_days)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create escrow: {e}")
            return {"success": False, "error": str(e)}
    
    async def fund_escrow(
        self,
        escrow_id: str,
        payment_proof: Dict,
        funded_by: str
    ) -> Dict[str, Any]:
        """Mark escrow as funded (simulate payment verification)"""
        try:
            escrow = await self.db.escrow_transactions.find_one({"id": escrow_id})
            if not escrow:
                return {"success": False, "error": "Escrow not found"}
            
            if escrow["status"] != EscrowStatus.PENDING.value:
                return {"success": False, "error": f"Escrow is {escrow['status']}, cannot fund"}
            
            # In production, verify payment with payment processor
            # For now, simulate successful funding
            
            funded_at = datetime.utcnow()
            auto_release_at = funded_at + timedelta(days=self.automatic_release_days)
            
            # Update escrow status
            await self.db.escrow_transactions.update_one(
                {"id": escrow_id},
                {
                    "$set": {
                        "status": EscrowStatus.FUNDED.value,
                        "funded_at": funded_at.isoformat(),
                        "auto_release_at": auto_release_at.isoformat(),
                        "payment_proof": payment_proof
                    },
                    "$push": {
                        "transaction_history": {
                            "action": "funded",
                            "timestamp": funded_at.isoformat(),
                            "actor": funded_by,
                            "details": payment_proof
                        }
                    }
                }
            )
            
            # Add to escrow balance tracking
            self.escrow_balance[escrow_id] = escrow["amount"]
            
            # Notify parties
            await self._notify_escrow_update(escrow_id, "funded")
            
            return {
                "success": True,
                "status": EscrowStatus.FUNDED.value,
                "funded_at": funded_at.isoformat(),
                "auto_release_at": auto_release_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to fund escrow: {e}")
            return {"success": False, "error": str(e)}
    
    async def request_release(
        self,
        escrow_id: str,
        requested_by: str,
        release_reason: str = "Transaction completed"
    ) -> Dict[str, Any]:
        """Request release of escrowed funds"""
        try:
            escrow = await self.db.escrow_transactions.find_one({"id": escrow_id})
            if not escrow:
                return {"success": False, "error": "Escrow not found"}
            
            if escrow["status"] != EscrowStatus.FUNDED.value:
                return {"success": False, "error": f"Escrow is {escrow['status']}, cannot request release"}
            
            # Only buyer or seller can request release
            if requested_by not in [escrow["buyer_id"], escrow["seller_id"]]:
                return {"success": False, "error": "Unauthorized release request"}
            
            # Check if there's already a release request
            if "release_request" in escrow:
                existing_request = escrow["release_request"]
                if existing_request["status"] == "pending":
                    return {"success": False, "error": "Release already requested"}
            
            # Create release request
            release_request = {
                "requested_by": requested_by,
                "requested_at": datetime.utcnow().isoformat(),
                "reason": release_reason,
                "status": "pending",
                "approval_deadline": (datetime.utcnow() + timedelta(days=3)).isoformat()
            }
            
            await self.db.escrow_transactions.update_one(
                {"id": escrow_id},
                {
                    "$set": {"release_request": release_request},
                    "$push": {
                        "transaction_history": {
                            "action": "release_requested",
                            "timestamp": datetime.utcnow().isoformat(),
                            "actor": requested_by,
                            "details": {"reason": release_reason}
                        }
                    }
                }
            )
            
            # Notify other party
            other_party = escrow["seller_id"] if requested_by == escrow["buyer_id"] else escrow["buyer_id"]
            await self._notify_release_request(escrow_id, requested_by, other_party)
            
            return {
                "success": True,
                "release_request": release_request,
                "message": "Release requested. Waiting for approval or auto-approval in 3 days."
            }
            
        except Exception as e:
            logger.error(f"Failed to request release: {e}")
            return {"success": False, "error": str(e)}
    
    async def approve_release(
        self,
        escrow_id: str,
        approved_by: str
    ) -> Dict[str, Any]:
        """Approve release of escrowed funds"""
        try:
            escrow = await self.db.escrow_transactions.find_one({"id": escrow_id})
            if not escrow:
                return {"success": False, "error": "Escrow not found"}
            
            if "release_request" not in escrow:
                return {"success": False, "error": "No release request pending"}
            
            release_request = escrow["release_request"]
            if release_request["status"] != "pending":
                return {"success": False, "error": "Release request not pending"}
            
            # Only the other party can approve
            requester = release_request["requested_by"]
            if approved_by == requester:
                return {"success": False, "error": "Cannot approve your own release request"}
            
            if approved_by not in [escrow["buyer_id"], escrow["seller_id"]]:
                return {"success": False, "error": "Unauthorized to approve release"}
            
            # Execute release
            return await self._execute_release(escrow_id, approved_by, "approved")
            
        except Exception as e:
            logger.error(f"Failed to approve release: {e}")
            return {"success": False, "error": str(e)}
    
    async def auto_release_escrow(self, escrow_id: str) -> Dict[str, Any]:
        """Automatically release escrow after deadline"""
        try:
            escrow = await self.db.escrow_transactions.find_one({"id": escrow_id})
            if not escrow:
                return {"success": False, "error": "Escrow not found"}
            
            if escrow["status"] != EscrowStatus.FUNDED.value:
                return {"success": False, "error": f"Escrow is {escrow['status']}, cannot auto-release"}
            
            # Check if auto-release time has passed
            auto_release_at = datetime.fromisoformat(escrow["auto_release_at"])
            if datetime.utcnow() < auto_release_at:
                return {"success": False, "error": "Auto-release time not reached"}
            
            # Execute automatic release
            return await self._execute_release(escrow_id, "system", "auto_release")
            
        except Exception as e:
            logger.error(f"Failed to auto-release escrow: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_release(
        self,
        escrow_id: str,
        released_by: str,
        release_type: str
    ) -> Dict[str, Any]:
        """Execute the actual release of funds"""
        try:
            escrow = await self.db.escrow_transactions.find_one({"id": escrow_id})
            
            # In production, transfer funds via payment processor
            # For now, simulate the transfer
            
            released_at = datetime.utcnow()
            
            # Update escrow status
            await self.db.escrow_transactions.update_one(
                {"id": escrow_id},
                {
                    "$set": {
                        "status": EscrowStatus.RELEASED.value,
                        "released_at": released_at.isoformat(),
                        "released_by": released_by,
                        "release_type": release_type
                    },
                    "$push": {
                        "transaction_history": {
                            "action": "released",
                            "timestamp": released_at.isoformat(),
                            "actor": released_by,
                            "details": {
                                "release_type": release_type,
                                "amount_released": escrow["net_amount"]
                            }
                        }
                    }
                }
            )
            
            # Remove from balance tracking
            if escrow_id in self.escrow_balance:
                del self.escrow_balance[escrow_id]
            
            # Update listing status if applicable
            await self._complete_transaction(escrow["listing_id"], escrow["buyer_id"], escrow["seller_id"])
            
            # Notify parties
            await self._notify_escrow_update(escrow_id, "released")
            
            return {
                "success": True,
                "status": EscrowStatus.RELEASED.value,
                "released_at": released_at.isoformat(),
                "amount_released": escrow["net_amount"],
                "platform_fee": escrow["platform_fee"]
            }
            
        except Exception as e:
            logger.error(f"Failed to execute release: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_dispute(
        self,
        escrow_id: str,
        disputed_by: str,
        dispute_reason: str,
        evidence: List[Dict] = None
    ) -> Dict[str, Any]:
        """Create a dispute for an escrow transaction"""
        try:
            escrow = await self.db.escrow_transactions.find_one({"id": escrow_id})
            if not escrow:
                return {"success": False, "error": "Escrow not found"}
            
            if escrow["status"] not in [EscrowStatus.FUNDED.value]:
                return {"success": False, "error": f"Cannot dispute escrow with status {escrow['status']}"}
            
            if disputed_by not in [escrow["buyer_id"], escrow["seller_id"]]:
                return {"success": False, "error": "Unauthorized to create dispute"}
            
            # Create dispute record
            dispute_id = str(uuid.uuid4())
            dispute_data = {
                "id": dispute_id,
                "escrow_id": escrow_id,
                "disputed_by": disputed_by,
                "dispute_reason": dispute_reason,
                "status": DisputeStatus.OPEN.value,
                "created_at": datetime.utcnow().isoformat(),
                "evidence": evidence or [],
                "resolution": None,
                "resolved_by": None,
                "resolved_at": None,
                "dispute_history": [
                    {
                        "action": "dispute_created",
                        "timestamp": datetime.utcnow().isoformat(),
                        "actor": disputed_by,
                        "details": {"reason": dispute_reason}
                    }
                ]
            }
            
            # Store dispute
            await self.db.escrow_disputes.insert_one(dispute_data)
            
            # Update escrow status
            await self.db.escrow_transactions.update_one(
                {"id": escrow_id},
                {
                    "$set": {"status": EscrowStatus.IN_DISPUTE.value},
                    "$push": {
                        "transaction_history": {
                            "action": "dispute_created",
                            "timestamp": datetime.utcnow().isoformat(),
                            "actor": disputed_by,
                            "details": {"dispute_id": dispute_id, "reason": dispute_reason}
                        }
                    }
                }
            )
            
            # Notify parties and admin
            await self._notify_dispute_created(escrow_id, dispute_id, disputed_by)
            
            return {
                "success": True,
                "dispute_id": dispute_id,
                "status": DisputeStatus.OPEN.value,
                "message": "Dispute created. An admin will review within 24 hours."
            }
            
        except Exception as e:
            logger.error(f"Failed to create dispute: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_escrow_details(self, escrow_id: str, requested_by: str = None) -> Dict[str, Any]:
        """Get detailed escrow information"""
        try:
            escrow = await self.db.escrow_transactions.find_one({"id": escrow_id})
            if not escrow:
                return {"success": False, "error": "Escrow not found"}
            
            # Remove internal fields
            escrow.pop("_id", None)
            
            # Add calculated fields
            escrow["is_expired"] = (
                escrow["status"] == EscrowStatus.FUNDED.value and
                datetime.utcnow() > datetime.fromisoformat(escrow["auto_release_at"])
            )
            
            # Get dispute info if exists
            if escrow["status"] == EscrowStatus.IN_DISPUTE.value:
                dispute = await self.db.escrow_disputes.find_one({"escrow_id": escrow_id})
                if dispute:
                    dispute.pop("_id", None)
                    escrow["dispute"] = dispute
            
            return {"success": True, "escrow": escrow}
            
        except Exception as e:
            logger.error(f"Failed to get escrow details: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_escrows(
        self,
        user_id: str,
        status: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get escrow transactions for a user"""
        try:
            query = {
                "$or": [
                    {"buyer_id": user_id},
                    {"seller_id": user_id}
                ]
            }
            
            if status:
                query["status"] = status
            
            escrows = await self.db.escrow_transactions.find(query).sort("created_at", -1).limit(limit).to_list(length=None)
            
            # Clean up data
            for escrow in escrows:
                escrow.pop("_id", None)
                escrow["user_role"] = "buyer" if escrow["buyer_id"] == user_id else "seller"
            
            return escrows
            
        except Exception as e:
            logger.error(f"Failed to get user escrows: {e}")
            return []
    
    async def _generate_payment_instructions(self, escrow_data: Dict) -> Dict:
        """Generate payment instructions for escrow funding"""
        # In production, integrate with payment processor
        # For now, return mock instructions
        
        return {
            "payment_method": escrow_data["payment_method"],
            "amount": escrow_data["amount"],
            "currency": escrow_data["currency"],
            "reference": f"ESCROW-{escrow_data['id'][:8]}",
            "instructions": {
                "bank_transfer": {
                    "account_name": "Cataloro Marketplace Escrow",
                    "iban": "DE89 3704 0044 0532 0130 00",
                    "bic": "COBADEFFXXX",
                    "reference": f"ESCROW-{escrow_data['id'][:8]}"
                }
            },
            "deadline": (datetime.utcnow() + timedelta(days=3)).isoformat()
        }
    
    async def _notify_escrow_update(self, escrow_id: str, event_type: str):
        """Notify parties about escrow updates"""
        try:
            # In production, send notifications via email/SMS/push
            logger.info(f"📧 Escrow {escrow_id} notification: {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to send escrow notification: {e}")
    
    async def _notify_release_request(self, escrow_id: str, requested_by: str, notify_user: str):
        """Notify about release requests"""
        try:
            logger.info(f"📧 Release request notification: {escrow_id} by {requested_by} to {notify_user}")
            
        except Exception as e:
            logger.error(f"Failed to send release request notification: {e}")
    
    async def _notify_dispute_created(self, escrow_id: str, dispute_id: str, disputed_by: str):
        """Notify about dispute creation"""
        try:
            logger.info(f"🚨 Dispute created: {dispute_id} for escrow {escrow_id} by {disputed_by}")
            
        except Exception as e:
            logger.error(f"Failed to send dispute notification: {e}")
    
    async def _complete_transaction(self, listing_id: str, buyer_id: str, seller_id: str):
        """Complete the marketplace transaction"""
        try:
            # Update listing status
            await self.db.listings.update_one(
                {"id": listing_id},
                {"$set": {"status": "sold", "sold_to": buyer_id, "sold_at": datetime.utcnow().isoformat()}}
            )
            
            # Create order record
            order_data = {
                "id": str(uuid.uuid4()),
                "listing_id": listing_id,
                "buyer_id": buyer_id,
                "seller_id": seller_id,
                "status": "completed",
                "payment_method": "escrow",
                "created_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat()
            }
            
            await self.db.orders.insert_one(order_data)
            
        except Exception as e:
            logger.error(f"Failed to complete transaction: {e}")
    
    async def get_escrow_statistics(self) -> Dict[str, Any]:
        """Get escrow service statistics"""
        try:
            total_escrows = await self.db.escrow_transactions.count_documents({})
            active_escrows = await self.db.escrow_transactions.count_documents({
                "status": {"$in": [EscrowStatus.FUNDED.value, EscrowStatus.PENDING.value]}
            })
            
            disputes = await self.db.escrow_disputes.count_documents({})
            active_disputes = await self.db.escrow_disputes.count_documents({
                "status": {"$in": [DisputeStatus.OPEN.value, DisputeStatus.IN_REVIEW.value]}
            })
            
            # Calculate total volume
            pipeline = [
                {"$group": {"_id": None, "total_volume": {"$sum": "$amount"}}}
            ]
            volume_result = await self.db.escrow_transactions.aggregate(pipeline).to_list(length=1)
            total_volume = volume_result[0]["total_volume"] if volume_result else 0
            
            return {
                "total_escrows": total_escrows,
                "active_escrows": active_escrows,
                "total_disputes": disputes,
                "active_disputes": active_disputes,
                "total_volume": total_volume,
                "current_balance": sum(self.escrow_balance.values()),
                "fee_percentage": self.escrow_fee_percentage,
                "minimum_amount": self.minimum_escrow_amount,
                "auto_release_days": self.automatic_release_days
            }
            
        except Exception as e:
            logger.error(f"Failed to get escrow statistics: {e}")
            return {}

# Global escrow service instance
escrow_service = None

async def init_escrow_service(db):
    """Initialize escrow service"""
    global escrow_service
    escrow_service = EscrowService(db)
    return escrow_service

def get_escrow_service():
    """Get escrow service instance"""
    return escrow_service