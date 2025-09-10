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

  // Simple search filtering
  const filteredListings = listings.filter(listing =>
    listing.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    listing.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSearch = (query) => {
    setSearchTerm(query);
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
        searchTerm={searchTerm}
      />

      {/* Quick Actions */}
      <div className="px-4 -mt-6 relative z-10">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search listings..."
                  value={searchTerm}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-gray-100 dark:bg-gray-700 border-0 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:bg-white dark:focus:bg-gray-600"
                />
              </div>
            </div>
            <button
              onClick={() => setIsMobileFiltersOpen(true)}
              className="ml-3 p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Filter className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

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
          onApplyFilters={(filters) => {
            // Simple client-side filtering for now
            setIsMobileFiltersOpen(false);
          }}
        />
      )}
    </div>
  );
}

export default MobileBrowsePage;