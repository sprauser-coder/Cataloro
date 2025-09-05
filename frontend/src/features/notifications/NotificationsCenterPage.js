/**
 * CATALORO - Notifications Center Page
 * Extension of the header notification tab with full management capabilities
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Bell, 
  X, 
  CheckCircle, 
  AlertCircle, 
  Info, 
  Gift,
  Settings,
  Trash2,
  MarkAsUnreadIcon,
  Eye,
  EyeOff,
  Filter,
  Search,
  RefreshCw,
  Archive,
  Download,
  AlertTriangle,
  Check,
  Square,
  CheckSquare
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function NotificationsCenterPage() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // 'all', 'unread', 'read', 'archived'
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedNotifications, setSelectedNotifications] = useState([]);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null);
  const [bulkActionLoading, setBulkActionLoading] = useState(false);
  
  const { user } = useAuth();
  const { showToast } = useNotifications();

  useEffect(() => {
    loadNotifications();
  }, [user?.id]);

  useEffect(() => {
    // Keyboard shortcuts for bulk actions
    const handleKeyPress = (e) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'a':
            e.preventDefault();
            setSelectedNotifications(prev => {
              const allIds = filteredNotifications.map(n => n.id);
              return allIds.length > 0 ? allIds : [];
            });
            break;
          case 'd':
            e.preventDefault();
            setSelectedNotifications([]);
            break;
          case 'r':
            e.preventDefault();
            setSelectedNotifications(prev => {
              if (prev.length > 0) {
                markAsRead(prev);
              }
              return prev;
            });
            break;
          case 'Delete':
            e.preventDefault();
            setSelectedNotifications(prev => {
              if (prev.length > 0) {
                handleBulkAction(() => deleteNotifications(prev));
              }
              return prev;
            });
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []); // Remove selectedNotifications from dependency array to prevent re-renders

  const loadNotifications = async () => {
    try {
      setLoading(true);
      
      // Load notifications from backend using the corrected endpoint
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${user.id}/notifications`);
      
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)));
      } else {
        // Fallback - load from localStorage (header notifications)
        const headerNotifications = JSON.parse(localStorage.getItem('user_notifications') || '[]');
        setNotifications(headerNotifications);
      }
    } catch (error) {
      console.error('Error loading notifications:', error);
      showToast('Failed to load notifications', 'error');
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationIds) => {
    try {
      const idsArray = Array.isArray(notificationIds) ? notificationIds : [notificationIds];
      
      for (const id of idsArray) {
        await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${user.id}/notifications/${id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ read: true })
        });
      }
      
      // Update local state
      setNotifications(prev => 
        prev.map(notif => 
          idsArray.includes(notif.id) ? { ...notif, read: true } : notif
        )
      );
      
      showToast('Marked as read', 'success');
    } catch (error) {
      console.error('Error marking as read:', error);
      showToast('Failed to mark as read', 'error');
    }
  };

  const markAsUnread = async (notificationIds) => {
    try {
      const idsArray = Array.isArray(notificationIds) ? notificationIds : [notificationIds];
      
      for (const id of idsArray) {
        await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${user.id}/notifications/${id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ read: false })
        });
      }
      
      // Update local state
      setNotifications(prev => 
        prev.map(notif => 
          idsArray.includes(notif.id) ? { ...notif, read: false } : notif
        )
      );
      
      showToast('Marked as unread', 'success');
    } catch (error) {
      console.error('Error marking as unread:', error);
      showToast('Failed to mark as unread', 'error');
    }
  };

  const deleteNotifications = async (notificationIds) => {
    try {
      setBulkActionLoading(true);
      const idsArray = Array.isArray(notificationIds) ? notificationIds : [notificationIds];
      
      let successCount = 0;
      let failureCount = 0;
      
      for (const id of idsArray) {
        const notification = notifications.find(n => n.id === id);
        const notificationType = notification?.type || 'unknown';
        
        // Try multiple deletion endpoints for regular notifications only (system notifications are handled separately as toasts)
        const endpoints = [
          `api/user/${user.id}/notifications/${id}`,
          `api/notifications/${id}?user_id=${user.id}`
        ];
        
        let deleteSuccess = false;
        
        for (const endpoint of endpoints) {
          try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/${endpoint}`, {
              method: 'DELETE'
            });
            
            if (response.ok) {
              deleteSuccess = true;
              successCount++;
              console.log(`✅ Successfully deleted ${notificationType} notification via: ${endpoint}`);
              break;
            }
          } catch (error) {
            console.log(`❌ Delete attempt error for ${notificationType} via ${endpoint}:`, error);
          }
        }
        
        if (!deleteSuccess) {
          failureCount++;
          console.error(`❌ Failed to delete ${notificationType} notification with ID: ${id}`);
        }
      }
      
      // Update local state for successfully deleted notifications
      if (successCount > 0) {
        setNotifications(prev => prev.filter(notif => !idsArray.includes(notif.id) || 
          !notifications.find(n => n.id === notif.id && idsArray.includes(notif.id))));
        setSelectedNotifications([]);
      }
      
      // Show appropriate feedback
      if (failureCount === 0) {
        showToast(`Successfully deleted ${successCount} notification(s)`, 'success');
      } else if (successCount === 0) {
        showToast(`Failed to delete ${failureCount} notification(s). Please try again.`, 'error');
      } else {
        showToast(`Deleted ${successCount} notification(s), ${failureCount} failed. Please try again for the failed ones.`, 'warning');
      }
      
    } catch (error) {
      console.error('Error in bulk delete:', error);
      showToast('Failed to delete notifications', 'error');
    } finally {
      setBulkActionLoading(false);
    }
  };

  const archiveNotifications = async (notificationIds) => {
    try {
      setBulkActionLoading(true);
      const idsArray = Array.isArray(notificationIds) ? notificationIds : [notificationIds];
      
      for (const id of idsArray) {
        await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${user.id}/notifications/${id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ archived: true })
        });
      }
      
      // Update local state
      setNotifications(prev => 
        prev.map(notif => 
          idsArray.includes(notif.id) ? { ...notif, archived: true } : notif
        )
      );
      setSelectedNotifications([]);
      
      showToast(`Archived ${idsArray.length} notification(s)`, 'success');
    } catch (error) {
      console.error('Error archiving notifications:', error);
      showToast('Failed to archive notifications', 'error');
    } finally {
      setBulkActionLoading(false);
    }
  };

  const unarchiveNotifications = async (notificationIds) => {
    try {
      setBulkActionLoading(true);
      const idsArray = Array.isArray(notificationIds) ? notificationIds : [notificationIds];
      
      for (const id of idsArray) {
        await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${user.id}/notifications/${id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ archived: false })
        });
      }
      
      // Update local state
      setNotifications(prev => 
        prev.map(notif => 
          idsArray.includes(notif.id) ? { ...notif, archived: false } : notif
        )
      );
      setSelectedNotifications([]);
      
      showToast(`Unarchived ${idsArray.length} notification(s)`, 'success');
    } catch (error) {
      console.error('Error unarchiving notifications:', error);
      showToast('Failed to unarchive notifications', 'error');
    } finally {
      setBulkActionLoading(false);
    }
  };

  const exportNotifications = () => {
    try {
      const exportData = selectedNotifications.length > 0 
        ? notifications.filter(n => selectedNotifications.includes(n.id))
        : filteredNotifications;
      
      const csvContent = [
        ['Title', 'Message', 'Type', 'Read', 'Archived', 'Created At'].join(','),
        ...exportData.map(n => [
          `"${n.title || ''}"`,
          `"${(n.message || n.content || '').replace(/"/g, '""')}"`,
          n.type || 'info',
          n.read ? 'Yes' : 'No',
          n.archived ? 'Yes' : 'No',
          new Date(n.created_at || n.timestamp).toLocaleString()
        ].join(','))
      ].join('\n');
      
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `notifications-${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      showToast(`Exported ${exportData.length} notifications`, 'success');
    } catch (error) {
      console.error('Error exporting notifications:', error);
      showToast('Failed to export notifications', 'error');
    }
  };

  const handleBulkAction = (action) => {
    if (selectedNotifications.length === 0) {
      showToast('Please select notifications first', 'warning');
      return;
    }

    setConfirmAction(() => action);
    setShowConfirmDialog(true);
  };

  const confirmBulkAction = async () => {
    if (!confirmAction) return;
    
    setBulkActionLoading(true);
    setShowConfirmDialog(false);
    
    try {
      await confirmAction();
    } catch (error) {
      console.error('Bulk action error:', error);
    } finally {
      setBulkActionLoading(false);
      setConfirmAction(null);
    }
  };

  const cancelBulkAction = () => {
    setShowConfirmDialog(false);
    setConfirmAction(null);
  };

  const handleSingleDelete = async (notificationId, notificationType) => {
    try {
      // Enhanced deletion logic for different notification types and collections
      setBulkActionLoading(true);
      
      const endpoints = [
        `api/user/${user.id}/notifications/${notificationId}`,
        `api/notifications/${notificationId}?user_id=${user.id}`,
        `api/user/${user.id}/system-notifications/${notificationId}`
      ];
      
      let deleteSuccess = false;
      let lastError = null;
      
      // Try multiple endpoints to ensure deletion works for all notification types
      for (const endpoint of endpoints) {
        try {
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/${endpoint}`, {
            method: 'DELETE'
          });
          
          if (response.ok) {
            deleteSuccess = true;
            console.log(`✅ Successfully deleted notification via: ${endpoint}`);
            break;
          } else {
            console.log(`⚠️ Delete attempt failed via ${endpoint}: ${response.status}`);
          }
        } catch (error) {
          lastError = error;
          console.log(`❌ Delete attempt error via ${endpoint}:`, error);
        }
      }
      
      if (deleteSuccess) {
        // Update local state
        setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
        setSelectedNotifications(prev => prev.filter(id => id !== notificationId));
        showToast('Notification deleted successfully', 'success');
      } else {
        console.error('All deletion attempts failed:', lastError);
        showToast(`Failed to delete notification (${notificationType}). Please try again.`, 'error');
      }
    } catch (error) {
      console.error('Error in handleSingleDelete:', error);
      showToast('Failed to delete notification', 'error');
    } finally {
      setBulkActionLoading(false);
    }
  };

  const markAllAsRead = async () => {
    const unreadIds = notifications.filter(n => !n.read).map(n => n.id);
    if (unreadIds.length > 0) {
      await markAsRead(unreadIds);
    }
  };

  const toggleSelectNotification = (id) => {
    setSelectedNotifications(prev => 
      prev.includes(id) 
        ? prev.filter(nid => nid !== id)
        : [...prev, id]
    );
  };

  const selectAll = () => {
    setSelectedNotifications(filteredNotifications.map(n => n.id));
  };

  const deselectAll = () => {
    setSelectedNotifications([]);
  };

  // Filter notifications
  const filteredNotifications = notifications.filter(notification => {
    const matchesFilter = filter === 'all' || 
      (filter === 'unread' && !notification.read && !notification.archived) ||
      (filter === 'read' && notification.read && !notification.archived) ||
      (filter === 'archived' && notification.archived);
    
    const matchesSearch = !searchTerm || 
      notification.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      notification.message?.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesFilter && matchesSearch;
  });

  const getNotificationIcon = (type) => {
    const iconClass = "w-6 h-6";
    switch (type) {
      case 'success':
        return <CheckCircle className={`${iconClass} text-green-600`} />;
      case 'warning':
        return <AlertCircle className={`${iconClass} text-yellow-600`} />;
      case 'error':
        return <AlertCircle className={`${iconClass} text-red-600`} />;
      case 'info':
        return <Info className={`${iconClass} text-blue-600`} />;
      case 'welcome':
        return <Gift className={`${iconClass} text-purple-600`} />;
      case 'system':
        return <Settings className={`${iconClass} text-indigo-600`} />;
      case 'message':
        return <Bell className={`${iconClass} text-cyan-600`} />;
      case 'alert':
        return <AlertTriangle className={`${iconClass} text-orange-600`} />;
      case 'order':
      case 'order_complete':
        return <CheckCircle className={`${iconClass} text-green-600`} />;
      default:
        return <Bell className={`${iconClass} text-gray-600`} />;
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'success':
        return 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200 dark:from-green-900/20 dark:to-emerald-900/20 dark:border-green-700';
      case 'warning':
        return 'bg-gradient-to-r from-yellow-50 to-amber-50 border-yellow-200 dark:from-yellow-900/20 dark:to-amber-900/20 dark:border-yellow-700';
      case 'error':
        return 'bg-gradient-to-r from-red-50 to-rose-50 border-red-200 dark:from-red-900/20 dark:to-rose-900/20 dark:border-red-700';
      case 'info':
        return 'bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200 dark:from-blue-900/20 dark:to-cyan-900/20 dark:border-blue-700';
      case 'welcome':
        return 'bg-gradient-to-r from-purple-50 to-violet-50 border-purple-200 dark:from-purple-900/20 dark:to-violet-900/20 dark:border-purple-700';
      case 'system':
        return 'bg-gradient-to-r from-indigo-50 to-blue-50 border-indigo-200 dark:from-indigo-900/20 dark:to-blue-900/20 dark:border-indigo-700';
      case 'message':
        return 'bg-gradient-to-r from-cyan-50 to-teal-50 border-cyan-200 dark:from-cyan-900/20 dark:to-teal-900/20 dark:border-cyan-700';
      case 'alert':
        return 'bg-gradient-to-r from-orange-50 to-red-50 border-orange-200 dark:from-orange-900/20 dark:to-red-900/20 dark:border-orange-700';
      case 'order':
      case 'order_complete':
        return 'bg-gradient-to-r from-emerald-50 to-green-50 border-emerald-200 dark:from-emerald-900/20 dark:to-green-900/20 dark:border-emerald-700';
      default:
        return 'bg-gradient-to-r from-gray-50 to-slate-50 border-gray-200 dark:from-gray-800/50 dark:to-slate-800/50 dark:border-gray-700';
    }
  };

  if (loading) {
    return (
      <div className="fade-in">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Notifications Center</h1>
          <p className="text-gray-600 dark:text-gray-300">Manage all your notifications</p>
        </div>
        
        <div className="cataloro-card-glass p-8 text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">Loading notifications...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Notifications Center</h1>
        <p className="text-gray-600 dark:text-gray-300">
          Manage all your system notifications and alerts
        </p>
      </div>

      {/* Controls */}
      <div className="cataloro-card-glass p-6 mb-8">
        <div className="flex flex-col space-y-4">
          
          {/* Top Row: Search, Filter, and Actions */}
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            
            {/* Search and Filter */}
            <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 flex-1">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search notifications..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-3 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="flex items-center space-x-2">
                <Filter className="w-5 h-5 text-gray-400" />
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All Notifications</option>
                  <option value="unread">Unread Only</option>
                  <option value="read">Read Only</option>
                  <option value="archived">Archived</option>
                </select>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col lg:flex-row lg:items-center space-y-3 lg:space-y-0 lg:space-x-4">
              <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                <span className="flex items-center">
                  <Bell className="w-4 h-4 mr-1" />
                  {filteredNotifications.length} of {notifications.length}
                </span>
                <span className="flex items-center">
                  <Eye className="w-4 h-4 mr-1" />
                  {notifications.filter(n => !n.read).length} unread
                </span>
                <span className="flex items-center">
                  <Archive className="w-4 h-4 mr-1" />
                  {notifications.filter(n => n.archived).length} archived
                </span>
              </div>
              
              <div className="flex items-center space-x-3">
                <button
                  onClick={loadNotifications}
                  className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
                  title="Refresh (Ctrl+R)"
                >
                  <RefreshCw className="w-5 h-5" />
                </button>

                <button
                  onClick={markAllAsRead}
                  className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                  title="Mark All Read (Ctrl+Shift+R)"
                >
                  Mark All Read
                </button>

                <button
                  onClick={exportNotifications}
                  className="px-4 py-2 bg-indigo-100 text-indigo-700 text-sm font-medium rounded-lg hover:bg-indigo-200 transition-colors flex items-center"
                  title="Export All (Ctrl+E)"
                >
                  <Download className="w-4 h-4 mr-1" />
                  Export All
                </button>
              </div>
            </div>
          </div>

          {/* Master Selection Row */}
          {filteredNotifications.length > 0 && (
            <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-4">
                {/* Master Checkbox */}
                <div 
                  className={`w-6 h-6 rounded-lg border-2 transition-all duration-200 flex items-center justify-center cursor-pointer ${
                    selectedNotifications.length === filteredNotifications.length && filteredNotifications.length > 0
                      ? 'bg-purple-500 border-purple-500 shadow-lg'
                      : selectedNotifications.length > 0
                        ? 'bg-purple-200 border-purple-400'
                        : 'border-gray-300 dark:border-gray-600 hover:border-purple-400 dark:hover:border-purple-500'
                  }`}
                  onClick={() => {
                    if (selectedNotifications.length === filteredNotifications.length) {
                      deselectAll();
                    } else {
                      selectAll();
                    }
                  }}
                >
                  {selectedNotifications.length === filteredNotifications.length && filteredNotifications.length > 0 ? (
                    <Check className="w-4 h-4 text-white" />
                  ) : selectedNotifications.length > 0 ? (
                    <div className="w-2 h-2 bg-purple-600 rounded-sm"></div>
                  ) : null}
                </div>
                
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {selectedNotifications.length === filteredNotifications.length && filteredNotifications.length > 0
                    ? `All ${filteredNotifications.length} notifications selected`
                    : selectedNotifications.length > 0
                      ? `${selectedNotifications.length} of ${filteredNotifications.length} notifications selected`
                      : `Select notifications for bulk actions`
                  }
                </span>

                {selectedNotifications.length > 0 && (
                  <button
                    onClick={deselectAll}
                    className="text-sm text-purple-600 dark:text-purple-400 hover:text-purple-800 dark:hover:text-purple-200 flex items-center"
                  >
                    <X className="w-4 h-4 mr-1" />
                    Clear Selection
                  </button>
                )}
              </div>

              <div className="text-sm text-gray-500 dark:text-gray-400">
                Use Ctrl+A to select all, Ctrl+D to deselect
              </div>
            </div>
          )}

          {/* Bulk Actions */}
          {selectedNotifications.length > 0 && (
            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
                <div className="flex items-center space-x-2">
                  <CheckSquare className="w-5 h-5 text-purple-600" />
                  <span className="font-medium text-gray-900 dark:text-white">
                    Bulk Actions for {selectedNotifications.length} selected notifications
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={() => markAsRead(selectedNotifications)}
                    disabled={bulkActionLoading}
                    className="px-4 py-2 bg-green-100 text-green-700 text-sm font-medium rounded-lg hover:bg-green-200 transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Eye className="w-4 h-4 mr-1" />
                    Mark Read
                  </button>
                  
                  <button
                    onClick={() => markAsUnread(selectedNotifications)}
                    disabled={bulkActionLoading}
                    className="px-4 py-2 bg-blue-100 text-blue-700 text-sm font-medium rounded-lg hover:bg-blue-200 transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <EyeOff className="w-4 h-4 mr-1" />
                    Mark Unread
                  </button>
                  
                  <button
                    onClick={() => handleBulkAction(() => archiveNotifications(selectedNotifications))}
                    disabled={bulkActionLoading}
                    className="px-4 py-2 bg-yellow-100 text-yellow-700 text-sm font-medium rounded-lg hover:bg-yellow-200 transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Archive className="w-4 h-4 mr-1" />
                    Archive
                  </button>

                  {filter === 'archived' && (
                    <button
                      onClick={() => handleBulkAction(() => unarchiveNotifications(selectedNotifications))}
                      disabled={bulkActionLoading}
                      className="px-4 py-2 bg-purple-100 text-purple-700 text-sm font-medium rounded-lg hover:bg-purple-200 transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Archive className="w-4 h-4 mr-1" />
                      Unarchive
                    </button>
                  )}
                  
                  <button
                    onClick={exportNotifications}
                    disabled={bulkActionLoading}
                    className="px-4 py-2 bg-indigo-100 text-indigo-700 text-sm font-medium rounded-lg hover:bg-indigo-200 transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Download className="w-4 h-4 mr-1" />
                    Export Selected
                  </button>
                  
                  <button
                    onClick={() => handleBulkAction(() => deleteNotifications(selectedNotifications))}
                    disabled={bulkActionLoading}
                    className="px-4 py-2 bg-red-100 text-red-700 text-sm font-medium rounded-lg hover:bg-red-200 transition-colors flex items-center disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                  >
                    <Trash2 className="w-4 h-4 mr-1" />
                    Delete Selected
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Notifications List */}
      {filteredNotifications.length === 0 ? (
        <div className="cataloro-card-glass p-12 text-center">
          <Bell className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            {searchTerm ? 'No matching notifications' : 'No notifications'}
          </h3>
          <p className="text-gray-600 dark:text-gray-300">
            {searchTerm 
              ? `No notifications match your search for "${searchTerm}"`
              : filter === 'unread' 
                ? "You're all caught up! No unread notifications."
                : "You don't have any notifications yet."
            }
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredNotifications.map((notification) => (
            <div
              key={notification.id}
              className={`group relative overflow-hidden rounded-2xl border transition-all duration-300 hover:shadow-lg ${
                getNotificationColor(notification.type)
              } ${!notification.read ? 'ring-2 ring-blue-200 dark:ring-blue-700 shadow-md' : ''} ${
                notification.archived ? 'opacity-75 border-dashed' : ''
              } ${selectedNotifications.includes(notification.id) ? 'ring-2 ring-purple-500 shadow-lg transform scale-[1.02]' : ''}`}
            >
              {/* Selection Overlay */}
              {selectedNotifications.includes(notification.id) && (
                <div className="absolute inset-0 bg-purple-500/10 dark:bg-purple-400/10"></div>
              )}

              <div className="p-6">
                <div className="flex items-start space-x-4">
                  {/* Enhanced Checkbox */}
                  <div className="flex-shrink-0 pt-1">
                    <div 
                      className={`w-6 h-6 rounded-lg border-2 transition-all duration-200 flex items-center justify-center cursor-pointer ${
                        selectedNotifications.includes(notification.id)
                          ? 'bg-purple-500 border-purple-500 shadow-lg'
                          : 'border-gray-300 dark:border-gray-600 hover:border-purple-400 dark:hover:border-purple-500'
                      }`}
                      onClick={() => toggleSelectNotification(notification.id)}
                    >
                      {selectedNotifications.includes(notification.id) && (
                        <Check className="w-4 h-4 text-white" />
                      )}
                    </div>
                  </div>

                  {/* Notification Icon */}
                  <div className="flex-shrink-0 pt-1">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                      selectedNotifications.includes(notification.id) ? 'scale-110' : ''
                    } transition-transform duration-200`}>
                      {getNotificationIcon(notification.type)}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <h4 className="text-lg font-semibold text-gray-900 dark:text-white line-clamp-1">
                          {notification.title}
                        </h4>
                        
                        {/* Status Badges */}
                        <div className="flex items-center space-x-2">
                          {!notification.read && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                              <span className="w-2 h-2 bg-blue-500 rounded-full mr-1"></span>
                              New
                            </span>
                          )}
                          
                          {notification.archived && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300">
                              <Archive className="w-3 h-3 mr-1" />
                              Archived
                            </span>
                          )}

                          {notification.type === 'system' && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300">
                              <Settings className="w-3 h-3 mr-1" />
                              System
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                        <span>{new Date(notification.created_at || notification.timestamp).toLocaleString()}</span>
                      </div>
                    </div>

                    <p className="text-gray-700 dark:text-gray-300 mb-4 line-clamp-2">
                      {notification.message || notification.content}
                    </p>

                    {/* Enhanced Actions */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {!notification.read ? (
                          <button
                            onClick={() => markAsRead(notification.id)}
                            className="inline-flex items-center px-3 py-1.5 bg-blue-100 text-blue-700 text-sm font-medium rounded-lg hover:bg-blue-200 transition-colors"
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            Mark Read
                          </button>
                        ) : (
                          <button
                            onClick={() => markAsUnread(notification.id)}
                            className="inline-flex items-center px-3 py-1.5 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 transition-colors"
                          >
                            <EyeOff className="w-4 h-4 mr-1" />
                            Mark Unread
                          </button>
                        )}

                        {!notification.archived ? (
                          <button
                            onClick={() => archiveNotifications(notification.id)}
                            className="inline-flex items-center px-3 py-1.5 bg-yellow-100 text-yellow-700 text-sm font-medium rounded-lg hover:bg-yellow-200 transition-colors"
                          >
                            <Archive className="w-4 h-4 mr-1" />
                            Archive
                          </button>
                        ) : (
                          <button
                            onClick={() => unarchiveNotifications(notification.id)}
                            className="inline-flex items-center px-3 py-1.5 bg-purple-100 text-purple-700 text-sm font-medium rounded-lg hover:bg-purple-200 transition-colors"
                          >
                            <Archive className="w-4 h-4 mr-1" />
                            Unarchive
                          </button>
                        )}
                      </div>

                      <button
                        onClick={() => handleSingleDelete(notification.id, notification.type)}
                        className="inline-flex items-center px-3 py-1.5 bg-red-100 text-red-700 text-sm font-medium rounded-lg hover:bg-red-200 transition-colors group-hover:shadow-md"
                      >
                        <Trash2 className="w-4 h-4 mr-1" />
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Load More */}
      {filteredNotifications.length > 0 && filteredNotifications.length < notifications.length && (
        <div className="text-center mt-8">
          <button className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium">
            Load More Notifications
          </button>
        </div>
      )}

      {/* Confirmation Dialog */}
      {showConfirmDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md mx-4 shadow-2xl">
            <div className="flex items-center mb-4">
              <AlertTriangle className="w-6 h-6 text-yellow-500 mr-3" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Confirm Bulk Action
              </h3>
            </div>
            
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              Are you sure you want to perform this action on {selectedNotifications.length} selected notification{selectedNotifications.length > 1 ? 's' : ''}? This action cannot be undone.
            </p>
            
            <div className="flex space-x-3">
              <button
                onClick={confirmBulkAction}
                disabled={bulkActionLoading}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {bulkActionLoading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                ) : (
                  <Check className="w-4 h-4 mr-2" />
                )}
                Confirm
              </button>
              
              <button
                onClick={cancelBulkAction}
                disabled={bulkActionLoading}
                className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <X className="w-4 h-4 mr-2" />
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default NotificationsCenterPage;