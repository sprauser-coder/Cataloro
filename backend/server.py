"""
CATALORO - Marketplace Backend Server
Scalable FastAPI backend with MongoDB integration
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import uuid
from datetime import datetime
from typing import List, Optional
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
    id: str = None
    title: str
    description: str
    price: float
    category: str
    seller_id: str
    status: str = "active"
    created_at: datetime = None
    images: List[str] = []

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
        user = {
            "id": user_id,
            "username": credentials.get("username", "demo_user"),
            "email": credentials["email"],
            "full_name": "Demo User",
            "role": "admin" if credentials["email"] == "admin@cataloro.com" else "user",
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        await db.users.insert_one(user)
    
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

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)