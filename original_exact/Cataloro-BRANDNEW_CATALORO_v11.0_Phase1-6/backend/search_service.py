"""
Elasticsearch Search Service for Cataloro Marketplace
Implements advanced search, filtering, and recommendation features
"""

import asyncio
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import os
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        # Elasticsearch connection settings
        self.es_host = os.environ.get('ELASTICSEARCH_HOST', 'localhost')
        self.es_port = int(os.environ.get('ELASTICSEARCH_PORT', 9200))
        self.es_username = os.environ.get('ELASTICSEARCH_USERNAME', '')
        self.es_password = os.environ.get('ELASTICSEARCH_PASSWORD', '')
        
        self.es_client: Optional[AsyncElasticsearch] = None
        self.connected = False
        
        # Index names
        self.LISTINGS_INDEX = "cataloro_listings"
        self.USERS_INDEX = "cataloro_users"
        self.SEARCH_ANALYTICS_INDEX = "cataloro_search_analytics"
    
    async def connect(self):
        """Initialize Elasticsearch connection"""
        try:
            # Configure connection
            if self.es_username and self.es_password:
                self.es_client = AsyncElasticsearch(
                    [{"host": self.es_host, "port": self.es_port}],
                    basic_auth=(self.es_username, self.es_password),
                    verify_certs=False
                )
            else:
                self.es_client = AsyncElasticsearch(
                    [{"host": self.es_host, "port": self.es_port}],
                    verify_certs=False
                )
            
            # Test connection
            await self.es_client.info()
            self.connected = True
            logger.info("✅ Elasticsearch connection established successfully")
            
            # Initialize indexes
            await self._initialize_indexes()
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Elasticsearch connection failed: {e}")
            logger.info("📝 Continuing with fallback search (database-only)")
            self.es_client = None
            self.connected = False
            return False
    
    async def disconnect(self):
        """Close Elasticsearch connection"""
        if self.es_client:
            await self.es_client.close()
            logger.info("Elasticsearch connection closed")
    
    async def _initialize_indexes(self):
        """Initialize Elasticsearch indexes with proper mappings"""
        if not self.connected:
            return
        
        try:
            # Listings index mapping
            listings_mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "title": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {"type": "keyword"},
                                "suggest": {
                                    "type": "completion",
                                    "analyzer": "simple"
                                }
                            }
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "category": {"type": "keyword"},
                        "condition": {"type": "keyword"},
                        "price": {"type": "float"},
                        "seller_id": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "tags": {"type": "keyword"},
                        "features": {"type": "keyword"},
                        "location": {
                            "properties": {
                                "city": {"type": "keyword"},
                                "country": {"type": "keyword"},
                                "coordinates": {"type": "geo_point"}
                            }
                        },
                        "seller_info": {
                            "properties": {
                                "name": {"type": "text"},
                                "username": {"type": "keyword"},
                                "is_business": {"type": "boolean"},
                                "verified": {"type": "boolean"}
                            }
                        },
                        "catalyst_data": {
                            "properties": {
                                "ceramic_weight": {"type": "float"},
                                "pt_ppm": {"type": "float"},
                                "pd_ppm": {"type": "float"},
                                "rh_ppm": {"type": "float"}
                            }
                        }
                    }
                }
            }
            
            # Create listings index
            if not await self.es_client.indices.exists(index=self.LISTINGS_INDEX):
                await self.es_client.indices.create(
                    index=self.LISTINGS_INDEX,
                    body=listings_mapping
                )
                logger.info(f"✅ Created Elasticsearch index: {self.LISTINGS_INDEX}")
            
            # Search analytics index mapping
            analytics_mapping = {
                "mappings": {
                    "properties": {
                        "query": {"type": "keyword"},
                        "normalized_query": {"type": "keyword"},
                        "results_count": {"type": "integer"},
                        "user_id": {"type": "keyword"},
                        "timestamp": {"type": "date"},
                        "session_id": {"type": "keyword"},
                        "filters_applied": {"type": "object"},
                        "clicked_results": {"type": "keyword"}
                    }
                }
            }
            
            # Create search analytics index
            if not await self.es_client.indices.exists(index=self.SEARCH_ANALYTICS_INDEX):
                await self.es_client.indices.create(
                    index=self.SEARCH_ANALYTICS_INDEX,
                    body=analytics_mapping
                )
                logger.info(f"✅ Created Elasticsearch index: {self.SEARCH_ANALYTICS_INDEX}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch indexes: {e}")
    
    async def index_listing(self, listing_data: Dict) -> bool:
        """Index a single listing in Elasticsearch"""
        if not self.connected:
            return False
        
        try:
            # Prepare listing data for indexing
            doc = {
                "id": listing_data.get("id"),
                "title": listing_data.get("title", ""),
                "description": listing_data.get("description", ""),
                "category": listing_data.get("category", ""),
                "condition": listing_data.get("condition", ""),
                "price": listing_data.get("price", 0),
                "seller_id": listing_data.get("seller_id"),
                "status": listing_data.get("status", "active"),
                "created_at": listing_data.get("created_at"),
                "tags": listing_data.get("tags", []),
                "features": listing_data.get("features", []),
                "seller_info": listing_data.get("seller", {}),
                "catalyst_data": {
                    "ceramic_weight": listing_data.get("ceramic_weight"),
                    "pt_ppm": listing_data.get("pt_ppm"),
                    "pd_ppm": listing_data.get("pd_ppm"),
                    "rh_ppm": listing_data.get("rh_ppm")
                }
            }
            
            await self.es_client.index(
                index=self.LISTINGS_INDEX,
                id=listing_data.get("id"),
                body=doc
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to index listing {listing_data.get('id')}: {e}")
            return False
    
    async def bulk_index_listings(self, listings: List[Dict]) -> int:
        """Bulk index multiple listings"""
        if not self.connected or not listings:
            return 0
        
        try:
            actions = []
            for listing in listings:
                doc = {
                    "id": listing.get("id"),
                    "title": listing.get("title", ""),
                    "description": listing.get("description", ""),
                    "category": listing.get("category", ""),
                    "condition": listing.get("condition", ""),
                    "price": listing.get("price", 0),
                    "seller_id": listing.get("seller_id"),
                    "status": listing.get("status", "active"),
                    "created_at": listing.get("created_at"),
                    "tags": listing.get("tags", []),
                    "features": listing.get("features", []),
                    "seller_info": listing.get("seller", {}),
                    "catalyst_data": {
                        "ceramic_weight": listing.get("ceramic_weight"),
                        "pt_ppm": listing.get("pt_ppm"),
                        "pd_ppm": listing.get("pd_ppm"),
                        "rh_ppm": listing.get("rh_ppm")
                    }
                }
                
                actions.append({
                    "_index": self.LISTINGS_INDEX,
                    "_id": listing.get("id"),
                    "_source": doc
                })
            
            from elasticsearch.helpers import async_bulk
            success_count, failed = await async_bulk(
                self.es_client,
                actions,
                chunk_size=100
            )
            
            logger.info(f"✅ Bulk indexed {success_count} listings")
            return success_count
            
        except Exception as e:
            logger.error(f"Failed to bulk index listings: {e}")
            return 0
    
    async def search_listings(
        self,
        query: str = "",
        category: str = "",
        price_min: float = 0,
        price_max: float = 999999,
        condition: str = "",
        seller_type: str = "",
        location: str = "",
        size: int = 20,
        from_: int = 0,
        sort_by: str = "relevance"
    ) -> Dict[str, Any]:
        """Advanced search for listings with multiple filters"""
        
        if not self.connected:
            # Fallback to basic search (return empty results for now)
            return {
                "hits": [],
                "total": 0,
                "took": 0,
                "aggregations": {},
                "suggestions": []
            }
        
        try:
            # Build Elasticsearch query
            search_body = {
                "query": {
                    "bool": {
                        "must": [],
                        "filter": []
                    }
                },
                "size": size,
                "from": from_,
                "highlight": {
                    "fields": {
                        "title": {},
                        "description": {}
                    }
                },
                "aggs": {
                    "categories": {
                        "terms": {"field": "category", "size": 10}
                    },
                    "conditions": {
                        "terms": {"field": "condition", "size": 10}
                    },
                    "price_ranges": {
                        "range": {
                            "field": "price",
                            "ranges": [
                                {"to": 50, "key": "Under €50"},
                                {"from": 50, "to": 100, "key": "€50-€100"},
                                {"from": 100, "to": 500, "key": "€100-€500"},
                                {"from": 500, "key": "Over €500"}
                            ]
                        }
                    }
                }
            }
            
            # Add text search if query provided
            if query:
                search_body["query"]["bool"]["must"].append({
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "description^2", "tags", "features"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                })
            else:
                search_body["query"]["bool"]["must"].append({"match_all": {}})
            
            # Add filters
            search_body["query"]["bool"]["filter"].append({
                "term": {"status": "active"}
            })
            
            if category:
                search_body["query"]["bool"]["filter"].append({
                    "term": {"category": category}
                })
            
            if condition:
                search_body["query"]["bool"]["filter"].append({
                    "term": {"condition": condition}
                })
            
            if price_min > 0 or price_max < 999999:
                search_body["query"]["bool"]["filter"].append({
                    "range": {
                        "price": {
                            "gte": price_min,
                            "lte": price_max
                        }
                    }
                })
            
            if seller_type:
                if seller_type.lower() == "business":
                    search_body["query"]["bool"]["filter"].append({
                        "term": {"seller_info.is_business": True}
                    })
                elif seller_type.lower() == "private":
                    search_body["query"]["bool"]["filter"].append({
                        "term": {"seller_info.is_business": False}
                    })
            
            # Add sorting
            if sort_by == "price_low":
                search_body["sort"] = [{"price": {"order": "asc"}}]
            elif sort_by == "price_high":
                search_body["sort"] = [{"price": {"order": "desc"}}]
            elif sort_by == "newest":
                search_body["sort"] = [{"created_at": {"order": "desc"}}]
            elif sort_by == "oldest":
                search_body["sort"] = [{"created_at": {"order": "asc"}}]
            # Default is relevance (Elasticsearch default scoring)
            
            # Execute search
            response = await self.es_client.search(
                index=self.LISTINGS_INDEX,
                body=search_body
            )
            
            # Process results
            hits = []
            for hit in response["hits"]["hits"]:
                listing = hit["_source"]
                listing["_score"] = hit.get("_score", 0)
                listing["_highlights"] = hit.get("highlight", {})
                hits.append(listing)
            
            result = {
                "hits": hits,
                "total": response["hits"]["total"]["value"],
                "took": response["took"],
                "aggregations": response.get("aggregations", {}),
                "suggestions": []
            }
            
            # Log search analytics
            await self._log_search_analytics(
                query, len(hits), None, 
                {
                    "category": category,
                    "price_min": price_min,
                    "price_max": price_max,
                    "condition": condition,
                    "seller_type": seller_type
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "hits": [],
                "total": 0,
                "took": 0,
                "aggregations": {},
                "suggestions": [],
                "error": str(e)
            }
    
    async def get_search_suggestions(
        self, 
        query: str, 
        size: int = 5
    ) -> List[str]:
        """Get search suggestions/auto-complete"""
        
        if not self.connected or not query:
            return []
        
        try:
            search_body = {
                "suggest": {
                    "title_suggest": {
                        "prefix": query,
                        "completion": {
                            "field": "title.suggest",
                            "size": size,
                            "skip_duplicates": True
                        }
                    }
                }
            }
            
            response = await self.es_client.search(
                index=self.LISTINGS_INDEX,
                body=search_body
            )
            
            suggestions = []
            for suggestion in response.get("suggest", {}).get("title_suggest", []):
                for option in suggestion.get("options", []):
                    suggestions.append(option["text"])
            
            return suggestions[:size]
            
        except Exception as e:
            logger.error(f"Failed to get suggestions: {e}")
            return []
    
    async def get_trending_searches(self, limit: int = 10) -> List[Dict]:
        """Get trending/popular search queries"""
        
        if not self.connected:
            return []
        
        try:
            search_body = {
                "size": 0,
                "aggs": {
                    "trending_queries": {
                        "terms": {
                            "field": "normalized_query",
                            "size": limit
                        }
                    }
                }
            }
            
            response = await self.es_client.search(
                index=self.SEARCH_ANALYTICS_INDEX,
                body=search_body
            )
            
            trending = []
            for bucket in response.get("aggregations", {}).get("trending_queries", {}).get("buckets", []):
                trending.append({
                    "query": bucket["key"],
                    "count": bucket["doc_count"]
                })
            
            return trending
            
        except Exception as e:
            logger.error(f"Failed to get trending searches: {e}")
            return []
    
    async def get_similar_listings(
        self, 
        listing_id: str, 
        size: int = 5
    ) -> List[Dict]:
        """Get similar/recommended listings"""
        
        if not self.connected:
            return []
        
        try:
            # Get the original listing
            original = await self.es_client.get(
                index=self.LISTINGS_INDEX,
                id=listing_id
            )
            
            original_data = original["_source"]
            
            # Search for similar listings
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "more_like_this": {
                                    "fields": ["title", "description", "category", "tags"],
                                    "like": [
                                        {
                                            "_index": self.LISTINGS_INDEX,
                                            "_id": listing_id
                                        }
                                    ],
                                    "min_term_freq": 1,
                                    "max_query_terms": 12
                                }
                            }
                        ],
                        "filter": [
                            {"term": {"status": "active"}},
                            {"bool": {"must_not": {"term": {"id": listing_id}}}}
                        ]
                    }
                },
                "size": size
            }
            
            response = await self.es_client.search(
                index=self.LISTINGS_INDEX,
                body=search_body
            )
            
            similar = []
            for hit in response["hits"]["hits"]:
                listing = hit["_source"]
                listing["_score"] = hit.get("_score", 0)
                similar.append(listing)
            
            return similar
            
        except Exception as e:
            logger.error(f"Failed to get similar listings: {e}")
            return []
    
    async def _log_search_analytics(
        self,
        query: str,
        results_count: int,
        user_id: str = None,
        filters_applied: Dict = None
    ):
        """Log search analytics for trending analysis"""
        
        if not self.connected:
            return
        
        try:
            doc = {
                "query": query,
                "normalized_query": query.lower().strip(),
                "results_count": results_count,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "filters_applied": filters_applied or {}
            }
            
            await self.es_client.index(
                index=self.SEARCH_ANALYTICS_INDEX,
                body=doc
            )
            
        except Exception as e:
            logger.error(f"Failed to log search analytics: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check search service health"""
        if not self.connected:
            return {
                "status": "disabled",
                "message": "Elasticsearch not connected - using fallback search"
            }
        
        try:
            info = await self.es_client.info()
            cluster_health = await self.es_client.cluster.health()
            
            # Get index statistics
            listings_stats = await self.es_client.indices.stats(index=self.LISTINGS_INDEX)
            total_docs = listings_stats["indices"][self.LISTINGS_INDEX]["total"]["docs"]["count"]
            
            return {
                "status": "healthy",
                "connected": True,
                "elasticsearch_version": info["version"]["number"],
                "cluster_status": cluster_health["status"],
                "indexed_listings": total_docs,
                "indexes": [self.LISTINGS_INDEX, self.SEARCH_ANALYTICS_INDEX]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

# Global search service instance
search_service = SearchService()

async def init_search():
    """Initialize search service"""
    await search_service.connect()

async def cleanup_search():
    """Cleanup search service"""  
    await search_service.disconnect()