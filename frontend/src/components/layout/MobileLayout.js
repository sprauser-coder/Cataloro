/**
 * CATALORO - Mobile-Optimized Layout
 * Hybrid navigation system with bottom nav + hamburger menu
 */

import React, { useState, useEffect } from 'react';
import { Outlet, Navigate, useLocation } from 'react-router-dom';
import { Menu, Shield } from 'lucide-react';
import MobileBottomNav from './MobileBottomNav';
import MobileNav from './MobileNav';
import MobileAdminDrawer from '../mobile/MobileAdminDrawer';
import NotificationToast from '../ui/NotificationToast';
import { useNotifications } from '../../context/NotificationContext';
import { loadAndApplySiteConfiguration } from '../../utils/siteConfiguration';

function MobileLayout() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [darkMode, setDarkMode] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isAdminDrawerOpen, setIsAdminDrawerOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    // Check authentication status
    const token = localStorage.getItem('cataloro_token');
    const userData = localStorage.getItem('cataloro_user');
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
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

  // Check for dark mode preference and load site configuration
  useEffect(() => {
    const savedDarkMode = localStorage.getItem('cataloro_dark_mode');
    if (savedDarkMode === 'true') {
      setDarkMode(true);
      document.documentElement.classList.add('dark');
    }
    
    // Load and apply saved site configuration on app startup
    loadAndApplySiteConfiguration();
  }, []);

  // Close menus on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
    setIsAdminDrawerOpen(false);
  }, [location]);

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('cataloro_dark_mode', newDarkMode.toString());
    
    if (newDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-800 dark:text-white">Loading Cataloro...</h2>
        </div>
      </div>
    );
  }

  // Allow public access to certain routes like public profiles
  const publicRoutes = ['/profile/'];
  const isPublicRoute = publicRoutes.some(route => location.pathname.startsWith(route));
  
  if (!isAuthenticated && !isPublicRoute) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className={`min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300 ${darkMode ? 'dark' : ''}`}>
      
      {/* Mobile Header Bar */}
      <div className="lg:hidden fixed top-0 left-0 right-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 z-30">
        <div className="flex items-center justify-between px-4 py-3">
          {/* Left: Menu Button */}
          <button
            onClick={() => setIsMobileMenuOpen(true)}
            className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          >
            <Menu className="w-6 h-6" />
          </button>

          {/* Center: Logo */}
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">C</span>
            </div>
            <h1 className="text-lg font-bold text-gray-900 dark:text-white">Cataloro</h1>
          </div>

          {/* Right: Admin Access (if admin) */}
          <div className="flex items-center space-x-2">
            {user && user.role === 'admin' && (
              <button
                onClick={() => setIsAdminDrawerOpen(true)}
                className="p-2 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
              >
                <Shield className="w-5 h-5" />
              </button>
            )}
            
            {/* User Avatar */}
            {user && (
              <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-xs">
                  {user.full_name?.charAt(0) || user.username?.charAt(0) || 'U'}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Top Padding */}
      <div className="h-16 lg:hidden"></div>

      {/* Main Content */}
      <main className="min-h-[calc(100vh-8rem)] lg:min-h-screen">
        <Outlet />
      </main>

      {/* Mobile Bottom Navigation */}
      <MobileBottomNav />

      {/* Mobile Navigation Drawer */}
      <MobileNav 
        isOpen={isMobileMenuOpen} 
        onClose={() => setIsMobileMenuOpen(false)}
        darkMode={darkMode}
        toggleDarkMode={toggleDarkMode}
      />

      {/* Mobile Admin Drawer */}
      {user && user.role === 'admin' && (
        <MobileAdminDrawer
          isOpen={isAdminDrawerOpen}
          onClose={() => setIsAdminDrawerOpen(false)}
        />
      )}

      {/* Notification Toast */}
      <NotificationToast />

      {/* Backdrop for all mobile overlays */}
      {(isMobileMenuOpen || isAdminDrawerOpen) && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => {
            setIsMobileMenuOpen(false);
            setIsAdminDrawerOpen(false);
          }}
        />
      )}
    </div>
  );
}

export default MobileLayout;