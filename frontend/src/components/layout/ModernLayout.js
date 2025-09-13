/**
 * CATALORO - Ultra-Modern Layout with Header Navigation
 * Sleek, modern design with comprehensive marketplace features
 */

import React, { useState, useEffect } from 'react';
import { Outlet, Navigate, useLocation, useNavigate } from 'react-router-dom';
import ModernHeader from './ModernHeader';
import MobileNav from './MobileNav';
import Footer from './Footer';
import NotificationToast from '../ui/NotificationToast';
import { useNotifications } from '../../context/NotificationContext';
import { loadAndApplySiteConfiguration } from '../../utils/siteConfiguration';

function ModernLayout() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Check authentication status
    const checkAuth = () => {
      const token = localStorage.getItem('cataloro_token');
      const user = localStorage.getItem('cataloro_user');
      
      console.log('🔐 Auth check - token:', !!token, 'user:', !!user, 'location:', location.pathname);
      
      if (token && user) {
        try {
          const userObj = JSON.parse(user);
          console.log('🔐 Auth success - user:', userObj.full_name || userObj.name);
          setIsAuthenticated(true);
        } catch (error) {
          console.log('🔐 Auth failed - invalid user data:', error);
          localStorage.removeItem('cataloro_token');
          localStorage.removeItem('cataloro_user');
          setIsAuthenticated(false);
        }
      } else {
        console.log('🔐 Auth failed - missing token or user');
        setIsAuthenticated(false);
      }
      
      setIsLoading(false);
    };
    
    // Initial check
    checkAuth();
    
    // Listen for storage changes (when user logs in from another tab or after login)
    const handleStorageChange = (e) => {
      if (e.key === 'cataloro_token' || e.key === 'cataloro_user') {
        console.log('🔐 Storage changed, re-checking auth');
        checkAuth();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [location.pathname, navigate]); // Include navigate in dependencies

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

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
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
      {/* Modern Header Navigation */}
      <ModernHeader 
        darkMode={darkMode}
        toggleDarkMode={toggleDarkMode}
        isMobileMenuOpen={isMobileMenuOpen}
        setIsMobileMenuOpen={setIsMobileMenuOpen}
      />

      {/* Mobile Navigation Overlay */}
      <MobileNav 
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
      />

      {/* Main Content Area */}
      <main className="pt-20 min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Outlet />
        </div>
      </main>

      {/* Footer */}
      <Footer />

      {/* Notification Toast Container */}
      <NotificationToast />

      {/* Backdrop for mobile menu */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}
    </div>
  );
}

export default ModernLayout;