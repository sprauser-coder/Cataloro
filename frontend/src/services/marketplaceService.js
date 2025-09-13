/**
 * CATALORO - Marketplace Service
 * API calls for marketplace functionality
 */

import axios from 'axios';
import { API_ENDPOINTS, ENV_CONFIG } from '../config/directions';

class MarketplaceService {
  async browseListings(filters = {}, userId = null, page = 1, pageSize = 40) {
    try {
      const params = new URLSearchParams(filters);
      
      // Add pagination parameters
      params.append('limit', pageSize.toString());
      params.append('offset', ((page - 1) * pageSize).toString());
      
      // Add user_id if provided
      if (userId) {
        params.append('user_id', userId);
      }
      
      // Add bid_filter if provided
      if (filters.bidFilter && filters.bidFilter !== 'all') {
        params.append('bid_filter', filters.bidFilter);
      }
      
      console.log('🌐 API call to browse - page:', page, 'pageSize:', pageSize, 'filters:', filters);
      
      // Use the browse endpoint that now returns {listings: [], pagination: {}}
      const response = await axios.get(`${ENV_CONFIG.API_BASE_URL}/api/marketplace/browse?${params}`);
      
      // The API now returns {listings: [], pagination: {}} instead of just an array
      if (response.data && response.data.listings) {
        console.log('🌐 API response - listings:', response.data.listings.length, 'pagination:', response.data.pagination);
        return response.data; // Return the full response with pagination metadata
      } else {
        // Fallback for old API format (just array)
        console.log('🌐 API response - fallback array format:', response.data.length);
        return {
          listings: response.data,
          pagination: {
            current_page: page,
            total_pages: 1,
            total_count: response.data.length,
            page_size: pageSize,
            has_next: false,
            has_prev: false
          }
        };
      }
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch listings');
    }
  }

  async getMyListings(userId) {
    try {
      // Get all listings with high limit to ensure consistency with tenders overview count
      const response = await axios.get(API_ENDPOINTS.USER.MY_LISTINGS.replace('{user_id}', userId), {
        params: {
          status: 'all', // Get all statuses for frontend filtering
          limit: 1000 // High limit to get all listings (matching tenders overview unlimited behavior)
        }
      });
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