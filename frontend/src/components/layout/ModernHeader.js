/**
 * CATALORO - Ultra-Modern Header Navigation
 * Sleek header with comprehensive navigation and enhanced notifications
 */

import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Bell, 
  User, 
  Heart,
  MessageCircle,
  Settings,
  LogOut,
  Package,
  Moon,
  Sun,
  Menu,
  X,
  Store,
  BarChart3,
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
  Globe,
  Plus,
  ShoppingCart,
  HelpCircle, Mail, FileText, Home, Camera,
  Calendar, Download, Upload, Edit, EyeOff, Lock,
  Unlock, Key, Users, UserPlus, Phone, Smartphone, Monitor, Tablet,
  Laptop, Activity, Award, Target, Compass, Map, Navigation,
  Bookmark, Tag, SortAsc, Grid, Layers, Archive, Folder,
  File, Image, Video, Music, Headphones, Mic, Play, Pause,
  Square, SkipBack, SkipForward, Repeat, Shuffle, Share, ExternalLink,
  Link as LinkIcon, Copy, AlertTriangle, AlertCircle, Info, CheckCircle
} from 'lucide-react';
import { APP_ROUTES } from '../../config/directions';
import { useAuth } from '../../context/AuthContext';
import { useMarketplace } from '../../context/MarketplaceContext';
import { useNotifications } from '../../context/NotificationContext';
import { liveService } from '../../services/liveService';
import usePermissions from '../../hooks/usePermissions';
import { useMenuSettings } from '../../hooks/useMenuSettings';

function ModernHeader({ darkMode, toggleDarkMode, isMobileMenuOpen, setIsMobileMenuOpen }) {
  const { user, logout } = useAuth();
  const { favoriteCount } = useMarketplace();
  const { showToast } = useNotifications();
  const { permissions, isAdmin, isSeller, isBuyer, isAdminLevel, getUserDisplay } = usePermissions();
  const { isMenuItemVisible } = useMenuSettings();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showTendersMenu, setShowTendersMenu] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadNotifications, setUnreadNotifications] = useState(0);
  const [unreadMessages, setUnreadMessages] = useState(0);
  const [sessionReadMessageIds, setSessionReadMessageIds] = useState(new Set()); // Moved to component level
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
  // Load notifications from backend with enhanced features and rate limit handling
  const loadNotifications = async (showNewNotificationAlert = false) => {
    if (!user?.id) return;
    
    try {
      const userNotifications = await liveService.getUserNotifications(user.id);
      const userMessages = await liveService.getUserMessages(user.id);
      
      // Ensure we have arrays to work with
      const notificationsArray = Array.isArray(userNotifications) ? userNotifications : [];
      const messagesArray = Array.isArray(userMessages) ? userMessages : [];
      
      // Check for new notifications since last check
      if (showNewNotificationAlert && notifications.length > 0) {
        const newNotifications = notificationsArray.filter(n => 
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
      
      setNotifications(notificationsArray);
      setUnreadNotifications(notificationsArray.filter(n => !n.is_read).length);
      setUnreadMessages(messagesArray.filter(m => !m.is_read && m.sender_id !== user.id).length);
      setLastNotificationCheck(Date.now());
    } catch (error) {
      console.error('Failed to load notifications:', error);
      
      // Handle rate limiting specifically
      if (error.message?.includes('429') || error.status === 429) {
        console.warn('⚠️ Rate limit detected - backing off notifications polling');
        // Don't reset data on rate limit, just log the warning
        return;
      }
      
      // Use empty array as fallback for other errors
      setNotifications([]);
      setUnreadNotifications(0);
      setUnreadMessages(0);
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
      // Disabled automatic notification permission request to avoid browser errors
      // requestNotificationPermission(); // Only request on user interaction
      
      // Set up real-time notification polling every 5 minutes (reduced from 2 minutes to prevent rate limiting)
      const notificationInterval = setInterval(() => {
        loadNotifications(true);
      }, 300000); // 5 minutes instead of 2 minutes
      
      // Listen for custom events when messages are marked as read
      const handleMessagesMarkedAsRead = (event) => {
        console.log('📧 ModernHeader received messagesMarkedAsRead event with detail:', event.detail);
        const messageIds = event.detail?.messageIds || [];
        const count = event.detail?.count || 0;
        
        console.log(`🔢 Reducing unread message count by ${count} (current: ${unreadMessages})`);
        
        // Update session read message tracking
        setSessionReadMessageIds(prev => {
          const updated = new Set(prev);
          messageIds.forEach(id => updated.add(id));
          console.log('📝 Updated session read message IDs:', Array.from(updated));
          return updated;
        });
        
        // Immediately reduce unread count by the number of messages marked as read
        setUnreadMessages(prev => {
          const newCount = Math.max(0, prev - count);
          console.log(`📊 Updated unread messages count: ${prev} → ${newCount}`);
          return newCount;
        });
        
        // Also refresh from server to sync
        console.log('🔄 Triggering loadNotifications to sync with server');
        loadNotifications(true);
      };
      
      const handleMessagesSessionReset = () => {
        console.log('🔄 Messages session reset - restoring original unread counts');
        setSessionReadMessageIds(new Set());
        // Reload notifications to get true unread count from server
        loadNotifications(true);
      };
      
      window.addEventListener('messagesMarkedAsRead', handleMessagesMarkedAsRead);
      window.addEventListener('messagesSessionReset', handleMessagesSessionReset);
      
      return () => {
        clearInterval(notificationInterval);
        window.removeEventListener('messagesMarkedAsRead', handleMessagesMarkedAsRead);
        window.removeEventListener('messagesSessionReset', handleMessagesSessionReset);
      };
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
      if (showTendersMenu && !event.target.closest('.tenders-dropdown')) {
        setShowTendersMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showUserMenu, showNotifications, showTendersMenu]);

  // Smart notification click handler
  const handleNotificationClick = async (notification) => {
    try {
      // Mark notification as read first
      await markNotificationAsRead(notification.id);
      
      // Close notifications dropdown
      setShowNotifications(false);
      
      // Navigate based on notification type
      switch (notification.type) {
        case 'tender_accepted':
          // Navigate to Buy > Bought Items tab
          navigate('/buy?tab=bought-items');
          break;
          
        case 'tender_offer':
        case 'new_tender_offer':
          // Navigate to Sell > Sell Tenders tab
          navigate('/sell?tab=tenders');
          if (notification.listing_id) {
            // Add listing parameter if available
            setTimeout(() => {
              const urlParams = new URLSearchParams(window.location.search);
              urlParams.set('listing', notification.listing_id);
              navigate('/sell?tab=tenders&' + urlParams.toString(), { replace: true });
            }, 100);
          }
          break;
          
        case 'tender_rejected':
          // Navigate to Buy > Items (keeping existing behavior but with new Buy page structure)
          navigate('/buy?tab=tenders');
          break;
          
        case 'order_completed':
        case 'transaction_completed':
        case 'transaction_marked_completed':
          // Navigate to Buy > Bought Items
          navigate('/buy?tab=bought-items');
          break;
          
        case 'transaction_fully_completed':
        case 'order_fully_completed':
          // Navigate to Buy > Completed
          navigate('/buy?tab=completed');
          break;
          
        case 'order_shipped':
        case 'listing_sold':
          // Navigate to My Listings page with Closed filter (keep existing for seller notifications)
          navigate('/my-listings');
          setTimeout(() => {
            const urlParams = new URLSearchParams();
            urlParams.set('filter', 'closed');
            navigate('/my-listings?' + urlParams.toString(), { replace: true });
          }, 100);
          break;
          
        case 'message':
        case 'new_message':
          // Navigate to Messages page (keep existing)
          if (notification.message_id) {
            navigate(`/messages?id=${notification.message_id}`);
          } else {
            navigate('/messages');
          }
          break;
          
        case 'buy_request':
        case 'purchase_request':
          // Navigate to My Listings page with Active filter (keep existing)
          navigate('/my-listings');
          setTimeout(() => {
            const urlParams = new URLSearchParams();
            urlParams.set('filter', 'active');
            navigate('/my-listings?' + urlParams.toString(), { replace: true });
          }, 100);
          break;
          
        case 'buy_approved':
        case 'purchase_approved':
          // Navigate to deals page instead of cart (keep existing)
          navigate('/deals');
          break;
          
        case 'buy_rejected':
        case 'purchase_rejected':
          // Navigate to browse page to find alternatives (keep existing)
          navigate('/browse');
          break;
          
        case 'favorite':
        case 'wishlist_update':
          // Navigate to favorites page (keep existing)
          navigate('/favorites');
          break;
          
        case 'listing_approved':
        case 'listing_updated':
          // Navigate to My Listings (keep existing)
          navigate('/my-listings');
          break;
          
        case 'profile_update':
        case 'account_update':
          // Navigate to profile settings (keep existing)
          navigate('/profile');
          break;
          
        case 'new_user_registration':
        case 'user_registration':
          // For ADMIN users: Navigate to Admin Panel > Users tab
          if (user?.role === 'admin' || user?.is_admin) {
            navigate('/admin?tab=users');
          } else {
            // For non-admin users, go to notifications center
            navigate('/notifications');
          }
          break;
          
        case 'system':
        case 'announcement':
          // Navigate to notifications center for full details (keep existing)
          navigate('/notifications');
          break;
          
        default:
          // For unknown notification types, go to notifications center (keep existing)
          navigate('/notifications');
          break;
      }
      
      showToast(`Navigating to ${notification.title}`, 'info');
      
    } catch (error) {
      console.error('Error handling notification click:', error);
      showToast('Error navigating from notification', 'error');
    }
  };
  
  // Handle logout functionality
  const handleLogout = () => {
    logout();
    navigate('/login');
    showToast('Logged out successfully', 'success');
  };

  const isActive = (path) => location.pathname === path;

  // Icon mapping for custom menu items
  const iconMap = {
    Store, Plus, MessageCircle, DollarSign, ShoppingCart, Heart, Bell, User,
    Settings, LogOut, Package, Shield, Menu, X, Sun, Moon, Globe,
    BarChart3, TrendingUp, HelpCircle, Mail, FileText, Home, Star, Camera,
    Calendar, Clock, Download, Upload, Edit, Trash2, Eye, EyeOff, Lock,
    Unlock, Key, Users, UserPlus, Phone, Smartphone, Monitor, Tablet,
    Laptop, Zap, Activity, Award, Target, Compass, Map, Navigation,
    Bookmark, Tag, Filter, SortAsc, List, Grid, Layers, Archive, Folder,
    File, Image, Video, Music, Headphones, Mic, Volume2, Play, Pause,
    Square, SkipBack, SkipForward, Repeat, Shuffle, Share, ExternalLink,
    LinkIcon, Copy, Check, AlertTriangle, AlertCircle, Info, CheckCircle
  };

  // Define navigation items for the main nav (excluding items that have dedicated sections)
  const allNavigationItems = [
    { label: 'About', path: '/info', icon: Globe, key: 'about' },
    { label: 'Browse', path: '/browse', icon: Store, key: 'browse' },
    { label: 'Buy', path: '/buy', icon: ShoppingCart, key: 'buy' },
    { label: 'Sell', path: '/sell', icon: Package, key: 'sell' },
    { label: 'Notifications', path: '/notifications', icon: Bell, key: 'notifications' },
  ];

  // Filter navigation items based on menu visibility settings
  const navigationItems = allNavigationItems.filter(item => 
    isMenuItemVisible('desktop_menu', item.key)
  );

  // Get custom menu items - these should appear first by default
  const { getCustomMenuItems } = useMenuSettings();
  const customMenuItems = getCustomMenuItems('desktop_menu');

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
              {/* Custom Menu Items - Render First */}
              {customMenuItems.map((item) => {
                const isActive = location.pathname === item.url;
                const isExternal = item.url.startsWith('http');
                const IconComponent = iconMap[item.icon] || Star; // Default to Star if icon not found
                
                return isExternal ? (
                  <a
                    key={item.id}
                    href={item.url}
                    target={item.target || '_self'}
                    rel={item.target === '_blank' ? 'noopener noreferrer' : undefined}
                    className="flex items-center space-x-2 px-4 py-2 rounded-xl transition-all duration-300 font-medium text-sm text-gray-700 dark:text-white/80 hover:text-gray-900 dark:hover:text-white hover:bg-white/10 dark:hover:bg-white/10"
                  >
                    <IconComponent className="w-4 h-4" />
                    <span className="font-medium">{item.label}</span>
                    {item.target === '_blank' && <span className="text-xs opacity-60">↗</span>}
                  </a>
                ) : (
                  <Link
                    key={item.id}
                    to={item.url}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-all duration-300 font-medium text-sm ${
                      isActive
                        ? 'bg-gray-300/30 dark:bg-gray-500/30 text-gray-800 dark:text-white shadow-lg backdrop-blur-md border border-gray-300 dark:border-gray-500/30'
                        : 'text-gray-700 dark:text-white/80 hover:text-gray-900 dark:hover:text-white hover:bg-white/10 dark:hover:bg-white/10'
                    }`}
                    style={isActive ? (darkMode ? {
                      background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%)',
                      backdropFilter: 'blur(20px)',
                      boxShadow: '0 4px 15px rgba(255, 255, 255, 0.1)'
                    } : {
                      background: 'linear-gradient(135deg, rgba(156, 163, 175, 0.25) 0%, rgba(156, 163, 175, 0.15) 100%)',
                      backdropFilter: 'blur(20px)',
                      boxShadow: '0 4px 15px rgba(156, 163, 175, 0.2)'
                    }) : {}}
                  >
                    <IconComponent className="w-4 h-4" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}

              {/* Default Navigation Items - Render After Custom Items */}
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-all duration-300 font-medium text-sm ${
                      isActive
                        ? 'bg-gray-300/30 dark:bg-gray-500/30 text-gray-800 dark:text-white shadow-lg backdrop-blur-md border border-gray-300 dark:border-gray-500/30'
                        : 'text-gray-700 dark:text-white/80 hover:text-gray-900 dark:hover:text-white hover:bg-white/10 dark:hover:bg-white/10'
                    }`}
                    style={isActive ? (darkMode ? {
                      background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%)',
                      backdropFilter: 'blur(20px)',
                      boxShadow: '0 4px 15px rgba(255, 255, 255, 0.1)'
                    } : {
                      background: 'linear-gradient(135deg, rgba(156, 163, 175, 0.25) 0%, rgba(156, 163, 175, 0.15) 100%)',
                      backdropFilter: 'blur(20px)',
                      boxShadow: '0 4px 15px rgba(156, 163, 175, 0.2)'
                    }) : {}}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}
              
              {/* Buy and Sell links removed from sidebar - they are now in main navigation */}
              
              {/* Admin Link - Menu settings visibility */}
              {isMenuItemVisible('desktop_menu', 'admin_panel') && (
                <Link
                  to="/admin"
                  className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-all duration-300 font-medium text-sm shadow-lg backdrop-blur-md ${
                    isAdminLevel() ? 'text-gray-900 dark:text-gray-900' : 'text-gray-700 dark:text-white/80'
                  }`}
                  style={{
                    background: location.pathname === '/admin' 
                      ? (isAdmin() 
                          ? 'linear-gradient(135deg, rgba(255, 193, 7, 0.9) 0%, rgba(255, 152, 0, 0.8) 100%)'
                          : 'linear-gradient(135deg, rgba(147, 51, 234, 0.8) 0%, rgba(79, 70, 229, 0.7) 100%)')
                      : (isAdmin()
                          ? 'linear-gradient(135deg, rgba(255, 193, 7, 0.7) 0%, rgba(255, 152, 0, 0.6) 100%)'
                          : 'linear-gradient(135deg, rgba(147, 51, 234, 0.6) 0%, rgba(79, 70, 229, 0.5) 100%)'),
                    backdropFilter: 'blur(20px)',
                    boxShadow: isAdmin() 
                      ? '0 4px 15px rgba(255, 193, 7, 0.3)'
                      : '0 4px 15px rgba(147, 51, 234, 0.3)',
                    border: isAdmin() 
                      ? '1px solid rgba(255, 193, 7, 0.4)'
                      : '1px solid rgba(147, 51, 234, 0.4)'
                  }}
                >
                  <Shield className="w-4 h-4" />
                  <span className="font-medium">{isAdmin() ? 'Admin' : 'Manager'}</span>
                </Link>
              )}
            </nav>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            
            {/* Quick Actions (Desktop) */}
            <div className="hidden lg:flex items-center space-x-2">
              {/* Messages */}
              {isMenuItemVisible('desktop_menu', 'messages') && (
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
              )}

              {/* Favorites */}
              {isMenuItemVisible('desktop_menu', 'favorites') && (
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
              )}

              {/* Create Listing Button (replaced shopping cart) */}
              {isMenuItemVisible('desktop_menu', 'create_listing') && (
                <Link
                  to="/create-listing"
                  className="relative p-3 text-gray-700 dark:text-white/80 hover:text-gray-900 dark:hover:text-white transition-all duration-300 group"
                style={{
                  background: darkMode 
                    ? 'linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(34, 197, 94, 0.1) 100%)'
                    : 'linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(34, 197, 94, 0.05) 100%)',
                  backdropFilter: 'blur(20px)',
                  borderRadius: '16px',
                  border: darkMode 
                    ? '1px solid rgba(34, 197, 94, 0.2)'
                    : '1px solid rgba(34, 197, 94, 0.15)'
                }}
                title="Create New Listing"
              >
                <Plus className="w-5 h-5 text-green-600 dark:text-green-400" />
              </Link>
              )}
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

              {/* Enhanced Notifications Dropdown - Redesigned for Better Width Management */}
              {showNotifications && (
                <div className="absolute right-0 mt-3 w-80 max-w-[90vw] rounded-2xl shadow-2xl py-3 z-50 notifications-dropdown-enhanced animate-in" style={{
                  background: darkMode 
                    ? 'rgba(0, 0, 0, 0.95)'
                    : 'rgba(255, 255, 255, 0.95)',
                  backdropFilter: 'blur(25px)',
                  border: darkMode 
                    ? '1px solid rgba(255, 255, 255, 0.2)' 
                    : '1px solid rgba(0, 0, 0, 0.2)',
                  animation: 'slideDown 0.3s ease-out'
                }}>
                  {/* Compact Header with Controls */}
                  <div className="px-4 py-3 border-b border-white/10">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-bold text-gray-900 dark:text-white text-base flex items-center">
                        <Bell className="w-4 h-4 mr-2" />
                        Notifications
                        {unreadNotifications > 0 && (
                          <span className="ml-2 bg-red-500 text-white text-xs px-1.5 py-0.5 rounded-full">
                            {unreadNotifications}
                          </span>
                        )}
                      </h3>
                    </div>
                    
                    {/* Compact Controls */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-1.5">
                        {/* Compact Filter Dropdown */}
                        <select
                          value={notificationFilter}
                          onChange={(e) => setNotificationFilter(e.target.value)}
                          className="text-xs bg-transparent border border-white/20 rounded-md px-1.5 py-1 text-gray-600 dark:text-white/80 focus:outline-none focus:ring-1 focus:ring-blue-500 min-w-0 w-16"
                        >
                          <option value="all">All</option>
                          <option value="unread">New</option>
                          <option value="read">Read</option>
                        </select>
                        
                        {/* Compact Action Buttons */}
                        <button
                          onClick={() => {
                            const newSoundEnabled = !soundEnabled;
                            setSoundEnabled(newSoundEnabled);
                            localStorage.setItem('cataloro_notification_sound', newSoundEnabled.toString());
                          }}
                          className="p-1 text-gray-600 dark:text-white/80 hover:text-gray-800 dark:hover:text-white transition-colors"
                          title={soundEnabled ? 'Disable sound' : 'Enable sound'}
                        >
                          {soundEnabled ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
                        </button>
                        
                        <button 
                          onClick={() => loadNotifications()}
                          className="p-1 text-gray-600 dark:text-white/80 hover:text-gray-800 dark:hover:text-white transition-colors"
                          title="Refresh"
                        >
                          <RefreshCw className="w-3.5 h-3.5" />
                        </button>
                      </div>
                      
                      {/* Quick Actions */}
                      <div className="flex items-center">
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
                      <div className="px-4 py-6 text-center">
                        <div className="w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-3">
                          <Bell className="w-6 h-6 text-gray-400" />
                        </div>
                        <p className="text-gray-600 dark:text-gray-400 font-medium text-sm">
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
                          onClick={() => handleNotificationClick(notification)}
                          className={`group px-4 py-3 hover:bg-white/5 dark:hover:bg-white/5 cursor-pointer border-l-3 transition-all duration-300 ${
                            !notification.is_read ? 'bg-blue-50/30 dark:bg-blue-900/30' : ''
                          } ${index === 0 ? 'animate-in' : ''}`}
                          style={{
                            borderColor: notification.type === 'message' ? '#667eea' :
                                      notification.type === 'favorite' ? '#f093fb' :
                                      notification.type === 'payment' ? '#43e97b' :
                                      notification.type === 'buy_request' ? '#fbbf24' :
                                      notification.type === 'buy_approved' ? '#10b981' :
                                      notification.type === 'buy_rejected' ? '#ef4444' :
                                      notification.type === 'tender_accepted' ? '#10b981' :
                                      notification.type === 'tender_offer' ? '#f59e0b' :
                                      notification.type === 'tender_rejected' ? '#ef4444' :
                                      notification.type === 'new_tender_offer' ? '#f59e0b' :
                                      notification.type === 'order_completed' ? '#10b981' : '#9ca3af',
                            animationDelay: `${index * 0.1}s`
                          }}
                        >
                          <div className="flex items-start space-x-2.5">
                            {/* Compact Icon */}
                            <div className={`p-1.5 rounded-full flex-shrink-0 ${
                              notification.type === 'message' ? 'bg-blue-100 text-blue-600' :
                              notification.type === 'favorite' ? 'bg-pink-100 text-pink-600' :
                              notification.type === 'payment' ? 'bg-green-100 text-green-600' :
                              notification.type === 'buy_request' ? 'bg-yellow-100 text-yellow-600' :
                              notification.type === 'buy_approved' ? 'bg-green-100 text-green-600' :
                              notification.type === 'buy_rejected' ? 'bg-red-100 text-red-600' :
                              'bg-gray-100 text-gray-600'
                            }`}>
                              {notification.type === 'message' ? <MessageCircle className="w-3.5 h-3.5" /> :
                               notification.type === 'favorite' ? <Heart className="w-3.5 h-3.5" /> :
                               notification.type === 'payment' ? <DollarSign className="w-3.5 h-3.5" /> :
                               notification.type === 'buy_request' ? <Package className="w-3.5 h-3.5" /> :
                               notification.type === 'buy_approved' ? <Check className="w-3.5 h-3.5" /> :
                               notification.type === 'buy_rejected' ? <X className="w-3.5 h-3.5" /> :
                               <Bell className="w-3.5 h-3.5" />}
                            </div>
                            
                            {/* Compact Content */}
                            <div className="flex-1 min-w-0 overflow-hidden">
                              <div className="flex items-start justify-between">
                                <div className="flex-1 min-w-0 pr-2">
                                  <p className={`text-sm font-semibold truncate ${!notification.is_read ? 'text-gray-900 dark:text-white' : 'text-gray-700 dark:text-gray-300'}`}>
                                    {notification.title}
                                  </p>
                                  <p className="text-xs text-gray-600 dark:text-white/70 mt-0.5 line-clamp-2 leading-tight">
                                    {notification.message}
                                  </p>
                                </div>
                                <div className="flex items-center space-x-1 flex-shrink-0">
                                  {!notification.is_read && (
                                    <div className="w-1.5 h-1.5 bg-blue-600 rounded-full"></div>
                                  )}
                                  {/* Compact Delete Button */}
                                  <button
                                    onClick={(e) => deleteNotification(notification.id, e)}
                                    className="opacity-0 group-hover:opacity-100 p-0.5 text-gray-400 hover:text-red-600 transition-all duration-200"
                                    title="Delete"
                                  >
                                    <Trash2 className="w-3 h-3" />
                                  </button>
                                </div>
                              </div>
                              
                              {/* Compact Footer with Time and Actions */}
                              <div className="flex items-center justify-between mt-2">
                                <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                                  <Clock className="w-3 h-3 mr-1" />
                                  <span className="truncate">
                                    {new Date(notification.created_at).toLocaleDateString()} {new Date(notification.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                  </span>
                                </div>
                                
                                {/* Compact Action Buttons */}
                                <div className="flex items-center space-x-1 flex-shrink-0">
                                  {!notification.is_read && (
                                    <button
                                      onClick={(e) => handleMarkAsRead(notification.id, e)}
                                      className="p-1 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-900/70 transition-all duration-200"
                                      title="Mark read"
                                    >
                                      <CheckCheck className="w-3 h-3" />
                                    </button>
                                  )}
                                  
                                  {/* Quick Actions for Different Types */}
                                  {notification.type === 'buy_request' && (
                                    <>
                                      <button
                                        onClick={(e) => handleAcceptRequest(notification.id, e)}
                                        className="p-1 bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300 rounded hover:bg-green-200 dark:hover:bg-green-900/70 transition-all duration-200"
                                        title="Accept"
                                      >
                                        <Check className="w-3 h-3" />
                                      </button>
                                      <button 
                                        onClick={(e) => handleDeclineRequest(notification.id, e)}
                                        className="p-1 bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 rounded hover:bg-red-200 dark:hover:bg-red-900/70 transition-all duration-200"
                                        title="Decline"
                                      >
                                        <X className="w-3 h-3" />
                                      </button>
                                    </>
                                  )}
                                  
                                  {notification.type === 'message' && (
                                    <button
                                      onClick={(e) => handleReplyToMessage(notification.id, e)}
                                      className="p-1 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-900/70 transition-all duration-200"
                                      title="Reply"
                                    >
                                      <MessageCircle className="w-3 h-3" />
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
                  
                  {/* Compact Footer */}
                  <div className="px-4 py-2 border-t border-white/10">
                    <div className="flex items-center justify-between">
                      <Link
                        to="/notifications"
                        className="text-xs text-gray-600 dark:text-white/80 hover:text-gray-800 dark:hover:text-white font-medium flex items-center transition-colors"
                        onClick={() => setShowNotifications(false)}
                      >
                        View all notifications
                        <TrendingUp className="w-3 h-3 ml-1" />
                      </Link>
                      
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {getFilteredNotifications().length} total
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
                    {user?.username || user?.full_name || 'User'}
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
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-base font-bold text-gray-900 dark:text-white">
                          {user?.username || user?.full_name}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-white/70">{user?.email}</p>
                      </div>
                      {/* Role Badge - Clean single display */}
                      <div className="flex flex-col items-end">
                        <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${
                          getUserDisplay().badge === 'Admin' 
                            ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                            : getUserDisplay().badge === 'Manager'
                            ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300'
                            : getUserDisplay().badge === 'Seller'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                            : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                        }`}>
                          {getUserDisplay().badge}
                        </span>
                      </div>
                    </div>
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
                    
                    {/* My Listings - Only for sellers and admins */}
                    {permissions.selling.canManageListings && (
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
                    )}
                    
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
                    
                    {/* Admin Panel - Role-based access */}
                    {permissions.ui.showAdminPanelLink && isMenuItemVisible('desktop_menu', 'admin_panel') && (
                      <Link
                        to="/admin"
                        className="flex items-center px-6 py-3 text-sm text-gray-700 dark:text-white/90 hover:text-gray-900 dark:hover:text-white hover:bg-white/5 dark:hover:bg-white/5 transition-all duration-300 group"
                        onClick={() => setShowUserMenu(false)}
                      >
                        <div className="p-2 rounded-lg mr-3 group-hover:bg-white/10 transition-all duration-300" style={{
                          background: isAdmin()
                            ? 'linear-gradient(135deg, rgba(250, 112, 154, 0.2), rgba(254, 225, 64, 0.1))'
                            : 'linear-gradient(135deg, rgba(147, 51, 234, 0.2), rgba(79, 70, 229, 0.1))'
                        }}>
                          <Shield className="w-4 h-4" />
                        </div>
                        <span className="font-medium">{isAdmin() ? 'Admin Panel' : 'Manager Panel'}</span>
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