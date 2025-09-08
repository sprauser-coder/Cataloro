import React, { useState, useEffect } from 'react';
import { 
  Sparkles,
  Shield,
  Globe,
  Zap,
  Activity,
  TrendingUp,
  Users,
  DollarSign,
  RefreshCw,
  Settings,
  Eye,
  ArrowRight
} from 'lucide-react';
import { useWebSocket } from '../realtime/WebSocketProvider';
import CurrencyConverter from '../currency/CurrencyConverter';
import EscrowDashboard from '../escrow/EscrowDashboard';
import AIRecommendationsWidget from '../ai/AIRecommendationsWidget';

const Phase5Dashboard = ({ currentUser }) => {
  const [activeSection, setActiveSection] = useState('overview');
  const [phase5Status, setPhase5Status] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    websocket: { connections: 0, users: 0 },
    multicurrency: { supported_currencies: 0, base_currency: 'EUR' },
    escrow: { total_escrows: 0, active_escrows: 0 },
    ai: { total_interactions: 0, unique_users: 0 }
  });

  const { isConnected, onlineUsers, notifications } = useWebSocket();

  useEffect(() => {
    fetchPhase5Status();
  }, []);

  const fetchPhase5Status = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/v2/status`);
      
      if (response.ok) {
        const data = await response.json();
        setPhase5Status(data);
        
        // Extract stats from services
        const newStats = {
          websocket: {
            connections: data.services?.websocket?.connections || 0,
            users: data.services?.websocket?.users || 0
          },
          multicurrency: {
            supported_currencies: data.services?.multicurrency?.supported_currencies || 0,
            base_currency: data.services?.multicurrency?.base_currency || 'EUR'
          },
          escrow: {
            total_escrows: data.services?.escrow?.total_escrows || 0,
            active_escrows: data.services?.escrow?.active_escrows || 0
          },
          ai: {
            total_interactions: data.services?.ai_recommendations?.total_interactions || 0,
            unique_users: data.services?.ai_recommendations?.unique_users || 0
          }
        };
        setStats(newStats);
      }
    } catch (error) {
      console.error('Failed to fetch Phase 5 status:', error);
    } finally {
      setLoading(false);
    }
  };

  const getServiceStatusColor = (status) => {
    switch (status) {
      case 'operational':
        return 'text-green-600 bg-green-100 dark:bg-green-900/30 dark:text-green-400';
      case 'partial':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'error':
      case 'not_initialized':
        return 'text-red-600 bg-red-100 dark:bg-red-900/30 dark:text-red-400';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900/30 dark:text-gray-400';
    }
  };

  const sections = [
    {
      id: 'overview',
      label: 'Overview',
      icon: Activity,
      description: 'Phase 5 feature summary'
    },
    {
      id: 'realtime',
      label: 'Real-Time',
      icon: Zap,
      description: 'Live connections and notifications'
    },
    {
      id: 'currency',
      label: 'Multi-Currency',
      icon: Globe,
      description: 'Currency conversion and management'
    },
    {
      id: 'escrow',
      label: 'Escrow',
      icon: Shield,
      description: 'Secure transaction management'
    },
    {
      id: 'ai',
      label: 'AI Recommendations',
      icon: Sparkles,
      description: 'Personalized item suggestions'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading Phase 5 Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-emerald-600 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Phase 5: Advanced Marketplace</h1>
            <p className="text-purple-100">
              Real-time features, multi-currency support, secure escrow, and AI recommendations
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${
              phase5Status?.overall_status === 'operational' 
                ? 'bg-green-100/20 text-green-100' 
                : 'bg-yellow-100/20 text-yellow-100'
            }`}>
              {phase5Status?.overall_status === 'operational' ? 'All Systems Operational' : 'Partial Operations'}
            </div>
            <button
              onClick={fetchPhase5Status}
              className="p-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-600">
        <div className="border-b border-gray-200 dark:border-gray-600">
          <nav className="flex space-x-8 px-6">
            {sections.map((section) => {
              const Icon = section.icon;
              const isActive = activeSection === section.id;
              
              return (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                    isActive
                      ? 'border-purple-500 text-purple-600 dark:text-purple-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{section.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="space-y-6">
        {/* Overview Section */}
        {activeSection === 'overview' && (
          <div className="space-y-6">
            {/* Service Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Real-Time Status */}
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                    <Zap className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">Real-Time</h3>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      getServiceStatusColor(phase5Status?.services?.websocket?.status)
                    }`}>
                      {isConnected ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Online Users</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {onlineUsers.length}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Notifications</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {notifications.length}
                    </span>
                  </div>
                </div>
              </div>

              {/* Multi-Currency Status */}
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                    <Globe className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">Multi-Currency</h3>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      getServiceStatusColor(phase5Status?.services?.multicurrency?.status)
                    }`}>
                      {phase5Status?.services?.multicurrency?.status || 'Unknown'}
                    </span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Currencies</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {stats.multicurrency.supported_currencies}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Base</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {stats.multicurrency.base_currency}
                    </span>
                  </div>
                </div>
              </div>

              {/* Escrow Status */}
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                    <Shield className="w-5 h-5 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">Escrow</h3>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      getServiceStatusColor(phase5Status?.services?.escrow?.status)
                    }`}>
                      {phase5Status?.services?.escrow?.status || 'Unknown'}
                    </span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Total</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {stats.escrow.total_escrows}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Active</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {stats.escrow.active_escrows}
                    </span>
                  </div>
                </div>
              </div>

              {/* AI Recommendations Status */}
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
                    <Sparkles className="w-5 h-5 text-yellow-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">AI Engine</h3>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      getServiceStatusColor(phase5Status?.services?.ai_recommendations?.status)
                    }`}>
                      {phase5Status?.services?.ai_recommendations?.status || 'Unknown'}
                    </span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Interactions</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {stats.ai.total_interactions}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Users</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {stats.ai.unique_users}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Feature Highlights */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Phase 5 Features Overview
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {sections.slice(1).map((section) => {
                  const Icon = section.icon;
                  return (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className="flex items-center space-x-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-left group"
                    >
                      <div className="p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                        <Icon className="w-6 h-6 text-purple-600" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400">
                          {section.label}
                        </h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {section.description}
                        </p>
                      </div>
                      <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-purple-600 dark:group-hover:text-purple-400" />
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Real-Time Section */}
        {activeSection === 'realtime' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Real-Time Features
              </h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Connection Status */}
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900 dark:text-white">Connection Status</h4>
                  <div className="flex items-center space-x-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {isConnected ? 'Connected to real-time services' : 'Disconnected'}
                    </span>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Online Users</span>
                      <span className="font-medium text-gray-900 dark:text-white">{onlineUsers.length}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Unread Notifications</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {notifications.filter(n => !n.read).length}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Recent Notifications */}
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900 dark:text-white">Recent Notifications</h4>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {notifications.slice(0, 5).map((notification, index) => (
                      <div key={index} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {notification.title}
                            </div>
                            <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                              {notification.message}
                            </div>
                          </div>
                          {!notification.read && (
                            <div className="w-2 h-2 bg-blue-500 rounded-full ml-2 mt-1"></div>
                          )}
                        </div>
                      </div>
                    ))}
                    {notifications.length === 0 && (
                      <div className="text-center py-4 text-gray-500 dark:text-gray-400">
                        No notifications yet
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Currency Section */}
        {activeSection === 'currency' && (
          <div className="space-y-6">
            <CurrencyConverter />
          </div>
        )}

        {/* Escrow Section */}
        {activeSection === 'escrow' && currentUser && (
          <div className="space-y-6">
            <EscrowDashboard userId={currentUser.id} />
          </div>
        )}

        {/* AI Section */}
        {activeSection === 'ai' && currentUser && (
          <div className="space-y-6">
            <AIRecommendationsWidget 
              userId={currentUser.id}
              limit={8}
              showTrending={true}
              showPersonalized={true}
              onItemClick={(listing) => {
                // Navigate to listing detail page
                window.location.href = `/product/${listing.id}`;
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default Phase5Dashboard;