from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, File, UploadFile
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
    user_id: str = Field(default="")  # Auto-generated friendly ID like USER001
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    address: Optional[str] = None
    rating: float = Field(default=0.0)
    total_reviews: int = Field(default=0)
    is_blocked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)

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
    users = await db.users.find({"user_id": {"$regex": "^USER\\d+$"}}).to_list(length=None)
    
    if not users:
        return "USER001"
    
    # Extract numbers from user_ids and find the maximum
    max_num = 0
    for user in users:
        user_id = user.get('user_id', '')
        if user_id.startswith('USER') and user_id[4:].isdigit():
            num = int(user_id[4:])
            max_num = max(max_num, num)
    
    # Return next sequential ID
    next_num = max_num + 1
    return f"USER{next_num:03d}"

def prepare_for_mongo(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item, dict):
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

# Listing Routes
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
    limit: int = 20,
    skip: int = 0
):
    query = {"status": ListingStatus.ACTIVE}
    
    if category:
        query["category"] = category
    if listing_type:
        query["listing_type"] = listing_type
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Price filtering
    if min_price is not None or max_price is not None:
        price_query = {}
        if min_price is not None:
            price_query["$gte"] = min_price
        if max_price is not None:
            price_query["$lte"] = max_price
        query["$or"] = [
            {"price": price_query},
            {"current_bid": price_query}
        ]
    
    listings = await db.listings.find(query).skip(skip).limit(limit).to_list(length=None)
    return [ProductListing(**parse_from_mongo(listing)) for listing in listings]

@api_router.get("/listings/{listing_id}", response_model=ProductListing)
async def get_listing(listing_id: str):
    listing = await db.listings.find_one({"id": listing_id})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Increment views
    await db.listings.update_one({"id": listing_id}, {"$inc": {"views": 1}})
    
    return ProductListing(**parse_from_mongo(listing))

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
    
    # Create order
    order_dict = order_data.dict()
    order_dict['buyer_id'] = current_user.id
    order_dict['seller_id'] = listing_obj.seller_id
    order_dict['total_amount'] = total_amount
    
    order = Order(**order_dict)
    order_doc = prepare_for_mongo(order.dict())
    
    await db.orders.insert_one(order_doc)
    
    # Update listing status if sold out
    if order_data.quantity >= listing_obj.quantity:
        await db.listings.update_one(
            {"id": order_data.listing_id},
            {"$set": {"status": ListingStatus.SOLD}}
        )
    
    # Remove from cart if exists
    await db.cart_items.delete_many({"user_id": current_user.id, "listing_id": order_data.listing_id})
    
    return order

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
    return {"message": "Marketplace API"}

# ===========================
# ADMIN ROUTES
# ===========================

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

# Admin Order Management
@api_router.get("/admin/orders")
async def get_all_orders(admin: User = Depends(get_admin_user)):
    """Get all orders for admin management"""
    orders = await db.orders.find({}).sort("created_at", -1).to_list(length=None)
    
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
@api_router.get("/admin/cms/settings")
async def get_site_settings(admin: User = Depends(get_admin_user)):
    """Get current site settings"""
    settings = await db.site_settings.find_one({})
    if not settings:
        # Create default settings with all fields
        default_settings = SiteSettings()
        settings_doc = prepare_for_mongo(default_settings.dict(exclude_unset=False))
        await db.site_settings.insert_one(settings_doc)
        return default_settings.dict(exclude_unset=False)
    
    # Parse the database settings and return as SiteSettings instance
    parsed_settings = parse_from_mongo(settings)
    
    # Create instance - missing fields will use defaults from Pydantic model
    site_settings = SiteSettings(**parsed_settings)
    return site_settings.dict(exclude_unset=False)

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
        print(f"DEBUG: Created default settings with {len(current_settings)} fields")
    else:
        current_settings = parse_from_mongo(current_settings)
        print(f"DEBUG: Found existing settings with {len(current_settings)} fields")
    
    # Update current settings with new data
    current_settings.update(settings_data)
    print(f"DEBUG: After update, settings has {len(current_settings)} fields")
    print(f"DEBUG: font_color in current_settings: {current_settings.get('font_color')}")
    
    # Ensure all fields are present by creating SiteSettings instance
    try:
        updated_settings = SiteSettings(**current_settings)
        print(f"DEBUG: SiteSettings instance created successfully")
        print(f"DEBUG: updated_settings.font_color: {updated_settings.font_color}")
        settings_doc = prepare_for_mongo(updated_settings.dict(exclude_unset=False))
        print(f"DEBUG: Final document has {len(settings_doc)} fields")
        print(f"DEBUG: font_color in final doc: {settings_doc.get('font_color')}")
    except Exception as e:
        print(f"DEBUG: Error creating SiteSettings instance: {e}")
        return {"error": str(e)}
    
    # Replace the entire document to ensure all fields are saved
    result = await db.site_settings.replace_one(
        {},
        settings_doc,
        upsert=True
    )
    
    print(f"DEBUG: Database operation result: matched={result.matched_count}, modified={result.modified_count}")
    
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
        return SiteSettings().dict()
    return SiteSettings(**parse_from_mongo(settings)).dict()

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