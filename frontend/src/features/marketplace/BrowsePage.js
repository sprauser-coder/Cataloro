/**
 * CATALORO - Catalyst Database Browse Page
 * Browse and search chemical catalysts with hero-style interface
 */

import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Grid3X3, 
  List, 
  Heart, 
  SlidersHorizontal,
  X
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { marketplaceService } from '../../services/marketplaceService';
import { useNotifications } from '../../context/NotificationContext';
import { useAuth } from '../../context/AuthContext';
import { liveService } from '../../services/liveService';

function BrowsePage() {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [sortBy, setSortBy] = useState('newest');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    category: 'all',
    priceRange: 'all',
    condition: 'all',
    location: 'all'
  });
  
  // Message modal state
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [messageContent, setMessageContent] = useState('');
  const [sending, setSending] = useState(false);
  
  const { showToast } = useNotifications();
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchListings();
  }, []);

  const fetchListings = async () => {
    try {
      setLoading(true);
      const data = await marketplaceService.browseListings();
      setListings(Array.isArray(data) ? data : []);
    } catch (error) {
      showToast('Failed to load catalysts', 'error');
      console.error('Failed to fetch listings:', error);
      setListings([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      category: 'all',
      priceRange: 'all', 
      condition: 'all',
      location: 'all'
    });
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
    setMessageContent(`Hi! I'm interested in your catalyst "${item.title}". Is it still available?`);
    setShowMessageModal(true);
  };

  // Send message
  const sendMessage = async () => {
    if (!messageContent.trim()) return;
    
    setSending(true);
    try {
      await liveService.sendMessage(
        user.id,
        selectedProduct.seller_id,
        messageContent.trim(),
        'text',
        { listing_id: selectedProduct.id, listing_title: selectedProduct.title }
      );
      
      showToast('Message sent successfully!', 'success');
      setShowMessageModal(false);
      setMessageContent('');
      setSelectedProduct(null);
    } catch (error) {
      console.error('Failed to send message:', error);
      showToast('Failed to send message', 'error');
    } finally {
      setSending(false);
    }
  };

  const handleAddToFavorites = async (listingId) => {
    try {
      // Implementation for adding to favorites
      showToast('Added to favorites', 'success');
    } catch (error) {
      showToast('Failed to add to favorites', 'error');
    }
  };

  // Filter and sort listings
  const filteredListings = listings.filter(listing => {
    const matchesSearch = !searchQuery || 
      listing.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      listing.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesCategory = filters.category === 'all' || listing.category === filters.category;
    const matchesCondition = filters.condition === 'all' || listing.condition === filters.condition;
    
    return matchesSearch && matchesCategory && matchesCondition;
  });

  const sortedListings = [...filteredListings].sort((a, b) => {
    switch (sortBy) {
      case 'price_low':
        return (a.price || 0) - (b.price || 0);
      case 'price_high':
        return (b.price || 0) - (a.price || 0);
      case 'newest':
      default:
        return new Date(b.created_at || Date.now()) - new Date(a.created_at || Date.now());
    }
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      {/* Hero Search Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-700 text-white rounded-2xl p-8 mb-8">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl font-bold mb-4">Chemical Catalyst Database</h1>
          <p className="text-xl text-blue-100 mb-8">
            Discover high-performance catalysts for your chemical processes
          </p>
          
          {/* Hero Search Bar */}
          <div className="relative max-w-2xl mx-auto mb-6">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-6 w-6 text-gray-400" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearch}
              placeholder="Search by catalyst name, metal type, or reaction..."
              className="block w-full pl-12 pr-4 py-4 text-lg border-0 rounded-xl bg-white/90 backdrop-blur-sm shadow-lg focus:ring-4 focus:ring-white/30 focus:bg-white transition-all duration-200 text-gray-900 placeholder-gray-500"
            />
          </div>
          
          {/* Quick Filter Chips */}
          <div className="flex flex-wrap justify-center gap-3">
            <button 
              onClick={() => setSearchQuery('platinum')}
              className="px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full text-sm font-medium hover:bg-white/30 transition-all duration-200"
            >
              Platinum Catalysts
            </button>
            <button 
              onClick={() => setSearchQuery('hydrogenation')}
              className="px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full text-sm font-medium hover:bg-white/30 transition-all duration-200"
            >
              Hydrogenation
            </button>
            <button 
              onClick={() => setSearchQuery('oxidation')}
              className="px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full text-sm font-medium hover:bg-white/30 transition-all duration-200"
            >
              Oxidation
            </button>
            <button 
              onClick={() => setSearchQuery('zeolite')}
              className="px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full text-sm font-medium hover:bg-white/30 transition-all duration-200"
            >
              Zeolites
            </button>
          </div>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          {/* Filter Toggle */}
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-all duration-200"
            >
              <SlidersHorizontal className="w-4 h-4 mr-2" />
              Filters
              {(filters.category !== 'all' || filters.condition !== 'all') && (
                <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                  Active
                </span>
              )}
            </button>
            
            {(filters.category !== 'all' || filters.condition !== 'all') && (
              <button
                onClick={clearFilters}
                className="text-sm text-gray-600 hover:text-gray-800 flex items-center"
              >
                <X className="w-4 h-4 mr-1" />
                Clear All
              </button>
            )}
          </div>

          {/* Results and Controls */}
          <div className="flex items-center space-x-4">
            <p className="text-gray-600">
              {sortedListings.length} catalysts found
            </p>
            
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="newest">Newest First</option>
              <option value="price_low">Price: Low to High</option>
              <option value="price_high">Price: High to Low</option>
            </select>

            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-md transition-all duration-200 ${
                  viewMode === 'grid' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-600'
                }`}
              >
                <Grid3X3 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-md transition-all duration-200 ${
                  viewMode === 'list' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-600'
                }`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Expandable Filters */}
        {showFilters && (
          <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4 pt-6 border-t border-gray-200">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Categories</option>
                <option value="catalysts">Catalysts</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Condition</label>
              <select
                value={filters.condition}
                onChange={(e) => handleFilterChange('condition', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">Any Condition</option>
                <option value="new">New</option>
                <option value="used">Used</option>
                <option value="refurbished">Refurbished</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Price Range</label>
              <select
                value={filters.priceRange}
                onChange={(e) => handleFilterChange('priceRange', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">Any Price</option>
                <option value="0-100">Under $100</option>
                <option value="100-500">$100 - $500</option>
                <option value="500-1000">$500 - $1,000</option>
                <option value="1000+">Over $1,000</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
              <select
                value={filters.location}
                onChange={(e) => handleFilterChange('location', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">Any Location</option>
                <option value="local">Local Only</option>
                <option value="nationwide">Nationwide</option>
                <option value="international">International</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Listings Grid/List */}
      {sortedListings.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No listings found</h3>
          <p className="text-gray-600">
            {searchQuery ? 'Try adjusting your search terms' : 'Be the first to create a listing!'}
          </p>
        </div>
      ) : (
        <div className={viewMode === 'grid' ? 'listings-grid' : 'space-y-4'}>
          {sortedListings.map((listing) => (
            <ListingCard
              key={listing.id}
              listing={listing}
              viewMode={viewMode}
              onAddToFavorites={handleAddToFavorites}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Listing Card Component
function ListingCard({ listing, viewMode, onAddToFavorites }) {
  const isGridView = viewMode === 'grid';

  return (
    <div className={isGridView ? 'listing-tile' : 'cataloro-card p-4 flex space-x-4'}>
      {/* Image */}
      <div className={isGridView ? '' : 'w-32 h-32 flex-shrink-0'}>
        <img
          src={listing.images?.[0] || '/api/placeholder/400/300'}
          alt={listing.title}
          className={isGridView ? 'listing-image' : 'w-full h-full object-cover rounded-lg'}
        />
      </div>

      {/* Content */}
      <div className={isGridView ? 'listing-content' : 'flex-1 min-w-0'}>
        <div className="flex justify-between items-start mb-2">
          <h3 className={isGridView ? 'listing-title' : 'font-semibold text-lg text-gray-900'}>
            {listing.title}
          </h3>
          <button
            onClick={() => onAddToFavorites(listing.id)}
            className="text-gray-400 hover:text-red-500 transition-colors duration-200"
          >
            <Heart className="w-5 h-5" />
          </button>
        </div>

        <p className={isGridView ? 'listing-price' : 'text-2xl font-bold text-blue-600 mb-2'}>
          ${listing.price.toFixed(2)}
        </p>

        <p className={isGridView ? 'listing-description' : 'text-gray-600 mb-4'}>
          {listing.description}
        </p>

        {!isGridView && (
          <div className="flex items-center justify-between">
            <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
              {listing.category}
            </span>
            <span className="text-sm text-gray-500">
              {new Date(listing.created_at).toLocaleDateString()}
            </span>
          </div>
        )}

        {isGridView && (
          <div className="flex items-center justify-between mt-4">
            <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
              {listing.category}
            </span>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
              View Details
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default BrowsePage;