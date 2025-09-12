/**
 * CATALORO - Reviews and Ratings Section
 * Phase 2: Enhanced Social Commerce - Review system for listings and sellers
 */

import React, { useState, useEffect } from 'react';
import { Star, ThumbsUp, MessageCircle, User, Camera, Shield, Flag } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function ReviewsSection({ listingId, sellerId, className = "" }) {
  const [reviews, setReviews] = useState([]);
  const [overallRating, setOverallRating] = useState(0);
  const [reviewCounts, setReviewCounts] = useState({ 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 });
  const [isLoading, setIsLoading] = useState(true);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [newReview, setNewReview] = useState({
    rating: 5,
    title: '',
    content: '',
    images: [],
    wouldRecommend: true
  });
  const [sortBy, setSortBy] = useState('newest');
  const [filterBy, setFilterBy] = useState('all');

  const { user } = useAuth();
  const { showToast } = useNotifications();

  useEffect(() => {
    loadReviews();
  }, [listingId, sortBy, filterBy]);

  const loadReviews = async () => {
    try {
      setIsLoading(true);
      
      // Mock data for demonstration - replace with actual API call
      const mockReviews = [
        {
          id: '1',
          userId: 'user1',
          userName: 'Sarah Johnson',
          userAvatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b47c?w=50&h=50&fit=crop&crop=face',
          rating: 5,
          title: 'Excellent product and fast shipping!',
          content: 'This item exceeded my expectations. The quality is outstanding and the seller was very responsive to my questions. Highly recommended!',
          images: ['https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=200&h=200&fit=crop'],
          wouldRecommend: true,
          verified: true,
          helpfulCount: 12,
          createdAt: '2024-01-15T10:30:00Z',
          sellerResponse: {
            content: 'Thank you for the wonderful review! We really appreciate your business.',
            createdAt: '2024-01-16T09:15:00Z'
          }
        },
        {
          id: '2',
          userId: 'user2',
          userName: 'Mike Chen',
          userAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=50&h=50&fit=crop&crop=face',
          rating: 4,
          title: 'Good value for money',
          content: 'The item is as described and arrived in good condition. Packaging could be better, but overall satisfied with the purchase.',
          images: [],
          wouldRecommend: true,
          verified: true,
          helpfulCount: 8,
          createdAt: '2024-01-10T14:20:00Z'
        },
        {
          id: '3',
          userId: 'user3',
          userName: 'Emma Rodriguez',
          userAvatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=50&h=50&fit=crop&crop=face',
          rating: 5,
          title: 'Perfect condition, exactly as advertised',
          content: 'Amazing seller! The item was exactly as described and shipped super fast. Will definitely buy from this seller again.',
          images: ['https://images.unsplash.com/photo-1560472355-536de3962603?w=200&h=200&fit=crop'],
          wouldRecommend: true,
          verified: true,
          helpfulCount: 15,
          createdAt: '2024-01-08T16:45:00Z'
        }
      ];

      setReviews(mockReviews);
      
      // Calculate overall rating
      const totalRating = mockReviews.reduce((sum, review) => sum + review.rating, 0);
      setOverallRating(totalRating / mockReviews.length);
      
      // Calculate rating distribution
      const counts = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };
      mockReviews.forEach(review => {
        counts[review.rating]++;
      });
      setReviewCounts(counts);
      
    } catch (error) {
      console.error('Error loading reviews:', error);
      showToast('Failed to load reviews', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    
    if (!user) {
      showToast('Please login to write a review', 'error');
      return;
    }

    try {
      // Mock submission - replace with actual API call
      const reviewData = {
        ...newReview,
        listingId,
        sellerId,
        userId: user.id,
        userName: user.full_name || user.username,
        userAvatar: user.avatar,
        verified: user.verified || false,
        createdAt: new Date().toISOString()
      };

      // Add to reviews list (in real app, this would be done server-side)
      setReviews(prev => [reviewData, ...prev]);
      
      // Reset form
      setNewReview({
        rating: 5,
        title: '',
        content: '',
        images: [],
        wouldRecommend: true
      });
      setShowReviewForm(false);
      
      showToast('Review submitted successfully!', 'success');
      
    } catch (error) {
      console.error('Error submitting review:', error);
      showToast('Failed to submit review', 'error');
    }
  };

  const handleHelpful = async (reviewId) => {
    try {
      // Mock API call
      setReviews(prev => prev.map(review => 
        review.id === reviewId 
          ? { ...review, helpfulCount: (review.helpfulCount || 0) + 1 }
          : review
      ));
      showToast('Thank you for your feedback!', 'success');
    } catch (error) {
      console.error('Error marking review as helpful:', error);
    }
  };

  const renderStars = (rating, size = 'w-4 h-4') => {
    return (
      <div className="flex">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`${size} ${
              star <= rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    );
  };

  const renderRatingDistribution = () => {
    const totalReviews = reviews.length;
    
    return (
      <div className="space-y-2">
        {[5, 4, 3, 2, 1].map((rating) => (
          <div key={rating} className="flex items-center space-x-2">
            <span className="text-sm font-medium w-3">{rating}</span>
            <Star className="w-4 h-4 text-yellow-400 fill-current" />
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div
                className="bg-yellow-400 h-2 rounded-full"
                style={{
                  width: totalReviews > 0 ? `${(reviewCounts[rating] / totalReviews) * 100}%` : '0%'
                }}
              />
            </div>
            <span className="text-sm text-gray-600 w-8">{reviewCounts[rating]}</span>
          </div>
        ))}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="border-b border-gray-200 pb-4">
                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
                  <div className="flex-1">
                    <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold text-gray-900">Reviews & Ratings</h3>
          {user && (
            <button
              onClick={() => setShowReviewForm(!showReviewForm)}
              className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors duration-200"
            >
              Write Review
            </button>
          )}
        </div>

        {/* Rating Summary */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="text-center">
            <div className="text-4xl font-bold text-gray-900 mb-2">
              {overallRating.toFixed(1)}
            </div>
            <div className="flex items-center justify-center mb-2">
              {renderStars(Math.round(overallRating), 'w-5 h-5')}
            </div>
            <p className="text-sm text-gray-600">{reviews.length} reviews</p>
          </div>
          
          <div>
            {renderRatingDistribution()}
          </div>
        </div>
      </div>

      {/* Review Form */}
      {showReviewForm && (
        <div className="p-6 bg-gray-50 border-b border-gray-200">
          <form onSubmit={handleSubmitReview} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rating
              </label>
              <div className="flex space-x-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setNewReview(prev => ({ ...prev, rating: star }))}
                    className="focus:outline-none"
                  >
                    <Star
                      className={`w-8 h-8 ${
                        star <= newReview.rating 
                          ? 'text-yellow-400 fill-current' 
                          : 'text-gray-300 hover:text-yellow-300'
                      } transition-colors duration-200`}
                    />
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Review Title
              </label>
              <input
                type="text"
                value={newReview.title}
                onChange={(e) => setNewReview(prev => ({ ...prev, title: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Summarize your experience"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Review Content
              </label>
              <textarea
                value={newReview.content}
                onChange={(e) => setNewReview(prev => ({ ...prev, content: e.target.value }))}
                rows={4}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Share your experience with this product..."
                required
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="recommend"
                checked={newReview.wouldRecommend}
                onChange={(e) => setNewReview(prev => ({ ...prev, wouldRecommend: e.target.checked }))}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="recommend" className="ml-2 text-sm text-gray-700">
                I would recommend this product to others
              </label>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowReviewForm(false)}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
              >
                Submit Review
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="highest">Highest Rated</option>
              <option value="lowest">Lowest Rated</option>
              <option value="helpful">Most Helpful</option>
            </select>

            <select
              value={filterBy}
              onChange={(e) => setFilterBy(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Reviews</option>
              <option value="5">5 Stars</option>
              <option value="4">4 Stars</option>
              <option value="3">3 Stars</option>
              <option value="2">2 Stars</option>
              <option value="1">1 Star</option>
              <option value="verified">Verified Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Reviews List */}
      <div className="p-6">
        {reviews.length > 0 ? (
          <div className="space-y-6">
            {reviews.map((review) => (
              <div key={review.id} className="border-b border-gray-200 pb-6 last:border-b-0">
                <div className="flex items-start space-x-4">
                  <img
                    src={review.userAvatar}
                    alt={review.userName}
                    className="w-10 h-10 rounded-full object-cover"
                  />
                  
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium text-gray-900">{review.userName}</h4>
                        {review.verified && (
                          <div className="flex items-center text-green-600">
                            <Shield className="w-4 h-4 mr-1" />
                            <span className="text-xs font-medium">Verified</span>
                          </div>
                        )}
                      </div>
                      <span className="text-sm text-gray-500">
                        {new Date(review.createdAt).toLocaleDateString()}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2 mb-2">
                      {renderStars(review.rating)}
                      {review.wouldRecommend && (
                        <span className="text-xs text-green-600 font-medium">Recommends</span>
                      )}
                    </div>

                    <h5 className="font-medium text-gray-900 mb-2">{review.title}</h5>
                    <p className="text-gray-700 text-sm leading-relaxed mb-3">{review.content}</p>

                    {review.images && review.images.length > 0 && (
                      <div className="flex space-x-2 mb-3">
                        {review.images.map((image, index) => (
                          <img
                            key={index}
                            src={image}
                            alt={`Review ${index + 1}`}
                            className="w-20 h-20 object-cover rounded-lg cursor-pointer hover:opacity-80 transition-opacity duration-200"
                          />
                        ))}
                      </div>
                    )}

                    <div className="flex items-center space-x-4 text-sm">
                      <button
                        onClick={() => handleHelpful(review.id)}
                        className="flex items-center text-gray-600 hover:text-blue-600 transition-colors duration-200"
                      >
                        <ThumbsUp className="w-4 h-4 mr-1" />
                        Helpful ({review.helpfulCount || 0})
                      </button>
                      
                      <button className="flex items-center text-gray-600 hover:text-blue-600 transition-colors duration-200">
                        <MessageCircle className="w-4 h-4 mr-1" />
                        Reply
                      </button>
                      
                      <button className="flex items-center text-gray-600 hover:text-red-600 transition-colors duration-200">
                        <Flag className="w-4 h-4 mr-1" />
                        Report
                      </button>
                    </div>

                    {review.sellerResponse && (
                      <div className="mt-4 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                        <div className="flex items-center mb-2">
                          <User className="w-4 h-4 text-blue-600 mr-2" />
                          <span className="text-sm font-medium text-blue-900">Seller Response</span>
                          <span className="text-xs text-blue-700 ml-auto">
                            {new Date(review.sellerResponse.createdAt).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-sm text-blue-800">{review.sellerResponse.content}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <MessageCircle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">No Reviews Yet</h4>
            <p className="text-gray-600">Be the first to write a review for this product!</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ReviewsSection;