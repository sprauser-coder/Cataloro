import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { marketplaceAPI, favoritesAPI } from '../../services/api';
import { useToast } from '../../hooks/use-toast';
import Header from '../../components/layout/Header';
import Footer from '../../components/layout/Footer';
import ProductCard from '../../components/marketplace/ProductCard';
import FilterBar from '../../components/marketplace/FilterBar';
import { Button } from '../../components/ui/button';
import { Card, CardContent } from '../../components/ui/card';
import { ChevronLeft, ChevronRight, Grid, List, Package } from 'lucide-react';

const BrowsePage = () => {
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
  
  const [filters, setFilters] = useState({
    search: '',
    category: 'all',
    condition: 'all',
    listing_type: 'all',
    price_min: '',
    price_max: '',
    sort_by: 'created_desc'
  });

  // Fetch listings with filters and pagination
  const fetchListings = async (resetPage = false) => {
    try {
      setLoading(true);
      
      const page = resetPage ? 1 : currentPage;
      if (resetPage) setCurrentPage(1);

      // Prepare API parameters
      const params = {
        limit: itemsPerPage,
        skip: (page - 1) * itemsPerPage,
        sort_by: filters.sort_by
      };

      // Add search filters
      if (filters.search) params.search = filters.search;
      if (filters.category !== 'all') params.category = filters.category;
      if (filters.condition !== 'all') params.condition = filters.condition;
      if (filters.listing_type !== 'all') params.listing_type = filters.listing_type;
      if (filters.price_min) params.price_min = parseFloat(filters.price_min);
      if (filters.price_max) params.price_max = parseFloat(filters.price_max);

      // Fetch listings and total count
      const [listingsResponse, countResponse] = await Promise.all([
        marketplaceAPI.getListings(params),
        marketplaceAPI.getListings({ ...params, count_only: true })
      ]);

      setListings(listingsResponse.data);
      setTotalCount(countResponse.data.total || listingsResponse.data.length);

    } catch (error) {
      console.error('Error fetching listings:', error);
      toast({
        title: "Error",
        description: "Failed to load listings. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  // Fetch user favorites
  const fetchFavorites = async () => {
    if (!user) return;
    
    try {
      const response = await favoritesAPI.getFavorites();
      setFavorites(response.data.map(fav => ({
        listing_id: fav.listing_id,
        favorite_id: fav.id
      })));
    } catch (error) {
      console.error('Error fetching favorites:', error);
    }
  };

  // Handle filter changes
  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
  };

  // Handle favorite toggle
  const handleFavoriteToggle = (listingId, isNowFavorited) => {
    if (isNowFavorited) {
      // Add to favorites list (favorite_id will be set by ProductCard)
      setFavorites(prev => [...prev, { listing_id: listingId, favorite_id: null }]);
    } else {
      // Remove from favorites list
      setFavorites(prev => prev.filter(fav => fav.listing_id !== listingId));
    }
  };

  // Pagination helpers
  const totalPages = Math.ceil(totalCount / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage + 1;
  const endIndex = Math.min(currentPage * itemsPerPage, totalCount);

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Effects
  useEffect(() => {
    fetchListings(true); // Reset page when filters change
  }, [filters, itemsPerPage]);

  useEffect(() => {
    fetchListings(); // Don't reset page when only page changes
  }, [currentPage]);

  useEffect(() => {
    fetchFavorites();
  }, [user]);

  // Helper function to check if listing is favorited
  const isListingFavorited = (listingId) => {
    return favorites.some(fav => fav.listing_id === listingId);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-light text-slate-900 mb-4 tracking-tight">
            Discover Amazing Deals
          </h1>
          <p className="text-lg text-slate-600 font-light">
            Browse thousands of products from trusted sellers
          </p>
        </div>

        {/* Filters */}
        <div className="mb-8">
          <FilterBar 
            onFiltersChange={handleFiltersChange}
            initialFilters={filters}
          />
        </div>

        {/* Results Header */}
        <Card className="border-0 shadow-sm mb-6">
          <CardContent className="p-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              {/* Results Count */}
              <div className="flex items-center gap-4">
                <div className="text-sm text-slate-600">
                  {loading ? (
                    "Loading..."
                  ) : (
                    <>
                      Showing {totalCount > 0 ? startIndex : 0}-{endIndex} of {totalCount} items
                      {filters.search && ` for "${filters.search}"`}
                    </>
                  )}
                </div>
              </div>

              {/* View Controls */}
              <div className="flex items-center gap-4">
                {/* Items per page */}
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-slate-600">Show:</span>
                  <select
                    value={itemsPerPage}
                    onChange={(e) => setItemsPerPage(Number(e.target.value))}
                    className="border border-slate-200 rounded px-2 py-1 text-sm focus:ring-2 focus:ring-purple-200 focus:border-purple-300"
                  >
                    <option value={12}>12</option>
                    <option value={24}>24</option>
                    <option value={48}>48</option>
                  </select>
                </div>

                {/* View mode toggle */}
                <div className="flex items-center border border-slate-200 rounded">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-2 ${viewMode === 'grid' ? 'bg-purple-100 text-purple-600' : 'text-slate-400 hover:text-slate-600'}`}
                  >
                    <Grid className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-2 ${viewMode === 'list' ? 'bg-purple-100 text-purple-600' : 'text-slate-400 hover:text-slate-600'}`}
                  >
                    <List className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center py-16">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
              <p className="mt-2 text-slate-600">Loading products...</p>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && listings.length === 0 && (
          <Card className="border-0 shadow-sm">
            <CardContent className="text-center py-16">
              <Package className="h-16 w-16 mx-auto text-slate-400 mb-4" />
              <h3 className="text-xl font-semibold text-slate-700 mb-2">No products found</h3>
              <p className="text-slate-500 mb-6">
                {filters.search || filters.category !== 'all' || filters.condition !== 'all' 
                  ? "Try adjusting your filters to see more results"
                  : "No products are currently available"
                }
              </p>
              {(filters.search || filters.category !== 'all' || filters.condition !== 'all') && (
                <Button
                  onClick={() => setFilters({
                    search: '',
                    category: 'all',
                    condition: 'all',
                    listing_type: 'all',
                    price_min: '',
                    price_max: '',
                    sort_by: 'created_desc'
                  })}
                  variant="outline"
                  className="border-purple-200 text-purple-600 hover:bg-purple-50"
                >
                  Clear all filters
                </Button>
              )}
            </CardContent>
          </Card>
        )}

        {/* Products Grid/List */}
        {!loading && listings.length > 0 && (
          <>
            <div className={`
              ${viewMode === 'grid' 
                ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6' 
                : 'space-y-4'
              }
            `}>
              {listings.map((listing) => (
                <ProductCard
                  key={listing.id}
                  listing={listing}
                  onFavoriteToggle={handleFavoriteToggle}
                  isInFavorites={isListingFavorited(listing.id)}
                />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <Card className="border-0 shadow-sm mt-8">
                <CardContent className="p-4">
                  <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                    {/* Page Info */}
                    <div className="text-sm text-slate-600">
                      Page {currentPage} of {totalPages}
                    </div>

                    {/* Pagination Controls */}
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                        className="border-slate-200"
                      >
                        <ChevronLeft className="h-4 w-4" />
                        Previous
                      </Button>

                      {/* Page Numbers */}
                      <div className="flex items-center gap-1">
                        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                          let pageNum;
                          if (totalPages <= 5) {
                            pageNum = i + 1;
                          } else if (currentPage <= 3) {
                            pageNum = i + 1;
                          } else if (currentPage >= totalPages - 2) {
                            pageNum = totalPages - 4 + i;
                          } else {
                            pageNum = currentPage - 2 + i;
                          }

                          return (
                            <Button
                              key={pageNum}
                              variant={currentPage === pageNum ? "default" : "outline"}
                              size="sm"
                              onClick={() => handlePageChange(pageNum)}
                              className={`w-10 h-10 ${
                                currentPage === pageNum 
                                  ? 'bg-purple-600 text-white' 
                                  : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                              }`}
                            >
                              {pageNum}
                            </Button>
                          );
                        })}
                      </div>

                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === totalPages}
                        className="border-slate-200"
                      >
                        Next
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>

                    {/* Jump to page */}
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-slate-600">Go to:</span>
                      <input
                        type="number"
                        min="1"
                        max={totalPages}
                        value={currentPage}
                        onChange={(e) => {
                          const page = parseInt(e.target.value);
                          if (page >= 1 && page <= totalPages) {
                            handlePageChange(page);
                          }
                        }}
                        className="w-16 px-2 py-1 border border-slate-200 rounded text-center focus:ring-2 focus:ring-purple-200 focus:border-purple-300"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </div>

      <Footer />
    </div>
  );
};

export default BrowsePage;