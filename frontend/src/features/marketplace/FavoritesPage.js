/**
 * CATALORO - Favorites Page
 * Display user's favorite listings with real-time updates
 */

import React, { useState, useEffect } from 'react';
import { Heart, Trash2, ExternalLink, ShoppingCart, MessageCircle, Star, MapPin, Clock } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useMarketplace } from '../../context/MarketplaceContext';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function FavoritesPage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const navigate = useNavigate();
  
  // Use MarketplaceContext for favorites management
  const {
    favorites,
    removeFromFavorites,
    addToCart,
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
    } catch (error) {
      showToast('Failed to remove from favorites', 'error');
    }
  };

  const handleAddToCart = async (item) => {
    try {
      await addToCart(item, user.id);
      showToast(`Added ${item.title} to cart!`, 'success');
    } catch (error) {
      showToast('Failed to add to cart', 'error');
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
              onAddToCart={handleAddToCart}
              onNavigate={navigate}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Enhanced Favorite Card Component
function FavoriteCard({ item, onRemove, onAddToCart, onNavigate }) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isHovered, setIsHovered] = useState(false);

  const handleNextImage = (e) => {
    e.stopPropagation();
    if (item.images && item.images.length > 1) {
      setCurrentImageIndex((prev) => (prev + 1) % item.images.length);
    }
  };

  const handleCardClick = () => {
    onNavigate(`/product/${item.id}`);
  };

  const handleQuickAction = (e, action) => {
    e.stopPropagation();
    action();
  };

  return (
    <div 
      className="group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 overflow-hidden cursor-pointer hover:-translate-y-2"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleCardClick}
    >
      {/* Image Section */}
      <div className="relative">
        <img
          src={item.images?.[currentImageIndex] || item.images?.[0] || '/api/placeholder/400/300'}
          alt={item.title}
          className="w-full h-64 object-cover transition-transform duration-300 group-hover:scale-105"
          onClick={handleNextImage}
        />
        
        {/* Image Indicators */}
        {item.images && item.images.length > 1 && (
          <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex space-x-1">
            {item.images.map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full ${
                  index === currentImageIndex ? 'bg-white' : 'bg-white/50'
                }`}
              />
            ))}
          </div>
        )}

        {/* Favorite Badge */}
        <div className="absolute top-2 left-2">
          <span className="inline-block bg-red-500 text-white text-xs px-2 py-1 rounded-full font-medium">
            ❤️ Favorite
          </span>
        </div>

        {/* Remove from Favorites Button */}
        <div className={`absolute top-2 right-2 transition-opacity duration-200 ${
          isHovered ? 'opacity-100' : 'opacity-0'
        }`}>
          <button
            onClick={(e) => handleQuickAction(e, () => onRemove(item.id))}
            className="p-2 bg-white/90 dark:bg-gray-800/90 rounded-full shadow-sm transition-all duration-200 text-red-500 hover:text-red-600"
          >
            <Heart className="w-5 h-5 fill-current" />
          </button>
        </div>

        {/* Favorited Date */}
        {item.favorited_at && (
          <div className="absolute bottom-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded-full">
            Added {new Date(item.favorited_at).toLocaleDateString()}
          </div>
        )}
      </div>

      {/* Content Section */}
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold text-lg text-gray-900 dark:text-white group-hover:text-blue-600 transition-colors line-clamp-2">
            {item.title}
          </h3>
        </div>

        {/* Price Section */}
        <div className="flex items-center space-x-2 mb-3">
          <span className="text-2xl font-bold text-gray-900 dark:text-white">
            ${parseFloat(item.price).toFixed(2)}
          </span>
          {item.original_price && item.original_price > item.price && (
            <>
              <span className="text-lg text-gray-500 line-through">
                ${parseFloat(item.original_price).toFixed(2)}
              </span>
              <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-medium">
                {Math.round((1 - item.price / item.original_price) * 100)}% off
              </span>
            </>
          )}
        </div>

        {/* Rating and Reviews */}
        {item.rating && (
          <div className="flex items-center space-x-2 mb-3">
            <div className="flex items-center">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-4 h-4 ${
                    i < Math.floor(item.rating || 0)
                      ? 'text-yellow-400 fill-current'
                      : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {item.rating} ({item.seller?.reviews || 0} reviews)
            </span>
          </div>
        )}

        {/* Seller Info */}
        <div className="flex items-center space-x-2 mb-3">
          <div className="w-6 h-6 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
            <span className="text-white text-xs font-bold">
              {item.seller?.charAt(0) || 'S'}
            </span>
          </div>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {item.seller || 'Unknown Seller'}
          </span>
          {item.verified && (
            <span className="text-blue-500 text-xs">✓ Verified</span>
          )}
        </div>

        {/* Location and Category */}
        <div className="text-sm text-gray-500 dark:text-gray-400 mb-4 space-y-1">
          {item.location && (
            <div className="flex items-center">
              <MapPin className="w-4 h-4 mr-1" />
              {item.location}
            </div>
          )}
          <div className="flex items-center justify-between">
            <span className="inline-block bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs px-2 py-1 rounded-full">
              {item.category}
            </span>
            <span className="text-xs">
              Condition: {item.condition}
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-2">
          <button
            onClick={(e) => handleQuickAction(e, () => onAddToCart(item))}
            className="flex-1 flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-lg font-medium transition-colors"
          >
            <ShoppingCart className="w-4 h-4" />
            <span>Add to Cart</span>
          </button>
          <button 
            onClick={(e) => handleQuickAction(e, () => {})}
            className="px-4 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <MessageCircle className="w-4 h-4" />
          </button>
          <button
            onClick={(e) => handleQuickAction(e, () => onRemove(item.id))}
            className="px-4 py-2.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default FavoritesPage;