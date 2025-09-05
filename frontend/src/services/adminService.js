/**
 * CATALORO - Admin Service
 * API calls for administrative functions
 */

import axios from 'axios';
import { API_ENDPOINTS } from '../config/directions';

class AdminService {
  async getDashboard() {
    try {
      // Add cache-busting parameter to force fresh data
      const response = await axios.get(`${API_ENDPOINTS.ADMIN.DASHBOARD}?_t=${Date.now()}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch dashboard data');
    }
  }

  async getKPIs() {
    try {
      const response = await axios.get(API_ENDPOINTS.ADMIN.KPIS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch KPIs');
    }
  }

  async getAllUsers() {
    try {
      const response = await axios.get(API_ENDPOINTS.ADMIN.USERS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch users');
    }
  }

  async updateUser(userId, userData) {
    try {
      const response = await axios.put(API_ENDPOINTS.ADMIN.USERS.replace('{user_id}', userId), userData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update user');
    }
  }

  async deleteUser(userId) {
    try {
      await axios.delete(`${API_ENDPOINTS.ADMIN.USERS}/${userId}`);
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete user');
    }
  }

  async suspendUser(userId) {
    try {
      const response = await axios.put(`${API_ENDPOINTS.ADMIN.USERS}/${userId}/suspend`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to suspend user');
    }
  }

  async activateUser(userId) {
    try {
      const response = await axios.put(`${API_ENDPOINTS.ADMIN.USERS}/${userId}/activate`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to activate user');
    }
  }

  async getSettings() {
    try {
      const response = await axios.get(API_ENDPOINTS.ADMIN.SETTINGS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch settings');
    }
  }

  async updateSettings(settings) {
    try {
      const response = await axios.put(API_ENDPOINTS.ADMIN.SETTINGS, settings);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update settings');
    }
  }

  async uploadLogo(logoFile) {
    try {
      const formData = new FormData();
      formData.append('logo', logoFile);
      
      const response = await axios.post(API_ENDPOINTS.ADMIN.LOGO, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to upload logo');
    }
  }

  async getSystemStats() {
    try {
      const response = await axios.get(`${API_ENDPOINTS.ADMIN.DASHBOARD}/stats`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch system stats');
    }
  }
}

export const adminService = new AdminService();
export default adminService;