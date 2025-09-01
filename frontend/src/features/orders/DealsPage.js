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
  const [activeFilter, setActiveFilter] = useState('all'); // For tile filtering
  const [sortBy, setSortBy] = useState('newest'); // New sorting option
  const [searchTerm, setSearchTerm] = useState(''); // New search functionality
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
      // Use the correct API endpoint that we fixed earlier
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/my-deals/${user.id}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      
      // Sort deals by created_at date (newest first)
      const sortedDeals = data.sort((a, b) => {
        const dateA = new Date(a.created_at || a.approved_at || '2023-01-01');
        const dateB = new Date(b.created_at || b.approved_at || '2023-01-01');
        return dateB - dateA; // Newest first
      });
      
      setDeals(sortedDeals);
    } catch (error) {
      showToast('Failed to load your deals', 'error');
      console.error('Failed to fetch deals:', error);
      
      // Fallback to demo data if API fails
      const demoDeals = [
        {
          id: '1',
          listing_id: 'listing1',
          buyer_id: user.id,
          seller_id: 'seller1',
          status: 'approved',
          amount: 299.99,
          created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          approved_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
          listing: {
            id: 'listing1',
            title: 'MacBook Pro 14" M2',
            price: 299.99,
            image: '/api/placeholder/300/200'
          },
          seller: {
            id: 'seller1',
            username: 'tech_seller',
            email: 'seller@example.com'
          }
        },
        {
          id: '2',
          listing_id: 'listing2',
          buyer_id: 'buyer2',
          seller_id: user.id,
          status: 'completed',
          amount: 150.50,
          created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          approved_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
          listing: {
            id: 'listing2',
            title: 'Gaming Mouse',
            price: 150.50,
            image: '/api/placeholder/300/200'
          },
          buyer: {
            id: 'buyer2',
            username: 'gamer_buyer',
            email: 'buyer@example.com'
          }
        }
      ];
      setDeals(demoDeals);
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

  // Handle tile clicks for filtering
  const handleTileClick = (filter) => {
    setActiveFilter(filter);
    setActiveTab(filter); // Also update tab
  };

  // Use activeFilter instead of activeTab for consistency
  const filteredDeals = activeFilter === 'all' ? deals : deals.filter(deal => {
    if (activeFilter === 'totalValue') return deal.status === 'completed'; // For total value, show completed deals
    return deal.status === activeFilter;
  });

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

      {/* Stats Cards - CLICKABLE & REDUCED MARGIN */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-4">
        <button
          onClick={() => handleTileClick('all')}
          className={`cataloro-card-glass text-left transition-all duration-200 hover:scale-105 ${
            activeFilter === 'all' ? 'ring-2 ring-blue-500 bg-blue-50/20 dark:bg-blue-900/20' : ''
          }`}
        >
          <div className="p-6 text-center">
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">{deals.length}</div>
            <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Total Deals</div>
          </div>
        </button>
        <button
          onClick={() => handleTileClick('pending')}
          className={`cataloro-card-glass text-left transition-all duration-200 hover:scale-105 ${
            activeFilter === 'pending' ? 'ring-2 ring-orange-500 bg-orange-50/20 dark:bg-orange-900/20' : ''
          }`}
        >
          <div className="p-6 text-center">
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-orange-600 to-yellow-600 bg-clip-text text-transparent">{deals.filter(d => d.status === 'pending').length}</div>
            <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Pending</div>
          </div>
        </button>
        <button
          onClick={() => handleTileClick('completed')}
          className={`cataloro-card-glass text-left transition-all duration-200 hover:scale-105 ${
            activeFilter === 'completed' ? 'ring-2 ring-green-500 bg-green-50/20 dark:bg-green-900/20' : ''
          }`}
        >
          <div className="p-6 text-center">
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">{deals.filter(d => d.status === 'completed').length}</div>
            <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Completed</div>
          </div>
        </button>
        <button
          onClick={() => handleTileClick('totalValue')}
          className={`cataloro-card-glass text-left transition-all duration-200 hover:scale-105 ${
            activeFilter === 'totalValue' ? 'ring-2 ring-emerald-500 bg-emerald-50/20 dark:bg-emerald-900/20' : ''
          }`}
        >
          <div className="p-6 text-center">
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
              ${deals.filter(d => d.status === 'completed').reduce((sum, d) => sum + d.amount, 0).toFixed(2)}
            </div>
            <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Total Value</div>
          </div>
        </button>
      </div>

      {/* Filter Indicator */}
      {activeFilter !== 'all' && (
        <div className="mb-4 flex items-center justify-between bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
          <span className="text-blue-800 dark:text-blue-300 font-medium">
            Showing {activeFilter === 'totalValue' ? 'completed' : activeFilter} deals ({filteredDeals.length} items)
          </span>
          <button 
            onClick={() => {setActiveFilter('all'); setActiveTab('all');}}
            className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium"
          >
            Show All
          </button>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="cataloro-card-glass mb-8">
        <div className="border-b border-white/10">
          <nav className="-mb-px flex space-x-8 px-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 text-sm font-medium transition-all duration-300 border-b-2 ${
                  activeTab === tab.id
                    ? 'text-gray-900 dark:text-white border-blue-600'
                    : 'text-gray-600 dark:text-gray-400 border-transparent hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                {tab.label}
                <span className="ml-2 bg-white/20 dark:bg-white/10 text-gray-600 dark:text-gray-300 py-1 px-2 rounded-full text-xs backdrop-blur-md">
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
          <div className="cataloro-card-glass p-12">
            <div className="w-24 h-24 bg-gradient-to-r from-purple-600/20 to-blue-600/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <Package className="w-12 h-12 text-gray-600 dark:text-gray-300" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">No deals found</h3>
            <p className="text-gray-600 dark:text-gray-300 max-w-md mx-auto">
              {activeTab === 'all' 
                ? 'Start buying or selling to see your deals here'
                : `No ${activeTab} deals at the moment`
              }
            </p>
          </div>
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
        return 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300';
      case 'completed':
        return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300';
      case 'cancelled':
        return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300';
      case 'disputed':
        return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300';
      default:
        return 'bg-gray-100 dark:bg-gray-700/50 text-gray-800 dark:text-gray-300';
    }
  };

  const isBuyer = deal.buyer_id === currentUserId;
  const userRole = isBuyer ? 'Buyer' : 'Seller';

  return (
    <div className="cataloro-card-glass p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          {getStatusIcon(deal.status)}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">Deal #{deal.id?.slice(-8)}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300">You are the {userRole}</p>
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium backdrop-blur-md ${getStatusColor(deal.status)}`}>
          {deal.status.toUpperCase()}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Deal Details */}
        <div className="md:col-span-2">
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Listing</label>
              <p className="text-gray-900 dark:text-white">Listing ID: {deal.listing_id}</p>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Amount</label>
                <p className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">${deal.amount?.toFixed(2)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Date</label>
                <p className="text-gray-900 dark:text-white">
                  {deal.created_at ? new Date(deal.created_at).toLocaleDateString() : 'N/A'}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Buyer</label>
                <p className="text-gray-900 dark:text-white">User {deal.buyer_id?.slice(-8)}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500 dark:text-gray-400">Seller</label>
                <p className="text-gray-900 dark:text-white">User {deal.seller_id?.slice(-8)}</p>
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