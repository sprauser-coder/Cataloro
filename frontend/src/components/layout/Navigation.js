/**
 * CATALORO - Navigation Component  
 * Ultra-modern sidebar navigation with role-based menu items
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Search, 
  Package, 
  HandHeart, 
  Shield, 
  Heart, 
  Bell, 
  User, 
  LogOut 
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { APP_ROUTES, USER_ROLES } from '../../config/directions';

function Navigation() {
  const location = useLocation();
  const { user, logout, isAdmin } = useAuth();

  const isActive = (path) => location.pathname === path;

  const menuItems = [
    {
      label: 'Browse',
      path: APP_ROUTES.BROWSE,
      icon: Search,
      roles: [USER_ROLES.USER, USER_ROLES.ADMIN, USER_ROLES.MODERATOR]
    },
    {
      label: 'My Listings',
      path: APP_ROUTES.MY_LISTINGS,
      icon: Package,
      roles: [USER_ROLES.USER, USER_ROLES.ADMIN, USER_ROLES.MODERATOR]
    },
    {
      label: 'My Deals',
      path: APP_ROUTES.MY_DEALS,
      icon: HandHeart,
      roles: [USER_ROLES.USER, USER_ROLES.ADMIN, USER_ROLES.MODERATOR]
    },
    {
      label: '*Admin Panel',
      path: APP_ROUTES.ADMIN_PANEL,
      icon: Shield,
      roles: [USER_ROLES.ADMIN],
      isAdmin: true
    },
    {
      label: 'Favorites',
      path: APP_ROUTES.FAVORITES,
      icon: Heart,
      roles: [USER_ROLES.USER, USER_ROLES.ADMIN, USER_ROLES.MODERATOR]
    },
    {
      label: 'Notifications',
      path: APP_ROUTES.NOTIFICATIONS,
      icon: Bell,
      roles: [USER_ROLES.USER, USER_ROLES.ADMIN, USER_ROLES.MODERATOR]
    },
    {
      label: 'Profile Page',
      path: APP_ROUTES.PROFILE,
      icon: User,
      roles: [USER_ROLES.USER, USER_ROLES.ADMIN, USER_ROLES.MODERATOR]
    }
  ];

  const filteredMenuItems = menuItems.filter(item => {
    if (item.isAdmin && !isAdmin()) {
      return false;
    }
    return item.roles.includes(user?.role);
  });

  return (
    <nav className="fixed left-0 top-16 bottom-0 w-64 bg-white border-r border-gray-200 z-30">
      <div className="flex flex-col h-full">
        {/* Navigation Menu */}
        <div className="flex-1 px-4 py-6 space-y-2">
          {filteredMenuItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  nav-item
                  ${active ? 'active' : ''}
                  ${item.isAdmin ? 'nav-item-admin' : ''}
                `}
              >
                <Icon className="w-5 h-5 mr-3" />
                <span className="font-medium">{item.label}</span>
                {item.isAdmin && (
                  <span className="ml-auto text-xs bg-purple-100 text-purple-600 px-2 py-1 rounded-full">
                    ADMIN
                  </span>
                )}
              </Link>
            );
          })}
        </div>

        {/* User Info & Logout */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
              <span className="text-white font-medium">
                {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user?.full_name || user?.username || 'User'}
              </p>
              <p className="text-xs text-gray-500 truncate">
                {user?.email}
              </p>
              {user?.role && (
                <span className="inline-block text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded-full mt-1">
                  {user.role.toUpperCase()}
                </span>
              )}
            </div>
          </div>
          
          <button
            onClick={logout}
            className="w-full flex items-center px-3 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-all duration-200"
          >
            <LogOut className="w-4 h-4 mr-3" />
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navigation;