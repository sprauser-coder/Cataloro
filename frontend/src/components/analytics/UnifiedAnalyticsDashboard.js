import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import { 
  BarChart3, 
  TrendingUp, 
  DollarSign, 
  Users, 
  Target,
  RefreshCw,
  Calendar,
  ArrowUp,
  ArrowDown,
  PieChart as PieChartIcon,
  Activity,
  Zap,
  Shield,
  AlertTriangle
} from 'lucide-react';

const UnifiedAnalyticsDashboard = ({ className = '' }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [userAnalytics, setUserAnalytics] = useState(null);
  const [salesAnalytics, setSalesAnalytics] = useState(null);
  const [marketplacAnalytics, setMarketplaceAnalytics] = useState(null);
  const [predictiveData, setPredictiveData] = useState(null);
  const [marketTrends, setMarketTrends] = useState([]);
  const [sellerPerformance, setSellerPerformance] = useState([]);
  const [revenueInsights, setRevenueInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedTimeRange, setSelectedTimeRange] = useState('30');

  useEffect(() => {
    fetchAnalyticsData();
  }, [selectedTimeRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      // Fetch unified analytics data from consolidated endpoints
      const [dashboardRes, userRes, salesRes, marketplaceRes, predictiveRes, trendsRes, sellersRes, revenueRes] = await Promise.all([
        fetch(`${backendUrl}/api/v2/advanced/analytics/dashboard`),
        fetch(`${backendUrl}/api/v2/advanced/analytics/user?days=${selectedTimeRange}`),
        fetch(`${backendUrl}/api/v2/advanced/analytics/sales?days=${selectedTimeRange}`),
        fetch(`${backendUrl}/api/v2/advanced/analytics/marketplace?days=${selectedTimeRange}`),
        fetch(`${backendUrl}/api/v2/advanced/analytics/predictive?forecast_days=${selectedTimeRange}`),
        fetch(`${backendUrl}/api/v2/advanced/analytics/market-trends?time_period=${selectedTimeRange}d`),
        fetch(`${backendUrl}/api/v2/advanced/analytics/seller-performance`),
        fetch(`${backendUrl}/api/v2/advanced/analytics/revenue-insights?period=monthly`)
      ]);

      const [dashboard, user, sales, marketplace, predictive, trends, sellers, revenue] = await Promise.all([
        dashboardRes.json(),
        userRes.json(),
        salesRes.json(),  
        marketplaceRes.json(),
        predictiveRes.json(),
        trendsRes.json(),
        sellersRes.json(),
        revenueRes.json()
      ]);

      // Set all data from unified backend services
      if (dashboard.success) setDashboardData(dashboard.dashboard_data);
      if (user.success) setUserAnalytics(user.analytics);
      if (sales.success) setSalesAnalytics(sales.analytics);
      if (marketplace.success) setMarketplaceAnalytics(marketplace.analytics);
      if (predictive.success) setPredictiveData(predictive.predictions);
      if (trends.success) setMarketTrends(trends.trends);
      if (sellers.success) setSellerPerformance(sellers.seller_performance);
      if (revenue.success) setRevenueInsights(revenue.revenue_insights);

    } catch (error) {
      console.error('Failed to fetch unified analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => `€${amount?.toLocaleString() || 0}`;
  const formatPercentage = (value) => `${value > 0 ? '+' : ''}${(value || 0).toFixed(1)}%`;

  const getTrendIcon = (direction) => {
    switch (direction) {
      case 'up':
        return <ArrowUp className="w-4 h-4 text-green-500" />;
      case 'down':
        return <ArrowDown className="w-4 h-4 text-red-500" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading unified analytics...</p>
          </div>
        </div>
      </div>
    );
  }

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* KPI Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Users className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {userAnalytics?.summary?.total_users?.toLocaleString() || 0}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Total Users</div>
              <div className="text-sm font-medium text-green-600">
                +{userAnalytics?.summary?.new_users || 0} this period
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <DollarSign className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {formatCurrency(salesAnalytics?.summary?.total_revenue)}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Total Revenue</div>
              <div className="text-sm font-medium text-blue-600">
                {formatCurrency(salesAnalytics?.summary?.avg_transaction_value)} avg/transaction
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
              <Target className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {marketplacAnalytics?.summary?.total_active_listings || 0}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Active Listings</div>
              <div className="text-sm font-medium text-green-600">
                +{marketplacAnalytics?.summary?.new_listings || 0} this period
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
              <TrendingUp className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {(salesAnalytics?.summary?.conversion_rate || 0).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Conversion Rate</div>
              <div className="text-sm font-medium text-gray-600">
                {salesAnalytics?.summary?.total_transactions || 0} transactions
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      {userAnalytics && salesAnalytics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Revenue Trend */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Revenue Trend
            </h3>
            <div className="text-center py-8 text-gray-500">
              <DollarSign className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>Revenue: {formatCurrency(salesAnalytics.summary?.total_revenue)}</p>
              <p className="text-sm">Transactions: {salesAnalytics.summary?.total_transactions || 0}</p>
            </div>
          </div>

          {/* User Growth */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              User Growth
            </h3>
            <div className="text-center py-8 text-gray-500">
              <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>Total Users: {userAnalytics.summary?.total_users || 0}</p>
              <p className="text-sm">Growth Rate: {formatPercentage(userAnalytics.summary?.user_growth_rate)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderPredictiveTab = () => (
    <div className="space-y-6">
      {/* Predictive Analytics Cards */}
      {predictiveData && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
            {selectedTimeRange}-Day Forecasts
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Revenue Forecast */}
            <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {formatCurrency(predictiveData.revenue_forecast?.forecast)}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">Revenue Forecast</div>
              <div className="flex items-center justify-center space-x-2">
                <span className={`text-xs px-2 py-1 rounded ${
                  predictiveData.revenue_forecast?.trend === 'increasing' 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                }`}>
                  {predictiveData.revenue_forecast?.trend || 'stable'}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {((predictiveData.revenue_forecast?.confidence || 0) * 100).toFixed(0)}% confidence
                </span>
              </div>
            </div>

            {/* User Growth Forecast */}
            <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {predictiveData.user_growth_forecast?.forecast || 0}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">New Users Forecast</div>
              <div className="flex items-center justify-center space-x-2">
                <span className={`text-xs px-2 py-1 rounded ${
                  predictiveData.user_growth_forecast?.trend === 'growing' 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                }`}>
                  {predictiveData.user_growth_forecast?.trend || 'stable'}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {((predictiveData.user_growth_forecast?.confidence || 0) * 100).toFixed(0)}% confidence
                </span>
              </div>
            </div>

            {/* Listing Volume Forecast */}
            <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {predictiveData.listing_volume_forecast?.forecast || 0}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">New Listings Forecast</div>
              <div className="flex items-center justify-center space-x-2">
                <span className={`text-xs px-2 py-1 rounded ${
                  predictiveData.listing_volume_forecast?.trend === 'steady' 
                    ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400' 
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                }`}>
                  {predictiveData.listing_volume_forecast?.trend || 'stable'}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {((predictiveData.listing_volume_forecast?.confidence || 0) * 100).toFixed(0)}% confidence
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Market Trends */}
      {marketTrends.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Market Trends Analysis
          </h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={marketTrends.slice(0, 8)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
                  <Bar dataKey="predicted_growth" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900 dark:text-white">Top Growing Categories</h4>
              {marketTrends.slice(0, 5).map((trend, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="flex items-center space-x-3">
                    {getTrendIcon(trend.trend_direction)}
                    <span className="font-medium text-gray-900 dark:text-white">{trend.category}</span>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900 dark:text-white">
                      {formatPercentage(trend.predicted_growth)}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {(trend.confidence_score * 100).toFixed(0)}% confidence
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderPerformanceTab = () => (
    <div className="space-y-6">
      {/* Seller Performance */}
      {sellerPerformance.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Seller Performance Forecasting
          </h3>
          
          <div className="space-y-3">
            {sellerPerformance.slice(0, 8).map((seller, index) => (
              <div key={index} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900 dark:text-white">{seller.seller_name}</h4>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {seller.current_rating?.toFixed(1)} → {seller.predicted_rating?.toFixed(1)}
                    </span>
                    {getTrendIcon(seller.sales_trend)}
                  </div>
                </div>
                
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  Revenue Forecast: {formatCurrency(seller.revenue_forecast)}
                </div>
                
                {seller.recommendations?.length > 0 && (
                  <div className="text-xs text-blue-600 dark:text-blue-400">
                    💡 {seller.recommendations[0]}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Revenue Insights */}
      {revenueInsights.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Revenue Optimization Insights
          </h3>
          
          <div className="space-y-4">
            {revenueInsights.map((insight, index) => (
              <div key={index} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900 dark:text-white capitalize">{insight.period}</h4>
                  <div className="text-green-600 dark:text-green-400 font-semibold">
                    {formatPercentage(insight.growth_rate)}
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Actual: </span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {formatCurrency(insight.actual_revenue)}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Predicted: </span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {formatCurrency(insight.predicted_revenue)}
                    </span>
                  </div>
                </div>
                
                {insight.optimization_opportunities?.length > 0 && (
                  <div className="text-xs text-purple-600 dark:text-purple-400">
                    🎯 {insight.optimization_opportunities[0]}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderRecommendationsTab = () => (
    <div className="space-y-6">
      {/* AI-Powered Recommendations */}
      {dashboardData?.recommendations && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            AI-Powered Business Recommendations
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {dashboardData.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="p-1 bg-blue-100 dark:bg-blue-900/30 rounded">
                  <Zap className="w-4 h-4 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900 dark:text-white">{recommendation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Marketplace Health Indicators */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
          Marketplace Health Indicators
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div className="text-2xl font-bold text-green-600 mb-1">
              {userAnalytics?.summary?.total_users || 0}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Active Users</div>
          </div>
          
          <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="text-2xl font-bold text-blue-600 mb-1">
              {marketplacAnalytics?.summary?.total_active_listings || 0}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Active Listings</div>
          </div>
          
          <div className="text-center p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
            <div className="text-2xl font-bold text-purple-600 mb-1">
              {formatCurrency(salesAnalytics?.summary?.total_revenue)}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Revenue</div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
            <BarChart3 className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Unified Analytics Dashboard
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Comprehensive business intelligence and predictive insights
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </select>
          
          <button
            onClick={fetchAnalyticsData}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <nav className="flex space-x-8" aria-label="Tabs">
          {[
            { id: 'overview', name: 'Overview', icon: '📊' },
            { id: 'predictive', name: 'Predictive', icon: '🔮' },
            { id: 'performance', name: 'Performance', icon: '📈' },
            { id: 'recommendations', name: 'Recommendations', icon: '💡' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
              } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && renderOverviewTab()}
      {activeTab === 'predictive' && renderPredictiveTab()}
      {activeTab === 'performance' && renderPerformanceTab()}
      {activeTab === 'recommendations' && renderRecommendationsTab()}

      {/* Last Updated */}
      <div className="text-center text-sm text-gray-500 dark:text-gray-400">
        Last updated: {new Date().toLocaleString()} | 
        Data source: Unified Analytics Service (Real Database Only)
      </div>
    </div>
  );
};

export default UnifiedAnalyticsDashboard;