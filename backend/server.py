from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import motor.motor_asyncio
import os
import uuid
import redis
import json
from contextlib import asynccontextmanager

# Database and Cache setup
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.cataloro_marketplace

# Redis setup
try:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    REDIS_AVAILABLE = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Cataloro Marketplace API")
    print(f"📊 MongoDB: {MONGO_URL}")
    print(f"🔴 Redis: {'✅ Available' if REDIS_AVAILABLE else '❌ Unavailable'}")
    
    # Initialize database with sample data
    await initialize_database()
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Cataloro Marketplace API")

app = FastAPI(
    title="Cataloro Marketplace API",
    description="Clean, optimized marketplace API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class Listing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    price: float
    category: str = "Catalysts"
    condition: str = "New"
    seller_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "active"
    images: List[str] = []
    
    # Address
    street: str = ""
    post_code: str = ""
    city: str = ""
    country: str = ""
    
    # Catalyst specific
    catalyst_id: Optional[str] = None
    catalyst_name: Optional[str] = None
    ceramic_weight: float = 0.0
    pt_g: float = 0.0
    pd_g: float = 0.0
    rh_g: float = 0.0

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    name: str = ""
    is_business: bool = False
    business_name: str = ""
    verified: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    city: str = ""
    country: str = ""

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database: str
    cache: str

# Database initialization
async def initialize_database():
    """Initialize database with sample data"""
    try:
        # Check if we already have data
        user_count = await db.users.count_documents({})
        listing_count = await db.listings.count_documents({})
        
        if user_count > 0 and listing_count > 0:
            print(f"📊 Database already initialized: {user_count} users, {listing_count} listings")
            return
            
        print("🔄 Initializing database with sample data...")
        
        # Create sample users
        sample_users = [
            {
                "id": "demo_user_1",
                "username": "demo_user",
                "email": "demo@cataloro.com",
                "name": "Demo User",
                "is_business": False,
                "verified": True,
                "created_at": datetime.now(timezone.utc),
                "city": "Berlin",
                "country": "Germany"
            },
            {
                "id": "seller_user_1", 
                "username": "catalyst_seller",
                "email": "seller@cataloro.com",
                "name": "Catalyst Seller",
                "is_business": True,
                "business_name": "Catalyst Solutions GmbH",
                "verified": True,
                "created_at": datetime.now(timezone.utc),
                "city": "Munich",
                "country": "Germany"
            }
        ]
        
        await db.users.insert_many(sample_users)
        
        # Create sample listings
        sample_listings = [
            {
                "id": str(uuid.uuid4()),
                "title": "BMW 320d Catalytic Converter",
                "description": "High-quality catalytic converter for BMW 320d. Contains precious metals: Pt: 1.2g, Pd: 2.4g, Rh: 0.3g. Excellent condition.",
                "price": 450.00,
                "category": "Catalysts",
                "condition": "Used",
                "seller_id": "seller_user_1",
                "created_at": datetime.now(timezone.utc),
                "status": "active",
                "street": "Hauptstraße 123",
                "post_code": "80331",
                "city": "Munich", 
                "country": "Germany",
                "catalyst_id": "BMW320D_CAT_001",
                "catalyst_name": "BMW 320d Catalyst",
                "ceramic_weight": 1.5,
                "pt_g": 1.2,
                "pd_g": 2.4,
                "rh_g": 0.3,
                "images": []
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Mercedes E-Class Catalyst",
                "description": "Original Mercedes E-Class catalytic converter. Premium quality with high precious metal content.",
                "price": 680.00,
                "category": "Catalysts", 
                "condition": "Used",
                "seller_id": "seller_user_1",
                "created_at": datetime.now(timezone.utc),
                "status": "active",
                "street": "Berliner Str. 45",
                "post_code": "10117",
                "city": "Berlin",
                "country": "Germany",
                "catalyst_id": "MERC_ECLASS_001",
                "catalyst_name": "Mercedes E-Class Catalyst",
                "ceramic_weight": 2.1,
                "pt_g": 1.8,
                "pd_g": 3.2,
                "rh_g": 0.5,
                "images": []
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Audi A4 Catalytic Converter", 
                "description": "Audi A4 catalyst in good condition. Tested and verified precious metal content.",
                "price": 520.00,
                "category": "Catalysts",
                "condition": "Used", 
                "seller_id": "seller_user_1",
                "created_at": datetime.now(timezone.utc),
                "status": "active",
                "street": "Königsallee 67",
                "post_code": "40212", 
                "city": "Düsseldorf",
                "country": "Germany",
                "catalyst_id": "AUDI_A4_001",
                "catalyst_name": "Audi A4 Catalyst",
                "ceramic_weight": 1.8,
                "pt_g": 1.5,
                "pd_g": 2.8,
                "rh_g": 0.4,
                "images": []
            }
        ]
        
        await db.listings.insert_many(sample_listings)
        
        # Create indexes for performance
        await db.listings.create_index("seller_id")
        await db.listings.create_index("status")
        await db.listings.create_index("category")
        await db.listings.create_index("created_at")
        await db.users.create_index("username", unique=True)
        await db.users.create_index("email", unique=True)
        
        print(f"✅ Database initialized successfully: {len(sample_users)} users, {len(sample_listings)} listings")
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")

# Helper functions
def cache_get(key: str):
    """Get from Redis cache"""
    if not REDIS_AVAILABLE:
        return None
    try:
        return redis_client.get(key)
    except:
        return None

def cache_set(key: str, value: str, ttl: int = 300):
    """Set to Redis cache"""
    if not REDIS_AVAILABLE:
        return False
    try:
        return redis_client.setex(key, ttl, value)
    except:
        return False

async def enrich_listings_with_seller_info(listings: List[dict]) -> List[dict]:
    """Enrich listings with seller information using batch fetching"""
    if not listings:
        return []
    
    # Get unique seller IDs
    seller_ids = list(set([listing.get('seller_id') for listing in listings if listing.get('seller_id')]))
    
    # Batch fetch seller information
    sellers_cursor = db.users.find({"id": {"$in": seller_ids}})
    sellers = await sellers_cursor.to_list(length=None)
    
    # Create seller lookup dictionary
    seller_lookup = {seller['id']: seller for seller in sellers}
    
    # Enrich listings
    enriched_listings = []
    for listing in listings:
        seller_id = listing.get('seller_id')
        seller_info = seller_lookup.get(seller_id, {})
        
        # Add seller info
        listing['seller'] = {
            'name': seller_info.get('name', 'Unknown'),
            'username': seller_info.get('username', 'unknown'),
            'email': seller_info.get('email', ''),
            'is_business': seller_info.get('is_business', False),
            'business_name': seller_info.get('business_name', ''),
            'verified': seller_info.get('verified', False),
            'city': seller_info.get('city', ''),
            'country': seller_info.get('country', ''),
            'location': f"{seller_info.get('city', '')}, {seller_info.get('country', '')}".strip(', ')
        }
        
        # Add address info
        listing['address'] = {
            'street': listing.get('street', ''),
            'post_code': listing.get('post_code', ''),
            'city': listing.get('city', ''),
            'country': listing.get('country', ''),
            'use_profile_address': True
        }
        
        # Add bid info (placeholder)
        listing['bid_info'] = {
            'has_bids': False,
            'total_bids': 0,
            'highest_bid': listing.get('price', 0) * 0.85,  # 85% of listing price
            'highest_bidder_id': ''
        }
        
        # Add time info (placeholder)
        listing['time_info'] = {
            'has_time_limit': False,
            'is_expired': False,
            'time_remaining_seconds': 0,
            'expires_at': None,
            'status_text': 'No time limit'
        }
        
        # Add catalyst specs
        if listing.get('catalyst_id'):
            listing['catalyst_specs'] = {
                'weight': listing.get('ceramic_weight', 0),
                'total_price': listing.get('price', 0),
                'pt_g': listing.get('pt_g', 0),
                'pd_g': listing.get('pd_g', 0),
                'rh_g': listing.get('rh_g', 0),
                'is_override': False
            }
            listing['is_catalyst_listing'] = True
            listing['calculated_price'] = listing.get('price', 0)
        
        # Add additional fields
        listing['views'] = 0
        listing['favorites_count'] = 0
        listing['expires_at'] = None
        listing['is_expired'] = False
        listing['winning_bidder_id'] = None
        listing['updated_at'] = listing.get('created_at', datetime.now(timezone.utc))
        
        enriched_listings.append(listing)
    
    return enriched_listings

# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    return {"message": "Cataloro Marketplace API v2.0", "status": "running"}

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    
    # Check database
    try:
        await db.admin.command('ping')
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    # Check cache
    cache_status = "connected" if REDIS_AVAILABLE else "unavailable"
    
    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        timestamp=datetime.now(timezone.utc).isoformat(),
        database=db_status,
        cache=cache_status
    )

@app.get("/api/marketplace/browse")
async def browse_listings(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    seller_type: Optional[str] = None
):
    """Browse marketplace listings with optimized performance"""
    
    try:
        # Create cache key
        cache_key = f"browse_v4_{page}_{limit}_{category}_{min_price}_{max_price}_{seller_type}"
        
        # Try cache first
        cached_result = cache_get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Build query
        query = {"status": "active"}
        
        if category:
            query["category"] = category
            
        if min_price is not None or max_price is not None:
            price_query = {}
            if min_price is not None:
                price_query["$gte"] = min_price
            if max_price is not None:
                price_query["$lte"] = max_price
            query["price"] = price_query
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Execute query with sorting
        cursor = db.listings.find(query).sort("created_at", -1).skip(skip).limit(limit)
        listings = await cursor.to_list(length=None)
        
        # Enrich with seller information using batch fetching
        enriched_listings = await enrich_listings_with_seller_info(listings)
        
        # Apply seller type filter after enrichment (if needed)
        if seller_type:
            if seller_type == "business":
                enriched_listings = [l for l in enriched_listings if l['seller']['is_business']]
            elif seller_type == "individual":
                enriched_listings = [l for l in enriched_listings if not l['seller']['is_business']]
        
        # Cache result
        cache_set(cache_key, json.dumps(enriched_listings, default=str), ttl=300)
        
        return enriched_listings
        
    except Exception as e:
        print(f"Error in browse_listings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching listings: {str(e)}")

@app.get("/api/listings")
async def get_listings(user_id: Optional[str] = None):
    """Get listings, optionally filtered by user"""
    
    try:
        query = {"status": "active"}
        if user_id:
            query["seller_id"] = user_id
            
        cursor = db.listings.find(query).sort("created_at", -1)
        listings = await cursor.to_list(length=None)
        
        return listings
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching listings: {str(e)}")

@app.post("/api/listings")
async def create_listing(listing: Listing):
    """Create a new listing"""
    
    try:
        listing_dict = listing.dict()
        listing_dict['created_at'] = datetime.now(timezone.utc)
        
        result = await db.listings.insert_one(listing_dict)
        
        if result.inserted_id:
            return {"id": listing.id, "status": "created"}
        else:
            raise HTTPException(status_code=400, detail="Failed to create listing")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating listing: {str(e)}")

@app.get("/api/listings/{listing_id}")
async def get_listing(listing_id: str):
    """Get a specific listing"""
    
    try:
        listing = await db.listings.find_one({"id": listing_id})
        
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
            
        # Enrich with seller info
        enriched_listings = await enrich_listings_with_seller_info([listing])
        
        return enriched_listings[0] if enriched_listings else listing
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching listing: {str(e)}")

@app.get("/api/users")
async def get_users():
    """Get all users"""
    
    try:
        cursor = db.users.find({}).sort("created_at", -1)
        users = await cursor.to_list(length=None)
        return users
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@app.post("/api/users")
async def create_user(user: User):
    """Create a new user"""
    
    try:
        user_dict = user.dict()
        user_dict['created_at'] = datetime.now(timezone.utc)
        
        result = await db.users.insert_one(user_dict)
        
        if result.inserted_id:
            return {"id": user.id, "status": "created"}
        else:
            raise HTTPException(status_code=400, detail="Failed to create user")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@app.get("/api/admin/dashboard")
async def admin_dashboard():
    """Admin dashboard data"""
    
    try:
        # Get counts
        user_count = await db.users.count_documents({})
        listing_count = await db.listings.count_documents({"status": "active"})
        
        # Calculate total revenue (sum of all listing prices)
        pipeline = [
            {"$match": {"status": "active"}},
            {"$group": {"_id": None, "total": {"$sum": "$price"}}}
        ]
        revenue_result = await db.listings.aggregate(pipeline).to_list(length=1)
        total_revenue = revenue_result[0]['total'] if revenue_result else 0
        
        return {
            "total_users": user_count,
            "active_listings": listing_count,
            "total_revenue": total_revenue,
            "conversion_rate": 85.5,  # Mock data
            "system_health": {
                "cpu": 15,
                "memory": 45,
                "storage": 30
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard data: {str(e)}")

# Authentication endpoints (simplified)
@app.post("/api/auth/login")
async def login(credentials: dict):
    """Simple login endpoint"""
    return {
        "access_token": "demo_token_" + str(uuid.uuid4()),
        "token_type": "bearer",
        "user": {
            "id": "demo_user_1",
            "username": "demo_user",
            "email": "demo@cataloro.com"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)