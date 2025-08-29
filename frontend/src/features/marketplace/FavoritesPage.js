/**
 * CATALORO - Favorites Page
 * Display user's favorite listings
 */

import React, { useState, useEffect } from 'react';
import { Heart, Trash2, ExternalLink } from 'lucide-react';
import { marketplaceService } from '../../services/marketplaceService';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function FavoritesPage() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const { showToast } = useNotifications();

  useEffect(() => {
    if (user?.id) {
      fetchFavorites();
    }
  }, [user?.id]);

  const fetchFavorites = async () => {
    try {
      setLoading(true);
      const data = await marketplaceService.getFavorites(user.id);
      setFavorites(data);
    } catch (error) {
      showToast('Failed to load favorites', 'error');
      console.error('Failed to fetch favorites:', error);
      // Show dummy data for demo
      setFavorites([
        {
          id: '1',
          title: 'Vintage Camera',
          description: 'Beautiful vintage camera in excellent condition',
          price: 450.00,
          category: 'Photography',
          images: ['https://images.unsplash.com/photo-1606983340077-e4cd46b37f18?w=400'],
          created_at: new Date().toISOString()
        },
        {
          id: '2',
          title: 'Designer Watch',
          description: 'Luxury timepiece with leather strap',
          price: 1200.00,
          category: 'Accessories',
          images: ['https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400'],
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveFromFavorites = async (listingId) => {
    try {
      await marketplaceService.removeFromFavorites(user.id, listingId);
      setFavorites(favorites.filter(item => item.id !== listingId));
      showToast('Removed from favorites', 'success');
    } catch (error) {
      showToast('Failed to remove from favorites', 'error');
    }
  };

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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">My Favorites</h1>
        <p className="text-gray-600">Items you've saved for later</p>
      </div>

      {/* Favorites Grid */}
      {favorites.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Heart className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No favorites yet</h3>
          <p className="text-gray-600 mb-6">Start browsing and save items you love</p>
          <button className="cataloro-button-primary">
            Browse Marketplace
          </button>
        </div>
      ) : (
        <>
          <div className="mb-6">
            <p className="text-gray-600">You have {favorites.length} favorite items</p>
          </div>
          
          <div className="listings-grid">
            {favorites.map((item) => (
              <FavoriteCard
                key={item.id}
                item={item}
                onRemove={handleRemoveFromFavorites}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

// Favorite Card Component
function FavoriteCard({ item, onRemove }) {
  return (
    <div className="listing-tile">
      {/* Image */}
      <div className="relative">
        <img
          src={item.images?.[0] || '/api/placeholder/400/300'}
          alt={item.title}
          className="listing-image"
        />
        
        {/* Remove from Favorites Button */}
        <button
          onClick={() => onRemove(item.id)}
          className="absolute top-3 right-3 p-2 bg-white bg-opacity-90 rounded-full hover:bg-opacity-100 transition-all duration-200 text-red-500 hover:text-red-600"
        >
          <Heart className="w-5 h-5 fill-current" />
        </button>
      </div>

      {/* Content */}
      <div className="listing-content">
        <h3 className="listing-title">{item.title}</h3>
        <p className="listing-price">${item.price.toFixed(2)}</p>
        <p className="listing-description">{item.description}</p>
        
        <div className="flex items-center justify-between mt-4">
          <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
            {item.category}
          </span>
          <button className="flex items-center text-blue-600 hover:text-blue-700 text-sm font-medium">
            <ExternalLink className="w-4 h-4 mr-1" />
            View
          </button>
        </div>

        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex space-x-2">
            <button className="flex-1 cataloro-button-primary text-sm py-2">
              Contact Seller
            </button>
            <button
              onClick={() => onRemove(item.id)}
              className="px-3 py-2 text-gray-400 hover:text-red-500 transition-colors duration-200"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FavoritesPage;