import React, { useState, useEffect } from 'react';
import { 
  Users, 
  UserPlus, 
  Shield, 
  Settings, 
  Activity, 
  RefreshCw,
  Search,
  Filter,
  Eye,
  Edit,
  Trash2,
  Lock,
  Unlock,
  Crown,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const EnhancedUserManagementPanel = ({ className = '' }) => {
  const [analytics, setAnalytics] = useState(null);
  const [roleHierarchy, setRoleHierarchy] = useState(null);
  const [userActivities, setUserActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState('all');

  useEffect(() => {
    fetchUserManagementData();
  }, []);

  const fetchUserManagementData = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      const [analyticsRes, hierarchyRes, activitiesRes] = await Promise.all([
        fetch(`${backendUrl}/api/v2/phase6/users/analytics`),
        fetch(`${backendUrl}/api/v2/phase6/users/role-hierarchy`),
        fetch(`${backendUrl}/api/v2/phase6/users/activity?limit=20`)
      ]);

      const [analyticsData, hierarchyData, activitiesData] = await Promise.all([
        analyticsRes.json(),
        hierarchyRes.json(),
        activitiesRes.json()
      ]);

      if (analyticsData.success) setAnalytics(analyticsData.analytics);
      if (hierarchyData.success) setRoleHierarchy(hierarchyData.hierarchy);
      if (activitiesData.success) setUserActivities(activitiesData.activities);

    } catch (error) {
      console.error('Failed to fetch user management data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getUserPermissions = async (userId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/v2/phase6/users/permissions/${userId}`);
      const data = await response.json();
      
      if (data.success) {
        alert(`User Permissions:\nRole: ${data.permissions.role}\nPermissions: ${data.permissions.permissions.length}\nExpires: ${data.permissions.expires_at || 'Never'}`);
      }
    } catch (error) {
      console.error('Failed to fetch user permissions:', error);
    }
  };

  const getRoleIcon = (role) => {
    switch (role.toLowerCase()) {
      case 'super_admin':
        return <Crown className="w-4 h-4 text-yellow-500" />;
      case 'admin':
        return <Shield className="w-4 h-4 text-red-500" />;
      case 'moderator':
        return <Eye className="w-4 h-4 text-blue-500" />;
      case 'seller':
        return <Users className="w-4 h-4 text-green-500" />;
      case 'buyer':
        return <Users className="w-4 h-4 text-gray-500" />;
      default:
        return <Users className="w-4 h-4 text-gray-400" />;
    }
  };

  const getActivityIcon = (action) => {
    switch (action) {
      case 'role_assigned':
        return <UserPlus className="w-4 h-4 text-green-500" />;
      case 'permissions_updated':
        return <Settings className="w-4 h-4 text-blue-500" />;
      case 'login':
        return <Lock className="w-4 h-4 text-gray-500" />;
      case 'logout':
        return <Unlock className="w-4 h-4 text-gray-500" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  const getActivityStatusColor = (success) => {
    return success ? 'text-green-600 bg-green-100 dark:bg-green-900/30 dark:text-green-400' : 'text-red-600 bg-red-100 dark:bg-red-900/30 dark:text-red-400';
  };

  const filteredActivities = userActivities.filter(activity => {
    const matchesSearch = searchTerm === '' || 
      activity.user_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      activity.action.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesSearch;
  });

  const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading user management panel...</p>
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
          <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
            <Users className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Enhanced User Management
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Advanced role management and user activity monitoring
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={fetchUserManagementData}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Overview Stats */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <Users className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {analytics.overview.total_users}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Users</div>
                <div className="text-sm text-blue-600">
                  {analytics.overview.total_roles} roles available
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <Activity className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {analytics.overview.active_sessions}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Active Sessions</div>
                <div className="text-sm text-green-600">
                  {analytics.overview.recent_activities_24h} activities today
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <Shield className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {Object.keys(analytics.permissions).length}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Permission Types</div>
                <div className="text-sm text-purple-600">
                  Enterprise-grade access control
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-orange-100 dark:bg-orange-900/30 rounded-lg">
                <Settings className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {analytics.tenants.active_tenants}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Active Tenants</div>
                <div className="text-sm text-orange-600">
                  Multi-tenant architecture
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Role Distribution and Hierarchy */}
      {analytics && roleHierarchy && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Role Distribution Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              User Role Distribution
            </h3>
            
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={Object.entries(analytics.roles).map(([role, count]) => ({
                    name: role.replace('_', ' ').toUpperCase(),
                    value: count
                  }))}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {Object.entries(analytics.roles).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Role Hierarchy */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Role Hierarchy & Permissions
            </h3>
            
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {roleHierarchy.hierarchy_levels.reverse().map((role, index) => {
                const roleData = roleHierarchy.roles[role];
                if (!roleData) return null;
                
                return (
                  <div key={role} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        {getRoleIcon(role)}
                        <span className="font-medium text-gray-900 dark:text-white">
                          {role.replace('_', ' ').toUpperCase()}
                        </span>
                        <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-1 rounded">
                          Level {roleData.level}
                        </span>
                      </div>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {roleData.permission_count} permissions
                      </span>
                    </div>
                    
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                      {roleData.permissions.slice(0, 3).join(', ')}
                      {roleData.permissions.length > 3 && ` +${roleData.permissions.length - 3} more`}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Permission Usage Analytics */}
      {analytics && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Permission Usage Analytics
          </h3>
          
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={Object.entries(analytics.permissions).map(([permission, count]) => ({
              name: permission.replace('_', ' '),
              count: count
            })).slice(0, 10)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* User Activity Log */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Recent User Activities
          </h3>
          
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search activities..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>
        </div>
        
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {filteredActivities.map((activity, index) => (
            <div key={index} className="flex items-start space-x-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="p-2 bg-white dark:bg-gray-800 rounded-lg">
                {getActivityIcon(activity.action)}
              </div>
              
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-gray-900 dark:text-white">
                    {activity.action.replace('_', ' ').toUpperCase()}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className={`text-xs px-2 py-1 rounded-full ${getActivityStatusColor(activity.success)}`}>
                      {activity.success ? 'Success' : 'Failed'}
                    </span>
                    <button
                      onClick={() => getUserPermissions(activity.user_id)}
                      className="text-xs text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200"
                    >
                      View User
                    </button>
                  </div>
                </div>
                
                <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  User: {activity.user_id} | Resource: {activity.resource}
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="text-xs text-gray-500">
                    {new Date(activity.timestamp).toLocaleString()}
                  </div>
                  <div className="text-xs text-gray-500">
                    IP: {activity.ip_address}
                  </div>
                </div>
                
                {activity.details && (
                  <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                    Details: {JSON.stringify(activity.details)}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {filteredActivities.length === 0 && (
            <div className="text-center py-8">
              <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">No activities found</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          User Management Actions
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => alert('Create user functionality would be implemented here')}
            className="flex items-center space-x-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
          >
            <UserPlus className="w-5 h-5 text-blue-600" />
            <span className="font-medium text-gray-900 dark:text-white">Create User</span>
          </button>
          
          <button
            onClick={() => alert('Bulk role assignment functionality would be implemented here')}
            className="flex items-center space-x-2 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
          >
            <Settings className="w-5 h-5 text-green-600" />
            <span className="font-medium text-gray-900 dark:text-white">Bulk Assign Roles</span>
          </button>
          
          <button
            onClick={() => alert('Export user data functionality would be implemented here')}
            className="flex items-center space-x-2 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors"
          >
            <Activity className="w-5 h-5 text-purple-600" />
            <span className="font-medium text-gray-900 dark:text-white">Export Data</span>
          </button>
        </div>
      </div>

      {/* Recommendations */}
      {analytics && analytics.recommendations && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            User Management Recommendations
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analytics.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div className="p-1 bg-blue-100 dark:bg-blue-900/30 rounded">
                  <AlertTriangle className="w-4 h-4 text-blue-600" />
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

export default EnhancedUserManagementPanel;