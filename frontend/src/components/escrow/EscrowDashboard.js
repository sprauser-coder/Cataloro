import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Plus, 
  Filter, 
  Search, 
  RefreshCw,
  DollarSign,
  Clock,
  CheckCircle,
  AlertTriangle,
  TrendingUp
} from 'lucide-react';
import EscrowTransactionCard from './EscrowTransactionCard';

const EscrowDashboard = ({ userId }) => {
  const [escrows, setEscrows] = useState([]);
  const [filteredEscrows, setFilteredEscrows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    completed: 0,
    totalValue: 0
  });

  useEffect(() => {
    fetchEscrows();
  }, [userId]);

  useEffect(() => {
    filterEscrows();
  }, [escrows, filter, searchTerm]);

  const fetchEscrows = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/v2/escrow/user/${userId}`);
      
      if (response.ok) {
        const data = await response.json();
        setEscrows(data.escrows || []);
        calculateStats(data.escrows || []);
      }
    } catch (error) {
      console.error('Failed to fetch escrows:', error);
      setEscrows([]);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (escrowList) => {
    const stats = {
      total: escrowList.length,
      active: escrowList.filter(e => ['pending', 'funded'].includes(e.status)).length,
      completed: escrowList.filter(e => e.status === 'released').length,
      totalValue: escrowList.reduce((sum, e) => sum + (e.amount || 0), 0)
    };
    setStats(stats);
  };

  const filterEscrows = () => {
    let filtered = [...escrows];

    // Apply status filter
    if (filter !== 'all') {
      filtered = filtered.filter(escrow => escrow.status === filter);
    }

    // Apply search filter
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(escrow => 
        escrow.id.toLowerCase().includes(search) ||
        escrow.listing_id?.toLowerCase().includes(search) ||
        (escrow.amount && escrow.amount.toString().includes(search))
      );
    }

    // Sort by created date (newest first)
    filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    setFilteredEscrows(filtered);
  };

  const handleStatusUpdate = async (escrowId, action) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      let endpoint = '';
      let method = 'POST';
      let body = {};

      switch (action) {
        case 'fund':
          endpoint = `/api/v2/escrow/${escrowId}/fund`;
          body = {
            funded_by: userId,
            payment_proof: { method: 'bank_transfer', reference: `PAY-${Date.now()}` }
          };
          break;
        case 'request_release':
          endpoint = `/api/v2/escrow/${escrowId}/release`;
          body = {
            requested_by: userId,
            reason: 'Transaction completed successfully'
          };
          break;
        case 'approve_release':
          endpoint = `/api/v2/escrow/${escrowId}/approve`;
          body = { approved_by: userId };
          break;
        case 'dispute':
          endpoint = `/api/v2/escrow/${escrowId}/dispute`;
          body = {
            disputed_by: userId,
            reason: 'Issue with transaction',
            evidence: []
          };
          break;
        default:
          return;
      }

      const response = await fetch(`${backendUrl}${endpoint}`, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      if (response.ok) {
        // Refresh escrows after successful action
        await fetchEscrows();
      } else {
        const error = await response.json();
        console.error('Action failed:', error);
        alert(`Action failed: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Failed to update escrow:', error);
      alert('Failed to update escrow. Please try again.');
    }
  };

  const handleViewDetails = (escrow) => {
    // Open detailed view modal or navigate to detail page
    console.log('View escrow details:', escrow);
    // You can implement a detailed modal or navigation here
  };

  const getFilterOptions = () => [
    { value: 'all', label: 'All Transactions', count: stats.total },
    { value: 'pending', label: 'Pending', count: escrows.filter(e => e.status === 'pending').length },
    { value: 'funded', label: 'Funded', count: escrows.filter(e => e.status === 'funded').length },
    { value: 'released', label: 'Completed', count: escrows.filter(e => e.status === 'released').length },
    { value: 'in_dispute', label: 'In Dispute', count: escrows.filter(e => e.status === 'in_dispute').length }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading escrow transactions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
            <Shield className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Escrow Transactions
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Secure transactions with buyer protection
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={fetchEscrows}
            disabled={loading}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
          
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>New Escrow</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow border border-gray-200 dark:border-gray-600">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Shield className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.total}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Total Escrows
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow border border-gray-200 dark:border-gray-600">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.active}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Active Escrows
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow border border-gray-200 dark:border-gray-600">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.completed}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Completed
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow border border-gray-200 dark:border-gray-600">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <DollarSign className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                €{stats.totalValue.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Total Value
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow border border-gray-200 dark:border-gray-600">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="flex items-center space-x-4">
            <Filter className="w-5 h-5 text-gray-400" />
            <div className="flex flex-wrap gap-2">
              {getFilterOptions().map((option) => (
                <button
                  key={option.value}
                  onClick={() => setFilter(option.value)}
                  className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                    filter === option.value
                      ? 'bg-blue-100 dark:bg-blue-900/30 border-blue-300 dark:border-blue-600 text-blue-700 dark:text-blue-300'
                      : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
                  }`}
                >
                  {option.label} ({option.count})
                </button>
              ))}
            </div>
          </div>
          
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search by ID or amount..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            />
          </div>
        </div>
      </div>

      {/* Escrow List */}
      <div className="space-y-4">
        {filteredEscrows.length === 0 ? (
          <div className="text-center py-12">
            <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              {escrows.length === 0 ? 'No Escrow Transactions' : 'No Results Found'}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {escrows.length === 0 
                ? 'You haven\'t created any escrow transactions yet.' 
                : 'Try adjusting your filters or search terms.'
              }
            </p>
            {escrows.length === 0 && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span>Create Your First Escrow</span>
              </button>
            )}
          </div>
        ) : (
          filteredEscrows.map((escrow) => (
            <EscrowTransactionCard
              key={escrow.id}
              escrow={escrow}
              currentUserId={userId}
              onStatusUpdate={handleStatusUpdate}
              onViewDetails={handleViewDetails}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default EscrowDashboard;