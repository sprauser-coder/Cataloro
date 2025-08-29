/**
 * CATALORO - Notification Context
 * Global notification state management
 */

import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { notificationService } from '../services/notificationService';
import { useAuth } from './AuthContext';

// Initial state
const initialState = {
  notifications: [],
  unreadCount: 0,
  isLoading: false,
  error: null
};

// Action types
const NOTIFICATION_ACTIONS = {
  FETCH_START: 'FETCH_START',
  FETCH_SUCCESS: 'FETCH_SUCCESS',
  FETCH_FAILURE: 'FETCH_FAILURE',
  MARK_AS_READ: 'MARK_AS_READ',
  MARK_ALL_AS_READ: 'MARK_ALL_AS_READ',
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION'
};

// Reducer
function notificationReducer(state, action) {
  switch (action.type) {
    case NOTIFICATION_ACTIONS.FETCH_START:
      return {
        ...state,
        isLoading: true,
        error: null
      };
    case NOTIFICATION_ACTIONS.FETCH_SUCCESS:
      const notifications = action.payload;
      const unreadCount = notifications.filter(n => !n.is_read).length;
      return {
        ...state,
        notifications,
        unreadCount,
        isLoading: false,
        error: null
      };
    case NOTIFICATION_ACTIONS.FETCH_FAILURE:
      return {
        ...state,
        isLoading: false,
        error: action.payload
      };
    case NOTIFICATION_ACTIONS.MARK_AS_READ:
      const updatedNotifications = state.notifications.map(n =>
        n.id === action.payload ? { ...n, is_read: true } : n
      );
      return {
        ...state,
        notifications: updatedNotifications,
        unreadCount: Math.max(0, state.unreadCount - 1)
      };
    case NOTIFICATION_ACTIONS.MARK_ALL_AS_READ:
      return {
        ...state,
        notifications: state.notifications.map(n => ({ ...n, is_read: true })),
        unreadCount: 0
      };
    case NOTIFICATION_ACTIONS.ADD_NOTIFICATION:
      return {
        ...state,
        notifications: [action.payload, ...state.notifications],
        unreadCount: state.unreadCount + 1
      };
    case NOTIFICATION_ACTIONS.REMOVE_NOTIFICATION:
      const filteredNotifications = state.notifications.filter(n => n.id !== action.payload);
      return {
        ...state,
        notifications: filteredNotifications,
        unreadCount: filteredNotifications.filter(n => !n.is_read).length
      };
    default:
      return state;
  }
}

// Create context
const NotificationContext = createContext();

// Provider component
export function NotificationProvider({ children }) {
  const [state, dispatch] = useReducer(notificationReducer, initialState);
  
  // Don't access auth during initialization - will be handled by components that need it
  // const { user, isAuthenticated } = useAuth();

  // Fetch notifications when user is authenticated - will be called by components
  // useEffect(() => {
  //   if (isAuthenticated && user?.id) {
  //     fetchNotifications();
  //   }
  // }, [isAuthenticated, user?.id]);

  // Actions
  const fetchNotifications = async (userId = null) => {
    if (!userId) return;

    dispatch({ type: NOTIFICATION_ACTIONS.FETCH_START });
    
    try {
      const notifications = await notificationService.getUserNotifications(userId);
      dispatch({
        type: NOTIFICATION_ACTIONS.FETCH_SUCCESS,
        payload: notifications
      });
    } catch (error) {
      dispatch({
        type: NOTIFICATION_ACTIONS.FETCH_FAILURE,
        payload: error.message
      });
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await notificationService.markAsRead(notificationId);
      dispatch({
        type: NOTIFICATION_ACTIONS.MARK_AS_READ,
        payload: notificationId
      });
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async (userId = null) => {
    if (!userId) return;

    try {
      await notificationService.markAllAsRead(user.id);
      dispatch({ type: NOTIFICATION_ACTIONS.MARK_ALL_AS_READ });
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  const addNotification = (notification) => {
    dispatch({
      type: NOTIFICATION_ACTIONS.ADD_NOTIFICATION,
      payload: {
        id: Date.now().toString(),
        user_id: user?.id,
        created_at: new Date().toISOString(),
        is_read: false,
        ...notification
      }
    });
  };

  const removeNotification = (notificationId) => {
    dispatch({
      type: NOTIFICATION_ACTIONS.REMOVE_NOTIFICATION,
      payload: notificationId
    });
  };

  // Show toast notification (for UI feedback)
  const showToast = (message, type = 'info') => {
    addNotification({
      title: type.charAt(0).toUpperCase() + type.slice(1),
      message,
      type
    });

    // Auto-remove after 5 seconds
    setTimeout(() => {
      removeNotification(Date.now().toString());
    }, 5000);
  };

  const value = {
    // State
    ...state,
    
    // Actions
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    addNotification,
    removeNotification,
    showToast
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}

// Custom hook to use notification context
export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
}

export default NotificationContext;