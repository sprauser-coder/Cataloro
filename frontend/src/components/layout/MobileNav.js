/**
 * CATALORO - Mobile Navigation Drawer
 * Sleek mobile navigation with all features
 */

import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
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
  TrendingUp,
  Award,
  Globe,
  LogOut
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

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
        { label: 'About Platform', path: '/info', icon: Globe },
        { label: 'Browse All', path: '/browse', icon: Store }
      ]
    },
    {
      title: 'My Account',
      items: [
        { label: 'My Listings', path: '/my-listings', icon: Package },
        { label: 'Buy Management', path: '/buy-management', icon: ShoppingCart },
        { label: 'Messages', path: '/messages', icon: MessageCircle },
        { label: 'Favorites', path: '/favorites', icon: Heart }
      ]
    },
    {
      title: 'Settings',
      items: [
        { label: 'Profile', path: '/profile', icon: User },
        { label: 'Notifications', path: '/notifications', icon: Bell }
      ]
    }
  ];

  // Admin users can access admin panel through separate dedicated button/icon
  // Removed admin section from mobile nav to keep it clean

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Navigation Drawer - Completely Redesigned for Mobile */}
      <div
        className={`fixed top-0 left-0 h-full w-64 max-w-[70vw] bg-white dark:bg-gray-900 shadow-2xl z-50 transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:hidden`}
      >
        {/* Compact Header */}
        <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-600 to-purple-600">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">C</span>
              </div>
              <div>
                <h2 className="text-sm font-bold text-white">Cataloro</h2>
                <p className="text-xs text-white/80">Marketplace</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1 text-white/80 hover:text-white hover:bg-white/20 rounded-md transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {/* Compact User Info */}
          {user && (
            <div className="mt-2 flex items-center space-x-2 p-2 bg-white/10 rounded-md">
              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-xs">
                  {user.full_name?.charAt(0) || user.username?.charAt(0) || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-white text-xs truncate">
                  {user.full_name || user.username}
                </p>
                <p className="text-xs text-white/70 uppercase">
                  {user.role}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Compact Navigation */}
        <div className="flex-1 overflow-y-auto py-2">
          {navigationSections.map((section) => (
            <div key={section.title} className="mb-3">
              <h3 className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400 font-semibold mb-1 px-4">
                {section.title}
              </h3>
              <div className="space-y-0">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={onClose}
                      className={`flex items-center space-x-3 px-4 py-2 text-sm font-medium transition-all duration-200 touch-manipulation ${
                        isActive(item.path)
                          ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 border-r-2 border-blue-600'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 active:bg-gray-100 dark:active:bg-gray-700'
                      }`}
                    >
                      <Icon className="w-4 h-4 flex-shrink-0" />
                      <span className="truncate">{item.label}</span>
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Compact Footer */}
        <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            Cataloro v2.0
          </p>
        </div>
      </div>
    </>
  );
}

export default MobileNav;