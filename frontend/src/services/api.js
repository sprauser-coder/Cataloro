import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://217.154.0.82';
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (userData) => api.post('/auth/register', userData),
  getProfile: () => api.get('/profile'),
};

// Admin API
export const adminAPI = {
  getStats: () => api.get('/admin/stats'),
  getUsers: () => api.get('/admin/users'),
  getListings: () => api.get('/admin/listings'),
  getOrders: () => api.get('/admin/orders'),
  getSiteSettings: () => api.get('/admin/cms/settings'),
  updateSiteSettings: (settings) => api.put('/admin/cms/settings', settings),
};

// Marketplace API
export const marketplaceAPI = {
  getListings: (params) => api.get('/listings', { params }),
  getListingById: (id) => api.get(`/listings/${id}`),
  createListing: (listingData) => api.post('/listings', listingData),
  uploadImage: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/listings/upload-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  getCategories: () => api.get('/categories'),
};

// Orders API
export const ordersAPI = {
  getOrders: () => api.get('/orders'),
  createOrder: (orderData) => api.post('/orders', orderData),
  getOrderById: (id) => api.get(`/orders/${id}`),
};

// Favorites API
export const favoritesAPI = {
  getFavorites: () => api.get('/favorites'),
  addFavorite: (listingId) => api.post('/favorites', { listing_id: listingId }),
  removeFavorite: (favoriteId) => api.delete(`/favorites/${favoriteId}`),
};

export default api;