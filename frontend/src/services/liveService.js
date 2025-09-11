/**
 * CATALORO - Live Functionality Service
 * API service for favorites, messaging, and notifications
 */

import { ENV_CONFIG } from '../config/directions';

class LiveService {
  constructor() {
    this.baseURL = ENV_CONFIG.API_BASE_URL;
    this.rateLimitBackoff = {}; // Track rate limit backoff for different endpoints
  }

  // Rate limit handler with exponential backoff
  async handleRateLimitedRequest(url, options = {}, retryCount = 0) {
    const maxRetries = 3;
    const backoffKey = url.split('?')[0]; // Use base URL as key
    
    // Check if we're in backoff period for this endpoint
    if (this.rateLimitBackoff[backoffKey] && Date.now() < this.rateLimitBackoff[backoffKey]) {
      console.warn(`⏳ Rate limit backoff active for ${backoffKey} - skipping request`);
      throw new Error('Rate limit backoff - request skipped');
    }

    try {
      const response = await fetch(url, options);
      
      if (response.status === 429) {
        // Calculate backoff time: 2^retryCount * 30 seconds
        const backoffTime = Math.pow(2, retryCount) * 30000; // 30s, 60s, 120s, etc.
        this.rateLimitBackoff[backoffKey] = Date.now() + backoffTime;
        
        console.warn(`🚦 Rate limit hit for ${backoffKey} - backing off for ${backoffTime/1000}s`);
        
        if (retryCount < maxRetries) {
          // Wait and retry
          await new Promise(resolve => setTimeout(resolve, backoffTime));
          return this.handleRateLimitedRequest(url, options, retryCount + 1);
        } else {
          throw new Error('429 Too Many Requests - Max retries exceeded');
        }
      }
      
      // Clear backoff on successful request
      delete this.rateLimitBackoff[backoffKey];
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return response;
    } catch (error) {
      if (error.message.includes('429') || error.message.includes('Rate limit')) {
        throw error;
      }
      console.error('Request error:', error);
      throw error;
    }
  }

  // ============================================================================
  // FAVORITES API
  // ============================================================================
  
  async getUserFavorites(userId) {
    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await this.handleRateLimitedRequest(`${this.baseURL}/api/user/${userId}/favorites`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      return await response.json();
    } catch (error) {
      console.error('Error fetching favorites:', error);
      throw error;
    }
  }

  async addToFavorites(userId, itemId) {
    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${this.baseURL}/api/user/${userId}/favorites/${itemId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error adding to favorites:', error);
      throw error;
    }
  }

  async removeFromFavorites(userId, itemId) {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}/favorites/${itemId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error removing from favorites:', error);
      throw error;
    }
  }



  // ============================================================================
  // MESSAGING API
  // ============================================================================
  
  async getUserMessages(userId) {
    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${this.baseURL}/api/user/${userId}/messages`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching messages:', error);
      throw error;
    }
  }

  async sendMessage(messageData) {
    try {
      // Extract sender_id from messageData for the URL path
      const senderId = messageData.sender_id;
      if (!senderId) {
        throw new Error('sender_id is required in messageData');
      }
      
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${this.baseURL}/api/user/${senderId}/messages`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(messageData)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  async markMessageRead(userId, messageId) {
    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${this.baseURL}/api/user/${userId}/messages/${messageId}/read`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error marking message as read:', error);
      throw error;
    }
  }

  // ============================================================================
  // NOTIFICATIONS API
  // ============================================================================
  
  async getUserNotifications(userId) {
    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${this.baseURL}/api/user/${userId}/notifications`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching notifications:', error);
      throw error;
    }
  }

  async createNotification(userId, notificationData) {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}/notifications`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(notificationData)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error creating notification:', error);
      throw error;
    }
  }

  async markNotificationRead(userId, notificationId) {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}/notifications/${notificationId}/read`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error marking notification as read:', error);
      throw error;
    }
  }

  async searchUsers(query) {
    try {
      const response = await fetch(`${this.baseURL}/users/search?q=${encodeURIComponent(query)}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error searching users:', error);
      throw error;
    }
  }
}

export const liveService = new LiveService();
export default liveService;