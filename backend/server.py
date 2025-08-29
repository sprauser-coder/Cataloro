"""
CATALORO - Marketplace Backend Server
Scalable FastAPI backend with MongoDB integration
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import uuid
import json
import pandas as pd
import io
import base64
from datetime import datetime
from typing import List, Optional, Dict, Any
import motor.motor_asyncio
from bson import ObjectId

# Initialize FastAPI app
app = FastAPI(
    title="Cataloro Marketplace API",
    description="Scalable marketplace backend with feature-based architecture",
    version="1.0.0"
)

# CORS Configuration for production deployment
origins = [
    "http://217.154.0.82",
    "https://217.154.0.82",
    "http://localhost:3000",  # Development
    "http://localhost:3001",  # Development alternative
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.cataloro_marketplace

# Pydantic Models
class User(BaseModel):
    id: str = None
    username: str
    email: str
    full_name: str
    role: str = "user"
    created_at: datetime = None
    is_active: bool = True

class Listing(BaseModel):
    title: str
    description: str
    price: float
    category: str
    condition: str
    seller_id: str
    images: List[str] = []
    tags: List[str] = []
    features: List[str] = []

class CatalystData(BaseModel):
    cat_id: str
    name: str
    ceramic_weight: float
    pt_ppm: float
    pd_ppm: float
    rh_ppm: float
    add_info: Optional[str] = ""
    
class CatalystPriceSettings(BaseModel):
    pt_price: float
    pd_price: float  
    rh_price: float
    renumeration_pt: float
    renumeration_pd: float
    renumeration_rh: float

class CatalystPriceOverride(BaseModel):
    catalyst_id: str
    override_price: float
    is_override: bool = True

class Deal(BaseModel):
    id: str = None
    listing_id: str
    buyer_id: str
    seller_id: str
    status: str = "pending"
    amount: float
    created_at: datetime = None

class Notification(BaseModel):
    id: str = None
    user_id: str
    title: str
    message: str
    type: str
    is_read: bool = False
    created_at: datetime = None

# Utility Functions
def generate_id():
    return str(uuid.uuid4())

def serialize_doc(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

# Health Check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "app": "Cataloro Marketplace", "version": "1.0.0"}

# Authentication Endpoints
@app.post("/api/auth/register")
async def register_user(user_data: dict):
    user_id = generate_id()
    user = {
        "id": user_id,
        "username": user_data["username"],
        "email": user_data["email"],
        "full_name": user_data["full_name"],
        "role": "user",
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data["email"]})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    await db.users.insert_one(user)
    return {"message": "User registered successfully", "user_id": user_id}

@app.post("/api/auth/login")
async def login_user(credentials: dict):
    # Mock authentication for demo
    user = await db.users.find_one({"email": credentials["email"]})
    if not user:
        # Create demo user if not exists
        user_id = generate_id()
        
        # Set full name based on user type
        if credentials["email"] == "admin@cataloro.com":
            full_name = "Sash"
            username = "sash_admin"
        else:
            full_name = "Demo User"
            username = credentials.get("username", "demo_user")
        
        user = {
            "id": user_id,
            "username": username,
            "email": credentials["email"],
            "full_name": full_name,
            "role": "admin" if credentials["email"] == "admin@cataloro.com" else "user",
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        await db.users.insert_one(user)
    else:
        # Update existing admin user to have the correct name
        if credentials["email"] == "admin@cataloro.com" and user.get("full_name") != "Sash":
            await db.users.update_one(
                {"email": "admin@cataloro.com"},
                {"$set": {"full_name": "Sash", "username": "sash_admin"}}
            )
            # Refresh user data
            user = await db.users.find_one({"email": credentials["email"]})
    
    # Get user ID for token
    user_id = user.get('id') if user else generate_id()
    
    return {
        "message": "Login successful",
        "user": serialize_doc(user),
        "token": f"mock_token_{user_id}"
    }

@app.get("/api/auth/profile/{user_id}")
async def get_profile(user_id: str):
    # Try to find user by id field first, then by _id
    user = await db.users.find_one({"id": user_id})
    if not user:
        # Try with _id in case it's stored differently
        try:
            from bson import ObjectId
            user = await db.users.find_one({"_id": ObjectId(user_id)})
        except:
            pass
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_doc(user)

# Marketplace Endpoints
@app.get("/api/marketplace/browse")
async def browse_listings():
    listings_cursor = db.listings.find({"status": "active"}).limit(50)
    listings = []
    async for listing in listings_cursor:
        listings.append(serialize_doc(listing))
    
    # Add dummy data if empty
    if not listings:
        dummy_listings = [
            {
                "id": generate_id(),
                "title": "MacBook Pro 16-inch",
                "description": "Excellent condition, barely used",
                "price": 2500.00,
                "category": "Electronics",
                "seller_id": "demo_seller_1",
                "status": "active",
                "created_at": datetime.utcnow(),
                "images": ["https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400"]
            },
            {
                "id": generate_id(),
                "title": "Vintage Guitar",
                "description": "Classic acoustic guitar with rich sound",
                "price": 800.00,
                "category": "Music",
                "seller_id": "demo_seller_2",
                "status": "active",
                "created_at": datetime.utcnow(),
                "images": ["https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=400"]
            },
            {
                "id": generate_id(),
                "title": "Designer Handbag",
                "description": "Authentic luxury handbag in perfect condition",
                "price": 1200.00,
                "category": "Fashion",
                "seller_id": "demo_seller_3",
                "status": "active",
                "created_at": datetime.utcnow(),
                "images": ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400"]
            }
        ]
        
        # Insert dummy data
        for listing in dummy_listings:
            await db.listings.insert_one(listing)
        
        # Return serialized dummy data
        return [serialize_doc(listing) for listing in dummy_listings]
    
    return listings

@app.get("/api/user/my-listings/{user_id}")
async def get_my_listings(user_id: str):
    listings_cursor = db.listings.find({"seller_id": user_id})
    listings = []
    async for listing in listings_cursor:
        listings.append(serialize_doc(listing))
    return listings

@app.get("/api/user/my-deals/{user_id}")
async def get_my_deals(user_id: str):
    deals_cursor = db.deals.find({
        "$or": [{"buyer_id": user_id}, {"seller_id": user_id}]
    })
    deals = []
    async for deal in deals_cursor:
        deals.append(serialize_doc(deal))
    return deals

@app.get("/api/user/notifications/{user_id}")
async def get_notifications(user_id: str):
    notifications_cursor = db.notifications.find({"user_id": user_id}).sort("created_at", -1)
    notifications = []
    async for notification in notifications_cursor:
        notifications.append(serialize_doc(notification))
    
    # Add dummy notifications if empty
    if not notifications:
        dummy_notifications = [
            {
                "id": generate_id(),
                "user_id": user_id,
                "title": "New message",
                "message": "You have a new message about your MacBook listing",
                "type": "message",
                "is_read": False,
                "created_at": datetime.utcnow()
            },
            {
                "id": generate_id(),
                "user_id": user_id,
                "title": "Listing viewed",
                "message": "Your vintage guitar listing has been viewed 5 times today",
                "type": "info",
                "is_read": False,
                "created_at": datetime.utcnow()
            }
        ]
        
        for notification in dummy_notifications:
            await db.notifications.insert_one(notification)
        
        # Return serialized dummy data
        return [serialize_doc(notification) for notification in dummy_notifications]
    
    return notifications

# Admin Endpoints
@app.get("/api/admin/dashboard")
async def get_admin_dashboard():
    # Get KPIs
    total_users = await db.users.count_documents({})
    total_listings = await db.listings.count_documents({})
    active_listings = await db.listings.count_documents({"status": "active"})
    total_deals = await db.deals.count_documents({})
    
    return {
        "kpis": {
            "total_users": total_users or 156,  # Demo data
            "total_listings": total_listings or 234,
            "active_listings": active_listings or 189,
            "total_deals": total_deals or 67,
            "revenue": 45680.50,  # Demo revenue
            "growth_rate": 12.5   # Demo growth
        },
        "recent_activity": [
            {"action": "New user registered", "timestamp": datetime.utcnow()},
            {"action": "Listing created", "timestamp": datetime.utcnow()},
            {"action": "Deal completed", "timestamp": datetime.utcnow()}
        ]
    }

@app.get("/api/admin/users")
async def get_all_users():
    users_cursor = db.users.find({})
    users = []
    async for user in users_cursor:
        users.append(serialize_doc(user))
    return users

@app.put("/api/admin/users/{user_id}")
async def update_user(user_id: str, user_data: dict):
    # Try to update by UUID id field first
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": user_data}
    )
    
    # If not found, try by ObjectId (for API compatibility)
    if result.matched_count == 0:
        try:
            from bson import ObjectId
            result = await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": user_data}
            )
        except:
            pass
    
    if result.modified_count:
        return {"message": "User updated successfully"}
    raise HTTPException(status_code=404, detail="User not found")

# Site Branding and Settings Endpoints
@app.get("/api/admin/settings")
async def get_site_settings():
    """Get site branding and configuration settings"""
    try:
        # Get settings from database or return defaults
        settings = await db.site_settings.find_one({"type": "site_branding"})
        
        if not settings:
            # Return default settings
            default_settings = {
                "site_name": "Cataloro",
                "site_description": "Modern Marketplace Platform",
                "logo_url": "/favicon.ico",
                "logo_light_url": "",
                "logo_dark_url": "",
                "theme_color": "#3B82F6",
                "allow_registration": True,
                "require_approval": False,
                "email_notifications": True,
                "commission_rate": 5.0,
                "max_file_size": 10
            }
            return default_settings
        
        # Remove MongoDB _id field
        settings.pop('_id', None)
        settings.pop('type', None)
        return settings
        
    except Exception as e:
        return {
            "site_name": "Cataloro",
            "site_description": "Modern Marketplace Platform",
            "logo_url": "/favicon.ico",
            "logo_light_url": "",
            "logo_dark_url": "",
            "theme_color": "#3B82F6"
        }

@app.put("/api/admin/settings")
async def update_site_settings(settings_data: dict):
    """Update site branding and configuration settings"""
    try:
        # Add metadata
        settings_data["type"] = "site_branding"
        settings_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Update or insert settings
        result = await db.site_settings.update_one(
            {"type": "site_branding"},
            {"$set": settings_data},
            upsert=True
        )
        
        return {"message": "Site settings updated successfully", "modified": result.modified_count}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

@app.post("/api/admin/logo")
async def upload_logo(file: UploadFile = File(...), mode: str = "light"):
    """Upload logo file and return URL"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (2MB limit)
        contents = await file.read()
        if len(contents) > 2 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 2MB")
        
        # Reset file pointer
        await file.seek(0)
        
        # For demo purposes, return a data URL
        import base64
        file_data = base64.b64encode(contents).decode()
        file_url = f"data:{file.content_type};base64,{file_data}"
        
        # In production, you would save to a file system or cloud storage
        # and return the public URL
        
        return {
            "message": "Logo uploaded successfully",
            "url": file_url,
            "mode": mode,
            "filename": file.filename,
            "size": len(contents)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload logo: {str(e)}")

# Marketplace Listings Endpoints
@app.get("/api/listings")
async def get_all_listings(
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    condition: str = None,
    search: str = None,
    limit: int = 20,
    offset: int = 0
):
    """Get all listings with optional filtering"""
    try:
        query = {}
        
        if category and category != 'all':
            query['category'] = category
        if condition and condition != 'all':
            query['condition'] = condition
        if min_price is not None:
            query['price'] = {'$gte': min_price}
        if max_price is not None:
            if 'price' in query:
                query['price']['$lte'] = max_price
            else:
                query['price'] = {'$lte': max_price}
        
        # Get listings from database
        listings_cursor = db.listings.find(query).sort("created_at", -1).skip(offset).limit(limit)
        listings = []
        
        async for listing in listings_cursor:
            listing['_id'] = str(listing['_id'])
            listings.append(listing)
        
        return {
            "listings": listings,
            "total": await db.listings.count_documents(query)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch listings: {str(e)}")

@app.post("/api/listings")
async def create_listing(listing_data: dict):
    """Create a new listing"""
    try:
        # Add metadata
        listing_data["id"] = str(uuid.uuid4())
        listing_data["created_at"] = datetime.utcnow().isoformat()
        listing_data["updated_at"] = datetime.utcnow().isoformat()
        listing_data["status"] = "active"
        listing_data["views"] = 0
        listing_data["favorites_count"] = 0
        
        # Validate required fields
        required_fields = ['title', 'description', 'price', 'category', 'condition', 'seller_id']
        for field in required_fields:
            if field not in listing_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Insert into database
        result = await db.listings.insert_one(listing_data)
        
        return {
            "message": "Listing created successfully",
            "listing_id": listing_data["id"],
            "status": "active"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create listing: {str(e)}")

@app.put("/api/listings/{listing_id}")
async def update_listing(listing_id: str, update_data: dict):
    """Update an existing listing"""
    try:
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = await db.listings.update_one(
            {"id": listing_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        return {"message": "Listing updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update listing: {str(e)}")

@app.delete("/api/listings/{listing_id}")
async def delete_listing(listing_id: str):
    """Delete a listing"""
    try:
        result = await db.listings.delete_one({"id": listing_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        return {"message": "Listing deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete listing: {str(e)}")

@app.get("/api/listings/{listing_id}")
async def get_listing(listing_id: str):
    """Get a specific listing by ID"""
    try:
        listing = await db.listings.find_one({"id": listing_id})
        
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        listing['_id'] = str(listing['_id'])
        
        # Increment view count
        await db.listings.update_one(
            {"id": listing_id},
            {"$inc": {"views": 1}}
        )
        
        return listing
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch listing: {str(e)}")

@app.post("/api/listings/{listing_id}/images")
async def upload_listing_image(listing_id: str, file: UploadFile = File(...)):
    """Upload image for a listing"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (5MB limit)
        contents = await file.read()
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 5MB")
        
        # For demo purposes, return a data URL
        import base64
        file_data = base64.b64encode(contents).decode()
        image_url = f"data:{file.content_type};base64,{file_data}"
        
        # Update listing with new image
        result = await db.listings.update_one(
            {"id": listing_id},
            {"$push": {"images": image_url}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        return {
            "message": "Image uploaded successfully",
            "image_url": image_url,
            "filename": file.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

# ============================================================================
# LIVE FUNCTIONALITY ENDPOINTS
# ============================================================================

# Favorites endpoints
@app.get("/api/user/{user_id}/favorites")
async def get_user_favorites(user_id: str):
    """Get user's favorite items"""
    try:
        favorites = await db.user_favorites.find({"user_id": user_id}).to_list(length=None)
        
        for favorite in favorites:
            favorite['_id'] = str(favorite['_id'])
        
        return favorites
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch favorites: {str(e)}")

@app.post("/api/user/{user_id}/favorites/{item_id}")
async def add_to_favorites(user_id: str, item_id: str):
    """Add item to user's favorites"""
    try:
        favorite_data = {
            "user_id": user_id,
            "item_id": item_id,
            "created_at": datetime.utcnow().isoformat(),
            "id": str(uuid.uuid4())
        }
        
        # Check if already exists
        existing = await db.user_favorites.find_one({"user_id": user_id, "item_id": item_id})
        if existing:
            return {"message": "Item already in favorites"}
        
        await db.user_favorites.insert_one(favorite_data)
        return {"message": "Added to favorites successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add to favorites: {str(e)}")

@app.delete("/api/user/{user_id}/favorites/{item_id}")
async def remove_from_favorites(user_id: str, item_id: str):
    """Remove item from user's favorites"""
    try:
        result = await db.user_favorites.delete_one({"user_id": user_id, "item_id": item_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Favorite not found")
        
        return {"message": "Removed from favorites successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove from favorites: {str(e)}")

# Cart endpoints  
@app.get("/api/user/{user_id}/cart")
async def get_user_cart(user_id: str):
    """Get user's cart items"""
    try:
        cart_items = await db.user_cart.find({"user_id": user_id}).to_list(length=None)
        
        for item in cart_items:
            item['_id'] = str(item['_id'])
        
        return cart_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cart: {str(e)}")

@app.post("/api/user/{user_id}/cart")
async def add_to_cart(user_id: str, cart_item: dict):
    """Add item to user's cart"""
    try:
        cart_data = {
            "user_id": user_id,
            "item_id": cart_item.get("item_id"),
            "quantity": cart_item.get("quantity", 1),
            "price": cart_item.get("price", 0),
            "created_at": datetime.utcnow().isoformat(),
            "id": str(uuid.uuid4())
        }
        
        # Check if item already in cart
        existing = await db.user_cart.find_one({"user_id": user_id, "item_id": cart_item.get("item_id")})
        if existing:
            # Update quantity
            new_quantity = existing["quantity"] + cart_item.get("quantity", 1)
            await db.user_cart.update_one(
                {"user_id": user_id, "item_id": cart_item.get("item_id")},
                {"$set": {"quantity": new_quantity, "updated_at": datetime.utcnow().isoformat()}}
            )
            return {"message": "Cart quantity updated"}
        
        await db.user_cart.insert_one(cart_data)
        return {"message": "Added to cart successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add to cart: {str(e)}")

@app.put("/api/user/{user_id}/cart/{item_id}")
async def update_cart_item(user_id: str, item_id: str, update_data: dict):
    """Update cart item quantity"""
    try:
        result = await db.user_cart.update_one(
            {"user_id": user_id, "item_id": item_id},
            {"$set": {
                "quantity": update_data.get("quantity", 1),
                "updated_at": datetime.utcnow().isoformat()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        return {"message": "Cart item updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update cart item: {str(e)}")

@app.delete("/api/user/{user_id}/cart/{item_id}")
async def remove_from_cart(user_id: str, item_id: str):
    """Remove item from cart"""
    try:
        result = await db.user_cart.delete_one({"user_id": user_id, "item_id": item_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        return {"message": "Removed from cart successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove from cart: {str(e)}")

# Messages endpoints
@app.get("/api/user/{user_id}/messages")
async def get_user_messages(user_id: str):
    """Get user's messages"""
    try:
        messages = await db.user_messages.find({"$or": [{"sender_id": user_id}, {"recipient_id": user_id}]}).sort("created_at", -1).to_list(length=None)
        
        for message in messages:
            message['_id'] = str(message['_id'])
        
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")

@app.post("/api/user/{user_id}/messages")
async def send_message(user_id: str, message_data: dict):
    """Send a message"""
    try:
        message = {
            "sender_id": user_id,
            "recipient_id": message_data.get("recipient_id"),
            "subject": message_data.get("subject", ""),
            "content": message_data.get("content"),
            "is_read": False,
            "created_at": datetime.utcnow().isoformat(),
            "id": str(uuid.uuid4())
        }
        
        await db.user_messages.insert_one(message)
        return {"message": "Message sent successfully", "id": message["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@app.put("/api/user/{user_id}/messages/{message_id}/read")
async def mark_message_read(user_id: str, message_id: str):
    """Mark message as read"""
    try:
        result = await db.user_messages.update_one(
            {"id": message_id, "$or": [{"sender_id": user_id}, {"recipient_id": user_id}]},
            {"$set": {"is_read": True, "read_at": datetime.utcnow().isoformat()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return {"message": "Message marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark message as read: {str(e)}")

# Notifications endpoints
@app.get("/api/user/{user_id}/notifications")
async def get_user_notifications(user_id: str):
    """Get user's notifications"""
    try:
        notifications = await db.user_notifications.find({"user_id": user_id}).sort("created_at", -1).to_list(length=None)
        
        for notification in notifications:
            notification['_id'] = str(notification['_id'])
        
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")

@app.post("/api/user/{user_id}/notifications")
async def create_notification(user_id: str, notification_data: dict):
    """Create a notification"""
    try:
        notification = {
            "user_id": user_id,
            "title": notification_data.get("title"),
            "message": notification_data.get("message"),
            "type": notification_data.get("type", "info"),
            "is_read": False,
            "created_at": datetime.utcnow().isoformat(),
            "id": str(uuid.uuid4())
        }
        
        await db.user_notifications.insert_one(notification)
        return {"message": "Notification created successfully", "id": notification["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create notification: {str(e)}")

@app.put("/api/user/{user_id}/notifications/{notification_id}/read")
async def mark_notification_read(user_id: str, notification_id: str):
    """Mark notification as read"""
    try:
        result = await db.user_notifications.update_one(
            {"user_id": user_id, "id": notification_id},
            {"$set": {"is_read": True, "read_at": datetime.utcnow().isoformat()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"message": "Notification marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")

# ============================================================================
# CAT DATABASE ENDPOINTS
# ============================================================================

@app.post("/api/admin/catalyst/upload")
async def upload_catalyst_excel(file: UploadFile = File(...)):
    """Upload Excel file with catalyst data"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="File must be Excel format (.xlsx or .xls)")
        
        contents = await file.read()
        
        # Check file size (limit to 10MB)
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size too large. Maximum 10MB allowed.")
        
        df = pd.read_excel(io.BytesIO(contents))
        
        # Validate required columns
        required_columns = ['cat_id', 'name', 'ceramic_weight', 'pt_ppm', 'pd_ppm', 'rh_ppm']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(status_code=400, detail=f"Missing required columns: {missing_columns}")
        
        # Validate data and process
        catalysts = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Helper function to safely convert to float
                def safe_float(value, field_name, row_num):
                    if pd.isna(value) or value == '' or value is None:
                        return 0.0
                    try:
                        result = float(value)
                        # Check for valid range (avoid infinity and very large numbers)
                        if not (-1e10 <= result <= 1e10):
                            errors.append(f"Row {row_num}: {field_name} value {result} is out of valid range")
                            return 0.0
                        return result
                    except (ValueError, TypeError):
                        errors.append(f"Row {row_num}: Invalid {field_name} value '{value}'")
                        return 0.0
                
                row_num = index + 2  # +2 because Excel rows start at 1 and we have header
                
                catalyst_data = {
                    "cat_id": str(row.get('cat_id', '')).strip(),
                    "name": str(row.get('name', '')).strip(),
                    "ceramic_weight": safe_float(row.get('ceramic_weight'), 'ceramic_weight', row_num),
                    "pt_ppm": safe_float(row.get('pt_ppm'), 'pt_ppm', row_num),
                    "pd_ppm": safe_float(row.get('pd_ppm'), 'pd_ppm', row_num),
                    "rh_ppm": safe_float(row.get('rh_ppm'), 'rh_ppm', row_num),
                    "add_info": str(row.get('add_info', '')).strip(),
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "id": str(uuid.uuid4())
                }
                
                # Validate required fields
                if not catalyst_data["cat_id"]:
                    errors.append(f"Row {row_num}: cat_id is required")
                    continue
                    
                if not catalyst_data["name"]:
                    errors.append(f"Row {row_num}: name is required")
                    continue
                
                catalysts.append(catalyst_data)
                
            except Exception as row_error:
                errors.append(f"Row {index + 2}: {str(row_error)}")
                continue
        
        # Check if we have any valid data
        if not catalysts and errors:
            raise HTTPException(status_code=400, detail=f"No valid data found. Errors: {'; '.join(errors[:5])}")
        
        # Clear existing data and insert new
        await db.catalyst_data.delete_many({})
        if catalysts:
            await db.catalyst_data.insert_many(catalysts)
        
        response = {
            "message": f"Successfully uploaded {len(catalysts)} catalyst records",
            "count": len(catalysts),
            "columns": list(df.columns),
            "total_rows": len(df),
            "valid_rows": len(catalysts),
            "errors_count": len(errors)
        }
        
        if errors:
            response["errors"] = errors[:10]  # First 10 errors
            response["message"] += f" with {len(errors)} warnings/errors"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "Out of range float values" in error_msg:
            error_msg = "Excel file contains numbers that are too large. Please check your numeric values."
        raise HTTPException(status_code=500, detail=f"Failed to upload catalyst data: {error_msg}")

@app.get("/api/admin/catalyst/data")
async def get_catalyst_data():
    """Get all catalyst data for the Data tab"""
    try:
        catalysts = await db.catalyst_data.find({}).to_list(length=None)
        
        # Convert MongoDB ObjectId to string
        for catalyst in catalysts:
            catalyst['_id'] = str(catalyst['_id'])
        
        return catalysts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch catalyst data: {str(e)}")

@app.put("/api/admin/catalyst/data/{catalyst_id}")
async def update_catalyst_data(catalyst_id: str, update_data: dict):
    """Update specific catalyst data"""
    try:
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = await db.catalyst_data.update_one(
            {"id": catalyst_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Catalyst not found")
        
        return {"message": "Catalyst data updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update catalyst data: {str(e)}")

@app.get("/api/admin/catalyst/price-settings")
async def get_price_settings():
    """Get catalyst price calculation settings"""
    try:
        settings = await db.catalyst_price_settings.find_one({"type": "price_settings"})
        
        if not settings:
            # Return default settings
            default_settings = {
                "pt_price": 25.0,
                "pd_price": 18.0,
                "rh_price": 45.0,
                "renumeration_pt": 0.95,
                "renumeration_pd": 0.92,
                "renumeration_rh": 0.88
            }
            return default_settings
        
        settings['_id'] = str(settings['_id'])
        return settings
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch price settings: {str(e)}")

@app.put("/api/admin/catalyst/price-settings")
async def update_price_settings(settings: CatalystPriceSettings):
    """Update catalyst price calculation settings"""
    try:
        settings_data = settings.dict()
        settings_data.update({
            "type": "price_settings",
            "updated_at": datetime.utcnow().isoformat()
        })
        
        result = await db.catalyst_price_settings.update_one(
            {"type": "price_settings"},
            {"$set": settings_data},
            upsert=True
        )
        
        return {"message": "Price settings updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update price settings: {str(e)}")

@app.get("/api/admin/catalyst/calculations")
async def get_catalyst_calculations():
    """Get calculated prices for all catalysts"""
    try:
        # Get price settings
        settings = await db.catalyst_price_settings.find_one({"type": "price_settings"})
        if not settings:
            # Default values
            settings = {
                "pt_price": 25.0,
                "pd_price": 18.0,
                "rh_price": 45.0,
                "renumeration_pt": 0.95,
                "renumeration_pd": 0.92,
                "renumeration_rh": 0.88
            }
        
        # Get all catalyst data
        catalysts = await db.catalyst_data.find({}).to_list(length=None)
        
        # Get price overrides
        overrides = await db.catalyst_price_overrides.find({}).to_list(length=None)
        override_dict = {override['catalyst_id']: override for override in overrides}
        
        # Calculate prices
        calculations = []
        for catalyst in catalysts:
            catalyst_id = catalyst['id']
            
            # Check for override
            if catalyst_id in override_dict and override_dict[catalyst_id]['is_override']:
                total_price = override_dict[catalyst_id]['override_price']
                is_override = True
            else:
                # Calculate standard price
                ceramic_weight = catalyst.get('ceramic_weight', 0)
                pt_ppm = catalyst.get('pt_ppm', 0)
                pd_ppm = catalyst.get('pd_ppm', 0)
                rh_ppm = catalyst.get('rh_ppm', 0)
                
                pt_value = (ceramic_weight * (pt_ppm / 1000) * settings['renumeration_pt']) * settings['pt_price']
                pd_value = (ceramic_weight * (pd_ppm / 1000) * settings['renumeration_pd']) * settings['pd_price']
                rh_value = (ceramic_weight * (rh_ppm / 1000) * settings['renumeration_rh']) * settings['rh_price']
                
                total_price = pt_value + pd_value + rh_value
                is_override = False
            
            calculations.append({
                "_id": catalyst_id,
                "database_id": catalyst_id,
                "cat_id": catalyst.get('cat_id', ''),
                "name": catalyst.get('name', ''),
                "total_price": round(total_price, 2),
                "is_override": is_override
            })
        
        return calculations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate prices: {str(e)}")

@app.post("/api/admin/catalyst/override/{catalyst_id}")
async def set_price_override(catalyst_id: str, override_data: CatalystPriceOverride):
    """Set price override for specific catalyst"""
    try:
        override_doc = override_data.dict()
        override_doc.update({
            "catalyst_id": catalyst_id,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        result = await db.catalyst_price_overrides.update_one(
            {"catalyst_id": catalyst_id},
            {"$set": override_doc},
            upsert=True
        )
        
        return {"message": "Price override set successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set price override: {str(e)}")

@app.post("/api/admin/catalyst/reset/{catalyst_id}")
async def reset_price_calculation(catalyst_id: str):
    """Reset catalyst to standard price calculation"""
    try:
        result = await db.catalyst_price_overrides.update_one(
            {"catalyst_id": catalyst_id},
            {"$set": {"is_override": False, "updated_at": datetime.utcnow().isoformat()}}
        )
        
        return {"message": "Price calculation reset to standard"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset price calculation: {str(e)}")

@app.delete("/api/admin/catalyst/database")
async def delete_catalyst_database():
    """Delete all catalyst data from the database"""
    try:
        # Delete all catalyst data
        result_data = await db.catalyst_data.delete_many({})
        
        # Delete all price overrides
        result_overrides = await db.catalyst_price_overrides.delete_many({})
        
        # Reset price settings to default (optional - you might want to keep settings)
        # await db.catalyst_price_settings.delete_many({})
        
        return {
            "message": "Catalyst database deleted successfully",
            "deleted_records": result_data.deleted_count,
            "deleted_overrides": result_overrides.deleted_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete catalyst database: {str(e)}")

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)