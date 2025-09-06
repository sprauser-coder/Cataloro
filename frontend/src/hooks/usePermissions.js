/**
 * RBAC Permissions Hook
 * Role-Based Access Control for Cataloro Marketplace
 */

import { useAuth } from '../context/AuthContext';

export const usePermissions = () => {
  const { user } = useAuth();
  
  // Get user role (prioritize new RBAC field over legacy)
  const getUserRole = () => {
    if (!user) return null;
    return user.user_role || user.role || 'user';
  };

  const userRole = getUserRole();
  const badge = user?.badge || (user?.role === 'admin' ? 'Admin' : 'Buyer');

  // Permission categories
  const permissions = {
    // Admin Panel Access
    adminPanel: {
      canAccess: userRole === 'Admin' || userRole === 'Admin-Manager',
      canAccessUserManagement: userRole === 'Admin' || userRole === 'Admin-Manager',
      canAccessListingsManagement: userRole === 'Admin' || userRole === 'Admin-Manager',
      canAccessDatDatabase: userRole === 'Admin' || userRole === 'Admin-Manager',
      canAccessAdsManager: userRole === 'Admin', // Only full admin
      canAccessSystemNotifications: userRole === 'Admin', // Only full admin
      canDeleteDatabase: userRole === 'Admin', // Restricted for Admin-Manager
      canUploadExcel: userRole === 'Admin', // Restricted for Admin-Manager
    },

    // Browse Page Permissions
    browse: {
      canAccess: true, // All users can browse
      canViewMarketRange: true,
      canViewSellerInfo: true,
      canViewLocation: true,
      canViewTimeLeft: true,
      canViewBidInfo: true,
      canPlaceBid: userRole === 'User-Buyer' || userRole === 'Admin' || userRole === 'Admin-Manager',
      canSeeBiddingControls: userRole === 'User-Buyer' || userRole === 'Admin' || userRole === 'Admin-Manager',
    },

    // Tenders Permissions
    tenders: {
      canAccess: true, // All users can access tenders
      canSubmitTender: userRole === 'User-Buyer' || userRole === 'Admin' || userRole === 'Admin-Manager',
      canManageTenders: userRole === 'User-Seller' || userRole === 'Admin' || userRole === 'Admin-Manager',
      canViewMyTenders: userRole === 'User-Buyer' || userRole === 'Admin' || userRole === 'Admin-Manager',
      canViewTenderManagement: userRole === 'User-Seller' || userRole === 'Admin' || userRole === 'Admin-Manager',
    },

    // Selling Permissions
    selling: {
      canCreateListing: userRole === 'User-Seller' || userRole === 'Admin' || userRole === 'Admin-Manager',
      canManageListings: userRole === 'User-Seller' || userRole === 'Admin' || userRole === 'Admin-Manager',
      canAccessSellingFunctions: userRole === 'User-Seller' || userRole === 'Admin' || userRole === 'Admin-Manager',
    },

    // General User Permissions
    user: {
      canAccessProfile: true,
      canAccessMessages: true,
      canAccessNotifications: true,
      canAccessFavorites: userRole === 'User-Buyer' || userRole === 'Admin' || userRole === 'Admin-Manager',
    },

    // UI Display Permissions
    ui: {
      showAdminPanelLink: userRole === 'Admin' || userRole === 'Admin-Manager',
      showTenderManagementLink: userRole === 'User-Seller' || userRole === 'Admin' || userRole === 'Admin-Manager',
      showMyTendersLink: userRole === 'User-Buyer' || userRole === 'Admin' || userRole === 'Admin-Manager',
      showCreateListingLink: userRole === 'User-Seller' || userRole === 'Admin' || userRole === 'Admin-Manager',
      showSellingFeatures: userRole === 'User-Seller' || userRole === 'Admin' || userRole === 'Admin-Manager',
      showBuyingFeatures: userRole === 'User-Buyer' || userRole === 'Admin' || userRole === 'Admin-Manager',
    }
  };

  // Helper functions
  const isAdmin = () => userRole === 'Admin';
  const isAdminManager = () => userRole === 'Admin-Manager';
  const isSeller = () => userRole === 'User-Seller';
  const isBuyer = () => userRole === 'User-Buyer';
  const isAdminLevel = () => userRole === 'Admin' || userRole === 'Admin-Manager';

  const hasPermission = (category, permission) => {
    return permissions[category]?.[permission] || false;
  };

  const canAccess = (feature) => {
    switch (feature) {
      case 'admin':
        return permissions.adminPanel.canAccess;
      case 'browse-bidding':
        return permissions.browse.canPlaceBid;
      case 'tenders':
        return permissions.tenders.canAccess;
      case 'selling':
        return permissions.selling.canAccessSellingFunctions;
      case 'favorites':
        return permissions.user.canAccessFavorites;
      default:
        return false;
    }
  };

  // Get user display information
  const getUserDisplay = () => ({
    role: userRole,
    badge: badge,
    name: user?.full_name || user?.username || 'User',
    email: user?.email || '',
    isAdmin: isAdmin(),
    isAdminManager: isAdminManager(),
    isSeller: isSeller(),
    isBuyer: isBuyer(),
    isAdminLevel: isAdminLevel()
  });

  return {
    permissions,
    userRole,
    badge,
    isAdmin,
    isAdminManager,
    isSeller,
    isBuyer,
    isAdminLevel,
    hasPermission,
    canAccess,
    getUserDisplay
  };
};

export default usePermissions;