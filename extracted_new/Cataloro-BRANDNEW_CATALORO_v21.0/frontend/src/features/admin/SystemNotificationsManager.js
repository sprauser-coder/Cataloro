/**
 * CATALORO - Admin System Notifications Manager
 * Manage green toast notifications that appear in the top right corner
 */

import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Bell, 
  AlertCircle, 
  CheckCircle, 
  Info, 
  Settings, 
  Users, 
  Clock, 
  Eye,
  Save,
  X,
  Calendar,
  Zap
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function SystemNotificationsManager() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingNotification, setEditingNotification] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    message: '',
    type: 'success',
    event_trigger: 'manual',
    target_users: 'all',
    user_ids: [],
    show_duration: 5000,
    delay_before_show: 0,
    expires_at: '',
    auto_dismiss: true,
    is_active: true
  });

  const { user } = useAuth();
  const { showToast } = useNotifications();

  // Event trigger options
  const eventTriggers = [
    { value: 'manual', label: 'Manual Trigger', description: 'Show immediately when activated' },
    { value: 'login', label: 'User Login', description: 'Show when user logs in' },
    { value: 'first_login', label: 'First Login', description: 'Show only on user\'s first login' },
    { value: 'profile_update', label: 'Profile Update', description: 'Show after profile is updated' },
    { value: 'purchase_complete', label: 'Purchase Complete', description: 'Show after successful purchase' },
    { value: 'listing_published', label: 'Listing Published', description: 'Show after listing is published' },
    { value: 'message_received', label: 'Message Received', description: 'Show when user receives a message' },
    { value: 'daily', label: 'Daily', description: 'Show once per day' },
    { value: 'weekly', label: 'Weekly', description: 'Show once per week' }
  ];

  // Notification types with colors
  const notificationTypes = [
    { value: 'success', label: 'Success', color: 'green', icon: CheckCircle },
    { value: 'info', label: 'Information', color: 'blue', icon: Info },
    { value: 'warning', label: 'Warning', color: 'yellow', icon: AlertCircle },
    { value: 'error', label: 'Error', color: 'red', icon: AlertCircle },
    { value: 'welcome', label: 'Welcome', color: 'purple', icon: Bell }
  ];

  useEffect(() => {
    loadSystemNotifications();
  }, []);

  const loadSystemNotifications = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/system-notifications`);
      
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
      } else {
        throw new Error('Failed to load notifications');
      }
    } catch (error) {
      console.error('Error loading system notifications:', error);
      showToast('Failed to load system notifications', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateNotification = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/system-notifications`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          created_by: user.id,
          expires_at: formData.expires_at || null
        })
      });

      if (response.ok) {
        showToast('System notification created successfully!', 'success');
        setShowCreateModal(false);
        resetForm();
        loadSystemNotifications();
      } else {
        throw new Error('Failed to create notification');
      }
    } catch (error) {
      console.error('Error creating notification:', error);
      showToast('Failed to create notification', 'error');
    }
  };

  const handleUpdateNotification = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/system-notifications/${editingNotification.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          expires_at: formData.expires_at || null
        })
      });

      if (response.ok) {
        showToast('System notification updated successfully!', 'success');
        setEditingNotification(null);
        resetForm();
        loadSystemNotifications();
      } else {
        throw new Error('Failed to update notification');
      }
    } catch (error) {
      console.error('Error updating notification:', error);
      showToast('Failed to update notification', 'error');
    }
  };

  const handleDeleteNotification = async (notificationId) => {
    if (!window.confirm('Are you sure you want to delete this system notification?')) {
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/system-notifications/${notificationId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        showToast('System notification deleted successfully!', 'success');
        loadSystemNotifications();
      } else {
        throw new Error('Failed to delete notification');
      }
    } catch (error) {
      console.error('Error deleting notification:', error);
      showToast('Failed to delete notification', 'error');
    }
  };

  const handleToggleActive = async (notification) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/system-notifications/${notification.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !notification.is_active })
      });

      if (response.ok) {
        showToast(`Notification ${!notification.is_active ? 'activated' : 'deactivated'}!`, 'success');
        loadSystemNotifications();
      } else {
        throw new Error('Failed to toggle notification');
      }
    } catch (error) {
      console.error('Error toggling notification:', error);
      showToast('Failed to toggle notification', 'error');
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      message: '',
      type: 'success',
      event_trigger: 'manual',
      target_users: 'all',
      user_ids: [],
      show_duration: 5000,
      delay_before_show: 0,
      expires_at: '',
      auto_dismiss: true,
      is_active: true
    });
  };

  const openEditModal = (notification) => {
    setEditingNotification(notification);
    setFormData({
      title: notification.title || '',
      message: notification.message || '',
      type: notification.type || 'success',
      event_trigger: notification.event_trigger || 'manual', // Default to 'manual' if missing
      target_users: notification.target_users || 'all',
      user_ids: notification.user_ids || [],
      show_duration: notification.show_duration || 5000,
      delay_before_show: notification.delay_before_show || 0,
      expires_at: notification.expires_at ? notification.expires_at.split('T')[0] : '',
      auto_dismiss: notification.auto_dismiss !== false,
      is_active: notification.is_active !== false
    });
  };

  const getTypeIcon = (type) => {
    const typeConfig = notificationTypes.find(t => t.value === type);
    const IconComponent = typeConfig?.icon || Bell;
    return <IconComponent className="w-5 h-5" />;
  };

  const getTypeColor = (type) => {
    const typeConfig = notificationTypes.find(t => t.value === type);
    return typeConfig?.color || 'gray';
  };

  const getEventTriggerLabel = (trigger) => {
    // Handle missing or null event_trigger field by defaulting to 'manual'
    const eventTrigger = trigger || 'manual';
    const eventConfig = eventTriggers.find(e => e.value === eventTrigger);
    return eventConfig?.label || 'Manual Trigger';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
            <Bell className="w-7 h-7 mr-3 text-green-600" />
            System Notifications Manager
          </h2>
          <p className="text-gray-600 dark:text-gray-300 mt-1">
            Manage green toast notifications that appear in the top right corner
          </p>
        </div>
        
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Notification
        </button>
      </div>

      {/* Notifications List */}
      <div className="grid grid-cols-1 gap-4">
        {notifications.length === 0 ? (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-xl">
            <Bell className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-2">
              No System Notifications
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Create your first system notification to manage green toast messages
            </p>
          </div>
        ) : (
          notifications.map((notification) => (
            <div key={notification.id} className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  {/* Type Icon */}
                  <div className={`p-3 rounded-lg bg-${getTypeColor(notification.type)}-100 text-${getTypeColor(notification.type)}-600`}>
                    {getTypeIcon(notification.type)}
                  </div>
                  
                  {/* Content */}
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {notification.title}
                      </h3>
                      
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        notification.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {notification.is_active ? 'Active' : 'Inactive'}
                      </span>
                      
                      <span className={`px-2 py-1 rounded-full text-xs font-medium bg-${getTypeColor(notification.type)}-100 text-${getTypeColor(notification.type)}-800`}>
                        {notification.type}
                      </span>
                    </div>
                    
                    <p className="text-gray-700 dark:text-gray-300 mb-3">
                      {notification.message}
                    </p>
                    
                    {/* Metadata */}
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600 dark:text-gray-400">
                      <div className="flex items-center">
                        <Zap className="w-4 h-4 mr-1" />
                        <span>{getEventTriggerLabel(notification.event_trigger)}</span>
                      </div>
                      
                      <div className="flex items-center">
                        <Users className="w-4 h-4 mr-1" />
                        <span>{notification.target_users === 'all' ? 'All Users' : 'Specific Users'}</span>
                      </div>
                      
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-1" />
                        <span>{notification.show_duration / 1000}s duration</span>
                      </div>
                      
                      <div className="flex items-center">
                        <Eye className="w-4 h-4 mr-1" />
                        <span>{notification.display_count || 0} views</span>
                      </div>
                    </div>
                    
                    {notification.expires_at && (
                      <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                        <Calendar className="w-4 h-4 inline mr-1" />
                        Expires: {new Date(notification.expires_at).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleToggleActive(notification)}
                    className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                      notification.is_active 
                        ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200' 
                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                    }`}
                  >
                    {notification.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                  
                  <button
                    onClick={() => openEditModal(notification)}
                    className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-lg hover:bg-blue-200 transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  
                  <button
                    onClick={() => handleDeleteNotification(notification.id)}
                    className="px-3 py-1 bg-red-100 text-red-700 text-sm rounded-lg hover:bg-red-200 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create/Edit Modal */}
      {(showCreateModal || editingNotification) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  {editingNotification ? 'Edit System Notification' : 'Create New System Notification'}
                </h3>
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setEditingNotification(null);
                    resetForm();
                  }}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            <form onSubmit={editingNotification ? handleUpdateNotification : handleCreateNotification} className="p-6 space-y-6">
              {/* Basic Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Notification Title *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="e.g., Welcome to the new Cataloro!"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Notification Type *
                  </label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    {notificationTypes.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Message Content *
                </label>
                <textarea
                  value={formData.message}
                  onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Enter the notification message that will appear in the green toast..."
                  required
                />
              </div>

              {/* Trigger and Timing */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Event Trigger *
                  </label>
                  <select
                    value={formData.event_trigger}
                    onChange={(e) => setFormData(prev => ({ ...prev, event_trigger: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    {eventTriggers.map(trigger => (
                      <option key={trigger.value} value={trigger.value}>{trigger.label}</option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    {eventTriggers.find(t => t.value === formData.event_trigger)?.description}
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Target Users
                  </label>
                  <select
                    value={formData.target_users}
                    onChange={(e) => setFormData(prev => ({ ...prev, target_users: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="all">All Users</option>
                    <option value="new_users">New Users Only</option>
                    <option value="returning_users">Returning Users</option>
                    <option value="specific_ids">Specific User IDs</option>
                  </select>
                </div>
              </div>

              {/* Timing Settings */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Delay Before Show (ms)
                  </label>
                  <input
                    type="number"
                    value={formData.delay_before_show}
                    onChange={(e) => setFormData(prev => ({ ...prev, delay_before_show: parseInt(e.target.value) || 0 }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    min="0"
                    step="500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Show Duration (ms)
                  </label>
                  <input
                    type="number"
                    value={formData.show_duration}
                    onChange={(e) => setFormData(prev => ({ ...prev, show_duration: parseInt(e.target.value) || 5000 }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    min="1000"
                    step="1000"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Expires On (Optional)
                  </label>
                  <input
                    type="date"
                    value={formData.expires_at}
                    onChange={(e) => setFormData(prev => ({ ...prev, expires_at: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
              </div>

              {/* Options */}
              <div className="flex items-center space-x-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.auto_dismiss}
                    onChange={(e) => setFormData(prev => ({ ...prev, auto_dismiss: e.target.checked }))}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Auto Dismiss</span>
                </label>
                
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Active</span>
                </label>
              </div>

              {/* Actions */}
              <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateModal(false);
                    setEditingNotification(null);
                    resetForm();
                  }}
                  className="px-4 py-2 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingNotification ? 'Update' : 'Create'} Notification
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default SystemNotificationsManager;