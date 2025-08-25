import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Switch } from '../components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { useToast } from '../hooks/use-toast';
import { 
  User, Star, Calendar, MapPin, Heart, Package, ShoppingCart, 
  MessageCircle, Activity, Settings, HomeIcon, Eye, Edit, 
  TrendingUp, Award, Shield, Globe, Phone, Mail, Camera, 
  AlertTriangle, Zap, Bell, Clock, Euro, Upload, Plus
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

// Comprehensive Profile Component
const ComprehensiveProfile = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);

  // Enhanced Profile Data State
  const [profileData, setProfileData] = useState({
    user_id: user?.user_id || '',
    username: user?.username || '',
    full_name: user?.full_name || '',
    email: user?.email || '',
    phone: '',
    bio: '',
    location: '',
    website: '',
    joined_date: user?.created_at || '',
    is_business: false,
    company_name: '',
    country: '',
    vat_number: '',
    profile_picture_url: '',
    social_links: {
      facebook: '',
      twitter: '',
      instagram: '',
      linkedin: ''
    },
    preferences: {
      email_notifications: true,
      sms_notifications: false,
      marketing_emails: true,
      push_notifications: true,
      theme: 'light',
      language: 'en',
      currency: 'EUR',
      timezone: 'Europe/London'
    },
    verification: {
      email_verified: true,
      phone_verified: false,
      identity_verified: false,
      business_verified: false
    }
  });

  // Enhanced Statistics State
  const [stats, setStats] = useState({
    total_orders: 0,
    total_listings: 0,
    total_spent: 0,
    total_earned: 0,
    avg_rating: 0,
    total_reviews: 0,
    successful_transactions: 0,
    profile_views: 0,
    wishlist_items: 0,
    active_chats: 0,
    response_rate: 0,
    avg_response_time: 0,
    account_level: 'Bronze',
    trust_score: 85,
    badges_earned: 3
  });

  // Data Arrays
  const [orders, setOrders] = useState([]);
  const [listings, setListings] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [messages, setMessages] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [activityData, setActivityData] = useState([]);

  // Dialog States
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [profilePictureUploading, setProfilePictureUploading] = useState(false);

  // Password Data
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      await Promise.all([
        fetchProfileData(),
        fetchUserStats(),
        fetchUserOrders(),
        fetchUserListings(),
        fetchUserFavorites(),
        fetchUserMessages(),
        fetchUserReviews(),
        fetchActivityData()
      ]);
    } catch (error) {
      console.error('Error fetching profile data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProfileData = async () => {
    try {
      const response = await axios.get(`${API}/profile`);
      setProfileData(prev => ({ ...prev, ...response.data }));
    } catch (error) {
      console.error('Profile fetch error:', error);
    }
  };

  const fetchUserStats = async () => {
    try {
      const response = await axios.get(`${API}/profile/stats`);
      setStats(response.data);
    } catch (error) {
      // Enhanced mock stats for demonstration
      setStats({
        total_orders: 24,
        total_listings: 15,
        total_spent: 1847.50,
        total_earned: 1234.80,
        avg_rating: 4.8,
        total_reviews: 47,
        successful_transactions: 39,
        profile_views: 1205,
        wishlist_items: 67,
        active_chats: 5,
        response_rate: 96,
        avg_response_time: 1.8,
        account_level: 'Gold',
        trust_score: 92,
        badges_earned: 7
      });
    }
  };

  const fetchUserOrders = async () => {
    try {
      const response = await axios.get(`${API}/orders`);
      setOrders(response.data);
    } catch (error) {
      // Enhanced mock data
      setOrders([
        { id: '1', title: 'Vintage Leather Jacket', status: 'completed', total: 199.99, created_at: '2025-08-20', seller: 'RetroFashion' },
        { id: '2', title: 'MacBook Pro 2021', status: 'shipped', total: 1899.00, created_at: '2025-08-22', seller: 'TechDeals' },
        { id: '3', title: 'Designer Sunglasses', status: 'pending', total: 159.99, created_at: '2025-08-24', seller: 'LuxuryGoods' },
      ]);
    }
  };

  const fetchUserListings = async () => {
    try {
      const response = await axios.get(`${API}/listings/user`);
      setListings(response.data);
    } catch (error) {
      // Enhanced mock data
      setListings([
        { id: '1', title: 'Vintage Film Camera', status: 'active', price: 450, views: 234, watchers: 12, created_at: '2025-08-15' },
        { id: '2', title: 'Designer Handbag', status: 'sold', price: 320, views: 156, watchers: 8, created_at: '2025-08-10' },
        { id: '3', title: 'Gaming Chair', status: 'active', price: 180, views: 89, watchers: 5, created_at: '2025-08-18' },
      ]);
    }
  };

  const fetchUserFavorites = async () => {
    try {
      const response = await axios.get(`${API}/favorites`);
      setFavorites(response.data);
    } catch (error) {
      // Enhanced mock data
      setFavorites([
        { id: '1', title: 'Modern Sofa Set', price: 899, image: '/placeholder.jpg', seller: 'HomeDecor' },
        { id: '2', title: 'Wireless Headphones', price: 249, image: '/placeholder.jpg', seller: 'AudioTech' },
        { id: '3', title: 'Vintage Watch', price: 599, image: '/placeholder.jpg', seller: 'Timepieces' },
      ]);
    }
  };

  const fetchUserMessages = async () => {
    try {
      const response = await axios.get(`${API}/messages`);
      setMessages(response.data);
    } catch (error) {
      // Enhanced mock data
      setMessages([
        { id: '1', sender: 'John Doe', message: 'Is this item still available? I\'m very interested!', time: '2h ago', read: false, avatar: '/placeholder.jpg' },
        { id: '2', sender: 'Jane Smith', message: 'Thank you for the quick delivery! Excellent condition.', time: '1d ago', read: true, avatar: '/placeholder.jpg' },
        { id: '3', sender: 'Mike Wilson', message: 'Can you provide more details about the warranty?', time: '2d ago', read: false, avatar: '/placeholder.jpg' },
      ]);
    }
  };

  const fetchUserReviews = async () => {
    try {
      const response = await axios.get(`${API}/reviews/user`);
      setReviews(response.data);
    } catch (error) {
      // Enhanced mock data
      setReviews([
        { id: '1', reviewer: 'Alice Johnson', rating: 5, comment: 'Excellent seller! Fast shipping and item exactly as described. Highly recommended!', date: '2025-08-20', item: 'Vintage Camera' },
        { id: '2', reviewer: 'Bob Wilson', rating: 4, comment: 'Good product quality. Minor delay in shipping but overall satisfied.', date: '2025-08-18', item: 'Designer Jacket' },
        { id: '3', reviewer: 'Carol Davis', rating: 5, comment: 'Amazing communication and beautiful item. Will buy again!', date: '2025-08-15', item: 'Vintage Watch' },
      ]);
    }
  };

  const fetchActivityData = async () => {
    try {
      const response = await axios.get(`${API}/profile/activity`);
      setActivityData(response.data);
    } catch (error) {
      // Enhanced mock activity data
      setActivityData([
        { type: 'listing_created', title: 'Created new listing: Vintage Film Camera', time: '2 hours ago', icon: '📦', color: 'green' },
        { type: 'order_completed', title: 'Completed purchase of MacBook Pro', time: '5 hours ago', icon: '✅', color: 'blue' },
        { type: 'review_received', title: 'Received 5-star review from Alice Johnson', time: '1 day ago', icon: '⭐', color: 'yellow' },
        { type: 'message_sent', title: 'Replied to inquiry about vintage camera', time: '1 day ago', icon: '💬', color: 'purple' },
        { type: 'favorite_added', title: 'Added Modern Sofa Set to favorites', time: '2 days ago', icon: '❤️', color: 'red' },
        { type: 'profile_updated', title: 'Updated profile information', time: '3 days ago', icon: '👤', color: 'gray' },
        { type: 'badge_earned', title: 'Earned "Trusted Seller" badge', time: '1 week ago', icon: '🏆', color: 'gold' },
      ]);
    }
  };

  const updateProfile = async () => {
    try {
      await axios.put(`${API}/profile`, profileData);
      toast({
        title: "Success",
        description: "Profile updated successfully"
      });
      setIsEditing(false);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update profile",
        variant: "destructive"
      });
    }
  };

  const handleProfilePictureUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      toast({
        title: "Invalid file type",
        description: "Please select an image file",
        variant: "destructive"
      });
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      toast({
        title: "File too large",
        description: "Please select an image smaller than 5MB",
        variant: "destructive"
      });
      return;
    }

    setProfilePictureUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API}/profile/upload-picture`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setProfileData({
        ...profileData,
        profile_picture_url: response.data.profile_picture_url
      });

      toast({
        title: "Success",
        description: "Profile picture updated successfully"
      });
    } catch (error) {
      toast({
        title: "Upload failed",
        description: "Failed to upload profile picture",
        variant: "destructive"
      });
    } finally {
      setProfilePictureUploading(false);
    }
  };

  const getImageUrl = (url) => {
    if (!url) return null;
    return url.startsWith('http') ? url : `${BACKEND_URL}${url}`;
  };

  const getBadgeColor = (level) => {
    switch (level) {
      case 'Bronze': return 'bg-amber-100 text-amber-800';
      case 'Silver': return 'bg-gray-100 text-gray-800';
      case 'Gold': return 'bg-yellow-100 text-yellow-800';
      case 'Platinum': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Enhanced Profile Header */}
        <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 rounded-2xl p-8 text-white mb-8 shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <div className="relative">
                <div className="w-24 h-24 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center overflow-hidden ring-4 ring-white/30">
                  {profileData.profile_picture_url ? (
                    <img 
                      src={getImageUrl(profileData.profile_picture_url)}
                      alt="Profile"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <User className="w-12 h-12 text-white/70" />
                  )}
                </div>
                {/* Online Status Indicator */}
                <div className="absolute -bottom-1 -right-1 w-7 h-7 bg-green-500 rounded-full border-3 border-white flex items-center justify-center">
                  <Zap className="w-3 h-3 text-white" />
                </div>
                {/* Level Badge */}
                <div className={`absolute -top-2 -right-2 px-2 py-1 rounded-full text-xs font-bold ${getBadgeColor(stats.account_level)}`}>
                  {stats.account_level}
                </div>
              </div>
              <div>
                <h1 className="text-4xl font-bold mb-1">{profileData.full_name || profileData.username}</h1>
                <p className="text-blue-100 text-lg mb-2">@{profileData.username}</p>
                <div className="flex items-center space-x-6 text-sm">
                  <span className="flex items-center bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full">
                    <Calendar className="w-4 h-4 mr-2" />
                    Joined {new Date(profileData.joined_date).toLocaleDateString()}
                  </span>
                  <span className="flex items-center bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full">
                    <MapPin className="w-4 h-4 mr-2" />
                    {profileData.location || 'Location not set'}
                  </span>
                  <span className="flex items-center bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full">
                    <Shield className="w-4 h-4 mr-2" />
                    Trust Score: {stats.trust_score}%
                  </span>
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center justify-end space-x-3 mb-3">
                <div className="text-center">
                  <div className="text-3xl font-bold">{stats.avg_rating.toFixed(1)}</div>
                  <div className="flex items-center justify-center">
                    <Star className="w-4 h-4 text-yellow-300 fill-current mr-1" />
                    <span className="text-blue-100 text-sm">({stats.total_reviews})</span>
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold">{stats.successful_transactions}</div>
                  <div className="text-blue-100 text-sm">Transactions</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold">{stats.badges_earned}</div>
                  <div className="text-blue-100 text-sm">Badges</div>
                </div>
              </div>
              <div className="flex space-x-2">
                <Button 
                  variant="secondary" 
                  size="sm"
                  onClick={() => setIsEditing(!isEditing)}
                  className="bg-white/20 hover:bg-white/30 text-white border-white/30"
                >
                  <Edit className="w-4 h-4 mr-1" />
                  {isEditing ? 'Cancel Edit' : 'Edit Profile'}
                </Button>
                <Button 
                  variant="secondary" 
                  size="sm"
                  className="bg-white/20 hover:bg-white/30 text-white border-white/30"
                >
                  <Eye className="w-4 h-4 mr-1" />
                  Public View
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-8">
          {[
            { label: 'Profile Views', value: stats.profile_views, icon: Eye, color: 'blue' },
            { label: 'Active Listings', value: stats.total_listings, icon: Package, color: 'green' },
            { label: 'Total Orders', value: stats.total_orders, icon: ShoppingCart, color: 'purple' },
            { label: 'Favorites', value: stats.wishlist_items, icon: Heart, color: 'red' },
            { label: 'Response Rate', value: `${stats.response_rate}%`, icon: MessageCircle, color: 'orange' },
            { label: 'Avg Response', value: `${stats.avg_response_time}h`, icon: Clock, color: 'indigo' },
          ].map((stat, index) => {
            const Icon = stat.icon;
            return (
              <Card key={index} className={`hover:shadow-lg transition-shadow bg-gradient-to-br from-${stat.color}-50 to-${stat.color}-100 border-${stat.color}-200`}>
                <CardContent className="p-4 text-center">
                  <Icon className={`w-8 h-8 mx-auto mb-2 text-${stat.color}-600`} />
                  <div className={`text-2xl font-bold text-${stat.color}-800`}>{stat.value}</div>
                  <div className={`text-sm text-${stat.color}-600`}>{stat.label}</div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Navigation Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm">
            <TabsList className="grid grid-cols-4 lg:grid-cols-8 w-full h-auto p-1">
              {[
                { id: 'overview', label: 'Overview', icon: HomeIcon },
                { id: 'activity', label: 'Activity', icon: Activity },
                { id: 'listings', label: 'Listings', icon: Package },
                { id: 'orders', label: 'Orders', icon: ShoppingCart },
                { id: 'favorites', label: 'Favorites', icon: Heart },
                { id: 'messages', label: 'Messages', icon: MessageCircle },
                { id: 'reviews', label: 'Reviews', icon: Star },
                { id: 'settings', label: 'Settings', icon: Settings }
              ].map((tab) => {
                const Icon = tab.icon;
                return (
                  <TabsTrigger
                    key={tab.id}
                    value={tab.id}
                    className="flex flex-col items-center space-y-1 py-3 data-[state=active]:bg-blue-500 data-[state=active]:text-white"
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-xs">{tab.label}</span>
                    {tab.id === 'messages' && messages.filter(m => !m.read).length > 0 && (
                      <span className="absolute top-1 right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                        {messages.filter(m => !m.read).length}
                      </span>
                    )}
                  </TabsTrigger>
                );
              })}
            </TabsList>
          </div>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                {/* Profile Information Card */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <User className="w-5 h-5 mr-2" />
                      Profile Information
                    </CardTitle>
                    <CardDescription>Your personal details and preferences</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {isEditing ? (
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <Label htmlFor="fullName">Full Name</Label>
                            <Input
                              id="fullName"
                              value={profileData.full_name}
                              onChange={(e) => setProfileData({...profileData, full_name: e.target.value})}
                            />
                          </div>
                          <div>
                            <Label htmlFor="username">Username</Label>
                            <Input
                              id="username"
                              value={profileData.username}
                              onChange={(e) => setProfileData({...profileData, username: e.target.value})}
                            />
                          </div>
                        </div>
                        <div>
                          <Label htmlFor="bio">Bio</Label>
                          <Textarea
                            id="bio"
                            value={profileData.bio}
                            onChange={(e) => setProfileData({...profileData, bio: e.target.value})}
                            placeholder="Tell us about yourself..."
                            rows={3}
                          />
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <Label htmlFor="location">Location</Label>
                            <Input
                              id="location"
                              value={profileData.location}
                              onChange={(e) => setProfileData({...profileData, location: e.target.value})}
                              placeholder="City, Country"
                            />
                          </div>
                          <div>
                            <Label htmlFor="website">Website</Label>
                            <Input
                              id="website"
                              type="url"
                              value={profileData.website}
                              onChange={(e) => setProfileData({...profileData, website: e.target.value})}
                              placeholder="https://your-website.com"
                            />
                          </div>
                        </div>
                        <div className="flex justify-end space-x-2">
                          <Button variant="outline" onClick={() => setIsEditing(false)}>
                            Cancel
                          </Button>
                          <Button onClick={updateProfile}>
                            Save Changes
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm font-medium text-gray-500">Full Name</p>
                            <p className="text-lg">{profileData.full_name || 'Not provided'}</p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-500">Username</p>
                            <p className="text-lg">@{profileData.username}</p>
                          </div>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-500">Bio</p>
                          <p className="text-gray-900">{profileData.bio || 'No bio added yet.'}</p>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm font-medium text-gray-500">Location</p>
                            <p className="text-lg flex items-center">
                              <MapPin className="w-4 h-4 mr-1" />
                              {profileData.location || 'Not specified'}
                            </p>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-500">Website</p>
                            <p className="text-lg flex items-center">
                              <Globe className="w-4 h-4 mr-1" />
                              {profileData.website ? (
                                <a href={profileData.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                  {profileData.website}
                                </a>
                              ) : 'Not provided'}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Recent Activity */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Activity className="w-5 h-5 mr-2" />
                      Recent Activity
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {activityData.slice(0, 5).map((activity, index) => (
                        <div key={index} className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
                          <div className="text-2xl">{activity.icon}</div>
                          <div className="flex-1">
                            <p className="font-medium">{activity.title}</p>
                            <p className="text-sm text-gray-500">{activity.time}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                    <Button 
                      variant="outline" 
                      className="w-full mt-4"
                      onClick={() => setActiveTab('activity')}
                    >
                      View All Activity
                    </Button>
                  </CardContent>
                </Card>
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Account Level & Badges */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Award className="w-5 h-5 mr-2" />
                      Account Status
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="text-center">
                      <div className={`inline-flex items-center px-4 py-2 rounded-full text-lg font-bold ${getBadgeColor(stats.account_level)}`}>
                        <Award className="w-5 h-5 mr-2" />
                        {stats.account_level} Member
                      </div>
                      <p className="text-sm text-gray-500 mt-2">Trust Score: {stats.trust_score}%</p>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Progress to Platinum</span>
                        <span>78%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full" style={{ width: '78%' }}></div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Verification Status */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Shield className="w-5 h-5 mr-2" />
                      Verification
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {[
                      { label: 'Email Verified', status: profileData.verification?.email_verified, icon: Mail },
                      { label: 'Phone Verified', status: profileData.verification?.phone_verified, icon: Phone },
                      { label: 'Identity Verified', status: profileData.verification?.identity_verified, icon: Shield },
                      { label: 'Business Verified', status: profileData.verification?.business_verified, icon: Award }
                    ].map((item, index) => {
                      const Icon = item.icon;
                      return (
                        <div key={index} className="flex items-center justify-between">
                          <div className="flex items-center">
                            <Icon className="w-4 h-4 mr-2 text-gray-400" />
                            <span className="text-sm">{item.label}</span>
                          </div>
                          <div className={`w-4 h-4 rounded-full flex items-center justify-center ${
                            item.status ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
                          }`}>
                            {item.status ? '✓' : '○'}
                          </div>
                        </div>
                      );
                    })}
                    <Button size="sm" variant="outline" className="w-full mt-2">
                      Complete Verification
                    </Button>
                  </CardContent>
                </Card>

                {/* Quick Actions */}
                <Card>
                  <CardHeader>
                    <CardTitle>Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <Button variant="outline" size="sm" className="w-full justify-start">
                      <Plus className="w-4 h-4 mr-2" />
                      Create New Listing
                    </Button>
                    <Button variant="outline" size="sm" className="w-full justify-start">
                      <MessageCircle className="w-4 h-4 mr-2" />
                      Message Center
                    </Button>
                    <Button variant="outline" size="sm" className="w-full justify-start">
                      <TrendingUp className="w-4 h-4 mr-2" />
                      View Analytics
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Activity Tab */}
          <TabsContent value="activity" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  Complete Activity History
                </CardTitle>
                <CardDescription>All your marketplace activities and interactions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {activityData.map((activity, index) => (
                    <div key={index} className={`flex items-center space-x-4 p-4 rounded-lg border-l-4 border-l-${activity.color}-500 bg-${activity.color}-50`}>
                      <div className="text-3xl">{activity.icon}</div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{activity.title}</p>
                        <p className="text-sm text-gray-500">{activity.time}</p>
                      </div>
                      <div className={`px-2 py-1 rounded-full text-xs font-medium bg-${activity.color}-100 text-${activity.color}-800`}>
                        {activity.type.replace('_', ' ').toUpperCase()}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Other tabs would be implemented similarly... */}
          <TabsContent value="listings">
            <Card>
              <CardHeader>
                <CardTitle>My Listings</CardTitle>
              </CardHeader>
              <CardContent>
                <p>Listings content would go here...</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="orders">
            <Card>
              <CardHeader>
                <CardTitle>My Orders</CardTitle>
              </CardHeader>
              <CardContent>
                <p>Orders content would go here...</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="favorites">
            <Card>
              <CardHeader>
                <CardTitle>My Favorites</CardTitle>
              </CardHeader>
              <CardContent>
                <p>Favorites content would go here...</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="messages">
            <Card>
              <CardHeader>
                <CardTitle>Messages</CardTitle>
              </CardHeader>
              <CardContent>
                <p>Messages content would go here...</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reviews">
            <Card>
              <CardHeader>
                <CardTitle>Reviews</CardTitle>
              </CardHeader>
              <CardContent>
                <p>Reviews content would go here...</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle>Settings</CardTitle>
              </CardHeader>
              <CardContent>
                <p>Settings content would go here...</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ComprehensiveProfile;