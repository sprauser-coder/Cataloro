/**
 * System Notifications List Component
 * Extracted from AdminPanel.js for better maintainability
 */

import React, { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';

function SystemNotificationsList() {
  const [systemNotifications, setSystemNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSystemNotifications();
  }, []);

  const fetchSystemNotifications = async () => {
    setLoading(true);
    try {
      // Fetch all notifications from the system (admin view)
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/notifications`);
      if (response.ok) {
        const notifications = await response.json();
        setSystemNotifications(notifications.slice(0, 10)); // Show latest 10
      } else {
        // Fallback - fetch some sample user notifications to show real data
        const fallbackResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/notifications/admin`);
        if (fallbackResponse.ok) {
          const fallbackNotifications = await fallbackResponse.json();
          setSystemNotifications(fallbackNotifications.slice(0, 10));
        }
      }
    } catch (error) {
      console.error('Failed to fetch system notifications:', error);
      setSystemNotifications([]);
    } finally {
      setLoading(false);
    }
  };

  const deleteSystemNotification = async (notificationId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/notifications/${notificationId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        setSystemNotifications(prev => prev.filter(n => n.id !== notificationId));
      }
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600 dark:text-gray-400">Loading notifications...</span>
      </div>
    );
  }

  if (systemNotifications.length === 0) {
    return (
      <div className="text-center py-8">
        <Bell className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No System Notifications</h3>
        <p className="text-gray-600 dark:text-gray-400">No notifications are currently active in the system.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {systemNotifications.map((notification) => (
        <div key={notification.id} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <div className={`w-3 h-3 rounded-full ${
                  notification.type === 'message' ? 'bg-blue-500' :
                  notification.type === 'buy_approved' ? 'bg-green-500' :
                  notification.type === 'favorite' ? 'bg-pink-500' :
                  notification.type === 'buy_request' ? 'bg-orange-500' :
                  notification.type === 'payment' ? 'bg-green-600' :
                  'bg-gray-500'
                }`}></div>
                <h5 className="font-medium text-gray-900 dark:text-white">{notification.title}</h5>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  notification.is_read 
                    ? 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400' 
                    : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                }`}>
                  {notification.is_read ? 'Read' : 'Unread'}
                </span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{notification.message}</p>
              <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-500">
                <span>To: {notification.user_email || 'System'}</span>
                <span>•</span>
                <span>{new Date(notification.created_at).toLocaleString()}</span>
              </div>
            </div>
            <button
              onClick={() => deleteSystemNotification(notification.id)}
              className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 p-1 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              title="Delete notification"
            >
              <Bell className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

export default SystemNotificationsList;