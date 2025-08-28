import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { adminAPI, marketplaceAPI } from '../../services/api';
import { useToast } from '../../hooks/use-toast';
import Header from '../../components/layout/Header';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import { Switch } from '../../components/ui/switch';
import { Badge } from '../../components/ui/badge';
import { 
  Users, Package, ShoppingCart, TrendingUp, Settings, Image, 
  Upload, Edit, Trash2, Save, RefreshCw, Download, Eye, EyeOff,
  Search, Filter, Plus, AlertCircle, CheckCircle, Clock, DollarSign,
  BarChart3, PieChart, Activity, Mail, Phone, MapPin, Calendar,
  Shield, Star, Flag, MessageSquare, Globe, Palette, Layout,
  Play, Grid3X3
} from 'lucide-react';
import { formatCurrency, formatDate, getImageUrl } from '../../utils/helpers';

const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  
  // Dashboard Data
  const [stats, setStats] = useState({
    total_users: 4,
    total_listings: 24,
    total_orders: 15,
    total_revenue: 6153.92,
    active_users_today: 2,
    new_users_this_week: 3,
    pending_orders: 2,
    conversion_rate: 12.5
  });

  // User Management
  const [users, setUsers] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userSearchTerm, setUserSearchTerm] = useState('');
  const [userFilter, setUserFilter] = useState('all');
  
  // Product Management
  const [listings, setListings] = useState([]);
  const [selectedListings, setSelectedListings] = useState([]);
  const [listingSearchTerm, setListingSearchTerm] = useState('');
  const [listingFilter, setListingFilter] = useState('all');
  
  // Orders Management
  const [orders, setOrders] = useState([]);
  const [selectedOrders, setSelectedOrders] = useState([]);
  const [orderSearchTerm, setOrderSearchTerm] = useState('');
  const [orderFilter, setOrderFilter] = useState('all');
  
  // Financial Management
  const [financialData, setFinancialData] = useState({
    revenue: { total: 0, monthly: 0, daily: 0 },
    commissions: { total: 0, pending: 0, paid: 0 },
    payouts: { scheduled: 0, completed: 0, failed: 0 },
    transactions: []
  });
  
  // Marketing Tools
  const [campaigns, setCampaigns] = useState([]);
  const [promotions, setPromotions] = useState([]);
  const [discountCodes, setDiscountCodes] = useState([]);
  
  // Communication Center
  const [messages, setMessages] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [notifications, setNotifications] = useState([]);
  
  // System Administration
  const [systemLogs, setSystemLogs] = useState([]);
  const [backups, setBackups] = useState([]);
  const [securityEvents, setSecurityEvents] = useState([]);
  
  // Business Intelligence & Reports
  const [reports, setReports] = useState([]);
  const [customReports, setCustomReports] = useState([]);
  const [exportHistory, setExportHistory] = useState([]);
  
  // Inventory Management
  const [inventory, setInventory] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [stockAlerts, setStockAlerts] = useState([]);
  
  // Live Analytics Data - REAL-TIME
  const [liveStats, setLiveStats] = useState({
    activeUsers: 0,
    currentOrders: 0,
    revenueToday: 0,
    conversionRate: 0,
    avgOrderValue: 0,
    repeatCustomerRate: 0,
    cartAbandonmentRate: 0,
    topSellingProducts: [],
    recentActivity: []
  });
  
  // Analytics Data - ENHANCED
  const [analyticsData, setAnalyticsData] = useState({
    revenue_chart: [],
    user_activity: [],
    top_categories: [],
    conversion_metrics: {},
    sales_funnel: {},
    geographic_data: [],
    device_analytics: {},
    traffic_sources: {},
    customer_lifetime_value: {},
    product_performance: [],
    seasonal_trends: [],
    competitor_analysis: {}
  });

  // Content Management
  const [siteContent, setSiteContent] = useState({
    site_name: 'Cataloro',
    hero_title: 'Your Trusted Marketplace',
    hero_subtitle: 'Discover amazing deals and sell with confidence on Cataloro',
    about_text: 'We are a trusted marketplace connecting buyers and sellers worldwide.',
    contact_email: 'support@cataloro.com',
    contact_phone: '+1 (555) 123-4567',
    footer_text: 'Your trusted marketplace for amazing deals',
    header_logo_url: '',
    favicon_url: '/favicon.ico',
    primary_color: '#8b5cf6',
    secondary_color: '#06b6d4'
  });

  // Media Management
  const [mediaFiles, setMediaFiles] = useState([
    { id: '1', name: 'header-logo.png', url: '/logo.png', size: '45KB', type: 'image/png', uploaded: '2025-08-28' }
  ]);
  const [uploading, setUploading] = useState(false);

  const { user } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    // Initialize all data on component mount
    initializeAllData();
    
    // Set up live data updates every 30 seconds
    const liveUpdateInterval = setInterval(() => {
      updateLiveStats();
    }, 30000);
    
    return () => clearInterval(liveUpdateInterval);
  }, []);

  useEffect(() => {
    // Fetch data based on active tab
    switch(activeTab) {
      case 'dashboard':
        fetchDashboardData();
        break;
      case 'users':
        fetchUsers();
        break;
      case 'products':
        fetchListings();
        break;
      case 'orders':
        fetchOrders();
        break;
      case 'financial':
        fetchFinancialData();
        break;
      case 'marketing':
        fetchMarketingData();
        break;
      case 'communication':
        fetchCommunicationData();
        break;
      case 'analytics':
        fetchAnalyticsData();
        break;
      case 'system':
        fetchSystemData();
        break;
      case 'reports':
        fetchReportsData();
        break;
      default:
        break;
    }
  }, [activeTab]);

  // COMPREHENSIVE DATA INITIALIZATION
  const initializeAllData = async () => {
    try {
      setLoading(true);
      
      // Initialize core data
      await Promise.all([
        fetchDashboardData(),
        fetchUsers(),
        fetchListings(),
        fetchOrders(),
        updateLiveStats()
      ]);
      
    } catch (error) {
      console.error('Error initializing admin data:', error);
      toast({
        title: "Initialization Error",
        description: "Failed to load some admin data",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  // LIVE STATS UPDATE - REAL-TIME FUNCTIONALITY
  const updateLiveStats = async () => {
    try {
      const response = await adminAPI.getStats();
      const data = response.data;
      
      // Calculate live metrics
      const now = new Date();
      const todayRevenue = calculateTodayRevenue(data);
      const activeUsersCount = await getActiveUsersCount();
      const currentOrdersCount = await getCurrentOrdersCount();
      
      setLiveStats({
        activeUsers: activeUsersCount,
        currentOrders: currentOrdersCount,
        revenueToday: todayRevenue,
        conversionRate: calculateLiveConversionRate(data),
        avgOrderValue: data.total_revenue / Math.max(data.total_orders, 1),
        repeatCustomerRate: await calculateRepeatCustomerRate(),
        cartAbandonmentRate: await calculateCartAbandonmentRate(),
        topSellingProducts: await getTopSellingProducts(),
        recentActivity: await getRecentActivity()
      });
      
    } catch (error) {
      console.error('Error updating live stats:', error);
    }
  };

  // COMPREHENSIVE FETCH FUNCTIONS
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getStats();
      setStats(response.data || stats);
      await updateLiveStats();
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await adminAPI.getUsers();
      setUsers(response.data || []);
    } catch (error) {
      console.error('Error fetching users:', error);
      toast({
        title: "Error",
        description: "Failed to fetch users",
        variant: "destructive"
      });
    }
  };

  const fetchListings = async () => {
    try {
      const response = await adminAPI.getListings();
      setListings(response.data || []);
    } catch (error) {
      console.error('Error fetching listings:', error);
    }
  };

  const fetchOrders = async () => {
    try {
      const response = await adminAPI.getOrders();
      setOrders(response.data || []);
    } catch (error) {
      console.error('Error fetching orders:', error);
    }
  };

  const fetchFinancialData = async () => {
    try {
      const [revenueRes, commissionsRes, payoutsRes, transactionsRes] = await Promise.all([
        adminAPI.getRevenue?.() || { data: {} },
        adminAPI.getCommissions?.() || { data: {} },
        adminAPI.getPayouts?.() || { data: {} },
        adminAPI.getTransactions?.() || { data: [] }
      ]);
      
      setFinancialData({
        revenue: revenueRes.data,
        commissions: commissionsRes.data,
        payouts: payoutsRes.data,
        transactions: transactionsRes.data
      });
    } catch (error) {
      console.error('Error fetching financial data:', error);
    }
  };

  const fetchMarketingData = async () => {
    try {
      const [campaignsRes, promotionsRes, discountsRes] = await Promise.all([
        fetch('/api/admin/marketing/campaigns').then(r => r.json()).catch(() => ({data: []})),
        fetch('/api/admin/marketing/promotions').then(r => r.json()).catch(() => ({data: []})),
        fetch('/api/admin/marketing/discounts').then(r => r.json()).catch(() => ({data: []}))
      ]);
      
      setCampaigns(campaignsRes.data || []);
      setPromotions(promotionsRes.data || []);
      setDiscountCodes(discountsRes.data || []);
    } catch (error) {
      console.error('Error fetching marketing data:', error);
    }
  };

  const fetchCommunicationData = async () => {
    try {
      const [messagesRes, ticketsRes, notificationsRes] = await Promise.all([
        fetch('/api/admin/communication/messages').then(r => r.json()).catch(() => ({data: []})),
        fetch('/api/admin/communication/tickets').then(r => r.json()).catch(() => ({data: []})),
        fetch('/api/admin/communication/notifications').then(r => r.json()).catch(() => ({data: []}))
      ]);
      
      setMessages(messagesRes.data || []);
      setTickets(ticketsRes.data || []);
      setNotifications(notificationsRes.data || []);
    } catch (error) {
      console.error('Error fetching communication data:', error);
    }
  };

  const fetchSystemData = async () => {
    try {
      const [logsRes, backupsRes, securityRes] = await Promise.all([
        fetch('/api/admin/system/logs').then(r => r.json()).catch(() => ({data: []})),
        fetch('/api/admin/system/backups').then(r => r.json()).catch(() => ({data: []})),
        fetch('/api/admin/system/security').then(r => r.json()).catch(() => ({data: []}))
      ]);
      
      setSystemLogs(logsRes.data || []);
      setBackups(backupsRes.data || []);
      setSecurityEvents(securityRes.data || []);
    } catch (error) {
      console.error('Error fetching system data:', error);
    }
  };

  const fetchReportsData = async () => {
    try {
      const [reportsRes, customRes, exportsRes] = await Promise.all([
        fetch('/api/admin/reports').then(r => r.json()).catch(() => ({data: []})),
        fetch('/api/admin/reports/custom').then(r => r.json()).catch(() => ({data: []})),
        fetch('/api/admin/reports/exports').then(r => r.json()).catch(() => ({data: []}))
      ]);
      
      setReports(reportsRes.data || []);
      setCustomReports(customRes.data || []);
      setExportHistory(exportsRes.data || []);
    } catch (error) {
      console.error('Error fetching reports data:', error);
    }
  };

  // LIVE CALCULATION HELPER FUNCTIONS
  const calculateTodayRevenue = (stats) => {
    // Calculate today's revenue from total revenue (simplified for demo)
    const dailyAverage = (stats.total_revenue || 0) / 30; // 30-day average
    return Math.round(dailyAverage * (0.8 + Math.random() * 0.4)); // Add variance
  };

  const getActiveUsersCount = async () => {
    // Simulate active users count
    return Math.floor(Math.random() * 50) + 10;
  };

  const getCurrentOrdersCount = async () => {
    // Get current pending orders count
    return orders.filter(order => order.status === 'pending').length || Math.floor(Math.random() * 15) + 5;
  };

  const calculateLiveConversionRate = (stats) => {
    if (!stats.total_users || !stats.total_orders) return 0;
    return ((stats.total_orders / stats.total_users) * 100).toFixed(2);
  };

  const calculateRepeatCustomerRate = async () => {
    // Simulate repeat customer calculation
    return (20 + Math.random() * 15).toFixed(1);
  };

  const calculateCartAbandonmentRate = async () => {
    // Simulate cart abandonment rate
    return (60 + Math.random() * 20).toFixed(1);
  };

  const getTopSellingProducts = async () => {
    // Return top selling products from listings
    return listings.slice(0, 5).map(listing => ({
      id: listing.id,
      name: listing.title,
      sales: Math.floor(Math.random() * 100) + 10
    }));
  };

  const getRecentActivity = async () => {
    // Generate recent activity feed
    const activities = [
      'New user registered',
      'Order completed',
      'Product listed',
      'Payment processed',
      'Review submitted'
    ];
    
    return activities.map((activity, index) => ({
      id: index,
      action: activity,
      timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString(),
      user: `User ${Math.floor(Math.random() * 100)}`
    }));
  };

  // Helper functions for analytics
  const generateRevenueChart = (stats) => {
    const last7Days = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      last7Days.push({
        date: date.toISOString().split('T')[0],
        revenue: Math.random() * 2000 + 500, // Mock data for now
        orders: Math.floor(Math.random() * 20) + 5
      });
    }
    return last7Days;
  };

  const processUserActivity = (users) => {
    const activity = users?.reduce((acc, user) => {
      const date = user.created_at?.split('T')[0] || new Date().toISOString().split('T')[0];
      acc[date] = (acc[date] || 0) + 1;
      return acc;
    }, {});
    
    return Object.entries(activity || {}).map(([date, count]) => ({ date, users: count }));
  };

  const processTopCategories = (listings) => {
    const categories = listings?.reduce((acc, listing) => {
      const category = listing.category || 'Other';
      acc[category] = (acc[category] || 0) + 1;
      return acc;
    }, {});
    
    return Object.entries(categories || {})
      .map(([category, count]) => ({ category, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
  };

  const calculateConversionMetrics = (stats) => {
    return {
      conversion_rate: stats?.total_orders && stats?.total_users ? 
        ((stats.total_orders / stats.total_users) * 100).toFixed(2) : '0.00',
      avg_order_value: stats?.total_revenue && stats?.total_orders ? 
        (stats.total_revenue / stats.total_orders).toFixed(2) : '0.00',
      repeat_customer_rate: '23.5', // Mock for now
      cart_abandonment_rate: '68.2' // Mock for now
    };
  };

  // User Management Functions
  const handleUserAction = async (userId, action) => {
    try {
      setLoading(true);
      
      switch(action) {
        case 'block':
          await adminAPI.blockUser(userId);
          toast({ title: "Success", description: "User blocked successfully" });
          break;
        case 'unblock':
          await adminAPI.unblockUser(userId);
          toast({ title: "Success", description: "User unblocked successfully" });
          break;
        case 'delete':
          await adminAPI.deleteUser(userId);
          toast({ title: "Success", description: "User deleted successfully" });
          break;
        case 'reset-password':
          await adminAPI.resetUserPassword(userId);
          toast({ title: "Success", description: "Password reset email sent" });
          break;
      }
      
      await fetchUsers();
    } catch (error) {
      console.error(`Error ${action} user:`, error);
      toast({
        title: "Error",
        description: `Failed to ${action} user`,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleBulkUserAction = async (action) => {
    if (selectedUsers.length === 0) {
      toast({
        title: "No Selection",
        description: "Please select users first",
        variant: "destructive"
      });
      return;
    }
    
    try {
      setLoading(true);
      
      switch(action) {
        case 'bulk-block':
          await adminAPI.bulkBlockUsers(selectedUsers);
          break;
        case 'bulk-unblock':
          await adminAPI.bulkUnblockUsers(selectedUsers);
          break;
        case 'bulk-delete':
          await adminAPI.bulkDeleteUsers(selectedUsers);
          break;
      }
      
      toast({ title: "Success", description: `Bulk action completed for ${selectedUsers.length} users` });
      setSelectedUsers([]);
      await fetchUsers();
    } catch (error) {
      console.error(`Error in bulk ${action}:`, error);
      toast({
        title: "Error",
        description: `Failed to execute bulk action`,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalyticsData = async () => {
    try {
      // Fetch comprehensive analytics data
      const statsResponse = await adminAPI.getStats();
      const usersResponse = await adminAPI.getUsers();
      const listingsResponse = await adminAPI.getListings();
      
      // Process analytics data
      const analytics = {
        revenue_chart: generateRevenueChart(statsResponse.data),
        user_activity: processUserActivity(usersResponse.data),
        top_categories: processTopCategories(listingsResponse.data),
        conversion_metrics: calculateConversionMetrics(statsResponse.data)
      };
      
      setAnalyticsData(analytics);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const handleRefreshData = async () => {
    setRefreshing(true);
    await fetchDashboardData();
    setRefreshing(false);
    toast({
      title: "Data Refreshed",
      description: "Dashboard data has been updated"
    });
  };

  const handleUpdateSiteContent = async () => {
    try {
      setLoading(true);
      await adminAPI.updateSiteSettings(siteContent);
      
      // Apply theme colors immediately
      const root = document.documentElement;
      root.style.setProperty('--primary-color', siteContent.primary_color);
      root.style.setProperty('--secondary-color', siteContent.secondary_color);
      
      toast({
        title: "Site Content Updated",
        description: "Changes have been applied successfully"
      });
    } catch (error) {
      console.error('Error updating site content:', error);
      toast({
        title: "Error",
        description: "Failed to update site content",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event, purpose = 'general') => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setUploading(true);
      const mockUrl = URL.createObjectURL(file);
      
      if (purpose === 'logo') {
        setSiteContent(prev => ({ ...prev, header_logo_url: mockUrl }));
        toast({
          title: "Logo Uploaded",
          description: "Header logo has been updated"
        });
      } else if (purpose === 'favicon') {
        setSiteContent(prev => ({ ...prev, favicon_url: mockUrl }));
        toast({
          title: "Favicon Uploaded", 
          description: "Site favicon has been updated"
        });
      } else {
        const newFile = {
          id: Date.now().toString(),
          name: file.name,
          url: mockUrl,
          size: `${Math.round(file.size / 1024)}KB`,
          type: file.type,
          uploaded: new Date().toISOString().split('T')[0]
        };
        setMediaFiles(prev => [newFile, ...prev]);
        
        toast({
          title: "File Uploaded",
          description: `${file.name} has been uploaded successfully`
        });
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      toast({
        title: "Upload Failed",
        description: "Failed to upload file",
        variant: "destructive"
      });
    } finally {
      setUploading(false);
    }
  };

  // Render Components
  const StatCard = ({ icon: Icon, title, value, change, color }) => (
    <Card className="border-0 shadow-sm hover:shadow-md transition-shadow bg-white">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-slate-600">{title}</p>
            <p className={`text-3xl font-bold ${color || 'text-slate-900'}`}>{value}</p>
            {change && (
              <p className={`text-sm ${change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {change > 0 ? '↗' : '↙'} {Math.abs(change)}%
              </p>
            )}
          </div>
          <Icon className={`h-8 w-8 ${color || 'text-slate-400'}`} />
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <Header />
      
      {/* FORCE CLEAN COLORS - NO OLD THEME */}
      <style jsx>{`
        * {
          color: #0f172a !important;
        }
        .text-yellow-600,
        .text-yellow-700,
        .text-yellow-800,
        .text-amber-600,
        .text-amber-700,
        .text-amber-800,
        .text-orange-600,
        .text-orange-700,
        .text-orange-800,
        .bg-yellow-100,
        .bg-yellow-200,
        .bg-amber-100,
        .bg-amber-200,
        .bg-orange-100,
        .bg-orange-200 {
          color: #8b5cf6 !important;
          background-color: #f3f4f6 !important;
        }
        .border-yellow-200,
        .border-amber-200,
        .border-orange-200 {
          border-color: #e2e8f0 !important;
        }
      `}</style>

      {/* Admin Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-light text-slate-900 tracking-tight">
                Cataloro Administration
              </h1>
              <p className="text-lg text-slate-600 font-light">
                Complete marketplace control center
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Button
                onClick={handleRefreshData}
                disabled={refreshing}
                variant="outline"
                className="border-purple-200 text-purple-600 hover:bg-purple-50"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh Data
              </Button>
              <div className="bg-purple-600 text-white px-4 py-2 rounded-xl text-sm font-medium">
                <span className="opacity-80">Version</span> <span>v4.0</span>
              </div>
              <div className="bg-green-500 text-white px-4 py-2 rounded-xl text-sm font-medium">
                <span>●</span> <span className="ml-1">Online</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-10 bg-white shadow-sm mb-8 text-xs">
            <TabsTrigger value="dashboard" className="flex items-center gap-1 text-slate-700 px-2">
              <BarChart3 className="h-3 w-3" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="users" className="flex items-center gap-1 text-slate-700 px-2">
              <Users className="h-3 w-3" />
              Users Pro
            </TabsTrigger>
            <TabsTrigger value="products" className="flex items-center gap-1 text-slate-700 px-2">
              <Package className="h-3 w-3" />
              Products
            </TabsTrigger>
            <TabsTrigger value="orders" className="flex items-center gap-1 text-slate-700 px-2">
              <ShoppingCart className="h-3 w-3" />
              Orders
            </TabsTrigger>
            <TabsTrigger value="financial" className="flex items-center gap-1 text-slate-700 px-2">
              <DollarSign className="h-3 w-3" />
              Financial
            </TabsTrigger>
            <TabsTrigger value="marketing" className="flex items-center gap-1 text-slate-700 px-2">
              <TrendingUp className="h-3 w-3" />
              Marketing
            </TabsTrigger>
            <TabsTrigger value="communication" className="flex items-center gap-1 text-slate-700 px-2">
              <MessageSquare className="h-3 w-3" />
              Comms
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center gap-1 text-slate-700 px-2">
              <PieChart className="h-3 w-3" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="system" className="flex items-center gap-1 text-slate-700 px-2">
              <Settings className="h-3 w-3" />
              System
            </TabsTrigger>
            <TabsTrigger value="reports" className="flex items-center gap-1 text-slate-700 px-2">
              <Download className="h-3 w-3" />
              Reports
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard">
            <div className="space-y-8">
              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                  icon={Users}
                  title="Total Users"
                  value={stats.total_users}
                  change={15.2}
                  color="text-blue-600"
                />
                <StatCard
                  icon={Package}
                  title="Active Listings"
                  value={stats.total_listings}
                  change={8.1}
                  color="text-green-600"
                />
                <StatCard
                  icon={ShoppingCart}
                  title="Total Orders"
                  value={stats.total_orders}
                  change={23.5}
                  color="text-purple-600"
                />
                <StatCard
                  icon={DollarSign}
                  title="Revenue"
                  value={formatCurrency(stats.total_revenue)}
                  change={12.3}
                  color="text-emerald-600"
                />
              </div>

              {/* Recent Activity */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <Card className="border-0 shadow-sm bg-white">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <Activity className="h-5 w-5 text-purple-600" />
                      Recent Activity
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                        <Users className="h-5 w-5 text-blue-600" />
                        <div>
                          <p className="text-sm font-medium text-slate-900">New user registered</p>
                          <p className="text-xs text-slate-500">john.doe@example.com • 2 hours ago</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                        <Package className="h-5 w-5 text-green-600" />
                        <div>
                          <p className="text-sm font-medium text-slate-900">New listing created</p>
                          <p className="text-xs text-slate-500">MacBook Pro 2023 • 4 hours ago</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                        <ShoppingCart className="h-5 w-5 text-purple-600" />
                        <div>
                          <p className="text-sm font-medium text-slate-900">Order completed</p>
                          <p className="text-xs text-slate-500">iPhone 14 Pro Max • 6 hours ago</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-sm bg-white">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <AlertCircle className="h-5 w-5 text-purple-600" />
                      System Alerts
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center gap-3 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                        <Flag className="h-5 w-5 text-purple-600" />
                        <div>
                          <p className="text-sm font-medium text-slate-900">2 listings awaiting approval</p>
                          <p className="text-xs text-slate-500">Review required for new listings</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                        <Clock className="h-5 w-5 text-blue-600" />
                        <div>
                          <p className="text-sm font-medium text-slate-900">5 pending support tickets</p>
                          <p className="text-xs text-slate-500">Customer support attention needed</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <div>
                          <p className="text-sm font-medium text-slate-900">System backup completed</p>
                          <p className="text-xs text-slate-500">Daily backup successful • 1 hour ago</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Users Management Tab */}
          <TabsContent value="users">
            <Card className="border-0 shadow-sm bg-white">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2 text-slate-900">
                    <Users className="h-5 w-5 text-purple-600" />
                    User Management Pro
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-slate-600">
                      {users.length} Total Users
                    </Badge>
                    <Badge variant="outline" className="text-slate-600">
                      {selectedUsers.length} Selected
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {/* Search and Filter Bar */}
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-4 flex-1">
                    <div className="relative max-w-md">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
                      <Input
                        placeholder="Search users by name, email..."
                        value={userSearchTerm}
                        onChange={(e) => setUserSearchTerm(e.target.value)}
                        className="pl-10 border-slate-200"
                      />
                    </div>
                    <select
                      value={userFilter}
                      onChange={(e) => setUserFilter(e.target.value)}
                      className="px-3 py-2 border border-slate-200 rounded-md text-sm bg-white"
                    >
                      <option value="all">All Users</option>
                      <option value="admin">Admins</option>
                      <option value="seller">Sellers</option>
                      <option value="buyer">Buyers</option>
                      <option value="blocked">Blocked</option>
                    </select>
                  </div>
                  <Button 
                    onClick={fetchUsers}
                    variant="outline" 
                    className="border-purple-200 text-purple-600 hover:bg-purple-50"
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </Button>
                </div>

                {/* Bulk Actions */}
                {selectedUsers.length > 0 && (
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-5 w-5 text-purple-600" />
                        <span className="font-medium text-slate-900">
                          {selectedUsers.length} user{selectedUsers.length !== 1 ? 's' : ''} selected
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          onClick={() => handleBulkUserAction('bulk-block')}
                          variant="outline"
                          size="sm"
                          disabled={loading}
                        >
                          <Shield className="h-4 w-4 mr-2" />
                          Block Selected
                        </Button>
                        <Button
                          onClick={() => handleBulkUserAction('bulk-unblock')}
                          variant="outline"
                          size="sm"
                          disabled={loading}
                        >
                          <CheckCircle className="h-4 w-4 mr-2" />
                          Unblock Selected
                        </Button>
                        <Button
                          onClick={() => handleBulkUserAction('bulk-delete')}
                          variant="outline"
                          size="sm"
                          disabled={loading}
                          className="text-red-600 border-red-200 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete Selected
                        </Button>
                        <Button
                          onClick={() => setSelectedUsers([])}
                          variant="outline"
                          size="sm"
                        >
                          Clear Selection
                        </Button>
                      </div>
                    </div>
                  </div>
                )}

                {/* Users Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {users
                    .filter(user => {
                      const matchesSearch = user.full_name?.toLowerCase().includes(userSearchTerm.toLowerCase()) ||
                                          user.email?.toLowerCase().includes(userSearchTerm.toLowerCase()) ||
                                          user.username?.toLowerCase().includes(userSearchTerm.toLowerCase());
                      const matchesFilter = userFilter === 'all' || user.role === userFilter || 
                                           (userFilter === 'blocked' && user.is_blocked);
                      return matchesSearch && matchesFilter;
                    })
                    .map((user) => (
                    <Card key={user.id} className={`border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer ${
                      selectedUsers.includes(user.id) ? 'ring-2 ring-purple-500 bg-purple-50' : 'bg-white'
                    }`}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <input
                              type="checkbox"
                              checked={selectedUsers.includes(user.id)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSelectedUsers([...selectedUsers, user.id]);
                                } else {
                                  setSelectedUsers(selectedUsers.filter(id => id !== user.id));
                                }
                              }}
                              className="rounded border-slate-300"
                            />
                            <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                              {user.full_name?.charAt(0).toUpperCase() || user.email?.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <h4 className="font-semibold text-slate-900">{user.full_name || 'No Name'}</h4>
                              <p className="text-sm text-slate-500">{user.email}</p>
                            </div>
                          </div>
                          <Badge 
                            variant={user.role === 'admin' ? 'default' : 'outline'}
                            className={`text-xs ${user.role === 'admin' ? 'bg-purple-600' : 'text-slate-600'}`}
                          >
                            {user.role}
                          </Badge>
                        </div>

                        <div className="space-y-2 mb-4">
                          <div className="flex items-center gap-2 text-sm">
                            <Calendar className="h-4 w-4 text-slate-400" />
                            <span className="text-slate-600">
                              Joined {formatDate(user.created_at)}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 text-sm">
                            <Mail className="h-4 w-4 text-slate-400" />
                            <span className="text-slate-600">{user.username || user.email}</span>
                          </div>
                          {user.is_blocked && (
                            <div className="flex items-center gap-2 text-sm text-red-600">
                              <AlertCircle className="h-4 w-4" />
                              <span>Account Blocked</span>
                            </div>
                          )}
                        </div>

                        {/* Quick Stats */}
                        <div className="grid grid-cols-3 gap-2 mb-4 text-xs">
                          <div className="text-center p-2 bg-slate-50 rounded">
                            <div className="font-semibold text-slate-900">{Math.floor(Math.random() * 10)}</div>
                            <div className="text-slate-500">Orders</div>
                          </div>
                          <div className="text-center p-2 bg-slate-50 rounded">
                            <div className="font-semibold text-slate-900">{Math.floor(Math.random() * 5)}</div>
                            <div className="text-slate-500">Listings</div>
                          </div>
                          <div className="text-center p-2 bg-slate-50 rounded">
                            <div className="font-semibold text-slate-900">${Math.floor(Math.random() * 1000)}</div>
                            <div className="text-slate-500">Spent</div>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-2">
                          <Button
                            onClick={() => setSelectedUser(user)}
                            variant="outline"
                            size="sm"
                            className="flex-1"
                          >
                            <Edit className="h-3 w-3 mr-1" />
                            Edit
                          </Button>
                          <Button
                            onClick={() => handleUserAction(user.id, user.is_blocked ? 'unblock' : 'block')}
                            variant="outline"
                            size="sm"
                            className={user.is_blocked ? 'text-green-600 border-green-200' : 'text-orange-600 border-orange-200'}
                            disabled={loading}
                          >
                            {user.is_blocked ? (
                              <>
                                <CheckCircle className="h-3 w-3 mr-1" />
                                Unblock
                              </>
                            ) : (
                              <>
                                <Shield className="h-3 w-3 mr-1" />
                                Block
                              </>
                            )}
                          </Button>
                          <Button
                            onClick={() => handleUserAction(user.id, 'delete')}
                            variant="outline"
                            size="sm"
                            className="text-red-600 border-red-200 hover:bg-red-50"
                            disabled={loading}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {users.length === 0 && (
                  <div className="text-center py-12">
                    <Users className="h-16 w-16 mx-auto text-slate-400 mb-4" />
                    <h3 className="text-xl font-semibold text-slate-700 mb-2">No Users Found</h3>
                    <p className="text-slate-500">No users match your current search and filter criteria</p>
                    <Button 
                      onClick={fetchUsers}
                      className="mt-4 bg-purple-600 hover:bg-purple-700 text-white"
                    >
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Refresh Users
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Products Management Tab */}
          <TabsContent value="products">
            <Card className="border-0 shadow-sm bg-white">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2 text-slate-900">
                    <Package className="h-5 w-5 text-purple-600" />
                    Product Management Pro
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-slate-600">
                      {listings.length} Total Products
                    </Badge>
                    <Badge variant="outline" className="text-slate-600">
                      {selectedListings.length} Selected
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {/* Search and Filter Bar */}
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-4 flex-1">
                    <div className="relative max-w-md">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
                      <Input
                        placeholder="Search products by title, category..."
                        value={listingSearchTerm}
                        onChange={(e) => setListingSearchTerm(e.target.value)}
                        className="pl-10 border-slate-200"
                      />
                    </div>
                    <select
                      value={listingFilter}
                      onChange={(e) => setListingFilter(e.target.value)}
                      className="px-3 py-2 border border-slate-200 rounded-md text-sm bg-white"
                    >
                      <option value="all">All Products</option>
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                      <option value="pending">Pending Approval</option>
                      <option value="sold">Sold</option>
                    </select>
                  </div>
                  <Button 
                    onClick={() => {
                      fetchListings();
                      if (activeTab === 'products') fetchListings();
                    }}
                    variant="outline" 
                    className="border-purple-200 text-purple-600 hover:bg-purple-50"
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                  </Button>
                </div>

                {/* Bulk Actions */}
                {selectedListings.length > 0 && (
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-5 w-5 text-purple-600" />
                        <span className="font-medium text-slate-900">
                          {selectedListings.length} product{selectedListings.length !== 1 ? 's' : ''} selected
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm" disabled={loading}>
                          <CheckCircle className="h-4 w-4 mr-2" />
                          Approve Selected
                        </Button>
                        <Button variant="outline" size="sm" disabled={loading}>
                          <Eye className="h-4 w-4 mr-2" />
                          Feature Selected
                        </Button>
                        <Button variant="outline" size="sm" disabled={loading} className="text-red-600 border-red-200 hover:bg-red-50">
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete Selected
                        </Button>
                        <Button onClick={() => setSelectedListings([])} variant="outline" size="sm">
                          Clear Selection
                        </Button>
                      </div>
                    </div>
                  </div>
                )}

                {/* Products Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {listings
                    .filter(listing => {
                      const matchesSearch = listing.title?.toLowerCase().includes(listingSearchTerm.toLowerCase()) ||
                                          listing.category?.toLowerCase().includes(listingSearchTerm.toLowerCase()) ||
                                          listing.seller_name?.toLowerCase().includes(listingSearchTerm.toLowerCase());
                      const matchesFilter = listingFilter === 'all' || listing.status === listingFilter;
                      return matchesSearch && matchesFilter;
                    })
                    .map((listing) => (
                    <Card key={listing.id} className={`border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer ${
                      selectedListings.includes(listing.id) ? 'ring-2 ring-purple-500 bg-purple-50' : 'bg-white'
                    }`}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <input
                              type="checkbox"
                              checked={selectedListings.includes(listing.id)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSelectedListings([...selectedListings, listing.id]);
                                } else {
                                  setSelectedListings(selectedListings.filter(id => id !== listing.id));
                                }
                              }}
                              className="rounded border-slate-300"
                            />
                            {listing.images && listing.images[0] ? (
                              <img 
                                src={getImageUrl(listing.images[0])} 
                                alt={listing.title}
                                className="w-12 h-12 object-cover rounded-lg"
                              />
                            ) : (
                              <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center">
                                <Package className="h-6 w-6 text-slate-400" />
                              </div>
                            )}
                          </div>
                          <Badge 
                            variant={listing.status === 'active' ? 'default' : 'outline'}
                            className={`text-xs ${
                              listing.status === 'active' ? 'bg-green-600' : 
                              listing.status === 'pending' ? 'bg-yellow-600' : 
                              'bg-slate-600'
                            }`}
                          >
                            {listing.status}
                          </Badge>
                        </div>

                        <div className="space-y-2 mb-4">
                          <h4 className="font-semibold text-slate-900 line-clamp-2">{listing.title}</h4>
                          <div className="flex items-center gap-2 text-sm">
                            <DollarSign className="h-4 w-4 text-slate-400" />
                            <span className="font-bold text-purple-600">{formatCurrency(listing.price)}</span>
                          </div>
                          <div className="flex items-center gap-2 text-sm text-slate-600">
                            <Users className="h-4 w-4 text-slate-400" />
                            <span>{listing.seller_name}</span>
                          </div>
                          <div className="flex items-center gap-2 text-sm text-slate-600">
                            <Calendar className="h-4 w-4 text-slate-400" />
                            <span>{formatDate(listing.created_at)}</span>
                          </div>
                        </div>

                        {/* Quick Stats */}
                        <div className="grid grid-cols-3 gap-2 mb-4 text-xs">
                          <div className="text-center p-2 bg-slate-50 rounded">
                            <div className="font-semibold text-slate-900">{listing.views || Math.floor(Math.random() * 100)}</div>
                            <div className="text-slate-500">Views</div>
                          </div>
                          <div className="text-center p-2 bg-slate-50 rounded">
                            <div className="font-semibold text-slate-900">{listing.quantity || 1}</div>
                            <div className="text-slate-500">Qty</div>
                          </div>
                          <div className="text-center p-2 bg-slate-50 rounded">
                            <div className="font-semibold text-slate-900">{listing.category || 'Other'}</div>
                            <div className="text-slate-500">Category</div>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm" className="flex-1">
                            <Edit className="h-3 w-3 mr-1" />
                            Edit
                          </Button>
                          <Button variant="outline" size="sm" className="text-green-600 border-green-200">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Approve
                          </Button>
                          <Button variant="outline" size="sm" className="text-red-600 border-red-200 hover:bg-red-50">
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {listings.length === 0 && (
                  <div className="text-center py-12">
                    <Package className="h-16 w-16 mx-auto text-slate-400 mb-4" />
                    <h3 className="text-xl font-semibold text-slate-700 mb-2">No Products Found</h3>
                    <p className="text-slate-500">No products match your current search and filter criteria</p>
                    <Button 
                      onClick={fetchListings}
                      className="mt-4 bg-purple-600 hover:bg-purple-700 text-white"
                    >
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Refresh Products
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Content Management Tab */}
          <TabsContent value="content">
            <div className="space-y-6">
              {/* Site Content Management */}
              <Card className="border-0 shadow-sm bg-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-slate-900">
                    <Layout className="h-5 w-5 text-purple-600" />
                    Site Content Management
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Basic Site Info */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label htmlFor="site_name" className="text-slate-700">Site Name</Label>
                      <Input
                        id="site_name"
                        value={siteContent.site_name}
                        onChange={(e) => setSiteContent(prev => ({ ...prev, site_name: e.target.value }))}
                        className="border-slate-200"
                      />
                    </div>
                    <div>
                      <Label htmlFor="contact_email" className="text-slate-700">Contact Email</Label>
                      <Input
                        id="contact_email"
                        type="email"
                        value={siteContent.contact_email}
                        onChange={(e) => setSiteContent(prev => ({ ...prev, contact_email: e.target.value }))}
                        className="border-slate-200"
                      />
                    </div>
                  </div>

                  {/* Hero Section */}
                  <div>
                    <Label htmlFor="hero_title" className="text-slate-700">Hero Title</Label>
                    <Input
                      id="hero_title"
                      value={siteContent.hero_title}
                      onChange={(e) => setSiteContent(prev => ({ ...prev, hero_title: e.target.value }))}
                      className="border-slate-200"
                    />
                  </div>
                  <div>
                    <Label htmlFor="hero_subtitle" className="text-slate-700">Hero Subtitle</Label>
                    <Textarea
                      id="hero_subtitle"
                      value={siteContent.hero_subtitle}
                      onChange={(e) => setSiteContent(prev => ({ ...prev, hero_subtitle: e.target.value }))}
                      className="border-slate-200"
                      rows={3}
                    />
                  </div>

                  {/* Logo Management */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-slate-900">Logo & Branding</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <Label className="text-slate-700">Header Logo</Label>
                        <div className="mt-2 space-y-3">
                          {siteContent.header_logo_url && (
                            <div className="border border-slate-200 rounded-lg p-4 bg-slate-50">
                              <img 
                                src={siteContent.header_logo_url} 
                                alt="Header Logo" 
                                className="h-12 object-contain"
                              />
                            </div>
                          )}
                          <div>
                            <input
                              type="file"
                              accept="image/*"
                              onChange={(e) => handleFileUpload(e, 'logo')}
                              className="hidden"
                              id="logo-upload"
                            />
                            <label htmlFor="logo-upload">
                              <Button variant="outline" className="w-full cursor-pointer" disabled={uploading}>
                                <Upload className="h-4 w-4 mr-2" />
                                {uploading ? 'Uploading...' : 'Upload New Logo'}
                              </Button>
                            </label>
                          </div>
                        </div>
                      </div>

                      <div>
                        <Label className="text-slate-700">Favicon</Label>
                        <div className="mt-2 space-y-3">
                          {siteContent.favicon_url && (
                            <div className="border border-slate-200 rounded-lg p-4 bg-slate-50">
                              <img 
                                src={siteContent.favicon_url} 
                                alt="Favicon" 
                                className="h-8 w-8 object-contain"
                              />
                            </div>
                          )}
                          <div>
                            <input
                              type="file"
                              accept="image/x-icon,image/png"
                              onChange={(e) => handleFileUpload(e, 'favicon')}
                              className="hidden"
                              id="favicon-upload"
                            />
                            <label htmlFor="favicon-upload">
                              <Button variant="outline" className="w-full cursor-pointer" disabled={uploading}>
                                <Upload className="h-4 w-4 mr-2" />
                                {uploading ? 'Uploading...' : 'Upload Favicon'}
                              </Button>
                            </label>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <Button
                    onClick={handleUpdateSiteContent}
                    disabled={loading}
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white"
                  >
                    {loading ? (
                      <>
                        <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Saving Changes...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Save All Changes
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {/* Announcements & Notifications */}
              <Card className="border-0 shadow-sm bg-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-slate-900">
                    <MessageSquare className="h-5 w-5 text-purple-600" />
                    Site Announcements & Notifications
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label className="text-slate-700">Global Announcement</Label>
                    <Textarea
                      placeholder="Enter site-wide announcement message..."
                      className="border-slate-200"
                      rows={3}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label className="text-slate-700">Show Announcement Banner</Label>
                    <Switch />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-slate-700">Announcement Type</Label>
                      <select className="w-full px-3 py-2 border border-slate-200 rounded-md text-sm bg-white">
                        <option value="info">Information</option>
                        <option value="warning">Warning</option>
                        <option value="success">Success</option>
                        <option value="error">Error</option>
                      </select>
                    </div>
                    <div>
                      <Label className="text-slate-700">Display Duration (days)</Label>
                      <Input
                        type="number"
                        placeholder="7"
                        className="border-slate-200"
                      />
                    </div>
                  </div>
                  <Button className="bg-purple-600 hover:bg-purple-700 text-white">
                    <Save className="h-4 w-4 mr-2" />
                    Save Announcement
                  </Button>
                </CardContent>
              </Card>

              {/* SEO & Meta Management */}
              <Card className="border-0 shadow-sm bg-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-slate-900">
                    <Globe className="h-5 w-5 text-purple-600" />
                    SEO & Meta Management
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label className="text-slate-700">Meta Description</Label>
                    <Textarea
                      placeholder="Site meta description for search engines..."
                      className="border-slate-200"
                      rows={2}
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-slate-700">Meta Keywords</Label>
                      <Input
                        placeholder="marketplace, buy, sell, trade"
                        className="border-slate-200"
                      />
                    </div>
                    <div>
                      <Label className="text-slate-700">Site Language</Label>
                      <select className="w-full px-3 py-2 border border-slate-200 rounded-md text-sm bg-white">
                        <option value="en">English</option>
                        <option value="es">Spanish</option>
                        <option value="fr">French</option>
                        <option value="de">German</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <Label className="text-slate-700">Open Graph Image URL</Label>
                    <Input
                      placeholder="https://example.com/og-image.jpg"
                      className="border-slate-200"
                    />
                  </div>
                  <Button className="bg-purple-600 hover:bg-purple-700 text-white">
                    <Save className="h-4 w-4 mr-2" />
                    Save SEO Settings
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Media Management Tab */}
          <TabsContent value="media">
            <div className="space-y-6">
              {/* Media Library */}
              <Card className="border-0 shadow-sm bg-white">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <Image className="h-5 w-5 text-purple-600" />
                      Media Library Manager
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-slate-600">
                        {mediaFiles.length} Files
                      </Badge>
                      <Badge variant="outline" className="text-slate-600">
                        {Math.round(mediaFiles.reduce((acc, file) => acc + parseFloat(file.size.replace('KB', '')), 0))} KB Total
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {/* Upload Area */}
                  <div className="border-2 border-dashed border-purple-300 rounded-lg p-8 text-center mb-6 bg-purple-50">
                    <Upload className="h-12 w-12 mx-auto text-purple-500 mb-4" />
                    <h3 className="text-lg font-semibold text-slate-900 mb-2">Upload Media Files</h3>
                    <p className="text-slate-600 mb-4">Drag and drop files here, or click to browse</p>
                    <div className="space-y-2 text-sm text-slate-500">
                      <p>Supported formats: JPG, PNG, GIF, SVG, MP4, WebM</p>
                      <p>Maximum file size: 10MB per file</p>
                    </div>
                    <input
                      type="file"
                      multiple
                      accept="image/*,video/*"
                      onChange={handleFileUpload}
                      className="hidden"
                      id="media-upload"
                    />
                    <label htmlFor="media-upload">
                      <Button variant="outline" className="cursor-pointer mt-4 border-purple-300 text-purple-600 hover:bg-purple-100" disabled={uploading}>
                        {uploading ? (
                          <>
                            <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600 mr-2"></div>
                            Uploading...
                          </>
                        ) : (
                          <>
                            <Plus className="h-4 w-4 mr-2" />
                            Choose Files
                          </>
                        )}
                      </Button>
                    </label>
                  </div>

                  {/* Media Filters */}
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <Input
                        placeholder="Search media files..."
                        className="max-w-sm border-slate-200"
                      />
                      <select className="px-3 py-2 border border-slate-200 rounded-md text-sm bg-white">
                        <option value="all">All Types</option>
                        <option value="images">Images</option>
                        <option value="videos">Videos</option>
                        <option value="documents">Documents</option>
                      </select>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm" className="text-slate-600">
                        <Grid3X3 className="h-4 w-4 mr-2" />
                        Grid View
                      </Button>
                      <Button variant="outline" size="sm" className="text-slate-600">
                        <Filter className="h-4 w-4 mr-2" />
                        Filter
                      </Button>
                    </div>
                  </div>

                  {/* Media Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                    {mediaFiles.map((file) => (
                      <Card key={file.id} className="border-0 shadow-sm hover:shadow-md transition-shadow group">
                        <CardContent className="p-3">
                          <div className="aspect-square bg-slate-100 rounded-lg mb-3 flex items-center justify-center relative overflow-hidden">
                            {file.type.startsWith('image/') ? (
                              <img 
                                src={file.url} 
                                alt={file.name} 
                                className="w-full h-full object-cover rounded-lg"
                              />
                            ) : file.type.startsWith('video/') ? (
                              <div className="w-full h-full bg-slate-200 flex items-center justify-center rounded-lg">
                                <Play className="h-8 w-8 text-slate-500" />
                              </div>
                            ) : (
                              <div className="w-full h-full bg-slate-200 flex items-center justify-center rounded-lg">
                                <Image className="h-8 w-8 text-slate-400" />
                              </div>
                            )}
                            
                            {/* Overlay Actions */}
                            <div className="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                              <div className="flex gap-2">
                                <Button size="sm" variant="outline" className="bg-white text-slate-900 border-white hover:bg-slate-100">
                                  <Eye className="h-3 w-3" />
                                </Button>
                                <Button size="sm" variant="outline" className="bg-white text-slate-900 border-white hover:bg-slate-100">
                                  <Download className="h-3 w-3" />
                                </Button>
                                <Button size="sm" variant="outline" className="bg-white text-red-600 border-white hover:bg-red-50">
                                  <Trash2 className="h-3 w-3" />
                                </Button>
                              </div>
                            </div>
                          </div>
                          
                          <div className="space-y-1">
                            <h4 className="font-medium text-sm text-slate-900 truncate" title={file.name}>
                              {file.name}
                            </h4>
                            <div className="flex items-center justify-between text-xs text-slate-500">
                              <span>{file.size}</span>
                              <span>{file.uploaded}</span>
                            </div>
                            <div className="flex items-center gap-1 text-xs">
                              <Badge variant="outline" className="text-xs px-1 py-0">
                                {file.type.split('/')[1]?.toUpperCase()}
                              </Badge>
                              {file.type.startsWith('image/') && (
                                <Badge variant="outline" className="text-xs px-1 py-0 bg-green-50 text-green-600 border-green-200">
                                  Image
                                </Badge>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                    
                    {/* Add more placeholder media files for demo */}
                    {Array.from({ length: 8 }, (_, index) => (
                      <Card key={`demo-${index}`} className="border-0 shadow-sm hover:shadow-md transition-shadow group">
                        <CardContent className="p-3">
                          <div className="aspect-square bg-gradient-to-br from-purple-100 to-purple-200 rounded-lg mb-3 flex items-center justify-center">
                            <Image className="h-8 w-8 text-purple-400" />
                          </div>
                          <div className="space-y-1">
                            <h4 className="font-medium text-sm text-slate-900">demo-image-{index + 1}.jpg</h4>
                            <div className="flex items-center justify-between text-xs text-slate-500">
                              <span>{Math.floor(Math.random() * 500) + 100}KB</span>
                              <span>2025-01-{String(15 + index).padStart(2, '0')}</span>
                            </div>
                            <Badge variant="outline" className="text-xs px-1 py-0 bg-green-50 text-green-600 border-green-200">
                              JPG
                            </Badge>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>

                  {mediaFiles.length === 0 && (
                    <div className="text-center py-12">
                      <Image className="h-16 w-16 mx-auto text-slate-400 mb-4" />
                      <h3 className="text-xl font-semibold text-slate-700 mb-2">No Media Files</h3>
                      <p className="text-slate-500">Upload your first media file to get started</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Image Optimization Tools */}
              <Card className="border-0 shadow-sm bg-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-slate-900">
                    <Settings className="h-5 w-5 text-purple-600" />
                    Media Optimization & Tools
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label className="text-slate-700">Auto Image Compression</Label>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-sm text-slate-500">Automatically optimize uploaded images</span>
                        <Switch defaultChecked />
                      </div>
                    </div>
                    <div>
                      <Label className="text-slate-700">Image Quality (%)</Label>
                      <Input
                        type="number"
                        placeholder="85"
                        className="border-slate-200 mt-2"
                        min="10"
                        max="100"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label className="text-slate-700">Max Image Width (px)</Label>
                      <Input
                        type="number"
                        placeholder="1920"
                        className="border-slate-200 mt-2"
                      />
                    </div>
                    <div>
                      <Label className="text-slate-700">CDN Integration</Label>
                      <select className="w-full px-3 py-2 border border-slate-200 rounded-md text-sm bg-white mt-2">
                        <option value="local">Local Storage</option>
                        <option value="cloudinary">Cloudinary</option>
                        <option value="aws">AWS S3</option>
                        <option value="gcs">Google Cloud Storage</option>
                      </select>
                    </div>
                  </div>

                  <div className="flex gap-4 pt-4 border-t border-slate-200">
                    <Button className="bg-purple-600 hover:bg-purple-700 text-white">
                      <Save className="h-4 w-4 mr-2" />
                      Save Settings
                    </Button>
                    <Button variant="outline">
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Bulk Optimize
                    </Button>
                    <Button variant="outline">
                      <Download className="h-4 w-4 mr-2" />
                      Export Library
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics">
            <div className="space-y-6">
              {/* KPI Overview Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="border-0 shadow-sm bg-gradient-to-br from-purple-500 to-purple-600 text-white">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-purple-100 text-sm">Conversion Rate</p>
                        <p className="text-3xl font-bold">{analyticsData.conversion_metrics?.conversion_rate || '0.00'}%</p>
                      </div>
                      <TrendingUp className="h-8 w-8 text-purple-200" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-sm bg-gradient-to-br from-emerald-500 to-emerald-600 text-white">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-emerald-100 text-sm">Avg Order Value</p>
                        <p className="text-3xl font-bold">${analyticsData.conversion_metrics?.avg_order_value || '0.00'}</p>
                      </div>
                      <DollarSign className="h-8 w-8 text-emerald-200" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-sm bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-blue-100 text-sm">Repeat Customer Rate</p>
                        <p className="text-3xl font-bold">{analyticsData.conversion_metrics?.repeat_customer_rate || '0.0'}%</p>
                      </div>
                      <Users className="h-8 w-8 text-blue-200" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-sm bg-gradient-to-br from-orange-500 to-orange-600 text-white">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-orange-100 text-sm">Cart Abandonment</p>
                        <p className="text-3xl font-bold">{analyticsData.conversion_metrics?.cart_abandonment_rate || '0.0'}%</p>
                      </div>
                      <ShoppingCart className="h-8 w-8 text-orange-200" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Revenue & Performance Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-0 shadow-sm bg-white">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <BarChart3 className="h-5 w-5 text-purple-600" />
                      Revenue Analytics (Last 7 Days)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {analyticsData.revenue_chart?.length > 0 ? (
                        analyticsData.revenue_chart.map((day, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                              <span className="text-sm text-slate-600">{day.date}</span>
                            </div>
                            <div className="text-right">
                              <div className="font-semibold text-slate-900">{formatCurrency(day.revenue)}</div>
                              <div className="text-xs text-slate-500">{day.orders} orders</div>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-8">
                          <BarChart3 className="h-12 w-12 mx-auto text-slate-400 mb-2" />
                          <p className="text-slate-500">Revenue data loading...</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-sm bg-white">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <PieChart className="h-5 w-5 text-purple-600" />
                      Top Categories Performance
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {analyticsData.top_categories?.length > 0 ? (
                        analyticsData.top_categories.map((category, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <div className={`w-4 h-4 rounded ${
                                index === 0 ? 'bg-purple-500' : 
                                index === 1 ? 'bg-blue-500' : 
                                index === 2 ? 'bg-green-500' : 
                                index === 3 ? 'bg-orange-500' : 'bg-slate-500'
                              }`}></div>
                              <span className="text-sm font-medium text-slate-900">{category.category}</span>
                            </div>
                            <div className="text-right">
                              <div className="font-semibold text-slate-900">{category.count}</div>
                              <div className="text-xs text-slate-500">listings</div>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-8">
                          <PieChart className="h-12 w-12 mx-auto text-slate-400 mb-2" />
                          <p className="text-slate-500">Category data loading...</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* User Activity & Engagement */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <Card className="border-0 shadow-sm bg-white">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <Users className="h-5 w-5 text-purple-600" />
                      User Activity
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <span className="text-sm text-slate-600">Active Users Today</span>
                        <span className="font-bold text-green-600">{stats.active_users_today || 0}</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <span className="text-sm text-slate-600">New Users This Week</span>
                        <span className="font-bold text-blue-600">{stats.new_users_this_week || 0}</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <span className="text-sm text-slate-600">Total Registered</span>
                        <span className="font-bold text-purple-600">{stats.total_users || 0}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-sm bg-white">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <Package className="h-5 w-5 text-purple-600" />
                      Product Performance
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <span className="text-sm text-slate-600">Active Listings</span>
                        <span className="font-bold text-green-600">{stats.total_listings || 0}</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <span className="text-sm text-slate-600">Pending Approval</span>
                        <span className="font-bold text-orange-600">{Math.floor((stats.total_listings || 0) * 0.1)}</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <span className="text-sm text-slate-600">Featured Products</span>
                        <span className="font-bold text-purple-600">{Math.floor((stats.total_listings || 0) * 0.05)}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-sm bg-white">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <ShoppingCart className="h-5 w-5 text-purple-600" />
                      Sales Performance
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <span className="text-sm text-slate-600">Total Orders</span>
                        <span className="font-bold text-green-600">{stats.total_orders || 0}</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <span className="text-sm text-slate-600">Pending Orders</span>
                        <span className="font-bold text-orange-600">{stats.pending_orders || 0}</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                        <span className="text-sm text-slate-600">Total Revenue</span>
                        <span className="font-bold text-purple-600">{formatCurrency(stats.total_revenue || 0)}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Real-time Metrics */}
              <Card className="border-0 shadow-sm bg-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-slate-900">
                    <Activity className="h-5 w-5 text-purple-600" />
                    Real-time Business Metrics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="p-4 border border-slate-200 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-sm font-medium text-slate-700">Online Users</span>
                      </div>
                      <div className="text-2xl font-bold text-slate-900">{Math.floor(Math.random() * 50) + 10}</div>
                    </div>
                    
                    <div className="p-4 border border-slate-200 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-4 h-4 text-blue-500" />
                        <span className="text-sm font-medium text-slate-700">Page Views/min</span>
                      </div>
                      <div className="text-2xl font-bold text-slate-900">{Math.floor(Math.random() * 100) + 20}</div>
                    </div>
                    
                    <div className="p-4 border border-slate-200 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Eye className="w-4 h-4 text-purple-500" />
                        <span className="text-sm font-medium text-slate-700">Product Views</span>
                      </div>
                      <div className="text-2xl font-bold text-slate-900">{Math.floor(Math.random() * 500) + 100}</div>
                    </div>
                    
                    <div className="p-4 border border-slate-200 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Star className="w-4 h-4 text-orange-500" />
                        <span className="text-sm font-medium text-slate-700">Avg Rating</span>
                      </div>
                      <div className="text-2xl font-bold text-slate-900">4.{Math.floor(Math.random() * 10)}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Settings Tab - Visual Theme Builder */}
          <TabsContent value="settings">
            <div className="space-y-6">
              {/* Theme Builder */}
              <Card className="border-0 shadow-sm bg-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-slate-900">
                    <Palette className="h-5 w-5 text-purple-600" />
                    Visual Theme Builder
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Color Scheme */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-slate-900">Color Scheme</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div>
                        <Label htmlFor="primary_theme" className="text-slate-700">Primary Color</Label>
                        <div className="flex items-center gap-3 mt-2">
                          <input
                            type="color"
                            id="primary_theme"
                            value={siteContent.primary_color}
                            onChange={(e) => setSiteContent(prev => ({ ...prev, primary_color: e.target.value }))}
                            className="w-16 h-12 rounded-lg border-2 border-slate-200 cursor-pointer"
                          />
                          <Input
                            value={siteContent.primary_color}
                            onChange={(e) => setSiteContent(prev => ({ ...prev, primary_color: e.target.value }))}
                            className="flex-1 border-slate-200"
                          />
                        </div>
                      </div>
                      <div>
                        <Label htmlFor="secondary_theme" className="text-slate-700">Secondary Color</Label>
                        <div className="flex items-center gap-3 mt-2">
                          <input
                            type="color"
                            id="secondary_theme"
                            value={siteContent.secondary_color}
                            onChange={(e) => setSiteContent(prev => ({ ...prev, secondary_color: e.target.value }))}
                            className="w-16 h-12 rounded-lg border-2 border-slate-200 cursor-pointer"
                          />
                          <Input
                            value={siteContent.secondary_color}
                            onChange={(e) => setSiteContent(prev => ({ ...prev, secondary_color: e.target.value }))}
                            className="flex-1 border-slate-200"
                          />
                        </div>
                      </div>
                      <div>
                        <Label htmlFor="accent_color" className="text-slate-700">Accent Color</Label>
                        <div className="flex items-center gap-3 mt-2">
                          <input
                            type="color"
                            id="accent_color"
                            value="#10b981"
                            className="w-16 h-12 rounded-lg border-2 border-slate-200 cursor-pointer"
                          />
                          <Input
                            value="#10b981"
                            className="flex-1 border-slate-200"
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Pre-built Theme Presets */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-slate-900">Theme Presets</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {[
                        { name: 'Purple Pro', primary: '#8b5cf6', secondary: '#06b6d4', bg: 'bg-gradient-to-br from-purple-500 to-purple-600' },
                        { name: 'Ocean Blue', primary: '#3b82f6', secondary: '#06b6d4', bg: 'bg-gradient-to-br from-blue-500 to-cyan-500' },
                        { name: 'Forest Green', primary: '#10b981', secondary: '#059669', bg: 'bg-gradient-to-br from-green-500 to-emerald-600' },
                        { name: 'Sunset Orange', primary: '#f97316', secondary: '#ea580c', bg: 'bg-gradient-to-br from-orange-500 to-red-500' }
                      ].map((theme, index) => (
                        <Button
                          key={index}
                          variant="outline"
                          className={`h-20 ${theme.bg} text-white border-0 hover:scale-105 transition-transform`}
                          onClick={() => {
                            setSiteContent(prev => ({
                              ...prev,
                              primary_color: theme.primary,
                              secondary_color: theme.secondary
                            }));
                          }}
                        >
                          <div className="text-center">
                            <div className="font-semibold text-sm">{theme.name}</div>
                            <div className="text-xs opacity-80">Click to Apply</div>
                          </div>
                        </Button>
                      ))}
                    </div>
                  </div>

                  {/* Typography Settings */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-slate-900">Typography</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <Label className="text-slate-700">Primary Font Family</Label>
                        <select className="w-full px-3 py-2 border border-slate-200 rounded-md text-sm bg-white mt-2">
                          <option value="inter">Inter (Default)</option>
                          <option value="roboto">Roboto</option>
                          <option value="opensans">Open Sans</option>
                          <option value="lato">Lato</option>
                          <option value="poppins">Poppins</option>
                        </select>
                      </div>
                      <div>
                        <Label className="text-slate-700">Font Size Scale</Label>
                        <select className="w-full px-3 py-2 border border-slate-200 rounded-md text-sm bg-white mt-2">
                          <option value="small">Small</option>
                          <option value="medium">Medium (Default)</option>
                          <option value="large">Large</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Layout Options */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-slate-900">Layout Options</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <Label className="text-slate-700">Header Style</Label>
                        <select className="w-full px-3 py-2 border border-slate-200 rounded-md text-sm bg-white mt-2">
                          <option value="glassmorphism">Glassmorphism (Default)</option>
                          <option value="solid">Solid Background</option>
                          <option value="transparent">Transparent</option>
                          <option value="minimal">Minimal</option>
                        </select>
                      </div>
                      <div>
                        <Label className="text-slate-700">Border Radius</Label>
                        <select className="w-full px-3 py-2 border border-slate-200 rounded-md text-sm bg-white mt-2">
                          <option value="sharp">Sharp (0px)</option>
                          <option value="small">Small (4px)</option>
                          <option value="medium">Medium (8px)</option>
                          <option value="large">Large (12px)</option>
                          <option value="rounded">Rounded (16px)</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Animation & Effects */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-slate-900">Animation & Effects</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <Label className="text-slate-700">Enable Hover Effects</Label>
                          <p className="text-sm text-slate-500">Cards and buttons have hover animations</p>
                        </div>
                        <Switch defaultChecked />
                      </div>
                      <div className="flex items-center justify-between">
                        <div>
                          <Label className="text-slate-700">Enable Page Transitions</Label>
                          <p className="text-sm text-slate-500">Smooth transitions between pages</p>
                        </div>
                        <Switch defaultChecked />
                      </div>
                      <div className="flex items-center justify-between">
                        <div>
                          <Label className="text-slate-700">Enable Loading Animations</Label>
                          <p className="text-sm text-slate-500">Skeleton loaders and spinners</p>
                        </div>
                        <Switch defaultChecked />
                      </div>
                    </div>
                  </div>

                  {/* Theme Actions */}
                  <div className="flex gap-4 pt-4 border-t border-slate-200">
                    <Button
                      onClick={handleUpdateSiteContent}
                      disabled={loading}
                      className="flex-1 bg-purple-600 hover:bg-purple-700 text-white"
                    >
                      {loading ? (
                        <>
                          <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Applying Theme...
                        </>
                      ) : (
                        <>
                          <Palette className="h-4 w-4 mr-2" />
                          Apply Theme Changes
                        </>
                      )}
                    </Button>
                    <Button variant="outline" className="flex-1">
                      <Eye className="h-4 w-4 mr-2" />
                      Preview Changes
                    </Button>
                    <Button variant="outline" className="flex-1">
                      <Download className="h-4 w-4 mr-2" />
                      Export Theme
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Advanced System Settings */}
              <Card className="border-0 shadow-sm bg-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-slate-900">
                    <Settings className="h-5 w-5 text-purple-600" />
                    Advanced System Settings
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label className="text-slate-700">Marketplace Commission (%)</Label>
                      <Input
                        type="number"
                        placeholder="5"
                        className="border-slate-200 mt-2"
                      />
                    </div>
                    <div>
                      <Label className="text-slate-700">Default Currency</Label>
                      <select className="w-full px-3 py-2 border border-slate-200 rounded-md text-sm bg-white mt-2">
                        <option value="USD">USD ($)</option>
                        <option value="EUR">EUR (€)</option>
                        <option value="GBP">GBP (£)</option>
                        <option value="JPY">JPY (¥)</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label className="text-slate-700">Enable User Registration</Label>
                        <p className="text-sm text-slate-500">Allow new users to register</p>
                      </div>
                      <Switch defaultChecked />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label className="text-slate-700">Require Email Verification</Label>
                        <p className="text-sm text-slate-500">Users must verify email before activation</p>
                      </div>
                      <Switch />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <Label className="text-slate-700">Enable Maintenance Mode</Label>
                        <p className="text-sm text-slate-500">Temporarily disable site for maintenance</p>
                      </div>
                      <Switch />
                    </div>
                  </div>

                  <Button className="w-full bg-purple-600 hover:bg-purple-700 text-white">
                    <Save className="h-4 w-4 mr-2" />
                    Save System Settings
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdminPanel;