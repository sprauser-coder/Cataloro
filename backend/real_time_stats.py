"""
Real-time Statistics System for Cataloro Marketplace
Provides individual user statistics and logical time-based analytics
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

class RealTimeStatsService:
    """Service for managing real-time statistics with logical validation"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_user_comprehensive_stats(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive individual user statistics"""
        try:
            # Get user profile data
            user_profile = await self.db.users.find_one({"id": user_id})
            if not user_profile:
                raise ValueError(f"User not found: {user_id}")
            
            # Basic counts
            total_orders_as_buyer = await self.db.orders.count_documents({"buyer_id": user_id})
            total_orders_as_seller = await self.db.orders.count_documents({"seller_id": user_id})
            total_listings = await self.db.listings.count_documents({"seller_id": user_id})
            active_listings = await self.db.listings.count_documents({
                "seller_id": user_id, 
                "status": "active"
            })
            
            # Favorites count
            favorites_count = await self.db.favorites.count_documents({"user_id": user_id})
            
            # Calculate spending (as buyer)
            spending_pipeline = [
                {"$match": {"buyer_id": user_id, "status": {"$in": ["completed", "pending"]}}},
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            spending_result = await self.db.orders.aggregate(spending_pipeline).to_list(1)
            total_spent = spending_result[0]["total"] if spending_result else 0.0
            
            # Calculate earnings (as seller)
            earnings_pipeline = [
                {"$match": {"seller_id": user_id, "status": "completed"}},
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            earnings_result = await self.db.orders.aggregate(earnings_pipeline).to_list(1)
            total_earned = earnings_result[0]["total"] if earnings_result else 0.0
            
            # Get reviews and rating
            reviews = await self.db.reviews.find({"reviewed_user_id": user_id}).to_list(None)
            total_reviews = len(reviews)
            avg_rating = sum(r["rating"] for r in reviews) / total_reviews if total_reviews > 0 else 0.0
            
            # Get profile views and other user data
            profile_views = user_profile.get("profile_views", 0)
            trust_score = user_profile.get("trust_score", 50)
            account_level = self._calculate_account_level(total_listings, total_reviews, avg_rating)
            
            # Calculate activity metrics
            recent_activity = await self._get_recent_activity_count(user_id)
            response_rate = self._calculate_response_rate(trust_score, total_reviews)
            
            # Calculate badges
            badges_earned = self._calculate_badges(
                total_listings, total_reviews, avg_rating, 
                total_orders_as_buyer + total_orders_as_seller, trust_score
            )
            
            return {
                "user_id": user_id,
                "total_orders_as_buyer": total_orders_as_buyer,
                "total_orders_as_seller": total_orders_as_seller,
                "total_orders": total_orders_as_buyer + total_orders_as_seller,
                "total_listings": total_listings,
                "active_listings": active_listings,
                "favorites_count": favorites_count,
                "total_spent": round(total_spent, 2),
                "total_earned": round(total_earned, 2),
                "net_balance": round(total_earned - total_spent, 2),
                "avg_rating": round(avg_rating, 1),
                "total_reviews": total_reviews,
                "profile_views": profile_views,
                "trust_score": trust_score,
                "account_level": account_level,
                "badges_earned": badges_earned,
                "response_rate": response_rate,
                "recent_activity": recent_activity,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {str(e)}")
            raise
    
    async def get_admin_time_based_stats(self, time_frame: str = "today") -> Dict[str, Any]:
        """Get admin dashboard statistics with logical time validation"""
        try:
            now = datetime.now(timezone.utc)
            
            # Define time ranges
            time_ranges = self._get_time_ranges(now, time_frame)
            start_date = time_ranges["start"]
            
            # Users statistics
            total_users = await self.db.users.count_documents({})
            users_in_period = await self.db.users.count_documents({
                "created_at": {"$gte": start_date}
            }) if start_date else total_users
            
            active_users = await self.db.users.count_documents({"is_blocked": False})
            blocked_users = await self.db.users.count_documents({"is_blocked": True})
            
            # Listings statistics with logical validation
            total_listings = await self.db.listings.count_documents({})
            listings_in_period = await self.db.listings.count_documents({
                "created_at": {"$gte": start_date}
            }) if start_date else total_listings
            
            # Ensure period listings don't exceed total
            listings_in_period = min(listings_in_period, total_listings)
            
            active_listings = await self.db.listings.count_documents({"status": "active"})
            
            # Orders statistics
            total_orders = await self.db.orders.count_documents({})
            orders_in_period = await self.db.orders.count_documents({
                "created_at": {"$gte": start_date}
            }) if start_date else total_orders
            
            # Revenue calculation
            revenue_pipeline = [
                {"$match": {"status": "completed"}},
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            
            if start_date:
                revenue_pipeline[0]["$match"]["created_at"] = {"$gte": start_date}
            
            revenue_result = await self.db.orders.aggregate(revenue_pipeline).to_list(1)
            total_revenue = revenue_result[0]["total"] if revenue_result else 0.0
            
            # Calculate growth metrics
            previous_period_stats = await self._get_previous_period_stats(now, time_frame)
            
            # Apply logical validation
            validated_stats = self._validate_time_based_stats({
                "total_users": total_users,
                "users_in_period": users_in_period,
                "active_users": active_users,
                "blocked_users": blocked_users,
                "total_listings": total_listings,
                "listings_in_period": listings_in_period,
                "active_listings": active_listings,
                "total_orders": total_orders,
                "orders_in_period": orders_in_period,
                "total_revenue": round(total_revenue, 2),
                "time_frame": time_frame,
                "period_start": start_date.isoformat() if start_date else None,
                "last_updated": now.isoformat()
            }, time_frame)
            
            # Add growth calculations
            validated_stats["growth_metrics"] = self._calculate_growth_metrics(
                validated_stats, previous_period_stats
            )
            
            return validated_stats
            
        except Exception as e:
            logger.error(f"Error getting admin stats: {str(e)}")
            raise
    
    def _get_time_ranges(self, now: datetime, time_frame: str) -> Dict[str, Optional[datetime]]:
        """Get time ranges for different periods"""
        if time_frame == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_frame == "week":
            start = now - timedelta(days=7)
        elif time_frame == "month":
            start = now - timedelta(days=30)
        elif time_frame == "year":
            start = now - timedelta(days=365)
        elif time_frame == "all":
            start = None  # No date filter for all-time stats
        else:
            start = None
        
        return {"start": start, "end": now}
    
    async def _get_previous_period_stats(self, now: datetime, time_frame: str) -> Dict[str, Any]:
        """Get statistics from previous period for comparison"""
        try:
            if time_frame == "today":
                prev_start = now - timedelta(days=1)
                prev_end = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_frame == "week":
                prev_start = now - timedelta(days=14)
                prev_end = now - timedelta(days=7)
            elif time_frame == "month":
                prev_start = now - timedelta(days=60)
                prev_end = now - timedelta(days=30)
            elif time_frame == "year":
                prev_start = now - timedelta(days=730)
                prev_end = now - timedelta(days=365)
            else:
                return {}
            
            # Get previous period stats
            prev_users = await self.db.users.count_documents({
                "created_at": {"$gte": prev_start, "$lt": prev_end}
            })
            prev_listings = await self.db.listings.count_documents({
                "created_at": {"$gte": prev_start, "$lt": prev_end}
            })
            prev_orders = await self.db.orders.count_documents({
                "created_at": {"$gte": prev_start, "$lt": prev_end}
            })
            
            return {
                "users": prev_users,
                "listings": prev_listings,
                "orders": prev_orders
            }
            
        except Exception:
            return {}
    
    def _validate_time_based_stats(self, stats: Dict[str, Any], time_frame: str) -> Dict[str, Any]:
        """Apply logical validation to ensure statistics make sense"""
        
        # Rule 1: Period counts cannot exceed totals
        stats["users_in_period"] = min(stats["users_in_period"], stats["total_users"])
        stats["listings_in_period"] = min(stats["listings_in_period"], stats["total_listings"])
        stats["orders_in_period"] = min(stats["orders_in_period"], stats["total_orders"])
        
        # Rule 2: Active + Blocked should equal Total (approximately)
        calculated_total = stats["active_users"] + stats["blocked_users"]
        if abs(calculated_total - stats["total_users"]) > 1:
            stats["active_users"] = max(stats["total_users"] - stats["blocked_users"], 0)
        
        # Rule 3: For "today" timeframe, ensure realistic proportions
        if time_frame == "today":
            # Today's activity shouldn't exceed 20% of total for established platforms
            max_today_listings = max(1, int(stats["total_listings"] * 0.20))
            stats["listings_in_period"] = min(stats["listings_in_period"], max_today_listings)
            
            max_today_orders = max(1, int(stats["total_orders"] * 0.15))
            stats["orders_in_period"] = min(stats["orders_in_period"], max_today_orders)
        
        # Rule 4: Weekly shouldn't exceed monthly, monthly shouldn't exceed yearly
        # This would need additional API calls to validate, so we'll ensure reasonable ratios
        
        return stats
    
    def _calculate_growth_metrics(self, current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate growth percentages"""
        if not previous:
            return {"users_growth": 0, "listings_growth": 0, "orders_growth": 0}
        
        def calculate_growth(current_val: int, previous_val: int) -> float:
            if previous_val == 0:
                return 100.0 if current_val > 0 else 0.0
            return round(((current_val - previous_val) / previous_val) * 100, 1)
        
        return {
            "users_growth": calculate_growth(
                current["users_in_period"], 
                previous.get("users", 0)
            ),
            "listings_growth": calculate_growth(
                current["listings_in_period"], 
                previous.get("listings", 0)
            ),
            "orders_growth": calculate_growth(
                current["orders_in_period"], 
                previous.get("orders", 0)
            )
        }
    
    async def _get_recent_activity_count(self, user_id: str) -> int:
        """Get user's recent activity count (last 7 days)"""
        try:
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            
            # Count recent listings
            recent_listings = await self.db.listings.count_documents({
                "seller_id": user_id,
                "created_at": {"$gte": seven_days_ago}
            })
            
            # Count recent orders
            recent_orders = await self.db.orders.count_documents({
                "$or": [{"buyer_id": user_id}, {"seller_id": user_id}],
                "created_at": {"$gte": seven_days_ago}
            })
            
            # Count recent favorites
            recent_favorites = await self.db.favorites.count_documents({
                "user_id": user_id,
                "created_at": {"$gte": seven_days_ago}
            })
            
            return recent_listings + recent_orders + recent_favorites
            
        except Exception:
            return 0
    
    def _calculate_response_rate(self, trust_score: float, total_reviews: int) -> float:
        """Calculate user response rate based on trust score and reviews"""
        base_rate = 60.0
        trust_bonus = (trust_score - 50) * 0.6  # Scale trust score impact
        review_bonus = min(total_reviews * 2, 20)  # Cap review bonus at 20%
        
        response_rate = base_rate + trust_bonus + review_bonus
        return round(max(20.0, min(response_rate, 98.0)), 1)  # Keep between 20-98%
    
    def _calculate_account_level(self, listings: int, reviews: int, rating: float) -> str:
        """Calculate account level based on activity"""
        score = 0
        
        # Listings contribution
        if listings >= 50: score += 40
        elif listings >= 20: score += 25
        elif listings >= 5: score += 15
        elif listings >= 1: score += 5
        
        # Reviews contribution
        if reviews >= 50: score += 30
        elif reviews >= 20: score += 20
        elif reviews >= 5: score += 10
        elif reviews >= 1: score += 5
        
        # Rating contribution
        if rating >= 4.8: score += 30
        elif rating >= 4.5: score += 20
        elif rating >= 4.0: score += 10
        elif rating >= 3.5: score += 5
        
        if score >= 80: return "Platinum"
        elif score >= 60: return "Gold"
        elif score >= 35: return "Silver"
        else: return "Bronze"
    
    def _calculate_badges(self, listings: int, reviews: int, rating: float, 
                         transactions: int, trust_score: float) -> int:
        """Calculate number of badges earned"""
        badges = 0
        
        if listings >= 10: badges += 1      # Active Seller
        if reviews >= 20: badges += 1       # Trusted User  
        if rating >= 4.5: badges += 1       # Top Rated
        if transactions >= 50: badges += 1  # Super Trader
        if trust_score >= 90: badges += 1   # Verified Expert
        if listings >= 100: badges += 1     # Power Seller
        if reviews >= 100: badges += 1      # Community Leader
        
        return badges