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
  Archive
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import usePermissions from '../../hooks/usePermissions';

function BuyManagementPage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const { permissions } = usePermissions();
  const [activeTab, setActiveTab] = useState('bought-items');
  const [boughtItems, setBoughtItems] = useState([]);
  const [baskets, setBaskets] = useState([]);
  const [selectedBasket, setSelectedBasket] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [assignmentFilter, setAssignmentFilter] = useState('all'); // all, assigned, not-assigned
  const [showCreateBasket, setShowCreateBasket] = useState(false);
  const [showEditBasket, setShowEditBasket] = useState(false);
  const [basketForm, setBasketForm] = useState({ name: '', description: '' });

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

  // Assign item to basket
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
        showToast('Item assigned to basket', 'success');
        loadBoughtItems();
        loadBaskets();
      } else {
        showToast('Failed to assign item', 'error');
      }
    } catch (error) {
      console.error('Error assigning item:', error);
      showToast('Error assigning item', 'error');
    }
  };

  useEffect(() => {
    loadBoughtItems();
    loadBaskets();
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
    const ptG = items.reduce((sum, item) => sum + ((item.weight || 0) * (item.pt_ppm || 0) / 1000 * (item.renumeration_pt || 0)), 0);
    const pdG = items.reduce((sum, item) => sum + ((item.weight || 0) * (item.pd_ppm || 0) / 1000 * (item.renumeration_pd || 0)), 0);
    const rhG = items.reduce((sum, item) => sum + ((item.weight || 0) * (item.rh_ppm || 0) / 1000 * (item.renumeration_rh || 0)), 0);
    
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
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center">
                <ShoppingCart className="w-8 h-8 mr-3 text-blue-600" />
                Buy Management
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

        {/* Tabs */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow mb-6">
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
            </nav>
          </div>
          
          <div className="p-6">
            {activeTab === 'bought-items' && (
              <BoughtItemsTab 
                items={filteredItems}
                baskets={baskets}
                searchTerm={searchTerm}
                setSearchTerm={setSearchTerm}
                onAssignToBasket={assignItemToBasket}
                onCreateBasket={() => setShowCreateBasket(true)}
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
                calculateTotals={calculateBasketTotals}
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
function BoughtItemsTab({ items, baskets, searchTerm, setSearchTerm, onAssignToBasket, onCreateBasket, loading }) {
  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="flex items-center justify-between">
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
        
        <div className="text-sm text-gray-500 dark:text-gray-400">
          {items.length} items found
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
              onCreateBasket={onCreateBasket}
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
function BasketsTab({ baskets, onCreateBasket, onEditBasket, onDeleteBasket, calculateTotals, loading }) {
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
function BoughtItemCard({ item, baskets, onAssignToBasket, onCreateBasket }) {
  const [showAssignMenu, setShowAssignMenu] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0 });
  const buttonRef = React.useRef(null);

  const handleToggleMenu = () => {
    if (!showAssignMenu && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      setDropdownPosition({
        top: rect.bottom + window.scrollY + 8,
        left: rect.right - 224 + window.scrollX // 224px is w-56 width
      });
    }
    setShowAssignMenu(!showAssignMenu);
  };

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event) => {
      if (buttonRef.current && !buttonRef.current.contains(event.target)) {
        setShowAssignMenu(false);
      }
    };

    if (showAssignMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showAssignMenu]);

  return (
    <>
      <div className="bg-white dark:bg-gray-700 rounded-lg shadow border border-gray-200 dark:border-gray-600">
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
        
        <div className="p-4">
          <div className="flex items-start justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {item.title}
            </h3>
            {item.basket_id && (
              <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                <Archive className="w-3 h-3 mr-1" />
                Assigned
              </span>
            )}
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
          </div>

          {/* Assignment Button */}
          <button
            ref={buttonRef}
            onClick={handleToggleMenu}
            disabled={!!item.basket_id}
            className={`w-full inline-flex items-center justify-center px-3 py-2 border rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 ${
              item.basket_id
                ? 'border-gray-300 text-gray-500 bg-gray-50 cursor-not-allowed dark:border-gray-600 dark:text-gray-400 dark:bg-gray-800'
                : 'border-blue-300 text-blue-700 bg-blue-50 hover:bg-blue-100 focus:ring-blue-500 dark:border-blue-600 dark:text-blue-400 dark:bg-blue-900 dark:hover:bg-blue-800'
            }`}
          >
            {item.basket_id ? 'Already Assigned' : 'Assign to Basket'}
            <MoreHorizontal className="w-4 h-4 ml-2" />
          </button>
        </div>
      </div>

      {/* Fixed Position Dropdown Portal */}
      {showAssignMenu && !item.basket_id && (
        <div 
          className="fixed w-56 rounded-md shadow-lg bg-white dark:bg-gray-700 ring-1 ring-black ring-opacity-5 z-[9999]"
          style={{
            top: `${dropdownPosition.top}px`,
            left: `${dropdownPosition.left}px`,
          }}
        >
          <div className="py-1">
            {baskets.length > 0 ? (
              baskets.map((basket) => (
                <button
                  key={basket.id}
                  onClick={() => {
                    onAssignToBasket(item.id, basket.id);
                    setShowAssignMenu(false);
                  }}
                  className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 w-full text-left"
                >
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
              className="block px-4 py-2 text-sm text-blue-600 dark:text-blue-400 hover:bg-gray-100 dark:hover:bg-gray-600 w-full text-left"
            >
              <Plus className="w-4 h-4 inline mr-2" />
              Create New Basket
            </button>
          </div>
        </div>
      )}
    </>
  );
}

// Basket Card Component
function BasketCard({ basket, totals, onEdit, onDelete }) {
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

        {/* Items List Preview */}
        {basket.items && basket.items.length > 0 && (
          <div className="mt-4">
            <h5 className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
              Items in Basket
            </h5>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {basket.items.slice(0, 3).map((item, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <span className="text-gray-900 dark:text-white truncate">
                    {item.title}
                  </span>
                  <span className="text-gray-500 dark:text-gray-400">
                    €{item.price?.toFixed(2) || '0.00'}
                  </span>
                </div>
              ))}
              {basket.items.length > 3 && (
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  +{basket.items.length - 3} more items
                </div>
              )}
            </div>
          </div>
        )}
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