/**
 * CATALORO - Centralized Configuration
 * All routes, URLs, and constants in one place
 */

// Environment configuration
export const ENV_CONFIG = {
  FRONTEND_URL: process.env.REACT_APP_FRONTEND_URL || 'http://localhost:3000',
  BACKEND_URL: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001',
  API_BASE_URL: process.env.REACT_APP_BACKEND_URL ? `${process.env.REACT_APP_BACKEND_URL}/api` : 'http://localhost:8001/api'
};

// Application routes
export const APP_ROUTES = {
  // Auth routes
  LOGIN: '/login',
  REGISTER: '/register',
  
  // Main marketplace routes
  HOME: '/',
  BROWSE: '/browse',
  CATEGORIES: '/categories',
  SEARCH: '/search',
  CART: '/cart',
  
  // User routes
  MY_LISTINGS: '/my-listings',
  MY_DEALS: '/my-deals',
  FAVORITES: '/favorites',
  PROFILE: '/profile',
  NOTIFICATIONS: '/notifications',
  
  // Admin routes
  ADMIN_PANEL: '/admin',
  ADMIN_USERS: '/admin/users',
  ADMIN_ANALYTICS: '/admin/analytics'
};

// API endpoints
export const API_ENDPOINTS = {
  // Auth endpoints
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  LOGOUT: '/auth/logout',
  PROFILE: '/auth/profile',
  
  // User endpoints
  USERS: '/users',
  USER_PROFILE: '/users/profile',
  
  // Marketplace endpoints
  PRODUCTS: '/products',
  CATEGORIES: '/categories',
  SEARCH: '/search',
  
  // Orders endpoints
  ORDERS: '/orders',
  CHECKOUT: '/orders/checkout',
  
  // Notifications endpoints
  NOTIFICATIONS: '/notifications',
  
  // Admin endpoints
  ADMIN: {
    DASHBOARD: '/admin/dashboard',
    KPIS: '/admin/kpis',
    USERS: '/admin/users',
    SETTINGS: '/admin/settings',
    LOGO: '/admin/logo',
    STATS: '/admin/stats'
  }
};

// User roles
export const USER_ROLES = {
  USER: 'user',
  MODERATOR: 'moderator', 
  ADMIN: 'admin'
};

// Application constants
export const APP_CONSTANTS = {
  APP_NAME: 'Cataloro',
  APP_DESCRIPTION: 'Ultra-Modern Marketplace',
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
  SUPPORTED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
  PAGINATION_LIMIT: 20,
  SEARCH_DEBOUNCE_MS: 300,
  NOTIFICATION_TIMEOUT: 5000
};

// Theme configuration
export const THEME_CONFIG = {
  PRIMARY_COLOR: 'blue',
  SECONDARY_COLOR: 'purple',
  SUCCESS_COLOR: 'green',
  ERROR_COLOR: 'red',
  WARNING_COLOR: 'yellow',
  INFO_COLOR: 'blue'
};

export default {
  ENV_CONFIG,
  APP_ROUTES,
  API_ENDPOINTS,
  USER_ROLES,
  APP_CONSTANTS,
  THEME_CONFIG
};