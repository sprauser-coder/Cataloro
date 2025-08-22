from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
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

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET', 'your-secret-key')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
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
    
    # Create user
    user_dict = user_data.dict()
    del user_dict['password']
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
    if current_user.role not in [UserRole.SELLER, UserRole.BOTH]:
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

# Admin Models
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
    
    # Create admin user
    user_dict = admin_data.copy()
    del user_dict['password']
    admin_user = User(**user_dict)
    
    user_doc = prepare_for_mongo(admin_user.dict())
    user_doc['password'] = hashed_password
    
    await db.users.insert_one(user_doc)
    
    return {"message": "Default admin created", "email": "admin@marketplace.com", "password": "admin123"}

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