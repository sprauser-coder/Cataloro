import React, { useState, useEffect } from 'react';
import { Bell, X, Check, Package, ShoppingCart, Heart, MessageCircle, Star } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { useAuth } from '../../context/AuthContext';
import { formatDate } from '../../utils/helpers';

const NotificationCenter = () => {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  // Mock notifications - in real app, these would come from WebSocket or API
  useEffect(() => {
    if (user) {
      const mockNotifications = [
        {
          id: '1',
          type: 'order_update',
          title: 'Order Shipped',
          message: 'Your order for iPhone 14 Pro has been shipped and is on the way!',
          timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
          read: false,
          icon: Package,
          color: 'text-blue-600',
          actionUrl: '/orders'
        },
        {
          id: '2',
          type: 'new_message',
          title: 'New Message',
          message: 'John Smith sent you a message about the vintage jacket listing.',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
          read: false,
          icon: MessageCircle,
          color: 'text-green-600',
          actionUrl: '/messages'
        },
        {
          id: '3',
          type: 'favorite_price_drop',
          title: 'Price Drop Alert',
          message: 'The gaming laptop in your favorites dropped by €100!',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5), // 5 hours ago
          read: true,
          icon: Heart,
          color: 'text-red-600',
          actionUrl: '/favorites'
        },
        {
          id: '4',
          type: 'new_review',
          title: 'New Review',
          message: 'You received a 5-star review for your recent sale.',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
          read: true,
          icon: Star,
          color: 'text-yellow-600',
          actionUrl: '/profile'
        },
        {
          id: '5',
          type: 'listing_sold',
          title: 'Item Sold',
          message: 'Congratulations! Your MacBook Pro listing has been sold.',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 48), // 2 days ago
          read: true,
          icon: ShoppingCart,
          color: 'text-green-600',
          actionUrl: '/orders'
        }
      ];

      setNotifications(mockNotifications);
      setUnreadCount(mockNotifications.filter(n => !n.read).length);
    }
  }, [user]);

  const markAsRead = (notificationId) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === notificationId ? { ...notif, read: true } : notif
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(notif => ({ ...notif, read: true })));
    setUnreadCount(0);
  };

  const removeNotification = (notificationId) => {
    setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
    const wasUnread = notifications.find(n => n.id === notificationId)?.read === false;
    if (wasUnread) {
      setUnreadCount(prev => Math.max(0, prev - 1));
    }
  };

  const handleNotificationClick = (notification) => {
    if (!notification.read) {
      markAsRead(notification.id);
    }
    
    if (notification.actionUrl) {
      window.location.hash = notification.actionUrl;
    }
    
    setIsOpen(false);
  };

  const getRelativeTime = (timestamp) => {
    const now = new Date();
    const diffInSeconds = Math.floor((now - timestamp) / 1000);
    
    if (diffInSeconds < 60) {
      return 'Just now';
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes}m ago`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours}h ago`;
    } else {
      const days = Math.floor(diffInSeconds / 86400);
      return `${days}d ago`;
    }
  };

  if (!user) return null;

  return (
    <div className="relative">
      {/* Bell Icon Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-purple-100 hover:text-white hover:bg-purple-500/20 rounded-xl transition-colors"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <Badge 
            className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center text-xs bg-red-500 text-white border-0 p-0"
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </Badge>
        )}
      </button>

      {/* Notification Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Notification Panel */}
          <div className="absolute right-0 top-full mt-2 w-80 z-50">
            <Card className="border-0 shadow-xl bg-white">
              <CardContent className="p-0">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-slate-200">
                  <h3 className="font-semibold text-slate-900">Notifications</h3>
                  <div className="flex items-center gap-2">
                    {unreadCount > 0 && (
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={markAllAsRead}
                        className="text-xs text-purple-600 hover:text-purple-700 hover:bg-purple-50"
                      >
                        Mark all read
                      </Button>
                    )}
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => setIsOpen(false)}
                      className="p-1"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                {/* Notifications List */}
                <div className="max-h-96 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="text-center py-8">
                      <Bell className="h-12 w-12 mx-auto text-slate-400 mb-4" />
                      <p className="text-slate-500">No notifications yet</p>
                    </div>
                  ) : (
                    <div className="divide-y divide-slate-100">
                      {notifications.map((notification) => {
                        const Icon = notification.icon;
                        return (
                          <div
                            key={notification.id}
                            onClick={() => handleNotificationClick(notification)}
                            className={`p-4 hover:bg-slate-50 cursor-pointer transition-colors ${
                              !notification.read ? 'bg-purple-50 border-l-4 border-l-purple-500' : ''
                            }`}
                          >
                            <div className="flex items-start gap-3">
                              <div className={`flex-shrink-0 ${notification.color}`}>
                                <Icon className="h-5 w-5" />
                              </div>
                              
                              <div className="flex-1 min-w-0">
                                <div className="flex items-start justify-between">
                                  <h4 className={`font-medium text-sm ${
                                    !notification.read ? 'text-slate-900' : 'text-slate-700'
                                  }`}>
                                    {notification.title}
                                  </h4>
                                  
                                  <div className="flex items-center gap-1 ml-2">
                                    <span className="text-xs text-slate-500 whitespace-nowrap">
                                      {getRelativeTime(notification.timestamp)}
                                    </span>
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        removeNotification(notification.id);
                                      }}
                                      className="p-0.5 text-slate-400 hover:text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity"
                                    >
                                      <X className="h-3 w-3" />
                                    </button>
                                  </div>
                                </div>
                                
                                <p className={`text-sm mt-1 ${
                                  !notification.read ? 'text-slate-700' : 'text-slate-500'
                                }`}>
                                  {notification.message}
                                </p>

                                {!notification.read && (
                                  <div className="flex items-center gap-2 mt-2">
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        markAsRead(notification.id);
                                      }}
                                      className="flex items-center gap-1 text-xs text-purple-600 hover:text-purple-700"
                                    >
                                      <Check className="h-3 w-3" />
                                      Mark as read
                                    </button>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>

                {/* Footer */}
                {notifications.length > 0 && (
                  <div className="p-4 border-t border-slate-200 bg-slate-50">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="w-full text-purple-600 hover:text-purple-700 hover:bg-purple-50"
                      onClick={() => {
                        setIsOpen(false);
                        window.location.hash = '/notifications';
                      }}
                    >
                      View All Notifications
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
};

export default NotificationCenter;