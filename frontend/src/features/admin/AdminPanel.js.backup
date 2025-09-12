/**
 * CATALORO - Ultra-Modern Admin Panel
 * Real KPI functionality, complete user management, and site customization
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Users, 
  Package, 
  DollarSign, 
  TrendingUp, 
  Settings, 
  Upload,
  Edit,
  Trash2,
  Ban,
  Building,
  CheckCircle,
  BarChart3,
  PieChart,
  Activity,
  Eye,
  Heart,
  ShoppingCart,
  Star,
  Camera,
  Save,
  X,
  Check,
  User,
  RefreshCw,
  Download,
  AlertTriangle,
  Shield,
  Palette,
  Globe,
  Lock,
  Zap,
  Mail,
  Bell,
  Monitor,
  Smartphone,
  Code,
  Database,
  Server,
  Wifi,
  Search,
  Filter,
  ToggleLeft,
  ToggleRight,
  Target,
  ExternalLink,
  Play,
  Pause,
  Calculator,
  Sliders,
  Layout,
  Type,
  Image as ImageIcon,
  Link as LinkIcon,
  Power,
  Wrench,
  Bug,
  HardDrive,
  Cpu,
  MemoryStick,
  Network,
  Phone,
  CloudUpload,
  Store,
  ArrowRight,
  ArrowDown,
  UserPlus,
  Plus,
  ShoppingBag,
  MessageCircle,
  CreditCard,
  FileText,
  ThumbsUp,
  Truck,
  MapPin,
  Clock,
  CheckSquare,
  Calendar,
  TrendingDown,
  AlertCircle,
  Info,
  HelpCircle,
  BookOpen,
  Layers,
  GitBranch,
  RotateCcw,
  Navigation
} from 'lucide-react';
import { adminService } from '../../services/adminService';
import { useAuth } from '../../context/AuthContext';
import { useMarketplace } from '../../context/MarketplaceContext';
import ContentManagementSystem from './ContentManagementSystem';
import SystemNotificationsManager from './SystemNotificationsManager';
import { useNotifications } from '../../context/NotificationContext';
import usePermissions from '../../hooks/usePermissions';
import { applySiteConfiguration } from '../../utils/siteConfiguration';
import { getTimeRemaining, isAdExpired, activateAd, deactivateExpiredAds, calculateExpirationDate } from '../../utils/adsConfiguration';
import BusinessTab from './BusinessTab';
import PDFExportCenter from './PDFExportCenter';
import MenuSettings from '../../components/admin/MenuSettings';
import FooterManagement from '../../components/admin/FooterManagement';
import DashboardTab from '../../components/admin/tabs/DashboardTab';
import UsersTab from '../../components/admin/tabs/UsersTab';
import ListingsTab from '../../components/admin/tabs/ListingsTab';
import SystemNotificationsList from '../../components/admin/shared/SystemNotificationsList';
import { getTabConfig, TabNavigation, AdminHeader } from '../../components/admin/shared/AdminLayout';

function AdminPanel() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [systemNotifications, setSystemNotifications] = useState([]);
  const [siteConfiguration, setSiteConfiguration] = useState({
    site_title: 'Cataloro Marketplace',
    hero_title: 'Leading European Catalytic Converter Marketplace',
    hero_subtitle: 'Connecting buyers and sellers across the catalyst industry',
    primary_color: '#4F46E5',
    secondary_color: '#7C3AED',
    logo_url: '',
    footer_logo_url: '',
    contact_email: 'contact@cataloro.com',
    support_email: 'support@cataloro.com',
    phone: '+1-800-CATALYST',
    address: '123 Business Avenue, Commerce City, CC 12345',
    social_links: {
      facebook: '',
      twitter: '',
      linkedin: '',
      instagram: ''
    },
    business_hours: 'Monday - Friday: 9:00 AM - 6:00 PM',
    timezone: 'UTC',
    default_language: 'en',
    supported_languages: ['en', 'de', 'fr', 'es'],
    maintenance_mode: false,
    maintenance_message: '',
    analytics_enabled: true,
    google_analytics_id: '',
    facebook_pixel_id: '',
    seo_title: 'Cataloro - Premium Catalytic Converter Marketplace',
    seo_description: 'Europe\'s leading marketplace for catalytic converters and automotive exhaust components.',
    seo_keywords: 'catalytic converter, marketplace, automotive, exhaust, catalyst'
  });

  const { user, showToast } = useAuth();
  const { updateSiteConfig } = useMarketplace();
  const { notifications } = useNotifications(); 
  const { hasPermission } = usePermissions();

  useEffect(() => {
    fetchDashboardData();
    fetchUsers();
    fetchSystemNotifications();
    fetchSiteConfiguration();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const data = await adminService.getDashboardData();
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      showToast?.('Failed to load dashboard data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const usersData = await adminService.getUsers();
      setUsers(usersData);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      showToast?.('Failed to load users', 'error');
    }
  };

  const fetchSystemNotifications = async () => {
    try {
      const notificationsData = await adminService.getSystemNotifications();
      setSystemNotifications(notificationsData);
    } catch (error) {
      console.error('Failed to fetch system notifications:', error);
    }
  };

  const fetchSiteConfiguration = async () => {
    try {
      const config = await adminService.getSiteConfiguration();
      if (config) {
        setSiteConfiguration(config);
      }
    } catch (error) {
      console.error('Failed to fetch site configuration:', error);
    }
  };

  const updateSiteConfiguration = async (newConfig) => {
    try {
      const updatedConfig = await adminService.updateSiteConfiguration(newConfig);
      setSiteConfiguration(updatedConfig);
      updateSiteConfig(updatedConfig);
      applySiteConfiguration(updatedConfig);
      showToast?.('Site configuration updated successfully', 'success');
    } catch (error) {
      console.error('Failed to update site configuration:', error);
      showToast?.('Failed to update site configuration', 'error');
    }
  };

  const handleUpdateUser = async (userData) => {
    try {
      const updatedUser = await adminService.updateUser(userData);
      setUsers(users.map(u => u.id === updatedUser.id ? updatedUser : u));
      showToast?.('User updated successfully', 'success');
    } catch (error) {
      console.error('Failed to update user:', error);
      showToast?.('Failed to update user', 'error');
    }
  };

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3, component: DashboardTab },
    { id: 'users', label: 'Users', icon: Users, component: UsersTab },
    { id: 'listings', label: 'Listings', icon: Package, component: ListingsTab },
    { id: 'business', label: 'Business', icon: Building, component: BusinessTab },
    { id: 'ads', label: 'Ads Management', icon: Target, component: AdsManagementTab },
    { id: 'content', label: 'Content', icon: FileText, component: ContentManagementTab },
    { id: 'settings', label: 'Settings', icon: Settings, component: SettingsTab },
    { id: 'catalyst', label: 'Cat Database', icon: Database, component: CatDatabaseTab },
    { id: 'site-admin', label: 'Site Administration', icon: Globe, component: SiteAdministrationTab },
    { id: 'export', label: 'PDF Export', icon: Download, component: PDFExportCenter }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading admin panel...</p>
        </div>
      </div>
    );
  }

  if (!user?.isAdmin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center p-8">
          <Shield className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Access Denied</h1>
          <p className="text-gray-600 dark:text-gray-400">You don't have permission to access the admin panel.</p>
        </div>
      </div>
    );
  }

  const renderTabContent = () => {
    const activeTabConfig = tabs.find(tab => tab.id === activeTab);
    if (!activeTabConfig) return null;

    const Component = activeTabConfig.component;
    
    switch (activeTab) {
      case 'dashboard':
        return <DashboardTab dashboardData={dashboardData} showToast={showToast} />;
      case 'users':
        return <UsersTab users={users} onUpdateUser={handleUpdateUser} showToast={showToast} />;
      case 'listings':
        return <ListingsTab showToast={showToast} />;
      case 'business':
        return <BusinessTab showToast={showToast} />;
      case 'ads':
        return <AdsManagementTab showToast={showToast} />;
      case 'content':
        return <ContentManagementTab showToast={showToast} />;
      case 'settings':
        return <SettingsTab 
          siteConfiguration={siteConfiguration} 
          onUpdateConfiguration={updateSiteConfiguration}
          showToast={showToast} 
        />;
      case 'catalyst':
        return <CatDatabaseTab showToast={showToast} />;
      case 'site-admin':
        return <SiteAdministrationTab showToast={showToast} />;
      case 'export':
        return <PDFExportCenter showToast={showToast} />;
      default:
        return <DashboardTab dashboardData={dashboardData} showToast={showToast} />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <AdminHeader user={user} />
      
      <div className="flex">
        <TabNavigation 
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
        
        <main className="flex-1 p-8">
          <div className="max-w-7xl mx-auto">
            {renderTabContent()}
          </div>
        </main>
      </div>

      {/* System Notifications */}
      <SystemNotificationsList 
        notifications={systemNotifications}
        onDismiss={(id) => {
          setSystemNotifications(prev => prev.filter(n => n.id !== id));
        }}
      />
    </div>
  );
}

// Placeholder components for tabs that haven't been extracted yet
function AdsManagementTab({ showToast }) {
  return (
    <div className="cataloro-card-glass p-8 text-center">
      <Target className="w-16 h-16 mx-auto mb-4 text-yellow-500" />
      <h2 className="text-2xl font-bold mb-4">Ads Management</h2>
      <p className="text-gray-600 dark:text-gray-400">Ads management functionality will be available soon.</p>
    </div>
  );
}

function ContentManagementTab({ showToast }) {
  return (
    <div className="cataloro-card-glass p-8 text-center">
      <FileText className="w-16 h-16 mx-auto mb-4 text-blue-500" />
      <h2 className="text-2xl font-bold mb-4">Content Management</h2>
      <p className="text-gray-600 dark:text-gray-400">Content management functionality will be available soon.</p>
    </div>
  );
}

function SettingsTab({ siteConfiguration, onUpdateConfiguration, showToast }) {
  return (
    <div className="cataloro-card-glass p-8 text-center">
      <Settings className="w-16 h-16 mx-auto mb-4 text-purple-500" />
      <h2 className="text-2xl font-bold mb-4">Site Settings</h2>
      <p className="text-gray-600 dark:text-gray-400">Site settings functionality will be available soon.</p>
    </div>
  );
}

function CatDatabaseTab({ showToast }) {
  return (
    <div className="cataloro-card-glass p-8 text-center">
      <Database className="w-16 h-16 mx-auto mb-4 text-green-500" />
      <h2 className="text-2xl font-bold mb-4">Catalyst Database</h2>
      <p className="text-gray-600 dark:text-gray-400">Catalyst database functionality will be available soon.</p>
    </div>
  );
}

function SiteAdministrationTab({ showToast }) {
  return (
    <div className="cataloro-card-glass p-8 text-center">
      <Globe className="w-16 h-16 mx-auto mb-4 text-indigo-500" />
      <h2 className="text-2xl font-bold mb-4">Site Administration</h2>
      <p className="text-gray-600 dark:text-gray-400">Site administration functionality will be available soon.</p>
    </div>
  );
}

export default AdminPanel;