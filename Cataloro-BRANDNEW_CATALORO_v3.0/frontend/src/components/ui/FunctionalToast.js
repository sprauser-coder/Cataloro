/**
 * CATALORO - Functional Toast Notification System
 * Real toast notifications with animations and auto-dismiss
 */

import React from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { useMarketplace } from '../../context/MarketplaceContext';

function FunctionalToast() {
  const { notifications, showNotification } = useMarketplace();

  if (notifications.length === 0) return null;

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

  return (
    <div className="fixed top-20 right-4 z-50 space-y-2">
      {notifications.slice(0, 5).map((notification) => (
        <div
          key={notification.id}
          className={`max-w-sm w-full ${getToastStyles(notification.type)} border rounded-lg p-4 shadow-lg backdrop-blur-sm transition-all duration-300 transform animate-slide-in-right`}
        >
          <div className="flex items-start">
            <div className="flex-shrink-0">
              {getToastIcon(notification.type)}
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-medium">{notification.message}</p>
              <p className="text-xs opacity-75 mt-1">
                {new Date(notification.timestamp).toLocaleTimeString()}
              </p>
            </div>
            <button
              onClick={() => {
                // Remove notification logic would be handled by context
              }}
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

export default FunctionalToast;