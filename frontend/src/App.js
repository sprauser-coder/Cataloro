import React, { useState, useEffect, useContext, createContext } from 'react';
import './App.css';
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Textarea } from './components/ui/textarea';
import { Label } from './components/ui/label';
import { Avatar, AvatarFallback, AvatarImage } from './components/ui/avatar';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { useToast } from './hooks/use-toast';
import { Toaster } from './components/ui/toaster';
import { Search, ShoppingCart, User, Plus, Heart, Star, Clock, Euro, Package, Eye, Gavel, Trash2, Edit, MapPin, X } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Utility function to format error messages
const formatErrorMessage = (error, fallbackMessage) => {
  try {
    if (!error?.response?.data?.detail) {
      return fallbackMessage;
    }
    
    const detail = error.response.data.detail;
    
    if (Array.isArray(detail)) {
      // Multiple validation errors - ensure we return a single string
      const errorMessages = detail.map(err => {
        if (!err || typeof err !== 'object') {
          return 'Invalid error format';
        }
        const location = (err.loc && Array.isArray(err.loc)) ? err.loc.join('.') + ': ' : '';
        const message = typeof err.msg === 'string' ? err.msg : 'Validation error';
        return `${location}${message}`;
      });
      return errorMessages.join(', ');
    } else if (typeof detail === 'string') {
      // Single string error
      return detail;
    } else if (detail && typeof detail === 'object' && typeof detail.msg === 'string') {
      // Single validation error object
      return detail.msg;
    }
    
    return fallbackMessage;
  } catch (e) {
    // Fallback in case of any error in processing
    return fallbackMessage;
  }
};

// Auth Context
const AuthContext = createContext();

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const savedUser = localStorage.getItem('user');
        if (savedUser) {
          setUser(JSON.parse(savedUser));
        }
      } catch (error) {
        console.error('Invalid token');
        logout();
      }
    }
    setLoading(false);
  }, [token]);

  const login = (tokenData) => {
    setToken(tokenData.access_token);
    setUser(tokenData.user);
    localStorage.setItem('token', tokenData.access_token);
    localStorage.setItem('user', JSON.stringify(tokenData.user));
    axios.defaults.headers.common['Authorization'] = `Bearer ${tokenData.access_token}`;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    token,
    login,
    logout,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { token, loading } = useAuth();
  
  if (loading) {
    return <div className="flex justify-center items-center min-h-screen">Loading...</div>;
  }
  
  return token ? children : <Navigate to="/auth" />;
};

// Header Component
const Header = () => {
  const { user, logout } = useAuth();
  const [cartCount, setCartCount] = useState(0);
  const [customNavigation, setCustomNavigation] = useState([]);
  const [siteSettings, setSiteSettings] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      fetchCartCount();
    }
    
    // Load navigation and settings from global state or fetch
    const loadHeaderData = () => {
      if (window.cataloroNavigation) {
        setCustomNavigation(window.cataloroNavigation);
      }
      if (window.cataloroSettings) {
        setSiteSettings(window.cataloroSettings);
      }
    };
    
    loadHeaderData();
    
    // Listen for navigation updates
    const handleNavigationUpdate = (event) => {
      setCustomNavigation(event.detail);
    };
    
    // Listen for settings updates (e.g., after logo upload)
    const handleSettingsUpdate = (event) => {
      if (window.cataloroSettings) {
        setSiteSettings(window.cataloroSettings);
      }
    };
    
    window.addEventListener('cataloroNavigationLoaded', handleNavigationUpdate);
    window.addEventListener('cataloroSettingsUpdated', handleSettingsUpdate);
    
    return () => {
      window.removeEventListener('cataloroNavigationLoaded', handleNavigationUpdate);
      window.removeEventListener('cataloroSettingsUpdated', handleSettingsUpdate);
    };
  }, [user]);

  const fetchCartCount = async () => {
    try {
      const response = await axios.get(`${API}/cart`);
      setCartCount(response.data.length);
    } catch (error) {
      console.error('Error fetching cart count:', error);
    }
  };

  const siteName = siteSettings?.site_name || 'Cataloro';

  return (
    <header className="bg-white shadow-lg border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center space-x-2">
            {siteSettings?.header_logo_url && siteSettings.header_logo_url.trim() !== '' ? (
              <img 
                src={`${BACKEND_URL}${siteSettings.header_logo_url}`} 
                alt={siteSettings.header_logo_alt || 'Logo'} 
                className="h-8 w-auto object-contain"
                onError={(e) => {
                  // If image fails to load, hide it and show fallback
                  e.target.style.display = 'none';
                  const fallback = e.target.parentElement.querySelector('.logo-fallback');
                  if (fallback) fallback.style.display = 'flex';
                }}
              />
            ) : null}
            <div className={`logo-fallback flex items-center space-x-2 ${siteSettings?.header_logo_url && siteSettings.header_logo_url.trim() !== '' ? 'hidden' : ''}`}>
              <Package className="h-8 w-8 text-indigo-600" />
              <span className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                {siteName}
              </span>
            </div>
          </Link>
          
          <nav className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-gray-700 hover:text-indigo-600 font-medium transition-colors">
              Browse
            </Link>
            <Link to="/sell" className="text-gray-700 hover:text-indigo-600 font-medium transition-colors">
              Sell
            </Link>
            <Link to="/orders" className="text-gray-700 hover:text-indigo-600 font-medium transition-colors">
              My Orders
            </Link>
            {/* Dynamic Navigation from CMS */}
            {customNavigation.map((navItem) => (
              <Link
                key={navItem.id}
                to={navItem.url}
                className="text-gray-700 hover:text-indigo-600 font-medium transition-colors"
                target={navItem.target}
              >
                {navItem.label}
              </Link>
            ))}
            {user?.role === 'admin' && (
              <Link to="/admin" className="text-red-600 hover:text-red-800 font-medium transition-colors">
                Cataloro Admin
              </Link>
            )}
          </nav>

          <div className="flex items-center space-x-4">
            <Link to="/cart" className="relative">
              <Button variant="ghost" size="sm" className="relative">
                <ShoppingCart className="h-5 w-5" />
                {cartCount > 0 && (
                  <Badge className="absolute -top-2 -right-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs">
                    {cartCount}
                  </Badge>
                )}
              </Button>
            </Link>
            
            <div className="flex items-center space-x-2">
              <Avatar className="h-8 w-8">
                <AvatarFallback>{user?.full_name?.charAt(0) || 'U'}</AvatarFallback>
              </Avatar>
              <span className="text-sm font-medium">{user?.full_name}</span>
              <Button variant="ghost" size="sm" onClick={logout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

// Auth Component
const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    full_name: '',
    role: 'buyer',
    phone: '',
    address: ''
  });
  const { login } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const data = isLogin ? 
        { email: formData.email, password: formData.password } : 
        formData;
      
      const response = await axios.post(`${API}${endpoint}`, data);
      login(response.data);
      navigate('/');
      toast({
        title: isLogin ? "Welcome back!" : "Account created!",
        description: isLogin ? "You've been logged in successfully." : "Your account has been created and you're now logged in."
      });
    } catch (error) {
      toast({
        title: "Error",
        description: formatErrorMessage(error, "Something went wrong"),
        variant: "destructive"
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-2xl border-0 bg-white/90 backdrop-blur-sm">
          <CardHeader className="text-center pb-8">
            <div className="mx-auto mb-4 p-3 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full w-fit">
              <Package className="h-8 w-8 text-white" />
            </div>
            <CardTitle className="text-2xl font-bold">
              {isLogin ? 'Welcome Back' : 'Join Cataloro'}
            </CardTitle>
            <CardDescription>
              {isLogin ? 'Sign in to your account' : 'Create your account and start trading on Cataloro'}
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                  className="mt-1"
                />
              </div>
              
              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                  className="mt-1"
                />
              </div>
              
              {!isLogin && (
                <>
                  <div>
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      value={formData.username}
                      onChange={(e) => setFormData({...formData, username: e.target.value})}
                      required
                      className="mt-1"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="full_name">Full Name</Label>
                    <Input
                      id="full_name"
                      value={formData.full_name}
                      onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                      required
                      className="mt-1"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="role">I want to</Label>
                    <Select value={formData.role} onValueChange={(value) => setFormData({...formData, role: value})}>
                      <SelectTrigger className="mt-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="buyer">Buy items</SelectItem>
                        <SelectItem value="seller">Sell items</SelectItem>
                        <SelectItem value="both">Both buy and sell</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="phone">Phone (Optional)</Label>
                    <Input
                      id="phone"
                      value={formData.phone}
                      onChange={(e) => setFormData({...formData, phone: e.target.value})}
                      className="mt-1"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="address">Address (Optional)</Label>
                    <Input
                      id="address"
                      value={formData.address}
                      onChange={(e) => setFormData({...formData, address: e.target.value})}
                      className="mt-1"
                    />
                  </div>
                </>
              )}
              
              <Button type="submit" className="w-full mt-6 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700">
                {isLogin ? 'Sign In' : 'Create Account'}
              </Button>
            </form>
            
            <div className="mt-6 text-center">
              <button
                type="button"
                onClick={() => setIsLogin(!isLogin)}
                className="text-indigo-600 hover:text-indigo-800 font-medium"
              >
                {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Home Component
const Home = () => {
  const [listings, setListings] = useState([]);
  const [categories, setCategories] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [listingType, setListingType] = useState('');
  const [loading, setLoading] = useState(true);
  const [siteSettings, setSiteSettings] = useState(null);
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    fetchCategories();
    fetchListings();
    
    // Load site settings for dynamic content
    if (window.cataloroSettings) {
      setSiteSettings(window.cataloroSettings);
    }
  }, []);

  useEffect(() => {
    fetchListings();
  }, [searchTerm, selectedCategory, listingType]);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchListings = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      if (selectedCategory && selectedCategory !== 'all') params.append('category', selectedCategory);
      if (listingType) params.append('listing_type', listingType);
      
      const response = await axios.get(`${API}/listings?${params}`);
      setListings(response.data);
    } catch (error) {
      console.error('Error fetching listings:', error);
      toast({
        title: "Error",
        description: "Failed to fetch listings",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (listing) => {
    if (listing.listing_type === 'fixed_price') {
      return `€${listing.price?.toFixed(2)}`;
    } else {
      if (listing.current_bid) {
        return `Current bid: €${listing.current_bid.toFixed(2)}`;
      } else {
        return `Starting bid: $${listing.starting_bid?.toFixed(2)}`;
      }
    }
  };

  const formatTimeRemaining = (endTime) => {
    const now = new Date();
    const end = new Date(endTime);
    const diff = end - now;
    
    if (diff <= 0) return 'Auction ended';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  // Dynamic hero section style based on CMS settings
  const getHeroStyle = () => {
    if (!siteSettings) return {};
    
    const baseStyle = {
      background: siteSettings.hero_background_type === 'gradient' 
        ? `linear-gradient(135deg, ${siteSettings.hero_background_gradient_start} 0%, ${siteSettings.hero_background_gradient_end} 100%)`
        : siteSettings.hero_background_color,
      color: siteSettings.hero_text_color,
      height: siteSettings.hero_height || '600px',
      display: 'flex',
      alignItems: 'center'
    };
    
    return baseStyle;
  };

  const heroTitle = siteSettings?.hero_title || 'Discover Amazing Deals';
  const heroSubtitle = siteSettings?.hero_subtitle || 'Buy and sell with confidence on Cataloro - your trusted marketplace for amazing deals';

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      {/* Dynamic Hero Section */}
      <div className="text-white" style={getHeroStyle()}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
          <div className="text-center">
            <h1 
              className="text-6xl font-bold mb-6"
              style={{color: siteSettings?.hero_title_color || '#ffffff'}}
            >
              {heroTitle}
            </h1>
            <p 
              className="text-xl mb-8 opacity-90"
              style={{color: siteSettings?.hero_subtitle_color || '#f1f5f9'}}
            >
              {heroSubtitle}
            </p>
            
            {/* Search Bar */}
            <div className="max-w-2xl mx-auto">
              <div className="flex space-x-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <Input
                    placeholder="Search for anything..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 h-12 bg-white text-gray-900"
                  />
                </div>
                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger className="w-48 h-12 bg-white text-gray-900">
                    <SelectValue placeholder="All Categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    {categories.map((category) => (
                      <SelectItem key={category} value={category}>
                        {category}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="mb-6">
          <Tabs value={listingType} onValueChange={setListingType}>
            <TabsList>
              <TabsTrigger value="">All Items</TabsTrigger>
              <TabsTrigger value="fixed_price">Buy Now</TabsTrigger>
              <TabsTrigger value="auction">Auctions</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {/* Listings Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <div className="h-48 bg-gray-300 rounded-t-lg"></div>
                <CardContent className="p-4">
                  <div className="h-4 bg-gray-300 rounded mb-2"></div>
                  <div className="h-3 bg-gray-300 rounded mb-2"></div>
                  <div className="h-3 bg-gray-300 rounded w-1/2"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {listings.map((listing) => (
              <Card key={listing.id} className="hover:shadow-lg transition-shadow cursor-pointer group" onClick={() => navigate(`/listing/${listing.id}`)}>
                <div className="relative overflow-hidden rounded-t-lg">
                  <img
                    src={
                      listing.images?.[0] 
                        ? (listing.images[0].startsWith('/uploads/') 
                            ? `${BACKEND_URL}${listing.images[0]}` 
                            : listing.images[0])
                        : 'https://images.unsplash.com/photo-1534452203293-494d7ddbf7e0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwzfHxzaG9wcGluZ3xlbnwwfHx8fDE3NTU4Njk0MzR8MA&ixlib=rb-4.1.0&q=85'
                    }
                    alt={listing.title}
                    className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-2 left-2">
                    <Badge variant={listing.listing_type === 'auction' ? 'destructive' : 'default'}>
                      {listing.listing_type === 'auction' ? (
                        <><Gavel className="h-3 w-3 mr-1" /> Auction</>
                      ) : (
                        <><Euro className="h-3 w-3 mr-1" /> Buy Now</>
                      )}
                    </Badge>
                  </div>
                  <div className="absolute top-2 right-2">
                    <Badge variant="secondary" className="bg-white/90">
                      <Eye className="h-3 w-3 mr-1" />
                      {listing.views}
                    </Badge>
                  </div>
                </div>
                
                <CardContent className="p-4">
                  <h3 className="font-semibold text-lg mb-2 line-clamp-2">{listing.title}</h3>
                  <p className="text-gray-600 text-sm mb-3 line-clamp-2">{listing.description}</p>
                  
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-lg font-bold text-indigo-600">
                      {formatPrice(listing)}
                    </span>
                    <Badge variant="outline">{listing.condition}</Badge>
                  </div>
                  
                  {listing.listing_type === 'auction' && listing.auction_end_time && (
                    <div className="flex items-center text-sm text-gray-500 mb-3">
                      <Clock className="h-4 w-4 mr-1" />
                      {formatTimeRemaining(listing.auction_end_time)}
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between">
                    <Badge variant="secondary">{listing.category}</Badge>
                    <span className="text-sm text-gray-500 flex items-center">
                      <MapPin className="h-3 w-3 mr-1" />
                      {listing.location}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {!loading && listings.length === 0 && (
          <div className="text-center py-12">
            <Package className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No items found</h3>
            <p className="text-gray-500 mb-4">Try adjusting your search or filters</p>
            <Button onClick={() => navigate('/sell')} className="bg-gradient-to-r from-indigo-600 to-purple-600">
              <Plus className="h-4 w-4 mr-2" />
              List Your First Item
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

// Listing Detail Component
const ListingDetail = () => {
  const { id } = useParams();
  const [listing, setListing] = useState(null);
  const [bids, setBids] = useState([]);
  const [bidAmount, setBidAmount] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    fetchListing();
    fetchBids();
  }, [id]);

  const fetchListing = async () => {
    try {
      const response = await axios.get(`${API}/listings/${id}`);
      setListing(response.data);
    } catch (error) {
      console.error('Error fetching listing:', error);
      toast({
        title: "Error",
        description: "Failed to fetch listing details",
        variant: "destructive"
      });
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const fetchBids = async () => {
    try {
      const response = await axios.get(`${API}/listings/${id}/bids`);
      setBids(response.data);
    } catch (error) {
      console.error('Error fetching bids:', error);
    }
  };

  const handleAddToCart = async () => {
    try {
      await axios.post(`${API}/cart`, {
        listing_id: id,
        quantity: quantity
      });
      toast({
        title: "Added to cart!",
        description: "Item has been added to your cart"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: formatErrorMessage(error, "Failed to add to cart"),
        variant: "destructive"
      });
    }
  };

  const handlePlaceBid = async () => {
    try {
      await axios.post(`${API}/bids`, {
        listing_id: id,
        amount: parseFloat(bidAmount)
      });
      setBidAmount('');
      fetchListing();
      fetchBids();
      toast({
        title: "Bid placed!",
        description: "Your bid has been placed successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: formatErrorMessage(error, "Failed to place bid"),
        variant: "destructive"
      });
    }
  };

  const handleBuyNow = async () => {
    try {
      await axios.post(`${API}/orders`, {
        listing_id: id,
        quantity: quantity,
        shipping_address: user?.address || "Please update your address"
      });
      toast({
        title: "Order placed!",
        description: "Your order has been placed successfully"
      });
      navigate('/orders');
    } catch (error) {
      toast({
        title: "Error",
        description: formatErrorMessage(error, "Failed to place order"),
        variant: "destructive"
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex justify-center items-center h-96">
          <div className="animate-pulse">Loading...</div>
        </div>
      </div>
    );
  }

  if (!listing) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="text-center py-12">Listing not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Images Gallery */}
          <div>
            {listing.images && listing.images.length > 0 ? (
              <div className="space-y-4">
                {/* Main Image */}
                <img
                  src={
                    listing.images[0].startsWith('/uploads/') 
                      ? `${API}${listing.images[0]}` 
                      : listing.images[0]
                  }
                  alt={listing.title}
                  className="w-full h-96 object-cover rounded-lg main-listing-image"
                />
                
                {/* Thumbnail Gallery */}
                {listing.images.length > 1 && (
                  <div className="grid grid-cols-3 gap-2">
                    {listing.images.slice(1).map((image, index) => (
                      <img
                        key={index}
                        src={
                          image.startsWith('/uploads/') 
                            ? `${API}${image}` 
                            : image
                        }
                        alt={`${listing.title} ${index + 2}`}
                        className="w-full h-24 object-cover rounded cursor-pointer hover:opacity-75"
                        onClick={() => {
                          // You can implement image switching functionality here
                          const mainImg = document.querySelector('.main-listing-image');
                          if (mainImg) {
                            mainImg.src = image.startsWith('/uploads/') ? `${BACKEND_URL}${image}` : image;
                          }
                        }}
                      />
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <img
                src="https://images.unsplash.com/photo-1534452203293-494d7ddbf7e0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwzfHxzaG9wcGluZ3xlbnwwfHx8fDE3NTU4Njk0MzR8MA&ixlib=rb-4.1.0&q=85"
                alt={listing.title}
                className="w-full h-96 object-cover rounded-lg"
              />
            )}
          </div>

          {/* Details */}
          <div>
            <div className="mb-4">
              <Badge variant={listing.listing_type === 'auction' ? 'destructive' : 'default'} className="mb-2">
                {listing.listing_type === 'auction' ? 'Auction' : 'Buy Now'}
              </Badge>
              <h1 className="text-3xl font-bold mb-2">{listing.title}</h1>
              <p className="text-gray-600">{listing.description}</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm mb-6">
              {listing.listing_type === 'fixed_price' ? (
                <>
                  <div className="text-3xl font-bold text-green-600 mb-4">
                    €{listing.price?.toFixed(2)}
                  </div>
                  <div className="mb-4">
                    <Label htmlFor="quantity">Quantity</Label>
                    <Input
                      id="quantity"
                      type="number"
                      min="1"
                      max={listing.quantity}
                      value={quantity}
                      onChange={(e) => setQuantity(parseInt(e.target.value))}
                      className="mt-1 w-24"
                    />
                  </div>
                  <div className="space-y-2">
                    <Button onClick={handleBuyNow} className="w-full bg-green-600 hover:bg-green-700">
                      Buy Now
                    </Button>
                    <Button onClick={handleAddToCart} variant="outline" className="w-full">
                      Add to Cart
                    </Button>
                  </div>
                </>
              ) : (
                <>
                  <div className="mb-4">
                    <div className="text-xl font-semibold">
                      Current Bid: ${listing.current_bid?.toFixed(2) || listing.starting_bid?.toFixed(2)}
                    </div>
                    {listing.auction_end_time && (
                      <div className="text-sm text-gray-500">
                        Ends: {new Date(listing.auction_end_time).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                  <div className="mb-4">
                    <Label htmlFor="bid">Your Bid ($)</Label>
                    <Input
                      id="bid"
                      type="number"
                      value={bidAmount}
                      onChange={(e) => setBidAmount(e.target.value)}
                      className="mt-1"
                      placeholder="Enter bid amount"
                    />
                  </div>
                  <Button onClick={handlePlaceBid} className="w-full">
                    Place Bid
                  </Button>
                  {listing.buyout_price && (
                    <Button onClick={handleBuyNow} variant="outline" className="w-full mt-2">
                      Buy Now - €{listing.buyout_price.toFixed(2)}
                    </Button>
                  )}
                </>
              )}
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm">
              <h3 className="font-semibold mb-4">Item Details</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Condition:</span>
                  <span>{listing.condition}</span>
                </div>
                <div className="flex justify-between">
                  <span>Category:</span>
                  <span>{listing.category}</span>
                </div>
                <div className="flex justify-between">
                  <span>Location:</span>
                  <span>{listing.location}</span>
                </div>
                <div className="flex justify-between">
                  <span>Shipping:</span>
                  <span>${listing.shipping_cost?.toFixed(2) || 'Free'}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bid History for Auctions */}
        {listing.listing_type === 'auction' && bids.length > 0 && (
          <div className="mt-8">
            <Card>
              <CardHeader>
                <CardTitle>Bid History</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {bids.slice(0, 5).map((bid) => (
                    <div key={bid.id} className="flex justify-between items-center py-2 border-b">
                      <span>${bid.amount.toFixed(2)}</span>
                      <span className="text-sm text-gray-500">
                        {new Date(bid.timestamp).toLocaleDateString()}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

// Sell Component
const Sell = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    listing_type: 'fixed_price',
    price: '',
    starting_bid: '',
    buyout_price: '',
    condition: 'New',
    quantity: 1,
    location: '',
    shipping_cost: '',
    auction_duration_hours: 24
  });
  const [categories, setCategories] = useState([]);
  const [uploadedImages, setUploadedImages] = useState([]); // Array to store uploaded image URLs
  const [uploading, setUploading] = useState(false); // Loading state for image uploads
  const { user } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast({
        title: "Error",
        description: "Please select an image file",
        variant: "destructive"
      });
      return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast({
        title: "Error",
        description: "File size too large. Maximum 10MB allowed",
        variant: "destructive"
      });
      return;
    }

    // Check if we already have 3 images
    if (uploadedImages.length >= 3) {
      toast({
        title: "Error",
        description: "Maximum 3 images allowed per listing",
        variant: "destructive"
      });
      return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API}/listings/upload-image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Add the uploaded image URL to our array
      setUploadedImages(prev => [...prev, response.data.image_url]);

      toast({
        title: "Success",
        description: "Image uploaded successfully",
      });

      // Clear the file input
      event.target.value = '';

    } catch (error) {
      console.error('Image upload error:', error.response?.data);
      
      toast({
        title: "Error",
        description: "Failed to upload image. Please try again.",
        variant: "destructive"
      });
    } finally {
      setUploading(false);
    }
  };

  const removeImage = (indexToRemove) => {
    setUploadedImages(prev => prev.filter((_, index) => index !== indexToRemove));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = { ...formData };
      if (data.price) data.price = parseFloat(data.price);
      if (data.starting_bid) data.starting_bid = parseFloat(data.starting_bid);
      if (data.buyout_price) data.buyout_price = parseFloat(data.buyout_price);
      if (data.shipping_cost) data.shipping_cost = parseFloat(data.shipping_cost);
      if (data.auction_duration_hours) data.auction_duration_hours = parseInt(data.auction_duration_hours);
      
      // Add uploaded images to the listing data
      data.images = uploadedImages;

      const response = await axios.post(`${API}/listings`, data);
      toast({
        title: "Listing created!",
        description: "Your item has been listed successfully"
      });
      navigate(`/listing/${response.data.id}`);
    } catch (error) {
      console.error('Create listing error:', error.response?.data);
      
      toast({
        title: "Error",
        description: "Failed to create listing. Please check your input and try again.",
        variant: "destructive"
      });
    }
  };

  if (user?.role === 'buyer') {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-2xl mx-auto px-4 py-8 text-center">
          <h2 className="text-2xl font-bold mb-4">Seller Account Required</h2>
          <p className="text-gray-600">You need to be registered as a seller to create listings.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="max-w-2xl mx-auto px-4 py-8">
        <Card>
          <CardHeader>
            <CardTitle>Create New Listing</CardTitle>
            <CardDescription>List your item on Cataloro and reach thousands of potential buyers</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  required
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  required
                  className="mt-1"
                  rows={4}
                />
              </div>

              {/* Image Upload Section */}
              <div>
                <Label>Product Images (up to 3)</Label>
                <div className="mt-2 space-y-4">
                  {/* Upload Button */}
                  {uploadedImages.length < 3 && (
                    <div>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageUpload}
                        disabled={uploading}
                        className="hidden"
                        id="image-upload"
                      />
                      <label
                        htmlFor="image-upload"
                        className={`inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer ${
                          uploading ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                      >
                        {uploading ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600 mr-2"></div>
                            Uploading...
                          </>
                        ) : (
                          <>
                            <Plus className="h-4 w-4 mr-2" />
                            Add Image ({uploadedImages.length}/3)
                          </>
                        )}
                      </label>
                      <p className="text-xs text-gray-500 mt-1">PNG, JPG, JPEG files only, max 10MB each</p>
                    </div>
                  )}

                  {/* Image Preview Grid */}
                  {uploadedImages.length > 0 && (
                    <div className="grid grid-cols-3 gap-4">
                      {uploadedImages.map((imageUrl, index) => (
                        <div key={index} className="relative">
                          <img
                            src={imageUrl.startsWith('/uploads/') ? `${BACKEND_URL}${imageUrl}` : imageUrl}
                            alt={`Upload ${index + 1}`}
                            className="w-full h-24 object-cover rounded-lg border"
                          />
                          <button
                            type="button"
                            onClick={() => removeImage(index)}
                            className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="category">Category</Label>
                  <Select value={formData.category} onValueChange={(value) => setFormData({...formData, category: value})}>
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category} value={category}>
                          {category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="condition">Condition</Label>
                  <Select value={formData.condition} onValueChange={(value) => setFormData({...formData, condition: value})}>
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="New">New</SelectItem>
                      <SelectItem value="Like New">Like New</SelectItem>
                      <SelectItem value="Good">Good</SelectItem>
                      <SelectItem value="Fair">Fair</SelectItem>
                      <SelectItem value="Poor">Poor</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label>Listing Type</Label>
                <Tabs value={formData.listing_type} onValueChange={(value) => setFormData({...formData, listing_type: value})}>
                  <TabsList className="grid w-full grid-cols-2 mt-1">
                    <TabsTrigger value="fixed_price">Fixed Price</TabsTrigger>
                    <TabsTrigger value="auction">Auction</TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>

              {formData.listing_type === 'fixed_price' ? (
                <div>
                  <Label htmlFor="price">Price (€)</Label>
                  <Input
                    id="price"
                    type="number"
                    step="0.01"
                    value={formData.price}
                    onChange={(e) => setFormData({...formData, price: e.target.value})}
                    required
                    className="mt-1"
                  />
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="starting_bid">Starting Bid ($)</Label>
                    <Input
                      id="starting_bid"
                      type="number"
                      step="0.01"
                      value={formData.starting_bid}
                      onChange={(e) => setFormData({...formData, starting_bid: e.target.value})}
                      required
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="buyout_price">Buy Now Price (€ - Optional)</Label>
                    <Input
                      id="buyout_price"
                      type="number"
                      step="0.01"
                      value={formData.buyout_price}
                      onChange={(e) => setFormData({...formData, buyout_price: e.target.value})}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="auction_duration">Auction Duration (Hours)</Label>
                    <Select value={formData.auction_duration_hours.toString()} onValueChange={(value) => setFormData({...formData, auction_duration_hours: parseInt(value)})}>
                      <SelectTrigger className="mt-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">1 Hour</SelectItem>
                        <SelectItem value="6">6 Hours</SelectItem>
                        <SelectItem value="12">12 Hours</SelectItem>
                        <SelectItem value="24">1 Day</SelectItem>
                        <SelectItem value="72">3 Days</SelectItem>
                        <SelectItem value="168">7 Days</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="quantity">Quantity</Label>
                  <Input
                    id="quantity"
                    type="number"
                    min="1"
                    value={formData.quantity}
                    onChange={(e) => setFormData({...formData, quantity: parseInt(e.target.value)})}
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="shipping_cost">Shipping Cost ($)</Label>
                  <Input
                    id="shipping_cost"
                    type="number"
                    step="0.01"
                    value={formData.shipping_cost}
                    onChange={(e) => setFormData({...formData, shipping_cost: e.target.value})}
                    placeholder="0.00 for free shipping"
                    className="mt-1"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="location">Location</Label>
                <Input
                  id="location"
                  value={formData.location}
                  onChange={(e) => setFormData({...formData, location: e.target.value})}
                  required
                  className="mt-1"
                />
              </div>

              <Button type="submit" className="w-full bg-gradient-to-r from-indigo-600 to-purple-600">
                Create Listing
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Cart Component
const Cart = () => {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const response = await axios.get(`${API}/cart`);
      setCartItems(response.data);
    } catch (error) {
      console.error('Error fetching cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeFromCart = async (itemId) => {
    try {
      await axios.delete(`${API}/cart/${itemId}`);
      fetchCart();
      toast({
        title: "Item removed",
        description: "Item has been removed from your cart"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to remove item from cart",
        variant: "destructive"
      });
    }
  };

  const calculateTotal = () => {
    return cartItems.reduce((total, item) => {
      return total + (item.listing.price * item.cart_item.quantity);
    }, 0);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex justify-center items-center h-96">
          Loading cart...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Shopping Cart</h1>
        
        {cartItems.length === 0 ? (
          <div className="text-center py-12">
            <ShoppingCart className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Your cart is empty</h3>
            <p className="text-gray-500 mb-4">Start shopping to add items to your cart</p>
            <Button onClick={() => navigate('/')} className="bg-gradient-to-r from-indigo-600 to-purple-600">
              Continue Shopping
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <div className="space-y-4">
                {cartItems.map((item) => (
                  <Card key={item.cart_item.id}>
                    <CardContent className="p-4">
                      <div className="flex items-center space-x-4">
                        <img
                          src={
                            item.listing.images?.[0] 
                              ? (item.listing.images[0].startsWith('/uploads/') 
                                  ? `${API}${item.listing.images[0]}` 
                                  : item.listing.images[0])
                              : 'https://images.unsplash.com/photo-1534452203293-494d7ddbf7e0?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwzfHxzaG9wcGluZ3xlbnwwfHx8fDE3NTU4Njk0MzR8MA&ixlib=rb-4.1.0&q=85'
                          }
                          alt={item.listing.title}
                          className="w-20 h-20 object-cover rounded"
                        />
                        <div className="flex-1">
                          <h3 className="font-semibold">{item.listing.title}</h3>
                          <p className="text-gray-600 text-sm">{item.listing.condition}</p>
                          <div className="flex items-center justify-between mt-2">
                            <span className="font-bold text-lg">€{item.listing.price.toFixed(2)}</span>
                            <div className="flex items-center space-x-2">
                              <span>Qty: {item.cart_item.quantity}</span>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removeFromCart(item.cart_item.id)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
            
            <div>
              <Card>
                <CardHeader>
                  <CardTitle>Order Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Subtotal:</span>
                      <span>${calculateTotal().toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between font-bold text-lg border-t pt-2">
                      <span>Total:</span>
                      <span>${calculateTotal().toFixed(2)}</span>
                    </div>
                  </div>
                  <Button className="w-full mt-4 bg-green-600 hover:bg-green-700">
                    Proceed to Checkout
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Admin Panel Component
const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [appearanceTab, setAppearanceTab] = useState('typography');
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [listings, setListings] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [siteSettings, setSiteSettings] = useState(null);
  const [pages, setPages] = useState([]);
  const [navigation, setNavigation] = useState([]);
  const [selectedPage, setSelectedPage] = useState(null);
  const [editingContent, setEditingContent] = useState('');
  const { user } = useAuth();
  const { toast } = useToast();

  // Check if user is admin
  if (user?.role !== 'admin') {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-2xl mx-auto px-4 py-8 text-center">
          <h2 className="text-2xl font-bold mb-4">Access Denied</h2>
          <p className="text-gray-600">You need admin privileges to access this page.</p>
        </div>
      </div>
    );
  }

  useEffect(() => {
    if (activeTab === 'dashboard') {
      fetchStats();
    } else if (activeTab === 'users') {
      fetchUsers();
    } else if (activeTab === 'listings') {
      fetchListings();
    } else if (activeTab === 'orders') {
      fetchOrders();
    } else if (activeTab === 'cms') {
      fetchPages();
    } else if (activeTab === 'settings') {
      fetchSiteSettings();
    } else if (activeTab === 'appearance') {
      fetchSiteSettings();
    }
  }, [activeTab]);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/stats`);
      setStats(response.data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch statistics",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/users`);
      setUsers(response.data);
      setSelectedUsers([]);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch users",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchListings = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/listings`);
      setListings(response.data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch listings",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/orders`);
      setOrders(response.data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch orders",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const blockUser = async (userId) => {
    try {
      await axios.put(`${API}/admin/users/${userId}/block`);
      toast({
        title: "Success",
        description: "User blocked successfully"
      });
      fetchUsers();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to block user",
        variant: "destructive"
      });
    }
  };

  const unblockUser = async (userId) => {
    try {
      await axios.put(`${API}/admin/users/${userId}/unblock`);
      toast({
        title: "Success",
        description: "User unblocked successfully"
      });
      fetchUsers();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to unblock user",
        variant: "destructive"
      });
    }
  };

  const deleteUser = async (userId) => {
    if (!confirm('Are you sure you want to permanently delete this user? This action cannot be undone.')) return;
    
    try {
      await axios.delete(`${API}/admin/users/${userId}`);
      toast({
        title: "Success",
        description: "User deleted successfully"
      });
      fetchUsers();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete user",
        variant: "destructive"
      });
    }
  };

  const resetUserPassword = async (userId) => {
    if (!confirm('Are you sure you want to reset this user\'s password? They will receive a temporary password.')) return;
    
    try {
      const response = await axios.put(`${API}/admin/users/${userId}/reset-password`);
      toast({
        title: "Password Reset",
        description: `New temporary password: ${response.data.temporary_password}`,
        duration: 10000
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to reset password",
        variant: "destructive"
      });
    }
  };

  const deleteListing = async (listingId) => {
    if (!confirm('Are you sure you want to delete this listing?')) return;
    
    try {
      await axios.delete(`${API}/admin/listings/${listingId}`);
      toast({
        title: "Success",
        description: "Listing deleted successfully"
      });
      fetchListings();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete listing",
        variant: "destructive"
      });
    }
  };

  const handleUserSelection = (userId, isSelected) => {
    if (isSelected) {
      setSelectedUsers([...selectedUsers, userId]);
    } else {
      setSelectedUsers(selectedUsers.filter(id => id !== userId));
    }
  };

  const selectAllUsers = () => {
    if (selectedUsers.length === users.length) {
      setSelectedUsers([]);
    } else {
      setSelectedUsers(users.map(user => user.id));
    }
  };

  const bulkBlockUsers = async () => {
    if (selectedUsers.length === 0) return;
    if (!confirm(`Block ${selectedUsers.length} selected users?`)) return;
    
    try {
      await axios.put(`${API}/admin/users/bulk-block`, selectedUsers);
      toast({
        title: "Success",
        description: `Blocked ${selectedUsers.length} users`
      });
      fetchUsers();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to block users",
        variant: "destructive"
      });
    }
  };

  const bulkUnblockUsers = async () => {
    if (selectedUsers.length === 0) return;
    if (!confirm(`Unblock ${selectedUsers.length} selected users?`)) return;
    
    try {
      await axios.put(`${API}/admin/users/bulk-unblock`, selectedUsers);
      toast({
        title: "Success",
        description: `Unblocked ${selectedUsers.length} users`
      });
      fetchUsers();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to unblock users",
        variant: "destructive"
      });
    }
  };

  const bulkDeleteUsers = async () => {
    if (selectedUsers.length === 0) return;
    if (!confirm(`⚠️ PERMANENTLY DELETE ${selectedUsers.length} users and ALL their data? This cannot be undone!`)) return;
    
    try {
      await axios.delete(`${API}/admin/users/bulk-delete`, { data: selectedUsers });
      toast({
        title: "Success",
        description: `Deleted ${selectedUsers.length} users and their data`
      });
      fetchUsers();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete users",
        variant: "destructive"
      });
    }
  };

  const bulkDeactivateAll = async () => {
    if (!confirm('⚠️ DEACTIVATE ALL USERS (except admins)? This will block all regular users from accessing the platform.')) return;
    
    try {
      const response = await axios.put(`${API}/admin/users/bulk-deactivate-all`);
      toast({
        title: "Bulk Deactivation Complete",
        description: response.data.message
      });
      fetchUsers();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to deactivate users",
        variant: "destructive"
      });
    }
  };

  const bulkActivateAll = async () => {
    if (!confirm('Activate ALL users on the platform?')) return;
    
    try {
      const response = await axios.put(`${API}/admin/users/bulk-activate-all`);
      toast({
        title: "Bulk Activation Complete",
        description: response.data.message
      });
      fetchUsers();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to activate users",
        variant: "destructive"
      });
    }
  };

  const deleteAllNonAdminUsers = async () => {
    const confirmText = "DELETE ALL NON-ADMIN USERS";
    const userConfirm = prompt(`⚠️ DANGER: This will PERMANENTLY DELETE ALL non-admin users and their data!\n\nType "${confirmText}" to confirm:`);
    
    if (userConfirm !== confirmText) {
      toast({
        title: "Operation Cancelled",
        description: "Confirmation text did not match"
      });
      return;
    }
    
    try {
      const response = await axios.delete(`${API}/admin/users/delete-all-non-admin`);
      toast({
        title: "⚠️ BULK DELETE COMPLETED",
        description: `${response.data.users_deleted} users and all their data deleted`,
        variant: "destructive",
        duration: 8000
      });
      fetchUsers();
      fetchStats();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete all users",
        variant: "destructive"
      });
    }
  };

  const generateMissingUserIds = async () => {
    try {
      const response = await axios.post(`${API}/admin/generate-user-ids`);
      toast({
        title: "User IDs Generated",
        description: response.data.message,
        duration: 5000
      });
      fetchUsers();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate user IDs",
        variant: "destructive"
      });
    }
  };

  // CMS Functions
  const fetchSiteSettings = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/cms/settings`);
      setSiteSettings(response.data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch site settings",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLogoUpload = async (event, logoType) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (file.type !== 'image/png') {
      toast({
        title: "Error",
        description: "Please select a PNG file",
        variant: "destructive"
      });
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast({
        title: "Error",
        description: "File size too large. Maximum 5MB allowed",
        variant: "destructive"
      });
      return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);
      formData.append('logo_type', logoType);

      const response = await axios.post(`${API}/admin/cms/upload-logo?logo_type=${logoType}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Update site settings with new logo URL
      setSiteSettings(prev => ({
        ...prev,
        [`${logoType}_logo_url`]: response.data.logo_url
      }));

      // Also update global window settings so the main app can see changes
      if (window.cataloroSettings) {
        window.cataloroSettings[`${logoType}_logo_url`] = response.data.logo_url;
      }

      // Trigger a window event to notify components of settings change
      window.dispatchEvent(new CustomEvent('cataloroSettingsUpdated', { 
        detail: { logoType, logoUrl: response.data.logo_url }
      }));

      toast({
        title: "Success",
        description: `${logoType.charAt(0).toUpperCase() + logoType.slice(1)} logo uploaded successfully`,
      });

    } catch (error) {
      toast({
        title: "Error",
        description: formatErrorMessage(error, "Failed to upload logo"),
        variant: "destructive"
      });
    } finally {
      setUploading(false);
      // Clear the file input
      event.target.value = '';
    }
  };

  const fetchPages = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/cms/pages`);
      setPages(response.data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch pages",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchNavigation = async () => {
    try {
      const response = await axios.get(`${API}/admin/cms/navigation`);
      setNavigation(response.data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch navigation",
        variant: "destructive"
      });
    }
  };

  const updateSiteSettings = async (settingsData) => {
    try {
      await axios.put(`${API}/admin/cms/settings`, settingsData);
      toast({
        title: "Success",
        description: "Site settings updated successfully"
      });
      await fetchSiteSettings();
      
      // Refresh the main website settings as well
      const settingsResponse = await axios.get(`${API}/cms/settings`);
      const settings = settingsResponse.data;
      window.cataloroSettings = settings;
      
      // Apply updated settings to the main website immediately
      if (settings.site_name) {
        document.title = `${settings.site_name} - ${settings.site_tagline}`;
      }
      
      if (settings.global_font_family) {
        document.body.style.fontFamily = settings.global_font_family;
        
        // Apply CSS custom properties for immediate visual update
        const root = document.documentElement;
        root.style.setProperty('--global-font-family', `${settings.global_font_family}, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif`);
      }
      
      // Apply CSS custom properties for immediate visual update
      const root = document.documentElement;
      root.style.setProperty('--primary-color', settings.primary_color || '#6366f1');
      root.style.setProperty('--secondary-color', settings.secondary_color || '#8b5cf6');
      root.style.setProperty('--accent-color', settings.accent_color || '#ef4444');
      root.style.setProperty('--background-color', settings.background_color || '#f8fafc');
      
      // Hero section colors
      root.style.setProperty('--hero-bg-start', settings.hero_background_gradient_start || '#667eea');
      root.style.setProperty('--hero-bg-end', settings.hero_background_gradient_end || '#764ba2');
      root.style.setProperty('--hero-text-color', settings.hero_text_color || '#ffffff');
      root.style.setProperty('--hero-subtitle-color', settings.hero_subtitle_color || '#f1f5f9');
      root.style.setProperty('--hero-height', settings.hero_height || '600px');
      
      // Typography
      root.style.setProperty('--h1-size', settings.h1_size || '3rem');
      root.style.setProperty('--h2-size', settings.h2_size || '2.25rem');
      root.style.setProperty('--h3-size', settings.h3_size || '1.875rem');
      root.style.setProperty('--h4-size', settings.h4_size || '1.5rem');
      root.style.setProperty('--h5-size', settings.h5_size || '1.25rem');
      root.style.setProperty('--h1-color', settings.h1_color || '#1f2937');
      root.style.setProperty('--h2-color', settings.h2_color || '#374151');
      root.style.setProperty('--h3-color', settings.h3_color || '#4b5563');
      root.style.setProperty('--h4-color', settings.h4_color || '#6b7280');
      root.style.setProperty('--h5-color', settings.h5_color || '#9ca3af');
      
      // Trigger a page refresh to apply all changes
      setTimeout(() => {
        window.location.reload();
      }, 1000);
      
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update site settings",
        variant: "destructive"
      });
    }
  };

  // Add missing saveAppearanceSettings function
  const saveAppearanceSettings = async () => {
    try {
      await updateSiteSettings(siteSettings);
      toast({
        title: "Success",
        description: "Appearance settings saved successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save appearance settings",
        variant: "destructive"
      });
    }
  };

  const createPage = async (pageData) => {
    try {
      await axios.post(`${API}/admin/cms/pages`, pageData);
      toast({
        title: "Success",
        description: "Page created successfully"
      });
      fetchPages();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create page",
        variant: "destructive"
      });
    }
  };

  const updatePage = async (pageSlug, pageData) => {
    try {
      await axios.put(`${API}/admin/cms/pages/${pageSlug}`, pageData);
      toast({
        title: "Success",
        description: "Page updated successfully"
      });
      fetchPages();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update page",
        variant: "destructive"
      });
    }
  };

  const deletePage = async (pageSlug) => {
    if (!confirm('Are you sure you want to delete this page?')) return;
    
    try {
      await axios.delete(`${API}/admin/cms/pages/${pageSlug}`);
      toast({
        title: "Success",
        description: "Page deleted successfully"
      });
      fetchPages();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete page",
        variant: "destructive"
      });
    }
  };

  const syncNavigationWithPages = async () => {
    try {
      const response = await axios.post(`${API}/admin/cms/sync-navigation`);
      toast({
        title: "Navigation Synced",
        description: response.data.message
      });
      await fetchNavigation();
      
      // Refresh the main website navigation as well
      const navResponse = await axios.get(`${API}/cms/navigation`);
      window.cataloroNavigation = navResponse.data;
      window.dispatchEvent(new CustomEvent('cataloroNavigationLoaded', { detail: navResponse.data }));
    } catch (error) {
      toast({
        title: "Error", 
        description: "Failed to sync navigation",
        variant: "destructive"
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Cataloro Admin</h1>
          <p className="text-gray-600">Manage users, listings, and monitor platform activity</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-8">
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
            <TabsTrigger value="listings">Listings</TabsTrigger>
            <TabsTrigger value="orders">Orders</TabsTrigger>
            <TabsTrigger value="appearance">Appearance</TabsTrigger>
            <TabsTrigger value="pages">Page Management</TabsTrigger>
            <TabsTrigger value="settings">General Settings</TabsTrigger>
            <TabsTrigger value="database">Database</TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard">
            {loading ? (
              <div className="flex justify-center py-8">Loading...</div>
            ) : stats ? (
              <div className="space-y-6">
                {/* Key Metrics Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600">Total Users</p>
                          <p className="text-2xl font-bold">{stats.total_users}</p>
                        </div>
                        <User className="h-8 w-8 text-blue-600" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600">Active Listings</p>
                          <p className="text-2xl font-bold">{stats.total_listings}</p>
                        </div>
                        <Package className="h-8 w-8 text-green-600" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600">Completed Orders</p>
                          <p className="text-2xl font-bold">{stats.total_orders}</p>
                        </div>
                        <Gavel className="h-8 w-8 text-purple-600" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600">Total Revenue</p>
                          <p className="text-2xl font-bold">€{stats.total_revenue.toFixed(2)}</p>
                        </div>
                        <Euro className="h-8 w-8 text-yellow-600" />
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Analytics Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Visitor Analytics */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Daily Visitors (Last 7 Days)</CardTitle>
                      <CardDescription>Website traffic overview</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                        <div className="text-center">
                          <Eye className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                          <p className="text-gray-500">Visitor analytics coming soon</p>
                          <p className="text-sm text-gray-400">Integration with analytics service required</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Visitor Countries */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Visitor Countries</CardTitle>
                      <CardDescription>Geographic distribution of visitors</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm">🇩🇪 Germany</span>
                          <span className="text-sm font-medium">45%</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">🇺🇸 United States</span>
                          <span className="text-sm font-medium">23%</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">🇬🇧 United Kingdom</span>
                          <span className="text-sm font-medium">12%</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">🇫🇷 France</span>
                          <span className="text-sm font-medium">8%</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm">🌍 Others</span>
                          <span className="text-sm font-medium">12%</span>
                        </div>
                        <p className="text-xs text-gray-400 mt-4">Sample data - integrate with analytics service for real data</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Listing Performance */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Listing Performance</CardTitle>
                      <CardDescription>Overview of marketplace activity</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                            <span className="text-sm font-medium">Completed Listings</span>
                          </div>
                          <span className="text-lg font-bold text-green-600">{Math.max(0, stats.total_orders || 0)}</span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                            <span className="text-sm font-medium">Active Listings</span>
                          </div>
                          <span className="text-lg font-bold text-blue-600">{Math.max(0, stats.total_listings || 0)}</span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                            <span className="text-sm font-medium">Pending Orders</span>
                          </div>
                          <span className="text-lg font-bold text-yellow-600">0</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Quick Actions */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Quick Actions</CardTitle>
                      <CardDescription>Common administrative tasks</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 gap-3">
                        <Button 
                          variant="outline" 
                          className="h-20 flex flex-col items-center justify-center"
                          onClick={() => setActiveTab('users')}
                        >
                          <User className="h-6 w-6 mb-2" />
                          <span className="text-xs">Manage Users</span>
                        </Button>
                        <Button 
                          variant="outline" 
                          className="h-20 flex flex-col items-center justify-center"
                          onClick={() => setActiveTab('listings')}
                        >
                          <Package className="h-6 w-6 mb-2" />
                          <span className="text-xs">View Listings</span>
                        </Button>
                        <Button 
                          variant="outline" 
                          className="h-20 flex flex-col items-center justify-center"
                          onClick={() => setActiveTab('appearance')}
                        >
                          <Edit className="h-6 w-6 mb-2" />
                          <span className="text-xs">Customize</span>
                        </Button>
                        <Button 
                          variant="outline" 
                          className="h-20 flex flex-col items-center justify-center"
                          onClick={() => setActiveTab('settings')}
                        >
                          <MapPin className="h-6 w-6 mb-2" />
                          <span className="text-xs">Settings</span>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <p>Failed to load dashboard data</p>
              </div>
            )}
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users">
            {loading ? (
              <div className="flex justify-center py-8">Loading...</div>
            ) : (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>User Management</CardTitle>
                    <CardDescription>View and manage all platform users with detailed information</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {/* Bulk Actions */}
                    <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                      <h4 className="font-medium mb-3">Bulk Actions & System Tools</h4>
                      <div className="flex flex-wrap gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={generateMissingUserIds}
                        >
                          Generate User IDs
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={selectAllUsers}
                        >
                          Select All
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={bulkDeactivateAll}
                        >
                          Deactivate All
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={deleteAllNonAdminUsers}
                        >
                          Delete All Non-Admin
                        </Button>
                      </div>
                    </div>

                    {/* Users List with Enhanced Information */}
                    <div className="space-y-4">
                      {users.map((user) => (
                        <Card key={user.id} className="border-l-4 border-l-blue-500">
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-4 flex-1">
                                <div className="flex items-center space-x-2">
                                  <input
                                    type="checkbox"
                                    checked={selectedUsers.includes(user.id)}
                                    onChange={(e) => {
                                      if (e.target.checked) {
                                        setSelectedUsers([...selectedUsers, user.id]);
                                      } else {
                                        setSelectedUsers(selectedUsers.filter(id => id !== user.id));
                                      }
                                    }}
                                    className="rounded"
                                  />
                                </div>
                                
                                <div className="flex-1">
                                  <div className="flex items-center space-x-3 mb-2">
                                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                                      {(user?.name || 'U').charAt(0).toUpperCase()}
                                    </div>
                                    <div>
                                      <div className="flex items-center space-x-2">
                                        <h3 className="font-semibold text-lg">{user?.name || 'Unknown User'}</h3>
                                        <Badge variant={user.role === 'admin' ? 'default' : user.role === 'seller' ? 'secondary' : 'outline'}>
                                          {user.role}
                                        </Badge>
                                        {user.is_active === false && (
                                          <Badge variant="destructive">Blocked</Badge>
                                        )}
                                      </div>
                                      <p className="text-gray-600">{user?.email || 'No email'}</p>
                                      <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                                        <span>ID: {user.user_id || 'Not assigned'}</span>
                                        <span>•</span>
                                        <span>Joined: {new Date(user.created_at).toLocaleDateString()}</span>
                                      </div>
                                    </div>
                                  </div>
                                  
                                  {/* Quick User Stats */}
                                  <div className="grid grid-cols-3 gap-4 mt-3 p-3 bg-gray-50 rounded-lg">
                                    <div className="text-center">
                                      <p className="text-lg font-semibold text-blue-600">0</p>
                                      <p className="text-xs text-gray-500">Orders</p>
                                    </div>
                                    <div className="text-center">
                                      <p className="text-lg font-semibold text-green-600">0</p>
                                      <p className="text-xs text-gray-500">Listings</p>
                                    </div>
                                    <div className="text-center">
                                      <p className="text-lg font-semibold text-yellow-600">€0.00</p>
                                      <p className="text-xs text-gray-500">Spent</p>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Action Buttons */}
                              <div className="flex items-center space-x-2">
                                <Dialog>
                                  <DialogTrigger asChild>
                                    <Button variant="outline" size="sm">
                                      <Eye className="h-4 w-4 mr-1" />
                                      Details
                                    </Button>
                                  </DialogTrigger>
                                  <DialogContent className="max-w-2xl">
                                    <DialogHeader>
                                      <DialogTitle>User Details - {user?.name || 'Unknown User'}</DialogTitle>
                                      <DialogDescription>
                                        Complete user information and activity history
                                      </DialogDescription>
                                    </DialogHeader>
                                    <div className="space-y-6">
                                      {/* User Profile Section */}
                                      <div className="grid grid-cols-2 gap-4">
                                        <div>
                                          <h4 className="font-medium mb-3">Profile Information</h4>
                                          <div className="space-y-2 text-sm">
                                            <div><strong>Name:</strong> {user?.name || 'Unknown'}</div>
                                            <div><strong>Email:</strong> {user?.email || 'No email'}</div>
                                            <div><strong>User ID:</strong> {user?.user_id || 'Not assigned'}</div>
                                            <div><strong>Role:</strong> <Badge variant="outline">{user?.role || 'Unknown'}</Badge></div>
                                            <div><strong>Status:</strong> 
                                              <Badge variant={user?.is_active ? "default" : "destructive"}>
                                                {user?.is_active ? "Active" : "Blocked"}
                                              </Badge>
                                            </div>
                                            <div><strong>Joined:</strong> {user?.created_at ? new Date(user.created_at).toLocaleString() : 'Unknown'}</div>
                                          </div>
                                        </div>
                                        <div>
                                          <h4 className="font-medium mb-3">Account Statistics</h4>
                                          <div className="space-y-3">
                                            <div className="p-3 bg-blue-50 rounded-lg">
                                              <div className="flex justify-between items-center">
                                                <span className="text-sm">Total Orders</span>
                                                <span className="font-semibold">0</span>
                                              </div>
                                            </div>
                                            <div className="p-3 bg-green-50 rounded-lg">
                                              <div className="flex justify-between items-center">
                                                <span className="text-sm">Active Listings</span>
                                                <span className="font-semibold">0</span>
                                              </div>
                                            </div>
                                            <div className="p-3 bg-yellow-50 rounded-lg">
                                              <div className="flex justify-between items-center">
                                                <span className="text-sm">Total Spent</span>
                                                <span className="font-semibold">€0.00</span>
                                              </div>
                                            </div>
                                          </div>
                                        </div>
                                      </div>
                                      
                                      {/* Activity Timeline */}
                                      <div>
                                        <h4 className="font-medium mb-3">Recent Activity</h4>
                                        <div className="space-y-2 text-sm">
                                          <div className="p-2 border-l-4 border-blue-200 bg-blue-50 rounded-r">
                                            <div className="font-medium">Account Created</div>
                                            <div className="text-gray-600">{user?.created_at ? new Date(user.created_at).toLocaleString() : 'Unknown date'}</div>
                                          </div>
                                          <div className="p-2 border-l-4 border-gray-200 bg-gray-50 rounded-r">
                                            <div className="font-medium">No recent activity</div>
                                            <div className="text-gray-600">User activity will appear here</div>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </DialogContent>
                                </Dialog>

                                {user.is_active ? (
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => blockUser(user.id)}
                                  >
                                    Block
                                  </Button>
                                ) : (
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => unblockUser(user.id)}
                                  >
                                    Unblock
                                  </Button>
                                )}
                                
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => resetUserPassword(user.id)}
                                >
                                  Reset Password
                                </Button>
                                
                                <Button
                                  variant="destructive"
                                  size="sm"
                                  onClick={() => deleteUser(user.id)}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>

                    {users.length === 0 && (
                      <div className="text-center py-12">
                        <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No users found</h3>
                        <p className="text-gray-500">Users will appear here once they register</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          {/* Listings Tab */}
          <TabsContent value="listings">
            {loading ? (
              <div className="flex justify-center py-8">Loading...</div>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>Listing Management</CardTitle>
                  <CardDescription>View and manage all platform listings</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {listings.map((listing) => (
                      <div key={listing.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex-1">
                          <h3 className="font-semibold">{listing.title}</h3>
                          <p className="text-sm text-gray-600">by {listing.seller_name}</p>
                          <div className="flex items-center space-x-2 mt-1">
                            <Badge variant="outline">{listing.category}</Badge>
                            <Badge variant={listing.status === 'active' ? 'default' : 'secondary'}>
                              {listing.status}
                            </Badge>
                            <span className="text-sm text-gray-500">Views: {listing.views}</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <div className="text-right">
                            <p className="font-semibold">€{listing.price?.toFixed(2)}</p>
                            <p className="text-sm text-gray-500">
                              {new Date(listing.created_at).toLocaleDateString()}
                            </p>
                          </div>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => deleteListing(listing.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Orders Tab */}
          <TabsContent value="orders">
            {loading ? (
              <div className="flex justify-center py-8">Loading...</div>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>Order Management</CardTitle>
                  <CardDescription>View all platform orders</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {orders.map((orderData) => (
                      <div key={orderData.order.id} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-semibold">Order #{orderData.order.id}</h3>
                          <Badge variant={orderData.order.status === 'completed' ? 'default' : 'secondary'}>
                            {orderData.order.status}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                          <div>
                            <p className="text-gray-600">Buyer</p>
                            <p>{orderData.buyer?.full_name}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Seller</p>
                            <p>{orderData.seller?.full_name}</p>
                          </div>
                          <div>
                            <p className="text-gray-600">Amount</p>
                            <p className="font-semibold">${orderData.order.total_amount.toFixed(2)}</p>
                          </div>
                        </div>
                        {orderData.listing && (
                          <p className="text-sm text-gray-600 mt-2">
                            Item: {orderData.listing.title}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Content Management Tab */}
          <TabsContent value="cms">
            {loading ? (
              <div className="flex justify-center py-8">Loading...</div>
            ) : (
              <div className="space-y-6">
                {/* Hero Section Customization */}
                {siteSettings && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Hero Section Customization</CardTitle>
                      <CardDescription>Customize the main hero/search section appearance and content</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-6">
                        {/* Hero Text Content */}
                        <div className="grid grid-cols-1 gap-4">
                          <div>
                            <label className="block text-sm font-medium mb-2">Hero Title</label>
                            <input
                              type="text"
                              className="w-full p-3 border rounded-md"
                              value={siteSettings.hero_title}
                              onChange={(e) => setSiteSettings({...siteSettings, hero_title: e.target.value})}
                              placeholder="e.g., Discover Amazing Deals"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium mb-2">Hero Subtitle</label>
                            <textarea
                              className="w-full p-3 border rounded-md"
                              rows="3"
                              value={siteSettings.hero_subtitle}
                              onChange={(e) => setSiteSettings({...siteSettings, hero_subtitle: e.target.value})}
                              placeholder="e.g., Buy and sell with confidence on Cataloro"
                            />
                          </div>
                        </div>

                        {/* Background Settings */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div>
                            <label className="block text-sm font-medium mb-2">Background Type</label>
                            <select
                              className="w-full p-2 border rounded-md"
                              value={siteSettings.hero_background_type}
                              onChange={(e) => setSiteSettings({...siteSettings, hero_background_type: e.target.value})}
                            >
                              <option value="solid">Solid Color</option>
                              <option value="gradient">Gradient</option>
                            </select>
                          </div>
                          
                          {siteSettings.hero_background_type === 'solid' ? (
                            <div>
                              <label className="block text-sm font-medium mb-2">Background Color</label>
                              <div className="flex items-center space-x-2">
                                <input
                                  type="color"
                                  value={siteSettings.hero_background_color}
                                  onChange={(e) => setSiteSettings({...siteSettings, hero_background_color: e.target.value})}
                                  className="w-12 h-10 border rounded"
                                />
                                <input
                                  type="text"
                                  value={siteSettings.hero_background_color}
                                  onChange={(e) => setSiteSettings({...siteSettings, hero_background_color: e.target.value})}
                                  className="flex-1 p-2 border rounded-md font-mono"
                                />
                              </div>
                            </div>
                          ) : (
                            <>
                              <div>
                                <label className="block text-sm font-medium mb-2">Gradient Start Color</label>
                                <div className="flex items-center space-x-2">
                                  <input
                                    type="color"
                                    value={siteSettings.hero_background_gradient_start}
                                    onChange={(e) => setSiteSettings({...siteSettings, hero_background_gradient_start: e.target.value})}
                                    className="w-12 h-10 border rounded"
                                  />
                                  <input
                                    type="text"
                                    value={siteSettings.hero_background_gradient_start}
                                    onChange={(e) => setSiteSettings({...siteSettings, hero_background_gradient_start: e.target.value})}
                                    className="flex-1 p-2 border rounded-md font-mono"
                                  />
                                </div>
                              </div>
                              <div>
                                <label className="block text-sm font-medium mb-2">Gradient End Color</label>
                                <div className="flex items-center space-x-2">
                                  <input
                                    type="color"
                                    value={siteSettings.hero_background_gradient_end}
                                    onChange={(e) => setSiteSettings({...siteSettings, hero_background_gradient_end: e.target.value})}
                                    className="w-12 h-10 border rounded"
                                  />
                                  <input
                                    type="text"
                                    value={siteSettings.hero_background_gradient_end}
                                    onChange={(e) => setSiteSettings({...siteSettings, hero_background_gradient_end: e.target.value})}
                                    className="flex-1 p-2 border rounded-md font-mono"
                                  />
                                </div>
                              </div>
                            </>
                          )}
                        </div>

                        {/* Text Colors */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium mb-2">Hero Title Color</label>
                            <div className="flex items-center space-x-2">
                              <input
                                type="color"
                                value={siteSettings.hero_text_color}
                                onChange={(e) => setSiteSettings({...siteSettings, hero_text_color: e.target.value})}
                                className="w-12 h-10 border rounded"
                              />
                              <input
                                type="text"
                                value={siteSettings.hero_text_color}
                                onChange={(e) => setSiteSettings({...siteSettings, hero_text_color: e.target.value})}
                                className="flex-1 p-2 border rounded-md font-mono"
                              />
                            </div>
                          </div>
                          <div>
                            <label className="block text-sm font-medium mb-2">Hero Subtitle Color</label>
                            <div className="flex items-center space-x-2">
                              <input
                                type="color"
                                value={siteSettings.hero_subtitle_color}
                                onChange={(e) => setSiteSettings({...siteSettings, hero_subtitle_color: e.target.value})}
                                className="w-12 h-10 border rounded"
                              />
                              <input
                                type="text"
                                value={siteSettings.hero_subtitle_color}
                                onChange={(e) => setSiteSettings({...siteSettings, hero_subtitle_color: e.target.value})}
                                className="flex-1 p-2 border rounded-md font-mono"
                              />
                            </div>
                          </div>
                        </div>

                        {/* Hero Preview */}
                        <div className="p-6 rounded-lg border flex items-center justify-center" style={{
                          background: siteSettings.hero_background_type === 'gradient' 
                            ? `linear-gradient(135deg, ${siteSettings.hero_background_gradient_start} 0%, ${siteSettings.hero_background_gradient_end} 100%)`
                            : siteSettings.hero_background_color,
                          color: siteSettings.hero_text_color,
                          textAlign: 'center',
                          height: siteSettings.hero_height || '600px',
                          maxHeight: '300px' // Limit preview height
                        }}>
                          <div>
                            <h1 className="text-4xl font-bold mb-4" style={{color: siteSettings.hero_text_color}}>
                              {siteSettings.hero_title}
                            </h1>
                            <p className="text-xl" style={{color: siteSettings.hero_subtitle_color}}>
                              {siteSettings.hero_subtitle}
                            </p>
                            <p className="text-sm opacity-75 mt-2">Height: {siteSettings.hero_height || '600px'}</p>
                          </div>
                        </div>

                        <Button
                          onClick={() => updateSiteSettings(siteSettings)}
                          className="w-full"
                        >
                          Save Hero Section Changes
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}

                <Card>
                  <CardHeader>
                    <CardTitle>Page Management</CardTitle>
                    <CardDescription>Manage pages and automatically add them to navigation</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-lg font-semibold">Pages</h3>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          onClick={syncNavigationWithPages}
                        >
                          Sync Navigation
                        </Button>
                        <Button 
                          onClick={() => {
                            const newPage = {
                              page_slug: prompt('Enter page slug (e.g., about, terms):'),
                              title: prompt('Enter page title:'),
                              content: '<p>New page content...</p>',
                              is_published: true,
                              meta_description: ''
                            };
                            if (newPage.page_slug && newPage.title) {
                              createPage(newPage);
                            }
                          }}
                        >
                          Create New Page
                        </Button>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      {pages.map((page) => (
                        <div key={page.id} className="flex items-center justify-between p-4 border rounded-lg">
                          <div>
                            <h4 className="font-semibold">{page.title}</h4>
                            <p className="text-sm text-gray-600">/{page.page_slug}</p>
                            <div className="flex items-center space-x-2 mt-1">
                              <Badge variant={page.is_published ? 'default' : 'secondary'}>
                                {page.is_published ? 'Published' : 'Draft'}
                              </Badge>
                              <Badge variant="outline">Auto-added to menu</Badge>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                setSelectedPage(page);
                                setEditingContent(page.content);
                              }}
                            >
                              Edit
                            </Button>
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => deletePage(page.page_slug)}
                            >
                              Delete
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    {selectedPage && (
                      <div className="mt-6 p-4 border rounded-lg bg-gray-50">
                        <h4 className="font-semibold mb-4">Editing: {selectedPage.title}</h4>
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium mb-2">Content (HTML)</label>
                            <textarea
                              className="w-full h-64 p-3 border rounded-md font-mono"
                              value={editingContent}
                              onChange={(e) => setEditingContent(e.target.value)}
                              placeholder="Enter HTML content..."
                            />
                          </div>
                          <div className="flex space-x-2">
                            <Button
                              onClick={() => {
                                updatePage(selectedPage.page_slug, {
                                  ...selectedPage,
                                  content: editingContent
                                });
                                setSelectedPage(null);
                                setEditingContent('');
                              }}
                            >
                              Save Changes
                            </Button>
                            <Button
                              variant="outline"
                              onClick={() => {
                                setSelectedPage(null);
                                setEditingContent('');
                              }}
                            >
                              Cancel
                            </Button>
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          {/* Site Settings Tab */}
          <TabsContent value="settings">
            {loading ? (
              <div className="flex justify-center py-8">Loading...</div>
            ) : siteSettings ? (
              <Card>
                <CardHeader>
                  <CardTitle>Site Settings</CardTitle>
                  <CardDescription>Configure your marketplace settings</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* Logo Upload Section */}
                    <div className="border rounded-lg p-4 bg-gray-50">
                      <h3 className="text-lg font-medium mb-4">Logo Settings</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">Header Logo</label>
                          {siteSettings.header_logo_url && (
                            <div className="mb-2">
                              <img 
                                src={siteSettings.header_logo_url ? `${BACKEND_URL}${siteSettings.header_logo_url}` : ''} 
                                alt="Current Header Logo" 
                                className="max-h-16 object-contain border rounded"
                              />
                            </div>
                          )}
                          <input
                            type="file"
                            accept=".png"
                            onChange={(e) => handleLogoUpload(e, 'header')}
                            className="w-full p-2 border rounded-md"
                          />
                          <p className="text-xs text-gray-500 mt-1">PNG files only, max 5MB</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">Logo Alt Text</label>
                          <input
                            type="text"
                            className="w-full p-2 border rounded-md"
                            value={siteSettings.header_logo_alt || ''}
                            onChange={(e) => setSiteSettings({...siteSettings, header_logo_alt: e.target.value})}
                            placeholder="Cataloro Logo"
                          />
                        </div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Site Name</label>
                        <input
                          type="text"
                          className="w-full p-2 border rounded-md"
                          value={siteSettings.site_name}
                          onChange={(e) => setSiteSettings({...siteSettings, site_name: e.target.value})}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">Site Tagline</label>
                        <input
                          type="text"
                          className="w-full p-2 border rounded-md"
                          value={siteSettings.site_tagline}
                          onChange={(e) => setSiteSettings({...siteSettings, site_tagline: e.target.value})}
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">Hero Title</label>
                      <input
                        type="text"
                        className="w-full p-2 border rounded-md"
                        value={siteSettings.hero_title}
                        onChange={(e) => setSiteSettings({...siteSettings, hero_title: e.target.value})}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">Hero Subtitle</label>
                      <textarea
                        className="w-full p-2 border rounded-md"
                        rows="3"
                        value={siteSettings.hero_subtitle}
                        onChange={(e) => setSiteSettings({...siteSettings, hero_subtitle: e.target.value})}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">Hero Section Height</label>
                      <div className="flex items-center space-x-2">
                        <input
                          type="range"
                          min="300"
                          max="1000"
                          step="50"
                          value={parseInt(siteSettings.hero_height?.replace('px', '') || '600')}
                          onChange={(e) => setSiteSettings({...siteSettings, hero_height: `${e.target.value}px`})}
                          className="flex-1"
                        />
                        <input
                          type="text"
                          value={siteSettings.hero_height || '600px'}
                          onChange={(e) => setSiteSettings({...siteSettings, hero_height: e.target.value})}
                          className="w-20 p-2 border rounded-md text-center"
                          placeholder="600px"
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1">Adjust the height of the hero section (300px - 1000px)</p>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">Features</label>
                        <div className="space-y-2">
                          <label className="flex items-center">
                            <input
                              type="checkbox"
                              checked={siteSettings.show_hero_section}
                              onChange={(e) => setSiteSettings({...siteSettings, show_hero_section: e.target.checked})}
                              className="mr-2"
                            />
                            Show Hero Section
                          </label>
                          <label className="flex items-center">
                            <input
                              type="checkbox"
                              checked={siteSettings.show_categories}
                              onChange={(e) => setSiteSettings({...siteSettings, show_categories: e.target.checked})}
                              className="mr-2"
                            />
                            Show Categories
                          </label>
                          <label className="flex items-center">
                            <input
                              type="checkbox"
                              checked={siteSettings.show_auctions}
                              onChange={(e) => setSiteSettings({...siteSettings, show_auctions: e.target.checked})}
                              className="mr-2"
                            />
                            Enable Auctions
                          </label>
                          <label className="flex items-center">
                            <input
                              type="checkbox"
                              checked={siteSettings.enable_cart}
                              onChange={(e) => setSiteSettings({...siteSettings, enable_cart: e.target.checked})}
                              className="mr-2"
                            />
                            Enable Shopping Cart
                          </label>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-2">User Permissions</label>
                        <div className="space-y-2">
                          <label className="flex items-center">
                            <input
                              type="checkbox"
                              checked={siteSettings.allow_user_registration}
                              onChange={(e) => setSiteSettings({...siteSettings, allow_user_registration: e.target.checked})}
                              className="mr-2"
                            />
                            Allow User Registration
                          </label>
                          <label className="flex items-center">
                            <input
                              type="checkbox"
                              checked={siteSettings.enable_reviews}
                              onChange={(e) => setSiteSettings({...siteSettings, enable_reviews: e.target.checked})}
                              className="mr-2"
                            />
                            Enable Reviews
                          </label>
                        </div>
                        <div className="mt-4">
                          <label className="block text-sm font-medium mb-2">Max Images per Listing</label>
                          <input
                            type="number"
                            min="1"
                            max="10"
                            className="w-full p-2 border rounded-md"
                            value={siteSettings.max_images_per_listing}
                            onChange={(e) => setSiteSettings({...siteSettings, max_images_per_listing: parseInt(e.target.value)})}
                          />
                        </div>
                      </div>
                    </div>
                    
                    <Button
                      onClick={() => updateSiteSettings(siteSettings)}
                      className="w-full"
                    >
                      Save Settings
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : null}
          </TabsContent>

          {/* Appearance Tab */}
          <TabsContent value="appearance">
            {loading ? (
              <div className="flex justify-center py-8">Loading...</div>
            ) : siteSettings ? (
              <div className="space-y-6">
                {/* Sub-navigation for Appearance sections */}
                <div className="border-b border-gray-200">
                  <nav className="-mb-px flex space-x-8">
                    <button
                      className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm ${
                        appearanceTab === 'typography' 
                          ? 'border-indigo-500 text-indigo-600' 
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                      onClick={() => setAppearanceTab('typography')}
                    >
                      Typography
                    </button>
                    <button
                      className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm ${
                        appearanceTab === 'colors' 
                          ? 'border-indigo-500 text-indigo-600' 
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                      onClick={() => setAppearanceTab('colors')}
                    >
                      Theme Colours
                    </button>
                    <button
                      className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm ${
                        appearanceTab === 'hero' 
                          ? 'border-indigo-500 text-indigo-600' 
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                      onClick={() => setAppearanceTab('hero')}
                    >
                      Hero Selection
                    </button>
                  </nav>
                </div>

                {/* Typography Section */}
                {appearanceTab === 'typography' && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Typography Settings</CardTitle>
                      <CardDescription>Customize fonts and text appearance across your site</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-6">
                        {/* Global Font Family */}
                        <div>
                          <label className="block text-sm font-medium mb-2">Global Font Family</label>
                          <select
                            className="w-full p-3 border rounded-md"
                            value={siteSettings.global_font_family || 'Inter'}
                            onChange={(e) => setSiteSettings({...siteSettings, global_font_family: e.target.value})}
                          >
                            <option value="Inter">Inter</option>
                            <option value="Roboto">Roboto</option>
                            <option value="Open Sans">Open Sans</option>
                            <option value="Lato">Lato</option>
                            <option value="Poppins">Poppins</option>
                            <option value="Source Sans Pro">Source Sans Pro</option>
                            <option value="PT Sans">PT Sans</option>
                            <option value="Arial">Arial</option>
                            <option value="Helvetica">Helvetica</option>
                            <option value="Georgia">Georgia</option>
                            <option value="Times">Times</option>
                          </select>
                        </div>

                        {/* Heading Sizes and Colors */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {/* H1 Settings */}
                          <div className="space-y-3">
                            <h4 className="font-medium">H1 Heading</h4>
                            <div className="flex items-center space-x-3">
                              <input
                                type="range"
                                min="24"
                                max="72"
                                value={parseInt(siteSettings.h1_size?.replace('px', '') || '36')}
                                onChange={(e) => setSiteSettings({...siteSettings, h1_size: e.target.value + 'px'})}
                                className="flex-1"
                              />
                              <input
                                type="text"
                                value={siteSettings.h1_size || '36px'}
                                onChange={(e) => setSiteSettings({...siteSettings, h1_size: e.target.value})}
                                className="w-16 p-1 border rounded text-center text-sm"
                              />
                              <input
                                type="color"
                                value={siteSettings.h1_color || '#1f2937'}
                                onChange={(e) => setSiteSettings({...siteSettings, h1_color: e.target.value})}
                                className="w-10 h-10 border rounded cursor-pointer"
                              />
                            </div>
                            <h1 
                              className="font-bold" 
                              style={{
                                fontSize: siteSettings.h1_size || '36px',
                                color: siteSettings.h1_color || '#1f2937',
                                fontFamily: siteSettings.global_font_family || 'Inter'
                              }}
                            >
                              Sample H1 Text
                            </h1>
                          </div>

                          {/* H2 Settings */}
                          <div className="space-y-3">
                            <h4 className="font-medium">H2 Heading</h4>
                            <div className="flex items-center space-x-3">
                              <input
                                type="range"
                                min="20"
                                max="48"
                                value={parseInt(siteSettings.h2_size?.replace('px', '') || '30')}
                                onChange={(e) => setSiteSettings({...siteSettings, h2_size: e.target.value + 'px'})}
                                className="flex-1"
                              />
                              <input
                                type="text"
                                value={siteSettings.h2_size || '30px'}
                                onChange={(e) => setSiteSettings({...siteSettings, h2_size: e.target.value})}
                                className="w-16 p-1 border rounded text-center text-sm"
                              />
                              <input
                                type="color"
                                value={siteSettings.h2_color || '#374151'}
                                onChange={(e) => setSiteSettings({...siteSettings, h2_color: e.target.value})}
                                className="w-10 h-10 border rounded cursor-pointer"
                              />
                            </div>
                            <h2 
                              className="font-semibold" 
                              style={{
                                fontSize: siteSettings.h2_size || '30px',
                                color: siteSettings.h2_color || '#374151',
                                fontFamily: siteSettings.global_font_family || 'Inter'
                              }}
                            >
                              Sample H2 Text
                            </h2>
                          </div>

                          {/* H3 Settings */}
                          <div className="space-y-3">
                            <h4 className="font-medium">H3 Heading</h4>
                            <div className="flex items-center space-x-3">
                              <input
                                type="range"
                                min="18"
                                max="36"
                                value={parseInt(siteSettings.h3_size?.replace('px', '') || '24')}
                                onChange={(e) => setSiteSettings({...siteSettings, h3_size: e.target.value + 'px'})}
                                className="flex-1"
                              />
                              <input
                                type="text"
                                value={siteSettings.h3_size || '24px'}
                                onChange={(e) => setSiteSettings({...siteSettings, h3_size: e.target.value})}
                                className="w-16 p-1 border rounded text-center text-sm"
                              />
                              <input
                                type="color"
                                value={siteSettings.h3_color || '#4b5563'}
                                onChange={(e) => setSiteSettings({...siteSettings, h3_color: e.target.value})}
                                className="w-10 h-10 border rounded cursor-pointer"
                              />
                            </div>
                            <h3 
                              className="font-medium" 
                              style={{
                                fontSize: siteSettings.h3_size || '24px',
                                color: siteSettings.h3_color || '#4b5563',
                                fontFamily: siteSettings.global_font_family || 'Inter'
                              }}
                            >
                              Sample H3 Text
                            </h3>
                          </div>

                          {/* H4 & H5 Settings */}
                          <div className="space-y-3">
                            <h4 className="font-medium">H4 & H5 Headings</h4>
                            <div className="space-y-2">
                              <div className="flex items-center space-x-3">
                                <span className="text-sm w-8">H4:</span>
                                <input
                                  type="range"
                                  min="16"
                                  max="28"
                                  value={parseInt(siteSettings.h4_size?.replace('px', '') || '20')}
                                  onChange={(e) => setSiteSettings({...siteSettings, h4_size: e.target.value + 'px'})}
                                  className="flex-1"
                                />
                                <input
                                  type="color"
                                  value={siteSettings.h4_color || '#6b7280'}
                                  onChange={(e) => setSiteSettings({...siteSettings, h4_color: e.target.value})}
                                  className="w-8 h-8 border rounded cursor-pointer"
                                />
                              </div>
                              <div className="flex items-center space-x-3">
                                <span className="text-sm w-8">H5:</span>
                                <input
                                  type="range"
                                  min="14"
                                  max="24"
                                  value={parseInt(siteSettings.h5_size?.replace('px', '') || '18')}
                                  onChange={(e) => setSiteSettings({...siteSettings, h5_size: e.target.value + 'px'})}
                                  className="flex-1"
                                />
                                <input
                                  type="color"
                                  value={siteSettings.h5_color || '#9ca3af'}
                                  onChange={(e) => setSiteSettings({...siteSettings, h5_color: e.target.value})}
                                  className="w-8 h-8 border rounded cursor-pointer"
                                />
                              </div>
                            </div>
                          </div>
                        </div>

                        <Button 
                          onClick={() => updateSiteSettings(siteSettings)}
                          className="w-full"
                        >
                          Save Typography Settings
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Theme Colors Section */}
                {appearanceTab === 'colors' && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Theme Colors</CardTitle>
                      <CardDescription>Customize the color scheme of your marketplace</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {/* Primary Colors */}
                          <div className="space-y-4">
                            <h4 className="font-medium">Primary Colors</h4>
                            <div className="space-y-3">
                              <div className="flex items-center space-x-3">
                                <label className="w-24 text-sm">Primary:</label>
                                <input
                                  type="color"
                                  value={siteSettings.primary_color || '#6366f1'}
                                  onChange={(e) => setSiteSettings({...siteSettings, primary_color: e.target.value})}
                                  className="w-12 h-12 border rounded cursor-pointer"
                                />
                                <span className="text-sm text-gray-500">{siteSettings.primary_color || '#6366f1'}</span>
                              </div>
                              <div className="flex items-center space-x-3">
                                <label className="w-24 text-sm">Secondary:</label>
                                <input
                                  type="color"
                                  value={siteSettings.secondary_color || '#f59e0b'}
                                  onChange={(e) => setSiteSettings({...siteSettings, secondary_color: e.target.value})}
                                  className="w-12 h-12 border rounded cursor-pointer"
                                />
                                <span className="text-sm text-gray-500">{siteSettings.secondary_color || '#f59e0b'}</span>
                              </div>
                              <div className="flex items-center space-x-3">
                                <label className="w-24 text-sm">Accent:</label>
                                <input
                                  type="color"
                                  value={siteSettings.accent_color || '#10b981'}
                                  onChange={(e) => setSiteSettings({...siteSettings, accent_color: e.target.value})}
                                  className="w-12 h-12 border rounded cursor-pointer"
                                />
                                <span className="text-sm text-gray-500">{siteSettings.accent_color || '#10b981'}</span>
                              </div>
                            </div>
                          </div>

                          {/* Status Colors */}
                          <div className="space-y-4">
                            <h4 className="font-medium">Status Colors</h4>
                            <div className="space-y-3">
                              <div className="flex items-center space-x-3">
                                <label className="w-24 text-sm">Success:</label>
                                <input
                                  type="color"
                                  value={siteSettings.success_color || '#10b981'}
                                  onChange={(e) => setSiteSettings({...siteSettings, success_color: e.target.value})}
                                  className="w-12 h-12 border rounded cursor-pointer"
                                />
                                <span className="text-sm text-gray-500">{siteSettings.success_color || '#10b981'}</span>
                              </div>
                              <div className="flex items-center space-x-3">
                                <label className="w-24 text-sm">Warning:</label>
                                <input
                                  type="color"
                                  value={siteSettings.warning_color || '#f59e0b'}
                                  onChange={(e) => setSiteSettings({...siteSettings, warning_color: e.target.value})}
                                  className="w-12 h-12 border rounded cursor-pointer"
                                />
                                <span className="text-sm text-gray-500">{siteSettings.warning_color || '#f59e0b'}</span>
                              </div>
                              <div className="flex items-center space-x-3">
                                <label className="w-24 text-sm">Error:</label>
                                <input
                                  type="color"
                                  value={siteSettings.error_color || '#ef4444'}
                                  onChange={(e) => setSiteSettings({...siteSettings, error_color: e.target.value})}
                                  className="w-12 h-12 border rounded cursor-pointer"
                                />
                                <span className="text-sm text-gray-500">{siteSettings.error_color || '#ef4444'}</span>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Color Preview */}
                        <div className="p-6 border rounded-lg">
                          <h4 className="font-medium mb-4">Color Preview</h4>
                          <div className="flex space-x-4">
                            <div 
                              className="px-4 py-2 rounded text-white font-medium"
                              style={{backgroundColor: siteSettings.primary_color || '#6366f1'}}
                            >
                              Primary Button
                            </div>
                            <div 
                              className="px-4 py-2 rounded text-white font-medium"
                              style={{backgroundColor: siteSettings.secondary_color || '#f59e0b'}}
                            >
                              Secondary Button
                            </div>
                            <div 
                              className="px-4 py-2 rounded text-white font-medium"
                              style={{backgroundColor: siteSettings.success_color || '#10b981'}}
                            >
                              Success
                            </div>
                            <div 
                              className="px-4 py-2 rounded text-white font-medium"
                              style={{backgroundColor: siteSettings.error_color || '#ef4444'}}
                            >
                              Error
                            </div>
                          </div>
                        </div>

                        <Button 
                          onClick={() => updateSiteSettings(siteSettings)}
                          className="w-full"
                        >
                          Save Color Settings
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Hero Selection Section */}
                {appearanceTab === 'hero' && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Hero Section Customization</CardTitle>
                      <CardDescription>Customize the main hero/banner section of your homepage</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-6">
                        {/* Hero Content */}
                        <div className="grid grid-cols-1 gap-4">
                          <div>
                            <label className="block text-sm font-medium mb-2">Hero Title</label>
                            <input
                              type="text"
                              className="w-full p-3 border rounded-md"
                              value={siteSettings.hero_title || ''}
                              onChange={(e) => setSiteSettings({...siteSettings, hero_title: e.target.value})}
                              placeholder="e.g., Discover Amazing Deals"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium mb-2">Hero Subtitle</label>
                            <textarea
                              className="w-full p-3 border rounded-md"
                              rows={3}
                              value={siteSettings.hero_subtitle || ''}
                              onChange={(e) => setSiteSettings({...siteSettings, hero_subtitle: e.target.value})}
                              placeholder="e.g., Buy and sell with confidence on Cataloro"
                            />
                          </div>
                          
                          <div>
                            <label className="block text-sm font-medium mb-2">Hero Section Height</label>
                            <div className="flex items-center space-x-2">
                              <input
                                type="range"
                                min="300"
                                max="1000"
                                step="50"
                                value={parseInt(siteSettings.hero_height?.replace('px', '') || '600')}
                                onChange={(e) => setSiteSettings({...siteSettings, hero_height: `${e.target.value}px`})}
                                className="flex-1"
                              />
                              <input
                                type="text"
                                value={siteSettings.hero_height || '600px'}
                                onChange={(e) => setSiteSettings({...siteSettings, hero_height: e.target.value})}
                                className="w-20 p-2 border rounded-md text-center"
                                placeholder="600px"
                              />
                            </div>
                            <p className="text-xs text-gray-500 mt-1">Adjust the height of the hero section (300px - 1000px)</p>
                          </div>
                        </div>

                        {/* Background Settings */}
                        <div className="space-y-4">
                          <h4 className="font-medium">Background Settings</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="block text-sm font-medium mb-2">Background Type</label>
                              <select
                                className="w-full p-3 border rounded-md"
                                value={siteSettings.hero_background_type || 'gradient'}
                                onChange={(e) => setSiteSettings({...siteSettings, hero_background_type: e.target.value})}
                              >
                                <option value="solid">Solid Color</option>
                                <option value="gradient">Gradient</option>
                              </select>
                            </div>
                            
                            {siteSettings.hero_background_type === 'solid' ? (
                              <div>
                                <label className="block text-sm font-medium mb-2">Background Color</label>
                                <input
                                  type="color"
                                  value={siteSettings.hero_background_color || '#6366f1'}
                                  onChange={(e) => setSiteSettings({...siteSettings, hero_background_color: e.target.value})}
                                  className="w-full h-12 border rounded cursor-pointer"
                                />
                              </div>
                            ) : (
                              <>
                                <div>
                                  <label className="block text-sm font-medium mb-2">Gradient Start</label>
                                  <input
                                    type="color"
                                    value={siteSettings.hero_background_gradient_start || '#667eea'}
                                    onChange={(e) => setSiteSettings({...siteSettings, hero_background_gradient_start: e.target.value})}
                                    className="w-full h-12 border rounded cursor-pointer"
                                  />
                                </div>
                                <div>
                                  <label className="block text-sm font-medium mb-2">Gradient End</label>
                                  <input
                                    type="color"
                                    value={siteSettings.hero_background_gradient_end || '#764ba2'}
                                    onChange={(e) => setSiteSettings({...siteSettings, hero_background_gradient_end: e.target.value})}
                                    className="w-full h-12 border rounded cursor-pointer"
                                  />
                                </div>
                              </>
                            )}
                          </div>
                        </div>

                        {/* Text Colors */}
                        <div className="space-y-4">
                          <h4 className="font-medium">Text Colors</h4>
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <label className="block text-sm font-medium mb-2">Title Color</label>
                              <input
                                type="color"
                                value={siteSettings.hero_text_color || '#ffffff'}
                                onChange={(e) => setSiteSettings({...siteSettings, hero_text_color: e.target.value})}
                                className="w-full h-12 border rounded cursor-pointer"
                              />
                            </div>
                            <div>
                              <label className="block text-sm font-medium mb-2">Subtitle Color</label>
                              <input
                                type="color"
                                value={siteSettings.hero_subtitle_color || '#f1f5f9'}
                                onChange={(e) => setSiteSettings({...siteSettings, hero_subtitle_color: e.target.value})}
                                className="w-full h-12 border rounded cursor-pointer"
                              />
                            </div>
                          </div>
                        </div>

                        {/* Hero Preview */}
                        <div className="p-6 rounded-lg border flex items-center justify-center" style={{
                          background: siteSettings.hero_background_type === 'gradient' 
                            ? `linear-gradient(135deg, ${siteSettings.hero_background_gradient_start} 0%, ${siteSettings.hero_background_gradient_end} 100%)`
                            : siteSettings.hero_background_color,
                          color: siteSettings.hero_text_color,
                          textAlign: 'center',
                          height: siteSettings.hero_height || '600px',
                          maxHeight: '300px' // Limit preview height
                        }}>
                          <div>
                            <h1 className="text-4xl font-bold mb-4" style={{color: siteSettings.hero_text_color}}>
                              {siteSettings.hero_title || 'Your Hero Title'}
                            </h1>
                            <p className="text-xl" style={{color: siteSettings.hero_subtitle_color}}>
                              {siteSettings.hero_subtitle || 'Your hero subtitle description'}
                            </p>
                            <p className="text-sm opacity-75 mt-2">Height: {siteSettings.hero_height || '600px'}</p>
                          </div>
                        </div>

                        <Button 
                          onClick={() => updateSiteSettings(siteSettings)}
                          className="w-full"
                        >
                          Save Hero Settings
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : (
              <div className="text-center py-12">
                <p>Failed to load appearance settings</p>
              </div>
            )}
          </TabsContent>

          {/* Page Management Tab */}
          <TabsContent value="pages">
            {loading ? (
              <div className="flex justify-center py-8">Loading...</div>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>Page Management</CardTitle>
                  <CardDescription>Create and manage custom pages for your website</CardDescription>
                </CardHeader>
                <CardContent>
                  {/* Page Management content will be added here */}
                  <div className="text-center py-12">
                    <p className="text-gray-500">Page management features coming soon</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* General Settings Tab */}
          <TabsContent value="settings">
            {loading ? (
              <div className="flex justify-center py-8">Loading...</div>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>General Settings</CardTitle>
                  <CardDescription>Basic site configuration and settings</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* Site Settings */}
                    <Card>
                      <CardHeader>
                        <CardTitle>Site Settings</CardTitle>
                        <CardDescription>Basic site configuration</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium mb-2">Site Name</label>
                            <input
                              type="text"
                              className="w-full p-3 border rounded-md"
                              value={siteSettings?.site_name || ''}
                              onChange={(e) => setSiteSettings({...siteSettings, site_name: e.target.value})}
                              placeholder="e.g., Cataloro"
                            />
                          </div>
                          
                          {/* Logo Settings */}
                          <div>
                            <label className="block text-sm font-medium mb-2">Logo Settings</label>
                            <div className="space-y-3">
                              {/* Current Logo Display */}
                              {siteSettings?.header_logo_url && (
                                <div className="flex items-center space-x-3 p-3 border rounded-md bg-gray-50">
                                  <img
                                    src={`${BACKEND_URL}${siteSettings.header_logo_url}`}
                                    alt="Current Logo"
                                    className="h-12 w-auto object-contain"
                                  />
                                  <div>
                                    <p className="text-sm font-medium">Current Logo</p>
                                    <p className="text-xs text-gray-500">{siteSettings.header_logo_alt || 'No alt text'}</p>
                                  </div>
                                </div>
                              )}
                              
                              {/* Logo Upload */}
                              <div>
                                <input
                                  type="file"
                                  accept=".png"
                                  onChange={(e) => handleLogoUpload(e, 'header')}
                                  disabled={uploading}
                                  className="hidden"
                                  id="logo-upload"
                                />
                                <label
                                  htmlFor="logo-upload"
                                  className={`inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer ${
                                    uploading ? 'opacity-50 cursor-not-allowed' : ''
                                  }`}
                                >
                                  {uploading ? (
                                    <>
                                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600 mr-2"></div>
                                      Uploading...
                                    </>
                                  ) : (
                                    <>
                                      <Plus className="h-4 w-4 mr-2" />
                                      Upload Logo (PNG only)
                                    </>
                                  )}
                                </label>
                                <p className="text-xs text-gray-500 mt-1">PNG files only, max 5MB</p>
                              </div>
                              
                              {/* Logo Alt Text */}
                              <div>
                                <label className="block text-sm font-medium mb-1">Logo Alt Text</label>
                                <input
                                  type="text"
                                  className="w-full p-2 border rounded-md"
                                  value={siteSettings?.header_logo_alt || ''}
                                  onChange={(e) => setSiteSettings({...siteSettings, header_logo_alt: e.target.value})}
                                  placeholder="e.g., Cataloro Logo"
                                />
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Database Tab */}
          <TabsContent value="database">
            {loading ? (
              <div className="flex justify-center py-8">Loading...</div>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>Database Management</CardTitle>
                  <CardDescription>Upload and manage database files</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                      <div className="text-center">
                        <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <h4 className="text-lg font-medium text-gray-900 mb-2">Upload Excel File</h4>
                        <p className="text-gray-500 mb-4">Upload a .xls or .xlsx file to create a new database</p>
                        <input
                          type="file"
                          accept=".xls,.xlsx"
                          className="hidden"
                          id="database-upload"
                        />
                        <label
                          htmlFor="database-upload"
                          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 cursor-pointer"
                        >
                          Choose Excel File
                        </label>
                      </div>
                    </div>
                    
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <div className="flex">
                        <div className="flex-shrink-0">
                          <Eye className="h-5 w-5 text-yellow-400" />
                        </div>
                        <div className="ml-3">
                          <h3 className="text-sm font-medium text-yellow-800">Important Notice</h3>
                          <div className="mt-2 text-sm text-yellow-700">
                            <p>Uploading a new database file will replace existing data. Please ensure you have a backup before proceeding.</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};
const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API}/orders`);
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex justify-center items-center h-96">
          Loading orders...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">My Orders</h1>
        
        {orders.length === 0 ? (
          <div className="text-center py-12">
            <Package className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No orders yet</h3>
            <p className="text-gray-500 mb-4">Your order history will appear here</p>
            <Button onClick={() => navigate('/')} className="bg-gradient-to-r from-indigo-600 to-purple-600">
              Start Shopping
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            {orders.map((orderData) => (
              <Card key={orderData.order.id}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-lg">{orderData.listing?.title}</h3>
                      <p className="text-gray-600">Order #{orderData.order.id}</p>
                      <p className="text-sm text-gray-500">
                        Placed on {new Date(orderData.order.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <Badge variant={orderData.order.status === 'completed' ? 'default' : 'secondary'}>
                      {orderData.order.status}
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Quantity</p>
                      <p className="font-semibold">{orderData.order.quantity}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Total Amount</p>
                      <p className="font-semibold">${orderData.order.total_amount.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Seller</p>
                      <p className="font-semibold">{orderData.seller?.full_name}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Dynamic CMS Page Component
const CMSPage = () => {
  const { slug } = useParams();
  const [pageContent, setPageContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPageContent();
  }, [slug]);

  const fetchPageContent = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API}/cms/pages/${slug}`);
      setPageContent(response.data);
    } catch (error) {
      console.error('Failed to fetch page content:', error);
      setError('Page not found');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !pageContent) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Page Not Found</h1>
            <p className="text-gray-600 mb-8">The page you're looking for doesn't exist.</p>
            <Link 
              to="/" 
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              Go Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-4xl mx-auto px-4 py-8">
        <article className="bg-white rounded-lg shadow-sm p-8">
          <header className="mb-8">
            <h1 
              className="text-4xl font-bold mb-4"
              style={{
                color: window.cataloroSettings?.h1_color || '#1f2937',
                fontSize: window.cataloroSettings?.h1_size || '2.5rem'
              }}
            >
              {pageContent.title}
            </h1>
            {pageContent.meta_description && (
              <p className="text-lg text-gray-600">{pageContent.meta_description}</p>
            )}
          </header>
          
          <div 
            className="prose prose-lg max-w-none"
            style={{
              fontFamily: window.cataloroSettings?.global_font_family || 'Inter'
            }}
            dangerouslySetInnerHTML={{ __html: pageContent.content }}
          />
          
          {pageContent.updated_at && (
            <footer className="mt-8 pt-8 border-t border-gray-200">
              <p className="text-sm text-gray-500">
                Last updated: {new Date(pageContent.updated_at).toLocaleDateString()}
              </p>
            </footer>
          )}
        </article>
      </main>
    </div>
  );
};

// Main App Component
function App() {
  // Very targeted branding removal
  useEffect(() => {
    const removeBrandingOnly = () => {
      // Only target elements that specifically contain "Made with Emergent"
      const allElements = document.querySelectorAll('*');
      allElements.forEach(element => {
        if (element.textContent && element.textContent.includes('Made with Emergent')) {
          const style = window.getComputedStyle(element);
          // Only hide if it's positioned fixed in bottom-right (typical for branding)
          if (style.position === 'fixed' && 
              (style.bottom === '20px' || style.bottom === '10px') && 
              (style.right === '20px' || style.right === '10px')) {
            element.style.display = 'none';
          }
        }
      });
    };

    // Run after a short delay to let the page load
    const timeout = setTimeout(removeBrandingOnly, 1000);
    
    return () => clearTimeout(timeout);
  }, []);

  // Load CMS data on app startup
  useEffect(() => {
    const loadCMSData = async () => {
      try {
        // Fetch site settings for main website
        const settingsResponse = await axios.get(`${API}/cms/settings`);
        const settings = settingsResponse.data;
        
        // Apply site settings to document
        if (settings.site_name) {
          document.title = `${settings.site_name} - ${settings.site_tagline}`;
        }
        
        // Apply global font family using CSS custom properties with higher specificity
        if (settings.global_font_family) {
          document.body.style.fontFamily = settings.global_font_family;
          // Update CSS custom property for global font family
          const root = document.documentElement;
          root.style.setProperty('--global-font-family', `${settings.global_font_family}, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif`);
        }
        
        // Apply CSS custom properties for dynamic theming
        const root = document.documentElement;
        root.style.setProperty('--primary-color', settings.primary_color || '#6366f1');
        root.style.setProperty('--secondary-color', settings.secondary_color || '#8b5cf6');
        root.style.setProperty('--accent-color', settings.accent_color || '#ef4444');
        root.style.setProperty('--background-color', settings.background_color || '#f8fafc');
        
        // Hero section colors
        root.style.setProperty('--hero-bg-start', settings.hero_background_gradient_start || '#667eea');
        root.style.setProperty('--hero-bg-end', settings.hero_background_gradient_end || '#764ba2');
        root.style.setProperty('--hero-text-color', settings.hero_text_color || '#ffffff');
        root.style.setProperty('--hero-subtitle-color', settings.hero_subtitle_color || '#f1f5f9');
        root.style.setProperty('--hero-height', settings.hero_height || '600px');
        
        // Typography
        root.style.setProperty('--h1-size', settings.h1_size || '3rem');
        root.style.setProperty('--h2-size', settings.h2_size || '2.25rem');
        root.style.setProperty('--h3-size', settings.h3_size || '1.875rem');
        root.style.setProperty('--h4-size', settings.h4_size || '1.5rem');
        root.style.setProperty('--h5-size', settings.h5_size || '1.25rem');
        root.style.setProperty('--h1-color', settings.h1_color || '#1f2937');
        root.style.setProperty('--h2-color', settings.h2_color || '#374151');
        root.style.setProperty('--h3-color', settings.h3_color || '#4b5563');
        root.style.setProperty('--h4-color', settings.h4_color || '#6b7280');
        root.style.setProperty('--h5-color', settings.h5_color || '#9ca3af');
        
        // Store settings globally for components to use
        window.cataloroSettings = settings;
        
      } catch (error) {
        console.error('Failed to load CMS settings:', error);
      }
      
      try {
        // Fetch navigation for main website
        const navResponse = await axios.get(`${API}/cms/navigation`);
        const navigation = navResponse.data;
        
        // Store navigation globally for header component to use
        window.cataloroNavigation = navigation;
        
        // Trigger custom event to notify components of navigation update
        window.dispatchEvent(new CustomEvent('cataloroNavigationLoaded', { detail: navigation }));
        
      } catch (error) {
        console.error('Failed to load navigation:', error);
      }
    };
    
    loadCMSData();
  }, []);

  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/auth" element={<Auth />} />
            <Route path="/" element={
              <ProtectedRoute>
                <Home />
              </ProtectedRoute>  
            } />
            <Route path="/listing/:id" element={
              <ProtectedRoute>
                <ListingDetail />
              </ProtectedRoute>
            } />
            <Route path="/sell" element={
              <ProtectedRoute>
                <Sell />
              </ProtectedRoute>
            } />
            <Route path="/cart" element={
              <ProtectedRoute>
                <Cart />
              </ProtectedRoute>
            } />
            <Route path="/orders" element={
              <ProtectedRoute>
                <Orders />
              </ProtectedRoute>
            } />
            <Route path="/admin" element={
              <ProtectedRoute>
                <AdminPanel />
              </ProtectedRoute>
            } />
            {/* Dynamic CMS Pages Route */}
            <Route path="/:slug" element={<CMSPage />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </div>
    </AuthProvider>
  );
}

export default App;