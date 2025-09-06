/**
 * CATALORO - Favorites Page
 * Display user's favorite listings with real-time updates
 */

import React, { useState, useEffect } from 'react';
import { Heart, MapPin, Clock, Eye } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useMarketplace } from '../../context/MarketplaceContext';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

// Hook to get ads configuration
function useAdsConfig() {
  const [adsConfig, setAdsConfig] = useState(null);
  
  useEffect(() => {
    const loadAdsConfig = () => {
      try {
        const savedConfig = localStorage.getItem('cataloro_site_config');
        if (savedConfig) {
          const config = JSON.parse(savedConfig);
          setAdsConfig(config.adsManager || null);
        }
      } catch (error) {
        console.warn('Could not load ads configuration');
      }
    };

    // Load initially
    loadAdsConfig();

    // Listen for ads config updates
    const handleAdsConfigUpdate = () => {
      loadAdsConfig();
    };

    window.addEventListener('adsConfigUpdated', handleAdsConfigUpdate);
    window.addEventListener('storage', handleAdsConfigUpdate);

    return () => {
      window.removeEventListener('adsConfigUpdated', handleAdsConfigUpdate);
      window.removeEventListener('storage', handleAdsConfigUpdate);
    };
  }, []);
  
  return adsConfig;
}

function FavoritesPage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const navigate = useNavigate();
  const adsConfig = useAdsConfig();
  
  // Use MarketplaceContext for favorites management
  const {
    favorites,
    removeFromFavorites,
    loadUserFavorites,
    isLoading
  } = useMarketplace();

  useEffect(() => {
    if (user?.id) {
      // Load user's favorites when component mounts
      loadUserFavorites(user.id);
    }
  }, [user?.id, loadUserFavorites]);

  const handleRemoveFromFavorites = async (listingId) => {
    try {
      await removeFromFavorites(listingId, user.id);
      showToast('Removed from favorites', 'success');
    } catch {
      showToast('Failed to remove from favorites', 'error');
    }
  };



  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading your favorites...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white rounded-2xl p-8">
        <h1 className="text-3xl font-bold mb-2">My Favorites</h1>
        <p className="text-xl opacity-90">Items you've saved for later</p>
        {favorites.length > 0 && (
          <p className="text-lg opacity-80 mt-2">You have {favorites.length} favorite items</p>
        )}
      </div>

      {/* Favorites Page Advertisement */}
      {adsConfig?.favoriteAd?.active && adsConfig.favoriteAd.image && (
        <div 
          className={`bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm hover:shadow-md transition-shadow ${adsConfig.favoriteAd.url ? 'cursor-pointer' : ''}`}
          style={{ 
            width: adsConfig.favoriteAd.width || '100%',
            maxWidth: '100%'
          }}
          onClick={() => {
            if (adsConfig.favoriteAd.url) {
              // Track ad click
              console.log('Favorites ad clicked:', adsConfig.favoriteAd.url);
              window.open(adsConfig.favoriteAd.url, '_blank');
            }
          }}
        >
          <img
            src={adsConfig.favoriteAd.image}
            alt={adsConfig.favoriteAd.description || 'Advertisement'}
            className="w-full object-cover"
            style={{ height: adsConfig.favoriteAd.height || '200px' }}
          />
          {adsConfig.favoriteAd.description && (
            <div className="p-4">
              <p className="text-gray-700 dark:text-gray-300 text-sm">{adsConfig.favoriteAd.description}</p>
            </div>
          )}
        </div>
      )}

      {/* Favorites Content */}
      {favorites.length === 0 ? (
        <div className="text-center py-16">
          <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
            <Heart className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No favorites yet</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">Start browsing and save items you love</p>
          <Link
            to="/browse"
            className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors"
          >
            Browse Marketplace
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {favorites.map((item) => (
            <FavoriteCard
              key={item.id}
              item={item}
              onRemove={handleRemoveFromFavorites}
              onNavigate={navigate}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Enhanced Favorite Card Component - Matches Browse Page ProductCard exactly
function FavoriteCard({ item, onRemove, onNavigate }) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  const handleCardClick = () => {
    onNavigate(`/product/${item.id}`);
  };

  const handleFavoriteToggle = (e) => {
    e.stopPropagation();
    onRemove(item.id); // Remove from favorites
  };

  return (
    <div 
      className="product-card group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 overflow-hidden cursor-pointer hover:-translate-y-1"
      onClick={handleCardClick}
    >
      {/* Image Section - Matches Browse Page exactly */}
      <div className="relative">
        {/* Clickable overlay for image navigation */}
        <div 
          className="absolute inset-0 cursor-pointer z-10"
          onClick={(e) => {
            e.stopPropagation();
            handleCardClick();
          }}
          title="View product details"
        />
        
        <img
          src={item.images?.[currentImageIndex] || item.images?.[0] || '/api/placeholder/400/300'}
          alt={item.title}
          className="w-full h-64 object-cover transition-transform duration-300 group-hover:scale-[1.02]"
        />
        
        {/* Image Indicators */}
        {item.images && item.images.length > 1 && (
          <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex space-x-1 z-20">
            {item.images.map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full cursor-pointer ${
                  index === currentImageIndex ? 'bg-white' : 'bg-white/50'
                }`}
                onClick={(e) => {
                  e.stopPropagation();
                  setCurrentImageIndex(index);
                }}
              />
            ))}
          </div>
        )}

        {/* Tags and Badges - Matches Browse Page */}
        <div className="absolute top-2 left-2 space-y-1 z-20">
          {item.tags?.map((tag) => (
            <span
              key={tag}
              className="inline-block bg-red-500 text-white text-xs px-2 py-1 rounded-full font-medium"
            >
              {tag}
            </span>
          ))}
          
          {/* Business/Private Badge */}
          <div>
            <span
              className={`inline-block text-white text-xs px-2 py-1 rounded-full font-medium ${
                item.seller?.is_business 
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600' 
                  : 'bg-gradient-to-r from-green-600 to-emerald-600'
              }`}
            >
              {item.seller?.is_business ? 'Business' : 'Private'}
            </span>
          </div>
        </div>

        {/* Favorite Button - Shows as filled heart since it's in favorites */}
        <div className="absolute top-2 right-2 z-20">
          <button
            onClick={handleFavoriteToggle}
            className="favorites-button wishlist-button add-to-favorites p-3 bg-red-500/90 text-white backdrop-blur-lg rounded-full shadow-lg transition-all duration-300 transform hover:scale-110 shadow-red-500/25"
            title="Remove from favorites"
          >
            <Heart className="w-4 h-4 fill-current" />
          </button>
        </div>
      </div>

      {/* Product Info Section - Matches Browse Page exactly */}
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-bold text-gray-900 dark:text-white text-lg line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors flex-1 mr-2">
            {item.title}
          </h3>
        </div>
        
        {/* Price and Condition */}
        <div className="flex items-center justify-between mb-3">
          <span className="price-display text-2xl font-bold text-blue-600 dark:text-blue-400">
            €{typeof item.price === 'number' ? item.price.toLocaleString() : item.price}
          </span>
          <span className="text-sm text-gray-500 dark:text-gray-400 capitalize bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-full">
            {item.condition || 'New'}
          </span>
        </div>

        {/* Location */}
        <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-300 mb-2">
          <MapPin className="w-4 h-4" />
          <span>{item.location || 'Location not specified'}</span>
        </div>

        {/* Date and Views */}
        <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-4">
          <div className="flex items-center space-x-1">
            <Clock className="w-4 h-4" />
            <span>{new Date(item.created_at || Date.now()).toLocaleDateString()}</span>
          </div>
          {item.views && (
            <div className="flex items-center space-x-1">
              <Eye className="w-4 h-4" />
              <span>{item.views} views</span>
            </div>
          )}
        </div>

        {/* Seller Info - Matches Browse Page */}
        <div className="flex items-center space-x-3 mb-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
            {(item.seller?.name || item.seller?.username || 'U').charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {item.seller?.name || item.seller?.username || 'Unknown Seller'}
            </p>
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {item.seller?.location && (
                  <span className="flex items-center">
                    <MapPin className="w-3 h-3 mr-1" />
                    {item.seller.location}
                  </span>
                )}
              </span>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={handleCardClick}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg font-medium transition-all duration-200 flex items-center justify-center space-x-2 group-hover:bg-blue-700"
        >
          <Eye className="w-4 h-4" />
          <span>View Details</span>
        </button>
      </div>
    </div>
  );
}

export default FavoritesPage;