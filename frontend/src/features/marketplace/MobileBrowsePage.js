/**
 * CATALORO - Mobile Browse Page (SIMPLIFIED FOR SPEED)
 * Optimized mobile marketplace browsing without complex context dependencies
 */

import React, { useState, useEffect } from 'react';
import { Search, Filter, TrendingUp, Package, Clock, DollarSign } from 'lucide-react';
import MobileHeroSection from '../../components/mobile/MobileHeroSection';
import MobileListingCard from '../../components/mobile/MobileListingCard';
import MobileFilters from '../../components/mobile/MobileFilters';

function MobileBrowsePage() {
  // Simple local state - no complex context
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isMobileFiltersOpen, setIsMobileFiltersOpen] = useState(false);
  const [filters, setFilters] = useState({
    category: '',
    priceRange: { min: 0, max: 1000 },
    location: '',
    condition: '',
    dateRange: '',
    rating: 0,
    sortBy: 'newest'
  });
  const [filteredListings, setFilteredListings] = useState([]);
  const [quickStats, setQuickStats] = useState({
    totalListings: 0,
    newToday: 0,
    hotDeals: 0,
    avgPrice: 0
  });

  // Simple, direct API call - no context complexity
  const loadListings = async () => {
    try {
      setLoading(true);
      console.log('📱 Mobile browse: Loading listings directly from API');
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/marketplace/browse`);
      if (!response.ok) throw new Error('Failed to fetch');
      
      const data = await response.json();
      console.log('📱 Mobile browse: Loaded', data.length, 'listings');
      
      setListings(data);
      
      // Calculate quick stats
      const stats = {
        totalListings: data.length,
        newToday: data.filter(item => {
          const createdDate = new Date(item.created_at);
          const today = new Date();
          return createdDate.toDateString() === today.toDateString();
        }).length,
        hotDeals: data.filter(item => item.isHotDeal || item.discount > 0).length,
        avgPrice: data.length > 0 
          ? Math.round(data.reduce((sum, item) => sum + (item.price || 0), 0) / data.length)
          : 0
      };
      setQuickStats(stats);
      
    } catch (error) {
      console.error('❌ Mobile browse: Error loading listings:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load listings on component mount - ONLY ONCE
  useEffect(() => {
    loadListings();
  }, []);

  // Apply filters when listings change
  useEffect(() => {
    if (listings.length > 0) {
      applyFilters(listings, searchTerm, filters);
    }
  }, [listings]);

  const handleSearch = (term) => {
    setSearchTerm(term);
    applyFilters(listings, term, filters);
  };

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
    applyFilters(listings, searchTerm, newFilters);
  };

  const applyFilters = (allListings, searchTerm, activeFilters) => {
    let filtered = [...allListings];

    // Search filter
    if (searchTerm && searchTerm.trim()) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(listing => 
        listing.title?.toLowerCase().includes(searchLower) ||
        listing.description?.toLowerCase().includes(searchLower) ||
        listing.seller?.username?.toLowerCase().includes(searchLower)
      );
    }

    // Price range filter
    if (activeFilters.priceRange && activeFilters.priceRange.min > 0 || activeFilters.priceRange.max < 1000) {
      filtered = filtered.filter(listing => {
        const price = listing.price || 0;
        return price >= activeFilters.priceRange.min && price <= activeFilters.priceRange.max;
      });
    }

    // Category filter
    if (activeFilters.category && activeFilters.category !== '') {
      filtered = filtered.filter(listing => 
        listing.category?.toLowerCase() === activeFilters.category.toLowerCase()
      );
    }

    // Condition filter
    if (activeFilters.condition && activeFilters.condition !== '') {
      filtered = filtered.filter(listing => 
        listing.condition?.toLowerCase() === activeFilters.condition.toLowerCase()
      );
    }

    // Sort results
    switch (activeFilters.sortBy) {
      case 'price_low':
        filtered.sort((a, b) => (a.price || 0) - (b.price || 0));
        break;
      case 'price_high':
        filtered.sort((a, b) => (b.price || 0) - (a.price || 0));
        break;
      case 'newest':
        filtered.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
        break;
      case 'oldest':
        filtered.sort((a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0));
        break;
      default:
        // Keep original order
        break;
    }

    setFilteredListings(filtered);
  };

  const handleBidUpdate = (listingId, updatedListing) => {
    // Update the specific listing in the listings array
    setListings(prevListings => 
      prevListings.map(listing => 
        listing.id === listingId ? updatedListing : listing
      )
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading listings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
      {/* Hero Section */}
      <MobileHeroSection 
        quickStats={quickStats}
        onSearch={handleSearch}
        onFilterToggle={() => setIsMobileFiltersOpen(true)}
        searchTerm={searchTerm}
      />



      {/* Stats Bar */}
      <div className="px-4 mb-6">
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl text-white p-4">
          <div className="grid grid-cols-4 gap-4 text-center">
            <div>
              <Package className="w-5 h-5 mx-auto mb-1 opacity-80" />
              <div className="text-lg font-bold">{quickStats.totalListings}</div>
              <div className="text-xs opacity-80">Total</div>
            </div>
            <div>
              <Clock className="w-5 h-5 mx-auto mb-1 opacity-80" />
              <div className="text-lg font-bold">{quickStats.newToday}</div>
              <div className="text-xs opacity-80">New Today</div>
            </div>
            <div>
              <TrendingUp className="w-5 h-5 mx-auto mb-1 opacity-80" />
              <div className="text-lg font-bold">{quickStats.hotDeals}</div>
              <div className="text-xs opacity-80">Hot Deals</div>
            </div>
            <div>
              <DollarSign className="w-5 h-5 mx-auto mb-1 opacity-80" />
              <div className="text-lg font-bold">€{quickStats.avgPrice}</div>
              <div className="text-xs opacity-80">Avg Price</div>
            </div>
          </div>
        </div>
      </div>

      {/* Listings Grid */}
      <div className="px-4">
        {filteredListings.length === 0 ? (
          <div className="text-center py-12">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              No listings found
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              {searchTerm ? 'Try adjusting your search terms' : 'Be the first to list an item!'}
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {filteredListings.map((listing) => (
              <MobileListingCard 
                key={listing.id} 
                listing={listing} 
                onBidUpdate={handleBidUpdate}
              />
            ))}
          </div>
        )}
      </div>

      {/* Mobile Filters Modal */}
      {isMobileFiltersOpen && (
        <MobileFilters 
          onClose={() => setIsMobileFiltersOpen(false)}
          onApplyFilters={(newFilters) => {
            handleFiltersChange(newFilters);
            setIsMobileFiltersOpen(false);
          }}
        />
      )}
    </div>
  );
}

export default MobileBrowsePage;