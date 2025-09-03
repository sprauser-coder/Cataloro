import React from 'react';
import { useAuth } from '../../context/AuthContext';
import AdminDashboardFixed from './AdminDashboardFix';

function AdminPanel() {
  const { user } = useAuth();
  
  // Simple admin check - if user is admin role or specific admin email
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

  return <AdminDashboardFixed />;
}

export default AdminPanel;