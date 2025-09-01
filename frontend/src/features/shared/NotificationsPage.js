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
import { liveService } from '../../services/liveService';
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

  // Fetch real notifications from backend
  const fetchNotifications = async () => {
    if (!user?.id) return;
    
    setLoading(true);
    try {
      // Fetch real notifications from backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/notifications/${user.id}`);
      if (response.ok) {
        const realNotifications = await response.json();
        setNotifications(realNotifications || []);
        setUnreadCount(realNotifications.filter(n => !n.is_read).length);
      } else {
        throw new Error('Failed to fetch notifications');
      }
    } catch (error) {
      console.error('Failed to load real notifications:', error);
      
      // Enhanced demo notifications as fallback
      const enhancedDemoNotifications = [
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
        }
      ];
      
      setNotifications(enhancedDemoNotifications);
      setUnreadCount(enhancedDemoNotifications.filter(n => !n.is_read).length);
    } finally {
      setLoading(false);
    }
  };

  // Load notifications on component mount and when user changes
  useEffect(() => {
    fetchNotifications();
  }, [user]);

  // Mark notification as read
  const markAsRead = async (notificationId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/notifications/${notificationId}/read`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'user-id': user?.id
        }
      });
      
      if (response.ok) {
        setNotifications(notifications.map(n => 
          n.id === notificationId ? { ...n, is_read: true } : n
        ));
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  // Delete notification
  const deleteNotification = async (notificationId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/notifications/${notificationId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'user-id': user?.id
        }
      });
      
      if (response.ok) {
        const deletedNotification = notifications.find(n => n.id === notificationId);
        setNotifications(notifications.filter(n => n.id !== notificationId));
        if (deletedNotification && !deletedNotification.is_read) {
          setUnreadCount(prev => Math.max(0, prev - 1));
        }
      }
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  // Mark all as read
  const markAllAsRead = async () => {
    try {
      const unreadNotifications = notifications.filter(n => !n.is_read);
      await Promise.all(unreadNotifications.map(n => markAsRead(n.id)));
      setNotifications(notifications.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header */}
        <div className="cataloro-card-glass p-8 mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center space-x-4 mb-6 lg:mb-0">
              <div className="p-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl">
                <Bell className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Notifications</h1>
                <p className="text-gray-600 dark:text-gray-300">
                  {unreadCount > 0 ? `${unreadCount} unread notification${unreadCount > 1 ? 's' : ''}` : 'All caught up!'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Sound toggle */}
              <button
                onClick={() => {
                  const newSoundEnabled = !soundEnabled;
                  setSoundEnabled(newSoundEnabled);
                  localStorage.setItem('cataloro_notification_sound', newSoundEnabled.toString());
                }}
                className="p-3 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title={soundEnabled ? 'Disable sounds' : 'Enable sounds'}
              >
                {soundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
              </button>
              
              {/* Refresh */}
              <button
                onClick={() => window.location.reload()}
                className="p-3 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                title="Refresh notifications"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
              
              {/* Mark all read */}
              {unreadCount > 0 && (
                <button
                  onClick={handleMarkAllAsRead}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                >
                  Mark All Read
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="cataloro-card-glass p-6 mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            
            {/* Search */}
            <div className="relative flex-1 lg:max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search notifications..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-3 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Filter buttons - Enhanced alignment */}
            <div className="flex flex-wrap items-center justify-center lg:justify-start gap-2">
              {[
                { id: 'all', label: 'All', count: notifications.length },
                { id: 'unread', label: 'Unread', count: unreadCount },
                { id: 'message', label: 'Messages', count: notifications.filter(n => n.type === 'message').length },
                { id: 'buy_request', label: 'Requests', count: notifications.filter(n => n.type === 'buy_request').length }
              ].map(filterOption => (
                <button
                  key={filterOption.id}
                  onClick={() => setFilter(filterOption.id)}
                  className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 whitespace-nowrap ${
                    filter === filterOption.id
                      ? 'bg-blue-600 text-white shadow-md transform scale-105'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 hover:shadow-sm'
                  }`}
                >
                  <span>{filterOption.label}</span>
                  {filterOption.count > 0 && (
                    <span className={`ml-1.5 px-1.5 py-0.5 rounded-full text-xs font-bold min-w-[20px] text-center ${
                      filter === filterOption.id
                        ? 'bg-white/30 text-white'
                        : 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300'
                    }`}>
                      {filterOption.count}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Notifications List */}
        <div className="space-y-4">
          {loading ? (
            <div className="cataloro-card-glass p-12 text-center">
              <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Loading notifications...</h3>
            </div>
          ) : filteredNotifications.length === 0 ? (
            <div className="cataloro-card-glass p-12 text-center">
              <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
                <Bell className="w-12 h-12 text-gray-400" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                {searchTerm ? 'No matching notifications' : 'No notifications'}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {searchTerm ? 'Try adjusting your search terms.' : 'When you have new activity, it will appear here.'}
              </p>
            </div>
          ) : (
            filteredNotifications.map((notification) => {
              const color = getNotificationColor(notification.type);
              const isSelected = selectedNotifications.includes(notification.id);
              
              return (
                <div
                  key={notification.id}
                  className={`cataloro-card-glass p-6 transition-all duration-300 hover:scale-[1.02] cursor-pointer ${
                    !notification.is_read ? 'ring-2 ring-blue-500/30 bg-blue-50/30 dark:bg-blue-900/20' : ''
                  } ${isSelected ? 'ring-2 ring-purple-500/50' : ''}`}
                  onClick={() => {
                    if (!notification.is_read) {
                      handleMarkAsRead(notification.id);
                    }
                    if (notification.action_url) {
                      window.location.href = notification.action_url;
                    }
                  }}
                >
                  <div className="flex items-start space-x-4">
                    
                    {/* Notification Icon */}
                    <div className={`p-3 rounded-xl ${
                      color === 'blue' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' :
                      color === 'pink' ? 'bg-pink-100 text-pink-600 dark:bg-pink-900/30 dark:text-pink-400' :
                      color === 'yellow' ? 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400' :
                      color === 'green' ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' :
                      color === 'red' ? 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400' :
                      color === 'purple' ? 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400' :
                      'bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-400'
                    }`}>
                      {getNotificationIcon(notification.type)}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                            {notification.title}
                          </h4>
                          <p className="text-gray-600 dark:text-gray-300 mb-3">
                            {notification.message}
                          </p>
                          
                          {/* Metadata */}
                          {notification.metadata && (
                            <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400 mb-3">
                              {notification.metadata.amount && (
                                <span className="flex items-center">
                                  <DollarSign className="w-4 h-4 mr-1" />
                                  ${notification.metadata.amount}
                                </span>
                              )}
                              {notification.metadata.item && (
                                <span className="flex items-center">
                                  <Package className="w-4 h-4 mr-1" />
                                  {notification.metadata.item}
                                </span>
                              )}
                              {notification.metadata.views && (
                                <span className="flex items-center">
                                  <Eye className="w-4 h-4 mr-1" />
                                  {notification.metadata.views} views
                                </span>
                              )}
                            </div>
                          )}
                          
                          {/* Timestamp */}
                          <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                            <Clock className="w-4 h-4 mr-2" />
                            {new Date(notification.created_at).toLocaleString()}
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center space-x-2 ml-4">
                          {!notification.is_read && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleMarkAsRead(notification.id);
                              }}
                              className="p-2 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                              title="Mark as read"
                            >
                              <Check className="w-4 h-4" />
                            </button>
                          )}
                          
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDelete(notification.id);
                            }}
                            className="p-2 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                            title="Delete notification"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                          
                          {notification.action_url && (
                            <Link
                              to={notification.action_url}
                              className="p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                              title="Go to related page"
                              onClick={(e) => e.stopPropagation()}
                            >
                              <ArrowRight className="w-4 h-4" />
                            </Link>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Unread indicator */}
                    {!notification.is_read && (
                      <div className="w-3 h-3 bg-blue-600 rounded-full animate-pulse mt-1"></div>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Summary */}
        {filteredNotifications.length > 0 && (
          <div className="cataloro-card-glass p-6 mt-8">
            <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-300">
              <span>
                Showing {filteredNotifications.length} of {notifications.length} notifications
              </span>
              <span>
                {unreadCount} unread
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}



export default NotificationsPage;