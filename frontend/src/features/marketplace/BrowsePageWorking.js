import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { marketplaceAPI, favoritesAPI } from '../../services/api';
import { useToast } from '../../hooks/use-toast';
import Header from '../../components/layout/Header';
import Footer from '../../components/layout/Footer';
import ProductCard from '../../components/marketplace/ProductCard';
import { Button } from '../../components/ui/button';
import { Card, CardContent } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Badge } from '../../components/ui/badge';
import { 
  Search, Filter, Grid, List, SlidersHorizontal, Package,
  ChevronLeft, ChevronRight, Star, MapPin, Euro, Calendar,
  Zap, TrendingUp, Heart, Eye, RotateCcw, ArrowUpDown
} from 'lucide-react';

const BrowsePageWorking = () => {
  const { user } = useAuth();
  const { toast } = useToast();

  // State management
  const [listings, setListings] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(12);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [showFilters, setShowFilters] = useState(false);
  
  const [filters, setFilters] = useState({
    search: '',
    category: 'all',
    condition: 'all',
    listing_type: 'all',
    price_min: '',
    price_max: '',
    location: '',
    sort_by: 'created_desc'
  });

  // Categories with counts
  const categories = [
    { value: 'all', label: 'All Categories', count: 156 },
    { value: 'catalytic_converters', label: 'Catalytic Converters', count: 89 },
    { value: 'exhaust_systems', label: 'Exhaust Systems', count: 34 },
    { value: 'dpf_filters', label: 'DPF Filters', count: 23 },
    { value: 'mufflers', label: 'Mufflers & Silencers', count: 10 }
  ];

  // Popular filters
  const popularFilters = [
    { label: 'BMW Parts', filter: { search: 'bmw' }, count: 45 },
    { label: 'Mercedes Parts', filter: { search: 'mercedes' }, count: 38 },
    { label: 'Audi Parts', filter: { search: 'audi' }, count: 32 },
    { label: 'New Condition', filter: { condition: 'new' }, count: 28 },
    { label: 'Under €100', filter: { price_max: '100' }, count: 67 }
  ];

  useEffect(() => {
    fetchListings();
    fetchFavorites();
  }, [currentPage, itemsPerPage, filters]);

  const fetchListings = async (resetPage = false) => {
    try {
      setLoading(true);
      
      const page = resetPage ? 1 : currentPage;
      if (resetPage) setCurrentPage(1);

      const params = {
        limit: itemsPerPage,
        skip: (page - 1) * itemsPerPage,
        sort_by: filters.sort_by
      };

      // Add filter parameters
      if (filters.search) params.search = filters.search;
      if (filters.category !== 'all') params.category = filters.category;
      if (filters.condition !== 'all') params.condition = filters.condition;
      if (filters.listing_type !== 'all') params.listing_type = filters.listing_type;
      if (filters.price_min) params.price_min = parseFloat(filters.price_min);
      if (filters.price_max) params.price_max = parseFloat(filters.price_max);
      if (filters.location) params.location = filters.location;

      const response = await marketplaceAPI.getListings(params);
      
      if (response?.listings) {
        setListings(response.listings);
        setTotalCount(response.total || 0);
      }
    } catch (error) {
      console.error('Error fetching listings:', error);
      toast({
        title: "Error",
        description: "Failed to load listings",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchFavorites = async () => {
    try {
      const response = await favoritesAPI.getFavorites();
      setFavorites(response?.favorites?.map(fav => fav.listing_id) || []);
    } catch (error) {
      console.error('Error fetching favorites:', error);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleSearch = (searchTerm) => {
    setFilters(prev => ({ ...prev, search: searchTerm }));
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      category: 'all',
      condition: 'all',
      listing_type: 'all',
      price_min: '',
      price_max: '',
      location: '',
      sort_by: 'created_desc'
    });
  };

  const applyPopularFilter = (popularFilter) => {
    setFilters(prev => ({ ...prev, ...popularFilter.filter }));
    fetchListings(true);
    toast({
      title: "Filter Applied",
      description: `Showing results for: ${popularFilter.label}`,
    });
  };

  const toggleFavorite = async (listingId) => {
    try {
      if (favorites.includes(listingId)) {
        await favoritesAPI.removeFavorite(listingId);
        setFavorites(prev => prev.filter(id => id !== listingId));
        toast({
          title: "Removed from favorites",
          description: "Item removed from your favorites list"
        });
      } else {
        await favoritesAPI.addFavorite(listingId);
        setFavorites(prev => [...prev, listingId]);
        toast({
          title: "Added to favorites",
          description: "Item added to your favorites list"
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update favorites",
        variant: "destructive"
      });
    }
  };

  const totalPages = Math.ceil(totalCount / itemsPerPage);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-purple-50/30">
      <Header />
      
      <div className="container mx-auto px-4 py-8">
        {/* Hero Search Section */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-4">
            Browse Automotive Parts
          </h1>
          <p className="text-lg text-slate-600 mb-6">
            Find quality catalytic converters, exhaust systems, and more from trusted sellers
          </p>
          
          {/* Main Search Bar */}
          <div className="max-w-2xl mx-auto relative">
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 h-5 w-5" />
                <Input
                  placeholder="Search by part name, car model, or seller..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && fetchListings(true)}
                  className="pl-12 h-12 text-lg bg-white shadow-lg border-2 border-slate-200 focus:border-purple-500 transition-all"
                />
              </div>
              <Button 
                onClick={() => fetchListings(true)}
                className="h-12 px-8 bg-purple-600 hover:bg-purple-700 text-white shadow-lg"
              >
                <Search className="h-5 w-5 mr-2" />
                Search
              </Button>
            </div>
          </div>
        </div>

        {/* Popular Filters */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-3">Popular Searches</h3>
          <div className="flex flex-wrap gap-2">
            {popularFilters.map((filter, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                onClick={() => applyPopularFilter(filter)}
                className="bg-white hover:bg-purple-50 border-slate-200 hover:border-purple-300"
              >
                {filter.label}
                <Badge variant="secondary" className="ml-2 text-xs">
                  {filter.count}
                </Badge>
              </Button>
            ))}
          </div>
        </div>

        {/* Filters and Controls */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6">
          <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
            <div className="flex flex-wrap gap-4 flex-1">
              {/* Category Filter */}
              <div className="min-w-48">
                <Select value={filters.category} onValueChange={(value) => handleFilterChange('category', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category.value} value={category.value}>
                        <div className="flex items-center justify-between w-full">
                          <span>{category.label}</span>
                          <Badge variant="secondary" className="ml-2">{category.count}</Badge>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Condition Filter */}
              <div className="min-w-36">
                <Select value={filters.condition} onValueChange={(value) => handleFilterChange('condition', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Condition" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Conditions</SelectItem>
                    <SelectItem value="new">New</SelectItem>
                    <SelectItem value="like_new">Like New</SelectItem>
                    <SelectItem value="good">Good</SelectItem>
                    <SelectItem value="fair">Fair</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Price Range */}
              <div className="flex gap-2 items-center">
                <Input
                  type="number"
                  placeholder="Min €"
                  value={filters.price_min}
                  onChange={(e) => handleFilterChange('price_min', e.target.value)}
                  className="w-24"
                />
                <span className="text-slate-400">-</span>
                <Input
                  type="number"
                  placeholder="Max €"
                  value={filters.price_max}
                  onChange={(e) => handleFilterChange('price_max', e.target.value)}
                  className="w-24"
                />
              </div>

              {/* Location Filter */}
              <div className="min-w-36">
                <Input
                  placeholder="Location"
                  value={filters.location}
                  onChange={(e) => handleFilterChange('location', e.target.value)}
                />
              </div>
            </div>

            <div className="flex gap-2 items-center">
              {/* Sort */}
              <Select value={filters.sort_by} onValueChange={(value) => handleFilterChange('sort_by', value)}>
                <SelectTrigger className="w-40">
                  <ArrowUpDown className="h-4 w-4 mr-2" />
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="created_desc">Newest First</SelectItem>
                  <SelectItem value="created_asc">Oldest First</SelectItem>
                  <SelectItem value="price_asc">Price: Low to High</SelectItem>
                  <SelectItem value="price_desc">Price: High to Low</SelectItem>
                  <SelectItem value="rating_desc">Highest Rated</SelectItem>
                </SelectContent>
              </Select>

              {/* View Mode */}
              <div className="flex rounded-lg border border-slate-200 overflow-hidden">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('grid')}
                  className="rounded-none"
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('list')}
                  className="rounded-none"
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>

              {/* Clear Filters */}
              <Button variant="outline" size="sm" onClick={clearFilters}>
                <RotateCcw className="h-4 w-4 mr-2" />
                Clear
              </Button>
            </div>
          </div>

          {/* Active Filters Display */}
          {(filters.search || filters.category !== 'all' || filters.condition !== 'all' || filters.price_min || filters.price_max || filters.location) && (
            <div className="mt-4 pt-4 border-t border-slate-200">
              <div className="flex flex-wrap gap-2 items-center">
                <span className="text-sm font-medium text-slate-600">Active filters:</span>
                {filters.search && (
                  <Badge variant="secondary" className="flex items-center gap-1">
                    Search: "{filters.search}"
                    <button onClick={() => handleFilterChange('search', '')} className="ml-1 hover:text-red-500">×</button>
                  </Badge>
                )}
                {filters.category !== 'all' && (
                  <Badge variant="secondary" className="flex items-center gap-1">
                    Category: {categories.find(c => c.value === filters.category)?.label}
                    <button onClick={() => handleFilterChange('category', 'all')} className="ml-1 hover:text-red-500">×</button>
                  </Badge>
                )}
                {filters.condition !== 'all' && (
                  <Badge variant="secondary" className="flex items-center gap-1">
                    Condition: {filters.condition}
                    <button onClick={() => handleFilterChange('condition', 'all')} className="ml-1 hover:text-red-500">×</button>
                  </Badge>
                )}
                {(filters.price_min || filters.price_max) && (
                  <Badge variant="secondary" className="flex items-center gap-1">
                    Price: €{filters.price_min || '0'} - €{filters.price_max || '∞'}
                    <button onClick={() => {
                      handleFilterChange('price_min', '');
                      handleFilterChange('price_max', '');
                    }} className="ml-1 hover:text-red-500">×</button>
                  </Badge>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Results Summary */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">
              {totalCount.toLocaleString()} parts found
            </h2>
            <p className="text-slate-600">
              Showing {((currentPage - 1) * itemsPerPage) + 1} - {Math.min(currentPage * itemsPerPage, totalCount)} of {totalCount} results
            </p>
          </div>
          
          {/* Items per page */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-600">Show:</span>
            <Select value={itemsPerPage.toString()} onValueChange={(value) => setItemsPerPage(parseInt(value))}>
              <SelectTrigger className="w-20">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="12">12</SelectItem>
                <SelectItem value="24">24</SelectItem>
                <SelectItem value="48">48</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[...Array(8)].map((_, index) => (
              <Card key={index} className="animate-pulse">
                <div className="h-48 bg-slate-200 rounded-t-lg"></div>
                <CardContent className="p-4 space-y-2">
                  <div className="h-4 bg-slate-200 rounded w-3/4"></div>
                  <div className="h-4 bg-slate-200 rounded w-1/2"></div>
                  <div className="h-6 bg-slate-200 rounded w-1/4"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Results Grid/List */}
        {!loading && (
          <div className={
            viewMode === 'grid' 
              ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
              : "space-y-4"
          }>
            {listings.map((listing) => (
              <ProductCard
                key={listing.id}
                listing={listing}
                isFavorite={favorites.includes(listing.id)}
                onToggleFavorite={() => toggleFavorite(listing.id)}
                viewMode={viewMode}
                className="transition-all hover:shadow-lg hover:scale-105"
              />
            ))}
          </div>
        )}

        {/* No Results */}
        {!loading && listings.length === 0 && (
          <Card className="text-center py-16">
            <CardContent>
              <Package className="h-16 w-16 text-slate-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-900 mb-2">No parts found</h3>
              <p className="text-slate-600 mb-4">
                Try adjusting your filters or search terms to find what you're looking for.
              </p>
              <Button onClick={clearFilters} className="bg-purple-600 hover:bg-purple-700">
                <RotateCcw className="h-4 w-4 mr-2" />
                Clear All Filters
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Pagination */}
        {!loading && totalPages > 1 && (
          <div className="flex justify-center items-center gap-2 mt-8">
            <Button
              variant="outline"
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            
            {/* Page Numbers */}
            <div className="flex gap-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const pageNum = Math.max(1, currentPage - 2) + i;
                if (pageNum > totalPages) return null;
                
                return (
                  <Button
                    key={pageNum}
                    variant={currentPage === pageNum ? "default" : "outline"}
                    size="sm"
                    onClick={() => setCurrentPage(pageNum)}
                    className="w-10"
                  >
                    {pageNum}
                  </Button>
                );
              })}
            </div>
            
            <Button
              variant="outline"
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
      
      <Footer />
    </div>
  );
};

export default BrowsePageWorking;