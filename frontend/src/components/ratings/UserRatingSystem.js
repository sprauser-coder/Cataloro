/**
 * CATALORO - User Rating System Component
 * Transaction-based user-to-user ratings with comprehensive statistics
 */

import React, { useState, useEffect } from 'react';
import { 
  Star,
  Award,
  TrendingUp,
  Shield,
  CheckCircle,
  User,
  Calendar,
  MessageCircle,
  X,
  Send,
  AlertCircle,
  BarChart3,
  Users,
  Package
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

// Rating Service
class RatingService {
  constructor(baseURL) {
    this.baseURL = baseURL || process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  }

  async createRating(ratingData) {
    const response = await fetch(`${this.baseURL}/api/user-ratings/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(ratingData)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create rating');
    }
    return response.json();
  }

  async getUserRatings(userId, asSeller = null, limit = 50) {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (asSeller !== null) params.append('as_seller', asSeller.toString());
    
    const response = await fetch(`${this.baseURL}/api/user-ratings/${userId}?${params}`);
    if (!response.ok) throw new Error('Failed to fetch ratings');
    return response.json();
  }

  async getRatingStats(userId) {
    const response = await fetch(`${this.baseURL}/api/user-ratings/${userId}/stats`);
    if (!response.ok) throw new Error('Failed to fetch rating stats');
    return response.json();
  }

  async canRateUser(userId, targetUserId) {
    const response = await fetch(`${this.baseURL}/api/user-ratings/can-rate/${userId}/${targetUserId}`);
    if (!response.ok) throw new Error('Failed to check rating availability');
    return response.json();
  }
}

// Star Rating Component
function StarRating({ rating, size = 'md', editable = false, onChange }) {
  const [hoverRating, setHoverRating] = useState(0);
  
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
    xl: 'w-8 h-8'
  };

  const handleClick = (value) => {
    if (editable && onChange) {
      onChange(value);
    }
  };

  const handleMouseEnter = (value) => {
    if (editable) {
      setHoverRating(value);
    }
  };

  const handleMouseLeave = () => {
    if (editable) {
      setHoverRating(0);
    }
  };

  return (
    <div className="flex items-center space-x-1">
      {[1, 2, 3, 4, 5].map((star) => {
        const filled = editable ? 
          (hoverRating >= star || (!hoverRating && rating >= star)) :
          rating >= star;
        
        return (
          <button
            key={star}
            type="button"
            onClick={() => handleClick(star)}
            onMouseEnter={() => handleMouseEnter(star)}
            onMouseLeave={handleMouseLeave}
            disabled={!editable}
            className={`${sizeClasses[size]} ${
              editable ? 'cursor-pointer hover:scale-110 transition-transform' : 'cursor-default'
            } ${filled ? 'text-yellow-400 fill-current' : 'text-gray-300 dark:text-gray-600'}`}
          >
            <Star className="w-full h-full" />
          </button>
        );
      })}
    </div>
  );
}

// Rating Statistics Display
function RatingStats({ stats, className = '' }) {
  if (!stats || stats.total_ratings === 0) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <Star className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No ratings yet</h3>
        <p className="text-gray-600 dark:text-gray-400">This user hasn't received any ratings yet.</p>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Overall Rating */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-2">
          <span className="text-4xl font-bold text-gray-900 dark:text-white mr-2">
            {stats.average_rating}
          </span>
          <StarRating rating={stats.average_rating} size="lg" />
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          Based on {stats.total_ratings} rating{stats.total_ratings !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Rating Distribution */}
      <div className="mb-8">
        <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-4">Rating Distribution</h4>
        <div className="space-y-2">
          {[5, 4, 3, 2, 1].map((star) => {
            const count = stats.rating_distribution[star] || 0;
            const percentage = stats.total_ratings > 0 ? (count / stats.total_ratings) * 100 : 0;
            
            return (
              <div key={star} className="flex items-center space-x-3">
                <span className="text-sm text-gray-600 dark:text-gray-400 w-8">{star}★</span>
                <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-yellow-400 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <span className="text-sm text-gray-600 dark:text-gray-400 w-8 text-right">{count}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Seller vs Buyer Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Package className="w-4 h-4 text-green-600 dark:text-green-400" />
            <span className="text-sm font-medium text-green-800 dark:text-green-200">As Seller</span>
          </div>
          <div className="flex items-center space-x-2">
            <StarRating rating={stats.seller_rating} size="sm" />
            <span className="text-lg font-bold text-green-900 dark:text-green-100">
              {stats.seller_rating}
            </span>
          </div>
          <p className="text-xs text-green-600 dark:text-green-400 mt-1">
            {stats.seller_stats.count} rating{stats.seller_stats.count !== 1 ? 's' : ''}
          </p>
        </div>

        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <User className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span className="text-sm font-medium text-blue-800 dark:text-blue-200">As Buyer</span>
          </div>
          <div className="flex items-center space-x-2">
            <StarRating rating={stats.buyer_rating} size="sm" />
            <span className="text-lg font-bold text-blue-900 dark:text-blue-100">
              {stats.buyer_rating}
            </span>
          </div>
          <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
            {stats.buyer_stats.count} rating{stats.buyer_stats.count !== 1 ? 's' : ''}
          </p>
        </div>
      </div>
    </div>
  );
}

// Individual Rating Display
function RatingCard({ rating, className = '' }) {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 ${className}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
            <User className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="font-medium text-gray-900 dark:text-white">
              {rating.rater?.full_name || rating.rater?.username || 'Unknown User'}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              @{rating.rater?.username || 'unknown'}
            </p>
          </div>
        </div>
        
        <div className="text-right">
          <StarRating rating={rating.rating} size="sm" />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {new Date(rating.created_at).toLocaleDateString()}
          </p>
        </div>
      </div>

      {rating.comment && (
        <div className="mb-3">
          <p className="text-gray-700 dark:text-gray-300 text-sm">{rating.comment}</p>
        </div>
      )}

      <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
        <div className="flex items-center space-x-4">
          <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
            rating.rating_type === 'seller' 
              ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
              : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
          }`}>
            {rating.rating_type === 'seller' ? 'As Seller' : 'As Buyer'}
          </span>
          
          {rating.is_verified && (
            <div className="flex items-center space-x-1 text-green-600 dark:text-green-400">
              <CheckCircle className="w-3 h-3" />
              <span>Verified Transaction</span>
            </div>
          )}
        </div>
        
        {rating.listing_title && (
          <span className="truncate max-w-32" title={rating.listing_title}>
            {rating.listing_title}
          </span>
        )}
      </div>
    </div>
  );
}

// Rating Form Modal
function RatingModal({ isOpen, onClose, targetUser, availableTransactions, onSubmit }) {
  const [selectedTransaction, setSelectedTransaction] = useState('');
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (availableTransactions?.length === 1) {
      setSelectedTransaction(availableTransactions[0].transaction_id);
    }
  }, [availableTransactions]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedTransaction) {
      return;
    }

    setSubmitting(true);
    try {
      await onSubmit({
        transaction_id: selectedTransaction,
        rating,
        comment: comment.trim()
      });
      onClose();
      setRating(5);
      setComment('');
      setSelectedTransaction('');
    } catch (error) {
      console.error('Failed to submit rating:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md mx-4 shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">Rate User</h3>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {/* User Info */}
          <div className="flex items-center space-x-3 mb-6 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
              <User className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="font-medium text-gray-900 dark:text-white">
                {targetUser?.full_name || targetUser?.username || 'Unknown User'}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                @{targetUser?.username || 'unknown'}
              </p>
            </div>
          </div>

          {/* Transaction Selection */}
          {availableTransactions?.length > 1 && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Select Transaction
              </label>
              <select
                value={selectedTransaction}
                onChange={(e) => setSelectedTransaction(e.target.value)}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Select a transaction</option>
                {availableTransactions.map((transaction) => (
                  <option key={transaction.transaction_id} value={transaction.transaction_id}>
                    Transaction from {new Date(transaction.created_at).toLocaleDateString()}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Rating Input */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Your Rating
            </label>
            <div className="flex items-center justify-center space-x-2">
              <StarRating 
                rating={rating} 
                size="xl" 
                editable={true} 
                onChange={setRating}
              />
              <span className="text-2xl font-bold text-gray-900 dark:text-white ml-4">
                {rating}
              </span>
            </div>
          </div>

          {/* Comment */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Comment (Optional)
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Share your experience with this user..."
              rows={4}
              className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              maxLength={500}
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {comment.length}/500 characters
            </p>
          </div>

          {/* Submit Button */}
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!selectedTransaction || submitting}
              className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                selectedTransaction && !submitting
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl'
                  : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
              }`}
            >
              {submitting ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent animate-spin rounded-full"></div>
                  <span>Submitting...</span>
                </div>
              ) : (
                'Submit Rating'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Main User Rating System Component
function UserRatingSystem({ userId, targetUserId, showRateButton = false, className = '' }) {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const [stats, setStats] = useState(null);
  const [ratings, setRatings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [canRate, setCanRate] = useState(null);
  const [targetUserInfo, setTargetUserInfo] = useState(null);

  const ratingService = new RatingService();

  useEffect(() => {
    if (userId) {
      loadRatings();
    }
  }, [userId, activeTab]);

  useEffect(() => {
    if (showRateButton && user && targetUserId) {
      checkCanRate();
    }
  }, [showRateButton, user, targetUserId]);

  const loadRatings = async () => {
    try {
      setLoading(true);
      const [statsData, ratingsData] = await Promise.all([
        ratingService.getRatingStats(userId),
        ratingService.getUserRatings(
          userId, 
          activeTab === 'seller' ? true : activeTab === 'buyer' ? false : null
        )
      ]);
      
      setStats(statsData);
      setRatings(ratingsData);
    } catch (error) {
      console.error('Failed to load ratings:', error);
      showToast('Failed to load ratings', 'error');
    } finally {
      setLoading(false);
    }
  };

  const checkCanRate = async () => {
    try {
      const result = await ratingService.canRateUser(user.id, targetUserId);
      setCanRate(result);
      
      // Get target user info for modal
      if (result.can_rate) {
        // You might want to fetch user info from a separate endpoint
        setTargetUserInfo({ username: 'target_user', full_name: 'Target User' });
      }
    } catch (error) {
      console.error('Failed to check rating availability:', error);
      setCanRate({ can_rate: false, reason: 'Error checking rating availability' });
    }
  };

  const handleSubmitRating = async (ratingData) => {
    try {
      await ratingService.createRating({
        rater_id: user.id,
        rated_user_id: targetUserId,
        ...ratingData
      });
      
      showToast('Rating submitted successfully!', 'success');
      setShowRatingModal(false);
      
      // Refresh ratings if viewing the same user
      if (userId === targetUserId) {
        loadRatings();
      }
      
      // Refresh can rate status
      checkCanRate();
    } catch (error) {
      showToast(error.message || 'Failed to submit rating', 'error');
      throw error;
    }
  };

  if (loading) {
    return (
      <div className={`flex items-center justify-center py-12 ${className}`}>
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading ratings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Rate Button */}
      {showRateButton && canRate && (
        <div className="mb-6">
          {canRate.can_rate ? (
            <button
              onClick={() => setShowRatingModal(true)}
              className="w-full px-4 py-3 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-lg font-medium hover:from-yellow-600 hover:to-orange-600 transition-all duration-200 flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl"
            >
              <Star className="w-5 h-5" />
              <span>Rate This User</span>
            </button>
          ) : (
            <div className="w-full px-4 py-3 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded-lg text-center border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-center space-x-2">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm">{canRate.reason}</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Statistics */}
      <RatingStats stats={stats} className="mb-8" />

      {/* Tabs */}
      <div className="flex items-center justify-center mb-6">
        <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-1 flex space-x-1">
          {[
            { key: 'all', label: 'All Ratings', count: stats?.total_ratings || 0 },
            { key: 'seller', label: 'as Seller', count: stats?.seller_stats?.count || 0 },
            { key: 'buyer', label: 'as Buyer', count: stats?.buyer_stats?.count || 0 }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                activeTab === tab.key
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              {tab.label} ({tab.count})
            </button>
          ))}
        </div>
      </div>

      {/* Ratings List */}
      <div className="space-y-4">
        {ratings.length === 0 ? (
          <div className="text-center py-12">
            <Star className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              No {activeTab === 'all' ? '' : activeTab} ratings yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              {activeTab === 'all' 
                ? 'This user hasn\'t received any ratings yet.'
                : `No ratings as ${activeTab} yet.`}
            </p>
          </div>
        ) : (
          ratings.map((rating) => (
            <RatingCard key={rating.id} rating={rating} />
          ))
        )}
      </div>

      {/* Rating Modal */}
      <RatingModal
        isOpen={showRatingModal}
        onClose={() => setShowRatingModal(false)}
        targetUser={targetUserInfo}
        availableTransactions={canRate?.available_transactions}
        onSubmit={handleSubmitRating}
      />
    </div>
  );
}

export default UserRatingSystem;
export { StarRating, RatingStats, RatingCard };