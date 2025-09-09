/**
 * CATALORO - Mobile Browse Page
 * Optimized mobile marketplace experience
 */

import React, { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import { useMarketplace } from '../../context/MarketplaceContext';
import { useNotifications } from '../../context/NotificationContext';

// Mobile Components
import MobileHeroSection from '../../components/mobile/MobileHeroSection';
import MobileFilters from '../../components/mobile/MobileFilters';
import MobileListingCard from '../../components/mobile/MobileListingCard';

function MobileBrowsePage() {
  // Core marketplace state
  const { 
    filteredProducts,
    globalSearchQuery,
    globalFilters,
    isLoading,
    refreshListings,
    searchListings,
    updateFilters,
    updateGlobalSearchQuery
  } = useMarketplace();
  
  const { showToast } = useNotifications();

  // Mobile-specific state
  const [isMobileFiltersOpen, setIsMobileFiltersOpen] = useState(false);
  const [quickStats, setQuickStats] = useState({});

  // Load quick stats for mobile hero
  useEffect(() => {
    const calculateQuickStats = () => {
      const stats = {
        totalListings: filteredProducts.length,
        newToday: filteredProducts.filter(item => {
          const createdDate = new Date(item.created_at);
          const today = new Date();
          return createdDate.toDateString() === today.toDateString();
        }).length,
        hotDeals: filteredProducts.filter(item => item.isHotDeal || item.discount > 0).length,
        avgPrice: filteredProducts.length > 0 
          ? Math.round(filteredProducts.reduce((sum, item) => sum + (item.price || 0), 0) / filteredProducts.length)
          : 0
      };
      setQuickStats(stats);
    };

    calculateQuickStats();
  }, [filteredProducts]);

  // Mobile event handlers
  const handleMobileSearch = (query) => {
    updateGlobalSearchQuery(query);
    searchListings(query);
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
        // Add to favorites logic
        showToast('Added to favorites', 'success');
      } else {
        // Remove from favorites logic
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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading catalysts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mobile-container">
      {/* Mobile Hero Section */}
      <MobileHeroSection
        onSearch={handleMobileSearch}
        onFilterToggle={handleMobileFiltersToggle}
        quickStats={quickStats}
      />

      {/* Mobile Filters */}
      <MobileFilters
        isOpen={isMobileFiltersOpen}
        onClose={() => setIsMobileFiltersOpen(false)}
        filters={globalFilters}
        onFiltersChange={handleMobileFiltersChange}
        availableFilters={{
          categories: ['Catalytic Converters', 'Diesel Particulate Filters', 'Ceramic Catalysts'],
          locations: ['Germany', 'France', 'United Kingdom', 'Netherlands'],
          conditions: ['New', 'Like New', 'Good', 'Fair', 'Used']
        }}
      />

      {/* Mobile Listings */}
      <div className="px-4 pb-20">
        {filteredProducts.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="mobile-title text-gray-900 dark:text-white mb-2">
              No catalysts found
            </h3>
            <p className="mobile-body text-gray-500 dark:text-gray-400">
              Try adjusting your search or filters
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredProducts.map((listing) => (
              <MobileListingCard
                key={listing.id}
                listing={listing}
                onFavorite={handleMobileFavorite}
                onContact={handleMobileContact}
                onQuickView={handleMobileQuickView}
              />
            ))}
          </div>
        )}

        {/* Load More Button for Mobile */}
        {filteredProducts.length > 0 && filteredProducts.length % 10 === 0 && (
          <div className="mt-6 text-center">
            <button className="mobile-button bg-blue-600 text-white hover:bg-blue-700 transition-colors">
              Load More Results
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default MobileBrowsePage;