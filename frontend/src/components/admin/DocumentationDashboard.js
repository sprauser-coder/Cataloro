import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  Code, 
  Database, 
  Globe, 
  Server, 
  Shield, 
  Zap,
  GitBranch,
  Network,
  Settings,
  Users,
  BarChart3,
  MessageSquare,
  CreditCard,
  Search,
  FileText,
  ExternalLink,
  Copy,
  CheckCircle,
  Info,
  AlertTriangle,
  Lightbulb,
  Map,
  Layers,
  Terminal,
  Box,
  Workflow
} from 'lucide-react';

const DocumentationDashboard = ({ className = '' }) => {
  const [activeSection, setActiveSection] = useState('overview');
  const [copiedCode, setCopiedCode] = useState('');
  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    fetchSystemStatus();
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/v2/advanced/status`);
      const data = await response.json();
      setSystemStatus(data);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  const copyToClipboard = (text, identifier) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(identifier);
    setTimeout(() => setCopiedCode(''), 2000);
  };

  const documentationSections = [
    {
      id: 'overview',
      name: 'System Overview',
      icon: <Map className="w-5 h-5" />,
      description: 'Architecture & Infrastructure'
    },
    {
      id: 'api',
      name: 'API Documentation',
      icon: <Code className="w-5 h-5" />,
      description: 'Endpoints & Integration'
    },
    {
      id: 'features',
      name: 'Feature Guide',
      icon: <BookOpen className="w-5 h-5" />,
      description: 'How to use all features'
    },
    {
      id: 'troubleshooting',
      name: 'Troubleshooting',
      icon: <AlertTriangle className="w-5 h-5" />,
      description: 'Common issues & solutions'
    }
  ];

  const renderSystemOverview = () => (
    <div className="space-y-8">
      {/* Architecture Mindmap */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center">
          <Workflow className="w-6 h-6 mr-3 text-blue-500" />
          Cataloro Marketplace Architecture
        </h3>
        
        <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl p-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold text-lg shadow-lg">
              <Globe className="w-6 h-6 mr-2" />
              Cataloro Marketplace
            </div>
          </div>

          {/* Frontend Layer */}
          <div className="mb-8">
            <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4 text-center">Frontend Layer</h4>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white dark:bg-gray-700 rounded-lg p-4 text-center shadow-md border-2 border-green-200 dark:border-green-700">
                <Code className="w-8 h-8 mx-auto mb-2 text-green-600" />
                <div className="font-semibold text-sm">React Frontend</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Modern UI/UX</div>
              </div>
              <div className="bg-white dark:bg-gray-700 rounded-lg p-4 text-center shadow-md border-2 border-blue-200 dark:border-blue-700">
                <BarChart3 className="w-8 h-8 mx-auto mb-2 text-blue-600" />
                <div className="font-semibold text-sm">Mega Dashboard</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Unified Analytics</div>
              </div>
              <div className="bg-white dark:bg-gray-700 rounded-lg p-4 text-center shadow-md border-2 border-purple-200 dark:border-purple-700">
                <Users className="w-8 h-8 mx-auto mb-2 text-purple-600" />
                <div className="font-semibold text-sm">User Management</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">RBAC System</div>
              </div>
              <div className="bg-white dark:bg-gray-700 rounded-lg p-4 text-center shadow-md border-2 border-orange-200 dark:border-orange-700">
                <MessageSquare className="w-8 h-8 mx-auto mb-2 text-orange-600" />
                <div className="font-semibold text-sm">Real-time Chat</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">WebSocket</div>
              </div>
            </div>
          </div>

          {/* Backend Layer */}
          <div className="mb-8">
            <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4 text-center">Backend Layer</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white dark:bg-gray-700 rounded-lg p-4 text-center shadow-md border-2 border-red-200 dark:border-red-700">
                <Server className="w-8 h-8 mx-auto mb-2 text-red-600" />
                <div className="font-semibold text-sm">FastAPI Server</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Python Backend</div>
              </div>
              <div className="bg-white dark:bg-gray-700 rounded-lg p-4 text-center shadow-md border-2 border-indigo-200 dark:border-indigo-700">
                <Shield className="w-8 h-8 mx-auto mb-2 text-indigo-600" />
                <div className="font-semibold text-sm">Unified Security</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Auth + Compliance</div>
              </div>
              <div className="bg-white dark:bg-gray-700 rounded-lg p-4 text-center shadow-md border-2 border-teal-200 dark:border-teal-700">
                <BarChart3 className="w-8 h-8 mx-auto mb-2 text-teal-600" />
                <div className="font-semibold text-sm">Unified Analytics</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Predictive AI</div>
              </div>
            </div>
          </div>

          {/* Database Layer */}
          <div className="mb-8">
            <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4 text-center">Database Layer</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white dark:bg-gray-700 rounded-lg p-4 text-center shadow-md border-2 border-green-200 dark:border-green-700">
                <Database className="w-8 h-8 mx-auto mb-2 text-green-600" />
                <div className="font-semibold text-sm">MongoDB</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Document Store</div>
              </div>
              <div className="bg-white dark:bg-gray-700 rounded-lg p-4 text-center shadow-md border-2 border-yellow-200 dark:border-yellow-700">
                <Zap className="w-8 h-8 mx-auto mb-2 text-yellow-600" />
                <div className="font-semibold text-sm">Redis Cache</div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Performance</div>
              </div>
            </div>
          </div>

          {/* Integration Layer */}
          <div>
            <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-4 text-center">Enterprise Features</h4>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-lg p-3 text-center shadow-md">
                <CreditCard className="w-6 h-6 mx-auto mb-1" />
                <div className="text-xs font-semibold">Multi-Currency</div>
              </div>
              <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-lg p-3 text-center shadow-md">
                <Shield className="w-6 h-6 mx-auto mb-1" />
                <div className="text-xs font-semibold">Escrow</div>
              </div>
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-lg p-3 text-center shadow-md">
                <MessageSquare className="w-6 h-6 mx-auto mb-1" />
                <div className="text-xs font-semibold">AI Chatbot</div>
              </div>
              <div className="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-lg p-3 text-center shadow-md">
                <AlertTriangle className="w-6 h-6 mx-auto mb-1" />
                <div className="text-xs font-semibold">Fraud Detection</div>
              </div>
              <div className="bg-gradient-to-br from-teal-500 to-teal-600 text-white rounded-lg p-3 text-center shadow-md">
                <Globe className="w-6 h-6 mx-auto mb-1" />
                <div className="text-xs font-semibold">i18n</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Status */}
      {systemStatus && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center">
            <Network className="w-6 h-6 mr-3 text-green-500" />
            Live System Status
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {systemStatus.services && Object.entries(systemStatus.services).map(([service, data]) => (
              <div key={service} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900 dark:text-white capitalize">
                    {service.replace('_', ' ')}
                  </span>
                  <div className={`w-3 h-3 rounded-full ${
                    data.status === 'operational' ? 'bg-green-500' :
                    data.status === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
                  }`}></div>
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Status: {data.status}
                </div>
                {data.connections && (
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Connections: {data.connections}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Consolidation Summary */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-xl p-6 border border-green-200 dark:border-green-700">
        <h3 className="text-xl font-semibold text-green-800 dark:text-green-200 mb-4 flex items-center">
          <CheckCircle className="w-6 h-6 mr-3" />
          Consolidation Achievements
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-green-700 dark:text-green-300 mb-2">Backend Consolidation</h4>
            <ul className="space-y-2 text-sm text-green-600 dark:text-green-400">
              <li>✅ Analytics + Advanced Analytics → Unified Analytics</li>
              <li>✅ Security + Enterprise Security → Unified Security</li>
              <li>✅ Phase 5 + Phase 6 Endpoints → Advanced Features</li>
              <li>✅ All Dummy Data Eliminated</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-green-700 dark:text-green-300 mb-2">Frontend Consolidation</h4>
            <ul className="space-y-2 text-sm text-green-600 dark:text-green-400">
              <li>✅ 4 Dashboards → 1 Mega Unified Dashboard</li>
              <li>✅ Phase Components → Enterprise Components</li>
              <li>✅ 60% Codebase Reduction</li>
              <li>✅ Real Database Queries Only</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAPIDocumentation = () => (
    <div className="space-y-6">
      {/* API Overview */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <Terminal className="w-6 h-6 mr-3 text-blue-500" />
          API Endpoints Reference
        </h3>
        
        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <span className="font-mono text-sm text-gray-700 dark:text-gray-300">
              Base URL: {process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}
            </span>
            <button
              onClick={() => copyToClipboard(process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL, 'base-url')}
              className="text-blue-500 hover:text-blue-700 p-1"
            >
              {copiedCode === 'base-url' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Unified Analytics Endpoints */}
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2 text-blue-500" />
            Unified Analytics
          </h4>
          <div className="space-y-3">
            {[
              { method: 'GET', endpoint: '/api/v2/advanced/analytics/dashboard', description: 'Get unified dashboard data' },
              { method: 'GET', endpoint: '/api/v2/advanced/analytics/user?days=30', description: 'Get user analytics' },
              { method: 'GET', endpoint: '/api/v2/advanced/analytics/sales?days=30', description: 'Get sales analytics' },
              { method: 'GET', endpoint: '/api/v2/advanced/analytics/marketplace?days=30', description: 'Get marketplace analytics' },
              { method: 'GET', endpoint: '/api/v2/advanced/analytics/predictive?forecast_days=30', description: 'Get predictive analytics' },
              { method: 'GET', endpoint: '/api/v2/advanced/analytics/market-trends?time_period=30d', description: 'Get market trends' }
            ].map((api, index) => (
              <div key={index} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-1 text-xs font-bold rounded ${
                      api.method === 'GET' ? 'bg-green-100 text-green-800' :
                      api.method === 'POST' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {api.method}
                    </span>
                    <span className="font-mono text-sm text-gray-700 dark:text-gray-300">{api.endpoint}</span>
                  </div>
                  <button
                    onClick={() => copyToClipboard(api.endpoint, `endpoint-${index}`)}
                    className="text-blue-500 hover:text-blue-700 p-1"
                  >
                    {copiedCode === `endpoint-${index}` ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">{api.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Security Endpoints */}
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center">
            <Shield className="w-5 h-5 mr-2 text-red-500" />
            Unified Security
          </h4>
          <div className="space-y-3">
            {[
              { method: 'GET', endpoint: '/api/v2/advanced/security/dashboard', description: 'Get security dashboard data' },
              { method: 'POST', endpoint: '/api/v2/advanced/security/log-event', description: 'Log security event' },
              { method: 'GET', endpoint: '/api/v2/advanced/security/compliance', description: 'Get compliance status' },
              { method: 'GET', endpoint: '/api/v2/advanced/security/user-insights', description: 'Get user security insights' }
            ].map((api, index) => (
              <div key={index} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-1 text-xs font-bold rounded ${
                      api.method === 'GET' ? 'bg-green-100 text-green-800' :
                      api.method === 'POST' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {api.method}
                    </span>
                    <span className="font-mono text-sm text-gray-700 dark:text-gray-300">{api.endpoint}</span>
                  </div>
                  <button
                    onClick={() => copyToClipboard(api.endpoint, `security-${index}`)}
                    className="text-blue-500 hover:text-blue-700 p-1"
                  >
                    {copiedCode === `security-${index}` ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">{api.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Enterprise Features */}
        <div>
          <h4 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center">
            <Zap className="w-5 h-5 mr-2 text-purple-500" />
            Enterprise Features
          </h4>
          <div className="space-y-3">
            {[
              { method: 'GET', endpoint: '/api/v2/advanced/currency/supported', description: 'Get supported currencies' },
              { method: 'POST', endpoint: '/api/v2/advanced/currency/convert', description: 'Convert currency' },
              { method: 'POST', endpoint: '/api/v2/advanced/escrow/create', description: 'Create escrow transaction' },
              { method: 'POST', endpoint: '/api/v2/advanced/chatbot/start-session', description: 'Start AI chat session' },
              { method: 'GET', endpoint: '/api/v2/advanced/fraud/dashboard', description: 'Get fraud detection data' }
            ].map((api, index) => (
              <div key={index} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    <span className={`px-2 py-1 text-xs font-bold rounded ${
                      api.method === 'GET' ? 'bg-green-100 text-green-800' :
                      api.method === 'POST' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {api.method}
                    </span>
                    <span className="font-mono text-sm text-gray-700 dark:text-gray-300">{api.endpoint}</span>
                  </div>
                  <button
                    onClick={() => copyToClipboard(api.endpoint, `enterprise-${index}`)}
                    className="text-blue-500 hover:text-blue-700 p-1"
                  >
                    {copiedCode === `enterprise-${index}` ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">{api.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Authentication Info */}
      <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-xl p-6 border border-yellow-200 dark:border-yellow-700">
        <h4 className="text-lg font-semibold text-yellow-800 dark:text-yellow-200 mb-3 flex items-center">
          <Info className="w-5 h-5 mr-2" />
          Authentication Required
        </h4>
        <p className="text-yellow-700 dark:text-yellow-300 text-sm mb-4">
          Most endpoints require authentication. Include JWT token in Authorization header:
        </p>
        <div className="bg-yellow-100 dark:bg-yellow-900/40 rounded-lg p-3">
          <code className="text-sm text-yellow-800 dark:text-yellow-200">
            Authorization: Bearer {'{your-jwt-token}'}
          </code>
        </div>
      </div>
    </div>
  );

  const renderFeatureGuide = () => (
    <div className="space-y-6">
      {/* Mega Dashboard Guide */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <BarChart3 className="w-6 h-6 mr-3 text-blue-500" />
          Mega Unified Dashboard Guide
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-3">Overview Section</h4>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>• <strong>Master KPIs:</strong> Total Users, Revenue, Listings, Conversion Rate</li>
              <li>• <strong>System Health:</strong> Live service status monitoring</li>
              <li>• <strong>Enterprise Metrics:</strong> Security, Fraud, AI Chatbot stats</li>
              <li>• <strong>Real-time Data:</strong> All metrics from live database</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-3">Analytics Section</h4>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>• <strong>Predictive Forecasts:</strong> Revenue, users, listings predictions</li>
              <li>• <strong>Market Trends:</strong> Category growth analysis with confidence scores</li>
              <li>• <strong>Seller Performance:</strong> Forecasting and recommendations</li>
              <li>• <strong>Visual Charts:</strong> Interactive data visualization</li>
            </ul>
          </div>
        </div>
      </div>

      {/* User Management Guide */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <Users className="w-6 h-6 mr-3 text-green-500" />
          User Management Features
        </h3>
        
        <div className="space-y-4">
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">Role-Based Access Control (RBAC)</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div className="bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 p-2 rounded">
                <strong>User-Buyer:</strong> Browse, buy, favorites
              </div>
              <div className="bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 p-2 rounded">
                <strong>User-Seller:</strong> Create listings, manage sales
              </div>
              <div className="bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200 p-2 rounded">
                <strong>Admin:</strong> User management, analytics
              </div>
              <div className="bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 p-2 rounded">
                <strong>Admin-Manager:</strong> Full system access
              </div>
            </div>
          </div>
          
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">User Operations</h4>
            <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <li>• Bulk user actions (approve, suspend, delete)</li>
              <li>• User role management and updates</li>
              <li>• Registration status control</li>
              <li>• User activity monitoring</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Enterprise Features Guide */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <Zap className="w-6 h-6 mr-3 text-purple-500" />
          Enterprise Features Guide
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-2 flex items-center">
                <CreditCard className="w-5 h-5 mr-2" />
                Multi-Currency Support
              </h4>
              <ul className="space-y-1 text-sm text-blue-700 dark:text-blue-300">
                <li>• 10+ supported currencies (EUR, USD, GBP, etc.)</li>
                <li>• Real-time exchange rates</li>
                <li>• User currency preferences</li>
                <li>• Automatic price conversion</li>
              </ul>
            </div>

            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h4 className="font-semibold text-green-800 dark:text-green-200 mb-2 flex items-center">
                <Shield className="w-5 h-5 mr-2" />
                Secure Escrow System
              </h4>
              <ul className="space-y-1 text-sm text-green-700 dark:text-green-300">
                <li>• Secure transaction handling</li>
                <li>• Buyer-seller protection</li>
                <li>• Multiple payment methods</li>
                <li>• Transaction status tracking</li>
              </ul>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
              <h4 className="font-semibold text-purple-800 dark:text-purple-200 mb-2 flex items-center">
                <MessageSquare className="w-5 h-5 mr-2" />
                AI Chatbot Assistant
              </h4>
              <ul className="space-y-1 text-sm text-purple-700 dark:text-purple-300">
                <li>• Natural language processing</li>
                <li>• Customer service automation</li>
                <li>• Multi-session support</li>
                <li>• Performance analytics</li>
              </ul>
            </div>

            <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
              <h4 className="font-semibold text-red-800 dark:text-red-200 mb-2 flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2" />
                Fraud Detection
              </h4>
              <ul className="space-y-1 text-sm text-red-700 dark:text-red-300">
                <li>• AI-powered transaction analysis</li>
                <li>• Real-time risk scoring</li>
                <li>• Automated alert system</li>
                <li>• Compliance monitoring</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Tips */}
      <div className="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 rounded-xl p-6 border border-yellow-200 dark:border-yellow-700">
        <h3 className="text-xl font-semibold text-yellow-800 dark:text-yellow-200 mb-4 flex items-center">
          <Lightbulb className="w-6 h-6 mr-3" />
          Pro Tips
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-yellow-700 dark:text-yellow-300 mb-2">Performance Optimization</h4>
            <ul className="space-y-1 text-sm text-yellow-600 dark:text-yellow-400">
              <li>• Use time range filters for better dashboard performance</li>
              <li>• Enable caching for frequently accessed data</li>
              <li>• Monitor system status regularly</li>
              <li>• Use bulk operations for multiple users</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-yellow-700 dark:text-yellow-300 mb-2">Security Best Practices</h4>
            <ul className="space-y-1 text-sm text-yellow-600 dark:text-yellow-400">
              <li>• Regularly review security alerts</li>
              <li>• Monitor high-risk user accounts</li>
              <li>• Keep compliance checks updated</li>
              <li>• Use strong authentication policies</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTroubleshooting = () => (
    <div className="space-y-6">
      {/* Common Issues */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <AlertTriangle className="w-6 h-6 mr-3 text-red-500" />
          Common Issues & Solutions
        </h3>
        
        <div className="space-y-4">
          <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border border-red-200 dark:border-red-700">
            <h4 className="font-semibold text-red-800 dark:text-red-200 mb-2">Dashboard Not Loading</h4>
            <div className="text-sm text-red-700 dark:text-red-300 space-y-1">
              <p><strong>Symptoms:</strong> Spinner shows indefinitely, data not appearing</p>
              <p><strong>Causes:</strong> Backend service down, network issues, authentication expired</p>
              <p><strong>Solutions:</strong></p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>Check system status in Overview section</li>
                <li>Refresh the page and re-authenticate</li>
                <li>Verify backend service is running</li>
                <li>Check browser console for errors</li>
              </ul>
            </div>
          </div>

          <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 border border-yellow-200 dark:border-yellow-700">
            <h4 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-2">API Endpoints Not Responding</h4>
            <div className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
              <p><strong>Symptoms:</strong> 500/502/503 errors, timeout responses</p>
              <p><strong>Causes:</strong> Service overload, database connectivity, rate limiting</p>
              <p><strong>Solutions:</strong></p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>Check service status in system overview</li>
                <li>Restart backend services if needed</li>
                <li>Verify database connections</li>
                <li>Check rate limiting policies</li>
              </ul>
            </div>
          </div>

          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-700">
            <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">Analytics Data Inconsistency</h4>
            <div className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
              <p><strong>Symptoms:</strong> Conflicting numbers, missing data points</p>
              <p><strong>Causes:</strong> Cache inconsistency, database synchronization</p>
              <p><strong>Solutions:</strong></p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>Clear analytics cache</li>
                <li>Refresh dashboard data</li>
                <li>Check time range settings</li>
                <li>Verify data consolidation process</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Issues */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border">
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <Settings className="w-6 h-6 mr-3 text-gray-500" />
          Performance Troubleshooting
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-3">Slow Dashboard Loading</h4>
            <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <div className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5"></div>
                <span>Reduce time range (use 7 days instead of 90 days)</span>
              </div>
              <div className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5"></div>
                <span>Enable browser caching</span>
              </div>
              <div className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5"></div>
                <span>Check network connectivity</span>
              </div>
              <div className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5"></div>
                <span>Monitor server resource usage</span>
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-3">High Memory Usage</h4>
            <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <div className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5"></div>
                <span>Clear browser cache and cookies</span>
              </div>
              <div className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5"></div>
                <span>Close unused browser tabs</span>
              </div>
              <div className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5"></div>
                <span>Restart browser if necessary</span>
              </div>
              <div className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-1.5"></div>
                <span>Check for memory leaks in console</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Contact Support */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl p-6 border border-blue-200 dark:border-blue-700">
        <h3 className="text-xl font-semibold text-blue-800 dark:text-blue-200 mb-4 flex items-center">
          <ExternalLink className="w-6 h-6 mr-3" />
          Need More Help?
        </h3>
        
        <div className="text-blue-700 dark:text-blue-300">
          <p className="mb-4">If you can't resolve the issue using this guide:</p>
          <div className="space-y-2 text-sm">
            <div>📧 <strong>Email Support:</strong> admin@cataloro.com</div>
            <div>🔧 <strong>Technical Issues:</strong> Check system logs in /var/log/supervisor/</div>
            <div>📚 <strong>Documentation:</strong> This comprehensive guide covers all features</div>
            <div>🚨 <strong>Emergency:</strong> Use troubleshoot_agent for critical issues</div>
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
          <div className="p-2 bg-gradient-to-r from-green-500 to-blue-600 rounded-lg">
            <BookOpen className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Documentation Dashboard
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Comprehensive system guide, API docs & troubleshooting
            </p>
          </div>
        </div>
      </div>

      {/* Section Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {documentationSections.map((section) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`p-4 text-left rounded-lg transition-colors border-2 ${
                activeSection === section.id
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
              }`}
            >
              <div className="flex items-center space-x-3 mb-2">
                <div className={`p-2 rounded-lg ${
                  activeSection === section.id 
                    ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
                    : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                }`}>
                  {section.icon}
                </div>
              </div>
              <div className="text-sm font-medium text-gray-900 dark:text-white">{section.name}</div>
              <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">{section.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Section Content */}
      <div>
        {activeSection === 'overview' && renderSystemOverview()}
        {activeSection === 'api' && renderAPIDocumentation()}
        {activeSection === 'features' && renderFeatureGuide()}
        {activeSection === 'troubleshooting' && renderTroubleshooting()}
      </div>

      {/* Footer */}
      <div className="text-center text-sm text-gray-500 dark:text-gray-400">
        Documentation Dashboard | 
        System Architecture + API Reference + Feature Guides + Troubleshooting | 
        Last updated: {new Date().toLocaleString()}
      </div>
    </div>
  );
};

export default DocumentationDashboard;