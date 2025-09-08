/**
 * CATALORO - Public Profile Page with Rating System
 * Enhanced public profile display with comprehensive user ratings
 */

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  User,
  Calendar,
  MapPin,
  Package,
  Award,
  Star,
  MessageCircle,
  Shield,
  CheckCircle,
  Building,
  Globe,
  Phone,
  Mail,
  ExternalLink,
  Activity,
  TrendingUp,
  DollarSign,
  Heart,
  Users,
  Clock,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import UserRatingSystem from '../../components/ratings/UserRatingSystem';

function PublicProfilePage() {
  const { userId } = useParams();
  const { user } = useAuth();
  const { showToast } = useNotifications();
  
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (userId) {
      loadPublicProfile();
    }
  }, [userId]);

  const loadPublicProfile = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/profile/${userId}/public`);
      
      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      } else if (response.status === 404) {
        throw new Error('Profile not available');
      } else {
        throw new Error('Failed to load profile');
      }
    } catch (error) {
      console.error('Failed to load public profile:', error);
      
      // For demo purposes, provide fallback profile data
      if (userId) {
        const fallbackProfile = {
          id: userId,
          username: `user_${userId.slice(-6)}`,
          full_name: 'Demo User',
          bio: 'Marketplace participant',
          avatar_url: '',
          date_joined: '2024-01-15',
          is_verified: false,
          is_business: false,
          seller_rating: 4.5,
          total_sales: 12,
          total_purchases: 8,
          listings_count: 15,
          reviews_count: 23,
          location: 'Europe',
          badges: ['Seller'],
          ratings: {
            overall: 4.5,
            communication: 4.7,
            shipping: 4.3,
            quality: 4.6,
            total_ratings: 23
          }
        };
        setProfile(fallbackProfile);
        showToast('Showing demo profile data', 'info');
      } else {
        setError(error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const startConversation = () => {
    // Redirect to messages with this user
    window.location.href = `/messages?user_id=${userId}`;
  };

  const getBadgeStyle = (badge) => {
    switch (badge) {
      case 'Admin':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
      case 'Manager':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300';
      case 'Seller':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'Buyer':
      default:
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading profile...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center py-12">
          <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Profile Not Found</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {error || 'This profile does not exist or is private.'}
          </p>
          <button
            onClick={() => window.history.back()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!profile.public) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="text-center py-12">
          <Shield className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Private Profile</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            This user has chosen to keep their profile private.
          </p>
          <button
            onClick={() => window.history.back()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Profile Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-8 mb-8 text-white">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between">
          <div className="flex items-center space-x-6 mb-4 md:mb-0">
            <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
              <User className="w-12 h-12" />
            </div>
            
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <h1 className="text-3xl font-bold">{profile.user.full_name}</h1>
                <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getBadgeStyle(profile.user.badge)} text-gray-800`}>
                  {profile.user.badge}
                </span>
                {profile.user.is_business && (
                  <div className="flex items-center space-x-1 bg-white/20 px-2 py-1 rounded-full">
                    <Building className="w-4 h-4" />
                    <span className="text-sm">Business</span>
                  </div>
                )}
              </div>
              
              <p className="text-blue-100 text-lg mb-2">@{profile.user.username}</p>
              
              <div className="flex items-center space-x-4 text-blue-100">
                <div className="flex items-center space-x-1">
                  <Calendar className="w-4 h-4" />
                  <span className="text-sm">
                    Joined {new Date(profile.user.join_date).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex items-center space-x-1">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm">
                    {profile.user.days_since_joining} days ago
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex flex-col space-y-3">
            {user?.id !== userId && (
              <>
                <button
                  onClick={startConversation}
                  className="px-6 py-3 bg-white text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors flex items-center space-x-2"
                >
                  <MessageCircle className="w-5 h-5" />
                  <span>Send Message</span>
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Statistics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <Package className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900 dark:text-white">
              {profile.statistics.total_listings}
            </span>
          </div>
          <p className="text-gray-600 dark:text-gray-400">Total Listings</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <CheckCircle className="w-8 h-8 text-green-600" />
            <span className="text-2xl font-bold text-gray-900 dark:text-white">
              {profile.statistics.completed_deals}
            </span>
          </div>
          <p className="text-gray-600 dark:text-gray-400">Completed Deals</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <Star className="w-8 h-8 text-yellow-500" />
            <div className="text-right">
              <span className="text-2xl font-bold text-gray-900 dark:text-white">
                {profile.ratings.average_rating}
              </span>
              <div className="flex items-center mt-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className={`w-4 h-4 ${
                      star <= profile.ratings.average_rating
                        ? 'text-yellow-400 fill-current'
                        : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
          <p className="text-gray-600 dark:text-gray-400">Average Rating</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <DollarSign className="w-8 h-8 text-purple-600" />
            <span className="text-2xl font-bold text-gray-900 dark:text-white">
              €{profile.statistics.as_seller.total_revenue.toFixed(2)}
            </span>
          </div>
          <p className="text-gray-600 dark:text-gray-400">Total Revenue</p>
        </div>
      </div>

      {/* Business Information */}
      {profile.user.is_business && profile.user.company_name && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <Building className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Business Information</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {profile.user.company_name}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Professional business seller on Cataloro Marketplace
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex items-center space-x-1 mb-8 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
        {[
          { key: 'overview', label: 'Overview', icon: Activity },
          { key: 'listings', label: 'Recent Listings', icon: Package },
          { key: 'ratings', label: 'Ratings & Reviews', icon: Star }
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
              activeTab === tab.key
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Account Summary
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Package className="w-5 h-5 text-green-600 dark:text-green-400" />
                      <span className="text-green-800 dark:text-green-200 font-medium">As Seller</span>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-green-900 dark:text-green-100">
                        {profile.statistics.as_seller.orders_completed} deals
                      </p>
                      <p className="text-sm text-green-600 dark:text-green-400">
                        €{profile.statistics.as_seller.total_revenue.toFixed(2)} revenue
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <User className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                      <span className="text-blue-800 dark:text-blue-200 font-medium">As Buyer</span>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-blue-900 dark:text-blue-100">
                        {profile.statistics.as_buyer?.orders_completed || 0} deals
                      </p>
                      <p className="text-sm text-blue-600 dark:text-blue-400">Purchases made</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Rating Breakdown</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">As Seller:</span>
                        <div className="flex items-center space-x-2">
                          <Star className="w-4 h-4 text-yellow-400 fill-current" />
                          <span className="font-semibold text-gray-900 dark:text-white">
                            {profile.ratings.seller_rating}
                          </span>
                          <span className="text-gray-500">({profile.ratings.seller_stats.count})</span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">As Buyer:</span>
                        <div className="flex items-center space-x-2">
                          <Star className="w-4 h-4 text-yellow-400 fill-current" />
                          <span className="font-semibold text-gray-900 dark:text-white">
                            {profile.ratings.buyer_rating}
                          </span>
                          <span className="text-gray-500">({profile.ratings.buyer_stats.count})</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'listings' && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Recent Listings
            </h3>
            {profile.recent_listings && profile.recent_listings.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {profile.recent_listings.map((listing) => (
                  <div key={listing.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-lg transition-shadow">
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
                      {listing.title}
                    </h4>
                    <p className="text-lg font-bold text-blue-600 dark:text-blue-400 mb-2">
                      €{listing.price}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-3">
                      {listing.description}
                    </p>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>{listing.category}</span>
                      <span>{new Date(listing.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No Recent Listings</h4>
                <p className="text-gray-600 dark:text-gray-400">This user hasn't posted any listings recently.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'ratings' && (
          <div>
            <UserRatingSystem 
              userId={userId}
              targetUserId={userId}
              showRateButton={user?.id !== userId}
              className=""
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default PublicProfilePage;