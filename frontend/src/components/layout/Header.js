/**
 * CATALORO - Header Component
 * Modern top navigation with branding and user actions
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bell, Search, LogOut, Settings, Clock } from 'lucide-react';
import { UI_CONFIG, APP_ROUTES } from '../../config/directions';

function Header() {
  const [user, setUser] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [pendingOrders, setPendingOrders] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotificationDropdown, setShowNotificationDropdown] = useState(false);

  useEffect(() => {
    // Get user from localStorage
    const userData = localStorage.getItem('cataloro_user');
    if (userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        
        // Fetch pending orders count for sellers
        fetchPendingOrdersCount(parsedUser.id);
        // Fetch notifications
        fetchNotifications(parsedUser.id);
      } catch (error) {
        console.error('Error parsing user data:', error);
      }
    }
  }, []);

  const fetchPendingOrdersCount = async (userId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/orders/seller/${userId}`);
      if (response.ok) {
        const orders = await response.json();
        setPendingOrders(orders.length);
      }
    } catch (error) {
      console.error('Error fetching pending orders:', error);
    }
  };

  const fetchNotifications = async (userId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${userId}/notifications`);
      if (response.ok) {
        const userNotifications = await response.json();
        setNotifications(userNotifications.slice(0, 5)); // Show only 5 recent notifications
        const unreadNotifications = userNotifications.filter(n => !n.is_read);
        setUnreadCount(unreadNotifications.length + pendingOrders);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
      setUnreadCount(pendingOrders); // Fallback to just pending orders
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('cataloro_token');
    localStorage.removeItem('cataloro_user');
    setShowUserMenu(false);
    window.location.href = '/login';
  };

  return (
    <header className="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-40">
      <div className="flex items-center justify-between px-6 h-16">
        {/* Brand */}
        <div className="flex items-center">
          <Link to={APP_ROUTES.BROWSE} className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">C</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900">{UI_CONFIG.APP_NAME}</h1>
          </Link>
        </div>

        {/* Search Bar */}
        <div className="flex-1 max-w-2xl mx-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search marketplace..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50 focus:bg-white transition-all duration-200"
            />
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotificationDropdown(!showNotificationDropdown)}
              className="relative p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200"
            >
              <Bell className="w-6 h-6" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>

            {/* Notification Dropdown */}
            {showNotificationDropdown && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                <div className="px-4 py-2 border-b border-gray-100">
                  <p className="text-sm font-medium text-gray-900">Notifications</p>
                </div>
                
                {pendingOrders > 0 ? (
                  <Link
                    to="/pending-sales"
                    onClick={() => setShowNotificationDropdown(false)}
                    className="flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 border-b border-gray-100"
                  >
                    <div className="p-2 bg-yellow-100 rounded-lg mr-3">
                      <Clock className="w-4 h-4 text-yellow-600" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">
                        {pendingOrders} Pending Buy Request{pendingOrders !== 1 ? 's' : ''}
                      </p>
                      <p className="text-xs text-gray-500">
                        Customers want to buy your items
                      </p>
                    </div>
                  </Link>
                ) : (
                  <div className="px-4 py-6 text-center text-gray-500">
                    <Bell className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                    <p className="text-sm">No new notifications</p>
                  </div>
                )}

                <Link
                  to={APP_ROUTES.NOTIFICATIONS}
                  onClick={() => setShowNotificationDropdown(false)}
                  className="flex items-center px-4 py-2 text-sm text-blue-600 hover:bg-blue-50"
                >
                  View All Notifications
                </Link>
              </div>
            )}
          </div>

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-3 p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200"
            >
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">
                  {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                </span>
              </div>
              <span className="font-medium hidden sm:block">
                {user?.full_name || user?.username || 'User'}
              </span>
            </button>

            {/* Dropdown Menu */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                <div className="px-4 py-2 border-b border-gray-100">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.full_name || user?.username}
                  </p>
                  <p className="text-sm text-gray-500">{user?.email}</p>
                </div>
                
                <Link
                  to={APP_ROUTES.PROFILE}
                  onClick={() => setShowUserMenu(false)}
                  className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <Settings className="w-4 h-4 mr-3" />
                  Profile Settings
                </Link>
                
                <button
                  onClick={handleLogout}
                  className="flex items-center w-full px-4 py-2 text-sm text-red-700 hover:bg-red-50"
                >
                  <LogOut className="w-4 h-4 mr-3" />
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;