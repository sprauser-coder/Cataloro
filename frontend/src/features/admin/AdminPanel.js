/**
 * CATALORO - Admin Panel
 * Properly restored with clean structure and all requested functionalities
 */

import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Package, 
  DollarSign, 
  TrendingUp, 
  Settings, 
  Edit,
  Trash2,
  BarChart3,
  Activity,
  Save,
  X,
  RefreshCw,
  Shield,
  Layout,
  Database,
  Bell,
  FileText,
  Plus
} from 'lucide-react';

// Import specialized admin components
import ContentManagementSystem from './ContentManagementSystem';
import SystemNotificationsManager from './SystemNotificationsManager';
import BusinessTab from './BusinessTab';

import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function AdminPanel() {
  // Complete state management
  const [activeTab, setActiveTab] = useState('dashboard');
  const [activeSubTab, setActiveSubTab] = useState('overview');
  const [dashboardData, setDashboardData] = useState(null);
  const [users, setUsers] = useState([]);
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);
  const [logoFile, setLogoFile] = useState(null);
  const [logoPreview, setLogoPreview] = useState('');
  
  // User management states
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [newUserData, setNewUserData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: 'user'
  });
  const [creatingUser, setCreatingUser] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  // Price settings states
  const [priceSettings, setPriceSettings] = useState({
    pt_price: 25.0,
    pd_price: 18.0,
    rh_price: 45.0,
    renumeration_pt: 0.95,
    renumeration_pd: 0.92,
    renumeration_rh: 0.88,
    price_range_min_percent: 10.0,
    price_range_max_percent: 10.0
  });

  // Analytics states
  const [analyticsData, setAnalyticsData] = useState(null);
  const [selectedDateRange, setSelectedDateRange] = useState('7d');
  
  // Tools states
  const [selectedTool, setSelectedTool] = useState('database');
  const [toolsData, setToolsData] = useState({});

  const { user } = useAuth();
  const { showToast } = useNotifications();

  // Admin access control
  const isAdmin = () => {
    return user && (user.role === 'admin' || user.email === 'admin@cataloro.com');
  };

  if (!isAdmin()) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="text-center p-8">
          <Shield className="w-24 h-24 text-red-500 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Access Denied</h2>
          <p className="text-gray-600 dark:text-gray-400">You need administrator privileges to access this panel.</p>
        </div>
      </div>
    );
  }

  // Data fetching effects
  useEffect(() => {
    if (activeTab === 'dashboard') {
      fetchRealDashboardData();
    } else if (activeTab === 'users') {
      fetchUsers();
    } else if (activeSubTab === 'settings' || activeTab === 'administration') {
      fetchSettings();
    } else if (activeSubTab === 'basis' || activeTab === 'administration') {
      fetchPriceSettings();
    } else if (activeTab === 'analytics') {
      fetchAnalyticsData();
    }
  }, [activeTab, activeSubTab]);

  // Complete data fetching functions
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

  const fetchPriceSettings = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/catalyst-price-settings`);
      if (response.ok) {
        const data = await response.json();
        setPriceSettings(data);
      }
    } catch (error) {
      console.error('Price settings fetch error:', error);
    }
  };

  const fetchAnalyticsData = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/analytics?range=${selectedDateRange}`);
      if (response.ok) {
        const data = await response.json();
        setAnalyticsData(data);
      }
    } catch (error) {
      console.error('Analytics fetch error:', error);
    }
  };

  // Complete management functions
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

  const updatePriceSettings = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/admin/catalyst-price-settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(priceSettings)
      });

      if (response.ok) {
        showToast('Price settings updated successfully!', 'success');
      } else {
        showToast('Failed to update price settings', 'error');
      }
    } catch (error) {
      showToast('Failed to update price settings', 'error');
    }
  };

  // Main tab definitions - COMPLETE LIST
  const mainTabs = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'users', label: 'User Management', icon: Users },
    { id: 'content', label: 'Content Management', icon: FileText },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp },
    { id: 'notifications', label: 'System Notifications', icon: Bell },
    { id: 'business', label: 'Business Process Map', icon: Store },
    { id: 'administration', label: 'Site Administration', icon: Settings },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'tools', label: 'Developer Tools', icon: Code }
  ];

  // Sub-tab definitions
  const getSubTabs = () => {
    switch (activeTab) {
      case 'administration':
        return [
          { id: 'settings', label: 'General Settings', icon: Settings },
          { id: 'basis', label: 'Cat Database & Basis', icon: Database },
          { id: 'hero', label: 'Hero Selection', icon: Layout },
          { id: 'appearance', label: 'Appearance', icon: Palette },
          { id: 'email', label: 'Email Settings', icon: Mail }
        ];
      case 'analytics':
        return [
          { id: 'overview', label: 'Overview', icon: BarChart3 },
          { id: 'users', label: 'User Analytics', icon: Users },
          { id: 'sales', label: 'Sales Analytics', icon: DollarSign },
          { id: 'performance', label: 'Performance', icon: TrendingUp }
        ];
      case 'tools':
        return [
          { id: 'database', label: 'Database Tools', icon: Database },
          { id: 'logs', label: 'System Logs', icon: FileText },
          { id: 'backup', label: 'Backup & Restore', icon: Archive },
          { id: 'maintenance', label: 'Maintenance', icon: Settings }
        ];
      case 'security':
        return [
          { id: 'permissions', label: 'Permissions', icon: Shield },
          { id: 'audit', label: 'Audit Logs', icon: Search },
          { id: 'firewall', label: 'Firewall', icon: Lock },
          { id: 'monitoring', label: 'Monitoring', icon: Eye }
        ];
      default:
        return [];
    }
  };

  const subTabs = getSubTabs();
  const { kpis, recent_activity } = dashboardData || {};

  if (loading && activeTab === 'dashboard') {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* COMPLETE HEADER */}
      <div className="bg-white dark:bg-gray-800 shadow-lg border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-full">
          {/* Top Header */}
          <div className="px-8 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl">
                  <Shield className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Cataloro Admin Panel</h1>
                  <p className="text-gray-600 dark:text-gray-400">Complete marketplace management system</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Welcome, <span className="font-semibold">{user?.username || 'Administrator'}</span>
                </div>
                <button
                  onClick={fetchRealDashboardData}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Refresh</span>
                </button>
              </div>
            </div>
          </div>

          {/* MAIN TAB NAVIGATION */}
          <div className="px-8">
            <div className="border-b border-gray-200 dark:border-gray-700">
              <nav className="flex space-x-8">
                {mainTabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => {
                      setActiveTab(tab.id);
                      setActiveSubTab(getSubTabs()[0]?.id || 'overview');
                    }}
                    className={`flex items-center space-x-2 px-1 py-4 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                        : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:border-gray-300'
                    }`}
                  >
                    <tab.icon className="w-5 h-5" />
                    <span>{tab.label}</span>
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* SUB-TAB NAVIGATION */}
          {subTabs.length > 0 && (
            <div className="px-8 py-4 bg-gray-50 dark:bg-gray-700/50">
              <nav className="flex space-x-6">
                {subTabs.map((subTab) => (
                  <button
                    key={subTab.id}
                    onClick={() => setActiveSubTab(subTab.id)}
                    className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      activeSubTab === subTab.id
                        ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                        : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800'
                    }`}
                  >
                    <subTab.icon className="w-4 h-4" />
                    <span>{subTab.label}</span>
                  </button>
                ))}
              </nav>
            </div>
          )}
        </div>
      </div>

      {/* MAIN CONTENT AREA */}
      <div className="max-w-full px-8 py-8">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Dashboard Overview</h2>
              <p className="text-gray-600 dark:text-gray-400">Real-time marketplace metrics and key performance indicators</p>
            </div>

            {/* KPI Cards with REAL data */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center">
                  <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                    <Users className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Total Users</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">
                      {kpis?.total_users || 0}
                    </p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">Real database count</p>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center">
                  <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
                    <Package className="w-8 h-8 text-green-600 dark:text-green-400" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Total Listings</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">
                      {kpis?.total_listings || 0}
                    </p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">Active marketplace</p>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center">
                  <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                    <DollarSign className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Revenue</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">
                      €{kpis?.revenue?.toFixed(2) || '0.00'}
                    </p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">From completed deals</p>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center">
                  <div className="p-3 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
                    <TrendingUp className="w-8 h-8 text-orange-600 dark:text-orange-400" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">Growth Rate</p>
                    <p className="text-3xl font-bold text-gray-900 dark:text-white">
                      {kpis?.growth_rate?.toFixed(1) || '0.0'}%
                    </p>
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1">Monthly growth</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            {recent_activity && recent_activity.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                    <Activity className="w-5 h-5 mr-2 text-blue-600" />
                    Recent Activity
                  </h3>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    {recent_activity.map((activity, index) => (
                      <div key={index} className="flex items-center space-x-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                        <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
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
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">User Management</h2>
                <p className="text-gray-600 dark:text-gray-400">Manage users, roles, and permissions</p>
              </div>
              <button
                onClick={() => setShowCreateUser(true)}
                className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
              >
                <Plus className="w-5 h-5" />
                <span>Create New User</span>
              </button>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
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
                            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
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
                          <div className="flex items-center justify-end space-x-2">
                            <button
                              onClick={() => setEditingUser(user)}
                              className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 p-2 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => deleteUser(user.id)}
                              className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
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

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-8">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics & Reports</h2>
                <p className="text-gray-600 dark:text-gray-400">Comprehensive marketplace analytics and insights</p>
              </div>
              <div className="flex items-center space-x-4">
                <select
                  value={selectedDateRange}
                  onChange={(e) => setSelectedDateRange(e.target.value)}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="7d">Last 7 days</option>
                  <option value="30d">Last 30 days</option>
                  <option value="90d">Last 3 months</option>
                  <option value="1y">Last year</option>
                </select>
                <button
                  onClick={fetchAnalyticsData}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Refresh</span>
                </button>
              </div>
            </div>

            {/* Analytics Sub-tabs Content */}
            {activeSubTab === 'overview' && (
              <div className="text-center py-16">
                <BarChart3 className="w-24 h-24 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Analytics Overview</h3>
                <p className="text-gray-600 dark:text-gray-400">Comprehensive analytics dashboard coming soon</p>
              </div>
            )}
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
        {activeTab === 'administration' && (
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Site Administration</h2>
              <p className="text-gray-600 dark:text-gray-400">Configure site settings, pricing, and appearance</p>
            </div>

            {/* Cat Database & Basis */}
            {activeSubTab === 'basis' && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                    <Database className="w-5 h-5 mr-2 text-blue-600" />
                    Cat Database & Basis
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                    Manage catalyst database and pricing basis settings
                  </p>
                </div>
                <div className="p-6 space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">PT Price</label>
                      <input
                        type="number"
                        step="0.1"
                        value={priceSettings.pt_price}
                        onChange={(e) => setPriceSettings({...priceSettings, pt_price: parseFloat(e.target.value) || 0})}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">PD Price</label>
                      <input
                        type="number"
                        step="0.1"
                        value={priceSettings.pd_price}
                        onChange={(e) => setPriceSettings({...priceSettings, pd_price: parseFloat(e.target.value) || 0})}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">RH Price</label>
                      <input
                        type="number"
                        step="0.1"
                        value={priceSettings.rh_price}
                        onChange={(e) => setPriceSettings({...priceSettings, rh_price: parseFloat(e.target.value) || 0})}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                  </div>

                  {/* Price Range Settings Section */}
                  <div className="mt-8">
                    <div className="mb-4">
                      <h4 className="text-md font-semibold text-gray-900 dark:text-white">Price Range Configuration</h4>
                      <p className="text-gray-600 dark:text-gray-400 text-sm">
                        Configure the dynamic price range percentages for catalog listings.
                      </p>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Minimum Price Reduction (%)
                        </label>
                        <div className="relative">
                          <input
                            type="number"
                            step="0.1"
                            min="0"
                            max="50"
                            value={priceSettings.price_range_min_percent}
                            onChange={(e) => setPriceSettings({...priceSettings, price_range_min_percent: parseFloat(e.target.value) || 0})}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white pr-8"
                          />
                          <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400 text-sm">%</span>
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          Currently: -{priceSettings.price_range_min_percent}% from base price
                        </p>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                          Maximum Price Increase (%)
                        </label>
                        <div className="relative">
                          <input
                            type="number"
                            step="0.1"
                            min="0"
                            max="100"
                            value={priceSettings.price_range_max_percent}
                            onChange={(e) => setPriceSettings({...priceSettings, price_range_max_percent: parseFloat(e.target.value) || 0})}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white pr-8"
                          />
                          <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 dark:text-gray-400 text-sm">%</span>
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          Currently: +{priceSettings.price_range_max_percent}% from base price
                        </p>
                      </div>
                    </div>
                    
                    {/* Price Range Preview */}
                    <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <div className="text-sm text-blue-800 dark:text-blue-300">
                        <strong>Preview:</strong> For a €100.00 base price, the range will be €{(100 * (100 - priceSettings.price_range_min_percent) / 100).toFixed(2)} - €{(100 * (100 + priceSettings.price_range_max_percent) / 100).toFixed(2)}
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <button
                      onClick={updatePriceSettings}
                      className="flex items-center space-x-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
                    >
                      <Save className="w-4 h-4" />
                      <span>Save Price Settings</span>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Hero Selection */}
            {activeSubTab === 'hero' && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                    <Layout className="w-5 h-5 mr-2 text-purple-600" />
                    Hero Selection & Display Options
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
                    Configure hero section display and layout options
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
            )}

            {/* General Settings */}
            {activeSubTab === 'settings' && (
              <div className="text-center py-16">
                <Settings className="w-24 h-24 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">General Settings</h3>
                <p className="text-gray-600 dark:text-gray-400">Site configuration options coming soon</p>
              </div>
            )}
          </div>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Security & Permissions</h2>
              <p className="text-gray-600 dark:text-gray-400">Manage security settings and user permissions</p>
            </div>

            <div className="text-center py-16">
              <Shield className="w-24 h-24 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Security Dashboard</h3>
              <p className="text-gray-600 dark:text-gray-400">Advanced security features coming soon</p>
            </div>
          </div>
        )}

        {/* Developer Tools Tab */}
        {activeTab === 'tools' && (
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Developer Tools</h2>
              <p className="text-gray-600 dark:text-gray-400">System maintenance and developer utilities</p>
            </div>

            <div className="text-center py-16">
              <Code className="w-24 h-24 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Developer Tools</h3>
              <p className="text-gray-600 dark:text-gray-400">System tools and utilities coming soon</p>
            </div>
          </div>
        )}
      </div>

      {/* Create User Modal */}
      {showCreateUser && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full border border-gray-200 dark:border-gray-700">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
                  <Plus className="w-5 h-5 mr-2 text-blue-600" />
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
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter password"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Full Name</label>
                <input
                  type="text"
                  value={newUserData.full_name}
                  onChange={(e) => setNewUserData({...newUserData, full_name: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter full name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Role*</label>
                <select
                  value={newUserData.role}
                  onChange={(e) => setNewUserData({...newUserData, role: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Only administrators can create other admin accounts
                </p>
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
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center space-x-2"
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