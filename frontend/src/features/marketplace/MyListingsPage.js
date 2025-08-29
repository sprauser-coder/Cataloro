/**
 * CATALORO - My Listings Page
 * Tile pattern with all user's created listings
 */

import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Eye, MoreHorizontal } from 'lucide-react';
import { marketplaceService } from '../../services/marketplaceService';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function MyListingsPage() {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const { showToast } = useNotifications();

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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">My Listings</h1>
            <p className="text-gray-600">Manage your marketplace listings</p>
          </div>
          <button className="cataloro-button-primary flex items-center">
            <Plus className="w-5 h-5 mr-2" />
            Create New Listing
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="kpi-card">
          <div className="kpi-value text-blue-600">{listings.length}</div>
          <div className="kpi-label">Total Listings</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-value text-green-600">{listings.filter(l => l.status === 'active').length}</div>
          <div className="kpi-label">Active</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-value text-orange-600">{listings.filter(l => l.status === 'draft').length}</div>
          <div className="kpi-label">Drafts</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-value text-gray-600">{listings.filter(l => l.status === 'sold').length}</div>
          <div className="kpi-label">Sold</div>
        </div>
      </div>

      {/* Listings Grid */}
      {listings.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Plus className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No listings yet</h3>
          <p className="text-gray-600 mb-6">Create your first listing to start selling</p>
          <button className="cataloro-button-primary">
            Create Your First Listing
          </button>
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

// My Listing Card Component
function MyListingCard({ listing, onDelete }) {
  const [showMenu, setShowMenu] = useState(false);

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'sold':
        return 'bg-gray-100 text-gray-800';
      case 'draft':
        return 'bg-orange-100 text-orange-800';
      case 'expired':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
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
        
        {/* Status Badge */}
        <span className={`absolute top-3 left-3 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(listing.status)}`}>
          {listing.status.toUpperCase()}
        </span>

        {/* Action Menu */}
        <div className="absolute top-3 right-3">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-2 bg-white bg-opacity-90 rounded-full hover:bg-opacity-100 transition-all duration-200"
          >
            <MoreHorizontal className="w-4 h-4 text-gray-600" />
          </button>

          {showMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-10">
              <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center">
                <Eye className="w-4 h-4 mr-3" />
                View Details
              </button>
              <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center">
                <Edit className="w-4 h-4 mr-3" />
                Edit Listing
              </button>
              <button
                onClick={() => {
                  onDelete(listing.id);
                  setShowMenu(false);
                }}
                className="w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-red-50 flex items-center"
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
        <h3 className="listing-title">{listing.title}</h3>
        <p className="listing-price">${listing.price.toFixed(2)}</p>
        <p className="listing-description">{listing.description}</p>
        
        <div className="flex items-center justify-between mt-4">
          <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
            {listing.category}
          </span>
          <span className="text-sm text-gray-500">
            {new Date(listing.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>
    </div>
  );
}

export default MyListingsPage;