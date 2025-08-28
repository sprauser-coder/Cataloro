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
                <BrowsePage />
              </ProtectedRoute>
            } />
            
            <Route path="/sell" element={
              <ProtectedRoute>
                <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
                  <div className="max-w-7xl mx-auto px-4 py-16">
                    <h1 className="text-4xl font-light text-slate-900 mb-8">Sell Products</h1>
                    <div className="bg-white rounded-2xl p-12 text-center">
                      <div className="text-6xl mb-4">💰</div>
                      <h3 className="text-xl font-semibold text-slate-700 mb-2">Sell Page</h3>
                      <p className="text-slate-500">Product selling functionality will be implemented here</p>
                    </div>
                  </div>
                </div>
              </ProtectedRoute>
            } />
            
            <Route path="/orders" element={
              <ProtectedRoute>
                <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
                  <div className="max-w-7xl mx-auto px-4 py-16">
                    <h1 className="text-4xl font-light text-slate-900 mb-8">My Orders</h1>
                    <div className="bg-white rounded-2xl p-12 text-center">
                      <div className="text-6xl mb-4">📦</div>
                      <h3 className="text-xl font-semibold text-slate-700 mb-2">Orders Page</h3>
                      <p className="text-slate-500">Order management functionality will be implemented here</p>
                    </div>
                  </div>
                </div>
              </ProtectedRoute>
            } />
            
            <Route path="/favorites" element={
              <ProtectedRoute>
                <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
                  <div className="max-w-7xl mx-auto px-4 py-16">
                    <h1 className="text-4xl font-light text-slate-900 mb-8">My Favorites</h1>
                    <div className="bg-white rounded-2xl p-12 text-center">
                      <div className="text-6xl mb-4">❤️</div>
                      <h3 className="text-xl font-semibold text-slate-700 mb-2">Favorites Page</h3>
                      <p className="text-slate-500">Favorites management functionality will be implemented here</p>
                    </div>
                  </div>
                </div>
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