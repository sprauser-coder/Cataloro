/**
 * CATALORO - Deals Page
 * All executed listings from the user (bought/offered)
 */

import React, { useState, useEffect } from 'react';
import { Package, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { marketplaceService } from '../../services/marketplaceService';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function DealsPage() {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');
  const { user } = useAuth();
  const { showToast } = useNotifications();

  useEffect(() => {
    if (user?.id) {
      fetchMyDeals();
    }
  }, [user?.id]);

  const fetchMyDeals = async () => {
    try {
      setLoading(true);
      const data = await marketplaceService.getMyDeals(user.id);
      setDeals(data);
    } catch (error) {
      showToast('Failed to load your deals', 'error');
      console.error('Failed to fetch deals:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'all', label: 'All Deals', count: deals.length },
    { id: 'pending', label: 'Pending', count: deals.filter(d => d.status === 'pending').length },
    { id: 'completed', label: 'Completed', count: deals.filter(d => d.status === 'completed').length },
    { id: 'cancelled', label: 'Cancelled', count: deals.filter(d => d.status === 'cancelled').length }
  ];

  const filteredDeals = activeTab === 'all' ? deals : deals.filter(deal => deal.status === activeTab);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">My Deals</h1>
        <p className="text-gray-600 dark:text-gray-300">Track your buying and selling transactions</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="cataloro-card-glass">
          <div className="p-6 text-center">
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">{deals.length}</div>
            <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Total Deals</div>
          </div>
        </div>
        <div className="cataloro-card-glass">
          <div className="p-6 text-center">
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-orange-600 to-yellow-600 bg-clip-text text-transparent">{deals.filter(d => d.status === 'pending').length}</div>
            <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Pending</div>
          </div>
        </div>
        <div className="cataloro-card-glass">
          <div className="p-6 text-center">
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">{deals.filter(d => d.status === 'completed').length}</div>
            <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Completed</div>
          </div>
        </div>
        <div className="cataloro-card-glass">
          <div className="p-6 text-center">
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
              ${deals.filter(d => d.status === 'completed').reduce((sum, d) => sum + d.amount, 0).toFixed(2)}
            </div>
            <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Total Value</div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="cataloro-card mb-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`admin-tab ${activeTab === tab.id ? 'active' : ''}`}
              >
                {tab.label}
                <span className="ml-2 bg-gray-100 text-gray-600 py-1 px-2 rounded-full text-xs">
                  {tab.count}
                </span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Deals List */}
      {filteredDeals.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Package className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No deals found</h3>
          <p className="text-gray-600">
            {activeTab === 'all' 
              ? 'Start buying or selling to see your deals here'
              : `No ${activeTab} deals at the moment`
            }
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredDeals.map((deal) => (
            <DealCard key={deal.id} deal={deal} currentUserId={user.id} />
          ))}
        </div>
      )}
    </div>
  );
}

// Deal Card Component
function DealCard({ deal, currentUserId }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-5 h-5 text-orange-500" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'disputed':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-orange-100 text-orange-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      case 'disputed':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const isBuyer = deal.buyer_id === currentUserId;
  const userRole = isBuyer ? 'Buyer' : 'Seller';

  return (
    <div className="cataloro-card p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          {getStatusIcon(deal.status)}
          <div>
            <h3 className="font-semibold text-gray-900">Deal #{deal.id?.slice(-8)}</h3>
            <p className="text-sm text-gray-600">You are the {userRole}</p>
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(deal.status)}`}>
          {deal.status.toUpperCase()}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Deal Details */}
        <div className="md:col-span-2">
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-500">Listing</label>
              <p className="text-gray-900">Listing ID: {deal.listing_id}</p>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Amount</label>
                <p className="text-xl font-bold text-blue-600">${deal.amount?.toFixed(2)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Date</label>
                <p className="text-gray-900">
                  {deal.created_at ? new Date(deal.created_at).toLocaleDateString() : 'N/A'}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Buyer</label>
                <p className="text-gray-900">User {deal.buyer_id?.slice(-8)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Seller</label>
                <p className="text-gray-900">User {deal.seller_id?.slice(-8)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col justify-center space-y-3">
          {deal.status === 'pending' && (
            <>
              <button className="cataloro-button-primary">
                {isBuyer ? 'Confirm Receipt' : 'Mark as Shipped'}
              </button>
              <button className="cataloro-button-secondary text-red-600 border-red-300 hover:bg-red-50">
                Cancel Deal
              </button>
            </>
          )}
          
          {deal.status === 'completed' && (
            <button className="cataloro-button-secondary">
              View Details
            </button>
          )}

          {deal.status === 'disputed' && (
            <button className="cataloro-button-primary">
              Contact Support
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default DealsPage;