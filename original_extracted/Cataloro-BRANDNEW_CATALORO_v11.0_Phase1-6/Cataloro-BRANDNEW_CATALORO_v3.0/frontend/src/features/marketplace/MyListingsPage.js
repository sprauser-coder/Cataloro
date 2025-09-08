/**
 * CATALORO - My Listings Page
 * Tile pattern with all user's created listings
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Plus, Edit, Trash2, Eye, MoreHorizontal } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { marketplaceService } from '../../services/marketplaceService';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function MyListingsPage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const [searchParams] = useSearchParams();
  
  // Get filter from URL parameters
  const urlFilter = searchParams.get('filter');
  
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState(urlFilter || 'all'); // Use URL filter if available
  const navigate = useNavigate();

  // Update URL parameters when activeFilter changes
  useEffect(() => {
    const currentParams = new URLSearchParams(window.location.search);
    if (activeFilter !== 'all') {
      currentParams.set('filter', activeFilter);
    } else {
      currentParams.delete('filter');
    }
    const newUrl = `${window.location.pathname}${currentParams.toString() ? '?' + currentParams.toString() : ''}`;
    window.history.replaceState({}, '', newUrl);
  }, [activeFilter]);

  // Sync activeFilter with URL parameters
  useEffect(() => {
    const urlFilter = searchParams.get('filter');
    if (urlFilter && urlFilter !== activeFilter) {
      setActiveFilter(urlFilter);
    }
  }, [searchParams]);

  useEffect(() => {
    if (user?.id) {
      fetchMyListings();
    }
  }, [user?.id]);

  const fetchMyListings = async () => {
    try {
      setLoading(true);
      const data = await marketplaceService.getMyListings(user.id);
      setListings(data);
    } catch (error) {
      showToast('Failed to load your listings', 'error');
      console.error('Failed to fetch listings:', error);
    } finally {
      setLoading(false);
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
      showToast('Failed to delete listing', 'error');
    }
  };

  // Handle tile clicks for filtering
  const handleTileClick = (filter) => {
    setActiveFilter(filter);
  };

  // Handle create new listing
  const handleCreateListing = () => {
    navigate('/create-listing');
  };

  // Filter listings based on active filter
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

  const filteredListings = getFilteredListings();

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">My Listings</h1>
            <p className="text-gray-600 dark:text-gray-300">Manage your marketplace listings</p>
          </div>
          <button 
            onClick={handleCreateListing}
            className="cataloro-button-primary flex items-center"
          >
            <Plus className="w-5 h-5 mr-2" />
            Create New Listing
          </button>
        </div>
      </div>

      {/* Stats Cards - CLICKABLE & REDUCED MARGIN */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-4">
        <button
          onClick={() => handleTileClick('all')}
          className={`cataloro-card-glass text-left transition-all duration-200 hover:scale-105 ${
            activeFilter === 'all' ? 'ring-2 ring-blue-500 bg-blue-50/20 dark:bg-blue-900/20' : ''
          }`}
        >
          <div className="p-6 text-center">
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">{listings.length}</div>
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
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">{listings.filter(l => l.status === 'active').length}</div>
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
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-red-600 to-pink-600 bg-clip-text text-transparent">{listings.filter(l => l.status === 'sold' || l.status === 'closed').length}</div>
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
            <div className="text-3xl font-bold mb-2 bg-gradient-to-r from-orange-600 to-yellow-600 bg-clip-text text-transparent">{listings.filter(l => l.status === 'draft' || l.is_draft).length}</div>
            <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wide">Drafts</div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Finish & publish later</div>
          </div>
        </button>
      </div>

      {/* Filter Indicator */}
      {activeFilter !== 'all' && (
        <div className="mb-4 flex items-center justify-between bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
          <span className="text-blue-800 dark:text-blue-300 font-medium">
            Showing {activeFilter} listings ({filteredListings.length} items)
          </span>
          <button 
            onClick={() => setActiveFilter('all')}
            className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium"
          >
            Show All
          </button>
        </div>
      )}

      {/* Listings Grid */}
      {filteredListings.length === 0 ? (
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
          {filteredListings.map((listing) => (
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

// My Listing Card Component
function MyListingCard({ listing, onDelete }) {
  const [showMenu, setShowMenu] = useState(false);

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

export default MyListingsPage;