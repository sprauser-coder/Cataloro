/**
 * CATALORO - Central Configuration & Directions
 * All paths, URLs, and resources should reference this file
 * NO HARDCODED PATHS ALLOWED IN OTHER FILES!
 */

// Environment Detection - Force development for localhost
const isDevelopment = true; // Always use development in this environment
const isProduction = false;

// API Configuration
export const API_CONFIG = {
  // Development URLs (Emergent environment)
  development: {
    BACKEND_URL: process.env.REACT_APP_BACKEND_URL || 'https://d79e004a-2868-4b55-a561-f41324cbae81.preview.emergentagent.com:8001',
    FRONTEND_URL: 'https://d79e004a-2868-4b55-a561-f41324cbae81.preview.emergentagent.com'
  },
  // Production URLs (Your server)
  production: {
    BACKEND_URL: 'http://217.154.0.82/api',
    FRONTEND_URL: 'http://217.154.0.82'
  }
};

// Current Environment URLs
export const CURRENT_ENV = isDevelopment ? API_CONFIG.development : API_CONFIG.production;

// API Endpoints
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: `${CURRENT_ENV.BACKEND_URL}/api/auth/login`,
    REGISTER: `${CURRENT_ENV.BACKEND_URL}/api/auth/register`,
    LOGOUT: `${CURRENT_ENV.BACKEND_URL}/api/auth/logout`,
    PROFILE: `${CURRENT_ENV.BACKEND_URL}/api/auth/profile`,
    REFRESH: `${CURRENT_ENV.BACKEND_URL}/api/auth/refresh`
  },
  
  // Marketplace
  MARKETPLACE: {
    LISTINGS: `${CURRENT_ENV.BACKEND_URL}/api/marketplace/listings`,
    BROWSE: `${CURRENT_ENV.BACKEND_URL}/api/marketplace/browse`,
    FAVORITES: `${CURRENT_ENV.BACKEND_URL}/api/marketplace/favorites`,
    SEARCH: `${CURRENT_ENV.BACKEND_URL}/api/marketplace/search`
  },
  
  // User Management
  USER: {
    MY_LISTINGS: `${CURRENT_ENV.BACKEND_URL}/api/user/my-listings`,
    MY_DEALS: `${CURRENT_ENV.BACKEND_URL}/api/user/my-deals`,
    NOTIFICATIONS: `${CURRENT_ENV.BACKEND_URL}/api/user/notifications`,
    PROFILE: `${CURRENT_ENV.BACKEND_URL}/api/user/profile`
  },
  
  // Admin
  ADMIN: {
    DASHBOARD: `${CURRENT_ENV.BACKEND_URL}/api/admin/dashboard`,
    USERS: `${CURRENT_ENV.BACKEND_URL}/api/admin/users`,
    SETTINGS: `${CURRENT_ENV.BACKEND_URL}/api/admin/settings`,
    KPIS: `${CURRENT_ENV.BACKEND_URL}/api/admin/kpis`,
    LOGO: `${CURRENT_ENV.BACKEND_URL}/api/admin/logo`
  }
};

// Application Routes (Frontend)
export const APP_ROUTES = {
  HOME: '/',
  BROWSE: '/browse',
  MY_LISTINGS: '/my-listings',
  MY_DEALS: '/my-deals',
  ADMIN_PANEL: '/admin',
  FAVORITES: '/favorites',
  NOTIFICATIONS: '/notifications',
  PROFILE: '/profile',
  LOGIN: '/login',
  REGISTER: '/register'
};

// UI Configuration
export const UI_CONFIG = {
  APP_NAME: 'Cataloro',
  LOGO_URL: '/assets/logo.png',
  DEFAULT_AVATAR: '/assets/default-avatar.png',
  PAGINATION_SIZE: 12,
  NOTIFICATION_TIMEOUT: 5000
};

// User Roles
export const USER_ROLES = {
  USER: 'user',
  ADMIN: 'admin',
  MODERATOR: 'moderator'
};

// Status Constants
export const LISTING_STATUS = {
  ACTIVE: 'active',
  SOLD: 'sold',
  DRAFT: 'draft',
  EXPIRED: 'expired'
};

export const DEAL_STATUS = {
  PENDING: 'pending',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled',
  DISPUTED: 'disputed'
};

// Deployment Configuration
export const DEPLOYMENT_CONFIG = {
  SSH_HOST: '217.154.0.82',
  DEPLOY_PATH: '/var/www',
  APP_NAME: 'cataloro'
};

export default {
  API_CONFIG,
  CURRENT_ENV,
  API_ENDPOINTS,
  APP_ROUTES,
  UI_CONFIG,
  USER_ROLES,
  LISTING_STATUS,
  DEAL_STATUS,
  DEPLOYMENT_CONFIG
};