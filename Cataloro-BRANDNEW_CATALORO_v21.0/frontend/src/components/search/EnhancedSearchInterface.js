import React, { useState, useEffect, useCallback } from 'react';
import { debounce } from 'lodash';

const EnhancedSearchInterface = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [trendingSearches, setTrendingSearches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  // Advanced filters
  const [filters, setFilters] = useState({
    category: '',
    price_min: '',
    price_max: '',
    condition: '',
    seller_type: '',
    sort_by: 'relevance'
  });

  const [currentPage, setCurrentPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const resultsPerPage = 20;

  useEffect(() => {
    fetchTrendingSearches();
  }, []);

  useEffect(() => {
    if (searchQuery.trim()) {
      performSearch();
      debouncedGetSuggestions(searchQuery);
    } else {
      setSearchResults([]);
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [searchQuery, filters, currentPage]);

  const debouncedGetSuggestions = useCallback(
    debounce(async (query) => {
      if (query.length < 2) return;
      
      try {
        const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
        const response = await fetch(`${backendUrl}/api/marketplace/search/suggestions?q=${encodeURIComponent(query)}&limit=5`);
        const data = await response.json();
        setSuggestions(data.suggestions || []);
        setShowSuggestions(true);
      } catch (error) {
        console.error('Failed to fetch suggestions:', error);
      }
    }, 300),
    []
  );

  const fetchTrendingSearches = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/marketplace/search/trending?limit=10`);
      const data = await response.json();
      setTrendingSearches(data.trending || []);
    } catch (error) {
      console.error('Failed to fetch trending searches:', error);
    }
  };

  const performSearch = async () => {
    if (!searchQuery.trim() && !Object.values(filters).some(v => v)) return;

    setLoading(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      const params = new URLSearchParams({
        q: searchQuery,
        page: currentPage.toString(),
        limit: resultsPerPage.toString(),
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v))
      });

      const response = await fetch(`${backendUrl}/api/marketplace/search?${params}`);
      const data = await response.json();
      
      setSearchResults(data.results || []);
      setTotalResults(data.total || 0);
      setShowSuggestions(false);
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setSearchQuery(suggestion);
    setShowSuggestions(false);
    setCurrentPage(1);
  };

  const handleTrendingClick = (trending) => {
    setSearchQuery(trending.query);
    setCurrentPage(1);
  };

  const handleFilterChange = (filterKey, value) => {
    setFilters(prev => ({ ...prev, [filterKey]: value }));
    setCurrentPage(1);
  };

  const clearFilters = () => {
    setFilters({
      category: '',
      price_min: '',
      price_max: '',
      condition: '',
      seller_type: '',
      sort_by: 'relevance'
    });
    setCurrentPage(1);
  };

  const getSimilarListings = async (listingId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/marketplace/listings/${listingId}/similar?limit=3`);
      const data = await response.json();
      return data.similar_listings || [];
    } catch (error) {
      console.error('Failed to fetch similar listings:', error);
      return [];
    }
  };

  const renderSearchResults = () => {
    if (loading) {
      return (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Searching...</p>
        </div>
      );
    }

    if (searchResults.length === 0) {
      return (
        <div className="text-center py-12">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
          <p className="text-gray-600">Try adjusting your search terms or filters</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {searchResults.map((listing) => (
          <SearchResultCard key={listing.id} listing={listing} getSimilarListings={getSimilarListings} />
        ))}
      </div>
    );
  };

  const totalPages = Math.ceil(totalResults / resultsPerPage);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Advanced Search</h1>
          <p className="text-gray-600 mt-2">
            Enhanced search with intelligent suggestions and advanced filtering
          </p>
        </div>

        {/* Search Interface */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          {/* Main Search Bar */}
          <div className="relative mb-6">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for catalysts, vehicles, parts..."
                className="w-full px-4 py-3 pl-10 pr-4 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>

            {/* Search Suggestions */}
            {showSuggestions && suggestions.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
                {suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="w-full px-4 py-2 text-left hover:bg-gray-100 first:rounded-t-lg last:rounded-b-lg"
                  >
                    <div className="flex items-center">
                      <svg className="h-4 w-4 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                      {suggestion}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Advanced Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-4">
            <select
              value={filters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Categories</option>
              <option value="automotive">Automotive</option>
              <option value="industrial">Industrial</option>
              <option value="marine">Marine</option>
              <option value="motorcycle">Motorcycle</option>
            </select>

            <input
              type="number"
              value={filters.price_min}
              onChange={(e) => handleFilterChange('price_min', e.target.value)}
              placeholder="Min Price (€)"
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />

            <input
              type="number"
              value={filters.price_max}
              onChange={(e) => handleFilterChange('price_max', e.target.value)}
              placeholder="Max Price (€)"
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />

            <select
              value={filters.condition}
              onChange={(e) => handleFilterChange('condition', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Any Condition</option>
              <option value="new">New</option>
              <option value="used">Used</option>
              <option value="refurbished">Refurbished</option>
            </select>

            <select
              value={filters.seller_type}
              onChange={(e) => handleFilterChange('seller_type', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Any Seller</option>
              <option value="Business">Business</option>
              <option value="Private">Private</option>
            </select>

            <select
              value={filters.sort_by}
              onChange={(e) => handleFilterChange('sort_by', e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="relevance">Relevance</option>
              <option value="price_low">Price: Low to High</option>
              <option value="price_high">Price: High to Low</option>
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
            </select>
          </div>

          {/* Filter Actions */}
          <div className="flex items-center justify-between">
            <button
              onClick={clearFilters}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Clear all filters
            </button>
            <div className="text-sm text-gray-600">
              {totalResults} results found
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            {/* Trending Searches */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Trending Searches</h3>
              <div className="space-y-2">
                {trendingSearches.map((trending, index) => (
                  <button
                    key={index}
                    onClick={() => handleTrendingClick(trending)}
                    className="w-full text-left px-3 py-2 text-sm bg-gray-50 hover:bg-gray-100 rounded-md transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span>{trending.query}</span>
                      <span className="text-xs text-gray-500">{trending.count}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Search Tips */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Search Tips</h3>
              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3"></div>
                  <div>Use specific terms like "BMW catalyst" or "Ford exhaust"</div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-2 h-2 bg-green-500 rounded-full mt-2 mr-3"></div>
                  <div>Filter by price range to find items in your budget</div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-2 h-2 bg-purple-500 rounded-full mt-2 mr-3"></div>
                  <div>Sort by newest to see recent listings first</div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-2 h-2 bg-orange-500 rounded-full mt-2 mr-3"></div>
                  <div>Use category filters to narrow down results</div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Search Results */}
            <div className="bg-white rounded-lg shadow p-6">
              {renderSearchResults()}

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-8 flex items-center justify-between">
                  <div className="flex items-center">
                    <button
                      onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                      disabled={currentPage === 1}
                      className="px-3 py-2 text-sm bg-white border border-gray-300 rounded-l-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    <span className="px-4 py-2 text-sm bg-gray-50 border-t border-b border-gray-300">
                      Page {currentPage} of {totalPages}
                    </span>
                    <button
                      onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                      disabled={currentPage === totalPages}
                      className="px-3 py-2 text-sm bg-white border border-gray-300 rounded-r-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </div>
                  <div className="text-sm text-gray-600">
                    Showing {((currentPage - 1) * resultsPerPage) + 1}-{Math.min(currentPage * resultsPerPage, totalResults)} of {totalResults} results
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const SearchResultCard = ({ listing, getSimilarListings }) => {
  const [similarListings, setSimilarListings] = useState([]);
  const [showSimilar, setShowSimilar] = useState(false);

  const handleShowSimilar = async () => {
    if (!showSimilar) {
      const similar = await getSimilarListings(listing.id);
      setSimilarListings(similar);
    }
    setShowSimilar(!showSimilar);
  };

  return (
    <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0 w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center">
          <span className="text-gray-500 text-xs">IMG</span>
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-lg font-medium text-gray-900 truncate">
                {listing.title}
              </h3>
              <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                {listing.description}
              </p>
              
              <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                <span className="capitalize">{listing.category}</span>
                <span className="capitalize">{listing.condition}</span>
                {listing.seller && (
                  <span>{listing.seller.username} ({listing.seller.is_business ? 'Business' : 'Private'})</span>
                )}
              </div>
            </div>
            
            <div className="flex-shrink-0 text-right">
              <div className="text-xl font-bold text-gray-900">
                €{listing.price}
              </div>
              <div className="text-sm text-gray-500 mt-1">
                {new Date(listing.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>
          
          <div className="flex items-center justify-between mt-4">
            <button
              onClick={handleShowSimilar}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              {showSimilar ? 'Hide Similar' : 'Show Similar Items'}
            </button>
            
            <div className="flex space-x-2">
              <button className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors">
                View Details
              </button>
              <button className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 transition-colors">
                Contact Seller
              </button>
            </div>
          </div>
          
          {/* Similar Listings */}
          {showSimilar && similarListings.length > 0 && (
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Similar Items</h4>
              <div className="space-y-2">
                {similarListings.map((similar) => (
                  <div key={similar.id} className="flex items-center justify-between text-sm">
                    <span className="text-gray-700 truncate flex-1 mr-2">{similar.title}</span>
                    <span className="font-medium text-gray-900">€{similar.price}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EnhancedSearchInterface;