/**
 * CATALORO - Main Layout Component
 * Header, Navigation, and Content wrapper with modern design
 */

import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Navigation from './Navigation';
import { useAuth } from '../../context/AuthContext';

function Layout() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="spinner"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect to login via routing
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Fixed Header */}
      <Header />
      
      {/* Main Content Area */}
      <div className="flex">
        {/* Side Navigation */}
        <Navigation />
        
        {/* Main Content */}
        <main className="flex-1 ml-64 pt-16">
          <div className="p-6">
            <div className="max-w-7xl mx-auto">
              <Outlet />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default Layout;