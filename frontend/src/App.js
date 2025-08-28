import React from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';

// Context Providers
import { AuthProvider } from './context/AuthContext';

// Components
import { Toaster } from './components/ui/toaster';

// Feature Components
import AuthPage from './features/auth/AuthPage';
import ProtectedRoute from './features/auth/ProtectedRoute';
import AdminProtectedRoute from './features/auth/AdminProtectedRoute';
import HomePage from './features/marketplace/HomePage';
import BrowsePageSimple from './features/marketplace/BrowsePageSimple';
import SellPage from './features/listings/SellPage';
import FavoritesPage from './features/favorites/FavoritesPage';
import OrdersPage from './features/orders/OrdersPage';
import AdminPanel from './features/admin/AdminPanel';

// Styles
import './App.css';

// Version logging
console.log('🎯 CATALORO CLEAN ARCHITECTURE - VERSION 3.0 - MODULAR DESIGN');
console.log('✨ Features: Clean Architecture, Purple Theme, Modular Components');

function App() {
  return (
    <HashRouter>
      <AuthProvider>
        <div className="App">
          <Routes>
            {/* Public Routes */}
            <Route path="/auth" element={<AuthPage />} />
            
            {/* Protected Routes */}
            <Route path="/" element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            } />
            
            <Route path="/browse" element={
              <ProtectedRoute>
                <BrowsePageSimple />
              </ProtectedRoute>
            } />
            
            <Route path="/sell" element={
              <ProtectedRoute>
                <SellPage />
              </ProtectedRoute>
            } />
            
            <Route path="/orders" element={
              <ProtectedRoute>
                <OrdersPage />
              </ProtectedRoute>
            } />
            
            <Route path="/favorites" element={
              <ProtectedRoute>
                <FavoritesPage />
              </ProtectedRoute>
            } />
            
            {/* Admin Routes */}
            <Route path="/admin" element={
              <AdminProtectedRoute>
                <AdminPanel />
              </AdminProtectedRoute>
            } />
            
            {/* Default redirect */}
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
          
          {/* Global Toast Notifications */}
          <Toaster />
        </div>
      </AuthProvider>
    </HashRouter>
  );
}

export default App;