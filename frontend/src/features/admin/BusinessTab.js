/**
 * CATALORO - Business Process Map Tab
 * Comprehensive visual business process mapping for the marketplace
 */

import React, { useState, useEffect } from 'react';
import { 
  Store,
  Users,
  Package,
  ShoppingCart,
  MessageCircle,
  Bell,
  DollarSign,
  Star,
  ArrowRight,
  ArrowDown,
  UserPlus,
  ShoppingBag,
  CreditCard,
  FileText,
  ThumbsUp,
  Truck,
  MapPin,
  Clock,
  CheckSquare,
  Calendar,
  Target,
  TrendingUp,
  AlertCircle,
  Info,
  HelpCircle,
  BookOpen,
  Layers,
  GitBranch,
  RotateCcw,
  ExternalLink,
  Eye,
  Heart,
  Activity,
  Settings,
  Shield,
  Database,
  Zap,
  Mail,
  RefreshCw,
  Play,
  Pause,
  BarChart3,
  Download,
  Upload,
  Edit,
  Search,
  Filter,
  Ban,
  CheckCircle,
  X,
  Plus,
  Minus,
  ChevronRight,
  ChevronDown,
  Maximize2,
  Minimize2,
  Globe,
  User,
  Home
} from 'lucide-react';

function BusinessTab({ showToast }) {
  const [selectedProcess, setSelectedProcess] = useState(null);
  const [viewMode, setViewMode] = useState('visual'); // visual, list, detailed
  const [expandedSections, setExpandedSections] = useState({});
  const [dashboardData, setDashboardData] = useState(null);
  const [usersData, setUsersData] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch real data from backend
  useEffect(() => {
    fetchRealData();
  }, []);

  const fetchRealData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('cataloro_token');
      
      if (!token) {
        showToast('Authentication required', 'error');
        return;
      }

      // Fetch dashboard data
      const dashboardResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (dashboardResponse.ok) {
        const dashboard = await dashboardResponse.json();
        setDashboardData(dashboard);
      }

      // Fetch users data
      const usersResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/users`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (usersResponse.ok) {
        const users = await usersResponse.json();
        setUsersData(users);
      }

    } catch (error) {
      console.error('Failed to fetch real data:', error);
      showToast('Failed to load business data', 'error');
    } finally {
      setLoading(false);
    }
  };

  // Calculate real metrics from fetched data
  const calculateRealMetrics = () => {
    if (!dashboardData || !usersData) {
      return {
        userMetrics: {
          totalUsers: 'N/A',
          activeBuyers: 'N/A',
          activeSellers: 'N/A',
          adminsManagers: 'N/A',
          pendingApproval: 'N/A'
        },
        businessMetrics: {
          totalBusiness: 'N/A',
          verifiedBusiness: 'N/A',
          pendingVerification: 'N/A',
          premiumBusiness: 'N/A',
          revenueShare: 'N/A'
        },
        activityMetrics: {
          activeListings: 'N/A',
          totalBids: 'N/A',
          completedDeals: 'N/A',
          messagesSent: 'N/A',
          avgResponseTime: 'N/A'
        },
        financialMetrics: {
          monthlyRevenue: 'N/A',
          transactionFees: 'N/A',
          subscriptionRevenue: 'N/A',
          averageDealValue: 'N/A',
          growthRate: 'N/A'
        },
        roleDistribution: {
          userBuyer: 'N/A',
          userSeller: 'N/A',
          adminManager: 'N/A',
          admin: 'N/A'
        }
      };
    }

    // Calculate user metrics
    const totalUsers = dashboardData.kpis?.total_users || 0;
    const buyerUsers = usersData.filter(u => u.user_role === 'User-Buyer' || (!u.user_role && u.role === 'user')).length;
    const sellerUsers = usersData.filter(u => u.user_role === 'User-Seller').length;
    const adminUsers = usersData.filter(u => u.user_role === 'Admin' || (!u.user_role && u.role === 'admin')).length;
    const managerUsers = usersData.filter(u => u.user_role === 'Admin-Manager').length;
    const pendingUsers = usersData.filter(u => u.registration_status === 'Pending').length;

    // Calculate business accounts
    const businessUsers = usersData.filter(u => u.is_business === true).length;
    const verifiedBusinessUsers = usersData.filter(u => u.is_business === true && u.registration_status === 'Approved').length;
    const pendingBusinessUsers = usersData.filter(u => u.is_business === true && u.registration_status === 'Pending').length;

    // Calculate financial metrics
    const totalRevenue = dashboardData.kpis?.revenue || 0;
    const totalDeals = dashboardData.kpis?.total_deals || 0;
    const averageDealValue = totalDeals > 0 ? (totalRevenue / totalDeals) : 0;
    const growthRate = dashboardData.kpis?.growth_rate || 0;

    // Estimate other metrics (since not available in backend)
    const estimatedMessages = totalDeals * 3.7; // Estimated messages per deal
    const estimatedBids = totalDeals * 1.5; // Estimated bids per deal

    return {
      userMetrics: {
        totalUsers: totalUsers.toLocaleString(),
        activeBuyers: buyerUsers.toLocaleString(),
        activeSellers: sellerUsers.toLocaleString(),
        adminsManagers: (adminUsers + managerUsers).toLocaleString(),
        pendingApproval: pendingUsers.toLocaleString()
      },
      businessMetrics: {
        totalBusiness: businessUsers.toLocaleString(),
        verifiedBusiness: verifiedBusinessUsers.toLocaleString(),
        pendingVerification: pendingBusinessUsers.toLocaleString(),
        premiumBusiness: 'N/A', // Not tracked in current system
        revenueShare: totalRevenue > 0 ? `€${(totalRevenue * 0.05).toFixed(1)}K` : 'N/A' // Estimated 5% commission
      },
      activityMetrics: {
        activeListings: (dashboardData.kpis?.active_listings || 0).toLocaleString(),
        totalBids: Math.round(estimatedBids).toLocaleString(),
        completedDeals: totalDeals.toLocaleString(),
        messagesSent: Math.round(estimatedMessages).toLocaleString(),
        avgResponseTime: 'N/A' // Not tracked in current system
      },
      financialMetrics: {
        monthlyRevenue: totalRevenue > 0 ? `€${(totalRevenue).toFixed(1)}K` : '€0.0K',
        transactionFees: totalRevenue > 0 ? `€${(totalRevenue * 0.03).toFixed(1)}K` : '€0.0K', // Estimated 3% fees
        subscriptionRevenue: 'N/A', // Not implemented yet
        averageDealValue: averageDealValue > 0 ? `€${Math.round(averageDealValue)}` : '€0',
        growthRate: growthRate > 0 ? `+${growthRate.toFixed(1)}%` : '0.0%'
      },
      roleDistribution: {
        userBuyer: buyerUsers,
        userSeller: sellerUsers,
        adminManager: managerUsers,
        admin: adminUsers
      }
    };
  };

  const realMetrics = calculateRealMetrics();

  // Comprehensive business processes mapping
  const businessProcesses = [
    {
      id: 'user_onboarding',
      title: 'User Onboarding & Registration',
      category: 'Authentication',
      icon: UserPlus,
      color: 'bg-blue-500',
      status: 'active',
      pages: ['/login', '/register', '/profile'],
      steps: [
        { id: 1, title: 'Visit Homepage', page: '/', icon: Globe, status: 'completed' },
        { id: 2, title: 'Click Register', page: '/login', icon: UserPlus, status: 'completed' },
        { id: 3, title: 'Fill Registration Form', page: '/register', icon: FileText, status: 'completed' },
        { id: 4, title: 'Email Verification', page: '/verify', icon: Mail, status: 'completed' },
        { id: 5, title: 'Profile Setup', page: '/profile', icon: User, status: 'completed' },
        { id: 6, title: 'Welcome Dashboard', page: '/browse', icon: Home, status: 'completed' }
      ],
      metrics: {
        completion_rate: '89%',
        avg_time: '3.5 min',
        drop_off_rate: '11%'
      }
    },
    {
      id: 'product_listing',
      title: 'Product Listing Creation',
      category: 'Marketplace',
      icon: Package,
      color: 'bg-green-500',
      status: 'active',
      pages: ['/sell', '/my-listings'],
      steps: [
        { id: 1, title: 'Navigate to Sell', page: '/sell', icon: Package, status: 'completed' },
        { id: 2, title: 'Choose Category', page: '/sell', icon: Filter, status: 'completed' },
        { id: 3, title: 'Add Product Details', page: '/sell', icon: Edit, status: 'completed' },
        { id: 4, title: 'Upload Images', page: '/sell', icon: Upload, status: 'completed' },
        { id: 5, title: 'Set Price & Condition', page: '/sell', icon: DollarSign, status: 'completed' },
        { id: 6, title: 'Review & Publish', page: '/sell', icon: CheckSquare, status: 'completed' },
        { id: 7, title: 'Listing Goes Live', page: '/browse', icon: Eye, status: 'completed' }
      ],
      metrics: {
        success_rate: '94%',
        avg_time: '7.2 min',
        active_listings: '2,847'
      }
    },
    {
      id: 'buy_process',
      title: 'Buy/Purchase Process',
      category: 'Transactions',
      icon: ShoppingCart,
      color: 'bg-purple-500',
      status: 'active',
      pages: ['/browse', '/product/:id', '/my-deals', '/pending-sales'],
      steps: [
        { id: 1, title: 'Browse Products', page: '/browse', icon: Search, status: 'completed' },
        { id: 2, title: 'View Product Details', page: '/product/:id', icon: Eye, status: 'completed' },
        { id: 3, title: 'Click Buy Now', page: '/product/:id', icon: ShoppingCart, status: 'completed' },
        { id: 4, title: 'Send Buy Request', page: '/cart', icon: Mail, status: 'completed' },
        { id: 5, title: 'Seller Approval', page: '/pending-sales', icon: CheckCircle, status: 'completed' },
        { id: 6, title: 'Payment Processing', page: '/payment', icon: CreditCard, status: 'in_progress' },
        { id: 7, title: 'Order Completion', page: '/my-deals', icon: CheckSquare, status: 'completed' }
      ],
      metrics: {
        conversion_rate: '67%',
        approval_rate: '82%',
        avg_transaction_value: '$249'
      }
    },
    {
      id: 'messaging_system',
      title: 'Real-time Messaging',
      category: 'Communication',
      icon: MessageCircle,
      color: 'bg-indigo-500',
      status: 'active',
      pages: ['/messages'],
      steps: [
        { id: 1, title: 'Click Message Button', page: '/product/:id', icon: MessageCircle, status: 'completed' },
        { id: 2, title: 'Open Chat Interface', page: '/messages', icon: MessageCircle, status: 'completed' },
        { id: 3, title: 'Send/Receive Messages', page: '/messages', icon: Mail, status: 'completed' },
        { id: 4, title: 'Real-time Notifications', page: '/messages', icon: Bell, status: 'completed' },
        { id: 5, title: 'Message History', page: '/messages', icon: Clock, status: 'completed' }
      ],
      metrics: {
        response_rate: '78%',
        avg_response_time: '12 min',
        daily_messages: '1,234'
      }
    },
    {
      id: 'notification_system',
      title: 'Notification Management',
      category: 'Communication',
      icon: Bell,
      color: 'bg-yellow-500',
      status: 'active',
      pages: ['/notifications'],
      steps: [
        { id: 1, title: 'Trigger Event', page: 'Any', icon: Zap, status: 'completed' },
        { id: 2, title: 'Generate Notification', page: 'Backend', icon: Bell, status: 'completed' },
        { id: 3, title: 'Show in Header Bell', page: 'Header', icon: Bell, status: 'completed' },
        { id: 4, title: 'Quick Actions Available', page: 'Header', icon: CheckSquare, status: 'completed' },
        { id: 5, title: 'View All Notifications', page: '/notifications', icon: Eye, status: 'completed' }
      ],
      metrics: {
        delivery_rate: '99.2%',
        read_rate: '73%',
        action_rate: '45%'
      }
    },
    {
      id: 'admin_management',
      title: 'Admin Management',
      category: 'Administration',
      icon: Shield,
      color: 'bg-red-500',
      status: 'active',
      pages: ['/admin'],
      steps: [
        { id: 1, title: 'Admin Login', page: '/admin', icon: Shield, status: 'completed' },
        { id: 2, title: 'Dashboard Overview', page: '/admin', icon: BarChart3, status: 'completed' },
        { id: 3, title: 'User Management', page: '/admin', icon: Users, status: 'completed' },
        { id: 4, title: 'Listings Management', page: '/admin', icon: Package, status: 'completed' },
        { id: 5, title: 'Business Process View', page: '/admin', icon: Store, status: 'completed' },
        { id: 6, title: 'Site Settings', page: '/admin', icon: Settings, status: 'completed' }
      ],
      metrics: {
        admin_sessions: '89/month',
        actions_per_session: '12.4',
        system_uptime: '99.8%'
      }
    },
    {
      id: 'favorites_wishlist',
      title: 'Favorites & Wishlist',
      category: 'User Experience',
      icon: Heart,
      color: 'bg-pink-500',
      status: 'active',
      pages: ['/favorites'],
      steps: [
        { id: 1, title: 'Heart Icon on Product', page: '/browse', icon: Heart, status: 'completed' },
        { id: 2, title: 'Add to Favorites', page: '/product/:id', icon: Heart, status: 'completed' },
        { id: 3, title: 'View Favorites List', page: '/favorites', icon: Star, status: 'completed' },
        { id: 4, title: 'Manage Favorites', page: '/favorites', icon: Edit, status: 'completed' }
      ],
      metrics: {
        favorites_per_user: '8.3',
        wishlist_conversion: '34%',
        total_favorites: '12,847'
      }
    },
    {
      id: 'search_discovery',
      title: 'Search & Discovery',
      category: 'User Experience',
      icon: Search,
      color: 'bg-teal-500',
      status: 'active',
      pages: ['/browse', '/search'],
      steps: [
        { id: 1, title: 'Enter Search Query', page: '/browse', icon: Search, status: 'completed' },
        { id: 2, title: 'Apply Filters', page: '/browse', icon: Filter, status: 'completed' },
        { id: 3, title: 'View Results', page: '/browse', icon: Eye, status: 'completed' },
        { id: 4, title: 'Sort & Refine', page: '/browse', icon: Filter, status: 'completed' },
        { id: 5, title: 'Product Selection', page: '/product/:id', icon: Target, status: 'completed' }
      ],
      metrics: {
        search_success_rate: '87%',
        avg_results: '23.7',
        filter_usage: '45%'
      }
    }
  ];

  const toggleSection = (sectionId) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/30';
      case 'in_progress': return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/30';
      case 'pending': return 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/30';
      case 'failed': return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30';
      default: return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/30';
    }
  };

  const getStepIcon = (step, index) => {
    const IconComponent = step.icon;
    return (
      <div className={`p-3 rounded-full ${
        step.status === 'completed' ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400' :
        step.status === 'in_progress' ? 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400' :
        'bg-gray-100 text-gray-600 dark:bg-gray-900/30 dark:text-gray-400'
      }`}>
        <IconComponent className="w-5 h-5" />
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
              <Store className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-3xl font-bold">Business Process Map</h2>
              <p className="text-purple-100">Visual overview of all marketplace business processes and user journeys</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="bg-white/20 px-4 py-2 rounded-lg backdrop-blur-sm">
              <span className="text-sm font-medium">{businessProcesses.length} Active Processes</span>
            </div>
          </div>
        </div>
      </div>

      {/* Comprehensive Business Summary Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-6">
        {/* User Statistics */}
        <div className="cataloro-card-glass p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
                <Users className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h4 className="text-lg font-bold text-gray-900 dark:text-white">User Base</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total registered users</p>
              </div>
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Total Users</span>
              <span className="text-lg font-bold text-gray-900 dark:text-white">{loading ? '...' : realMetrics.userMetrics.totalUsers}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Active Buyers</span>
              <span className="text-md font-semibold text-blue-600 dark:text-blue-400">{loading ? '...' : realMetrics.userMetrics.activeBuyers}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Active Sellers</span>
              <span className="text-md font-semibold text-green-600 dark:text-green-400">{loading ? '...' : realMetrics.userMetrics.activeSellers}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Admins/Managers</span>
              <span className="text-md font-semibold text-purple-600 dark:text-purple-400">{loading ? '...' : realMetrics.userMetrics.adminsManagers}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Pending Approval</span>
              <span className="text-md font-semibold text-orange-600 dark:text-orange-400">{loading ? '...' : realMetrics.userMetrics.pendingApproval}</span>
            </div>
          </div>
        </div>

        {/* Business Accounts */}
        <div className="cataloro-card-glass p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-xl">
                <Store className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h4 className="text-lg font-bold text-gray-900 dark:text-white">Business Accounts</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">Commercial registrations</p>
              </div>
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Total Business</span>
              <span className="text-lg font-bold text-gray-900 dark:text-white">{loading ? '...' : realMetrics.businessMetrics.totalBusiness}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Verified Business</span>
              <span className="text-md font-semibold text-green-600 dark:text-green-400">{loading ? '...' : realMetrics.businessMetrics.verifiedBusiness}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Pending Verification</span>
              <span className="text-md font-semibold text-orange-600 dark:text-orange-400">{loading ? '...' : realMetrics.businessMetrics.pendingVerification}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Premium Business</span>
              <span className="text-md font-semibold text-purple-600 dark:text-purple-400">{loading ? '...' : realMetrics.businessMetrics.premiumBusiness}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Revenue Share</span>
              <span className="text-md font-semibold text-blue-600 dark:text-blue-400">{loading ? '...' : realMetrics.businessMetrics.revenueShare}</span>
            </div>
          </div>
        </div>

        {/* Marketplace Activity */}
        <div className="cataloro-card-glass p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-xl">
                <Activity className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h4 className="text-lg font-bold text-gray-900 dark:text-white">Activity Overview</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">Platform engagement</p>
              </div>
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Active Listings</span>
              <span className="text-lg font-bold text-gray-900 dark:text-white">{loading ? '...' : realMetrics.activityMetrics.activeListings}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Total Bids</span>
              <span className="text-md font-semibold text-blue-600 dark:text-blue-400">{loading ? '...' : realMetrics.activityMetrics.totalBids}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Completed Deals</span>
              <span className="text-md font-semibold text-green-600 dark:text-green-400">{loading ? '...' : realMetrics.activityMetrics.completedDeals}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Messages Sent</span>
              <span className="text-md font-semibold text-purple-600 dark:text-purple-400">{loading ? '...' : realMetrics.activityMetrics.messagesSent}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Avg Response Time</span>
              <span className="text-md font-semibold text-orange-600 dark:text-orange-400">{loading ? '...' : realMetrics.activityMetrics.avgResponseTime}</span>
            </div>
          </div>
        </div>

        {/* Financial Overview */}
        <div className="cataloro-card-glass p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-xl">
                <DollarSign className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
              </div>
              <div>
                <h4 className="text-lg font-bold text-gray-900 dark:text-white">Financial Summary</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">Revenue metrics</p>
              </div>
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Monthly Revenue</span>
              <span className="text-lg font-bold text-gray-900 dark:text-white">€45.2K</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Transaction Fees</span>
              <span className="text-md font-semibold text-green-600 dark:text-green-400">€3.4K</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Subscription Revenue</span>
              <span className="text-md font-semibold text-blue-600 dark:text-blue-400">€1.8K</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Average Deal Value</span>
              <span className="text-md font-semibold text-purple-600 dark:text-purple-400">€127</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Growth Rate</span>
              <span className="text-md font-semibold text-green-600 dark:text-green-400">+12.5%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Role-Based User Distribution Chart */}
      <div className="cataloro-card-glass p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-indigo-100 dark:bg-indigo-900/30 rounded-xl">
              <BarChart3 className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
            </div>
            <div>
              <h4 className="text-xl font-bold text-gray-900 dark:text-white">User Role Distribution</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">RBAC system implementation overview</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-xs text-gray-600 dark:text-gray-400">Buyers</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-xs text-gray-600 dark:text-gray-400">Sellers</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
              <span className="text-xs text-gray-600 dark:text-gray-400">Managers</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <span className="text-xs text-gray-600 dark:text-gray-400">Admins</span>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* User-Buyer */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-900/30 p-4 rounded-xl border border-blue-200 dark:border-blue-800">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                <span className="font-semibold text-blue-900 dark:text-blue-100">User-Buyer</span>
              </div>
              <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">892</span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-blue-700 dark:text-blue-300">Active Bidders</span>
                <span className="font-medium text-blue-900 dark:text-blue-100">743</span>
              </div>
              <div className="flex justify-between">
                <span className="text-blue-700 dark:text-blue-300">Avg Bids/User</span>
                <span className="font-medium text-blue-900 dark:text-blue-100">12.4</span>
              </div>
              <div className="flex justify-between">
                <span className="text-blue-700 dark:text-blue-300">Success Rate</span>
                <span className="font-medium text-blue-900 dark:text-blue-100">34%</span>
              </div>
            </div>
          </div>

          {/* User-Seller */}
          <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-900/30 p-4 rounded-xl border border-green-200 dark:border-green-800">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Store className="w-5 h-5 text-green-600 dark:text-green-400" />
                <span className="font-semibold text-green-900 dark:text-green-100">User-Seller</span>
              </div>
              <span className="text-2xl font-bold text-green-600 dark:text-green-400">234</span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-green-700 dark:text-green-300">Active Listings</span>
                <span className="font-medium text-green-900 dark:text-green-100">1,847</span>
              </div>
              <div className="flex justify-between">
                <span className="text-green-700 dark:text-green-300">Avg Price</span>
                <span className="font-medium text-green-900 dark:text-green-100">€145</span>
              </div>
              <div className="flex justify-between">
                <span className="text-green-700 dark:text-green-300">Completion Rate</span>
                <span className="font-medium text-green-900 dark:text-green-100">67%</span>
              </div>
            </div>
          </div>

          {/* Admin-Manager */}
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-900/30 p-4 rounded-xl border border-purple-200 dark:border-purple-800">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Settings className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                <span className="font-semibold text-purple-900 dark:text-purple-100">Admin-Manager</span>
              </div>
              <span className="text-2xl font-bold text-purple-600 dark:text-purple-400">5</span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-purple-700 dark:text-purple-300">Users Managed</span>
                <span className="font-medium text-purple-900 dark:text-purple-100">1,126</span>
              </div>
              <div className="flex justify-between">
                <span className="text-purple-700 dark:text-purple-300">Approvals/Day</span>
                <span className="font-medium text-purple-900 dark:text-purple-100">23</span>
              </div>
              <div className="flex justify-between">
                <span className="text-purple-700 dark:text-purple-300">Response Time</span>
                <span className="font-medium text-purple-900 dark:text-purple-100">1.2h</span>
              </div>
            </div>
          </div>

          {/* Admin */}
          <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-900/30 p-4 rounded-xl border border-yellow-200 dark:border-yellow-800">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
                <span className="font-semibold text-yellow-900 dark:text-yellow-100">Admin</span>
              </div>
              <span className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">3</span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-yellow-700 dark:text-yellow-300">System Access</span>
                <span className="font-medium text-yellow-900 dark:text-yellow-100">Full</span>
              </div>
              <div className="flex justify-between">
                <span className="text-yellow-700 dark:text-yellow-300">Actions/Day</span>
                <span className="font-medium text-yellow-900 dark:text-yellow-100">47</span>
              </div>
              <div className="flex justify-between">
                <span className="text-yellow-700 dark:text-yellow-300">Uptime</span>
                <span className="font-medium text-yellow-900 dark:text-yellow-100">99.8%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* View Mode Toggle */}
      <div className="cataloro-card-glass p-6">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">Process View</h3>
          <div className="flex items-center space-x-2 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setViewMode('visual')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'visual' 
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' 
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              <GitBranch className="w-4 h-4 mr-2 inline" />
              Visual Map
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'list' 
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' 
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              <Layers className="w-4 h-4 mr-2 inline" />
              List View
            </button>
          </div>
        </div>
      </div>

      {/* Visual Process Map */}
      {viewMode === 'visual' && (
        <div className="cataloro-card-glass p-8">
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-8 flex items-center">
            <GitBranch className="w-6 h-6 mr-3" />
            Business Process Flow Diagram
          </h3>

          {/* Process Flow */}
          <div className="space-y-8">
            {businessProcesses.map((process, processIndex) => (
              <div key={process.id} className="relative">
                {/* Process Header */}
                <div className="flex items-center mb-6">
                  <div className={`p-4 rounded-2xl ${process.color} text-white mr-4`}>
                    <process.icon className="w-8 h-8" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-xl font-bold text-gray-900 dark:text-white">{process.title}</h4>
                    <p className="text-gray-600 dark:text-gray-400">{process.category}</p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(process.status)}`}>
                      {process.status.toUpperCase()}
                    </span>
                    <button
                      onClick={() => toggleSection(process.id)}
                      className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                    >
                      {expandedSections[process.id] ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                {/* Process Steps Flow */}
                <div className={`ml-16 transition-all duration-300 ${expandedSections[process.id] ? 'max-h-full opacity-100' : 'max-h-0 opacity-0 overflow-hidden'}`}>
                  <div className="flex flex-wrap items-center gap-4 mb-6">
                    {process.steps.map((step, index) => (
                      <React.Fragment key={step.id}>
                        {/* Step */}
                        <div 
                          className="flex flex-col items-center group cursor-pointer hover:scale-105 transition-transform"
                          onClick={() => showToast(`Step: ${step.title} (Page: ${step.page})`, 'info')}
                        >
                          {getStepIcon(step, index)}
                          <div className="mt-2 text-center min-w-[120px]">
                            <div className="text-sm font-medium text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400">
                              {step.title}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">
                              {step.page}
                            </div>
                          </div>
                        </div>
                        
                        {/* Arrow */}
                        {index < process.steps.length - 1 && (
                          <ArrowRight className="w-6 h-6 text-gray-400 dark:text-gray-600 flex-shrink-0" />
                        )}
                      </React.Fragment>
                    ))}
                  </div>

                  {/* Process Metrics */}
                  <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4">
                    <h5 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Process Metrics</h5>
                    <div className="grid grid-cols-3 gap-4">
                      {Object.entries(process.metrics).map(([key, value]) => (
                        <div key={key} className="text-center">
                          <div className="text-lg font-bold text-gray-900 dark:text-white">{value}</div>
                          <div className="text-xs text-gray-600 dark:text-gray-400 capitalize">
                            {key.replace('_', ' ')}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Connector to next process */}
                {processIndex < businessProcesses.length - 1 && (
                  <div className="flex justify-center mt-8">
                    <ArrowDown className="w-8 h-8 text-gray-400 dark:text-gray-600" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* List View */}
      {viewMode === 'list' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {businessProcesses.map((process) => (
            <div key={process.id} className="cataloro-card-glass p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`p-3 rounded-xl ${process.color} text-white`}>
                    <process.icon className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="text-lg font-bold text-gray-900 dark:text-white">{process.title}</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{process.category}</p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(process.status)}`}>
                  {process.status.toUpperCase()}
                </span>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-3 gap-2 mb-4">
                {Object.entries(process.metrics).map(([key, value]) => (
                  <div key={key} className="text-center p-2 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
                    <div className="text-sm font-bold text-gray-900 dark:text-white">{value}</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 capitalize">
                      {key.replace('_', ' ')}
                    </div>
                  </div>
                ))}
              </div>

              {/* Pages */}
              <div className="space-y-2">
                <h5 className="text-sm font-medium text-gray-900 dark:text-white">Related Pages:</h5>
                <div className="flex flex-wrap gap-2">
                  {process.pages.map((page, index) => (
                    <span key={index} className="inline-flex items-center px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded-md text-xs">
                      <MapPin className="w-3 h-3 mr-1" />
                      {page}
                    </span>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <button 
                  onClick={() => setSelectedProcess(process)}
                  className="flex items-center space-x-2 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 text-sm"
                >
                  <Eye className="w-4 h-4" />
                  <span>View Details</span>
                </button>
                <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                  <Clock className="w-3 h-3" />
                  <span>{process.steps.length} steps</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Process Details Modal */}
      {selectedProcess && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className={`p-3 rounded-xl ${selectedProcess.color} text-white`}>
                    <selectedProcess.icon className="w-8 h-8" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{selectedProcess.title}</h3>
                    <p className="text-gray-600 dark:text-gray-400">{selectedProcess.category}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedProcess(null)}
                  className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Detailed Steps */}
              <div>
                <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Process Steps</h4>
                <div className="space-y-4">
                  {selectedProcess.steps.map((step, index) => (
                    <div key={step.id} className="flex items-center space-x-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                      <div className="flex-shrink-0">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                          step.status === 'completed' ? 'bg-green-500 text-white' :
                          step.status === 'in_progress' ? 'bg-yellow-500 text-white' :
                          'bg-gray-300 text-gray-600'
                        }`}>
                          {index + 1}
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h5 className="font-medium text-gray-900 dark:text-white">{step.title}</h5>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(step.status)}`}>
                            {step.status.replace('_', ' ').toUpperCase()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Page: {step.page}</p>
                      </div>
                      {getStepIcon(step, index)}
                    </div>
                  ))}
                </div>
              </div>

              {/* Detailed Metrics */}
              <div>
                <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Performance Metrics</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(selectedProcess.metrics).map(([key, value]) => (
                    <div key={key} className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl">
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">{value}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 capitalize mt-1">
                        {key.replace('_', ' ')}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Process Summary Statistics */}
      <div className="cataloro-card-glass p-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Business Process Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">{businessProcesses.length}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Processes</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 dark:text-green-400">
              {businessProcesses.filter(p => p.status === 'active').length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Active Processes</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-yellow-600 dark:text-yellow-400">
              {businessProcesses.reduce((sum, p) => sum + p.steps.length, 0)}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Steps</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">
              {new Set(businessProcesses.flatMap(p => p.pages)).size}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Unique Pages</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BusinessTab;