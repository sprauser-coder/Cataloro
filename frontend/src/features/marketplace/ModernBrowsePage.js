/**
 * CATALORO - Ultra-Modern Browse Page
 * Advanced marketplace browsing with filters, search, and modern UI
 */

import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  Grid3X3, 
  List, 
  Heart, 
  Share2, 
  Eye, 
  Star,
  MapPin,
  Clock,
  TrendingUp,
  Zap,
  ShoppingCart,
  MessageCircle,
  SlidersHorizontal,
  X,
  ChevronDown,
  ArrowUpDown
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { marketplaceService } from '../../services/marketplaceService';
import { useMarketplace } from '../../context/MarketplaceContext';

function ModernBrowsePage() {
  // Use marketplace context
  const {
    allProducts,
    filteredProducts,
    addToCart,
    addToFavorites,
    favorites,
    setSearchQuery: setGlobalSearchQuery,
    setFilters: setGlobalFilters,
    setSortBy: setGlobalSortBy,
    setViewMode: setGlobalViewMode,
    searchQuery: globalSearchQuery,
    activeFilters: globalFilters,
    sortBy: globalSortBy,
    viewMode: globalViewMode,
    isLoading
  } = useMarketplace();

  const [showFilters, setShowFilters] = useState(false);
  const [heroContent, setHeroContent] = useState({
    title: 'Discover Amazing Products',
    description: 'From electronics to fashion, find everything you need in one place',
    height: 400,
    image_url: ''
  });
  
  // Use global search and filter states from context
  const searchQuery = globalSearchQuery;
  const filters = globalFilters;
  const sortBy = globalSortBy;
  const viewMode = globalViewMode;
  const listings = allProducts;
  const filteredListings = filteredProducts;

  const [categories] = useState([
    'Electronics', 'Fashion', 'Home & Garden', 'Sports', 'Books', 'Music',
    'Cars', 'Real Estate', 'Jobs', 'Services'
  ]);

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
                  placeholder="Search for anything you need..."
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
        <div className="flex items-center space-x-6">
          <p className="text-gray-600 dark:text-gray-400">
            <span className="font-semibold text-gray-900 dark:text-white">{filteredListings.length}</span> products found
            {searchQuery && ` for "${searchQuery}"`}
          </p>
          
          <div className="hidden md:flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
            <span className="flex items-center">
              <TrendingUp className="w-4 h-4 mr-1" />
              Trending
            </span>
            <span className="flex items-center">
              <Zap className="w-4 h-4 mr-1" />
              Fast Shipping
            </span>
          </div>
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
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Category Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Category
              </label>
              <select
                value={filters.category}
                onChange={(e) => updateFilters({...filters, category: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="all">All Categories</option>
                {categories.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>

            {/* Price Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Price Range
              </label>
              <div className="space-y-2">
                <input
                  type="range"
                  min="0"
                  max="10000"
                  value={filters.priceRange[1]}
                  onChange={(e) => updateFilters({...filters, priceRange: [0, parseInt(e.target.value)]})}
                  className="w-full"
                />
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                  <span>$0</span>
                  <span>${filters.priceRange[1]}</span>
                </div>
              </div>
            </div>

            {/* Condition Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Condition
              </label>
              <select
                value={filters.condition}
                onChange={(e) => updateFilters({...filters, condition: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="all">Any Condition</option>
                <option value="New">New</option>
                <option value="Like New">Like New</option>
                <option value="Excellent">Excellent</option>
                <option value="Good">Good</option>
                <option value="Fair">Fair</option>
              </select>
            </div>

            {/* Quick Actions */}
            <div className="flex items-end">
              <button
                onClick={() => updateFilters({category: 'all', priceRange: [0, 10000], condition: 'all', location: 'all', rating: 0})}
                className="w-full px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
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
              onAddToFavorites={handleAddToFavorites}
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
    </div>
  );
}

// Enhanced Product Card Component
function ProductCard({ item, viewMode, onAddToCart, onAddToFavorites }) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isHovered, setIsHovered] = useState(false);
  const navigate = useNavigate();

  const isGridView = viewMode === 'grid';

  const handleNextImage = (e) => {
    e.stopPropagation(); // Prevent navigation when clicking image navigation
    if (item.images && item.images.length > 1) {
      setCurrentImageIndex((prev) => (prev + 1) % item.images.length);
    }
  };

  const handleCardClick = () => {
    navigate(`/product/${item.id}`);
  };

  const handleQuickAction = (e, action) => {
    e.stopPropagation(); // Prevent navigation when clicking action buttons
    action();
  };

  return (
    <div 
      className={`group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 overflow-hidden cursor-pointer ${
        isGridView ? 'hover:-translate-y-2' : 'flex space-x-4 p-4'
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={handleCardClick}
    >
      {/* Image Section */}
      <div className={`relative ${isGridView ? '' : 'w-48 h-48 flex-shrink-0'}`}>
        <img
          src={item.images?.[currentImageIndex] || item.images?.[0] || '/api/placeholder/400/300'}
          alt={item.title}
          className={`object-cover transition-transform duration-300 group-hover:scale-105 ${
            isGridView ? 'w-full h-64' : 'w-full h-full rounded-lg'
          }`}
          onClick={handleNextImage}
        />
        
        {/* Image Indicators */}
        {item.images && item.images.length > 1 && (
          <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex space-x-1">
            {item.images.map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full ${
                  index === currentImageIndex ? 'bg-white' : 'bg-white/50'
                }`}
              />
            ))}
          </div>
        )}

        {/* Tags and Badges */}
        <div className="absolute top-2 left-2 space-y-1">
          {item.tags?.map((tag) => (
            <span
              key={tag}
              className="inline-block bg-red-500 text-white text-xs px-2 py-1 rounded-full font-medium"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Quick Actions */}
        <div className={`absolute top-2 right-2 space-y-2 transition-opacity duration-200 ${
          isHovered ? 'opacity-100' : 'opacity-0'
        }`}>
          <button
            onClick={(e) => handleQuickAction(e, () => onAddToFavorites(item))}
            className="p-2 bg-white/90 dark:bg-gray-800/90 text-gray-700 dark:text-gray-300 hover:text-red-500 rounded-full shadow-sm transition-colors"
          >
            <Heart className="w-5 h-5" />
          </button>
          <button 
            onClick={(e) => handleQuickAction(e, () => {})}
            className="p-2 bg-white/90 dark:bg-gray-800/90 text-gray-700 dark:text-gray-300 hover:text-blue-500 rounded-full shadow-sm transition-colors"
          >
            <Share2 className="w-5 h-5" />
          </button>
        </div>

        {/* Views Counter */}
        <div className="absolute bottom-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded-full flex items-center">
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
        <div className="flex items-center space-x-2 mb-3">
          <span className="text-2xl font-bold text-gray-900 dark:text-white">
            ${item.price.toFixed(2)}
          </span>
          {item.originalPrice && item.originalPrice > item.price && (
            <>
              <span className="text-lg text-gray-500 line-through">
                ${item.originalPrice.toFixed(2)}
              </span>
              <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-medium">
                {Math.round((1 - item.price / item.originalPrice) * 100)}% off
              </span>
            </>
          )}
        </div>

        {/* Rating and Reviews */}
        {item.rating && (
          <div className="flex items-center space-x-2 mb-3">
            <div className="flex items-center">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-4 h-4 ${
                    i < Math.floor(item.rating)
                      ? 'text-yellow-400 fill-current'
                      : 'text-gray-300'
                  }`}
                />
              ))}
            </div>
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {item.rating} ({item.seller?.reviews} reviews)
            </span>
          </div>
        )}

        {/* Seller Info */}
        <div className="flex items-center space-x-2 mb-3">
          <div className="w-6 h-6 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
            <span className="text-white text-xs font-bold">
              {item.seller?.name?.charAt(0)}
            </span>
          </div>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {item.seller?.name}
          </span>
          {item.seller?.verified && (
            <span className="text-blue-500 text-xs">✓ Verified</span>
          )}
        </div>

        {/* Location and Shipping */}
        <div className="text-sm text-gray-500 dark:text-gray-400 mb-4 space-y-1">
          <div className="flex items-center">
            <MapPin className="w-4 h-4 mr-1" />
            {item.seller?.location}
          </div>
          {item.shipping && (
            <div className="flex items-center text-green-600">
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

        {/* Action Buttons */}
        <div className={`flex space-x-2 ${isGridView ? '' : 'mt-4'}`}>
          <button
            onClick={(e) => handleQuickAction(e, () => onAddToCart(item))}
            className="flex-1 flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-lg font-medium transition-colors"
          >
            <ShoppingCart className="w-4 h-4" />
            <span>Add to Cart</span>
          </button>
          <button 
            onClick={(e) => handleQuickAction(e, () => {})}
            className="px-4 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <MessageCircle className="w-4 h-4" />
          </button>
        </div>

        {/* Condition and Time */}
        <div className="flex items-center justify-between mt-3 text-xs text-gray-500 dark:text-gray-400">
          <span>Condition: {item.condition}</span>
          <span>{new Date(item.createdAt).toLocaleDateString()}</span>
        </div>
      </div>
    </div>
  );
}

export default ModernBrowsePage;