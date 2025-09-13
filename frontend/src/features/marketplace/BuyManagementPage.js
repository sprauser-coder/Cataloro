/**
 * Buy Management Page
 * Manages bought items and baskets for users
 */

import React, { useState, useEffect } from 'react';
import { 
  ShoppingCart, 
  Package,
  Plus,
  Edit3,
  Trash2,
  MoreHorizontal,
  RefreshCw,
  Filter,
  Search,
  Calendar,
  DollarSign,
  Tag,
  User,
  MapPin,
  Clock,
  ExternalLink,
  Check,
  X,
  BookOpen,
  Eye,
  Settings,
  Archive,
  Download,
  Loader2
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import usePermissions from '../../hooks/usePermissions';

function BuyManagementPage({ initialTab = 'bought-items', hideNavigation = false, showOnlyTab = null }) {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const { permissions } = usePermissions();
  const [activeTab, setActiveTab] = useState(showOnlyTab || initialTab);
  const [completedTransactions, setCompletedTransactions] = useState([]);
  const [boughtItems, setBoughtItems] = useState([]);
  const [baskets, setBaskets] = useState([]);
  const [selectedBasket, setSelectedBasket] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [assignmentFilter, setAssignmentFilter] = useState('all'); // all, assigned, not-assigned
  const [showCreateBasket, setShowCreateBasket] = useState(false);
  const [showEditBasket, setShowEditBasket] = useState(false);
  const [basketForm, setBasketForm] = useState({ name: '', description: '' });
  const [exportingBaskets, setExportingBaskets] = useState({}); // Track which baskets are being exported

  // Load bought items
  const loadBoughtItems = async () => {
    if (!user?.id) return;
    
    try {
      setLoading(true);
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/user/bought-items/${user.id}`,
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );
      
      if (response.ok) {
        const items = await response.json();
        setBoughtItems(items);
      } else {
        console.error('Failed to load bought items');
        setBoughtItems([]);
      }
    } catch (error) {
      console.error('Error loading bought items:', error);
      setBoughtItems([]);
    } finally {
      setLoading(false);
    }
  };

  // Load baskets
  const loadBaskets = async () => {
    if (!user?.id) return;
    
    try {
      setLoading(true);
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/user/baskets/${user.id}`,
        {
          headers: { 'Content-Type': 'application/json' }
        }
      );
      
      if (response.ok) {
        const basketsData = await response.json();
        setBaskets(basketsData);
      } else {
        console.error('Failed to load baskets');
        setBaskets([]);
      }
    } catch (error) {
      console.error('Error loading baskets:', error);
      setBaskets([]);
    } finally {
      setLoading(false);
    }
  };

  // Load completed transactions
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
        setCompletedTransactions(transactionsData);
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

  // Create new basket
  const createBasket = async () => {
    if (!basketForm.name.trim()) {
      showToast('Basket name is required', 'error');
      return;
    }

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/user/baskets`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: user.id,
            name: basketForm.name.trim(),
            description: basketForm.description.trim()
          })
        }
      );
      
      if (response.ok) {
        showToast('Basket created successfully', 'success');
        setShowCreateBasket(false);
        setBasketForm({ name: '', description: '' });
        loadBaskets();
      } else {
        showToast('Failed to create basket', 'error');
      }
    } catch (error) {
      console.error('Error creating basket:', error);
      showToast('Error creating basket', 'error');
    }
  };

  // Update basket
  const updateBasket = async () => {
    if (!basketForm.name.trim() || !selectedBasket) {
      showToast('Basket name is required', 'error');
      return;
    }

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/user/baskets/${selectedBasket.id}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: basketForm.name.trim(),
            description: basketForm.description.trim()
          })
        }
      );
      
      if (response.ok) {
        showToast('Basket updated successfully', 'success');
        setShowEditBasket(false);
        setSelectedBasket(null);
        setBasketForm({ name: '', description: '' });
        loadBaskets();
      } else {
        showToast('Failed to update basket', 'error');
      }
    } catch (error) {
      console.error('Error updating basket:', error);
      showToast('Error updating basket', 'error');
    }
  };

  // Delete basket
  const deleteBasket = async (basketId) => {
    if (!window.confirm('Are you sure you want to delete this basket? All items will be unassigned.')) {
      return;
    }

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/user/baskets/${basketId}`,
        {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' }
        }
      );
      
      if (response.ok) {
        showToast('Basket deleted successfully', 'success');
        loadBaskets();
        loadBoughtItems(); // Refresh bought items to update assignment status
      } else {
        showToast('Failed to delete basket', 'error');
      }
    } catch (error) {
      console.error('Error deleting basket:', error);
      showToast('Error deleting basket', 'error');
    }
  };

  // Export basket as PDF
  const exportBasketPDF = async (basket, totals) => {
    // Set loading state for the specific basket
    setExportingBaskets(prev => ({ ...prev, [basket.id]: true }));
    
    try {
      showToast('Generating PDF export...', 'info');
      
      const exportData = {
        basketId: basket.id,
        basketName: basket.name,
        basketDescription: basket.description,
        totals: totals,
        items: basket.items || [],
        userId: user.id,
        exportDate: new Date().toISOString()
      };

      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/user/export-basket-pdf`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(exportData)
        }
      );

      if (!response.ok) {
        throw new Error(`Export failed: ${response.statusText}`);
      }

      // Handle file download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
      const filename = `cataloro-basket-${basket.name.replace(/[^a-zA-Z0-9]/g, '_')}-${timestamp}.pdf`;
      link.download = filename;
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      showToast('Basket PDF exported successfully!', 'success');

    } catch (error) {
      console.error('Export error:', error);
      showToast(`Export failed: ${error.message}`, 'error');
    } finally {
      // Clear loading state for the specific basket
      setExportingBaskets(prev => ({ ...prev, [basket.id]: false }));
    }
  };

  // Unassign item from basket
  const unassignItemFromBasket = async (itemId) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/user/bought-items/${itemId}/unassign`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' }
        }
      );
      
      if (response.ok) {
        showToast('Item unassigned from basket successfully', 'success');
        
        // Update the local state immediately for better UX
        setBoughtItems(prevItems => 
          prevItems.map(item => 
            item.id === itemId 
              ? { ...item, basket_id: null }
              : item
          )
        );
        
        // Reload data to ensure consistency
        loadBoughtItems();
        loadBaskets();
      } else {
        const errorText = await response.text();
        console.error('Unassign failed:', errorText);
        showToast('Failed to unassign item from basket', 'error');
      }
    } catch (error) {
      console.error('Error unassigning item:', error);
      showToast('Error unassigning item from basket', 'error');
    }
  };
  // Reassign item to different basket
  const reassignItemToBasket = async (itemId, fromBasketId, toBasketId) => {
    try {
      // First unassign from current basket
      const unassignResponse = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/user/bought-items/${itemId}/unassign`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' }
        }
      );
      
      if (!unassignResponse.ok) {
        throw new Error('Failed to unassign item');
      }
      
      // Then assign to new basket
      const assignResponse = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/user/bought-items/${itemId}/assign`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ basket_id: toBasketId })
        }
      );
      
      if (assignResponse.ok) {
        showToast('Item reassigned to basket successfully', 'success');
        loadBoughtItems();
        loadBaskets();
      } else {
        throw new Error('Failed to assign item to new basket');
      }
    } catch (error) {
      console.error('Error reassigning item:', error);
      showToast('Error reassigning item to basket', 'error');
    }
  };

  const assignItemToBasket = async (itemId, basketId) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/user/bought-items/${itemId}/assign`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ basket_id: basketId })
        }
      );
      
      if (response.ok) {
        showToast('Item assigned to basket successfully', 'success');
        
        // Update the local state immediately for better UX
        setBoughtItems(prevItems => 
          prevItems.map(item => 
            item.id === itemId 
              ? { ...item, basket_id: basketId }
              : item
          )
        );
        
        // Reload data to ensure consistency
        loadBoughtItems();
        loadBaskets();
      } else {
        const errorText = await response.text();
        console.error('Assignment failed:', errorText);
        showToast('Failed to assign item to basket', 'error');
      }
    } catch (error) {
      console.error('Error assigning item:', error);
      showToast('Error assigning item to basket', 'error');
    }
  };

  // Mark transaction as completed
  const markTransactionComplete = async (listingId, notes = '', method = 'meeting') => {
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
            notes: notes,
            method: method
          })
        }
      );
      
      if (response.ok) {
        const result = await response.json();
        showToast(
          result.is_fully_completed 
            ? 'Transaction fully completed!' 
            : 'Transaction marked as completed. Waiting for other party confirmation.', 
          'success'
        );
        
        // Reload data to reflect changes
        loadBoughtItems();
        loadCompletedTransactions();
      } else {
        const errorText = await response.text();
        console.error('Mark complete failed:', errorText);
        showToast('Failed to mark transaction complete', 'error');
      }
    } catch (error) {
      console.error('Error marking transaction complete:', error);
      showToast('Error marking transaction complete', 'error');
    }
  };

  // Undo transaction completion
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
        
        // Reload data to reflect changes
        loadCompletedTransactions();
        loadBoughtItems();
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

  useEffect(() => {
    loadBoughtItems();
    loadBaskets();
    loadCompletedTransactions();
  }, [user?.id]);

  // Filter items based on search and assignment status
  const filteredItems = boughtItems.filter(item => {
    const matchesSearch = item.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.seller_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = assignmentFilter === 'all' || 
                         (assignmentFilter === 'assigned' && item.basket_id) ||
                         (assignmentFilter === 'not-assigned' && !item.basket_id);
    
    return matchesSearch && matchesFilter;
  });

  // Calculate basket totals
  const calculateBasketTotals = (basket) => {
    const items = basket.items || [];
    const valuePaid = items.reduce((sum, item) => sum + (item.price || 0), 0);
    
    // Enhanced calculation logic: use pre-calculated values if available, otherwise calculate from PPM
    const ptG = items.reduce((sum, item) => {
      // Check if pre-calculated pt_g value exists and is non-zero
      if (item.pt_g && item.pt_g > 0) {
        return sum + item.pt_g;
      }
      // Fallback to PPM-based calculation
      return sum + ((item.weight || 0) * (item.pt_ppm || 0) / 1000 * (item.renumeration_pt || 0));
    }, 0);
    
    const pdG = items.reduce((sum, item) => {
      // Check if pre-calculated pd_g value exists and is non-zero
      if (item.pd_g && item.pd_g > 0) {
        return sum + item.pd_g;
      }
      // Fallback to PPM-based calculation
      return sum + ((item.weight || 0) * (item.pd_ppm || 0) / 1000 * (item.renumeration_pd || 0));
    }, 0);
    
    const rhG = items.reduce((sum, item) => {
      // Check if pre-calculated rh_g value exists and is non-zero
      if (item.rh_g && item.rh_g > 0) {
        return sum + item.rh_g;
      }
      // Fallback to PPM-based calculation
      return sum + ((item.weight || 0) * (item.rh_ppm || 0) / 1000 * (item.renumeration_rh || 0));
    }, 0);
    
    return { valuePaid, ptG, pdG, rhG };
  };

  if (!permissions.ui.showBuyingFeatures && user?.user_role !== 'Admin' && user?.user_role !== 'Admin-Manager') {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <Package className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">Access Denied</h3>
          <p className="mt-1 text-sm text-gray-500">You don't have permission to access buy management.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header */}
        {!hideNavigation && (
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
                  <ShoppingCart className="w-8 h-8 mr-3 text-blue-600" />
                  Inventory
                </h1>
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  Manage your purchased items and organize them into baskets
                </p>
              </div>
              
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => {
                    loadBoughtItems();
                    loadBaskets();
                    loadCompletedTransactions();
                  }}
                  disabled={loading}
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                  Refresh
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow mb-6">
          {!hideNavigation && (
            <div className="border-b border-gray-200 dark:border-gray-700">
              <nav className="-mb-px flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('bought-items')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'bought-items'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <Package className="w-4 h-4 inline mr-2" />
                Bought Items
              </button>
              
              <button
                onClick={() => setActiveTab('baskets')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'baskets'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <Archive className="w-4 h-4 inline mr-2" />
                Baskets
              </button>
              
              <button
                onClick={() => setActiveTab('completed')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'completed'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                }`}
              >
                <Check className="w-4 h-4 inline mr-2" />
                Completed
              </button>
            </nav>
            </div>
          )}
          
          <div className="p-6">
            {activeTab === 'bought-items' && (
              <BoughtItemsTab 
                items={filteredItems}
                baskets={baskets}
                searchTerm={searchTerm}
                setSearchTerm={setSearchTerm}
                assignmentFilter={assignmentFilter}
                setAssignmentFilter={setAssignmentFilter}
                onAssignToBasket={assignItemToBasket}
                onUnassignFromBasket={unassignItemFromBasket}
                onCreateBasket={() => setShowCreateBasket(true)}
                onMarkComplete={markTransactionComplete}
                loading={loading}
              />
            )}
            
            {activeTab === 'baskets' && (
              <BasketsTab 
                baskets={baskets}
                onCreateBasket={() => setShowCreateBasket(true)}
                onEditBasket={(basket) => {
                  setSelectedBasket(basket);
                  setBasketForm({ name: basket.name, description: basket.description || '' });
                  setShowEditBasket(true);
                }}
                onDeleteBasket={deleteBasket}
                onExportBasket={exportBasketPDF}
                onUnassignFromBasket={unassignItemFromBasket}
                onReassignToBasket={reassignItemToBasket}
                calculateTotals={calculateBasketTotals}
                loading={loading}
                exportingBaskets={exportingBaskets}
              />
            )}
            
            {activeTab === 'completed' && (
              <CompletedTab 
                transactions={completedTransactions}
                onUndoCompletion={undoTransactionCompletion}
                loading={loading}
              />
            )}
          </div>
        </div>

        {/* Create Basket Modal */}
        {showCreateBasket && (
          <BasketModal
            title="Create New Basket"
            form={basketForm}
            setForm={setBasketForm}
            onSave={createBasket}
            onClose={() => {
              setShowCreateBasket(false);
              setBasketForm({ name: '', description: '' });
            }}
          />
        )}

        {/* Edit Basket Modal */}
        {showEditBasket && (
          <BasketModal
            title="Edit Basket"
            form={basketForm}
            setForm={setBasketForm}
            onSave={updateBasket}
            onClose={() => {
              setShowEditBasket(false);
              setSelectedBasket(null);
              setBasketForm({ name: '', description: '' });
            }}
          />
        )}
      </div>
    </div>
  );
}

// Bought Items Tab Component
function BoughtItemsTab({ items, baskets, searchTerm, setSearchTerm, assignmentFilter, setAssignmentFilter, onAssignToBasket, onUnassignFromBasket, onCreateBasket, onMarkComplete, loading }) {
  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search bought items..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        
        {/* Assignment Filter */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <select
              value={assignmentFilter}
              onChange={(e) => setAssignmentFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Items</option>
              <option value="assigned">Assigned</option>
              <option value="not-assigned">Not Assigned</option>
            </select>
          </div>
          
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {items.length} items found
          </div>
        </div>
      </div>

      {/* Items List */}
      {loading ? (
        <div className="text-center py-8">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto text-gray-400" />
          <p className="mt-2 text-sm text-gray-500">Loading bought items...</p>
        </div>
      ) : items.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((item) => (
            <BoughtItemCard 
              key={item.id} 
              item={item} 
              baskets={baskets}
              onAssignToBasket={onAssignToBasket}
              onUnassignFromBasket={onUnassignFromBasket}
              onCreateBasket={onCreateBasket}
              onMarkComplete={onMarkComplete}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Package className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No bought items</h3>
          <p className="mt-1 text-sm text-gray-500">Items you purchase will appear here.</p>
        </div>
      )}
    </div>
  );
}

// Baskets Tab Component
function BasketsTab({ baskets, onCreateBasket, onEditBasket, onDeleteBasket, onExportBasket, onUnassignFromBasket, onReassignToBasket, calculateTotals, loading, exportingBaskets }) {
  return (
    <div className="space-y-6">
      {/* Header with Create Button */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Your Baskets</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Organize your purchased items into baskets
          </p>
        </div>
        
        <button
          onClick={onCreateBasket}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Basket
        </button>
      </div>

      {/* Baskets List */}
      {loading ? (
        <div className="text-center py-8">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto text-gray-400" />
          <p className="mt-2 text-sm text-gray-500">Loading baskets...</p>
        </div>
      ) : baskets.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {baskets.map((basket) => (
            <BasketCard
              key={basket.id}
              basket={basket}
              totals={calculateTotals(basket)}
              onEdit={() => onEditBasket(basket)}
              onDelete={() => onDeleteBasket(basket.id)}
              onExport={() => onExportBasket(basket, calculateTotals(basket))}
              onUnassignFromBasket={onUnassignFromBasket}
              onReassignToBasket={onReassignToBasket}
              allBaskets={baskets}
              isExporting={exportingBaskets[basket.id] || false}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Archive className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No baskets created</h3>
          <p className="mt-1 text-sm text-gray-500">Create your first basket to organize items.</p>
          <button
            onClick={onCreateBasket}
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create First Basket
          </button>
        </div>
      )}
    </div>
  );
}

// Bought Item Card Component
function BoughtItemCard({ item, baskets, onAssignToBasket, onUnassignFromBasket, onCreateBasket, onMarkComplete }) {
  const [showAssignMenu, setShowAssignMenu] = useState(false);
  const [showCompleteModal, setShowCompleteModal] = useState(false);

  return (
    <div className="bg-white dark:bg-gray-700 rounded-lg shadow border border-gray-200 dark:border-gray-600 relative">
      {/* Item Image */}
      {item.image && (
        <div className="aspect-w-16 aspect-h-9 overflow-hidden rounded-t-lg">
          <img
            src={item.image}
            alt={item.title}
            className="w-full h-48 object-cover"
          />
        </div>
      )}
      
      {/* ASSIGNED Badge Overlay */}
      {item.basket_id && (
        <div className="absolute top-4 right-4 z-10">
          <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold bg-green-600 text-white shadow-lg">
            <Archive className="w-4 h-4 mr-2" />
            ASSIGNED
          </span>
        </div>
      )}
      
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
            {item.title}
          </h3>
        </div>
        
        <div className="space-y-2 mb-4">
          <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
            <DollarSign className="w-3 h-3 mr-1" />
            €{item.price?.toFixed(2) || '0.00'}
          </div>
          
          <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
            <User className="w-3 h-3 mr-1" />
            {item.seller_name || 'Unknown Seller'}
          </div>
          
          <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
            <Calendar className="w-3 h-3 mr-1" />
            {new Date(item.purchased_at).toLocaleDateString()}
          </div>

          {/* Basket Assignment Info */}
          {item.basket_id && (
            <div className="flex items-center text-xs text-green-600 dark:text-green-400">
              <Archive className="w-3 h-3 mr-1" />
              Assigned to basket
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="space-y-2">
          {/* Mark as Completed Button */}
          <button
            onClick={() => setShowCompleteModal(true)}
            className="w-full inline-flex items-center justify-center px-3 py-2 border rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all border-green-300 text-green-700 bg-green-50 hover:bg-green-100 focus:ring-green-500 dark:border-green-600 dark:text-green-400 dark:bg-green-900 dark:hover:bg-green-800"
          >
            <Check className="w-4 h-4 mr-2" />
            Mark as Completed
          </button>

          {/* Assignment Dropdown - Using simple relative positioning */}
          <div className="relative z-50">
            {item.basket_id ? (
              <button
                onClick={() => {
                  if (window.confirm('Unassign this item from the basket? This will allow you to reassign it with updated catalyst values.')) {
                    onUnassignFromBasket(item.id);
                  }
                }}
                className="w-full inline-flex items-center justify-center px-3 py-2 border rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all border-red-300 text-red-700 bg-red-50 hover:bg-red-100 focus:ring-red-500 dark:border-red-600 dark:text-red-400 dark:bg-red-900 dark:hover:bg-red-800"
              >
                Unassign
              </button>
            ) : (
              <button
                onClick={() => setShowAssignMenu(!showAssignMenu)}
                className="w-full inline-flex items-center justify-center px-3 py-2 border rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all border-blue-300 text-blue-700 bg-blue-50 hover:bg-blue-100 focus:ring-blue-500 dark:border-blue-600 dark:text-blue-400 dark:bg-blue-900 dark:hover:bg-blue-800"
              >
                Assign to Basket
                <MoreHorizontal className="w-4 h-4 ml-2" />
              </button>
            )}

          {/* Simple absolute positioned dropdown */}
          {showAssignMenu && !item.basket_id && (
            <div className="absolute left-0 right-0 mt-2 bg-white dark:bg-gray-700 rounded-md shadow-lg border border-gray-200 dark:border-gray-600 z-[100]">
              <div className="py-1">
                {baskets.length > 0 ? (
                  baskets.map((basket) => (
                    <button
                      key={basket.id}
                      onClick={() => {
                        onAssignToBasket(item.id, basket.id);
                        setShowAssignMenu(false);
                      }}
                      className="block w-full px-4 py-2 text-sm text-left text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                    >
                      <Archive className="w-4 h-4 inline mr-2" />
                      {basket.name}
                    </button>
                  ))
                ) : (
                  <div className="px-4 py-2 text-sm text-gray-500 dark:text-gray-400">
                    No baskets available
                  </div>
                )}
                
                {baskets.length > 0 && (
                  <div className="border-t border-gray-200 dark:border-gray-600 my-1"></div>
                )}
                
                <button
                  onClick={() => {
                    onCreateBasket();
                    setShowAssignMenu(false);
                  }}
                  className="block w-full px-4 py-2 text-sm text-left text-blue-600 dark:text-blue-400 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                >
                  <Plus className="w-4 h-4 inline mr-2" />
                  Create New Basket
                </button>
              </div>
            </div>
          )}
          </div>
        </div>
      </div>

      {/* Completion Modal */}
      {showCompleteModal && (
        <CompletionModal
          item={item}
          onComplete={(notes, method) => {
            onMarkComplete(item.listing_id, notes, method);
            setShowCompleteModal(false);
          }}
          onClose={() => setShowCompleteModal(false)}
        />
      )}
    </div>
  );
}

// Basket Card Component
function BasketCard({ basket, totals, onEdit, onDelete, onExport, onUnassignFromBasket, onReassignToBasket, allBaskets, isExporting }) {
  const [showReassignMenu, setShowReassignMenu] = useState(null); // Track which item's menu is open

  return (
    <div className="bg-white dark:bg-gray-700 rounded-lg shadow border border-gray-200 dark:border-gray-600">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              {basket.name}
            </h3>
            {basket.description && (
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {basket.description}
              </p>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={onExport}
              disabled={isExporting}
              className={`p-2 transition-colors ${
                isExporting 
                  ? 'text-green-600 dark:text-green-400 cursor-not-allowed' 
                  : 'text-gray-400 hover:text-green-600 dark:hover:text-green-400'
              }`}
              title={isExporting ? "Exporting PDF..." : "Export basket as PDF"}
            >
              {isExporting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Download className="w-4 h-4" />
              )}
            </button>
            <button
              onClick={onEdit}
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <Edit3 className="w-4 h-4" />
            </button>
            <button
              onClick={onDelete}
              className="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Items Count */}
        <div className="mb-4">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
            {basket.items?.length || 0} items
          </span>
        </div>

        {/* Totals Summary */}
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Summary</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <dt className="text-xs text-gray-500 dark:text-gray-400">Value Paid</dt>
              <dd className="text-sm font-medium text-gray-900 dark:text-white">
                €{totals.valuePaid.toFixed(2)}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500 dark:text-gray-400">Pt g</dt>
              <dd className="text-sm font-medium text-gray-900 dark:text-white">
                {totals.ptG.toFixed(4)}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500 dark:text-gray-400">Pd g</dt>
              <dd className="text-sm font-medium text-gray-900 dark:text-white">
                {totals.pdG.toFixed(4)}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500 dark:text-gray-400">Rh g</dt>
              <dd className="text-sm font-medium text-gray-900 dark:text-white">
                {totals.rhG.toFixed(4)}
              </dd>
            </div>
          </div>
        </div>

        {/* Items List Preview with Actions */}
        {basket.items && basket.items.length > 0 && (
          <div className="mt-4">
            <h5 className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
              Items in Basket
            </h5>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {basket.items.map((item, index) => (
                <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-900 dark:text-white truncate flex-1 mr-2">
                      {item.title}
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      €{item.price?.toFixed(2) || '0.00'}
                    </span>
                  </div>
                  
                  {/* Action buttons for each item */}
                  <div className="flex items-center space-x-2 relative">
                    <button
                      onClick={() => {
                        if (window.confirm(`Unassign "${item.title}" from this basket?`)) {
                          onUnassignFromBasket(item.id);
                        }
                      }}
                      className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 dark:bg-red-900/50 dark:text-red-400 dark:hover:bg-red-900"
                    >
                      Unassign
                    </button>
                    
                    <div className="relative">
                      <button
                        onClick={() => setShowReassignMenu(showReassignMenu === item.id ? null : item.id)}
                        className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 dark:bg-blue-900/50 dark:text-blue-400 dark:hover:bg-blue-900"
                      >
                        Reassign
                      </button>
                      
                      {/* Reassign dropdown */}
                      {showReassignMenu === item.id && (
                        <div className="absolute left-0 top-full mt-1 bg-white dark:bg-gray-700 rounded-md shadow-lg border border-gray-200 dark:border-gray-600 z-50 min-w-32">
                          <div className="py-1">
                            {allBaskets.filter(b => b.id !== basket.id).length > 0 ? (
                              allBaskets.filter(b => b.id !== basket.id).map((targetBasket) => (
                                <button
                                  key={targetBasket.id}
                                  onClick={() => {
                                    onReassignToBasket(item.id, basket.id, targetBasket.id);
                                    setShowReassignMenu(null);
                                  }}
                                  className="block w-full px-3 py-2 text-sm text-left text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                                >
                                  <Archive className="w-3 h-3 inline mr-2" />
                                  {targetBasket.name}
                                </button>
                              ))
                            ) : (
                              <div className="px-3 py-2 text-sm text-gray-500 dark:text-gray-400">
                                No other baskets
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              {basket.items.length > 5 && (
                <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
                  Showing first 5 items
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Completed Tab Component
function CompletedTab({ transactions, onUndoCompletion, loading }) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">Completed Transactions</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Items that have been physically handed over between buyer and seller
        </p>
      </div>

      {/* Transactions List */}
      {loading ? (
        <div className="text-center py-8">
          <RefreshCw className="w-6 h-6 animate-spin mx-auto text-gray-400" />
          <p className="mt-2 text-sm text-gray-500">Loading completed transactions...</p>
        </div>
      ) : transactions.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {transactions.map((transaction) => (
            <CompletedTransactionCard
              key={transaction.id}
              transaction={transaction}
              onUndoCompletion={onUndoCompletion}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Check className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No completed transactions</h3>
          <p className="mt-1 text-sm text-gray-500">Transactions you mark as completed will appear here.</p>
        </div>
      )}
    </div>
  );
}

// Completed Transaction Card Component
function CompletedTransactionCard({ transaction, onUndoCompletion }) {
  const isFullyCompleted = transaction.is_fully_completed;
  const userRole = transaction.user_role_in_transaction; // "buyer" or "seller"
  const otherParty = transaction.other_party;
  
  const buyerConfirmed = !!transaction.buyer_confirmed_at;
  const sellerConfirmed = !!transaction.seller_confirmed_at;

  return (
    <div className="bg-white dark:bg-gray-700 rounded-lg shadow border border-gray-200 dark:border-gray-600 relative">
      {/* Completion Status Badge */}
      <div className="absolute top-4 right-4 z-10">
        {isFullyCompleted ? (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-green-600 text-white shadow-lg">
            <Check className="w-3 h-3 mr-1" />
            FULLY COMPLETED
          </span>
        ) : (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-yellow-600 text-white shadow-lg">
            <Clock className="w-3 h-3 mr-1" />
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
              <User className="w-3 h-3 mr-1" />
              {userRole === 'buyer' ? 'Bought from' : 'Sold to'}: {otherParty?.name || 'Unknown'}
            </div>
            
            <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
              <Calendar className="w-3 h-3 mr-1" />
              Completed: {new Date(transaction.created_at).toLocaleDateString()}
            </div>

            {transaction.completion_method && (
              <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                <MapPin className="w-3 h-3 mr-1" />
                Method: {transaction.completion_method}
              </div>
            )}
          </div>
        </div>

        {/* Completion Status */}
        <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <h4 className="text-xs font-medium text-gray-900 dark:text-white mb-2">Completion Status</h4>
          <div className="space-y-1">
            <div className="flex items-center text-xs">
              {buyerConfirmed ? (
                <Check className="w-3 h-3 text-green-600 mr-2" />
              ) : (
                <X className="w-3 h-3 text-red-500 mr-2" />
              )}
              <span className={buyerConfirmed ? 'text-green-600' : 'text-gray-500'}>
                Buyer confirmed
              </span>
            </div>
            <div className="flex items-center text-xs">
              {sellerConfirmed ? (
                <Check className="w-3 h-3 text-green-600 mr-2" />
              ) : (
                <X className="w-3 h-3 text-red-500 mr-2" />
              )}
              <span className={sellerConfirmed ? 'text-green-600' : 'text-gray-500'}>
                Seller confirmed
              </span>
            </div>
          </div>
        </div>

        {/* Notes */}
        {transaction.completion_notes && (
          <div className="mb-4 text-xs text-gray-600 dark:text-gray-400">
            <strong>Notes:</strong> {transaction.completion_notes}
          </div>
        )}

        {/* Undo Button */}
        <button
          onClick={() => {
            if (window.confirm('Undo your completion confirmation for this transaction?')) {
              onUndoCompletion(transaction.id);
            }
          }}
          className="w-full inline-flex items-center justify-center px-3 py-2 border rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all border-red-300 text-red-700 bg-red-50 hover:bg-red-100 focus:ring-red-500 dark:border-red-600 dark:text-red-400 dark:bg-red-900 dark:hover:bg-red-800"
        >
          <X className="w-4 h-4 mr-2" />
          Undo My Confirmation
        </button>
      </div>
    </div>
  );
}

// Completion Modal Component
function CompletionModal({ item, onComplete, onClose }) {
  const [notes, setNotes] = React.useState('');
  const [method, setMethod] = React.useState('meeting');

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white dark:bg-gray-800">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white text-center mb-4">
            Mark Transaction as Completed
          </h3>
          
          <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <p className="text-sm text-gray-900 dark:text-white font-medium">{item.title}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">€{item.price?.toFixed(2)}</p>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Completion Method
              </label>
              <select
                value={method}
                onChange={(e) => setMethod(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="meeting">In-person meeting</option>
                <option value="pickup">Pickup</option>
                <option value="delivery">Delivery</option>
                <option value="shipping">Shipping</option>
                <option value="other">Other</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Notes (Optional)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add any notes about the completion..."
                rows="3"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div className="flex items-center justify-end space-x-3 mt-6">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-400 dark:hover:bg-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Cancel
            </button>
            <button
              onClick={() => onComplete(notes, method)}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              Mark as Completed
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Basket Modal Component
function BasketModal({ title, form, setForm, onSave, onClose }) {
  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white dark:bg-gray-800">
        <div className="mt-3">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white text-center mb-4">
            {title}
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Basket Name
              </label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="Enter basket name..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Description (Optional)
              </label>
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="Enter description..."
                rows="3"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div className="flex items-center justify-end space-x-3 mt-6">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-400 dark:hover:bg-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Cancel
            </button>
            <button
              onClick={onSave}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BuyManagementPage;