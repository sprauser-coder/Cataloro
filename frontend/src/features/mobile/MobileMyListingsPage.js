/**
 * CATALORO - Mobile My Listings Page
 * Mobile-optimized listings management with compact cards and touch-friendly interface
 */

import React, { useState, useEffect } from 'react';
import { ArrowLeft, Plus, Edit, Trash2, Eye, MoreVertical, Package, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { marketplaceService } from '../../services/marketplaceService';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function MobileMyListingsPage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('all');
  const navigate = useNavigate();

  useEffect(() => {
    if (user?.id) {
      fetchMyListings();
    }
  }, [user]);

  const fetchMyListings = async () => {
    try {
      setLoading(true);
      const data = await marketplaceService.getMyListings(user.id);
      setListings(data);
    } catch (error) {
      console.error('Error fetching listings:', error);
      showToast('Failed to load listings', 'error');
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
      console.error('Error deleting listing:', error);
      showToast('Failed to delete listing', 'error');
    }
  };

  const filteredListings = listings.filter(listing => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'active') return listing.status === 'active';
    if (activeFilter === 'sold') return listing.status === 'sold';
    if (activeFilter === 'expired') return listing.status === 'expired';
    return true;
  });

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'sold':
        return <Package className="w-4 h-4 text-blue-500" />;
      case 'expired':
        return <Clock className="w-4 h-4 text-orange-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'sold':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
      case 'expired':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        {/* Mobile Header */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
          <div className="flex items-center">
            <button
              onClick={() => navigate(-1)}
              className="mr-3 p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">My Listings</h1>
          </div>
        </div>

        <div className="flex items-center justify-center h-64">
          <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
      {/* Mobile Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <button
              onClick={() => navigate(-1)}
              className="mr-3 p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">My Listings</h1>
          </div>
          <Link
            to="/create-listing"
            className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
          </Link>
        </div>

        {/* Filter Tabs */}
        <div className="flex space-x-1 mt-3 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
          {[
            { key: 'all', label: 'All' },
            { key: 'active', label: 'Active' },
            { key: 'sold', label: 'Sold' },
            { key: 'expired', label: 'Expired' }
          ].map((filter) => (
            <button
              key={filter.key}
              onClick={() => setActiveFilter(filter.key)}
              className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors ${
                activeFilter === filter.key
                  ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              {filter.label}
            </button>
          ))}
        </div>
      </div>

      {/* Listings Grid */}
      <div className="p-4">
        {filteredListings.length === 0 ? (
          <div className="text-center py-12">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              No listings found
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {activeFilter === 'all' 
                ? "You haven't created any listings yet"
                : `No ${activeFilter} listings found`
              }
            </p>
            <Link
              to="/create-listing"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center"
            >
              <Plus className="w-5 h-5 mr-2" />
              Create Your First Listing
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredListings.map((listing) => (
              <MobileListingCard
                key={listing.id}
                listing={listing}
                onDelete={handleDeleteListing}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Mobile-optimized listing card component
function MobileListingCard({ listing, onDelete }) {
  const [showActions, setShowActions] = useState(false);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'sold':
        return <Package className="w-4 h-4 text-blue-500" />;
      case 'expired':
        return <Clock className="w-4 h-4 text-orange-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'sold':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
      case 'expired':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
      <div className="flex">
        {/* Image */}
        <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 flex-shrink-0 flex items-center justify-center">
          {listing.images && listing.images.length > 0 ? (
            <img
              src={listing.images[0]}
              alt={listing.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <Package className="w-8 h-8 text-white" />
          )}
        </div>

        {/* Content */}
        <div className="flex-1 p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                {listing.title}
              </h3>
              <p className="text-lg font-bold text-blue-600 dark:text-blue-400 mt-1">
                €{listing.price}
              </p>
              
              {/* Status Badge */}
              <div className="flex items-center mt-2">
                {getStatusIcon(listing.status)}
                <span className={`ml-1 text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(listing.status)}`}>
                  {listing.status?.charAt(0).toUpperCase() + listing.status?.slice(1)}
                </span>
              </div>
            </div>

            {/* Actions Menu */}
            <div className="relative">
              <button
                onClick={() => setShowActions(!showActions)}
                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <MoreVertical className="w-5 h-5" />
              </button>

              {showActions && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowActions(false)}
                  ></div>
                  <div className="absolute right-0 top-full mt-1 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-20">
                    <Link
                      to={`/listing/${listing.id}`}
                      className="flex items-center px-4 py-3 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                      onClick={() => setShowActions(false)}
                    >
                      <Eye className="w-4 h-4 mr-3" />
                      View Details
                    </Link>
                    <button
                      onClick={() => {
                        setShowActions(false);
                        // Navigate to edit page when available
                      }}
                      className="flex items-center w-full px-4 py-3 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
                    >
                      <Edit className="w-4 h-4 mr-3" />
                      Edit Listing
                    </button>
                    <button
                      onClick={() => {
                        setShowActions(false);
                        onDelete(listing.id);
                      }}
                      className="flex items-center w-full px-4 py-3 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
                    >
                      <Trash2 className="w-4 h-4 mr-3" />
                      Delete
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center justify-between mt-3 text-xs text-gray-500 dark:text-gray-400">
            <span>
              {listing.total_bids || 0} bid{(listing.total_bids || 0) !== 1 ? 's' : ''}
            </span>
            <span>
              {listing.created_at ? new Date(listing.created_at).toLocaleDateString() : 'N/A'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MobileMyListingsPage;