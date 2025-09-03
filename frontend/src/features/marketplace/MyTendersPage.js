/**
 * CATALORO - My Tenders Page
 * Allows buyers to view their submitted tender offers and their status
 */

import React, { useState, useEffect } from 'react';
import { 
  DollarSign, 
  Clock, 
  CheckCircle, 
  XCircle,
  AlertCircle,
  TrendingUp,
  RefreshCw,
  MessageCircle
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function MyTendersPage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const [tenders, setTenders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchMyTenders();
    }
  }, [user]);

  const fetchMyTenders = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/tenders/buyer/${user.id}`);
      
      if (response.ok) {
        const data = await response.json();
        setTenders(data);
      } else {
        showToast('Failed to load your tenders', 'error');
      }
    } catch (error) {
      console.error('Failed to fetch my tenders:', error);
      showToast('Error loading tender data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'accepted':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'rejected':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'active':
        return 'Pending';
      case 'accepted':
        return 'Accepted';
      case 'rejected':
        return 'Rejected';
      default:
        return 'Unknown';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
      case 'accepted':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'rejected':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
    }
  };

  if (!user) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Please Login</h2>
        <p className="text-gray-600 dark:text-gray-400">You need to be logged in to view your tenders.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading your tenders...</p>
        </div>
      </div>
    );
  }

  const activeTenders = tenders.filter(t => t.status === 'active');
  const acceptedTenders = tenders.filter(t => t.status === 'accepted');
  const rejectedTenders = tenders.filter(t => t.status === 'rejected');
  const totalTenderValue = tenders.reduce((sum, tender) => sum + tender.offer_amount, 0);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Tender Offers</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Track all your submitted tender offers and their status
          </p>
        </div>
        
        <button
          onClick={fetchMyTenders}
          className="mt-4 lg:mt-0 flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <DollarSign className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Tenders</h3>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{tenders.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
              <Clock className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Active</h3>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{activeTenders.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Accepted</h3>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{acceptedTenders.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
              <TrendingUp className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Value</h3>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">€{totalTenderValue.toFixed(2)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tenders List */}
      {tenders.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="w-24 h-24 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-6">
            <DollarSign className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No Tender Offers</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            You haven't submitted any tender offers yet.
          </p>
          <Link
            to="/browse"
            className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
          >
            Browse Listings
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {tenders.map((tender) => (
            <div key={tender.id} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              <div className="flex items-start space-x-4">
                {/* Listing Image */}
                <div className="w-20 h-20 flex-shrink-0">
                  <img
                    src={tender.listing.images?.[0] || '/api/placeholder/400/300'}
                    alt={tender.listing.title}
                    className="w-full h-full object-cover rounded-lg"
                  />
                </div>
                
                {/* Tender Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
                        {tender.listing.title}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Starting Price: €{tender.listing.price.toFixed(2)}
                      </p>
                      {/* Seller Information */}
                      {tender.seller && (
                        <div className="mt-2 flex items-center space-x-2">
                          <span className="text-xs text-gray-500 dark:text-gray-500">Seller:</span>
                          <div className="flex items-center space-x-1">
                            {tender.seller.is_business && (
                              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                                Business
                              </span>
                            )}
                            <span className="text-sm font-medium text-gray-900 dark:text-white">
                              {tender.seller.business_name || tender.seller.full_name || tender.seller.username}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(tender.status)}`}>
                      {getStatusIcon(tender.status)}
                      <span className="ml-1">{getStatusText(tender.status)}</span>
                    </span>
                  </div>
                  
                  <div className="mt-4 flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="text-center">
                        <p className="text-sm text-gray-600 dark:text-gray-400">Your Offer</p>
                        <p className="text-xl font-bold text-blue-600 dark:text-blue-400">
                          €{tender.offer_amount.toFixed(2)}
                        </p>
                      </div>
                      
                      <div className="text-center">
                        <p className="text-sm text-gray-600 dark:text-gray-400">Submitted</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {new Date(tender.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    
                    {tender.status === 'accepted' && (
                      <div className="flex items-center space-x-2">
                        <div className="text-center">
                          <p className="text-sm text-green-600 dark:text-green-400 font-medium">Congratulations!</p>
                          <p className="text-xs text-gray-600 dark:text-gray-400">Your tender was accepted</p>
                        </div>
                        <button
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center space-x-2"
                          title="Message seller"
                        >
                          <MessageCircle className="w-4 h-4" />
                          <span>Contact Seller</span>
                        </button>
                      </div>
                    )}
                    
                    {tender.status === 'active' && (
                      <div className="text-center">
                        <p className="text-sm text-yellow-600 dark:text-yellow-400 font-medium">Waiting for response</p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">Seller will review your offer</p>
                      </div>
                    )}
                    
                    {tender.status === 'rejected' && (
                      <div className="text-center">
                        <p className="text-sm text-red-600 dark:text-red-400 font-medium">Not selected</p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">Better luck next time</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MyTendersPage;