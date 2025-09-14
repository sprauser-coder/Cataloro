/**
 * CATALORO - Modern Browse Page (Desktop + Mobile Responsive)
 * Comprehensive marketplace with desktop and mobile optimizations
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
  Monitor,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
// Removed unused import
import { useMarketplace } from '../../context/MarketplaceContext';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import { liveService } from '../../services/liveService';
import { trackAdClick } from '../../utils/adsConfiguration';
import usePermissions from '../../hooks/usePermissions';

// Mobile Components
import MobileHeroSection from '../../components/mobile/MobileHeroSection';
import MobileFilters from '../../components/mobile/MobileFilters';
import MobileListingCard from '../../components/mobile/MobileListingCard';

// Hook to get ads configuration
function useAdsConfig() {
  const [adsConfig, setAdsConfig] = useState(null);
  const [configVersion, setConfigVersion] = useState(0);
  
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
            
            // Log specific image URLs for debugging
            if (config.adsManager.browsePageAd) {
              console.log('🔍 ModernBrowsePage - Browse page ad image URL:', config.adsManager.browsePageAd.image);
            }
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
                height: '600px',
                url: '',
                clicks: 0
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
              height: '600px',
              url: '',
              clicks: 0
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
            height: '600px',
            url: '',
            clicks: 0
          }
        };
        setAdsConfig(defaultAdsConfig);
      }
    };

    // Load initially
    loadAdsConfig();

    // Listen for ads config updates
    const handleAdsConfigUpdate = (event) => {
      console.log('🔍 ModernBrowsePage - Ads config update event received:', event.detail);
      setConfigVersion(prev => prev + 1); // Force re-render
      setTimeout(loadAdsConfig, 100); // Small delay to ensure localStorage is updated
    };

    const handleStorageChange = (event) => {
      if (event.key === 'cataloro_site_config') {
        console.log('🔍 ModernBrowsePage - Storage change detected');
        setConfigVersion(prev => prev + 1); // Force re-render
        setTimeout(loadAdsConfig, 100);
      }
    };

    window.addEventListener('adsConfigUpdated', handleAdsConfigUpdate);
    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('adsConfigUpdated', handleAdsConfigUpdate);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [configVersion]); // Add configVersion as dependency to force reloads
  
  // Debug log current state
  useEffect(() => {
    console.log('🔍 ModernBrowsePage - Current adsConfig state:', adsConfig);
    if (adsConfig?.browsePageAd) {
      console.log('🔍 ModernBrowsePage - Browse page ad config:', adsConfig.browsePageAd);
      console.log('🔍 ModernBrowsePage - Browse page ad image URL:', adsConfig.browsePageAd.image);
    }
  }, [adsConfig]);
  
  return adsConfig;
}

function ModernBrowsePage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const { permissions } = usePermissions();
  const navigate = useNavigate();
  const adsConfig = useAdsConfig();
  
  // Use marketplace context
  const {
    filteredProducts,
    allProducts,
    loadInitialProducts,
    changePage,
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
    currentPage,
    totalPages,
    totalListings,
    isLoadingPage,
    pageSize,
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

  // Mobile-specific state
  const [isMobileFiltersOpen, setIsMobileFiltersOpen] = useState(false);
  const [quickStats, setQuickStats] = useState({});

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
  
  // Hero content state
  const [heroContent, setHeroContent] = useState({
    title: 'Discover Amazing Products',
    description: 'From electronics to fashion, find everything you need in one place',
    height: 400,
    image_url: '',
    search_placeholder: 'Search for anything you need...',
    display_mode: 'boxed',
    background_type: 'gradient',
    background_color: '#3B82F6',
    background_gradient_from: '#3f6ec7',
    background_gradient_to: '#ec4899',
    background_image: '',
    gradient_opacity: 0.8,
    background_size: 'cover',
    background_repeat: 'no-repeat',
    background_position: 'center'
  });
  
  // Use global search and filter states from context
  const searchQuery = globalSearchQuery;
  const filters = globalFilters;
  const sortBy = globalSortBy;
  const viewMode = globalViewMode;
  // Removed unused variable
  const filteredListings = filteredProducts;

  // Removed categories array since we're using type filter instead

  // Generate dynamic hero background style based on heroContent
  const getHeroBackgroundStyle = () => {
    // Convert hex color to rgba with opacity
    const hexToRgba = (hex, opacity) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      if (!result) return hex;
      const r = parseInt(result[1], 16);
      const g = parseInt(result[2], 16);
      const b = parseInt(result[3], 16);
      return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    };

    const isFullWidth = heroContent.display_mode === 'full_width';
    const gradientOpacity = heroContent.gradient_opacity || 0.8;
    
    const baseStyle = {
      height: `${heroContent.height || 400}px`,
      minHeight: '300px',
      marginTop: '-2rem',
      marginBottom: '2rem'
    };

    // Add full-width margins only if display mode is full_width
    if (isFullWidth) {
      baseStyle.marginLeft = 'calc(-50vw + 50%)';
      baseStyle.marginRight = 'calc(-50vw + 50%)';
    } else {
      baseStyle.marginLeft = '0';
      baseStyle.marginRight = '0';
      baseStyle.borderRadius = '1rem';
    }

    // Add background image styling properties for image and image-gradient types
    if (heroContent.background_type === 'image' || heroContent.background_type === 'image-gradient') {
      baseStyle.backgroundSize = heroContent.background_size || 'cover';
      baseStyle.backgroundPosition = heroContent.background_position || 'center';
      baseStyle.backgroundRepeat = heroContent.background_repeat || 'no-repeat';
    }

    switch (heroContent.background_type) {
      case 'gradient':
        return {
          ...baseStyle,
          backgroundImage: `linear-gradient(to right, ${heroContent.background_gradient_from || '#3f6ec7'}, ${heroContent.background_gradient_to || '#ec4899'})`
        };
      case 'solid':
        return {
          ...baseStyle,
          backgroundColor: heroContent.background_color || '#3B82F6'
        };
      case 'image':
        return {
          ...baseStyle,
          backgroundImage: heroContent.background_image 
            ? `linear-gradient(rgba(0,0,0,${gradientOpacity * 0.5}), rgba(0,0,0,${gradientOpacity * 0.5})), url(${heroContent.background_image})`
            : 'linear-gradient(to right, #3f6ec7, #a855f7, #ec4899)'
        };
      case 'image-gradient':
        const gradientFromRgba = hexToRgba(heroContent.background_gradient_from || '#3f6ec7', gradientOpacity);
        const gradientToRgba = hexToRgba(heroContent.background_gradient_to || '#ec4899', gradientOpacity);
        
        return {
          ...baseStyle,
          backgroundImage: heroContent.background_image 
            ? `linear-gradient(to right, ${gradientFromRgba}, ${gradientToRgba}), url(${heroContent.background_image})`
            : `linear-gradient(to right, ${heroContent.background_gradient_from || '#3f6ec7'}, ${heroContent.background_gradient_to || '#ec4899'})`
        };
      default:
        return {
          ...baseStyle,
          backgroundImage: 'linear-gradient(to right, #3f6ec7, #a855f7, #ec4899)'
        };
    }
  };

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

  // Load quick stats for mobile hero
  useEffect(() => {
    const calculateQuickStats = () => {
      const stats = {
        totalListings: filteredListings.length,
        newToday: filteredListings.filter(item => {
          const createdDate = new Date(item.created_at);
          const today = new Date();
          return createdDate.toDateString() === today.toDateString();
        }).length,
        hotDeals: filteredListings.filter(item => item.isHotDeal || item.discount > 0).length,
        avgPrice: filteredListings.length > 0 
          ? Math.round(filteredListings.reduce((sum, item) => sum + (item.price || 0), 0) / filteredListings.length)
          : 0
      };
      setQuickStats(stats);
    };

    calculateQuickStats();
  }, [filteredListings]);

  // Mobile handlers
  const handleMobileSearch = (query) => {
    updateSearchQuery(query);
  };

  const handleMobileFiltersToggle = () => {
    setIsMobileFiltersOpen(true);
  };

  const handleMobileFiltersChange = (newFilters) => {
    updateFilters(newFilters);
  };

  const handleMobileFavorite = async (listingId, isFavorited) => {
    try {
      if (isFavorited) {
        await addToFavorites(listingId);
        showToast('Added to favorites', 'success');
      } else {
        await removeFromFavorites(listingId);
        showToast('Removed from favorites', 'success');
      }
    } catch (error) {
      showToast('Error updating favorites', 'error');
    }
  };

  const handleMobileContact = (listing) => {
    // Navigate to messaging or show contact modal
    showToast(`Contact seller for ${listing.title}`, 'info');
  };

  const handleMobileQuickView = (listing) => {
    // Show quick view modal or navigate to product detail
    window.location.href = `/listing/${listing.id}`;
  };
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

    // Enhanced check to prevent owner from bidding on own listing
    const isOwner = item.seller?.username === user.username || 
                    item.seller_id === user.id || 
                    item.seller?.id === user.id;
    
    if (isOwner) {
      showToast('You cannot bid on your own listing', 'error');
      return;
    }

    // Set loading state for this specific item
    setSubmittingTenders(prev => ({ ...prev, [item.id]: true }));

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tenders/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('cataloro_token')}`
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

  // Pagination component (reusable for top and bottom)
  const PaginationControls = ({ showInfo = true, position = "bottom" }) => {
    if (filteredListings.length === 0) return null;

    return (
      <div className={`flex items-center justify-between ${position === "top" ? "pb-6" : "pt-8"} border-${position === "top" ? "b" : "t"} border-gray-200 dark:border-gray-700`}>
        {/* Pagination Info */}
        {showInfo && (
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <span>
              Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, totalListings)} of {totalListings} listings
            </span>
          </div>
        )}

        {/* Pagination Buttons */}
        <div className={`flex items-center space-x-2 ${!showInfo ? "w-full justify-center" : ""}`}>
          {/* Previous Button */}
          <button
            onClick={() => changePage(currentPage - 1)}
            disabled={currentPage === 1 || isLoadingPage}
            className={`flex items-center px-3 py-2 rounded-lg border transition-colors ${
              currentPage === 1 || isLoadingPage
                ? 'border-gray-200 dark:border-gray-700 text-gray-400 dark:text-gray-600 cursor-not-allowed'
                : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            Previous
          </button>

          {/* Page Numbers */}
          <div className="flex items-center space-x-1">
            {(() => {
              const pages = [];
              const maxVisible = 5;
              let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
              let endPage = Math.min(totalPages, startPage + maxVisible - 1);
              
              if (endPage - startPage + 1 < maxVisible) {
                startPage = Math.max(1, endPage - maxVisible + 1);
              }

              // First page + ellipsis
              if (startPage > 1) {
                pages.push(
                  <button
                    key={1}
                    onClick={() => changePage(1)}
                    disabled={isLoadingPage}
                    className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
                  >
                    1
                  </button>
                );
                if (startPage > 2) {
                  pages.push(<span key="start-ellipsis" className="px-2 text-gray-400">...</span>);
                }
              }

              // Main page numbers
              for (let i = startPage; i <= endPage; i++) {
                pages.push(
                  <button
                    key={i}
                    onClick={() => changePage(i)}
                    disabled={isLoadingPage}
                    className={`px-3 py-2 rounded-lg border transition-colors disabled:opacity-50 ${
                      i === currentPage
                        ? 'border-blue-500 bg-blue-500 text-white'
                        : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    {i}
                  </button>
                );
              }

              // Last page + ellipsis
              if (endPage < totalPages) {
                if (endPage < totalPages - 1) {
                  pages.push(<span key="end-ellipsis" className="px-2 text-gray-400">...</span>);
                }
                pages.push(
                  <button
                    key={totalPages}
                    onClick={() => changePage(totalPages)}
                    disabled={isLoadingPage}
                    className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
                  >
                    {totalPages}
                  </button>
                );
              }

              return pages;
            })()}
          </div>

          {/* Next Button */}
          <button
            onClick={() => changePage(currentPage + 1)}
            disabled={currentPage === totalPages || isLoadingPage}
            className={`flex items-center px-3 py-2 rounded-lg border transition-colors ${
              currentPage === totalPages || isLoadingPage
                ? 'border-gray-200 dark:border-gray-700 text-gray-400 dark:text-gray-600 cursor-not-allowed'
                : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            Next
            <ChevronRight className="w-4 h-4 ml-1" />
          </button>
        </div>
      </div>
    );
  };

  const updateFilters = (newFilters) => {
    console.log('🔥 updateFilters called with:', newFilters);
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
      {/* Desktop Hero Section - Dynamic width based on display mode */}
      <div 
        className={`hero-section relative text-white overflow-hidden ${
          heroContent.display_mode === 'full_width' ? 'w-screen' : 'w-full'
        }`}
        style={getHeroBackgroundStyle()}
      >
        <div className="absolute inset-0 bg-black/20"></div>
        
        <div className="relative z-10 text-center flex flex-col justify-center h-full px-8 max-w-7xl mx-auto">
          {/* Hero Image - displayed over text if image_url exists */}
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
            {heroContent.title || 'Discover Amazing Products'}
          </h1>
          <p className="text-xl mb-8 opacity-90 max-w-3xl mx-auto">
            {heroContent.description || 'From electronics to fashion, find everything you need in one place'}
          </p>
          
          {/* Hero Search Bar - Responsive width */}
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
          {/* Removed redundant results count since pagination shows "Showing X to Y of Z listings" */}
          {searchQuery && (
            <span className="text-lg font-semibold">
              Search results for "{searchQuery}"
            </span>
          )}
          
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

          {/* Hot Deals Quick Filter - REMOVED as requested by user */}

          {/* My Bids Quick Filter */}
          {user && (
            <button
              onClick={() => updateFilters({...filters, bidFilter: filters.bidFilter === 'placed_bid' ? 'all' : 'placed_bid'})}
              className={`flex items-center space-x-2 px-4 py-3 border rounded-xl transition-all duration-200 ${
                filters.bidFilter === 'placed_bid'
                  ? 'bg-blue-500 text-white border-blue-500 shadow-lg'
                  : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 hover:border-blue-300'
              }`}
            >
              <span className="text-sm">💰</span>
              <span className="hidden sm:inline">My Bids</span>
            </button>
          )}

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
            
            {/* NEW: Bid Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                My Activity
              </label>
              <select
                value={filters.bidFilter || 'all'}
                onChange={(e) => updateFilters({...filters, bidFilter: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white h-10 leading-none"
                disabled={!user}
              >
                <option value="all">All Listings</option>
                <option value="placed_bid">I Placed a Bid</option>
                <option value="not_placed_bid">I Haven't Bid Yet</option>
                <option value="own_listings">My Listings</option>
              </select>
              {!user && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Login to filter by your activity
                </p>
              )}
            </div>

            {/* NEW: Hot Deals Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Special Deals
              </label>
              <select
                value={filters.hotDeals || 'all'}
                onChange={(e) => updateFilters({...filters, hotDeals: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white h-10 leading-none"
              >
                <option value="all">All Items</option>
                <option value="expiring_soon">⏰ Expiring Soon (under 48h)</option>
                <option value="no_time_limit">♾️ No Time Limit</option>
              </select>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Find items ending soon for better deals
              </p>
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
            <div className="flex flex-col md:col-span-3">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Actions
              </label>
              <div className="flex space-x-4">
                <button
                  onClick={() => updateFilters({type: 'all', priceFrom: 0, priceTo: 10000, location: 'all', rating: 0, bidFilter: 'all', hotDeals: 'all'})}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors h-10"
                >
                  Clear All Filters
                </button>
                {user && (
                  <button
                    onClick={() => updateFilters({...filters, bidFilter: 'own_listings'})}
                    className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors h-10"
                  >
                    Show My Listings
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Products Grid/List */}
      <div className="mt-6">

      {/* Top Pagination Controls */}
      <PaginationControls showInfo={true} position="top" />

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
                  permissions={permissions}
                />
              ))}
            </div>
          </div>

          {/* Browse Page Advertisement */}
          {adsConfig?.browsePageAd?.active && (
            <div className="flex-shrink-0">
              <div 
                className={`bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm hover:shadow-md transition-all duration-200 ${
                  adsConfig.browsePageAd.url ? 'cursor-pointer hover:scale-[1.02]' : ''
                }`}
                style={{
                  width: adsConfig.browsePageAd.width || '300px',
                  height: adsConfig.browsePageAd.height || '600px'
                }}
                onClick={(e) => {
                  console.log('🔗 Ad clicked!');
                  console.log('🔗 Event details:', { 
                    target: e.target.tagName, 
                    currentTarget: e.currentTarget.tagName,
                    url: adsConfig.browsePageAd.url 
                  });
                  
                  if (adsConfig.browsePageAd.url) {
                    e.preventDefault(); // Prevent any default behavior
                    e.stopPropagation(); // Stop event from bubbling up
                    e.stopImmediatePropagation(); // Stop all other handlers
                    
                    console.log('🔗 Opening URL in new tab:', adsConfig.browsePageAd.url);
                    
                    // Track the click
                    trackAdClick('browsePageAd');
                    
                    // Force URL to open in new tab using multiple methods
                    try {
                      const newWindow = window.open(adsConfig.browsePageAd.url, '_blank', 'noopener,noreferrer');
                      if (newWindow) {
                        newWindow.focus();
                        console.log('✅ Successfully opened URL in new tab');
                      } else {
                        console.log('❌ Popup blocked - trying alternative method');
                        // Fallback: create temporary link and click it
                        const link = document.createElement('a');
                        link.href = adsConfig.browsePageAd.url;
                        link.target = '_blank';
                        link.rel = 'noopener noreferrer';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        console.log('✅ Opened URL using fallback method');
                      }
                    } catch (error) {
                      console.error('❌ Failed to open URL:', error);
                    }
                    
                    return false; // Ensure no further processing
                  } else {
                    console.log('🔗 No URL configured for ad');
                  }
                }}
              >
                {adsConfig.browsePageAd.image ? (
                  <div className="relative w-full h-full">
                    <img
                      src={adsConfig.browsePageAd.image}
                      alt={adsConfig.browsePageAd.description || 'Advertisement'}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        console.error('Ad image failed to load:', adsConfig.browsePageAd.image);
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                    {/* Fallback placeholder if image fails */}
                    <div className="absolute inset-0 flex-col items-center justify-center p-6 text-center hidden">
                      <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Monitor className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Advertisement Space</h3>
                      <p className="text-gray-600 dark:text-gray-400 text-sm">{adsConfig.browsePageAd.description}</p>
                    </div>
                    {/* REMOVED: Description overlay - show clean image only */}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center p-6 text-center h-full">
                    <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Monitor className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Advertisement Space</h3>
                    {adsConfig.browsePageAd.description ? (
                      <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">{adsConfig.browsePageAd.description}</p>
                    ) : (
                      <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">Your ad will appear here</p>
                    )}
                    <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
                      Runtime: {adsConfig.browsePageAd.runtime || '1 month'}
                    </div>
                    {adsConfig.browsePageAd.clicks > 0 && (
                      <div className="mt-2 text-xs text-blue-600 dark:text-blue-400">
                        {adsConfig.browsePageAd.clicks} clicks
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
      </div>

      {/* Bottom Pagination Controls */}
      <PaginationControls showInfo={true} position="bottom" />

      {/* Loading Overlay for Page Changes */}
      {isLoadingPage && (
        <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-40">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-xl flex items-center space-x-3">
            <RefreshCw className="w-5 h-5 animate-spin text-blue-500" />
            <span className="text-gray-700 dark:text-gray-300">Loading page {currentPage}...</span>
          </div>
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
      return `${hours}h ${minutes}m ${secs}s`;
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

// Simple helper functions

// Enhanced Product Card Component (used in JSX below)
function ProductCard({ item, viewMode, onSubmitTender, onFavoriteToggle, onMessageSeller, isInFavorites, isSubmittingTender, tenderConfirmation, priceRangeSettings, userActiveBids, user, permissions }) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  // Removed unused state
  const [priceSuggestion, setPriceSuggestion] = useState(null);
  const [loadingSuggestion, setLoadingSuggestion] = useState(false);
  const navigate = useNavigate();

  const isGridView = viewMode === 'grid';
  
  // Check if current user is the owner of this listing
  const isOwner = user && (
    item.seller?.username === user.username || 
    item.seller_id === user.id || 
    item.seller?.id === user.id
  );
  
  // User can place bid if they have permission AND are not the owner
  const canPlaceBid = permissions?.browse?.canPlaceBid && !isOwner;
  
  // Debug: Log ownership information for diagnosis 
  React.useEffect(() => {
    console.log(`🔍 ProductCard [${item.id?.slice(0, 8)}] - ${item.title}:`, {
      seller_username: item.seller?.username,
      seller_id: item.seller_id,
      user_username: user?.username,
      user_id: user?.id,
      isOwner: isOwner,
      canPlaceBid: canPlaceBid
    });
  }, [item.id, item.seller, item.seller_id, user?.username, user?.id, isOwner, canPlaceBid]);

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
      className={`product-card group bg-white dark:bg-gray-800 rounded-xl transition-all duration-300 overflow-hidden cursor-pointer ${
        // Partner listing border
        (() => {
          const { calculateTimeRemaining } = require('../../utils/timezone');
          const { expired } = calculateTimeRemaining(item.public_at);
          return item.is_partners_only && item.public_at && !expired
            ? 'border border-pink-600 shadow-lg shadow-pink-100 dark:shadow-pink-900/20' 
            : 'border border-gray-200 dark:border-gray-700';
        })()
      } ${
        isGridView ? 'hover:-translate-y-1 hover:shadow-xl' : 'flex space-x-4 p-4'
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
          
          {/* Partner Access Badge */}
          {item.show_partner_badge && item.visibility_reason === 'partner_access' && (
            <div>
              <span className="inline-flex items-center text-white text-xs px-2 py-1 rounded-full font-medium bg-gradient-to-r from-purple-600 to-pink-600 shadow-lg animate-pulse">
                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                </svg>
                Partner Only
              </span>
            </div>
          )}
        </div>

        {/* Partner Offer Badge - Bottom Left Position */}
        <div className="absolute bottom-2 left-2 z-20">
          {/* Combined Partner Offer Badge with Countdown */}
          {item.is_partners_only && item.public_at && (() => {
            // Import timezone utility functions
            const { formatPartnerTimeRemaining } = require('../../utils/timezone');
            const timeText = formatPartnerTimeRemaining(item.public_at);
            
            // Only show if time remaining is positive
            if (!timeText) return null;
            
            return (
              <div>
                <span className="inline-flex items-center text-white text-xs px-2 py-1 rounded-full font-medium bg-gradient-to-r from-purple-600 to-pink-600 shadow-lg">
                  <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                  </svg>
                  Partner Listing • {timeText}
                </span>
              </div>
            );
          })()}
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

        {/* Hot Deal Badge - Bottom Left Corner */}
        {(() => {
          const timeInfo = item.time_info;
          if (!timeInfo?.has_time_limit || timeInfo.is_expired) return null;
          
          const timeRemainingHours = timeInfo.time_remaining_seconds ? 
            timeInfo.time_remaining_seconds / 3600 : 0;
          
          if (timeRemainingHours > 0 && timeRemainingHours <= 24) {
            return (
              <div className="absolute bottom-2 left-2 bg-gradient-to-r from-red-500 to-orange-500 text-white text-xs px-3 py-1 rounded-full font-bold flex items-center z-20 shadow-lg animate-pulse">
                🔥 HOT DEAL
              </div>
            );
          } else if (timeRemainingHours > 24 && timeRemainingHours <= 48) {
            return (
              <div className="absolute bottom-2 left-2 bg-gradient-to-r from-yellow-500 to-orange-400 text-white text-xs px-3 py-1 rounded-full font-bold flex items-center z-20 shadow-lg">
                ⏰ ENDS SOON
              </div>
            );
          }
          
          return null;
        })()}
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

        {/* 6. Time Left - Always show for consistency */}
        <div className="mb-3">
          <div className={`relative overflow-hidden rounded-xl border-2 ${
            item.time_info?.has_time_limit
              ? item.time_info.is_expired 
                ? 'border-red-200 dark:border-red-800 bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/30'
                : item.time_info.time_remaining_seconds <= 3600
                  ? 'border-red-200 dark:border-red-800 bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/30'
                  : item.time_info.time_remaining_seconds <= 21600
                    ? 'border-orange-200 dark:border-orange-800 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/30'
                    : item.time_info.time_remaining_seconds <= 86400
                      ? 'border-yellow-200 dark:border-yellow-800 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/30'
                      : 'border-green-200 dark:border-green-800 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/30'
              : 'border-green-200 dark:border-green-800 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/30'
          }`}>
            <div className={`absolute top-0 right-0 w-12 h-12 rounded-bl-full ${
              item.time_info?.has_time_limit
                ? item.time_info.is_expired || item.time_info.time_remaining_seconds <= 3600
                  ? 'bg-gradient-to-bl from-red-200/20 to-transparent dark:from-red-600/10'
                  : item.time_info.time_remaining_seconds <= 21600
                    ? 'bg-gradient-to-bl from-orange-200/20 to-transparent dark:from-orange-600/10'
                    : item.time_info.time_remaining_seconds <= 86400
                      ? 'bg-gradient-to-bl from-yellow-200/20 to-transparent dark:from-yellow-600/10'
                      : 'bg-gradient-to-bl from-green-200/20 to-transparent dark:from-green-600/10'
                : 'bg-gradient-to-bl from-green-200/20 to-transparent dark:from-green-600/10'
            }`}></div>
            <div className="relative p-3">
              <div className="flex items-center space-x-2">
                <div className={`p-1.5 rounded-lg shadow-sm ${
                  item.time_info?.has_time_limit
                    ? item.time_info.is_expired || item.time_info.time_remaining_seconds <= 3600
                      ? 'bg-gradient-to-r from-red-500 to-red-600'
                      : item.time_info.time_remaining_seconds <= 21600
                        ? 'bg-gradient-to-r from-orange-500 to-orange-600'
                        : item.time_info.time_remaining_seconds <= 86400
                          ? 'bg-gradient-to-r from-yellow-500 to-yellow-600'
                          : 'bg-gradient-to-r from-green-500 to-green-600'
                    : 'bg-gradient-to-r from-green-500 to-green-600'
                }`}>
                  <Clock className="w-3 h-3 text-white" />
                </div>
                <div>
                  <div className={`text-xs font-medium uppercase tracking-wide ${
                    item.time_info?.has_time_limit
                      ? item.time_info.is_expired || item.time_info.time_remaining_seconds <= 3600
                        ? 'text-red-700 dark:text-red-300'
                        : item.time_info.time_remaining_seconds <= 21600
                          ? 'text-orange-700 dark:text-orange-300'
                          : item.time_info.time_remaining_seconds <= 86400
                            ? 'text-yellow-700 dark:text-yellow-300'
                            : 'text-green-700 dark:text-green-300'
                      : 'text-green-700 dark:text-green-300'
                  }`}>
                    {item.time_info?.has_time_limit 
                      ? (item.time_info.is_expired ? 'Expired' : 'Time Left')
                      : 'Without Time Limit'
                    }
                  </div>
                  <div className={`text-sm font-bold leading-tight ${
                    item.time_info?.has_time_limit
                      ? item.time_info.is_expired || item.time_info.time_remaining_seconds <= 3600
                        ? 'text-red-900 dark:text-red-100'
                        : item.time_info.time_remaining_seconds <= 21600
                          ? 'text-orange-900 dark:text-orange-100'
                          : item.time_info.time_remaining_seconds <= 86400
                            ? 'text-yellow-900 dark:text-yellow-100'
                            : 'text-green-900 dark:text-green-100'
                      : 'text-green-900 dark:text-green-100'
                  }`}>
                    {item.time_info?.has_time_limit 
                      ? <CountdownTimer timeInfo={item.time_info} />
                      : 'Always Available'
                    }
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

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
          
          {/* Bidding Controls - Role-based access with owner check */}
          {canPlaceBid ? (
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
          ) : isOwner ? (
            /* Show owner message */
            <div className="mt-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <span className="text-sm font-medium text-yellow-700 dark:text-yellow-300">
                  Your Listing - Bidding Disabled
                </span>
              </div>
              <p className="text-xs text-yellow-600 dark:text-yellow-400">
                You cannot bid on your own listing.
              </p>
              {/* Show bid info for owners */}
              <div className="mt-2 flex items-center justify-between text-sm">
                <span className="text-yellow-600 dark:text-yellow-400">Current highest bid:</span>
                <span className="font-semibold text-yellow-900 dark:text-yellow-100">
                  €{(item.bid_info?.highest_bid || item.price || 0).toFixed(2)}
                </span>
              </div>
            </div>
          ) : (
            /* Show disabled bidding interface for sellers with explanation */
            <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Seller Account - Bidding Disabled
                </span>
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Seller accounts can view all bid information but cannot place bids. Switch to a buyer account to participate in bidding.
              </p>
              {/* Show bid info for sellers */}
              <div className="mt-2 flex items-center justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Current highest bid:</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  €{(item.bid_info?.highest_bid || item.price || 0).toFixed(2)}
                </span>
              </div>
            </div>
          )}
          
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