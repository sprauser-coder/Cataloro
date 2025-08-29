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
import { Link } from 'react-router-dom';
import { marketplaceService } from '../../services/marketplaceService';
import { useMarketplace } from '../../context/MarketplaceContext';

function ModernBrowsePage() {
  const [listings, setListings] = useState([]);
  const [filteredListings, setFilteredListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  
  // Filter states
  const [filters, setFilters] = useState({
    category: 'all',
    priceRange: [0, 10000],
    condition: 'all',
    location: 'all',
    rating: 0
  });

  const [categories] = useState([
    'Electronics', 'Fashion', 'Home & Garden', 'Sports', 'Books', 'Music',
    'Cars', 'Real Estate', 'Jobs', 'Services'
  ]);

  const [featuredProducts] = useState([
    {
      id: 'featured-1',
      title: 'iPhone 15 Pro Max',
      price: 1199,
      originalPrice: 1299,
      image: 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400',
      rating: 4.8,
      reviews: 124,
      seller: 'TechStore Pro',
      location: 'New York, NY',
      featured: true,
      tag: 'Best Seller'
    },
    {
      id: 'featured-2', 
      title: 'MacBook Air M2',
      price: 999,
      originalPrice: 1199,
      image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400',
      rating: 4.9,
      reviews: 89,
      seller: 'Apple Certified',
      location: 'San Francisco, CA',
      featured: true,
      tag: 'Limited Offer'
    }
  ]);

  useEffect(() => {
    fetchListings();
  }, []);

  useEffect(() => {
    applyFiltersAndSearch();
  }, [listings, searchQuery, filters, sortBy]);

  const fetchListings = async () => {
    try {
      setLoading(true);
      const data = await marketplaceService.browseListings();
      
      // Enhanced dummy data with more details
      const enhancedListings = [
        {
          id: '1',
          title: 'MacBook Pro 16-inch M3',
          description: 'Like new condition, barely used for 2 months. Includes original box, charger, and all accessories.',
          price: 2499,
          originalPrice: 2799,
          category: 'Electronics',
          seller: {
            name: 'TechGuru123',
            rating: 4.9,
            reviews: 156,
            verified: true,
            location: 'San Francisco, CA'
          },
          images: [
            'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400',
            'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=400'
          ],
          condition: 'Like New',
          views: 234,
          favorites: 45,
          createdAt: new Date().toISOString(),
          features: ['M3 Pro Chip', '32GB RAM', '1TB SSD', 'Space Gray'],
          shipping: 'Free shipping',
          rating: 4.8,
          tags: ['Hot Deal', 'Fast Shipping']
        },
        {
          id: '2',
          title: 'Vintage Gibson Les Paul Guitar',
          description: 'Authentic 1979 Gibson Les Paul in excellent condition. Perfect for collectors and professional musicians.',
          price: 3200,
          originalPrice: 3800,
          category: 'Music',
          seller: {
            name: 'MusicStore_Pro',
            rating: 4.8,
            reviews: 89,
            verified: true,
            location: 'Nashville, TN'
          },
          images: [
            'https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=400',
            'https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?w=400'
          ],
          condition: 'Excellent',
          views: 189,
          favorites: 67,
          createdAt: new Date(Date.now() - 86400000).toISOString(),
          features: ['1979 Model', 'Original Case', 'Certificate of Authenticity'],
          shipping: 'Insured shipping',
          rating: 4.9,
          tags: ['Vintage', 'Authenticated']
        },
        {
          id: '3',
          title: 'Designer Leather Handbag',
          description: 'Authentic Louis Vuitton handbag in pristine condition. Comes with authenticity card and dust bag.',
          price: 1850,
          originalPrice: 2200,
          category: 'Fashion',
          seller: {
            name: 'LuxuryItems_NYC',
            rating: 4.7,
            reviews: 245,
            verified: true,
            location: 'New York, NY'
          },
          images: [
            'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400',
            'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400'
          ],
          condition: 'Excellent',
          views: 156,
          favorites: 89,
          createdAt: new Date(Date.now() - 172800000).toISOString(),
          features: ['Authentic', 'Dust Bag Included', 'Care Card'],
          shipping: 'Express delivery',
          rating: 4.6,
          tags: ['Luxury', 'Authentic']
        },
        {
          id: '4',
          title: 'Gaming Setup - RTX 4080 PC',
          description: 'High-end gaming PC build with RTX 4080, perfect for 4K gaming and content creation.',
          price: 2800,
          category: 'Electronics',
          seller: {
            name: 'PCBuilder_Expert',
            rating: 4.9,
            reviews: 78,
            verified: true,
            location: 'Austin, TX'
          },
          images: [
            'https://images.unsplash.com/photo-1587831990711-23ca6441447b?w=400'
          ],
          condition: 'New',
          views: 298,
          favorites: 112,
          createdAt: new Date(Date.now() - 43200000).toISOString(),
          features: ['RTX 4080', 'Intel i7-13700K', '32GB RAM', 'RGB Lighting'],
          shipping: 'Local pickup available',
          rating: 5.0,
          tags: ['Gaming', 'Custom Built']
        }
      ];
      
      setListings(enhancedListings);
    } catch (error) {
      console.error('Failed to fetch listings:', error);
      // Use enhanced dummy data on error
      setListings([]);
    } finally {
      setLoading(false);
    }
  };

  const applyFiltersAndSearch = () => {
    let filtered = [...listings];

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(item =>
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.category.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Category filter
    if (filters.category !== 'all') {
      filtered = filtered.filter(item => item.category === filters.category);
    }

    // Price range filter
    filtered = filtered.filter(item => 
      item.price >= filters.priceRange[0] && item.price <= filters.priceRange[1]
    );

    // Condition filter
    if (filters.condition !== 'all') {
      filtered = filtered.filter(item => item.condition === filters.condition);
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'price_low':
          return a.price - b.price;
        case 'price_high':
          return b.price - a.price;
        case 'rating':
          return (b.rating || 0) - (a.rating || 0);
        case 'popular':
          return (b.views || 0) - (a.views || 0);
        case 'newest':
        default:
          return new Date(b.createdAt) - new Date(a.createdAt);
      }
    });

    setFilteredListings(filtered);
  };

  const handleAddToCart = (item) => {
    // Add to cart logic here
    alert(`Added ${item.title} to cart!`);
  };

  const handleAddToFavorites = (itemId) => {
    // Add to favorites logic here
    alert(`Added to favorites!`);
  };

  if (loading) {
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
      {/* Hero Section with Featured Products */}
      <div className="relative bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative z-10">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Discover Amazing Products
          </h1>
          <p className="text-xl mb-8 opacity-90">
            From electronics to fashion, find everything you need in one place
          </p>
          
          {/* Featured Products Carousel */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
            {featuredProducts.map((product) => (
              <div key={product.id} className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                <div className="flex items-center space-x-4">
                  <img 
                    src={product.image} 
                    alt={product.title}
                    className="w-20 h-20 object-cover rounded-lg"
                  />
                  <div className="flex-1">
                    <span className="inline-block bg-yellow-400 text-black text-xs px-2 py-1 rounded-full font-medium mb-2">
                      {product.tag}
                    </span>
                    <h3 className="font-bold text-lg">{product.title}</h3>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="text-2xl font-bold">${product.price}</span>
                      <span className="text-sm line-through opacity-70">${product.originalPrice}</span>
                    </div>
                    <div className="flex items-center mt-2">
                      <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                      <span className="text-sm ml-1">{product.rating} ({product.reviews})</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Search and Filter Controls */}
      <div className="flex flex-col lg:flex-row gap-4 items-center justify-between">
        
        {/* Advanced Search */}
        <div className="flex-1 max-w-2xl">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search by title, description, or category..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 shadow-sm"
            />
          </div>
        </div>

        {/* Filter and Sort Controls */}
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
            onChange={(e) => setSortBy(e.target.value)}
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
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-lg transition-all duration-200 ${
                viewMode === 'grid' 
                ? 'bg-white dark:bg-gray-700 shadow-sm text-blue-600' 
                : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              <Grid3X3 className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
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
                onChange={(e) => setFilters({...filters, category: e.target.value})}
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
                  onChange={(e) => setFilters({...filters, priceRange: [0, parseInt(e.target.value)]})}
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
                onChange={(e) => setFilters({...filters, condition: e.target.value})}
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
                onClick={() => setFilters({category: 'all', priceRange: [0, 10000], condition: 'all', location: 'all', rating: 0})}
                className="w-full px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Results Count and Quick Stats */}
      <div className="flex items-center justify-between">
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
      </div>

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

  const isGridView = viewMode === 'grid';

  const handleNextImage = () => {
    if (item.images && item.images.length > 1) {
      setCurrentImageIndex((prev) => (prev + 1) % item.images.length);
    }
  };

  return (
    <div 
      className={`group bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 overflow-hidden ${
        isGridView ? 'hover:-translate-y-2' : 'flex space-x-4 p-4'
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
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
            onClick={() => onAddToFavorites(item.id)}
            className="p-2 bg-white/90 dark:bg-gray-800/90 text-gray-700 dark:text-gray-300 hover:text-red-500 rounded-full shadow-sm transition-colors"
          >
            <Heart className="w-5 h-5" />
          </button>
          <button className="p-2 bg-white/90 dark:bg-gray-800/90 text-gray-700 dark:text-gray-300 hover:text-blue-500 rounded-full shadow-sm transition-colors">
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
            onClick={() => onAddToCart(item)}
            className="flex-1 flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-lg font-medium transition-colors"
          >
            <ShoppingCart className="w-4 h-4" />
            <span>Add to Cart</span>
          </button>
          <button className="px-4 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors">
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