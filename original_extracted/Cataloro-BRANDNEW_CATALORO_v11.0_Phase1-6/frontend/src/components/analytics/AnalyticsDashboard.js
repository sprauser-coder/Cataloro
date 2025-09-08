import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';

const AnalyticsDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [kpisData, setKpiData] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      // Fetch all analytics data
      const [dashboardRes, kpisRes, predictionsRes] = await Promise.all([
        fetch(`${backendUrl}/api/admin/analytics/dashboard`),
        fetch(`${backendUrl}/api/admin/analytics/kpis`),
        fetch(`${backendUrl}/api/admin/analytics/predictive`)
      ]);

      const dashboard = await dashboardRes.json();
      const kpis = await kpisRes.json();
      const predictive = await predictionsRes.json();

      setDashboardData(dashboard);
      setKpiData(kpis);
      setPredictions(predictive.predictions);
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading Analytics Dashboard...</p>
        </div>
      </div>
    );
  }

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-bold">👥</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Users</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData?.overview?.total_users || 0}
              </p>
              <p className="text-xs text-green-600">
                +{dashboardData?.overview?.new_users_30d || 0} this month
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-bold">€</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Revenue</p>
              <p className="text-2xl font-bold text-gray-900">
                €{dashboardData?.overview?.total_revenue || 0}
              </p>
              <p className="text-xs text-blue-600">
                {dashboardData?.trends?.avg_transaction_value || 0} avg/transaction
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-bold">📋</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Active Listings</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData?.overview?.active_listings || 0}
              </p>
              <p className="text-xs text-green-600">
                +{dashboardData?.trends?.new_listings_30d || 0} this month
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-bold">📈</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Conversion Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {(dashboardData?.overview?.conversion_rate * 100 || 0).toFixed(1)}%
              </p>
              <p className="text-xs text-gray-600">
                {dashboardData?.overview?.total_transactions || 0} transactions
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Health Scores */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Business Health Scores</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {kpisData?.health_scores && Object.entries(kpisData.health_scores).map(([key, value]) => (
            <div key={key} className="text-center">
              <div className="mb-2">
                <div className="w-16 h-16 mx-auto">
                  <svg className="w-16 h-16 transform -rotate-90">
                    <circle
                      cx="32" cy="32" r="28"
                      stroke="#e5e7eb" strokeWidth="4" fill="transparent"
                    />
                    <circle
                      cx="32" cy="32" r="28"
                      stroke={value > 70 ? "#10b981" : value > 40 ? "#f59e0b" : "#ef4444"}
                      strokeWidth="4" fill="transparent"
                      strokeDasharray={`${2 * Math.PI * 28}`}
                      strokeDashoffset={`${2 * Math.PI * 28 * (1 - value / 100)}`}
                      className="transition-all duration-300"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-sm font-bold">{value.toFixed(1)}%</span>
                  </div>
                </div>
              </div>
              <p className="text-sm font-medium text-gray-700 capitalize">
                {key.replace('_', ' ')}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Registration Trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">User Registration Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={dashboardData?.charts_data?.daily_registrations || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="_id" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* User Type Breakdown */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">User Type Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={dashboardData?.charts_data?.user_type_breakdown?.map(item => ({
                  name: item._id,
                  value: item.count
                })) || []}
                cx="50%" cy="50%" innerRadius={40} outerRadius={100}
                paddingAngle={5} dataKey="value"
              >
                {dashboardData?.charts_data?.user_type_breakdown?.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );

  const renderPredictionsTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-6">30-Day Forecasts</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Revenue Forecast */}
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-3xl font-bold text-blue-600 mb-2">
              €{predictions?.revenue_forecast?.forecast?.toFixed(2) || 0}
            </div>
            <div className="text-sm text-gray-600 mb-2">Revenue Forecast</div>
            <div className="flex items-center justify-center space-x-2">
              <span className={`text-xs px-2 py-1 rounded ${
                predictions?.revenue_forecast?.trend === 'increasing' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {predictions?.revenue_forecast?.trend || 'stable'}
              </span>
              <span className="text-xs text-gray-500">
                {((predictions?.revenue_forecast?.confidence || 0) * 100).toFixed(0)}% confidence
              </span>
            </div>
          </div>

          {/* User Growth Forecast */}
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {predictions?.user_growth_forecast?.forecast || 0}
            </div>
            <div className="text-sm text-gray-600 mb-2">New Users Forecast</div>
            <div className="flex items-center justify-center space-x-2">
              <span className={`text-xs px-2 py-1 rounded ${
                predictions?.user_growth_forecast?.trend === 'growing' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {predictions?.user_growth_forecast?.trend || 'stable'}
              </span>
              <span className="text-xs text-gray-500">
                {((predictions?.user_growth_forecast?.confidence || 0) * 100).toFixed(0)}% confidence
              </span>
            </div>
          </div>

          {/* Listing Volume Forecast */}
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {predictions?.listing_volume_forecast?.forecast || 0}
            </div>
            <div className="text-sm text-gray-600 mb-2">New Listings Forecast</div>
            <div className="flex items-center justify-center space-x-2">
              <span className={`text-xs px-2 py-1 rounded ${
                predictions?.listing_volume_forecast?.trend === 'steady' 
                  ? 'bg-blue-100 text-blue-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {predictions?.listing_volume_forecast?.trend || 'stable'}
              </span>
              <span className="text-xs text-gray-500">
                {((predictions?.listing_volume_forecast?.confidence || 0) * 100).toFixed(0)}% confidence
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Market Trends */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Market Trends & Insights</h3>
        <div className="space-y-4">
          {predictions?.market_trends?.map((trend, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">{trend.category}</p>
                <p className="text-sm text-gray-600">{trend.insight}</p>
              </div>
            </div>
          )) || [
            <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm font-medium text-gray-900">Marketplace Growth</p>
                <p className="text-sm text-gray-600">Steady growth expected based on current trends</p>
              </div>
            </div>
          ]}
        </div>
      </div>
    </div>
  );

  const renderRecommendationsTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-6">Business Recommendations</h3>
        
        <div className="space-y-4">
          {kpisData?.recommendations?.map((rec, index) => (
            <div key={index} className="border-l-4 border-blue-500 pl-4 py-3">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">{rec.category}</h4>
                <span className={`px-2 py-1 text-xs rounded ${
                  rec.priority === 'high' 
                    ? 'bg-red-100 text-red-800' 
                    : rec.priority === 'medium'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-green-100 text-green-800'
                }`}>
                  {rec.priority} priority
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-2">{rec.message}</p>
              {rec.expected_impact && (
                <p className="text-xs text-blue-600 font-medium">
                  Expected Impact: {rec.expected_impact}
                </p>
              )}
            </div>
          )) || []}
        </div>
      </div>

      {/* Performance Indicators */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-6">Performance Indicators</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {dashboardData?.performance_indicators && Object.entries(dashboardData.performance_indicators).map(([key, value]) => (
            <div key={key} className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-lg font-semibold text-gray-900 mb-1">
                {typeof value === 'number' ? value.toFixed(1) : value}
              </div>
              <div className="text-sm text-gray-600 capitalize">
                {key.replace('_', ' ')}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Business Intelligence Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Comprehensive analytics and insights for Cataloro Marketplace
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { id: 'overview', name: 'Overview', icon: '📊' },
              { id: 'predictions', name: 'Predictions', icon: '🔮' },
              { id: 'recommendations', name: 'Recommendations', icon: '💡' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
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
        {activeTab === 'predictions' && renderPredictionsTab()}
        {activeTab === 'recommendations' && renderRecommendationsTab()}

        {/* Refresh Button */}
        <div className="mt-8 text-center">
          <button
            onClick={fetchAnalyticsData}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh Analytics Data
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;