/**
 * CATALORO - Mobile Listing Card Component
 * Swipeable listing card optimized for mobile with touch gestures
 */

import React, { useState } from 'react';
import { Heart, Eye, Clock, MapPin, Star, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';

function MobileListingCard({ listing, onFavorite, onQuickView }) {
  const [isFavorited, setIsFavorited] = useState(listing.favorited || false);

  const handleFavorite = () => {
    setIsFavorited(!isFavorited);
    onFavorite?.(listing.id, !isFavorited);
  };

  const handleQuickView = () => {
    onQuickView?.(listing);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    return `${Math.floor(diffInHours / 24)}d ago`;
  };

  return (
    <div className="relative mb-4">
      {/* Main Card - Simplified without swipe functionality */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <Link to={`/listing/${listing.id}`} className="block">
          {/* Image */}
          <div className="relative aspect-video bg-gray-100 dark:bg-gray-700">
            {listing.images && listing.images.length > 0 ? (
              <img
                src={listing.images[0]}
                alt={listing.title}
                className="w-full h-full object-cover"
                loading="lazy"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <div className="text-gray-400 text-center">
                  <div className="w-12 h-12 bg-gray-200 dark:bg-gray-600 rounded-lg mx-auto mb-2 flex items-center justify-center">
                    <span className="text-lg font-bold">C</span>
                  </div>
                  <p className="text-sm">No Image</p>
                </div>
              </div>
            )}

            {/* Quick action buttons */}
            <div className="absolute top-2 right-2 flex space-x-2">
              <button
                onClick={(e) => { e.preventDefault(); handleQuickView(); }}
                className="p-2 bg-black/50 text-white rounded-full backdrop-blur-sm hover:bg-black/70 transition-colors"
              >
                <Eye className="w-4 h-4" />
              </button>
            </div>

            {/* Hot deal badge */}
            {listing.isHotDeal && (
              <div className="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-medium">
                Hot Deal
              </div>
            )}

            {/* Image count indicator */}
            {listing.images && listing.images.length > 1 && (
              <div className="absolute bottom-2 right-2 bg-black/50 text-white px-2 py-1 rounded-full text-xs">
                +{listing.images.length - 1}
              </div>
            )}
          </div>

          {/* Content */}
          <div className="p-4">
            {/* Title and Price */}
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold text-gray-900 dark:text-white text-lg leading-tight flex-1 mr-2">
                {listing.title}
              </h3>
              <div className="text-right">
                <p className="text-xl font-bold text-blue-600 dark:text-blue-400">
                  {formatPrice(listing.bid_info?.has_bids && listing.bid_info?.highest_bid 
                    ? listing.bid_info.highest_bid 
                    : listing.price)}
                </p>
                {listing.bid_info?.has_bids && listing.bid_info?.total_bids > 0 && (
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {listing.bid_info.total_bids} bid{listing.bid_info.total_bids !== 1 ? 's' : ''}
                  </p>
                )}
              </div>
            </div>

            {/* Description */}
            <p className="text-gray-600 dark:text-gray-300 text-sm mb-3 line-clamp-2">
              {listing.description}
            </p>

            {/* Metadata */}
            <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-3">
              <div className="flex items-center space-x-3">
                <div className="flex items-center">
                  <MapPin className="w-4 h-4 mr-1" />
                  <span>{listing.location || 'Location'}</span>
                </div>
                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  <span>{formatTimeAgo(listing.created_at)}</span>
                </div>
              </div>
              
              {listing.rating && (
                <div className="flex items-center">
                  <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
                  <span>{listing.rating}</span>
                </div>
              )}
            </div>

            {/* Action Bar - Simplified without contact */}
            <div className="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-700">
              <button
                onClick={(e) => { e.preventDefault(); handleFavorite(); }}
                className={`flex items-center space-x-1 px-4 py-2 rounded-lg transition-colors ${
                  isFavorited
                    ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                <Heart className={`w-4 h-4 ${isFavorited ? 'fill-current' : ''}`} />
                <span className="text-sm">Save</span>
              </button>

              <ChevronRight className="w-5 h-5 text-gray-400" />
            </div>
          </div>
        </Link>
      </div>
    </div>
  );
}

export default MobileListingCard;