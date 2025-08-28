import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { adminAPI } from '../../services/api';
import { useToast } from '../../hooks/use-toast';
import Header from '../../components/layout/Header';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';

const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const [siteSettings, setSiteSettings] = useState({
    site_name: 'Cataloro',
    primary_color: '#8b5cf6',
    secondary_color: '#06b6d4',
    font_family: 'Inter'
  });
  
  const { user } = useAuth();
  const { toast } = useToast();

  // Apply theme colors to the entire site
  const applyThemeColors = (settings) => {
    const root = document.documentElement;
    root.style.setProperty('--primary-color', settings.primary_color || '#8b5cf6');
    root.style.setProperty('--secondary-color', settings.secondary_color || '#06b6d4');
    
    toast({
      title: "Theme Updated",
      description: "Theme colors have been applied successfully"
    });
  };

  useEffect(() => {
    if (activeTab === 'dashboard') {
      fetchStats();
    } else if (activeTab === 'users') {
      fetchUsers();
    } else if (activeTab === 'products') {
      fetchListings();
    }
  }, [activeTab]);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
      toast({
        title: "Error",
        description: "Failed to fetch statistics",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getUsers();
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
      toast({
        title: "Error",
        description: "Failed to fetch users",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchListings = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getListings();
      setListings(response.data);
    } catch (error) {
      console.error('Error fetching listings:', error);
      toast({
        title: "Error",
        description: "Failed to fetch listings",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const updateSiteSettings = async (newSettings) => {
    try {
      await adminAPI.updateSiteSettings(newSettings);
      setSiteSettings(newSettings);
      applyThemeColors(newSettings);
      toast({
        title: "Success",
        description: "Site settings updated successfully"
      });
    } catch (error) {
      console.error('Error updating site settings:', error);
      toast({
        title: "Error",
        description: "Failed to update site settings",
        variant: "destructive"
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <Header />
      
      {/* Modern Admin Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-light text-slate-900">Cataloro Admin</h1>
              <p className="text-slate-600 font-light">Complete marketplace management and customization</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="bg-purple-600 text-white px-4 py-2 rounded-xl text-sm font-medium">
                <span className="opacity-80">Version</span> <span>v3.0</span>
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
          <TabsList className="grid w-full grid-cols-6 bg-white shadow-sm">
            <TabsTrigger value="dashboard">📊 Overview</TabsTrigger>
            <TabsTrigger value="theme-builder">🎨 Theme Builder</TabsTrigger>
            <TabsTrigger value="users">👥 Users</TabsTrigger>
            <TabsTrigger value="products">🛍️ Products</TabsTrigger>
            <TabsTrigger value="analytics">📈 Analytics</TabsTrigger>
            <TabsTrigger value="media">🖼️ Media</TabsTrigger>
          </TabsList>

          {/* Overview Dashboard Tab */}
          <TabsContent value="dashboard">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-3xl font-bold text-purple-600 mb-2">{stats?.total_users || 0}</div>
                  <div className="text-sm text-slate-600">Total Users</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-3xl font-bold text-blue-600 mb-2">{stats?.total_listings || 0}</div>
                  <div className="text-sm text-slate-600">Active Listings</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-3xl font-bold text-green-600 mb-2">{stats?.total_orders || 0}</div>
                  <div className="text-sm text-slate-600">Transactions</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6 text-center">
                  <div className="text-3xl font-bold text-orange-600 mb-2">€{stats?.total_revenue || '0'}</div>
                  <div className="text-sm text-slate-600">Revenue</div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Theme Builder */}
          <TabsContent value="theme-builder">
            <Card>
              <CardHeader>
                <CardTitle>🎨 Visual Theme Builder</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Theme Controls */}
                  <div className="space-y-6">
                    <h3 className="text-xl font-semibold mb-4">🎨 Color Palette</h3>
                    
                    {/* Primary Color */}
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-2">Primary Color</label>
                      <div className="flex items-center gap-3">
                        <input
                          type="color"
                          value={siteSettings?.primary_color || '#8b5cf6'}
                          onChange={(e) => {
                            const newSettings = {...siteSettings, primary_color: e.target.value};
                            setSiteSettings(newSettings);
                            applyThemeColors(newSettings);
                          }}
                          className="w-16 h-12 rounded-lg border-2 border-slate-200 cursor-pointer"
                        />
                        <input
                          type="text"
                          value={siteSettings?.primary_color || '#8b5cf6'}
                          onChange={(e) => {
                            const newSettings = {...siteSettings, primary_color: e.target.value};
                            setSiteSettings(newSettings);
                          }}
                          className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          placeholder="#8b5cf6"
                        />
                      </div>
                      <p className="text-sm text-slate-500 mt-1">Main brand color for buttons and accents</p>
                    </div>

                    {/* Secondary Color */}
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-2">Secondary Color</label>
                      <div className="flex items-center gap-3">
                        <input
                          type="color"
                          value={siteSettings?.secondary_color || '#06b6d4'}
                          onChange={(e) => {
                            const newSettings = {...siteSettings, secondary_color: e.target.value};
                            setSiteSettings(newSettings);
                            applyThemeColors(newSettings);
                          }}
                          className="w-16 h-12 rounded-lg border-2 border-slate-200 cursor-pointer"
                        />
                        <input
                          type="text"
                          value={siteSettings?.secondary_color || '#06b6d4'}
                          onChange={(e) => {
                            const newSettings = {...siteSettings, secondary_color: e.target.value};
                            setSiteSettings(newSettings);
                          }}
                          className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          placeholder="#06b6d4"
                        />
                      </div>
                      <p className="text-sm text-slate-500 mt-1">Used for highlights and special elements</p>
                    </div>

                    {/* Save Button */}
                    <Button 
                      onClick={() => updateSiteSettings(siteSettings)}
                      className="w-full bg-purple-600 hover:bg-purple-700"
                    >
                      💾 Save Theme Changes
                    </Button>
                  </div>

                  {/* Live Preview */}
                  <div className="space-y-6">
                    <h3 className="text-xl font-semibold mb-4">👁️ Live Preview</h3>
                    
                    {/* Preview Header */}
                    <Card>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg" style={{backgroundColor: siteSettings?.primary_color || '#8b5cf6'}}></div>
                            <span className="font-semibold">Cataloro</span>
                          </div>
                          <div className="flex gap-2">
                            <span className="px-3 py-1 rounded text-sm" style={{backgroundColor: siteSettings?.primary_color || '#8b5cf6', color: 'white'}}>Browse</span>
                            <span className="px-3 py-1 rounded text-sm border">Sell</span>
                          </div>
                        </div>
                        
                        {/* Preview Card */}
                        <div className="border rounded-lg p-4 bg-gray-50">
                          <h4 className="font-medium mb-2">Sample Product Card</h4>
                          <p className="text-sm text-gray-600 mb-3">This is how products will appear with your theme</p>
                          <div className="flex gap-2">
                            <button 
                              className="px-4 py-2 rounded text-sm font-medium text-white"
                              style={{backgroundColor: siteSettings?.primary_color || '#8b5cf6'}}
                            >
                              Add to Cart
                            </button>
                            <button 
                              className="px-4 py-2 rounded text-sm font-medium border"
                              style={{borderColor: siteSettings?.secondary_color || '#06b6d4', color: siteSettings?.secondary_color || '#06b6d4'}}
                            >
                              View Details
                            </button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users">
            <Card>
              <CardHeader>
                <CardTitle>👥 User Management</CardTitle>
              </CardHeader>
              <CardContent>
                {users.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">👥</div>
                    <h3 className="text-xl font-semibold text-slate-700 mb-2">No Users Yet</h3>
                    <p className="text-slate-500">Users will appear here once they register</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {users.map((user) => (
                      <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div>
                          <h4 className="font-medium">{user.full_name}</h4>
                          <p className="text-sm text-slate-500">{user.email}</p>
                          <p className="text-xs text-slate-400">{user.role}</p>
                        </div>
                        <div className="text-sm text-slate-500">
                          Joined {new Date(user.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Products Tab */}
          <TabsContent value="products">
            <Card>
              <CardHeader>
                <CardTitle>🛍️ Product Management</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🛍️</div>
                  <h3 className="text-xl font-semibold text-slate-700 mb-2">Product Management</h3>
                  <p className="text-slate-500">Advanced product management features coming soon</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics">
            <Card>
              <CardHeader>
                <CardTitle>📈 Advanced Analytics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📈</div>
                  <h3 className="text-xl font-semibold text-slate-700 mb-2">Analytics Dashboard</h3>
                  <p className="text-slate-500">Comprehensive analytics and reporting features coming soon</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Media Tab */}
          <TabsContent value="media">
            <Card>
              <CardHeader>
                <CardTitle>🖼️ Media Manager</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🖼️</div>
                  <h3 className="text-xl font-semibold text-slate-700 mb-2">Media Library</h3>
                  <p className="text-slate-500">Advanced media management and optimization tools coming soon</p>
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