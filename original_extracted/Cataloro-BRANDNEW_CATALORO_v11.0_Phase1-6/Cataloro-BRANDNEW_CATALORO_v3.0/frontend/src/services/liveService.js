/**
 * CATALORO - Live Functionality Service
 * API service for favorites, cart, messaging, and notifications
 */

import { ENV_CONFIG } from '../config/directions';

class LiveService {
  constructor() {
    this.baseURL = ENV_CONFIG.API_BASE_URL;
  }

  // ============================================================================
  // FAVORITES API
  // ============================================================================
  
  async getUserFavorites(userId) {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}/favorites`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching favorites:', error);
      throw error;
    }
  }

  async addToFavorites(userId, itemId) {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}/favorites/${itemId}`, {
        method: 'POST',
        headers: {
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
  // CART API
  // ============================================================================
  
  async getUserCart(userId) {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}/cart`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching cart:', error);
      throw error;
    }
  }

  async addToCart(userId, cartItem) {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}/cart`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(cartItem)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error adding to cart:', error);
      throw error;
    }
  }

  async updateCartItem(userId, itemId, updateData) {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}/cart/${itemId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error updating cart item:', error);
      throw error;
    }
  }

  async removeFromCart(userId, itemId) {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}/cart/${itemId}`, {
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
      console.error('Error removing from cart:', error);
      throw error;
    }
  }

  // ============================================================================
  // MESSAGING API
  // ============================================================================
  
  async getUserMessages(userId) {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}/messages`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching messages:', error);
      throw error;
    }
  }

  async sendMessage(userId, messageData) {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}/messages`, {
        method: 'POST',
        headers: {
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
      const response = await fetch(`${this.baseURL}/user/${userId}/messages/${messageId}/read`, {
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
      console.error('Error marking message as read:', error);
      throw error;
    }
  }

  // ============================================================================
  // NOTIFICATIONS API
  // ============================================================================
  
  async getUserNotifications(userId) {
    try {
      const response = await fetch(`${this.baseURL}/user/${userId}/notifications`);
      
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