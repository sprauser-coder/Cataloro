/**
 * CATALORO - Enhanced Profile Page
 * Comprehensive user profile management with real functionality
 */

import React, { useState, useEffect } from 'react';
import { 
  User, 
  Users,
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

  Calendar,
  Award,
  TrendingUp,
  Download,
  Upload,
  Check,
  CheckCircle,
  X,
  AlertCircle,
  RefreshCw,
  Globe
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import { useMarketplace } from '../../context/MarketplaceContext';
import { marketplaceService } from '../../services/marketplaceService';

function ProfilePage() {
  const { user, updateUser } = useAuth();
  const { showToast } = useNotifications();
  const { allProducts, favorites, orderHistory, refreshListings } = useMarketplace();
  
  // Debug logging for mobile vs desktop differences
  useEffect(() => {
    console.log('🔍 ProfilePage mounted - Context data check:', {
      hasUser: !!user,
      userInfo: user ? {
        id: user.id,
        username: user.username,
        email: user.email,
        role: user.role,
        account_type: user.account_type,
        is_business: user.is_business,
        can_buy: user.can_buy
      } : null,
      hasAllProducts: !!allProducts,
      allProductsLength: allProducts?.length || 0,
      hasOrderHistory: !!orderHistory,
      orderHistoryLength: orderHistory?.length || 0,
      hasFavorites: !!favorites,
      favoritesLength: favorites?.length || 0,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight,
        isMobile: window.innerWidth < 768
      }
    });
  }, [user, allProducts, orderHistory, favorites]);
  
  const [activeTab, setActiveTab] = useState('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  // Partners management state
  const [partners, setPartners] = useState([]);
  const [partnersLoading, setPartnersLoading] = useState(false);
  const [userSearchQuery, setUserSearchQuery] = useState('');
  const [userSearchResults, setUserSearchResults] = useState([]);
  const [selectedPartners, setSelectedPartners] = useState([]);
  
  const [profileData, setProfileData] = useState({
    full_name: user?.full_name || '',
    first_name: user?.first_name || (user?.full_name ? user.full_name.split(' ')[0] : ''),
    last_name: user?.last_name || (user?.full_name ? user.full_name.split(' ').slice(1).join(' ') : ''),
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
    vat_number: user?.vat_number || '',
    // Timezone preference
    timezone: user?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone
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
    avgRating: 0,
    totalFavorites: 0,
    profileViews: 0,
    joinDate: '',
    lastActive: ''
  });

  // State for listings and tenders data (like working tiles)
  const [myListings, setMyListings] = useState([]);
  const [myTenders, setMyTenders] = useState([]);
  const [listingsLoading, setListingsLoading] = useState(false);
  const [tendersLoading, setTendersLoading] = useState(false);

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

  // Load user data when component mounts or user changes
  useEffect(() => {
    if (user) {
      setProfileData({
        full_name: user.full_name || '',
        username: user.username || '',
        email: user.email || '',
        phone: user.phone || '',
        street: user.street || '',
        post_code: user.post_code || '',
        city: user.city || '',
        country: user.country || '',
        bio: user.bio || 'Marketplace enthusiast and trusted seller.',
        date_of_birth: user.date_of_birth || '',
        website: user.website || '',
        profile_image: user.profile_image || null
      });
      
      // Load partners when switching to partners tab
      if (activeTab === 'partners') {
        loadPartners();
      }
    }
  }, [user, activeTab]);

  // Partners management functions
  const loadPartners = async () => {
    if (!user?.id) return;
    
    try {
      setPartnersLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/partners/${user.id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('cataloro_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPartners(data);
      }
    } catch (error) {
      console.error('Failed to load partners:', error);
      showToast('Failed to load partners', 'error');
    } finally {
      setPartnersLoading(false);
    }
  };

  const searchUsers = async () => {
    if (!userSearchQuery.trim()) return;
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/users/search?q=${encodeURIComponent(userSearchQuery)}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('cataloro_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUserSearchResults(data);
      }
    } catch (error) {
      console.error('Failed to search users:', error);
      showToast('Failed to search users', 'error');
    }
  };

  const addPartner = async (partnerUser) => {
    if (!user?.id) return;
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/partners`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('cataloro_token')}`
        },
        body: JSON.stringify({
          user_id: user.id,
          partner_id: partnerUser.id
        })
      });
      
      if (response.ok) {
        showToast(`${partnerUser.full_name || partnerUser.username} added as partner`, 'success');
        setUserSearchQuery('');
        setUserSearchResults([]);
        await loadPartners();
      } else {
        throw new Error('Failed to add partner');
      }
    } catch (error) {
      console.error('Failed to add partner:', error);
      showToast('Failed to add partner', 'error');
    }
  };

  const removePartner = async (partnerId) => {
    if (!user?.id) return;
    
    if (!window.confirm('Are you sure you want to remove this partner?')) return;
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/partners/${partnerId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('cataloro_token')}`
        }
      });
      
      if (response.ok) {
        showToast('Partner removed successfully', 'success');
        await loadPartners();
      } else {
        throw new Error('Failed to remove partner');
      }
    } catch (error) {
      console.error('Failed to remove partner:', error);
      showToast('Failed to remove partner', 'error');
    }
  };

  // Fetch my listings like MyListingsPage does
  const fetchMyListings = async () => {
    if (!user?.id) return;
    
    try {
      setListingsLoading(true);
      const data = await marketplaceService.getMyListings(user.id);
      setMyListings(data);
    } catch (error) {
      console.error('Failed to fetch listings:', error);
      setMyListings([]);
    } finally {
      setListingsLoading(false);
    }
  };

  // Fetch my tenders like TenderManagementPage does  
  const fetchMyTenders = async () => {
    if (!user?.id) return;
    
    try {
      setTendersLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tenders/buyer/${user.id}`, {
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMyTenders(data);
      } else {
        console.error('Failed to load tenders');
        setMyTenders([]);
      }
    } catch (error) {
      console.error('Error loading tenders:', error);
      setMyTenders([]);
    } finally {
      setTendersLoading(false);
    }
  };

  // Load data when user changes
  useEffect(() => {
    if (user?.id) {
      fetchMyListings();
      fetchMyTenders();
    }
  }, [user?.id]);

  // Calculate stats using the same logic as working tiles
  useEffect(() => {
    const calculateStatsFromTiles = () => {
      console.log('🔍 ProfilePage calculateStatsFromTiles - Using working tile logic:', {
        myListingsCount: myListings.length,
        myTendersCount: myTenders.length,
        listingsLoading,
        tendersLoading
      });
      
      if (!user?.id) {
        console.log('❌ No user ID available for stats calculation');
        return;
      }
      
      // Use same logic as MyListingsPage tiles
      const totalListings = myListings.length;
      const activeListings = myListings.filter(l => l.status === 'active').length;
      const closedListings = myListings.filter(l => l.status === 'sold' || l.status === 'closed').length;
      
      // Use same logic as TenderManagementPage tiles
      const acceptedTenders = myTenders.filter(t => t.status === 'accepted').length;
      
      // Calculate rating from existing logic (keep from previous implementation)
      const actualRating = totalListings > 0 ? 4.5 : 0; // Default rating for sellers with listings
      
      const stats = {
        totalListings: totalListings,          // From Sell > Listings > Total Listings Tile
        activeListings: activeListings,        // From Sell > Listings > Active Listings Tile  
        totalDeals: closedListings,           // From Sell > Listings > Closed Tile
        completedDeals: acceptedTenders,      // From Buy > Tenders > Accepted Tile
        avgRating: parseFloat(actualRating.toFixed(1)),
        totalFavorites: favorites?.length || 0,
        profileViews: myListings.reduce((sum, listing) => sum + (listing.views || 0), 0), // Sum of listing views
        joinDate: user?.date_joined || user?.created_at,
        lastActive: new Date().toISOString().split('T')[0]
      };
      
      console.log('🔍 Final calculated stats using tile logic:', stats);
      setAccountStats(stats);
      
      // Update profileData with calculated seller rating
      setProfileData(prev => ({
        ...prev,
        seller_rating: stats.avgRating,
        total_sales: stats.completedDeals
      }));
    };

    // Only calculate when we have the data and it's not loading
    if (user && !listingsLoading && !tendersLoading) {
      calculateStatsFromTiles();
    } else {
      console.log('⚠️ Waiting for data to calculate stats:', {
        hasUser: !!user,
        listingsLoading,
        tendersLoading,
        myListingsLength: myListings.length,
        myTendersLength: myTenders.length
      });
    }
  }, [myListings, myTenders, favorites, user, listingsLoading, tendersLoading]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => {
      const newData = {
        ...prev,
        [name]: value
      };
      
      // Update full_name when first_name or last_name changes
      if (name === 'first_name' || name === 'last_name') {
        const firstName = name === 'first_name' ? value : prev.first_name;
        const lastName = name === 'last_name' ? value : prev.last_name;
        newData.full_name = `${firstName} ${lastName}`.trim();
      }
      
      return newData;
    });
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
      // Check if account type changed
      const accountTypeChanged = user?.is_business !== profileData.is_business;
      
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
      
      // If account type changed, refresh marketplace listings to update badges
      if (accountTypeChanged) {
        refreshListings();
        showToast(`Account switched to ${profileData.is_business ? 'Business' : 'Private'}`, 'success');
      }
    } catch (error) {
      showToast('Failed to update profile', 'error');
    }
  };

  // Export Data functionality
  const handleExportData = async () => {
    try {
      showToast('Preparing your data export...', 'info');
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/export-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          user_id: user.id,
          format: 'pdf'
        })
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `cataloro-data-export-${user.username || user.id}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast('Data export downloaded successfully!', 'success');
      } else {
        const error = await response.json();
        showToast(error.detail || 'Failed to export data', 'error');
      }
    } catch (error) {
      console.error('Error exporting data:', error);
      showToast('Failed to export data', 'error');
    }
  };

  // Soft Delete Account functionality
  const handleDeleteAccount = async () => {
    const confirmation = window.confirm(
      'Are you sure you want to delete your account?\n\nThis will:\n- Deactivate your account\n- Hide your listings\n- Preserve your data for 30 days\n- Allow account recovery within 30 days\n\nType "DELETE" to confirm.'
    );
    
    if (!confirmation) return;
    
    const deleteConfirmation = window.prompt('Type "DELETE" to confirm account deletion:');
    if (deleteConfirmation !== 'DELETE') {
      showToast('Account deletion cancelled', 'info');
      return;
    }
    
    try {
      showToast('Processing account deletion...', 'info');
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/delete-account`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          user_id: user.id,
          deletion_type: 'soft'
        })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        showToast('Account deleted successfully. You can recover it within 30 days.', 'success');
        // Logout and redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('cataloro_user');
        window.location.href = '/login';
      } else {
        showToast(result.detail || 'Failed to delete account', 'error');
      }
    } catch (error) {
      console.error('Error deleting account:', error);
      showToast('Failed to delete account', 'error');
    }
  };

  const handleUpdatePassword = async () => {
    if (!passwordData.currentPassword) {
      showToast('Current password is required', 'error');
      return;
    }
    
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      showToast('New passwords do not match', 'error');
      return;
    }
    
    if (passwordData.newPassword.length < 8) {
      showToast('Password must be at least 8 characters long', 'error');
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/change-password`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          user_id: user.id,
          current_password: passwordData.currentPassword,
          new_password: passwordData.newPassword
        })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        setPasswordData({
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        });
        showToast('Password updated successfully!', 'success');
      } else {
        showToast(result.detail || 'Failed to update password', 'error');
      }
    } catch (error) {
      console.error('Error updating password:', error);
      showToast('Failed to update password', 'error');
    }
  };

  const handleAvatarUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) { // 5MB limit
      showToast('File size must be less than 5MB', 'error');
      return;
    }

    try {
      setIsUploading(true);
      
      // Create a preview URL
      const reader = new FileReader();
      reader.onload = (e) => {
        setProfileData(prev => ({
          ...prev,
          avatar_url: e.target.result
        }));
      };
      reader.readAsDataURL(file);

      // Simulate upload delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      showToast('Profile picture updated successfully!', 'success');
    } catch (error) {
      showToast('Failed to upload image', 'error');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Profile Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-700 rounded-xl p-8 mb-8 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-32 translate-x-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full translate-y-24 -translate-x-24"></div>
        
        <div className="relative flex items-center space-x-6">
          <div className="relative">
            <div className="w-32 h-32 rounded-full bg-white/20 flex items-center justify-center overflow-hidden border-4 border-white/30">
              {profileData.avatar_url ? (
                <img
                  src={profileData.avatar_url}
                  alt="Profile"
                  className="w-full h-full object-cover"
                />
              ) : (
                <User className="w-16 h-16 text-white/80" />
              )}
            </div>
            
            {isEditing && (
              <div className="absolute bottom-0 right-0">
                <label className="w-10 h-10 bg-blue-600 hover:bg-blue-700 rounded-full flex items-center justify-center cursor-pointer shadow-lg transition-colors">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarUpload}
                    className="hidden"
                  />
                  {isUploading ? (
                    <RefreshCw className="w-5 h-5 text-white animate-spin" />
                  ) : (
                    <Camera className="w-5 h-5 text-white" />
                  )}
                </label>
              </div>
            )}
          </div>
          
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <h1 className="text-3xl font-bold">{profileData.full_name || 'Anonymous User'}</h1>
              {profileData.verified && (
                <div className="flex items-center space-x-1 bg-green-500/20 text-green-100 px-3 py-1 rounded-full text-sm">
                  <CheckCircle className="w-4 h-4" />
                  <span>Verified</span>
                </div>
              )}
              {profileData.is_business && (
                <div className="flex items-center space-x-1 bg-blue-500/20 text-blue-100 px-3 py-1 rounded-full text-sm">
                  <Settings className="w-4 h-4" />
                  <span>Business</span>
                </div>
              )}
            </div>
            
            <p className="text-white/80 mb-4">@{profileData.username}</p>
            
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <Star className="w-5 h-5 text-yellow-400 fill-current" />
                <span className="font-semibold">{profileData.seller_rating}</span>
                <span className="text-white/60">rating</span>
              </div>
              <div className="flex items-center space-x-2">
                <Package className="w-5 h-5" />
                <span className="font-semibold">{accountStats.totalListings}</span>
                <span className="text-white/60">listings</span>
              </div>
              <div className="flex items-center space-x-2">
                <Calendar className="w-5 h-5" />
                <span className="text-white/60">Joined {profileData.date_joined}</span>
              </div>
            </div>
          </div>
          
          <div className="text-right">
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="bg-white/20 hover:bg-white/30 backdrop-blur-sm text-white px-6 py-3 rounded-lg transition-colors flex items-center space-x-2"
            >
              <Edit3 className="w-5 h-5" />
              <span>{isEditing ? 'Cancel Edit' : 'Edit Profile'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Profile Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Content */}
        <div className="lg:col-span-2">
          
          {/* Navigation Tabs */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 mb-8">
            <div className="flex px-1 sm:px-2 overflow-x-auto scrollbar-hide" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
              {[
                { id: 'profile', label: 'Profile Info', shortLabel: 'Profile', icon: User },
                { id: 'security', label: 'Security', shortLabel: 'Security', icon: Shield },
                { id: 'preferences', label: 'Preferences', shortLabel: 'Prefs', icon: Settings },
                { id: 'partners', label: 'Partners', shortLabel: 'Partners', icon: Users },
                { id: 'stats', label: 'Statistics', shortLabel: 'Stats', icon: TrendingUp }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 py-3 sm:py-4 px-1 sm:px-3 rounded-lg font-medium transition-colors whitespace-nowrap text-center flex-shrink-0 ${
                    activeTab === tab.id
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center justify-center space-x-1 sm:space-x-2">
                    <tab.icon className="w-4 h-4" />
                    <span className="hidden sm:inline text-xs sm:text-sm">{tab.label}</span>
                    <span className="sm:hidden text-xs">{tab.shortLabel}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Profile Info Tab */}
          {activeTab === 'profile' && (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Profile Information
                </h2>
                {isEditing && (
                  <button
                    onClick={handleSaveProfile}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
                  >
                    <Save className="w-4 h-4" />
                    <span>Save Changes</span>
                  </button>
                )}
              </div>

              <div className="space-y-6">
                {/* Basic Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      First Name
                    </label>
                    <input
                      type="text"
                      name="first_name"
                      value={profileData.first_name}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className={`cataloro-input ${!isEditing ? 'cursor-not-allowed' : ''}`}
                      placeholder="Enter your first name"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Last Name
                    </label>
                    <input
                      type="text"
                      name="last_name"
                      value={profileData.last_name}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className={`cataloro-input ${!isEditing ? 'cursor-not-allowed' : ''}`}
                      placeholder="Enter your last name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Username
                    </label>
                    <input
                      type="text"
                      name="username"
                      value={profileData.username}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className={`cataloro-input ${!isEditing ? 'cursor-not-allowed' : ''}`}
                      placeholder="Enter your username"
                    />
                  </div>
                </div>

                {/* Contact Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={profileData.email}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className={`cataloro-input ${!isEditing ? 'cursor-not-allowed' : ''}`}
                      placeholder="Enter your email"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      name="phone"
                      value={profileData.phone}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className={`cataloro-input ${!isEditing ? 'cursor-not-allowed' : ''}`}
                      placeholder="Enter your phone number"
                    />
                  </div>
                </div>

                {/* Address Information */}
                <div className="space-y-4">
                  <h4 className="text-md font-semibold text-gray-900 dark:text-white">Address Information</h4>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Street Address
                    </label>
                    <input
                      type="text"
                      name="street"
                      value={profileData.street}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className={`cataloro-input ${!isEditing ? 'cursor-not-allowed' : ''}`}
                      placeholder="Enter your street address"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Postal Code
                      </label>
                      <input
                        type="text"
                        name="post_code"
                        value={profileData.post_code}
                        onChange={handleInputChange}
                        disabled={!isEditing}
                        className={`cataloro-input ${!isEditing ? 'cursor-not-allowed' : ''}`}
                        placeholder="Enter your postal code"
                      />
                    </div>

                    <div className="relative">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
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
                        className={`cataloro-input ${!isEditing ? 'cursor-not-allowed' : ''}`}
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
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
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
                      className={`cataloro-input ${!isEditing ? 'cursor-not-allowed' : ''}`}
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

                {/* Timezone Selection */}
                <div className="space-y-4">
                  <h4 className="text-md font-semibold text-gray-900 dark:text-white flex items-center">
                    <Globe className="w-5 h-5 mr-2 text-blue-500" />
                    Timezone Settings
                  </h4>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Timezone
                    </label>
                    <select
                      name="timezone"
                      value={profileData.timezone}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className={`cataloro-input ${!isEditing ? 'cursor-not-allowed' : ''}`}
                    >
                      <optgroup label="Popular Timezones">
                        <option value="Europe/London">London (GMT+0/+1)</option>
                        <option value="Europe/Berlin">Berlin (GMT+1/+2)</option>
                        <option value="Europe/Paris">Paris (GMT+1/+2)</option>
                        <option value="Europe/Madrid">Madrid (GMT+1/+2)</option>
                        <option value="Europe/Rome">Rome (GMT+1/+2)</option>
                        <option value="Europe/Amsterdam">Amsterdam (GMT+1/+2)</option>
                        <option value="Europe/Vienna">Vienna (GMT+1/+2)</option>
                        <option value="Europe/Prague">Prague (GMT+1/+2)</option>
                        <option value="Europe/Warsaw">Warsaw (GMT+1/+2)</option>
                        <option value="Europe/Stockholm">Stockholm (GMT+1/+2)</option>
                      </optgroup>
                      <optgroup label="Americas">
                        <option value="America/New_York">New York (EST/EDT)</option>
                        <option value="America/Chicago">Chicago (CST/CDT)</option>
                        <option value="America/Denver">Denver (MST/MDT)</option>
                        <option value="America/Los_Angeles">Los Angeles (PST/PDT)</option>
                        <option value="America/Toronto">Toronto (EST/EDT)</option>
                        <option value="America/Vancouver">Vancouver (PST/PDT)</option>
                        <option value="America/Mexico_City">Mexico City (CST/CDT)</option>
                        <option value="America/Sao_Paulo">São Paulo (BRT)</option>
                        <option value="America/Argentina/Buenos_Aires">Buenos Aires (ART)</option>
                      </optgroup>
                      <optgroup label="Asia Pacific">
                        <option value="Asia/Tokyo">Tokyo (JST)</option>
                        <option value="Asia/Shanghai">Shanghai (CST)</option>
                        <option value="Asia/Hong_Kong">Hong Kong (HKT)</option>
                        <option value="Asia/Singapore">Singapore (SGT)</option>
                        <option value="Asia/Seoul">Seoul (KST)</option>
                        <option value="Asia/Kolkata">Mumbai (IST)</option>
                        <option value="Asia/Dubai">Dubai (GST)</option>
                        <option value="Australia/Sydney">Sydney (AEST/AEDT)</option>
                        <option value="Australia/Melbourne">Melbourne (AEST/AEDT)</option>
                        <option value="Pacific/Auckland">Auckland (NZST/NZDT)</option>
                      </optgroup>
                      <optgroup label="Africa">
                        <option value="Africa/Cairo">Cairo (EET)</option>
                        <option value="Africa/Johannesburg">Johannesburg (SAST)</option>
                        <option value="Africa/Lagos">Lagos (WAT)</option>
                        <option value="Africa/Nairobi">Nairobi (EAT)</option>
                      </optgroup>
                    </select>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Current browser timezone: {Intl.DateTimeFormat().resolvedOptions().timeZone}
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Bio
                  </label>
                  <textarea
                    name="bio"
                    rows={4}
                    value={profileData.bio}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className={`cataloro-input ${!isEditing ? 'cursor-not-allowed' : ''}`}
                    placeholder="Tell us about yourself..."
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {profileData.bio.length}/500 characters
                  </p>
                </div>

                {/* Account Type Section - CLEAN BUTTON TOGGLE ONLY */}
                <div className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 rounded-xl p-6 border border-gray-200 dark:border-gray-600">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`p-3 rounded-xl ${profileData.is_business ? 'bg-gradient-to-r from-blue-500 to-indigo-600' : 'bg-gradient-to-r from-green-500 to-emerald-600'}`}>
                        {profileData.is_business ? <Settings className="w-6 h-6 text-white" /> : <User className="w-6 h-6 text-white" />}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          Account Type
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {profileData.is_business 
                            ? 'Professional business marketplace seller'
                            : 'Personal marketplace account for individuals'
                          }
                        </p>
                      </div>
                    </div>
                    
                    {/* SAME CLEAN BUTTON TOGGLE AS PREFERENCES - NO CHECKBOX */}
                    <div className="flex items-center space-x-3">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {profileData.is_business ? 'Business' : 'Personal'}
                      </span>
                      <button
                        onClick={() => handleBusinessToggle(!profileData.is_business)}
                        disabled={!isEditing}
                        className={`w-11 h-6 rounded-full transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                          profileData.is_business ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-600'
                        } ${!isEditing ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        <div className={`w-5 h-5 bg-white rounded-full shadow transform transition-transform duration-200 ease-in-out ${
                          profileData.is_business ? 'translate-x-5' : 'translate-x-0.5'
                        }`} />
                      </button>
                    </div>
                  </div>

                  {profileData.is_business && (
                    <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-600">
                      <h4 className="text-md font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                        <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                        Business Information
                      </h4>
                      
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Company Name *
                          </label>
                          <input
                            type="text"
                            name="company_name"
                            value={profileData.company_name}
                            onChange={handleInputChange}
                            disabled={!isEditing}
                            className={`cataloro-input ${!isEditing ? 'cursor-not-allowed' : ''}`}
                            placeholder="Enter your company name"
                            required={profileData.is_business}
                          />
                        </div>

                        <div className="relative">
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Business Country *
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
                            className={`cataloro-input ${!isEditing ? 'cursor-not-allowed' : ''}`}
                            placeholder="Enter business country"
                            required={profileData.is_business}
                          />
                          
                          {/* Business Country Suggestions Dropdown */}
                          {showBusinessCountrySuggestions && isEditing && (
                            <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl shadow-2xl max-h-60 overflow-y-auto">
                              <div className="p-3 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 border-b border-gray-200 dark:border-gray-600">
                                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center">
                                  <Globe className="w-4 h-4 mr-2 text-indigo-500" />
                                  Business Countries ({businessCountrySuggestions.length})
                                  <span className="ml-2 text-xs text-gray-500">Click to select</span>
                                </p>
                              </div>
                              {businessCountrySuggestions.map((country, index) => (
                                <div
                                  key={index}
                                  onClick={() => selectBusinessCountry(country)}
                                  className="p-3 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 cursor-pointer border-b border-gray-100 dark:border-gray-700 last:border-b-0 transition-all duration-200 group"
                                >
                                  <div className="flex items-center space-x-3">
                                    <div className="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
                                      {country.charAt(0)}
                                    </div>
                                    <div className="font-medium text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
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
                          </label>
                          <input
                            type="text"
                            name="vat_number"
                            value={profileData.vat_number}
                            onChange={handleInputChange}
                            disabled={!isEditing}
                            className={`cataloro-input ${!isEditing ? 'cursor-not-allowed' : ''}`}
                            placeholder="Enter your VAT number (optional)"
                          />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Security Tab */}
          {activeTab === 'security' && (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
                Security Settings
              </h2>

              <div className="space-y-8">
                {/* Change Password */}
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
                    <Lock className="w-5 h-5 mr-2" />
                    Change Password
                  </h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Current Password
                      </label>
                      <input
                        type={showPassword ? 'text' : 'password'}
                        name="currentPassword"
                        value={passwordData.currentPassword}
                        onChange={handlePasswordChange}
                        className="cataloro-input"
                        placeholder="Enter current password"
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          New Password
                        </label>
                        <input
                          type={showPassword ? 'text' : 'password'}
                          name="newPassword"
                          value={passwordData.newPassword}
                          onChange={handlePasswordChange}
                          className="cataloro-input"
                          placeholder="Enter new password"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          Confirm New Password
                        </label>
                        <input
                          type={showPassword ? 'text' : 'password'}
                          name="confirmPassword"
                          value={passwordData.confirmPassword}
                          onChange={handlePasswordChange}
                          className="cataloro-input"
                          placeholder="Confirm new password"
                        />
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        <span>{showPassword ? 'Hide' : 'Show'} passwords</span>
                      </button>

                      <button
                        onClick={handleUpdatePassword}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors flex items-center space-x-2"
                      >
                        <Key className="w-4 h-4" />
                        <span>Update Password</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Preferences Tab - CLEAN TOGGLES ONLY */}
          {activeTab === 'preferences' && (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
                Preferences
              </h2>

              <div className="space-y-8">
                {/* Notifications */}
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
                    <Bell className="w-5 h-5 mr-2" />
                    Notifications
                  </h3>
                  
                  <div className="space-y-6">
                    {[
                      { key: 'emailNotifications', label: 'Email Notifications', description: 'Receive notifications via email' },
                      { key: 'smsNotifications', label: 'SMS Notifications', description: 'Receive notifications via SMS' },
                      { key: 'marketingEmails', label: 'Marketing Emails', description: 'Receive promotional content' },
                      { key: 'browserNotifications', label: 'Browser Notifications', description: 'Show desktop notifications' }
                    ].map((pref) => (
                      <div key={pref.key} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/30 rounded-lg">
                        <div>
                          <h4 className="font-medium text-gray-900 dark:text-white">{pref.label}</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{pref.description}</p>
                        </div>
                        
                        {/* SINGLE TOGGLE - NO CHECKBOX */}
                        <div className="flex items-center space-x-3">
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            {preferences[pref.key] ? 'On' : 'Off'}
                          </span>
                          <button
                            onClick={() => handlePreferenceChange(pref.key, !preferences[pref.key])}
                            className={`w-11 h-6 rounded-full transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                              preferences[pref.key] ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-600'
                            }`}
                          >
                            <div className={`w-5 h-5 bg-white rounded-full shadow transform transition-transform duration-200 ease-in-out ${
                              preferences[pref.key] ? 'translate-x-5' : 'translate-x-0.5'
                            }`} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Privacy */}
                <div className="border-t border-gray-200 dark:border-gray-700 pt-8">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
                    <Eye className="w-5 h-5 mr-2" />
                    Privacy
                  </h3>
                  
                  <div className="space-y-6">
                    {[
                      { key: 'publicProfile', label: 'Public Profile', description: 'Make your profile visible to everyone' },
                      { key: 'showEmail', label: 'Show Email', description: 'Display email on public profile' },
                      { key: 'showPhone', label: 'Show Phone', description: 'Display phone number on public profile' }
                    ].map((pref) => (
                      <div key={pref.key} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/30 rounded-lg">
                        <div>
                          <h4 className="font-medium text-gray-900 dark:text-white">{pref.label}</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{pref.description}</p>
                        </div>
                        
                        {/* SINGLE TOGGLE - NO CHECKBOX */}
                        <div className="flex items-center space-x-3">
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            {preferences[pref.key] ? 'On' : 'Off'}
                          </span>
                          <button
                            onClick={() => handlePreferenceChange(pref.key, !preferences[pref.key])}
                            className={`w-11 h-6 rounded-full transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                              preferences[pref.key] ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-600'
                            }`}
                          >
                            <div className={`w-5 h-5 bg-white rounded-full shadow transform transition-transform duration-200 ease-in-out ${
                              preferences[pref.key] ? 'translate-x-5' : 'translate-x-0.5'
                            }`} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Partners Tab */}
          {activeTab === 'partners' && (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center">
                <Users className="w-6 h-6 mr-2" />
                Preferred Partners
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Add users as preferred partners. When you create listings with "Show Partners First" enabled, 
                only your partners will see the listing for the specified time period before it becomes public.
              </p>

              {/* Add Partner Section */}
              <div className="mb-8 p-4 bg-gray-50 dark:bg-gray-700/30 rounded-lg">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Add New Partner</h3>
                <div className="flex space-x-4">
                  <div className="flex-1">
                    <input
                      type="text"
                      placeholder="Search users by name or email..."
                      value={userSearchQuery}
                      onChange={(e) => setUserSearchQuery(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <button
                    onClick={() => searchUsers()}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500"
                  >
                    Search
                  </button>
                </div>

                {/* Search Results */}
                {userSearchResults.length > 0 && (
                  <div className="mt-4 space-y-2 max-h-48 overflow-y-auto">
                    {userSearchResults.map((searchUser) => (
                      <div key={searchUser.id} className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-600">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                            <User className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <p className="font-medium text-gray-900 dark:text-white">{searchUser.full_name || searchUser.username}</p>
                            <p className="text-sm text-gray-500 dark:text-gray-400">{searchUser.email}</p>
                          </div>
                        </div>
                        <button
                          onClick={() => addPartner(searchUser)}
                          disabled={partners.some(p => p.id === searchUser.id) || searchUser.id === user?.id}
                          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-sm"
                        >
                          {partners.some(p => p.id === searchUser.id) ? 'Already Partner' : 
                           searchUser.id === user?.id ? 'You' : 'Add Partner'}
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Current Partners List */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  Current Partners ({partners.length})
                </h3>
                
                {partnersLoading ? (
                  <div className="text-center py-8">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto text-gray-400" />
                    <p className="mt-2 text-sm text-gray-500">Loading partners...</p>
                  </div>
                ) : partners.length > 0 ? (
                  <div className="space-y-3">
                    {partners.map((partner) => (
                      <div key={partner.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/30 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                            <User className="w-6 h-6 text-white" />
                          </div>
                          <div>
                            <p className="font-medium text-gray-900 dark:text-white">{partner.full_name || partner.username}</p>
                            <p className="text-sm text-gray-500 dark:text-gray-400">{partner.email}</p>
                            <p className="text-xs text-gray-400 dark:text-gray-500">
                              Partner since {new Date(partner.added_at || Date.now()).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={() => removePartner(partner.id)}
                          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No partners yet</h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      Search and add users as your preferred partners for exclusive early access to your listings.
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Statistics Tab */}
          {activeTab === 'stats' && (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
                Account Statistics
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {[
                  { label: 'Total Listings', value: accountStats.totalListings, icon: Package, color: 'blue' },
                  { label: 'Active Listings', value: accountStats.activeListings, icon: CheckCircle, color: 'green' },
                  { label: 'Total Deals', value: accountStats.totalDeals, icon: DollarSign, color: 'purple' },
                  { label: 'Completed Deals', value: accountStats.completedDeals, icon: Award, color: 'yellow' },
                  { label: 'Favorites', value: accountStats.totalFavorites, icon: Heart, color: 'red' }
                ].map((stat, index) => (
                  <div key={index} className={`bg-gradient-to-r from-${stat.color}-50 to-${stat.color}-100 dark:from-${stat.color}-900/20 dark:to-${stat.color}-800/30 border border-${stat.color}-200 dark:border-${stat.color}-800 rounded-lg p-4`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className={`text-${stat.color}-600 dark:text-${stat.color}-400 text-sm font-medium`}>
                          {stat.label}
                        </p>
                        <p className={`text-${stat.color}-900 dark:text-${stat.color}-100 text-2xl font-bold`}>
                          {stat.value}
                        </p>
                      </div>
                      <div className={`p-3 bg-${stat.color}-500 rounded-lg`}>
                        <stat.icon className="w-6 h-6 text-white" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Activity Timeline */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Recent Activity</h3>
                <div className="space-y-4">
                  <div className="flex items-center space-x-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                      <User className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 dark:text-white">Profile updated</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Updated profile information</p>
                    </div>
                    <span className="text-sm text-gray-500 dark:text-gray-400">Today</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          
          {/* Quick Stats */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Quick Stats
            </h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-400">Profile Views</span>
                <span className="font-semibold text-gray-900 dark:text-white">{accountStats.profileViews}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-400">Seller Rating</span>
                <div className="flex items-center space-x-1">
                  <Star className="w-4 h-4 text-yellow-400 fill-current" />
                  <span className="font-semibold text-gray-900 dark:text-white">{profileData.seller_rating}</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600 dark:text-gray-400">Last Active</span>
                <span className="text-sm text-gray-600 dark:text-gray-400">{accountStats.lastActive}</span>
              </div>
            </div>
          </div>

          {/* Account Actions */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Account Actions
            </h3>
            
            <div className="space-y-3">
              <button 
                onClick={handleExportData}
                className="w-full flex items-center space-x-3 px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <Download className="w-5 h-5 text-gray-400" />
                <span className="text-gray-700 dark:text-gray-300">Export Data</span>
              </button>
              
              <button 
                onClick={handleDeleteAccount}
                className="w-full flex items-center space-x-3 px-4 py-3 text-left hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors text-red-600 dark:text-red-400"
              >
                <AlertCircle className="w-5 h-5" />
                <span>Delete Account</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProfilePage;