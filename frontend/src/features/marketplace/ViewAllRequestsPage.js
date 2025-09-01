/**
 * CATALORO - View All Requests Page
 * Comprehensive page for viewing all buy/sell requests (both as buyer and seller)
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
  RefreshCw,
  Filter,
  Eye,
  ArrowUpDown,
  ShoppingBag,
  DollarSign
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import { Link } from 'react-router-dom';

function ViewAllRequestsPage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  
  const [buyerOrders, setBuyerOrders] = useState([]);
  const [sellerOrders, setSellerOrders] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [processingOrder, setProcessingOrder] = useState(null);
  const [activeTab, setActiveTab] = useState('buyer'); // buyer, seller, all
  const [statusFilter, setStatusFilter] = useState('all'); // all, pending, approved, rejected, expired
  const [sortBy, setSortBy] = useState('newest'); // newest, oldest, price_high, price_low

  useEffect(() => {
    if (user) {
      fetchAllOrders();
    }
  }, [user]);

  const fetchAllOrders = async () => {
    if (!user) return;
    
    setIsLoading(true);
    try {
      // Fetch buyer orders
      const buyerResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/orders/buyer/${user.id}`);
      if (buyerResponse.ok) {
        const buyerData = await buyerResponse.json();
        setBuyerOrders(buyerData);
      }

      // Fetch seller orders  
      const sellerResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/orders/seller/${user.id}`);
      if (sellerResponse.ok) {
        const sellerData = await sellerResponse.json();
        setSellerOrders(sellerData);
      }
    } catch (error) {
      console.error('Error fetching orders:', error);
      showToast('Failed to load requests', 'error');
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

      if (response.ok) {
        showToast('Request approved successfully!', 'success');
        fetchAllOrders();
      } else {
        const data = await response.json();
        showToast(data.detail || 'Failed to approve request', 'error');
      }
    } catch (error) {
      console.error('Error approving order:', error);
      showToast('Failed to approve request', 'error');
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

      if (response.ok) {
        showToast('Request rejected', 'info');
        fetchAllOrders();
      } else {
        const data = await response.json();
        showToast(data.detail || 'Failed to reject request', 'error');
      }
    } catch (error) {
      console.error('Error rejecting order:', error);
      showToast('Failed to reject request', 'error');
    } finally {
      setProcessingOrder(null);
    }
  };

  const handleCancelOrder = async (orderId) => {
    setProcessingOrder(orderId);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/orders/${orderId}/cancel`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          buyer_id: user.id
        })
      });

      if (response.ok) {
        showToast('Request cancelled successfully', 'success');
        fetchAllOrders();
      } else {
        const data = await response.json();
        showToast(data.detail || 'Failed to cancel request', 'error');
      }
    } catch (error) {
      console.error('Error cancelling order:', error);
      showToast('Failed to cancel request', 'error');
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
      return `${days}d ${remainingHours}h`;
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'approved':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'rejected':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'expired':
        return 'text-gray-600 bg-gray-50 border-gray-200';
      case 'cancelled':
        return 'text-orange-600 bg-orange-50 border-orange-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4" />;
      case 'approved':
        return <CheckCircle className="w-4 h-4" />;
      case 'rejected':
        return <XCircle className="w-4 h-4" />;
      case 'expired':
        return <Calendar className="w-4 h-4" />;
      case 'cancelled':
        return <XCircle className="w-4 h-4" />;
      default:
        return <Package className="w-4 h-4" />;
    }
  };

  const filterAndSortOrders = (orders, type) => {
    let filtered = orders;

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(order => order.status === statusFilter);
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'oldest':
          return new Date(a.created_at) - new Date(b.created_at);
        case 'price_high':
          return (b.listing?.price || 0) - (a.listing?.price || 0);
        case 'price_low':
          return (a.listing?.price || 0) - (b.listing?.price || 0);
        case 'newest':
        default:
          return new Date(b.created_at) - new Date(a.created_at);
      }
    });

    return filtered;
  };

  const getDisplayOrders = () => {
    if (activeTab === 'buyer') {
      return filterAndSortOrders(buyerOrders, 'buyer');
    } else if (activeTab === 'seller') {
      return filterAndSortOrders(sellerOrders, 'seller');
    } else {
      return filterAndSortOrders([...buyerOrders, ...sellerOrders], 'all');
    }
  };

  const getTotalStats = () => {
    const allOrders = [...buyerOrders, ...sellerOrders];
    return {
      total: allOrders.length,
      pending: allOrders.filter(o => o.status === 'pending').length,
      approved: allOrders.filter(o => o.status === 'approved').length,
      totalValue: allOrders.reduce((sum, o) => sum + (o.listing?.price || 0), 0)
    };
  };

  const stats = getTotalStats();
  const displayOrders = getDisplayOrders();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading all requests...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
            <ShoppingBag className="w-8 h-8 mr-3 text-blue-600" />
            All Requests
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage all your buy and sell requests in one place
          </p>
        </div>
        <button
          onClick={fetchAllOrders}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
              <Package className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.total}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">Total Requests</p>
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
                {stats.pending}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">Pending</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-xl">
              <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.approved}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">Approved</p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-xl">
              <DollarSign className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                €{stats.totalValue.toFixed(2)}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">Total Value</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Tabs */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          {/* Tabs */}
          <div className="flex space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('buyer')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'buyer'
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow'
                  : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              My Purchases ({buyerOrders.length})
            </button>
            <button
              onClick={() => setActiveTab('seller')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'seller'
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow'
                  : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              My Sales ({sellerOrders.length})
            </button>
            <button
              onClick={() => setActiveTab('all')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'all'
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow'
                  : 'text-gray-600 dark:text-gray-400'
              }`}
            >
              All Requests ({stats.total})
            </button>
          </div>

          {/* Filters */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="expired">Expired</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            <div className="flex items-center space-x-2">
              <ArrowUpDown className="w-4 h-4 text-gray-500" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="price_high">Price: High to Low</option>
                <option value="price_low">Price: Low to High</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Orders List */}
      {displayOrders.length === 0 ? (
        <div className="text-center py-12">
          <Package className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-2">
            No requests found
          </h3>
          <p className="text-gray-500 dark:text-gray-500">
            {activeTab === 'buyer' && 'You haven\'t made any purchase requests yet.'}
            {activeTab === 'seller' && 'You haven\'t received any sale requests yet.'}
            {activeTab === 'all' && 'No requests match your current filters.'}
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {displayOrders.map((order) => {
            const isBuyerOrder = buyerOrders.some(bo => bo.id === order.id);
            return (
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
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                            {order.listing?.title || 'Unknown Item'}
                          </h3>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(order.status)}`}>
                            {getStatusIcon(order.status)}
                            <span className="ml-1 capitalize">{order.status}</span>
                          </span>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            isBuyerOrder ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
                          }`}>
                            {isBuyerOrder ? 'Purchase' : 'Sale'}
                          </span>
                        </div>
                        
                        <p className="text-2xl font-bold text-green-600 dark:text-green-400 mb-2">
                          €{order.listing?.price?.toFixed(2) || '0.00'}
                        </p>

                        {/* User Info */}
                        <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                          <div className="flex items-center space-x-2">
                            <User className="w-4 h-4" />
                            <span>
                              {isBuyerOrder 
                                ? `Seller: ${order.seller?.username || 'Unknown'}`
                                : `Buyer: ${order.buyer?.username || 'Unknown'}`
                              }
                            </span>
                          </div>
                          {(order.status === 'approved' && order.seller?.email) && (
                            <div className="flex items-center space-x-2">
                              <Mail className="w-4 h-4" />
                              <span>{order.seller.email}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Time/Status Info */}
                    <div className="text-right">
                      {order.status === 'pending' && (
                        <div className="text-sm font-medium text-yellow-600 dark:text-yellow-400 mb-1">
                          <Clock className="w-4 h-4 inline mr-1" />
                          {formatTimeRemaining(order.expires_at)} remaining
                        </div>
                      )}
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        <Calendar className="w-3 h-3 inline mr-1" />
                        Created {new Date(order.created_at).toLocaleDateString()}
                      </div>
                      {order.approved_at && (
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          Approved {new Date(order.approved_at).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                    {order.status === 'pending' && !isBuyerOrder && (
                      <>
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
                      </>
                    )}

                    {order.status === 'pending' && isBuyerOrder && (
                      <button
                        onClick={() => handleCancelOrder(order.id)}
                        disabled={processingOrder === order.id}
                        className="flex items-center space-x-2 px-4 py-2 border border-red-300 text-red-700 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                      >
                        <XCircle className="w-4 h-4" />
                        <span>Cancel Request</span>
                      </button>
                    )}

                    <Link
                      to={`/product/${order.listing?.id}`}
                      className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                    >
                      <Eye className="w-4 h-4" />
                      <span>View Listing</span>
                    </Link>

                    {order.status === 'approved' && (
                      <button className="flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors">
                        <MessageCircle className="w-4 h-4" />
                        <span>Message</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default ViewAllRequestsPage;