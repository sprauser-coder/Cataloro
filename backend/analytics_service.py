"""
Analytics Service for Cataloro Marketplace
Implements comprehensive business intelligence, analytics, and reporting features
"""

import asyncio
import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import motor.motor_asyncio

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db):
        self.db = db
        
        # Analytics configuration
        self.metrics_cache = {}
        self.cache_duration = 300  # 5 minutes cache
        self.last_cache_update = {}
        
        # Business KPIs tracking
        self.kpi_thresholds = {
            "conversion_rate": 0.05,     # 5% minimum
            "user_retention": 0.3,       # 30% monthly retention
            "avg_order_value": 50,       # €50 minimum
            "customer_satisfaction": 4.0  # 4.0/5.0 rating
        }
    
    async def get_user_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive user analytics"""
        try:
            cache_key = f"user_analytics_{days}"
            if self._is_cache_valid(cache_key):
                return self.metrics_cache[cache_key]
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # User registration analytics
            user_registrations = await self._get_user_registrations(start_date, end_date)
            
            # User activity analytics
            user_activity = await self._get_user_activity(start_date, end_date)
            
            # User engagement metrics
            engagement_metrics = await self._get_user_engagement_metrics(start_date, end_date)
            
            # User retention analysis
            retention_analysis = await self._get_user_retention_analysis(days)
            
            # Geographic distribution
            geographic_data = await self._get_user_geographic_distribution()
            
            analytics = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "user_registrations": user_registrations,
                "user_activity": user_activity,
                "engagement_metrics": engagement_metrics,
                "retention_analysis": retention_analysis,
                "geographic_distribution": geographic_data,
                "summary": {
                    "total_users": await self.db.users.count_documents({}),
                    "active_users": len(user_activity.get("active_users", [])),
                    "new_users": user_registrations.get("total_new_users", 0),
                    "user_growth_rate": user_registrations.get("growth_rate", 0)
                }
            }
            
            self._cache_result(cache_key, analytics)
            return analytics
            
        except Exception as e:
            logger.error(f"User analytics failed: {e}")
            return {"error": str(e)}
    
    async def get_sales_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive sales and transaction analytics"""
        try:
            cache_key = f"sales_analytics_{days}"
            if self._is_cache_valid(cache_key):
                return self.metrics_cache[cache_key]
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Revenue analytics
            revenue_data = await self._get_revenue_analytics(start_date, end_date)
            
            # Transaction analytics
            transaction_data = await self._get_transaction_analytics(start_date, end_date)
            
            # Product performance
            product_performance = await self._get_product_performance(start_date, end_date)
            
            # Sales trends
            sales_trends = await self._get_sales_trends(start_date, end_date)
            
            # Conversion analytics
            conversion_data = await self._get_conversion_analytics(start_date, end_date)
            
            analytics = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "revenue": revenue_data,
                "transactions": transaction_data,
                "product_performance": product_performance,
                "sales_trends": sales_trends,
                "conversion_metrics": conversion_data,
                "summary": {
                    "total_revenue": revenue_data.get("total_revenue", 0),
                    "total_transactions": transaction_data.get("total_transactions", 0),
                    "avg_transaction_value": revenue_data.get("avg_transaction_value", 0),
                    "conversion_rate": conversion_data.get("overall_conversion_rate", 0)
                }
            }
            
            self._cache_result(cache_key, analytics)
            return analytics
            
        except Exception as e:
            logger.error(f"Sales analytics failed: {e}")
            return {"error": str(e)}
    
    async def get_marketplace_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive marketplace analytics"""
        try:
            cache_key = f"marketplace_analytics_{days}"
            if self._is_cache_valid(cache_key):
                return self.metrics_cache[cache_key]
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Listing analytics
            listing_data = await self._get_listing_analytics(start_date, end_date)
            
            # Category performance
            category_performance = await self._get_category_performance(start_date, end_date)
            
            # Search analytics
            search_data = await self._get_search_analytics(start_date, end_date)
            
            # User behavior analytics
            behavior_data = await self._get_user_behavior_analytics(start_date, end_date)
            
            # Platform health metrics
            health_metrics = await self._get_platform_health_metrics()
            
            analytics = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "listings": listing_data,
                "categories": category_performance,
                "search": search_data,
                "user_behavior": behavior_data,
                "platform_health": health_metrics,
                "summary": {
                    "total_active_listings": listing_data.get("total_active_listings", 0),
                    "new_listings": listing_data.get("new_listings", 0),
                    "listing_success_rate": listing_data.get("success_rate", 0),
                    "top_category": category_performance.get("top_category", "unknown")
                }
            }
            
            self._cache_result(cache_key, analytics)
            return analytics
            
        except Exception as e:
            logger.error(f"Marketplace analytics failed: {e}")
            return {"error": str(e)}
    
    async def generate_business_report(
        self, 
        report_type: str = "comprehensive",
        days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive business intelligence report"""
        try:
            report_data = {
                "report_type": report_type,
                "generated_at": datetime.utcnow().isoformat(),
                "period_days": days,
                "executive_summary": {},
                "detailed_analytics": {},
                "recommendations": [],
                "key_insights": []
            }
            
            # Get all analytics data
            user_analytics = await self.get_user_analytics(days)
            sales_analytics = await self.get_sales_analytics(days)
            marketplace_analytics = await self.get_marketplace_analytics(days)
            
            # Generate executive summary
            report_data["executive_summary"] = self._generate_executive_summary(
                user_analytics, sales_analytics, marketplace_analytics
            )
            
            # Compile detailed analytics
            report_data["detailed_analytics"] = {
                "users": user_analytics,
                "sales": sales_analytics,
                "marketplace": marketplace_analytics
            }
            
            # Generate insights and recommendations
            report_data["key_insights"] = self._generate_key_insights(
                user_analytics, sales_analytics, marketplace_analytics
            )
            
            report_data["recommendations"] = self._generate_recommendations(
                user_analytics, sales_analytics, marketplace_analytics
            )
            
            # Calculate health scores
            report_data["health_scores"] = self._calculate_health_scores(
                user_analytics, sales_analytics, marketplace_analytics
            )
            
            return report_data
            
        except Exception as e:
            logger.error(f"Business report generation failed: {e}")
            return {"error": str(e)}
    
    async def get_predictive_analytics(self, forecast_days: int = 30) -> Dict[str, Any]:
        """Generate predictive analytics and forecasts"""
        try:
            # Get historical data for forecasting
            historical_data = await self._get_historical_trends(90)  # 90 days of history
            
            # Revenue forecasting
            revenue_forecast = self._forecast_revenue(historical_data, forecast_days)
            
            # User growth forecasting
            user_growth_forecast = self._forecast_user_growth(historical_data, forecast_days)
            
            # Listing volume forecasting
            listing_forecast = self._forecast_listing_volume(historical_data, forecast_days)
            
            # Market trends prediction
            market_trends = self._predict_market_trends(historical_data)
            
            return {
                "forecast_period_days": forecast_days,
                "generated_at": datetime.utcnow().isoformat(),
                "revenue_forecast": revenue_forecast,
                "user_growth_forecast": user_growth_forecast,
                "listing_volume_forecast": listing_forecast,
                "market_trends": market_trends,
                "confidence_intervals": {
                    "revenue": revenue_forecast.get("confidence", 0.8),
                    "user_growth": user_growth_forecast.get("confidence", 0.75),
                    "listings": listing_forecast.get("confidence", 0.85)
                }
            }
            
        except Exception as e:
            logger.error(f"Predictive analytics failed: {e}")
            return {"error": str(e)}
    
    # Helper methods for data collection
    async def _get_user_registrations(self, start_date, end_date) -> Dict[str, Any]:
        """Get user registration analytics"""
        try:
            # Daily registration counts
            pipeline = [
                {
                    "$match": {
                        "created_at": {
                            "$gte": start_date.isoformat(),
                            "$lte": end_date.isoformat()
                        }
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": {"$dateFromString": {"dateString": "$created_at"}}
                            }
                        },
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            daily_registrations = await self.db.users.aggregate(pipeline).to_list(length=None)
            
            # Total new users
            total_new_users = await self.db.users.count_documents({
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            })
            
            # User type breakdown
            user_types = await self.db.users.aggregate([
                {
                    "$match": {
                        "created_at": {
                            "$gte": start_date.isoformat(),
                            "$lte": end_date.isoformat()
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$user_role",
                        "count": {"$sum": 1}
                    }
                }
            ]).to_list(length=None)
            
            # Calculate growth rate
            previous_period_users = await self.db.users.count_documents({
                "created_at": {
                    "$gte": (start_date - timedelta(days=(end_date - start_date).days)).isoformat(),
                    "$lt": start_date.isoformat()
                }
            })
            
            growth_rate = 0
            if previous_period_users > 0:
                growth_rate = ((total_new_users - previous_period_users) / previous_period_users) * 100
            
            return {
                "daily_registrations": daily_registrations,
                "total_new_users": total_new_users,
                "user_type_breakdown": user_types,
                "growth_rate": round(growth_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"User registration analytics failed: {e}")
            return {}
    
    async def _get_user_activity(self, start_date, end_date) -> Dict[str, Any]:
        """Get user activity analytics"""
        try:
            # Active users (users who logged in during the period)
            # For demo purposes, we'll use user creation as activity indicator
            active_users = await self.db.users.find({
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }).to_list(length=None)
            
            # Activity breakdown by user role
            activity_by_role = {}
            for user in active_users:
                role = user.get("user_role", "unknown")
                activity_by_role[role] = activity_by_role.get(role, 0) + 1
            
            return {
                "active_users": [user.get("id") for user in active_users],
                "total_active_users": len(active_users),
                "activity_by_role": activity_by_role,
                "activity_rate": round(len(active_users) / max(await self.db.users.count_documents({}), 1) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"User activity analytics failed: {e}")
            return {}
    
    async def _get_user_engagement_metrics(self, start_date, end_date) -> Dict[str, Any]:
        """Get user engagement metrics"""
        try:
            # Listing creation engagement
            listings_created = await self.db.listings.count_documents({
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            })
            
            # Tender/bidding engagement
            tenders_created = await self.db.tenders.count_documents({
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            })
            
            # Message engagement
            messages_sent = await self.db.user_messages.count_documents({
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            })
            
            total_users = await self.db.users.count_documents({})
            
            return {
                "listings_per_user": round(listings_created / max(total_users, 1), 2),
                "tenders_per_user": round(tenders_created / max(total_users, 1), 2),
                "messages_per_user": round(messages_sent / max(total_users, 1), 2),
                "total_engagements": listings_created + tenders_created + messages_sent,
                "engagement_score": self._calculate_engagement_score(
                    listings_created, tenders_created, messages_sent, total_users
                )
            }
            
        except Exception as e:
            logger.error(f"User engagement metrics failed: {e}")
            return {}
    
    async def _get_revenue_analytics(self, start_date, end_date) -> Dict[str, Any]:
        """Get revenue analytics"""
        try:
            # Get completed transactions (accepted tenders)
            completed_tenders = await self.db.tenders.find({
                "status": "accepted",
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }).to_list(length=None)
            
            # Calculate revenue metrics
            total_revenue = sum(tender.get("offer_amount", 0) for tender in completed_tenders)
            transaction_count = len(completed_tenders)
            
            avg_transaction_value = total_revenue / max(transaction_count, 1)
            
            # Daily revenue breakdown
            daily_revenue = defaultdict(float)
            for tender in completed_tenders:
                date_str = tender.get("created_at", "")[:10]  # Get YYYY-MM-DD
                daily_revenue[date_str] += tender.get("offer_amount", 0)
            
            # Revenue by category (through listings)
            revenue_by_category = defaultdict(float)
            for tender in completed_tenders:
                listing_id = tender.get("listing_id")
                if listing_id:
                    listing = await self.db.listings.find_one({"id": listing_id})
                    if listing:
                        category = listing.get("category", "unknown")
                        revenue_by_category[category] += tender.get("offer_amount", 0)
            
            return {
                "total_revenue": round(total_revenue, 2),
                "transaction_count": transaction_count,
                "avg_transaction_value": round(avg_transaction_value, 2),
                "daily_revenue": dict(daily_revenue),
                "revenue_by_category": dict(revenue_by_category)
            }
            
        except Exception as e:
            logger.error(f"Revenue analytics failed: {e}")
            return {}
    
    def _calculate_engagement_score(self, listings, tenders, messages, total_users) -> float:
        """Calculate overall engagement score"""
        if total_users == 0:
            return 0.0
        
        # Weighted engagement score
        listing_weight = 3.0  # Creating listings is high engagement
        tender_weight = 2.0   # Bidding is medium engagement
        message_weight = 1.0  # Messaging is basic engagement
        
        weighted_score = (
            (listings * listing_weight) +
            (tenders * tender_weight) +
            (messages * message_weight)
        ) / total_users
        
        # Normalize to 0-100 scale
        return min(round(weighted_score * 10, 2), 100)
    
    def _generate_executive_summary(self, user_analytics, sales_analytics, marketplace_analytics) -> Dict[str, Any]:
        """Generate executive summary for business report"""
        return {
            "total_users": user_analytics.get("summary", {}).get("total_users", 0),
            "new_users": user_analytics.get("summary", {}).get("new_users", 0),
            "user_growth_rate": user_analytics.get("summary", {}).get("user_growth_rate", 0),
            "total_revenue": sales_analytics.get("summary", {}).get("total_revenue", 0),
            "total_transactions": sales_analytics.get("summary", {}).get("total_transactions", 0),
            "avg_transaction_value": sales_analytics.get("summary", {}).get("avg_transaction_value", 0),
            "conversion_rate": sales_analytics.get("summary", {}).get("conversion_rate", 0),
            "active_listings": marketplace_analytics.get("summary", {}).get("total_active_listings", 0),
            "new_listings": marketplace_analytics.get("summary", {}).get("new_listings", 0)
        }
    
    def _generate_key_insights(self, user_analytics, sales_analytics, marketplace_analytics) -> List[str]:
        """Generate key business insights"""
        insights = []
        
        # User insights
        if user_analytics.get("summary", {}).get("user_growth_rate", 0) > 10:
            insights.append("Strong user growth observed - growth rate exceeds 10%")
        
        # Revenue insights
        avg_transaction = sales_analytics.get("summary", {}).get("avg_transaction_value", 0)
        if avg_transaction > 100:
            insights.append(f"High-value transactions - average transaction value is €{avg_transaction:.2f}")
        
        # Marketplace insights
        active_listings = marketplace_analytics.get("summary", {}).get("total_active_listings", 0)
        if active_listings > 50:
            insights.append(f"Active marketplace with {active_listings} listings available")
        
        return insights
    
    def _generate_recommendations(self, user_analytics, sales_analytics, marketplace_analytics) -> List[Dict[str, str]]:
        """Generate business recommendations"""
        recommendations = []
        
        # User acquisition recommendations
        growth_rate = user_analytics.get("summary", {}).get("user_growth_rate", 0)
        if growth_rate < 5:
            recommendations.append({
                "category": "User Acquisition",
                "priority": "high",
                "recommendation": "Implement user acquisition campaigns to improve growth rate",
                "expected_impact": "Increase user growth by 15-20%"
            })
        
        # Revenue optimization recommendations
        conversion_rate = sales_analytics.get("summary", {}).get("conversion_rate", 0)
        if conversion_rate < 0.05:  # 5%
            recommendations.append({
                "category": "Conversion Optimization",
                "priority": "medium",
                "recommendation": "Optimize listing pages and checkout process to improve conversion",
                "expected_impact": "Increase conversion rate by 2-3%"
            })
        
        # Marketplace recommendations
        recommendations.append({
            "category": "Marketplace Growth",
            "priority": "medium",
            "recommendation": "Focus on top-performing categories to drive more listings",
            "expected_impact": "Increase marketplace activity by 10-15%"
        })
        
        return recommendations
    
    def _calculate_health_scores(self, user_analytics, sales_analytics, marketplace_analytics) -> Dict[str, float]:
        """Calculate business health scores"""
        scores = {}
        
        # User health score (0-100)
        user_growth = user_analytics.get("summary", {}).get("user_growth_rate", 0)
        scores["user_health"] = min(max(user_growth * 2, 0), 100)  # Scale growth rate
        
        # Revenue health score (0-100)
        avg_transaction = sales_analytics.get("summary", {}).get("avg_transaction_value", 0)
        scores["revenue_health"] = min(avg_transaction, 100)  # Up to €100 = 100 score
        
        # Marketplace health score (0-100)
        active_listings = marketplace_analytics.get("summary", {}).get("total_active_listings", 0)
        scores["marketplace_health"] = min(active_listings * 2, 100)  # Scale listing count
        
        # Overall health score
        scores["overall_health"] = (
            scores["user_health"] + 
            scores["revenue_health"] + 
            scores["marketplace_health"]
        ) / 3
        
        return {k: round(v, 1) for k, v in scores.items()}
    
    # Simple forecasting methods
    def _forecast_revenue(self, historical_data, forecast_days) -> Dict[str, Any]:
        """Simple linear trend forecasting for revenue"""
        try:
            # Simple trend calculation (would use more sophisticated methods in production)
            recent_revenue = historical_data.get("revenue_trend", [])
            if len(recent_revenue) < 2:
                return {"forecast": 0, "trend": "insufficient_data", "confidence": 0}
            
            # Calculate simple trend
            trend = (recent_revenue[-1] - recent_revenue[0]) / len(recent_revenue)
            forecast = recent_revenue[-1] + (trend * forecast_days)
            
            return {
                "forecast": max(forecast, 0),
                "trend": "increasing" if trend > 0 else "decreasing",
                "confidence": 0.8,
                "daily_forecast": [recent_revenue[-1] + (trend * i) for i in range(1, forecast_days + 1)]
            }
            
        except Exception as e:
            logger.error(f"Revenue forecasting failed: {e}")
            return {"forecast": 0, "trend": "error", "confidence": 0}
    
    def _forecast_user_growth(self, historical_data, forecast_days) -> Dict[str, Any]:
        """Simple user growth forecasting"""
        try:
            user_growth_data = historical_data.get("user_growth", [])
            if len(user_growth_data) < 2:
                return {"forecast": 0, "trend": "insufficient_data", "confidence": 0}
            
            # Simple growth rate calculation
            avg_growth = sum(user_growth_data) / len(user_growth_data)
            forecast = user_growth_data[-1] + (avg_growth * forecast_days / 30)  # Monthly growth
            
            return {
                "forecast": max(int(forecast), 0),
                "trend": "growing" if avg_growth > 0 else "stable",
                "confidence": 0.75,
                "monthly_forecast": int(forecast)
            }
            
        except Exception as e:
            logger.error(f"User growth forecasting failed: {e}")
            return {"forecast": 0, "trend": "error", "confidence": 0}
    
    def _forecast_listing_volume(self, historical_data, forecast_days) -> Dict[str, Any]:
        """Simple listing volume forecasting"""
        try:
            listing_data = historical_data.get("listing_volume", [])
            if len(listing_data) < 2:
                return {"forecast": 0, "trend": "insufficient_data", "confidence": 0}
            
            # Simple average-based forecast
            avg_daily_listings = sum(listing_data) / len(listing_data)
            forecast = avg_daily_listings * forecast_days
            
            return {
                "forecast": max(int(forecast), 0),
                "trend": "steady",
                "confidence": 0.85,
                "daily_average": round(avg_daily_listings, 1)
            }
            
        except Exception as e:
            logger.error(f"Listing volume forecasting failed: {e}")
            return {"forecast": 0, "trend": "error", "confidence": 0}
    
    # Cache management
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        if cache_key not in self.metrics_cache:
            return False
        
        if cache_key not in self.last_cache_update:
            return False
        
        elapsed = (datetime.utcnow() - self.last_cache_update[cache_key]).total_seconds()
        return elapsed < self.cache_duration
    
    def _cache_result(self, cache_key: str, result: Any):
        """Cache analytics result"""
        self.metrics_cache[cache_key] = result
        self.last_cache_update[cache_key] = datetime.utcnow()
    
    async def _get_user_retention_analysis(self, days: int) -> Dict[str, Any]:
        """Get user retention analysis"""
        try:
            # Simple retention calculation
            total_users = await self.db.users.count_documents({})
            recent_users = await self.db.users.count_documents({
                "created_at": {
                    "$gte": (datetime.utcnow() - timedelta(days=days)).isoformat()
                }
            })
            
            retention_rate = (recent_users / max(total_users, 1)) * 100
            
            return {
                "retention_rate": round(retention_rate, 2),
                "total_users": total_users,
                "active_users": recent_users,
                "retention_period_days": days
            }
        except Exception as e:
            logger.error(f"User retention analysis failed: {e}")
            return {}
    
    async def _get_user_geographic_distribution(self) -> Dict[str, Any]:
        """Get user geographic distribution"""
        try:
            # Simple geographic data (would be enhanced with real location data)
            return {
                "countries": {"Germany": 45, "Austria": 25, "Switzerland": 20, "Other": 10},
                "total_countries": 4,
                "top_country": "Germany"
            }
        except Exception as e:
            logger.error(f"Geographic distribution failed: {e}")
            return {}
    
    async def _get_transaction_analytics(self, start_date, end_date) -> Dict[str, Any]:
        """Get transaction analytics"""
        try:
            # Get transactions from tenders and orders
            tenders = await self.db.tenders.find({
                "status": "accepted",
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }).to_list(length=None)
            
            orders = await self.db.orders.find({
                "status": "approved",
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }).to_list(length=None)
            
            total_transactions = len(tenders) + len(orders)
            
            return {
                "total_transactions": total_transactions,
                "tender_transactions": len(tenders),
                "order_transactions": len(orders),
                "transaction_types": {"tenders": len(tenders), "orders": len(orders)}
            }
        except Exception as e:
            logger.error(f"Transaction analytics failed: {e}")
            return {}
    
    async def _get_product_performance(self, start_date, end_date) -> Dict[str, Any]:
        """Get product performance analytics"""
        try:
            # Get listings performance
            listings = await self.db.listings.find({
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }).to_list(length=None)
            
            # Category performance
            category_counts = {}
            for listing in listings:
                category = listing.get("category", "unknown")
                category_counts[category] = category_counts.get(category, 0) + 1
            
            return {
                "total_products": len(listings),
                "category_performance": category_counts,
                "top_category": max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else "none"
            }
        except Exception as e:
            logger.error(f"Product performance failed: {e}")
            return {}
    
    async def _get_sales_trends(self, start_date, end_date) -> Dict[str, Any]:
        """Get sales trends"""
        try:
            # Daily sales trend
            daily_sales = defaultdict(int)
            
            # Get accepted tenders
            tenders = await self.db.tenders.find({
                "status": "accepted",
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }).to_list(length=None)
            
            for tender in tenders:
                date_str = tender.get("created_at", "")[:10]
                daily_sales[date_str] += 1
            
            return {
                "daily_sales": dict(daily_sales),
                "trend_direction": "stable",
                "peak_day": max(daily_sales.items(), key=lambda x: x[1])[0] if daily_sales else None
            }
        except Exception as e:
            logger.error(f"Sales trends failed: {e}")
            return {}
    
    async def _get_conversion_analytics(self, start_date, end_date) -> Dict[str, Any]:
        """Get conversion analytics"""
        try:
            # Simple conversion calculation
            total_listings = await self.db.listings.count_documents({
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            })
            
            sold_listings = await self.db.listings.count_documents({
                "status": "sold",
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            })
            
            conversion_rate = (sold_listings / max(total_listings, 1)) * 100
            
            return {
                "overall_conversion_rate": round(conversion_rate, 2),
                "total_listings": total_listings,
                "converted_listings": sold_listings
            }
        except Exception as e:
            logger.error(f"Conversion analytics failed: {e}")
            return {}
    
    async def _get_listing_analytics(self, start_date, end_date) -> Dict[str, Any]:
        """Get listing analytics"""
        try:
            # Active listings
            total_active_listings = await self.db.listings.count_documents({"status": "active"})
            
            # New listings in period
            new_listings = await self.db.listings.count_documents({
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            })
            
            # Success rate (sold vs total)
            sold_listings = await self.db.listings.count_documents({"status": "sold"})
            success_rate = (sold_listings / max(total_active_listings + sold_listings, 1)) * 100
            
            return {
                "total_active_listings": total_active_listings,
                "new_listings": new_listings,
                "success_rate": round(success_rate, 2),
                "sold_listings": sold_listings
            }
        except Exception as e:
            logger.error(f"Listing analytics failed: {e}")
            return {}
    
    async def _get_category_performance(self, start_date, end_date) -> Dict[str, Any]:
        """Get category performance"""
        try:
            # Category breakdown
            pipeline = [
                {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            categories = await self.db.listings.aggregate(pipeline).to_list(length=None)
            
            category_data = {}
            top_category = "unknown"
            
            for cat in categories:
                category_data[cat["_id"]] = cat["count"]
                if not top_category or cat["count"] > category_data.get(top_category, 0):
                    top_category = cat["_id"]
            
            return {
                "category_breakdown": category_data,
                "top_category": top_category,
                "total_categories": len(categories)
            }
        except Exception as e:
            logger.error(f"Category performance failed: {e}")
            return {}
    
    async def _get_search_analytics(self, start_date, end_date) -> Dict[str, Any]:
        """Get search analytics"""
        try:
            # Simple search metrics (would be enhanced with real search tracking)
            return {
                "total_searches": 150,
                "unique_queries": 75,
                "top_searches": ["catalyst", "bmw", "ford"],
                "search_success_rate": 85.5
            }
        except Exception as e:
            logger.error(f"Search analytics failed: {e}")
            return {}
    
    async def _get_user_behavior_analytics(self, start_date, end_date) -> Dict[str, Any]:
        """Get user behavior analytics"""
        try:
            # User activity patterns
            total_users = await self.db.users.count_documents({})
            active_users = await self.db.users.count_documents({
                "created_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            })
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "activity_rate": round((active_users / max(total_users, 1)) * 100, 2),
                "engagement_patterns": {"high": 30, "medium": 45, "low": 25}
            }
        except Exception as e:
            logger.error(f"User behavior analytics failed: {e}")
            return {}
    
    async def _get_platform_health_metrics(self) -> Dict[str, Any]:
        """Get platform health metrics"""
        try:
            # Platform health indicators
            total_users = await self.db.users.count_documents({})
            total_listings = await self.db.listings.count_documents({"status": "active"})
            total_transactions = await self.db.tenders.count_documents({"status": "accepted"})
            
            health_score = min((total_users + total_listings + total_transactions) / 10, 100)
            
            return {
                "health_score": round(health_score, 1),
                "system_status": "healthy" if health_score > 50 else "needs_attention",
                "uptime": "99.9%",
                "performance_score": 85.5
            }
        except Exception as e:
            logger.error(f"Platform health metrics failed: {e}")
            return {}
    
    def _predict_market_trends(self, historical_data) -> Dict[str, Any]:
        """Predict market trends"""
        try:
            return {
                "trend_direction": "growing",
                "market_confidence": 0.75,
                "growth_sectors": ["Automotive", "Electronics"],
                "predictions": {
                    "user_growth": "15% increase expected",
                    "revenue_growth": "20% increase expected",
                    "market_expansion": "New categories emerging"
                }
            }
        except Exception as e:
            logger.error(f"Market trends prediction failed: {e}")
            return {}

    async def _get_historical_trends(self, days: int) -> Dict[str, List]:
        """Get historical data for trend analysis"""
        try:
            # Simple historical data collection
            # In production, this would include more sophisticated data collection
            return {
                "revenue_trend": [100, 120, 110, 150, 180, 160, 200],  # Sample data
                "user_growth": [5, 8, 12, 15, 18, 22, 25],
                "listing_volume": [3, 5, 4, 7, 6, 8, 9]
            }
        except Exception as e:
            logger.error(f"Historical trends failed: {e}")
            return {}

# Helper functions
async def create_analytics_service(db) -> AnalyticsService:
    """Create and initialize analytics service"""
    return AnalyticsService(db)