/**
 * CATALORO - Mobile Filters Component
 * Touch-optimized filters with drawer interface and range sliders
 */

import React, { useState, useEffect } from 'react';
import { 
  Filter, 
  X, 
  ChevronDown, 
  ChevronUp, 
  Check,
  MapPin,
  Calendar,
  DollarSign,
  Tag,
  Star
} from 'lucide-react';

function MobileFilters({ 
  isOpen, 
  onClose, 
  filters, 
  onFiltersChange, 
  availableFilters = {} 
}) {
  // Default filters structure to prevent undefined errors
  const defaultFilters = {
    category: '',
    priceRange: { min: 0, max: 1000 },
    location: '',
    condition: '',
    dateRange: '',
    rating: 0,
    sortBy: 'newest'
  };

  const [localFilters, setLocalFilters] = useState(filters || defaultFilters);
  const [expandedSections, setExpandedSections] = useState({
    price: false,
    location: false,
    category: false,
    condition: false,
    date: false,
    rating: false
  });

  useEffect(() => {
    // Ensure filters is properly merged with defaults
    setLocalFilters(prevFilters => ({
      ...defaultFilters,
      ...filters
    }));
  }, [filters]);

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const updateFilter = (key, value) => {
    setLocalFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handlePriceChange = (type, value) => {
    setLocalFilters(prev => ({
      ...prev,
      priceRange: {
        ...prev.priceRange,
        [type]: parseInt(value) || 0
      }
    }));
  };

  const clearFilters = () => {
    setLocalFilters(defaultFilters);
  };

  const applyFilters = () => {
    onFiltersChange(localFilters);
    onClose();
  };

  const getActiveFiltersCount = () => {
    if (!localFilters) return 0;
    
    let count = 0;
    if (localFilters.category) count++;
    if (localFilters.location) count++;
    if (localFilters.condition) count++;
    if (localFilters.dateRange) count++;
    if (localFilters.rating && localFilters.rating > 0) count++;
    if (localFilters.priceRange?.min > 0 || localFilters.priceRange?.max < 1000) count++;
    return count;
  };

  const categories = availableFilters.categories || [
    'Catalytic Converters',
    'Diesel Particulate Filters',
    'Ceramic Catalysts',
    'Metallic Catalysts',
    'Three-way Catalysts',
    'Oxidation Catalysts'
  ];

  const locations = availableFilters.locations || [
    'Germany',
    'France',
    'United Kingdom',
    'Netherlands',
    'Belgium',
    'Italy',
    'Spain'
  ];

  const conditions = availableFilters.conditions || [
    'New',
    'Like New',
    'Good',
    'Fair',
    'Used'
  ];

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Filter Drawer */}
      <div className={`fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 rounded-t-2xl shadow-2xl z-50 transform transition-transform duration-300 ease-out lg:hidden ${
        isOpen ? 'translate-y-0' : 'translate-y-full'
      }`}>
        {/* Handle */}
        <div className="w-12 h-1 bg-gray-300 dark:bg-gray-600 rounded-full mx-auto mt-3"></div>

        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Filters
            </h2>
            {getActiveFiltersCount() > 0 && (
              <div className="bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                {getActiveFiltersCount()}
              </div>
            )}
          </div>
          
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filters Content */}
        <div className="max-h-[70vh] overflow-y-auto">
          <div className="p-4 space-y-6">
            
            {/* Quick Sort */}
            <div>
              <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Sort By</h3>
              <div className="grid grid-cols-2 gap-2">
                  {[
                    { key: 'newest', label: 'Newest' },
                    { key: 'oldest', label: 'Oldest' },
                    { key: 'price_low', label: 'Price: Low to High' },
                    { key: 'price_high', label: 'Price: High to Low' }
                  ].map((option) => (
                    <button
                      key={option.key}
                      onClick={() => updateFilter('sortBy', option.key)}
                      className={`p-3 text-sm rounded-lg border transition-colors ${
                        localFilters?.sortBy === option.key
                          ? 'bg-blue-100 dark:bg-blue-900/30 border-blue-500 text-blue-700 dark:text-blue-300'
                          : 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300'
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
              </div>
            </div>

            {/* Price Range */}
            <div>
              <button
                onClick={() => toggleSection('price')}
                className="flex items-center justify-between w-full text-left"
              >
                <div className="flex items-center space-x-2">
                  <DollarSign className="w-4 h-4 text-gray-500" />
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white">Price Range</h3>
                </div>
                {expandedSections.price ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              
              {expandedSections.price && (
                <div className="mt-3 space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Min Price</label>
                      <input
                        type="number"
                        value={localFilters.priceRange?.min || 0}
                        onChange={(e) => handlePriceChange('min', e.target.value)}
                        className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm"
                        placeholder="0"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Max Price</label>
                      <input
                        type="number"
                        value={localFilters.priceRange?.max || 1000}
                        onChange={(e) => handlePriceChange('max', e.target.value)}
                        className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm"
                        placeholder="1000"
                      />
                    </div>
                  </div>
                  
                  {/* Range Slider */}
                  <div className="px-2">
                    <input
                      type="range"
                      min="0"
                      max="1000"
                      value={localFilters.priceRange?.max || 1000}
                      onChange={(e) => handlePriceChange('max', e.target.value)}
                      className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Category */}
            <div>
              <button
                onClick={() => toggleSection('category')}
                className="flex items-center justify-between w-full text-left"
              >
                <div className="flex items-center space-x-2">
                  <Tag className="w-4 h-4 text-gray-500" />
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white">Category</h3>
                </div>
                {expandedSections.category ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              
              {expandedSections.category && (
                <div className="mt-3 space-y-2">
                  {categories.map((category) => (
                    <button
                      key={category}
                      onClick={() => updateFilter('category', category === localFilters?.category ? '' : category)}
                      className={`flex items-center justify-between w-full p-3 rounded-lg border transition-colors ${
                        localFilters?.category === category
                          ? 'bg-blue-100 dark:bg-blue-900/30 border-blue-500 text-blue-700 dark:text-blue-300'
                          : 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                    >
                      <span className="text-sm">{category}</span>
                      {localFilters?.category === category && <Check className="w-4 h-4" />}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Location */}
            <div>
              <button
                onClick={() => toggleSection('location')}
                className="flex items-center justify-between w-full text-left"
              >
                <div className="flex items-center space-x-2">
                  <MapPin className="w-4 h-4 text-gray-500" />
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white">Location</h3>
                </div>
                {expandedSections.location ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              
              {expandedSections.location && (
                <div className="mt-3 space-y-2">
                  {locations.map((location) => (
                    <button
                      key={location}
                      onClick={() => updateFilter('location', location === localFilters?.location ? '' : location)}
                      className={`flex items-center justify-between w-full p-3 rounded-lg border transition-colors ${
                        localFilters?.location === location
                          ? 'bg-blue-100 dark:bg-blue-900/30 border-blue-500 text-blue-700 dark:text-blue-300'
                          : 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                    >
                      <span className="text-sm">{location}</span>
                      {localFilters?.location === location && <Check className="w-4 h-4" />}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Condition */}
            <div>
              <button
                onClick={() => toggleSection('condition')}
                className="flex items-center justify-between w-full text-left"
              >
                <div className="flex items-center space-x-2">
                  <Star className="w-4 h-4 text-gray-500" />
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white">Condition</h3>
                </div>
                {expandedSections.condition ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              
              {expandedSections.condition && (
                <div className="mt-3 grid grid-cols-2 gap-2">
                  {conditions.map((condition) => (
                    <button
                      key={condition}
                      onClick={() => updateFilter('condition', condition === localFilters?.condition ? '' : condition)}
                      className={`p-3 text-sm rounded-lg border transition-colors ${
                        localFilters?.condition === condition
                          ? 'bg-blue-100 dark:bg-blue-900/30 border-blue-500 text-blue-700 dark:text-blue-300'
                          : 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300'
                      }`}
                    >
                      {condition}
                    </button>
                  ))}
                </div>
              )}
            </div>

          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <div className="flex space-x-3">
            <button
              onClick={clearFilters}
              className="flex-1 px-4 py-3 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
            >
              Clear All
            </button>
            <button
              onClick={applyFilters}
              className="flex-1 px-4 py-3 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Apply Filters ({getActiveFiltersCount()})
            </button>
          </div>
        </div>

        {/* Safe area padding */}
        <div className="h-safe-area-inset-bottom"></div>
      </div>
    </>
  );
}

export default MobileFilters;