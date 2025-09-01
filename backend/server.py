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
from datetime import datetime, timedelta
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

class Order(BaseModel):
    id: str = None
    buyer_id: str
    seller_id: str
    listing_id: str
    status: str = "pending"  # pending, approved, rejected, expired, cancelled
    created_at: datetime = None
    expires_at: datetime = None
    approved_at: datetime = None

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
        "is_active": True,
        # Business account fields
        "is_business": user_data.get("is_business", False),
        "business_name": user_data.get("business_name", ""),
        "company_name": user_data.get("company_name", "")
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
async def browse_listings(
    type: str = "all",  # Filter by seller type: "all", "Private", "Business"
    price_from: int = 0,  # Minimum price filter
    price_to: int = 999999  # Maximum price filter
):
    """Browse available listings with seller information and filters"""
    try:
        # Build query for active listings
        query = {"status": "active"}
        
        # Apply price range filter
        if price_from > 0 or price_to < 999999:
            query["price"] = {}
            if price_from > 0:
                query["price"]["$gte"] = price_from
            if price_to < 999999:
                query["price"]["$lte"] = price_to
        
        # Get filtered listings
        listings = await db.listings.find(query).to_list(length=None)
        
        # Enrich listings with seller information
        enriched_listings = []
        for listing in listings:
            # Ensure consistent ID format (use UUID 'id' field, not ObjectId '_id')
            if 'id' not in listing and '_id' in listing:
                listing['id'] = str(listing['_id'])
            elif 'id' in listing:
                listing['id'] = listing['id']  # Keep existing UUID
            
            # Remove MongoDB ObjectId to avoid confusion
            listing.pop('_id', None)
            
            # Fetch seller information from users collection
            seller_id = listing.get('seller_id')
            if seller_id:
                try:
                    # Try to find user by id field first, then by _id (same as profile endpoint)
                    seller_profile = await db.users.find_one({"id": seller_id})
                    if not seller_profile:
                        # Try with _id in case it's stored differently
                        try:
                            from bson import ObjectId
                            seller_profile = await db.users.find_one({"_id": ObjectId(seller_id)})
                        except:
                            pass
                    
                    if seller_profile:
                        print(f"DEBUG: Seller profile data: {seller_profile}")
                        # Enrich listing with seller information
                        listing['seller'] = {
                            "name": seller_profile.get('username') or seller_profile.get('name') or seller_profile.get('email', 'Unknown'),
                            "username": seller_profile.get('username') or seller_profile.get('name') or 'Unknown',
                            "email": seller_profile.get('email', ''),
                            "is_business": seller_profile.get('is_business', False),
                            "business_name": seller_profile.get('company_name', ''),
                            "verified": seller_profile.get('verified', False),
                            "location": listing.get('address', {}).get('city', '') + 
                                      (', ' + listing.get('address', {}).get('country', '') if listing.get('address', {}).get('country') else '') or
                                      seller_profile.get('city', '') + 
                                      (', ' + seller_profile.get('country', '') if seller_profile.get('country') else '') or
                                      'Location not specified'
                        }
                    else:
                        # Fallback seller info if profile not found
                        listing['seller'] = {
                            "name": "Unknown User",
                            "username": "Unknown",
                            "email": "",
                            "is_business": False,
                            "business_name": "",
                            "verified": False,
                            "location": "Location not specified"
                        }
                except Exception as seller_error:
                    print(f"Error fetching seller info for {seller_id}: {seller_error}")
                    # Fallback seller info
                    listing['seller'] = {
                        "name": "Unknown User",
                        "username": "Unknown", 
                        "email": "",
                        "is_business": False,
                        "business_name": "",
                        "verified": False,
                        "location": "Location not specified"
                    }
            else:
                # No seller_id found
                listing['seller'] = {
                    "name": "Unknown User",
                    "username": "Unknown",
                    "email": "",
                    "is_business": False,
                    "business_name": "",
                    "verified": False,
                    "location": "Location not specified"
                }
            
            enriched_listings.append(listing)
        
        # Apply seller type filter after enrichment (since we need seller info)
        if type != "all":
            if type == "Private":
                enriched_listings = [listing for listing in enriched_listings if not listing.get('seller', {}).get('is_business', False)]
            elif type == "Business":
                enriched_listings = [listing for listing in enriched_listings if listing.get('seller', {}).get('is_business', False)]
        
        return enriched_listings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to browse listings: {str(e)}")

@app.get("/api/user/my-listings/{user_id}")
async def get_my_listings(user_id: str):
    """Get user's listings - only active listings for consistency with browse"""
    try:
        # Only return active listings to match browse page behavior
        listings = await db.listings.find({"seller_id": user_id, "status": "active"}).sort("created_at", -1).to_list(length=None)
        
        # Ensure consistent ID format
        for listing in listings:
            if 'id' not in listing and '_id' in listing:
                listing['id'] = str(listing['_id'])
            listing.pop('_id', None)
        
        return listings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user listings: {str(e)}")

@app.get("/api/user/my-deals/{user_id}")
async def get_my_deals(user_id: str):
    """Get all deals (approved orders) for a user - both as buyer and seller"""
    try:
        # Get all orders where user is buyer or seller and status is approved
        orders_cursor = db.orders.find({
            "$and": [
                {"$or": [{"buyer_id": user_id}, {"seller_id": user_id}]},
                {"status": {"$in": ["approved", "completed"]}}
            ]
        }).sort("created_at", -1)
        
        deals = []
        async for order in orders_cursor:
            # Enrich with listing data
            listing = await db.listings.find_one({"id": order.get("listing_id")})
            
            # Enrich with buyer data if user is seller
            buyer_info = {}
            if order.get("buyer_id") != user_id:
                buyer = await db.users.find_one({"id": order.get("buyer_id")})
                if buyer:
                    buyer_info = {
                        "id": buyer.get("id"),
                        "username": buyer.get("username", "Unknown"),
                        "email": buyer.get("email", "")
                    }
            
            # Enrich with seller data if user is buyer
            seller_info = {}
            if order.get("seller_id") != user_id:
                seller = await db.users.find_one({"id": order.get("seller_id")})
                if seller:
                    seller_info = {
                        "id": seller.get("id"),
                        "username": seller.get("username", "Unknown"),
                        "email": seller.get("email", "")
                    }
            
            # Create deal object
            deal = {
                "id": order.get("id"),
                "listing_id": order.get("listing_id"),
                "buyer_id": order.get("buyer_id"),
                "seller_id": order.get("seller_id"),
                "status": order.get("status"),
                "amount": listing.get("price", 0) if listing else 0,
                "created_at": order.get("created_at"),
                "approved_at": order.get("approved_at"),
                "listing": {
                    "id": listing.get("id", ""),
                    "title": listing.get("title", "Unknown Item"),
                    "price": listing.get("price", 0),
                    "image": listing.get("images", [""])[0] if listing and listing.get("images") else ""
                } if listing else {},
                "buyer": buyer_info,
                "seller": seller_info
            }
            
            deals.append(deal)
        
        return deals
    except Exception as e:
        print(f"Error fetching deals: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch deals: {str(e)}")

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

@app.get("/api/listings/{listing_id}")
async def get_listing(listing_id: str):
    """Get a single listing by ID"""
    try:
        # Try to find by UUID 'id' field first (preferred format)
        listing = await db.listings.find_one({"id": listing_id})
        
        # If not found by UUID, try by ObjectId (backward compatibility)
        if not listing:
            try:
                from bson import ObjectId
                if ObjectId.is_valid(listing_id):
                    listing = await db.listings.find_one({"_id": ObjectId(listing_id)})
            except:
                pass
        
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
        
        # Convert ObjectId to string for JSON serialization
        if listing.get('_id'):
            listing['_id'] = str(listing['_id'])
        
        return listing
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch listing: {str(e)}")

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
    """Delete a listing by ID with proper ID format handling"""
    try:
        # Try to delete by UUID 'id' field first (preferred format)
        result = await db.listings.delete_one({"id": listing_id})
        
        # If not found by UUID, try by ObjectId (backward compatibility)
        if result.deleted_count == 0:
            try:
                from bson import ObjectId
                if ObjectId.is_valid(listing_id):
                    result = await db.listings.delete_one({"_id": ObjectId(listing_id)})
            except:
                pass  # Not a valid ObjectId, continue with original error
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Listing with ID {listing_id} not found")
        
        return {"message": f"Listing {listing_id} deleted successfully", "deleted_count": result.deleted_count}
    except HTTPException:
        raise
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
    """Get user's favorite items with full listing details"""
    try:
        # Get user's favorite item IDs
        favorites = await db.user_favorites.find({"user_id": user_id}).to_list(length=None)
        
        if not favorites:
            return []
        
        # Extract item IDs from favorites
        item_ids = [favorite["item_id"] for favorite in favorites]
        
        # Get full listing details for favorite items
        favorite_listings = []
        for item_id in item_ids:
            listing = await db.listings.find_one({"id": item_id})
            if listing:
                listing['_id'] = str(listing['_id'])
                # Add favorite metadata
                favorite_record = next((fav for fav in favorites if fav["item_id"] == item_id), None)
                if favorite_record:
                    listing['favorited_at'] = favorite_record.get('created_at')
                favorite_listings.append(listing)
        
        return favorite_listings
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
    """Get user's messages with sender/recipient information"""
    try:
        messages = await db.user_messages.find({"$or": [{"sender_id": user_id}, {"recipient_id": user_id}]}).sort("created_at", -1).to_list(length=None)
        
        # Enrich messages with user information
        enriched_messages = []
        for message in messages:
            message['_id'] = str(message['_id'])
            
            # Add sender information with fallback lookup
            sender = await db.users.find_one({"id": message['sender_id']})
            if not sender:
                # Try with _id in case it's stored differently
                try:
                    from bson import ObjectId
                    sender = await db.users.find_one({"_id": ObjectId(message['sender_id'])})
                except:
                    pass
            message['sender_name'] = sender.get('full_name', sender.get('username', 'Unknown')) if sender else 'Unknown'
            
            # Add recipient information with fallback lookup
            recipient = await db.users.find_one({"id": message['recipient_id']})
            if not recipient:
                # Try with _id in case it's stored differently
                try:
                    from bson import ObjectId
                    recipient = await db.users.find_one({"_id": ObjectId(message['recipient_id'])})
                except:
                    pass
            message['recipient_name'] = recipient.get('full_name', recipient.get('username', 'Unknown')) if recipient else 'Unknown'
            
            enriched_messages.append(message)
        
        return enriched_messages
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

@app.get("/api/users/search")
async def search_users(q: str = ""):
    """Search users by username or full name for messaging"""
    try:
        if len(q.strip()) < 2:
            return []
        
        users = await db.users.find({
            "$or": [
                {"username": {"$regex": q, "$options": "i"}},
                {"full_name": {"$regex": q, "$options": "i"}}
            ]
        }).limit(10).to_list(length=None)
        
        # Return only necessary fields for privacy
        user_results = []
        for user in users:
            user_results.append({
                "id": user['id'],
                "username": user['username'],
                "full_name": user.get('full_name', ''),
                "display_name": user.get('full_name', user['username'])
            })
        
        return user_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search users: {str(e)}")

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

@app.delete("/api/notifications/{notification_id}")
async def delete_notification(notification_id: str, user_id: str = None):
    """Delete notification by ID"""
    try:
        # Support both direct notification ID and user-scoped deletion
        query = {"id": notification_id}
        if user_id:
            query["user_id"] = user_id
        
        # Try both collections for compatibility
        result = await db.notifications.delete_one(query)
        if result.deleted_count == 0:
            result = await db.user_notifications.delete_one(query)
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"message": "Notification deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete notification: {str(e)}")

@app.delete("/api/user/{user_id}/notifications/{notification_id}")
async def delete_user_notification(user_id: str, notification_id: str):
    """Delete specific user notification"""
    try:
        # Try both collections for compatibility
        result = await db.notifications.delete_one({
            "user_id": user_id, 
            "id": notification_id
        })
        
        if result.deleted_count == 0:
            result = await db.user_notifications.delete_one({
                "user_id": user_id, 
                "id": notification_id
            })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"message": "Notification deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete notification: {str(e)}")

# ============================================================================
# ORDER MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/orders/create")
async def create_buy_request(order_data: dict):
    """Create a buy request (pending order)"""
    try:
        listing_id = order_data.get("listing_id")
        buyer_id = order_data.get("buyer_id")
        
        if not listing_id or not buyer_id:
            raise HTTPException(status_code=400, detail="listing_id and buyer_id are required")
        
        # Check if listing exists and is active
        listing = await db.listings.find_one({"id": listing_id, "status": "active"})
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found or not active")
        
        seller_id = listing.get("seller_id")
        if seller_id == buyer_id:
            raise HTTPException(status_code=400, detail="Cannot buy your own listing")
        
        # Check if there's already a pending order for this listing (first-come-first-served)
        existing_order = await db.orders.find_one({
            "listing_id": listing_id, 
            "status": "pending"
        })
        if existing_order:
            raise HTTPException(status_code=409, detail="This item already has a pending buy request")
        
        # Create the order
        order_id = generate_id()
        current_time = datetime.utcnow()
        expires_at = datetime.utcnow().replace(microsecond=0) + timedelta(hours=48)  # 48 hours from now
        
        order = {
            "id": order_id,
            "buyer_id": buyer_id,
            "seller_id": seller_id,
            "listing_id": listing_id,
            "status": "pending",
            "created_at": current_time,
            "expires_at": expires_at
        }
        
        await db.orders.insert_one(order)
        
        # Create notification for seller
        notification = {
            "user_id": seller_id,
            "title": "New Buy Request",
            "message": f"Someone wants to buy your item: {listing.get('title', 'Unknown item')}",
            "type": "buy_request",
            "is_read": False,
            "created_at": current_time.isoformat(),
            "id": str(uuid.uuid4()),
            "order_id": order_id,
            "listing_id": listing_id
        }
        
        await db.user_notifications.insert_one(notification)
        
        return {
            "message": "Buy request created successfully",
            "order_id": order_id,
            "expires_at": expires_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create buy request: {str(e)}")

@app.get("/api/orders/seller/{seller_id}")
async def get_seller_pending_orders(seller_id: str):
    """Get all pending buy requests for a seller"""
    try:
        # Find pending orders for this seller
        orders = await db.orders.find({
            "seller_id": seller_id,
            "status": "pending"
        }).sort("created_at", -1).to_list(length=None)
        
        # Enrich with listing and buyer information
        enriched_orders = []
        for order in orders:
            # Get listing details
            listing = await db.listings.find_one({"id": order["listing_id"]})
            if not listing:
                continue
                
            # Get buyer details
            buyer = await db.users.find_one({"id": order["buyer_id"]})
            buyer_info = {
                "id": buyer.get("id", ""),
                "username": buyer.get("username", "Unknown"),
                "full_name": buyer.get("full_name", ""),
                "email": buyer.get("email", "")
            } if buyer else {}
            
            enriched_order = {
                "id": order["id"],
                "status": order["status"],
                "created_at": order["created_at"].isoformat() if order.get("created_at") else "",
                "expires_at": order["expires_at"].isoformat() if order.get("expires_at") else "",
                "listing": {
                    "id": listing.get("id", ""),
                    "title": listing.get("title", ""),
                    "price": listing.get("price", 0),
                    "image": listing.get("image", "")
                },
                "buyer": buyer_info
            }
            enriched_orders.append(enriched_order)
        
        return enriched_orders
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get seller orders: {str(e)}")

@app.get("/api/orders/buyer/{buyer_id}")
async def get_buyer_orders(buyer_id: str):
    """Get all orders for a buyer (pending and completed)"""
    try:
        orders = await db.orders.find({
            "buyer_id": buyer_id
        }).sort("created_at", -1).to_list(length=None)
        
        # Enrich with listing and seller information
        enriched_orders = []
        for order in orders:
            # Get listing details
            listing = await db.listings.find_one({"id": order["listing_id"]})
            if not listing:
                continue
                
            # Get seller details
            seller = await db.users.find_one({"id": order["seller_id"]})
            seller_info = {
                "id": seller.get("id", ""),
                "username": seller.get("username", "Unknown"),
                "full_name": seller.get("full_name", ""),
                "email": seller.get("email", "") if order["status"] == "approved" else ""  # Only show contact after approval
            } if seller else {}
            
            enriched_order = {
                "id": order["id"],
                "status": order["status"],
                "created_at": order["created_at"].isoformat() if order.get("created_at") else "",
                "expires_at": order["expires_at"].isoformat() if order.get("expires_at") else "",
                "approved_at": order["approved_at"].isoformat() if order.get("approved_at") else "",
                "listing": {
                    "id": listing.get("id", ""),
                    "title": listing.get("title", ""),
                    "price": listing.get("price", 0),
                    "image": listing.get("image", "")
                },
                "seller": seller_info
            }
            enriched_orders.append(enriched_order)
        
        return enriched_orders
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get buyer orders: {str(e)}")

@app.put("/api/orders/{order_id}/approve")
async def approve_buy_request(order_id: str, approval_data: dict):
    """Approve a buy request"""
    try:
        seller_id = approval_data.get("seller_id")
        if not seller_id:
            raise HTTPException(status_code=400, detail="seller_id is required")
        
        # Find the order
        order = await db.orders.find_one({"id": order_id, "seller_id": seller_id, "status": "pending"})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found or not pending")
        
        # Check if order has expired
        if order.get("expires_at") and datetime.utcnow() > order["expires_at"]:
            # Mark as expired
            await db.orders.update_one(
                {"id": order_id},
                {"$set": {"status": "expired"}}
            )
            raise HTTPException(status_code=410, detail="Order has expired")
        
        current_time = datetime.utcnow()
        
        # Update order status
        await db.orders.update_one(
            {"id": order_id},
            {
                "$set": {
                    "status": "approved",
                    "approved_at": current_time
                }
            }
        )
        
        # Update listing status to sold
        await db.listings.update_one(
            {"id": order["listing_id"]},
            {"$set": {"status": "sold", "sold_at": current_time}}
        )
        
        # Create notification for buyer
        listing = await db.listings.find_one({"id": order["listing_id"]})
        notification = {
            "user_id": order["buyer_id"],
            "title": "Buy Request Approved!",
            "message": f"Your buy request for '{listing.get('title', 'Unknown item')}' has been approved!",
            "type": "buy_approved",
            "is_read": False,
            "created_at": current_time.isoformat(),
            "id": str(uuid.uuid4()),
            "order_id": order_id,
            "listing_id": order["listing_id"]
        }
        
        await db.user_notifications.insert_one(notification)
        
        # TODO: Trigger chat creation between buyer and seller
        
        return {"message": "Buy request approved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve buy request: {str(e)}")

@app.put("/api/orders/{order_id}/reject")
async def reject_buy_request(order_id: str, rejection_data: dict):
    """Reject a buy request"""
    try:
        seller_id = rejection_data.get("seller_id")
        if not seller_id:
            raise HTTPException(status_code=400, detail="seller_id is required")
        
        # Find the order
        order = await db.orders.find_one({"id": order_id, "seller_id": seller_id, "status": "pending"})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found or not pending")
        
        # Update order status
        await db.orders.update_one(
            {"id": order_id},
            {"$set": {"status": "rejected"}}
        )
        
        # Create notification for buyer
        listing = await db.listings.find_one({"id": order["listing_id"]})
        notification = {
            "user_id": order["buyer_id"],
            "title": "Buy Request Declined",
            "message": f"Your buy request for '{listing.get('title', 'Unknown item')}' has been declined.",
            "type": "buy_rejected",
            "is_read": False,
            "created_at": datetime.utcnow().isoformat(),
            "id": str(uuid.uuid4()),
            "order_id": order_id,
            "listing_id": order["listing_id"]
        }
        
        await db.user_notifications.insert_one(notification)
        
        return {"message": "Buy request rejected successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reject buy request: {str(e)}")

@app.put("/api/orders/{order_id}/cancel")
async def cancel_order(order_id: str, cancel_data: dict):
    """Cancel an order"""
    try:
        user_id = cancel_data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Find the order
        order = await db.orders.find_one({"id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Check if user is authorized to cancel (buyer or seller)
        if user_id not in [order.get("buyer_id"), order.get("seller_id")]:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this order")
        
        # Can only cancel pending or approved orders
        if order["status"] not in ["pending", "approved"]:
            raise HTTPException(status_code=400, detail="Order cannot be cancelled")
        
        # Update order status
        await db.orders.update_one(
            {"id": order_id},
            {"$set": {"status": "cancelled", "cancelled_at": datetime.utcnow()}}
        )
        
        # If order was approved, make listing available again
        if order["status"] == "approved":
            await db.listings.update_one(
                {"id": order["listing_id"]},
                {"$set": {"status": "active", "sold_at": None}}
            )
        
        return {"message": "Order cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")

@app.put("/api/orders/{order_id}/ship")
async def mark_order_shipped(order_id: str, ship_data: dict):
    """Mark order as shipped (seller action)"""
    try:
        user_id = ship_data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Find the order
        order = await db.orders.find_one({"id": order_id, "seller_id": user_id, "status": "approved"})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found or not approved")
        
        # Update order status
        await db.orders.update_one(
            {"id": order_id},
            {"$set": {"status": "shipped", "shipped_at": datetime.utcnow()}}
        )
        
        # Create notification for buyer
        listing = await db.listings.find_one({"id": order["listing_id"]})
        notification = {
            "user_id": order["buyer_id"],
            "title": "Order Shipped!",
            "message": f"Your order for '{listing.get('title', 'Unknown item')}' has been shipped!",
            "type": "order_shipped",
            "is_read": False,
            "created_at": datetime.utcnow()
        }
        
        await db.user_notifications.insert_one(notification)
        
        return {"message": "Order marked as shipped"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark order as shipped: {str(e)}")

@app.put("/api/orders/{order_id}/complete")
async def complete_order(order_id: str, complete_data: dict):
    """Complete order (buyer confirms receipt)"""
    try:
        user_id = complete_data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Find the order
        order = await db.orders.find_one({"id": order_id, "buyer_id": user_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found or not authorized")
        
        # Can complete from approved or shipped status
        if order["status"] not in ["approved", "shipped"]:
            raise HTTPException(status_code=400, detail="Order cannot be completed")
        
        # Update order status
        await db.orders.update_one(
            {"id": order_id},
            {"$set": {"status": "completed", "completed_at": datetime.utcnow()}}
        )
        
        # Create notification for seller
        listing = await db.listings.find_one({"id": order["listing_id"]})
        notification = {
            "user_id": order["seller_id"],
            "title": "Order Completed!",
            "message": f"Your sale of '{listing.get('title', 'Unknown item')}' has been completed!",
            "type": "order_completed",
            "is_read": False,
            "created_at": datetime.utcnow()
        }
        
        await db.user_notifications.insert_one(notification)
        
        return {"message": "Order completed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete order: {str(e)}")

@app.post("/api/orders/cleanup-expired")
async def cleanup_expired_orders():
    """Cleanup expired orders (can be called by a cron job)"""
    try:
        current_time = datetime.utcnow()
        
        # Find expired pending orders
        expired_orders = await db.orders.find({
            "status": "pending",
            "expires_at": {"$lt": current_time}
        }).to_list(length=None)
        
        updated_count = 0
        for order in expired_orders:
            # Update order status to expired
            await db.orders.update_one(
                {"id": order["id"]},
                {"$set": {"status": "expired"}}
            )
            
            # Notify buyer about expiration
            listing = await db.listings.find_one({"id": order["listing_id"]})
            notification = {
                "user_id": order["buyer_id"],
                "title": "Buy Request Expired",
                "message": f"Your buy request for '{listing.get('title', 'Unknown item')}' has expired after 48 hours.",
                "type": "buy_expired",
                "is_read": False,
                "created_at": current_time.isoformat(),
                "id": str(uuid.uuid4()),
                "order_id": order["id"],
                "listing_id": order["listing_id"]
            }
            
            await db.user_notifications.insert_one(notification)
            updated_count += 1
        
        return {"message": f"Cleaned up {updated_count} expired orders"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup expired orders: {str(e)}")

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
        
        # Validate required columns (add_info is optional)
        required_columns = ['cat_id', 'name', 'ceramic_weight', 'pt_ppm', 'pd_ppm', 'rh_ppm']
        optional_columns = ['add_info']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(status_code=400, detail=f"Missing required columns: {missing_columns}. Optional columns: {optional_columns}")
        
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