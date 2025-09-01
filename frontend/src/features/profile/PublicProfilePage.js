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
import { useAuth } from '../../context/AuthContext';
import { useMarketplace } from '../../context/MarketplaceContext';

function PublicProfilePage() {
  const { userId } = useParams();
  const { user: currentUser } = useAuth();
  const { allProducts } = useMarketplace();
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

  // Load interactions (messages and deals) with this user
  const loadUserInteractions = async (targetUserId) => {
    try {
      // Mock interaction data - in real app, this would fetch from backend
      const mockInteractions = {
        messages: [
          {
            id: '1',
            subject: 'Question about MacBook Pro',
            last_message: 'Is this still available?',
            created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
          },
          {
            id: '2', 
            subject: 'Pickup arrangement',
            last_message: 'When can we meet?',
            created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
          }
        ],
        deals: [
          {
            id: '1',
            item_title: 'iPhone 13 Pro',
            amount: 699,
            status: 'completed',
            date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
          }
        ]
      };
      
      setInteractions({
        ...mockInteractions,
        totalInteractions: mockInteractions.messages.length + mockInteractions.deals.length
      });
    } catch (error) {
      console.error('Failed to load user interactions:', error);
    }
  };

  useEffect(() => {
    const loadPublicProfile = async () => {
      try {
        setLoading(true);
        
        // Fetch real user data from backend
        let fetchedUser = null;
        
        try {
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${userId}`);
          if (response.ok) {
            fetchedUser = await response.json();
          }
        } catch (error) {
          console.log('Backend API not available, using fallback data');
        }
        
        // If no backend data, use current user data for own profile or create realistic demo data
        if (!fetchedUser) {
          if (userId === currentUser?.id) {
            // Show current user's actual data
            fetchedUser = {
              id: currentUser.id,
              full_name: currentUser.full_name || 'Demo User',
              username: currentUser.username || 'demo_user',
              email: currentUser.email,
              bio: currentUser.bio || "Passionate marketplace enthusiast with years of experience in buying and selling quality items.",
              avatar_url: currentUser.avatar_url || '',
              city: currentUser.city || 'Berlin',
              country: currentUser.country || 'Germany',
              date_joined: currentUser.date_joined || '2023-06-15',
              verified: currentUser.verified || true,
              is_business: currentUser.is_business || false,
              company_name: currentUser.company_name || '',
              seller_rating: currentUser.seller_rating || 4.7,
              phone: currentUser.phone || '+49 123 456 789',
              publicProfile: true,
              showEmail: false,
              showPhone: false
            };
          } else {
            // Create realistic demo data for other users
            const demoProfiles = {
              'user1': {
                full_name: 'Sarah Johnson',
                username: 'sash_admin',
                bio: 'Tech enthusiast and gadget collector. Selling quality electronics and vintage items.',
                city: 'Munich',
                verified: true,
                is_business: false,
                seller_rating: 4.8
              },
              'user2': {
                full_name: 'Mike Electronics',
                username: 'mike_tech',
                bio: 'Electronics retailer with 5+ years experience. Specializing in laptops and mobile devices.',
                city: 'Hamburg',
                verified: true,
                is_business: true,
                company_name: 'TechStore Hamburg',
                seller_rating: 4.9
              }
            };
            
            const demoProfile = demoProfiles[userId] || demoProfiles['user1'];
            fetchedUser = {
              id: userId,
              full_name: demoProfile.full_name,
              username: demoProfile.username,
              email: `${demoProfile.username}@example.com`,
              bio: demoProfile.bio,
              avatar_url: '',
              city: demoProfile.city,
              country: 'Germany',
              date_joined: '2023-06-15',
              verified: demoProfile.verified,
              is_business: demoProfile.is_business,
              company_name: demoProfile.company_name || '',
              seller_rating: demoProfile.seller_rating,
              phone: '+49 123 456 789',
              publicProfile: true,
              showEmail: false,
              showPhone: false
            };
          }
        }
        
        setProfileUser(fetchedUser);
        
        // Load interactions with this user if it's not current user
        if (userId !== currentUser?.id) {
          await loadUserInteractions(userId);
        }
        
        // Calculate user listings and stats
        const listings = allProducts.filter(p => 
          p.seller === fetchedUser.username || 
          p.seller === fetchedUser.full_name ||
          p.seller_id === userId
        );
        
        setUserListings(listings.slice(0, 6)); // Show first 6 listings
        
        const stats = {
          totalListings: listings.length,
          activeListings: listings.filter(p => p.inStock !== false).length,
          totalSales: Math.floor(Math.random() * 50) + 10,
          avgRating: fetchedUser.seller_rating,
          responseRate: Math.floor(Math.random() * 20) + 80,
          memberSince: fetchedUser.date_joined,
          lastActive: 'Active today'
        };
        
        setUserStats(stats);
        
      } catch (error) {
        console.error('Failed to load public profile:', error);
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      loadPublicProfile();
    }
  }, [userId, allProducts]);

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
                  {profileUser.full_name}
                </h1>
                
                <div className="flex items-center justify-center lg:justify-start space-x-2 mt-2 lg:mt-0">
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
                
                {profileUser.showEmail && (
                  <a
                    href={`mailto:${profileUser.email}`}
                    className="cataloro-button-secondary flex items-center justify-center"
                  >
                    <Mail className="w-5 h-5 mr-2" />
                    Send Email
                  </a>
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
          <div className="lg:col-span-1 space-y-8">
            
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