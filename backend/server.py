from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import shutil
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create uploads directory for logo files
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount static files for serving uploaded logos
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Also serve uploads through API route for proxy compatibility
# api_router.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="api_uploads")

# Alternative: Add API endpoint for serving images
from fastapi.responses import FileResponse

@api_router.get("/uploads/{filename}")
async def serve_upload_file(filename: str):
    """Serve uploaded files through API route for proxy compatibility"""
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET', 'your-secret-key')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours for better user experience

security = HTTPBearer()

# Enums
class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    BOTH = "both"
    ADMIN = "admin"

class ListingType(str, Enum):
    FIXED_PRICE = "fixed_price"
    AUCTION = "auction"

class ListingStatus(str, Enum):
    ACTIVE = "active"
    SOLD = "sold"
    EXPIRED = "expired"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(default="")  # Auto-generated friendly ID like U00001
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    address: Optional[str] = None
    bio: Optional[str] = None  # Phase 3A: User biography
    location: Optional[str] = None  # Phase 3A: User location
    website: Optional[str] = None
    rating: float = Field(default=0.0)
    total_reviews: int = Field(default=0)
    is_blocked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None  # Phase 3A: Profile update tracking
    is_active: bool = Field(default=True)
    is_business: Optional[bool] = Field(default=False)  # Business profile fields
    company_name: Optional[str] = None
    country: Optional[str] = None
    vat_number: Optional[str] = None
    # Enhanced profile fields
    social_links: Optional[Dict[str, str]] = Field(default_factory=dict)
    preferences: Optional[Dict[str, Any]] = Field(default_factory=lambda: {
        "email_notifications": True,
        "sms_notifications": False,
        "marketing_emails": True,
        "push_notifications": True,
        "theme": "light",
        "language": "en",
        "currency": "EUR",
        "timezone": "Europe/London"
    })
    verification: Optional[Dict[str, bool]] = Field(default_factory=lambda: {
        "email_verified": False,
        "phone_verified": False,
        "identity_verified": False,
        "business_verified": False
    })
    # Statistics tracking
    profile_views: int = Field(default=0)
    trust_score: int = Field(default=50)  # 0-100 scale
    account_level: str = Field(default="Bronze")  # Bronze, Silver, Gold, Platinum

class UserActivity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    activity_type: str  # 'listing_created', 'order_completed', 'review_received', etc.
    title: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)  # Additional data
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserStats(BaseModel):
    user_id: str
    total_orders: int = Field(default=0)
    total_listings: int = Field(default=0)
    total_spent: float = Field(default=0.0)
    total_earned: float = Field(default=0.0)
    avg_rating: float = Field(default=0.0)
    total_reviews: int = Field(default=0)
    successful_transactions: int = Field(default=0)
    response_rate: float = Field(default=0.0)  # Percentage
    avg_response_time: float = Field(default=0.0)  # Hours
    badges_earned: int = Field(default=0)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Review(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reviewer_id: str
    reviewed_user_id: str
    order_id: Optional[str] = None
    listing_id: Optional[str] = None
    rating: int = Field(ge=1, le=5)  # 1-5 stars
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    receiver_id: str
    subject: Optional[str] = None
    message: str
    read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None
    preferences: Optional[Dict[str, Any]] = None

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    address: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class ProductListing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str
    title: str
    description: str
    category: str
    images: List[str] = Field(default_factory=list)
    listing_type: ListingType
    price: Optional[float] = None  # For fixed price
    starting_bid: Optional[float] = None  # For auctions
    current_bid: Optional[float] = None
    buyout_price: Optional[float] = None  # Optional buyout for auctions
    condition: str
    quantity: int = Field(default=1)
    location: str
    shipping_cost: Optional[float] = None
    auction_end_time: Optional[datetime] = None
    status: ListingStatus = Field(default=ListingStatus.ACTIVE)
    views: int = Field(default=0)
    watchers: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ListingCreate(BaseModel):
    title: str
    description: str
    category: str
    images: List[str] = Field(default_factory=list)
    listing_type: ListingType
    price: Optional[float] = None
    starting_bid: Optional[float] = None
    buyout_price: Optional[float] = None
    condition: str
    quantity: int = Field(default=1)
    location: str
    shipping_cost: Optional[float] = None
    auction_duration_hours: Optional[int] = None

class Bid(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    listing_id: str
    bidder_id: str
    amount: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BidCreate(BaseModel):
    listing_id: str
    amount: float

class CartItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    listing_id: str
    quantity: int = Field(default=1)
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CartItemCreate(BaseModel):
    listing_id: str
    quantity: int = Field(default=1)

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    buyer_id: str
    seller_id: str
    listing_id: str
    quantity: int
    total_amount: float
    shipping_address: str
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrderCreate(BaseModel):
    listing_id: str
    quantity: int
    shipping_address: str

class Review(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reviewer_id: str
    reviewed_user_id: str
    order_id: str
    rating: int  # 1-5
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReviewCreate(BaseModel):
    reviewed_user_id: str
    order_id: str
    rating: int
    comment: Optional[str] = None

# Helper functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=8)  # 8 hours for better UX
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check if user is blocked
    if user.get('is_blocked', False):
        raise HTTPException(status_code=403, detail="Account has been blocked")
    
    return User(**user)

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def generate_user_id():
    """Generate next sequential user ID"""
    # Find the highest user_id number
    users = await db.users.find({"user_id": {"$regex": "^U\\d+$"}}).to_list(length=None)
    
    if not users:
        return "U00001"
    
    # Extract numbers from user_ids and find the maximum
    max_num = 0
    for user in users:
        user_id = user.get('user_id', '')
        if user_id.startswith('U') and user_id[1:].isdigit():
            num = int(user_id[1:])
            max_num = max(max_num, num)
    
    # Generate next user ID
    next_num = max_num + 1
    return f"U{next_num:05d}"

def prepare_for_mongo(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item, dict):
        # Remove MongoDB _id field if present
        if '_id' in item:
            del item['_id']
            
        for key, value in item.items():
            if isinstance(value, str) and 'T' in value and value.endswith('Z'):
                try:
                    item[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    pass
    return item

# Auth Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"$or": [{"email": user_data.email}, {"username": user_data.username}]})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email or username already exists")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Generate user ID
    user_id = await generate_user_id()
    
    # Create user
    user_dict = user_data.dict()
    del user_dict['password']
    user_dict['user_id'] = user_id
    user = User(**user_dict)
    
    user_doc = prepare_for_mongo(user.dict())
    user_doc['password'] = hashed_password
    
    await db.users.insert_one(user_doc)
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    
    return Token(access_token=access_token, token_type="bearer", user=user)

@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    user_doc = await db.users.find_one({"email": credentials.email})
    if not user_doc or not verify_password(credentials.password, user_doc['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = User(**parse_from_mongo(user_doc))
    access_token = create_access_token(data={"sub": user.id})
    
    return Token(access_token=access_token, token_type="bearer", user=user)

# Listing Routes - Count endpoint MUST come first before parameterized routes
@api_router.get("/listings/count")
async def get_listings_count(
    category: Optional[str] = None,
    search: Optional[str] = None,
    listing_type: Optional[ListingType] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    condition: Optional[str] = None,
    region: Optional[str] = None
):
    """Get total count of active listings matching filters"""
    query = {"status": ListingStatus.ACTIVE}
    
    # Apply same filters as get_listings
    if category:
        query["category"] = category
    if listing_type:
        query["listing_type"] = listing_type
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    if condition:
        query["condition"] = condition
    if region:
        query["region"] = region
    
    # Price filtering - fix the query structure
    if min_price is not None or max_price is not None:
        price_query = {}
        if min_price is not None:
            price_query["$gte"] = min_price
        if max_price is not None:
            price_query["$lte"] = max_price
        
        # Don't overwrite existing $or queries
        if "$or" in query:
            # Add price conditions to existing $or
            existing_or = query["$or"]
            query["$and"] = [
                {"$or": existing_or},
                {"$or": [
                    {"price": price_query, "listing_type": "fixed_price"},
                    {"current_bid": price_query, "listing_type": "auction"}
                ]}
            ]
            del query["$or"]
        else:
            query["$or"] = [
                {"price": price_query, "listing_type": "fixed_price"},
                {"current_bid": price_query, "listing_type": "auction"}
            ]
    
    try:
        count = await db.listings.count_documents(query)
        return {"total_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error counting listings: {str(e)}")

@api_router.post("/listings", response_model=ProductListing)
async def create_listing(listing_data: ListingCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SELLER, UserRole.BOTH, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only sellers can create listings")
    
    listing_dict = listing_data.dict()
    listing_dict['seller_id'] = current_user.id
    
    # Set auction end time if it's an auction
    if listing_data.listing_type == ListingType.AUCTION and listing_data.auction_duration_hours:
        listing_dict['auction_end_time'] = datetime.now(timezone.utc) + timedelta(hours=listing_data.auction_duration_hours)
        listing_dict['current_bid'] = listing_data.starting_bid
    
    listing = ProductListing(**listing_dict)
    listing_doc = prepare_for_mongo(listing.dict())
    
    await db.listings.insert_one(listing_doc)
    return listing

@api_router.get("/listings", response_model=List[ProductListing])
async def get_listings(
    category: Optional[str] = None,
    search: Optional[str] = None,
    listing_type: Optional[ListingType] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    # Phase 3D: Enhanced filtering and sorting
    sort_by: Optional[str] = "created_desc",
    condition: Optional[str] = None,
    region: Optional[str] = None,
    max_distance: Optional[float] = None,
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None,
    limit: int = 20,
    skip: int = 0
):
    """Get listings with enhanced filtering and sorting (Phase 3D)"""
    query = {"status": ListingStatus.ACTIVE}
    
    # Existing filters
    if category:
        query["category"] = category
    if listing_type:
        query["listing_type"] = listing_type
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Phase 3D: New filters
    if condition:
        query["condition"] = condition
        
    if region:
        query["region"] = region
    
    # Price filtering (enhanced)
    if min_price is not None or max_price is not None:
        price_query = {}
        if min_price is not None:
            price_query["$gte"] = min_price
        if max_price is not None:
            price_query["$lte"] = max_price
        
        # Apply to both fixed price and auction current prices
        query["$or"] = [
            {"price": price_query, "listing_type": "fixed_price"},
            {"current_bid": price_query, "listing_type": "auction"}
        ]
    
    # Phase 3D: Sorting options
    sort_options = {
        "created_desc": [("created_at", -1)],
        "created_asc": [("created_at", 1)],
        "price_high": [("price", -1), ("current_bid", -1)],
        "price_low": [("price", 1), ("current_bid", 1)],
        "views_desc": [("views", -1)],
        "title_asc": [("title", 1)],
    }
    
    sort_criteria = sort_options.get(sort_by, [("created_at", -1)])
    
    # Execute query with sorting
    cursor = db.listings.find(query)
    
    # Apply sorting
    for field, direction in sort_criteria:
        cursor = cursor.sort(field, direction)
    
    # Apply pagination
    cursor = cursor.skip(skip).limit(limit)
    
    # Convert results
    listings = []
    async for listing_doc in cursor:
        listing_data = parse_from_mongo(listing_doc)
        
        # Phase 3D: Distance filtering (future infrastructure)
        if max_distance and user_lat and user_lng and listing_data.get("latitude") and listing_data.get("longitude"):
            # Calculate distance using Haversine formula
            import math
            
            lat1, lng1 = math.radians(user_lat), math.radians(user_lng)
            lat2, lng2 = math.radians(listing_data["latitude"]), math.radians(listing_data["longitude"])
            
            dlat, dlng = lat2 - lat1, lng2 - lng1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
            distance = 2 * math.asin(math.sqrt(a)) * 6371  # Earth radius in km
            
            if distance > max_distance:
                continue  # Skip this listing if it's too far
                
        # Add seller information
        seller = await db.users.find_one({"id": listing_data["seller_id"]})
        if seller:
            listing_data["seller_name"] = seller.get("full_name", "Unknown")
            listing_data["seller_username"] = seller.get("username", "unknown")
        
        listings.append(listing_data)
    
    return [ProductListing(**listing) for listing in listings]

@api_router.get("/listings/my-listings")
async def get_my_listings(current_user: User = Depends(get_current_user)):
    """Get current user's listings"""
    try:
        # Find listings created by current user
        cursor = db.listings.find({"seller_id": current_user.id})
        listings = []
        
        async for listing_doc in cursor:
            listing_data = parse_from_mongo(listing_doc)
            
            # Add seller information
            listing_data["seller_name"] = current_user.full_name
            listing_data["seller_username"] = current_user.username
            
            listings.append(listing_data)
        
        # Sort by creation date (newest first)
        listings.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        
        return listings
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user listings: {str(e)}")



# Bidding Routes
@api_router.post("/bids", response_model=Bid)
async def place_bid(bid_data: BidCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.BUYER, UserRole.BOTH]:
        raise HTTPException(status_code=403, detail="Only buyers can place bids")
    
    listing = await db.listings.find_one({"id": bid_data.listing_id})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    listing_obj = ProductListing(**parse_from_mongo(listing))
    
    if listing_obj.listing_type != ListingType.AUCTION:
        raise HTTPException(status_code=400, detail="This is not an auction listing")
    
    if listing_obj.auction_end_time and datetime.now(timezone.utc) > listing_obj.auction_end_time:
        raise HTTPException(status_code=400, detail="Auction has ended")
    
    if listing_obj.current_bid and bid_data.amount <= listing_obj.current_bid:
        raise HTTPException(status_code=400, detail="Bid must be higher than current bid")
    
    if not listing_obj.current_bid and bid_data.amount < listing_obj.starting_bid:
        raise HTTPException(status_code=400, detail="Bid must be at least the starting bid")
    
    # Create bid
    bid_dict = bid_data.dict()
    bid_dict['bidder_id'] = current_user.id
    bid = Bid(**bid_dict)
    
    # Update listing with new current bid
    await db.listings.update_one(
        {"id": bid_data.listing_id},
        {"$set": {"current_bid": bid_data.amount}}
    )
    
    bid_doc = prepare_for_mongo(bid.dict())
    await db.bids.insert_one(bid_doc)
    
    return bid

@api_router.get("/listings/{listing_id}/bids", response_model=List[Bid])
async def get_listing_bids(listing_id: str):
    bids = await db.bids.find({"listing_id": listing_id}).sort("timestamp", -1).to_list(length=None)
    return [Bid(**parse_from_mongo(bid)) for bid in bids]

# Cart Routes
@api_router.post("/cart", response_model=CartItem)
async def add_to_cart(item_data: CartItemCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.BUYER, UserRole.BOTH]:
        raise HTTPException(status_code=403, detail="Only buyers can add items to cart")
    
    listing = await db.listings.find_one({"id": item_data.listing_id})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    listing_obj = ProductListing(**parse_from_mongo(listing))
    if listing_obj.listing_type != ListingType.FIXED_PRICE:
        raise HTTPException(status_code=400, detail="Only fixed-price items can be added to cart")
    
    # Check if item already in cart
    existing_item = await db.cart_items.find_one({"user_id": current_user.id, "listing_id": item_data.listing_id})
    if existing_item:
        # Update quantity
        new_quantity = existing_item['quantity'] + item_data.quantity
        await db.cart_items.update_one(
            {"id": existing_item['id']},
            {"$set": {"quantity": new_quantity}}
        )
        updated_item = await db.cart_items.find_one({"id": existing_item['id']})
        return CartItem(**parse_from_mongo(updated_item))
    
    # Create new cart item
    item_dict = item_data.dict()
    item_dict['user_id'] = current_user.id
    cart_item = CartItem(**item_dict)
    
    cart_doc = prepare_for_mongo(cart_item.dict())
    await db.cart_items.insert_one(cart_doc)
    
    return cart_item

@api_router.get("/cart", response_model=List[Dict[str, Any]])
async def get_cart(current_user: User = Depends(get_current_user)):
    cart_items = await db.cart_items.find({"user_id": current_user.id}).to_list(length=None)
    
    result = []
    for item in cart_items:
        cart_item = CartItem(**parse_from_mongo(item))
        listing = await db.listings.find_one({"id": cart_item.listing_id})
        if listing:
            listing_obj = ProductListing(**parse_from_mongo(listing))
            result.append({
                "cart_item": cart_item,
                "listing": listing_obj
            })
    
    return result

@api_router.delete("/cart/{item_id}")
async def remove_from_cart(item_id: str, current_user: User = Depends(get_current_user)):
    result = await db.cart_items.delete_one({"id": item_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Item removed from cart"}

# Individual Listing Route - MUST come after all specific routes
@api_router.get("/listings/{listing_id}", response_model=ProductListing)
async def get_listing(listing_id: str):
    """Get a specific listing by ID"""
    listing = await db.listings.find_one({"id": listing_id})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Increment views
    await db.listings.update_one({"id": listing_id}, {"$inc": {"views": 1}})
    
    return ProductListing(**parse_from_mongo(listing))

# Order Routes
@api_router.post("/orders", response_model=Order)
async def create_order(order_data: OrderCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.BUYER, UserRole.BOTH]:
        raise HTTPException(status_code=403, detail="Only buyers can create orders")
    
    listing = await db.listings.find_one({"id": order_data.listing_id})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    listing_obj = ProductListing(**parse_from_mongo(listing))
    
    if listing_obj.listing_type == ListingType.FIXED_PRICE:
        total_amount = listing_obj.price * order_data.quantity
    else:
        # For auction, can only buy if there's a buyout price
        if not listing_obj.buyout_price:
            raise HTTPException(status_code=400, detail="This auction doesn't have a buyout option")
        total_amount = listing_obj.buyout_price * order_data.quantity
    
    # Create order with pending status (Phase 3C: Order Approval Workflow)
    order_dict = order_data.dict()
    order_dict['buyer_id'] = current_user.id
    order_dict['seller_id'] = listing_obj.seller_id
    order_dict['total_amount'] = total_amount
    order_dict['status'] = OrderStatus.PENDING  # Start as pending for seller approval
    
    order = Order(**order_dict)
    order_doc = prepare_for_mongo(order.dict())
    
    await db.orders.insert_one(order_doc)
    
    # Phase 3C: Send notification to seller for order approval
    seller = await db.users.find_one({"id": listing_obj.seller_id})
    if seller:
        await create_notification(
            user_id=listing_obj.seller_id,
            notification_type=NotificationType.ORDER_RECEIVED,
            title="New Order Received!",
            message=f"{current_user.full_name} wants to buy your '{listing_obj.title}' for €{total_amount:.2f}",
            data={
                "order_id": order.id,
                "listing_id": order_data.listing_id,
                "buyer_name": current_user.full_name,
                "buyer_id": current_user.id,
                "amount": total_amount,
                "quantity": order_data.quantity
            }
        )
    
    # Don't update listing status yet - wait for seller approval
    # Remove from cart if exists
    await db.cart_items.delete_many({"user_id": current_user.id, "listing_id": order_data.listing_id})
    
    return order

# Phase 3C: Order Approval Endpoints
@api_router.put("/orders/{order_id}/approve")
async def approve_order(order_id: str, current_user: User = Depends(get_current_user)):
    """Seller approves an order"""
    try:
        # Find the order
        order_doc = await db.orders.find_one({"id": order_id})
        if not order_doc:
            raise HTTPException(status_code=404, detail="Order not found")
            
        order = Order(**parse_from_mongo(order_doc))
        
        # Check if current user is the seller
        if order.seller_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only the seller can approve this order")
            
        # Check if order is in pending status
        if order.status != OrderStatus.PENDING:
            raise HTTPException(status_code=400, detail="Order is not pending approval")
            
        # Update order status to completed
        await db.orders.update_one(
            {"id": order_id},
            {"$set": {"status": OrderStatus.COMPLETED, "updated_at": datetime.now(timezone.utc)}}
        )
        
        # Update listing status to sold and reduce quantity
        listing = await db.listings.find_one({"id": order.listing_id})
        if listing:
            new_quantity = max(0, listing.get("quantity", 0) - order.quantity)
            update_data = {"quantity": new_quantity, "updated_at": datetime.now(timezone.utc)}
            
            if new_quantity == 0:
                update_data["status"] = ListingStatus.SOLD
                
            await db.listings.update_one(
                {"id": order.listing_id},
                {"$set": update_data}
            )
        
        # Send notification to buyer
        await create_notification(
            user_id=order.buyer_id,
            notification_type=NotificationType.ORDER_APPROVED,
            title="Order Approved!",
            message=f"Your order for '{listing.get('title', 'item')}' has been approved by the seller.",
            data={
                "order_id": order_id,
                "listing_id": order.listing_id,
                "seller_name": current_user.full_name,
                "amount": order.total_amount
            }
        )
        
        return {"message": "Order approved successfully", "order_id": order_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve order: {str(e)}")

@api_router.put("/orders/{order_id}/reject")
async def reject_order(
    order_id: str, 
    rejection_reason: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Seller rejects an order"""
    try:
        # Find the order
        order_doc = await db.orders.find_one({"id": order_id})
        if not order_doc:
            raise HTTPException(status_code=404, detail="Order not found")
            
        order = Order(**parse_from_mongo(order_doc))
        
        # Check if current user is the seller
        if order.seller_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only the seller can reject this order")
            
        # Check if order is in pending status
        if order.status != OrderStatus.PENDING:
            raise HTTPException(status_code=400, detail="Order is not pending approval")
            
        # Update order status to cancelled
        await db.orders.update_one(
            {"id": order_id},
            {
                "$set": {
                    "status": OrderStatus.CANCELLED,
                    "rejection_reason": rejection_reason or "Seller rejected the order",
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Get listing info for notification
        listing = await db.listings.find_one({"id": order.listing_id})
        
        # Send notification to buyer
        await create_notification(
            user_id=order.buyer_id,
            notification_type=NotificationType.ORDER_REJECTED,
            title="Order Rejected",
            message=f"Your order for '{listing.get('title', 'item')}' was rejected by the seller. Reason: {rejection_reason or 'No reason provided'}",
            data={
                "order_id": order_id,
                "listing_id": order.listing_id,
                "seller_name": current_user.full_name,
                "reason": rejection_reason
            }
        )
        
        return {"message": "Order rejected successfully", "order_id": order_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reject order: {str(e)}")

@api_router.get("/orders", response_model=List[Dict[str, Any]])
async def get_user_orders(current_user: User = Depends(get_current_user)):
    orders = await db.orders.find({
        "$or": [
            {"buyer_id": current_user.id},
            {"seller_id": current_user.id}
        ]
    }).sort("created_at", -1).to_list(length=None)
    
    result = []
    for order_doc in orders:
        order = Order(**parse_from_mongo(order_doc))
        listing = await db.listings.find_one({"id": order.listing_id})
        buyer = await db.users.find_one({"id": order.buyer_id})
        seller = await db.users.find_one({"id": order.seller_id})
        
        result.append({
            "order": order,
            "listing": ProductListing(**parse_from_mongo(listing)) if listing else None,
            "buyer": User(**parse_from_mongo(buyer)) if buyer else None,
            "seller": User(**parse_from_mongo(seller)) if seller else None
        })
    
    return result

# Review Routes
@api_router.post("/reviews", response_model=Review)
async def create_review(review_data: ReviewCreate, current_user: User = Depends(get_current_user)):
    # Verify order exists and user is part of it
    order = await db.orders.find_one({"id": review_data.order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order_obj = Order(**parse_from_mongo(order))
    if current_user.id not in [order_obj.buyer_id, order_obj.seller_id]:
        raise HTTPException(status_code=403, detail="You can only review orders you're part of")
    
    # Create review
    review_dict = review_data.dict()
    review_dict['reviewer_id'] = current_user.id
    review = Review(**review_dict)
    
    review_doc = prepare_for_mongo(review.dict())
    await db.reviews.insert_one(review_doc)
    
    # Update user rating
    user_reviews = await db.reviews.find({"reviewed_user_id": review_data.reviewed_user_id}).to_list(length=None)
    avg_rating = sum(r['rating'] for r in user_reviews) / len(user_reviews)
    
    await db.users.update_one(
        {"id": review_data.reviewed_user_id},
        {"$set": {"rating": avg_rating, "total_reviews": len(user_reviews)}}
    )
    
    return review

@api_router.get("/users/{user_id}/reviews", response_model=List[Dict[str, Any]])
async def get_user_reviews(user_id: str):
    reviews = await db.reviews.find({"reviewed_user_id": user_id}).sort("created_at", -1).to_list(length=None)
    
    result = []
    for review_doc in reviews:
        review = Review(**parse_from_mongo(review_doc))
        reviewer = await db.users.find_one({"id": review.reviewer_id})
        result.append({
            "review": review,
            "reviewer": User(**parse_from_mongo(reviewer)) if reviewer else None
        })
    
    return result

# Utility Routes
@api_router.get("/categories")
async def get_categories():
    return [
        "Electronics", "Fashion", "Home & Garden", "Sports", "Books",
        "Automotive", "Health & Beauty", "Toys", "Art & Collectibles", "Other"
    ]



@api_router.get("/")
async def root():
    return {"message": "Marketplace API", "version": "bulk-test-v1"}

@api_router.get("/test-bulk-endpoints")
async def test_bulk_endpoints():
    return {"message": "Bulk endpoints test", "timestamp": datetime.now().isoformat()}

# Favorites System (replaces cart)
@api_router.post("/favorites")
async def add_to_favorites(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Add item to user's favorites"""
    listing_id = request.get("listing_id")
    
    # Check if listing exists and is active
    listing = await db.listings.find_one({"id": listing_id, "status": "active"})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found or inactive")
    
    # Check if already in favorites
    existing = await db.favorites.find_one({
        "user_id": current_user.id,
        "listing_id": listing_id
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Item already in favorites")
    
    # Add to favorites
    favorite_data = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "listing_id": listing_id,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.favorites.insert_one(prepare_for_mongo(favorite_data))
    
    return {"message": "Added to favorites", "favorite_id": favorite_data["id"]}

@api_router.get("/favorites")
async def get_user_favorites(current_user: User = Depends(get_current_user)):
    """Get user's favorite items (only active listings)"""
    favorites = await db.favorites.find({"user_id": current_user.id}).to_list(length=None)
    
    result = []
    for favorite in favorites:
        # Get the listing details
        listing = await db.listings.find_one({"id": favorite["listing_id"]})
        
        # Only include favorites for active listings
        if listing and listing.get("status") == "active":
            result.append({
                "favorite_id": favorite["id"],
                "listing": ProductListing(**parse_from_mongo(listing)),
                "added_at": favorite["created_at"]
            })
    
    return result

@api_router.delete("/favorites/{favorite_id}")
async def remove_from_favorites(
    favorite_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove item from favorites"""
    result = await db.favorites.delete_one({
        "id": favorite_id,
        "user_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    return {"message": "Removed from favorites"}

@api_router.delete("/admin/navigation/test-pages")
async def delete_test_pages(admin: User = Depends(get_admin_user)):
    """Delete all test pages from navigation"""
    # Delete navigation items that contain test-related keywords
    result = await db.navigation.delete_many({
        "$or": [
            {"label": {"$regex": "test", "$options": "i"}},
            {"label": {"$regex": "preview", "$options": "i"}},
            {"label": {"$regex": "🚀", "$options": "i"}},
            {"url": {"$regex": "test", "$options": "i"}}
        ]
    })
    
    # Also delete test pages from pages collection
    pages_result = await db.pages.delete_many({
        "$or": [
            {"title": {"$regex": "test", "$options": "i"}},
            {"title": {"$regex": "preview", "$options": "i"}},
            {"title": {"$regex": "🚀", "$options": "i"}},
            {"slug": {"$regex": "test", "$options": "i"}}
        ]
    })
    
    return {
        "message": f"Deleted {result.deleted_count} test navigation items and {pages_result.deleted_count} test pages",
        "navigation_deleted": result.deleted_count,
        "pages_deleted": pages_result.deleted_count
    }

@api_router.get("/admin/navigation")
async def get_navigation_items(admin: User = Depends(get_admin_user)):
    """Get all navigation items"""
    nav_items = await db.navigation.find({}).to_list(length=None)
    return [parse_from_mongo(item) for item in nav_items]

@api_router.delete("/admin/navigation/{nav_id}")
async def delete_navigation_item(nav_id: str, admin: User = Depends(get_admin_user)):
    """Delete a navigation item"""
    result = await db.navigation.delete_one({"id": nav_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Navigation item not found")
    
    return {"message": "Navigation item deleted successfully"}

# CMS Models
class SiteSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    site_name: str = Field(default="Cataloro")
    site_tagline: str = Field(default="Your trusted marketplace for amazing deals")
    hero_title: str = Field(default="Discover Amazing Deals")
    hero_subtitle: str = Field(default="Buy and sell with confidence on Cataloro - your trusted marketplace for amazing deals")
    
    # Logo Settings
    header_logo_url: Optional[str] = Field(default=None)  # Main header logo
    header_logo_alt: str = Field(default="Cataloro Logo")  # Alt text for header logo
    header_logo_size: str = Field(default="h-8")  # Logo size class (h-6, h-8, h-10, etc.)
    
    # Color Settings
    primary_color: str = Field(default="#6366f1")  # indigo-600
    secondary_color: str = Field(default="#8b5cf6")  # purple-600
    accent_color: str = Field(default="#ef4444")  # red-500
    background_color: str = Field(default="#f8fafc")  # slate-50
    
    # Hero Section Customization
    hero_background_type: str = Field(default="gradient")  # "solid", "gradient"
    hero_background_color: str = Field(default="#6366f1")  # Primary color
    hero_background_gradient_start: str = Field(default="#667eea")
    hero_background_gradient_end: str = Field(default="#764ba2")
    hero_text_color: str = Field(default="#ffffff")
    hero_subtitle_color: str = Field(default="#f1f5f9")  # Light gray
    hero_height: str = Field(default="600px")  # Hero section height
    
    # Typography Settings
    global_font_family: str = Field(default="Inter")  # "Inter", "Roboto", "Open Sans", "Poppins", etc.
    h1_size: str = Field(default="3rem")  # 48px
    h2_size: str = Field(default="2.25rem")  # 36px  
    h3_size: str = Field(default="1.875rem")  # 30px
    h4_size: str = Field(default="1.5rem")  # 24px
    h5_size: str = Field(default="1.25rem")  # 20px
    h1_color: str = Field(default="#1f2937")  # gray-800
    h2_color: str = Field(default="#374151")  # gray-700
    h3_color: str = Field(default="#4b5563")  # gray-600
    h4_color: str = Field(default="#6b7280")  # gray-500
    h5_color: str = Field(default="#9ca3af")  # gray-400
    
    # Phase 2: New Color Settings
    font_color: str = Field(default="#1f2937")  # Default text color
    link_color: str = Field(default="#3b82f6")  # Default link color (blue-500)
    link_hover_color: str = Field(default="#1d4ed8")  # Default link hover color (blue-700)
    
    # Phase 2: Hero Section Enhancements
    hero_image_url: Optional[str] = Field(default=None)  # Image above hero title
    hero_background_image_url: Optional[str] = Field(default=None)  # Background image
    hero_background_size: str = Field(default="cover")  # cover, contain, auto
    
    # Feature Toggles
    show_hero_section: bool = Field(default=True)
    show_categories: bool = Field(default=True)
    show_auctions: bool = Field(default=True)
    show_buy_now: bool = Field(default=True)
    allow_user_registration: bool = Field(default=True)
    enable_reviews: bool = Field(default=True)
    enable_cart: bool = Field(default=True)
    max_images_per_listing: int = Field(default=5)
    auto_add_pages_to_menu: bool = Field(default=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PageContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    page_slug: str  # 'home', 'about', 'terms', etc.
    title: str
    content: str  # HTML content
    is_published: bool = Field(default=True)
    meta_description: str = Field(default="")
    custom_css: str = Field(default="")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NavigationItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    label: str
    url: str
    order: int = Field(default=0)
    is_visible: bool = Field(default=True)
    parent_id: Optional[str] = None
    target: str = Field(default="_self")  # _self, _blank

class AdminStats(BaseModel):
    total_users: int
    active_users: int
    blocked_users: int
    total_listings: int
    active_listings: int
    total_orders: int
    total_revenue: float

class SEOSettings(BaseModel):
    site_title: str = Field(default="Cataloro - Your Trusted Marketplace")
    meta_description: str = Field(default="Buy and sell with confidence on Cataloro marketplace")
    meta_keywords: str = Field(default="marketplace, buy, sell, ecommerce, cataloro")
    favicon_url: str = Field(default="/favicon.ico")
    og_title: str = Field(default="Cataloro Marketplace")
    og_description: str = Field(default="Your trusted marketplace for amazing deals")
    og_image: str = Field(default="")
    twitter_card: str = Field(default="summary_large_image")
    robots_txt: str = Field(default="User-agent: *\nAllow: /")
    canonical_url: str = Field(default="")
    structured_data: str = Field(default='{"@context": "https://schema.org", "@type": "Organization", "name": "Cataloro", "description": "Your trusted marketplace"}')
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserManagement(BaseModel):
    id: str
    user_id: str
    email: str
    username: str
    full_name: str
    role: str
    is_blocked: bool
    created_at: datetime
    total_orders: Optional[int] = 0
    total_listings: Optional[int] = 0

class ListingManagement(BaseModel):
    id: str
    title: str
    seller_id: str
    seller_name: str
    price: Optional[float]
    status: str
    created_at: datetime
    views: int
    category: str

# Admin Analytics Endpoints
@api_router.get("/admin/stats", response_model=AdminStats)
async def get_admin_stats(admin: User = Depends(get_admin_user)):
    """Get platform statistics"""
    # Count users
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"is_blocked": False})
    blocked_users = await db.users.count_documents({"is_blocked": True})
    
    # Count listings
    total_listings = await db.listings.count_documents({})
    active_listings = await db.listings.count_documents({"status": "active"})
    
    # Count orders and revenue
    total_orders = await db.orders.count_documents({})
    orders = await db.orders.find({}).to_list(length=None)
    total_revenue = sum(order.get('total_amount', 0) for order in orders)
    
    return AdminStats(
        total_users=total_users,
        active_users=active_users,
        blocked_users=blocked_users,
        total_listings=total_listings,
        active_listings=active_listings,
        total_orders=total_orders,
        total_revenue=total_revenue
    )

# Admin User Management
@api_router.get("/admin/users", response_model=List[UserManagement])
async def get_all_users(admin: User = Depends(get_admin_user)):
    """Get all users for admin management"""
    users = await db.users.find({}).to_list(length=None)
    
    result = []
    for user_doc in users:
        user = User(**parse_from_mongo(user_doc))
        
        # Count user's orders and listings
        orders_count = await db.orders.count_documents({"buyer_id": user.id})
        listings_count = await db.listings.count_documents({"seller_id": user.id})
        
        result.append(UserManagement(
            id=user.id,
            user_id=user.user_id or "Not Generated",
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            is_blocked=user.is_blocked,
            created_at=user.created_at,
            total_orders=orders_count,
            total_listings=listings_count
        ))
    
    return result

@api_router.put("/admin/users/{user_id}/block")
async def block_user(user_id: str, admin: User = Depends(get_admin_user)):
    """Block a user"""
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"is_blocked": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User blocked successfully"}

@api_router.put("/admin/users/{user_id}/unblock")
async def unblock_user(user_id: str, admin: User = Depends(get_admin_user)):
    """Unblock a user"""
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"is_blocked": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User unblocked successfully"}

@api_router.put("/admin/users/{user_id}/reset-password")
async def reset_user_password(user_id: str, admin: User = Depends(get_admin_user)):
    """Reset user password to a temporary password"""
    import secrets
    import string
    
    # Generate temporary password
    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    hashed_temp_password = hash_password(temp_password)
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"password": hashed_temp_password}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Password reset successfully", "temporary_password": temp_password}

@api_router.put("/admin/users/bulk-block")
async def bulk_block_users(user_ids: List[str], admin: User = Depends(get_admin_user)):
    """Block multiple users"""
    result = await db.users.update_many(
        {"id": {"$in": user_ids}},
        {"$set": {"is_blocked": True}}
    )
    
    return {"message": f"Blocked {result.modified_count} users successfully"}

@api_router.put("/admin/users/bulk-unblock")
async def bulk_unblock_users(user_ids: List[str], admin: User = Depends(get_admin_user)):
    """Unblock multiple users"""
    result = await db.users.update_many(
        {"id": {"$in": user_ids}},
        {"$set": {"is_blocked": False}}
    )
    
    return {"message": f"Unblocked {result.modified_count} users successfully"}

@api_router.put("/admin/users/bulk-deactivate-all")
async def bulk_deactivate_all_users(admin: User = Depends(get_admin_user)):
    """Deactivate all users except admins"""
    result = await db.users.update_many(
        {"role": {"$ne": "admin"}},
        {"$set": {"is_blocked": True}}
    )
    
    return {"message": f"Deactivated {result.modified_count} users (admins excluded)"}

@api_router.put("/admin/users/bulk-activate-all")
async def bulk_activate_all_users(admin: User = Depends(get_admin_user)):
    """Activate all users"""
    result = await db.users.update_many(
        {},
        {"$set": {"is_blocked": False}}
    )
    
    return {"message": f"Activated {result.modified_count} users"}

@api_router.delete("/admin/users/bulk-delete")
async def bulk_delete_users(user_ids: List[str], admin: User = Depends(get_admin_user)):
    """Delete multiple users and their data"""
    deleted_count = 0
    
    for user_id in user_ids:
        # Skip if trying to delete admin
        user = await db.users.find_one({"id": user_id})
        if user and user.get('role') == 'admin':
            continue
            
        # Delete user's listings
        await db.listings.delete_many({"seller_id": user_id})
        
        # Delete user's cart items
        await db.cart_items.delete_many({"user_id": user_id})
        
        # Delete user's bids
        await db.bids.delete_many({"bidder_id": user_id})
        
        # Delete user's reviews
        await db.reviews.delete_many({"$or": [{"reviewer_id": user_id}, {"reviewed_user_id": user_id}]})
        
        # Mark orders as deleted (keep for seller records)
        await db.orders.update_many(
            {"$or": [{"buyer_id": user_id}, {"seller_id": user_id}]},
            {"$set": {"user_deleted": True}}
        )
        
        # Delete the user
        result = await db.users.delete_one({"id": user_id})
        if result.deleted_count > 0:
            deleted_count += 1
    
    return {"message": f"Deleted {deleted_count} users and all associated data"}

@api_router.delete("/admin/users/delete-all-non-admin")
async def delete_all_non_admin_users(admin: User = Depends(get_admin_user)):
    """Delete all non-admin users and their data - DANGEROUS OPERATION"""
    # Get all non-admin users
    non_admin_users = await db.users.find({"role": {"$ne": "admin"}}).to_list(length=None)
    user_ids = [user['id'] for user in non_admin_users]
    
    if not user_ids:
        return {"message": "No non-admin users to delete"}
    
    # Delete all user data
    listings_deleted = await db.listings.delete_many({"seller_id": {"$in": user_ids}})
    cart_deleted = await db.cart_items.delete_many({"user_id": {"$in": user_ids}})
    bids_deleted = await db.bids.delete_many({"bidder_id": {"$in": user_ids}})
    reviews_deleted = await db.reviews.delete_many({
        "$or": [
            {"reviewer_id": {"$in": user_ids}}, 
            {"reviewed_user_id": {"$in": user_ids}}
        ]
    })
    
    # Mark orders as deleted
    orders_updated = await db.orders.update_many(
        {"$or": [{"buyer_id": {"$in": user_ids}}, {"seller_id": {"$in": user_ids}}]},
        {"$set": {"user_deleted": True}}
    )
    
    # Delete all non-admin users
    users_deleted = await db.users.delete_many({"role": {"$ne": "admin"}})
    
    return {
        "message": f"BULK DELETE COMPLETED",
        "users_deleted": users_deleted.deleted_count,
        "listings_deleted": listings_deleted.deleted_count,
        "cart_items_deleted": cart_deleted.deleted_count,
        "bids_deleted": bids_deleted.deleted_count,
        "reviews_deleted": reviews_deleted.deleted_count,
        "orders_marked_deleted": orders_updated.modified_count
    }

@api_router.delete("/admin/users/{user_id}")
async def delete_user(user_id: str, admin: User = Depends(get_admin_user)):
    """Delete a user and all associated data"""
    # Delete user's listings
    await db.listings.delete_many({"seller_id": user_id})
    
    # Delete user's cart items
    await db.cart_items.delete_many({"user_id": user_id})
    
    # Delete user's bids
    await db.bids.delete_many({"bidder_id": user_id})
    
    # Delete user's reviews
    await db.reviews.delete_many({"$or": [{"reviewer_id": user_id}, {"reviewed_user_id": user_id}]})
    
    # Delete user's orders (keep for seller records, just mark as deleted)
    await db.orders.update_many(
        {"$or": [{"buyer_id": user_id}, {"seller_id": user_id}]},
        {"$set": {"user_deleted": True}}
    )
    
    # Finally delete the user
    result = await db.users.delete_one({"id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User and all associated data deleted successfully"}

# Admin Listing Management
@api_router.get("/admin/listings", response_model=List[ListingManagement])
async def get_all_listings(admin: User = Depends(get_admin_user)):
    """Get all listings for admin management"""
    listings = await db.listings.find({}).sort("created_at", -1).to_list(length=None)
    
    result = []
    for listing_doc in listings:
        listing = ProductListing(**parse_from_mongo(listing_doc))
        
        # Get seller info
        seller = await db.users.find_one({"id": listing.seller_id})
        seller_name = seller.get('full_name', 'Unknown') if seller else 'Unknown'
        
        result.append(ListingManagement(
            id=listing.id,
            title=listing.title,
            seller_id=listing.seller_id,
            seller_name=seller_name,
            price=listing.price or listing.current_bid,
            status=listing.status,
            created_at=listing.created_at,
            views=listing.views,
            category=listing.category
        ))
    
    return result

@api_router.delete("/admin/listings/{listing_id}")
async def delete_listing(listing_id: str, admin: User = Depends(get_admin_user)):
    """Delete a listing"""
    # Also delete associated bids and cart items
    await db.bids.delete_many({"listing_id": listing_id})
    await db.cart_items.delete_many({"listing_id": listing_id})
    
    result = await db.listings.delete_one({"id": listing_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return {"message": "Listing deleted successfully"}

@api_router.put("/admin/listings/{listing_id}/status")
async def update_listing_status(
    listing_id: str, 
    status: ListingStatus, 
    admin: User = Depends(get_admin_user)
):
    """Update listing status"""
    result = await db.listings.update_one(
        {"id": listing_id},
        {"$set": {"status": status}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return {"message": f"Listing status updated to {status}"}

@api_router.put("/admin/listings/{listing_id}")
async def update_listing(
    listing_id: str, 
    listing_data: dict, 
    admin: User = Depends(get_admin_user)
):
    """Update listing details"""
    # Remove any fields that shouldn't be updated
    allowed_fields = ['title', 'description', 'price', 'category', 'condition', 'quantity', 'location', 'listing_type']
    update_data = {k: v for k, v in listing_data.items() if k in allowed_fields}
    update_data['updated_at'] = datetime.now(timezone.utc)
    
    result = await db.listings.update_one(
        {"id": listing_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return {"message": "Listing updated successfully"}

# Admin Order Management
@api_router.get("/admin/orders")
async def get_all_orders(
    status_filter: str = None,  # "pending", "completed", "all"
    time_frame: str = None,  # "today", "yesterday", "last_week", "last_month", "last_year"
    admin: User = Depends(get_admin_user)
):
    """Get all orders for admin management with filters"""
    # Build query based on filters
    query = {}
    
    # Status filter
    if status_filter and status_filter != "all":
        if status_filter == "pending":
            query["status"] = {"$in": ["pending", "confirmed"]}
        elif status_filter == "completed":
            query["status"] = "completed"
    
    # Time frame filter
    if time_frame:
        now = datetime.now(timezone.utc)
        if time_frame == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            query["created_at"] = {"$gte": start_date}
        elif time_frame == "yesterday":
            end_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = end_date - timedelta(days=1)
            query["created_at"] = {"$gte": start_date, "$lt": end_date}
        elif time_frame == "last_week":
            start_date = now - timedelta(days=7)
            query["created_at"] = {"$gte": start_date}
        elif time_frame == "last_month":
            start_date = now - timedelta(days=30)
            query["created_at"] = {"$gte": start_date}
        elif time_frame == "last_year":
            start_date = now - timedelta(days=365)
            query["created_at"] = {"$gte": start_date}
    
    orders = await db.orders.find(query).sort("created_at", -1).to_list(length=None)
    
    result = []
    for order_doc in orders:
        order = Order(**parse_from_mongo(order_doc))
        
        # Get buyer and seller info
        buyer = await db.users.find_one({"id": order.buyer_id})
        seller = await db.users.find_one({"id": order.seller_id})
        listing = await db.listings.find_one({"id": order.listing_id})
        
        result.append({
            "order": order,
            "buyer": User(**parse_from_mongo(buyer)) if buyer else None,
            "seller": User(**parse_from_mongo(seller)) if seller else None,
            "listing": ProductListing(**parse_from_mongo(listing)) if listing else None
        })
    
    return result

# Create default admin user
@api_router.post("/admin/create-default-admin")
async def create_default_admin():
    """Create default admin user - only works if no admin exists"""
    existing_admin = await db.users.find_one({"role": "admin"})
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin user already exists")
    
    admin_data = {
        "email": "admin@marketplace.com",
        "username": "admin",
        "password": "admin123",
        "full_name": "System Administrator",
        "role": "admin"
    }
    
    # Hash password
    hashed_password = hash_password(admin_data['password'])
    
    # Generate user ID
    user_id = await generate_user_id()
    
    # Create admin user
    user_dict = admin_data.copy()
    del user_dict['password']
    user_dict['user_id'] = user_id
    admin_user = User(**user_dict)
    
    user_doc = prepare_for_mongo(admin_user.dict())
    user_doc['password'] = hashed_password
    
    await db.users.insert_one(user_doc)
    
    return {"message": "Default admin created", "email": "admin@marketplace.com", "password": "admin123", "user_id": user_id}

@api_router.post("/admin/generate-user-ids")
async def generate_missing_user_ids(admin: User = Depends(get_admin_user)):
    """Generate user IDs for existing users who don't have them"""
    # Find users without user_id or with empty user_id
    users_without_ids = await db.users.find({
        "$or": [
            {"user_id": {"$exists": False}},
            {"user_id": ""},
            {"user_id": None}
        ]
    }).to_list(length=None)
    
    updated_count = 0
    generated_ids = []
    
    for user_doc in users_without_ids:
        # Generate new user ID
        new_user_id = await generate_user_id()
        
        # Update the user
        result = await db.users.update_one(
            {"id": user_doc["id"]},
            {"$set": {"user_id": new_user_id}}
        )
        
        if result.modified_count > 0:
            updated_count += 1
            generated_ids.append({
                "email": user_doc.get("email", "Unknown"),
                "username": user_doc.get("username", "Unknown"),
                "user_id": new_user_id
            })
    
    return {
        "message": f"Generated user IDs for {updated_count} users",
        "updated_count": updated_count,
        "generated_ids": generated_ids
    }

# ===========================
# CMS ROUTES
# ===========================

# Site Settings Management
# Test endpoint to debug Phase 2 fields
@api_router.get("/admin/cms/test-settings")
async def test_site_settings(admin: User = Depends(get_admin_user)):
    """Test endpoint to debug Phase 2 fields"""
    site_settings = SiteSettings()
    result = site_settings.dict(exclude_unset=False)
    
    return {
        "total_fields": len(result),
        "phase2_fields": {
            "font_color": result.get("font_color"),
            "link_color": result.get("link_color"), 
            "link_hover_color": result.get("link_hover_color"),
            "hero_image_url": result.get("hero_image_url"),
            "hero_background_image_url": result.get("hero_background_image_url"),
            "hero_background_size": result.get("hero_background_size")
        },
        "all_fields": sorted(result.keys())
    }

@api_router.get("/admin/cms/settings")
async def get_site_settings(admin: User = Depends(get_admin_user)):
    """Get current site settings"""
    # Always return a fresh SiteSettings instance with all fields
    settings = await db.site_settings.find_one({})
    if settings:
        parsed_settings = parse_from_mongo(settings)
        site_settings = SiteSettings(**parsed_settings)
    else:
        site_settings = SiteSettings()
    
    # Return the complete settings dict
    result = site_settings.dict(exclude_unset=False)
    
    # Update database with complete settings for future use
    settings_doc = prepare_for_mongo(result)
    await db.site_settings.replace_one({}, settings_doc, upsert=True)
    
    return result

@api_router.put("/admin/cms/settings")
async def update_site_settings(settings_data: dict, admin: User = Depends(get_admin_user)):
    """Update site settings"""
    settings_data['updated_at'] = datetime.now(timezone.utc)
    
    # Get current settings or create default
    current_settings = await db.site_settings.find_one({})
    if not current_settings:
        # Create default settings with all fields
        default_settings = SiteSettings()
        current_settings = prepare_for_mongo(default_settings.dict(exclude_unset=False))
    else:
        current_settings = parse_from_mongo(current_settings)
    
    # Update current settings with new data
    current_settings.update(settings_data)
    
    # Ensure all fields are present by creating SiteSettings instance
    updated_settings = SiteSettings(**current_settings)
    settings_doc = prepare_for_mongo(updated_settings.dict(exclude_unset=False))
    
    # Replace the entire document to ensure all fields are saved
    result = await db.site_settings.replace_one(
        {},
        settings_doc,
        upsert=True
    )
    
    return {"message": "Site settings updated successfully"}

# Page Content Management
@api_router.get("/admin/cms/pages")
async def get_all_pages(admin: User = Depends(get_admin_user)):
    """Get all pages"""
    pages = await db.page_content.find({}).to_list(length=None)
    return [PageContent(**parse_from_mongo(page)) for page in pages]

@api_router.get("/admin/cms/pages/{page_slug}")
async def get_page_content(page_slug: str, admin: User = Depends(get_admin_user)):
    """Get specific page content"""
    page = await db.page_content.find_one({"page_slug": page_slug})
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return PageContent(**parse_from_mongo(page))

@api_router.post("/admin/cms/pages")
async def create_page(page_data: dict, admin: User = Depends(get_admin_user)):
    """Create new page"""
    page = PageContent(**page_data)
    page_doc = prepare_for_mongo(page.dict())
    await db.page_content.insert_one(page_doc)
    
    # Auto-add to navigation if enabled
    settings = await db.site_settings.find_one({})
    if not settings or settings.get('auto_add_pages_to_menu', True):
        # Get current max order
        nav_items = await db.navigation.find({}).to_list(length=None)
        max_order = max([item.get('order', 0) for item in nav_items]) if nav_items else 0
        
        # Create navigation item
        nav_item = NavigationItem(
            label=page.title,
            url=f"/{page.page_slug}",
            order=max_order + 1,
            is_visible=page.is_published,
            target="_self"
        )
        nav_doc = prepare_for_mongo(nav_item.dict())
        await db.navigation.insert_one(nav_doc)
    
    return {"message": "Page created successfully", "page": page}

@api_router.put("/admin/cms/pages/{page_slug}")
async def update_page_content(page_slug: str, page_data: dict, admin: User = Depends(get_admin_user)):
    """Update page content"""
    page_data['updated_at'] = datetime.now(timezone.utc)
    
    result = await db.page_content.update_one(
        {"page_slug": page_slug},
        {"$set": page_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Update navigation item if it exists
    nav_update_data = {}
    if 'title' in page_data:
        nav_update_data['label'] = page_data['title']
    if 'is_published' in page_data:
        nav_update_data['is_visible'] = page_data['is_published']
    
    if nav_update_data:
        await db.navigation.update_one(
            {"url": f"/{page_slug}"},
            {"$set": nav_update_data}
        )
    
    return {"message": "Page updated successfully"}

@api_router.delete("/admin/cms/pages/{page_slug}")
async def delete_page(page_slug: str, admin: User = Depends(get_admin_user)):
    """Delete page"""
    result = await db.page_content.delete_one({"page_slug": page_slug})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    
    # Also delete from navigation
    await db.navigation.delete_one({"url": f"/{page_slug}"})
    
    return {"message": "Page deleted successfully"}

@api_router.post("/admin/cms/sync-navigation")
async def sync_navigation_with_pages(admin: User = Depends(get_admin_user)):
    """Sync navigation items with existing pages"""
    pages = await db.page_content.find({"is_published": True}).to_list(length=None)
    existing_nav = await db.navigation.find({}).to_list(length=None)
    
    # Get existing navigation URLs
    existing_urls = {item.get('url') for item in existing_nav}
    
    # Add missing pages to navigation
    added_count = 0
    max_order = max([item.get('order', 0) for item in existing_nav]) if existing_nav else 0
    
    for page_doc in pages:
        page_url = f"/{page_doc['page_slug']}"
        if page_url not in existing_urls:
            nav_item = NavigationItem(
                label=page_doc['title'],
                url=page_url,
                order=max_order + added_count + 1,
                is_visible=True,
                target="_self"
            )
            nav_doc = prepare_for_mongo(nav_item.dict())
            await db.navigation.insert_one(nav_doc)
            added_count += 1
    
    return {"message": f"Added {added_count} pages to navigation", "added_count": added_count}

# Navigation Management
@api_router.get("/admin/cms/navigation")
async def get_navigation(admin: User = Depends(get_admin_user)):
    """Get navigation items"""
    nav_items = await db.navigation.find({}).sort("order", 1).to_list(length=None)
    return [NavigationItem(**parse_from_mongo(item)) for item in nav_items]

@api_router.post("/admin/cms/navigation")
async def create_navigation_item(nav_data: dict, admin: User = Depends(get_admin_user)):
    """Create navigation item"""
    nav_item = NavigationItem(**nav_data)
    nav_doc = prepare_for_mongo(nav_item.dict())
    await db.navigation.insert_one(nav_doc)
    return {"message": "Navigation item created successfully", "item": nav_item}

@api_router.put("/admin/cms/navigation/{nav_id}")
async def update_navigation_item(nav_id: str, nav_data: dict, admin: User = Depends(get_admin_user)):
    """Update navigation item"""
    result = await db.navigation.update_one(
        {"id": nav_id},
        {"$set": nav_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Navigation item not found")
    
    return {"message": "Navigation item updated successfully"}

@api_router.delete("/admin/cms/navigation/{nav_id}")
async def delete_navigation_item(nav_id: str, admin: User = Depends(get_admin_user)):
    """Delete navigation item"""
    result = await db.navigation.delete_one({"id": nav_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Navigation item not found")
    
    return {"message": "Navigation item deleted successfully"}

# Logo Upload Endpoints
@api_router.post("/admin/cms/upload-logo")
async def upload_logo(
    logo_type: str = "header",  # header, footer, favicon
    file: UploadFile = File(...),
    admin: User = Depends(get_admin_user)
):
    """Upload logo file (PNG only)"""
    
    # Validate file type
    if not file.content_type == "image/png":
        raise HTTPException(status_code=400, detail="Only PNG files are allowed")
    
    # Validate file size (max 5MB)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=400, detail="File size too large. Maximum 5MB allowed")
    
    # Generate unique filename
    file_extension = ".png"
    unique_filename = f"{logo_type}_logo_{uuid.uuid4().hex}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Update site settings with new logo URL
    logo_url = f"/uploads/{unique_filename}"
    
    # Get current settings
    current_settings = await db.site_settings.find_one({})
    if not current_settings:
        # Create default settings if none exist
        default_settings = SiteSettings()
        current_settings = default_settings.dict()
    
    # Update the appropriate logo field
    if logo_type == "header":
        # Remove old logo file if it exists BEFORE updating the setting
        old_logo_url = current_settings.get("header_logo_url")
        if old_logo_url and old_logo_url.startswith("/uploads/"):
            old_file_path = UPLOAD_DIR / old_logo_url.split("/")[-1]
            if old_file_path.exists():
                try:
                    old_file_path.unlink()
                except Exception:
                    pass  # Ignore errors when deleting old files
        
        # Now set the new logo URL
        current_settings["header_logo_url"] = logo_url
    
    # Update settings in database
    await db.site_settings.replace_one(
        {},
        current_settings,
        upsert=True
    )
    
    return {
        "message": "Logo uploaded successfully",
        "logo_url": logo_url,
        "logo_type": logo_type
    }

# Hero Image Upload Endpoints
@api_router.post("/admin/cms/upload-hero-image")
async def upload_hero_image(
    file: UploadFile = File(...),
    admin: User = Depends(get_admin_user)
):
    """Upload hero image file (PNG, JPG, JPEG only)"""
    
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PNG and JPEG files are allowed")
    
    # Validate file size (max 5MB)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=400, detail="File size too large. Maximum 5MB allowed")
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1] or ".png"
    unique_filename = f"hero_image_{uuid.uuid4().hex}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Generate URL
    hero_image_url = f"/uploads/{unique_filename}"
    
    return {
        "message": "Hero image uploaded successfully",
        "hero_image_url": hero_image_url
    }

@api_router.post("/admin/cms/upload-hero-background")
async def upload_hero_background(
    file: UploadFile = File(...),
    admin: User = Depends(get_admin_user)
):
    """Upload hero background image file (PNG, JPG, JPEG only)"""
    
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PNG and JPEG files are allowed")
    
    # Validate file size (max 25MB for backgrounds)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > 25 * 1024 * 1024:  # 25MB limit
        raise HTTPException(status_code=400, detail="File size too large. Maximum 25MB allowed")
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1] or ".png"
    unique_filename = f"hero_background_{uuid.uuid4().hex}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Generate URL
    hero_background_image_url = f"/uploads/{unique_filename}"
    
    return {
        "message": "Hero background image uploaded successfully",
        "hero_background_image_url": hero_background_image_url
    }

# SEO Settings Endpoints
@api_router.get("/admin/seo")
async def get_seo_settings(current_user: User = Depends(get_admin_user)):
    """Get SEO settings for admin"""
    try:
        # Try to get existing SEO settings
        seo_doc = await db.seo_settings.find_one({})
        
        if seo_doc:
            # Convert MongoDB document to SEOSettings model
            seo_settings = SEOSettings(**parse_from_mongo(seo_doc))
            return seo_settings.dict()
        else:
            # Return default settings
            default_settings = SEOSettings()
            return default_settings.dict()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get SEO settings: {str(e)}")

@api_router.post("/admin/seo")
async def save_seo_settings(
    seo_data: SEOSettings,
    current_user: User = Depends(get_admin_user)
):
    """Save SEO settings"""
    try:
        # Update timestamps
        seo_data.updated_at = datetime.now(timezone.utc)
        
        # Convert to dict for MongoDB
        seo_dict = prepare_for_mongo(seo_data.dict())
        
        # Upsert the settings (update if exists, create if not)
        await db.seo_settings.replace_one(
            {},  # Empty filter to match any document (since we only have one SEO settings document)
            seo_dict,
            upsert=True
        )
        
        return {
            "message": "SEO settings saved successfully",
            "settings": seo_dict
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save SEO settings: {str(e)}")

# Listing Image Upload Endpoints
@api_router.post("/listings/upload-image")
async def upload_listing_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload image for listings (PNG, JPG, JPEG only)"""
    
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only PNG and JPEG files are allowed")
    
    # Validate file size (max 10MB for listing images)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File size too large. Maximum 10MB allowed")
    
    # Generate unique filename
    file_extension = ".png" if file.content_type == "image/png" else ".jpg"
    unique_filename = f"listing_{uuid.uuid4().hex}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Return the image URL
    image_url = f"/uploads/{unique_filename}"
    
    return {
        "message": "Image uploaded successfully",
        "image_url": image_url
    }

# Public CMS Endpoints (for frontend)
@api_router.get("/cms/settings")
async def get_public_site_settings():
    """Get public site settings"""
    settings = await db.site_settings.find_one({})
    if not settings:
        return SiteSettings().dict(exclude_unset=False)
    return SiteSettings(**parse_from_mongo(settings)).dict(exclude_unset=False)

@api_router.get("/cms/pages/{page_slug}")
async def get_public_page_content(page_slug: str):
    """Get public page content"""
    page = await db.page_content.find_one({"page_slug": page_slug, "is_published": True})
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return PageContent(**parse_from_mongo(page)).dict()

@api_router.get("/cms/navigation")
async def get_public_navigation():
    """Get public navigation items"""
    nav_items = await db.navigation.find({"is_visible": True}).sort("order", 1).to_list(length=None)
    return [NavigationItem(**parse_from_mongo(item)).dict() for item in nav_items]

# Enhanced Profile Management Endpoints

@api_router.get("/profile/stats")
async def get_user_stats(current_user: User = Depends(get_current_user)):
    """Get comprehensive user statistics"""
    user_id = current_user.id
    
    # Get basic stats from database
    total_orders = await db.orders.count_documents({"user_id": user_id})
    total_listings = await db.listings.count_documents({"seller_id": user_id})
    
    # Calculate earnings from completed orders
    earnings_pipeline = [
        {"$match": {"seller_id": user_id, "status": "completed"}},
        {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
    ]
    earnings_result = await db.orders.aggregate(earnings_pipeline).to_list(1)
    total_earned = earnings_result[0]["total"] if earnings_result else 0.0
    
    # Calculate spending from user's orders
    spending_pipeline = [
        {"$match": {"user_id": user_id, "status": "completed"}},
        {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
    ]
    spending_result = await db.orders.aggregate(spending_pipeline).to_list(1)
    total_spent = spending_result[0]["total"] if spending_result else 0.0
    
    # Get reviews for this user
    reviews = await db.reviews.find({"reviewed_user_id": user_id}).to_list(None)
    total_reviews = len(reviews)
    avg_rating = sum(r["rating"] for r in reviews) / total_reviews if total_reviews > 0 else 0.0
    
    # Count successful transactions
    successful_transactions = await db.orders.count_documents({
        "$or": [{"user_id": user_id}, {"seller_id": user_id}],
        "status": "completed"
    })
    
    # Get user profile data for additional stats
    user_profile = await db.users.find_one({"id": user_id})
    profile_views = user_profile.get("profile_views", 0) if user_profile else 0
    trust_score = user_profile.get("trust_score", 50) if user_profile else 50
    account_level = user_profile.get("account_level", "Bronze") if user_profile else "Bronze"
    
    # Calculate badges based on achievements
    badges_earned = 0
    if total_listings >= 10: badges_earned += 1  # Active Seller
    if total_reviews >= 20: badges_earned += 1   # Trusted User
    if avg_rating >= 4.5: badges_earned += 1     # Top Rated
    if successful_transactions >= 50: badges_earned += 1  # Super Trader
    if trust_score >= 90: badges_earned += 1     # Verified Expert
    
    # Calculate response rate (mock for now, can be improved with message tracking)
    response_rate = min(95.0, 60.0 + (trust_score * 0.4))
    avg_response_time = max(0.5, 5.0 - (trust_score * 0.05))
    
    return {
        "total_orders": total_orders,
        "total_listings": total_listings,
        "total_spent": round(total_spent, 2),
        "total_earned": round(total_earned, 2),
        "avg_rating": round(avg_rating, 1),
        "total_reviews": total_reviews,
        "successful_transactions": successful_transactions,
        "profile_views": profile_views,
        "trust_score": trust_score,
        "account_level": account_level,
        "badges_earned": badges_earned,
        "response_rate": round(response_rate, 1),
        "avg_response_time": round(avg_response_time, 1)
    }

@api_router.get("/profile/activity")
async def get_user_activity(current_user: User = Depends(get_current_user)):
    """Get user activity timeline"""
    user_id = current_user.id
    
    activities = []
    
    # Get recent listings
    recent_listings = await db.listings.find(
        {"seller_id": user_id}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    for listing in recent_listings:
        time_diff = datetime.now(timezone.utc) - listing["created_at"]
        hours_ago = int(time_diff.total_seconds() / 3600)
        time_str = f"{hours_ago}h ago" if hours_ago < 24 else f"{int(hours_ago/24)}d ago"
        
        activities.append({
            "type": "listing_created",
            "title": f"Created new listing: {listing['title']}",
            "time": time_str,
            "icon": "📦",
            "color": "green",
            "metadata": {"listing_id": listing["id"]}
        })
    
    # Get recent orders
    recent_orders = await db.orders.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    for order in recent_orders:
        time_diff = datetime.now(timezone.utc) - order["created_at"]
        hours_ago = int(time_diff.total_seconds() / 3600)
        time_str = f"{hours_ago}h ago" if hours_ago < 24 else f"{int(hours_ago/24)}d ago"
        
        status_icon = "✅" if order["status"] == "completed" else "🛒"
        status_text = "Completed purchase" if order["status"] == "completed" else "Placed order"
        
        # Get listing title
        listing = await db.listings.find_one({"id": order["listing_id"]})
        listing_title = listing["title"] if listing else "Unknown item"
        
        activities.append({
            "type": "order_" + order["status"],
            "title": f"{status_text}: {listing_title}",
            "time": time_str,
            "icon": status_icon,
            "color": "blue" if order["status"] == "completed" else "purple",
            "metadata": {"order_id": order["id"]}
        })
    
    # Get recent reviews received
    recent_reviews = await db.reviews.find(
        {"reviewed_user_id": user_id}
    ).sort("created_at", -1).limit(3).to_list(3)
    
    for review in recent_reviews:
        time_diff = datetime.now(timezone.utc) - review["created_at"]
        hours_ago = int(time_diff.total_seconds() / 3600)
        time_str = f"{hours_ago}h ago" if hours_ago < 24 else f"{int(hours_ago/24)}d ago"
        
        # Get reviewer name
        reviewer = await db.users.find_one({"id": review["reviewer_id"]})
        reviewer_name = reviewer["full_name"] if reviewer else "Anonymous"
        
        activities.append({
            "type": "review_received",
            "title": f"Received {review['rating']}-star review from {reviewer_name}",
            "time": time_str,
            "icon": "⭐",
            "color": "yellow",
            "metadata": {"review_id": review["id"], "rating": review["rating"]}
        })
    
    # Sort all activities by time (most recent first)
    activities.sort(key=lambda x: x["time"])
    
    return activities[:10]  # Return top 10 activities

@api_router.put("/profile")
async def update_profile(
    profile_update: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user profile information"""
    user_id = current_user.id
    
    update_data = {}
    if profile_update.full_name is not None:
        update_data["full_name"] = profile_update.full_name
    if profile_update.bio is not None:
        update_data["bio"] = profile_update.bio
    if profile_update.location is not None:
        update_data["location"] = profile_update.location
    if profile_update.website is not None:
        update_data["website"] = profile_update.website
    if profile_update.phone is not None:
        update_data["phone"] = profile_update.phone
    if profile_update.social_links is not None:
        update_data["social_links"] = profile_update.social_links
    if profile_update.preferences is not None:
        update_data["preferences"] = profile_update.preferences
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Profile updated successfully"}

@api_router.post("/profile/upload-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload user profile picture"""
    user_id = current_user.id
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate file size (5MB limit)
    if file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1]
    filename = f"profile_{user_id}_{int(datetime.now().timestamp())}.{file_extension}"
    file_path = UPLOAD_DIR / filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update user profile with new picture URL
    profile_picture_url = f"/uploads/{filename}"
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "profile_picture_url": profile_picture_url,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    return {"profile_picture_url": profile_picture_url}

@api_router.get("/profile/increment-view/{profile_user_id}")
async def increment_profile_view(profile_user_id: str):
    """Increment profile view count (can be called anonymously)"""
    await db.users.update_one(
        {"id": profile_user_id},
        {"$inc": {"profile_views": 1}}
    )
    return {"message": "Profile view incremented"}

# Messages and Reviews Endpoints

@api_router.get("/messages")
async def get_user_messages(current_user: dict = Depends(get_current_user)):
    """Get user messages"""
    user_id = current_user["id"]
    
    messages = await db.messages.find({
        "$or": [
            {"sender_id": user_id},
            {"receiver_id": user_id}
        ]
    }).sort("created_at", -1).limit(20).to_list(20)
    
    result = []
    for msg in messages:
        # Get sender info
        sender = await db.users.find_one({"id": msg["sender_id"]})
        sender_name = sender["full_name"] if sender else "Unknown User"
        
        time_diff = datetime.now(timezone.utc) - msg["created_at"]
        hours_ago = int(time_diff.total_seconds() / 3600)
        time_str = f"{hours_ago}h ago" if hours_ago < 24 else f"{int(hours_ago/24)}d ago"
        
        result.append({
            "id": msg["id"],
            "sender": sender_name,
            "message": msg["message"],
            "time": time_str,
            "read": msg.get("read", False),
            "is_sender": msg["sender_id"] == user_id
        })
    
    return result

@api_router.get("/reviews/user")
async def get_user_reviews(current_user: dict = Depends(get_current_user)):
    """Get reviews for the current user"""
    user_id = current_user["id"]
    
    reviews = await db.reviews.find({"reviewed_user_id": user_id}).sort("created_at", -1).to_list(None)
    
    result = []
    for review in reviews:
        # Get reviewer info
        reviewer = await db.users.find_one({"id": review["reviewer_id"]})
        reviewer_name = reviewer["full_name"] if reviewer else "Anonymous"
        
        # Get item info if available
        item = "Unknown Item"
        if review.get("listing_id"):
            listing = await db.listings.find_one({"id": review["listing_id"]})
            item = listing["title"] if listing else "Unknown Item"
        
        result.append({
            "id": review["id"],
            "reviewer": reviewer_name,
            "rating": review["rating"],
            "comment": review.get("comment", ""),
            "date": review["created_at"].strftime("%Y-%m-%d"),
            "item": item
        })
    
    return result

@api_router.get("/orders")
async def get_user_orders(current_user: dict = Depends(get_current_user)):
    """Get user's orders with enhanced details"""
    user_id = current_user["id"]
    
    orders = await db.orders.find({"user_id": user_id}).sort("created_at", -1).to_list(None)
    
    result = []
    for order in orders:
        # Get listing info
        listing = await db.listings.find_one({"id": order["listing_id"]})
        title = listing["title"] if listing else "Unknown Item"
        
        # Get seller info
        seller = await db.users.find_one({"id": order.get("seller_id", "")})
        seller_name = seller["full_name"] if seller else "Unknown Seller"
        
        result.append({
            "id": order["id"],
            "title": title,
            "status": order["status"],
            "total": order["total_amount"],
            "created_at": order["created_at"].strftime("%Y-%m-%d"),
            "seller": seller_name
        })
    
    return result

@api_router.get("/listings/user")
async def get_user_listings(current_user: dict = Depends(get_current_user)):
    """Get user's listings with enhanced details"""
    user_id = current_user["id"]
    
    listings = await db.listings.find({"seller_id": user_id}).sort("created_at", -1).to_list(None)
    
    result = []
    for listing in listings:
        # Calculate watchers (users who favorited this listing)
        watchers = await db.favorites.count_documents({"listing_id": listing["id"]})
        
        result.append({
            "id": listing["id"],
            "title": listing["title"],
            "status": listing["status"],
            "price": listing["price"],
            "views": listing.get("views", 0),
            "watchers": watchers,
            "created_at": listing["created_at"].strftime("%Y-%m-%d")
        })
    
    return result

# Update existing profile endpoint to return enhanced data

class ProfileUpdate(BaseModel):
    """User profile update model"""
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    is_business: Optional[bool] = None
    company_name: Optional[str] = None
    country: Optional[str] = None
    vat_number: Optional[str] = None

class UserProfile(BaseModel):
    """User profile response model"""
    id: str
    user_id: str  # Added user_id field for v1.0.2
    username: str
    full_name: str
    email: str
    phone: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_business: Optional[bool] = None
    company_name: Optional[str] = None
    country: Optional[str] = None
    vat_number: Optional[str] = None

class UserStats(BaseModel):
    """User statistics model"""
    total_orders: int = 0
    total_listings: int = 0
    total_spent: float = 0.0
    total_earned: float = 0.0
    avg_rating: float = 0.0
    total_reviews: int = 0

@api_router.get("/profile", response_model=UserProfile)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    try:
        # Convert User model to ProfileResponse
        profile_data = {
            "id": current_user.id,
            "user_id": getattr(current_user, 'user_id', ''),  # Added user_id field for v1.0.2
            "username": current_user.username,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "phone": getattr(current_user, 'phone', None),
            "bio": getattr(current_user, 'bio', None),
            "location": getattr(current_user, 'location', None),
            "role": current_user.role,
            "created_at": current_user.created_at,
            "updated_at": getattr(current_user, 'updated_at', None),
            "is_business": getattr(current_user, 'is_business', False),
            "company_name": getattr(current_user, 'company_name', None),
            "country": getattr(current_user, 'country', None),
            "vat_number": getattr(current_user, 'vat_number', None)
        }
        
        return UserProfile(**profile_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profile: {str(e)}")

@api_router.put("/profile", response_model=UserProfile)  
async def update_user_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile"""
    try:
        # Prepare update data
        update_data = {}
        
        if profile_update.username is not None:
            # Check if username is already taken
            existing_user = await db.users.find_one({
                "username": profile_update.username,
                "id": {"$ne": current_user.id}
            })
            if existing_user:
                raise HTTPException(status_code=400, detail="Username already taken")
            update_data["username"] = profile_update.username
            
        if profile_update.full_name is not None:
            update_data["full_name"] = profile_update.full_name
            
        if profile_update.phone is not None:
            update_data["phone"] = profile_update.phone
            
        if profile_update.bio is not None:
            update_data["bio"] = profile_update.bio
            
        if profile_update.location is not None:
            update_data["location"] = profile_update.location
            
        if profile_update.is_business is not None:
            update_data["is_business"] = profile_update.is_business
            
        if profile_update.company_name is not None:
            update_data["company_name"] = profile_update.company_name
            
        if profile_update.country is not None:
            update_data["country"] = profile_update.country
            
        if profile_update.vat_number is not None:
            update_data["vat_number"] = profile_update.vat_number
            
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            
            # Update user in database
            await db.users.update_one(
                {"id": current_user.id},
                {"$set": update_data}
            )
            
            # Fetch updated user
            updated_user_doc = await db.users.find_one({"id": current_user.id})
            if not updated_user_doc:
                raise HTTPException(status_code=404, detail="User not found after update")
                
            updated_user_doc = parse_from_mongo(updated_user_doc)
            
            # Convert to profile response
            profile_data = {
                "id": updated_user_doc["id"],
                "user_id": updated_user_doc.get("user_id", ""),  # Added user_id field for v1.0.2
                "username": updated_user_doc["username"],
                "full_name": updated_user_doc["full_name"],
                "email": updated_user_doc["email"],
                "phone": updated_user_doc.get("phone"),
                "bio": updated_user_doc.get("bio"),
                "location": updated_user_doc.get("location"),
                "role": updated_user_doc["role"],
                "created_at": updated_user_doc["created_at"],
                "updated_at": updated_user_doc.get("updated_at"),
                "is_business": updated_user_doc.get("is_business", False),
                "company_name": updated_user_doc.get("company_name"),
                "country": updated_user_doc.get("country"),
                "vat_number": updated_user_doc.get("vat_number")
            }
            
            return UserProfile(**profile_data)
        else:
            # No updates provided, return current profile
            return await get_user_profile(current_user)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@api_router.get("/profile/stats", response_model=UserStats)
async def get_user_stats(current_user: User = Depends(get_current_user)):
    """Get current user's statistics"""
    try:
        stats = UserStats()
        
        # Count user's orders
        orders_count = await db.orders.count_documents({"buyer_id": current_user.id})
        stats.total_orders = orders_count
        
        # Calculate total spent
        orders_cursor = db.orders.find({"buyer_id": current_user.id})
        total_spent = 0.0
        async for order in orders_cursor:
            if order.get("total_amount"):
                total_spent += float(order["total_amount"])
        stats.total_spent = total_spent
        
        # Count user's listings  
        listings_count = await db.listings.count_documents({"seller_id": current_user.id})
        stats.total_listings = listings_count
        
        # Calculate total earned (from completed orders of user's listings)
        listings_cursor = db.listings.find({"seller_id": current_user.id})
        total_earned = 0.0
        async for listing in listings_cursor:
            # Find completed orders for this listing
            completed_orders = db.orders.find({
                "listing_id": listing["id"],
                "status": "completed"
            })
            async for order in completed_orders:
                if order.get("total_amount"):
                    total_earned += float(order["total_amount"])
        stats.total_earned = total_earned
        
        # Get user rating and reviews
        stats.avg_rating = getattr(current_user, 'rating', 0.0)
        stats.total_reviews = getattr(current_user, 'total_reviews', 0)
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user statistics: {str(e)}")

# ===========================
# BULK ACTIONS ENDPOINTS (Phase 3B)
# ===========================

class BulkListingUpdate(BaseModel):
    """Bulk listing update model"""
    listing_ids: List[str]
    status: Optional[str] = None
    category: Optional[str] = None
    featured: Optional[bool] = None

class BulkPriceUpdate(BaseModel):
    """Bulk price update model"""
    listing_ids: List[str]
    price_type: str  # 'increase', 'decrease', 'set'
    price_value: float

class BulkDeleteRequest(BaseModel):
    """Bulk delete model"""
    listing_ids: List[str]

# ===========================
# NOTIFICATION SYSTEM (Phase 3C)
# ===========================

class NotificationType(str, Enum):
    ORDER_RECEIVED = "order_received"
    ORDER_APPROVED = "order_approved"
    ORDER_REJECTED = "order_rejected"
    ORDER_COMPLETED = "order_completed"
    LISTING_SOLD = "listing_sold"
    PAYMENT_RECEIVED = "payment_received"
    MESSAGE_RECEIVED = "message_received"

class Notification(BaseModel):
    """Notification model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    notification_type: NotificationType
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None  # Additional data (order_id, listing_id, etc.)
    read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConnectionManager:
    """WebSocket connection manager for real-time notifications"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"User {user_id} connected to notifications")
    
    def disconnect(self, user_id: str):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"User {user_id} disconnected from notifications")
    
    async def send_personal_notification(self, user_id: str, notification: dict):
        """Send notification to specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(notification)
                return True
            except Exception as e:
                print(f"Failed to send notification to {user_id}: {e}")
                # Remove stale connection
                self.disconnect(user_id)
                return False
        return False
    
    async def broadcast_notification(self, notification: dict, exclude_user_id: Optional[str] = None):
        """Broadcast notification to all connected users"""
        for user_id, connection in self.active_connections.items():
            if exclude_user_id and user_id == exclude_user_id:
                continue
            try:
                await connection.send_json(notification)
            except Exception as e:
                print(f"Failed to broadcast to {user_id}: {e}")
                # Remove stale connection
                self.disconnect(user_id)

# Global connection manager
connection_manager = ConnectionManager()

@api_router.post("/admin/listings/bulk-delete")
async def bulk_delete_listings(
    request: BulkDeleteRequest,
    admin: User = Depends(get_admin_user)
):
    """Bulk delete listings"""
    try:
        result = await db.listings.delete_many({
            "id": {"$in": request.listing_ids}
        })
        
        return {
            "message": f"Successfully deleted {result.deleted_count} listings",
            "deleted_count": result.deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete listings: {str(e)}")

@api_router.post("/admin/listings/bulk-update")
async def bulk_update_listings(
    request: BulkListingUpdate,
    admin: User = Depends(get_admin_user)
):
    """Bulk update listing properties"""
    try:
        update_data = {}
        
        if request.status is not None:
            update_data["status"] = request.status
        if request.category is not None:
            update_data["category"] = request.category
        if request.featured is not None:
            update_data["featured"] = request.featured
            
        if not update_data:
            raise HTTPException(status_code=400, detail="No update fields provided")
            
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        result = await db.listings.update_many(
            {"id": {"$in": request.listing_ids}},
            {"$set": update_data}
        )
        
        return {
            "message": f"Successfully updated {result.modified_count} listings",
            "modified_count": result.modified_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update listings: {str(e)}")

@api_router.post("/admin/listings/bulk-price-update")
async def bulk_price_update_listings(
    request: BulkPriceUpdate,
    admin: User = Depends(get_admin_user)
):
    """Bulk update listing prices"""
    try:
        # Get current listings to calculate new prices
        cursor = db.listings.find({"id": {"$in": request.listing_ids}})
        
        updates = []
        async for listing in cursor:
            current_price = float(listing.get("price", 0))
            
            if request.price_type == "increase":
                new_price = current_price * (1 + request.price_value / 100)
            elif request.price_type == "decrease":
                new_price = current_price * (1 - request.price_value / 100)
                new_price = max(0.01, new_price)  # Ensure minimum price
            elif request.price_type == "set":
                new_price = request.price_value
            else:
                continue
                
            updates.append({
                "listing_id": listing["id"],
                "old_price": current_price,
                "new_price": round(new_price, 2)
            })
            
            # Update the listing
            await db.listings.update_one(
                {"id": listing["id"]},
                {
                    "$set": {
                        "price": round(new_price, 2),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
        
        return {
            "message": f"Successfully updated prices for {len(updates)} listings",
            "updates": updates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update prices: {str(e)}")

# ===========================
# NOTIFICATION ENDPOINTS (Phase 3C)
# ===========================

@api_router.websocket("/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time notifications"""
    try:
        await connection_manager.connect(websocket, user_id)
        
        # Send any unread notifications when user connects
        unread_notifications = await get_user_notifications(user_id, unread_only=True)
        for notification in unread_notifications:
            await connection_manager.send_personal_notification(user_id, {
                "type": "notification",
                "data": notification
            })
        
        # Keep connection alive
        while True:
            try:
                # Receive heartbeat or other messages from client
                message = await websocket.receive_text()
                if message == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error for user {user_id}: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(user_id)

async def create_notification(
    user_id: str,
    notification_type: NotificationType,
    title: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> str:
    """Create and send notification"""
    try:
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            data=data or {}
        )
        
        # Save to database
        notification_doc = prepare_for_mongo(notification.dict())
        await db.notifications.insert_one(notification_doc)
        
        # Send real-time notification
        await connection_manager.send_personal_notification(user_id, {
            "type": "notification",
            "data": notification.dict()
        })
        
        return notification.id
        
    except Exception as e:
        print(f"Failed to create notification: {e}")
        return None

async def get_user_notifications(user_id: str, unread_only: bool = False) -> List[dict]:
    """Get user notifications"""
    try:
        query = {"user_id": user_id}
        if unread_only:
            query["read"] = False
            
        cursor = db.notifications.find(query).sort("created_at", -1)
        notifications = []
        
        async for doc in cursor:
            notification = parse_from_mongo(doc)
            notifications.append(notification)
            
        return notifications
        
    except Exception as e:
        print(f"Failed to get notifications: {e}")
        return []

@api_router.get("/notifications")
async def get_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Get user notifications"""
    try:
        notifications = await get_user_notifications(current_user.id, unread_only)
        return {
            "notifications": notifications,
            "unread_count": len([n for n in notifications if not n.get("read", False)])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mark notification as read"""
    try:
        result = await db.notifications.update_one(
            {"id": notification_id, "user_id": current_user.id},
            {"$set": {"read": True}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")

@api_router.put("/notifications/mark-all-read")
async def mark_all_notifications_read(current_user: User = Depends(get_current_user)):
    """Mark all user notifications as read"""
    try:
        result = await db.notifications.update_many(
            {"user_id": current_user.id, "read": False},
            {"$set": {"read": True}}
        )
        
        return {
            "message": f"Marked {result.modified_count} notifications as read"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notifications as read: {str(e)}")

@api_router.delete("/notifications/clear-all")
async def clear_all_notifications(current_user: User = Depends(get_current_user)):
    """Clear (delete) all user notifications"""
    try:
        result = await db.notifications.delete_many(
            {"user_id": current_user.id}
        )
        
        return {
            "message": f"Cleared {result.deleted_count} notifications",
            "deleted_count": result.deleted_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear notifications: {str(e)}")

# Bulk Order Management Endpoints
class OrderBulkUpdateRequest(BaseModel):
    order_ids: List[str]
    status: Optional[str] = None

class OrderBulkDeleteRequest(BaseModel):
    order_ids: List[str]

@api_router.post("/admin/orders/bulk-update")
async def bulk_update_orders(
    request: OrderBulkUpdateRequest,
    admin: User = Depends(get_admin_user)
):
    """Bulk update order status"""
    try:
        if not request.order_ids:
            raise HTTPException(status_code=400, detail="No order IDs provided")
        
        # Build update query
        update_data = {
            "updated_at": datetime.now(timezone.utc)
        }
        
        if request.status:
            update_data["status"] = request.status
            if request.status == "completed":
                update_data["completed_at"] = datetime.now(timezone.utc)
        
        # Update orders
        result = await db.orders.update_many(
            {"id": {"$in": request.order_ids}},
            {"$set": update_data}
        )
        
        return {
            "message": f"Successfully updated {result.modified_count} orders",
            "updated_count": result.modified_count,
            "status": request.status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update orders: {str(e)}")

@api_router.post("/admin/orders/bulk-delete")
async def bulk_delete_orders(
    request: OrderBulkDeleteRequest,
    admin: User = Depends(get_admin_user)
):
    """Bulk delete orders"""
    try:
        if not request.order_ids:
            raise HTTPException(status_code=400, detail="No order IDs provided")
        
        # Delete orders
        result = await db.orders.delete_many(
            {"id": {"$in": request.order_ids}}
        )
        
        return {
            "message": f"Successfully deleted {result.deleted_count} orders",
            "deleted_count": result.deleted_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete orders: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()