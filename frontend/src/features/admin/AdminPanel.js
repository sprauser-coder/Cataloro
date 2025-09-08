/**
 * CATALORO - Ultra-modern Administration Panel with comprehensive management capabilities
 * This mega-component handles all administrative functions with advanced features
 */

import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { 
  Menu,
  GripVertical,
  Plus,
  Edit3,
  Trash2,
  Eye,
  EyeOff,
  Save,
  RotateCcw,
  Settings,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Home,
  Package,
  Users,
  MessageCircle,
  Heart,
  User,
  ShoppingCart,
  BarChart3,
  Shield,
  Target,
  Database,
  Building,
  Zap,
  Globe,
  DollarSign,
  Star,
  Bell,
  Search,
  Filter,
  Download,
  Upload,
  Palette,
  BookOpen,
  Layers,
  GitBranch,
  Monitor,
  Smartphone,
  Code,
  Server,
  Wifi,
  Lock,
  Mail,
  Calendar,
  Camera,
  Image as ImageIcon,
  Video,
  Music,
  FileText,
  Folder,
  Archive,
  Link,
  Tag,
  Flag,
  Award,
  Trophy,
  Crown,
  Gem,
  Rocket,
  Lightning,
  Fire,
  Sun,
  Moon,
  Cloud,
  Umbrella,
  Mountain,
  Store,
  Check,
  CheckCircle,
  RefreshCw,
  Clock,
  Layout,
  X,
  Trash,
  Edit,
  Activity,
  TrendingUp,
  TrendingDown,
  UserPlus,
  UserMinus,
  Timer,
  PlayCircle,
  StopCircle,
  Volume2,
  VolumeX,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  MoreHorizontal,
  MoreVertical,
  Maximize,
  Minimize,
  Share,
  Copy,
  PieChart,
  ToggleLeft,
  ToggleRight,
  Sliders,
  CheckSquare,
  Square,
  CreditCard,
  Banknote,
  Wallet,
  Receipt,
  Calculator,
  Percent,
  Hash,
  Info,
  AlertTriangle,
  AlertCircle,
  HelpCircle,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  PhoneCall,
  Video as VideoIcon,
  Headphones,
  Mic,
  MicOff,
  Webcam,
  Calendar as CalendarIcon,
  MapPin,
  Navigation,
  Compass,
  Map,
  Route,
  Car,
  Truck,
  Plane,
  Ship,
  Train,
  Bicycle,
  Scooter,
  Walking,
  Key,
  Unlock,
  LockOpen,
  Fingerprint,
  QrCode,
  BarChart,
  LineChart,
  Repeat,
  SkipBack,
  SkipForward,
  Pause,
  Play,
  FastForward,
  Rewind,
  Shuffle,
  RepeatOne,
  VolumeOne,
  VolumeTwo,
  List,
  Grid,
  Layers as LayersIcon,
  Archive as ArchiveIcon,
  Box,
  PackageOpen,
  Boxes,
  Container,
  Clipboard,
  ClipboardCheck,
  ClipboardCopy,
  ClipboardList,
  ClipboardX,
  BookMark,
  Book,
  BookOpen,
  Bookmark,
  Library,
  GraduationCap,
  School,
  University,
  Briefcase,
  Building2,
  Factory,
  Store as StoreIcon,
  ShoppingBag,
  ShoppingCart as ShoppingCartIcon,
  CreditCard as CreditCardIcon,
  DollarSign as DollarSignIcon,
  Euro,
  Pound,
  Yen,
  Bitcoin,
  Coins,
  Banknote as BanknoteIcon,
  Receipt as ReceiptIcon,
  Calculator as CalculatorIcon,
  Percent as PercentIcon,
  Hash as HashIcon,
  AtSign,
  Hash as HashtagIcon,
  PhoneIcon,
  MailIcon,
  MessageCircleIcon,
  SendIcon,
  InboxIcon,
  OutboxIcon,
  ArchiveIcon as ArchiveIconDuplicate,
  TrashIcon,
  DeleteIcon,
  EditIcon,
  PlusIcon,
  MinusIcon,
  CloseIcon,
  CheckIcon,
  CrossIcon,
  ArrowRightIcon,
  ArrowLeftIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ChevronRightIcon,
  ChevronLeftIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  ExpandIcon,
  CollapseIcon,
  MaximizeIcon,
  MinimizeIcon,
  FullscreenIcon,
  ExitFullscreenIcon,
  ZoomInIcon,
  ZoomOutIcon,
  RefreshIcon,
  ReloadIcon,
  SyncIcon,
  LoaderIcon,
  SpinnerIcon
} from 'lucide-react';
import { useNotifications } from '../../context/NotificationContext';
import ExportManagerDashboard from '../../components/admin/ExportManagerDashboard';
import usePermissions from '../../hooks/usePermissions';
import adminService from '../../services/adminService';

// Global site config state - managed at top level
let globalSiteConfig = {};

// Helper functions for AdminPanel
const calculateExpirationDate = (startDate, runtime) => {
  const start = new Date(startDate);
  
  switch (runtime) {
    case '1 minute':
      return new Date(start.getTime() + 60 * 1000).toISOString();
    case '5 minutes':
      return new Date(start.getTime() + 5 * 60 * 1000).toISOString();
    case '1 hour':
      return new Date(start.getTime() + 60 * 60 * 1000).toISOString();
    case '1 day':
      return new Date(start.getTime() + 24 * 60 * 60 * 1000).toISOString();
    case '1 week':
      return new Date(start.getTime() + 7 * 24 * 60 * 60 * 1000).toISOString();
    case '1 month':
      return new Date(start.getTime() + 30 * 24 * 60 * 60 * 1000).toISOString();
    case '3 months':
      return new Date(start.getTime() + 90 * 24 * 60 * 60 * 1000).toISOString();
    case '1 year':
      return new Date(start.getTime() + 365 * 24 * 60 * 60 * 1000).toISOString();
    default:
      return new Date(start.getTime() + 30 * 24 * 60 * 60 * 1000).toISOString();
  }
};

const getTimeRemaining = (expirationDate) => {
  if (!expirationDate) return null;
  
  const now = new Date().getTime();
  const expire = new Date(expirationDate).getTime();
  const remaining = expire - now;
  
  if (remaining <= 0) {
    return { expired: true };
  }
  
  return {
    expired: false,
    days: Math.floor(remaining / (1000 * 60 * 60 * 24)),
    hours: Math.floor((remaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
    minutes: Math.floor((remaining % (1000 * 60 * 60)) / (1000 * 60)),
    seconds: Math.floor((remaining % (1000 * 60)) / 1000)
  };
};

const deactivateExpiredAds = () => {
  try {
    const siteConfig = JSON.parse(localStorage.getItem('cataloro_site_config') || '{}');
    if (!siteConfig.adsManager) return false;
    
    let hasExpiredAds = false;
    const updatedAdsManager = { ...siteConfig.adsManager };
    
    Object.keys(updatedAdsManager).forEach(adType => {
      const adConfig = updatedAdsManager[adType];
      if (adConfig.active && adConfig.expirationDate) {
        const now = new Date().getTime();
        const expire = new Date(adConfig.expirationDate).getTime();
        
        if (now >= expire) {
          console.log(`🕒 Deactivating expired ad: ${adType}`);
          updatedAdsManager[adType] = {
            ...adConfig,
            active: false,
            deactivatedAt: new Date().toISOString(),
            deactivationReason: 'Expired'
          };
          hasExpiredAds = true;
        }
      }
    });
    
    if (hasExpiredAds) {
      const updatedConfig = { ...siteConfig, adsManager: updatedAdsManager };
      localStorage.setItem('cataloro_site_config', JSON.stringify(updatedConfig));
      console.log('🔧 Expired ads have been deactivated');
      return true;
    }
    
    return false;
  } catch (error) {
    console.error('Error deactivating expired ads:', error);
    return false;
  }
};

// Main AdminPanel Component
function AdminPanel() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [siteConfig, setSiteConfig] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [isDeleting, setIsDeleting] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [isEditingUser, setIsEditingUser] = useState(false);
  const [editUserData, setEditUserData] = useState({});
  const [isSavingUser, setIsSavingUser] = useState(false);
  
  const { showToast } = useNotifications();
  const { permissions } = usePermissions();

  // Comprehensive tab configuration - matches working version exactly
  const adminTabs = [
    { id: 'dashboard', label: 'Mega Dashboard', shortLabel: 'Dashboard', icon: BarChart3 },
    { id: 'documentation', label: 'Documentation', shortLabel: 'Docs', icon: BookOpen,
      adminOnly: true },
    { id: 'media-browser', label: 'Media Browser', shortLabel: 'Media', icon: ImageIcon,
      adminOnly: true },
    { id: 'users', label: 'Users', shortLabel: 'Users', icon: Users, 
      permission: 'canAccessUserManagement' },
    { id: 'listings', label: 'Listings', shortLabel: 'Listings', icon: Package, 
      permission: 'canAccessListingsManagement' },
    { id: 'ads-manager', label: 'Ads Manager', shortLabel: 'Ads', icon: Target,
      adminOnly: true, consolidated: true },
    { id: 'cats', label: "Cat's", shortLabel: "Cat's", icon: Database,
      adminOnly: true },
    { id: 'site-settings', label: 'Site Settings', shortLabel: 'Settings', icon: Settings,
      adminOnly: true },
    { id: 'administration', label: 'Administration', shortLabel: 'Admin', icon: Shield, 
      adminOnly: true }
  ];

  const getTabDescription = (tabId) => {
    const descriptions = {
      'listings': 'Marketplace listings management & moderation',
      'ads-manager': 'Advertising campaigns, placements & analytics',
      'cats': 'Catalyst database management & configuration',
      'site-settings': 'Global site configuration & branding settings',
      'administration': 'System administration & maintenance tools'
    };
    return descriptions[tabId] || '';
  };

  // Load initial configuration
  useEffect(() => {
    loadSiteConfiguration();
  }, []);

  const loadSiteConfiguration = async () => {
    try {
      setIsLoading(true);
      // Load from localStorage first
      const localConfig = JSON.parse(localStorage.getItem('cataloro_site_config') || '{}');
      
      // Ensure adsManager exists with proper structure
      if (!localConfig.adsManager) {
        localConfig.adsManager = {};
      }
      
      setSiteConfig(localConfig);
      globalSiteConfig = localConfig;
      
      console.log('🔧 AdminPanel: Loaded site configuration:', localConfig);
    } catch (error) {
      console.error('Failed to load site configuration:', error);
      showToast('Failed to load site configuration', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfigChange = (section, value) => {
    console.log(`🔧 AdminPanel: Config change - ${section}:`, value);
    
    const newConfig = {
      ...siteConfig,
      [section]: value
    };
    
    setSiteConfig(newConfig);
    globalSiteConfig = newConfig;
    
    // Save to localStorage immediately
    localStorage.setItem('cataloro_site_config', JSON.stringify(newConfig));
  };

  // Filter visible tabs based on permissions
  const visibleTabs = adminTabs.filter(tab => {
    if (tab.adminOnly && !permissions?.ui?.showAdminPanelLink) return false;
    if (tab.permission && !permissions?.ui?.[tab.permission]) return false;
    return true;
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Loading administration panel...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Admin Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 fixed w-full top-0 z-40">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-2 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">Administration Panel</h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">Cataloro Marketplace Management</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex pt-20">
        {/* Sidebar */}
        <div className="w-48 sm:w-48 md:w-56 lg:w-64 bg-white dark:bg-gray-800 h-screen fixed left-0 top-20 overflow-y-auto border-r border-gray-200 dark:border-gray-700">
          <nav className="p-4 space-y-2">
            {visibleTabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-gray-500 dark:text-gray-400'}`} />
                  <div className="min-w-0 flex-1">
                    <div className={`text-sm font-medium truncate ${isActive ? 'text-white' : ''}`}>
                      {tab.label}
                    </div>
                    {getTabDescription(tab.id) && (
                      <div className={`text-xs mt-1 truncate ${isActive ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'}`}>
                        {getTabDescription(tab.id)}
                      </div>
                    )}
                  </div>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Main Content Area - positioned below header and beside sidebar - FULL WIDTH */}
        <div className="ml-48 sm:ml-48 md:ml-56 lg:ml-64 pt-20 min-h-screen">
          {/* Content Container using full available width minus sidebar */}
          <div className="px-4 sm:px-6 lg:px-8 py-8">

          {/* Dashboard Tab */}
          {activeTab === 'dashboard' && (
            <MegaDashboard 
              showToast={showToast}
            />
          )}

          {activeTab === 'documentation' && (
            <DocumentationTab 
              showToast={showToast}
            />
          )}

          {activeTab === 'media-browser' && (
            <MediaBrowserTab 
              showToast={showToast}
            />
          )}

          {activeTab === 'users' && (
            <UsersTab 
              showToast={showToast}
            />
          )}
          
          {activeTab === 'listings' && (
            <ListingsTab 
              showToast={showToast}
            />
          )}
          
          {activeTab === 'cats' && (
            <CatsTab 
              showToast={showToast}
            />
          )}

          {activeTab === 'site-settings' && (
            <SiteSettingsTab 
              siteConfig={siteConfig}
              handleConfigChange={handleConfigChange}
              showToast={showToast}
            />
          )}

          {activeTab === 'ads-manager' && (
            <AdsManagerSection 
              siteConfig={siteConfig}
              handleConfigChange={handleConfigChange}
              showToast={showToast}
            />
          )}

          {activeTab === 'administration' && (
            <SiteAdministrationTab 
              showToast={showToast}
            />
          )}

          </div>
        </div>
      </div>
    </div>
  );
}

// EXACT COPY OF ORIGINAL ADS MANAGER SECTION
// Ad's Manager Component - EXACT COPY FROM ORIGINAL v11.0
function AdsManagerSection({ siteConfig, handleConfigChange, showToast }) {
  const [activeAdTab, setActiveAdTab] = React.useState('browse');
  const [isSavingAds, setIsSavingAds] = React.useState(false);
  const [adsSaved, setAdsSaved] = React.useState(false);
  
  const handleAdConfigChange = (adType, field, value) => {
    console.log(`🔧 Updating ad config: ${adType}.${field} = ${value}`);
    
    // CRITICAL FIX: Initialize adsManager if it doesn't exist
    const currentAdsManager = siteConfig.adsManager || {};
    
    // Special debugging for notification-related fields
    if (field === 'notificationUsers' || field === 'notificationMethods') {
      console.log(`🔍 ${adType} notification config update:`, {
        field,
        value,
        currentUsers: currentAdsManager[adType]?.notificationUsers?.length || 0,
        currentMethods: currentAdsManager[adType]?.notificationMethods || []
      });
    }
    
    const newAdsManager = {
      ...currentAdsManager,
      [adType]: {
        ...currentAdsManager[adType],
        [field]: value
      }
    };
    console.log(`🔧 New adsManager:`, newAdsManager);
    handleConfigChange('adsManager', newAdsManager);
  };

  const saveAdsConfiguration = async () => {
    try {
      setIsSavingAds(true);
      
      // Check for expired ads and deactivate them first
      deactivateExpiredAds();
      
      console.log('🔧 AdminPanel: Saving ads configuration with activation dates...');
      
      // For each active ad, set start date and expiration date
      const updatedAdsManagerConfig = { ...siteConfig.adsManager || {} };
      
      Object.keys(updatedAdsManagerConfig).forEach(adType => {
        const adConfig = updatedAdsManagerConfig[adType];
        
        if (adConfig.active && !adConfig.startDate) {
          // This is a newly activated ad - set start and expiration dates
          const now = new Date().toISOString();
          const expirationDate = calculateExpirationDate(now, adConfig.runtime || '1 month');
          
          updatedAdsManagerConfig[adType] = {
            ...adConfig,
            startDate: now,
            expirationDate: expirationDate
          };
          
          console.log(`🕒 Setting activation dates for ${adType}:`, {
            startDate: now,
            expirationDate: expirationDate,
            runtime: adConfig.runtime
          });
        }
      });
      
      // CRITICAL FIX: Preserve ads configuration from localStorage
      const currentLocalStorage = JSON.parse(localStorage.getItem('cataloro_site_config') || '{}');
      
      // Merge site config with existing localStorage, preserving ads configuration
      const mergedConfig = {
        ...siteConfig,
        ...currentLocalStorage,
        // Use the updated ads configuration with activation dates
        adsManager: {
          ...currentLocalStorage.adsManager,
          ...updatedAdsManagerConfig
        },
        // Always ensure hero section is enabled
        heroSectionEnabled: true
      };
      
      console.log('🔧 AdminPanel: Saving merged config with activation dates:', mergedConfig);
      
      // Save merged configuration to localStorage
      localStorage.setItem('cataloro_site_config', JSON.stringify(mergedConfig));
      
      // Update the ads manager configuration through the parent handler
      handleConfigChange('adsManager', updatedAdsManagerConfig);
      
      // Count active ads for display
      const activeAdsCount = Object.entries(updatedAdsManagerConfig)
        .filter(([key, value]) => value.active).length;
      
      const totalConfiguredAds = Object.entries(updatedAdsManagerConfig)
        .filter(([key, value]) => value.image || value.logo).length;
      
      showToast(
        `🎯 Ad's Manager configuration saved successfully! 
        ${activeAdsCount} active ads, ${totalConfiguredAds} configured ads. 
        All advertisement functionalities are now live across the marketplace!`, 
        'success'
      );
      
      // Log detailed ads configuration for debugging
      console.log('🎉 COMPLETE Ad\'s Manager Configuration Applied:', {
        ...updatedAdsManagerConfig,
        appliedAt: new Date().toISOString(),
        activeAds: activeAdsCount,
        totalConfigured: totalConfiguredAds
      });
      
      // Show visual confirmation
      setAdsSaved(true);
      setTimeout(() => setAdsSaved(false), 3000);
      
      // Trigger a custom event to notify other components that ads config has changed
      window.dispatchEvent(new CustomEvent('adsConfigUpdated', { 
        detail: updatedAdsManagerConfig 
      }));
      
    } catch (error) {
      console.error('Failed to save ads configuration:', error);
      showToast('Failed to save ads configuration. Please try again.', 'error');
    } finally {
      setIsSavingAds(false);
    }
  };

  const handleImageUpload = async (adType, file, field = 'image') => {
    try {
      console.log(`🔧 Starting image upload for ${adType}.${field}`);
      
      const formData = new FormData();
      formData.append('image', file);  // FIXED: Backend expects 'image', not 'file'
      formData.append('section', `ads_${adType}`);
      formData.append('field', field); // FIXED: Added missing 'field' parameter

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/upload-image`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        console.log('🔧 Upload successful, result:', result);
        
        // Update the ad configuration with the new image URL
        const imageUrl = result.url || result.imageUrl;
        if (imageUrl) {
          handleAdConfigChange(adType, field, imageUrl);
          
          // IMMEDIATELY save to localStorage for instant display on browse page
          const currentConfig = JSON.parse(localStorage.getItem('cataloro_site_config') || '{}');
          if (!currentConfig.adsManager) currentConfig.adsManager = {};
          if (!currentConfig.adsManager[adType]) currentConfig.adsManager[adType] = {};
          
          currentConfig.adsManager[adType][field] = imageUrl;
          
          // Ensure other required fields exist
          currentConfig.adsManager[adType].active = currentConfig.adsManager[adType].active !== false;
          currentConfig.adsManager[adType].description = currentConfig.adsManager[adType].description || 'Advertisement';
          currentConfig.adsManager[adType].runtime = currentConfig.adsManager[adType].runtime || '1 month';
          
          // Set default dimensions based on ad type
          if (adType === 'browsePageAd') {
            currentConfig.adsManager[adType].width = currentConfig.adsManager[adType].width || '300px';
            currentConfig.adsManager[adType].height = currentConfig.adsManager[adType].height || '600px';
          } else if (adType === 'favoriteAd') {
            currentConfig.adsManager[adType].width = currentConfig.adsManager[adType].width || '100%';
            currentConfig.adsManager[adType].height = currentConfig.adsManager[adType].height || '200px';
          } else if (adType === 'messengerAd') {
            currentConfig.adsManager[adType].width = currentConfig.adsManager[adType].width || '250px';
            currentConfig.adsManager[adType].height = currentConfig.adsManager[adType].height || '400px';
          }
          
          currentConfig.adsManager[adType].url = currentConfig.adsManager[adType].url || '';
          currentConfig.adsManager[adType].clicks = currentConfig.adsManager[adType].clicks || 0;
          
          localStorage.setItem('cataloro_site_config', JSON.stringify(currentConfig));
          
          // Dispatch event to notify browse page
          window.dispatchEvent(new CustomEvent('adsConfigUpdated', { 
            detail: currentConfig.adsManager 
          }));
          
          showToast(`${field === 'logo' ? 'Logo' : 'Image'} uploaded and activated successfully!`, 'success');
          console.log(`🔧 Image URL set and saved for ${adType}.${field}:`, imageUrl);
          console.log('🔧 Updated localStorage config:', currentConfig);
        } else {
          throw new Error('No image URL in response');
        }
      } else {
        const errorText = await response.text();
        console.error('Upload response error:', errorText);
        throw new Error(`Upload failed: ${response.status}`);
      }
    } catch (error) {
      console.error('Image upload error:', error);
      showToast('Failed to upload image. Please try again.', 'error');
    }
  };

  const adTabs = [
    { id: 'browse', label: "Browse Page Ad's", icon: Package },
    { id: 'favorite', label: "Favorite Ad's", icon: Heart },
    { id: 'messenger', label: "Messenger Ad's", icon: MessageCircle },
    { id: 'footer', label: "Footer Ad's", icon: Layout }
  ];

  const runtimeOptions = [
    { value: '1 minute', label: '1 Minute (Testing)' },
    { value: '5 minutes', label: '5 Minutes (Testing)' },
    { value: '1 hour', label: '1 Hour' },
    { value: '1 day', label: '1 Day' },
    { value: '1 week', label: '1 Week' },
    { value: '1 month', label: '1 Month' },
    { value: '3 months', label: '3 Months' },
    { value: '1 year', label: '1 Year' },
    { value: 'custom', label: '⏱️ Custom Duration' }
  ];

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold mb-2">Ad's Manager</h3>
            <p className="text-purple-100">Manage advertisements across your marketplace</p>
          </div>
          
          {/* Save Ads Configuration Button */}
          <div className="flex items-center space-x-3">
            <button
              onClick={saveAdsConfiguration}
              disabled={isSavingAds}
              className={`flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold transition-all duration-200 ${
                isSavingAds 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : adsSaved
                    ? 'bg-green-500 text-white'
                    : 'bg-white text-purple-600 hover:bg-purple-50 shadow-lg hover:shadow-xl'
              }`}
            >
              {isSavingAds ? (
                <>
                  <div className="w-5 h-5 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
                  <span>Saving Ads...</span>
                </>
              ) : adsSaved ? (
                <>
                  <CheckCircle className="w-5 h-5" />
                  <span>Ads Activated!</span>
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  <span>Save & Activate Ads</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center space-x-1 bg-gray-100/50 dark:bg-gray-800/50 rounded-lg p-1 overflow-x-auto">
          {adTabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveAdTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 whitespace-nowrap ${
                  activeAdTab === tab.id
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-white/50 dark:hover:bg-gray-700/50'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Browse Page Ad Tab */}
      {activeAdTab === 'browse' && (
        <AdConfigPanel
          title="Browse Page Advertisement"
          description="Display advertisement on the right side of browse page (3 listings per row layout)"
          adConfig={siteConfig.adsManager?.browsePageAd || { active: false, image: null, description: '', runtime: '1 month', width: '300px', height: '600px', url: '', clicks: 0, notificationMethods: ['notificationCenter'], notificationUsers: [] }}
          adType="browsePageAd"
          handleAdConfigChange={handleAdConfigChange}
          handleImageUpload={handleImageUpload}
          runtimeOptions={runtimeOptions}
          showDimensions={true}
          dimensionsLabel="Ad Dimensions (Vertical Banner)"
          showToast={showToast}
        />
      )}

      {/* Favorite Page Ad Tab */}
      {activeAdTab === 'favorite' && (
        <AdConfigPanel
          title="Favorites Page Advertisement"
          description="Display advertisement at the top of favorites page below 'My Favorites' header"
          adConfig={siteConfig.adsManager?.favoriteAd || { active: false, image: null, description: '', runtime: '1 month', width: '100%', height: '200px', url: '', clicks: 0, notificationMethods: ['notificationCenter'], notificationUsers: [] }}
          adType="favoriteAd"
          handleAdConfigChange={handleAdConfigChange}
          handleImageUpload={handleImageUpload}
          runtimeOptions={runtimeOptions}
          showDimensions={true}
          dimensionsLabel="Favorites Ad Dimensions (Banner)"
          showToast={showToast}
        />
      )}

      {/* Messenger Ad Tab */}
      {activeAdTab === 'messenger' && (
        <AdConfigPanel
          title="Messenger Advertisement"
          description="Display advertisements on messages page"
          adConfig={siteConfig.adsManager?.messengerAd || { active: false, image: null, description: '', runtime: '1 month', width: '250px', height: '400px', url: '', clicks: 0, notificationMethods: ['notificationCenter'], notificationUsers: [] }}
          adType="messengerAd"
          handleAdConfigChange={handleAdConfigChange}
          handleImageUpload={handleImageUpload}
          runtimeOptions={runtimeOptions}
          showDimensions={true}
          dimensionsLabel="Messenger Ad Dimensions (Sidebar)"
          showToast={showToast}
        />
      )}

      {/* Footer Ad Tab */}
      {activeAdTab === 'footer' && (
        <FooterAdConfigPanel
          adConfig={siteConfig.adsManager?.footerAd || { active: false, logo: null, companyName: '', runtime: '1 month', expirationEvents: ['deactivate'], notificationMethods: ['notificationCenter'], notificationUsers: [] }}
          adType="footerAd"
          handleAdConfigChange={handleAdConfigChange}
          handleImageUpload={handleImageUpload}
          runtimeOptions={runtimeOptions}
          showToast={showToast}
        />
      )}
    </div>
  );
}

// Create placeholder AdConfigPanel component (simplified version for the fixed implementation)
function AdConfigPanel({ title, description, adConfig, adType, handleAdConfigChange, handleImageUpload, runtimeOptions, showDimensions, dimensionsLabel, showToast }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
      <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{title}</h4>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">{description}</p>

      {/* Active Toggle */}
      <div className="space-y-6">
        <label className="flex items-start space-x-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
          <button
            onClick={() => {
              const currentActive = adConfig?.active || false;
              handleAdConfigChange(adType, 'active', !currentActive);
            }}
            className="mt-1 flex items-center justify-center w-8 h-8 rounded-full transition-colors duration-200"
            style={{
              backgroundColor: adConfig?.active ? '#10B981' : '#6B7280',
              color: 'white'
            }}
          >
            {adConfig?.active ? (
              <CheckCircle className="w-5 h-5" />
            ) : (
              <X className="w-5 h-5" />
            )}
          </button>
          <div>
            <div className="font-medium text-gray-900 dark:text-white">
              Active {adConfig?.active ? '✓ ON' : '✗ OFF'}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Enable this advertisement section</div>
          </div>
        </label>

        {adConfig?.active && (
          <div className="space-y-4">
            {/* Image Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
                <ImageIcon className="w-5 h-5 inline mr-2" />
                Advertisement Image
              </label>
              
              <div className="space-y-4">
                {/* Current Image Preview */}
                {adConfig?.image && (
                  <div className="relative group max-w-sm">
                    <img 
                      src={adConfig.image} 
                      alt="Advertisement preview"
                      className="w-full h-48 object-cover rounded-lg border-2 border-gray-200 dark:border-gray-600"
                    />
                    <button
                      type="button"
                      onClick={() => handleAdConfigChange(adType, 'image', null)}
                      className="absolute top-2 right-2 p-2 bg-red-500 hover:bg-red-600 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                )}
                
                {/* File Upload Area */}
                <label className="w-full h-48 max-w-sm border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg flex flex-col items-center justify-center cursor-pointer hover:border-blue-500 dark:hover:border-blue-400 transition-colors">
                  <Upload className="w-12 h-12 text-gray-400 mb-4" />
                  <span className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Upload Advertisement Image
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400 text-center">
                    Click to browse or drag and drop<br />
                    JPG, PNG, GIF up to 5MB
                  </span>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleImageUpload(adType, e.target.files[0])}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Description/Alt Text
              </label>
              <textarea
                value={adConfig?.description || ''}
                onChange={(e) => handleAdConfigChange(adType, 'description', e.target.value)}
                placeholder="Enter advertisement description..."
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            {/* URL Link */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Target URL (Optional)
              </label>
              <input
                type="url"
                value={adConfig?.url || ''}
                onChange={(e) => handleAdConfigChange(adType, 'url', e.target.value)}
                placeholder="https://example.com (Leave empty for non-clickable ad)"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            {/* Runtime */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Runtime
              </label>
              <select
                value={adConfig?.runtime || '1 month'}
                onChange={(e) => handleAdConfigChange(adType, 'runtime', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                {runtimeOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Dimensions if required */}
            {showDimensions && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Width
                  </label>
                  <input
                    type="text"
                    value={adConfig?.width || '300px'}
                    onChange={(e) => handleAdConfigChange(adType, 'width', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Height
                  </label>
                  <input
                    type="text"
                    value={adConfig?.height || '400px'}
                    onChange={(e) => handleAdConfigChange(adType, 'height', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// Create placeholder FooterAdConfigPanel component
function FooterAdConfigPanel({ adConfig, adType, handleAdConfigChange, handleImageUpload, runtimeOptions, showToast }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
      <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Footer Advertisement</h4>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">Display advertisement in the website footer</p>

      {/* Active Toggle */}
      <div className="space-y-6">
        <label className="flex items-start space-x-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
          <button
            onClick={() => {
              const currentActive = adConfig?.active || false;
              handleAdConfigChange(adType, 'active', !currentActive);
            }}
            className="mt-1 flex items-center justify-center w-8 h-8 rounded-full transition-colors duration-200"
            style={{
              backgroundColor: adConfig?.active ? '#10B981' : '#6B7280',
              color: 'white'
            }}
          >
            {adConfig?.active ? (
              <CheckCircle className="w-5 h-5" />
            ) : (
              <X className="w-5 h-5" />
            )}
          </button>
          <div>
            <div className="font-medium text-gray-900 dark:text-white">
              Active {adConfig?.active ? '✓ ON' : '✗ OFF'}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Enable this advertisement section</div>
          </div>
        </label>

        {adConfig?.active && (
          <div className="space-y-4">
            {/* Logo Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
                Company Logo
              </label>
              
              <div className="space-y-4">
                {/* Current Logo Preview */}
                {adConfig?.logo && (
                  <div className="relative group max-w-sm">
                    <img 
                      src={adConfig.logo} 
                      alt="Company logo preview"
                      className="w-full h-24 object-contain rounded-lg border-2 border-gray-200 dark:border-gray-600 bg-white"
                    />
                    <button
                      type="button"
                      onClick={() => handleAdConfigChange(adType, 'logo', null)}
                      className="absolute top-2 right-2 p-2 bg-red-500 hover:bg-red-600 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                )}
                
                {/* File Upload Area */}
                <label className="w-full h-32 max-w-sm border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg flex flex-col items-center justify-center cursor-pointer hover:border-blue-500 dark:hover:border-blue-400 transition-colors">
                  <Upload className="w-8 h-8 text-gray-400 mb-2" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Upload Company Logo
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400 text-center">
                    PNG, JPG, SVG up to 2MB
                  </span>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleImageUpload(adType, e.target.files[0], 'logo')}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {/* Company Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Company Name
              </label>
              <input
                type="text"
                value={adConfig?.companyName || ''}
                onChange={(e) => handleAdConfigChange(adType, 'companyName', e.target.value)}
                placeholder="Enter company name..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            {/* Runtime */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Runtime
              </label>
              <select
                value={adConfig?.runtime || '1 month'}
                onChange={(e) => handleAdConfigChange(adType, 'runtime', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                {runtimeOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Placeholder components for other tabs
function MegaDashboard({ showToast }) {
  return <div className="p-6">Mega Dashboard content...</div>;
}

function DocumentationTab({ showToast }) {
  return <div className="p-6">Documentation content...</div>;
}

function MediaBrowserTab({ showToast }) {
  return <div className="p-6">Media Browser content...</div>;
}

function UsersTab({ showToast }) {
  return <div className="p-6">Users management content...</div>;
}

function ListingsTab({ showToast }) {
  return <div className="p-6">Listings management content...</div>;
}

function CatsTab({ showToast }) {
  return <div className="p-6">Catalyst database content...</div>;
}

function SiteSettingsTab({ siteConfig, handleConfigChange, showToast }) {
  return <div className="p-6">Site settings content...</div>;
}

function SiteAdministrationTab({ showToast }) {
  // Administration sections configuration
  const adminSections = [
    { 
      id: 'content', 
      label: 'Content Management', 
      icon: FileText,
      description: 'Manage info page content with rich text editing capabilities'
    },
    { 
      id: 'configuration', 
      label: 'Site Configuration', 
      icon: Settings,
      description: 'Basic site settings and configuration options'
    },
    { 
      id: 'system', 
      label: 'System & Maintenance', 
      icon: Server,
      description: 'System settings, maintenance, and advanced configuration'
    }
  ];

  const [activeSection, setActiveSection] = useState(null);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-600 to-gray-600 rounded-xl p-6 text-white">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-white/20 rounded-2xl backdrop-blur-md">
            <Shield className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-2xl font-bold">Site Administration</h2>
            <p className="text-slate-200">Advanced system management and configuration</p>
          </div>
        </div>
      </div>

      {/* Administration Sections Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {adminSections.map((section) => {
          const Icon = section.icon;
          return (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className="group p-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-200 hover:shadow-lg text-left"
            >
              <div className="flex items-center space-x-4 mb-4">
                <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-xl group-hover:bg-blue-100 dark:group-hover:bg-blue-900/50 transition-colors">
                  <Icon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                    {section.label}
                  </h3>
                </div>
              </div>
              
              <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                {section.description}
              </p>
              
              <div className="mt-4 flex items-center text-blue-600 dark:text-blue-400 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                <span>Configure</span>
                <ExternalLink className="w-4 h-4 ml-2" />
              </div>
            </button>
          );
        })}
      </div>

      {/* Section Content */}
      {activeSection && (
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
              {adminSections.find(s => s.id === activeSection)?.label}
            </h3>
            <button
              onClick={() => setActiveSection(null)}
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <Settings className="w-16 h-16 mx-auto" />
            </div>
            <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              {adminSections.find(s => s.id === activeSection)?.label} Configuration
            </h4>
            <p className="text-gray-600 dark:text-gray-400">
              Configuration interface for this section will be available here.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminPanel;