/**
 * CATALORO - Main Layout Component
 * Header, Navigation, and Content wrapper with modern design
 */

import React, { useState, useEffect } from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import Header from './Header';
import Navigation from './Navigation';

function Layout() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check authentication status from localStorage
    const token = localStorage.getItem('cataloro_token');
    const user = localStorage.getItem('cataloro_user');
    
    if (token && user) {
      try {
        JSON.parse(user); // Validate user data
        setIsAuthenticated(true);
      } catch (error) {
        localStorage.removeItem('cataloro_token');
        localStorage.removeItem('cataloro_user');
        setIsAuthenticated(false);
      }
    } else {
      setIsAuthenticated(false);
    }
    
    setIsLoading(false);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
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