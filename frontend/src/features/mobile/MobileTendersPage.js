/**
 * CATALORO - Mobile Tenders Page
 * Mobile-optimized tenders management with bid history and selling management
 */

import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, 
  DollarSign, 
  Clock, 
  CheckCircle, 
  XCircle,
  Users,
  TrendingUp,
  Package,
  Eye,
  MessageCircle
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function MobileTendersPage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const [activeTab, setActiveTab] = useState('my-bids'); // 'my-bids' or 'selling'
  const [myBids, setMyBids] = useState([]);
  const [sellingTenders, setSellingTenders] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (user?.id) {
      loadTendersData();
    }
  }, [user, activeTab]);

  const loadTendersData = async () => {
    try {
      setLoading(true);
      
      if (activeTab === 'my-bids') {
        // Load user's bids - use the same endpoint as desktop
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'https://cataloro-repair.preview.emergentagent.com/api'}/api/tenders/buyer/${user.id}`);
        if (response.ok) {
          const data = await response.json();
          setMyBids(data);
        } else {
          console.error(`Failed to fetch buyer tenders: ${response.status}`);
          showToast('Failed to load your bids', 'error');
        }
      } else {
        // Load tenders for user's listings (selling) - use the same endpoint as desktop
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'https://cataloro-repair.preview.emergentagent.com/api'}/api/tenders/seller/${user.id}/overview`);
        if (response.ok) {
          const data = await response.json();
          setSellingTenders(data);
        } else {
          console.error(`Failed to fetch seller tenders: ${response.status}`);
          showToast('Failed to load selling tenders', 'error');
        }
      }
    } catch (error) {
      console.error('Error loading tenders data:', error);
      showToast('Failed to load tenders data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'accepted':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'rejected':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-orange-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'accepted':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'rejected':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
      case 'pending':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
          <div className="flex items-center">
            <button
              onClick={() => navigate(-1)}
              className="mr-3 p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">Tenders</h1>
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
        <div className="flex items-center">
          <button
            onClick={() => navigate(-1)}
            className="mr-3 p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-lg font-semibold text-gray-900 dark:text-white">Tenders</h1>
        </div>

        {/* Tab Selector */}
        <div className="flex space-x-1 mt-3 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('my-bids')}
            className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors flex items-center justify-center ${
              activeTab === 'my-bids'
                ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            <DollarSign className="w-4 h-4 mr-2" />
            My Bids
          </button>
          <button
            onClick={() => setActiveTab('selling')}
            className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors flex items-center justify-center ${
              activeTab === 'selling'
                ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            <Package className="w-4 h-4 mr-2" />
            Selling
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {activeTab === 'my-bids' ? (
          <MyBidsSection bids={myBids} />
        ) : (
          <SellingSection tenders={sellingTenders} />
        )}
      </div>
    </div>
  );
}

// My Bids Section Component
function MyBidsSection({ bids }) {
  if (bids.length === 0) {
    return (
      <div className="text-center py-12">
        <DollarSign className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          No bids yet
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Start bidding on items you're interested in
        </p>
        <Link
          to="/browse"
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center"
        >
          <Eye className="w-5 h-5 mr-2" />
          Browse Items
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {bids.map((bid) => (
        <BidCard key={bid.id} bid={bid} />
      ))}
    </div>
  );
}

// Selling Section Component
function SellingSection({ tenders }) {
  if (tenders.length === 0) {
    return (
      <div className="text-center py-12">
        <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          No bids on your items
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Create listings to start receiving bids
        </p>
        <Link
          to="/create-listing"
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center"
        >
          <Package className="w-5 h-5 mr-2" />
          Create Listing
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {tenders.map((listingOverview, index) => (
        <SellingCard key={listingOverview.listing?.id || index} listingOverview={listingOverview} />
      ))}
    </div>
  );
}

// Bid Card Component
function BidCard({ bid }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'accepted':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'rejected':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'pending':
      case 'active':
        return <Clock className="w-4 h-4 text-orange-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'accepted':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'rejected':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
      case 'pending':
      case 'active':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
            {bid.listing?.title || 'Unknown Item'}
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Bid placed on {bid.created_at ? new Date(bid.created_at).toLocaleDateString() : 'N/A'}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Seller: {bid.seller?.username || 'Unknown'}
          </p>
        </div>
        <div className="flex items-center">
          {getStatusIcon(bid.status)}
          <span className={`ml-1 text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(bid.status)}`}>
            {bid.status?.charAt(0).toUpperCase() + bid.status?.slice(1) || 'Active'}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">Your Bid</p>
            <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
              €{bid.offer_amount || 0}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">Listing Price</p>
            <p className="text-sm font-semibold text-gray-900 dark:text-white">
              €{bid.listing?.price || 0}
            </p>
          </div>
        </div>

        <Link
          to={`/listing/${bid.listing?.id}`}
          className="bg-blue-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors"
        >
          View Item
        </Link>
      </div>
    </div>
  );
}

// Selling Card Component  
function SellingCard({ listingOverview }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
            {listingOverview.listing?.title || 'Unknown Item'}
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Listed for €{listingOverview.listing?.price || 0}
          </p>
        </div>
        <div className="flex items-center bg-blue-100 dark:bg-blue-900/30 px-2 py-1 rounded-full">
          <Users className="w-4 h-4 text-blue-600 dark:text-blue-400 mr-1" />
          <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
            {listingOverview.tender_count || 0} bid{(listingOverview.tender_count || 0) !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">Highest Bid</p>
            <p className="text-lg font-bold text-green-600 dark:text-green-400">
              €{listingOverview.highest_offer || 0}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400">Active Tenders</p>
            <p className="text-sm font-semibold text-gray-900 dark:text-white">
              {listingOverview.tenders?.length || 0}
            </p>
          </div>
        </div>

        <div className="flex space-x-2">
          <Link
            to={`/listing/${listingOverview.listing?.id}`}
            className="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-3 py-2 rounded-lg text-sm hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
          >
            View
          </Link>
          <Link
            to={`/tenders?tab=listings&listing=${listingOverview.listing?.id}`}
            className="bg-blue-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors"
          >
            Manage
          </Link>
        </div>
      </div>
    </div>
  );
}

export default MobileTendersPage;