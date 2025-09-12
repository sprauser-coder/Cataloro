import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  Shield, 
  DollarSign, 
  Users, 
  Activity,
  RefreshCw,
  Eye,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  BarChart3,
  PieChart as PieChartIcon
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';

const FraudDetectionDashboard = ({ className = '' }) => {
  const [fraudData, setFraudData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState('24h');

  useEffect(() => {
    fetchFraudData();
  }, [selectedTimeframe]);

  const fetchFraudData = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      const response = await fetch(`${backendUrl}/api/v2/phase6/fraud/dashboard`);
      const data = await response.json();

      if (data.success) {
        setFraudData(data.fraud_data);
      }
    } catch (error) {
      console.error('Failed to fetch fraud data:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeTransaction = async (transactionData) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/v2/phase6/fraud/analyze-transaction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(transactionData)
      });
      
      const result = await response.json();
      if (result.success) {
        alert(`Transaction Analysis:\nFraud Probability: ${(result.analysis.fraud_probability * 100).toFixed(1)}%\nRecommendation: ${result.analysis.recommendation.toUpperCase()}`);
        fetchFraudData(); // Refresh data
      }
    } catch (error) {
      console.error('Failed to analyze transaction:', error);
    }
  };

  const resolveAlert = async (alertId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/v2/phase6/fraud/resolve-alert/${alertId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resolution: 'resolved',
          notes: 'Resolved from dashboard'
        })
      });
      
      const result = await response.json();
      if (result.success) {
        fetchFraudData(); // Refresh data
      }
    } catch (error) {
      console.error('Failed to resolve alert:', error);
    }
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'high':
        return 'text-red-600 bg-red-100 dark:bg-red-900/30 dark:text-red-400';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'low':
        return 'text-green-600 bg-green-100 dark:bg-green-900/30 dark:text-green-400';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900/30 dark:text-gray-400';
    }
  };

  const getRecommendationColor = (recommendation) => {
    switch (recommendation) {
      case 'block':
        return 'text-red-600 bg-red-100 dark:bg-red-900/30 dark:text-red-400';
      case 'review':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'approve':
        return 'text-green-600 bg-green-100 dark:bg-green-900/30 dark:text-green-400';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900/30 dark:text-gray-400';
    }
  };

  const COLORS = ['#ef4444', '#f59e0b', '#22c55e', '#3b82f6', '#8b5cf6'];

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-orange-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading fraud detection dashboard...</p>
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
          <div className="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
            <AlertTriangle className="w-6 h-6 text-orange-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Fraud Detection
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              AI-powered fraud detection and transaction monitoring
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
            onClick={fetchFraudData}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Overview Cards */}
      {fraudData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-lg">
                <AlertTriangle className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {fraudData.overview.active_alerts}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Active Alerts</div>
                <div className="text-sm text-red-600">
                  {fraudData.overview.recent_alerts_24h} in 24h
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {fraudData.overview.detection_accuracy.toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Detection Accuracy</div>
                <div className="text-sm text-green-600">
                  {fraudData.overview.false_positive_rate.toFixed(1)}% false positive
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <DollarSign className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {fraudData.transaction_metrics.blocked_today}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Blocked Today</div>
                <div className="text-sm text-blue-600">
                  {fraudData.transaction_metrics.approved_today} approved
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
                  {fraudData.risk_metrics.high_risk_users}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">High Risk Users</div>
                <div className="text-sm text-purple-600">
                  Avg Risk: {(fraudData.risk_metrics.average_risk_score * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Fraud Type Distribution and Recent Alerts */}
      {fraudData && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Fraud Type Distribution */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Fraud Type Distribution
            </h3>
            
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={Object.entries(fraudData.fraud_types).map(([key, value]) => ({
                    name: key.replace('_', ' ').toUpperCase(),
                    value: value
                  }))}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {Object.entries(fraudData.fraud_types).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Recent Fraud Alerts */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Recent Fraud Alerts
            </h3>
            
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {fraudData.recent_alerts.map((alert, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className={`p-1 rounded-full ${
                    alert.risk_score >= 0.8 ? 'bg-red-100 text-red-600' :
                    alert.risk_score >= 0.5 ? 'bg-yellow-100 text-yellow-600' :
                    'bg-green-100 text-green-600'
                  }`}>
                    <AlertTriangle className="w-3 h-3" />
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-gray-900 dark:text-white text-sm">
                        {alert.type.replace('_', ' ').toUpperCase()}
                      </span>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-gray-600 dark:text-gray-400">
                          Risk: {(alert.risk_score * 100).toFixed(0)}%
                        </span>
                        {alert.status === 'active' && (
                          <button
                            onClick={() => resolveAlert(alert.id)}
                            className="text-xs text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                          >
                            Resolve
                          </button>
                        )}
                      </div>
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                      User: {alert.user_id} | Confidence: {(alert.confidence * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(alert.detected_at).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Transaction Analysis Tool */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Transaction Analysis Tool
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <button
            onClick={() => analyzeTransaction({
              user_id: 'test_user_001',
              amount: 5000,
              payment_method: 'credit_card',
              transaction_id: `tx_${Date.now()}`
            })}
            className="flex items-center justify-center space-x-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
          >
            <DollarSign className="w-5 h-5 text-blue-600" />
            <span className="font-medium text-gray-900 dark:text-white">Test High Amount (€5,000)</span>
          </button>
          
          <button
            onClick={() => analyzeTransaction({
              user_id: 'test_user_002',
              amount: 500,
              payment_method: 'prepaid_card',
              unusual_location: true,
              transaction_id: `tx_${Date.now()}`
            })}
            className="flex items-center justify-center space-x-2 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg hover:bg-yellow-100 dark:hover:bg-yellow-900/30 transition-colors"
          >
            <AlertTriangle className="w-5 h-5 text-yellow-600" />
            <span className="font-medium text-gray-900 dark:text-white">Test Suspicious Location</span>
          </button>
          
          <button
            onClick={() => analyzeTransaction({
              user_id: 'test_user_003',
              amount: 100,
              payment_method: 'bank_transfer',
              transaction_id: `tx_${Date.now()}`
            })}
            className="flex items-center justify-center space-x-2 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
          >
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="font-medium text-gray-900 dark:text-white">Test Normal Transaction</span>
          </button>
        </div>
      </div>

      {/* Fraud Detection Trends */}
      {fraudData && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Detection Performance Trends
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center justify-center mb-2">
                <TrendingUp className="w-5 h-5 text-green-500 mr-2" />
                <span className="font-medium text-gray-900 dark:text-white">Fraud Trend</span>
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {fraudData.trends.fraud_trend}
              </div>
            </div>
            
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center justify-center mb-2">
                <Activity className="w-5 h-5 text-blue-500 mr-2" />
                <span className="font-medium text-gray-900 dark:text-white">Detection Trend</span>
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {fraudData.trends.detection_trend}
              </div>
            </div>
            
            <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center justify-center mb-2">
                <BarChart3 className="w-5 h-5 text-purple-500 mr-2" />
                <span className="font-medium text-gray-900 dark:text-white">False Positive Trend</span>
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {fraudData.trends.false_positive_trend}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {fraudData && fraudData.recommendations && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Fraud Prevention Recommendations
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {fraudData.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                <div className="p-1 bg-orange-100 dark:bg-orange-900/30 rounded">
                  <Shield className="w-4 h-4 text-orange-600" />
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

export default FraudDetectionDashboard;