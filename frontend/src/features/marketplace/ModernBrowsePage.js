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
  SlidersHorizontal,
  X,
  Send,
  User,
  Database,
  RefreshCw,
  MessageCircle,
  Monitor
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
// Removed unused import
import { useMarketplace } from '../../context/MarketplaceContext';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import { liveService } from '../../services/liveService';

// Hook to get ads configuration
function useAdsConfig() {
  const [adsConfig, setAdsConfig] = useState(null);
  
  useEffect(() => {
    const loadAdsConfig = () => {
      try {
        const savedConfig = localStorage.getItem('cataloro_site_config');
        console.log('🔍 ModernBrowsePage - Loading ads config from localStorage:', savedConfig ? 'exists' : 'not found');
        
        if (savedConfig) {
          const config = JSON.parse(savedConfig);
          console.log('🔍 ModernBrowsePage - Parsed config:', config);
          console.log('🔍 ModernBrowsePage - AdsManager exists:', !!config.adsManager);
          
          if (config.adsManager) {
            console.log('🔍 ModernBrowsePage - Setting ads config:', config.adsManager);
            setAdsConfig(config.adsManager);
          } else {
            console.log('⚠️ ModernBrowsePage - No adsManager in config, using defaults');
            // Set default configuration for browse page ad
            const defaultAdsConfig = {
              browsePageAd: {
                active: true,
                image: null,
                description: 'Advertisement Space',
                runtime: '1 month',
                width: '300px',
                height: '600px'
              }
            };
            setAdsConfig(defaultAdsConfig);
          }
        } else {
          console.log('⚠️ ModernBrowsePage - No saved config found, using defaults');
          // Set default configuration for browse page ad
          const defaultAdsConfig = {
            browsePageAd: {
              active: true,
              image: null,
              description: 'Advertisement Space',
              runtime: '1 month',
              width: '300px',
              height: '600px'
            }
          };
          setAdsConfig(defaultAdsConfig);
        }
      } catch (error) {
        console.error('❌ ModernBrowsePage - Error loading ads configuration:', error);
        // Set default configuration on error
        const defaultAdsConfig = {
          browsePageAd: {
            active: true,
            image: null,
            description: 'Advertisement Space',
            runtime: '1 month',
            width: '300px',
            height: '600px'
          }
        };
        setAdsConfig(defaultAdsConfig);
      }
    };

    // Load initially
    loadAdsConfig();

    // Listen for ads config updates
    const handleAdsConfigUpdate = () => {
      console.log('🔍 ModernBrowsePage - Ads config update event received');
      loadAdsConfig();
    };

    window.addEventListener('adsConfigUpdated', handleAdsConfigUpdate);
    window.addEventListener('storage', handleAdsConfigUpdate);

    return () => {
      window.removeEventListener('adsConfigUpdated', handleAdsConfigUpdate);
      window.removeEventListener('storage', handleAdsConfigUpdate);
    };
  }, []);
  
  // Debug log current state
  useEffect(() => {
    console.log('🔍 ModernBrowsePage - Current adsConfig state:', adsConfig);
    if (adsConfig?.browsePageAd) {
      console.log('🔍 ModernBrowsePage - Browse page ad config:', adsConfig.browsePageAd);
    }
  }, [adsConfig]);
  
  return adsConfig;
}

function ModernBrowsePage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const navigate = useNavigate();
  const adsConfig = useAdsConfig();
  
  // Use marketplace context
  const {
    filteredProducts,
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

  // Dynamic price range settings
  const [priceRangeSettings, setPriceRangeSettings] = useState({
    price_range_min_percent: 10.0,
    price_range_max_percent: 10.0
  });
  
  // User active bids
  const [userActiveBids, setUserActiveBids] = useState({});
  
  // Full-page bid confirmation modal
  const [bidConfirmationModal, setBidConfirmationModal] = useState({
    show: false,
    bidAmount: 0,
    itemTitle: '',
    itemId: '',
    success: false
  });

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

  // Fetch price range settings and user active bids
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

    const fetchUserActiveBids = async () => {
      if (user?.id) {
        try {
          const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
          const response = await fetch(`${backendUrl}/api/user/${user.id}/active-bids`);
          
          if (response.ok) {
            const { active_bids } = await response.json();
            setUserActiveBids(active_bids);
          }
        } catch (error) {
          console.error('Error fetching user active bids:', error);
        }
      }
    };

    fetchPriceRangeSettings();
    fetchUserActiveBids();
  }, [user?.id]);



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
        // Show full-page bid confirmation modal
        setBidConfirmationModal({
          show: true,
          bidAmount: parseFloat(offerAmount),
          itemTitle: item.title,
          itemId: item.id,
          success: true
        });
        
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
        setBidConfirmationModal({
          show: true,
          bidAmount: parseFloat(offerAmount),
          itemTitle: item.title,
          itemId: item.id,
          success: false,
          errorMessage: data.detail || 'Invalid tender offer'
        });
      } else {
        setBidConfirmationModal({
          show: true,
          bidAmount: parseFloat(offerAmount),
          itemTitle: item.title,
          itemId: item.id,
          success: false,
          errorMessage: 'Failed to submit tender offer'
        });
      }
    } catch (error) {
      console.error('Error submitting tender:', error);
      setBidConfirmationModal({
        show: true,
        bidAmount: parseFloat(offerAmount),
        itemTitle: item.title,
        itemId: item.id,
        success: false,
        errorMessage: 'Network error. Please check your connection and try again.'
      });
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
    <>
      {/* Full-Width Hero Section - Breaks out of container */}
      <div 
        className="hero-section relative text-white overflow-hidden w-screen"
        style={{ 
          height: '400px',
          minHeight: '300px',
          background: 'linear-gradient(to right, #3f6ec7, #a855f7, #ec4899)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          marginLeft: 'calc(-50vw + 50%)',
          marginRight: 'calc(-50vw + 50%)',
          marginTop: '-2rem', // Offset the container padding
          marginBottom: '2rem'
        }}
      >
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative z-10 text-center flex flex-col justify-center h-full px-8 max-w-7xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            {heroContent.title || 'Discover Amazing Products'}
          </h1>
          <p className="text-xl mb-8 opacity-90 max-w-3xl mx-auto">
            {heroContent.description || 'From electronics to fashion, find everything you need in one place'}
          </p>
          
          {/* Hero Search Bar - FULL WIDTH */}
          <div className="w-full">
            <div className="search-bar-container relative bg-white/10 backdrop-blur-sm rounded-2xl p-2 border border-white/20 max-w-4xl mx-auto">
              <div className="flex items-center">
                <Search className="absolute left-6 text-white/70 w-6 h-6" />
                <input
                  type="text"
                  placeholder={heroContent.search_placeholder || "Search for anything you need..."}
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

      {/* Main Content Container */}
      <div className="space-y-8">

      {/* Results Count and Filter Controls - INLINE */}
      <div 
        id="search-results" 
        className={`flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between ${
          heroContent.display_mode === 'full_width' ? 'mt-8' : ''
        }`}
      >
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
      <div className="mt-6">
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
        <div className="flex gap-6">
          {/* Products Grid */}
          <div className={`${
            adsConfig?.browsePageAd?.active ? 'flex-1' : 'w-full'
          }`}>
            <div className={viewMode === 'grid' 
              ? (adsConfig?.browsePageAd?.active 
                ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6' 
                : 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6')
              : 'space-y-4'
            }>
              {filteredListings.map((item) => (
                <ProductCard
                  key={item.id}
                  item={item}
                  viewMode={viewMode}
                  onSubmitTender={handleSubmitTender}
                  onFavoriteToggle={handleFavoriteToggle}
                  onMessageSeller={handleMessageSeller}
                  isInFavorites={isInFavorites}
                  isSubmittingTender={submittingTenders[item.id] || false}
                  tenderConfirmation={tenderConfirmations[item.id]}
                  priceRangeSettings={priceRangeSettings}
                  userActiveBids={userActiveBids}
                  user={user}
                />
              ))}
            </div>
          </div>

          {/* Browse Page Advertisement */}
          {adsConfig?.browsePageAd?.active && (
            <div className="flex-shrink-0">
              <div 
                className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm hover:shadow-md transition-shadow flex flex-col items-center justify-center"
                style={{
                  width: adsConfig.browsePageAd.width || '300px',
                  height: adsConfig.browsePageAd.height || '600px'
                }}
              >
                {adsConfig.browsePageAd.image ? (
                  <>
                    <img
                      src={adsConfig.browsePageAd.image}
                      alt={adsConfig.browsePageAd.description || 'Advertisement'}
                      className="w-full h-full object-cover"
                    />
                    {adsConfig.browsePageAd.description && (
                      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
                        <p className="text-white text-sm">{adsConfig.browsePageAd.description}</p>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="p-6 text-center">
                    <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Monitor className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Advertisement Space</h3>
                    {adsConfig.browsePageAd.description ? (
                      <p className="text-gray-600 dark:text-gray-400 text-sm">{adsConfig.browsePageAd.description}</p>
                    ) : (
                      <p className="text-gray-600 dark:text-gray-400 text-sm">Your ad will appear here</p>
                    )}
                    <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
                      Runtime: {adsConfig.browsePageAd.runtime || '1 month'}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
      </div>

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

      {/* Bid Confirmation Modal */}
      {bidConfirmationModal.show && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full">
            <div className={`p-6 border-b border-gray-200 dark:border-gray-700 ${
              bidConfirmationModal.success 
                ? 'bg-gradient-to-r from-green-600 to-emerald-600' 
                : 'bg-gradient-to-r from-red-600 to-pink-600'
            }`}>
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-white flex items-center">
                  {bidConfirmationModal.success ? (
                    <>
                      <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      Bid Submitted Successfully!
                    </>
                  ) : (
                    <>
                      <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      Bid Submission Failed
                    </>
                  )}
                </h3>
                <button
                  onClick={() => setBidConfirmationModal({ ...bidConfirmationModal, show: false })}
                  className="text-white hover:text-gray-200 transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            <div className="p-6">
              <div className="text-center">
                <div className="mb-4">
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {bidConfirmationModal.itemTitle}
                  </h4>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
                    €{bidConfirmationModal.bidAmount?.toFixed(2)}
                  </div>
                </div>

                {bidConfirmationModal.success ? (
                  <div className="space-y-3">
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-800">
                      <p className="text-green-800 dark:text-green-300 font-medium">
                        🎉 Your tender offer has been submitted successfully!
                      </p>
                      <p className="text-green-700 dark:text-green-400 text-sm mt-1">
                        The seller will be notified and can accept or decline your offer.
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-800">
                      <p className="text-red-800 dark:text-red-300 font-medium">
                        ❌ {bidConfirmationModal.errorMessage}
                      </p>
                      <p className="text-red-700 dark:text-red-400 text-sm mt-1">
                        Please check your bid amount and try again.
                      </p>
                    </div>
                  </div>
                )}

                <div className="mt-6">
                  <button
                    onClick={() => setBidConfirmationModal({ ...bidConfirmationModal, show: false })}
                    className={`w-full px-6 py-3 rounded-xl font-medium transition-colors ${
                      bidConfirmationModal.success
                        ? 'bg-green-600 hover:bg-green-700 text-white'
                        : 'bg-red-600 hover:bg-red-700 text-white'
                    }`}
                  >
                    {bidConfirmationModal.success ? 'Great!' : 'Try Again'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      </div>
    </>
  );
}

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

// Enhanced Product Card Component (used in JSX below)
function ProductCard({ item, viewMode, onSubmitTender, onFavoriteToggle, onMessageSeller, isInFavorites, isSubmittingTender, tenderConfirmation, priceRangeSettings, userActiveBids, user }) {
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
      className={`product-card group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 overflow-hidden cursor-pointer ${
        isGridView ? 'hover:-translate-y-1' : 'flex space-x-4 p-4'
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
          className={`object-cover transition-transform duration-300 group-hover:scale-[1.02] ${
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
            className={`favorites-button wishlist-button add-to-favorites p-3 backdrop-blur-lg rounded-full shadow-lg transition-all duration-300 transform hover:scale-110 ${
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

      {/* Content Section - Reorganized Structure: Picture, Title, Price, Market Range, Seller, Location, Time Left, Input Field, Date */}
      <div className={`${isGridView ? 'p-4' : 'flex-1 min-w-0'}`}>
        
        {/* 1. Title */}
        <div className="mb-3">
          <h3 className={`font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 transition-colors ${
            isGridView ? 'text-lg line-clamp-2' : 'text-xl'
          }`}>
            {item.title}
          </h3>
        </div>

        {/* 2. Price */}
        <div className="mb-3">
          <div className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-gray-900 dark:text-white">
              €{((item.bid_info?.has_bids && item.bid_info?.highest_bid) ? item.bid_info.highest_bid : item.price).toFixed(2)}
            </span>
            {item.bid_info?.has_bids && (
              <span className="text-sm text-gray-500 dark:text-gray-400 line-through">
                €{item.price.toFixed(2)} starting
              </span>
            )}
          </div>
        </div>

        {/* 3. Market Range - Show for catalyst items */}
        {item.category === 'Catalysts' && (
          <div className="mb-3">
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
                        €{(priceSuggestion * (100 - priceRangeSettings.price_range_min_percent) / 100).toFixed(0)} - €{(priceSuggestion * (100 + priceRangeSettings.price_range_max_percent) / 100).toFixed(0)}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        )}

        {/* 4. Seller */}
        <div className="mb-3">
          <div className="flex items-center space-x-2">
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
        </div>

        {/* 5. Location */}
        <div className="mb-3">
          <div className="flex items-center text-gray-500 dark:text-gray-400">
            <MapPin className="w-4 h-4 mr-1" />
            <span className="text-sm">
              {(() => {
                const city = item.address?.city || '';
                const country = item.address?.country || '';
                
                // If we have address data, use city and country only
                if (city || country) {
                  const parts = [city, country].filter(Boolean);
                  return parts.length > 0 ? parts.join(', ') : 'Location not specified';
                }
                
                // Fallback to seller location if no structured address
                if (item.seller?.location) {
                  const locationParts = item.seller.location.split(',').map(part => part.trim());
                  if (locationParts.length >= 2) {
                    return locationParts.slice(-2).join(', ');
                  } else {
                    return locationParts[0];
                  }
                }
                
                return 'Location not specified';
              })()}
            </span>
          </div>
        </div>

        {/* 6. Time Left */}
        {item.time_info?.has_time_limit && (
          <div className="mb-3">
            <div className={`relative overflow-hidden rounded-xl border-2 ${
              item.time_info.is_expired 
                ? 'border-red-200 dark:border-red-800 bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/30'
                : item.time_info.time_remaining_seconds <= 3600
                  ? 'border-red-200 dark:border-red-800 bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/30'
                  : item.time_info.time_remaining_seconds <= 21600
                    ? 'border-orange-200 dark:border-orange-800 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/30'
                    : item.time_info.time_remaining_seconds <= 86400
                      ? 'border-yellow-200 dark:border-yellow-800 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/30'
                      : 'border-green-200 dark:border-green-800 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/30'
            }`}>
              <div className={`absolute top-0 right-0 w-12 h-12 rounded-bl-full ${
                item.time_info.is_expired || item.time_info.time_remaining_seconds <= 3600
                  ? 'bg-gradient-to-bl from-red-200/20 to-transparent dark:from-red-600/10'
                  : item.time_info.time_remaining_seconds <= 21600
                    ? 'bg-gradient-to-bl from-orange-200/20 to-transparent dark:from-orange-600/10'
                    : item.time_info.time_remaining_seconds <= 86400
                      ? 'bg-gradient-to-bl from-yellow-200/20 to-transparent dark:from-yellow-600/10'
                      : 'bg-gradient-to-bl from-green-200/20 to-transparent dark:from-green-600/10'
              }`}></div>
              <div className="relative p-3">
                <div className="flex items-center space-x-2">
                  <div className={`p-1.5 rounded-lg shadow-sm ${
                    item.time_info.is_expired || item.time_info.time_remaining_seconds <= 3600
                      ? 'bg-gradient-to-r from-red-500 to-red-600'
                      : item.time_info.time_remaining_seconds <= 21600
                        ? 'bg-gradient-to-r from-orange-500 to-orange-600'
                        : item.time_info.time_remaining_seconds <= 86400
                          ? 'bg-gradient-to-r from-yellow-500 to-yellow-600'
                          : 'bg-gradient-to-r from-green-500 to-green-600'
                  }`}>
                    <Clock className="w-3 h-3 text-white" />
                  </div>
                  <div>
                    <div className={`text-xs font-medium uppercase tracking-wide ${
                      item.time_info.is_expired || item.time_info.time_remaining_seconds <= 3600
                        ? 'text-red-700 dark:text-red-300'
                        : item.time_info.time_remaining_seconds <= 21600
                          ? 'text-orange-700 dark:text-orange-300'
                          : item.time_info.time_remaining_seconds <= 86400
                            ? 'text-yellow-700 dark:text-yellow-300'
                            : 'text-green-700 dark:text-green-300'
                    }`}>
                      {item.time_info.is_expired ? 'Expired' : 'Time Left'}
                    </div>
                    <div className={`text-sm font-bold leading-tight ${
                      item.time_info.is_expired || item.time_info.time_remaining_seconds <= 3600
                        ? 'text-red-900 dark:text-red-100'
                        : item.time_info.time_remaining_seconds <= 21600
                          ? 'text-orange-900 dark:text-orange-100'
                          : item.time_info.time_remaining_seconds <= 86400
                            ? 'text-yellow-900 dark:text-yellow-100'
                            : 'text-green-900 dark:text-green-100'
                    }`}>
                      <CountdownTimer timeInfo={item.time_info} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 7. Input Field */}
        <div className="mb-3">
          {/* User is Highest Bidder Indicator */}
          {item.bid_info?.highest_bidder_id === user?.id && item.bid_info?.has_bids && (
            <div className="mb-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="flex items-center space-x-2">
                <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="text-blue-800 dark:text-blue-300 font-semibold text-sm">
                    🎉 You're the highest bidder!
                  </p>
                  <p className="text-blue-700 dark:text-blue-400 text-xs">
                    Your bid of €{item.bid_info.highest_bid.toFixed(2)} is currently winning
                  </p>
                </div>
              </div>
            </div>
          )}
          
          <div className="flex space-x-2" onClick={(e) => e.stopPropagation()}>
            <div className="flex-1">
              <input
                type="number"
                min={item.bid_info?.highest_bid || item.price || 0}
                step="10"
                placeholder={
                  item.time_info?.is_expired 
                    ? "Bid..." 
                    : item.bid_info?.highest_bidder_id === user?.id && item.bid_info?.has_bids
                      ? "Bid..."
                      : `Min: €${(item.bid_info?.highest_bid || item.price || 0).toFixed(2)}`
                }
                disabled={item.time_info?.is_expired || (item.bid_info?.highest_bidder_id === user?.id && item.bid_info?.has_bids)}
                className={`w-full px-3 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  item.time_info?.is_expired
                    ? 'border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 cursor-not-allowed'
                    : item.bid_info?.highest_bidder_id === user?.id && item.bid_info?.has_bids
                      ? 'border-blue-300 dark:border-blue-600 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 cursor-not-allowed'
                      : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
                }`}
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
                if (item.time_info?.is_expired) {
                  alert('This listing has expired. No more bids can be placed.');
                  return;
                }
                if (item.bid_info?.highest_bidder_id === user?.id && item.bid_info?.has_bids) {
                  alert('You are already the highest bidder! Wait for others to place higher bids.');
                  return;
                }
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
              disabled={isSubmittingTender || item.time_info?.is_expired || (item.bid_info?.highest_bidder_id === user?.id && item.bid_info?.has_bids)}
              className={`px-6 py-2.5 rounded-lg font-medium transition-colors flex items-center space-x-2 ${
                item.time_info?.is_expired
                  ? 'bg-red-400 text-red-100 cursor-not-allowed'
                  : item.bid_info?.highest_bidder_id === user?.id && item.bid_info?.has_bids
                    ? 'bg-blue-400 text-blue-100 cursor-not-allowed'
                    : 'bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white'
              }`}
              title={
                item.time_info?.is_expired 
                  ? "Listing has expired" 
                  : item.bid_info?.highest_bidder_id === user?.id && item.bid_info?.has_bids
                    ? "You are the highest bidder"
                    : "Submit tender offer"
              }
            >
              {item.time_info?.is_expired ? (
                <span>EXPIRED</span>
              ) : item.bid_info?.highest_bidder_id === user?.id && item.bid_info?.has_bids ? (
                <span>WINNING</span>
              ) : isSubmittingTender ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Submitting...</span>
                </>
              ) : (
                <span>Offer</span>
              )}
            </button>
          </div>
          
          {/* Tender Confirmation Message */}
          {tenderConfirmation?.visible && (
            <div className="mt-2 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800 animate-pulse">
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="text-green-800 dark:text-green-300 font-semibold text-sm">
                    ✅ Tender Submitted Successfully!
                  </p>
                  <p className="text-green-700 dark:text-green-400 text-xs">
                    Your offer of €{tenderConfirmation.amount.toFixed(2)} has been submitted to the seller
                  </p>
                </div>
              </div>
            </div>
          )}
          
          {/* Current Highest Bid Display */}
          {item.highest_bid && (
            <div className="mt-2 p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
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
        </div>

        {/* 8. Date */}
        <div className="mt-2 flex items-center justify-end text-xs text-gray-500 dark:text-gray-400 border-t border-gray-100 dark:border-gray-700 pt-2">
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
                : item.date 
                  ? new Date(item.date).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric'
                    })
                  : 'Date not available'
            }
          </span>
        </div>
      </div>
    </div>
  );
}

export default ModernBrowsePage;