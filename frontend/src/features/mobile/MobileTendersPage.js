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
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'https://menu-settings-debug.preview.emergentagent.com/api'}/api/tenders/buyer/${user.id}`);
        if (response.ok) {
          const data = await response.json();
          setMyBids(data);
        } else {
          console.error(`Failed to fetch buyer tenders: ${response.status}`);
          showToast('Failed to load your bids', 'error');
        }
      } else {
        // Load tenders for user's listings (selling) - use the same endpoint as desktop
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'https://menu-settings-debug.preview.emergentagent.com/api'}/api/tenders/seller/${user.id}/overview`);
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
          <SellingSection tenders={sellingTenders} onRefresh={loadTendersData} />
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
function SellingSection({ tenders, onRefresh }) {
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
        <SellingCard 
          key={listingOverview.listing?.id || index} 
          listingOverview={listingOverview}
          onManageTenders={onRefresh}
        />
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
function SellingCard({ listingOverview, onManageTenders }) {
  const [showTendersDropdown, setShowTendersDropdown] = useState(false);
  const [processingTender, setProcessingTender] = useState(null);

  const handleManageClick = (e) => {
    e.preventDefault();
    setShowTendersDropdown(!showTendersDropdown);
  };

  const handleAcceptTender = async (tenderId, tenderAmount) => {
    if (!window.confirm(`Accept this bid of €${tenderAmount}?`)) return;
    
    try {
      setProcessingTender(tenderId);
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'https://menu-settings-debug.preview.emergentagent.com/api'}/api/tenders/${tenderId}/accept`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seller_id: listingOverview.listing?.seller_id })
      });
      
      if (response.ok) {
        // Import showToast from parent component via props or use alert for now
        alert('✅ Tender accepted successfully!');
        setShowTendersDropdown(false);
        if (onManageTenders) onManageTenders(); // Refresh data
      } else {
        const errorText = await response.text();
        alert(`❌ Failed to accept tender: ${errorText}`);
      }
    } catch (error) {
      console.error('Error accepting tender:', error);
      alert('Error accepting tender');
    } finally {
      setProcessingTender(null);
    }
  };

  const handleRejectTender = async (tenderId, tenderAmount) => {
    if (!window.confirm(`Reject this bid of €${tenderAmount}?`)) return;
    
    try {
      setProcessingTender(tenderId);
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'https://menu-settings-debug.preview.emergentagent.com/api'}/api/tenders/${tenderId}/reject`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seller_id: listingOverview.listing?.seller_id })
      });
      
      if (response.ok) {
        alert('✅ Tender rejected successfully!');
        setShowTendersDropdown(false);
        if (onManageTenders) onManageTenders(); // Refresh data
      } else {
        const errorText = await response.text();
        alert(`❌ Failed to reject tender: ${errorText}`);
      }
    } catch (error) {
      console.error('Error rejecting tender:', error);
      alert('Error rejecting tender');
    } finally {
      setProcessingTender(null);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 shadow-sm relative">
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

      <div className="flex items-center justify-between mb-3">
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
          <button
            onClick={handleManageClick}
            className="bg-blue-600 text-white px-3 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors"
          >
            Manage
          </button>
        </div>
      </div>

      {/* Tenders Dropdown/Modal */}
      {showTendersDropdown && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 bg-black bg-opacity-25 z-10"
            onClick={() => setShowTendersDropdown(false)}
          ></div>
          
          {/* Dropdown Content */}
          <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-20 max-h-80 overflow-y-auto">
            <div className="p-3 border-b border-gray-200 dark:border-gray-700">
              <h4 className="text-sm font-semibold text-gray-900 dark:text-white">
                Manage Tenders ({listingOverview.tenders?.length || 0})
              </h4>
            </div>
            
            {listingOverview.tenders && listingOverview.tenders.length > 0 ? (
              <div className="max-h-60 overflow-y-auto">
                {listingOverview.tenders.map((tender, index) => (
                  <div key={tender.id || index} className="p-3 border-b border-gray-100 dark:border-gray-700 last:border-b-0">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {tender.buyer?.username || 'Anonymous'}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {tender.buyer?.is_business ? 'Business' : 'Individual'} • {tender.created_at ? new Date(tender.created_at).toLocaleDateString() : 'N/A'}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
                          €{tender.offer_amount || 0}
                        </p>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          tender.status === 'accepted' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                          tender.status === 'rejected' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' :
                          'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300'
                        }`}>
                          {tender.status?.charAt(0).toUpperCase() + tender.status?.slice(1) || 'Active'}
                        </span>
                      </div>
                    </div>
                    
                    {/* Always show Accept/Reject buttons unless tender is already accepted/rejected */}
                    {(!tender.status || tender.status.toLowerCase() !== 'accepted' && tender.status.toLowerCase() !== 'rejected') && (
                      <div className="flex space-x-2 mt-2">
                        <button
                          onClick={() => handleAcceptTender(tender.id, tender.offer_amount)}
                          disabled={processingTender === tender.id}
                          className="flex-1 bg-green-600 text-white px-3 py-2 rounded-lg text-xs font-medium hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center justify-center"
                        >
                          {processingTender === tender.id ? (
                            <>
                              <div className="animate-spin w-3 h-3 border border-white border-t-transparent rounded-full mr-1"></div>
                              Processing...
                            </>
                          ) : (
                            <>
                              <CheckCircle className="w-3 h-3 mr-1" />
                              Accept
                            </>
                          )}
                        </button>
                        <button
                          onClick={() => handleRejectTender(tender.id, tender.offer_amount)}
                          disabled={processingTender === tender.id}
                          className="flex-1 bg-red-600 text-white px-3 py-2 rounded-lg text-xs font-medium hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center justify-center"
                        >
                          {processingTender === tender.id ? (
                            <>
                              <div className="animate-spin w-3 h-3 border border-white border-t-transparent rounded-full mr-1"></div>
                              Processing...
                            </>
                          ) : (
                            <>
                              <XCircle className="w-3 h-3 mr-1" />
                              Reject
                            </>
                          )}
                        </button>
                      </div>
                    )}
                    
                    {/* Show message for already processed tenders */}
                    {(tender.status?.toLowerCase() === 'accepted' || tender.status?.toLowerCase() === 'rejected') && (
                      <div className="mt-2 text-center">
                        <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                          tender.status.toLowerCase() === 'accepted' 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                            : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                        }`}>
                          {tender.status.toLowerCase() === 'accepted' ? 'Tender Accepted' : 'Tender Rejected'}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 text-center">
                <p className="text-sm text-gray-500 dark:text-gray-400">No tenders yet</p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default MobileTendersPage;