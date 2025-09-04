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
  const [tendersOverview, setTendersOverview] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedListing, setSelectedListing] = useState(null);
  const [acceptingTender, setAcceptingTender] = useState(null);
  const [rejectingTender, setRejectingTender] = useState(null);

  useEffect(() => {
    if (user) {
      fetchTendersOverview();
    }
  }, [user]);

  const fetchTendersOverview = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
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
      setLoading(false);
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
        <p className="text-gray-600 dark:text-gray-400">You need to be logged in to manage tenders.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading tender overview...</p>
        </div>
      </div>
    );
  }

  const totalTenders = tendersOverview.reduce((sum, item) => sum + item.tender_count, 0);
  const totalHighestBids = tendersOverview.reduce((sum, item) => sum + (item.highest_offer || 0), 0);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Tender Management</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage tender offers for your listings
          </p>
        </div>
        
        <button
          onClick={fetchTendersOverview}
          className="mt-4 lg:mt-0 flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

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

export default TenderManagementPage;