/**
 * CATALORO - Catalyst Reviews and Ratings Section
 * Phase 2: Enhanced Social Commerce - Specialized review system for chemical catalysts
 */

import React, { useState, useEffect } from 'react';
import { Star, ThumbsUp, MessageCircle, User, Camera, Shield, Flag, Beaker, Activity, BarChart3 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function CatalystReviewsSection({ listingId, sellerId, className = "" }) {
  const [reviews, setReviews] = useState([]);
  const [overallRating, setOverallRating] = useState(0);
  const [reviewCounts, setReviewCounts] = useState({ 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 });
  const [performanceMetrics, setPerformanceMetrics] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [newReview, setNewReview] = useState({
    rating: 5,
    title: '',
    content: '',
    technicalDetails: {
      activityRating: 5,
      selectivityRating: 5,
      stabilityRating: 5,
      reactionConditions: '',
      yieldAchieved: '',
      observations: ''
    },
    wouldRecommend: true
  });
  const [sortBy, setSortBy] = useState('newest');

  const { user } = useAuth();
  const { showToast } = useNotifications();

  useEffect(() => {
    loadReviews();
  }, [listingId, sortBy]);

  const loadReviews = async () => {
    try {
      setIsLoading(true);
      
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/reviews/listing/${listingId}?sort_by=${sortBy}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setReviews(data.reviews || []);
        setOverallRating(data.average_rating || 0);
        setReviewCounts(data.rating_distribution || { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 });
        
        // Calculate performance metrics from reviews
        if (data.reviews && data.reviews.length > 0) {
          const metrics = calculatePerformanceMetrics(data.reviews);
          setPerformanceMetrics(metrics);
        }
      }
    } catch (error) {
      console.error('Error loading reviews:', error);
      showToast('Failed to load reviews', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const calculatePerformanceMetrics = (reviewsData) => {
    const metricsSum = reviewsData.reduce((acc, review) => {
      const tech = review.technical_details || {};
      return {
        activity: acc.activity + (tech.activityRating || 0),
        selectivity: acc.selectivity + (tech.selectivityRating || 0),
        stability: acc.stability + (tech.stabilityRating || 0),
        count: acc.count + 1
      };
    }, { activity: 0, selectivity: 0, stability: 0, count: 0 });

    if (metricsSum.count === 0) return {};

    return {
      avgActivity: (metricsSum.activity / metricsSum.count).toFixed(1),
      avgSelectivity: (metricsSum.selectivity / metricsSum.count).toFixed(1),
      avgStability: (metricsSum.stability / metricsSum.count).toFixed(1),
      totalReviews: metricsSum.count
    };
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    
    if (!user) {
      showToast('Please login to write a review', 'error');
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/reviews/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          listing_id: listingId,
          seller_id: sellerId,
          user_id: user.id,
          user_name: user.full_name || user.username,
          user_avatar: user.avatar,
          ...newReview,
          technical_details: newReview.technicalDetails,
          verified: user.verified || false
        })
      });

      if (response.ok) {
        showToast('Review submitted successfully!', 'success');
        setNewReview({
          rating: 5,
          title: '',
          content: '',
          technicalDetails: {
            activityRating: 5,
            selectivityRating: 5,
            stabilityRating: 5,
            reactionConditions: '',
            yieldAchieved: '',
            observations: ''
          },
          wouldRecommend: true
        });
        setShowReviewForm(false);
        loadReviews(); // Reload reviews
      } else {
        throw new Error('Failed to create review');
      }
    } catch (error) {
      console.error('Error submitting review:', error);
      showToast('Failed to submit review', 'error');
    }
  };

  const handleHelpful = async (reviewId) => {
    if (!user) {
      showToast('Please login to mark reviews as helpful', 'info');
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/reviews/${reviewId}/helpful`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id })
      });

      if (response.ok) {
        showToast('Thank you for your feedback!', 'success');
        loadReviews(); // Reload to get updated helpful count
      }
    } catch (error) {
      console.error('Error marking review as helpful:', error);
      showToast('Failed to mark as helpful', 'error');
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

  const renderPerformanceBar = (value, maxValue = 5) => {
    const percentage = (value / maxValue) * 100;
    return (
      <div className="flex-1 bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-500 h-2 rounded-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
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
          <h3 className="text-xl font-semibold text-gray-900 flex items-center">
            <Beaker className="h-5 w-5 mr-2 text-blue-600" />
            Catalyst Performance Reviews
          </h3>
          {user && (
            <button
              onClick={() => setShowReviewForm(!showReviewForm)}
              className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors duration-200"
            >
              Write Technical Review
            </button>
          )}
        </div>

        {/* Rating Summary */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Overall Rating */}
          <div className="text-center">
            <div className="text-4xl font-bold text-gray-900 mb-2">
              {overallRating.toFixed(1)}
            </div>
            <div className="flex items-center justify-center mb-2">
              {renderStars(Math.round(overallRating), 'w-5 h-5')}
            </div>
            <p className="text-sm text-gray-600">{reviews.length} reviews</p>
          </div>
          
          {/* Rating Distribution */}
          <div className="space-y-2">
            {[5, 4, 3, 2, 1].map((rating) => (
              <div key={rating} className="flex items-center space-x-2">
                <span className="text-sm font-medium w-3">{rating}</span>
                <Star className="w-4 h-4 text-yellow-400 fill-current" />
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-yellow-400 h-2 rounded-full"
                    style={{
                      width: reviews.length > 0 ? `${(reviewCounts[rating] / reviews.length) * 100}%` : '0%'
                    }}
                  />
                </div>
                <span className="text-sm text-gray-600 w-8">{reviewCounts[rating]}</span>
              </div>
            ))}
          </div>

          {/* Performance Metrics */}
          {performanceMetrics.totalReviews > 0 && (
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-gray-700 flex items-center">
                <BarChart3 className="h-4 w-4 mr-1" />
                Avg Performance
              </h4>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-600">Activity</span>
                  <div className="flex items-center space-x-2 w-2/3">
                    {renderPerformanceBar(performanceMetrics.avgActivity)}
                    <span className="text-xs font-medium text-gray-700">{performanceMetrics.avgActivity}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-600">Selectivity</span>
                  <div className="flex items-center space-x-2 w-2/3">
                    {renderPerformanceBar(performanceMetrics.avgSelectivity)}
                    <span className="text-xs font-medium text-gray-700">{performanceMetrics.avgSelectivity}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-600">Stability</span>
                  <div className="flex items-center space-x-2 w-2/3">
                    {renderPerformanceBar(performanceMetrics.avgStability)}
                    <span className="text-xs font-medium text-gray-700">{performanceMetrics.avgStability}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Review Form */}
      {showReviewForm && (
        <div className="p-6 bg-gray-50 border-b border-gray-200">
          <form onSubmit={handleSubmitReview} className="space-y-6">
            {/* Overall Rating */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Overall Rating
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

            {/* Technical Performance Ratings */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-blue-50 rounded-lg">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Activity className="h-4 w-4 inline mr-1" />
                  Activity
                </label>
                <div className="flex space-x-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setNewReview(prev => ({ 
                        ...prev, 
                        technicalDetails: { ...prev.technicalDetails, activityRating: star }
                      }))}
                      className="focus:outline-none"
                    >
                      <Star
                        className={`w-5 h-5 ${
                          star <= newReview.technicalDetails.activityRating 
                            ? 'text-blue-500 fill-current' 
                            : 'text-gray-300 hover:text-blue-400'
                        } transition-colors duration-200`}
                      />
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Selectivity
                </label>
                <div className="flex space-x-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setNewReview(prev => ({ 
                        ...prev, 
                        technicalDetails: { ...prev.technicalDetails, selectivityRating: star }
                      }))}
                      className="focus:outline-none"
                    >
                      <Star
                        className={`w-5 h-5 ${
                          star <= newReview.technicalDetails.selectivityRating 
                            ? 'text-green-500 fill-current' 
                            : 'text-gray-300 hover:text-green-400'
                        } transition-colors duration-200`}
                      />
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stability
                </label>
                <div className="flex space-x-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      onClick={() => setNewReview(prev => ({ 
                        ...prev, 
                        technicalDetails: { ...prev.technicalDetails, stabilityRating: star }
                      }))}
                      className="focus:outline-none"
                    >
                      <Star
                        className={`w-5 h-5 ${
                          star <= newReview.technicalDetails.stabilityRating 
                            ? 'text-purple-500 fill-current' 
                            : 'text-gray-300 hover:text-purple-400'
                        } transition-colors duration-200`}
                      />
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Review Title and Content */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Review Title
                </label>
                <input
                  type="text"
                  value={newReview.title}
                  onChange={(e) => setNewReview(prev => ({ ...prev, title: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Summarize your experience with this catalyst"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Yield Achieved (%)
                </label>
                <input
                  type="text"
                  value={newReview.technicalDetails.yieldAchieved}
                  onChange={(e) => setNewReview(prev => ({ 
                    ...prev, 
                    technicalDetails: { ...prev.technicalDetails, yieldAchieved: e.target.value }
                  }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., 95%"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reaction Conditions
              </label>
              <input
                type="text"
                value={newReview.technicalDetails.reactionConditions}
                onChange={(e) => setNewReview(prev => ({ 
                  ...prev, 
                  technicalDetails: { ...prev.technicalDetails, reactionConditions: e.target.value }
                }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., 150°C, 2 bar H2, 4 hours"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Detailed Review
              </label>
              <textarea
                value={newReview.content}
                onChange={(e) => setNewReview(prev => ({ ...prev, content: e.target.value }))}
                rows={4}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Share your detailed experience with this catalyst..."
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Observations
              </label>
              <textarea
                value={newReview.technicalDetails.observations}
                onChange={(e) => setNewReview(prev => ({ 
                  ...prev, 
                  technicalDetails: { ...prev.technicalDetails, observations: e.target.value }
                }))}
                rows={2}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Any other technical observations..."
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
                I would recommend this catalyst to other researchers
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
          <h4 className="text-sm font-medium text-gray-700">Reviews ({reviews.length})</h4>
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
                    src={review.user_avatar || '/api/placeholder/40/40'}
                    alt={review.user_name}
                    className="w-10 h-10 rounded-full object-cover"
                  />
                  
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <h4 className="font-medium text-gray-900">{review.user_name}</h4>
                        {review.verified && (
                          <div className="flex items-center text-green-600">
                            <Shield className="w-4 h-4 mr-1" />
                            <span className="text-xs font-medium">Verified</span>
                          </div>
                        )}
                      </div>
                      <span className="text-sm text-gray-500">
                        {new Date(review.created_at).toLocaleDateString()}
                      </span>
                    </div>

                    <div className="flex items-center space-x-4 mb-2">
                      {renderStars(review.rating)}
                      {review.would_recommend && (
                        <span className="text-xs text-green-600 font-medium bg-green-50 px-2 py-1 rounded-full">
                          Recommends
                        </span>
                      )}
                    </div>

                    <h5 className="font-medium text-gray-900 mb-2">{review.title}</h5>
                    <p className="text-gray-700 text-sm leading-relaxed mb-3">{review.content}</p>

                    {/* Technical Details */}
                    {review.technical_details && (
                      <div className="bg-gray-50 rounded-lg p-4 mb-3">
                        <h6 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
                          <Beaker className="h-4 w-4 mr-1" />
                          Technical Performance
                        </h6>
                        
                        <div className="grid grid-cols-3 gap-4 mb-3">
                          <div className="text-center">
                            <div className="text-sm text-gray-600">Activity</div>
                            {renderStars(review.technical_details.activityRating || 0, 'w-3 h-3')}
                          </div>
                          <div className="text-center">
                            <div className="text-sm text-gray-600">Selectivity</div>
                            {renderStars(review.technical_details.selectivityRating || 0, 'w-3 h-3')}
                          </div>
                          <div className="text-center">
                            <div className="text-sm text-gray-600">Stability</div>
                            {renderStars(review.technical_details.stabilityRating || 0, 'w-3 h-3')}
                          </div>
                        </div>

                        {(review.technical_details.reactionConditions || review.technical_details.yieldAchieved) && (
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                            {review.technical_details.reactionConditions && (
                              <div>
                                <span className="font-medium text-gray-700">Conditions:</span>
                                <span className="ml-2 text-gray-600">{review.technical_details.reactionConditions}</span>
                              </div>
                            )}
                            {review.technical_details.yieldAchieved && (
                              <div>
                                <span className="font-medium text-gray-700">Yield:</span>
                                <span className="ml-2 text-gray-600">{review.technical_details.yieldAchieved}</span>
                              </div>
                            )}
                          </div>
                        )}

                        {review.technical_details.observations && (
                          <div className="mt-2 text-sm">
                            <span className="font-medium text-gray-700">Observations:</span>
                            <p className="text-gray-600 mt-1">{review.technical_details.observations}</p>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="flex items-center space-x-4 text-sm">
                      <button
                        onClick={() => handleHelpful(review.id)}
                        className="flex items-center text-gray-600 hover:text-blue-600 transition-colors duration-200"
                      >
                        <ThumbsUp className="w-4 h-4 mr-1" />
                        Helpful ({review.helpful_count || 0})
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

                    {review.seller_response && (
                      <div className="mt-4 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                        <div className="flex items-center mb-2">
                          <User className="w-4 h-4 text-blue-600 mr-2" />
                          <span className="text-sm font-medium text-blue-900">Seller Response</span>
                          <span className="text-xs text-blue-700 ml-auto">
                            {new Date(review.seller_response.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-sm text-blue-800">{review.seller_response.content}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Beaker className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">No Reviews Yet</h4>
            <p className="text-gray-600">Be the first to write a technical review for this catalyst!</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default CatalystReviewsSection;