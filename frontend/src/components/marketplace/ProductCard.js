import React, { useState } from 'react';
import { Heart, Eye, MapPin, Clock, Star } from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Card, CardContent } from '../ui/card';
import { useAuth } from '../../context/AuthContext';
import { favoritesAPI } from '../../services/api';
import { useToast } from '../../hooks/use-toast';
import { formatCurrency, getImageUrl, formatDate } from '../../utils/helpers';

const ProductCard = ({ listing, onFavoriteToggle, isInFavorites = false }) => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [isFavorited, setIsFavorited] = useState(isInFavorites);
  const [favoriteId, setFavoriteId] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFavoriteToggle = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!user) {
      toast({
        title: "Login Required",
        description: "Please login to add favorites",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      if (isFavorited) {
        // Remove from favorites
        await favoritesAPI.removeFavorite(favoriteId);
        setIsFavorited(false);
        setFavoriteId(null);
        toast({
          title: "Removed from favorites",
          description: "Item removed successfully"
        });
      } else {
        // Add to favorites
        const response = await favoritesAPI.addFavorite(listing.id);
        setIsFavorited(true);
        setFavoriteId(response.data.id);
        toast({
          title: "Added to favorites",
          description: "Item saved successfully"
        });
      }
      
      if (onFavoriteToggle) {
        onFavoriteToggle(listing.id, !isFavorited);
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
      toast({
        title: "Error",
        description: "Failed to update favorites",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getConditionColor = (condition) => {
    switch (condition?.toLowerCase()) {
      case 'new': return 'bg-green-100 text-green-800';
      case 'like new': return 'bg-blue-100 text-blue-800';
      case 'good': return 'bg-yellow-100 text-yellow-800';
      case 'fair': return 'bg-orange-100 text-orange-800';
      case 'poor': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getListingTypeIcon = (type) => {
    return type === 'auction' ? '🔨' : '💰';
  };

  return (
    <Card className="group cursor-pointer transition-all duration-300 hover:shadow-lg hover:-translate-y-1 border-0 shadow-sm">
      <CardContent className="p-0">
        {/* Image Container */}
        <div className="relative overflow-hidden rounded-t-lg">
          {listing.images && listing.images.length > 0 ? (
            <img
              src={getImageUrl(listing.images[0])}
              alt={listing.title}
              className="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-105"
            />
          ) : (
            <div className="w-full h-48 bg-gradient-to-br from-purple-100 to-blue-100 flex items-center justify-center">
              <div className="text-4xl opacity-50">📦</div>
            </div>
          )}
          
          {/* Favorite Button */}
          <button
            onClick={handleFavoriteToggle}
            disabled={loading}
            className="absolute top-3 right-3 p-2 rounded-full bg-white/90 backdrop-blur-sm shadow-md hover:bg-white transition-colors"
          >
            <Heart 
              className={`h-4 w-4 transition-colors ${
                isFavorited ? 'fill-red-500 text-red-500' : 'text-gray-600 hover:text-red-500'
              }`} 
            />
          </button>

          {/* Listing Type Badge */}
          <div className="absolute top-3 left-3">
            <Badge className="bg-white/90 backdrop-blur-sm text-purple-700 border-0">
              {getListingTypeIcon(listing.listing_type)} {listing.listing_type === 'auction' ? 'Auction' : 'Buy Now'}
            </Badge>
          </div>

          {/* Views Badge */}
          {listing.views > 0 && (
            <div className="absolute bottom-3 right-3">
              <Badge variant="secondary" className="bg-black/50 text-white border-0">
                <Eye className="h-3 w-3 mr-1" />
                {listing.views}
              </Badge>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-4">
          {/* Title */}
          <h3 className="font-semibold text-slate-900 mb-2 line-clamp-2 group-hover:text-purple-600 transition-colors">
            {listing.title}
          </h3>

          {/* Price */}
          <div className="flex items-center justify-between mb-3">
            <div className="text-2xl font-bold text-purple-600">
              {formatCurrency(listing.price)}
            </div>
            {listing.listing_type === 'auction' && listing.current_bid && (
              <div className="text-sm text-slate-500">
                Bid: {formatCurrency(listing.current_bid)}
              </div>
            )}
          </div>

          {/* Category and Condition */}
          <div className="flex items-center gap-2 mb-3">
            <Badge variant="outline" className="text-xs">
              {listing.category}
            </Badge>
            <Badge className={`text-xs ${getConditionColor(listing.condition)}`}>
              {listing.condition}
            </Badge>
          </div>

          {/* Location and Time */}
          <div className="flex items-center justify-between text-sm text-slate-500 mb-3">
            <div className="flex items-center gap-1">
              <MapPin className="h-3 w-3" />
              <span className="truncate">{listing.location || 'Location not specified'}</span>
            </div>
            <div className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              <span>{formatDate(listing.created_at)}</span>
            </div>
          </div>

          {/* Seller Info */}
          {listing.seller_name && (
            <div className="flex items-center justify-between text-sm text-slate-600 mb-3">
              <span>By {listing.seller_name}</span>
              {listing.seller_rating && (
                <div className="flex items-center gap-1">
                  <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                  <span>{listing.seller_rating.toFixed(1)}</span>
                </div>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Button 
              className="flex-1 bg-purple-600 hover:bg-purple-700 text-white"
              size="sm"
            >
              {listing.listing_type === 'auction' ? 'Place Bid' : 'Buy Now'}
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              className="border-purple-200 text-purple-600 hover:bg-purple-50"
            >
              <Eye className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ProductCard;