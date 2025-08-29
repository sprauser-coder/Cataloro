/**
 * CATALORO - Authentication Service
 * API calls for user authentication
 */

import axios from 'axios';
import { API_ENDPOINTS } from '../../config/directions';

class AuthService {
  constructor() {
    // Configure axios defaults
    axios.defaults.timeout = 10000;
    
    // Add request interceptor to include token
    axios.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('cataloro_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('cataloro_token');
          localStorage.removeItem('cataloro_user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async login(email, password) {
    try {
      const response = await axios.post(API_ENDPOINTS.AUTH.LOGIN, {
        email,
        password
      });

      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  async register(userData) {
    try {
      const response = await axios.post(API_ENDPOINTS.AUTH.REGISTER, userData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  }

  async logout() {
    try {
      await axios.post(API_ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('cataloro_token');
      localStorage.removeItem('cataloro_user');
    }
  }

  async getProfile(userId) {
    try {
      const response = await axios.get(API_ENDPOINTS.AUTH.PROFILE.replace('{user_id}', userId));
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch profile');
    }
  }

  async refreshToken() {
    try {
      const response = await axios.post(API_ENDPOINTS.AUTH.REFRESH);
      const { token } = response.data;
      
      localStorage.setItem('cataloro_token', token);
      return token;
    } catch (error) {
      throw new Error('Token refresh failed');
    }
  }

  isAuthenticated() {
    const token = localStorage.getItem('cataloro_token');
    return !!token;
  }

  getCurrentUser() {
    try {
      const user = localStorage.getItem('cataloro_user');
      return user ? JSON.parse(user) : null;
    } catch (error) {
      console.error('Error parsing user data:', error);
      return null;
    }
  }

  getToken() {
    return localStorage.getItem('cataloro_token');
  }
}

export const authService = new AuthService();
export default authService;