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
  Plus,
  User,
  Check,
  Clock,
  Calendar,
  MapPin,
  X
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

// Import the existing components we'll use as tabs
import TenderManagementPage from './TenderManagementPage';
import MyListingsPage from './MyListingsPage';
import { CompletedTransactionCard } from './BuyManagementPage';

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
    if (!user?.id) return;
    
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
      id: 'accepted',
      label: 'Accepted Tenders',
      icon: CheckCircle,
      description: 'Manage accepted tenders and orders'
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
          
          {activeTab === 'accepted' && (
            <AcceptedTendersTab 
              user={user}
              onRefresh={loadCompletedTransactions}
            />
          )}
          
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
            <CompletedTransactionCard
              key={transaction.id}
              transaction={transaction}
              onUndoCompletion={undoTransactionCompletion}
            />
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

// Accepted Tenders Tab Component
function AcceptedTendersTab({ user, onRefresh }) {
  const [acceptedTenders, setAcceptedTenders] = useState([]);
  const [loading, setLoading] = useState(false);
  const { showToast } = useNotifications();

  // Load accepted tenders
  const loadAcceptedTenders = async () => {
    if (!user?.id) return;
    
    try {
      setLoading(true);
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/tenders/seller/${user.id}/accepted`,
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setAcceptedTenders(data);
      } else {
        console.error('Failed to load accepted tenders');
        setAcceptedTenders([]);
      }
    } catch (error) {
      console.error('Error loading accepted tenders:', error);
      setAcceptedTenders([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAcceptedTenders();
  }, [user?.id]);

  // Complete order - mark as completed
  const completeOrder = async (tenderId, listingId) => {
    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/user/complete-transaction`,
        {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ 
            listing_id: listingId,
            notes: 'Order completed by seller',
            method: 'seller_completion'
          })
        }
      );
      
      if (response.ok) {
        showToast('Order marked as completed successfully', 'success');
        loadAcceptedTenders(); // Refresh accepted tenders (should now be empty)
        loadCompletedTransactions(); // Refresh completed transactions
        
        // Redirect to Completed tab
        handleTabChange('completed');
      } else {
        showToast('Failed to complete order', 'error');
      }
    } catch (error) {
      console.error('Error completing order:', error);
      showToast('Error completing order', 'error');
    }
  };

  // Set back online - reactivate listing
  const setBackOnline = async (listingId, listingTitle) => {
    if (!window.confirm(`Set "${listingTitle}" back online? This will reactivate the listing and make it available for new tenders.`)) {
      return;
    }

    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/listings/${listingId}/reactivate`,
        {
          method: 'PUT',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        }
      );
      
      if (response.ok) {
        showToast('Listing set back online successfully', 'success');
        loadAcceptedTenders();
      } else {
        showToast('Failed to set listing back online', 'error');
      }
    } catch (error) {
      console.error('Error setting listing back online:', error);
      showToast('Error setting listing back online', 'error');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Accepted Tenders</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Manage tenders you have accepted and orders to fulfill
          </p>
        </div>
        
        <button
          onClick={loadAcceptedTenders}
          disabled={loading}
          className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Accepted Tenders List */}
      {loading ? (
        <div className="text-center py-8">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto text-gray-400" />
          <p className="mt-2 text-sm text-gray-500">Loading accepted tenders...</p>
        </div>
      ) : acceptedTenders.length > 0 ? (
        <div className="space-y-4">
          {acceptedTenders.map((tender) => (
            <div
              key={tender.id}
              className="bg-white dark:bg-gray-700 rounded-lg shadow border border-gray-200 dark:border-gray-600 p-6"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* Listing Info */}
                  <div className="flex items-start space-x-4">
                    {tender.listing_image && (
                      <img
                        src={tender.listing_image}
                        alt={tender.listing_title}
                        className="w-16 h-16 rounded-lg object-cover"
                      />
                    )}
                    <div className="flex-1">
                      <h4 className="text-lg font-medium text-gray-900 dark:text-white">
                        {tender.listing_title}
                      </h4>
                      <div className="mt-2 space-y-1">
                        <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                          <DollarSign className="w-4 h-4 mr-1" />
                          Accepted Amount: €{tender.offer_amount?.toFixed(2)}
                        </div>
                        <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                          <User className="w-4 h-4 mr-1" />
                          Buyer: {tender.buyer_name || 'Unknown'}
                        </div>
                        <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                          <RefreshCw className="w-4 h-4 mr-1" />
                          Accepted: {new Date(tender.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Tender Accepted Badge */}
                  <div className="mt-4">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-green-600 text-white">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Tender Accepted
                    </span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-col space-y-2 ml-4">
                  <button
                    onClick={() => completeOrder(tender.id, tender.listing_id)}
                    className="inline-flex items-center px-3 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Complete Order
                  </button>
                  
                  <button
                    onClick={() => setBackOnline(tender.listing_id, tender.listing_title)}
                    className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600"
                  >
                    <Package className="w-4 h-4 mr-2" />
                    Set Back Online
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <CheckCircle className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No accepted tenders</h3>
          <p className="mt-1 text-sm text-gray-500">
            Tenders you accept will appear here for order management.
          </p>
        </div>
      )}
    </div>
  );
}

export default SellPage;