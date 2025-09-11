/**
 * CATALORO - Mobile Bottom Navigation (Hybrid Navigation System)
 * Core mobile navigation with primary features - Part of hybrid approach
 */

import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Store, 
  Plus, 
  ShoppingCart, 
  Heart, 
  User,
  Search,
  MessageCircle,
  DollarSign,
  Package
} from 'lucide-react';
import { liveService } from '../../services/liveService';
import { useMenuSettings } from '../../hooks/useMenuSettings';

function MobileBottomNav() {
  const [user, setUser] = useState(null);
  const [cartCount, setCartCount] = useState(0);
  const [favoritesCount, setFavoritesCount] = useState(0);
  const [unreadMessages, setUnreadMessages] = useState(0);
  const { isMenuItemVisible } = useMenuSettings();
  const location = useLocation();

  useEffect(() => {
    const loadRealData = async () => {
      // Load user data
      const userData = localStorage.getItem('cataloro_user');
      if (userData) {
        try {
          const user = JSON.parse(userData);
          setUser(user);
          
          // Load real unread message count
          try {
            const messages = await liveService.getUserMessages(user.id);
            const unreadCount = messages.filter(msg => !msg.is_read && msg.recipient_id === user.id).length;
            setUnreadMessages(unreadCount);
            localStorage.setItem('cataloro_unread_messages', unreadCount.toString());
          } catch (error) {
            console.error('Error loading messages:', error);
            // Fallback to localStorage
            const savedMessages = localStorage.getItem('cataloro_unread_messages');
            if (savedMessages) {
              setUnreadMessages(parseInt(savedMessages, 10) || 0);
            }
          }

          // Load real unread notifications count
          try {
            const notifications = await liveService.getUserNotifications(user.id);
            const unreadNotificationsCount = notifications.filter(notif => !notif.is_read).length;
            setUnreadNotifications(unreadNotificationsCount);
            localStorage.setItem('cataloro_unread_notifications', unreadNotificationsCount.toString());
          } catch (error) {
            console.error('Error loading notifications:', error);
            // Fallback to localStorage
            const savedNotifications = localStorage.getItem('cataloro_unread_notifications');
            if (savedNotifications) {
              setUnreadNotifications(parseInt(savedNotifications, 10) || 0);
            }
          }
        } catch (error) {
          console.error('Error parsing user data:', error);
        }
      }

      // Load real cart count
      const savedCart = localStorage.getItem('cataloro_cart_count');
      if (savedCart) {
        setCartCount(parseInt(savedCart, 10) || 0);
      }
    };

    loadRealData();

    // Listen for real badge updates from the app
    const handleBadgeUpdate = (event) => {
      const { type, count } = event.detail;
      switch (type) {
        case 'messages':
          setUnreadMessages(count);
          localStorage.setItem('cataloro_unread_messages', count.toString());
          break;
        case 'notifications':
          setUnreadNotifications(count);
          localStorage.setItem('cataloro_unread_notifications', count.toString());
          break;
        case 'cart':
          setCartCount(count);
          localStorage.setItem('cataloro_cart_count', count.toString());
          break;
      }
    };

    window.addEventListener('updateMobileBadge', handleBadgeUpdate);

    return () => {
      window.removeEventListener('updateMobileBadge', handleBadgeUpdate);
    };
  }, []);

  const isActive = (path) => {
    if (path === '/browse' && location.pathname === '/') return true;
    return location.pathname === path;
  };

  const allBottomNavItems = [
    {
      label: 'Browse',
      path: '/browse',
      icon: Store,
      badge: null,
      key: 'browse'
    },
    {
      label: 'Messages',
      path: '/messages',
      icon: MessageCircle,
      badge: unreadMessages > 0 ? unreadMessages : null,
      key: 'messages'
    },
    {
      label: 'Notifications',
      path: '/notifications',
      icon: Bell,
      badge: unreadNotifications > 0 ? unreadNotifications : null,
      key: 'notifications'
    },
    {
      label: 'Create',
      path: '/create-listing',
      icon: Plus,
      badge: null,
      highlight: true, // Central create button
      key: 'create'
    },
    {
      label: 'Tenders',
      path: '/mobile-tenders',
      icon: DollarSign,
      badge: null,
      key: 'tenders'
    },
    {
      label: 'Listings',
      path: '/mobile-my-listings',
      icon: Package,
      badge: null,
      key: 'listings'
    }
  ];

  // Filter bottom nav items based on menu settings
  const bottomNavItems = allBottomNavItems.filter(item => 
    isMenuItemVisible('mobile_menu', item.key)
  );

  return (
    <>
      {/* Bottom Navigation Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 z-40 lg:hidden safe-area-pb">
        <div className="flex items-center justify-between px-2 py-2 max-w-md mx-auto">
          {bottomNavItems.map((item, index) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`relative flex flex-col items-center justify-center transition-all duration-200 touch-manipulation ${
                  item.highlight
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg rounded-2xl p-3 -mt-3 mx-2'
                    : active
                    ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 rounded-xl px-3 py-2'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 active:bg-gray-100 dark:active:bg-gray-800 rounded-xl px-3 py-2'
                }`}
                style={item.highlight ? { 
                  width: '60px',
                  height: '60px',
                  minWidth: '60px'
                } : { 
                  minHeight: '48px',
                  minWidth: '60px'
                }}
              >
                <div className="relative">
                  <Icon className={`${item.highlight ? 'w-6 h-6' : 'w-5 h-5'}`} />
                  
                  {/* Enhanced Badge for counts */}
                  {item.badge && (
                    <div className={`absolute -top-2 -right-2 text-white text-xs rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1 font-medium shadow-md ${
                      item.label === 'Messages' 
                        ? 'bg-red-500 animate-pulse' // Red pulsing for messages
                        : item.label === 'Notifications'
                        ? 'bg-blue-500' // Blue for notifications
                        : item.label === 'Cart'
                        ? 'bg-blue-500' // Blue for cart
                        : 'bg-green-500' // Green for others (like favorites)
                    }`}>
                      {item.badge > 99 ? '99+' : item.badge}
                    </div>
                  )}
                </div>
                
                {!item.highlight && (
                  <span className="text-xs mt-1 font-medium truncate w-full text-center">
                    {item.label}
                  </span>
                )}
              </Link>
            );
          })}
        </div>
        
        {/* Safe area for iPhone bottom indicator */}
        <div className="h-safe-area-inset-bottom bg-white dark:bg-gray-900"></div>
      </div>

      {/* Bottom padding to prevent content overlap */}
      <div className="h-20 lg:hidden"></div>
    </>
  );
}

export default MobileBottomNav;