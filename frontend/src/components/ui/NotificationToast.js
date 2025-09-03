/**
 * CATALORO - Modern Notification Toast System
 * Beautiful toast notifications with animations - Integrated with Admin System Notifications
 */

import React, { useState, useEffect } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle, Bell } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

function NotificationToast() {
  const [toasts, setToasts] = useState([]);
  const { user, isAuthenticated } = useAuth();

  // Load system notifications from backend instead of hardcoded demo
  useEffect(() => {
    if (isAuthenticated && user?.id) {
      loadSystemNotifications();
    }
  }, [isAuthenticated, user?.id]);

  const loadSystemNotifications = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${user.id}/system-notifications`);
      if (response.ok) {
        const data = await response.json();
        const notifications = data.notifications || [];
        
        // Show each system notification as a toast
        notifications.forEach((notification, index) => {
          setTimeout(() => {
            addToast(
              notification.message, 
              notification.type || 'info', 
              notification.show_duration || 5000,
              notification.id
            );
            
            // Mark as viewed after displaying
            markNotificationViewed(notification.id);
          }, index * 1000); // Stagger multiple notifications
        });
      }
    } catch (error) {
      console.error('Error loading system notifications:', error);
    }
  };

  const markNotificationViewed = async (notificationId) => {
    try {
      await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${user.id}/system-notifications/${notificationId}/view`, {
        method: 'POST'
      });
    } catch (error) {
      console.error('Error marking notification as viewed:', error);
    }
  };

  const addToast = (message, type = 'info', duration = 5000) => {
    const id = Date.now() + Math.random();
    const newToast = { id, message, type, duration };
    
    setToasts(prev => [...prev, newToast]);

    // Auto remove after duration
    setTimeout(() => {
      removeToast(id);
    }, duration);
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const getToastIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-orange-600" />;
      default:
        return <Info className="w-5 h-5 text-blue-600" />;
    }
  };

  const getToastStyles = (type) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200';
      case 'error':
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200';
      case 'warning':
        return 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800 text-orange-800 dark:text-orange-200';
      default:
        return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200';
    }
  };

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-20 right-4 z-50 space-y-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`max-w-sm w-full ${getToastStyles(toast.type)} border rounded-lg p-4 shadow-lg backdrop-blur-sm transition-all duration-300 transform animate-slide-in-right`}
        >
          <div className="flex items-start">
            <div className="flex-shrink-0">
              {getToastIcon(toast.type)}
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-medium">{toast.message}</p>
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              className="ml-4 flex-shrink-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

export default NotificationToast;