import React, { useState, useEffect } from 'react';
import { 
  Package, 
  Eye, 
  Edit, 
  Trash2, 
  Search, 
  Filter, 
  Plus,
  RefreshCw,
  CheckCircle,
  Ban,
  Star,
  Shield,
  X,
  Download,
  AlertTriangle,
  DollarSign
} from 'lucide-react';
import { Link } from 'react-router-dom';

function ListingsTabComponent({ showToast }) {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [activeSubTab, setActiveSubTab] = useState('active');
  const [selectedListings, setSelectedListings] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingListing, setEditingListing] = useState(null);

  // Fetch listings from API
  const fetchListings = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/listings`);
      if (response.ok) {
        const data = await response.json();
        console.log('📋 Fetched listings:', data.length, 'items');
        setListings(data);
      } else {
        console.error('Failed to fetch listings:', response.status);
        // Use fallback dummy data if API fails
        setListings([
          {
            id: '1',
            title: 'Professional Catalyst Converter',
            price: 250,
            seller_username: 'seller1',
            seller_full_name: 'Professional Seller',
            seller_id: 'seller_1',
            status: 'active',
            views: 45,
            created_date: '2024-01-15',
            image: null
          },
          {
            id: '2',  
            title: 'Automotive Exhaust Component',
            price: 180,
            seller_username: 'autoparts',
            seller_full_name: 'Auto Parts Pro',
            seller_id: 'seller_2',
            status: 'inactive',
            views: 23,
            created_date: '2024-01-12',
            image: null
          }
        ]);
      }
    } catch (error) {
      console.error('Error fetching listings:', error);
      setListings([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchListings();
  }, []);

  // Filter listings based on search term and status
  const filteredListings = listings.filter(listing => {
    const matchesSearch = !searchTerm || 
      listing.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      listing.seller_username?.toLowerCase().includes(searchTerm.toLowerCase());
    
    let matchesStatus = true;
    if (activeSubTab !== 'active') {
      switch (activeSubTab) {
        case 'pending':
          matchesStatus = listing.status === 'pending' || 
                         listing.status === 'awaiting_approval' || 
                         (listing.pendingOrders && listing.pendingOrders > 0);
          break;
        case 'inactive':
          matchesStatus = listing.status === 'inactive' || 
                         listing.status === 'deactivated' || 
                         listing.status === 'paused';
          break;
        case 'expired':
          matchesStatus = listing.status === 'expired';
          break;
        case 'sold':
          matchesStatus = listing.status === 'sold' || 
                         listing.status === 'completed' || 
                         listing.status === 'finished';
          break;
        default:
          matchesStatus = listing.status === 'active' || listing.status === 'approved';
      }
    } else {
      matchesStatus = listing.status === 'active' || listing.status === 'approved';
    }
    
    return matchesSearch && matchesStatus;
  });

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
      {/* Header Section */}
      <div className="cataloro-card-glass p-8">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-6 lg:space-y-0">
          <div className="text-center lg:text-left">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-3">Listings Management</h2>
            <p className="text-gray-600 dark:text-gray-300 text-lg">Comprehensive marketplace listings control center</p>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
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

      {/* Listings Table */}
      <div className="cataloro-card-glass overflow-hidden">
        <div className="px-6 py-4 border-b border-white/10 dark:border-white/10">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Listings Management</h3>
            <span className="bg-blue-100/80 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 px-3 py-1 rounded-full text-sm font-medium backdrop-blur-md">
              {filteredListings.length} results
            </span>
          </div>
        </div>
        
        <div className="max-w-full">
          <table className="w-full min-w-full">
            <thead className="bg-gray-50/80 dark:bg-gray-800/50 backdrop-blur-sm">
              <tr>
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
          </div>
        )}
      </div>
    </div>
  );
}

export default ListingsTabComponent;