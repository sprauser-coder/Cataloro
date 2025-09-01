/**
 * CATALORO - Enhanced Notifications Page
 * Modern notification management with advanced functionality
 */

import React, { useState, useEffect } from 'react';
import { 
  Bell, 
  Check, 
  CheckCheck, 
  Trash2, 
  Filter,
  Search,
  RefreshCw,
  MessageCircle,
  Heart,
  DollarSign,
  ShoppingCart,
  Star,
  User,
  Package,
  Eye,
  Settings,
  Calendar,
  Clock,
  MoreVertical,
  Archive,
  Volume2,
  VolumeX,
  Mail,
  ArrowRight,
  X
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Link } from 'react-router-dom';

function NotificationsPage() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [selectedNotifications, setSelectedNotifications] = useState([]);
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  // Enhanced demo notifications with more variety
  const demoNotifications = [
    {
      id: '1',
      title: 'New Message from Sarah',
      message: 'Hi! Is your MacBook Pro still available? I\'m very interested.',
      type: 'message',
      is_read: false,
      priority: 'high',
      user_avatar: '/api/placeholder/40/40',
      created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      action_url: '/messages',
      metadata: { sender_id: 'user123', conversation_id: 'conv1' }
    },
    {
      id: '2', 
      title: 'Buy Request Approved',
      message: 'Your purchase request for iPhone 14 Pro has been approved by the seller.',
      type: 'buy_approved',
      is_read: false,
      priority: 'high',
      created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      action_url: '/my-deals',
      metadata: { amount: 899, item: 'iPhone 14 Pro' }
    },
    {
      id: '3',
      title: 'Listing Favorited',
      message: 'Someone added your "Gaming Setup" to their favorites.',
      type: 'favorite',
      is_read: false,
      priority: 'medium',
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      metadata: { listing_id: 'listing123' }
    },
    {
      id: '4',
      title: 'New Buy Request',
      message: 'Mike wants to buy your "Vintage Guitar" for $1,200.',
      type: 'buy_request',
      is_read: true,
      priority: 'high',
      created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      action_url: '/pending-sales',
      metadata: { buyer: 'Mike', amount: 1200, item: 'Vintage Guitar' }
    },
    {
      id: '5',
      title: 'Payment Received',
      message: 'You received $459 for the sale of "Canon Camera Lens".',
      type: 'payment',
      is_read: true,
      priority: 'high',
      created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      metadata: { amount: 459, item: 'Canon Camera Lens' }
    },
    {
      id: '6',
      title: 'Profile View',
      message: 'Your profile was viewed 12 times today.',
      type: 'profile_view',
      is_read: true,
      priority: 'low',
      created_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
      metadata: { views: 12 }
    },
    {
      id: '7',
      title: 'System Update',
      message: 'New features have been added to the marketplace. Check them out!',
      type: 'system',
      is_read: false,
      priority: 'medium',
      created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      action_url: '/browse'
    }
  ];

  useEffect(() => {
    const loadNotifications = async () => {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setNotifications(demoNotifications);
      setUnreadCount(demoNotifications.filter(n => !n.is_read).length);
      setLoading(false);
    };

    loadNotifications();
    
    // Load sound preference
    const soundPref = localStorage.getItem('cataloro_notification_sound');
    setSoundEnabled(soundPref !== 'false');
  }, []);

  // Filter and search notifications
  const filteredNotifications = notifications.filter(notification => {
    const matchesFilter = filter === 'all' || 
                         (filter === 'unread' && !notification.is_read) ||
                         (filter === 'read' && notification.is_read) ||
                         (filter === notification.type);
    
    const matchesSearch = !searchTerm || 
                         notification.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         notification.message.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesFilter && matchesSearch;
  });

  // Get notification icon
  const getNotificationIcon = (type) => {
    const iconProps = { className: "w-5 h-5" };
    switch (type) {
      case 'message': return <MessageCircle {...iconProps} />;
      case 'favorite': return <Heart {...iconProps} />;
      case 'buy_request': return <ShoppingCart {...iconProps} />;
      case 'buy_approved': return <Check {...iconProps} />;
      case 'buy_rejected': return <X {...iconProps} />;
      case 'payment': return <DollarSign {...iconProps} />;
      case 'profile_view': return <Eye {...iconProps} />;
      case 'system': return <Settings {...iconProps} />;
      default: return <Bell {...iconProps} />;
    }
  };

  // Get notification color
  const getNotificationColor = (type) => {
    switch (type) {
      case 'message': return 'blue';
      case 'favorite': return 'pink';
      case 'buy_request': return 'yellow';
      case 'buy_approved': return 'green';
      case 'buy_rejected': return 'red';
      case 'payment': return 'green';
      case 'profile_view': return 'purple';
      case 'system': return 'gray';
      default: return 'blue';
    }
  };

  // Mark notification as read
  const handleMarkAsRead = (notificationId) => {
    setNotifications(notifications.map(n => 
      n.id === notificationId ? { ...n, is_read: true } : n
    ));
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  // Mark all as read
  const handleMarkAllAsRead = () => {
    setNotifications(notifications.map(n => ({ ...n, is_read: true })));
    setUnreadCount(0);
  };

  // Delete notification
  const handleDelete = (notificationId) => {
    const deleted = notifications.find(n => n.id === notificationId);
    setNotifications(notifications.filter(n => n.id !== notificationId));
    if (deleted && !deleted.is_read) {
      setUnreadCount(prev => Math.max(0, prev - 1));
    }
  };

  // Bulk actions
  const handleBulkAction = (action) => {
    if (action === 'markRead') {
      const unreadSelected = selectedNotifications.filter(id => 
        notifications.find(n => n.id === id && !n.is_read)
      );
      setNotifications(notifications.map(n => 
        selectedNotifications.includes(n.id) ? { ...n, is_read: true } : n
      ));
      setUnreadCount(prev => Math.max(0, prev - unreadSelected.length));
    } else if (action === 'delete') {
      const deletedUnread = selectedNotifications.filter(id => 
        notifications.find(n => n.id === id && !n.is_read)
      ).length;
      setNotifications(notifications.filter(n => !selectedNotifications.includes(n.id)));
      setUnreadCount(prev => Math.max(0, prev - deletedUnread));
    }
    setSelectedNotifications([]);
    setShowBulkActions(false);
  };

  return (
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