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
  Package,
  Bell
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
          
          // Load real unread message count (only messages from last 7 days)
          try {
            const messages = await liveService.getUserMessages(user.id);
            const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
            const unreadCount = messages.filter(msg => {
              const messageDate = new Date(msg.created_at);
              // Only count messages that are:
              // 1. Explicitly not read (is_read === false, not undefined)
              // 2. Sent TO the current user (not FROM the current user)
              // 3. Not self-messages (sender !== recipient)
              // 4. Within last 7 days
              const isUnread = msg.is_read === false && 
                               msg.recipient_id === user.id && 
                               msg.sender_id !== user.id && 
                               messageDate >= sevenDaysAgo;
              if (isUnread) {
                console.log(`🔍 BottomNav found unread message: from ${msg.sender_id} to ${msg.recipient_id}, is_read=${msg.is_read}, date=${messageDate.toISOString()}`);
              }
              return isUnread;
            }).length;
            console.log(`🔍 BottomNav calculated unread count: ${unreadCount} from ${messages.length} total messages`);
            setUnreadMessages(unreadCount);
            localStorage.setItem('cataloro_unread_messages', unreadCount.toString());
          } catch (error) {
            console.error('Error loading messages:', error);
            // Don't use fallback localStorage to avoid stale data
            setUnreadMessages(0);
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
  }, [unreadMessages]);

  const isActive = (path) => {
    if (path === '/browse' && location.pathname === '/') return true;
    return location.pathname === path;
  };

  // Check if user is seller-only based on actual user properties
  // For now, let's check email domain or username patterns to identify seller accounts
  const isSellerOnly = user && (
    user.email?.includes('seller') || 
    user.username?.includes('seller') ||
    user.email === 'ana@cataloro.com' || // Specific seller account mentioned by user
    user.username === 'ana_admin' ||
    (user.is_business === true && user.full_name?.toLowerCase().includes('business'))
  );
  
  console.log('🔍 MobileBottomNav - User role debug:', {
    user: user ? {
      id: user.id,
      username: user.username,
      email: user.email,
      full_name: user.full_name,
      is_business: user.is_business,
      role: user.role,
      account_type: user.account_type,
      can_buy: user.can_buy
    } : null,
    isSellerOnly: isSellerOnly,
    sellerChecks: user ? {
      emailIncludesSeller: user.email?.includes('seller'),
      usernameIncludesSeller: user.username?.includes('seller'),
      isAnaAccount: user.email === 'ana@cataloro.com',
      isAnaUsername: user.username === 'ana_admin',
      isBusiness: user.is_business === true
    } : null
  });

  const allBottomNavItems = isSellerOnly ? [
    // Seller-only navigation: Browse, Messages, Add Listing, Notifications, Sell
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
      label: 'Add Listing',
      path: '/create-listing',
      icon: Plus,
      badge: null,
      highlight: true, // Central create button
      key: 'create'
    },
    {
      label: 'Notifications',
      path: '/notifications',
      icon: Bell,
      badge: null, // Could add notification count here
      key: 'notifications'
    },
    {
      label: 'Sell',
      path: '/sell',
      icon: Package,
      badge: null,
      key: 'sell'
    }
  ] : [
    // Regular navigation: Browse, Messages, Create, Buy, Sell
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
      label: 'Create',
      path: '/create-listing',
      icon: Plus,
      badge: null,
      highlight: true, // Central create button
      key: 'create'
    },
    {
      label: 'Buy',
      path: '/buy',
      icon: ShoppingCart,
      badge: null,
      key: 'buy'
    },
    {
      label: 'Sell',
      path: '/sell',
      icon: Package,
      badge: null,
      key: 'sell'
    }
  ];

  // Filter bottom nav items based on menu settings
  const bottomNavItems = allBottomNavItems.filter(item => 
    isMenuItemVisible('mobile_menu', item.key)
  );

  console.log('🔍 MobileBottomNav rendering with:', {
    isSellerOnly,
    allBottomNavItemsCount: allBottomNavItems.length,
    allBottomNavLabels: allBottomNavItems.map(item => item.label),
    bottomNavItemsCount: bottomNavItems.length,
    bottomNavLabels: bottomNavItems.map(item => item.label)
  });

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
                        ? 'bg-red-500' // Red steady for messages
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