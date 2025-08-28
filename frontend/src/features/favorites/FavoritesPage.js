import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { favoritesAPI } from '../../services/api';
import { useToast } from '../../hooks/use-toast';
import Header from '../../components/layout/Header';
import Footer from '../../components/layout/Footer';
import ProductCard from '../../components/marketplace/ProductCard';
import { Card, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Heart, Trash2, Grid, List } from 'lucide-react';

const FavoritesPage = () => {
  const { user } = useAuth();
  const { toast } = useToast();

  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid');

  useEffect(() => {
    fetchFavorites();
  }, []);

  const fetchFavorites = async () => {
    try {
      setLoading(true);
      const response = await favoritesAPI.getFavorites();
      setFavorites(response.data || []);
    } catch (error) {
      console.error('Error fetching favorites:', error);
      toast({
        title: "Error",
        description: "Failed to load favorites. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFavoriteToggle = async (listingId, isNowFavorited) => {
    if (!isNowFavorited) {
      // Remove from favorites
      setFavorites(prev => prev.filter(fav => fav.listing.id !== listingId));
      toast({
        title: "Removed from favorites",
        description: "Item has been removed from your favorites"
      });
    }
  };

  const clearAllFavorites = async () => {
    if (favorites.length === 0) return;
    
    try {
      // Remove all favorites
      await Promise.all(favorites.map(fav => favoritesAPI.removeFavorite(fav.id)));
      setFavorites([]);
      toast({
        title: "All favorites cleared",
        description: "All items have been removed from your favorites"
      });
    } catch (error) {
      console.error('Error clearing favorites:', error);
      toast({
        title: "Error",
        description: "Failed to clear favorites. Please try again.",
        variant: "destructive"
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Heart className="h-8 w-8 text-red-500" />
            <h1 className="text-4xl font-light text-slate-900 tracking-tight">My Favorites</h1>
          </div>
          <p className="text-lg text-slate-600 font-light">
            Items you've saved for later
          </p>
        </div>

        {/* Controls */}
        {favorites.length > 0 && (
          <Card className="border-0 shadow-sm mb-6">
            <CardContent className="p-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                {/* Count */}
                <div className="text-sm text-slate-600">
                  {favorites.length} item{favorites.length !== 1 ? 's' : ''} in your favorites
                </div>

                {/* Actions */}
                <div className="flex items-center gap-4">
                  {/* Clear All */}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={clearAllFavorites}
                    className="border-red-200 text-red-600 hover:bg-red-50"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Clear All
                  </Button>

                  {/* View Mode Toggle */}
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
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center py-16">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
              <p className="mt-2 text-slate-600">Loading your favorites...</p>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && favorites.length === 0 && (
          <Card className="border-0 shadow-sm">
            <CardContent className="text-center py-16">
              <Heart className="h-16 w-16 mx-auto text-slate-400 mb-4" />
              <h3 className="text-xl font-semibold text-slate-700 mb-2">No favorites yet</h3>
              <p className="text-slate-500 mb-6">
                Start browsing and save items you're interested in
              </p>
              <Button
                onClick={() => window.location.href = '#/browse'}
                className="bg-purple-600 hover:bg-purple-700 text-white"
              >
                Browse Products
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Favorites Grid/List */}
        {!loading && favorites.length > 0 && (
          <div className={`
            ${viewMode === 'grid' 
              ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6' 
              : 'space-y-4'
            }
          `}>
            {favorites.map((favorite) => (
              <ProductCard
                key={favorite.id}
                listing={favorite.listing}
                onFavoriteToggle={handleFavoriteToggle}
                isInFavorites={true}
              />
            ))}
          </div>
        )}

        {/* Tips Section */}
        {!loading && favorites.length > 0 && (
          <Card className="border-0 shadow-sm bg-blue-50 mt-8">
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <Heart className="h-5 w-5 text-blue-600 mt-1" />
                <div>
                  <h4 className="font-medium text-blue-900 mb-2">Favorites Tips</h4>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Items in your favorites are saved privately - only you can see them</li>
                    <li>• You'll get notifications if the price drops on favorited items</li>
                    <li>• Keep track of items you're considering purchasing</li>
                    <li>• Favorites are synced across all your devices</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      <Footer />
    </div>
  );
};

export default FavoritesPage;