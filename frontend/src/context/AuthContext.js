/**
 * CATALORO - Authentication Context
 * Global authentication state management
 */

import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authService } from '../services/authService';
import { USER_ROLES } from '../config/directions';

// Initial state
const initialState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null
};

// Action types
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  SET_USER: 'SET_USER',
  CLEAR_ERROR: 'CLEAR_ERROR'
};

// Reducer
function authReducer(state, action) {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
      return {
        ...state,
        isLoading: true,
        error: null
      };
    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
        error: null
      };
    case AUTH_ACTIONS.LOGIN_FAILURE:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload
      };
    case AUTH_ACTIONS.LOGOUT:
      return {
        ...initialState
      };
    case AUTH_ACTIONS.SET_USER:
      return {
        ...state,
        user: action.payload
      };
    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };
    default:
      return state;
  }
}

// Create context
const AuthContext = createContext();

// Provider component
export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize auth state from localStorage
  useEffect(() => {
    const token = localStorage.getItem('cataloro_token');
    const user = localStorage.getItem('cataloro_user');
    
    if (token && user) {
      try {
        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: {
            token,
            user: JSON.parse(user)
          }
        });
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        localStorage.removeItem('cataloro_token');
        localStorage.removeItem('cataloro_user');
      }
    }
  }, []);

  // Auth actions
  const login = async (email, password) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });
    
    try {
      const response = await authService.login(email, password);
      
      // Store in localStorage
      localStorage.setItem('cataloro_token', response.token);
      localStorage.setItem('cataloro_user', JSON.stringify(response.user));
      
      dispatch({
        type: AUTH_ACTIONS.LOGIN_SUCCESS,
        payload: response
      });
      
      return response;
    } catch (error) {
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: error.message
      });
      throw error;
    }
  };

  const register = async (userData) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });
    
    try {
      const response = await authService.register(userData);
      
      // Auto-login after registration
      if (response.user_id) {
        return await login(userData.email, userData.password);
      }
      
      return response;
    } catch (error) {
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: error.message
      });
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('cataloro_token');
    localStorage.removeItem('cataloro_user');
    dispatch({ type: AUTH_ACTIONS.LOGOUT });
  };

  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  const updateUser = (updatedUserData) => {
    // Update localStorage
    localStorage.setItem('cataloro_user', JSON.stringify(updatedUserData));
    
    // Update context state
    dispatch({
      type: AUTH_ACTIONS.SET_USER,
      payload: updatedUserData
    });
  };

  // Helper functions
  const isAdmin = () => {
    return state.user?.role === USER_ROLES.ADMIN;
  };

  const isModerator = () => {
    return state.user?.role === USER_ROLES.MODERATOR || isAdmin();
  };

  const hasPermission = (requiredRole) => {
    if (!state.user) return false;
    
    const roleHierarchy = {
      [USER_ROLES.USER]: 1,
      [USER_ROLES.MODERATOR]: 2,
      [USER_ROLES.ADMIN]: 3
    };
    
    return roleHierarchy[state.user.role] >= roleHierarchy[requiredRole];
  };

  const value = {
    // State
    ...state,
    
    // Actions
    login,
    register,
    logout,
    clearError,
    
    // Helpers
    isAdmin,
    isModerator,
    hasPermission
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;