/**
 * CATALORO - Buy Management Page
 * Consolidated page with all buying-related functionality
 * Tabs: Tenders, Bought Items, Baskets, Completed
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  DollarSign,
  Package,
  Archive,
  CheckCircle,
  RefreshCw
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

// Import the existing components we'll use as tabs
import TenderManagementPage from './TenderManagementPage';
import BuyManagementPage from './BuyManagementPage';

function BuyPage() {
  const [activeTab, setActiveTab] = useState('tenders');
  const [searchParams, setSearchParams] = useSearchParams();
  const { user } = useAuth();
  const { showToast } = useNotifications();

  // Set active tab from URL parameters
  useEffect(() => {
    const tab = searchParams.get('tab');
    if (tab && ['tenders', 'bought-items', 'baskets', 'completed'].includes(tab)) {
      setActiveTab(tab);
    }
  }, [searchParams]);

  // Update URL when tab changes
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setSearchParams({ tab });
  };

  const tabs = [
    {
      id: 'tenders',
      label: 'Tenders',
      icon: DollarSign,
      description: 'Manage your bids and offers'
    },
    {
      id: 'bought-items',
      label: 'Bought Items',
      icon: Package,
      description: 'Items you have purchased'
    },
    {
      id: 'baskets',
      label: 'Baskets',
      icon: Archive,
      description: 'Organize your purchases'
    },
    {
      id: 'completed',
      label: 'Completed',
      icon: CheckCircle,
      description: 'Physically completed transactions'
    }
  ];

  if (!user) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 animate-spin mx-auto text-blue-600 mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading your buying dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Page Header */}
        <div className="mb-6 sm:mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white flex items-center">
                <Package className="w-6 h-6 sm:w-8 sm:h-8 mr-2 sm:mr-3 text-blue-600" />
                Buy Management
              </h1>
              <p className="mt-1 sm:mt-2 text-sm text-gray-600 dark:text-gray-400">
                Manage your purchases, bids, and completed transactions
              </p>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow border border-gray-200 dark:border-gray-700 mb-4 sm:mb-6">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex px-4 sm:px-6 overflow-x-auto scrollbar-hide" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }} aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              
              // Mobile-friendly tab labels
              const getMobileLabel = (tabId) => {
                switch(tabId) {
                  case 'tenders': return 'Tenders';
                  case 'bought-items': return 'Items';
                  case 'baskets': return 'Baskets';
                  case 'completed': return 'Done';
                  default: return tab.label;
                }
              };
              
              return (
                <button
                  key={tab.id}
                  onClick={() => handleTabChange(tab.id)}
                  className={`flex-1 py-3 sm:py-4 px-1 sm:px-3 border-b-2 font-medium text-xs sm:text-sm transition-colors duration-200 whitespace-nowrap text-center ${
                    isActive
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  <div className="flex items-center space-x-1 sm:space-x-2">
                    <Icon className="w-4 h-4" />
                    <span className="hidden sm:inline">{tab.label}</span>
                    <span className="sm:hidden">{getMobileLabel(tab.id)}</span>
                  </div>
                </button>
              );
            })}
          </nav>
        </div>

          {/* Tab Content */}
          <div className="p-4 sm:p-6">
          <div style={{ display: activeTab === 'tenders' ? 'block' : 'none' }}>
            <TenderManagementPage showBuyTabOnly={true} />
          </div>
          
          {(activeTab === 'bought-items' || activeTab === 'baskets' || activeTab === 'completed') && (
            <BuyManagementPage key={activeTab} initialTab={activeTab} hideNavigation={true} showOnlyTab={activeTab} />
          )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default BuyPage;