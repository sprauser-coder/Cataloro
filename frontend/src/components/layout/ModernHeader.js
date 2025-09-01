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
  TrendingUp,
  Trash2,
  RefreshCw,
  Volume2,
  VolumeX,
  BellOff,
  Globe
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
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [notificationFilter, setNotificationFilter] = useState('all'); // all, unread, read
  const [lastNotificationCheck, setLastNotificationCheck] = useState(Date.now());
  const navigate = useNavigate();
  const location = useLocation();
  const userMenuRef = useRef(null);
  const notificationRef = useRef(null);

  // Enhanced notification sound
  const playNotificationSound = () => {
    if (soundEnabled) {
      try {
        const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmIdBz6S3fPNeSsFJICO89iMOQkXZL7n6KdUFAg+ltryxnkpBSl+zfDZjjkKGGG+6OSlSxELStPx07dORgk2jNnuw3MoByJ9yvDQjj0KFmSx5eeScxELTanxx4A=');
        audio.volume = 0.3;
        audio.play().catch(console.error);
      } catch (error) {
        console.error('Could not play notification sound:', error);
      }
    }
  };

  // Delete notification (enhanced with backend API call)
  const deleteNotification = async (notificationId, event, showFeedback = true) => {
    if (event) event.stopPropagation();
    try {
      // Remove from local state immediately with animation
      const deletedNotification = notifications.find(n => n.id === notificationId);
      
      // Add removal animation class before removing
      const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
      if (notificationElement) {
        notificationElement.classList.add('notification-removing');
        setTimeout(() => {
          setNotifications(notifications.filter(n => n.id !== notificationId));
          if (deletedNotification && !deletedNotification.is_read) {
            setUnreadNotifications(prev => Math.max(0, prev - 1));
          }
        }, 300); // Match animation duration
      } else {
        // Immediate removal if element not found
        setNotifications(notifications.filter(n => n.id !== notificationId));
        if (deletedNotification && !deletedNotification.is_read) {
          setUnreadNotifications(prev => Math.max(0, prev - 1));
        }
      }
      
      // Backend API call to delete notification permanently
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${user?.id}/notifications/${notificationId}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          console.warn('Failed to delete notification from backend:', response.statusText);
        }
      } catch (apiError) {
        console.error('API error deleting notification:', apiError);
      }
      
      // Optional feedback
      if (showFeedback) {
        console.log('Notification removed');
      }
      
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  // Enhanced action handlers with auto-delete
  const handleMarkAsRead = async (notificationId, event) => {
    event.stopPropagation();
    try {
      await markNotificationAsRead(notificationId);
      // Auto-delete after marking as read
      setTimeout(() => {
        deleteNotification(notificationId, null, false);
      }, 1000); // 1 second delay to show the action was completed
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const handleAcceptRequest = async (notificationId, event) => {
    event.stopPropagation();
    try {
      // Navigate to pending sales for approval
      setShowNotifications(false);
      navigate('/pending-sales');
      // Auto-delete the notification
      setTimeout(() => {
        deleteNotification(notificationId, null, false);
      }, 500);
    } catch (error) {
      console.error('Failed to handle accept request:', error);
    }
  };

  const handleDeclineRequest = async (notificationId, event) => {
    event.stopPropagation();
    try {
      // TODO: Add actual reject functionality
      console.log('Request declined');
      // Auto-delete the notification immediately
      deleteNotification(notificationId, null, false);
    } catch (error) {
      console.error('Failed to handle decline request:', error);
    }
  };

  const handleReplyToMessage = async (notificationId, event) => {
    event.stopPropagation();
    try {
      // Navigate to messages
      setShowNotifications(false);
      navigate('/messages');
      // Auto-delete the notification
      setTimeout(() => {
        deleteNotification(notificationId, null, false);
      }, 500);
    } catch (error) {
      console.error('Failed to handle reply to message:', error);
    }
  };

  // Enhanced notification filtering
  const getFilteredNotifications = () => {
    let filtered = notifications;
    
    switch (notificationFilter) {
      case 'unread':
        filtered = notifications.filter(n => !n.is_read);
        break;
      case 'read':
        filtered = notifications.filter(n => n.is_read);
        break;
      default:
        filtered = notifications;
    }
    
    return filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  };
  // Load notifications from backend with enhanced features
  const loadNotifications = async (showNewNotificationAlert = false) => {
    if (!user?.id) return;
    
    try {
      const userNotifications = await liveService.getUserNotifications(user.id);
      const userMessages = await liveService.getUserMessages(user.id);
      
      // Check for new notifications since last check
      if (showNewNotificationAlert && notifications.length > 0) {
        const newNotifications = userNotifications.filter(n => 
          new Date(n.created_at) > new Date(lastNotificationCheck) && !n.is_read
        );
        
        if (newNotifications.length > 0) {
          playNotificationSound();
          // Show browser notification if supported
          if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(`${newNotifications.length} new notification${newNotifications.length > 1 ? 's' : ''}`, {
              body: newNotifications[0].title,
              icon: '/favicon.ico',
              tag: 'cataloro-notification'
            });
          }
        }
      }
      
      setNotifications(userNotifications);
      setUnreadNotifications(userNotifications.filter(n => !n.is_read).length);
      setUnreadMessages(userMessages.filter(m => !m.is_read && m.sender_id !== user.id).length);
      setLastNotificationCheck(Date.now());
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

  // Mark notification as read with animation
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

  // Mark all notifications as read with bulk operation
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

  // Request notification permission on component mount
  const requestNotificationPermission = () => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().then(permission => {
        console.log('Notification permission:', permission);
      });
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
      requestNotificationPermission();
      
      // Set up real-time notification polling every 30 seconds
      const notificationInterval = setInterval(() => {
        loadNotifications(true);
      }, 30000);
      
      return () => clearInterval(notificationInterval);
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

  // Load sound preference from localStorage
  useEffect(() => {
    const soundPref = localStorage.getItem('cataloro_notification_sound');
    setSoundEnabled(soundPref !== 'false');
  }, []);

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
    { label: 'Deals', path: '/my-deals', icon: DollarSign },
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
                  background: darkMode 
                    ? 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)'
                    : 'linear-gradient(135deg, rgba(0, 0, 0, 0.08) 0%, rgba(0, 0, 0, 0.04) 100%)',
                  backdropFilter: 'blur(20px)',
                  borderRadius: '16px',
                  border: darkMode 
                    ? '1px solid rgba(255, 255, 255, 0.1)'
                    : '1px solid rgba(0, 0, 0, 0.1)'
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
                  background: darkMode 
                    ? 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)'
                    : 'linear-gradient(135deg, rgba(0, 0, 0, 0.08) 0%, rgba(0, 0, 0, 0.04) 100%)',
                  backdropFilter: 'blur(20px)',
                  borderRadius: '16px',
                  border: darkMode 
                    ? '1px solid rgba(255, 255, 255, 0.1)'
                    : '1px solid rgba(0, 0, 0, 0.1)'
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

              {/* Enhanced Notifications Dropdown - State-of-the-Art Design */}
              {showNotifications && (
                <div className="absolute right-0 mt-3 w-96 rounded-2xl shadow-2xl py-3 z-50 notifications-dropdown-enhanced animate-in" style={{
                  background: darkMode 
                    ? 'rgba(0, 0, 0, 0.95)'
                    : 'rgba(255, 255, 255, 0.95)',
                  backdropFilter: 'blur(25px)',
                  border: darkMode 
                    ? '1px solid rgba(255, 255, 255, 0.2)' 
                    : '1px solid rgba(0, 0, 0, 0.2)',
                  animation: 'slideDown 0.3s ease-out'
                }}>
                  {/* Enhanced Header with Controls */}
                  <div className="px-6 py-4 border-b border-white/10">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-bold text-gray-900 dark:text-white text-lg flex items-center">
                        <Bell className="w-5 h-5 mr-2" />
                        Notifications
                        {unreadNotifications > 0 && (
                          <span className="ml-2 bg-red-500 text-white text-xs px-2 py-1 rounded-full animate-pulse">
                            {unreadNotifications}
                          </span>
                        )}
                      </h3>
                    </div>
                    
                    {/* Enhanced Controls */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {/* Filter Dropdown */}
                        <select
                          value={notificationFilter}
                          onChange={(e) => setNotificationFilter(e.target.value)}
                          className="text-xs bg-transparent border border-white/20 rounded-lg px-2 py-1 text-gray-600 dark:text-white/80 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="all">All</option>
                          <option value="unread">Unread</option>
                          <option value="read">Read</option>
                        </select>
                        
                        {/* Sound Toggle */}
                        <button
                          onClick={() => {
                            const newSoundEnabled = !soundEnabled;
                            setSoundEnabled(newSoundEnabled);
                            localStorage.setItem('cataloro_notification_sound', newSoundEnabled.toString());
                          }}
                          className="p-1 text-gray-600 dark:text-white/80 hover:text-gray-800 dark:hover:text-white transition-colors"
                          title={soundEnabled ? 'Disable sound' : 'Enable sound'}
                        >
                          {soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                        </button>
                        
                        {/* Refresh Button */}
                        <button 
                          onClick={() => loadNotifications()}
                          className="p-1 text-gray-600 dark:text-white/80 hover:text-gray-800 dark:hover:text-white transition-colors"
                          title="Refresh notifications"
                        >
                          <RefreshCw className="w-4 h-4" />
                        </button>
                      </div>
                      
                      {/* Quick Actions */}
                      <div className="flex items-center space-x-2">
                        {unreadNotifications > 0 && (
                          <button 
                            onClick={markAllNotificationsAsRead}
                            className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 font-medium transition-colors"
                          >
                            Mark all read
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Scrollable Notifications List */}
                  <div className="max-h-80 overflow-y-auto custom-scrollbar">
                    {getFilteredNotifications().length === 0 ? (
                      <div className="px-6 py-8 text-center">
                        <div className="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-3">
                          <Bell className="w-8 h-8 text-gray-400" />
                        </div>
                        <p className="text-gray-600 dark:text-gray-400 font-medium">
                          {notificationFilter === 'all' ? 'No notifications yet' : 
                           notificationFilter === 'unread' ? 'No unread notifications' : 
                           'No read notifications'}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                          We'll notify you when something important happens
                        </p>
                      </div>
                    ) : (
                      getFilteredNotifications().map((notification, index) => (
                        <div
                          key={notification.id}
                          data-notification-id={notification.id}
                          className={`group px-6 py-4 hover:bg-white/5 dark:hover:bg-white/5 cursor-pointer border-l-4 transition-all duration-300 ${
                            !notification.is_read ? 'bg-blue-50/30 dark:bg-blue-900/30' : ''
                          } ${index === 0 ? 'animate-in' : ''}`}
                          style={{
                            borderColor: notification.type === 'message' ? '#667eea' :
                                      notification.type === 'favorite' ? '#f093fb' :
                                      notification.type === 'payment' ? '#43e97b' :
                                      notification.type === 'buy_request' ? '#fbbf24' :
                                      notification.type === 'buy_approved' ? '#10b981' :
                                      notification.type === 'buy_rejected' ? '#ef4444' : '#9ca3af',
                            animationDelay: `${index * 0.1}s`
                          }}
                        >
                          <div className="flex items-start space-x-3">
                            {/* Enhanced Icon */}
                            <div className={`p-2 rounded-full ${
                              notification.type === 'message' ? 'bg-blue-100 text-blue-600' :
                              notification.type === 'favorite' ? 'bg-pink-100 text-pink-600' :
                              notification.type === 'payment' ? 'bg-green-100 text-green-600' :
                              notification.type === 'buy_request' ? 'bg-yellow-100 text-yellow-600' :
                              notification.type === 'buy_approved' ? 'bg-green-100 text-green-600' :
                              notification.type === 'buy_rejected' ? 'bg-red-100 text-red-600' :
                              'bg-gray-100 text-gray-600'
                            } ${!notification.is_read ? 'animate-pulse' : ''}`}>
                              {notification.type === 'message' ? <MessageCircle className="w-4 h-4" /> :
                               notification.type === 'favorite' ? <Heart className="w-4 h-4" /> :
                               notification.type === 'payment' ? <DollarSign className="w-4 h-4" /> :
                               notification.type === 'buy_request' ? <ShoppingCart className="w-4 h-4" /> :
                               notification.type === 'buy_approved' ? <Check className="w-4 h-4" /> :
                               notification.type === 'buy_rejected' ? <X className="w-4 h-4" /> :
                               <Bell className="w-4 h-4" />}
                            </div>
                            
                            {/* Enhanced Content */}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-start justify-between">
                                <p className={`text-sm font-semibold ${!notification.is_read ? 'text-gray-900 dark:text-white' : 'text-gray-700 dark:text-gray-300'}`}>
                                  {notification.title}
                                </p>
                                <div className="flex items-center space-x-1 ml-2">
                                  {!notification.is_read && (
                                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                                  )}
                                  {/* Delete Button */}
                                  <button
                                    onClick={(e) => deleteNotification(notification.id, e)}
                                    className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-600 transition-all duration-200"
                                    title="Delete notification"
                                  >
                                    <Trash2 className="w-3 h-3" />
                                  </button>
                                </div>
                              </div>
                              <p className="text-xs text-gray-600 dark:text-white/70 mt-1 line-clamp-2">
                                {notification.message}
                              </p>
                              <div className="flex items-center justify-between mt-2">
                                <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                                  <Clock className="w-3 h-3 mr-1" />
                                  {new Date(notification.created_at).toLocaleString()}
                                </div>
                                
                                {/* Quick Action Icon Buttons */}
                                <div className="flex items-center space-x-1">
                                  {!notification.is_read && (
                                    <button
                                      onClick={(e) => handleMarkAsRead(notification.id, e)}
                                      className="p-1.5 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-md hover:bg-blue-200 dark:hover:bg-blue-900/70 transition-all duration-200 hover:scale-110 group/tooltip relative"
                                      title="Mark as read & auto-delete"
                                    >
                                      <CheckCheck className="w-3.5 h-3.5" />
                                      {/* Tooltip */}
                                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 dark:bg-gray-700 text-white text-xs rounded-md opacity-0 group-hover/tooltip:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                                        Mark as read & auto-delete
                                        <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-2 border-transparent border-t-gray-900 dark:border-t-gray-700"></div>
                                      </div>
                                    </button>
                                  )}
                                  
                                  {/* Enhanced Quick Actions for Different Types */}
                                  {notification.type === 'buy_request' && (
                                    <>
                                      <button
                                        onClick={(e) => handleAcceptRequest(notification.id, e)}
                                        className="p-1.5 bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300 rounded-md hover:bg-green-200 dark:hover:bg-green-900/70 transition-all duration-200 hover:scale-110 group/tooltip relative"
                                        title="Accept request & auto-delete"
                                      >
                                        <Check className="w-3.5 h-3.5" />
                                        {/* Tooltip */}
                                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 dark:bg-gray-700 text-white text-xs rounded-md opacity-0 group-hover/tooltip:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                                          Accept request & auto-delete
                                          <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-2 border-transparent border-t-gray-900 dark:border-t-gray-700"></div>
                                        </div>
                                      </button>
                                      <button 
                                        onClick={(e) => handleDeclineRequest(notification.id, e)}
                                        className="p-1.5 bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 rounded-md hover:bg-red-200 dark:hover:bg-red-900/70 transition-all duration-200 hover:scale-110 group/tooltip relative"
                                        title="Decline request & auto-delete"
                                      >
                                        <X className="w-3.5 h-3.5" />
                                        {/* Tooltip */}
                                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 dark:bg-gray-700 text-white text-xs rounded-md opacity-0 group-hover/tooltip:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                                          Decline request & auto-delete
                                          <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-2 border-transparent border-t-gray-900 dark:border-t-gray-700"></div>
                                        </div>
                                      </button>
                                    </>
                                  )}
                                  
                                  {notification.type === 'message' && (
                                    <button
                                      onClick={(e) => handleReplyToMessage(notification.id, e)}
                                      className="p-1.5 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-md hover:bg-blue-200 dark:hover:bg-blue-900/70 transition-all duration-200 hover:scale-110 group/tooltip relative"
                                      title="Reply to message & auto-delete"
                                    >
                                      <MessageCircle className="w-3.5 h-3.5" />
                                      {/* Tooltip */}
                                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 dark:bg-gray-700 text-white text-xs rounded-md opacity-0 group-hover/tooltip:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                                        Reply to message & auto-delete
                                        <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-2 border-transparent border-t-gray-900 dark:border-t-gray-700"></div>
                                      </div>
                                    </button>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                  
                  {/* Enhanced Footer */}
                  <div className="px-6 py-3 border-t border-white/10">
                    <div className="flex items-center justify-between">
                      <Link
                        to="/notifications"
                        className="text-sm text-gray-600 dark:text-white/80 hover:text-gray-800 dark:hover:text-white font-medium flex items-center transition-colors"
                        onClick={() => setShowNotifications(false)}
                      >
                        View all notifications
                        <TrendingUp className="w-4 h-4 ml-1" />
                      </Link>
                      
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {getFilteredNotifications().length} notification{getFilteredNotifications().length !== 1 ? 's' : ''}
                      </div>
                    </div>
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
                    
                    <Link
                      to={`/profile/${user?.id}`}
                      className="flex items-center px-6 py-3 text-sm text-gray-700 dark:text-white/90 hover:text-gray-900 dark:hover:text-white hover:bg-white/5 dark:hover:bg-white/5 transition-all duration-300 group"
                      onClick={() => setShowUserMenu(false)}
                    >
                      <div className="p-2 rounded-lg mr-3 group-hover:bg-white/10 transition-all duration-300" style={{
                        background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(147, 197, 253, 0.1))'
                      }}>
                        <Globe className="w-4 h-4" />
                      </div>
                      <span className="font-medium">View Public Profile</span>
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