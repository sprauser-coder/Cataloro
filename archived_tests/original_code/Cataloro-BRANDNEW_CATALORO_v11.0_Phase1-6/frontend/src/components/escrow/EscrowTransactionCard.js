import React, { useState } from 'react';
import { 
  Shield, 
  Clock, 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  Eye,
  RefreshCw,
  DollarSign,
  User,
  Package,
  Calendar,
  ArrowRight
} from 'lucide-react';

const EscrowTransactionCard = ({ 
  escrow, 
  currentUserId,
  onStatusUpdate,
  onViewDetails,
  compact = false 
}) => {
  const [loading, setLoading] = useState(false);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'funded':
        return <Shield className="w-5 h-5 text-blue-500" />;
      case 'released':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'in_dispute':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-gray-500" />;
      default:
        return <Shield className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
      case 'funded':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
      case 'released':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
      case 'in_dispute':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending':
        return 'Awaiting Payment';
      case 'funded':
        return 'Funds Secured';
      case 'released':
        return 'Transaction Complete';
      case 'in_dispute':
        return 'Under Dispute';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status.charAt(0).toUpperCase() + status.slice(1);
    }
  };

  const getUserRole = () => {
    if (escrow.buyer_id === currentUserId) return 'buyer';
    if (escrow.seller_id === currentUserId) return 'seller';
    return 'observer';
  };

  const getAvailableActions = () => {
    const userRole = getUserRole();
    const actions = [];

    switch (escrow.status) {
      case 'pending':
        if (userRole === 'buyer') {
          actions.push({ 
            id: 'fund', 
            label: 'Fund Escrow', 
            variant: 'primary',
            icon: DollarSign 
          });
        }
        actions.push({ 
          id: 'cancel', 
          label: 'Cancel', 
          variant: 'secondary',
          icon: XCircle 
        });
        break;
        
      case 'funded':
        if (userRole === 'seller') {
          actions.push({ 
            id: 'request_release', 
            label: 'Request Release', 
            variant: 'primary',
            icon: CheckCircle 
          });
        }
        if (userRole === 'buyer') {
          actions.push({ 
            id: 'approve_release', 
            label: 'Approve Release', 
            variant: 'primary',
            icon: CheckCircle 
          });
        }
        actions.push({ 
          id: 'dispute', 
          label: 'Create Dispute', 
          variant: 'danger',
          icon: AlertTriangle 
        });
        break;
    }

    actions.push({ 
      id: 'view_details', 
      label: 'View Details', 
      variant: 'outline',
      icon: Eye 
    });

    return actions;
  };

  const handleAction = async (actionId) => {
    if (actionId === 'view_details') {
      onViewDetails?.(escrow);
      return;
    }

    setLoading(true);
    try {
      await onStatusUpdate?.(escrow.id, actionId);
    } catch (error) {
      console.error('Action failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount, currency = 'EUR') => {
    const symbols = { 'EUR': '€', 'USD': '$', 'GBP': '£' };
    const symbol = symbols[currency] || currency;
    return `${symbol}${amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;
  };

  if (compact) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600 hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {getStatusIcon(escrow.status)}
            <div>
              <div className="font-medium text-gray-900 dark:text-white">
                {formatCurrency(escrow.amount, escrow.currency)}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Escrow #{escrow.id.slice(-8)}
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(escrow.status)}`}>
              {getStatusText(escrow.status)}
            </span>
            <button
              onClick={() => onViewDetails?.(escrow)}
              className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-600">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
            <Shield className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Escrow Transaction
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              ID: {escrow.id.slice(-8)}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(escrow.status)}`}>
            {getStatusText(escrow.status)}
          </span>
          {loading && <RefreshCw className="w-4 h-4 animate-spin text-gray-400" />}
        </div>
      </div>

      {/* Transaction Details */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <DollarSign className="w-5 h-5 text-green-500 mx-auto mb-1" />
          <div className="text-lg font-semibold text-gray-900 dark:text-white">
            {formatCurrency(escrow.amount, escrow.currency)}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Amount</div>
        </div>
        
        <div className="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <User className="w-5 h-5 text-blue-500 mx-auto mb-1" />
          <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
            {getUserRole() === 'buyer' ? 'You (Buyer)' : `Buyer: ${escrow.buyer_id.slice(-6)}`}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Buyer</div>
        </div>
        
        <div className="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <Package className="w-5 h-5 text-purple-500 mx-auto mb-1" />
          <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
            {getUserRole() === 'seller' ? 'You (Seller)' : `Seller: ${escrow.seller_id.slice(-6)}`}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Seller</div>
        </div>
        
        <div className="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <Calendar className="w-5 h-5 text-orange-500 mx-auto mb-1" />
          <div className="text-sm font-medium text-gray-900 dark:text-white">
            {new Date(escrow.created_at).toLocaleDateString()}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Created</div>
        </div>
      </div>

      {/* Listing Information */}
      {escrow.listing_id && (
        <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="flex items-center space-x-2">
            <Package className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-medium text-blue-900 dark:text-blue-300">
              Related to listing: {escrow.listing_id.slice(-8)}
            </span>
          </div>
        </div>
      )}

      {/* Progress Indicator */}
      <div className="mb-6">
        <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
          <span>Transaction Progress</span>
          <span>
            {escrow.status === 'released' ? '100%' : 
             escrow.status === 'funded' ? '75%' : 
             escrow.status === 'pending' ? '25%' : '0%'}
          </span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div 
            className={`h-2 rounded-full transition-all duration-300 ${
              escrow.status === 'released' ? 'bg-green-500 w-full' :
              escrow.status === 'funded' ? 'bg-blue-500 w-3/4' :
              escrow.status === 'pending' ? 'bg-yellow-500 w-1/4' :
              'bg-gray-400 w-0'
            }`}
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-2">
        {getAvailableActions().map((action) => {
          const Icon = action.icon;
          return (
            <button
              key={action.id}
              onClick={() => handleAction(action.id)}
              disabled={loading}
              className={`
                inline-flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors
                ${action.variant === 'primary' 
                  ? 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-2 focus:ring-blue-500' 
                  : action.variant === 'danger'
                  ? 'bg-red-600 text-white hover:bg-red-700 focus:ring-2 focus:ring-red-500'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
                }
                ${loading ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              <Icon className="w-4 h-4" />
              <span>{action.label}</span>
            </button>
          );
        })}
      </div>

      {/* Auto-release warning */}
      {escrow.status === 'funded' && escrow.auto_release_at && (
        <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-yellow-600" />
            <span className="text-sm text-yellow-800 dark:text-yellow-300">
              Auto-release scheduled for: {new Date(escrow.auto_release_at).toLocaleString()}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default EscrowTransactionCard;