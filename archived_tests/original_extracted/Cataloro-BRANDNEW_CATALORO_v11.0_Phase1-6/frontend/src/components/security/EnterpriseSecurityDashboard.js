import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  RefreshCw,
  Eye,
  Users,
  Activity,
  Clock,
  FileText,
  Settings,
  Lock,
  Unlock,
  AlertCircle
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';

const EnterpriseSecurityDashboard = ({ className = '' }) => {
  const [securityData, setSecurityData] = useState(null);
  const [complianceData, setComplianceData] = useState(null);
  const [userInsights, setUserInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h');

  useEffect(() => {
    fetchSecurityData();
  }, [selectedTimeframe]);

  const fetchSecurityData = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      const [securityRes, complianceRes, insightsRes] = await Promise.all([
        fetch(`${backendUrl}/api/v2/phase6/security/dashboard`),
        fetch(`${backendUrl}/api/v2/phase6/security/compliance`),
        fetch(`${backendUrl}/api/v2/phase6/security/user-insights?limit=10`)
      ]);

      const [security, compliance, insights] = await Promise.all([
        securityRes.json(),
        complianceRes.json(),
        insightsRes.json()
      ]);

      if (security.success) setSecurityData(security.security_data);
      if (compliance.success) setComplianceData(compliance.compliance);
      if (insights.success) setUserInsights(insights.user_insights);

    } catch (error) {
      console.error('Failed to fetch security data:', error);
    } finally {
      setLoading(false);
    }
  };

  const logSecurityEvent = async (eventType, severity, description) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      await fetch(`${backendUrl}/api/v2/phase6/security/log-event`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_type: eventType,
          severity: severity,
          description: description,
          ip_address: '127.0.0.1'
        })
      });
      
      // Refresh data after logging event
      fetchSecurityData();
    } catch (error) {
      console.error('Failed to log security event:', error);
    }
  };

  const getSecurityScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getThreatLevelColor = (level) => {
    switch (level.toLowerCase()) {
      case 'low':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
      case 'high':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300';
      case 'critical':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
    }
  };

  const getComplianceStatusIcon = (status) => {
    switch (status) {
      case 'pass':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'fail':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const COLORS = ['#22c55e', '#ef4444', '#f59e0b', '#6b7280'];

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-red-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading security dashboard...</p>
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
          <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
            <Shield className="w-6 h-6 text-red-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Enterprise Security
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Advanced security monitoring and compliance management
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <select
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          
          <button
            onClick={fetchSecurityData}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Security Overview Cards */}
      {securityData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <Activity className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <div className={`text-2xl font-bold ${getSecurityScoreColor(securityData.overview.security_score)}`}>
                  {securityData.overview.security_score}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Security Score</div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {securityData.overview.critical_events}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Critical Events</div>
                <span className={`text-xs px-2 py-1 rounded-full ${getThreatLevelColor(securityData.threat_levels.current_threat_level)}`}>
                  {securityData.threat_levels.current_threat_level.toUpperCase()}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
                <Clock className="w-5 h-5 text-yellow-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {securityData.overview.unresolved_events}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Pending Events</div>
                <div className="text-sm text-orange-600">
                  {securityData.overview.recent_events_24h} in 24h
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <Users className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {securityData.overview.high_risk_users}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">High Risk Users</div>
                <div className="text-sm text-purple-600">
                  {securityData.overview.risk_percentage.toFixed(1)}% of total
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Security Events and Threat Analysis */}
      {securityData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Event Distribution Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Security Event Distribution
            </h3>
            
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={Object.entries(securityData.event_distribution).map(([key, value]) => ({
                name: key.replace('_', ' ').toUpperCase(),
                count: value
              }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Recent Security Events */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Recent Security Events
            </h3>
            
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {securityData.recent_events.map((event, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className={`p-1 rounded-full ${
                    event.severity === 'critical' ? 'bg-red-100 text-red-600' :
                    event.severity === 'high' ? 'bg-orange-100 text-orange-600' :
                    event.severity === 'medium' ? 'bg-yellow-100 text-yellow-600' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    <AlertTriangle className="w-3 h-3" />
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-gray-900 dark:text-white text-sm">
                        {event.type.replace('_', ' ').toUpperCase()}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        event.resolved ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {event.resolved ? 'Resolved' : 'Active'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                      {event.description}
                    </p>
                    <div className="text-xs text-gray-500">
                      {new Date(event.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Compliance Status */}
      {complianceData && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Compliance Status
            </h3>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Overall Score:</span>
              <span className={`font-bold ${getSecurityScoreColor(complianceData.overview.compliance_score)}`}>
                {complianceData.overview.compliance_score.toFixed(1)}%
              </span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Compliance by Category */}
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-3">By Category</h4>
              <div className="space-y-3">
                {Object.entries(complianceData.by_category).map(([category, stats]) => (
                  <div key={category} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900 dark:text-white">{category}</span>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {stats.pass}/{stats.total} passed
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: `${(stats.pass / stats.total) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Failing Checks */}
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-3">
                Issues Requiring Attention ({complianceData.failing_checks.length})
              </h4>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {complianceData.failing_checks.map((check, index) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                    {getComplianceStatusIcon('fail')}
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 dark:text-white text-sm">
                        {check.name}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        {check.category}
                      </div>
                      <div className="text-xs text-red-600 dark:text-red-400 mt-1">
                        Next check: {new Date(check.next_check).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* User Security Insights */}
      {userInsights.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            User Security Insights
          </h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {userInsights.slice(0, 10).map((user, index) => (
              <div key={index} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-gray-900 dark:text-white">
                      User {user.user_id.slice(-6)}
                    </span>
                    {user.mfa_enabled ? (
                      <Lock className="w-4 h-4 text-green-500" />
                    ) : (
                      <Unlock className="w-4 h-4 text-red-500" />
                    )}
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    user.risk_level === 'high' ? 'bg-red-100 text-red-800' :
                    user.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {user.risk_level.toUpperCase()} RISK
                  </span>
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Risk Score:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {(user.risk_score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Suspicious Activities:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {user.suspicious_activities}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Location Anomalies:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {user.location_anomalies}
                    </span>
                  </div>
                </div>
                
                {user.recommendations.length > 0 && (
                  <div className="mt-3 text-xs text-blue-600 dark:text-blue-400">
                    💡 {user.recommendations[0]}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Security Recommendations */}
      {securityData && securityData.recommendations && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Security Recommendations
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {securityData.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <div className="p-1 bg-red-100 dark:bg-red-900/30 rounded">
                  <Shield className="w-4 h-4 text-red-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900 dark:text-white">{recommendation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Quick Security Actions
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => logSecurityEvent('security_scan', 'medium', 'Manual security scan initiated')}
            className="flex items-center space-x-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
          >
            <Eye className="w-5 h-5 text-blue-600" />
            <span className="font-medium text-gray-900 dark:text-white">Run Security Scan</span>
          </button>
          
          <button
            onClick={() => logSecurityEvent('compliance_check', 'low', 'Manual compliance check initiated')}
            className="flex items-center space-x-2 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
          >
            <FileText className="w-5 h-5 text-green-600" />
            <span className="font-medium text-gray-900 dark:text-white">Check Compliance</span>
          </button>
          
          <button
            onClick={() => logSecurityEvent('security_review', 'high', 'Manual security review requested')}
            className="flex items-center space-x-2 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg hover:bg-yellow-100 dark:hover:bg-yellow-900/30 transition-colors"
          >
            <Settings className="w-5 h-5 text-yellow-600" />
            <span className="font-medium text-gray-900 dark:text-white">Request Review</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default EnterpriseSecurityDashboard;