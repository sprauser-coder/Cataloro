import React, { useState, useEffect } from 'react';
import { Search, SlidersHorizontal, X } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Badge } from '../ui/badge';
import { Card, CardContent } from '../ui/card';

const FilterBar = ({ onFiltersChange, initialFilters = {} }) => {
  const [filters, setFilters] = useState({
    search: '',
    category: 'all',
    condition: 'all',
    listing_type: 'all',
    price_min: '',
    price_max: '',
    sort_by: 'created_desc',
    ...initialFilters
  });

  const [showAdvanced, setShowAdvanced] = useState(false);
  const [categories, setCategories] = useState([
    'Electronics', 'Fashion', 'Home & Garden', 'Sports', 'Books', 
    'Toys', 'Automotive', 'Health & Beauty', 'Other'
  ]);

  useEffect(() => {
    // Debounce filter changes
    const timeoutId = setTimeout(() => {
      onFiltersChange(filters);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [filters, onFiltersChange]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      category: 'all',
      condition: 'all',
      listing_type: 'all',
      price_min: '',
      price_max: '',
      sort_by: 'created_desc'
    });
  };

  const getActiveFilterCount = () => {
    let count = 0;
    if (filters.search) count++;
    if (filters.category !== 'all') count++;
    if (filters.condition !== 'all') count++;
    if (filters.listing_type !== 'all') count++;
    if (filters.price_min || filters.price_max) count++;
    return count;
  };

  const activeFilterCount = getActiveFilterCount();

  return (
    <Card className="border-0 shadow-sm bg-white">
      <CardContent className="p-6">
        {/* Main Filter Row */}
        <div className="flex flex-col md:flex-row gap-4 mb-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
            <Input
              placeholder="Search products..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="pl-10 border-slate-200 focus:border-purple-300 focus:ring-purple-200"
            />
          </div>

          {/* Category */}
          <Select value={filters.category} onValueChange={(value) => handleFilterChange('category', value)}>
            <SelectTrigger className="w-full md:w-48 border-slate-200">
              <SelectValue placeholder="All Categories" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              {categories.map(category => (
                <SelectItem key={category} value={category.toLowerCase()}>
                  {category}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Sort */}
          <Select value={filters.sort_by} onValueChange={(value) => handleFilterChange('sort_by', value)}>
            <SelectTrigger className="w-full md:w-48 border-slate-200">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="created_desc">Newest First</SelectItem>
              <SelectItem value="created_asc">Oldest First</SelectItem>
              <SelectItem value="price_asc">Price: Low to High</SelectItem>
              <SelectItem value="price_desc">Price: High to Low</SelectItem>
              <SelectItem value="title_asc">A-Z</SelectItem>
              <SelectItem value="title_desc">Z-A</SelectItem>
            </SelectContent>
          </Select>

          {/* Advanced Filters Toggle */}
          <Button
            variant="outline"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="border-slate-200 text-slate-600 hover:bg-slate-50"
          >
            <SlidersHorizontal className="h-4 w-4 mr-2" />
            Filters
            {activeFilterCount > 0 && (
              <Badge className="ml-2 bg-purple-100 text-purple-600 text-xs">
                {activeFilterCount}
              </Badge>
            )}
          </Button>
        </div>

        {/* Advanced Filters */}
        {showAdvanced && (
          <div className="border-t border-slate-100 pt-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Condition */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Condition</label>
                <Select value={filters.condition} onValueChange={(value) => handleFilterChange('condition', value)}>
                  <SelectTrigger className="border-slate-200">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Any Condition</SelectItem>
                    <SelectItem value="new">New</SelectItem>
                    <SelectItem value="like new">Like New</SelectItem>
                    <SelectItem value="good">Good</SelectItem>
                    <SelectItem value="fair">Fair</SelectItem>
                    <SelectItem value="poor">Poor</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Listing Type */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Listing Type</label>
                <Select value={filters.listing_type} onValueChange={(value) => handleFilterChange('listing_type', value)}>
                  <SelectTrigger className="border-slate-200">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="fixed_price">Buy Now</SelectItem>
                    <SelectItem value="auction">Auction</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Price Range */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Min Price</label>
                <Input
                  type="number"
                  placeholder="€0"
                  value={filters.price_min}
                  onChange={(e) => handleFilterChange('price_min', e.target.value)}
                  className="border-slate-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Max Price</label>
                <Input
                  type="number"
                  placeholder="€999+"
                  value={filters.price_max}
                  onChange={(e) => handleFilterChange('price_max', e.target.value)}
                  className="border-slate-200"
                />
              </div>
            </div>

            {/* Clear Filters */}
            {activeFilterCount > 0 && (
              <div className="flex justify-end mt-4">
                <Button
                  variant="ghost"
                  onClick={clearFilters}
                  className="text-slate-600 hover:text-slate-800"
                >
                  <X className="h-4 w-4 mr-2" />
                  Clear all filters
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Active Filters Display */}
        {activeFilterCount > 0 && (
          <div className="flex flex-wrap gap-2 mt-4">
            {filters.search && (
              <Badge variant="secondary" className="bg-purple-100 text-purple-700">
                Search: "{filters.search}"
                <button
                  onClick={() => handleFilterChange('search', '')}
                  className="ml-1 hover:text-purple-900"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )}
            {filters.category !== 'all' && (
              <Badge variant="secondary" className="bg-purple-100 text-purple-700">
                Category: {categories.find(c => c.toLowerCase() === filters.category) || filters.category}
                <button
                  onClick={() => handleFilterChange('category', 'all')}
                  className="ml-1 hover:text-purple-900"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )}
            {filters.condition !== 'all' && (
              <Badge variant="secondary" className="bg-purple-100 text-purple-700">
                Condition: {filters.condition}
                <button
                  onClick={() => handleFilterChange('condition', 'all')}
                  className="ml-1 hover:text-purple-900"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )}
            {filters.listing_type !== 'all' && (
              <Badge variant="secondary" className="bg-purple-100 text-purple-700">
                Type: {filters.listing_type === 'fixed_price' ? 'Buy Now' : 'Auction'}
                <button
                  onClick={() => handleFilterChange('listing_type', 'all')}
                  className="ml-1 hover:text-purple-900"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )}
            {(filters.price_min || filters.price_max) && (
              <Badge variant="secondary" className="bg-purple-100 text-purple-700">
                Price: €{filters.price_min || '0'} - €{filters.price_max || '∞'}
                <button
                  onClick={() => {
                    handleFilterChange('price_min', '');
                    handleFilterChange('price_max', '');
                  }}
                  className="ml-1 hover:text-purple-900"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default FilterBar;