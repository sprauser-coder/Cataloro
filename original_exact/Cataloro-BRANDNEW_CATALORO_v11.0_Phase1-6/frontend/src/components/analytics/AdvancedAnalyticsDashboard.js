import React, { useState, useEffect } from 'react';
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
  PieChart,
  Activity,
  Zap
} from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart as RechartsPieChart, Cell } from 'recharts';

const AdvancedAnalyticsDashboard = ({ className = '' }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [marketTrends, setMarketTrends] = useState([]);
  const [sellerPerformance, setSellerPerformance] = useState([]);
  const [revenueInsights, setRevenueInsights] = useState([]);
  const [categoryPerformance, setCategoryPerformance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d');

  useEffect(() => {
    fetchAnalyticsData();
  }, [selectedTimeRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      // Fetch all analytics data in parallel
      const [dashboardRes, trendsRes, sellersRes, revenueRes, categoriesRes] = await Promise.all([
        fetch(`${backendUrl}/api/v2/phase6/analytics/dashboard`),
        fetch(`${backendUrl}/api/v2/phase6/analytics/market-trends?time_period=${selectedTimeRange}`),
        fetch(`${backendUrl}/api/v2/phase6/analytics/seller-performance`),
        fetch(`${backendUrl}/api/v2/phase6/analytics/revenue-insights?period=monthly`),
        fetch(`${backendUrl}/api/v2/phase6/analytics/category-performance`)
      ]);

      const [dashboard, trends, sellers, revenue, categories] = await Promise.all([
        dashboardRes.json(),
        trendsRes.json(),
        sellersRes.json(),
        revenueRes.json(),
        categoriesRes.json()
      ]);

      if (dashboard.success) setDashboardData(dashboard.dashboard_data);
      if (trends.success) setMarketTrends(trends.trends);
      if (sellers.success) setSellerPerformance(sellers.seller_performance);
      if (revenue.success) setRevenueInsights(revenue.revenue_insights);
      if (categories.success) setCategoryPerformance(categories.categories);

    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => `€${amount.toLocaleString()}`;
  
  const formatPercentage = (value) => `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;

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

  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0'];

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading advanced analytics...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
            <BarChart3 className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Advanced Analytics
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Enterprise business intelligence and predictive insights
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          
          <button
            onClick={fetchAnalyticsData}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Overview Cards */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <Users className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {dashboardData.overview.total_users.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Users</div>
                <div className="text-sm font-medium text-green-600">
                  {formatPercentage(dashboardData.overview.growth_rate)} growth
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
                  {formatCurrency(dashboardData.overview.monthly_revenue)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Monthly Revenue</div>
                <div className="text-sm font-medium text-green-600">
                  Forecast: {formatCurrency(dashboardData.predictions.next_month_revenue)}
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
                  {dashboardData.overview.active_sellers}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Active Sellers</div>
                <div className="text-sm font-medium text-blue-600">
                  Satisfaction: {dashboardData.overview.customer_satisfaction.toFixed(1)}/5
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
                <Zap className="w-5 h-5 text-yellow-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {dashboardData.trends.platform_health_score.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Platform Health</div>
                <div className="text-sm font-medium text-orange-600">
                  Risk Alerts: {dashboardData.predictions.risk_alerts}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Market Trends Chart */}
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
                  <Bar dataKey="predicted_growth" fill="#8884d8" />
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

      {/* Seller Performance and Revenue Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Seller Performance */}
        {sellerPerformance.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Seller Performance Forecast
            </h3>
            
            <div className="space-y-3">
              {sellerPerformance.slice(0, 5).map((seller, index) => (
                <div key={index} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900 dark:text-white">{seller.seller_name}</h4>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {seller.current_rating.toFixed(1)} → {seller.predicted_rating.toFixed(1)}
                      </span>
                      {seller.sales_trend === 'up' ? (
                        <ArrowUp className="w-4 h-4 text-green-500" />
                      ) : seller.sales_trend === 'down' ? (
                        <ArrowDown className="w-4 h-4 text-red-500" />
                      ) : (
                        <Activity className="w-4 h-4 text-gray-500" />
                      )}
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    Revenue Forecast: {formatCurrency(seller.revenue_forecast)}
                  </div>
                  
                  {seller.recommendations.length > 0 && (
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
              Revenue Optimization
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
                  
                  {insight.optimization_opportunities.length > 0 && (
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

      {/* Category Performance */}
      {categoryPerformance.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Category Performance Analysis
          </h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsPieChart>
                  <Pie
                    data={categoryPerformance.slice(0, 6)}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: €${value.toLocaleString()}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="sales"
                  >
                    {categoryPerformance.slice(0, 6).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => formatCurrency(value)} />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>
            
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900 dark:text-white">Category Metrics</h4>
              {categoryPerformance.slice(0, 6).map((category, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">{category.name}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Growth: {formatPercentage(category.growth)} | Rating: {category.customer_rating.toFixed(1)}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900 dark:text-white">
                      {formatCurrency(category.sales)}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {category.profit_margin.toFixed(1)}% margin
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {dashboardData && dashboardData.recommendations && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            AI-Powered Recommendations
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
    </div>
  );
};

export default AdvancedAnalyticsDashboard;