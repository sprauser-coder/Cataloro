/**
 * CATALORO - Ultra-Modern Browse Page
 * Advanced marketplace browsing with filters, search, and modern UI
 */

import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Grid3X3, 
  List, 
  Heart, 
  Eye, 
  MapPin,
  Clock,
  ShoppingCart,
  MessageCircle,
  SlidersHorizontal,
  X,
  Send,
  User,
  Database,
  RefreshCw
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
// Removed unused import
import { useMarketplace } from '../../context/MarketplaceContext';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import { liveService } from '../../services/liveService';

function ModernBrowsePage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const navigate = useNavigate();
  // Use marketplace context
  const {
    filteredProducts,
    addToCart,
    addToFavorites,
    removeFromFavorites,
    favorites,
    setSearchQuery: setGlobalSearchQuery,
    setFilters: setGlobalFilters,
    setSortBy: setGlobalSortBy,
    setViewMode: setGlobalViewMode,
    searchQuery: globalSearchQuery,
    activeFilters: globalFilters,
    sortBy: globalSortBy,
    viewMode: globalViewMode,
    isLoading,
    refreshListings: contextRefreshListings
  } = useMarketplace();

  // Message modal state
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [messageContent, setMessageContent] = useState('');
  const [sending, setSending] = useState(false);
  const [submittingTenders, setSubmittingTenders] = useState({}); // Track tender submission state per item
  const [tenderConfirmations, setTenderConfirmations] = useState({}); // Track successful tender submissions

  // Check if item is in favorites
  const isInFavorites = (itemId) => {
    return favorites.some(fav => fav.id === itemId);
  };

  // Handle favorite toggle
  const handleFavoriteToggle = async (item, e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!user) {
      showToast('Please login to add favorites', 'info');
      return;
    }
    
    if (isInFavorites(item.id)) {
      await removeFromFavorites(item.id, user.id);
    } else {
      await addToFavorites(item, user.id);
    }
  };

  // Handle message seller
  const handleMessageSeller = (item, e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!user) {
      showToast('Please login to message sellers', 'info');
      return;
    }
    
    if (item.seller_id === user.id) {
      showToast("You can't message yourself about your own listing", 'info');
      return;
    }
    
    setSelectedProduct(item);
    setMessageContent(`Hi! I'm interested in your listing "${item.title}". Is it still available?`);
    setShowMessageModal(true);
  };

  // Send message to seller
  const handleSendMessage = async () => {
    if (!messageContent.trim() || !selectedProduct) {
      showToast('Please enter a message', 'error');
      return;
    }

    try {
      setSending(true);
      await liveService.sendMessage(user.id, {
        recipient_id: selectedProduct.seller_id,
        subject: `Inquiry about: ${selectedProduct.title}`,
        content: messageContent
      });
      
      showToast('Message sent successfully!', 'success');
      setShowMessageModal(false);
      setMessageContent('');
      setSelectedProduct(null);
    } catch (error) {
      console.error('Failed to send message:', error);
      showToast('Failed to send message. Please try again.', 'error');
    } finally {
      setSending(false);
    }
  };

  // Refresh listings function
  const refreshListings = async () => {
    try {
      showToast('Refreshing listings...', 'info');
      // Use the marketplace context refresh function
      await contextRefreshListings();
      showToast('Listings refreshed!', 'success');
    } catch (error) {
      console.error('Failed to refresh listings:', error);
      showToast('Failed to refresh listings', 'error');
    }
  };

  const [showFilters, setShowFilters] = useState(false);
  const [heroContent, setHeroContent] = useState({
    title: 'Discover Amazing Products',
    description: 'From electronics to fashion, find everything you need in one place',
    height: 400,
    image_url: '',
    search_placeholder: 'Search for anything you need...'
  });
  
  // Use global search and filter states from context
  const searchQuery = globalSearchQuery;
  const filters = globalFilters;
  const sortBy = globalSortBy;
  const viewMode = globalViewMode;
  // Removed unused variable
  const filteredListings = filteredProducts;

  // Removed categories array since we're using type filter instead

  // Load hero content from localStorage on mount and listen for updates
  useEffect(() => {
    const loadHeroContent = () => {
      const savedHeroContent = localStorage.getItem('cataloro_hero_content');
      if (savedHeroContent) {
        try {
          setHeroContent(JSON.parse(savedHeroContent));
        } catch (error) {
          console.error('Error loading hero content:', error);
        }
      }
    };

    // Load initially
    loadHeroContent();

    // Listen for updates from admin panel
    const handleHeroUpdate = (event) => {
      setHeroContent(event.detail);
    };

    window.addEventListener('heroContentUpdated', handleHeroUpdate);

    // Cleanup listener
    return () => {
      window.removeEventListener('heroContentUpdated', handleHeroUpdate);
    };
  }, []);

  const handleAddToCart = (item) => {
    addToCart(item);
  };

  const handleSubmitTender = async (item, offerAmount) => {
    if (!user) {
      showToast('Please login to submit tender offers', 'error');
      return;
    }

    if (item.seller?.username === user.username || item.seller_id === user.id) {
      showToast('You cannot bid on your own listing', 'error');
      return;
    }

    // Set loading state for this specific item
    setSubmittingTenders(prev => ({ ...prev, [item.id]: true }));

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tenders/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          listing_id: item.id,
          buyer_id: user.id,
          offer_amount: parseFloat(offerAmount)
        })
      });

      const data = await response.json();

      if (response.ok) {
        showToast(`Tender offer of €${offerAmount} submitted successfully!`, 'success');
        
        // Show visual confirmation for this specific item
        setTenderConfirmations(prev => ({ 
          ...prev, 
          [item.id]: {
            amount: parseFloat(offerAmount),
            timestamp: new Date(),
            visible: true
          }
        }));
        
        // Hide confirmation after 5 seconds
        setTimeout(() => {
          setTenderConfirmations(prev => ({ ...prev, [item.id]: { ...prev[item.id], visible: false } }));
        }, 5000);
        
        // Refresh listings to show updated highest bid
        setTimeout(() => {
          contextRefreshListings();
        }, 1000);
        
      } else if (response.status === 400) {
        showToast(data.detail || 'Invalid tender offer', 'error');
      } else {
        showToast(data.detail || 'Failed to submit tender offer', 'error');
      }
    } catch (error) {
      console.error('Error submitting tender:', error);
      showToast('Failed to submit tender offer. Please try again.', 'error');
    } finally {
      // Clear loading state for this item
      setSubmittingTenders(prev => ({ ...prev, [item.id]: false }));
    }
  };

  const handleAddToFavorites = (item) => {
    addToFavorites(item);
  };

  const updateSearchQuery = (query) => {
    setGlobalSearchQuery(query);
  };

  const updateFilters = (newFilters) => {
    setGlobalFilters(newFilters);
  };

  const updateSortBy = (sort) => {
    setGlobalSortBy(sort);
  };

  const updateViewMode = (mode) => {
    setGlobalViewMode(mode);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading amazing products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Hero Section with Dynamic Content and Search - ROUNDED CORNERS */}
      <div 
        className="relative bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white overflow-hidden w-full rounded-2xl"
        style={{ 
          height: heroContent.height ? `${heroContent.height}px` : '400px',
          minHeight: '300px'
        }}
      >
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative z-10 text-center flex flex-col justify-center h-full px-8">
          {/* Hero Image */}
          {heroContent.image_url && (
            <div className="mb-6 flex justify-center">
              <img 
                src={heroContent.image_url} 
                alt="Hero" 
                className="max-h-24 max-w-48 object-contain" 
              />
            </div>
          )}
          
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            {heroContent.title}
          </h1>
          <p className="text-xl mb-8 opacity-90 max-w-3xl mx-auto">
            {heroContent.description}
          </p>
          
          {/* Hero Search Bar - FULL WIDTH */}
          <div className="w-full">
            <div className="relative bg-white/10 backdrop-blur-sm rounded-2xl p-2 border border-white/20 max-w-4xl mx-auto">
              <div className="flex items-center">
                <Search className="absolute left-6 text-white/70 w-6 h-6" />
                <input
                  type="text"
                  placeholder={heroContent.search_placeholder || 'Search for anything you need...'}
                  value={searchQuery}
                  onChange={(e) => updateSearchQuery(e.target.value)}
                  className="w-full pl-16 pr-4 py-4 bg-transparent text-white placeholder-white/70 text-lg focus:outline-none"
                />
                <button 
                  onClick={() => {
                    if (searchQuery.trim()) {
                      document.getElementById('search-results')?.scrollIntoView({ behavior: 'smooth' });
                    }
                  }}
                  className="flex-shrink-0 px-8 py-4 bg-white/20 hover:bg-white/30 backdrop-blur-sm text-white rounded-xl font-semibold transition-all duration-200 hover:scale-105"
                >
                  Search
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Results Count and Filter Controls - INLINE */}
      <div id="search-results" className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
        <div className="flex items-center gap-4 text-gray-600 dark:text-gray-300">
          <span className="text-lg font-semibold">
            {filteredListings.length} Result{filteredListings.length !== 1 ? 's' : ''}
            {searchQuery && ` for "${searchQuery}"`}
          </span>
          
          <button
            onClick={refreshListings}
            className="flex items-center space-x-2 px-3 py-2 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-lg font-medium transition-all duration-200 hover:scale-105"
            title="Refresh listings from server"
          >
            <RefreshCw className="w-4 h-4" />
            <span className="hidden sm:inline">Refresh</span>
          </button>
        </div>

        {/* Filter and Sort Controls - INLINE WITH RESULTS COUNT */}
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-200"
          >
            <SlidersHorizontal className="w-5 h-5" />
            <span>Filters</span>
          </button>

          <select
            value={sortBy}
            onChange={(e) => updateSortBy(e.target.value)}
            className="px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-700 dark:text-gray-300 focus:ring-2 focus:ring-blue-500"
          >
            <option value="newest">Newest First</option>
            <option value="price_low">Price: Low to High</option>
            <option value="price_high">Price: High to Low</option>
            <option value="rating">Highest Rated</option>
            <option value="popular">Most Popular</option>
          </select>

          <div className="flex bg-gray-100 dark:bg-gray-800 rounded-xl p-1">
            <button
              onClick={() => updateViewMode('grid')}
              className={`p-2 rounded-lg transition-all duration-200 ${
                viewMode === 'grid' 
                ? 'bg-white dark:bg-gray-700 shadow-sm text-blue-600' 
                : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              <Grid3X3 className="w-5 h-5" />
            </button>
            <button
              onClick={() => updateViewMode('list')}
              className={`p-2 rounded-lg transition-all duration-200 ${
                viewMode === 'list' 
                ? 'bg-white dark:bg-gray-700 shadow-sm text-blue-600' 
                : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Advanced Filters Panel */}
      {showFilters && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 shadow-lg">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Advanced Filters</h3>
            <button
              onClick={() => setShowFilters(false)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Type Filter (replaces Category) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Type
              </label>
              <select
                value={filters.type}
                onChange={(e) => updateFilters({...filters, type: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white h-10 leading-none"
              >
                <option value="all">All Types</option>
                <option value="Private">Private</option>
                <option value="Business">Business</option>
              </select>
            </div>

            {/* Price Range (from-to inputs) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Price Range (€)
              </label>
              <div className="flex items-center space-x-2 h-10">
                <div className="flex-1">
                  <input
                    type="number"
                    placeholder="From"
                    min="0"
                    value={filters.priceFrom}
                    onChange={(e) => updateFilters({...filters, priceFrom: parseInt(e.target.value) || 0})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm h-full"
                  />
                </div>
                <span className="text-gray-500 dark:text-gray-400 flex-shrink-0">-</span>
                <div className="flex-1">
                  <input
                    type="number"
                    placeholder="To"
                    min="0"
                    value={filters.priceTo}
                    onChange={(e) => updateFilters({...filters, priceTo: parseInt(e.target.value) || 10000})}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm h-full"
                  />
                </div>
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                From €{filters.priceFrom} to €{filters.priceTo}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="flex flex-col">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Actions
              </label>
              <button
                onClick={() => updateFilters({type: 'all', priceFrom: 0, priceTo: 10000, location: 'all', rating: 0})}
                className="w-full px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors h-10"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Products Grid/List */}
      {filteredListings.length === 0 ? (
        <div className="text-center py-16">
          <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
            <Search className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No products found</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {searchQuery ? 'Try adjusting your search terms or filters' : 'Be the first to create a listing!'}
          </p>
          <Link
            to="/create-listing"
            className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors"
          >
            Create Your First Listing
          </Link>
        </div>
      ) : (
        <div className={viewMode === 'grid' 
          ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6' 
          : 'space-y-4'
        }>
          {filteredListings.map((item) => (
            <ProductCard
              key={item.id}
              item={item}
              viewMode={viewMode}
              onAddToCart={handleAddToCart}
              onSubmitTender={handleSubmitTender}
              onFavoriteToggle={handleFavoriteToggle}
              onMessageSeller={handleMessageSeller}
              isInFavorites={isInFavorites}
              isSubmittingTender={submittingTenders[item.id] || false}
            />
          ))}
        </div>
      )}

      {/* Load More Button */}
      {filteredListings.length > 0 && (
        <div className="text-center pt-8">
          <button className="px-8 py-3 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium">
            Load More Products
          </button>
        </div>
      )}

      {/* Message Seller Modal */}
      {showMessageModal && selectedProduct && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-lg w-full">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-600 to-purple-600">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-white flex items-center">
                  <MessageCircle className="w-6 h-6 mr-2" />
                  Message Seller
                </h3>
                <button
                  onClick={() => setShowMessageModal(false)}
                  className="text-white hover:text-gray-200 transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            <div className="p-6">
              {/* Product Info */}
              <div className="flex items-start space-x-4 mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-xl">
                <img
                  src={selectedProduct.images?.[0] || '/api/placeholder/400/300'}
                  alt={selectedProduct.title}
                  className="w-16 h-16 object-cover rounded-lg"
                />
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-gray-900 dark:text-white truncate">
                    {selectedProduct.title}
                  </h4>
                  <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
                    €{parseFloat(selectedProduct.price || 0).toFixed(2)}
                  </p>
                  <div className="flex items-center mt-1 text-sm text-gray-600 dark:text-gray-400">
                    <User className="w-4 h-4 mr-1" />
                    Seller: {typeof selectedProduct.seller === 'string' ? selectedProduct.seller : 
                            (selectedProduct.seller?.name || selectedProduct.seller_id || 'Unknown')}
                  </div>
                </div>
              </div>

              {/* Message Input */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Your Message
                </label>
                <textarea
                  value={messageContent}
                  onChange={(e) => setMessageContent(e.target.value)}
                  rows={4}
                  className="w-full px-4 py-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 resize-none"
                  placeholder="Type your message to the seller..."
                />
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end space-x-4">
                <button
                  onClick={() => setShowMessageModal(false)}
                  className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-xl font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSendMessage}
                  disabled={!messageContent.trim() || sending}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-xl font-medium transition-colors flex items-center"
                >
                  {sending ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      Sending...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4 mr-2" />
                      Send Message
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Enhanced Product Card Component (used in JSX below)
function ProductCard({ item, viewMode, onAddToCart, onSubmitTender, onFavoriteToggle, onMessageSeller, isInFavorites, isSubmittingTender }) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  // Removed unused state
  const [priceSuggestion, setPriceSuggestion] = useState(null);
  const [loadingSuggestion, setLoadingSuggestion] = useState(false);
  const navigate = useNavigate();

  const isGridView = viewMode === 'grid';
  
  // Debug: Log seller data for first few items
  React.useEffect(() => {
    if (item.id && ['2e2836dc-c1f2-48e5-94a6-9aaf2828c16a', 'listing-0', 'listing-1'].includes(item.id)) {
      console.log(`🔍 ProductCard Debug - Item ${item.id}:`, {
        title: item.title,
        seller: item.seller,
        'seller.is_business': item.seller?.is_business,
        'seller.name': item.seller?.name,
        'seller.username': item.seller?.username
      });
    }
  }, [item.id, item.seller]);

  // Fetch price suggestion for catalyst items
  useEffect(() => {
    const fetchPriceSuggestion = async () => {
      // Only fetch price suggestions for catalyst items
      if (item.category === 'Catalysts' && (item.catalyst_id || item.title)) {
        setLoadingSuggestion(true);
        try {
          // Try to get price suggestion from Cat Database
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/catalyst/calculations`);
          if (response.ok) {
            const calculations = await response.json();
            
            // Find matching calculation by catalyst_id or title
            let suggestion = null;
            if (item.catalyst_id) {
              suggestion = calculations.find(calc => calc.cat_id === item.catalyst_id);
            } else {
              // Try to match by title
              suggestion = calculations.find(calc => 
                calc.name && calc.name.toLowerCase() === item.title.toLowerCase()
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
  }, [item.catalyst_id, item.title, item.category]);

  // Removed unused function

  const handleCardClick = () => {
    navigate(`/product/${item.id}`);
  };



  return (
    <div 
      className={`group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 overflow-hidden cursor-pointer ${
        isGridView ? 'hover:-translate-y-2' : 'flex space-x-4 p-4'
      }`}
      // Removed unused hover handlers
      onClick={handleCardClick}
    >
      {/* Image Section */}
      <div className={`relative ${isGridView ? '' : 'w-48 h-48 flex-shrink-0'}`}>
        {/* Clickable overlay for image navigation - positioned behind other elements */}
        <div 
          className="absolute inset-0 cursor-pointer z-10"
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/product/${item.id}`);
          }}
          title="View product details"
        />
        
        <img
          src={item.images?.[currentImageIndex] || item.images?.[0] || '/api/placeholder/400/300'}
          alt={item.title}
          className={`object-cover transition-transform duration-300 group-hover:scale-105 ${
            isGridView ? 'w-full h-64' : 'w-full h-full rounded-lg'
          }`}
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

        {/* Tags and Badges */}
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

        {/* Enhanced Favorite Button - Only Favorite, No Share */}
        <div className="absolute top-2 right-2 z-20">
          <button
            onClick={(e) => onFavoriteToggle(item, e)}
            className={`p-3 backdrop-blur-lg rounded-full shadow-lg transition-all duration-300 transform hover:scale-110 ${
              isInFavorites(item.id) 
                ? 'bg-red-500/90 text-white shadow-red-500/25' 
                : 'bg-white/90 dark:bg-gray-800/90 text-gray-700 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-500'
            }`}
            title={isInFavorites(item.id) ? 'Remove from favorites' : 'Add to favorites'}
          >
            {isInFavorites(item.id) ? (
              <Heart className="w-5 h-5 fill-current animate-pulse" />
            ) : (
              <Heart className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Views Counter */}
        <div className="absolute bottom-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded-full flex items-center z-20">
          <Eye className="w-3 h-3 mr-1" />
          {item.views}
        </div>
      </div>

      {/* Content Section */}
      <div className={`${isGridView ? 'p-4' : 'flex-1 min-w-0'}`}>
        <div className="flex items-start justify-between mb-2">
          <h3 className={`font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 transition-colors ${
            isGridView ? 'text-lg line-clamp-2' : 'text-xl'
          }`}>
            {item.title}
          </h3>
        </div>

        {/* Price Section */}
        <div className="mb-3">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-2xl font-bold text-gray-900 dark:text-white">
              €{item.price.toFixed(2)}
            </span>
          </div>
          
          {/* Market Price Suggestion - Show for catalyst items */}
          {item.category === 'Catalysts' && (
            <div className="space-y-1">
              {loadingSuggestion ? (
                <div className="flex items-center text-xs text-gray-500 dark:text-gray-400 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="w-3 h-3 border border-gray-400 border-t-transparent rounded-full animate-spin mr-2"></div>
                  Loading market range...
                </div>
              ) : priceSuggestion ? (
                <div className="relative overflow-hidden rounded-xl bg-gradient-to-br from-indigo-50 via-blue-50 to-cyan-50 dark:from-indigo-900/40 dark:via-blue-900/40 dark:to-cyan-900/40 border border-indigo-100 dark:border-indigo-800/60 shadow-sm">
                  <div className="absolute top-0 right-0 w-12 h-12 bg-gradient-to-bl from-indigo-200/20 to-transparent dark:from-indigo-600/10 rounded-bl-full"></div>
                  <div className="relative p-3">
                    <div className="flex items-center space-x-2">
                      <div className="p-1.5 rounded-lg bg-gradient-to-r from-indigo-500 to-blue-500 shadow-sm">
                        <Database className="w-3 h-3 text-white" />
                      </div>
                      <div>
                        <div className="text-xs font-medium text-indigo-700 dark:text-indigo-300 uppercase tracking-wide">
                          Market Range
                        </div>
                        <div className="text-sm font-bold text-indigo-900 dark:text-indigo-100 leading-tight">
                          €{(priceSuggestion * 0.9).toFixed(0)} - €{(priceSuggestion * 1.1).toFixed(0)}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : null}
            </div>
          )}
        </div>

        {/* Seller Info - Use username, remove rating */}
        <div className="flex items-center space-x-2 mb-3">
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold ${
            item.seller?.is_business 
              ? 'bg-gradient-to-r from-blue-500 to-indigo-600' 
              : 'bg-gradient-to-r from-green-500 to-emerald-600'
          }`}>
            <span>
              {(item.seller?.username || item.seller?.name || 'U').charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {item.seller?.username || item.seller?.name || 'Unknown User'}
            </span>
            {item.seller?.verified && (
              <span className="text-blue-500 text-xs">✓ Verified</span>
            )}
          </div>
        </div>

        {/* Location - Show only City, Country (no street) */}
        <div className="text-sm text-gray-500 dark:text-gray-400 mb-4">
          <div className="flex items-center">
            <MapPin className="w-4 h-4 mr-1" />
            {/* Format as City, Country only - exclude street */}
            {(() => {
              const city = item.address?.city || '';
              const country = item.address?.country || '';
              
              // If we have address data, use city and country only
              if (city || country) {
                const parts = [city, country].filter(Boolean);
                return parts.length > 0 ? parts.join(', ') : 'Location not specified';
              }
              
              // Fallback to seller location if no structured address
              // If seller location is already in "City, Country" format, use it
              // If it has more parts (like street), extract only last two parts
              if (item.seller?.location) {
                const locationParts = item.seller.location.split(',').map(part => part.trim());
                if (locationParts.length >= 2) {
                  // Take last two parts as City, Country
                  return locationParts.slice(-2).join(', ');
                } else {
                  // Single part, assume it's city
                  return locationParts[0];
                }
              }
              
              return 'Location not specified';
            })()}
          </div>
          {item.shipping && (
            <div className="flex items-center text-green-600 mt-1">
              <Clock className="w-4 h-4 mr-1" />
              {item.shipping}
            </div>
          )}
        </div>

        {/* Features */}
        {item.features && (
          <div className="flex flex-wrap gap-1 mb-4">
            {item.features.slice(0, 3).map((feature) => (
              <span
                key={feature}
                className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-1 rounded-full"
              >
                {feature}
              </span>
            ))}
          </div>
        )}

        {/* Tender Offer Section */}
        <div className={`${isGridView ? '' : 'mt-4'} relative z-30`}>
          {/* Current Highest Bid Display */}
          {item.highest_bid && (
            <div className="mb-3 p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
              <div className="flex items-center justify-between text-sm">
                <span className="text-yellow-800 dark:text-yellow-300 font-medium">
                  Current highest bid:
                </span>
                <span className="text-yellow-900 dark:text-yellow-200 font-bold">
                  €{parseFloat(item.highest_bid).toFixed(2)}
                </span>
              </div>
            </div>
          )}
          
          {/* Tender Input Form */}
          <div className="flex space-x-2" onClick={(e) => e.stopPropagation()}>
            <div className="flex-1">
              <input
                type="number"
                min={item.highest_bid || item.price || 0}
                step="10"
                placeholder={`Min: €${(item.highest_bid || item.price || 0).toFixed(2)}`}
                className="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                onClick={(e) => e.stopPropagation()}
                onFocus={(e) => e.stopPropagation()}
                onChange={(e) => {
                  e.stopPropagation();
                  const input = e.target;
                  input.dataset.offerAmount = e.target.value;
                }}
              />
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                const input = e.target.parentElement.previousElementSibling?.querySelector('input') || 
                             e.target.parentElement.parentElement.querySelector('input');
                const offerAmount = parseFloat(input?.value || 0);
                if (offerAmount && offerAmount >= (item.highest_bid || item.price || 0)) {
                  onSubmitTender(item, offerAmount);
                  input.value = ''; // Clear input after submission
                } else {
                  alert(`Please enter an amount of at least €${(item.highest_bid || item.price || 0).toFixed(2)}`);
                }
              }}
              className="px-6 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors flex items-center space-x-2"
              title="Submit tender offer"
            >
              <span>Offer</span>
            </button>
          </div>
          
          {/* Message Seller Button */}
          <button 
            onClick={(e) => {
              e.stopPropagation();
              onMessageSeller(item, e);
            }}
            className="w-full mt-2 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-blue-600 dark:hover:text-blue-400 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2"
            title="Message seller"
          >
            <MessageCircle className="w-4 h-4" />
            <span>Message Seller</span>
          </button>
        </div>

        {/* Date Only - Remove Condition */}
        <div className="flex items-center justify-end mt-3 text-xs text-gray-500 dark:text-gray-400">
          <span>
            {item.created_at 
              ? new Date(item.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric'
                })
              : item.createdAt 
                ? new Date(item.createdAt).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                  })
                : new Date().toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                  })
            }
          </span>
        </div>
      </div>
    </div>
  );
}

export default ModernBrowsePage;