/**
 * CATALORO - Ultra-Modern Admin Panel
 * Real KPI functionality, complete user management, and site customization
 */

import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Package, 
  BarChart3,
  Building,
  Target,
  FileText,
  Settings,
  Database,
  Globe,
  Download,
  Shield
} from 'lucide-react';
import DashboardTab from '../../components/admin/tabs/DashboardTab';
import UsersTab from '../../components/admin/tabs/UsersTab';
import ListingsTab from '../../components/admin/tabs/ListingsTab';
import BusinessTab from './BusinessTab';
import SystemNotificationsList from '../../components/admin/shared/SystemNotificationsList';
import { adminService } from '../../services/adminService';
import { useAuth } from '../../context/AuthContext';

function AdminPanel() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const { user, showToast } = useAuth();

  useEffect(() => {
    fetchDashboardData();
    fetchUsers();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const data = await adminService.getDashboardData();
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      showToast?.('Failed to load dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const usersData = await adminService.getUsers();
      setUsers(usersData);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      showToast?.('Failed to load users', 'error');
    }
  };

  const handleUpdateUser = async (userData) => {
    try {
      const updatedUser = await adminService.updateUser(userData);
      setUsers(users.map(u => u.id === updatedUser.id ? updatedUser : u));
      showToast?.('User updated successfully', 'success');
    } catch (error) {
      console.error('Failed to update user:', error);
      showToast?.('Failed to update user', 'error');
    }
  };

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'listings', label: 'Listings', icon: Package },
    { id: 'business', label: 'Business', icon: Building }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading admin panel...</p>
        </div>
      </div>
    );
  }

  if (!user?.isAdmin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center p-8">
          <Shield className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Access Denied</h1>
          <p className="text-gray-600 dark:text-gray-400">You don't have permission to access the admin panel.</p>
        </div>
      </div>
    );
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardTab dashboardData={dashboardData} showToast={showToast} />;
      case 'users':
        return <UsersTab users={users} onUpdateUser={handleUpdateUser} showToast={showToast} />;
      case 'listings':
        return <ListingsTab showToast={showToast} />;
      case 'business':
        return <BusinessTab showToast={showToast} />;
      default:
        return <DashboardTab dashboardData={dashboardData} showToast={showToast} />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Admin Panel</h1>
          </div>
        </div>
      </div>
      
      <div className="flex">
        <aside className="w-64 bg-white dark:bg-gray-800 shadow-sm">
          <nav className="mt-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center px-6 py-3 text-left ${
                    activeTab === tab.id
                      ? 'bg-blue-50 border-r-2 border-blue-600 text-blue-600'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-3" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </aside>
        
        <main className="flex-1 p-8">
          <div className="max-w-7xl mx-auto">
            {renderTabContent()}
          </div>
        </main>
      </div>
    </div>
  );
}

export default AdminPanel;