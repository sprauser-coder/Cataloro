/**
 * CATALORO - AI-Powered Recommendations Panel
 * Personalized product recommendations based on user behavior and preferences
 */

import React, { useState, useEffect } from 'react';
import { Sparkles, Heart, TrendingUp, User, Eye, Star } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useMarketplace } from '../../context/MarketplaceContext';
import { useNotifications } from '../../context/NotificationContext';

function RecommendationsPanel({ className = "", limit = 6 }) {
  const [recommendations, setRecommendations] = useState([]);
  const [userProfile, setUserProfile] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const { user } = useAuth();
  const { actions } = useMarketplace();
  const { showToast } = useNotifications();

  useEffect(() => {
    if (user?.id) {
      loadRecommendations();
    } else {
      loadPopularItems();
    }
  }, [user, limit]);

  const loadRecommendations = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/recommendations/${user.id}?limit=${limit}`
      );

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations || []);
        setUserProfile(data.user_profile || {});
      } else {
        throw new Error('Failed to load recommendations');
      }
    } catch (error) {
      console.error('Error loading recommendations:', error);
      setError('Failed to load recommendations');
      // Fallback to popular items
      loadPopularItems();
    } finally {
      setIsLoading(false);
    }
  };

  const loadPopularItems = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/marketplace/browse?limit=${limit}`
      );

      if (response.ok) {
        const data = await response.json();
        setRecommendations(Array.isArray(data) ? data.slice(0, limit) : []);
        setUserProfile({ preferred_categories: [], average_price: 0, interaction_count: 0 });
      } else {
        throw new Error('Failed to load popular items');
      }
    } catch (error) {
      console.error('Error loading popular items:', error);
      setError('Failed to load items');
      setRecommendations([]);
    } finally {
      setIsLoading(false);
    }
  };



  const handleAddToFavorites = async (product) => {
    try {
      await actions.addToFavorites(product, user?.id);
      showToast(`Added ${product.title} to favorites!`, 'success');
    } catch (error) {
      console.error('Error adding to favorites:', error);
      showToast('Failed to add item to favorites', 'error');
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const getRecommendationReason = (product, profile) => {
    if (!user?.id) return "Popular item";
    
    if (profile.preferred_categories?.includes(product.category)) {
      return `Based on your interest in ${product.category}`;
    }
    
    if (profile.average_price && Math.abs(product.price - profile.average_price) < profile.average_price * 0.3) {
      return "Matches your price range";
    }
    
    if (product.views > 100) {
      return "Trending item";
    }
    
    return "Recommended for you";
  };

  if (isLoading) {
    return (
      <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
        <div className="flex items-center mb-4">
          <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-500 border-t-transparent mr-3"></div>
          <h3 className="text-lg font-semibold text-gray-900">Loading Recommendations...</h3>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(limit)].map((_, index) => (
            <div key={index} className="animate-pulse">
              <div className="bg-gray-200 h-48 rounded-lg mb-3"></div>
              <div className="bg-gray-200 h-4 rounded mb-2"></div>
              <div className="bg-gray-200 h-3 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error && recommendations.length === 0) {
    return (
      <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
        <div className="text-center">
          <Sparkles className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Recommendations Unavailable</h3>
          <p className="text-gray-600 text-sm">We're having trouble loading recommendations right now.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg mr-3">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {user?.id ? 'Recommended for You' : 'Popular Items'}
              </h3>
              <p className="text-sm text-gray-600">
                {user?.id && userProfile.interaction_count > 0 
                  ? `Based on your ${userProfile.interaction_count} interactions`
                  : 'Discover amazing products'
                }
              </p>
            </div>
          </div>
          
          {user?.id && userProfile.preferred_categories?.length > 0 && (
            <div className="hidden sm:flex items-center space-x-2">
              {userProfile.preferred_categories.slice(0, 2).map((category, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full"
                >
                  {category}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* User Profile Summary */}
      {user?.id && userProfile.interaction_count > 0 && (
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-4">
              <div className="flex items-center text-gray-600">
                <User className="h-4 w-4 mr-1" />
                <span>{userProfile.interaction_count} interactions</span>
              </div>
              {userProfile.average_price > 0 && (
                <div className="flex items-center text-gray-600">
                  <TrendingUp className="h-4 w-4 mr-1" />
                  <span>Avg: {formatPrice(userProfile.average_price)}</span>
                </div>
              )}
            </div>
            
            <button
              onClick={loadRecommendations}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Refresh
            </button>
          </div>
        </div>
      )}

      {/* Recommendations Grid */}
      {recommendations.length > 0 ? (
        <div className="p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {recommendations.map((product, index) => (
              <div
                key={product.id || index}
                className="group relative bg-white border border-gray-200 rounded-lg hover:shadow-md transition-all duration-200"
              >
                {/* Product Image */}
                <div className="aspect-w-16 aspect-h-12 relative overflow-hidden rounded-t-lg">
                  <img
                    src={product.images?.[0] || product.image || '/api/placeholder/400/300'}
                    alt={product.title}
                    className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-200"
                  />
                  
                  {/* Quick Actions Overlay */}
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex space-x-2">
                      <button
                        onClick={() => handleAddToFavorites(product)}
                        className="p-2 bg-white rounded-full shadow-lg hover:bg-gray-50 transition-colors duration-200"
                      >
                        <Heart className="h-4 w-4 text-gray-600" />
                      </button>
                      <button
                        onClick={() => handleAddToCart(product)}
                        className="p-2 bg-blue-600 rounded-full shadow-lg hover:bg-blue-700 transition-colors duration-200"
                      >
                        <ShoppingCart className="h-4 w-4 text-white" />
                      </button>
                    </div>
                  </div>

                  {/* AI Badge */}
                  <div className="absolute top-2 left-2">
                    <span className="inline-flex items-center px-2 py-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-xs font-medium rounded-full">
                      <Sparkles className="h-3 w-3 mr-1" />
                      AI
                    </span>
                  </div>
                </div>

                {/* Product Info */}
                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="text-sm font-semibold text-gray-900 line-clamp-2 group-hover:text-blue-600 transition-colors duration-200">
                      {product.title}
                    </h4>
                    {product.rating && (
                      <div className="flex items-center ml-2">
                        <Star className="h-3 w-3 text-yellow-400 fill-current" />
                        <span className="text-xs text-gray-600 ml-1">{product.rating}</span>
                      </div>
                    )}
                  </div>

                  <p className="text-xs text-gray-600 mb-3 line-clamp-2">
                    {getRecommendationReason(product, userProfile)}
                  </p>

                  <div className="flex items-center justify-between">
                    <div className="flex flex-col">
                      <span className="text-lg font-bold text-gray-900">
                        {formatPrice(product.price)}
                      </span>
                      {product.originalPrice && product.originalPrice > product.price && (
                        <span className="text-xs text-gray-500 line-through">
                          {formatPrice(product.originalPrice)}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      {product.views && (
                        <div className="flex items-center">
                          <Eye className="h-3 w-3 mr-1" />
                          <span>{product.views}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Category Badge */}
                  <div className="mt-3">
                    <span className="inline-block px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">
                      {product.category}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* View More Button */}
          <div className="text-center mt-6">
            <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-200">
              View More Recommendations
              <TrendingUp className="ml-2 h-4 w-4" />
            </button>
          </div>
        </div>
      ) : (
        <div className="p-6 text-center">
          <Sparkles className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h4 className="text-lg font-medium text-gray-900 mb-2">No Recommendations Yet</h4>
          <p className="text-gray-600 text-sm">
            Start browsing and adding items to favorites to get personalized recommendations!
          </p>
        </div>
      )}
    </div>
  );
}

export default RecommendationsPanel;