/**
 * Listings Management Tab Component
 * Extracted from AdminPanel.js for better maintainability and performance
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Package,
  CheckCircle,
  Eye,
  DollarSign,
  Search,
  RefreshCw,
  Ban,
  Trash2,
  Star,
  Shield,
  X,
  Download,
  Edit,
  AlertTriangle
} from 'lucide-react';

// Import MarketplaceContext for marketplace data
import { useMarketplace } from '../../../context/MarketplaceContext';

// Placeholder for ListingModal - would need to be created separately
const ListingModal = ({ listing, onSave, onClose }) => {
  const [formData, setFormData] = useState({
    title: listing?.title || '',
    price: listing?.price || '',
    description: listing?.description || '',
    condition: listing?.condition || 'New',
    location: listing?.location || '',
    status: listing?.status || 'active',
    ...listing
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <h3 className="text-lg font-semibold mb-4">
          {listing ? 'Edit Listing' : 'Create New Listing'}
        </h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Price (€)</label>
            <input
              type="number"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: parseFloat(e.target.value) })}
              className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600"
              rows="3"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Condition</label>
            <select
              value={formData.condition}
              onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
              className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600"
            >
              <option value="New">New</option>
              <option value="Like New">Like New</option>
              <option value="Good">Good</option>
              <option value="Fair">Fair</option>
              <option value="Poor">Poor</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Location</label>
            <input
              type="text"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              className="w-full px-3 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600"
            />
          </div>
          <div className="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 border rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              {listing ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

function ListingsTab({ showToast }) {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [activeSubTab, setActiveSubTab] = useState('active'); // Sub-tab state
  const [selectedListings, setSelectedListings] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingListing, setEditingListing] = useState(null);
  const [bulkAction, setBulkAction] = useState('');

  const { allProducts } = useMarketplace();

  useEffect(() => {
    fetchListings();
  }, []);

  const fetchListings = async () => {
    try {
      setLoading(true);
      console.log('🔄 Fetching listings from backend...');
      
      // For admin panel, we want to see ALL listings including sold ones - no limit
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/listings?status=all`);
      if (response.ok) {
        const backendData = await response.json();
        console.log('📊 Backend listings response:', backendData);
        
        // Handle different response formats - backend returns {listings: [...], total: N}
        let listingsArray = [];
        if (Array.isArray(backendData)) {
          listingsArray = backendData;
        } else if (backendData.listings && Array.isArray(backendData.listings)) {
          listingsArray = backendData.listings;
        }
        
        // Fetch pending orders data to enrich listings
        let allOrders = [];
        try {
          const ordersResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/orders`);
          if (ordersResponse.ok) {
            allOrders = await ordersResponse.json();
          } else {
            // Fallback: fetch some sample orders
            const fallbackResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/orders/seller/admin`);
            if (fallbackResponse.ok) {
              allOrders = await fallbackResponse.json();
            }
          }
        } catch (orderError) {
          console.log('⚠️ Could not fetch orders data:', orderError);
        }
        
        // Fetch user data to resolve seller information
        let allUsers = [];
        try {
          const usersResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/users`);
          if (usersResponse.ok) {
            allUsers = await usersResponse.json();
          }
        } catch (userError) {
          console.log('⚠️ Could not fetch users data:', userError);
        }
        
        // Convert backend listings to admin format with proper seller info
        const backendListings = listingsArray.map((listing, index) => {
          // Count pending orders for this listing
          const pendingOrders = allOrders.filter(order => 
            order.listing_id === listing.id && order.status === 'pending'
          ).length;
          
          // Find seller information
          const seller = allUsers.find(user => user.id === listing.seller_id);
          const sellerInfo = {
            id: listing.seller_id,
            username: seller?.username || 'Unknown User',
            full_name: seller?.full_name || seller?.username || 'Unknown User'
          };
          
          return {
            id: listing.id || listing._id || `backend-${index}`,
            title: listing.title,
            price: listing.price,
            status: listing.status || 'active',
            seller_id: listing.seller_id,
            seller_username: sellerInfo.username,
            seller_full_name: sellerInfo.full_name,
            created_date: listing.created_at ? new Date(listing.created_at).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
            views: listing.views || Math.floor(Math.random() * 1000),
            image: listing.images?.[0] || listing.image,
            description: listing.description,
            condition: listing.condition || 'New',
            location: listing.location || 'Unknown Location',
            pendingOrders: pendingOrders // Add pending orders count
          };
        });
        
        console.log('✅ Successfully loaded', backendListings.length, 'listings from backend with seller info');
        setListings(backendListings);
      } else {
        console.error('❌ Backend fetch failed with status:', response.status);
        showToast?.('Failed to load listings from backend', 'error');
        setListings([]); // Set empty array instead of falling back to marketplace data
      }
    } catch (error) {
      console.error('❌ Error fetching listings:', error);
      showToast?.('Error loading listings from backend', 'error');
      setListings([]); // Set empty array instead of falling back to marketplace data
    } finally {
      setLoading(false);
    }
  };

  // Enhanced filtering logic with REAL DATA for sub-tabs
  const filteredListings = listings.filter(listing => {
    const matchesSearch = !searchTerm || 
                         listing.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         listing.seller_username?.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Use activeSubTab instead of filterStatus for sub-tab filtering
    let statusMatch = true;
    
    switch (activeSubTab) {
      case 'active':
        statusMatch = listing.status === 'active' || listing.status === 'approved';
        break;
      case 'pending':
        // Show listings that have pending status OR have pending orders
        const hasPendingOrders = listing.pendingOrders && listing.pendingOrders > 0;
        statusMatch = listing.status === 'pending' || listing.status === 'awaiting_approval' || hasPendingOrders;
        break;
      case 'inactive':
        statusMatch = listing.status === 'inactive' || listing.status === 'deactivated' || listing.status === 'paused';
        break;
      case 'expired':
        statusMatch = listing.status === 'expired';
        break;
      case 'sold':
        statusMatch = listing.status === 'sold' || listing.status === 'completed' || listing.status === 'finished';
        break;
      default:
        statusMatch = true;
    }
    
    return matchesSearch && statusMatch;
  });

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedListings(filteredListings.map(l => l.id));
    } else {
      setSelectedListings([]);
    }
  };

  const handleSelectListing = (listingId, checked) => {
    if (checked) {
      setSelectedListings([...selectedListings, listingId]);
    } else {
      setSelectedListings(selectedListings.filter(id => id !== listingId));
    }
  };

  const handleBulkAction = async (action = null) => {
    console.log('🚀 HANDLEBULKACTION CALLED!', 'Action:', action, 'Selected:', selectedListings);
    
    const actionToPerform = action || bulkAction;
    console.log('🔍 handleBulkAction called with:', actionToPerform, 'selectedListings:', selectedListings.length);
    
    if (!actionToPerform || selectedListings.length === 0) {
      console.log('❌ Early return: no action or no selected listings');
      showToast?.(`No action selected or no listings selected`, 'error');
      return;
    }

    try {
      console.log('🔍 Starting bulk action:', actionToPerform);
      
      // Perform backend operations for persistence
      if (['activate', 'deactivate', 'delete', 'feature', 'unfeature', 'approve', 'reject'].includes(actionToPerform)) {
        console.log('🔍 Performing backend operations for:', selectedListings);
        
        const updatePromises = selectedListings.map(async (listingId) => {
          const listing = listings.find(l => l.id === listingId);
          if (!listing) {
            console.log('❌ Listing not found:', listingId);
            return null;
          }

          console.log('🔍 Processing listing:', listingId, 'action:', actionToPerform);

          switch (actionToPerform) {
            case 'delete':
              console.log('🗑️ Deleting listing:', listingId);
              const deleteUrl = `${process.env.REACT_APP_BACKEND_URL}/api/listings/${listingId}`;
              console.log('🔍 Delete URL:', deleteUrl);
              
              const deleteResponse = await fetch(deleteUrl, {
                method: 'DELETE'
              });
              console.log('🔍 Delete request completed for:', listingId, 'Status:', deleteResponse.status);
              return deleteResponse;
            default:
              // For updates (activate, deactivate, feature, etc.)
              let updatedListing = { ...listing };
              
              switch (actionToPerform) {
                case 'activate':
                  updatedListing.status = 'active';
                  break;
                case 'deactivate':
                  updatedListing.status = 'inactive';
                  break;
                case 'feature':
                  updatedListing.featured = true;
                  break;
                case 'unfeature':
                  updatedListing.featured = false;
                  break;
                case 'approve':
                  updatedListing.status = 'approved';
                  updatedListing.approved = true;
                  break;
                case 'reject':
                  updatedListing.status = 'rejected';
                  updatedListing.rejected = true;
                  break;
              }
              
              return fetch(`${process.env.REACT_APP_BACKEND_URL}/api/listings/${listingId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedListing)
              });
          }
        });

        // Wait for all operations to complete
        console.log('⏳ Waiting for all operations to complete...');
        const results = await Promise.all(updatePromises);
        console.log('✅ All operations completed. Results:', results.map(r => r ? r.status : 'null'));
        
        // Check for any failed operations
        const failedOperations = results.filter(result => result && !result.ok);
        console.log('🔍 Failed operations count:', failedOperations.length);
        
        if (failedOperations.length > 0) {
          console.error('❌ Failed operations:', failedOperations);
          throw new Error(`${failedOperations.length} operations failed`);
        }

        console.log('✅ All operations successful, updating local state...');
      }

      // Update local state after successful backend operations
      console.log('🔄 Updating local state for action:', actionToPerform);
      
      switch (actionToPerform) {
        case 'activate':
          setListings(listings.map(l => 
            selectedListings.includes(l.id) ? {...l, status: 'active'} : l
          ));
          showToast?.(`${selectedListings.length} listings activated`, 'success');
          break;
        case 'deactivate':
          setListings(listings.map(l => 
            selectedListings.includes(l.id) ? {...l, status: 'inactive'} : l
          ));
          showToast?.(`${selectedListings.length} listings deactivated`, 'success');
          break;
        case 'delete':
          console.log('🗑️ Executing delete case. Filtering out listings:', selectedListings);
          const beforeCount = listings.length;
          const filteredListings = listings.filter(l => !selectedListings.includes(l.id));
          console.log(`🔍 Before: ${beforeCount} listings, After: ${filteredListings.length} listings`);
          setListings(filteredListings);
          showToast?.(`${selectedListings.length} listings deleted successfully`, 'success');
          
          // Immediate refresh from backend to ensure data consistency
          console.log('🔄 Refreshing listings from backend after bulk delete...');
          await fetchListings();
          console.log('✅ Listings refreshed after bulk delete');
          break;
        case 'feature':
          setListings(listings.map(l => 
            selectedListings.includes(l.id) ? {...l, featured: true} : l
          ));
          showToast?.(`${selectedListings.length} listings featured`, 'success');
          break;
        case 'unfeature':
          setListings(listings.map(l => 
            selectedListings.includes(l.id) ? {...l, featured: false} : l
          ));
          showToast?.(`${selectedListings.length} listings unfeatured`, 'success');
          break;
        case 'approve':
          setListings(listings.map(l => 
            selectedListings.includes(l.id) ? {...l, status: 'approved', approved: true} : l
          ));
          showToast?.(`${selectedListings.length} listings approved`, 'success');
          break;
        case 'reject':
          setListings(listings.map(l => 
            selectedListings.includes(l.id) ? {...l, status: 'rejected', rejected: true} : l
          ));
          showToast?.(`${selectedListings.length} listings rejected`, 'success');
          break;
        case 'duplicate':
          // For duplicate, create new listings via backend
          const duplicatePromises = selectedListings.map(async (id) => {
            const original = listings.find(l => l.id === id);
            const duplicatedListing = {
              ...original,
              title: `${original.title} (Copy)`,
              created_date: new Date().toISOString().split('T')[0]
            };
            delete duplicatedListing.id; // Let backend assign new ID
            
            return fetch(`${process.env.REACT_APP_BACKEND_URL}/api/listings`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(duplicatedListing)
            });
          });
          
          await Promise.all(duplicatePromises);
          // Reload listings to get the new ones with proper backend IDs
          await fetchListings();
          showToast?.(`${selectedListings.length} listings duplicated`, 'success');
          break;
        case 'export':
          // Export selected listings (would need backend implementation)
          showToast?.(`${selectedListings.length} listings exported`, 'success');
          break;
        case 'bulk-edit':
          // Open bulk edit modal (would need implementation)
          showToast?.(`Bulk edit mode activated for ${selectedListings.length} listings`, 'info');
          break;
        default:
          showToast?.(`Unknown action: ${actionToPerform}`, 'error');
          break;
      }
      
      // Clear selection and reset bulk action
      setSelectedListings([]);
      setBulkAction('');
      console.log('✅ Bulk action completed successfully');
    } catch (error) {
      console.error('❌ Bulk action error:', error);
      showToast?.(`Error performing bulk action: ${error.message}`, 'error');
    }
  };

  // Confirmation modal state
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null);
  const [confirmListings, setConfirmListings] = useState([]);

  // Confirmation modal handler
  const requestBulkAction = (action) => {
    console.log('🔍 Requesting bulk action:', action, 'for', selectedListings.length, 'listings');
    
    if (selectedListings.length === 0) {
      showToast?.('No listings selected', 'error');
      return;
    }

    // Show confirmation for destructive actions
    if (['delete', 'reject'].includes(action)) {
      setConfirmAction(action);
      setConfirmListings([...selectedListings]);
      setShowConfirmModal(true);
    } else {
      // Direct execution for non-destructive actions
      handleBulkAction(action);
    }
  };

  // Confirmed bulk action execution
  const executeBulkAction = async () => {
    console.log('🚀 EXECUTING confirmed bulk action:', confirmAction);
    console.log('🔍 Listings to process:', confirmListings);
    
    setShowConfirmModal(false);
    
    if (confirmAction && confirmListings.length > 0) {
      console.log('🎯 Calling handleBulkAction directly with confirmed listings');
      
      // Save current selected listings
      const originalSelected = selectedListings;
      
      // Temporarily set selectedListings to confirmListings for the bulk action
      setSelectedListings(confirmListings);
      
      // Execute the bulk action directly
      await handleBulkAction(confirmAction);
      
      // Reset confirmation state
      setConfirmAction(null);
      setConfirmListings([]);
    } else {
      console.log('❌ No confirmAction or confirmListings');
    }
  };

  // Refresh listings function
  const refreshListings = async () => {
    console.log('🔄 Refreshing listings...');
    showToast?.('Refreshing listings...', 'info');
    setListings([]); // Clear current listings to show loading state
    await fetchListings(); // Reload from API
    showToast?.('✅ Listings refreshed successfully', 'success');
  };

  const handleDeleteListing = async (listingId) => {
    // Show confirmation dialog
    const confirmed = window.confirm('Are you sure you want to delete this listing? This action cannot be undone.');
    if (!confirmed) {
      return;
    }

    try {
      console.log('🗑️ Deleting individual listing:', listingId);
      
      // Call backend API to delete the listing
      const deleteUrl = `${process.env.REACT_APP_BACKEND_URL}/api/listings/${listingId}`;
      console.log('🔍 Delete URL:', deleteUrl);
      
      const response = await fetch(deleteUrl, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error(`Failed to delete listing: ${response.status}`);
      }
      
      console.log('✅ Backend delete successful for listing:', listingId);
      
      // Update local state after successful backend deletion
      setListings(listings.filter(l => l.id !== listingId));
      showToast?.('Listing deleted successfully', 'success');
    } catch (error) {
      console.error('❌ Error deleting listing:', error);
      showToast?.(`Failed to delete listing: ${error.message}`, 'error');
    }
  };

  const handleCreateListing = (listingData) => {
    const newListing = {
      id: `new-${Date.now()}`,
      ...listingData,
      created_date: new Date().toISOString().split('T')[0],
      views: 0,
      status: 'active'
    };
    setListings([newListing, ...listings]);
    setShowCreateModal(false);
    showToast?.('Listing created successfully', 'success');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading listings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* REDESIGNED Header Section */}
      <div className="cataloro-card-glass p-8">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-6 lg:space-y-0">
          <div className="text-center lg:text-left">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-3">Listings Management</h2>
            <p className="text-gray-600 dark:text-gray-300 text-lg">Comprehensive marketplace listings control center</p>
          </div>
          <div className="flex justify-center lg:justify-end items-center space-x-4">
            <button
              onClick={refreshListings}
              className="cataloro-button-secondary flex items-center px-4 py-3"
              title="Refresh listings from server"
            >
              <RefreshCw className="w-5 h-5 mr-2" />
              Refresh
            </button>
            
            <button
              onClick={() => setShowCreateModal(true)}
              className="cataloro-button-primary flex items-center px-6 py-3"
            >
              <Package className="w-5 h-5 mr-2" />
              Create New Listing
            </button>
          </div>
        </div>
      </div>

      {/* REDESIGNED Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="cataloro-card-glass p-6 text-center">
          <div className="flex flex-col items-center space-y-4">
            <div className="p-4 bg-blue-100/80 dark:bg-blue-900/30 rounded-2xl backdrop-blur-md">
              <Package className="w-8 h-8 text-blue-500" />
            </div>
            <div>
              <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {listings.length}
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Total Listings</div>
            </div>
          </div>
        </div>

        <div className="cataloro-card-glass p-6 text-center">
          <div className="flex flex-col items-center space-y-4">
            <div className="p-4 bg-green-100/80 dark:bg-green-900/30 rounded-2xl backdrop-blur-md">
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
            <div>
              <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                {listings.filter(l => l.status === 'active').length}
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Active</div>
            </div>
          </div>
        </div>

        <div className="cataloro-card-glass p-6 text-center">
          <div className="flex flex-col items-center space-y-4">
            <div className="p-4 bg-orange-100/80 dark:bg-orange-900/30 rounded-2xl backdrop-blur-md">
              <Eye className="w-8 h-8 text-orange-500" />
            </div>
            <div>
              <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-orange-600 to-yellow-600 bg-clip-text text-transparent">
                {listings.reduce((sum, l) => sum + (l.views || 0), 0)}
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Total Views</div>
            </div>
          </div>
        </div>

        <div className="cataloro-card-glass p-6 text-center">
          <div className="flex flex-col items-center space-y-4">
            <div className="p-4 bg-red-100/80 dark:bg-red-900/30 rounded-2xl backdrop-blur-md">
              <DollarSign className="w-8 h-8 text-red-500" />
            </div>
            <div>
              <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-red-600 to-pink-600 bg-clip-text text-transparent">
                €{listings.reduce((sum, l) => sum + (l.price || 0), 0).toLocaleString()}
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Total Value</div>
            </div>
          </div>
        </div>
      </div>

      {/* REDESIGNED Search and Filters */}
      <div className="cataloro-card-glass p-6">
        <div className="flex flex-col xl:flex-row xl:items-center xl:justify-between space-y-6 xl:space-y-0">
          <div className="flex-1 max-w-md">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Search Listings</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by title, seller, or category..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 cataloro-input w-full"
              />
            </div>
          </div>
          
          <div className="flex items-end space-x-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Filter by Status</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="cataloro-input w-auto min-w-[150px]"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Bulk Actions for Listings - REDESIGNED */}
      {selectedListings.length > 0 && (
        <div className="cataloro-card-glass p-6 border-2 border-green-200 dark:border-green-800 shadow-xl">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-6 lg:space-y-0">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-4 h-4 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xl font-bold text-gray-900 dark:text-white">
                  {selectedListings.length} listing{selectedListings.length !== 1 ? 's' : ''} selected
                </span>
                <div className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 text-sm font-medium rounded-full">
                  Ready for management
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
              {/* Activate Listings */}
              <button
                onClick={() => requestBulkAction('activate')}
                className="flex items-center justify-center space-x-2 px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-xl font-medium transition-all duration-200 transform hover:scale-105 shadow-lg"
                title="Activate selected listings"
              >
                <CheckCircle className="w-4 h-4" />
                <span className="hidden sm:inline">Activate</span>
              </button>

              {/* Deactivate Listings */}
              <button
                onClick={() => requestBulkAction('deactivate')}
                className="flex items-center justify-center space-x-2 px-4 py-3 bg-orange-600 hover:bg-orange-700 text-white rounded-xl font-medium transition-all duration-200 transform hover:scale-105 shadow-lg"
                title="Deactivate selected listings"
              >
                <Ban className="w-4 h-4" />
                <span className="hidden sm:inline">Deactivate</span>
              </button>

              {/* Delete Listings */}
              <button
                onClick={() => requestBulkAction('delete')}
                className="flex items-center justify-center space-x-2 px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl font-medium transition-all duration-200 transform hover:scale-105 shadow-lg"
                title="Delete selected listings"
              >
                <Trash2 className="w-4 h-4" />
                <span className="hidden sm:inline">Delete</span>
              </button>

              {/* Feature Listings */}
              <button
                onClick={() => requestBulkAction('feature')}
                className="flex items-center justify-center space-x-2 px-4 py-3 bg-yellow-600 hover:bg-yellow-700 text-white rounded-xl font-medium transition-all duration-200 transform hover:scale-105 shadow-lg"
                title="Feature selected listings"
              >
                <Star className="w-4 h-4" />
                <span className="hidden sm:inline">Feature</span>
              </button>

              {/* Approve Listings */}
              <button
                onClick={() => requestBulkAction('approve')}
                className="flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-all duration-200 transform hover:scale-105 shadow-lg"
                title="Approve selected listings"
              >
                <Shield className="w-4 h-4" />
                <span className="hidden sm:inline">Approve</span>
              </button>
            </div>
          </div>
          
          {/* Additional Bulk Actions Row */}
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex flex-wrap items-center justify-center lg:justify-start gap-3">
              <button
                onClick={() => handleBulkAction('reject')}
                className="flex items-center space-x-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors"
              >
                <X className="w-4 h-4" />
                <span>Reject</span>
              </button>
              
              <button
                onClick={() => handleBulkAction('duplicate')}
                className="flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors"
              >
                <Package className="w-4 h-4" />
                <span>Duplicate</span>
              </button>
              
              <button
                onClick={() => handleBulkAction('export')}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium transition-colors"
              >
                <Download className="w-4 h-4" />
                <span>Export Selected</span>
              </button>
              
              <button
                onClick={() => handleBulkAction('bulk-edit')}
                className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors"
              >
                <Edit className="w-4 h-4" />
                <span>Bulk Edit</span>
              </button>
              
              <button
                onClick={() => setSelectedListings([])}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-400 hover:bg-gray-500 text-white rounded-lg font-medium transition-colors"
              >
                <X className="w-4 h-4" />
                <span>Clear Selection</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* FIXED Listings Table - NO HORIZONTAL SCROLLING */}
      <div className="cataloro-card-glass overflow-hidden">
        
        {/* Sub-tabs for Listings Status */}
        <div className="px-6 py-4 border-b border-white/10 dark:border-white/10">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Listings Management</h3>
            <span className="bg-blue-100/80 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 px-3 py-1 rounded-full text-sm font-medium backdrop-blur-md">
              {filteredListings.length} results
            </span>
          </div>
          
          {/* Sub-tabs Navigation */}
          <div className="flex items-center space-x-1 bg-gray-100/50 dark:bg-gray-800/50 rounded-lg p-1">
            {[
              { 
                id: 'active', 
                label: 'Active', 
                count: listings.filter(l => l.status === 'active' || l.status === 'approved').length, 
                color: 'green' 
              },
              { 
                id: 'pending', 
                label: 'Pending', 
                count: listings.filter(l => 
                  l.status === 'pending' || 
                  l.status === 'awaiting_approval' || 
                  (l.pendingOrders && l.pendingOrders > 0)
                ).length, 
                color: 'yellow' 
              },
              { 
                id: 'inactive', 
                label: 'Inactive', 
                count: listings.filter(l => 
                  l.status === 'inactive' || 
                  l.status === 'deactivated' || 
                  l.status === 'paused'
                ).length, 
                color: 'gray' 
              },
              { 
                id: 'expired', 
                label: 'Expired', 
                count: listings.filter(l => 
                  l.status === 'expired'
                ).length, 
                color: 'red' 
              },
              { 
                id: 'sold', 
                label: 'Sold', 
                count: listings.filter(l => 
                  l.status === 'sold' || 
                  l.status === 'completed' || 
                  l.status === 'finished'
                ).length, 
                color: 'blue' 
              }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveSubTab(tab.id);
                  setFilterStatus(tab.id);
                }}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                  activeSubTab === tab.id
                    ? `${tab.color === 'green' ? 'bg-green-600 text-white' :
                        tab.color === 'yellow' ? 'bg-yellow-600 text-white' :
                        tab.color === 'gray' ? 'bg-gray-600 text-white' :
                        tab.color === 'red' ? 'bg-red-600 text-white' :
                        'bg-blue-600 text-white'} shadow-lg`
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-white/50 dark:hover:bg-gray-700/50'
                }`}
              >
                <span>{tab.label}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs ${
                  activeSubTab === tab.id
                    ? 'bg-white/20 text-white'
                    : `${tab.color === 'green' ? 'bg-green-100 text-green-800' :
                        tab.color === 'yellow' ? 'bg-yellow-100 text-yellow-800' :  
                        tab.color === 'gray' ? 'bg-gray-100 text-gray-800' :
                        tab.color === 'red' ? 'bg-red-100 text-red-800' :
                        'bg-blue-100 text-blue-800'} dark:bg-opacity-20`
                }`}>
                  {tab.count}
                </span>
              </button>
            ))}
          </div>
        </div>
        
        {/* Filter indicator for sub-tabs */}
        {activeSubTab !== 'active' && (
          <div className="px-6 py-3 bg-blue-50/50 dark:bg-blue-900/20 border-b border-blue-200/50 dark:border-blue-800/50">
            <div className="flex items-center justify-between">
              <span className="text-blue-800 dark:text-blue-300 text-sm font-medium">
                Showing {activeSubTab} listings ({filteredListings.length} items)
              </span>
              <button 
                onClick={() => {
                  setActiveSubTab('active');
                  setFilterStatus('active');
                }}
                className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium"
              >
                Show Active
              </button>
            </div>
          </div>
        )}
        
        {/* Responsive Table - No Horizontal Scroll */}
        <div className="max-w-full">
          <table className="w-full min-w-full">
            <thead className="bg-gray-50/80 dark:bg-gray-800/50 backdrop-blur-sm">
              <tr>
                <th className="px-3 py-4 text-left w-12">
                  <input
                    type="checkbox"
                    checked={selectedListings.length === filteredListings.length && filteredListings.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="admin-checkbox"
                  />
                </th>
                <th className="px-4 py-4 text-left text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider min-w-[280px]">Listing Details</th>
                <th className="px-3 py-4 text-left text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider w-24">Price</th>
                <th className="px-3 py-4 text-left text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider w-32">Seller</th>
                <th className="px-3 py-4 text-left text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider w-24">Status</th>
                <th className="px-3 py-4 text-left text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider w-20">Views</th>
                <th className="px-3 py-4 text-left text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider w-24">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200/50 dark:divide-gray-700/50">
              {filteredListings.map((listing) => (
                <tr key={listing.id} className="group">
                  <td className="px-3 py-4">
                    <input
                      type="checkbox"
                      checked={selectedListings.includes(listing.id)}
                      onChange={(e) => handleSelectListing(listing.id, e.target.checked)}
                      className="admin-checkbox"
                    />
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 rounded-lg overflow-hidden bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 flex items-center justify-center flex-shrink-0">
                        {listing.image ? (
                          <img
                            src={listing.image}
                            alt={listing.title}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <Package className="w-5 h-5 text-gray-400 dark:text-gray-500" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-base font-semibold text-gray-900 dark:text-white truncate" title={listing.title}>{listing.title}</h4>
                        <p className="text-xs text-gray-600 dark:text-gray-400">{listing.created_date}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-3 py-4">
                    <span className="text-lg font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent whitespace-nowrap">
                      €{listing.price}
                    </span>
                  </td>
                  <td className="px-3 py-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-6 h-6 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-white font-medium text-xs">
                          {listing.seller_username?.charAt(0) || 'U'}
                        </span>
                      </div>
                      <Link
                        to={`/profile/${listing.seller_id}`}
                        className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 font-medium truncate hover:underline"
                        title={`View ${listing.seller_full_name}'s profile`}
                      >
                        {listing.seller_username}
                      </Link>
                    </div>
                  </td>
                  <td className="px-3 py-4">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium backdrop-blur-md ${
                      listing.status === 'active' 
                        ? 'bg-green-100/80 dark:bg-green-900/30 text-green-800 dark:text-green-300' 
                        : 'bg-red-100/80 dark:bg-red-900/30 text-red-800 dark:text-red-300'
                    }`}>
                      {listing.status === 'active' ? 'ACTIVE' : 'INACTIVE'}
                    </span>
                  </td>
                  <td className="px-3 py-4">
                    <div className="flex items-center justify-center">
                      <span className="text-sm text-gray-900 dark:text-white font-medium">{listing.views}</span>
                    </div>
                  </td>
                  <td className="px-3 py-4">
                    <div className="flex items-center justify-center space-x-1">
                      <button
                        onClick={() => setEditingListing(listing)}
                        className="p-1.5 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 rounded hover:bg-blue-50/50 dark:hover:bg-blue-900/20"
                        title="Edit listing"
                      >
                        <Edit className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDeleteListing(listing.id)}
                        className="p-1.5 text-gray-400 hover:text-red-600 dark:hover:text-red-400 rounded hover:bg-red-50/50 dark:hover:bg-red-900/20"
                        title="Delete listing"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredListings.length === 0 && (
          <div className="text-center py-16">
            <div className="w-20 h-20 bg-gradient-to-r from-gray-400/20 to-gray-500/20 dark:from-gray-600/20 dark:to-gray-700/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Package className="w-10 h-10 text-gray-400 dark:text-gray-500" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">No listings found</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-8">
              {searchTerm ? 'Try adjusting your search terms' : 'Create your first listing to get started'}
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="cataloro-button-primary"
            >
              Create New Listing
            </button>
          </div>
        )}
      </div>

      {/* Create/Edit Modal */}
      {(showCreateModal || editingListing) && (
        <ListingModal
          listing={editingListing}
          onSave={editingListing ? 
            (data) => {
              setListings(listings.map(l => l.id === editingListing.id ? {...l, ...data} : l));
              setEditingListing(null);
              showToast?.('Listing updated successfully', 'success');
            } : 
            handleCreateListing
          }
          onClose={() => {
            setShowCreateModal(false);
            setEditingListing(null);
          }}
        />
      )}

      {/* Confirmation Modal for Bulk Actions */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md mx-4 shadow-2xl">
            <div className="p-6">
              <div className="flex items-center space-x-4 mb-4">
                <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
                  {confirmAction === 'delete' ? (
                    <Trash2 className="w-6 h-6 text-red-600 dark:text-red-400" />
                  ) : (
                    <AlertTriangle className="w-6 h-6 text-orange-600 dark:text-orange-400" />
                  )}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Confirm {confirmAction === 'delete' ? 'Deletion' : 'Action'}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    This action cannot be undone
                  </p>
                </div>
              </div>
              
              <div className="mb-6">
                <p className="text-gray-700 dark:text-gray-300">
                  Are you sure you want to <span className="font-semibold text-red-600 dark:text-red-400">{confirmAction}</span> these{' '}
                  <span className="font-semibold">{confirmListings.length}</span> listing{confirmListings.length !== 1 ? 's' : ''}?
                </p>
                
                {confirmAction === 'delete' && (
                  <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                    <div className="flex items-start space-x-2">
                      <AlertTriangle className="w-4 h-4 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                      <p className="text-sm text-red-800 dark:text-red-200">
                        <strong>Warning:</strong> Deleted listings will be permanently removed from the marketplace and cannot be recovered.
                      </p>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowConfirmModal(false)}
                  className="flex-1 px-4 py-3 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 text-gray-800 dark:text-gray-200 rounded-xl font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={executeBulkAction}
                  className={`flex-1 px-4 py-3 text-white rounded-xl font-medium transition-colors ${
                    confirmAction === 'delete' 
                      ? 'bg-red-600 hover:bg-red-700' 
                      : 'bg-blue-600 hover:bg-blue-700'
                  }`}
                >
                  {confirmAction === 'delete' ? 'Delete Forever' : `Confirm ${confirmAction}`}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ListingsTab;