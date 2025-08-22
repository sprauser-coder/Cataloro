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
import { Search, ShoppingCart, User, Plus, Heart, Star, Clock, DollarSign, Package, Eye, Gavel, Trash2, Edit, MapPin, X } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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
    
    window.addEventListener('cataloroNavigationLoaded', handleNavigationUpdate);
    
    return () => {
      window.removeEventListener('cataloroNavigationLoaded', handleNavigationUpdate);
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
            {siteSettings?.header_logo_url ? (
              <img 
                src={`${API}${siteSettings.header_logo_url}`} 
                alt={siteSettings.header_logo_alt || 'Logo'} 
                className="h-8 w-auto object-contain"
              />
            ) : (
              <Package className="h-8 w-8 text-indigo-600" />
            )}
            <span className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              {siteName}
            </span>
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
        description: error.response?.data?.detail || "Something went wrong",
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
      return `$${listing.price?.toFixed(2)}`;
    } else {
      if (listing.current_bid) {
        return `Current bid: $${listing.current_bid.toFixed(2)}`;
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
      color: siteSettings.hero_text_color
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
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 
              className="text-5xl font-bold mb-6"
              style={{
                color: siteSettings?.hero_text_color || '#ffffff',
                fontSize: siteSettings?.h1_size || '3rem'
              }}
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
                            ? `${API}${listing.images[0]}` 
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
                        <><DollarSign className="h-3 w-3 mr-1" /> Buy Now</>
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
        description: error.response?.data?.detail || "Failed to add to cart",
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
        description: error.response?.data?.detail || "Failed to place bid",
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
        description: error.response?.data?.detail || "Failed to place order",
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
                            mainImg.src = image.startsWith('/uploads/') ? `${API}${image}` : image;
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
                    ${listing.price?.toFixed(2)}
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
                      Buy Now - ${listing.buyout_price.toFixed(2)}
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
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to upload image",
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
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to create listing",
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
                            src={`${API}${imageUrl}`}
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
                  <Label htmlFor="price">Price ($)</Label>
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
                    <Label htmlFor="buyout_price">Buy Now Price ($ - Optional)</Label>
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
                            <span className="font-bold text-lg">${item.listing.price.toFixed(2)}</span>
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
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [listings, setListings] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
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
    if (!file.type === 'image/png') {
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

      toast({
        title: "Success",
        description: `${logoType.charAt(0).toUpperCase() + logoType.slice(1)} logo uploaded successfully`,
      });

      // Clear the file input
      event.target.value = '';

    } catch (error) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to upload logo",
        variant: "destructive"
      });
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
        root.style.setProperty('--global-font-family', settings.global_font_family);
        
        // Create or update dynamic style element for font family override
        let fontStyleElement = document.getElementById('global-font-style');
        if (!fontStyleElement) {
          fontStyleElement = document.createElement('style');
          fontStyleElement.id = 'global-font-style';
          document.head.appendChild(fontStyleElement);
        }
        
        // CSS with high specificity to override Tailwind classes
        fontStyleElement.textContent = `
          /* Global font family override with high specificity */
          * {
            font-family: ${settings.global_font_family}, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif !important;
          }
          
          /* Ensure headings use the global font family */
          h1, h2, h3, h4, h5, h6, .text-3xl, .text-2xl, .text-xl, .text-lg, .font-bold, .font-semibold, .font-medium {
            font-family: ${settings.global_font_family}, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif !important;
          }
          
          /* Specific overrides for common Tailwind text classes */
          .prose, .prose h1, .prose h2, .prose h3, .prose h4, .prose h5, .prose h6 {
            font-family: ${settings.global_font_family}, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif !important;
          }
        `;
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
          <h1 className="text-3xl font-bold mb-2">Cataloro Admin Panel</h1>
          <p className="text-gray-600">Manage users, listings, and monitor platform activity</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-6">
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
            <TabsTrigger value="listings">Listings</TabsTrigger>
            <TabsTrigger value="orders">Orders</TabsTrigger>
            <TabsTrigger value="cms">Content</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
            <TabsTrigger value="appearance">Appearance</TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard">
            {loading ? (
              <div className="flex justify-center py-8">Loading...</div>
            ) : stats ? (
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
                        <p className="text-2xl font-bold">{stats.active_listings}</p>
                      </div>
                      <Package className="h-8 w-8 text-green-600" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">Total Orders</p>
                        <p className="text-2xl font-bold">{stats.total_orders}</p>
                      </div>
                      <ShoppingCart className="h-8 w-8 text-purple-600" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">Total Revenue</p>
                        <p className="text-2xl font-bold">${stats.total_revenue.toFixed(2)}</p>
                      </div>
                      <DollarSign className="h-8 w-8 text-yellow-600" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">Blocked Users</p>
                        <p className="text-2xl font-bold text-red-600">{stats.blocked_users}</p>
                      </div>
                      <Badge className="h-8 w-8 text-red-600" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : null}
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users">
            {loading ? (
              <div className="flex justify-center py-8">Loading...</div>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>User Management</CardTitle>
                  <CardDescription>View and manage all platform users</CardDescription>
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
                        {selectedUsers.length === users.length ? 'Deselect All' : 'Select All'}
                      </Button>
                      {selectedUsers.length > 0 && (
                        <>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={bulkBlockUsers}
                          >
                            Block Selected ({selectedUsers.length})
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={bulkUnblockUsers}
                          >
                            Unblock Selected ({selectedUsers.length})
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={bulkDeleteUsers}
                          >
                            Delete Selected ({selectedUsers.length})
                          </Button>
                        </>
                      )}
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={bulkDeactivateAll}
                      >
                        Deactivate All Users
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={bulkActivateAll}
                      >
                        Activate All Users
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={deleteAllNonAdminUsers}
                      >
                        ⚠️ Delete All Non-Admin
                      </Button>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    {users.map((user) => (
                      <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center space-x-4">
                          <input
                            type="checkbox"
                            checked={selectedUsers.includes(user.id)}
                            onChange={(e) => handleUserSelection(user.id, e.target.checked)}
                            className="w-4 h-4"
                          />
                          <div className="flex items-center space-x-4">
                            <Avatar>
                              <AvatarFallback>{user.full_name.charAt(0)}</AvatarFallback>
                            </Avatar>
                            <div>
                              <h3 className="font-semibold">{user.full_name}</h3>
                              <p className="text-sm text-gray-600">{user.email}</p>
                              <p className="text-xs text-gray-500">ID: {user.user_id}</p>
                              <div className="flex items-center space-x-2 mt-1">
                                <Badge variant="outline">{user.role}</Badge>
                                {user.is_blocked && <Badge variant="destructive">Blocked</Badge>}
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="text-sm text-gray-500">
                            <p>Orders: {user.total_orders}</p>
                            <p>Listings: {user.total_listings}</p>
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => resetUserPassword(user.id)}
                          >
                            Reset Password
                          </Button>
                          {user.is_blocked ? (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => unblockUser(user.id)}
                            >
                              Unblock
                            </Button>
                          ) : (
                            <Button
                              variant="destructive"
                              size="sm"
                              onClick={() => blockUser(user.id)}
                            >
                              Block
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
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
                            <p className="font-semibold">${listing.price?.toFixed(2)}</p>
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
                        <div className="p-6 rounded-lg border" style={{
                          background: siteSettings.hero_background_type === 'gradient' 
                            ? `linear-gradient(135deg, ${siteSettings.hero_background_gradient_start} 0%, ${siteSettings.hero_background_gradient_end} 100%)`
                            : siteSettings.hero_background_color,
                          color: siteSettings.hero_text_color,
                          textAlign: 'center'
                        }}>
                          <h1 className="text-4xl font-bold mb-4" style={{color: siteSettings.hero_text_color}}>
                            {siteSettings.hero_title}
                          </h1>
                          <p className="text-xl" style={{color: siteSettings.hero_subtitle_color}}>
                            {siteSettings.hero_subtitle}
                          </p>
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
                                src={`${API}${siteSettings.header_logo_url}`} 
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
                {/* Typography Settings */}
                <Card>
                  <CardHeader>
                    <CardTitle>Typography Settings</CardTitle>
                    <CardDescription>Customize fonts, heading sizes, and colors</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-6">
                      {/* Global Font */}
                      <div>
                        <label className="block text-sm font-medium mb-2">Global Font Family</label>
                        <select
                          className="w-full p-2 border rounded-md"
                          value={siteSettings.global_font_family}
                          onChange={(e) => setSiteSettings({...siteSettings, global_font_family: e.target.value})}
                        >
                          <option value="Inter">Inter</option>
                          <option value="Roboto">Roboto</option>
                          <option value="Open Sans">Open Sans</option>
                          <option value="Poppins">Poppins</option>
                          <option value="Nunito">Nunito</option>
                          <option value="Lato">Lato</option>
                          <option value="Montserrat">Montserrat</option>
                          <option value="Source Sans Pro">Source Sans Pro</option>
                          <option value="PT Sans">PT Sans</option>
                          <option value="Ubuntu">Ubuntu</option>
                        </select>
                      </div>

                      {/* Heading Sizes */}
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">H1 Size</label>
                          <select
                            className="w-full p-2 border rounded-md"
                            value={siteSettings.h1_size}
                            onChange={(e) => setSiteSettings({...siteSettings, h1_size: e.target.value})}
                          >
                            <option value="2rem">2rem (32px)</option>
                            <option value="2.25rem">2.25rem (36px)</option>
                            <option value="2.5rem">2.5rem (40px)</option>
                            <option value="3rem">3rem (48px)</option>
                            <option value="3.75rem">3.75rem (60px)</option>
                            <option value="4.5rem">4.5rem (72px)</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">H2 Size</label>
                          <select
                            className="w-full p-2 border rounded-md"
                            value={siteSettings.h2_size}
                            onChange={(e) => setSiteSettings({...siteSettings, h2_size: e.target.value})}
                          >
                            <option value="1.5rem">1.5rem (24px)</option>
                            <option value="1.875rem">1.875rem (30px)</option>
                            <option value="2.25rem">2.25rem (36px)</option>
                            <option value="3rem">3rem (48px)</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">H3 Size</label>
                          <select
                            className="w-full p-2 border rounded-md"
                            value={siteSettings.h3_size}
                            onChange={(e) => setSiteSettings({...siteSettings, h3_size: e.target.value})}
                          >
                            <option value="1.125rem">1.125rem (18px)</option>
                            <option value="1.25rem">1.25rem (20px)</option>
                            <option value="1.5rem">1.5rem (24px)</option>
                            <option value="1.875rem">1.875rem (30px)</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">H4 Size</label>
                          <select
                            className="w-full p-2 border rounded-md"
                            value={siteSettings.h4_size}
                            onChange={(e) => setSiteSettings({...siteSettings, h4_size: e.target.value})}
                          >
                            <option value="1rem">1rem (16px)</option>
                            <option value="1.125rem">1.125rem (18px)</option>
                            <option value="1.25rem">1.25rem (20px)</option>
                            <option value="1.5rem">1.5rem (24px)</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">H5 Size</label>
                          <select
                            className="w-full p-2 border rounded-md"
                            value={siteSettings.h5_size}
                            onChange={(e) => setSiteSettings({...siteSettings, h5_size: e.target.value})}
                          >
                            <option value="0.875rem">0.875rem (14px)</option>
                            <option value="1rem">1rem (16px)</option>
                            <option value="1.125rem">1.125rem (18px)</option>
                            <option value="1.25rem">1.25rem (20px)</option>
                          </select>
                        </div>
                      </div>

                      {/* Heading Colors */}
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">H1 Color</label>
                          <div className="flex items-center space-x-2">
                            <input
                              type="color"
                              value={siteSettings.h1_color}
                              onChange={(e) => setSiteSettings({...siteSettings, h1_color: e.target.value})}
                              className="w-12 h-10 border rounded"
                            />
                            <input
                              type="text"
                              value={siteSettings.h1_color}
                              onChange={(e) => setSiteSettings({...siteSettings, h1_color: e.target.value})}
                              className="flex-1 p-2 border rounded-md font-mono text-sm"
                            />
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">H2 Color</label>
                          <div className="flex items-center space-x-2">
                            <input
                              type="color"
                              value={siteSettings.h2_color}
                              onChange={(e) => setSiteSettings({...siteSettings, h2_color: e.target.value})}
                              className="w-12 h-10 border rounded"
                            />
                            <input
                              type="text"
                              value={siteSettings.h2_color}
                              onChange={(e) => setSiteSettings({...siteSettings, h2_color: e.target.value})}
                              className="flex-1 p-2 border rounded-md font-mono text-sm"
                            />
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">H3 Color</label>
                          <div className="flex items-center space-x-2">
                            <input
                              type="color"
                              value={siteSettings.h3_color}
                              onChange={(e) => setSiteSettings({...siteSettings, h3_color: e.target.value})}
                              className="w-12 h-10 border rounded"
                            />
                            <input
                              type="text"
                              value={siteSettings.h3_color}
                              onChange={(e) => setSiteSettings({...siteSettings, h3_color: e.target.value})}
                              className="flex-1 p-2 border rounded-md font-mono text-sm"
                            />
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">H4 Color</label>
                          <div className="flex items-center space-x-2">
                            <input
                              type="color"
                              value={siteSettings.h4_color}
                              onChange={(e) => setSiteSettings({...siteSettings, h4_color: e.target.value})}
                              className="w-12 h-10 border rounded"
                            />
                            <input
                              type="text"
                              value={siteSettings.h4_color}
                              onChange={(e) => setSiteSettings({...siteSettings, h4_color: e.target.value})}
                              className="flex-1 p-2 border rounded-md font-mono text-sm"
                            />
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">H5 Color</label>
                          <div className="flex items-center space-x-2">
                            <input
                              type="color"
                              value={siteSettings.h5_color}
                              onChange={(e) => setSiteSettings({...siteSettings, h5_color: e.target.value})}
                              className="w-12 h-10 border rounded"
                            />
                            <input
                              type="text"
                              value={siteSettings.h5_color}
                              onChange={(e) => setSiteSettings({...siteSettings, h5_color: e.target.value})}
                              className="flex-1 p-2 border rounded-md font-mono text-sm"
                            />
                          </div>
                        </div>
                      </div>

                      {/* Typography Preview */}
                      <div className="p-6 bg-gray-50 rounded-lg" style={{fontFamily: siteSettings.global_font_family}}>
                        <h4 className="font-medium mb-4">Typography Preview</h4>
                        <h1 style={{fontSize: siteSettings.h1_size, color: siteSettings.h1_color}} className="font-bold">
                          H1 Heading - {siteSettings.h1_size}
                        </h1>
                        <h2 style={{fontSize: siteSettings.h2_size, color: siteSettings.h2_color}} className="font-semibold mt-2">
                          H2 Heading - {siteSettings.h2_size}
                        </h2>
                        <h3 style={{fontSize: siteSettings.h3_size, color: siteSettings.h3_color}} className="font-medium mt-2">
                          H3 Heading - {siteSettings.h3_size}
                        </h3>
                        <h4 style={{fontSize: siteSettings.h4_size, color: siteSettings.h4_color}} className="font-medium mt-2">
                          H4 Heading - {siteSettings.h4_size}
                        </h4>
                        <h5 style={{fontSize: siteSettings.h5_size, color: siteSettings.h5_color}} className="font-medium mt-2">
                          H5 Heading - {siteSettings.h5_size}
                        </h5>
                        <p className="mt-4 text-gray-600">
                          This is how your text will look with the selected font family: <strong>{siteSettings.global_font_family}</strong>
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Theme Colors */}
                <Card>
                  <CardHeader>
                    <CardTitle>Theme Colors</CardTitle>
                    <CardDescription>Customize your marketplace color scheme</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm font-medium mb-2">Primary Color</label>
                          <div className="flex items-center space-x-2">
                            <input
                              type="color"
                              value={siteSettings.primary_color}
                              onChange={(e) => setSiteSettings({...siteSettings, primary_color: e.target.value})}
                              className="w-12 h-10 border rounded"
                            />
                            <input
                              type="text"
                              value={siteSettings.primary_color}
                              onChange={(e) => setSiteSettings({...siteSettings, primary_color: e.target.value})}
                              className="flex-1 p-2 border rounded-md font-mono"
                            />
                          </div>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium mb-2">Secondary Color</label>
                          <div className="flex items-center space-x-2">
                            <input
                              type="color"
                              value={siteSettings.secondary_color}
                              onChange={(e) => setSiteSettings({...siteSettings, secondary_color: e.target.value})}
                              className="w-12 h-10 border rounded"
                            />
                            <input
                              type="text"
                              value={siteSettings.secondary_color}
                              onChange={(e) => setSiteSettings({...siteSettings, secondary_color: e.target.value})}
                              className="flex-1 p-2 border rounded-md font-mono"
                            />
                          </div>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium mb-2">Accent Color</label>
                          <div className="flex items-center space-x-2">
                            <input
                              type="color"
                              value={siteSettings.accent_color}
                              onChange={(e) => setSiteSettings({...siteSettings, accent_color: e.target.value})}
                              className="w-12 h-10 border rounded"
                            />
                            <input
                              type="text"
                              value={siteSettings.accent_color}
                              onChange={(e) => setSiteSettings({...siteSettings, accent_color: e.target.value})}
                              className="flex-1 p-2 border rounded-md font-mono"
                            />
                          </div>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium mb-2">Background Color</label>
                          <div className="flex items-center space-x-2">
                            <input
                              type="color"
                              value={siteSettings.background_color}
                              onChange={(e) => setSiteSettings({...siteSettings, background_color: e.target.value})}
                              className="w-12 h-10 border rounded"
                            />
                            <input
                              type="text"
                              value={siteSettings.background_color}
                              onChange={(e) => setSiteSettings({...siteSettings, background_color: e.target.value})}
                              className="flex-1 p-2 border rounded-md font-mono"
                            />
                          </div>
                        </div>
                      </div>
                      
                      <div className="p-4 bg-gray-50 rounded-lg">
                        <h4 className="font-medium mb-4">Color Preview</h4>
                        <div className="flex items-center space-x-4">
                          <div 
                            className="w-16 h-16 rounded-lg flex items-center justify-center text-white font-bold text-xs"
                            style={{backgroundColor: siteSettings.primary_color}}
                          >
                            Primary
                          </div>
                          <div 
                            className="w-16 h-16 rounded-lg flex items-center justify-center text-white font-bold text-xs"
                            style={{backgroundColor: siteSettings.secondary_color}}
                          >
                            Secondary
                          </div>
                          <div 
                            className="w-16 h-16 rounded-lg flex items-center justify-center text-white font-bold text-xs"
                            style={{backgroundColor: siteSettings.accent_color}}
                          >
                            Accent
                          </div>
                          <div 
                            className="w-16 h-16 rounded-lg flex items-center justify-center border text-xs"
                            style={{backgroundColor: siteSettings.background_color}}
                          >
                            BG
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <div className="flex space-x-2">
                  <Button
                    onClick={() => updateSiteSettings(siteSettings)}
                    className="flex-1"
                  >
                    Save All Appearance Settings
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setSiteSettings({
                        ...siteSettings,
                        global_font_family: 'Inter',
                        h1_size: '3rem',
                        h2_size: '2.25rem',
                        h3_size: '1.875rem',
                        h4_size: '1.5rem',
                        h5_size: '1.25rem',
                        h1_color: '#1f2937',
                        h2_color: '#374151',
                        h3_color: '#4b5563',
                        h4_color: '#6b7280',
                        h5_color: '#9ca3af',
                        primary_color: '#6366f1',
                        secondary_color: '#8b5cf6',
                        accent_color: '#ef4444',
                        background_color: '#f8fafc'
                      });
                    }}
                  >
                    Reset to Defaults
                  </Button>
                </div>
              </div>
            ) : null}
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