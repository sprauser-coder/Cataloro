import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar
} from 'recharts';

const SecurityDashboard = () => {
  const [securityData, setSecurityData] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchSecurityData();
    const interval = setInterval(fetchSecurityData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const fetchSecurityData = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      const response = await fetch(`${backendUrl}/api/admin/security/dashboard`);
      const data = await response.json();

      setSecurityData(data.security_metrics);
      setAuditLogs(data.recent_audit_logs || []);
      setAlerts(data.active_security_alerts || []);
    } catch (error) {
      console.error('Failed to fetch security data:', error);
    } finally {
      setLoading(false);
    }
  };

  const resolveAlert = async (alertId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      const response = await fetch(`${backendUrl}/api/admin/security/alerts/${alertId}/resolve`, {
        method: 'POST'
      });

      if (response.ok) {
        fetchSecurityData(); // Refresh data
      }
    } catch (error) {
      console.error('Failed to resolve alert:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading Security Dashboard...</p>
        </div>
      </div>
    );
  }

  const getSecurityStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'secure':
        return 'text-green-600 bg-green-100';
      case 'medium_risk':
        return 'text-yellow-600 bg-yellow-100';
      case 'high_risk':
        return 'text-orange-600 bg-orange-100';
      case 'critical':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* Security Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Security Status</p>
              <p className="text-2xl font-bold text-gray-900 capitalize">
                {securityData?.security_status || 'Unknown'}
              </p>
              <span className={`text-xs px-2 py-1 rounded-full ${getSecurityStatusColor(securityData?.security_status)}`}>
                {securityData?.security_status || 'unknown'}
              </span>
            </div>
            <div className="text-2xl">🛡️</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Failed Login Attempts</p>
              <p className="text-2xl font-bold text-gray-900">
                {securityData?.failed_login_attempts?.recent_attempts_last_hour || 0}
              </p>
              <p className="text-xs text-red-600">
                {securityData?.failed_login_attempts?.blocked_identifiers || 0} blocked
              </p>
            </div>
            <div className="text-2xl">🔐</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Security Alerts</p>
              <p className="text-2xl font-bold text-gray-900">
                {securityData?.security_alerts?.active_alerts || 0}
              </p>
              <p className="text-xs text-orange-600">
                {securityData?.security_alerts?.recent_alerts_last_hour || 0} recent
              </p>
            </div>
            <div className="text-2xl">🚨</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Audit Entries</p>
              <p className="text-2xl font-bold text-gray-900">
                {securityData?.audit_logs?.total_entries || 0}
              </p>
              <p className="text-xs text-blue-600">
                {securityData?.audit_logs?.recent_entries_last_hour || 0} recent
              </p>
            </div>
            <div className="text-2xl">📋</div>
          </div>
        </div>
      </div>

      {/* Alert Severity Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Alert Severity Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={securityData?.security_alerts?.alert_severity_breakdown ? 
                  Object.entries(securityData.security_alerts.alert_severity_breakdown).map(([severity, count]) => ({
                    name: severity,
                    value: count,
                    color: severity === 'critical' ? '#ef4444' : 
                           severity === 'high' ? '#f97316' :
                           severity === 'medium' ? '#eab308' : '#22c55e'
                  })) : []
                }
                cx="50%" cy="50%" innerRadius={40} outerRadius={100}
                paddingAngle={5} dataKey="value"
              >
                {securityData?.security_alerts?.alert_severity_breakdown && 
                  Object.entries(securityData.security_alerts.alert_severity_breakdown).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={
                      entry[0] === 'critical' ? '#ef4444' : 
                      entry[0] === 'high' ? '#f97316' :
                      entry[0] === 'medium' ? '#eab308' : '#22c55e'
                    } />
                  ))
                }
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Security Metrics Summary</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">Total Unique Login Attempts</span>
              <span className="text-lg font-bold text-gray-900">
                {securityData?.failed_login_attempts?.total_unique_identifiers || 0}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">Blocked Identifiers</span>
              <span className="text-lg font-bold text-red-600">
                {securityData?.failed_login_attempts?.blocked_identifiers || 0}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">Total Audit Entries</span>
              <span className="text-lg font-bold text-blue-600">
                {securityData?.audit_logs?.total_entries || 0}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
              <span className="text-sm font-medium text-gray-700">Total Security Alerts</span>
              <span className="text-lg font-bold text-orange-600">
                {securityData?.security_alerts?.total_alerts || 0}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAlertsTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-medium text-gray-900">Active Security Alerts</h3>
          <span className="text-sm text-gray-500">
            {alerts.length} active alerts
          </span>
        </div>

        {alerts.length > 0 ? (
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div key={alert.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="font-medium text-gray-900">{alert.title}</h4>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                        alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                        alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {alert.severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{alert.description}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(alert.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <div className="ml-4">
                    <button
                      onClick={() => resolveAlert(alert.id)}
                      className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                    >
                      Resolve
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">✅</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Active Security Alerts</h3>
            <p className="text-gray-600">Your system is secure with no pending security issues.</p>
          </div>
        )}
      </div>
    </div>
  );

  const renderAuditLogsTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-6">Recent Audit Logs</h3>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Resource
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  IP Address
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Details
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {auditLogs.slice(0, 50).map((log) => (
                <tr key={log.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {log.user_id || 'system'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {log.action}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {log.resource}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {log.ip_address || 'N/A'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {log.details ? JSON.stringify(log.details).substring(0, 100) + '...' : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderRecommendationsTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-6">Security Recommendations</h3>
        
        <div className="space-y-4">
          <div className="border-l-4 border-green-500 pl-4 py-3">
            <h4 className="font-medium text-gray-900">Rate Limiting Active</h4>
            <p className="text-sm text-gray-600 mb-2">
              API rate limiting is active and protecting against brute force attacks.
            </p>
            <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">
              ✅ Implemented
            </span>
          </div>

          <div className="border-l-4 border-green-500 pl-4 py-3">
            <h4 className="font-medium text-gray-900">Input Validation & Sanitization</h4>
            <p className="text-sm text-gray-600 mb-2">
              All user inputs are validated and sanitized to prevent XSS and injection attacks.
            </p>
            <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">
              ✅ Implemented
            </span>
          </div>

          <div className="border-l-4 border-green-500 pl-4 py-3">
            <h4 className="font-medium text-gray-900">Comprehensive Audit Logging</h4>
            <p className="text-sm text-gray-600 mb-2">
              All security-relevant actions are logged for monitoring and compliance.
            </p>
            <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">
              ✅ Implemented
            </span>
          </div>

          <div className="border-l-4 border-blue-500 pl-4 py-3">
            <h4 className="font-medium text-gray-900">Monitor Failed Login Patterns</h4>
            <p className="text-sm text-gray-600 mb-2">
              Regularly review failed login attempts for suspicious patterns and potential threats.
            </p>
            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
              Monitor Regularly
            </span>
          </div>

          <div className="border-l-4 border-yellow-500 pl-4 py-3">
            <h4 className="font-medium text-gray-900">Two-Factor Authentication</h4>
            <p className="text-sm text-gray-600 mb-2">
              Consider implementing 2FA for admin accounts to enhance security further.
            </p>
            <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded">
              Future Enhancement
            </span>
          </div>

          <div className="border-l-4 border-yellow-500 pl-4 py-3">
            <h4 className="font-medium text-gray-900">Security Headers</h4>
            <p className="text-sm text-gray-600 mb-2">
              Implement additional security headers (HSTS, CSP, etc.) for enhanced protection.
            </p>
            <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded">
              Future Enhancement
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Security Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Comprehensive security monitoring and threat management
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { id: 'overview', name: 'Overview', icon: '🛡️' },
              { id: 'alerts', name: 'Alerts', icon: '🚨' },
              { id: 'audit', name: 'Audit Logs', icon: '📋' },
              { id: 'recommendations', name: 'Recommendations', icon: '💡' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-red-500 text-red-600'
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
        {activeTab === 'alerts' && renderAlertsTab()}
        {activeTab === 'audit' && renderAuditLogsTab()}
        {activeTab === 'recommendations' && renderRecommendationsTab()}

        {/* Refresh Button */}
        <div className="mt-8 text-center">
          <button
            onClick={fetchSecurityData}
            className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors"
          >
            Refresh Security Status
          </button>
        </div>
      </div>
    </div>
  );
};

export default SecurityDashboard;