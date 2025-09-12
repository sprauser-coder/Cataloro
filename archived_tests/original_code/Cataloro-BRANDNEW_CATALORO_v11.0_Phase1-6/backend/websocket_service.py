"""
WebSocket Service for Cataloro Marketplace - Phase 5A
Real-time bidding, messaging, notifications, and live updates
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
import socketio
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class UserSession:
    user_id: str
    username: str
    session_id: str
    connected_at: datetime
    last_activity: datetime
    rooms: Set[str]
    user_role: str = "buyer"
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "session_id": self.session_id,
            "connected_at": self.connected_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "rooms": list(self.rooms),
            "user_role": self.user_role
        }

class WebSocketService:
    def __init__(self, db):
        self.db = db
        self.sio = socketio.AsyncServer(
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True
        )
        
        # Connection tracking
        self.active_sessions: Dict[str, UserSession] = {}  # session_id -> UserSession
        self.user_sessions: Dict[str, Set[str]] = defaultdict(set)  # user_id -> set of session_ids
        self.room_members: Dict[str, Set[str]] = defaultdict(set)  # room -> set of session_ids
        
        # Real-time bidding tracking
        self.active_auctions: Dict[str, Dict] = {}  # listing_id -> auction_data
        self.bidding_rooms: Dict[str, Set[str]] = defaultdict(set)  # listing_id -> set of session_ids
        
        # Message queues for offline users
        self.offline_messages: Dict[str, List[Dict]] = defaultdict(list)  # user_id -> messages
        
        # Register event handlers
        self._register_event_handlers()
        
        logger.info("✅ WebSocket service initialized")
    
    def _register_event_handlers(self):
        """Register all WebSocket event handlers"""
        
        @self.sio.event
        async def connect(sid, environ, auth):
            """Handle client connection"""
            try:
                # Authenticate user
                user_data = await self._authenticate_connection(auth)
                if not user_data:
                    logger.warning(f"Unauthenticated connection attempt: {sid}")
                    return False
                
                # Create user session
                session = UserSession(
                    user_id=user_data["user_id"],
                    username=user_data["username"],
                    session_id=sid,
                    connected_at=datetime.utcnow(),
                    last_activity=datetime.utcnow(),
                    rooms=set(),
                    user_role=user_data.get("user_role", "buyer")
                )
                
                self.active_sessions[sid] = session
                self.user_sessions[user_data["user_id"]].add(sid)
                
                # Send connection confirmation
                await self.sio.emit('connection_confirmed', {
                    'user_id': user_data["user_id"],
                    'username': user_data["username"],
                    'timestamp': datetime.utcnow().isoformat()
                }, room=sid)
                
                # Deliver offline messages
                await self._deliver_offline_messages(user_data["user_id"], sid)
                
                # Notify other users about online status
                await self._broadcast_user_status(user_data["user_id"], "online")
                
                logger.info(f"✅ User connected: {user_data['username']} ({sid})")
                return True
                
            except Exception as e:
                logger.error(f"Connection error: {e}")
                return False
        
        @self.sio.event
        async def disconnect(sid):
            """Handle client disconnection"""
            try:
                if sid in self.active_sessions:
                    session = self.active_sessions[sid]
                    
                    # Remove from all rooms
                    for room in list(session.rooms):
                        await self._leave_room(sid, room)
                    
                    # Clean up session tracking
                    self.user_sessions[session.user_id].discard(sid)
                    if not self.user_sessions[session.user_id]:
                        del self.user_sessions[session.user_id]
                        # Notify about offline status
                        await self._broadcast_user_status(session.user_id, "offline")
                    
                    del self.active_sessions[sid]
                    
                    logger.info(f"❌ User disconnected: {session.username} ({sid})")
                
            except Exception as e:
                logger.error(f"Disconnect error: {e}")
        
        @self.sio.event
        async def join_room(sid, data):
            """Join a specific room (listing, chat, etc.)"""
            try:
                room_type = data.get('room_type')
                room_id = data.get('room_id')
                
                if not room_type or not room_id:
                    await self.sio.emit('error', {'message': 'Invalid room data'}, room=sid)
                    return
                
                room_name = f"{room_type}:{room_id}"
                await self._join_room(sid, room_name)
                
                await self.sio.emit('room_joined', {
                    'room_type': room_type,
                    'room_id': room_id,
                    'room_name': room_name
                }, room=sid)
                
            except Exception as e:
                logger.error(f"Join room error: {e}")
                await self.sio.emit('error', {'message': 'Failed to join room'}, room=sid)
        
        @self.sio.event
        async def leave_room(sid, data):
            """Leave a specific room"""
            try:
                room_type = data.get('room_type')
                room_id = data.get('room_id')
                
                room_name = f"{room_type}:{room_id}"
                await self._leave_room(sid, room_name)
                
                await self.sio.emit('room_left', {
                    'room_type': room_type,
                    'room_id': room_id
                }, room=sid)
                
            except Exception as e:
                logger.error(f"Leave room error: {e}")
        
        @self.sio.event
        async def send_message(sid, data):
            """Send a real-time message"""
            try:
                if sid not in self.active_sessions:
                    return
                
                session = self.active_sessions[sid]
                recipient_id = data.get('recipient_id')
                message_content = data.get('message')
                message_type = data.get('type', 'text')
                
                if not recipient_id or not message_content:
                    await self.sio.emit('error', {'message': 'Invalid message data'}, room=sid)
                    return
                
                # Create message object
                message = {
                    'id': f"msg_{int(time.time() * 1000)}",
                    'sender_id': session.user_id,
                    'sender_username': session.username,
                    'recipient_id': recipient_id,
                    'message': message_content,
                    'type': message_type,
                    'timestamp': datetime.utcnow().isoformat(),
                    'read': False
                }
                
                # Store in database
                await self._store_message(message)
                
                # Send to recipient if online
                recipient_sessions = self.user_sessions.get(recipient_id, set())
                if recipient_sessions:
                    for recipient_sid in recipient_sessions:
                        await self.sio.emit('new_message', message, room=recipient_sid)
                else:
                    # Store for offline delivery
                    self.offline_messages[recipient_id].append(message)
                
                # Confirm delivery to sender
                await self.sio.emit('message_sent', {
                    'message_id': message['id'],
                    'delivered': bool(recipient_sessions)
                }, room=sid)
                
            except Exception as e:
                logger.error(f"Send message error: {e}")
                await self.sio.emit('error', {'message': 'Failed to send message'}, room=sid)
        
        @self.sio.event
        async def place_bid(sid, data):
            """Handle real-time bidding"""
            try:
                if sid not in self.active_sessions:
                    return
                
                session = self.active_sessions[sid]
                listing_id = data.get('listing_id')
                bid_amount = data.get('bid_amount')
                
                if not listing_id or not bid_amount:
                    await self.sio.emit('error', {'message': 'Invalid bid data'}, room=sid)
                    return
                
                # Validate bid
                validation_result = await self._validate_bid(session.user_id, listing_id, bid_amount)
                if not validation_result['valid']:
                    await self.sio.emit('bid_rejected', {
                        'listing_id': listing_id,
                        'reason': validation_result['reason']
                    }, room=sid)
                    return
                
                # Create bid object
                bid = {
                    'id': f"bid_{int(time.time() * 1000)}",
                    'listing_id': listing_id,
                    'bidder_id': session.user_id,
                    'bidder_username': session.username,
                    'amount': bid_amount,
                    'timestamp': datetime.utcnow().isoformat(),
                    'status': 'active'
                }
                
                # Store bid in database
                await self._store_bid(bid)
                
                # Update auction tracking
                if listing_id not in self.active_auctions:
                    self.active_auctions[listing_id] = {
                        'current_high_bid': bid_amount,
                        'high_bidder': session.user_id,
                        'bid_count': 1,
                        'last_bid_time': datetime.utcnow()
                    }
                else:
                    auction = self.active_auctions[listing_id]
                    auction['current_high_bid'] = bid_amount
                    auction['high_bidder'] = session.user_id
                    auction['bid_count'] += 1
                    auction['last_bid_time'] = datetime.utcnow()
                
                # Broadcast bid to all watchers
                room_name = f"listing:{listing_id}"
                await self.sio.emit('new_bid', {
                    'listing_id': listing_id,
                    'bid': bid,
                    'auction_status': self.active_auctions[listing_id]
                }, room=room_name)
                
                # Notify listing owner
                listing = await self.db.listings.find_one({"id": listing_id})
                if listing:
                    seller_sessions = self.user_sessions.get(listing.get('seller_id'), set())
                    for seller_sid in seller_sessions:
                        await self.sio.emit('bid_received', {
                            'listing_id': listing_id,
                            'bid': bid
                        }, room=seller_sid)
                
            except Exception as e:
                logger.error(f"Place bid error: {e}")
                await self.sio.emit('error', {'message': 'Failed to place bid'}, room=sid)
        
        @self.sio.event
        async def watch_listing(sid, data):
            """Start watching a listing for real-time updates"""
            try:
                listing_id = data.get('listing_id')
                if not listing_id:
                    return
                
                room_name = f"listing:{listing_id}"
                await self.sio.enter_room(sid, room_name)
                
                if sid in self.active_sessions:
                    self.active_sessions[sid].rooms.add(room_name)
                    self.room_members[room_name].add(sid)
                
                # Send current auction status
                if listing_id in self.active_auctions:
                    await self.sio.emit('auction_status', {
                        'listing_id': listing_id,
                        'auction': self.active_auctions[listing_id]
                    }, room=sid)
                
            except Exception as e:
                logger.error(f"Watch listing error: {e}")
        
        @self.sio.event
        async def unwatch_listing(sid, data):
            """Stop watching a listing"""
            try:
                listing_id = data.get('listing_id')
                if not listing_id:
                    return
                
                room_name = f"listing:{listing_id}"
                await self.sio.leave_room(sid, room_name)
                
                if sid in self.active_sessions:
                    self.active_sessions[sid].rooms.discard(room_name)
                    self.room_members[room_name].discard(sid)
                
            except Exception as e:
                logger.error(f"Unwatch listing error: {e}")
        
        @self.sio.event
        async def get_online_users(sid, data):
            """Get list of online users"""
            try:
                if sid not in self.active_sessions:
                    return
                
                online_users = []
                for user_id, session_ids in self.user_sessions.items():
                    if session_ids:  # User has active sessions
                        # Get any active session to get user info
                        any_session_id = next(iter(session_ids))
                        if any_session_id in self.active_sessions:
                            session = self.active_sessions[any_session_id]
                            online_users.append({
                                'user_id': user_id,
                                'username': session.username,
                                'user_role': session.user_role,
                                'last_activity': session.last_activity.isoformat()
                            })
                
                await self.sio.emit('online_users', {
                    'users': online_users,
                    'total_count': len(online_users)
                }, room=sid)
                
            except Exception as e:
                logger.error(f"Get online users error: {e}")
    
    async def _authenticate_connection(self, auth) -> Optional[Dict]:
        """Authenticate WebSocket connection"""
        try:
            if not auth or 'user_id' not in auth:
                return None
            
            user_id = auth['user_id']
            # In a real implementation, validate the token/session
            # For now, fetch user data from database
            user = await self.db.users.find_one({"id": user_id})
            if user:
                return {
                    "user_id": user_id,
                    "username": user.get("username", "Unknown"),
                    "user_role": user.get("user_role", "buyer")
                }
            return None
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    async def _join_room(self, sid: str, room_name: str):
        """Join a room with tracking"""
        await self.sio.enter_room(sid, room_name)
        if sid in self.active_sessions:
            self.active_sessions[sid].rooms.add(room_name)
            self.room_members[room_name].add(sid)
    
    async def _leave_room(self, sid: str, room_name: str):
        """Leave a room with tracking"""
        await self.sio.leave_room(sid, room_name)
        if sid in self.active_sessions:
            self.active_sessions[sid].rooms.discard(room_name)
            self.room_members[room_name].discard(sid)
    
    async def _deliver_offline_messages(self, user_id: str, sid: str):
        """Deliver queued offline messages"""
        if user_id in self.offline_messages:
            messages = self.offline_messages[user_id]
            for message in messages:
                await self.sio.emit('offline_message', message, room=sid)
            # Clear delivered messages
            del self.offline_messages[user_id]
    
    async def _broadcast_user_status(self, user_id: str, status: str):
        """Broadcast user online/offline status"""
        try:
            user = await self.db.users.find_one({"id": user_id})
            if user:
                status_update = {
                    'user_id': user_id,
                    'username': user.get('username', 'Unknown'),
                    'status': status,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Broadcast to all connected users
                await self.sio.emit('user_status_update', status_update)
                
        except Exception as e:
            logger.error(f"Broadcast user status error: {e}")
    
    async def _store_message(self, message: Dict):
        """Store message in database"""
        try:
            # Convert to database format
            db_message = {
                "id": message['id'],
                "sender_id": message['sender_id'],
                "recipient_id": message['recipient_id'],
                "message": message['message'],
                "type": message['type'],
                "created_at": message['timestamp'],
                "read": False
            }
            
            await self.db.user_messages.insert_one(db_message)
            
        except Exception as e:
            logger.error(f"Store message error: {e}")
    
    async def _validate_bid(self, user_id: str, listing_id: str, bid_amount: float) -> Dict:
        """Validate a bid before processing"""
        try:
            # Check if listing exists and is active
            listing = await self.db.listings.find_one({"id": listing_id, "status": "active"})
            if not listing:
                return {"valid": False, "reason": "Listing not found or inactive"}
            
            # Check if user is not the seller
            if listing.get("seller_id") == user_id:
                return {"valid": False, "reason": "Cannot bid on your own listing"}
            
            # Check minimum bid amount
            current_price = listing.get("price", 0)
            if bid_amount <= current_price:
                return {"valid": False, "reason": f"Bid must be higher than current price of €{current_price}"}
            
            # Check if there's a higher bid
            if listing_id in self.active_auctions:
                current_high = self.active_auctions[listing_id]['current_high_bid']
                if bid_amount <= current_high:
                    return {"valid": False, "reason": f"Bid must be higher than current high bid of €{current_high}"}
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Bid validation error: {e}")
            return {"valid": False, "reason": "Validation error"}
    
    async def _store_bid(self, bid: Dict):
        """Store bid in database"""
        try:
            # Convert to database format (existing tender structure)
            db_bid = {
                "id": bid['id'],
                "listing_id": bid['listing_id'],
                "buyer_id": bid['bidder_id'],
                "offer_amount": bid['amount'],
                "message": f"Real-time bid of €{bid['amount']}",
                "status": "pending",
                "created_at": bid['timestamp']
            }
            
            await self.db.tenders.insert_one(db_bid)
            
        except Exception as e:
            logger.error(f"Store bid error: {e}")
    
    # Public API methods for external use
    async def send_notification(self, user_id: str, notification: Dict):
        """Send real-time notification to a user"""
        try:
            sessions = self.user_sessions.get(user_id, set())
            if sessions:
                for sid in sessions:
                    await self.sio.emit('notification', notification, room=sid)
            else:
                # Store for offline delivery
                self.offline_messages[user_id].append({
                    'type': 'notification',
                    'data': notification,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Send notification error: {e}")
    
    async def broadcast_listing_update(self, listing_id: str, update_data: Dict):
        """Broadcast listing updates to all watchers"""
        try:
            room_name = f"listing:{listing_id}"
            await self.sio.emit('listing_update', {
                'listing_id': listing_id,
                'update': update_data,
                'timestamp': datetime.utcnow().isoformat()
            }, room=room_name)
            
        except Exception as e:
            logger.error(f"Broadcast listing update error: {e}")
    
    async def get_connection_stats(self) -> Dict:
        """Get WebSocket connection statistics"""
        return {
            "total_connections": len(self.active_sessions),
            "unique_users": len(self.user_sessions),
            "active_rooms": len(self.room_members),
            "active_auctions": len(self.active_auctions),
            "offline_message_queues": len(self.offline_messages),
            "connected_users": [
                session.to_dict() for session in self.active_sessions.values()
            ]
        }

# Global WebSocket service instance
websocket_service = None

async def init_websocket_service(db):
    """Initialize WebSocket service"""
    global websocket_service
    websocket_service = WebSocketService(db)
    return websocket_service

def get_websocket_service():
    """Get WebSocket service instance"""
    return websocket_service