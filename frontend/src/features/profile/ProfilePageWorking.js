import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { profileAPI, listingsAPI } from '../../services/api';
import { useToast } from '../../hooks/use-toast';
import Header from '../../components/layout/Header';
import Footer from '../../components/layout/Footer';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { 
  User, MapPin, Star, Calendar, Package, DollarSign, 
  MessageCircle, Bell, Edit, Camera, Globe, Phone, Mail,
  TrendingUp, Users, ShoppingBag, Award, Settings, 
  BarChart3, PieChart, Activity, Target, Zap
} from 'lucide-react';

const ProfilePageWorking = () => {
  const { user, updateUserProfile } = useAuth();
  const { toast } = useToast();
  
  // State management
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Profile data
  const [profile, setProfile] = useState({});
  const [listings, setListings] = useState([]);
  const [stats, setStats] = useState({
    total_sales: 0,
    total_listings: 0,
    average_rating: 0,
    review_count: 0,
    response_time: '2 hours',
    completion_rate: 98.5,
    member_since: '2024'
  });
  
  // Messages and notifications
  const [messages, setMessages] = useState([
    {
      id: 1,
      from: 'buyer_john',
      subject: 'Question about BMW exhaust system',
      preview: 'Hi, I am interested in your BMW exhaust system listing...',
      time: '2 hours ago',
      unread: true
    },
    {
      id: 2,
      from: 'sarah_m',
      subject: 'Payment confirmation',
      preview: 'Payment has been processed for the Mercedes catalytic converter...',
      time: '5 hours ago',
      unread: false
    }
  ]);
  
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      type: 'sale',
      message: 'Your Audi A4 catalytic converter sold for €125',
      time: '1 hour ago',
      icon: DollarSign,
      color: 'text-green-600'
    },
    {
      id: 2,
      type: 'review',
      message: 'You received a 5-star review from buyer_mike',
      time: '3 hours ago',
      icon: Star,
      color: 'text-yellow-600'
    },
    {
      id: 3,
      type: 'message',
      message: 'New message about BMW X5 listing',
      time: '6 hours ago',
      icon: MessageCircle,
      color: 'text-blue-600'
    }
  ]);

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      
      // Simulate API calls with realistic data
      setProfile({
        ...user,
        bio: user?.bio || 'Professional automotive parts dealer with 10+ years experience',
        location: user?.location || 'Berlin, Germany',
        website: user?.website || 'www.autoparts-pro.com',
        business_verified: true,
        response_rate: 95.8,
        languages: ['German', 'English', 'French']
      });
      
      // Simulate stats
      setStats({
        total_sales: 1247,
        total_listings: 89,
        average_rating: 4.8,
        review_count: 312,
        response_time: '< 2 hours',
        completion_rate: 98.5,
        member_since: '2019',
        monthly_sales: 45,
        revenue_this_month: 4580
      });
      
    } catch (error) {
      console.error('Error fetching profile:', error);
      toast({
        title: "Error",
        description: "Failed to load profile data",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  // Modern Dashboard Tile Component
  const DashboardTile = ({ title, value, subtitle, icon: Icon, color, trend, bgGradient }) => (
    <Card className={`relative overflow-hidden border-0 shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-105 ${bgGradient}`}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white/80 text-sm font-medium">{title}</p>
            <p className="text-3xl font-bold text-white mt-1">{value}</p>
            {subtitle && <p className="text-white/70 text-xs mt-1">{subtitle}</p>}
          </div>
          <div className={`p-3 rounded-full bg-white/20 backdrop-blur-sm ${color}`}>
            <Icon className="h-8 w-8 text-white" />
          </div>
        </div>
        {trend && (
          <div className="mt-4 flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-green-300" />
            <span className="text-white/80 text-sm">{trend}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50/30 to-slate-100">
      <Header />
      
      <div className="container mx-auto px-4 py-8">
        {/* Profile Header */}
        <div className="relative mb-8">
          {/* Cover Image */}
          <div className="h-48 bg-gradient-to-r from-purple-600 via-blue-600 to-teal-600 rounded-2xl shadow-xl relative overflow-hidden">
            <div className="absolute inset-0 bg-black/20"></div>
            <div className="absolute bottom-6 left-6 right-6">
              <div className="flex items-end gap-6">
                {/* Profile Picture */}
                <div className="relative">
                  <div className="w-24 h-24 bg-white rounded-2xl shadow-xl flex items-center justify-center border-4 border-white">
                    <User className="h-12 w-12 text-purple-600" />
                  </div>
                  <Button size="sm" className="absolute -bottom-2 -right-2 h-8 w-8 p-0 bg-white text-purple-600 hover:bg-purple-50 shadow-md">
                    <Camera className="h-4 w-4" />
                  </Button>
                </div>
                
                {/* Profile Info */}
                <div className="flex-1 text-white pb-2">
                  <h1 className="text-3xl font-bold mb-1">{profile.full_name}</h1>
                  <div className="flex items-center gap-4 text-white/90">
                    <div className="flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      <span>{profile.location}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span>{stats.average_rating}</span>
                      <span className="text-white/70">({stats.review_count} reviews)</span>
                    </div>
                    {profile.business_verified && (
                      <Badge className="bg-green-500/20 text-green-100 border-green-300/30">
                        <Award className="h-3 w-3 mr-1" />
                        Verified Business
                      </Badge>
                    )}
                  </div>
                </div>
                
                {/* Action Buttons */}
                <div className="flex gap-2 pb-2">
                  <Button 
                    onClick={() => setEditing(!editing)}
                    className="bg-white/10 hover:bg-white/20 text-white border-white/20 backdrop-blur-sm"
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edit Profile
                  </Button>
                  <Button className="bg-white text-purple-600 hover:bg-purple-50">
                    <Settings className="h-4 w-4 mr-2" />
                    Settings
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Dashboard Tiles */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <DashboardTile
            title="Total Sales"
            value={stats.total_sales.toLocaleString()}
            subtitle="All time"
            icon={DollarSign}
            color="text-green-600"
            bgGradient="bg-gradient-to-br from-green-500 to-emerald-600"
            trend="+12% this month"
          />
          <DashboardTile
            title="Active Listings"
            value={stats.total_listings}
            subtitle="Currently listed"
            icon={Package}
            color="text-blue-600"
            bgGradient="bg-gradient-to-br from-blue-500 to-cyan-600"
            trend="3 new this week"
          />
          <DashboardTile
            title="Rating"
            value={stats.average_rating}
            subtitle={`${stats.review_count} reviews`}
            icon={Star}
            color="text-yellow-600"
            bgGradient="bg-gradient-to-br from-yellow-500 to-orange-500"
            trend="Excellent seller"
          />
          <DashboardTile
            title="Response Time"
            value={stats.response_time}
            subtitle={`${stats.response_rate}% response rate`}
            icon={Zap}
            color="text-purple-600"
            bgGradient="bg-gradient-to-br from-purple-500 to-pink-600"
            trend="Very responsive"
          />
        </div>

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 bg-white shadow-sm h-12">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="listings" className="flex items-center gap-2">
              <Package className="h-4 w-4" />
              Listings
            </TabsTrigger>
            <TabsTrigger value="messages" className="flex items-center gap-2">
              <MessageCircle className="h-4 w-4" />
              Messages
              {messages.filter(m => m.unread).length > 0 && (
                <Badge className="ml-1 h-5 w-5 p-0 bg-red-500 text-white text-xs">
                  {messages.filter(m => m.unread).length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="notifications" className="flex items-center gap-2">
              <Bell className="h-4 w-4" />
              Notifications
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center gap-2">
              <PieChart className="h-4 w-4" />
              Analytics
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Profile Information */}
              <div className="lg:col-span-2">
                <Card className="border-0 shadow-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <User className="h-5 w-5 text-purple-600" />
                      Profile Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {editing ? (
                      <div className="space-y-4">
                        <div>
                          <Label>Full Name</Label>
                          <Input
                            value={profile.full_name || ''}
                            onChange={(e) => setProfile(prev => ({ ...prev, full_name: e.target.value }))}
                          />
                        </div>
                        <div>
                          <Label>Bio</Label>
                          <Textarea
                            value={profile.bio || ''}
                            onChange={(e) => setProfile(prev => ({ ...prev, bio: e.target.value }))}
                            rows={3}
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Label>Location</Label>
                            <Input
                              value={profile.location || ''}
                              onChange={(e) => setProfile(prev => ({ ...prev, location: e.target.value }))}
                            />
                          </div>
                          <div>
                            <Label>Website</Label>
                            <Input
                              value={profile.website || ''}
                              onChange={(e) => setProfile(prev => ({ ...prev, website: e.target.value }))}
                            />
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button onClick={() => setEditing(false)} className="bg-purple-600 hover:bg-purple-700">
                            Save Changes
                          </Button>
                          <Button variant="outline" onClick={() => setEditing(false)}>
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <div>
                          <h4 className="font-semibold text-slate-900">About</h4>
                          <p className="text-slate-600 mt-1">{profile.bio}</p>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="flex items-center gap-2">
                            <MapPin className="h-4 w-4 text-slate-400" />
                            <span className="text-slate-600">{profile.location}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Globe className="h-4 w-4 text-slate-400" />
                            <span className="text-slate-600">{profile.website}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4 text-slate-400" />
                            <span className="text-slate-600">Member since {stats.member_since}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Users className="h-4 w-4 text-slate-400" />
                            <span className="text-slate-600">{profile.languages?.join(', ')}</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Quick Stats */}
              <div className="space-y-6">
                <Card className="border-0 shadow-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-5 w-5 text-purple-600" />
                      Quick Stats
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-600">Completion Rate</span>
                        <span className="font-semibold text-green-600">{stats.completion_rate}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-600">Monthly Sales</span>
                        <span className="font-semibold">{stats.monthly_sales}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-600">Revenue (Month)</span>
                        <span className="font-semibold text-purple-600">€{stats.revenue_this_month}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Messages Tab */}
          <TabsContent value="messages">
            <Card className="border-0 shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageCircle className="h-5 w-5 text-purple-600" />
                  Messages
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`p-4 rounded-lg border transition-colors hover:bg-slate-50 cursor-pointer ${
                        message.unread ? 'bg-purple-50 border-purple-200' : 'bg-white border-slate-200'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h4 className="font-semibold text-slate-900">{message.subject}</h4>
                            {message.unread && (
                              <Badge className="bg-purple-100 text-purple-700">New</Badge>
                            )}
                          </div>
                          <p className="text-slate-600 text-sm mt-1">From: {message.from}</p>
                          <p className="text-slate-500 text-sm mt-1">{message.preview}</p>
                        </div>
                        <span className="text-xs text-slate-400">{message.time}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Notifications Tab */}
          <TabsContent value="notifications">
            <Card className="border-0 shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="h-5 w-5 text-purple-600" />
                  Recent Notifications
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {notifications.map((notification) => (
                    <div key={notification.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-50">
                      <div className={`p-2 rounded-full ${notification.color.replace('text-', 'bg-').replace('-600', '-100')}`}>
                        <notification.icon className={`h-4 w-4 ${notification.color}`} />
                      </div>
                      <div className="flex-1">
                        <p className="text-slate-800">{notification.message}</p>
                        <p className="text-slate-500 text-sm">{notification.time}</p>
                      </div>
                    </div>
                  ))}
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

export default ProfilePageWorking;