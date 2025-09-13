/**
 * CATALORO - Sell Management Page
 * Consolidated page with all selling-related functionality
 * Tabs: Sell Tenders, Listings, Completed
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  DollarSign,
  Package,
  CheckCircle,
  RefreshCw,
  Plus
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

// Import the existing components we'll use as tabs
import TenderManagementPage from './TenderManagementPage';
import MyListingsPage from './MyListingsPage';

function SellPage() {
  const [activeTab, setActiveTab] = useState('tenders');
  const [searchParams, setSearchParams] = useSearchParams();
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const [completedTransactions, setCompletedTransactions] = useState([]);
  const [loading, setLoading] = useState(false);

  // Set active tab from URL parameters
  useEffect(() => {
    const tab = searchParams.get('tab');
    if (tab && ['tenders', 'listings', 'completed'].includes(tab)) {
      setActiveTab(tab);
    }
  }, [searchParams]);

  // Update URL when tab changes
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setSearchParams({ tab });
  };

  // Load completed transactions for seller
  const loadCompletedTransactions = async () => {
    if (!user?.id || activeTab !== 'completed') return;
    
    try {
      setLoading(true);
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/user/completed-transactions/${user.id}`,
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );
      
      if (response.ok) {
        const transactionsData = await response.json();
        // Filter to show only transactions where user is the seller
        const sellerTransactions = transactionsData.filter(t => t.user_role_in_transaction === 'seller');
        setCompletedTransactions(sellerTransactions);
      } else {
        console.error('Failed to load completed transactions');
        setCompletedTransactions([]);
      }
    } catch (error) {
      console.error('Error loading completed transactions:', error);
      setCompletedTransactions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCompletedTransactions();
  }, [user?.id, activeTab]);

  const tabs = [
    {
      id: 'tenders',
      label: 'Sell Tenders',
      icon: DollarSign,
      description: 'Manage received offers and bids'
    },
    {
      id: 'listings',
      label: 'My Listings',
      icon: Package,
      description: 'Manage your active listings'
    },
    {
      id: 'completed',
      label: 'Completed',
      icon: CheckCircle,
      description: 'Completed sales transactions'
    }
  ];

  if (!user) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 animate-spin mx-auto text-blue-600 mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading your selling dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6 space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Sell Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage your listings, received offers, and completed sales
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <a
            href="/create-listing"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Listing
          </a>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              
              return (
                <button
                  key={tab.id}
                  onClick={() => handleTabChange(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                    isActive
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <Icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </div>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          <div style={{ display: activeTab === 'tenders' ? 'block' : 'none' }}>
            <TenderManagementPage showSellTabOnly={true} />
          </div>
          
          <div style={{ display: activeTab === 'listings' ? 'block' : 'none' }}>
            <MyListingsPage />
          </div>
          
          {activeTab === 'completed' && (
            <CompletedSalesTab 
              transactions={completedTransactions}
              loading={loading}
              onRefresh={loadCompletedTransactions}
            />
          )}
        </div>
      </div>
    </div>
  );
}

// Completed Sales Tab Component
function CompletedSalesTab({ transactions, loading, onRefresh }) {
  const { showToast } = useNotifications();

  const undoTransactionCompletion = async (completionId) => {
    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/user/completed-transactions/${completionId}`,
        {
          method: 'DELETE',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      if (response.ok) {
        showToast('Transaction completion undone successfully', 'success');
        onRefresh();
      } else {
        const errorText = await response.text();
        console.error('Undo completion failed:', errorText);
        showToast('Failed to undo transaction completion', 'error');
      }
    } catch (error) {
      console.error('Error undoing transaction completion:', error);
      showToast('Error undoing transaction completion', 'error');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Completed Sales</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Items you've sold that have been physically handed over
          </p>
        </div>
        
        <button
          onClick={onRefresh}
          disabled={loading}
          className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Transactions List */}
      {loading ? (
        <div className="text-center py-8">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto text-gray-400" />
          <p className="mt-2 text-sm text-gray-500">Loading completed sales...</p>
        </div>
      ) : transactions.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {transactions.map((transaction) => (
            <div
              key={transaction.id}
              className="bg-white dark:bg-gray-700 rounded-lg shadow border border-gray-200 dark:border-gray-600 relative"
            >
              {/* Completion Status Badge */}
              <div className="absolute top-4 right-4 z-10">
                {transaction.is_fully_completed ? (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-green-600 text-white shadow-lg">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    COMPLETED
                  </span>
                ) : (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-yellow-600 text-white shadow-lg">
                    <RefreshCw className="w-3 h-3 mr-1" />
                    PENDING
                  </span>
                )}
              </div>

              {/* Item Image */}
              {transaction.listing_image && (
                <div className="aspect-w-16 aspect-h-9 overflow-hidden rounded-t-lg">
                  <img
                    src={transaction.listing_image}
                    alt={transaction.listing_title}
                    className="w-full h-48 object-cover"
                  />
                </div>
              )}
              
              <div className="p-4">
                <div className="mb-4">
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {transaction.listing_title}
                  </h3>
                  
                  <div className="space-y-1 mt-2">
                    <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                      <DollarSign className="w-3 h-3 mr-1" />
                      €{transaction.tender_amount?.toFixed(2) || transaction.listing_price?.toFixed(2) || '0.00'}
                    </div>
                    
                    <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                      <Package className="w-3 h-3 mr-1" />
                      Sold to: {transaction.other_party?.name || 'Unknown'}
                    </div>
                    
                    <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                      <RefreshCw className="w-3 h-3 mr-1" />
                      Completed: {new Date(transaction.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>

                {/* Undo Button */}
                <button
                  onClick={() => {
                    if (window.confirm('Undo your completion confirmation for this sale?')) {
                      undoTransactionCompletion(transaction.id);
                    }
                  }}
                  className="w-full inline-flex items-center justify-center px-3 py-2 border rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all border-red-300 text-red-700 bg-red-50 hover:bg-red-100 focus:ring-red-500 dark:border-red-600 dark:text-red-400 dark:bg-red-900 dark:hover:bg-red-800"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Undo My Confirmation
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <CheckCircle className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No completed sales</h3>
          <p className="mt-1 text-sm text-gray-500">
            Sales you mark as completed will appear here.
          </p>
        </div>
      )}
    </div>
  );
}

export default SellPage;