import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://cataloro-hub.preview.emergentagent.com';
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
  getListingsCount: (params) => api.get('/listings/count', { params }),
  searchListings: (query, params) => api.get('/listings/search', { params: { q: query, ...params } }),
  createListing: (listingData) => api.post('/listings', listingData),
  updateListing: (id, listingData) => api.put(`/listings/${id}`, listingData),
  deleteListing: (id) => api.delete(`/listings/${id}`),
  uploadImage: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/listings/upload-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  getCategories: () => api.get('/categories'),
  addToCart: (listingId, quantity = 1) => api.post('/cart', { listing_id: listingId, quantity }),
  placeBid: (listingId, bidAmount) => api.post(`/listings/${listingId}/bid`, { amount: bidAmount }),
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