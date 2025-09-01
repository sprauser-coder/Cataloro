/**
 * CATALORO - Main Application Component
 * Clean routing and providers only - following corporate architecture
 */

import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { NotificationProvider } from './context/NotificationContext';
import { MarketplaceProvider } from './context/MarketplaceContext';
import ModernLayout from './components/layout/ModernLayout';

// Modern Feature Components
import ModernBrowsePage from './features/marketplace/ModernBrowsePage';
import CategoriesPage from './features/marketplace/CategoriesPage';
import ShoppingCartPage from './features/marketplace/ShoppingCartPage';
import ProductDetailPage from './features/marketplace/ProductDetailPage';
import MyListingsPage from './features/marketplace/MyListingsPage';
import CreateListingPage from './features/marketplace/CreateListingPage';
import EditListingPage from './features/marketplace/EditListingPage';
import PendingSalesPage from './features/marketplace/PendingSalesPage';
import ViewAllRequestsPage from './features/marketplace/ViewAllRequestsPage';
import DealsPage from './features/orders/DealsPage';
import AdminPanel from './features/admin/AdminPanel';
import FavoritesPage from './features/marketplace/FavoritesPage';
import NotificationsPage from './features/shared/NotificationsPage';
import ProfilePage from './features/profile/ProfilePage';
import MessagesPage from './features/messaging/MessagesPage';
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
          <MarketplaceProvider>
            <Router>
              <Routes>
                {/* Public Routes */}
                <Route path={APP_ROUTES.LOGIN} element={<SimpleLoginPage />} />
                <Route path={APP_ROUTES.REGISTER} element={<RegisterPage />} />
                
                {/* Protected Routes with Modern Layout */}
                <Route path="/" element={<ModernLayout />}>
                  <Route index element={<Navigate to={APP_ROUTES.BROWSE} replace />} />
                  <Route path={APP_ROUTES.BROWSE} element={<ModernBrowsePage />} />
                  <Route path="categories" element={<CategoriesPage />} />
                  <Route path="cart" element={<ShoppingCartPage />} />
                  <Route path="product/:productId" element={<ProductDetailPage />} />
                  <Route path="search" element={<ModernBrowsePage />} />
                  <Route path="trending" element={<ModernBrowsePage />} />
                  <Route path="create-listing" element={<CreateListingPage />} />
                  <Route path="edit-listing/:id" element={<EditListingPage />} />
                  <Route path="pending-sales" element={<PendingSalesPage />} />
                  <Route path="view-all-requests" element={<ViewAllRequestsPage />} />
                  <Route path={APP_ROUTES.MY_LISTINGS} element={<MyListingsPage />} />
                  <Route path="my-orders" element={<DealsPage />} />
                  <Route path={APP_ROUTES.MY_DEALS} element={<DealsPage />} />
                  <Route path="messages" element={<MessagesPage />} />
                  <Route path="analytics" element={<AdminPanel />} />
                  <Route path="performance" element={<AdminPanel />} />
                  <Route path={APP_ROUTES.ADMIN_PANEL} element={<AdminPanel />} />
                  <Route path="admin/analytics" element={<AdminPanel />} />
                  <Route path="admin/users" element={<AdminPanel />} />
                  <Route path={APP_ROUTES.FAVORITES} element={<FavoritesPage />} />
                  <Route path={APP_ROUTES.NOTIFICATIONS} element={<NotificationsPage />} />
                  <Route path={APP_ROUTES.PROFILE} element={<ProfilePage />} />
                  <Route path="settings" element={<ProfilePage />} />
                </Route>

                {/* Fallback */}
                <Route path="*" element={<Navigate to={APP_ROUTES.BROWSE} replace />} />
              </Routes>
            </Router>
          </MarketplaceProvider>
        </NotificationProvider>
      </AuthProvider>
    </div>
  );
}

export default App;