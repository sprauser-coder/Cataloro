import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Package, 
  DollarSign, 
  TrendingUp, 
  Settings, 
  BarChart3,
  Shield,
  Bell,
  Globe,
  RefreshCw,
  Save,
  X,
  Trash2,
  Edit,
  Plus,
  Store,
  Palette,
  Mail,
  Database,
  Layout,
  FileText,
  Award,
  Target,
  Search
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

// Import all admin components
import ContentManagementSystem from './ContentManagementSystem';
import SystemNotificationsManager from './SystemNotificationsManager';
import BusinessTab from './BusinessTab';

function AdminPanel() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState(null);
  const [users, setUsers] = useState([]);
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);
  
  // User creation state
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [newUserData, setNewUserData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: 'user'
  });
  const [creatingUser, setCreatingUser] = useState(false);
  
  const { user } = useAuth();
  const { showToast } = useNotifications();

  // Admin check
  const isUserAdmin = user && (user.role === 'admin' || user.email === 'admin@cataloro.com');
  
  if (!isUserAdmin) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Access Denied</h2>
          <p className="text-gray-600 dark:text-gray-400">You need admin privileges to access this panel.</p>
        </div>
      </div>
    );
  }

  useEffect(() => {
    if (activeTab === 'dashboard') {
      fetchRealDashboardData();
    } else if (activeTab === 'users') {
      fetchUsers();
    } else if (activeTab === 'settings') {
      fetchSettings();
    }
  }, [activeTab]);

  const fetchRealDashboardData = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/dashboard`);
      
      if (response.ok) {
        const data = await response.json();
        setDashboardData({
          kpis: data?.kpis || {
            total_users: 0,
            total_listings: 0,
            active_listings: 0,
            total_deals: 0,
            revenue: 0.0,
            growth_rate: 0.0
          },
          recent_activity: data?.recent_activity || []
        });
      }
    } catch (error) {
      console.error('Dashboard error:', error);
      showToast('Failed to load dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/users`);
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      }
    } catch (error) {
      console.error('Users fetch error:', error);
    }
  };

  const fetchSettings = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/settings`);
      if (response.ok) {
        const data = await response.json();
        setSettings(data);
      }
    } catch (error) {
      console.error('Settings fetch error:', error);
    }
  };

  const createUser = async () => {
    try {
      setCreatingUser(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUserData)
      });

      if (response.ok) {
        showToast('User created successfully!', 'success');
        setShowCreateUser(false);
        setNewUserData({ username: '', email: '', password: '', full_name: '', role: 'user' });
        fetchUsers();
      } else {
        const error = await response.json();
        showToast(error.detail || 'Failed to create user', 'error');
      }
    } catch (error) {
      showToast('Failed to create user', 'error');
    } finally {
      setCreatingUser(false);
    }
  };

  const deleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/users/${userId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        showToast('User deleted successfully!', 'success');
        fetchUsers();
      } else {
        const error = await response.json();
        showToast(error.detail || 'Failed to delete user', 'error');
      }
    } catch (error) {
      showToast('Failed to delete user', 'error');
    }
  };

  const updateSettings = async (newSettings) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSettings)
      });

      if (response.ok) {
        showToast('Settings updated successfully!', 'success');
        setSettings(newSettings);
      } else {
        showToast('Failed to update settings', 'error');
      }
    } catch (error) {
      showToast('Failed to update settings', 'error');
    }
  };

  // Complete tab definitions with all original functionality
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3, description: 'Overview and KPIs' },
    { id: 'users', label: 'User Management', icon: Users, description: 'Manage users and roles' },
    { id: 'content', label: 'Content Management', icon: FileText, description: 'CMS and content editing' },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp, description: 'Performance metrics' },
    { id: 'notifications', label: 'System Notifications', icon: Bell, description: 'Notification management' },
    { id: 'business', label: 'Business Process Map', icon: Store, description: 'Process visualization' },
    { id: 'settings', label: 'Site Administration', icon: Settings, description: 'System settings' },
    { id: 'security', label: 'Security', icon: Shield, description: 'Security and permissions' }
  ];

  const { kpis, recent_activity } = dashboardData || {};

  if (loading && activeTab === 'dashboard') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <RefreshCw className="w-8 h-8 animate-spin text-purple-600" />
        <span className="ml-3 text-gray-600 dark:text-gray-400">Loading dashboard...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="flex">
        {/* Enhanced Sidebar with all tabs */}
        <div className="w-72 bg-white dark:bg-gray-800 shadow-xl border-r border-gray-200 dark:border-gray-700">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">Admin Panel</h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">Complete Management Suite</p>
              </div>
            </div>
          </div>
          
          <nav className="mt-6 px-3">
            <div className="space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center px-4 py-3 text-left text-sm font-medium rounded-lg transition-all duration-200 group ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-lg transform scale-105'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  <tab.icon className={`w-5 h-5 mr-3 ${activeTab === tab.id ? 'text-white' : 'text-gray-500'}`} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span>{tab.label}</span>
                      {activeTab === tab.id && <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>}
                    </div>
                    <div className={`text-xs mt-1 ${activeTab === tab.id ? 'text-purple-100' : 'text-gray-500'}`}>
                      {tab.description}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </nav>

          {/* Admin User Info */}
          <div className="absolute bottom-6 left-6 right-6">
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-sm">
                    {user?.username?.charAt(0).toUpperCase() || 'A'}
                  </span>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {user?.username || 'Admin'}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">Administrator</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 overflow-hidden">
          <div className="h-full overflow-y-auto">
            <div className="p-8">
              {/* Dashboard Tab */}
              {activeTab === 'dashboard' && (
                <div className="space-y-8">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard Overview</h2>
                      <p className="text-gray-600 dark:text-gray-400 mt-1">Real-time marketplace metrics and insights</p>
                    </div>
                    <button
                      onClick={fetchRealDashboardData}
                      className="flex items-center space-x-2 px-4 py-2 bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 rounded-lg hover:bg-purple-200 dark:hover:bg-purple-900/40 transition-colors"
                    >
                      <RefreshCw className="w-4 h-4" />
                      <span>Refresh Data</span>
                    </button>
                  </div>

                  {/* Enhanced KPI Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-purple-100 text-sm font-medium">Total Users</p>
                          <p className="text-3xl font-bold mt-1">{kpis?.total_users || 0}</p>
                          <p className="text-purple-200 text-xs mt-2">↗ Real database count</p>
                        </div>
                        <Users className="w-12 h-12 text-purple-200" />
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-blue-100 text-sm font-medium">Total Listings</p>
                          <p className="text-3xl font-bold mt-1">{kpis?.total_listings || 0}</p>
                          <p className="text-blue-200 text-xs mt-2">↗ Active marketplace items</p>
                        </div>
                        <Package className="w-12 h-12 text-blue-200" />
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-green-100 text-sm font-medium">Revenue</p>
                          <p className="text-3xl font-bold mt-1">€{kpis?.revenue?.toFixed(2) || '0.00'}</p>
                          <p className="text-green-200 text-xs mt-2">↗ From completed deals</p>
                        </div>
                        <DollarSign className="w-12 h-12 text-green-200" />
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl shadow-lg p-6 text-white">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-orange-100 text-sm font-medium">Growth Rate</p>
                          <p className="text-3xl font-bold mt-1">{kpis?.growth_rate?.toFixed(1) || '0.0'}%</p>
                          <p className="text-orange-200 text-xs mt-2">↗ Monthly growth</p>
                        </div>
                        <TrendingUp className="w-12 h-12 text-orange-200" />
                      </div>
                    </div>
                  </div>

                  {/* Recent Activity */}
                  {recent_activity && recent_activity.length > 0 && (
                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg">
                      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                          <BarChart3 className="w-5 h-5 mr-2 text-purple-600" />
                          Recent Activity
                        </h3>
                      </div>
                      <div className="p-6">
                        <div className="space-y-4">
                          {recent_activity.map((activity, index) => (
                            <div key={index} className="flex items-center space-x-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                              <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
                              <div className="flex-1">
                                <span className="text-gray-900 dark:text-gray-100 font-medium">{activity.action}</span>
                                <span className="text-gray-500 dark:text-gray-400 text-sm ml-2">
                                  {new Date(activity.timestamp).toLocaleString()}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* User Management Tab */}
              {activeTab === 'users' && (
                <div className="space-y-8">
                  <div className="flex justify-between items-center">
                    <div>
                      <h2 className="text-3xl font-bold text-gray-900 dark:text-white">User Management</h2>
                      <p className="text-gray-600 dark:text-gray-400 mt-1">Manage users, roles, and permissions</p>
                    </div>
                    <button
                      onClick={() => setShowCreateUser(true)}
                      className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg font-medium shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
                    >
                      <Plus className="w-5 h-5" />
                      <span>Create New User</span>
                    </button>
                  </div>

                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead className="bg-gray-50 dark:bg-gray-700">
                          <tr>
                            <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">User</th>
                            <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Role</th>
                            <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
                            <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Joined</th>
                            <th className="px-6 py-4 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                          {users.map((user) => (
                            <tr key={user.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="flex items-center">
                                  <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                                    <span className="text-white font-bold text-sm">
                                      {user.username?.charAt(0).toUpperCase() || 'U'}
                                    </span>
                                  </div>
                                  <div className="ml-4">
                                    <div className="text-sm font-medium text-gray-900 dark:text-white">{user.username}</div>
                                    <div className="text-sm text-gray-500 dark:text-gray-400">{user.email}</div>
                                  </div>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${
                                  user.role === 'admin' 
                                    ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300' 
                                    : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                                }`}>
                                  {user.role}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className="inline-flex px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">
                                  Active
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                <button
                                  onClick={() => deleteUser(user.id)}
                                  className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* Content Management Tab */}
              {activeTab === 'content' && (
                <div>
                  <ContentManagementSystem />
                </div>
              )}

              {/* System Notifications Tab */}
              {activeTab === 'notifications' && (
                <div>
                  <SystemNotificationsManager />
                </div>
              )}

              {/* Business Process Map Tab */}
              {activeTab === 'business' && (
                <div>
                  <BusinessTab showToast={showToast} />
                </div>
              )}

              {/* Site Administration Tab */}
              {activeTab === 'settings' && (
                <div className="space-y-8">
                  <div>
                    <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Site Administration</h2>
                    <p className="text-gray-600 dark:text-gray-400 mt-1">Configure site settings and appearance</p>
                  </div>

                  {/* Hero Display Configuration */}
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg">
                    <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                        <Layout className="w-5 h-5 mr-2 text-purple-600" />
                        Hero Display Configuration
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                        Customize how the hero section appears on your site
                      </p>
                    </div>
                    <div className="p-6 space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Display Mode
                          </label>
                          <select
                            value={settings.hero_display_mode || 'full_width'}
                            onChange={(e) => updateSettings({...settings, hero_display_mode: e.target.value})}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          >
                            <option value="full_width">Full Width</option>
                            <option value="boxed">Boxed</option>
                            <option value="centered">Centered</option>
                          </select>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Background Style
                          </label>
                          <select
                            value={settings.hero_background_style || 'gradient'}
                            onChange={(e) => updateSettings({...settings, hero_background_style: e.target.value})}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          >
                            <option value="gradient">Gradient</option>
                            <option value="image">Image</option>
                            <option value="solid">Solid</option>
                          </select>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Text Alignment
                          </label>
                          <select
                            value={settings.hero_text_alignment || 'center'}
                            onChange={(e) => updateSettings({...settings, hero_text_alignment: e.target.value})}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          >
                            <option value="left">Left</option>
                            <option value="center">Center</option>
                            <option value="right">Right</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Placeholder for other tabs */}
              {['analytics', 'security'].includes(activeTab) && (
                <div className="text-center py-16">
                  <div className="max-w-md mx-auto">
                    <div className="w-24 h-24 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6">
                      {activeTab === 'analytics' ? (
                        <TrendingUp className="w-12 h-12 text-white" />
                      ) : (
                        <Shield className="w-12 h-12 text-white" />
                      )}
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                      {tabs.find(t => t.id === activeTab)?.label}
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">
                      {tabs.find(t => t.id === activeTab)?.description}
                    </p>
                    <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                      <p className="text-blue-800 dark:text-blue-300 text-sm">
                        This section is under development and will be available in a future update.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Create User Modal */}
      {showCreateUser && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
                  <Plus className="w-5 h-5 mr-2 text-purple-600" />
                  Create New User
                </h3>
                <button 
                  onClick={() => setShowCreateUser(false)} 
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            <form onSubmit={(e) => { e.preventDefault(); createUser(); }} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Username*</label>
                <input
                  type="text"
                  required
                  value={newUserData.username}
                  onChange={(e) => setNewUserData({...newUserData, username: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Enter username"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Email*</label>
                <input
                  type="email"
                  required
                  value={newUserData.email}
                  onChange={(e) => setNewUserData({...newUserData, email: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Enter email address"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Password*</label>
                <input
                  type="password"
                  required
                  value={newUserData.password}
                  onChange={(e) => setNewUserData({...newUserData, password: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Enter password"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Full Name</label>
                <input
                  type="text"
                  value={newUserData.full_name}
                  onChange={(e) => setNewUserData({...newUserData, full_name: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Enter full name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Role*</label>
                <select
                  value={newUserData.role}
                  onChange={(e) => setNewUserData({...newUserData, role: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-700">
                <button
                  type="button"
                  onClick={() => setShowCreateUser(false)}
                  className="px-6 py-2 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creatingUser}
                  className="px-6 py-2 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg hover:from-purple-600 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2"
                >
                  {creatingUser ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Creating...</span>
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      <span>Create User</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminPanel;