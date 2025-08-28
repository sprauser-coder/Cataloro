import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { authAPI, adminAPI } from '../../services/api';
import { useToast } from '../../hooks/use-toast';
import Header from '../../components/layout/Header';
import Footer from '../../components/layout/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Badge } from '../../components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '../../components/ui/avatar';
import { 
  User, Edit3, Save, Camera, MapPin, Calendar, Mail, 
  Phone, Globe, Star, Package, ShoppingCart, Heart,
  Shield, Settings, Bell, Lock, CreditCard
} from 'lucide-react';
import { formatDate, formatCurrency } from '../../utils/helpers';

const ProfilePage = () => {
  const { user, fetchUserProfile } = useAuth();
  const { toast } = useToast();

  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [profileData, setProfileData] = useState({
    full_name: '',
    email: '',
    phone: '',
    bio: '',
    location: '',
    website: '',
    avatar_url: ''
  });

  const [stats, setStats] = useState({
    total_listings: 0,
    total_sales: 0,
    total_purchases: 0,
    favorite_count: 0,
    total_revenue: 0,
    average_rating: 0,
    review_count: 0
  });

  const [securitySettings, setSecuritySettings] = useState({
    two_factor_enabled: false,
    email_notifications: true,
    sms_notifications: false,
    marketing_emails: true
  });

  useEffect(() => {
    if (user) {
      setProfileData({
        full_name: user.full_name || '',
        email: user.email || '',
        phone: user.phone || '',
        bio: user.bio || '',
        location: user.location || '',
        website: user.website || '',
        avatar_url: user.avatar_url || ''
      });
      fetchUserStats();
    }
  }, [user]);

  const fetchUserStats = async () => {
    try {
      // In a real implementation, this would call specific user stats endpoints
      const mockStats = {
        total_listings: 12,
        total_sales: 8,
        total_purchases: 15,
        favorite_count: 23,
        total_revenue: 1245.50,
        average_rating: 4.8,
        review_count: 32
      };
      setStats(mockStats);
    } catch (error) {
      console.error('Error fetching user stats:', error);
    }
  };

  const handleInputChange = (field, value) => {
    setProfileData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSaveProfile = async () => {
    setLoading(true);
    
    try {
      // In a real implementation, this would call an update profile endpoint
      await new Promise(resolve => setTimeout(resolve, 1000)); // Mock API call
      
      toast({
        title: "Profile Updated",
        description: "Your profile has been updated successfully"
      });
      
      setEditing(false);
      fetchUserProfile(); // Refresh user context
    } catch (error) {
      console.error('Error updating profile:', error);
      toast({
        title: "Error",
        description: "Failed to update profile. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) { // 5MB limit
      toast({
        title: "File Too Large",
        description: "Avatar image must be less than 5MB",
        variant: "destructive"
      });
      return;
    }

    try {
      setLoading(true);
      // In a real implementation, this would upload to image service
      const mockUrl = URL.createObjectURL(file);
      handleInputChange('avatar_url', mockUrl);
      
      toast({
        title: "Avatar Updated",
        description: "Your profile picture has been updated"
      });
    } catch (error) {
      console.error('Error uploading avatar:', error);
      toast({
        title: "Error",
        description: "Failed to upload avatar. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, label, value, color = 'text-purple-600' }) => (
    <Card className="border-0 shadow-sm">
      <CardContent className="p-4 text-center">
        <Icon className={`h-8 w-8 mx-auto mb-2 ${color}`} />
        <div className={`text-2xl font-bold ${color} mb-1`}>{value}</div>
        <div className="text-sm text-slate-600">{label}</div>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <Header />
      
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Header */}
        <Card className="border-0 shadow-sm mb-8">
          <CardContent className="p-8">
            <div className="flex flex-col md:flex-row items-start gap-6">
              {/* Avatar Section */}
              <div className="relative">
                <Avatar className="w-32 h-32">
                  <AvatarImage src={profileData.avatar_url} />
                  <AvatarFallback className="text-2xl bg-purple-100 text-purple-600">
                    {profileData.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                  </AvatarFallback>
                </Avatar>
                
                {editing && (
                  <label className="absolute bottom-0 right-0 p-2 bg-purple-600 text-white rounded-full cursor-pointer hover:bg-purple-700 transition-colors">
                    <Camera className="h-4 w-4" />
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleAvatarUpload}
                      className="hidden"
                    />
                  </label>
                )}
              </div>

              {/* Profile Info */}
              <div className="flex-1">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h1 className="text-3xl font-light text-slate-900">
                      {profileData.full_name || user?.email}
                    </h1>
                    <div className="flex items-center gap-4 mt-2">
                      <Badge variant="outline" className="flex items-center gap-1">
                        <User className="h-3 w-3" />
                        {user?.role}
                      </Badge>
                      {stats.average_rating > 0 && (
                        <div className="flex items-center gap-1">
                          <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                          <span className="font-medium">{stats.average_rating}</span>
                          <span className="text-slate-500 text-sm">({stats.review_count} reviews)</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <Button
                    onClick={() => editing ? handleSaveProfile() : setEditing(true)}
                    disabled={loading}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    {loading ? (
                      <>
                        <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Saving...
                      </>
                    ) : editing ? (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Save Changes
                      </>
                    ) : (
                      <>
                        <Edit3 className="h-4 w-4 mr-2" />
                        Edit Profile
                      </>
                    )}
                  </Button>
                </div>

                {/* Basic Info */}
                <div className="space-y-3 text-sm">
                  {profileData.bio && (
                    <p className="text-slate-600">{profileData.bio}</p>
                  )}
                  
                  <div className="flex flex-wrap gap-4">
                    {profileData.location && (
                      <div className="flex items-center gap-1 text-slate-600">
                        <MapPin className="h-4 w-4" />
                        <span>{profileData.location}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-1 text-slate-600">
                      <Calendar className="h-4 w-4" />
                      <span>Joined {formatDate(user?.created_at)}</span>
                    </div>
                    {profileData.website && (
                      <div className="flex items-center gap-1 text-slate-600">
                        <Globe className="h-4 w-4" />
                        <a href={profileData.website} target="_blank" rel="noopener noreferrer" 
                           className="text-purple-600 hover:underline">
                          {profileData.website}
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-8">
          <StatCard 
            icon={Package} 
            label="Listings" 
            value={stats.total_listings}
            color="text-blue-600"
          />
          <StatCard 
            icon={ShoppingCart} 
            label="Sales" 
            value={stats.total_sales}
            color="text-green-600"
          />
          <StatCard 
            icon={Package} 
            label="Purchases" 
            value={stats.total_purchases}
            color="text-purple-600"
          />
          <StatCard 
            icon={Heart} 
            label="Favorites" 
            value={stats.favorite_count}
            color="text-red-600"
          />
          <StatCard 
            icon={CreditCard} 
            label="Revenue" 
            value={formatCurrency(stats.total_revenue)}
            color="text-emerald-600"
          />
          <StatCard 
            icon={Star} 
            label="Rating" 
            value={stats.average_rating.toFixed(1)}
            color="text-yellow-600"
          />
          <StatCard 
            icon={Shield} 
            label="Reviews" 
            value={stats.review_count}
            color="text-indigo-600"
          />
        </div>

        {/* Profile Tabs */}
        <Tabs defaultValue="profile" className="space-y-6">
          <TabsList className="grid grid-cols-4 w-full bg-white shadow-sm">
            <TabsTrigger value="profile" className="flex items-center gap-2">
              <User className="h-4 w-4" />
              Profile
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center gap-2">
              <Lock className="h-4 w-4" />
              Security
            </TabsTrigger>
            <TabsTrigger value="notifications" className="flex items-center gap-2">
              <Bell className="h-4 w-4" />
              Notifications
            </TabsTrigger>
            <TabsTrigger value="preferences" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Preferences
            </TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile">
            <Card className="border-0 shadow-sm">
              <CardHeader>
                <CardTitle>Personal Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <Label htmlFor="full_name">Full Name</Label>
                    <Input
                      id="full_name"
                      value={profileData.full_name}
                      onChange={(e) => handleInputChange('full_name', e.target.value)}
                      disabled={!editing}
                      className="border-slate-200"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      value={profileData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      disabled={!editing}
                      className="border-slate-200"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                      id="phone"
                      value={profileData.phone}
                      onChange={(e) => handleInputChange('phone', e.target.value)}
                      disabled={!editing}
                      className="border-slate-200"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      value={profileData.location}
                      onChange={(e) => handleInputChange('location', e.target.value)}
                      disabled={!editing}
                      className="border-slate-200"
                    />
                  </div>
                  
                  <div className="md:col-span-2">
                    <Label htmlFor="website">Website</Label>
                    <Input
                      id="website"
                      type="url"
                      value={profileData.website}
                      onChange={(e) => handleInputChange('website', e.target.value)}
                      disabled={!editing}
                      className="border-slate-200"
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="bio">Bio</Label>
                  <Textarea
                    id="bio"
                    value={profileData.bio}
                    onChange={(e) => handleInputChange('bio', e.target.value)}
                    disabled={!editing}
                    className="min-h-24 border-slate-200"
                    placeholder="Tell others about yourself..."
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security">
            <div className="space-y-6">
              <Card className="border-0 shadow-sm">
                <CardHeader>
                  <CardTitle>Password & Security</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button variant="outline" className="w-full justify-start">
                    <Lock className="h-4 w-4 mr-2" />
                    Change Password
                  </Button>
                  
                  <div className="flex items-center justify-between p-4 border border-slate-200 rounded-lg">
                    <div>
                      <h4 className="font-medium">Two-Factor Authentication</h4>
                      <p className="text-sm text-slate-600">Add extra security to your account</p>
                    </div>
                    <Badge variant={securitySettings.two_factor_enabled ? "default" : "secondary"}>
                      {securitySettings.two_factor_enabled ? "Enabled" : "Disabled"}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-0 shadow-sm">
                <CardHeader>
                  <CardTitle>Active Sessions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-4 border border-slate-200 rounded-lg">
                      <div>
                        <h4 className="font-medium">Current Session</h4>
                        <p className="text-sm text-slate-600">Chrome on Windows • Active now</p>
                      </div>
                      <Badge variant="default">Current</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Notifications Tab */}
          <TabsContent value="notifications">
            <Card className="border-0 shadow-sm">
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  {[
                    { key: 'email_notifications', label: 'Email Notifications', description: 'Receive updates via email' },
                    { key: 'sms_notifications', label: 'SMS Notifications', description: 'Receive updates via text message' },
                    { key: 'marketing_emails', label: 'Marketing Emails', description: 'Receive promotional content' }
                  ].map(setting => (
                    <div key={setting.key} className="flex items-center justify-between p-4 border border-slate-200 rounded-lg">
                      <div>
                        <h4 className="font-medium">{setting.label}</h4>
                        <p className="text-sm text-slate-600">{setting.description}</p>
                      </div>
                      <input
                        type="checkbox"
                        checked={securitySettings[setting.key]}
                        onChange={(e) => setSecuritySettings(prev => ({
                          ...prev,
                          [setting.key]: e.target.checked
                        }))}
                        className="w-4 h-4 text-purple-600 focus:ring-purple-500"
                      />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Preferences Tab */}
          <TabsContent value="preferences">
            <Card className="border-0 shadow-sm">
              <CardHeader>
                <CardTitle>Account Preferences</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="text-center py-12">
                  <Settings className="h-16 w-16 mx-auto text-slate-400 mb-4" />
                  <h3 className="text-lg font-semibold text-slate-700 mb-2">Preferences Settings</h3>
                  <p className="text-slate-500">Additional preference options will be available here</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      <Footer />
    </div>
  );
};

export default ProfilePage;