/**
 * CATALORO - Notification Service  
 * API calls for notification management
 */

import axios from 'axios';
import { API_ENDPOINTS } from '../../config/directions';

class NotificationService {
  async getUserNotifications(userId) {
    try {
      const response = await axios.get(API_ENDPOINTS.USER.NOTIFICATIONS.replace('{user_id}', userId));
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch notifications');
    }
  }

  async markAsRead(notificationId) {
    try {
      await axios.put(`${API_ENDPOINTS.USER.NOTIFICATIONS}/${notificationId}/read`);
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to mark notification as read');
    }
  }

  async markAllAsRead(userId) {
    try {
      await axios.put(`${API_ENDPOINTS.USER.NOTIFICATIONS.replace('{user_id}', userId)}/read-all`);
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to mark all notifications as read');
    }
  }

  async deleteNotification(notificationId) {
    try {
      await axios.delete(`${API_ENDPOINTS.USER.NOTIFICATIONS}/${notificationId}`);
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete notification');
    }
  }
}

export const notificationService = new NotificationService();
export default notificationService;