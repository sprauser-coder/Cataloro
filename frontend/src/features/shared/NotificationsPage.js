/**
 * CATALORO - Notifications Page
 * Display and manage user notifications with bell icon functionality
 */

import React, { useState, useEffect } from 'react';
import { Bell, Check, CheckCheck, Trash2, Filter } from 'lucide-react';
import { useNotifications } from '../../context/NotificationContext';

function NotificationsPage() {
  const { 
    notifications, 
    unreadCount, 
    loading, 
    markAsRead, 
    markAllAsRead,
    removeNotification,
    fetchNotifications
  } = useNotifications();
  
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchNotifications();
  }, []);

  const filteredNotifications = notifications.filter(notification => {
    if (filter === 'unread') return !notification.is_read;
    if (filter === 'read') return notification.is_read;
    return true;
  });

  const handleMarkAsRead = async (notificationId) => {
    await markAsRead(notificationId);
  };

  const handleMarkAllAsRead = async () => {
    await markAllAsRead();
  };

  const handleDelete = async (notificationId) => {
    removeNotification(notificationId);
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'message':
        return '💬';
      case 'info':
        return 'ℹ️';
      case 'success':
        return '✅';
      case 'warning':
        return '⚠️';
      case 'error':
        return '❌';
      case 'buy_request':
        return '🛒';
      case 'buy_approved':
        return '✅';
      case 'buy_rejected':
        return '❌';
      case 'buy_expired':
        return '⏰';
      default:
        return '🔔';
    }
  };

  const getNotificationTypeColor = (type) => {
    switch (type) {
      case 'message':
        return 'border-blue-500';
      case 'info':
        return 'border-blue-500';
      case 'success':
        return 'border-green-500';
      case 'warning':
        return 'border-yellow-500';
      case 'error':
        return 'border-red-500';
      case 'buy_request':
        return 'border-yellow-500';
      case 'buy_approved':
        return 'border-green-500';
      case 'buy_rejected':
        return 'border-red-500';
      case 'buy_expired':
        return 'border-orange-500';
      default:
        return 'border-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Notifications</h1>
            <p className="text-gray-600">Stay updated with your marketplace activity</p>
          </div>
          
          {/* Action Buttons */}
          <div className="flex space-x-3">
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllAsRead}
                className="cataloro-button-secondary flex items-center"
              >
                <CheckCheck className="w-4 h-4 mr-2" />
                Mark All Read
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Stats and Filters */}
      <div className="cataloro-card p-6 mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          {/* Stats */}
          <div className="flex space-x-6">
            <div>
              <span className="text-2xl font-bold text-blue-600">{notifications.length}</span>
              <span className="text-sm text-gray-600 ml-1">Total</span>
            </div>
            <div>
              <span className="text-2xl font-bold text-orange-600">{unreadCount}</span>
              <span className="text-sm text-gray-600 ml-1">Unread</span>
            </div>
            <div>
              <span className="text-2xl font-bold text-green-600">{notifications.length - unreadCount}</span>
              <span className="text-sm text-gray-600 ml-1">Read</span>
            </div>
          </div>

          {/* Filter */}
          <div className="flex items-center space-x-3">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="cataloro-input w-auto"
            >
              <option value="all">All Notifications</option>
              <option value="unread">Unread Only</option>
              <option value="read">Read Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Notifications List */}
      {filteredNotifications.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Bell className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {filter === 'all' ? 'No notifications' : `No ${filter} notifications`}
          </h3>
          <p className="text-gray-600">
            {filter === 'all' 
              ? 'When you get notifications, they\'ll appear here'
              : `You don't have any ${filter} notifications at the moment`
            }
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredNotifications.map((notification) => (
            <NotificationCard
              key={notification.id}
              notification={notification}
              onMarkAsRead={handleMarkAsRead}
              onDelete={handleDelete}
              getIcon={getNotificationIcon}
              getTypeColor={getNotificationTypeColor}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Notification Card Component
function NotificationCard({ notification, onMarkAsRead, onDelete, getIcon, getTypeColor }) {
  return (
    <div className={`
      notification-item
      ${notification.is_read ? 'notification-read' : 'notification-unread'}
      ${getTypeColor(notification.type)}
    `}>
      <div className="flex items-start space-x-4">
        {/* Icon */}
        <div className="flex-shrink-0 text-2xl">
          {getIcon(notification.type)}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className={`font-medium ${notification.is_read ? 'text-gray-700' : 'text-gray-900'}`}>
                {notification.title}
              </h4>
              <p className={`mt-1 text-sm ${notification.is_read ? 'text-gray-500' : 'text-gray-700'}`}>
                {notification.message}
              </p>
              <p className="mt-2 text-xs text-gray-400">
                {notification.created_at ? new Date(notification.created_at).toLocaleString() : 'Just now'}
              </p>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-2 ml-4">
              {!notification.is_read && (
                <button
                  onClick={() => onMarkAsRead(notification.id)}
                  className="p-1 text-gray-400 hover:text-blue-600 transition-colors duration-200"
                  title="Mark as read"
                >
                  <Check className="w-4 h-4" />
                </button>
              )}
              <button
                onClick={() => onDelete(notification.id)}
                className="p-1 text-gray-400 hover:text-red-600 transition-colors duration-200"
                title="Delete notification"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default NotificationsPage;