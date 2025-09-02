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

  // Load deals and live statistics
  const fetchLiveDealsData = useCallback(async (showRefreshToast = false) => {
    try {
      if (showRefreshToast) setRefreshing(true);
      
      // Fetch user deals
      const dealsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/my-deals/${user.id}`);
      let dealsData = [];
      
      if (dealsResponse.ok) {
        dealsData = await dealsResponse.json();
        console.log('✅ Live deals data loaded:', dealsData.length, 'deals');
      } else {
        console.log('⚠️ Using fallback for deals data');
        throw new Error('API unavailable');
      }
      
      // Sort deals by date
      const sortedDeals = dealsData.sort((a, b) => {
        const dateA = new Date(a.created_at || a.approved_at || '2023-01-01');
        const dateB = new Date(b.created_at || b.approved_at || '2023-01-01');
        return dateB - dateA;
      });
      
      setDeals(sortedDeals);
      
      // Calculate live statistics
      const stats = calculateLiveStats(dealsData);
      setLiveStats(stats);
      
      setLastUpdated(new Date());
      
      if (showRefreshToast) {
        showToast(`✅ Updated: ${dealsData.length} deals loaded with live statistics`, 'success');
      }
      
    } catch (error) {
      console.error('❌ Failed to fetch live deals data:', error);
      if (showRefreshToast) {
        showToast('⚠️ Failed to refresh live data - using cached data', 'warning');
      }
      
      // Only set loading to false, keep any existing data
      setDeals(prev => prev.length > 0 ? prev : []); // Keep existing data or empty array
      
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [user?.id, showToast]);

  // Calculate comprehensive live statistics
  const calculateLiveStats = (dealsData) => {
    if (!dealsData || dealsData.length === 0) {
      return {
        totalDeals: 0,
        totalValue: 0,
        pendingDeals: 0,
        completedDeals: 0,
        averageOrderValue: 0,
        successRate: 0,
        monthlyTrend: 0,
        topCategories: [],
        recentActivity: []
      };
    }

    const completedDeals = dealsData.filter(d => d.status === 'completed');
    const pendingDeals = dealsData.filter(d => d.status === 'pending' || d.status === 'approved');
    const totalValue = completedDeals.reduce((sum, d) => sum + (parseFloat(d.amount) || 0), 0);
    const avgOrderValue = completedDeals.length > 0 ? totalValue / completedDeals.length : 0;
    const successRate = dealsData.length > 0 ? (completedDeals.length / dealsData.length) * 100 : 0;

    // Calculate monthly trend (compare last 30 days vs previous 30 days)
    const now = new Date();
    const last30Days = dealsData.filter(d => {
      const dealDate = new Date(d.created_at || d.approved_at);
      const daysDiff = (now - dealDate) / (1000 * 60 * 60 * 24);
      return daysDiff <= 30;
    });
    
    const previous30Days = dealsData.filter(d => {
      const dealDate = new Date(d.created_at || d.approved_at);
      const daysDiff = (now - dealDate) / (1000 * 60 * 60 * 24);
      return daysDiff > 30 && daysDiff <= 60;
    });

    const monthlyTrend = previous30Days.length > 0 
      ? ((last30Days.length - previous30Days.length) / previous30Days.length) * 100 
      : 0;

    // Top categories (from listing data if available)
    const categoryCount = {};
    dealsData.forEach(deal => {
      const category = deal.listing?.category || 'Uncategorized';
      categoryCount[category] = (categoryCount[category] || 0) + 1;
    });
    
    const topCategories = Object.entries(categoryCount)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([category, count]) => ({ category, count }));

    // Recent activity (last 10 deals)
    const recentActivity = dealsData
      .slice(0, 10)
      .map(deal => ({
        id: deal.id,
        type: deal.buyer_id === user?.id ? 'purchase' : 'sale',
        title: deal.listing?.title || 'Deal',
        amount: deal.amount,
        status: deal.status,
        date: deal.created_at || deal.approved_at
      }));

    return {
      totalDeals: dealsData.length,
      totalValue,
      pendingDeals: pendingDeals.length,
      completedDeals: completedDeals.length,
      averageOrderValue: avgOrderValue,
      successRate,
      monthlyTrend,
      topCategories,
      recentActivity
    };
  };

  // Set up real-time updates
  useEffect(() => {
    if (user?.id) {
      fetchLiveDealsData();
      
      if (realTimeUpdates) {
        intervalRef.current = setInterval(() => {
          fetchLiveDealsData();
        }, 30000); // Update every 30 seconds
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [user?.id, realTimeUpdates, fetchLiveDealsData]);

  const handleRefresh = () => {
    fetchLiveDealsData(true);
  };

  const toggleRealTimeUpdates = () => {
    setRealTimeUpdates(prev => {
      const newValue = !prev;
      if (newValue) {
        showToast('🔄 Real-time updates enabled', 'success');
      } else {
        showToast('⏸️ Real-time updates paused', 'info');
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      }
      return newValue;
    });
  };

  const tabs = [
    { id: 'overview', label: 'Live Overview', icon: Activity, count: liveStats.totalDeals },
    { id: 'all', label: 'All Deals', icon: Package, count: deals.length },
    { id: 'pending', label: 'Pending', icon: Clock, count: deals.filter(d => d.status === 'pending' || d.status === 'approved').length },
    { id: 'completed', label: 'Completed', icon: CheckCircle, count: deals.filter(d => d.status === 'completed').length },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, count: liveStats.topCategories.length }
  ];

  // Handle tile clicks for filtering
  const handleTileClick = (filter) => {
    setActiveFilter(filter);
    setActiveTab(filter); // Also update tab
  };

  // Enhanced filtering and sorting with REAL DATA
  const getFilteredDeals = () => {
    if (activeTab === 'overview' || activeTab === 'analytics') {
      return []; // These tabs don't show deal lists
    }

    return deals.filter(deal => {
      // Filter by active tab
      let statusMatch = true;
      
      switch (activeTab) {
        case 'all':
          statusMatch = true; // Show all deals
          break;
        case 'pending':
          statusMatch = deal.status === 'pending' || deal.status === 'approved' || deal.status === 'in_progress';
          break;
        case 'completed':
          statusMatch = deal.status === 'completed' || deal.status === 'delivered' || deal.status === 'finished';
          break;
        case 'cancelled':
          statusMatch = deal.status === 'cancelled' || deal.status === 'rejected' || deal.status === 'failed';
          break;
        default:
          statusMatch = true;
      }
      
      // Filter by search term
      const searchMatch = !searchTerm || 
                         deal.listing?.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         deal.id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         deal.seller?.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         deal.buyer?.username?.toLowerCase().includes(searchTerm.toLowerCase());
      
      return statusMatch && searchMatch;
    });
  };

  const filteredAndSortedDeals = getFilteredDeals()
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
      {/* Enhanced Header with Live Status */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center">
              <Activity className="w-8 h-8 mr-3 text-blue-600" />
              Live Deals Dashboard
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Real-time tracking of your marketplace transactions and performance
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Real-time Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${realTimeUpdates ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {realTimeUpdates ? 'Live' : 'Paused'}
              </span>
            </div>
            
            {/* Last Updated */}
            {lastUpdated && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                Updated: {lastUpdated.toLocaleTimeString()}
              </span>
            )}
            
            {/* Controls */}
            <div className="flex space-x-2">
              <button
                onClick={toggleRealTimeUpdates}
                className={`px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  realTimeUpdates 
                    ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {realTimeUpdates ? 'Pause' : 'Resume'} Live
              </button>
              
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center"
              >
                <RefreshCw className={`w-4 h-4 mr-1 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Live Overview Dashboard - Only show when overview tab is active */}
      {activeTab === 'overview' && (
        <div className="space-y-8 mb-8">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="cataloro-card-glass p-6 text-center">
              <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {liveStats.totalDeals}
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Total Deals</div>
              <div className="flex items-center justify-center mt-2">
                {liveStats.monthlyTrend >= 0 ? (
                  <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-500 mr-1" />
                )}
                <span className={`text-xs ${liveStats.monthlyTrend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {Math.abs(liveStats.monthlyTrend).toFixed(1)}%
                </span>
              </div>
            </div>

            <div className="cataloro-card-glass p-6 text-center">
              <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                ${liveStats.totalValue.toFixed(2)}
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Total Value</div>
              <div className="text-xs text-gray-500 mt-2">
                Avg: ${liveStats.averageOrderValue.toFixed(2)}
              </div>
            </div>

            <div className="cataloro-card-glass p-6 text-center">
              <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-orange-600 to-yellow-600 bg-clip-text text-transparent">
                {liveStats.pendingDeals}
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Pending</div>
              <div className="text-xs text-gray-500 mt-2">
                Requires attention
              </div>
            </div>

            <div className="cataloro-card-glass p-6 text-center">
              <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                {liveStats.successRate.toFixed(1)}%
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Success Rate</div>
              <div className="text-xs text-gray-500 mt-2">
                {liveStats.completedDeals} completed
              </div>
            </div>
          </div>

          {/* Recent Activity & Top Categories */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Recent Activity Feed */}
            <div className="cataloro-card-glass p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <Zap className="w-5 h-5 mr-2 text-yellow-500" />
                Recent Activity
              </h3>
              
              {liveStats.recentActivity.length === 0 ? (
                <div className="text-center py-8">
                  <Activity className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">No recent activity</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-80 overflow-y-auto">
                  {liveStats.recentActivity.map((activity, index) => (
                    <div key={activity.id || index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-full ${
                          activity.type === 'purchase' ? 'bg-blue-100 text-blue-600' : 'bg-green-100 text-green-600'
                        }`}>
                          {activity.type === 'purchase' ? 
                            <Package className="w-4 h-4" /> : 
                            <DollarSign className="w-4 h-4" />
                          }
                        </div>
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white text-sm">
                            {activity.type === 'purchase' ? 'Purchased' : 'Sold'}: {activity.title}
                          </div>
                          <div className="text-xs text-gray-500">
                            {new Date(activity.date).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-green-600">${activity.amount}</div>
                        <div className={`text-xs px-2 py-1 rounded-full ${
                          activity.status === 'completed' ? 'bg-green-100 text-green-700' :
                          activity.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {activity.status}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Top Categories */}
            <div className="cataloro-card-glass p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <PieChart className="w-5 h-5 mr-2 text-purple-500" />
                Top Categories
              </h3>
              
              {liveStats.topCategories.length === 0 ? (
                <div className="text-center py-8">
                  <PieChart className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">No category data</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {liveStats.topCategories.map((category, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${{
                          0: 'bg-blue-500',
                          1: 'bg-green-500', 
                          2: 'bg-yellow-500',
                          3: 'bg-purple-500',
                          4: 'bg-red-500'
                        }[index]}`}></div>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {category.category}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-gray-900 dark:text-white">{category.count}</div>
                        <div className="text-xs text-gray-500">deals</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Stats Cards - Show for other tabs */}
      {activeTab !== 'overview' && (
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
      )}

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
            {tabs.map((tab) => {
              const IconComponent = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-2 text-sm font-medium transition-all duration-300 border-b-2 flex items-center ${
                    activeTab === tab.id
                      ? 'text-gray-900 dark:text-white border-blue-600'
                      : 'text-gray-600 dark:text-gray-400 border-transparent hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  <IconComponent className="w-4 h-4 mr-2" />
                  {tab.label}
                  <span className="ml-2 bg-white/20 dark:bg-white/10 text-gray-600 dark:text-gray-300 py-1 px-2 rounded-full text-xs backdrop-blur-md">
                    {tab.count}
                  </span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Deals List - Show for deal tabs */}
      {(activeTab === 'all' || activeTab === 'pending' || activeTab === 'completed' || activeTab === 'cancelled') && (
        <div className="cataloro-card-glass p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {activeTab === 'all' ? 'All Deals' : 
               activeTab === 'pending' ? 'Pending Deals' :
               activeTab === 'completed' ? 'Completed Deals' :
               'Cancelled Deals'} ({filteredAndSortedDeals.length})
            </h3>
            
            <div className="flex items-center space-x-4">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="highest_value">Highest Value</option>
                <option value="lowest_value">Lowest Value</option>
                <option value="status">By Status</option>
              </select>
            </div>
          </div>

          {filteredAndSortedDeals.length === 0 ? (
            <div className="text-center py-12">
              <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h4 className="text-xl font-medium text-gray-900 dark:text-white mb-2">
                No {activeTab === 'all' ? '' : activeTab} deals found
              </h4>
              <p className="text-gray-600 dark:text-gray-300">
                {searchTerm ? `No deals match your search for "${searchTerm}"` : 
                 activeTab === 'all' ? 'You haven\'t made any deals yet' :
                 `You don't have any ${activeTab} deals`}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredAndSortedDeals.map((deal) => (
                <div key={deal.id} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      {deal.listing?.image && (
                        <img
                          src={deal.listing.image}
                          alt={deal.listing.title}
                          className="w-16 h-16 object-cover rounded-lg"
                        />
                      )}
                      
                      <div>
                        <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {deal.listing?.title || 'Deal #' + deal.id}
                        </h4>
                        
                        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600 dark:text-gray-300">
                          <span className="flex items-center">
                            <User className="w-4 h-4 mr-1" />
                            {deal.buyer_id === user?.id ? 
                              `Seller: ${deal.seller?.username || deal.seller?.full_name || 'Unknown'}` :
                              `Buyer: ${deal.buyer?.username || deal.buyer?.full_name || 'Unknown'}`
                            }
                          </span>
                          
                          <span className="flex items-center">
                            <Calendar className="w-4 h-4 mr-1" />
                            {new Date(deal.created_at || deal.approved_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600 mb-2">
                        ${parseFloat(deal.amount || 0).toFixed(2)}
                      </div>
                      
                      <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                        deal.status === 'completed' ? 'bg-green-100 text-green-800' :
                        deal.status === 'pending' || deal.status === 'approved' ? 'bg-yellow-100 text-yellow-800' :
                        deal.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {deal.status?.charAt(0).toUpperCase() + deal.status?.slice(1) || 'Unknown'}
                      </div>
                      
                      <div className="text-xs text-gray-500 mt-2">
                        Deal ID: {deal.id.slice(0, 8)}...
                      </div>
                    </div>
                  </div>

                  {/* Deal Actions */}
                  <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                    <div className="text-sm text-gray-600 dark:text-gray-300">
                      {deal.buyer_id === user?.id ? 'You purchased this item' : 'You sold this item'}
                    </div>
                    
                    <div className="flex space-x-2">
                      <button className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-lg hover:bg-blue-200 transition-colors flex items-center">
                        <MessageCircle className="w-4 h-4 mr-1" />
                        Message
                      </button>
                      
                      <button className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 transition-colors flex items-center">
                        <Eye className="w-4 h-4 mr-1" />
                        Details
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
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