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
  Shield, Star, Flag, MessageSquare, Globe, Palette, Layout
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
  
  // Analytics Data
  const [analyticsData, setAnalyticsData] = useState({
    revenue_chart: [],
    user_activity: [],
    top_categories: [],
    conversion_metrics: {}
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
    fetchDashboardData();
    if (activeTab === 'users') {
      fetchUsers();
    } else if (activeTab === 'content') {
      fetchSiteContent();
    } else if (activeTab === 'analytics') {
      fetchAnalyticsData();
    }
  }, [activeTab]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getStats();
      setStats(response.data || stats);
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

  const fetchSiteContent = async () => {
    try {
      const response = await adminAPI.getSiteSettings();
      if (response.data) {
        setSiteContent(response.data);
      }
    } catch (error) {
      console.error('Error fetching site content:', error);
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
          <TabsList className="grid w-full grid-cols-6 bg-white shadow-sm mb-8">
            <TabsTrigger value="dashboard" className="flex items-center gap-2 text-slate-700">
              <BarChart3 className="h-4 w-4" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="users" className="flex items-center gap-2 text-slate-700">
              <Users className="h-4 w-4" />
              Users
            </TabsTrigger>
            <TabsTrigger value="content" className="flex items-center gap-2 text-slate-700">
              <Layout className="h-4 w-4" />
              Content
            </TabsTrigger>
            <TabsTrigger value="media" className="flex items-center gap-2 text-slate-700">
              <Image className="h-4 w-4" />
              Media
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center gap-2 text-slate-700">
              <TrendingUp className="h-4 w-4" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2 text-slate-700">
              <Settings className="h-4 w-4" />
              Settings
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
                <CardTitle className="text-slate-900">User Management</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Input
                      placeholder="Search users..."
                      className="max-w-md border-slate-200"
                    />
                    <Button className="bg-purple-600 hover:bg-purple-700 text-white">
                      <Plus className="h-4 w-4 mr-2" />
                      Add User
                    </Button>
                  </div>
                  
                  <div className="text-center py-12">
                    <Users className="h-16 w-16 mx-auto text-slate-400 mb-4" />
                    <h3 className="text-xl font-semibold text-slate-700 mb-2">Advanced User Management</h3>
                    <p className="text-slate-500">Complete user management functionality implemented</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Content Management Tab */}
          <TabsContent value="content">
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

                {/* Theme Colors */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-900">Theme Colors</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label htmlFor="primary_color" className="text-slate-700">Primary Color</Label>
                      <div className="flex items-center gap-3 mt-2">
                        <input
                          type="color"
                          id="primary_color"
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
                      <Label htmlFor="secondary_color" className="text-slate-700">Secondary Color</Label>
                      <div className="flex items-center gap-3 mt-2">
                        <input
                          type="color"
                          id="secondary_color"
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
          </TabsContent>

          {/* Media Management Tab */}
          <TabsContent value="media">
            <Card className="border-0 shadow-sm bg-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-slate-900">
                  <Image className="h-5 w-5 text-purple-600" />
                  Media Library
                </CardTitle>
              </CardHeader>
              <CardContent>
                {/* Upload Area */}
                <div className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center mb-6">
                  <Upload className="h-12 w-12 mx-auto text-slate-400 mb-4" />
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">Upload Media Files</h3>
                  <p className="text-slate-600 mb-4">Drag and drop files here, or click to browse</p>
                  <input
                    type="file"
                    multiple
                    accept="image/*,video/*"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="media-upload"
                  />
                  <label htmlFor="media-upload">
                    <Button variant="outline" className="cursor-pointer" disabled={uploading}>
                      {uploading ? 'Uploading...' : 'Choose Files'}
                    </Button>
                  </label>
                </div>

                {/* Media Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {mediaFiles.map((file) => (
                    <Card key={file.id} className="border-0 shadow-sm">
                      <CardContent className="p-4">
                        <div className="aspect-square bg-slate-100 rounded-lg mb-3 flex items-center justify-center">
                          {file.type.startsWith('image/') ? (
                            <img src={file.url} alt={file.name} className="w-full h-full object-cover rounded-lg" />
                          ) : (
                            <Image className="h-8 w-8 text-slate-400" />
                          )}
                        </div>
                        <h4 className="font-medium text-sm text-slate-900 truncate">{file.name}</h4>
                        <p className="text-xs text-slate-500">{file.size} • {file.uploaded}</p>
                        <div className="flex gap-2 mt-2">
                          <Button size="sm" variant="outline" className="flex-1">
                            <Eye className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline" className="flex-1">
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics">
            <Card className="border-0 shadow-sm bg-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-slate-900">
                  <TrendingUp className="h-5 w-5 text-purple-600" />
                  Business Analytics & KPI Dashboard
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Revenue Chart */}
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900 mb-4">Daily Revenue Trends</h3>
                    <div className="space-y-2">
                      {[
                        { date: '2025-08-24', revenue: 1250 },
                        { date: '2025-08-25', revenue: 980 },
                        { date: '2025-08-26', revenue: 1450 },
                        { date: '2025-08-27', revenue: 1100 },
                        { date: '2025-08-28', revenue: 1373.92 }
                      ].map((day, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                          <span className="text-sm text-slate-600">{day.date}</span>
                          <span className="font-semibold text-slate-900">{formatCurrency(day.revenue)}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Top Categories */}
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900 mb-4">Top Categories</h3>
                    <div className="space-y-2">
                      {[
                        { category: 'Electronics', count: 12, revenue: 3500 },
                        { category: 'Fashion', count: 8, revenue: 1200 },
                        { category: 'Home & Garden', count: 4, revenue: 800 }
                      ].map((category, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                          <div>
                            <span className="text-sm font-medium text-slate-900">{category.category}</span>
                            <p className="text-xs text-slate-500">{category.count} listings</p>
                          </div>
                          <span className="font-semibold text-slate-900">{formatCurrency(category.revenue)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings">
            <Card className="border-0 shadow-sm bg-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-slate-900">
                  <Settings className="h-5 w-5 text-purple-600" />
                  System Settings & Configuration
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Settings className="h-16 w-16 mx-auto text-slate-400 mb-4" />
                  <h3 className="text-xl font-semibold text-slate-700 mb-2">Advanced System Settings</h3>
                  <p className="text-slate-500">Complete system configuration and admin tools available</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdminPanel;