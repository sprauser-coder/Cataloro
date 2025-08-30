/**
 * CATALORO - Ultra-Modern Product Detail Page
 * Comprehensive product viewing with full functionality
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMarketplace } from '../../context/MarketplaceContext';
import {
  Heart,
  Share2,
  ShoppingCart,
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

function ProductDetailPage() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const {
    allProducts,
    addToCart,
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

  const handleAddToCart = () => {
    const cartItem = { ...product, quantity: 1 };
    addToCart(cartItem);
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

            {/* Rating and Reviews */}
            <div className="flex items-center space-x-4 mb-4">
              <div className="flex items-center space-x-2">
                <div className="flex items-center">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`w-5 h-5 ${
                        i < Math.floor(product.rating || 0)
                          ? 'text-yellow-400 fill-current'
                          : 'text-gray-300 dark:text-gray-600'
                      }`}
                    />
                  ))}
                </div>
                <span className="font-medium text-gray-900 dark:text-white">
                  {product.rating || 4.5}
                </span>
                <span className="text-gray-600 dark:text-gray-400">
                  ({product.reviewCount || product.reviews || 0} reviews)
                </span>
              </div>
              
              <div className="flex items-center space-x-1 text-gray-600 dark:text-gray-400">
                <Eye className="w-4 h-4" />
                <span>{product.views || 0} views</span>
              </div>
            </div>
          </div>

          {/* Price Section */}
          <div className="bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
            <div className="flex items-center space-x-4 mb-4">
              <div className="text-4xl font-bold text-gray-900 dark:text-white">
                €{product.price.toLocaleString()}
              </div>
            </div>

            {/* Market Price Suggestion for Catalyst Items */}
            {product.category === 'Catalysts' && (
              <div className="mb-4">
                {loadingSuggestion ? (
                  <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                    <div className="w-4 h-4 border border-gray-400 border-t-transparent rounded-full animate-spin mr-3"></div>
                    Loading market price analysis...
                  </div>
                ) : priceSuggestion && Math.abs(priceSuggestion - product.price) > 0.01 ? (
                  <div className="relative overflow-hidden rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 border border-blue-100 dark:border-blue-800/50">
                    <div className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-800/50">
                            <Database className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                          </div>
                          <div>
                            <div className="text-sm font-medium text-blue-700 dark:text-blue-300 uppercase tracking-wide">
                              Database Market Price
                            </div>
                            <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">
                              €{priceSuggestion.toFixed(2)}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          {product.price < priceSuggestion ? (
                            <div className="inline-flex items-center px-3 py-2 rounded-full bg-green-100 dark:bg-green-900/40 border border-green-200 dark:border-green-800">
                              <TrendingUp className="w-4 h-4 text-green-600 dark:text-green-400 mr-2" />
                              <span className="text-sm font-semibold text-green-700 dark:text-green-300">
                                Excellent Deal
                              </span>
                            </div>
                          ) : (
                            <div className="inline-flex items-center px-3 py-2 rounded-full bg-orange-100 dark:bg-orange-900/40 border border-orange-200 dark:border-orange-800">
                              <Info className="w-4 h-4 text-orange-600 dark:text-orange-400 mr-2" />
                              <span className="text-sm font-semibold text-orange-700 dark:text-orange-300">
                                Above Market
                              </span>
                            </div>
                          )}
                          <div className="text-sm text-blue-600 dark:text-blue-400 mt-2">
                            {product.price < priceSuggestion 
                              ? `You save €${(priceSuggestion - product.price).toFixed(2)}`
                              : `€${(product.price - priceSuggestion).toFixed(2)} above market`
                            }
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="absolute top-0 right-0 w-24 h-full bg-gradient-to-l from-blue-200/20 to-transparent dark:from-blue-700/20"></div>
                  </div>
                ) : priceSuggestion && Math.abs(priceSuggestion - product.price) <= 0.01 ? (
                  <div className="flex items-center space-x-3 p-3 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/30 dark:to-emerald-900/30 rounded-lg border border-green-200 dark:border-green-800/50">
                    <div className="p-1.5 rounded bg-green-100 dark:bg-green-800/50">
                      <Database className="w-4 h-4 text-green-600 dark:text-green-400" />
                    </div>
                    <span className="text-sm font-semibold text-green-700 dark:text-green-300">
                      Perfect Market Price Match
                    </span>
                  </div>
                ) : null}
              </div>
            )}

            {/* Condition and Availability */}
            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-gray-600 dark:text-gray-400">Condition:</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {product.condition || 'New'}
                </span>
              </div>
              
              <div className="flex items-center space-x-2">
                <Check className="w-4 h-4 text-green-500" />
                <span className="font-medium text-green-700 dark:text-green-400">
                  {product.inStock !== false ? 'In Stock' : 'Out of Stock'}
                </span>
              </div>
            </div>
          </div>

          {/* Add to Cart */}
          <div className="space-y-4">
            <button
              onClick={handleAddToCart}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-4 rounded-xl font-semibold text-lg transition-all duration-200 shadow-lg hover:shadow-xl flex items-center justify-center space-x-2"
            >
              <ShoppingCart className="w-6 h-6" />
              <span>Add to Cart - €{product.price.toLocaleString()}</span>
            </button>
          </div>

          {/* Shipping and Trust Indicators */}
          <div className="space-y-3">
            <div className="flex items-center space-x-3 text-gray-600 dark:text-gray-400">
              <Truck className="w-5 h-5 text-blue-600" />
              <span>{product.shipping || 'Standard shipping available'}</span>
            </div>
            <div className="flex items-center space-x-3 text-gray-600 dark:text-gray-400">
              <Clock className="w-5 h-5 text-green-600" />
              <span>{product.estimatedDelivery || '3-5 business days delivery'}</span>
            </div>
            <div className="flex items-center space-x-3 text-gray-600 dark:text-gray-400">
              <Shield className="w-5 h-5 text-purple-600" />
              <span>Buyer protection guarantee</span>
            </div>
          </div>
        </div>
      </div>

      {/* Product Details Tabs */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        
        {/* Tab Navigation */}
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          {[
            { id: 'description', label: 'Description' },
            { id: 'features', label: 'Features' },
            { id: 'seller', label: 'Seller Info' },
            { id: 'reviews', label: 'Reviews' }
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

          {selectedTab === 'features' && (
            <div className="space-y-3">
              {product.features && product.features.length > 0 ? (
                product.features.map((feature, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                    <span className="text-gray-700 dark:text-gray-300">{feature}</span>
                  </div>
                ))
              ) : (
                <p className="text-gray-600 dark:text-gray-400">No specific features listed for this product.</p>
              )}
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

          {selectedTab === 'reviews' && (
            <div className="space-y-6">
              <div className="text-center py-8">
                <MessageCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No reviews yet
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Be the first to review this product after purchasing.
                </p>
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