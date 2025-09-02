/**
 * CATALORO - Advanced Search Filters Component
 * Comprehensive filtering system with price ranges, categories, and conditions
 */

import React, { useState, useEffect } from 'react';
import { Filter, X, ChevronDown, DollarSign, MapPin, Star, Tag } from 'lucide-react';

function AdvancedFilters({ onFiltersChange, initialFilters = {}, className = "" }) {
  const [isOpen, setIsOpen] = useState(false);
  const [filters, setFilters] = useState({
    category: 'all',
    condition: 'all',
    priceFrom: '',
    priceTo: '',
    location: 'all',
    rating: 0,
    features: [],
    sortBy: 'newest',
    ...initialFilters
  });

  const [categories, setCategories] = useState([]);
  const [locations, setLocations] = useState([]);
  const [activeFilterCount, setActiveFilterCount] = useState(0);

  // Load available categories and locations
  useEffect(() => {
    loadFilterOptions();
  }, []);

  // Update active filter count
  useEffect(() => {
    let count = 0;
    if (filters.category !== 'all') count++;
    if (filters.condition !== 'all') count++;
    if (filters.priceFrom || filters.priceTo) count++;
    if (filters.location !== 'all') count++;
    if (filters.rating > 0) count++;
    if (filters.features.length > 0) count++;
    if (filters.sortBy !== 'newest') count++;
    
    setActiveFilterCount(count);
  }, [filters]);

  const loadFilterOptions = async () => {
    try {
      // Load categories
      const categoriesResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/listings?limit=1`);
      if (categoriesResponse.ok) {
        // This is a simplified approach - in a real app, you'd have a dedicated endpoint
        const sampleCategories = [
          'Electronics', 'Fashion', 'Home & Garden', 'Sports & Outdoors',
          'Musical Instruments', 'Photography', 'Books', 'Automotive',
          'Collectibles', 'Arts & Crafts', 'Health & Beauty', 'Toys & Games'
        ];
        setCategories(sampleCategories);
      }

      // Load locations
      const sampleLocations = [
        'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX',
        'Phoenix, AZ', 'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA',
        'Dallas, TX', 'San Jose, CA', 'Austin, TX', 'Jacksonville, FL'
      ];
      setLocations(sampleLocations);
    } catch (error) {
      console.error('Error loading filter options:', error);
    }
  };

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handlePriceChange = (type, value) => {
    const numValue = value === '' ? '' : Math.max(0, parseFloat(value) || 0);
    const newFilters = { ...filters, [type]: numValue };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleFeatureToggle = (feature) => {
    const newFeatures = filters.features.includes(feature)
      ? filters.features.filter(f => f !== feature)
      : [...filters.features, feature];
    
    const newFilters = { ...filters, features: newFeatures };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const clearAllFilters = () => {
    const defaultFilters = {
      category: 'all',
      condition: 'all',
      priceFrom: '',
      priceTo: '',
      location: 'all',
      rating: 0,
      features: [],
      sortBy: 'newest'
    };
    setFilters(defaultFilters);
    onFiltersChange(defaultFilters);
  };

  const clearFilter = (filterKey) => {
    let newFilters = { ...filters };
    
    switch (filterKey) {
      case 'category':
        newFilters.category = 'all';
        break;
      case 'condition':
        newFilters.condition = 'all';
        break;
      case 'price':
        newFilters.priceFrom = '';
        newFilters.priceTo = '';
        break;
      case 'location':
        newFilters.location = 'all';
        break;
      case 'rating':
        newFilters.rating = 0;
        break;
      case 'features':
        newFilters.features = [];
        break;
      case 'sortBy':
        newFilters.sortBy = 'newest';
        break;
      default:
        break;
    }
    
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const conditions = [
    { value: 'new', label: 'New' },
    { value: 'like-new', label: 'Like New' },
    { value: 'excellent', label: 'Excellent' },
    { value: 'good', label: 'Good' },
    { value: 'fair', label: 'Fair' },
    { value: 'used', label: 'Used' }
  ];

  const sortOptions = [
    { value: 'newest', label: 'Newest First' },
    { value: 'oldest', label: 'Oldest First' },
    { value: 'price_low', label: 'Price: Low to High' },
    { value: 'price_high', label: 'Price: High to Low' },
    { value: 'popular', label: 'Most Popular' },
    { value: 'rating', label: 'Highest Rated' }
  ];

  const commonFeatures = [
    'Free Shipping', 'Fast Delivery', 'Warranty Included', 'Return Policy',
    'Brand New', 'Verified Seller', 'Local Pickup', 'Negotiable Price'
  ];

  return (
    <div className={`relative ${className}`}>
      {/* Filter Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200 shadow-sm"
      >
        <Filter className="h-4 w-4 mr-2 text-gray-600" />
        <span className="text-sm font-medium text-gray-700">
          Filters
        </span>
        {activeFilterCount > 0 && (
          <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
            {activeFilterCount}
          </span>
        )}
        <ChevronDown className={`h-4 w-4 ml-2 text-gray-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Active Filters Pills */}
      {activeFilterCount > 0 && (
        <div className="flex flex-wrap gap-2 mt-3">
          {filters.category !== 'all' && (
            <div className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
              <Tag className="h-3 w-3 mr-1" />
              {filters.category}
              <button
                onClick={() => clearFilter('category')}
                className="ml-2 text-blue-600 hover:text-blue-800"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          )}
          
          {filters.condition !== 'all' && (
            <div className="inline-flex items-center px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
              Condition: {conditions.find(c => c.value === filters.condition)?.label}
              <button
                onClick={() => clearFilter('condition')}
                className="ml-2 text-green-600 hover:text-green-800"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          )}
          
          {(filters.priceFrom || filters.priceTo) && (
            <div className="inline-flex items-center px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">
              <DollarSign className="h-3 w-3 mr-1" />
              {filters.priceFrom && filters.priceTo 
                ? `$${filters.priceFrom} - $${filters.priceTo}`
                : filters.priceFrom 
                ? `From $${filters.priceFrom}`
                : `Up to $${filters.priceTo}`
              }
              <button
                onClick={() => clearFilter('price')}
                className="ml-2 text-purple-600 hover:text-purple-800"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          )}
          
          {filters.location !== 'all' && (
            <div className="inline-flex items-center px-3 py-1 bg-orange-100 text-orange-800 text-sm rounded-full">
              <MapPin className="h-3 w-3 mr-1" />
              {filters.location}
              <button
                onClick={() => clearFilter('location')}
                className="ml-2 text-orange-600 hover:text-orange-800"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          )}

          <button
            onClick={clearAllFilters}
            className="inline-flex items-center px-3 py-1 bg-gray-100 text-gray-600 text-sm rounded-full hover:bg-gray-200 transition-colors duration-200"
          >
            Clear All
            <X className="h-3 w-3 ml-1" />
          </button>
        </div>
      )}

      {/* Filters Panel */}
      {isOpen && (
        <div className="absolute z-40 top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-lg border border-gray-200 p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Metal Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Tag className="h-4 w-4 inline mr-1" />
                Metal Type
              </label>
              <select
                value={filters.metalType || 'all'}
                onChange={(e) => handleFilterChange('metalType', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Metals</option>
                <option value="platinum">Platinum</option>
                <option value="palladium">Palladium</option>
                <option value="rhodium">Rhodium</option>
                <option value="nickel">Nickel</option>
                <option value="cobalt">Cobalt</option>
                <option value="iron">Iron</option>
                <option value="copper">Copper</option>
                <option value="ruthenium">Ruthenium</option>
                <option value="gold">Gold</option>
                <option value="silver">Silver</option>
              </select>
            </div>

            {/* Condition Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Condition
              </label>
              <select
                value={filters.condition}
                onChange={(e) => handleFilterChange('condition', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">Any Condition</option>
                {conditions.map(condition => (
                  <option key={condition.value} value={condition.value}>{condition.label}</option>
                ))}
              </select>
            </div>

            {/* Location Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <MapPin className="h-4 w-4 inline mr-1" />
                Location
              </label>
              <select
                value={filters.location}
                onChange={(e) => handleFilterChange('location', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">Any Location</option>
                {locations.map(location => (
                  <option key={location} value={location}>{location}</option>
                ))}
              </select>
            </div>

            {/* Price Range */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <DollarSign className="h-4 w-4 inline mr-1" />
                Price Range
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="number"
                  placeholder="Min"
                  value={filters.priceFrom}
                  onChange={(e) => handlePriceChange('priceFrom', e.target.value)}
                  className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <span className="text-gray-500">to</span>
                <input
                  type="number"
                  placeholder="Max"
                  value={filters.priceTo}
                  onChange={(e) => handlePriceChange('priceTo', e.target.value)}
                  className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Sort By */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sort By
              </label>
              <select
                value={filters.sortBy}
                onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {sortOptions.map(option => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Features Filter */}
          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Features
            </label>
            <div className="flex flex-wrap gap-2">
              {commonFeatures.map(feature => (
                <button
                  key={feature}
                  onClick={() => handleFeatureToggle(feature)}
                  className={`px-3 py-1 text-sm rounded-full border transition-colors duration-200 ${
                    filters.features.includes(feature)
                      ? 'bg-blue-100 border-blue-300 text-blue-800'
                      : 'bg-gray-100 border-gray-300 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {feature}
                </button>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between items-center mt-6 pt-4 border-t border-gray-200">
            <button
              onClick={clearAllFilters}
              className="text-sm text-gray-600 hover:text-gray-800 transition-colors duration-200"
            >
              Clear All Filters
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors duration-200"
            >
              Apply Filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdvancedFilters;