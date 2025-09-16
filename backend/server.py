"""
CATALORO - FastAPI Backend Server
Enhanced marketplace platform with comprehensive features
"""

# Core imports
import os
import json
import uuid
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
import logging
from contextlib import asynccontextmanager
import traceback

# FastAPI and related imports
from fastapi import FastAPI, HTTPException, Depends, status, Request, Response, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Database imports  
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
import motor.motor_asyncio

# Pydantic models
from pydantic import BaseModel, Field, EmailStr, validator
from typing_extensions import Annotated

# Authentication and security
from passlib.context import CryptContext
from jose import JWTError, jwt
import bcrypt

# LLM Integration
from emergentintegrations.llm.chat import LlmChat, UserMessage
from monitoring_service import monitoring_service, MonitoringMiddleware

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'cataloro_marketplace')

# Initialize database client
client = AsyncIOMotorClient(MONGO_URL)
db: AsyncIOMotorDatabase = client[DATABASE_NAME]

# JWT Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

# Global services (will be initialized in startup)
cache_service = None
search_service = None
analytics_service = None
websocket_service = None
multicurrency_service = None
escrow_service = None
ai_recommendation_service = None

# FastAPI app
app = FastAPI(
    title="Cataloro Marketplace API",
    description="Enhanced marketplace platform with comprehensive features",
    version="2.0.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    MonitoringMiddleware,
    monitoring_service=monitoring_service
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Basic Models
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    user_type: str = Field(default="buyer", regex="^(buyer|seller|admin)$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    user_id: str
    created_at: datetime
    is_active: bool = True
    profile_picture: Optional[str] = None
    verification_status: str = "pending"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Authentication functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user from database
        user = await db.users.find_one({"user_id": user_id})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# Helper function to prepare user data
def prepare_user_response(user_data: dict) -> dict:
    """Prepare user data for response"""
    if '_id' in user_data:
        del user_data['_id']
    if 'password' in user_data:
        del user_data['password']
    
    return user_data

# Startup and Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Cataloro Marketplace API...")
    
    # Initialize cache service
    await init_cache()
    
    # Initialize search service
    await init_search()
    
    # Initialize analytics service
    global analytics_service
    analytics_service = await create_analytics_service(db)
    logger.info("✅ Analytics service initialized")
    
    # Initialize Phase 5 services
    global websocket_service, multicurrency_service, escrow_service, ai_recommendation_service
    
    websocket_service = await init_websocket_service(db)
    logger.info("✅ WebSocket service initialized")
    
    multicurrency_service = await init_multicurrency_service(db)
    logger.info("✅ Multi-currency service initialized")
    
    escrow_service = await init_escrow_service(db)
    logger.info("✅ Escrow service initialized")
    
    ai_recommendation_service = await init_ai_recommendation_service(db)
    logger.info("✅ AI Recommendation service initialized")
    
    # Start monitoring service
    await monitoring_service.start_monitoring()
    logger.info("✅ Monitoring service started")
    
    # Run database optimization (indexes) on startup
    try:
        from optimize_database import create_database_indexes
        await create_database_indexes()
        logger.info("✅ Database indexes optimized")
    except Exception as e:
        logger.warning(f"⚠️ Database optimization skipped: {e}")

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Cataloro Marketplace API...")

# Basic health endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        await client.admin.command('ping')
        
        # Get monitoring status
        health_status = monitoring_service.get_health_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "connected",
            "monitoring": health_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "disconnected",
            "error": str(e)
        }

# Authentication endpoints
@app.post("/api/auth/register", response_model=Token)
async def register_user(user: UserCreate):
    """Register a new user"""
    try:
        # Check if user exists
        existing_user = await db.users.find_one({
            "$or": [
                {"email": user.email},
                {"username": user.username}
            ]
        })
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )
        
        # Create user
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user.password)
        
        user_data = {
            "user_id": user_id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "user_type": user.user_type,
            "password": hashed_password,
            "created_at": datetime.now(timezone.utc),
            "is_active": True,
            "verification_status": "pending",
            "profile_picture": None
        }
        
        await db.users.insert_one(user_data)
        
        # Create access token
        access_token = create_access_token(data={"sub": user_id})
        
        # Prepare response
        user_response = UserResponse(**{k: v for k, v in user_data.items() if k != 'password'})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@app.post("/api/auth/login", response_model=Token)
async def login_user(user: UserLogin):
    """Login user"""
    try:
        # Find user
        db_user = await db.users.find_one({"email": user.email})
        
        if not db_user or not verify_password(user.password, db_user['password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not db_user.get('is_active', True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": db_user['user_id']})
        
        # Prepare response
        user_response = UserResponse(**{k: v for k, v in db_user.items() if k not in ['password', '_id']})
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

# Protected route example
@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    try:
        return UserResponse(**{k: v for k, v in current_user.items() if k not in ['password', '_id']})
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

# Monitoring endpoints
@app.get("/api/monitoring/health")
async def get_detailed_health():
    """Get detailed health and monitoring information"""
    return monitoring_service.get_health_status()

@app.get("/api/monitoring/performance")
async def get_performance_metrics():
    """Get performance metrics"""
    return monitoring_service.get_performance_summary()

@app.get("/api/monitoring/errors")
async def get_error_metrics():
    """Get error metrics"""
    return monitoring_service.get_error_summary()

@app.get("/api/monitoring/system")
async def get_system_metrics():
    """Get system metrics"""
    return monitoring_service.get_system_summary()

# Placeholder service initialization functions
async def init_cache():
    """Initialize cache service"""
    pass

async def init_search():
    """Initialize search service"""
    pass

async def create_analytics_service(db):
    """Create analytics service"""
    return {}

async def init_websocket_service(db):
    """Initialize websocket service"""
    return {}

async def init_multicurrency_service(db):
    """Initialize multicurrency service"""
    return {}

async def init_escrow_service(db):
    """Initialize escrow service"""
    return {}

async def init_ai_recommendation_service(db):
    """Initialize AI recommendation service"""
    return {}

# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    try:
        # Test database connection
        await client.admin.command('ping')
        logger.info("✅ Database connected successfully")
        
        # Initialize monitoring
        await monitoring_service.start_monitoring()
        logger.info("✅ Monitoring initialized")
        
        # Create indexes
        await create_indexes()
        logger.info("✅ Database indexes created")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

async def create_indexes():
    """Create database indexes"""
    try:
        # User indexes
        await db.users.create_index("user_id", unique=True)
        await db.users.create_index("email", unique=True)
        await db.users.create_index("username", unique=True)
        
        logger.info("✅ Database indexes created")
    except Exception as e:
        logger.error(f"Index creation error: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )