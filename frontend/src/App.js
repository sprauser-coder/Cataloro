/**
 * CATALORO - Main Application Component
 * Clean routing and providers only - following corporate architecture
 */

import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { NotificationProvider } from './context/NotificationContext';
import Layout from './components/layout/Layout';

// Feature Components
import BrowsePage from './features/marketplace/BrowsePage';
import MyListingsPage from './features/marketplace/MyListingsPage';
import DealsPage from './features/orders/DealsPage';
import AdminPanel from './features/admin/AdminPanel';
import FavoritesPage from './features/marketplace/FavoritesPage';
import NotificationsPage from './features/shared/NotificationsPage';
import ProfilePage from './features/profile/ProfilePage';
import SimpleLoginPage from './features/auth/SimpleLoginPage';
import RegisterPage from './features/auth/RegisterPage';

// Import centralized configuration
import { APP_ROUTES } from './config/directions';

import './App.css';

function App() {
  useEffect(() => {
    // Hide loading screen once React is mounted
    const loader = document.getElementById('app-loader');
    if (loader) {
      setTimeout(() => {
        loader.style.display = 'none';
      }, 500);
    }
  }, []);

  return (
    <div className="App">
      <AuthProvider>
        <NotificationProvider>
          <Router>
            <Routes>
              {/* Public Routes */}
              <Route path={APP_ROUTES.LOGIN} element={<SimpleLoginPage />} />
              <Route path={APP_ROUTES.REGISTER} element={<RegisterPage />} />
              
              {/* Protected Routes with Layout */}
              <Route path="/" element={<Layout />}>
                <Route index element={<Navigate to={APP_ROUTES.BROWSE} replace />} />
                <Route path={APP_ROUTES.BROWSE} element={<BrowsePage />} />
                <Route path={APP_ROUTES.MY_LISTINGS} element={<MyListingsPage />} />
                <Route path={APP_ROUTES.MY_DEALS} element={<DealsPage />} />
                <Route path={APP_ROUTES.ADMIN_PANEL} element={<AdminPanel />} />
                <Route path={APP_ROUTES.FAVORITES} element={<FavoritesPage />} />
                <Route path={APP_ROUTES.NOTIFICATIONS} element={<NotificationsPage />} />
                <Route path={APP_ROUTES.PROFILE} element={<ProfilePage />} />
              </Route>

              {/* Fallback */}
              <Route path="*" element={<Navigate to={APP_ROUTES.BROWSE} replace />} />
            </Routes>
          </Router>
        </NotificationProvider>
      </AuthProvider>
    </div>
  );
}

export default App;