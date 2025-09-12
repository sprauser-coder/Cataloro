/**
 * CATALORO - Mobile Listing Card Component
 * Enhanced mobile listing card with quick bid and market range features
 */

import React, { useState, useEffect } from 'react';
import { Heart, Eye, Clock, MapPin, Star, ChevronRight, DollarSign, TrendingUp, Database, AlertCircle, CheckCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function MobileListingCard({ listing, onFavorite, onQuickView, onBidUpdate }) {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  
  // Local state for real-time updates
  const [currentListing, setCurrentListing] = useState(listing);
  const [isFavorited, setIsFavorited] = useState(listing.favorited || false);
  const [bidAmount, setBidAmount] = useState('');
  const [isSubmittingBid, setIsSubmittingBid] = useState(false);
  const [bidError, setBidError] = useState('');
  const [bidSuccess, setBidSuccess] = useState(false);
  const [priceRangeSettings, setPriceRangeSettings] = useState({
    price_range_min_percent: 10.0,
    price_range_max_percent: 10.0
  });
  const [priceSuggestion, setPriceSuggestion] = useState(null);
  const [loadingSuggestion, setLoadingSuggestion] = useState(false);

  // Update local listing state when prop changes
  useEffect(() => {
    setCurrentListing(listing);
  }, [listing]);

  const handleFavorite = () => {
    setIsFavorited(!isFavorited);
    onFavorite?.(currentListing.id, !isFavorited);
  };

  const handleQuickView = () => {
    onQuickView?.(currentListing);
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

  // Check if current user can bid on this listing
  const canUserBid = () => {
    if (!user) return false;
    
    // Check if user is the owner of the listing
    const isOwner = currentListing.seller?.username === user.username || 
                    currentListing.seller_id === user.id || 
                    currentListing.seller?.id === user.id;
    
    if (isOwner) return false;
    
    // Check if user is already the highest bidder
    if (currentListing.bid_info?.has_bids && currentListing.bid_info?.highest_bidder_id === user.id) {
      return false;
    }
    
    return true;
  };

  // Calculate minimum bid amount
  const getMinimumBid = () => {
    if (currentListing.bid_info?.has_bids && currentListing.bid_info?.highest_bid) {
      return currentListing.bid_info.highest_bid + 1;
    }
    return currentListing.price + 1;
  };

  // Load price range settings and price suggestion on mount
  useEffect(() => {
    const fetchPriceRangeSettings = async () => {
      try {
        const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
        const response = await fetch(`${backendUrl}/api/marketplace/price-range-settings`);
        
        if (response.ok) {
          const settings = await response.json();
          setPriceRangeSettings(settings);
        }
      } catch (error) {
        console.error('Error fetching price range settings:', error);
      }
    };

    const fetchPriceSuggestion = async () => {
      // Only fetch price suggestions for catalyst items
      if (currentListing.category === 'Catalysts' && (currentListing.catalyst_id || currentListing.title)) {
        setLoadingSuggestion(true);
        try {
          const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
          const response = await fetch(`${backendUrl}/api/admin/catalyst/calculations`);
          if (response.ok) {
            const calculations = await response.json();
            
            // Find matching calculation by catalyst_id or title
            let suggestion = null;
            if (currentListing.catalyst_id) {
              suggestion = calculations.find(calc => calc.cat_id === currentListing.catalyst_id);
            } else {
              // Try to match by title
              suggestion = calculations.find(calc => 
                calc.name && calc.name.toLowerCase() === currentListing.title.toLowerCase()
              );
            }
            
            if (suggestion && suggestion.total_price) {
              setPriceSuggestion(parseFloat(suggestion.total_price));
            }
          }
        } catch (error) {
          console.error('Failed to fetch price suggestion:', error);
        } finally {
          setLoadingSuggestion(false);
        }
      }
    };

    fetchPriceRangeSettings();
    fetchPriceSuggestion();
  }, [currentListing.catalyst_id, currentListing.title, currentListing.category]);

  // Handle bid submission
  const handleSubmitBid = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!user) {
      showToast('Please login to place bids', 'error');
      return;
    }

    if (!canUserBid()) {
      if (currentListing.seller?.username === user.username || currentListing.seller_id === user.id) {
        showToast('You cannot bid on your own listing', 'error');
      } else if (currentListing.bid_info?.highest_bidder_id === user.id) {
        showToast('You are already the highest bidder', 'info');
      }
      return;
    }

    const bidValue = parseFloat(bidAmount);
    const minimumBid = getMinimumBid();

    if (!bidValue || bidValue < minimumBid) {
      setBidError(`Minimum bid: ${formatPrice(minimumBid)}`);
      return;
    }

    setBidError('');
    setIsSubmittingBid(true);

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/tenders/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('cataloro_token')}`
        },
        body: JSON.stringify({
          listing_id: currentListing.id,
          buyer_id: user.id,
          offer_amount: bidValue
        })
      });

      const data = await response.json();

      if (response.ok) {
        // Update local listing state with new bid information
        const updatedListing = {
          ...currentListing,
          bid_info: {
            ...currentListing.bid_info,
            has_bids: true,
            total_bids: (currentListing.bid_info?.total_bids || 0) + 1,
            highest_bid: bidValue,
            highest_bidder_id: user.id
          }
        };
        
        setCurrentListing(updatedListing);
        
        // Notify parent component of the bid update
        if (onBidUpdate) {
          onBidUpdate(listing.id, updatedListing);
        }
        
        setBidSuccess(true);
        setBidAmount('');
        showToast(`Bid of ${formatPrice(bidValue)} submitted successfully!`, 'success');
        
        // Hide success indicator after 3 seconds
        setTimeout(() => {
          setBidSuccess(false);
        }, 3000);
        
      } else {
        setBidError(data.detail || 'Failed to submit bid');
        showToast(data.detail || 'Failed to submit bid', 'error');
      }
    } catch (error) {
      console.error('Error submitting bid:', error);
      setBidError('Network error. Please try again.');
      showToast('Network error. Please try again.', 'error');
    } finally {
      setIsSubmittingBid(false);
    }
  };

  // Get bid button disabled state and text
  const getBidButtonState = () => {
    if (!user) {
      return { disabled: true, text: 'Login to Bid', color: 'bg-gray-400' };
    }
    
    if (!canUserBid()) {
      if (currentListing.seller?.username === user.username || currentListing.seller_id === user.id) {
        return { disabled: true, text: 'Your Listing', color: 'bg-gray-400' };
      } else if (currentListing.bid_info?.highest_bidder_id === user.id) {
        return { disabled: true, text: 'Highest Bidder', color: 'bg-green-500' };
      }
    }
    
    if (isSubmittingBid) {
      return { disabled: true, text: 'Submitting...', color: 'bg-blue-400' };
    }
    
    if (bidSuccess) {
      return { disabled: true, text: 'Bid Submitted!', color: 'bg-green-500' };
    }
    
    return { disabled: false, text: 'Place Bid', color: 'bg-blue-600 hover:bg-blue-700' };
  };

  const buttonState = getBidButtonState();

  return (
    <div className="relative mb-4">
      {/* Main Card - Simplified without swipe functionality */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        {/* Clickable Image Section */}
        <Link to={`/listing/${currentListing.id}`} className="block">
          {/* Image */}
          <div className="relative aspect-video bg-gray-100 dark:bg-gray-700">
            {currentListing.images && currentListing.images.length > 0 ? (
              <img
                src={currentListing.images[0]}
                alt={currentListing.title}
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
            {currentListing.isHotDeal && (
              <div className="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded-full text-xs font-medium">
                Hot Deal
              </div>
            )}

            {/* Image count indicator */}
            {currentListing.images && currentListing.images.length > 1 && (
              <div className="absolute bottom-2 right-2 bg-black/50 text-white px-2 py-1 rounded-full text-xs">
                +{currentListing.images.length - 1}
              </div>
            )}
          </div>
        </Link>

        {/* Non-clickable Content Section */}
        <div className="p-4">
            {/* Title and Price - Clickable for navigation */}
            <Link to={`/listing/${currentListing.id}`} className="block">
              <div className="flex justify-between items-start mb-2 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg p-2 -m-2 transition-colors">
                <h3 className="font-semibold text-gray-900 dark:text-white text-lg leading-tight flex-1 mr-2">
                  {currentListing.title}
                </h3>
                <div className="text-right">
                  <p className="text-xl font-bold text-blue-600 dark:text-blue-400">
                    {formatPrice(currentListing.bid_info?.has_bids && currentListing.bid_info?.highest_bid 
                      ? currentListing.bid_info.highest_bid 
                      : currentListing.price)}
                  </p>
                  {currentListing.bid_info?.has_bids && currentListing.bid_info?.total_bids > 0 && (
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {currentListing.bid_info.total_bids} bid{currentListing.bid_info.total_bids !== 1 ? 's' : ''}
                    </p>
                  )}
                </div>
              </div>
            </Link>

            {/* Description - REMOVED per user requirements */}

            {/* Market Range - Show for catalyst items */}
            {currentListing.category === 'Catalysts' && (
              <div className="mb-3">
                {loadingSuggestion ? (
                  <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 p-3 bg-gray-50 dark:bg-gray-800 rounded-xl">
                    <div className="w-3 h-3 border border-gray-400 border-t-transparent rounded-full animate-spin mr-2"></div>
                    Loading market range...
                  </div>
                ) : priceSuggestion ? (
                  <div className="relative overflow-hidden rounded-xl bg-gradient-to-br from-indigo-50 via-blue-50 to-cyan-50 dark:from-indigo-900/40 dark:via-blue-900/40 dark:to-cyan-900/40 border border-indigo-100 dark:border-indigo-800/60 shadow-sm">
                    <div className="absolute top-0 right-0 w-8 h-8 bg-gradient-to-bl from-indigo-200/20 to-transparent dark:from-indigo-600/10 rounded-bl-full"></div>
                    <div className="relative p-3">
                      <div className="flex items-center space-x-2">
                        <div className="p-1 rounded-lg bg-gradient-to-r from-indigo-500 to-blue-500 shadow-sm">
                          <Database className="w-3 h-3 text-white" />
                        </div>
                        <div>
                          <div className="text-xs font-medium text-indigo-700 dark:text-indigo-300 uppercase tracking-wide">
                            Market Range
                          </div>
                          <div className="text-sm font-bold text-indigo-900 dark:text-indigo-100 leading-tight">
                            €{(priceSuggestion * (100 - priceRangeSettings.price_range_min_percent) / 100).toFixed(0)} - €{(priceSuggestion * (100 + priceRangeSettings.price_range_max_percent) / 100).toFixed(0)}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : null}
              </div>
            )}

            {/* Metadata - Clickable for navigation */}
            <Link to={`/listing/${currentListing.id}`}>
              <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 mb-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg p-2 -m-2 transition-colors">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center">
                    <MapPin className="w-4 h-4 mr-1" />
                    <span>{currentListing.location || 'Location'}</span>
                  </div>
                  <div className="flex items-center">
                    <Clock className="w-4 h-4 mr-1" />
                    <span>{formatTimeAgo(currentListing.created_at)}</span>
                  </div>
                </div>
                
                {currentListing.rating && (
                  <div className="flex items-center">
                    <Star className="w-4 h-4 text-yellow-400 fill-current mr-1" />
                    <span>{currentListing.rating}</span>
                  </div>
                )}
              </div>
            </Link>

            {/* Quick Bid Input Field - Always Visible */}
            <div className="mb-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600">
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Quick Bid</span>
                {currentListing.bid_info?.has_bids && (
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    Min: {formatPrice(getMinimumBid())}
                  </span>
                )}
              </div>
              
              <form onSubmit={handleSubmitBid} className="space-y-2">
                <div className="flex space-x-2">
                  <div className="flex-1 relative">
                    <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="number"
                      min={getMinimumBid()}
                      step="1"
                      value={bidAmount}
                      onChange={(e) => {
                        setBidAmount(e.target.value);
                        setBidError('');
                      }}
                      placeholder={`Min: €${getMinimumBid()}`}
                      className="w-full pl-10 pr-4 py-2 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={!canUserBid() && user}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={buttonState.disabled}
                    className={`px-4 py-2 text-white text-sm font-medium rounded-lg transition-colors flex items-center ${buttonState.color}`}
                    onClick={(e) => e.stopPropagation()}
                  >
                    {isSubmittingBid && (
                      <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin mr-1"></div>
                    )}
                    {bidSuccess && (
                      <CheckCircle className="w-3 h-3 mr-1" />
                    )}
                    <span className="text-xs">{buttonState.text}</span>
                  </button>
                </div>
                
                {/* Error/Success Messages */}
                {bidError && (
                  <div className="flex items-center text-red-600 dark:text-red-400 text-xs">
                    <AlertCircle className="w-3 h-3 mr-1" />
                    {bidError}
                  </div>
                )}
                
                {bidSuccess && (
                  <div className="flex items-center text-green-600 dark:text-green-400 text-xs">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Bid submitted successfully!
                  </div>
                )}
              </form>
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
      </div>
    </div>
  );
}

export default MobileListingCard;