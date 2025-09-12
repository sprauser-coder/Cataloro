"""
AI Recommendation Service for Cataloro Marketplace - Phase 5C
Machine learning-powered product recommendations and personalization
"""

import asyncio
import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import uuid
import math

logger = logging.getLogger(__name__)

class AIRecommendationService:
    def __init__(self, db):
        self.db = db
        
        # Recommendation configuration
        self.min_interactions = 3  # Minimum interactions for recommendations
        self.max_recommendations = 20
        self.similarity_threshold = 0.1
        self.decay_factor = 0.95  # Decay for older interactions
        
        # Feature weights for similarity calculation
        self.feature_weights = {
            "category": 0.3,
            "price_range": 0.2,
            "condition": 0.15,
            "seller_type": 0.1,
            "location": 0.1,
            "keywords": 0.15
        }
        
        # User behavior tracking
        self.user_profiles = {}  # user_id -> profile data
        self.item_profiles = {}  # listing_id -> item features
        self.interaction_matrix = {}  # user_id -> {listing_id -> score}
        
        # Recommendation cache
        self.recommendation_cache = {}
        self.cache_duration = 3600  # 1 hour
        
        logger.info("✅ AI Recommendation service initialized")
    
    async def track_user_interaction(
        self,
        user_id: str,
        listing_id: str,
        interaction_type: str,
        context: Dict = None
    ):
        """Track user interactions for learning"""
        try:
            # Interaction weights
            interaction_weights = {
                "view": 1.0,
                "like": 2.0,
                "message": 3.0,
                "bid": 4.0,
                "purchase": 5.0,
                "share": 1.5,
                "save": 2.5
            }
            
            weight = interaction_weights.get(interaction_type, 1.0)
            
            # Store interaction
            interaction_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "listing_id": listing_id,
                "interaction_type": interaction_type,
                "weight": weight,
                "context": context or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.db.user_interactions.insert_one(interaction_data)
            
            # Update in-memory tracking
            if user_id not in self.interaction_matrix:
                self.interaction_matrix[user_id] = {}
            
            if listing_id not in self.interaction_matrix[user_id]:
                self.interaction_matrix[user_id][listing_id] = 0
            
            self.interaction_matrix[user_id][listing_id] += weight
            
            # Update user profile
            await self._update_user_profile(user_id, listing_id, interaction_type, weight)
            
        except Exception as e:
            logger.error(f"Failed to track user interaction: {e}")
    
    async def get_personalized_recommendations(
        self,
        user_id: str,
        limit: int = 10,
        exclude_own: bool = True
    ) -> List[Dict]:
        """Get personalized recommendations for a user"""
        try:
            # Check cache first
            cache_key = f"{user_id}_{limit}_{exclude_own}"
            if cache_key in self.recommendation_cache:
                cached_data = self.recommendation_cache[cache_key]
                if (datetime.utcnow() - cached_data["timestamp"]).seconds < self.cache_duration:
                    return cached_data["recommendations"]
            
            # Get user profile
            user_profile = await self._get_user_profile(user_id)
            if not user_profile:
                # New user - return popular items
                return await self._get_popular_recommendations(limit)
            
            # Get candidate listings
            candidate_listings = await self._get_candidate_listings(user_id, exclude_own)
            
            if not candidate_listings:
                return await self._get_popular_recommendations(limit)
            
            # Calculate recommendation scores
            scored_recommendations = []
            
            for listing in candidate_listings:
                # Content-based score
                content_score = await self._calculate_content_similarity(user_profile, listing)
                
                # Collaborative filtering score
                collaborative_score = await self._calculate_collaborative_score(user_id, listing["id"])
                
                # Popularity score
                popularity_score = await self._calculate_popularity_score(listing["id"])
                
                # Freshness score
                freshness_score = self._calculate_freshness_score(listing)
                
                # Combined score
                final_score = (
                    content_score * 0.4 +
                    collaborative_score * 0.3 +
                    popularity_score * 0.2 +
                    freshness_score * 0.1
                )
                
                if final_score > self.similarity_threshold:
                    scored_recommendations.append({
                        "listing": listing,
                        "score": final_score,
                        "reasons": self._generate_recommendation_reasons(
                            user_profile, listing, content_score, collaborative_score
                        )
                    })
            
            # Sort by score and return top N
            scored_recommendations.sort(key=lambda x: x["score"], reverse=True)
            recommendations = scored_recommendations[:limit]
            
            # Cache results
            self.recommendation_cache[cache_key] = {
                "recommendations": recommendations,
                "timestamp": datetime.utcnow()
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get personalized recommendations: {e}")
            return await self._get_popular_recommendations(limit)
    
    async def get_similar_items(
        self,
        listing_id: str,
        limit: int = 5
    ) -> List[Dict]:
        """Get items similar to a specific listing"""
        try:
            # Get the reference listing
            reference_listing = await self.db.listings.find_one({"id": listing_id})
            if not reference_listing:
                return []
            
            # Get candidate listings from same category
            candidates = await self.db.listings.find({
                "id": {"$ne": listing_id},
                "status": "active",
                "category": reference_listing.get("category")
            }).limit(100).to_list(length=None)
            
            if not candidates:
                return []
            
            similar_items = []
            
            for candidate in candidates:
                similarity_score = await self._calculate_item_similarity(reference_listing, candidate)
                
                if similarity_score > self.similarity_threshold:
                    similar_items.append({
                        "listing": self._serialize_listing(candidate),
                        "similarity_score": similarity_score,
                        "similarity_reasons": self._get_similarity_reasons(reference_listing, candidate)
                    })
            
            # Sort by similarity
            similar_items.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return similar_items[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get similar items: {e}")
            return []
    
    async def get_trending_items(
        self,
        category: str = None,
        timeframe_hours: int = 24,
        limit: int = 10
    ) -> List[Dict]:
        """Get trending items based on recent interactions"""
        try:
            # Calculate time threshold
            threshold_time = datetime.utcnow() - timedelta(hours=timeframe_hours)
            
            # Aggregate interactions
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": threshold_time.isoformat()}
                    }
                },
                {
                    "$group": {
                        "_id": "$listing_id",
                        "interaction_count": {"$sum": 1},
                        "weighted_score": {"$sum": "$weight"},
                        "unique_users": {"$addToSet": "$user_id"}
                    }
                },
                {
                    "$addFields": {
                        "unique_user_count": {"$size": "$unique_users"},
                        "trending_score": {
                            "$multiply": ["$weighted_score", {"$size": "$unique_users"}]
                        }
                    }
                },
                {"$sort": {"trending_score": -1}},
                {"$limit": limit * 2}  # Get more to filter by category
            ]
            
            trending_data = await self.db.user_interactions.aggregate(pipeline).to_list(length=None)
            
            if not trending_data:
                return await self._get_popular_recommendations(limit)
            
            # Get listing details and filter by category if specified
            trending_items = []
            
            for item in trending_data:
                listing = await self.db.listings.find_one({"id": item["_id"], "status": "active"})
                if listing and (not category or listing.get("category") == category):
                    trending_items.append({
                        "listing": self._serialize_listing(listing),
                        "trending_score": item["trending_score"],
                        "interaction_count": item["interaction_count"],
                        "unique_users": item["unique_user_count"]
                    })
                
                if len(trending_items) >= limit:
                    break
            
            return trending_items
            
        except Exception as e:
            logger.error(f"Failed to get trending items: {e}")
            return []
    
    async def get_user_based_recommendations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get recommendations based on similar users"""
        try:
            # Find similar users
            similar_users = await self._find_similar_users(user_id)
            
            if not similar_users:
                return []
            
            # Get items liked by similar users
            recommendations = []
            processed_listings = set()
            
            for similar_user_id, similarity_score in similar_users[:5]:  # Top 5 similar users
                # Get their highly rated items
                user_interactions = self.interaction_matrix.get(similar_user_id, {})
                
                for listing_id, interaction_score in sorted(
                    user_interactions.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:10]:
                    
                    if listing_id in processed_listings:
                        continue
                    
                    # Skip if current user already interacted with this item
                    if user_id in self.interaction_matrix and listing_id in self.interaction_matrix[user_id]:
                        continue
                    
                    listing = await self.db.listings.find_one({"id": listing_id, "status": "active"})
                    if listing:
                        recommendations.append({
                            "listing": self._serialize_listing(listing),
                            "recommendation_score": similarity_score * interaction_score,
                            "reason": f"Users with similar interests also liked this",
                            "similar_user_score": similarity_score
                        })
                        processed_listings.add(listing_id)
            
            # Sort by recommendation score
            recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get user-based recommendations: {e}")
            return []
    
    async def get_category_recommendations(
        self,
        user_id: str,
        category: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get recommendations within a specific category"""
        try:
            user_profile = await self._get_user_profile(user_id)
            
            # Get active listings in category
            category_listings = await self.db.listings.find({
                "category": category,
                "status": "active"
            }).limit(50).to_list(length=None)
            
            if not category_listings:
                return []
            
            scored_items = []
            
            for listing in category_listings:
                # Skip own listings
                if listing.get("seller_id") == user_id:
                    continue
                
                # Calculate relevance score
                if user_profile:
                    relevance_score = await self._calculate_content_similarity(user_profile, listing)
                else:
                    relevance_score = 0.5  # Default for new users
                
                # Add popularity boost
                popularity_score = await self._calculate_popularity_score(listing["id"])
                final_score = relevance_score * 0.7 + popularity_score * 0.3
                
                scored_items.append({
                    "listing": self._serialize_listing(listing),
                    "relevance_score": final_score,
                    "category": category
                })
            
            # Sort and return top items
            scored_items.sort(key=lambda x: x["relevance_score"], reverse=True)
            return scored_items[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get category recommendations: {e}")
            return []
    
    async def _get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get or build user profile"""
        try:
            if user_id in self.user_profiles:
                return self.user_profiles[user_id]
            
            # Build profile from interactions
            interactions = await self.db.user_interactions.find({
                "user_id": user_id
            }).sort("timestamp", -1).limit(100).to_list(length=None)
            
            if len(interactions) < self.min_interactions:
                return None
            
            # Analyze preferences
            category_scores = defaultdict(float)
            price_ranges = []
            condition_scores = defaultdict(float)
            keyword_scores = defaultdict(float)
            
            total_weight = 0
            
            for interaction in interactions:
                weight = interaction["weight"]
                total_weight += weight
                
                # Get listing details
                listing = await self.db.listings.find_one({"id": interaction["listing_id"]})
                if not listing:
                    continue
                
                # Category preferences
                category = listing.get("category", "unknown")
                category_scores[category] += weight
                
                # Price preferences
                price = listing.get("price", 0)
                price_ranges.append(price)
                
                # Condition preferences
                condition = listing.get("condition", "unknown")
                condition_scores[condition] += weight
                
                # Extract keywords from title and description
                title = listing.get("title", "").lower()
                description = listing.get("description", "").lower()
                
                for word in (title + " " + description).split():
                    if len(word) > 3:  # Skip short words
                        keyword_scores[word] += weight
            
            if total_weight == 0:
                return None
            
            # Normalize scores
            for category in category_scores:
                category_scores[category] /= total_weight
            
            for condition in condition_scores:
                condition_scores[condition] /= total_weight
            
            for keyword in keyword_scores:
                keyword_scores[keyword] /= total_weight
            
            # Calculate preferred price range
            if price_ranges:
                avg_price = np.mean(price_ranges)
                std_price = np.std(price_ranges)
                preferred_price_range = {
                    "min": max(0, avg_price - std_price),
                    "max": avg_price + std_price,
                    "average": avg_price
                }
            else:
                preferred_price_range = {"min": 0, "max": 999999, "average": 0}
            
            # Build profile
            profile = {
                "user_id": user_id,
                "categories": dict(category_scores),
                "conditions": dict(condition_scores),
                "price_range": preferred_price_range,
                "keywords": dict(sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)[:20]),
                "total_interactions": len(interactions),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Cache profile
            self.user_profiles[user_id] = profile
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    async def _calculate_content_similarity(
        self,
        user_profile: Dict,
        listing: Dict
    ) -> float:
        """Calculate content-based similarity score"""
        try:
            similarity_score = 0.0
            
            # Category similarity
            listing_category = listing.get("category", "")
            category_scores = user_profile.get("categories", {})
            category_sim = category_scores.get(listing_category, 0)
            similarity_score += category_sim * self.feature_weights["category"]
            
            # Price similarity
            listing_price = listing.get("price", 0)
            price_range = user_profile.get("price_range", {})
            
            if price_range["min"] <= listing_price <= price_range["max"]:
                price_sim = 1.0
            else:
                # Calculate distance from preferred range
                if listing_price < price_range["min"]:
                    distance = price_range["min"] - listing_price
                else:
                    distance = listing_price - price_range["max"]
                
                # Normalize distance (closer = higher similarity)
                max_distance = price_range["average"] if price_range["average"] > 0 else 1000
                price_sim = max(0, 1 - (distance / max_distance))
            
            similarity_score += price_sim * self.feature_weights["price_range"]
            
            # Condition similarity
            listing_condition = listing.get("condition", "")
            condition_scores = user_profile.get("conditions", {})
            condition_sim = condition_scores.get(listing_condition, 0)
            similarity_score += condition_sim * self.feature_weights["condition"]
            
            # Keyword similarity
            listing_text = (listing.get("title", "") + " " + listing.get("description", "")).lower()
            user_keywords = user_profile.get("keywords", {})
            
            keyword_sim = 0.0
            total_keyword_weight = sum(user_keywords.values())
            
            if total_keyword_weight > 0:
                for keyword, weight in user_keywords.items():
                    if keyword in listing_text:
                        keyword_sim += (weight / total_keyword_weight)
            
            similarity_score += keyword_sim * self.feature_weights["keywords"]
            
            return min(1.0, similarity_score)
            
        except Exception as e:
            logger.error(f"Failed to calculate content similarity: {e}")
            return 0.0
    
    async def _calculate_collaborative_score(
        self,
        user_id: str,
        listing_id: str
    ) -> float:
        """Calculate collaborative filtering score"""
        try:
            # Find users who interacted with this listing
            users_who_liked = []
            
            for uid, interactions in self.interaction_matrix.items():
                if listing_id in interactions and interactions[listing_id] > 2:  # Significant interaction
                    users_who_liked.append(uid)
            
            if not users_who_liked:
                return 0.0
            
            # Calculate similarity with those users
            similarity_scores = []
            
            for other_user_id in users_who_liked:
                similarity = await self._calculate_user_similarity(user_id, other_user_id)
                if similarity > 0:
                    similarity_scores.append(similarity)
            
            if not similarity_scores:
                return 0.0
            
            # Return average similarity
            return np.mean(similarity_scores)
            
        except Exception as e:
            logger.error(f"Failed to calculate collaborative score: {e}")
            return 0.0
    
    async def _calculate_popularity_score(self, listing_id: str) -> float:
        """Calculate popularity score based on interactions"""
        try:
            # Count recent interactions
            threshold_time = datetime.utcnow() - timedelta(days=7)
            
            interaction_count = await self.db.user_interactions.count_documents({
                "listing_id": listing_id,
                "timestamp": {"$gte": threshold_time.isoformat()}
            })
            
            # Normalize to 0-1 scale (log scale for large numbers)
            if interaction_count == 0:
                return 0.0
            
            # Use log scale to prevent very popular items from dominating
            normalized_score = min(1.0, math.log(interaction_count + 1) / math.log(100))
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"Failed to calculate popularity score: {e}")
            return 0.0
    
    def _calculate_freshness_score(self, listing: Dict) -> float:
        """Calculate freshness score based on listing age"""
        try:
            created_at = datetime.fromisoformat(listing["created_at"])
            age_hours = (datetime.utcnow() - created_at).total_seconds() / 3600
            
            # Fresher items get higher scores
            # Items lose 50% freshness after 7 days
            decay_rate = 0.5 ** (age_hours / (7 * 24))
            
            return decay_rate
            
        except Exception as e:
            logger.error(f"Failed to calculate freshness score: {e}")
            return 0.0
    
    async def _get_popular_recommendations(self, limit: int) -> List[Dict]:
        """Get popular items as fallback recommendations"""
        try:
            # Get listings with most interactions in the last 7 days
            threshold_time = datetime.utcnow() - timedelta(days=7)
            
            pipeline = [
                {
                    "$match": {
                        "timestamp": {"$gte": threshold_time.isoformat()}
                    }
                },
                {
                    "$group": {
                        "_id": "$listing_id",
                        "interaction_count": {"$sum": 1},
                        "weighted_score": {"$sum": "$weight"}
                    }
                },
                {"$sort": {"weighted_score": -1}},
                {"$limit": limit}
            ]
            
            popular_data = await self.db.user_interactions.aggregate(pipeline).to_list(length=None)
            
            recommendations = []
            
            for item in popular_data:
                listing = await self.db.listings.find_one({"id": item["_id"], "status": "active"})
                if listing:
                    recommendations.append({
                        "listing": self._serialize_listing(listing),
                        "score": 0.8,  # High score for popular items
                        "reasons": ["Popular item", "Trending in your area"]
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get popular recommendations: {e}")
            return []
    
    def _serialize_listing(self, listing: Dict) -> Dict:
        """Serialize listing for recommendations"""
        listing.pop("_id", None)
        return listing
    
    async def _calculate_item_similarity(self, listing1: Dict, listing2: Dict) -> float:
        """Calculate similarity between two listings"""
        try:
            similarity_score = 0.0
            
            # Category similarity (high weight)
            if listing1.get("category") == listing2.get("category"):
                similarity_score += 0.4
            
            # Price similarity (normalized difference)
            price1 = float(listing1.get("price", 0))
            price2 = float(listing2.get("price", 0))
            if price1 > 0 and price2 > 0:
                price_diff = abs(price1 - price2) / max(price1, price2)
                price_similarity = max(0, 1 - price_diff)
                similarity_score += price_similarity * 0.2
            
            # Title similarity (simple keyword matching)
            title1 = listing1.get("title", "").lower().split()
            title2 = listing2.get("title", "").lower().split()
            if title1 and title2:
                common_words = set(title1).intersection(set(title2))
                title_similarity = len(common_words) / max(len(set(title1)), len(set(title2)))
                similarity_score += title_similarity * 0.2
            
            # Condition similarity
            if listing1.get("condition") == listing2.get("condition"):
                similarity_score += 0.1
            
            # Location similarity (simplified)
            loc1 = listing1.get("address", {}).get("city", "")
            loc2 = listing2.get("address", {}).get("city", "")
            if loc1 and loc2 and loc1 == loc2:
                similarity_score += 0.1
            
            return min(similarity_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating item similarity: {e}")
            return 0.0
    
    async def get_recommendation_analytics(self) -> Dict[str, Any]:
        """Get recommendation service analytics"""
        try:
            total_interactions = await self.db.user_interactions.count_documents({})
            unique_users = len(await self.db.user_interactions.distinct("user_id"))
            
            # Get recent activity
            threshold_time = datetime.utcnow() - timedelta(days=7)
            recent_interactions = await self.db.user_interactions.count_documents({
                "timestamp": {"$gte": threshold_time.isoformat()}
            })
            
            return {
                "total_interactions": total_interactions,
                "unique_users": unique_users,
                "recent_interactions_7d": recent_interactions,
                "cached_profiles": len(self.user_profiles),
                "interaction_matrix_size": len(self.interaction_matrix),
                "recommendation_cache_size": len(self.recommendation_cache),
                "service_status": "operational"
            }
            
        except Exception as e:
            logger.error(f"Failed to get recommendation analytics: {e}")
            return {"service_status": "error", "error": str(e)}

# Global AI recommendation service instance
ai_recommendation_service = None

async def init_ai_recommendation_service(db):
    """Initialize AI recommendation service"""
    global ai_recommendation_service
    ai_recommendation_service = AIRecommendationService(db)
    return ai_recommendation_service

def get_ai_recommendation_service():
    """Get AI recommendation service instance"""
    return ai_recommendation_service