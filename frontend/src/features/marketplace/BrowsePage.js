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
  RefreshCw,
  Filter
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
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
  const [filters, setFilters] = useState({});
  const [totalCount, setTotalCount] = useState(0);
  const [searchMode, setSearchMode] = useState('standard'); // 'standard' or 'ai'
  const [searchIntent, setSearchIntent] = useState({});
  const [showRecommendations, setShowRecommendations] = useState(true);
  
  const { showToast } = useNotifications();
  const { user } = useAuth();

  useEffect(() => {
    fetchListings();
  }, []);

  useEffect(() => {
    if (searchQuery || Object.keys(filters).length > 0) {
      performSearch();
    } else {
      fetchListings();
    }
  }, [filters, sortBy]);

  const fetchListings = async () => {
    try {
      setLoading(true);
      const data = await marketplaceService.browseListings();
      setListings(Array.isArray(data) ? data : []);
      setTotalCount(Array.isArray(data) ? data.length : 0);
      setShowRecommendations((!searchQuery && Object.keys(filters).length === 0));
    } catch (error) {
      showToast('Failed to load listings', 'error');
      console.error('Failed to fetch listings:', error);
      setListings([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  };

  const performSearch = async (query = searchQuery, useAI = false) => {
    try {
      setLoading(true);
      setShowRecommendations(false);
      
      if (useAI && query && query.length >= 2) {
        // Use AI-powered intelligent search
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/search/intelligent`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: query,
            filters: filters,
            limit: 20
          })
        });

        if (response.ok) {
          const data = await response.json();
          setListings(data.results || []);
          setTotalCount(data.total || 0);
          setSearchIntent(data.search_intent || {});
          setSearchMode('ai');
          
          // Save search history if user is logged in
          if (user?.id) {
            await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/search/save-history`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                user_id: user.id,
                query: query,
                results_count: data.total || 0
              })
            });
          }
          
          showToast(`Found ${data.total || 0} catalysts with AI search`, 'success');
          return;
        }
      }
      
      // Fallback to standard search
      setSearchMode('standard');
      const data = await marketplaceService.browseListings(filters);
      const filteredData = Array.isArray(data) ? data.filter(item => 
        !query || 
        item.title.toLowerCase().includes(query.toLowerCase()) ||
        item.description.toLowerCase().includes(query.toLowerCase()) ||
        item.category.toLowerCase().includes(query.toLowerCase())
      ) : [];
      
      setListings(filteredData);
      setTotalCount(filteredData.length);
      
    } catch (error) {
      showToast('Search failed', 'error');
      console.error('Search failed:', error);
      setListings([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (query, useAI = true) => {
    setSearchQuery(query);
    performSearch(query, useAI);
  };

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleAddToFavorites = async (listingId) => {
    try {
      // Implementation for adding to favorites
      showToast('Added to favorites', 'success');
    } catch (error) {
      showToast('Failed to add to favorites', 'error');
    }
  };

  const sortedListings = [...listings].sort((a, b) => {
    switch (sortBy) {
      case 'price_low':
        return (a.price || 0) - (b.price || 0);
      case 'price_high':
        return (b.price || 0) - (a.price || 0);
      case 'popular':
        return (b.views || 0) - (a.views || 0);
      case 'rating':
        return (b.rating || 0) - (a.rating || 0);
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
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Catalyst Database</h1>
            <p className="text-gray-600">Find chemical catalysts with AI-powered technical search</p>
          </div>
          
          {searchMode === 'ai' && (
            <div className="hidden md:flex items-center px-3 py-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
              <Sparkles className="h-4 w-4 text-white mr-2" />
              <span className="text-white text-sm font-medium">AI Search Active</span>
            </div>
          )}
        </div>
      </div>

      {/* Smart Search Bar */}
      <div className="mb-6">
        <SmartSearchBar
          onSearch={handleSearch}
          placeholder="Search catalysts by metal, reaction type, or application..."
          className="max-w-2xl"
        />
      </div>

      {/* Advanced Filters and Controls */}
      <div className="cataloro-card p-6 mb-8">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          {/* Advanced Filters */}
          <div className="flex-1">
            <AdvancedFilters
              onFiltersChange={handleFiltersChange}
              initialFilters={filters}
            />
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-4">
            {/* Sort Dropdown */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="cataloro-input w-auto"
            >
              <option value="newest">Newest First</option>
              <option value="price_low">Price: Low to High</option>
              <option value="price_high">Price: High to Low</option>
              <option value="popular">Most Popular</option>
              <option value="rating">Highest Rated</option>
            </select>

            {/* View Mode Toggle */}
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-md transition-all duration-200 ${
                  viewMode === 'grid' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-600'
                }`}
              >
                <Grid className="w-4 h-4" />
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
      </div>

      {/* Search Intent & Results Info */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-600">
              Showing {totalCount} catalysts
              {searchQuery && ` for "${searchQuery}"`}
              {searchMode === 'ai' && searchIntent.enhanced_query && searchIntent.enhanced_query !== searchQuery && (
                <span className="ml-2 text-blue-600 text-sm">
                  • Enhanced: "{searchIntent.enhanced_query}"
                </span>
              )}
            </p>
            
            {searchMode === 'ai' && searchIntent.metal_type && (
              <p className="text-sm text-blue-600 mt-1">
                <Sparkles className="h-3 w-3 inline mr-1" />
                AI detected metal: {searchIntent.metal_type}
                {searchIntent.reaction_type && ` • Reaction: ${searchIntent.reaction_type}`}
              </p>
            )}
          </div>
          
          {searchQuery && (
            <button
              onClick={() => {
                setSearchQuery('');
                setSearchMode('standard');
                fetchListings();
              }}
              className="text-sm text-gray-500 hover:text-gray-700 transition-colors duration-200"
            >
              Clear Search
            </button>
          )}
        </div>
      </div>

      {/* Recommendations Panel - Show when no search/filters active */}
      {showRecommendations && (
        <div className="mb-8">
          <RecommendationsPanel limit={6} />
        </div>
      )}

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