/**
 * CATALORO - Pending Sales Page
 * Page for sellers to manage incoming buy requests
 */

import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  User, 
  Euro, 
  CheckCircle, 
  XCircle, 
  MessageCircle,
  Package,
  Calendar,
  Mail,
  RefreshCw
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function PendingSalesPage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const [pendingOrders, setPendingOrders] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [processingOrder, setProcessingOrder] = useState(null);

  useEffect(() => {
    if (user) {
      fetchPendingOrders();
    }
  }, [user]);

  const fetchPendingOrders = async () => {
    if (!user) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/orders/seller/${user.id}`);
      if (response.ok) {
        const orders = await response.json();
        setPendingOrders(orders);
      } else {
        console.error('Failed to fetch pending orders');
        showToast('Failed to load pending orders', 'error');
      }
    } catch (error) {
      console.error('Error fetching pending orders:', error);
      showToast('Failed to load pending orders', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApproveOrder = async (orderId) => {
    setProcessingOrder(orderId);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/orders/${orderId}/approve`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          seller_id: user.id
        })
      });

      const data = await response.json();

      if (response.ok) {
        showToast('Buy request approved! The buyer has been notified.', 'success');
        fetchPendingOrders(); // Refresh the list
      } else if (response.status === 410) {
        showToast('This request has expired', 'warning');
        fetchPendingOrders(); // Refresh to remove expired orders
      } else {
        showToast(data.detail || 'Failed to approve request', 'error');
      }
    } catch (error) {
      console.error('Error approving order:', error);
      showToast('Failed to approve request. Please try again.', 'error');
    } finally {
      setProcessingOrder(null);
    }
  };

  const handleRejectOrder = async (orderId) => {
    setProcessingOrder(orderId);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/orders/${orderId}/reject`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          seller_id: user.id
        })
      });

      const data = await response.json();

      if (response.ok) {
        showToast('Buy request rejected. The buyer has been notified.', 'info');
        fetchPendingOrders(); // Refresh the list
      } else {
        showToast(data.detail || 'Failed to reject request', 'error');
      }
    } catch (error) {
      console.error('Error rejecting order:', error);
      showToast('Failed to reject request. Please try again.', 'error');
    } finally {
      setProcessingOrder(null);
    }
  };

  const formatTimeRemaining = (expiresAt) => {
    const now = new Date();
    const expires = new Date(expiresAt);
    const diff = expires.getTime() - now.getTime();
    
    if (diff <= 0) {
      return 'Expired';
    }
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 24) {
      const days = Math.floor(hours / 24);
      const remainingHours = hours % 24;
      return `${days}d ${remainingHours}h remaining`;
    } else if (hours > 0) {
      return `${hours}h ${minutes}m remaining`;
    } else {
      return `${minutes}m remaining`;
    }
  };

  const getTimeRemainingColor = (expiresAt) => {
    const now = new Date();
    const expires = new Date(expiresAt);
    const diff = expires.getTime() - now.getTime();
    const hoursRemaining = diff / (1000 * 60 * 60);
    
    if (hoursRemaining <= 0) return 'text-red-600 dark:text-red-400';
    if (hoursRemaining <= 6) return 'text-orange-600 dark:text-orange-400';
    if (hoursRemaining <= 24) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-green-600 dark:text-green-400';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading pending sales...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Pending Sales
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage incoming buy requests for your listings
          </p>
        </div>
        <button
          onClick={fetchPendingOrders}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
              <Package className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                {pendingOrders.length}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">Pending Requests</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-xl">
              <Euro className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                €{pendingOrders.reduce((sum, order) => sum + (order.listing?.price || 0), 0).toFixed(2)}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">Potential Revenue</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-xl">
              <Clock className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                {pendingOrders.filter(order => {
                  const expires = new Date(order.expires_at);
                  const now = new Date();
                  return (expires.getTime() - now.getTime()) / (1000 * 60 * 60) <= 6;
                }).length}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">Expiring Soon</p>
            </div>
          </div>
        </div>
      </div>

      {/* Pending Orders List */}
      {pendingOrders.length === 0 ? (
        <div className="text-center py-12">
          <Package className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-2">
            No pending buy requests
          </h3>
          <p className="text-gray-500 dark:text-gray-500">
            When someone wants to buy your items, they'll appear here.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {pendingOrders.map((order) => (
            <div
              key={order.id}
              className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start space-x-4">
                    {/* Listing Image */}
                    <div className="w-20 h-20 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700 flex-shrink-0">
                      {order.listing?.image ? (
                        <img
                          src={order.listing.image}
                          alt={order.listing.title}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <Package className="w-8 h-8 text-gray-400" />
                        </div>
                      )}
                    </div>

                    {/* Order Details */}
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                        {order.listing?.title || 'Unknown Item'}
                      </h3>
                      <p className="text-2xl font-bold text-green-600 dark:text-green-400 mb-2">
                        €{order.listing?.price?.toFixed(2) || '0.00'}
                      </p>

                      {/* Buyer Info */}
                      <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                        <div className="flex items-center space-x-2">
                          <User className="w-4 h-4" />
                          <span>
                            {order.buyer?.full_name || order.buyer?.username || 'Unknown Buyer'}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Mail className="w-4 h-4" />
                          <span>{order.buyer?.email || 'N/A'}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Time Remaining */}
                  <div className="text-right">
                    <div className={`text-sm font-medium ${getTimeRemainingColor(order.expires_at)}`}>
                      <Clock className="w-4 h-4 inline mr-1" />
                      {formatTimeRemaining(order.expires_at)}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      <Calendar className="w-3 h-3 inline mr-1" />
                      Requested {new Date(order.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={() => handleRejectOrder(order.id)}
                    disabled={processingOrder === order.id}
                    className="flex items-center space-x-2 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
                  >
                    <XCircle className="w-4 h-4" />
                    <span>Reject</span>
                  </button>

                  <button
                    onClick={() => handleApproveOrder(order.id)}
                    disabled={processingOrder === order.id}
                    className="flex items-center space-x-2 px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
                  >
                    <CheckCircle className="w-4 h-4" />
                    <span>
                      {processingOrder === order.id ? 'Processing...' : 'Approve Sale'}
                    </span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PendingSalesPage;