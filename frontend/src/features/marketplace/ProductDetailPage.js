/**
 * CATALORO - Ultra-Modern Product Detail Page
 * Comprehensive product viewing with full functionality
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMarketplace } from '../../context/MarketplaceContext';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import {
  Heart,
  Share2,
  DollarSign,
  Star,
  MapPin,
  Truck,
  Shield,
  Clock,
  Eye,
  MessageCircle,
  Plus,
  Minus,
  ArrowLeft,
  Check,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Verified,
  Award,
  TrendingUp,
  Database,
  Info
} from 'lucide-react';

// Countdown Timer Component - Returns formatted time text
function CountdownTimer({ timeInfo }) {
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [isExpired, setIsExpired] = useState(false);
  
  useEffect(() => {
    if (!timeInfo?.has_time_limit || timeInfo.time_remaining_seconds === undefined || timeInfo.time_remaining_seconds === null) {
      return;
    }
    
    let initialSeconds = timeInfo.time_remaining_seconds;
    setTimeRemaining(initialSeconds);
    setIsExpired(initialSeconds <= 0);
    
    const interval = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          setIsExpired(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => clearInterval(interval);
  }, [timeInfo]);
  
  const formatTime = (seconds) => {
    if (seconds <= 0) return "EXPIRED";
    
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`;
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };
  
  if (!timeInfo?.has_time_limit) return null;
  
  return (
    <span>{isExpired ? 'EXPIRED' : formatTime(timeRemaining)}</span>
  );
}

function ProductDetailPage() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const {
    allProducts,
    addToFavorites,
    removeFromFavorites,
    favorites,
    addToRecentlyViewed,
    showNotification
  } = useMarketplace();

  const [product, setProduct] = useState(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [selectedTab, setSelectedTab] = useState('description');
  const [loading, setLoading] = useState(true);
  const [tenderAmount, setTenderAmount] = useState('');
  const [submittingTender, setSubmittingTender] = useState(false);
  const [tenderConfirmation, setTenderConfirmation] = useState(null);
  const [priceSuggestion, setPriceSuggestion] = useState(null);
  const [loadingSuggestion, setLoadingSuggestion] = useState(false);

  useEffect(() => {
    const foundProduct = allProducts.find(p => p.id === productId);
    if (foundProduct) {
      setProduct(foundProduct);
      addToRecentlyViewed(foundProduct);
      setLoading(false);
    } else {
      // If not found, redirect to browse
      navigate('/browse');
    }
  }, [productId, allProducts, navigate, addToRecentlyViewed]);

  // Fetch price suggestion for catalyst items
  useEffect(() => {
    const fetchPriceSuggestion = async () => {
      if (product && product.category === 'Catalysts' && (product.catalyst_id || product.title)) {
        setLoadingSuggestion(true);
        try {
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/catalyst/calculations`);
          if (response.ok) {
            const calculations = await response.json();
            
            let suggestion = null;
            if (product.catalyst_id) {
              suggestion = calculations.find(calc => calc.cat_id === product.catalyst_id);
            } else {
              suggestion = calculations.find(calc => 
                calc.name && calc.name.toLowerCase() === product.title.toLowerCase()
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

    fetchPriceSuggestion();
  }, [product]);

  if (loading || !product) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading product details...</p>
        </div>
      </div>
    );
  }

  const isFavorite = favorites.some(fav => fav.id === product.id);
  const images = product.images || [product.image || 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500'];

  const handleSubmitTender = async () => {
    if (!user) {
      showToast('Please login to submit tender offers', 'error');
      return;
    }

    if (product.seller?.username === user.username || product.seller_id === user.id) {
      showToast('You cannot bid on your own listing', 'error');
      return;
    }

    const offerAmount = parseFloat(tenderAmount);
    const minimumBid = product.highest_bid || product.price || 0;

    if (!offerAmount || offerAmount < minimumBid) {
      showToast(`Please enter an amount of at least €${minimumBid.toFixed(2)}`, 'error');
      return;
    }

    setSubmittingTender(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tenders/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          listing_id: product.id,
          buyer_id: user.id,
          offer_amount: offerAmount
        })
      });

      const data = await response.json();

      if (response.ok) {
        showToast(`Tender offer of €${offerAmount.toFixed(2)} submitted successfully!`, 'success');
        setTenderAmount(''); // Clear input
        
        // Show confirmation message
        setTenderConfirmation({
          amount: offerAmount,
          timestamp: new Date(),
          visible: true
        });
        
        // Hide confirmation after 8 seconds (longer for detail page)
        setTimeout(() => {
          setTenderConfirmation(prev => prev ? { ...prev, visible: false } : null);
        }, 8000);
        
        // Update product with new highest bid if this is higher
        if (offerAmount > (product.highest_bid || 0)) {
          setProduct(prev => ({ ...prev, highest_bid: offerAmount }));
        }
        
      } else if (response.status === 400) {
        showToast(data.detail || 'Invalid tender offer', 'error');
      } else {
        showToast(data.detail || 'Failed to submit tender offer', 'error');
      }
    } catch (error) {
      console.error('Error submitting tender:', error);
      showToast('Failed to submit tender offer. Please try again.', 'error');
    } finally {
      setSubmittingTender(false);
    }
  };

  const handleAddToFavorites = () => {
    if (isFavorite) {
      removeFromFavorites(product.id);
    } else {
      addToFavorites(product);
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: product.title,
        text: product.description,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      showNotification('Product link copied to clipboard!', 'success');
    }
  };

  const relatedProducts = allProducts
    .filter(p => p.id !== product.id && p.category === product.category)
    .slice(0, 4);

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      
      {/* Breadcrumb */}
      <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
        <button
          onClick={() => navigate('/browse')}
          className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
        >
          Browse
        </button>
        <span>›</span>
        <button
          onClick={() => navigate(`/browse?category=${encodeURIComponent(product.category)}`)}
          className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
        >
          {product.category}
        </button>
        <span>›</span>
        <span className="text-gray-900 dark:text-white font-medium">{product.title}</span>
      </div>

      {/* Back Button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
      >
        <ArrowLeft className="w-5 h-5" />
        <span>Back</span>
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        
        {/* Product Images */}
        <div className="space-y-4">
          {/* Main Image */}
          <div className="relative bg-gray-100 dark:bg-gray-800 rounded-2xl overflow-hidden aspect-square">
            <img
              src={images[selectedImageIndex]}
              alt={product.title}
              className="w-full h-full object-cover"
            />
            
            {/* Navigation Arrows */}
            {images.length > 1 && (
              <>
                <button
                  onClick={() => setSelectedImageIndex(prev => (prev - 1 + images.length) % images.length)}
                  className="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-white dark:hover:bg-gray-700 transition-colors"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setSelectedImageIndex(prev => (prev + 1) % images.length)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-white dark:hover:bg-gray-700 transition-colors"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </>
            )}

            {/* Image Counter */}
            {images.length > 1 && (
              <div className="absolute bottom-4 right-4 bg-black/50 text-white px-3 py-1 rounded-full text-sm">
                {selectedImageIndex + 1} / {images.length}
              </div>
            )}
          </div>

          {/* Thumbnail Images */}
          {images.length > 1 && (
            <div className="flex space-x-2 overflow-x-auto pb-2">
              {images.map((image, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedImageIndex(index)}
                  className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-colors ${
                    selectedImageIndex === index
                      ? 'border-blue-600'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <img
                    src={image}
                    alt={`${product.title} ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Product Information */}
        <div className="space-y-6">
          
          {/* Title and Basic Info */}
          <div>
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                  {product.title}
                </h1>
                
                {/* Seller Info */}
                <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                  <span>Sold by</span>
                  <div className="flex items-center space-x-1">
                    <span className="font-medium text-gray-900 dark:text-white">
                      {product.seller?.name || product.seller || 'Verified Seller'}
                    </span>
                    {product.seller?.verified && (
                      <Verified className="w-4 h-4 text-blue-600" />
                    )}
                  </div>
                  {product.seller?.location && (
                    <>
                      <span>•</span>
                      <div className="flex items-center space-x-1">
                        <MapPin className="w-4 h-4" />
                        <span>{product.seller.location}</span>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleAddToFavorites}
                  className={`p-3 rounded-full border transition-colors ${
                    isFavorite
                      ? 'border-red-500 bg-red-50 dark:bg-red-900/20 text-red-600'
                      : 'border-gray-300 dark:border-gray-600 hover:border-red-500 hover:text-red-600'
                  }`}
                >
                  <Heart className={`w-5 h-5 ${isFavorite ? 'fill-current' : ''}`} />
                </button>
                <button
                  onClick={handleShare}
                  className="p-3 rounded-full border border-gray-300 dark:border-gray-600 hover:border-blue-500 hover:text-blue-600 transition-colors"
                >
                  <Share2 className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Views Counter - Remove Rating Section */}
            <div className="flex items-center space-x-1 text-gray-600 dark:text-gray-400 mb-4">
              <Eye className="w-4 h-4" />
              <span>{product.views || 0} views</span>
            </div>
          </div>

          {/* Price Section */}
          <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
            <div className="flex items-center space-x-4 mb-4">
              <div className="text-4xl font-bold text-gray-900 dark:text-white">
                €{((product.bid_info?.has_bids && product.bid_info?.highest_bid) ? product.bid_info.highest_bid : product.price).toLocaleString()}
              </div>
              {product.bid_info?.has_bids && (
                <div className="text-lg text-gray-500 dark:text-gray-400 line-through">
                  Initial: €{product.price.toLocaleString()}
                </div>
              )}
            </div>

            {/* Market Price Suggestion for Catalyst Items */}
            {product.category === 'Catalysts' && (
              <div className="mb-4">
                {loadingSuggestion ? (
                  <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                    <div className="w-4 h-4 border border-gray-400 border-t-transparent rounded-full animate-spin mr-3"></div>
                    Loading market range...
                  </div>
                ) : priceSuggestion ? (
                  <div className="relative overflow-hidden rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 border border-blue-100 dark:border-blue-800/50">
                    <div className="p-4">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-800/50">
                          <Database className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                          <div className="text-sm font-medium text-blue-700 dark:text-blue-300 uppercase tracking-wide">
                            Market Range
                          </div>
                          <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                            €{(priceSuggestion * 0.9).toFixed(2)} - €{(priceSuggestion * 1.1).toFixed(2)}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="absolute top-0 right-0 w-24 h-full bg-gradient-to-l from-blue-200/20 to-transparent dark:from-blue-700/20"></div>
                  </div>
                ) : null}
              </div>
            )}
          </div>

          {/* Tender Submission Section */}
          <div className="space-y-4">
            {/* Tender Confirmation Message */}
            {tenderConfirmation?.visible && (
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-xl border-2 border-green-300 dark:border-green-700 animate-pulse">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h4 className="text-green-800 dark:text-green-300 font-bold text-lg">
                      🎉 Tender Offer Submitted Successfully!
                    </h4>
                    <p className="text-green-700 dark:text-green-400 text-sm mt-1">
                      Your competitive offer of <strong>€{tenderConfirmation.amount.toFixed(2)}</strong> has been submitted to the seller.
                    </p>
                    <p className="text-green-600 dark:text-green-500 text-xs mt-2">
                      📧 You will receive a notification when the seller responds to your offer.
                    </p>
                    <p className="text-green-600 dark:text-green-500 text-xs">
                      📱 Track all your tenders in "My Tenders" section.
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            {/* Time Limit Countdown Badge */}
            {product.time_info?.has_time_limit && (
              <div className="mb-4">
                <div className={`relative overflow-hidden rounded-xl border-2 ${
                  product.time_info.is_expired 
                    ? 'border-red-200 dark:border-red-800 bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/30'
                    : product.time_info.time_remaining_seconds <= 3600
                      ? 'border-red-200 dark:border-red-800 bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/30'
                      : product.time_info.time_remaining_seconds <= 21600
                        ? 'border-orange-200 dark:border-orange-800 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/30'
                        : product.time_info.time_remaining_seconds <= 86400
                          ? 'border-yellow-200 dark:border-yellow-800 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/30'
                          : 'border-green-200 dark:border-green-800 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/30'
                }`}>
                  <div className={`absolute top-0 right-0 w-16 h-16 rounded-bl-full ${
                    product.time_info.is_expired || product.time_info.time_remaining_seconds <= 3600
                      ? 'bg-gradient-to-bl from-red-200/20 to-transparent dark:from-red-600/10'
                      : product.time_info.time_remaining_seconds <= 21600
                        ? 'bg-gradient-to-bl from-orange-200/20 to-transparent dark:from-orange-600/10'
                        : product.time_info.time_remaining_seconds <= 86400
                          ? 'bg-gradient-to-bl from-yellow-200/20 to-transparent dark:from-yellow-600/10'
                          : 'bg-gradient-to-bl from-green-200/20 to-transparent dark:from-green-600/10'
                  }`}></div>
                  <div className="relative p-4">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg shadow-sm ${
                        product.time_info.is_expired || product.time_info.time_remaining_seconds <= 3600
                          ? 'bg-gradient-to-r from-red-500 to-red-600'
                          : product.time_info.time_remaining_seconds <= 21600
                            ? 'bg-gradient-to-r from-orange-500 to-orange-600'
                            : product.time_info.time_remaining_seconds <= 86400
                              ? 'bg-gradient-to-r from-yellow-500 to-yellow-600'
                              : 'bg-gradient-to-r from-green-500 to-green-600'
                      }`}>
                        <Clock className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <div className={`text-sm font-medium uppercase tracking-wide ${
                          product.time_info.is_expired || product.time_info.time_remaining_seconds <= 3600
                            ? 'text-red-700 dark:text-red-300'
                            : product.time_info.time_remaining_seconds <= 21600
                              ? 'text-orange-700 dark:text-orange-300'
                              : product.time_info.time_remaining_seconds <= 86400
                                ? 'text-yellow-700 dark:text-yellow-300'
                                : 'text-green-700 dark:text-green-300'
                        }`}>
                          {product.time_info.is_expired ? 'Listing Expired' : 'Time Remaining'}
                        </div>
                        <div className={`text-lg font-bold leading-tight ${
                          product.time_info.is_expired || product.time_info.time_remaining_seconds <= 3600
                            ? 'text-red-900 dark:text-red-100'
                            : product.time_info.time_remaining_seconds <= 21600
                              ? 'text-orange-900 dark:text-orange-100'
                              : product.time_info.time_remaining_seconds <= 86400
                                ? 'text-yellow-900 dark:text-yellow-100'
                                : 'text-green-900 dark:text-green-100'
                        }`}>
                          <CountdownTimer timeInfo={product.time_info} />
                        </div>
                        {product.time_info.is_expired && (
                          <div className="text-sm text-red-600 dark:text-red-400 mt-1">
                            🚫 No more bids can be placed
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Current Highest Bid Display */}
            {(product.bid_info?.has_bids || product.highest_bid) && (
              <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-xl border border-yellow-200 dark:border-yellow-800">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-yellow-800 dark:text-yellow-300 font-medium">
                      Current highest bid:
                    </span>
                    {product.bid_info?.total_bids > 0 && (
                      <div className="text-yellow-700 dark:text-yellow-400 text-xs mt-1">
                        {product.bid_info.total_bids} bid{product.bid_info.total_bids > 1 ? 's' : ''} received
                      </div>
                    )}
                  </div>
                  <span className="text-yellow-900 dark:text-yellow-200 font-bold text-lg">
                    €{parseFloat(product.bid_info?.highest_bid || product.highest_bid || 0).toFixed(2)}
                  </span>
                </div>
              </div>
            )}
            
            {/* Tender Input Form */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Your Tender Offer (€)
              </label>
              <div className="flex space-x-3">
                <input
                  type="number"
                  min={product.bid_info?.highest_bid || product.price || 0}
                  step="10"
                  value={tenderAmount}
                  onChange={(e) => setTenderAmount(e.target.value)}
                  placeholder={
                    product.time_info?.is_expired 
                      ? "Listing Expired" 
                      : `Minimum: €${(product.bid_info?.highest_bid || product.price || 0).toFixed(2)}`
                  }
                  disabled={product.time_info?.is_expired}
                  className={`flex-1 px-4 py-3 border rounded-xl text-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    product.time_info?.is_expired
                      ? 'border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 cursor-not-allowed'
                      : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
                  }`}
                />
                <button
                  onClick={(e) => {
                    if (product.time_info?.is_expired) {
                      showToast('This listing has expired. No more bids can be placed.', 'error');
                      return;
                    }
                    handleSubmitTender(e);
                  }}
                  disabled={submittingTender || !tenderAmount || product.time_info?.is_expired}
                  className={`px-8 py-3 rounded-xl font-semibold transition-all duration-200 shadow-lg hover:shadow-xl flex items-center space-x-2 ${
                    product.time_info?.is_expired
                      ? 'bg-red-400 text-red-100 cursor-not-allowed'
                      : 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 text-white'
                  }`}
                  title={product.time_info?.is_expired ? "Listing has expired" : "Submit tender offer"}
                >
                  {product.time_info?.is_expired ? (
                    <span>EXPIRED</span>
                  ) : submittingTender ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Submitting...</span>
                    </>
                  ) : (
                    <>
                      <DollarSign className="w-5 h-5" />
                      <span>Submit Offer</span>
                    </>
                  )}
                </button>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {product.time_info?.is_expired 
                  ? "🚫 This listing has expired. The highest bidder has automatically won." 
                  : `Enter your competitive offer. Minimum bid: €${(product.bid_info?.highest_bid || product.price || 0).toFixed(2)}`
                }
              </p>
            </div>
        </div>
      </div>

      {/* Product Details Tabs - Remove Features and Reviews */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        
        {/* Tab Navigation */}
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          {[
            { id: 'description', label: 'Description' },
            { id: 'seller', label: 'Seller Info' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id)}
              className={`px-6 py-4 font-medium transition-colors ${
                selectedTab === tab.id
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {selectedTab === 'description' && (
            <div className="prose dark:prose-invert max-w-none">
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                {product.description || 'No description available for this product.'}
              </p>
            </div>
          )}

          {selectedTab === 'seller' && (
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                  {(product.seller?.name || product.seller || 'S')[0]}
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center space-x-2">
                    <span>{product.seller?.name || product.seller || 'Verified Seller'}</span>
                    {product.seller?.verified && (
                      <Verified className="w-5 h-5 text-blue-600" />
                    )}
                  </h3>
                  <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                    <div className="flex items-center space-x-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span>{product.seller?.rating || 4.8} rating</span>
                    </div>
                    <span>•</span>
                    <span>{product.seller?.reviews || 156} reviews</span>
                    {product.seller?.location && (
                      <>
                        <span>•</span>
                        <div className="flex items-center space-x-1">
                          <MapPin className="w-4 h-4" />
                          <span>{product.seller.location}</span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Related Products */}
      {relatedProducts.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            More from {product.category}
          </h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {relatedProducts.map((relatedProduct) => (
              <div
                key={relatedProduct.id}
                onClick={() => navigate(`/product/${relatedProduct.id}`)}
                className="group cursor-pointer bg-gray-50 dark:bg-gray-700 rounded-xl overflow-hidden hover:shadow-lg transition-all duration-200"
              >
                <div className="aspect-square overflow-hidden">
                  <img
                    src={relatedProduct.images?.[0] || relatedProduct.image || 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=300'}
                    alt={relatedProduct.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                  />
                </div>
                <div className="p-4">
                  <h3 className="font-medium text-gray-900 dark:text-white mb-2 line-clamp-2">
                    {relatedProduct.title}
                  </h3>
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-bold text-blue-600">
                      €{relatedProduct.price.toLocaleString()}
                    </span>
                    <div className="flex items-center space-x-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {relatedProduct.rating || 4.5}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ProductDetailPage;