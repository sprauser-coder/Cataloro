/**
 * CATALORO - Mobile Listing Card Component
 * Swipeable listing card optimized for mobile with touch gestures
 */

import React, { useState, useRef } from 'react';
import { Heart, MessageCircle, Eye, Clock, MapPin, Star, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';

function MobileListingCard({ listing, onFavorite, onContact, onQuickView }) {
  const [isFavorited, setIsFavorited] = useState(listing.favorited || false);
  const [swipeDirection, setSwipeDirection] = useState(null);
  const [dragOffset, setDragOffset] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const cardRef = useRef(null);
  const startPos = useRef({ x: 0, y: 0 });

  // Touch event handlers for swipe gestures
  const handleTouchStart = (e) => {
    const touch = e.touches[0];
    startPos.current = { x: touch.clientX, y: touch.clientY };
    setIsDragging(true);
  };

  const handleTouchMove = (e) => {
    if (!isDragging) return;
    
    const touch = e.touches[0];
    const deltaX = touch.clientX - startPos.current.x;
    const deltaY = Math.abs(touch.clientY - startPos.current.y);
    
    // Only allow horizontal swipe if it's predominantly horizontal
    if (deltaY < 50) {
      setDragOffset(deltaX);
      
      // Determine swipe direction
      if (deltaX > 50) {
        setSwipeDirection('right'); // Favorite action
      } else if (deltaX < -50) {
        setSwipeDirection('left'); // Contact action
      } else {
        setSwipeDirection(null);
      }
    }
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
    
    // Execute action based on swipe
    if (swipeDirection === 'right' && dragOffset > 100) {
      handleFavorite();
    } else if (swipeDirection === 'left' && dragOffset < -100) {
      handleContact();
    }
    
    // Reset swipe state
    setDragOffset(0);
    setSwipeDirection(null);
  };

  const handleFavorite = () => {
    setIsFavorited(!isFavorited);
    onFavorite?.(listing.id, !isFavorited);
  };

  const handleContact = () => {
    onContact?.(listing);
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
      {/* Swipe Actions Background - Simplified to only favorite */}
      <div className="absolute inset-0 rounded-xl overflow-hidden">
        {/* Right swipe action (Favorite only) */}
        <div className={`absolute left-0 top-0 bottom-0 bg-red-500 flex items-center justify-center px-6 transition-all duration-200 ${
          swipeDirection === 'right' ? 'w-24' : 'w-0'
        }`}>
          <Heart className={`w-6 h-6 text-white ${isFavorited ? 'fill-current' : ''}`} />
        </div>
      </div>

      {/* Main Card */}
      <div
        ref={cardRef}
        className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden transition-transform duration-200"
        style={{
          transform: `translateX(${dragOffset}px)`,
          zIndex: isDragging ? 10 : 1
        }}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
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
                  {formatPrice(listing.price)}
                </p>
                {listing.originalPrice && listing.originalPrice > listing.price && (
                  <p className="text-sm text-gray-500 line-through">
                    {formatPrice(listing.originalPrice)}
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

            {/* Action Bar */}
            <div className="flex items-center justify-between pt-3 border-t border-gray-100 dark:border-gray-700">
              <div className="flex space-x-4">
                <button
                  onClick={(e) => { e.preventDefault(); handleFavorite(); }}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-lg transition-colors ${
                    isFavorited
                      ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  <Heart className={`w-4 h-4 ${isFavorited ? 'fill-current' : ''}`} />
                  <span className="text-sm">Save</span>
                </button>

                <button
                  onClick={(e) => { e.preventDefault(); handleContact(); }}
                  className="flex items-center space-x-1 px-3 py-2 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
                >
                  <MessageCircle className="w-4 h-4" />
                  <span className="text-sm">Contact</span>
                </button>
              </div>

              <ChevronRight className="w-5 h-5 text-gray-400" />
            </div>
          </div>
        </Link>
      </div>

      {/* Swipe hints */}
      {!isDragging && (
        <div className="absolute -bottom-6 left-0 right-0 flex justify-between px-4 text-xs text-gray-400">
          <span>← Swipe for favorite</span>
          <span>Swipe for contact →</span>
        </div>
      )}
    </div>
  );
}

export default MobileListingCard;