/**
 * CATALORO - Marketplace Service
 * API calls for marketplace functionality
 */

import axios from 'axios';
import { API_ENDPOINTS, ENV_CONFIG } from '../config/directions';

class MarketplaceService {
  async browseListings(filters = {}, userId = null) {
    try {
      const params = new URLSearchParams(filters);
      
      // Add user_id if provided
      if (userId) {
        params.append('user_id', userId);
      }
      
      // Add bid_filter if provided
      if (filters.bidFilter && filters.bidFilter !== 'all') {
        params.append('bid_filter', filters.bidFilter);
      }
      
      // Use the browse endpoint that returns array format instead of listings endpoint
      const response = await axios.get(`${ENV_CONFIG.API_BASE_URL}/api/marketplace/browse?${params}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch listings');
    }
  }

  async getMyListings(userId) {
    try {
      const response = await axios.get(API_ENDPOINTS.USER.MY_LISTINGS.replace('{user_id}', userId));
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch your listings');
    }
  }

  async getMyDeals(userId) {
    try {
      const response = await axios.get(API_ENDPOINTS.USER.MY_DEALS.replace('{user_id}', userId));
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch your deals');
    }
  }

  async createListing(listingData) {
    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await axios.post(`${ENV_CONFIG.API_BASE_URL}/api/listings`, listingData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to create listing');
    }
  }

  async updateListing(listingId, updateData) {
    try {
      const response = await axios.put(`${API_ENDPOINTS.MARKETPLACE.LISTINGS}/${listingId}`, updateData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to update listing');
    }
  }

  async deleteListing(listingId) {
    try {
      await axios.delete(`${API_ENDPOINTS.MARKETPLACE.LISTINGS}/${listingId}`);
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete listing');
    }
  }

  async searchListings(query) {
    try {
      const response = await axios.get(`${API_ENDPOINTS.MARKETPLACE.SEARCH}?q=${encodeURIComponent(query)}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Search failed');
    }
  }
}

export const marketplaceService = new MarketplaceService();
export default marketplaceService;