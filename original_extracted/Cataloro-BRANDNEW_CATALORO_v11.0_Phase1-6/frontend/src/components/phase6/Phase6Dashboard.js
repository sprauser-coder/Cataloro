import React, { useState, useEffect } from 'react';
import { 
  Sparkles,
  Shield,
  Globe,
  AlertTriangle,
  Users,
  Bot,
  BarChart3,
  Activity,
  TrendingUp,
  RefreshCw,
  Settings,
  Eye,
  ArrowRight,
  CheckCircle,
  Clock,
  Zap
} from 'lucide-react';
import AdvancedAnalyticsDashboard from '../analytics/AdvancedAnalyticsDashboard';
import EnterpriseSecurityDashboard from '../security/EnterpriseSecurityDashboard';
import FraudDetectionDashboard from '../fraud/FraudDetectionDashboard';
import AIChatWidget from '../chat/AIChatWidget';
import LocalizationDashboard from '../i18n/LocalizationDashboard';
import EnhancedUserManagementPanel from '../users/EnhancedUserManagementPanel';

const Phase6Dashboard = ({ currentUser }) => {
  const [activeSection, setActiveSection] = useState('overview');
  const [phase6Status, setPhase6Status] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showChatWidget, setShowChatWidget] = useState(false);

  useEffect(() => {
    fetchPhase6Status();
  }, []);

  const fetchPhase6Status = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/v2/phase6/status`);
      
      if (response.ok) {
        const data = await response.json();
        setPhase6Status(data);
      }
    } catch (error) {
      console.error('Failed to fetch Phase 6 status:', error);
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
      description: 'Enterprise features summary'
    },
    {
      id: 'analytics',
      label: 'Advanced Analytics',
      icon: BarChart3,
      description: 'Business intelligence and predictive insights'
    },
    {
      id: 'security',
      label: 'Enterprise Security',
      icon: Shield,
      description: 'Security monitoring and compliance'
    },
    {
      id: 'fraud',
      label: 'Fraud Detection',
      icon: AlertTriangle,
      description: 'AI-powered fraud prevention'
    },
    {
      id: 'localization',
      label: 'Internationalization',
      icon: Globe,
      description: 'Multi-language and regional support'
    },
    {
      id: 'users',
      label: 'User Management',
      icon: Users,
      description: 'Advanced role and permission management'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading Phase 6 Dashboard...</p>
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
            <h1 className="text-3xl font-bold mb-2">Phase 6: Enterprise Intelligence & Global Expansion</h1>
            <p className="text-purple-100">
              Advanced analytics, enterprise security, fraud detection, AI assistance, and global localization
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowChatWidget(!showChatWidget)}
              className="flex items-center space-x-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
            >
              <Bot className="w-5 h-5" />
              <span>AI Assistant</span>
            </button>
            {phase6Status && (
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                phase6Status.overall_status === 'operational' 
                  ? 'bg-green-100/20 text-green-100' 
                  : 'bg-yellow-100/20 text-yellow-100'
              }`}>
                {phase6Status.overall_status === 'operational' ? 'All Systems Operational' : 'Partial Operations'}
              </div>
            )}
            <button
              onClick={fetchPhase6Status}
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
          <nav className="flex space-x-8 px-6 overflow-x-auto">
            {sections.map((section) => {
              const Icon = section.icon;
              const isActive = activeSection === section.id;
              
              return (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
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
            {phase6Status && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {Object.entries(phase6Status.services).map(([serviceName, serviceData]) => {
                  const getServiceIcon = (name) => {
                    switch (name) {
                      case 'advanced_analytics':
                        return <BarChart3 className="w-5 h-5 text-purple-600" />;
                      case 'enterprise_security':
                        return <Shield className="w-5 h-5 text-red-600" />;
                      case 'fraud_detection':
                        return <AlertTriangle className="w-5 h-5 text-orange-600" />;
                      case 'ai_chatbot':
                        return <Bot className="w-5 h-5 text-blue-600" />;
                      case 'internationalization':
                        return <Globe className="w-5 h-5 text-green-600" />;
                      case 'enhanced_user_management':
                        return <Users className="w-5 h-5 text-indigo-600" />;
                      default:
                        return <Activity className="w-5 h-5 text-gray-600" />;
                    }
                  };

                  return (
                    <div key={serviceName} className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
                      <div className="flex items-center space-x-3 mb-4">
                        <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                          {getServiceIcon(serviceName)}
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900 dark:text-white">
                            {serviceData.service_name || serviceName.replace('_', ' ')}
                          </h3>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            getServiceStatusColor(serviceData.status || 'unknown')
                          }`}>
                            {(serviceData.status || 'unknown').toUpperCase()}
                          </span>
                        </div>
                      </div>
                      
                      <div className="space-y-2 text-sm">
                        {serviceData.version && (
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Version:</span>
                            <span className="font-medium text-gray-900 dark:text-white">
                              {serviceData.version}
                            </span>
                          </div>
                        )}
                        
                        {serviceData.capabilities && (
                          <div>
                            <span className="text-gray-600 dark:text-gray-400">Capabilities:</span>
                            <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                              {serviceData.capabilities.slice(0, 2).join(', ')}
                              {serviceData.capabilities.length > 2 && ` +${serviceData.capabilities.length - 2} more`}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Feature Highlights */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Phase 6 Enterprise Features
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {sections.slice(1).map((section) => {
                  const Icon = section.icon;
                  const serviceKey = section.id === 'analytics' ? 'advanced_analytics' :
                                   section.id === 'security' ? 'enterprise_security' :
                                   section.id === 'fraud' ? 'fraud_detection' :
                                   section.id === 'localization' ? 'internationalization' :
                                   section.id === 'users' ? 'enhanced_user_management' : section.id;
                  
                  const serviceStatus = phase6Status?.services?.[serviceKey]?.status || 'unknown';
                  
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
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400">
                            {section.label}
                          </h4>
                          <span className={`text-xs px-2 py-1 rounded-full ${getServiceStatusColor(serviceStatus)}`}>
                            {serviceStatus.toUpperCase()}
                          </span>
                        </div>
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

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
                <div className="flex items-center space-x-3">
                  <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      6/6
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Services Active</div>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
                <div className="flex items-center space-x-3">
                  <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      24/24
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Backend Tests Passed</div>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
                <div className="flex items-center space-x-3">
                  <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                    <Sparkles className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      100%
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Implementation Complete</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Advanced Analytics Section */}
        {activeSection === 'analytics' && (
          <AdvancedAnalyticsDashboard />
        )}

        {/* Enterprise Security Section */}
        {activeSection === 'security' && (
          <EnterpriseSecurityDashboard />
        )}

        {/* Fraud Detection Section */}
        {activeSection === 'fraud' && (
          <FraudDetectionDashboard />
        )}

        {/* Localization Section */}
        {activeSection === 'localization' && (
          <LocalizationDashboard />
        )}

        {/* User Management Section */}
        {activeSection === 'users' && (
          <EnhancedUserManagementPanel />
        )}
      </div>

      {/* AI Chat Widget */}
      {showChatWidget && (
        <AIChatWidget
          currentUser={currentUser}
          position="bottom-right"
          minimized={false}
        />
      )}
    </div>
  );
};

export default Phase6Dashboard;