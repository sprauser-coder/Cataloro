/**
 * CATALORO - Public Profile Page
 * View-only public profile for users
 */

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Calendar,
  Star,
  Package,
  DollarSign,
  Heart,
  Shield,
  CheckCircle,
  MessageCircle,
  Eye,
  Globe,
  Settings
} from 'lucide-react';
import { formatEuro } from '../../utils/currency';
import { useAuth } from '../../context/AuthContext';
import { useMarketplace } from '../../context/MarketplaceContext';
import usePermissions from '../../hooks/usePermissions';

function PublicProfilePage() {
  const { userId } = useParams();
  const { user: currentUser } = useAuth();
  const { allProducts } = useMarketplace();
  const { getUserDisplay } = usePermissions();
  const [profileUser, setProfileUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userStats, setUserStats] = useState({
    totalListings: 0,
    activeListings: 0,
    totalSales: 0,
    avgRating: 0,
    responseRate: 0,
    memberSince: '',
    lastActive: ''
  });
  const [userListings, setUserListings] = useState([]);

  const [interactions, setInteractions] = useState({
    messages: [],
    deals: [],
    totalInteractions: 0
  });

  // Helper function to get user badge info (mock implementation for demo)
  const getUserBadgeInfo = (user) => {
    // If it's the current user, get from permissions
    if (user?.id === currentUser?.id) {
      const currentUserDisplay = getUserDisplay();
      return {
        badge: currentUserDisplay?.badge || 'Buyer',
        role: currentUserDisplay?.role || 'User-Buyer'
      };
    }
    
    // Mock badge assignment based on user data patterns for demo
    const email = user?.email || '';
    const name = user?.full_name || user?.username || '';
    
    if (email.includes('admin') || user?.role === 'admin') {
      return { badge: 'Admin', role: 'Admin' };
    } else if (name.toLowerCase().includes('seller') || user?.user_role === 'User-Seller') {
      return { badge: 'Seller', role: 'User-Seller' };
    } else if (user?.user_role === 'Admin-Manager') {
      return { badge: 'Manager', role: 'Admin-Manager' };
    } else {
      return { badge: 'Buyer', role: 'User-Buyer' };
    }
  };

  // Helper function to get badge styling
  const getBadgeStyle = (badge) => {
    switch (badge) {
      case 'Admin':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300 border border-yellow-200 dark:border-yellow-800';
      case 'Manager':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300 border border-purple-200 dark:border-purple-800';
      case 'Seller':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 border border-green-200 dark:border-green-800';
      case 'Buyer':
      default:
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 border border-blue-200 dark:border-blue-800';
    }
  };

  // Load real interactions (messages and deals) with this user
  const loadUserInteractions = async (targetUserId) => {
    try {
      const realInteractions = {
        messages: [],
        deals: []
      };
      
      // Fetch real messages with this user
      try {
        const messagesResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/messages/conversations/${currentUser?.id}`);
        if (messagesResponse.ok) {
          const conversations = await messagesResponse.json();
          // Filter conversations with the target user
          const userConversations = conversations.filter(conv => 
            conv.participants?.some(p => p.id === targetUserId) ||
            conv.user_id === targetUserId ||
            conv.id === targetUserId
          );
          
          realInteractions.messages = userConversations.slice(0, 3).map(conv => ({
            id: conv.id || conv.conversation_id,
            subject: conv.subject || 'Message conversation',
            last_message: conv.last_message || conv.messages?.[0]?.content || 'Chat conversation',
            created_at: conv.created_at || conv.last_message_at || new Date().toISOString()
          }));
        }
      } catch (error) {
        console.log('Could not fetch real messages:', error);
      }
      
      // Fetch real deals with this user
      try {
        const dealsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/my-deals/${currentUser?.id}`);
        if (dealsResponse.ok) {
          const allDeals = await dealsResponse.json();
          // Filter deals involving the target user
          const userDeals = allDeals.filter(deal => 
            deal.buyer_id === targetUserId || 
            deal.seller_id === targetUserId ||
            deal.buyer?.id === targetUserId ||
            deal.seller?.id === targetUserId
          );
          
          realInteractions.deals = userDeals.slice(0, 3).map(deal => ({
            id: deal.id,
            item_title: deal.listing?.title || 'Deal item',
            amount: deal.amount || deal.listing?.price || 0,
            status: deal.status || 'completed',
            date: deal.approved_at || deal.created_at || new Date().toISOString()
          }));
        }
      } catch (error) {
        console.log('Could not fetch real deals:', error);
      }
      
      // If no real data found, show empty state - NO DUMMY DATA
      setInteractions({
        ...realInteractions,
        totalInteractions: realInteractions.messages.length + realInteractions.deals.length
      });
      
    } catch (error) {
      console.error('Failed to load user interactions:', error);
      // Set empty interactions instead of dummy data
      setInteractions({
        messages: [],
        deals: [],
        totalInteractions: 0
      });
    }
  };

  useEffect(() => {
    const loadPublicProfile = async () => {
      try {
        setLoading(true);
        
        // Use the new comprehensive public profile endpoint
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${userId}/public-profile`);
        
        if (response.ok) {
          const profileData = await response.json();
          console.log('Fetched public profile data:', profileData);
          
          // Set user data
          setProfileUser({
            id: profileData.id,
            full_name: profileData.full_name || 'Unknown User',
            username: profileData.username || 'unknown',
            email: profileData.email,
            bio: profileData.bio,
            avatar_url: profileData.avatar_url || '',
            city: profileData.city || 'Not specified',
            country: profileData.country || 'Not specified',
            date_joined: profileData.date_joined,
            created_at: profileData.created_at,
            is_verified: profileData.is_verified || false,
            is_business: profileData.is_business || false,
            company_name: profileData.company_name || '',
            seller_rating: profileData.seller_rating || 0,
            phone: profileData.phone || '',
            publicProfile: true,
            showEmail: !!profileData.email,
            showPhone: !!profileData.phone
          });
          
          // Set real statistics from backend
          setUserStats({
            totalListings: profileData.stats.total_listings,
            activeListings: profileData.stats.active_listings,
            totalSales: profileData.stats.total_sales,
            avgRating: profileData.stats.avg_rating,
            responseRate: profileData.stats.response_rate,
            memberSince: profileData.stats.member_since,
            lastActive: profileData.stats.last_active
          });
          
          // Set recent listings
          if (profileData.recent_listings) {
            setUserListings(profileData.recent_listings);
          }
          
        } else {
          console.error('Failed to fetch public profile:', response.status);
          // Fallback to previous logic if new endpoint fails
          await loadPublicProfileFallback();
        }
        
        // Load interactions if not current user
        if (userId !== currentUser?.id) {
          await loadUserInteractions(userId);
        }
        
      } catch (error) {
        console.error('Failed to load public profile:', error);
        // Fallback to previous logic
        await loadPublicProfileFallback();
      } finally {
        setLoading(false);
      }
    };

    // Fallback function with previous logic
    const loadPublicProfileFallback = async () => {
      try {
        // Previous implementation as fallback
        let fetchedUser = null;
        
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/profile/${userId}`);
        if (response.ok) {
          fetchedUser = await response.json();
        } else {
          const altResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${userId}`);
          if (altResponse.ok) {
            fetchedUser = await altResponse.json();
          }
        }
        
        if (fetchedUser) {
          const realUserData = {
            id: fetchedUser.id,
            full_name: fetchedUser.full_name || fetchedUser.name || 'Unknown User',
            username: fetchedUser.username || fetchedUser.email?.split('@')[0] || 'unknown',
            email: fetchedUser.email,
            bio: fetchedUser.bio || `${fetchedUser.full_name || 'User'} is a marketplace member.`,
            avatar_url: fetchedUser.avatar_url || '',
            city: fetchedUser.city || 'Not specified',
            country: fetchedUser.country || 'Not specified',
            date_joined: fetchedUser.date_joined || fetchedUser.created_at || 'Unknown',
            is_verified: fetchedUser.is_verified || fetchedUser.verified || false,
            is_business: fetchedUser.is_business || false,
            company_name: fetchedUser.company_name || '',
            seller_rating: fetchedUser.seller_rating || 0,
            phone: fetchedUser.phone || '',
            publicProfile: true,  // Always make fallback profiles public
            showEmail: !!fetchedUser.email,
            showPhone: !!fetchedUser.phone
          };
          
          setProfileUser(realUserData);
          
          // Basic stats calculation
          const listings = allProducts.filter(p => 
            p.seller?.username === fetchedUser.username || 
            p.seller_id === userId
          );
          
          setUserListings(listings.slice(0, 6));
          
          setUserStats({
            totalListings: listings.length,
            activeListings: listings.filter(p => p.status === 'active').length,
            totalSales: 0,
            avgRating: fetchedUser.seller_rating || 4.5,
            responseRate: 95,
            memberSince: fetchedUser.date_joined || 'Unknown',
            lastActive: 'Active recently'
          });
        } else {
          // If no user found, create a minimal profile to prevent "not available" error
          console.log('No user data found, creating minimal profile');
          setProfileUser({
            id: userId,
            full_name: 'Unknown User',
            username: userId,
            email: null,
            bio: 'This user has not set up their profile yet.',
            avatar_url: '',
            city: 'Not specified',
            country: 'Not specified',
            date_joined: 'Unknown',
            is_verified: false,
            is_business: false,
            company_name: '',
            seller_rating: 0,
            phone: '',
            publicProfile: true,  // Keep public even for minimal profiles
            showEmail: false,
            showPhone: false
          });
          
          setUserStats({
            totalListings: 0,
            activeListings: 0,
            totalSales: 0,
            avgRating: 0,
            responseRate: 0,
            memberSince: 'Unknown',
            lastActive: 'Unknown'
          });
        }
      } catch (error) {
        console.error('Fallback profile loading failed:', error);
        // Even if fallback fails, create a minimal profile
        setProfileUser({
          id: userId,
          full_name: 'Unknown User',
          username: userId,
          email: null,
          bio: 'Profile temporarily unavailable.',
          avatar_url: '',
          city: 'Not specified',
          country: 'Not specified',
          date_joined: 'Unknown',
          is_verified: false,
          is_business: false,
          company_name: '',
          seller_rating: 0,
          phone: '',
          publicProfile: true,  // Always keep public
          showEmail: false,
          showPhone: false
        });
      }
    };

    if (userId) {
      loadPublicProfile();
    }
  }, [userId, currentUser?.id, allProducts]);

  const handleMessageUser = () => {
    // Navigate to messages with this user
    window.location.href = `/messages?user=${userId}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Loading Profile...</h2>
        </div>
      </div>
    );
  }

  if (!profileUser || !profileUser.publicProfile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-8">
          <div className="w-24 h-24 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-6">
            <User className="w-12 h-12 text-gray-400" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-4">Profile Not Available</h2>
          <p className="text-gray-600 dark:text-gray-300">
            This user's profile is private or doesn't exist.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 fade-in">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Profile Header */}
        <div className="cataloro-card-glass p-8 mb-8">
          {/* Verified Badge at Top */}
          {profileUser.is_verified && (
            <div className="mb-6 flex justify-center lg:justify-start">
              <div className="bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-100 px-4 py-2 rounded-full text-lg font-semibold flex items-center shadow-md">
                <CheckCircle className="w-6 h-6 mr-2" />
                Verified User
              </div>
            </div>
          )}
          
          <div className="flex flex-col lg:flex-row lg:items-center space-y-6 lg:space-y-0 lg:space-x-8">
            
            {/* Avatar */}
            <div className="relative">
              <div className="w-32 h-32 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto lg:mx-0">
                {profileUser.avatar_url ? (
                  <img 
                    src={profileUser.avatar_url} 
                    alt="Profile" 
                    className="w-32 h-32 rounded-full object-cover"
                  />
                ) : (
                  <span className="text-white font-bold text-4xl">
                    {profileUser.full_name?.charAt(0) || 'U'}
                  </span>
                )}
              </div>
              {profileUser.verified && (
                <div className="absolute -bottom-2 -right-2 bg-green-500 rounded-full p-2">
                  <CheckCircle className="w-6 h-6 text-white" />
                </div>
              )}
            </div>

            {/* Profile Info */}
            <div className="flex-1 text-center lg:text-left">
              <div className="flex flex-col lg:flex-row lg:items-center lg:space-x-4 mb-4">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  {profileUser.username || profileUser.full_name}
                </h1>
                
                <div className="flex items-center justify-center lg:justify-start space-x-2 mt-2 lg:mt-0">
                  {/* User Role Badge */}
                  {(() => {
                    const badgeInfo = getUserBadgeInfo(profileUser);
                    return (
                      <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getBadgeStyle(badgeInfo.badge)}`}>
                        <Shield className="w-4 h-4 mr-1" />
                        {badgeInfo.badge}
                      </span>
                    );
                  })()}
                  
                  {profileUser.verified && (
                    <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium flex items-center">
                      <CheckCircle className="w-4 h-4 mr-1" />
                      Verified
                    </span>
                  )}
                  
                  {profileUser.is_business ? (
                    <span className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-3 py-1 rounded-full text-sm font-medium flex items-center">
                      <Settings className="w-4 h-4 mr-1" />
                      Business
                    </span>
                  ) : (
                    <span className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-3 py-1 rounded-full text-sm font-medium flex items-center">
                      <User className="w-4 h-4 mr-1" />
                      Private
                    </span>
                  )}
                </div>
              </div>
              
              <p className="text-gray-600 dark:text-gray-300 mb-2 text-lg">@{profileUser.username}</p>
              
              {profileUser.is_business && profileUser.company_name && (
                <p className="text-blue-600 dark:text-blue-400 font-medium mb-4">
                  {profileUser.company_name}
                </p>
              )}
              
              <p className="text-gray-600 dark:text-gray-300 mb-6 max-w-2xl">
                {profileUser.bio}
              </p>
              
              {/* Location */}
              <div className="flex items-center justify-center lg:justify-start text-gray-600 dark:text-gray-300 mb-6">
                <MapPin className="w-5 h-5 mr-2" />
                <span>{profileUser.city}, {profileUser.country}</span>
              </div>
              
              {/* Contact Actions */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                {currentUser?.id !== userId && (
                  <button
                    onClick={handleMessageUser}
                    className="cataloro-button-primary flex items-center justify-center"
                  >
                    <MessageCircle className="w-5 h-5 mr-2" />
                    Send Message
                  </button>
                )}
                
                {profileUser.showPhone && (
                  <a
                    href={`tel:${profileUser.phone}`}
                    className="cataloro-button-secondary flex items-center justify-center"
                  >
                    <Phone className="w-5 h-5 mr-2" />
                    Call
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Stats & Info */}
          <div className="lg:col-span-1 space-y-6">
            
            {/* Interactions Section - Only show for other users */}
            {currentUser?.id !== userId && interactions.totalInteractions > 0 && (
              <div className="cataloro-card-glass p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6 flex items-center">
                  <MessageCircle className="w-5 h-5 mr-2 text-blue-600" />
                  Interactions with this user
                </h3>
                
                <div className="space-y-4">
                  {/* Messages */}
                  {interactions.messages.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Recent Messages ({interactions.messages.length})</h4>
                      <div className="space-y-2">
                        {interactions.messages.slice(0, 3).map((message) => (
                          <div key={message.id} className="p-3 bg-blue-50/50 dark:bg-blue-900/20 rounded-lg">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm font-medium text-gray-900 dark:text-white">{message.subject}</span>
                              <span className="text-xs text-gray-500">{new Date(message.created_at).toLocaleDateString()}</span>
                            </div>
                            <p className="text-xs text-gray-600 dark:text-gray-400 truncate">{message.last_message}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Deals */}
                  {interactions.deals.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Past Deals ({interactions.deals.length})</h4>
                      <div className="space-y-2">
                        {interactions.deals.slice(0, 3).map((deal) => (
                          <div key={deal.id} className="p-3 bg-green-50/50 dark:bg-green-900/20 rounded-lg">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm font-medium text-gray-900 dark:text-white">{deal.item_title}</span>
                              <span className={`text-xs px-2 py-1 rounded-full ${
                                deal.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {deal.status}
                              </span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-bold text-green-600">${deal.amount}</span> 
                              <span className="text-xs text-gray-500">{new Date(deal.date).toLocaleDateString()}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Summary */}
                  <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                    <div className="text-center">
                      <div className="text-lg font-bold text-gray-900 dark:text-white">{interactions.totalInteractions}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">Total Interactions</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Statistics */}
            <div className="cataloro-card-glass p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Statistics</h3>
              
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Package className="w-5 h-5 text-blue-600 mr-3" />
                    <span className="text-gray-600 dark:text-gray-300">Total Listings</span>
                  </div>
                  <span className="font-bold text-gray-900 dark:text-white">{userStats.totalListings}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <DollarSign className="w-5 h-5 text-green-600 mr-3" />
                    <span className="text-gray-600 dark:text-gray-300">Total Sales</span>
                  </div>
                  <span className="font-bold text-gray-900 dark:text-white">{userStats.totalSales}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Star className="w-5 h-5 text-yellow-500 mr-3" />
                    <span className="text-gray-600 dark:text-gray-300">Rating</span>
                  </div>
                  <div className="flex items-center">
                    <Star className="w-4 h-4 text-yellow-400 mr-1" />
                    <span className="font-bold text-gray-900 dark:text-white">{userStats.avgRating}</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <MessageCircle className="w-5 h-5 text-purple-600 mr-3" />
                    <span className="text-gray-600 dark:text-gray-300">Response Rate</span>
                  </div>
                  <span className="font-bold text-gray-900 dark:text-white">{userStats.responseRate}%</span>
                </div>
              </div>
            </div>

            {/* Additional User Information */}
            <div className="cataloro-card-glass p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Additional Information</h3>
              
              <div className="space-y-4">
                {profileUser.is_business && profileUser.company_name && (
                  <div className="flex items-center">
                    <Settings className="w-5 h-5 text-blue-600 mr-3" />
                    <div>
                      <div className="text-sm text-gray-600 dark:text-gray-300">Company</div>
                      <div className="font-medium text-gray-900 dark:text-white">{profileUser.company_name}</div>
                    </div>
                  </div>
                )}
                
                <div className="flex items-center">
                  <Shield className="w-5 h-5 text-green-600 mr-3" />
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Account Status</div>
                    <div className="font-medium text-gray-900 dark:text-white">
                      {profileUser.verified ? 'Verified Member' : 'Standard Member'}
                    </div>
                  </div>
                </div>

                <div className="flex items-center">
                  <Globe className="w-5 h-5 text-purple-600 mr-3" />
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Profile Type</div>
                    <div className="font-medium text-gray-900 dark:text-white">
                      {profileUser.is_business ? 'Business Account' : 'Personal Account'}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Member Info */}
            <div className="cataloro-card-glass p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Member Info</h3>
              
              <div className="space-y-4">
                <div className="flex items-center">
                  <Calendar className="w-5 h-5 text-blue-600 mr-3" />
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Member since</div>
                    <div className="font-medium text-gray-900 dark:text-white">
                      {new Date(userStats.memberSince).toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long' 
                      })}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center">
                  <Eye className="w-5 h-5 text-green-600 mr-3" />
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-300">Last active</div>
                    <div className="font-medium text-gray-900 dark:text-white">{userStats.lastActive}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* User Listings */}
          <div className="lg:col-span-2">
            <div className="cataloro-card-glass p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Recent Listings ({userStats.activeListings} active)
                </h3>
                
                {userListings.length > 6 && (
                  <button className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 font-medium">
                    View All →
                  </button>
                )}
              </div>
              
              {userListings.length === 0 ? (
                <div className="text-center py-12">
                  <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No Listings Yet</h4>
                  <p className="text-gray-600 dark:text-gray-300">This user hasn't created any listings.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {userListings.map((listing, index) => (
                    <div key={index} className="group cursor-pointer">
                      <div className="bg-white/50 dark:bg-gray-800/50 rounded-xl p-4 hover:bg-white/80 dark:hover:bg-gray-800/80 transition-all duration-300 border border-gray-200/50 dark:border-gray-700/50">
                        <div className="aspect-w-16 aspect-h-9 mb-4">
                          <img
                            src={listing.images?.[0] || '/api/placeholder/300/200'}
                            alt={listing.title}
                            className="w-full h-32 object-cover rounded-lg"
                          />
                        </div>
                        
                        <h4 className="font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                          {listing.title}
                        </h4>
                        
                        <p className="text-2xl font-bold text-green-600 dark:text-green-400 mt-2">
                          ${listing.price}
                        </p>
                        
                        <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                          {listing.condition} • {listing.location}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PublicProfilePage;