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
    const userData = localStorage.getItem('cataloro_user');
    if (userData) {
      try {
        setUser(JSON.parse(userData));
      } catch (error) {
        console.error('Error parsing user data:', error);
      }
    }

    // Load counts from localStorage or context
    const savedCart = localStorage.getItem('cataloro_cart_count');
    const savedFavorites = localStorage.getItem('cataloro_favorites_count');
    const savedMessages = localStorage.getItem('cataloro_unread_messages');
    
    if (savedCart) setCartCount(parseInt(savedCart, 10) || 0);
    if (savedFavorites) setFavoritesCount(parseInt(savedFavorites, 10) || 0);
    if (savedMessages) setUnreadMessages(parseInt(savedMessages, 10) || 0);
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
      label: 'Search',
      path: '/search',
      icon: Search,
      badge: null
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
      badge: null
    }
  ];

  return (
    <>
      {/* Bottom Navigation Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 z-40 lg:hidden">
        <div className="flex items-center justify-around px-2 py-2">
          {bottomNavItems.map((item, index) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`relative flex flex-col items-center justify-center px-3 py-2 rounded-xl min-w-0 flex-1 transition-all duration-200 ${
                  item.highlight
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg scale-110 -mt-2'
                    : active
                    ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                }`}
                style={item.highlight ? { 
                  marginTop: '-8px',
                  borderRadius: '50%',
                  width: '56px',
                  height: '56px',
                  minWidth: '56px'
                } : {}}
              >
                <div className="relative">
                  <Icon className={`${item.highlight ? 'w-6 h-6' : 'w-5 h-5'}`} />
                  
                  {/* Badge for counts */}
                  {item.badge && (
                    <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1">
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