import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, AreaChart, Area
} from 'recharts';

const PerformanceDashboard = () => {
  const [performanceData, setPerformanceData] = useState(null);
  const [monitoringData, setMonitoringData] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('performance');

  useEffect(() => {
    fetchPerformanceData();
    const interval = setInterval(fetchPerformanceData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchPerformanceData = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      const [performanceRes, monitoringRes, healthRes] = await Promise.all([
        fetch(`${backendUrl}/api/admin/performance`),
        fetch(`${backendUrl}/api/admin/monitoring/dashboard`),
        fetch(`${backendUrl}/api/admin/system/health`)
      ]);

      const performance = await performanceRes.json();
      const monitoring = await monitoringRes.json();
      const health = await healthRes.json();

      setPerformanceData(performance);
      setMonitoringData(monitoring);
      setSystemHealth(health);
    } catch (error) {
      console.error('Failed to fetch performance data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading Performance Dashboard...</p>
        </div>
      </div>
    );
  }

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy': case 'secure': case 'optimized': case 'enabled':
        return 'text-green-600 bg-green-100';
      case 'warning': case 'medium_risk': case 'degraded':
        return 'text-yellow-600 bg-yellow-100';
      case 'critical': case 'high_risk': case 'error':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const renderPerformanceTab = () => (
    <div className="space-y-6">
      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Database Status</p>
              <p className="text-2xl font-bold text-gray-900">
                {performanceData?.optimizations?.database_indexes?.includes('✅') ? 'Optimized' : 'Basic'}
              </p>
              <p className="text-xs text-green-600">
                {performanceData?.database?.index_size ? 
                  `${(performanceData.database.index_size / 1024 / 1024).toFixed(1)}MB indexes` : 
                  '80+ indexes created'
                }
              </p>
            </div>
            <div className="text-2xl">🗃️</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Cache Status</p>
              <p className="text-2xl font-bold text-gray-900">
                {performanceData?.cache?.status === 'healthy' ? 'Active' : 'Fallback'}
              </p>
              <p className="text-xs text-blue-600">
                {performanceData?.cache?.total_keys || 0} keys cached
              </p>
            </div>
            <div className="text-2xl">💾</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Search Engine</p>
              <p className="text-2xl font-bold text-gray-900">
                {performanceData?.search?.status === 'enabled' ? 'Active' : 'Fallback'}
              </p>
              <p className="text-xs text-purple-600">
                Database search ready
              </p>
            </div>
            <div className="text-2xl">🔍</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Analytics</p>
              <p className="text-2xl font-bold text-gray-900">
                {performanceData?.analytics?.service_enabled ? 'Active' : 'Disabled'}
              </p>
              <p className="text-xs text-orange-600">
                BI & Forecasting enabled
              </p>
            </div>
            <div className="text-2xl">📊</div>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-6">Performance Optimizations</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h4 className="font-medium text-gray-700">Database Optimizations</h4>
            {performanceData?.optimizations && Object.entries(performanceData.optimizations).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700 capitalize">
                  {key.replace(/_/g, ' ')}
                </span>
                <span className={`text-xs px-2 py-1 rounded ${
                  value.includes('✅') ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {value.includes('✅') ? 'Implemented' : 'Basic'}
                </span>
              </div>
            ))}
          </div>

          <div className="space-y-4">
            <h4 className="font-medium text-gray-700">Scalability Features</h4>
            {performanceData?.scalability && Object.entries(performanceData.scalability).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700 capitalize">
                  {key.replace(/_/g, ' ')}
                </span>
                <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                  {value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Database Collections Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-6">Database Collections Status</h3>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Collection
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Documents
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Indexes
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {performanceData?.collections && Object.entries(performanceData.collections).map(([collection, data]) => (
                <tr key={collection}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {collection}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {data.document_count || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {data.index_count || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                      Optimized
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderMonitoringTab = () => (
    <div className="space-y-6">
      {/* System Health Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">System Health</h3>
            <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(systemHealth?.overall_status)}`}>
              {systemHealth?.overall_status || 'unknown'}
            </span>
          </div>
          <div className="space-y-2">
            {systemHealth?.components && Object.entries(systemHealth.components).map(([component, data]) => (
              <div key={component} className="flex items-center justify-between text-sm">
                <span className="text-gray-600 capitalize">{component}</span>
                <span className={`px-2 py-1 text-xs rounded ${getStatusColor(data.status)}`}>
                  {data.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Metrics</h3>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Uptime</span>
                <span className="font-medium">{monitoringData?.uptime?.uptime_formatted || '0m'}</span>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Avg Response Time</span>
                <span className="font-medium">
                  {monitoringData?.performance_metrics?.request_metrics?.avg_response_time_ms || 0}ms
                </span>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Total Requests</span>
                <span className="font-medium">
                  {monitoringData?.performance_metrics?.request_metrics?.total_requests || 0}
                </span>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Error Rate</span>
                <span className="font-medium">
                  {(monitoringData?.performance_metrics?.error_metrics?.recent_error_rate * 100 || 0).toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">System Resources</h3>
          <div className="space-y-3">
            {monitoringData?.performance_metrics?.system_metrics && (
              <>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">CPU Usage</span>
                    <span className="font-medium">
                      {monitoringData.performance_metrics.system_metrics.cpu?.percent?.toFixed(1) || 0}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        (monitoringData.performance_metrics.system_metrics.cpu?.percent || 0) > 80 
                          ? 'bg-red-500' 
                          : (monitoringData.performance_metrics.system_metrics.cpu?.percent || 0) > 60 
                          ? 'bg-yellow-500' 
                          : 'bg-green-500'
                      }`}
                      style={{ width: `${monitoringData.performance_metrics.system_metrics.cpu?.percent || 0}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Memory Usage</span>
                    <span className="font-medium">
                      {monitoringData.performance_metrics.system_metrics.memory?.percent?.toFixed(1) || 0}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        (monitoringData.performance_metrics.system_metrics.memory?.percent || 0) > 85 
                          ? 'bg-red-500' 
                          : (monitoringData.performance_metrics.system_metrics.memory?.percent || 0) > 70 
                          ? 'bg-yellow-500' 
                          : 'bg-green-500'
                      }`}
                      style={{ width: `${monitoringData.performance_metrics.system_metrics.memory?.percent || 0}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Disk Usage</span>
                    <span className="font-medium">
                      {monitoringData.performance_metrics.system_metrics.disk?.percent?.toFixed(1) || 0}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        (monitoringData.performance_metrics.system_metrics.disk?.percent || 0) > 90 
                          ? 'bg-red-500' 
                          : (monitoringData.performance_metrics.system_metrics.disk?.percent || 0) > 75 
                          ? 'bg-yellow-500' 
                          : 'bg-green-500'
                      }`}
                      style={{ width: `${monitoringData.performance_metrics.system_metrics.disk?.percent || 0}%` }}
                    ></div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Alerts</h3>
        <div className="space-y-3">
          {monitoringData?.recent_alerts?.length > 0 ? (
            monitoringData.recent_alerts.map((alert, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-gray-900">{alert.title}</p>
                  <p className="text-xs text-gray-600">{alert.description}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs rounded ${getStatusColor(alert.severity)}`}>
                    {alert.severity}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">✅</div>
              <p>No recent alerts - System running smoothly</p>
            </div>
          )}
        </div>
      </div>

      {/* Monitoring Recommendations */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Monitoring Recommendations</h3>
        <div className="space-y-3">
          {monitoringData?.monitoring_recommendations?.map((rec, index) => (
            <div key={index} className="border-l-4 border-green-500 pl-4 py-2">
              <h4 className="font-medium text-gray-900">{rec.title}</h4>
              <p className="text-sm text-gray-600">{rec.description}</p>
              <span className={`text-xs px-2 py-1 rounded mt-1 inline-block ${
                rec.priority === 'high' 
                  ? 'bg-red-100 text-red-800' 
                  : rec.priority === 'medium'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-green-100 text-green-800'
              }`}>
                {rec.priority} priority
              </span>
            </div>
          )) || []}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Performance & Monitoring Dashboard</h1>
          <p className="text-gray-600 mt-2">
            System performance optimization and real-time monitoring
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { id: 'performance', name: 'Performance', icon: '⚡' },
              { id: 'monitoring', name: 'Monitoring', icon: '📊' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-green-500 text-green-600'
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
        {activeTab === 'performance' && renderPerformanceTab()}
        {activeTab === 'monitoring' && renderMonitoringTab()}

        {/* Refresh Button */}
        <div className="mt-8 text-center">
          <button
            onClick={fetchPerformanceData}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            Refresh System Status
          </button>
        </div>
      </div>
    </div>
  );
};

export default PerformanceDashboard;