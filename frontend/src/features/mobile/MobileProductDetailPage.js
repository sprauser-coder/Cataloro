/**
 * CATALORO - Mobile Product Detail Page
 * Mobile-optimized product viewing with bidding functionality
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import {
  ArrowLeft,
  Heart,
  Share,
  MapPin,
  Clock,
  Star,
  Eye,
  DollarSign,
  AlertCircle,
  CheckCircle,
  User
} from 'lucide-react';

function MobileProductDetailPage() {
  const params = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useNotifications();

  // Handle both route patterns: /listing/:id and /product/:productId
  const productId = params.id || params.productId;

  console.log('🔍 MobileProductDetailPage params:', params);
  console.log('🆔 Product ID resolved:', productId);

  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [bidAmount, setBidAmount] = useState('');
  const [submittingBid, setSubmittingBid] = useState(false);
  const [isFavorited, setIsFavorited] = useState(false);

  // Load product data
  useEffect(() => {
    const loadProduct = async () => {
      try {
        console.log('🔍 Loading product:', productId);
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/marketplace/browse`);
        if (response.ok) {
          const allProducts = await response.json();
          const foundProduct = allProducts.find(p => p.id === productId);
          
          if (foundProduct) {
            setProduct(foundProduct);
            console.log('✅ Product loaded:', foundProduct.title);
          } else {
            console.log('❌ Product not found');
            showToast('Product not found', 'error');
            navigate('/browse');
          }
        } else {
          throw new Error('Failed to fetch products');
        }
      } catch (error) {
        console.error('❌ Error loading product:', error);
        showToast('Error loading product', 'error');
        navigate('/browse');
      } finally {
        setLoading(false);
      }
    };

    if (productId) {
      loadProduct();
    }
  }, [productId, navigate, showToast]);

  const handleBidSubmit = async () => {
    if (!bidAmount || parseFloat(bidAmount) <= 0) {
      showToast('Please enter a valid bid amount', 'error');
      return;
    }

    if (!user) {
      showToast('Please login to place a bid', 'error');
      return;
    }

    setSubmittingBid(true);
    try {
      console.log('💰 Submitting bid:', {
        listing_id: productId,
        buyer_id: user.id,
        offer_amount: parseFloat(bidAmount)
      });

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tenders/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          listing_id: productId,
          buyer_id: user.id,
          offer_amount: parseFloat(bidAmount)
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit bid');
      }

      const result = await response.json();
      console.log('✅ Bid submitted successfully:', result);
      
      showToast('Bid submitted successfully!', 'success');
      setBidAmount('');
      
      // Refresh product data to show updated bid info
      const refreshResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/marketplace/browse`);
      if (refreshResponse.ok) {
        const allProducts = await refreshResponse.json();
        const updatedProduct = allProducts.find(p => p.id === productId);
        if (updatedProduct) {
          setProduct(updatedProduct);
          console.log('🔄 Product data refreshed with updated bids');
        }
      }
      
    } catch (error) {
      console.error('❌ Error submitting bid:', error);
      showToast(error.message || 'Error submitting bid', 'error');
    } finally {
      setSubmittingBid(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading product details...</p>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center p-6">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Product not found</p>
          <button
            onClick={() => navigate('/browse')}
            className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg"
          >
            Back to Browse
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Mobile Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
        <div className="flex items-center justify-between p-4">
          <button
            onClick={() => navigate('/browse')}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full"
          >
            <ArrowLeft className="w-6 h-6 text-gray-700 dark:text-gray-300" />
          </button>
          <h1 className="text-lg font-semibold text-gray-900 dark:text-white truncate mx-4">
            {product.title}
          </h1>
          <div className="flex space-x-2">
            <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full">
              <Share className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            </button>
            <button 
              onClick={() => setIsFavorited(!isFavorited)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full"
            >
              <Heart className={`w-5 h-5 ${isFavorited ? 'text-red-500 fill-current' : 'text-gray-700 dark:text-gray-300'}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Product Images */}
      <div className="relative">
        <div className="aspect-square bg-gray-100 dark:bg-gray-700">
          {product.images && product.images.length > 0 ? (
            <img
              src={product.images[selectedImageIndex]}
              alt={product.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <div className="text-center text-gray-400">
                <div className="w-20 h-20 bg-gray-200 dark:bg-gray-600 rounded-lg mx-auto mb-4 flex items-center justify-center">
                  <span className="text-2xl font-bold">C</span>
                </div>
                <p>No Image</p>
              </div>
            </div>
          )}
        </div>

        {/* Image indicators */}
        {product.images && product.images.length > 1 && (
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
            {product.images.map((_, index) => (
              <button
                key={index}
                onClick={() => setSelectedImageIndex(index)}
                className={`w-2 h-2 rounded-full ${
                  index === selectedImageIndex ? 'bg-white' : 'bg-white/50'
                }`}
              />
            ))}
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="bg-white dark:bg-gray-800 p-6">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {product.title}
            </h2>
            <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
              <div className="flex items-center">
                <MapPin className="w-4 h-4 mr-1" />
                <span>{product.seller?.location || 'Unknown'}</span>
              </div>
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                <span>{formatTimeAgo(product.created_at)}</span>
              </div>
              <div className="flex items-center">
                <Eye className="w-4 h-4 mr-1" />
                <span>{product.viewCount || 0}</span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
              {formatPrice(product.bid_info?.has_bids && product.bid_info?.highest_bid 
                ? product.bid_info.highest_bid 
                : product.price)}
            </div>
            {product.bid_info?.has_bids && product.bid_info?.total_bids > 0 && (
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Current bid ({product.bid_info.total_bids} bid{product.bid_info.total_bids !== 1 ? 's' : ''})
              </div>
            )}
            {product.rating && (
              <div className="flex items-center mt-1">
                <Star className="w-4 h-4 text-yellow-500 fill-current" />
                <span className="text-sm text-gray-600 dark:text-gray-400 ml-1">
                  {product.rating} ({product.reviewCount || 0})
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg text-center">
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {product.bid_info?.total_bids || 0}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Bids</div>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg text-center">
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {product.bid_info?.highest_bid ? formatPrice(product.bid_info.highest_bid) : 'No bids'}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Highest Bid</div>
          </div>
        </div>

        {/* Description */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Description</h3>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
            {product.description || 'No description available.'}
          </p>
        </div>

        {/* Seller Info */}
        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
              <User className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h4 className="font-semibold text-gray-900 dark:text-white">
                {product.seller?.name || 'Unknown Seller'}
              </h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {product.seller?.is_business ? 'Business Seller' : 'Private Seller'}
              </p>
            </div>
            {product.seller?.verified && (
              <CheckCircle className="w-5 h-5 text-green-500" />
            )}
          </div>
        </div>
      </div>

      {/* Bidding Section */}
      <div className="bg-white dark:bg-gray-800 p-6 border-t border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Place Your Bid</h3>
        
        <div className="flex space-x-3">
          <div className="flex-1">
            <input
              type="number"
              value={bidAmount}
              onChange={(e) => setBidAmount(e.target.value)}
              placeholder={
                product.bid_info?.highest_bid 
                  ? `Min bid: €${(product.bid_info.highest_bid + 1).toFixed(0)}`
                  : `Min bid: €${product.price || 0}`
              }
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg 
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              min={product.bid_info?.highest_bid ? product.bid_info.highest_bid + 1 : product.price || 0}
              step="1"
            />
          </div>
          <button
            onClick={handleBidSubmit}
            disabled={submittingBid || !bidAmount}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 
                     text-white font-semibold rounded-lg transition-colors
                     flex items-center space-x-2"
          >
            {submittingBid ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Bidding...</span>
              </>
            ) : (
              <>
                <DollarSign className="w-4 h-4" />
                <span>Bid</span>
              </>
            )}
          </button>
        </div>

        <p className="text-sm text-gray-600 dark:text-gray-400 mt-3">
          Current highest bid: {product.bid_info?.highest_bid ? formatPrice(product.bid_info.highest_bid) : 'No bids yet'}
        </p>
      </div>

      {/* Bottom padding for mobile nav */}
      <div className="h-20"></div>
    </div>
  );
}

export default MobileProductDetailPage;