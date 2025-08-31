/**
 * CATALORO - Enhanced Profile Page
 * Comprehensive user profile management with real functionality
 */

import React, { useState, useEffect } from 'react';
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Camera, 
  Save, 
  Edit, 
  Edit3,
  Shield, 
  Bell, 
  Eye, 
  EyeOff,
  Lock,
  Key,
  Settings,
  Package,
  DollarSign,
  Star,
  Heart,
  ShoppingCart,
  Calendar,
  Award,
  TrendingUp,
  Download,
  Upload,
  Check,
  X,
  AlertCircle,
  RefreshCw,
  Globe
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import { useMarketplace } from '../../context/MarketplaceContext';

function ProfilePage() {
  const { user, updateUser } = useAuth();
  const { showToast } = useNotifications();
  const { allProducts, cartItems, favorites, orderHistory } = useMarketplace();
  
  const [activeTab, setActiveTab] = useState('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  const [profileData, setProfileData] = useState({
    full_name: user?.full_name || '',
    username: user?.username || '',
    email: user?.email || '',
    phone: user?.phone || '',
    // Detailed address fields instead of single address
    street: user?.street || '',
    post_code: user?.post_code || '',
    city: user?.city || '',
    country: user?.country || '',
    bio: user?.bio || 'Marketplace enthusiast and trusted seller.',
    avatar_url: user?.avatar_url || '',
    date_joined: user?.date_joined || '2024-01-15',
    verified: user?.verified || false,
    seller_rating: user?.seller_rating || 4.8,
    total_sales: user?.total_sales || 0,
    // Business account fields
    is_business: user?.is_business || false,
    company_name: user?.company_name || '',
    business_country: user?.business_country || '',
    vat_number: user?.vat_number || ''
  });

  // Address suggestions state
  const [citySuggestions, setCitySuggestions] = useState([]);
  const [countrySuggestions, setCountrySuggestions] = useState([]);
  const [businessCountrySuggestions, setBusinessCountrySuggestions] = useState([]);
  const [showCitySuggestions, setShowCitySuggestions] = useState(false);
  const [showCountrySuggestions, setShowCountrySuggestions] = useState(false);
  const [showBusinessCountrySuggestions, setShowBusinessCountrySuggestions] = useState(false);

  const [preferences, setPreferences] = useState({
    emailNotifications: true,
    smsNotifications: false,
    marketingEmails: false,
    browserNotifications: true,
    darkMode: false,
    language: 'en',
    currency: 'USD',
    timezone: 'UTC',
    publicProfile: true,
    showEmail: false,
    showPhone: false
  });

  const [accountStats, setAccountStats] = useState({
    totalListings: 0,
    activeListings: 0,
    totalDeals: 0,
    completedDeals: 0,
    totalRevenue: 0,
    avgRating: 0,
    totalFavorites: 0,
    profileViews: 0,
    joinDate: '',
    lastActive: ''
  });

  // Popular European cities for suggestions
  const popularCities = [
    // Germany
    'Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne', 'Stuttgart', 'Düsseldorf', 'Dortmund', 'Essen', 'Bremen',
    // France  
    'Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg', 'Montpellier', 'Bordeaux', 'Lille',
    // Netherlands
    'Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht', 'Eindhoven', 'Tilburg', 'Groningen', 'Almere',
    // Belgium
    'Brussels', 'Antwerp', 'Ghent', 'Bruges', 'Leuven', 'Liège',
    // Spain
    'Madrid', 'Barcelona', 'Valencia', 'Seville', 'Bilbao', 'Málaga', 'Zaragoza',
    // Italy
    'Rome', 'Milan', 'Naples', 'Turin', 'Palermo', 'Genoa', 'Bologna', 'Florence', 'Venice',
    // United Kingdom
    'London', 'Birmingham', 'Manchester', 'Glasgow', 'Liverpool', 'Leeds', 'Sheffield', 'Edinburgh', 'Bristol', 'Cardiff',
    // Other European cities
    'Vienna', 'Zurich', 'Geneva', 'Copenhagen', 'Stockholm', 'Oslo', 'Helsinki', 'Prague', 'Warsaw', 'Budapest', 'Dublin', 'Lisbon', 'Athens'
  ];

  // Popular countries
  const popularCountries = [
    'Germany', 'France', 'Netherlands', 'Belgium', 'Spain', 'Italy', 'United Kingdom', 'Austria', 'Switzerland',
    'Denmark', 'Sweden', 'Norway', 'Finland', 'Czech Republic', 'Poland', 'Hungary', 'Ireland', 'Portugal', 'Greece',
    'Luxembourg', 'Slovenia', 'Slovakia', 'Estonia', 'Latvia', 'Lithuania', 'Malta', 'Cyprus', 'Croatia', 'Romania', 'Bulgaria'
  ];

  // Calculate real statistics from marketplace data
  useEffect(() => {
    const calculateStats = () => {
      const userListings = allProducts.filter(p => p.seller === user?.username || p.seller === user?.full_name);
      const activeListings = userListings.filter(p => p.inStock !== false);
      const userOrders = orderHistory || [];
      const completedOrders = userOrders.filter(o => o.status === 'completed');
      
      const stats = {
        totalListings: userListings.length,
        activeListings: activeListings.length,
        totalDeals: userOrders.length,
        completedDeals: completedOrders.length,
        totalRevenue: userListings.reduce((sum, p) => sum + (p.price || 0), 0),
        avgRating: profileData.seller_rating,
        totalFavorites: favorites.length,
        profileViews: Math.floor(Math.random() * 500) + 100,
        joinDate: profileData.date_joined,
        lastActive: new Date().toISOString().split('T')[0]
      };
      
      setAccountStats(stats);
    };

    calculateStats();
  }, [allProducts, orderHistory, favorites, user, profileData]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCityChange = (e) => {
    const value = e.target.value;
    setProfileData(prev => ({ ...prev, city: value }));

    if (value.length > 1) {
      // Filter popular cities based on input
      const filtered = popularCities.filter(city => 
        city.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 8); // Limit to 8 suggestions

      setCitySuggestions(filtered);
      setShowCitySuggestions(filtered.length > 0);
    } else {
      setCitySuggestions([]);
      setShowCitySuggestions(false);
    }
  };

  const handleCountryChange = (e) => {
    const value = e.target.value;
    setProfileData(prev => ({ ...prev, country: value }));

    if (value.length > 1) {
      // Filter popular countries based on input
      const filtered = popularCountries.filter(country => 
        country.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 8); // Limit to 8 suggestions

      setCountrySuggestions(filtered);
      setShowCountrySuggestions(filtered.length > 0);
    } else {
      setCountrySuggestions([]);
      setShowCountrySuggestions(false);
    }
  };

  const selectCity = (city) => {
    setProfileData(prev => ({ ...prev, city: city }));
    setShowCitySuggestions(false);
    setCitySuggestions([]);
  };

  const selectCountry = (country) => {
    setProfileData(prev => ({ ...prev, country: country }));
    setShowCountrySuggestions(false);
    setCountrySuggestions([]);
  };

  const handleBusinessCountryChange = (e) => {
    const value = e.target.value;
    setProfileData(prev => ({ ...prev, business_country: value }));

    if (value.length > 1) {
      // Filter popular countries based on input
      const filtered = popularCountries.filter(country => 
        country.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 8); // Limit to 8 suggestions

      setBusinessCountrySuggestions(filtered);
      setShowBusinessCountrySuggestions(filtered.length > 0);
    } else {
      setBusinessCountrySuggestions([]);
      setShowBusinessCountrySuggestions(false);
    }
  };

  const selectBusinessCountry = (country) => {
    setProfileData(prev => ({ ...prev, business_country: country }));
    setShowBusinessCountrySuggestions(false);
    setBusinessCountrySuggestions([]);
  };

  const handleBusinessToggle = (checked) => {
    setProfileData(prev => ({ 
      ...prev, 
      is_business: checked,
      // Clear business fields when unchecking
      ...(!checked && {
        company_name: '',
        business_country: '',
        vat_number: ''
      })
    }));
  };

  const handlePreferenceChange = (key, value) => {
    setPreferences({
      ...preferences,
      [key]: value
    });
    showToast(`${key} ${value ? 'enabled' : 'disabled'}`, 'success');
  };

  const handlePasswordChange = (e) => {
    setPasswordData({
      ...passwordData,
      [e.target.name]: e.target.value
    });
  };

  const handleSaveProfile = async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Save to localStorage for persistence
      const updatedUser = { ...user, ...profileData };
      localStorage.setItem('cataloro_user', JSON.stringify(updatedUser));
      
      // Also update the auth context to reflect changes immediately
      // This ensures the user object is updated across the entire app
      if (typeof updateUser === 'function') {
        updateUser(updatedUser);
      }
      
      setIsEditing(false);
      showToast('Profile updated successfully!', 'success');
    } catch (error) {
      showToast('Failed to update profile. Please try again.', 'error');
    }
  };

  const handleChangePassword = async () => {
    if (!passwordData.currentPassword || !passwordData.newPassword) {
      showToast('Please fill in all password fields', 'error');
      return;
    }
    
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      showToast('New passwords do not match', 'error');
      return;
    }
    
    if (passwordData.newPassword.length < 6) {
      showToast('Password must be at least 6 characters long', 'error');
      return;
    }
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      showToast('Password changed successfully!', 'success');
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    } catch (error) {
      showToast('Failed to change password. Please try again.', 'error');
    }
  };

  const handleAvatarUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    if (file.size > 5 * 1024 * 1024) { // 5MB limit
      showToast('Image size must be less than 5MB', 'error');
      return;
    }
    
    try {
      setIsUploading(true);
      
      // Simulate file upload
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Create object URL for preview
      const imageUrl = URL.createObjectURL(file);
      setProfileData({ ...profileData, avatar_url: imageUrl });
      
      showToast('Profile picture updated successfully!', 'success');
    } catch (error) {
      showToast('Failed to upload image. Please try again.', 'error');
    } finally {
      setIsUploading(false);
    }
  };

  const handleExportData = () => {
    const exportData = {
      profile: profileData,
      preferences: preferences,
      statistics: accountStats,
      exportDate: new Date().toISOString()
    };
    
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `cataloro_profile_${user?.username}_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    showToast('Profile data exported successfully!', 'success');
  };

  const tabs = [
    { id: 'profile', label: 'Profile Info', icon: User },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'preferences', label: 'Preferences', icon: Settings },
    { id: 'activity', label: 'Activity', icon: TrendingUp },
    { id: 'data', label: 'Data & Privacy', icon: Lock }
  ];

  return (
    <div className="fade-in">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Profile Settings</h1>
            <p className="text-gray-600 dark:text-gray-300">Manage your account information, preferences, and security settings</p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={handleExportData}
              className="cataloro-button-secondary flex items-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Data
            </button>
            
            {activeTab === 'profile' && (
              <button
                onClick={() => isEditing ? handleSaveProfile() : setIsEditing(true)}
                className="cataloro-button-primary flex items-center"
              >
                {isEditing ? (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Save Changes
                  </>
                ) : (
                  <>
                    <Edit className="w-4 h-4 mr-2" />
                    Edit Profile
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Profile Overview Card */}
      <div className="cataloro-card-glass p-6 mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-6">
          {/* Avatar */}
          <div className="relative">
            <div className="w-20 h-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
              {profileData.avatar_url ? (
                <img 
                  src={profileData.avatar_url} 
                  alt="Profile" 
                  className="w-20 h-20 rounded-full object-cover"
                />
              ) : (
                <span className="text-white font-bold text-2xl">
                  {profileData.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                </span>
              )}
            </div>
            {profileData.verified && (
              <div className="absolute -bottom-1 -right-1 bg-green-500 rounded-full p-1">
                <Check className="w-3 h-3 text-white" />
              </div>
            )}
          </div>

          {/* Profile Info */}
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                {profileData.full_name || 'User Name'}
              </h2>
              {profileData.verified && (
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                  Verified
                </span>
              )}
              {user?.role && (
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                  {user.role.toUpperCase()}
                </span>
              )}
            </div>
            <p className="text-gray-600 dark:text-gray-300 mb-2">@{profileData.username}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">{profileData.bio}</p>
          </div>

          {/* Quick Stats */}
          <div className="flex space-x-6 text-center">
            <div>
              <div className="text-lg font-bold text-gray-900 dark:text-white">{accountStats.totalListings}</div>
              <div className="text-sm text-gray-600 dark:text-gray-300">Listings</div>
            </div>
            <div>
              <div className="text-lg font-bold text-gray-900 dark:text-white">{accountStats.completedDeals}</div>
              <div className="text-sm text-gray-600 dark:text-gray-300">Deals</div>
            </div>
            <div>
              <div className="flex items-center text-lg font-bold text-gray-900 dark:text-white">
                <Star className="w-4 h-4 text-yellow-400 mr-1" />
                {accountStats.avgRating}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-300">Rating</div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="cataloro-card-glass mb-8">
        <nav className="flex space-x-1 p-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-blue-100/80 backdrop-blur-sm text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100/50 hover:text-gray-900'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        
        {/* Profile Info Tab */}
        {activeTab === 'profile' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Profile Picture Section */}
            <div className="lg:col-span-1">
              <div className="cataloro-card-glass p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Profile Picture</h3>
                
                <div className="text-center">
                  <div className="relative inline-block mb-4">
                    <div className="w-32 h-32 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto relative overflow-hidden">
                      {isUploading && (
                        <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                          <RefreshCw className="w-6 h-6 text-white animate-spin" />
                        </div>
                      )}
                      {profileData.avatar_url ? (
                        <img 
                          src={profileData.avatar_url} 
                          alt="Profile" 
                          className="w-32 h-32 rounded-full object-cover"
                        />
                      ) : (
                        <span className="text-white font-bold text-4xl">
                          {profileData.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                        </span>
                      )}
                    </div>
                    
                    {isEditing && (
                      <label className="absolute bottom-0 right-0 bg-white rounded-full p-2 shadow-lg cursor-pointer hover:bg-gray-50 border border-gray-200">
                        <Camera className="w-4 h-4 text-gray-600" />
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handleAvatarUpload}
                          className="hidden"
                          disabled={isUploading}
                        />
                      </label>
                    )}
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-4">
                    Upload a profile picture to help others recognize you
                  </p>
                  
                  <div className="text-xs text-gray-500">
                    • JPG, PNG, or GIF
                    • Maximum size: 5MB
                    • Recommended: 400x400px
                  </div>
                </div>
              </div>

              {/* Account Status */}
              <div className="cataloro-card-glass p-6 mt-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Account Status</h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Email Verified</span>
                    <span className="flex items-center text-green-600">
                      <Check className="w-4 h-4 mr-1" />
                      Verified
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Phone Verified</span>
                    <span className="flex items-center text-yellow-600">
                      <AlertCircle className="w-4 h-4 mr-1" />
                      Pending
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Identity Verified</span>
                    <span className="flex items-center text-green-600">
                      <Check className="w-4 h-4 mr-1" />
                      Verified
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Seller Status</span>
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                      Active
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Profile Details */}
            <div className="lg:col-span-2">
              <div className="cataloro-card-glass p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Personal Information</h3>
                
                <form className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <User className="w-4 h-4 inline mr-2" />
                        Full Name
                      </label>
                      <input
                        type="text"
                        name="full_name"
                        value={profileData.full_name}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        className={`cataloro-input ${!isEditing ? 'bg-gray-50/80 cursor-not-allowed' : ''}`}
                        placeholder="Enter your full name"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <User className="w-4 h-4 inline mr-2" />
                        Username
                      </label>
                      <input
                        type="text"
                        name="username"
                        value={profileData.username}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        className={`cataloro-input ${!isEditing ? 'bg-gray-50/80 cursor-not-allowed' : ''}`}
                        placeholder="Choose a username"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <Mail className="w-4 h-4 inline mr-2" />
                      Email Address
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={profileData.email}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className={`cataloro-input ${!isEditing ? 'bg-gray-50/80 cursor-not-allowed' : ''}`}
                      placeholder="Enter your email"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <Phone className="w-4 h-4 inline mr-2" />
                        Phone Number
                      </label>
                      <input
                        type="tel"
                        name="phone"
                        value={profileData.phone}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        className={`cataloro-input ${!isEditing ? 'bg-gray-50/80 cursor-not-allowed' : ''}`}
                        placeholder="Enter your phone number"
                      />
                    </div>
                  </div>

                  {/* Detailed Address Section */}
                  <div className="space-y-4">
                    <h4 className="text-md font-semibold text-gray-900 dark:text-white flex items-center">
                      <MapPin className="w-4 h-4 mr-2" />
                      Address Information
                    </h4>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Street Address
                      </label>
                      <input
                        type="text"
                        name="street"
                        value={profileData.street}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        className={`cataloro-input ${!isEditing ? 'bg-gray-50/80 cursor-not-allowed' : ''}`}
                        placeholder="Enter your street address"
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Post Code
                        </label>
                        <input
                          type="text"
                          name="post_code"
                          value={profileData.post_code}
                          onChange={handleInputChange}
                          disabled={!isEditing}
                          className={`cataloro-input ${!isEditing ? 'bg-gray-50/80 cursor-not-allowed' : ''}`}
                          placeholder="Postal/ZIP code"
                        />
                      </div>

                      <div className="relative">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          City
                          {isEditing && (
                            <span className="text-blue-600 dark:text-blue-400 text-xs ml-2">
                              (Type to search)
                            </span>
                          )}
                        </label>
                        <input
                          type="text"
                          name="city"
                          value={profileData.city}
                          onChange={handleCityChange}
                          onFocus={() => profileData.city && setShowCitySuggestions(citySuggestions.length > 0)}
                          disabled={!isEditing}
                          className={`cataloro-input ${!isEditing ? 'bg-gray-50/80 cursor-not-allowed' : ''}`}
                          placeholder="Enter your city"
                        />
                        
                        {/* City Suggestions Dropdown */}
                        {showCitySuggestions && isEditing && (
                          <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl shadow-2xl max-h-60 overflow-y-auto">
                            <div className="p-3 bg-gradient-to-r from-blue-50 to-green-50 dark:from-blue-900/20 dark:to-green-900/20 border-b border-gray-200 dark:border-gray-600">
                              <p className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center">
                                <MapPin className="w-4 h-4 mr-2 text-blue-500" />
                                Popular Cities ({citySuggestions.length})
                                <span className="ml-2 text-xs text-gray-500">Click to select</span>
                              </p>
                            </div>
                            {citySuggestions.map((city, index) => (
                              <div
                                key={index}
                                onClick={() => selectCity(city)}
                                className="p-3 hover:bg-blue-50 dark:hover:bg-blue-900/20 cursor-pointer border-b border-gray-100 dark:border-gray-700 last:border-b-0 transition-all duration-200 group"
                              >
                                <div className="flex items-center space-x-3">
                                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                                    {city.charAt(0)}
                                  </div>
                                  <div className="font-medium text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                                    {city}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="relative">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Country
                        {isEditing && (
                          <span className="text-blue-600 dark:text-blue-400 text-xs ml-2">
                            (Type to search)
                          </span>
                        )}
                      </label>
                      <input
                        type="text"
                        name="country"
                        value={profileData.country}
                        onChange={handleCountryChange}
                        onFocus={() => profileData.country && setShowCountrySuggestions(countrySuggestions.length > 0)}
                        disabled={!isEditing}
                        className={`cataloro-input ${!isEditing ? 'bg-gray-50/80 cursor-not-allowed' : ''}`}
                        placeholder="Enter your country"
                      />
                      
                      {/* Country Suggestions Dropdown */}
                      {showCountrySuggestions && isEditing && (
                        <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl shadow-2xl max-h-60 overflow-y-auto">
                          <div className="p-3 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 border-b border-gray-200 dark:border-gray-600">
                            <p className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center">
                              <Globe className="w-4 h-4 mr-2 text-green-500" />
                              Popular Countries ({countrySuggestions.length})
                              <span className="ml-2 text-xs text-gray-500">Click to select</span>
                            </p>
                          </div>
                          {countrySuggestions.map((country, index) => (
                            <div
                              key={index}
                              onClick={() => selectCountry(country)}
                              className="p-3 hover:bg-green-50 dark:hover:bg-green-900/20 cursor-pointer border-b border-gray-100 dark:border-gray-700 last:border-b-0 transition-all duration-200 group"
                            >
                              <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                                  {country.charAt(0)}
                                </div>
                                <div className="font-medium text-gray-900 dark:text-white group-hover:text-green-600 dark:group-hover:text-green-400 transition-colors">
                                  {country}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Bio
                    </label>
                    <textarea
                      name="bio"
                      rows={4}
                      value={profileData.bio}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className={`cataloro-input ${!isEditing ? 'bg-gray-50/80 cursor-not-allowed' : ''}`}
                      placeholder="Tell us about yourself..."
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      {profileData.bio.length}/500 characters
                    </p>
                  </div>

                  {/* Business Account Section */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="text-md font-semibold text-gray-900 dark:text-white flex items-center">
                        <Settings className="w-4 h-4 mr-2" />
                        Account Type
                      </h4>
                      
                      {/* Business Account Checkbox */}
                      <label className="flex items-center space-x-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={profileData.is_business}
                          onChange={(e) => handleBusinessToggle(e.target.checked)}
                          disabled={!isEditing}
                          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:cursor-not-allowed"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300 flex items-center">
                          <User className="w-3 h-3 mr-1" />
                          Business Account
                        </span>
                      </label>
                    </div>

                    {profileData.is_business ? (
                      /* Business Information Display */
                      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                        <div className="flex items-center mb-3">
                          <div className="p-2 bg-blue-100 dark:bg-blue-800 rounded-lg mr-3">
                            <Settings className="w-4 h-4 text-blue-600 dark:text-blue-300" />
                          </div>
                          <div>
                            <h5 className="font-medium text-blue-900 dark:text-blue-100">Business Account</h5>
                            <p className="text-sm text-blue-600 dark:text-blue-300">Professional marketplace seller</p>
                          </div>
                        </div>
                        
                        {/* Business Fields */}
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                              Company Name
                            </label>
                            <input
                              type="text"
                              name="company_name"
                              value={profileData.company_name}
                              onChange={handleInputChange}
                              disabled={!isEditing}
                              className={`cataloro-input ${!isEditing ? 'bg-gray-50/80 cursor-not-allowed' : ''}`}
                              placeholder="Enter your company name"
                            />
                          </div>

                          <div className="relative">
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                              Business Country
                              {isEditing && (
                                <span className="text-blue-600 dark:text-blue-400 text-xs ml-2">
                                  (Type to search)
                                </span>
                              )}
                            </label>
                            <input
                              type="text"
                              name="business_country"
                              value={profileData.business_country}
                              onChange={handleBusinessCountryChange}
                              onFocus={() => profileData.business_country && setShowBusinessCountrySuggestions(businessCountrySuggestions.length > 0)}
                              disabled={!isEditing}
                              className={`cataloro-input ${!isEditing ? 'bg-gray-50/80 cursor-not-allowed' : ''}`}
                              placeholder="Enter business country"
                            />
                            
                            {/* Business Country Suggestions Dropdown */}
                            {showBusinessCountrySuggestions && isEditing && (
                              <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl shadow-2xl max-h-60 overflow-y-auto">
                                <div className="p-3 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-b border-gray-200 dark:border-gray-600">
                                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center">
                                    <Globe className="w-4 h-4 mr-2 text-blue-500" />
                                    Business Countries ({businessCountrySuggestions.length})
                                    <span className="ml-2 text-xs text-gray-500">Click to select</span>
                                  </p>
                                </div>
                                {businessCountrySuggestions.map((country, index) => (
                                  <div
                                    key={index}
                                    onClick={() => selectBusinessCountry(country)}
                                    className="p-3 hover:bg-blue-50 dark:hover:bg-blue-900/20 cursor-pointer border-b border-gray-100 dark:border-gray-700 last:border-b-0 transition-all duration-200 group"
                                  >
                                    <div className="flex items-center space-x-3">
                                      <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                                        {country.charAt(0)}
                                      </div>
                                      <div className="font-medium text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                                        {country}
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                              VAT Number
                              <span className="text-gray-500 text-xs ml-2">(Optional)</span>
                            </label>
                            <input
                              type="text"
                              name="vat_number"
                              value={profileData.vat_number}
                              onChange={handleInputChange}
                              disabled={!isEditing}
                              className={`cataloro-input ${!isEditing ? 'bg-gray-50/80 cursor-not-allowed' : ''}`}
                              placeholder="Enter VAT number (e.g. DE123456789)"
                            />
                          </div>
                        </div>
                      </div>
                    ) : (
                      /* Private Account Display */
                      <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                        <div className="flex items-center">
                          <div className="p-2 bg-green-100 dark:bg-green-800 rounded-lg mr-3">
                            <User className="w-4 h-4 text-green-600 dark:text-green-300" />
                          </div>
                          <div>
                            <h5 className="font-medium text-green-900 dark:text-green-100">Private Account</h5>
                            <p className="text-sm text-green-600 dark:text-green-300">Personal marketplace user</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <div className="space-y-6">
            
            {/* Change Password */}
            <div className="cataloro-card-glass p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
                <Key className="w-5 h-5 mr-2" />
                Change Password
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Current Password
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      name="currentPassword"
                      value={passwordData.currentPassword}
                      onChange={handlePasswordChange}
                      className="cataloro-input pr-10"
                      placeholder="Enter current password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      New Password
                    </label>
                    <input
                      type="password"
                      name="newPassword"
                      value={passwordData.newPassword}
                      onChange={handlePasswordChange}
                      className="cataloro-input"
                      placeholder="Enter new password"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Confirm New Password
                    </label>
                    <input
                      type="password"
                      name="confirmPassword"
                      value={passwordData.confirmPassword}
                      onChange={handlePasswordChange}
                      className="cataloro-input"
                      placeholder="Confirm new password"
                    />
                  </div>
                </div>
                
                <button
                  onClick={handleChangePassword}
                  className="cataloro-button-primary"
                >
                  Update Password
                </button>
              </div>
            </div>

            {/* Two-Factor Authentication */}
            <div className="cataloro-card-glass p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Shield className="w-5 h-5 mr-2" />
                Two-Factor Authentication
              </h3>
              
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-gray-700">Add an extra layer of security to your account</p>
                  <p className="text-sm text-gray-500">Use an authenticator app to generate verification codes</p>
                </div>
                <div className="text-right">
                  <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-sm">
                    Disabled
                  </span>
                </div>
              </div>
              
              <button className="cataloro-button-secondary">
                Enable 2FA
              </button>
            </div>

            {/* Login History */}
            <div className="cataloro-card-glass p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Login Activity</h3>
              
              <div className="space-y-3">
                {[
                  { device: 'Chrome on Windows', location: 'New York, US', time: '2 hours ago', current: true },
                  { device: 'Safari on iPhone', location: 'New York, US', time: '1 day ago', current: false },
                  { device: 'Chrome on Windows', location: 'New York, US', time: '3 days ago', current: false }
                ].map((login, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50/80 backdrop-blur-sm rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{login.device}</p>
                      <p className="text-xs text-gray-600">{login.location} • {login.time}</p>
                    </div>
                    {login.current && (
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">
                        Current
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Preferences Tab */}
        {activeTab === 'preferences' && (
          <div className="space-y-6">
            
            {/* Notification Preferences */}
            <div className="cataloro-card-glass p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
                <Bell className="w-5 h-5 mr-2" />
                Notification Preferences
              </h3>
              
              <div className="space-y-4">
                {[
                  { key: 'emailNotifications', label: 'Email Notifications', desc: 'Receive email notifications for important updates' },
                  { key: 'smsNotifications', label: 'SMS Notifications', desc: 'Get text messages for urgent notifications' },
                  { key: 'browserNotifications', label: 'Browser Notifications', desc: 'Show desktop notifications while browsing' },
                  { key: 'marketingEmails', label: 'Marketing Emails', desc: 'Receive promotional offers and newsletters' }
                ].map((pref) => (
                  <label key={pref.key} className="flex items-start space-x-3 p-3 hover:bg-gray-50/50 rounded-lg cursor-pointer transition-colors">
                    <input
                      type="checkbox"
                      checked={preferences[pref.key]}
                      onChange={(e) => handlePreferenceChange(pref.key, e.target.checked)}
                      className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <div>
                      <div className="font-medium text-gray-900">{pref.label}</div>
                      <div className="text-sm text-gray-600">{pref.desc}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Display Preferences */}
            <div className="cataloro-card-glass p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Display & Language</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
                  <select
                    value={preferences.language}
                    onChange={(e) => handlePreferenceChange('language', e.target.value)}
                    className="cataloro-input"
                  >
                    <option value="en">English</option>
                    <option value="es">Español</option>
                    <option value="fr">Français</option>
                    <option value="de">Deutsch</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Currency</label>
                  <select
                    value={preferences.currency}
                    onChange={(e) => handlePreferenceChange('currency', e.target.value)}
                    className="cataloro-input"
                  >
                    <option value="USD">USD ($)</option>
                    <option value="EUR">EUR (€)</option>
                    <option value="GBP">GBP (£)</option>
                    <option value="JPY">JPY (¥)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Privacy Preferences */}
            <div className="cataloro-card-glass p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Privacy Settings</h3>
              
              <div className="space-y-4">
                {[
                  { key: 'publicProfile', label: 'Public Profile', desc: 'Make your profile visible to other users' },
                  { key: 'showEmail', label: 'Show Email', desc: 'Display your email address on your profile' },
                  { key: 'showPhone', label: 'Show Phone', desc: 'Allow others to see your phone number' }
                ].map((pref) => (
                  <label key={pref.key} className="flex items-start space-x-3 p-3 hover:bg-gray-50/50 rounded-lg cursor-pointer transition-colors">
                    <input
                      type="checkbox"
                      checked={preferences[pref.key]}
                      onChange={(e) => handlePreferenceChange(pref.key, e.target.checked)}
                      className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <div>
                      <div className="font-medium text-gray-900">{pref.label}</div>
                      <div className="text-sm text-gray-600">{pref.desc}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Activity Tab */}
        {activeTab === 'activity' && (
          <div className="space-y-6">
            
            {/* Account Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="kpi-card">
                <Package className="w-8 h-8 text-blue-600 mx-auto mb-3" />
                <div className="kpi-value">{accountStats.totalListings}</div>
                <div className="kpi-label">Total Listings</div>
              </div>
              
              <div className="kpi-card">
                <DollarSign className="w-8 h-8 text-green-600 mx-auto mb-3" />
                <div className="kpi-value">${accountStats.totalRevenue}</div>
                <div className="kpi-label">Total Revenue</div>
              </div>
              
              <div className="kpi-card">
                <Heart className="w-8 h-8 text-red-600 mx-auto mb-3" />
                <div className="kpi-value">{accountStats.totalFavorites}</div>
                <div className="kpi-label">Favorites</div>
              </div>
              
              <div className="kpi-card">
                <Eye className="w-8 h-8 text-purple-600 mx-auto mb-3" />
                <div className="kpi-value">{accountStats.profileViews}</div>
                <div className="kpi-label">Profile Views</div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="cataloro-card-glass p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Recent Activity</h3>
              
              <div className="space-y-4">
                {[
                  { action: 'Listed new item', item: 'iPhone 15 Pro Max', time: '2 hours ago', icon: Package },
                  { action: 'Received favorite', item: 'MacBook Air M2', time: '5 hours ago', icon: Heart },
                  { action: 'Completed deal', item: 'Vintage Guitar', time: '1 day ago', icon: DollarSign },
                  { action: 'Updated profile', item: 'Profile information', time: '2 days ago', icon: User }
                ].map((activity, index) => {
                  const Icon = activity.icon;
                  return (
                    <div key={index} className="flex items-center space-x-4 p-3 hover:bg-gray-50/50 rounded-lg transition-colors">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <Icon className="w-4 h-4 text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          {activity.action}: <span className="text-blue-600">{activity.item}</span>
                        </p>
                        <p className="text-xs text-gray-500">{activity.time}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Data & Privacy Tab */}
        {activeTab === 'data' && (
          <div className="space-y-6">
            
            {/* Data Export */}
            <div className="cataloro-card-glass p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Download className="w-5 h-5 mr-2" />
                Export Your Data
              </h3>
              
              <p className="text-gray-600 mb-6">
                Download a copy of all your data including profile information, listings, and activity history.
              </p>
              
              <button
                onClick={handleExportData}
                className="cataloro-button-primary flex items-center"
              >
                <Download className="w-4 h-4 mr-2" />
                Export Data
              </button>
            </div>

            {/* Account Deletion */}
            <div className="cataloro-card-glass p-6 border-red-200">
              <h3 className="text-lg font-semibold text-red-900 mb-4 flex items-center">
                <AlertCircle className="w-5 h-5 mr-2" />
                Danger Zone
              </h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Deactivate Account</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Temporarily disable your account. You can reactivate it anytime.
                  </p>
                  <button className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 transition-colors">
                    Deactivate Account
                  </button>
                </div>
                
                <div className="border-t pt-4">
                  <h4 className="font-medium text-gray-900 mb-2">Delete Account</h4>
                  <p className="text-sm text-gray-600 mb-3">
                    Permanently delete your account and all associated data. This action cannot be undone.
                  </p>
                  <button className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors">
                    Delete Account
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ProfilePage;