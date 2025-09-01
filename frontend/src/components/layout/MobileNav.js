/**
 * CATALORO - Mobile Navigation Drawer
 * Sleek mobile navigation with all features
 */

import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Store,
  Package,
  ShoppingCart,
  Heart,
  MessageCircle,
  DollarSign,
  BarChart3,
  Grid3X3,
  Plus,
  Shield,
  Settings,
  User,
  Bell,
  Search,
  Zap,
  TrendingUp,
  Award
} from 'lucide-react';

function MobileNav({ isOpen, onClose }) {
  const [user, setUser] = useState(null);
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
  }, []);

  const isActive = (path) => location.pathname === path;
  const isAdmin = user?.role === 'admin';

  const navigationSections = [
    {
      title: 'Marketplace',
      items: [
        { label: 'Browse All', path: '/browse', icon: Store },
        { label: 'Categories', path: '/categories', icon: Grid3X3 },
        { label: 'Search', path: '/search', icon: Search },
        { label: 'Trending', path: '/trending', icon: TrendingUp }
      ]
    },
    {
      title: 'My Account',
      items: [
        { label: 'My Listings', path: '/my-listings', icon: Package },
        { label: 'My Deals', path: '/my-deals', icon: DollarSign },
        { label: 'Messages', path: '/messages', icon: MessageCircle },
        { label: 'Favorites', path: '/favorites', icon: Heart },
        { label: 'Cart', path: '/cart', icon: ShoppingCart }
      ]
    },
    {
      title: 'Selling',
      items: [
        { label: 'Create Listing', path: '/create-listing', icon: Plus },
        { label: 'Seller Analytics', path: '/analytics', icon: BarChart3 },
        { label: 'Performance', path: '/performance', icon: Award }
      ]
    }
  ];

  if (isAdmin) {
    navigationSections.push({
      title: 'Admin',
      items: [
        { label: 'Admin Dashboard', path: '/admin', icon: Shield },
        { label: 'Site Analytics', path: '/admin/analytics', icon: BarChart3 },
        { label: 'User Management', path: '/admin/users', icon: User }
      ]
    });
  }

  navigationSections.push({
    title: 'Settings',
    items: [
      { label: 'Profile', path: '/profile', icon: User },
      { label: 'Notifications', path: '/notifications', icon: Bell },
      { label: 'Settings', path: '/settings', icon: Settings }
    ]
  });

  return (
    <div
      className={`fixed top-0 left-0 h-full w-80 bg-white dark:bg-gray-900 shadow-2xl z-50 transform transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      } lg:hidden`}
    >
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
            <span className="text-white font-bold text-lg">C</span>
          </div>
          <div>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">Cataloro</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">Modern Marketplace</p>
          </div>
        </div>
        
        {user && (
          <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">
                  {user.full_name?.charAt(0) || user.username?.charAt(0) || 'U'}
                </span>
              </div>
              <div>
                <p className="font-medium text-gray-900 dark:text-white text-sm">
                  {user.full_name || user.username}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {user.role?.toUpperCase()}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4 space-y-6">
          {navigationSections.map((section) => (
            <div key={section.title}>
              <h3 className="text-xs uppercase tracking-wider text-gray-500 dark:text-gray-400 font-semibold mb-3 px-2">
                {section.title}
              </h3>
              <div className="space-y-1">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={onClose}
                      className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                        isActive(item.path)
                          ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span>{item.label}</span>
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Cataloro v2.0 - Ultra Modern
          </p>
        </div>
      </div>
    </div>
  );
}

export default MobileNav;