import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  TrendingUp, 
  Heart, 
  Eye, 
  Star,
  RefreshCw,
  ArrowRight,
  Clock,
  ThumbsUp,
  Filter
} from 'lucide-react';

const AIRecommendationsWidget = ({ 
  userId,
  category = null,
  limit = 6,
  showTrending = true,
  showPersonalized = true,
  compact = false,
  onItemClick
}) => {
  const [recommendations, setRecommendations] = useState([]);
  const [trendingItems, setTrendingItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('personalized');
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    fetchRecommendations();
    if (showTrending) {
      fetchTrendingItems();
    }
  }, [userId, category, limit]);

  const fetchRecommendations = async () => {
    if (!userId || !showPersonalized) return;

    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      let endpoint = `/api/v2/ai/recommendations/${userId}?limit=${limit}`;
      
      if (category) {
        endpoint = `/api/v2/ai/category/${userId}/${category}?limit=${limit}`;
      }

      const response = await fetch(`${backendUrl}${endpoint}`);
      const data = await response.json();
      
      if (data.success) {
        setRecommendations(data.recommendations || []);
        setLastUpdated(new Date());
      }
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
      setRecommendations([]);
    }
  };

  const fetchTrendingItems = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      let endpoint = `/v2/ai/trending?limit=${limit}`;
      
      if (category) {
        endpoint += `&category=${category}`;
      }

      const response = await fetch(`${backendUrl}${endpoint}`);
      const data = await response.json();
      
      if (data.success) {
        setTrendingItems(data.trending_items || []);
      }
    } catch (error) {
      console.error('Failed to fetch trending items:', error);
      setTrendingItems([]);
    } finally {
      setLoading(false);
    }
  };

  const trackInteraction = async (listingId, interactionType, context = {}) => {
    if (!userId) return;

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      await fetch(`${backendUrl}/v2/ai/interaction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          listing_id: listingId,
          interaction_type: interactionType,
          context: { ...context, source: 'ai_recommendations' }
        })
      });
    } catch (error) {
      console.error('Failed to track interaction:', error);
    }
  };

  const handleItemClick = async (item, source = 'recommendations') => {
    await trackInteraction(item.listing.id, 'view', { source });
    
    if (onItemClick) {
      onItemClick(item.listing);
    }
  };

  const handleRefresh = async () => {
    setLoading(true);
    await Promise.all([
      showPersonalized && fetchRecommendations(),
      showTrending && fetchTrendingItems()
    ]);
  };

  const formatPrice = (price, currency = 'EUR') => {
    const symbols = { 'EUR': '€', 'USD': '$', 'GBP': '£' };
    const symbol = symbols[currency] || currency;
    return `${symbol}${price?.toLocaleString() || 0}`;
  };

  const getReasonsDisplay = (reasons) => {
    if (!reasons || reasons.length === 0) return null;
    return reasons.slice(0, 2).join(', ');
  };

  const ItemCard = ({ item, source, showScore = false }) => {
    const listing = item.listing;
    const isRecommendation = 'score' in item;
    
    return (
      <div 
        onClick={() => handleItemClick(item, source)}
        className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600 hover:shadow-md hover:border-blue-300 dark:hover:border-blue-600 transition-all cursor-pointer group"
      >
        {/* Item Image */}
        <div className="aspect-square bg-gray-100 dark:bg-gray-700 rounded-lg mb-3 overflow-hidden">
          {listing.images && listing.images.length > 0 ? (
            <img
              src={listing.images[0]}
              alt={listing.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Sparkles className="w-8 h-8 text-gray-400" />
            </div>
          )}
        </div>

        {/* Item Details */}
        <div className="space-y-2">
          <h4 className="font-medium text-gray-900 dark:text-white line-clamp-2 text-sm">
            {listing.title || 'Untitled Listing'}
          </h4>
          
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-blue-600 dark:text-blue-400">
              {formatPrice(listing.price)}
            </span>
            {showScore && isRecommendation && (
              <div className="flex items-center space-x-1">
                <Star className="w-3 h-3 text-yellow-500" />
                <span className="text-xs text-gray-600 dark:text-gray-400">
                  {(item.score * 100).toFixed(0)}%
                </span>
              </div>
            )}
          </div>

          {/* Category */}
          {listing.category && (
            <span className="inline-block px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded">
              {listing.category}
            </span>
          )}

          {/* Recommendation Reasons */}
          {isRecommendation && item.reasons && (
            <div className="text-xs text-gray-500 dark:text-gray-500">
              {getReasonsDisplay(item.reasons)}
            </div>
          )}

          {/* Trending Score */}
          {!isRecommendation && item.trending_score && (
            <div className="flex items-center space-x-1">
              <TrendingUp className="w-3 h-3 text-green-500" />
              <span className="text-xs text-green-600 dark:text-green-400">
                Trending
              </span>
            </div>
          )}
        </div>
      </div>
    );
  };

  if (compact) {
    const items = activeTab === 'personalized' ? recommendations : trendingItems;
    
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-purple-500" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {activeTab === 'personalized' ? 'For You' : 'Trending'}
            </span>
          </div>
          
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
        
        <div className="space-y-2">
          {items.slice(0, 3).map((item, index) => (
            <div
              key={`${activeTab}-${index}`}
              onClick={() => handleItemClick(item, activeTab)}
              className="flex items-center space-x-3 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg cursor-pointer transition-colors"
            >
              <div className="w-12 h-12 bg-gray-100 dark:bg-gray-700 rounded-lg flex-shrink-0">
                {item.listing.images?.[0] ? (
                  <img
                    src={item.listing.images[0]}
                    alt={item.listing.title}
                    className="w-full h-full object-cover rounded-lg"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Sparkles className="w-4 h-4 text-gray-400" />
                  </div>
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {item.listing.title}
                </div>
                <div className="text-sm text-blue-600 dark:text-blue-400">
                  {formatPrice(item.listing.price)}
                </div>
              </div>
              
              <ArrowRight className="w-4 h-4 text-gray-400" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-600">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
            <Sparkles className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              AI Recommendations
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Personalized suggestions based on your activity
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {lastUpdated && (
            <span className="text-xs text-gray-500 dark:text-gray-500">
              Updated {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Tabs */}
      {showPersonalized && showTrending && (
        <div className="flex space-x-1 mb-6 bg-gray-100 dark:bg-gray-700 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('personalized')}
            className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'personalized'
                ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <Heart className="w-4 h-4" />
            <span>For You</span>
            {recommendations.length > 0 && (
              <span className="bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 px-2 py-0.5 rounded-full text-xs">
                {recommendations.length}
              </span>
            )}
          </button>
          
          <button
            onClick={() => setActiveTab('trending')}
            className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'trending'
                ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <TrendingUp className="w-4 h-4" />
            <span>Trending</span>
            {trendingItems.length > 0 && (
              <span className="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 px-2 py-0.5 rounded-full text-xs">
                {trendingItems.length}
              </span>
            )}
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading recommendations...</p>
          </div>
        </div>
      )}

      {/* Content */}
      {!loading && (
        <>
          {/* Personalized Recommendations */}
          {activeTab === 'personalized' && (
            <div>
              {recommendations.length === 0 ? (
                <div className="text-center py-12">
                  <Sparkles className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    No Recommendations Yet
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Browse some items to get personalized recommendations
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {recommendations.map((item, index) => (
                    <ItemCard
                      key={`rec-${index}`}
                      item={item}
                      source="personalized"
                      showScore={true}
                    />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Trending Items */}
          {activeTab === 'trending' && (
            <div>
              {trendingItems.length === 0 ? (
                <div className="text-center py-12">
                  <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    No Trending Items
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Check back later for trending items
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {trendingItems.map((item, index) => (
                    <ItemCard
                      key={`trend-${index}`}
                      item={item}
                      source="trending"
                    />
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default AIRecommendationsWidget;