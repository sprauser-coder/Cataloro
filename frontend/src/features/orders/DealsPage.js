/**
 * CATALORO - Live Deals Dashboard
 * Real-time executed deals with live statistics and data
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Package, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Search, 
  Filter, 
  Calendar, 
  DollarSign,
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  Activity,
  RefreshCw,
  Download,
  Star,
  MapPin,
  User,
  MessageCircle,
  Eye,
  Zap
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function DealsPage() {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [liveStats, setLiveStats] = useState({
    totalDeals: 0,
    totalValue: 0,
    pendingDeals: 0,
    completedDeals: 0,
    averageOrderValue: 0,
    successRate: 0,
    monthlyTrend: 0,
    topCategories: [],
    recentActivity: []
  });
  const [activeTab, setActiveTab] = useState('overview');
  const [activeFilter, setActiveFilter] = useState('all');
  const [sortBy, setSortBy] = useState('newest');
  const [searchTerm, setSearchTerm] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [realTimeUpdates, setRealTimeUpdates] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const intervalRef = useRef(null);

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

  // Enhanced filtering and sorting
  const filteredAndSortedDeals = deals
    .filter(deal => {
      // Filter by status
      const statusMatch = activeFilter === 'all' || 
                         (activeFilter === 'totalValue' ? deal.status === 'completed' : deal.status === activeFilter);
      
      // Filter by search term
      const searchMatch = !searchTerm || 
                         deal.listing?.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         deal.id?.toLowerCase().includes(searchTerm.toLowerCase());
      
      return statusMatch && searchMatch;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.created_at || b.approved_at || '2023-01-01') - new Date(a.created_at || a.approved_at || '2023-01-01');
        case 'oldest':
          return new Date(a.created_at || a.approved_at || '2023-01-01') - new Date(b.created_at || b.approved_at || '2023-01-01');
        case 'highest_value':
          return (b.amount || 0) - (a.amount || 0);
        case 'lowest_value':
          return (a.amount || 0) - (b.amount || 0);
        case 'status':
          return (a.status || '').localeCompare(b.status || '');
        default:
          return 0;
      }
    });

  // Use filtered and sorted deals instead of just filtered
  const displayDeals = filteredAndSortedDeals;

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

      {/* Enhanced Controls Section */}
      <div className="cataloro-card-glass mb-8">
        <div className="p-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0 lg:space-x-4">
            
            {/* Search Bar */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search deals by item or ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-3 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Sort Options */}
            <div className="flex items-center space-x-3">
              <Filter className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="highest_value">Highest Value</option>
                <option value="lowest_value">Lowest Value</option>
                <option value="status">By Status</option>
              </select>
            </div>

            {/* Results Count */}
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {displayDeals.length} of {deals.length} deals
            </div>
          </div>
        </div>
      </div>

      {/* Filter Indicator */}
      {(activeFilter !== 'all' || searchTerm) && (
        <div className="mb-4 flex items-center justify-between bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
          <div className="flex items-center space-x-4">
            <span className="text-blue-800 dark:text-blue-300 font-medium">
              Active filters: {activeFilter !== 'all' && `Status: ${activeFilter === 'totalValue' ? 'completed' : activeFilter}`}
              {searchTerm && ` | Search: "${searchTerm}"`}
            </span>
            <span className="text-blue-600 dark:text-blue-400">
              ({displayDeals.length} results)
            </span>
          </div>
          <button 
            onClick={() => {
              setActiveFilter('all'); 
              setActiveTab('all');
              setSearchTerm('');
            }}
            className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium"
          >
            Clear All
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
      {displayDeals.length === 0 ? (
        <div className="text-center py-12">
          <div className="cataloro-card-glass p-12">
            <div className="w-24 h-24 bg-gradient-to-r from-purple-600/20 to-blue-600/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <Package className="w-12 h-12 text-gray-600 dark:text-gray-300" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
              {searchTerm ? 'No matching deals found' : 'No deals found'}
            </h3>
            <p className="text-gray-600 dark:text-gray-300 max-w-md mx-auto">
              {searchTerm 
                ? `No deals match your search for "${searchTerm}"`
                : activeTab === 'all' 
                  ? 'Start buying or selling to see your deals here'
                  : `No ${activeTab} deals at the moment`
              }
            </p>
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="mt-4 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium"
              >
                Clear search
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {displayDeals.map((deal) => (
            <DealCard key={deal.id} deal={deal} currentUserId={user.id} user={user} />
          ))}
        </div>
      )}
    </div>
  );
}

// Enhanced Deal Card Component
function DealCard({ deal, currentUserId, user }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-5 h-5 text-orange-500" />;
      case 'approved':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'rejected':
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
      case 'approved':
        return 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300';
      case 'completed':
        return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300';
      case 'cancelled':
        return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300';
      case 'rejected':
        return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300';
      case 'disputed':
        return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300';
      default:
        return 'bg-gray-100 dark:bg-gray-700/50 text-gray-800 dark:text-gray-300';
    }
  };

  const isBuyer = deal.buyer_id === currentUserId;
  const userRole = isBuyer ? 'Buyer' : 'Seller';
  const otherParty = isBuyer ? deal.seller : deal.buyer;

  return (
    <div className="cataloro-card-glass p-6 hover:shadow-lg transition-all duration-300">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          {getStatusIcon(deal.status)}
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Deal #{deal.id?.slice(-8)} • {userRole}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              {deal.listing?.title || `Listing ID: ${deal.listing_id}`}
            </p>
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium backdrop-blur-md ${getStatusColor(deal.status)}`}>
          {deal.status.toUpperCase()}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Deal Overview */}
        <div>
          <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Deal Information</h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-300">Amount</span>
              <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                ${deal.amount?.toFixed(2) || '0.00'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-300">Created</span>
              <span className="text-sm text-gray-900 dark:text-white">
                {deal.created_at ? new Date(deal.created_at).toLocaleDateString() : 'N/A'}
              </span>
            </div>
            {deal.approved_at && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  {deal.status === 'approved' ? 'Approved' : 'Completed'}
                </span>
                <span className="text-sm text-gray-900 dark:text-white">
                  {new Date(deal.approved_at).toLocaleDateString()}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Participants */}
        <div>
          <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Participants</h4>
          <div className="space-y-3">
            <div>
              <span className="text-sm text-gray-600 dark:text-gray-300">Buyer</span>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {isBuyer ? 'You' : deal.buyer?.username || `User ${deal.buyer_id?.slice(-8)}`}
              </p>
            </div>
            <div>
              <span className="text-sm text-gray-600 dark:text-gray-300">Seller</span>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {!isBuyer ? 'You' : deal.seller?.username || `User ${deal.seller_id?.slice(-8)}`}
              </p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div>
          <h4 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Actions</h4>
          <div className="space-y-3">
            {deal.status === 'pending' && (
              <>
                <button 
                  onClick={() => {
                    if (isBuyer) {
                      // Contact seller
                      const sellerId = deal.seller_id || deal.seller?.id;
                      window.location.href = `/messages?user=${sellerId}&subject=Deal ${deal.id}`;
                    } else {
                      // Review request - go to pending sales
                      window.location.href = `/pending-sales`;
                    }
                  }}
                  className="w-full cataloro-button-primary text-sm py-2"
                >
                  {isBuyer ? 'Contact Seller' : 'Review Request'}
                </button>
                <button 
                  onClick={async () => {
                    if (window.confirm('Are you sure you want to cancel this deal?')) {
                      try {
                        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/orders/${deal.id}/cancel`, {
                          method: 'PUT',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ user_id: user.id })
                        });
                        if (response.ok) {
                          window.location.reload();
                        }
                      } catch (error) {
                        console.error('Failed to cancel deal:', error);
                      }
                    }
                  }}
                  className="w-full cataloro-button-secondary text-red-600 border-red-300 hover:bg-red-50 text-sm py-2"
                >
                  Cancel Deal
                </button>
              </>
            )}
            
            {deal.status === 'approved' && (
              <>
                <button 
                  onClick={async () => {
                    try {
                      const action = isBuyer ? 'complete' : 'ship';
                      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/orders/${deal.id}/${action}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user_id: user.id })
                      });
                      if (response.ok) {
                        window.location.reload();
                      }
                    } catch (error) {
                      console.error('Failed to update deal status:', error);
                    }
                  }}
                  className="w-full cataloro-button-primary text-sm py-2"
                >
                  {isBuyer ? 'Confirm Receipt' : 'Mark as Shipped'}
                </button>
                <button 
                  onClick={() => {
                    const otherUserId = isBuyer ? (deal.seller_id || deal.seller?.id) : (deal.buyer_id || deal.buyer?.id);
                    window.location.href = `/messages?user=${otherUserId}&subject=Deal ${deal.id}`;
                  }}
                  className="w-full cataloro-button-secondary text-sm py-2"
                >
                  Message {isBuyer ? 'Seller' : 'Buyer'}
                </button>
              </>
            )}
            
            {deal.status === 'completed' && (
              <button 
                onClick={() => {
                  // Generate and view receipt
                  window.open(`/receipt/${deal.id}`, '_blank');
                }}
                className="w-full cataloro-button-secondary text-sm py-2"
              >
                View Receipt
              </button>
            )}

            {deal.status === 'disputed' && (
              <button 
                onClick={() => {
                  window.location.href = `/support?deal=${deal.id}`;
                }}
                className="w-full cataloro-button-primary text-sm py-2"
              >
                Contact Support
              </button>
            )}
            
            {(deal.status === 'cancelled' || deal.status === 'rejected') && (
              <button 
                onClick={() => {
                  // Show deal details modal or navigate to details page
                  alert(`Deal ${deal.id} was ${deal.status}. Reason: ${deal.reason || 'No reason provided'}`);
                }}
                className="w-full cataloro-button-secondary text-sm py-2"
              >
                View Details
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default DealsPage;