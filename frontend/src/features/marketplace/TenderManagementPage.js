/**
 * CATALORO - Tender Management Page
 * Allows sellers to view and manage tender offers for their listings
 * Also includes Listings Management functionality (exact duplicate of My Listings)
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  DollarSign, 
  Clock, 
  Users, 
  CheckCircle, 
  XCircle,
  MessageCircle,
  Eye,
  TrendingUp,
  RefreshCw,
  Plus,
  Edit,
  Trash2,
  MoreHorizontal,
  FileText,
  Settings
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { marketplaceService } from '../../services/marketplaceService';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function TenderManagementPage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Tab management
  const [activeTab, setActiveTab] = useState('tenders');

  // Tender Management State
  const [tendersOverview, setTendersOverview] = useState([]);
  const [tendersLoading, setTendersLoading] = useState(true);
  const [selectedListing, setSelectedListing] = useState(null);
  const [acceptingTender, setAcceptingTender] = useState(null);
  const [rejectingTender, setRejectingTender] = useState(null);

  // Listings Management State (exact duplicate of MyListingsPage)
  const urlFilter = searchParams.get('filter');
  const [listings, setListings] = useState([]);
  const [listingsLoading, setListingsLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState(urlFilter || 'all');

  useEffect(() => {
    if (user) {
      fetchTendersOverview();
      fetchMyListings();
    }
  }, [user]);

  // Update URL parameters when activeFilter changes (for Listings Management)
  useEffect(() => {
    if (activeTab === 'listings') {
      const currentParams = new URLSearchParams(window.location.search);
      if (activeFilter !== 'all') {
        currentParams.set('filter', activeFilter);
      } else {
        currentParams.delete('filter');
      }
      const newUrl = `${window.location.pathname}${currentParams.toString() ? '?' + currentParams.toString() : ''}`;
      window.history.replaceState({}, '', newUrl);
    }
  }, [activeFilter, activeTab]);

  // Sync activeFilter with URL parameters (for Listings Management)
  useEffect(() => {
    const urlFilter = searchParams.get('filter');
    if (urlFilter && urlFilter !== activeFilter) {
      setActiveFilter(urlFilter);
    }
  }, [searchParams]);

  const fetchTendersOverview = async () => {
    if (!user) return;
    
    try {
      setTendersLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tenders/seller/${user.id}/overview`);
      
      if (response.ok) {
        const data = await response.json();
        setTendersOverview(data);
      } else {
        showToast('Failed to load tender overview', 'error');
      }
    } catch (error) {
      console.error('Failed to fetch tenders overview:', error);
      showToast('Error loading tender data', 'error');
    } finally {
      setTendersLoading(false);
    }
  };

  // Listings Management Functions (exact duplicate from MyListingsPage)
  const fetchMyListings = async () => {
    if (!user?.id) return;
    
    try {
      setListingsLoading(true);
      const data = await marketplaceService.getMyListings(user.id);
      setListings(data);
    } catch (error) {
      showToast('Failed to load your listings', 'error');
      console.error('Failed to fetch listings:', error);
    } finally {
      setListingsLoading(false);
    }
  };

  const handleDeleteListing = async (listingId) => {
    if (!window.confirm('Are you sure you want to delete this listing?')) {
      return;
    }

    try {
      await marketplaceService.deleteListing(listingId);
      setListings(listings.filter(listing => listing.id !== listingId));
      showToast('Listing deleted successfully', 'success');
    } catch (error) {
      console.error('Error deleting listing:', error);
      showToast('Failed to delete listing', 'error');
    }
  };

  // Handle tile clicks for filtering (for Listings Management)
  const handleTileClick = (filter) => {
    setActiveFilter(filter);
  };

  // Handle create new listing (for Listings Management)
  const handleCreateListing = () => {
    navigate('/create-listing');
  };

  // Filter listings based on active filter (for Listings Management)
  const getFilteredListings = () => {
    switch (activeFilter) {
      case 'active':
        return listings.filter(l => l.status === 'active');
      case 'drafts':
        return listings.filter(l => l.status === 'draft' || l.is_draft);
      case 'closed':
        return listings.filter(l => l.status === 'sold' || l.status === 'closed');
      default:
        return listings;
    }
  };

  const handleAcceptTender = async (tenderId, listingTitle, offerAmount) => {
    if (!user) return;
    
    const confirmed = window.confirm(
      `Accept tender offer of €${offerAmount.toFixed(2)} for "${listingTitle}"?\n\nThis will:\n- Accept this tender\n- Reject all other tenders for this listing\n- Mark the listing as SOLD\n- Send notifications to all bidders\n- Create a message thread with the winning bidder`
    );
    
    if (!confirmed) return;
    
    try {
      setAcceptingTender(tenderId);
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tenders/${tenderId}/accept`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          seller_id: user.id
        })
      });

      if (response.ok) {
        showToast(`Tender offer of €${offerAmount.toFixed(2)} accepted!`, 'success');
        fetchTendersOverview(); // Refresh data
      } else {
        const errorData = await response.json();
        showToast(errorData.detail || 'Failed to accept tender', 'error');
      }
    } catch (error) {
      console.error('Error accepting tender:', error);
      showToast('Error accepting tender. Please try again.', 'error');
    } finally {
      setAcceptingTender(null);
    }
  };

  const handleRejectTender = async (tenderId, listingTitle, offerAmount) => {
    if (!user) return;
    
    const confirmed = window.confirm(
      `Reject tender offer of €${offerAmount.toFixed(2)} for "${listingTitle}"?\n\nThis will send a rejection notification to the bidder.`
    );
    
    if (!confirmed) return;
    
    try {
      setRejectingTender(tenderId);
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tenders/${tenderId}/reject`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          seller_id: user.id
        })
      });

      if (response.ok) {
        showToast('Tender offer rejected', 'info');
        fetchTendersOverview(); // Refresh data
      } else {
        const errorData = await response.json();
        showToast(errorData.detail || 'Failed to reject tender', 'error');
      }
    } catch (error) {
      console.error('Error rejecting tender:', error);
      showToast('Error rejecting tender. Please try again.', 'error');
    } finally {
      setRejectingTender(null);
    }
  };

  if (!user) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Please Login</h2>
        <p className="text-gray-600 dark:text-gray-400">You need to be logged in to manage tenders and listings.</p>
      </div>
    );
  }

  const totalTenders = tendersOverview.reduce((sum, item) => sum + item.tender_count, 0);
  const totalHighestBids = tendersOverview.reduce((sum, item) => sum + (item.highest_offer || 0), 0);
  const filteredListings = getFilteredListings();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Management Center</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage your tenders and listings
          </p>
        </div>
        
        <div className="mt-4 lg:mt-0 flex items-center space-x-3">
          {activeTab === 'tenders' ? (
            <button
              onClick={fetchTendersOverview}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
          ) : (
            <button 
              onClick={handleCreateListing}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Create New Listing</span>
            </button>
          )}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('tenders')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'tenders'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4" />
              <span>Tender Management</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('listings')}
            className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
              activeTab === 'listings'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Settings className="w-4 h-4" />
              <span>Listings Management</span>
            </div>
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'tenders' && (
        <TenderManagementTab
          tendersOverview={tendersOverview}
          tendersLoading={tendersLoading}
          selectedListing={selectedListing}
          setSelectedListing={setSelectedListing}
          acceptingTender={acceptingTender}
          rejectingTender={rejectingTender}
          handleAcceptTender={handleAcceptTender}
          handleRejectTender={handleRejectTender}
          totalTenders={totalTenders}
          totalHighestBids={totalHighestBids}
        />
      )}

      {activeTab === 'listings' && (
        <ListingsManagementTab
          listings={filteredListings}
          allListings={listings}
          listingsLoading={listingsLoading}
          activeFilter={activeFilter}
          handleTileClick={handleTileClick}
          handleCreateListing={handleCreateListing}
          handleDeleteListing={handleDeleteListing}
        />
      )}
    </div>
  );
}

// Tender Management Tab Component
function TenderManagementTab({
  tendersOverview,
  tendersLoading,
  selectedListing,
  setSelectedListing,
  acceptingTender,
  rejectingTender,
  handleAcceptTender,
  handleRejectTender,
  totalTenders,
  totalHighestBids
}) {

  if (tendersLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading tender overview...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Users className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Listings</h3>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{tendersOverview.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Tenders</h3>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalTenders}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
              <DollarSign className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Bid Value</h3>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">€{totalHighestBids.toFixed(2)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Listings with Tenders */}
      {tendersOverview.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="w-24 h-24 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-6">
            <DollarSign className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No Active Listings</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            You don't have any active listings receiving tender offers.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {tendersOverview.map((item) => (
            <div key={item.listing.id} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
              {/* Listing Header */}
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-start space-x-4">
                  <img
                    src={item.listing.images?.[0] || '/api/placeholder/400/300'}
                    alt={item.listing.title}
                    className="w-20 h-20 object-cover rounded-lg"
                  />
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
                      {item.listing.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      Starting Price: €{item.listing.price.toFixed(2)}
                    </p>
                    <div className="flex items-center space-x-4 mt-2">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                        <Users className="w-3 h-3 mr-1" />
                        {item.tender_count} tender{item.tender_count !== 1 ? 's' : ''}
                      </span>
                      {item.highest_offer > 0 && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">
                          <TrendingUp className="w-3 h-3 mr-1" />
                          Highest: €{item.highest_offer.toFixed(2)}
                        </span>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedListing(selectedListing === item.listing.id ? null : item.listing.id)}
                    className="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors flex items-center space-x-2"
                  >
                    <Eye className="w-4 h-4" />
                    <span>{selectedListing === item.listing.id ? 'Hide' : 'View'} Tenders</span>
                  </button>
                </div>
              </div>

              {/* Tenders List */}
              {selectedListing === item.listing.id && (
                <div className="p-6">
                  {item.tenders.length === 0 ? (
                    <p className="text-gray-600 dark:text-gray-400 text-center py-4">
                      No active tenders for this listing.
                    </p>
                  ) : (
                    <div className="space-y-4">
                      {item.tenders.map((tender, index) => (
                        <div key={tender.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                          <div className="flex items-center space-x-4">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                              index === 0 ? 'bg-yellow-500' : 'bg-gray-400'
                            }`}>
                              #{index + 1}
                            </div>
                            <div>
                              <p className="font-semibold text-gray-900 dark:text-white">
                                €{tender.offer_amount.toFixed(2)}
                              </p>
                              <p className="text-sm text-gray-600 dark:text-gray-400">
                                by {tender.buyer.full_name || tender.buyer.username}
                              </p>
                              <p className="text-xs text-gray-500 dark:text-gray-500">
                                <Clock className="w-3 h-3 inline mr-1" />
                                {new Date(tender.created_at).toLocaleDateString()} at {new Date(tender.created_at).toLocaleTimeString()}
                              </p>
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => handleAcceptTender(tender.id, item.listing.title, tender.offer_amount)}
                              disabled={acceptingTender === tender.id}
                              className="px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white rounded-lg font-medium transition-colors flex items-center space-x-2"
                            >
                              {acceptingTender === tender.id ? (
                                <>
                                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                  <span>Accepting...</span>
                                </>
                              ) : (
                                <>
                                  <CheckCircle className="w-4 h-4" />
                                  <span>Accept</span>
                                </>
                              )}
                            </button>
                            
                            <button
                              onClick={() => handleRejectTender(tender.id, item.listing.title, tender.offer_amount)}
                              disabled={rejectingTender === tender.id}
                              className="px-3 py-2 bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white rounded-lg font-medium transition-colors flex items-center space-x-2"
                            >
                              {rejectingTender === tender.id ? (
                                <>
                                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                  <span>Rejecting...</span>
                                </>
                              ) : (
                                <>
                                  <XCircle className="w-4 h-4" />
                                  <span>Reject</span>
                                </>
                              )}
                            </button>
                            
                            <button
                              className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center space-x-2"
                              title="Message bidder"
                            >
                              <MessageCircle className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Listings Management Tab Component (exact duplicate of MyListingsPage functionality)
function ListingsManagementTab({
  listings,
  allListings,
  listingsLoading,
  activeFilter,
  handleTileClick,
  handleCreateListing,
  handleDeleteListing
}) {
  // Import icons for this component
  const { Plus } = require('lucide-react');
  if (listingsLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      {/* Stats Cards - CLICKABLE & REDUCED MARGIN */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-4">
        <button
          onClick={() => handleTileClick('all')}
          className={`cataloro-card-glass text-left transition-all duration-200 hover:scale-105 ${
            activeFilter === 'all' ? 'ring-2 ring-blue-500 bg-blue-50/20 dark:bg-blue-900/20' : ''
          }`}
        >
          <div className="p-6 text-center">
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">{allListings.length}</div>
            <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Total Listings</div>
          </div>
        </button>
        <button
          onClick={() => handleTileClick('active')}
          className={`cataloro-card-glass text-left transition-all duration-200 hover:scale-105 ${
            activeFilter === 'active' ? 'ring-2 ring-green-500 bg-green-50/20 dark:bg-green-900/20' : ''
          }`}
        >
          <div className="p-6 text-center">
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">{allListings.filter(l => l.status === 'active').length}</div>
            <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Active</div>
          </div>
        </button>
        <button
          onClick={() => handleTileClick('closed')}
          className={`cataloro-card-glass text-left transition-all duration-200 hover:scale-105 ${
            activeFilter === 'closed' ? 'ring-2 ring-red-500 bg-red-50/20 dark:bg-red-900/20' : ''
          }`}
        >
          <div className="p-6 text-center">
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-red-600 to-pink-600 bg-clip-text text-transparent">{allListings.filter(l => l.status === 'sold' || l.status === 'closed').length}</div>
            <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Closed</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Sold & completed</div>
          </div>
        </button>
        <button
          onClick={() => handleTileClick('drafts')}
          className={`cataloro-card-glass text-left transition-all duration-200 hover:scale-105 ${
            activeFilter === 'drafts' ? 'ring-2 ring-orange-500 bg-orange-50/20 dark:bg-orange-900/20' : ''
          }`}
        >
          <div className="p-6 text-center">
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-orange-600 to-yellow-600 bg-clip-text text-transparent">{allListings.filter(l => l.status === 'draft' || l.is_draft).length}</div>
            <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Drafts</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Finish & publish later</div>
          </div>
        </button>
      </div>

      {/* Filter Indicator */}
      {activeFilter !== 'all' && (
        <div className="mb-4 flex items-center justify-between bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
          <span className="text-blue-800 dark:text-blue-300 font-medium">
            Showing {activeFilter} listings ({listings.length} items)
          </span>
          <button 
            onClick={() => handleTileClick('all')}
            className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium"
          >
            Show All
          </button>
        </div>
      )}

      {/* Listings Grid */}
      {listings.length === 0 ? (
        <div className="text-center py-12">
          <div className="cataloro-card-glass p-12">
            <div className="w-24 h-24 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <Plus className="w-12 h-12 text-gray-600 dark:text-gray-300" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">No listings yet</h3>
            <p className="text-gray-600 dark:text-gray-300 mb-8 max-w-md mx-auto">Create your first listing to start selling on our modern marketplace</p>
            <button 
              onClick={handleCreateListing}
              className="cataloro-button-primary"
            >
              Create Your First Listing
            </button>
          </div>
        </div>
      ) : (
        <div className="listings-grid">
          {listings.map((listing) => (
            <MyListingCard
              key={listing.id}
              listing={listing}
              onDelete={handleDeleteListing}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// My Listing Card Component (exact duplicate from MyListingsPage)
function MyListingCard({ listing, onDelete }) {
  const [showMenu, setShowMenu] = useState(false);
  
  // Import icons for this component
  const { Edit, Trash2, MoreHorizontal, Eye } = require('lucide-react');
  const { Link } = require('react-router-dom');

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showMenu && !event.target.closest('.listing-menu-container')) {
        setShowMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showMenu]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300';
      case 'sold':
        return 'bg-gray-100 dark:bg-gray-700/50 text-gray-800 dark:text-gray-300';
      case 'draft':
        return 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300';
      case 'expired':
        return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300';
      default:
        return 'bg-gray-100 dark:bg-gray-700/50 text-gray-800 dark:text-gray-300';
    }
  };

  return (
    <div className="listing-tile">
      {/* Image */}
      <div className="relative">
        <img
          src={listing.images?.[0] || '/api/placeholder/400/300'}
          alt={listing.title}
          className="listing-image"
        />
        
        {/* Status Badge - Enhanced for Drafts */}
        <span className={`absolute top-3 left-3 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(listing.status || (listing.is_draft ? 'draft' : 'active'))}`}>
          {(listing.status || (listing.is_draft ? 'DRAFT' : 'ACTIVE')).toUpperCase()}
        </span>
        
        {/* Draft Indicator */}
        {(listing.is_draft || listing.status === 'draft') && (
          <div className="absolute top-3 right-16 bg-yellow-500 text-white px-2 py-1 rounded-full text-xs font-bold animate-pulse">
            DRAFT
          </div>
        )}

        {/* Action Menu */}
        <div className="absolute top-3 right-3 listing-menu-container">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowMenu(!showMenu);
            }}
            className="p-2 bg-white/90 dark:bg-gray-800/90 backdrop-blur-md rounded-full hover:bg-white dark:hover:bg-gray-800 transition-all duration-200 shadow-lg"
          >
            <MoreHorizontal className="w-4 h-4 text-gray-600 dark:text-gray-300" />
          </button>

          {showMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 py-2 z-50 backdrop-blur-xl">
              {/* Draft-specific actions */}
              {(listing.is_draft || listing.status === 'draft') && (
                <>
                  <Link
                    to={`/edit-listing/${listing.id}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowMenu(false);
                    }}
                    className="w-full text-left px-4 py-3 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 flex items-center transition-colors duration-200"
                  >
                    <Edit className="w-4 h-4 mr-3" />
                    Finish & Publish
                  </Link>
                  <div className="border-t border-gray-200 dark:border-gray-600 my-1"></div>
                </>
              )}
              
              {/* Regular actions for non-draft listings */}
              {!(listing.is_draft || listing.status === 'draft') && (
                <Link
                  to={`/product/${listing.id}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-4 py-3 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center transition-colors duration-200"
                >
                  <Eye className="w-4 h-4 mr-3" />
                  View Details
                </Link>
              )}
              
              <Link
                to={`/edit-listing/${listing.id}`}
                onClick={(e) => {
                  e.stopPropagation();
                  setShowMenu(false);
                }}
                className="w-full text-left px-4 py-3 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center transition-colors duration-200"
              >
                <Edit className="w-4 h-4 mr-3" />
                {(listing.is_draft || listing.status === 'draft') ? 'Continue Editing' : 'Edit Listing'}
              </Link>
              <div className="border-t border-gray-200 dark:border-gray-600 my-1"></div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(listing.id);
                  setShowMenu(false);
                }}
                className="w-full text-left px-4 py-3 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center transition-colors duration-200"
              >
                <Trash2 className="w-4 h-4 mr-3" />
                Delete Listing
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="listing-content">
        <h3 className="listing-title text-gray-900 dark:text-white">{listing.title}</h3>
        <p className="listing-price">€{listing.price.toFixed(2)}</p>
        <p className="listing-description text-gray-600 dark:text-gray-300">{listing.description}</p>
        
        <div className="flex items-center justify-between mt-4">
          <span className="inline-block bg-blue-100/80 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-xs px-3 py-1 rounded-full font-medium backdrop-blur-md">
            {listing.category}
          </span>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {new Date(listing.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>
    </div>
  );
}

export default TenderManagementPage;