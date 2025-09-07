import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  ArrowRight, 
  Eye, 
  Heart,
  Star,
  RefreshCw
} from 'lucide-react';

const SimilarItemsPanel = ({ 
  listingId,
  currentUserId = null,
  limit = 4,
  onItemClick,
  className = ''
}) => {
  const [similarItems, setSimilarItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (listingId) {
      fetchSimilarItems();
    }
  }, [listingId, limit]);

  const fetchSimilarItems = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/v2/ai/similar/${listingId}?limit=${limit}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch similar items');
      }
      
      const data = await response.json();
      
      if (data.success) {
        setSimilarItems(data.similar_items || []);
      } else {
        throw new Error(data.error || 'Failed to load similar items');
      }
    } catch (error) {
      console.error('Failed to fetch similar items:', error);
      setError(error.message);
      setSimilarItems([]);
    } finally {
      setLoading(false);
    }
  };

  const trackInteraction = async (targetListingId, interactionType) => {
    if (!currentUserId) return;

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      await fetch(`${backendUrl}/v2/ai/interaction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: currentUserId,
          listing_id: targetListingId,
          interaction_type: interactionType,
          context: { 
            source: 'similar_items',
            original_listing: listingId
          }
        })
      });
    } catch (error) {
      console.error('Failed to track interaction:', error);
    }
  };

  const handleItemClick = async (item) => {
    await trackInteraction(item.listing.id, 'view');
    
    if (onItemClick) {
      onItemClick(item.listing);
    }
  };

  const formatPrice = (price, currency = 'EUR') => {
    const symbols = { 'EUR': '€', 'USD': '$', 'GBP': '£' };
    const symbol = symbols[currency] || currency;
    return `${symbol}${price?.toLocaleString() || 0}`;
  };

  const getSimilarityReasons = (reasons) => {
    if (!reasons || reasons.length === 0) return [];
    return reasons.slice(0, 2);
  };

  if (loading) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-600 ${className}`}>
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
            <Sparkles className="w-5 h-5 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Similar Items
          </h3>
        </div>
        
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Finding similar items...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-600 ${className}`}>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
              <Sparkles className="w-5 h-5 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Similar Items
            </h3>
          </div>
          
          <button
            onClick={fetchSimilarItems}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
        
        <div className="text-center py-8">
          <div className="text-red-500 mb-2">Failed to load similar items</div>
          <button
            onClick={fetchSimilarItems}
            className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  if (similarItems.length === 0) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-600 ${className}`}>
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
            <Sparkles className="w-5 h-5 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Similar Items
          </h3>
        </div>
        
        <div className="text-center py-8">
          <Sparkles className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No Similar Items Found
          </h4>
          <p className="text-gray-600 dark:text-gray-400">
            We couldn't find any items similar to this one.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-600 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
            <Sparkles className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Similar Items
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              You might also like these items
            </p>
          </div>
        </div>
        
        <button
          onClick={fetchSimilarItems}
          className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          title="Refresh similar items"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Similar Items Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {similarItems.map((item, index) => {
          const listing = item.listing;
          const similarityReasons = getSimilarityReasons(item.similarity_reasons);
          
          return (
            <div
              key={`similar-${listing.id}-${index}`}
              onClick={() => handleItemClick(item)}
              className="group bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 hover:bg-gray-100 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-600 hover:border-purple-300 dark:hover:border-purple-600 transition-all cursor-pointer"
            >
              {/* Item Image */}
              <div className="aspect-square bg-gray-200 dark:bg-gray-600 rounded-lg mb-3 overflow-hidden">
                {listing.images && listing.images.length > 0 ? (
                  <img
                    src={listing.images[0]}
                    alt={listing.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Sparkles className="w-8 h-8 text-gray-400" />
                  </div>
                )}
              </div>

              {/* Item Details */}
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900 dark:text-white line-clamp-2 text-sm group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                  {listing.title || 'Untitled Listing'}
                </h4>
                
                <div className="flex items-center justify-between">
                  <span className="text-lg font-bold text-blue-600 dark:text-blue-400">
                    {formatPrice(listing.price)}
                  </span>
                  
                  {item.similarity_score && (
                    <div className="flex items-center space-x-1">
                      <Star className="w-3 h-3 text-yellow-500" />
                      <span className="text-xs text-gray-600 dark:text-gray-400">
                        {(item.similarity_score * 100).toFixed(0)}% match
                      </span>
                    </div>
                  )}
                </div>

                {/* Category */}
                {listing.category && (
                  <span className="inline-block px-2 py-1 text-xs bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded border">
                    {listing.category}
                  </span>
                )}

                {/* Similarity Reasons */}
                {similarityReasons.length > 0 && (
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    Similar: {similarityReasons.join(', ')}
                  </div>
                )}

                {/* Action Hint */}
                <div className="flex items-center justify-between pt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-500">
                    <Eye className="w-3 h-3" />
                    <span>View details</span>
                  </div>
                  <ArrowRight className="w-4 h-4 text-purple-500 transform group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* View More Link */}
      {similarItems.length >= limit && (
        <div className="mt-6 text-center">
          <button
            onClick={() => {
              // Track interest in more similar items
              trackInteraction(listingId, 'similar_items_expand');
              // You can implement navigation to a full similar items page here
            }}
            className="inline-flex items-center space-x-2 text-purple-600 dark:text-purple-400 hover:text-purple-800 dark:hover:text-purple-200 font-medium transition-colors"
          >
            <span>View more similar items</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
};

export default SimilarItemsPanel;