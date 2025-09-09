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
  MessageCircle
} from 'lucide-react';

function MobileBottomNav() {
  const [user, setUser] = useState(null);
  const [cartCount, setCartCount] = useState(0);
  const [favoritesCount, setFavoritesCount] = useState(0);
  const [unreadMessages, setUnreadMessages] = useState(0);
  const location = useLocation();

  useEffect(() => {
    // Load user data
    const userData = localStorage.getItem('cataloro_user');
    if (userData) {
      try {
        setUser(JSON.parse(userData));
      } catch (error) {
        console.error('Error parsing user data:', error);
      }
    }

    // Load REAL counts from backend and localStorage
    const loadRealCounts = async () => {
      try {
        // Load real cart count
        const savedCart = localStorage.getItem('cataloro_cart_count');
        if (savedCart) {
          setCartCount(parseInt(savedCart, 10) || 0);
        }

        // Load real unread messages count from backend
        if (userData) {
          const user = JSON.parse(userData);
          // This should be replaced with actual API call to get unread messages
          // For now, check localStorage for real message count
          const savedMessages = localStorage.getItem('cataloro_unread_messages');
          if (savedMessages) {
            setUnreadMessages(parseInt(savedMessages, 10) || 0);
          }
        }
      } catch (error) {
        console.error('Error loading real counts:', error);
      }
    };

    loadRealCounts();

    // Listen for real badge updates from the app
    const handleBadgeUpdate = (event) => {
      const { type, count } = event.detail;
      switch (type) {
        case 'messages':
          setUnreadMessages(count);
          localStorage.setItem('cataloro_unread_messages', count.toString());
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

  const bottomNavItems = [
    {
      label: 'Browse',
      path: '/browse',
      icon: Store,
      badge: null
    },
    {
      label: 'Messages',
      path: '/messages',
      icon: MessageCircle,
      badge: unreadMessages > 0 ? unreadMessages : null
    },
    {
      label: 'Create',
      path: '/create-listing',
      icon: Plus,
      badge: null,
      highlight: true // Central create button
    },
    {
      label: 'Cart',
      path: '/buy-management',
      icon: ShoppingCart,
      badge: cartCount > 0 ? cartCount : null
    },
    {
      label: 'Profile',
      path: '/profile',
      icon: User,
      badge: favoritesCount > 0 ? favoritesCount : null // Add favorites badge to profile
    }
  ];

  return (
    <>
      {/* Bottom Navigation Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 z-40 lg:hidden safe-area-pb">
        <div className="flex items-center justify-around px-1 py-1">
          {bottomNavItems.map((item, index) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`relative flex flex-col items-center justify-center px-2 py-2 rounded-xl min-w-0 flex-1 transition-all duration-200 touch-manipulation ${
                  item.highlight
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg scale-110 -mt-2'
                    : active
                    ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 active:bg-gray-100 dark:active:bg-gray-800'
                }`}
                style={item.highlight ? { 
                  marginTop: '-8px',
                  borderRadius: '12px', // Changed from 50% to 12px for square with rounded edges
                  width: '56px',
                  height: '56px',
                  minWidth: '56px'
                } : { minHeight: '44px' }}
              >
                <div className="relative">
                  <Icon className={`${item.highlight ? 'w-6 h-6' : 'w-5 h-5'}`} />
                  
                  {/* Enhanced Badge for counts */}
                  {item.badge && (
                    <div className={`absolute -top-2 -right-2 text-white text-xs rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1 font-medium shadow-md ${
                      item.label === 'Messages' 
                        ? 'bg-red-500 animate-pulse' // Red pulsing for messages
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