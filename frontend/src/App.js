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
  return (
    <div className="App">
      {/* Loading indicator */}
      <div id="app-loader" style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        fontSize: '1.2rem'
      }}>
        🚀 Loading Cataloro...
      </div>
      
      <Router>
        <Routes>
          {/* Public Routes - No context providers for now */}
          <Route path={APP_ROUTES.LOGIN} element={<SimpleLoginPage />} />
          <Route path={APP_ROUTES.REGISTER} element={<RegisterPage />} />
          <Route path="/" element={<SimpleLoginPage />} />
          <Route path="*" element={<SimpleLoginPage />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;