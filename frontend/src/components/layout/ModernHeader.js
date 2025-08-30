/**
 * CATALORO - Ultra-Modern Header Navigation
 * Sleek header with comprehensive navigation and enhanced notifications
 */

import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { 
  ShoppingCart, 
  Bell, 
  User, 
  Heart,
  MessageCircle,
  Settings,
  LogOut,
  Moon,
  Sun,
  Menu,
  X,
  Store,
  BarChart3,
  Package,
  DollarSign,
  Shield,
  Filter,
  List,
  Zap,
  ChevronDown,
  Check,
  CheckCheck,
  Star,
  Clock,
  Eye,
  TrendingUp
} from 'lucide-react';
import { APP_ROUTES } from '../../config/directions';
import { useAuth } from '../../context/AuthContext';
import { useMarketplace } from '../../context/MarketplaceContext';
import { liveService } from '../../services/liveService';

function ModernHeader({ darkMode, toggleDarkMode, isMobileMenuOpen, setIsMobileMenuOpen }) {
  const { user } = useAuth();
  const { cartItems, favoriteCount } = useMarketplace();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadNotifications, setUnreadNotifications] = useState(0);
  const [unreadMessages, setUnreadMessages] = useState(0);
  const [siteBranding, setSiteBranding] = useState({});
  const navigate = useNavigate();
  const location = useLocation();
  const userMenuRef = useRef(null);
  const notificationRef = useRef(null);

  // Load notifications from backend
  const loadNotifications = async () => {
    if (!user?.id) return;
    
    try {
      const userNotifications = await liveService.getUserNotifications(user.id);
      const userMessages = await liveService.getUserMessages(user.id);
      
      setNotifications(userNotifications);
      setUnreadNotifications(userNotifications.filter(n => !n.is_read).length);
      setUnreadMessages(userMessages.filter(m => !m.is_read && m.sender_id !== user.id).length);
    } catch (error) {
      console.error('Failed to load notifications:', error);
      // Use demo data as fallback
      const demoNotifications = [
        {
          id: '1',
          title: 'New message from John',
          message: 'About MacBook Pro listing',
          type: 'message',
          is_read: false,
          created_at: new Date(Date.now() - 2 * 60 * 1000).toISOString()
        },
        {
          id: '2',
          title: 'Your listing was favorited',
          message: 'iPhone 14 Pro Max - Space Black',
          type: 'favorite',
          is_read: false,
          created_at: new Date(Date.now() - 60 * 60 * 1000).toISOString()
        },
        {
          id: '3',
          title: 'Payment received',
          message: '$899 for Gaming Laptop sale',
          type: 'payment',
          is_read: true,
          created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString()
        }
      ];
      setNotifications(demoNotifications);
      setUnreadNotifications(demoNotifications.filter(n => !n.is_read).length);
      setUnreadMessages(2); // Demo fallback
    }
  };

  // Mark notification as read
  const markNotificationAsRead = async (notificationId) => {
    try {
      await liveService.markNotificationRead(user.id, notificationId);
      setNotifications(notifications.map(n => 
        n.id === notificationId ? { ...n, is_read: true } : n
      ));
      setUnreadNotifications(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  // Mark all notifications as read
  const markAllNotificationsAsRead = async () => {
    try {
      const unreadIds = notifications.filter(n => !n.is_read).map(n => n.id);
      await Promise.all(unreadIds.map(id => liveService.markNotificationRead(user.id, id)));
      setNotifications(notifications.map(n => ({ ...n, is_read: true })));
      setUnreadNotifications(0);
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  };

  useEffect(() => {
    // Function to load branding and notification data
    const loadData = () => {
      // Load site branding from localStorage
      const brandingData = localStorage.getItem('cataloro_site_branding');
      if (brandingData) {
        try {
          const parsedBranding = JSON.parse(brandingData);
          console.log('Header loading branding data:', parsedBranding);
          setSiteBranding(parsedBranding);
        } catch (error) {
          console.error('Error parsing branding data:', error);
        }
      } else {
        console.log('No branding data found in localStorage');
      }
    };

    // Load initial data
    loadData();
    
    // Load notifications if user is available
    if (user?.id) {
      loadNotifications();
    }

    // Listen for localStorage changes (when admin updates branding)
    const handleStorageChange = (e) => {
      if (e.key === 'cataloro_site_branding') {
        loadData();
      }
    };

    // Listen for custom events when branding is updated
    const handleBrandingUpdate = () => {
      loadData();
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('brandingUpdated', handleBrandingUpdate);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('brandingUpdated', handleBrandingUpdate);
    };
  }, [user?.id]);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('cataloro_token');
    localStorage.removeItem('cataloro_user');
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;
  const isAdmin = user?.role === 'admin';

  const navigationItems = [
    { label: 'Browse', path: '/browse', icon: Store },
    { label: 'Listings', path: '/my-listings', icon: Package },
    { label: 'Orders', path: '/my-orders', icon: DollarSign },
    ...(isAdmin ? [{ label: 'Admin', path: '/admin', icon: Shield }] : []),
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-white/20 shadow-lg shadow-black/5">
      <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 via-purple-600/5 to-pink-600/5"></div>
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* Logo and Brand - ENHANCED WITH DYNAMIC BRANDING */}
          <div className="flex items-center space-x-8">
            <Link to="/browse" className="flex items-center space-x-3 group header-logo">
              {(siteBranding.logo_light_url || siteBranding.logo_dark_url || siteBranding.logo_url) ? (
                // Custom Logo Mode - FULL LOGO REPLACEMENT (NO TEXT)
                <div className="relative">
                  <img 
                    src={darkMode ? (siteBranding.logo_dark_url || siteBranding.logo_url) : (siteBranding.logo_light_url || siteBranding.logo_url)}
                    alt={siteBranding.site_name || 'Cataloro'}
                    className="h-12 max-w-[200px] object-contain group-hover:opacity-90 transition-opacity duration-300"
                    onError={(e) => {
                      // Fallback to default icon + text if image fails
                      e.target.style.display = 'none';
                      e.target.parentElement.nextSibling.style.display = 'flex';
                    }}
                  />
                </div>
              ) : (
                // Default Icon + Text Mode
                <>
                  {/* Icon Container */}
                  <div className="relative">
                    <div className="w-12 h-12 rounded-2xl flex items-center justify-center relative overflow-hidden" style={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      boxShadow: '0 8px 25px rgba(103, 126, 234, 0.4)'
                    }}>
                      <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                      <Store className="w-7 h-7 text-white relative z-10" />
                    </div>
                    <div className="absolute inset-0 rounded-2xl" style={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      filter: 'blur(8px)',
                      opacity: '0.3',
                      transform: 'scale(1.1)'
                    }}></div>
                  </div>
                  
                  {/* Brand Text */}
                  <div className="hidden sm:block">
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white group-hover:text-gray-700 dark:group-hover:text-white/90 transition-colors header-title" style={{
                      background: 'linear-gradient(135deg, #1f2937 0%, #374151 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent'
                    }}>
                      {siteBranding.site_name || 'Cataloro'}
                    </h1>
                    <p className="text-xs text-gray-600 dark:text-white/70 font-medium tracking-wide">
                      {siteBranding.site_description || 'ULTRA-MODERN MARKETPLACE'}
                    </p>
                  </div>
                </>
              )}
              
              {/* Fallback Icon + Text (hidden by default, shown if logo fails to load) */}
              <div className="items-center space-x-3" style={{ display: 'none' }}>
                <div className="relative">
                  <div className="w-12 h-12 rounded-2xl flex items-center justify-center relative overflow-hidden" style={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    boxShadow: '0 8px 25px rgba(103, 126, 234, 0.4)'
                  }}>
                    <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    <Store className="w-7 h-7 text-white relative z-10" />
                  </div>
                </div>
                <div className="hidden sm:block">
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {siteBranding.site_name || 'Cataloro'}
                  </h1>
                  <p className="text-xs text-gray-600 dark:text-white/70 font-medium tracking-wide">
                    {siteBranding.site_description || 'ULTRA-MODERN MARKETPLACE'}
                  </p>
                </div>
              </div>
            </Link>

            {/* Navigation Links */}
            <nav className="hidden lg:flex space-x-2">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-all duration-300 font-medium text-sm ${
                      isActive
                        ? 'bg-white/20 dark:bg-white/20 text-gray-900 dark:text-white shadow-lg backdrop-blur-md'
                        : 'text-gray-700 dark:text-white/80 hover:text-gray-900 dark:hover:text-white hover:bg-white/10 dark:hover:bg-white/10'
                    }`}
                    style={isActive ? {
                      background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%)',
                      backdropFilter: 'blur(20px)',
                      boxShadow: '0 4px 15px rgba(255, 255, 255, 0.1)'
                    } : {}}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            
            {/* Quick Actions (Desktop) */}
            <div className="hidden lg:flex items-center space-x-2">
              {/* Messages */}
              <Link
                to="/messages"
                className="relative p-2 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-all duration-200"
              >
                <MessageCircle className="w-6 h-6" />
                {unreadMessages > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium">
                    {unreadMessages}
                  </span>
                )}
              </Link>

              {/* Favorites */}
              <Link
                to="/favorites"
                className="relative p-2 text-gray-600 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all duration-200"
              >
                <Heart className="w-6 h-6" />
                {favoriteCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium">
                    {favoriteCount}
                  </span>
                )}
              </Link>

              {/* Cart */}
              <Link
                to="/cart"
                className="relative p-3 text-gray-700 dark:text-white/80 hover:text-gray-900 dark:hover:text-white transition-all duration-300 group"
                style={{
                  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
                  backdropFilter: 'blur(20px)',
                  borderRadius: '16px',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}
              >
                <ShoppingCart className="w-5 h-5" />
                {(cartItems?.length > 0 || cartItems > 0) && (
                  <span className="absolute -top-2 -right-2 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold text-[10px]" style={{
                    background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                    boxShadow: '0 4px 15px rgba(240, 147, 251, 0.4)'
                  }}>
                    {Array.isArray(cartItems) ? cartItems.length : cartItems}
                  </span>
                )}
              </Link>
            </div>

            {/* Notifications */}
            <div className="relative" ref={notificationRef}>
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="relative p-3 text-gray-700 dark:text-white/80 hover:text-gray-900 dark:hover:text-white transition-all duration-300 group"
                style={{
                  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
                  backdropFilter: 'blur(20px)',
                  borderRadius: '16px',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}
              >
                <Bell className="w-5 h-5" />
                {unreadNotifications > 0 && (
                  <span className="absolute -top-2 -right-2 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold text-[10px]" style={{
                    background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
                    boxShadow: '0 4px 15px rgba(250, 112, 154, 0.4)'
                  }}>
                    {unreadNotifications}
                  </span>
                )}
              </button>

              {/* Modern Notifications Dropdown - 95% BACKGROUND OPACITY */}
              {showNotifications && (
                <div className="absolute right-0 mt-3 w-80 rounded-2xl shadow-2xl py-3 z-50 notifications-dropdown-enhanced" style={{
                  background: darkMode 
                    ? 'rgba(0, 0, 0, 0.95)'
                    : 'rgba(255, 255, 255, 0.95)',
                  backdropFilter: 'blur(25px)',
                  border: darkMode 
                    ? '1px solid rgba(255, 255, 255, 0.2)' 
                    : '1px solid rgba(0, 0, 0, 0.2)'
                }}>
                  <div className="px-6 py-4 border-b border-white/10">
                    <div className="flex items-center justify-between">
                      <h3 className="font-bold text-gray-900 dark:text-white text-lg">Notifications</h3>
                      <button className="text-sm text-gray-600 dark:text-white/80 hover:text-gray-800 dark:hover:text-white font-medium">Mark all read</button>
                    </div>
                  </div>
                  <div className="max-h-80 overflow-y-auto">
                    {/* Demo notifications with modern styling */}
                    <div className="px-6 py-4 hover:bg-white/5 dark:hover:bg-white/5 cursor-pointer border-l-4 transition-all duration-300" style={{borderColor: '#667eea'}}>
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">New message from John</p>
                      <p className="text-xs text-gray-600 dark:text-white/70 mt-1">About MacBook Pro listing</p>
                      <p className="text-xs text-gray-700 dark:text-white/80 mt-2 font-medium">2 min ago</p>
                    </div>
                    <div className="px-6 py-4 hover:bg-white/5 dark:hover:bg-white/5 cursor-pointer border-l-4 transition-all duration-300" style={{borderColor: '#f093fb'}}>
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">Your listing was favorited</p>
                      <p className="text-xs text-gray-600 dark:text-white/70 mt-1">iPhone 14 Pro Max - Space Black</p>
                      <p className="text-xs text-gray-700 dark:text-white/80 mt-2 font-medium">1 hour ago</p>
                    </div>
                    <div className="px-6 py-4 hover:bg-white/5 dark:hover:bg-white/5 cursor-pointer border-l-4 transition-all duration-300" style={{borderColor: '#43e97b'}}>
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">Payment received</p>
                      <p className="text-xs text-gray-600 dark:text-white/70 mt-1">$899 for Gaming Laptop sale</p>
                      <p className="text-xs text-gray-700 dark:text-white/80 mt-2 font-medium">3 hours ago</p>
                    </div>
                  </div>
                  <div className="px-6 py-3 border-t border-white/10">
                    <Link
                      to="/notifications"
                      className="text-sm text-gray-600 dark:text-white/80 hover:text-gray-800 dark:hover:text-white font-medium"
                      onClick={() => setShowNotifications(false)}
                    >
                      View all notifications →
                    </Link>
                  </div>
                </div>
              )}
            </div>

            {/* Dark Mode Toggle */}
            <button
              onClick={toggleDarkMode}
              className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-all duration-200"
            >
              {darkMode ? <Sun className="w-6 h-6" /> : <Moon className="w-6 h-6" />}
            </button>

            {/* User Profile */}
            <div className="relative" ref={userMenuRef}>
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-3 p-2 rounded-2xl transition-all duration-300 group"
                style={{
                  background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.06) 100%)',
                  backdropFilter: 'blur(20px)',
                  border: '1px solid rgba(255, 255, 255, 0.2)'
                }}
              >
                <div className="w-10 h-10 rounded-2xl flex items-center justify-center relative overflow-hidden" style={{
                  background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                  boxShadow: '0 6px 20px rgba(79, 172, 254, 0.4)'
                }}>
                  <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <span className="text-white font-bold text-sm relative z-10">
                    {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                  </span>
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">
                    {user?.full_name || user?.username || 'User'}
                  </p>
                  <p className="text-xs text-gray-600 dark:text-white/70 font-medium uppercase tracking-wide">
                    {user?.role}
                  </p>
                </div>
                <ChevronDown className={`w-4 h-4 text-gray-700 dark:text-white/80 transition-transform duration-300 ${showUserMenu ? 'rotate-180' : ''}`} />
              </button>

              {/* Modern User Dropdown Menu - 95% BACKGROUND OPACITY */}
              {showUserMenu && (
                <div className="absolute right-0 mt-3 w-72 rounded-2xl shadow-2xl py-2 z-50 profile-dropdown-enhanced" style={{
                  background: darkMode 
                    ? 'rgba(0, 0, 0, 0.95)'
                    : 'rgba(255, 255, 255, 0.95)',
                  backdropFilter: 'blur(25px)',
                  border: darkMode 
                    ? '1px solid rgba(255, 255, 255, 0.2)' 
                    : '1px solid rgba(0, 0, 0, 0.2)'
                }}>
                  <div className="px-6 py-4 border-b border-white/10">
                    <p className="text-base font-bold text-gray-900 dark:text-white">
                      {user?.full_name || user?.username}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-white/70">{user?.email}</p>
                  </div>
                  
                  <div className="py-2">
                    <Link
                      to="/profile"
                      className="flex items-center px-6 py-3 text-sm text-gray-700 dark:text-white/90 hover:text-gray-900 dark:hover:text-white hover:bg-white/5 dark:hover:bg-white/5 transition-all duration-300 group"
                      onClick={() => setShowUserMenu(false)}
                    >
                      <div className="p-2 rounded-lg mr-3 group-hover:bg-white/10 transition-all duration-300" style={{
                        background: 'linear-gradient(135deg, rgba(79, 172, 254, 0.2), rgba(0, 242, 254, 0.1))'
                      }}>
                        <User className="w-4 h-4" />
                      </div>
                      <span className="font-medium">Profile Settings</span>
                    </Link>
                    
                    <Link
                      to="/my-listings"
                      className="flex items-center px-6 py-3 text-sm text-gray-700 dark:text-white/90 hover:text-gray-900 dark:hover:text-white hover:bg-white/5 dark:hover:bg-white/5 transition-all duration-300 group"
                      onClick={() => setShowUserMenu(false)}
                    >
                      <div className="p-2 rounded-lg mr-3 group-hover:bg-white/10 transition-all duration-300" style={{
                        background: 'linear-gradient(135deg, rgba(240, 147, 251, 0.2), rgba(245, 87, 108, 0.1))'
                      }}>
                        <Package className="w-4 h-4" />
                      </div>
                      <span className="font-medium">My Listings</span>
                    </Link>
                    
                    {user?.role === 'admin' && (
                      <Link
                        to="/admin"
                        className="flex items-center px-6 py-3 text-sm text-gray-700 dark:text-white/90 hover:text-gray-900 dark:hover:text-white hover:bg-white/5 dark:hover:bg-white/5 transition-all duration-300 group"
                        onClick={() => setShowUserMenu(false)}
                      >
                        <div className="p-2 rounded-lg mr-3 group-hover:bg-white/10 transition-all duration-300" style={{
                          background: 'linear-gradient(135deg, rgba(250, 112, 154, 0.2), rgba(254, 225, 64, 0.1))'
                        }}>
                          <Shield className="w-4 h-4" />
                        </div>
                        <span className="font-medium">Admin Panel</span>
                      </Link>
                    )}
                  </div>
                  
                  <div className="border-t border-white/10 pt-2">
                    <button
                      onClick={handleLogout}
                      className="flex items-center w-full px-6 py-3 text-sm text-gray-700 dark:text-white/90 hover:text-red-600 dark:hover:text-red-300 hover:bg-red-500/10 dark:hover:bg-red-500/10 transition-all duration-300 group"
                    >
                      <div className="p-2 rounded-lg mr-3 group-hover:bg-red-500/20 transition-all duration-300" style={{
                        background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1))'
                      }}>
                        <LogOut className="w-4 h-4" />
                      </div>
                      <span className="font-medium">Sign Out</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Mobile Menu Toggle */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="lg:hidden p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-all duration-200"
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

export default ModernHeader;