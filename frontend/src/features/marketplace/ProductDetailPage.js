/**
 * CATALORO - Ultra-Modern Product Detail Page
 * Comprehensive product viewing with full functionality
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMarketplace } from '../../context/MarketplaceContext';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import usePermissions from '../../hooks/usePermissions';
import SimplePrice from '../../components/ui/SimplePrice';
import {
  Heart,
  DollarSign,
  MapPin,
  Clock,
  Eye,
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  Verified,
  Database,
  Settings,
  TrendingUp
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
  const { permissions } = usePermissions();
  
  // Safety check for permissions - check role directly for reliability
  const isAdminOrManager = (permissions?.userRole === 'Admin' || permissions?.userRole === 'Manager') || 
                          (permissions?.hasPermission && (permissions.hasPermission('admin') || permissions.hasPermission('manager'))) ||
                          false;
  
  // Debug logging for permissions and catalyst data (will help verify both permission checking and data availability)
  console.log('ProductDetailPage - Permission Debug:', {
    userRole: permissions?.userRole,
    isAdminOrManager: isAdminOrManager,
    permissions: permissions
  });
  
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
  
  // Debug logging for catalyst data when product is loaded
  useEffect(() => {
    if (product) {
      console.log('ProductDetailPage - Catalyst Data Debug:', {
        productId: product.id,
        title: product.title,
        ceramic_weight: product.ceramic_weight,
        pt_ppm: product.pt_ppm,
        pd_ppm: product.pd_ppm,
        rh_ppm: product.rh_ppm,
        pt_g: product.pt_g,
        pd_g: product.pd_g,
        rh_g: product.rh_g,
        hasCatalystData: !!(product.ceramic_weight || product.pt_ppm || product.pd_ppm || product.rh_ppm || product.pt_g || product.pd_g || product.rh_g)
      });
    }
  }, [product]);
  
  // Calculate if the listing is expired
  const isExpired = product?.time_info?.is_expired || false;

  useEffect(() => {
    const loadProduct = async () => {
      try {
        console.log('🔍 Loading product details for desktop:', productId);
        
        // First try to get detailed product info from individual listing endpoint (same as mobile)
        const detailResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/listings/${productId}`);
        if (detailResponse.ok) {
          const productDetail = await detailResponse.json();
          
          // Get current bidding information (same as mobile)
          const bidResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/listings/${productId}/tenders`);
          if (bidResponse.ok) {
            const tenders = await bidResponse.json();
            
            // Add bid information to product (same logic as mobile)
            const activeTenders = tenders.filter(t => t.status === 'active');
            if (activeTenders.length > 0) {
              const highestBid = Math.max(...activeTenders.map(t => t.offer_amount));
              const highestBidTender = activeTenders.find(t => t.offer_amount === highestBid);
              productDetail.bid_info = {
                has_bids: true,
                highest_bid: highestBid,
                highest_bidder_id: highestBidTender?.buyer_id,
                total_bids: activeTenders.length
              };
            } else {
              productDetail.bid_info = {
                has_bids: false,
                highest_bid: null,
                highest_bidder_id: null,
                total_bids: 0
              };
            }
          }
          
          setProduct(productDetail);
          addToRecentlyViewed(productDetail);
          console.log('✅ Desktop product detail loaded:', productDetail.title);
          console.log('💰 Desktop bid info:', productDetail.bid_info);
          setLoading(false);
          return;
        }
        
        // Fallback to cached data if individual listing fails
        console.log('⚠️ Individual listing failed, trying cached data');
        const foundProduct = allProducts.find(p => p.id === productId);
        if (foundProduct) {
          setProduct(foundProduct);
          addToRecentlyViewed(foundProduct);
          setLoading(false);
          return;
        }

        // Final fallback to browse endpoint
        if (allProducts.length > 0) {
          console.log('⚠️ Cached data failed, trying browse endpoint');
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/marketplace/browse`);
          if (response.ok) {
            const allListings = await response.json();
            const apiProduct = allListings.find(p => p.id === productId);
            if (apiProduct) {
              setProduct(apiProduct);
              addToRecentlyViewed(apiProduct);
              setLoading(false);
              return;
            }
          }
        
          // If still not found, redirect to browse
          console.log('❌ Product not found, redirecting to browse');
          navigate('/browse');
        }
        // If allProducts is empty, keep loading (wait for MarketplaceContext to load)
        
      } catch (error) {
        console.error('❌ Error loading desktop product:', error);
        // Try fallback to cached data
        const foundProduct = allProducts.find(p => p.id === productId);
        if (foundProduct) {
          setProduct(foundProduct);
          addToRecentlyViewed(foundProduct);
        } else {
          navigate('/browse');
        }
        setLoading(false);
      }
    };

    if (productId) {
      loadProduct();
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

    // Enhanced check to prevent owner from bidding on own listing
    const isOwner = product.seller?.username === user.username || 
                    product.seller_id === user.id || 
                    product.seller?.id === user.id;
    
    if (isOwner) {
      showToast('You cannot bid on your own listing', 'error');
      return;
    }

    // Check if user is already the highest bidder
    if (product.bid_info?.highest_bidder_id === user.id && product.bid_info?.has_bids) {
      showToast('You are already the highest bidder! Wait for others to place higher bids.', 'warning');
      return;
    }

    const offerAmount = parseFloat(tenderAmount);
    const minimumBid = product.bid_info?.highest_bid || product.price || 0;

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
        if (offerAmount > (product.bid_info?.highest_bid || product.highest_bid || 0)) {
          setProduct(prev => ({ 
            ...prev, 
            highest_bid: offerAmount,
            bid_info: {
              ...prev.bid_info,
              has_bids: true,
              highest_bid: offerAmount,
              total_bids: (prev.bid_info?.total_bids || 0) + 1
            }
          }));
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
        <span className="text-gray-900 dark:text-white">{product.title}</span>
      </div>

      {/* Two-Column Layout: Pictures Left, ALL Info Right */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Left Column: Pictures Only */}
          <div className="space-y-4">
            {/* Main Image */}
            <div className="relative group">
              <img
                src={images[selectedImageIndex]}
                alt={product.title}
                className="w-full h-96 object-cover rounded-xl"
              />
              {images.length > 1 && (
                <>
                  <button
                    onClick={() => setSelectedImageIndex(prev => 
                      prev === 0 ? images.length - 1 : prev - 1
                    )}
                    className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => setSelectedImageIndex(prev => 
                      prev === images.length - 1 ? 0 : prev + 1
                    )}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </>
              )}
            </div>
            
            {/* Thumbnail Images */}
            {images.length > 1 && (
              <div className="flex space-x-2 overflow-x-auto">
                {images.map((image, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedImageIndex(index)}
                    className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-colors ${
                      selectedImageIndex === index
                        ? 'border-blue-500'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                    }`}
                  >
                    <img
                      src={image}
                      alt={`${product.title} - ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Right Column: ALL Product Information */}
          <div className="space-y-6">
            {/* Title */}
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                {product.title}
              </h1>

              {/* Views Counter */}
              <div className="flex items-center space-x-1 text-gray-600 dark:text-gray-400 mb-4">
                <Eye className="w-4 h-4" />
                <span>{product.views || 0} views</span>
              </div>
            </div>

            {/* Favorites Button */}
            <div className="flex items-center space-x-4">
              <button
                onClick={handleAddToFavorites}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors ${
                  isFavorite
                    ? 'bg-red-50 border-red-200 text-red-600 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400'
                    : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                <Heart className={`w-5 h-5 ${isFavorite ? 'fill-current' : ''}`} />
                <span>{isFavorite ? 'Remove from Favorites' : 'Add to Favorites'}</span>
              </button>
            </div>

            {/* Enhanced Price Display */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/40 rounded-xl p-6 border-2 border-green-200 dark:border-green-800">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold text-green-700 dark:text-green-300 uppercase tracking-wide mb-1">
                    {product.bid_info?.has_bids ? 'Current Highest Bid' : 'Starting Price'}
                  </div>
                  <SimplePrice 
                    basePrice={(product.bid_info?.has_bids && product.bid_info?.highest_bid) ? product.bid_info.highest_bid : product.price}
                    baseCurrency="EUR"
                    showAlternativePrices={true}
                    compact={false}
                  />
                  {product.bid_info?.has_bids && (
                    <div className="text-sm text-green-600 dark:text-green-400 mt-2">
                      Starting price: €{product.price.toLocaleString()}
                    </div>
                  )}
                </div>
                <div className="text-right">
                  <div className="bg-green-600 text-white px-4 py-2 rounded-full text-sm font-medium">
                    {product.bid_info?.has_bids ? `${product.bid_info.total_bids || 0} bids` : 'No bids yet'}
                  </div>
                  {product.bid_info?.has_bids && (
                    <div className="text-xs text-green-700 dark:text-green-300 mt-1">
                      Total bids received
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Market Range - similar to tile listings format */}
            {product.market_range && (
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl p-6 border border-purple-200 dark:border-purple-800">
                <div className="flex items-center space-x-2 mb-2">
                  <TrendingUp className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                  <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-100">Market Range</h3>
                </div>
                <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">
                  {product.market_range}
                </div>
              </div>
            )}

            {/* Time Left - Always show for consistency */}
            <div className={`rounded-xl border-2 p-6 ${
              product.time_info?.has_time_limit
                ? product.time_info.is_expired 
                  ? 'border-red-200 dark:border-red-800 bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/30'
                  : product.time_info.time_remaining_seconds <= 3600
                    ? 'border-red-200 dark:border-red-800 bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/30'
                    : product.time_info.time_remaining_seconds <= 21600
                      ? 'border-orange-200 dark:border-orange-800 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/30'
                      : product.time_info.time_remaining_seconds <= 86400
                        ? 'border-yellow-200 dark:border-yellow-800 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/30'
                        : 'border-green-200 dark:border-green-800 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/30'
                : 'border-green-200 dark:border-green-800 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/30'
            }`}>
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg shadow-sm ${
                  product.time_info?.has_time_limit
                    ? product.time_info.is_expired || product.time_info.time_remaining_seconds <= 3600
                      ? 'bg-gradient-to-r from-red-500 to-red-600'
                      : product.time_info.time_remaining_seconds <= 21600
                        ? 'bg-gradient-to-r from-orange-500 to-orange-600'
                        : product.time_info.time_remaining_seconds <= 86400
                          ? 'bg-gradient-to-r from-yellow-500 to-yellow-600'
                          : 'bg-gradient-to-r from-green-500 to-green-600'
                    : 'bg-gradient-to-r from-green-500 to-green-600'
                }`}>
                  <Clock className="w-5 h-5 text-white" />
                </div>
                <div>
                  <div className={`text-sm font-medium uppercase tracking-wide ${
                    product.time_info?.has_time_limit
                      ? product.time_info.is_expired || product.time_info.time_remaining_seconds <= 3600
                        ? 'text-red-700 dark:text-red-300'
                        : product.time_info.time_remaining_seconds <= 21600
                          ? 'text-orange-700 dark:text-orange-300'
                          : product.time_info.time_remaining_seconds <= 86400
                            ? 'text-yellow-700 dark:text-yellow-300'
                            : 'text-green-700 dark:text-green-300'
                      : 'text-green-700 dark:text-green-300'
                  }`}>
                    {product.time_info?.has_time_limit 
                      ? (product.time_info.is_expired ? 'Expired' : 'Time Left')
                      : 'Without Time Limit'
                    }
                  </div>
                  <div className={`text-xl font-bold leading-tight ${
                    product.time_info?.has_time_limit
                      ? product.time_info.is_expired || product.time_info.time_remaining_seconds <= 3600
                        ? 'text-red-900 dark:text-red-100'
                        : product.time_info.time_remaining_seconds <= 21600
                          ? 'text-orange-900 dark:text-orange-100'
                          : product.time_info.time_remaining_seconds <= 86400
                            ? 'text-yellow-900 dark:text-yellow-100'
                            : 'text-green-900 dark:text-green-100'
                      : 'text-green-900 dark:text-green-100'
                  }`}>
                    {product.time_info?.has_time_limit 
                      ? <CountdownTimer timeInfo={product.time_info} />
                      : 'Always Available'
                    }
                  </div>
                </div>
              </div>
            </div>

            {/* Catalyst Content - Only visible to Admin/Manager */}
            {isAdminOrManager && (
              <CatalystContentBox 
                weight={product.ceramic_weight}
                ptPpm={product.pt_ppm}
                pdPpm={product.pd_ppm}
                rhPpm={product.rh_ppm}
                ptG={product.pt_g}
                pdG={product.pd_g}
                rhG={product.rh_g}
              />
            )}

            {/* Seller Information - Between Time Limit and Location */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-900/30 dark:to-indigo-900/40 rounded-xl p-6 border-2 border-blue-200 dark:border-blue-800">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg">
                  {(product.seller?.username || product.seller?.name || 'U').charAt(0).toUpperCase()}
                </div>
                <div className="flex-1">
                  <div className="text-sm font-medium text-blue-700 dark:text-blue-300 uppercase tracking-wide mb-1">
                    Sold by
                  </div>
                  <div className="text-xl font-bold text-blue-900 dark:text-blue-100">
                    {product.seller?.username || product.seller?.name || 'Unknown Seller'}
                  </div>
                  {product.seller?.is_business && product.seller?.business_name && (
                    <div className="text-sm text-blue-600 dark:text-blue-400 mt-1">
                      {product.seller.business_name}
                    </div>
                  )}
                </div>
                <div className="text-right">
                  <button
                    onClick={() => navigate(`/profile/${product.seller_id}`)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    View Profile
                  </button>
                  {product.seller?.verified && (
                    <div className="flex items-center justify-end space-x-1 mt-2">
                      <Verified className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                      <span className="text-xs text-blue-600 dark:text-blue-400">Verified</span>
                    </div>
                  )}
                </div>
              </div>
            </div>



            {/* Category */}
            <div>
              <span className="inline-block bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-sm px-3 py-1 rounded-full font-medium">
                {product.category}
              </span>
            </div>

            {/* Location */}
            <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
              <MapPin className="w-4 h-4" />
              <span>{product.location || 'Location not specified'}</span>
            </div>

            {/* Created Date */}
            <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400 text-sm mb-6">
              <Clock className="w-4 h-4" />
              <span>Listed on {new Date(product.created_at).toLocaleDateString()}</span>
            </div>

            {/* Bid Information Section */}
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 space-y-4">
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white">Bidding Information</h4>
              
              {/* User is Highest Bidder Indicator */}
              {product.bid_info?.highest_bidder_id === user?.id && product.bid_info?.has_bids && (
                <div className="mb-4 p-4 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <div className="text-green-800 dark:text-green-300 font-medium text-sm">
                      🎉 You're the highest bidder!
                    </div>
                  </div>
                  <div className="text-green-700 dark:text-green-400 text-xs mt-1">
                    Wait for others to place higher bids before you can bid again.
                  </div>
                </div>
              )}

              {/* Current Highest Bid */}
              {product.bid_info?.has_bids ? (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 dark:text-gray-300">Current Highest Bid:</span>
                  <span className="font-bold text-green-600 dark:text-green-400">
                    €{product.bid_info.highest_bid.toFixed(2)}
                  </span>
                </div>
              ) : (
                <div className="text-center text-gray-500 dark:text-gray-400 italic">
                  No bids yet - be the first to bid!
                </div>
              )}

              {/* Your Current Bid */}
              {product.bid_info?.user_bid && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 dark:text-gray-300">Your Current Bid:</span>
                  <span className="font-bold text-blue-600 dark:text-blue-400">
                    €{product.bid_info.user_bid.toFixed(2)}
                  </span>
                </div>
              )}

              {/* Your Tender Offer Input */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Your Tender Offer:
                </label>
                
                {/* Check if user is the listing owner */}
                {(product.seller?.username === user?.username || product.seller_id === user?.id || product.seller?.id === user?.id) ? (
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 text-center">
                    <div className="text-yellow-700 dark:text-yellow-300 font-medium">
                      You cannot bid on your own listing
                    </div>
                    <div className="text-sm text-yellow-600 dark:text-yellow-400 mt-1">
                      This is your product listing
                    </div>
                  </div>
                ) : (
                  <div className="flex space-x-2">
                    <input
                      type="number"
                      step="0.01"
                      min={product.bid_info?.highest_bid || product.price}
                      value={tenderAmount}
                      onChange={(e) => setTenderAmount(e.target.value)}
                      disabled={isExpired || (product.bid_info?.highest_bidder_id === user?.id && product.bid_info?.has_bids)}
                      className={`flex-1 px-3 py-2 border rounded-lg text-sm ${
                        isExpired || (product.bid_info?.highest_bidder_id === user?.id && product.bid_info?.has_bids)
                          ? 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                          : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-blue-500'
                      }`}
                      placeholder={
                        product.time_info?.is_expired 
                          ? "Expired" 
                          : product.bid_info?.highest_bidder_id === user?.id && product.bid_info?.has_bids
                            ? "You have the highest bid"
                            : `Minimum: €${(product.bid_info?.highest_bid || product.price || 0).toFixed(2)}`
                      }
                    />
                    <button
                      onClick={handleSubmitTender}
                      disabled={submittingTender || isExpired || (product.bid_info?.highest_bidder_id === user?.id && product.bid_info?.has_bids)}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors text-sm ${
                        submittingTender || isExpired || (product.bid_info?.highest_bidder_id === user?.id && product.bid_info?.has_bids)
                          ? 'bg-gray-300 dark:bg-gray-600 text-gray-500 cursor-not-allowed'
                          : 'bg-blue-600 hover:bg-blue-700 text-white'
                      }`}
                    >
                      {submittingTender ? 'Submitting...' : 'Submit Bid'}
                    </button>
                  </div>
                )}
              </div>

              {/* Time Remaining */}
              {product.time_info?.has_time_limit && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600 dark:text-gray-300">Time Remaining:</span>
                  <span className={`font-bold ${
                    product.time_info.is_expired 
                      ? 'text-red-600 dark:text-red-400' 
                      : product.time_info.time_remaining_seconds <= 3600
                        ? 'text-red-600 dark:text-red-400'
                        : product.time_info.time_remaining_seconds <= 86400
                          ? 'text-orange-600 dark:text-orange-400'
                          : 'text-green-600 dark:text-green-400'
                  }`}>
                    {product.time_info.is_expired 
                      ? 'EXPIRED' 
                      : product.time_info.time_remaining_display || 'Active'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>



      {/* Product Details Tabs - Only Description and Seller Info */}
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
                    {product.seller?.location && (
                      <div className="flex items-center space-x-1">
                        <MapPin className="w-4 h-4" />
                        <span>{product.seller.location}</span>
                      </div>
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
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Related Products</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {relatedProducts.map((relatedProduct) => (
              <div key={relatedProduct.id} className="group cursor-pointer" onClick={() => navigate(`/product/${relatedProduct.id}`)}>
                <div className="aspect-square bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden mb-3">
                  <img
                    src={relatedProduct.images?.[0] || relatedProduct.image || 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=300'}
                    alt={relatedProduct.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                  />
                </div>
                <h3 className="font-medium text-gray-900 dark:text-white group-hover:text-blue-600 transition-colors line-clamp-2">
                  {relatedProduct.title}
                </h3>
                <p className="text-lg font-bold text-gray-900 dark:text-white mt-1">
                  €{relatedProduct.price.toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Catalyst Content Box Component - Blue themed box showing weight and content values (Pt g, Pd g, Rh g)
function CatalystContentBox({ weight, ptPpm, pdPpm, rhPpm, ptG, pdG, rhG }) {
  const [priceSettings, setPriceSettings] = useState(null);

  useEffect(() => {
    const fetchPriceSettings = async () => {
      try {
        const token = localStorage.getItem('cataloro_token');
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/catalyst/price-settings`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        if (response.ok) {
          const settings = await response.json();
          setPriceSettings(settings);
        }
      } catch (error) {
        console.error('Failed to fetch price settings:', error);
      }
    };

    fetchPriceSettings();
  }, []);

  // Use stored g values if available, otherwise calculate from PPM
  let calculatedPtG, calculatedPdG, calculatedRhG;
  
  if (ptG !== undefined && pdG !== undefined && rhG !== undefined) {
    // Use stored values from unified calculations (new approach)
    calculatedPtG = ptG;
    calculatedPdG = pdG;
    calculatedRhG = rhG;
  } else if (priceSettings && weight && (ptPpm || pdPpm || rhPpm)) {
    // Calculate from PPM values (legacy approach)
    calculatedPtG = weight && ptPpm ? (weight * ptPpm / 1000) * (priceSettings.renumeration_pt || 0.98) : 0;
    calculatedPdG = weight && pdPpm ? (weight * pdPpm / 1000) * (priceSettings.renumeration_pd || 0.98) : 0;
    calculatedRhG = weight && rhPpm ? (weight * rhPpm / 1000) * (priceSettings.renumeration_rh || 0.9) : 0;
  } else {
    // No data available
    calculatedPtG = 0;
    calculatedPdG = 0;
    calculatedRhG = 0;
  }

  // Only show if there's meaningful data (weight or any content values)
  if (!weight && !calculatedPtG && !calculatedPdG && !calculatedRhG) {
    return null;
  }

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 border-2 border-blue-200 dark:border-blue-800">
      <div className="flex items-center space-x-2 mb-4">
        <Database className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100">Catalyst Content</h3>
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200">
          Admin Only
        </span>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-blue-100 dark:border-blue-800 shadow-sm">
          <div className="text-xs text-blue-600 dark:text-blue-400 uppercase font-medium mb-1">Weight</div>
          <div className="text-xl font-bold text-gray-900 dark:text-white">{weight || 0}g</div>
        </div>
        
        <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-blue-100 dark:border-blue-800 shadow-sm">
          <div className="text-xs text-blue-600 dark:text-blue-400 uppercase font-medium mb-1">Pt g</div>
          <div className="text-xl font-bold text-blue-600 dark:text-blue-400">{(calculatedPtG || 0).toFixed(4)}</div>
        </div>
        
        <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-blue-100 dark:border-blue-800 shadow-sm">
          <div className="text-xs text-green-600 dark:text-green-400 uppercase font-medium mb-1">Pd g</div>
          <div className="text-xl font-bold text-green-600 dark:text-green-400">{(calculatedPdG || 0).toFixed(4)}</div>
        </div>
        
        <div className="text-center p-4 bg-white dark:bg-gray-800 rounded-lg border border-blue-100 dark:border-blue-800 shadow-sm">
          <div className="text-xs text-purple-600 dark:text-purple-400 uppercase font-medium mb-1">Rh g</div>
          <div className="text-xl font-bold text-purple-600 dark:text-purple-400">{(calculatedRhG || 0).toFixed(4)}</div>
        </div>
      </div>
      
      <div className="mt-4 text-xs text-blue-600 dark:text-blue-400">
        <Database className="w-4 h-4 inline mr-1" />
        Content values visible only to Admin and Manager users for catalyst analysis.
      </div>
    </div>
  );
}

export default ProductDetailPage;