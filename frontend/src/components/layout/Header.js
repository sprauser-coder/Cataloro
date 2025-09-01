/**
 * CATALORO - Header Component
 * Modern top navigation with branding and user actions
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Bell, Search, LogOut, Settings, Clock, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
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

  const markNotificationAsRead = async (notificationId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${user.id}/notifications/${notificationId}/read`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        // Update local state
        setNotifications(prev => 
          prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
        );
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
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
              <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50 max-h-96 overflow-y-auto">
                <div className="px-4 py-2 border-b border-gray-100 flex items-center justify-between">
                  <p className="text-sm font-medium text-gray-900">Notifications</p>
                  <button
                    onClick={() => fetchNotifications(user?.id)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                </div>
                
                {/* Pending Orders Section */}
                {pendingOrders > 0 && (
                  <div className="border-b border-gray-100">
                    <Link
                      to="/pending-sales"
                      onClick={() => setShowNotificationDropdown(false)}
                      className="flex items-center px-4 py-3 text-sm text-gray-700 hover:bg-gray-50"
                    >
                      <div className="p-2 bg-yellow-100 rounded-lg mr-3">
                        <Clock className="w-4 h-4 text-yellow-600" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium">
                          {pendingOrders} Pending Buy Request{pendingOrders !== 1 ? 's' : ''}
                        </p>
                        <p className="text-xs text-gray-500">
                          Customers want to buy your items • Click to manage
                        </p>
                      </div>
                      <div className="text-xs text-blue-600 font-medium">
                        Manage →
                      </div>
                    </Link>
                  </div>
                )}

                {/* Recent Notifications */}
                {notifications.length > 0 ? (
                  <div className="max-h-64 overflow-y-auto">
                    {notifications.map((notification) => (
                      <div
                        key={notification.id}
                        className={`flex items-start px-4 py-3 text-sm hover:bg-gray-50 border-b border-gray-50 ${
                          !notification.is_read ? 'bg-blue-50/50' : ''
                        }`}
                      >
                        <div className={`p-2 rounded-lg mr-3 ${
                          notification.type === 'buy_request' ? 'bg-yellow-100' :
                          notification.type === 'buy_approved' ? 'bg-green-100' :
                          notification.type === 'buy_rejected' ? 'bg-red-100' :
                          'bg-blue-100'
                        }`}>
                          {notification.type === 'buy_request' && <Clock className="w-4 h-4 text-yellow-600" />}
                          {notification.type === 'buy_approved' && <CheckCircle className="w-4 h-4 text-green-600" />}
                          {notification.type === 'buy_rejected' && <XCircle className="w-4 h-4 text-red-600" />}
                          {!['buy_request', 'buy_approved', 'buy_rejected'].includes(notification.type) && 
                            <Bell className="w-4 h-4 text-blue-600" />}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-gray-900 truncate">
                            {notification.title}
                          </p>
                          <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                            {notification.message}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {new Date(notification.created_at).toLocaleDateString()}
                          </p>
                          
                          {/* Notification Actions */}
                          <div className="flex space-x-2 mt-2">
                            {!notification.is_read && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  markNotificationAsRead(notification.id);
                                }}
                                className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
                              >
                                Mark Read
                              </button>
                            )}
                            
                            {notification.type === 'buy_request' && notification.order_id && (
                              <Link
                                to="/pending-sales"
                                onClick={() => setShowNotificationDropdown(false)}
                                className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded hover:bg-yellow-200"
                              >
                                View Request
                              </Link>
                            )}
                            
                            {notification.type === 'buy_approved' && (
                              <Link
                                to="/cart"
                                onClick={() => setShowNotificationDropdown(false)}
                                className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200"
                              >
                                View Details
                              </Link>
                            )}
                          </div>
                        </div>
                        {!notification.is_read && (
                          <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : pendingOrders === 0 && (
                  <div className="px-4 py-6 text-center text-gray-500">
                    <Bell className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                    <p className="text-sm">No new notifications</p>
                  </div>
                )}

                {/* Quick Actions */}
                <div className="border-t border-gray-100 p-2">
                  <div className="flex space-x-2">
                    <Link
                      to="/cart"
                      onClick={() => setShowNotificationDropdown(false)}
                      className="flex-1 text-center px-3 py-2 text-xs bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100"
                    >
                      View Cart
                    </Link>
                    <Link
                      to="/pending-sales"
                      onClick={() => setShowNotificationDropdown(false)}
                      className="flex-1 text-center px-3 py-2 text-xs bg-yellow-50 text-yellow-700 rounded-md hover:bg-yellow-100"
                    >
                      Pending Sales
                    </Link>
                    <Link
                      to={APP_ROUTES.NOTIFICATIONS}
                      onClick={() => setShowNotificationDropdown(false)}
                      className="flex-1 text-center px-3 py-2 text-xs bg-gray-50 text-gray-700 rounded-md hover:bg-gray-100"
                    >
                      View All
                    </Link>
                  </div>
                </div>
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