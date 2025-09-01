/**
 * CATALORO - Ultra-Modern Info/Functionality Page
 * Comprehensive showcase of all marketplace features with stunning design
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Store, 
  ShoppingCart, 
  Heart, 
  MessageCircle, 
  Bell, 
  Shield, 
  Search, 
  TrendingUp, 
  Users, 
  Star, 
  Zap, 
  ArrowRight,
  CheckCircle,
  Package,
  DollarSign,
  Settings,
  BarChart3,
  Globe,
  Sparkles,
  Layout,
  Camera,
  Filter,
  Eye,
  UserCheck
} from 'lucide-react';
import { UI_CONFIG } from '../../config/directions';

function InfoPage() {
  const features = [
    {
      category: "Marketplace Core",
      icon: Store,
      color: "from-blue-500 to-purple-600",
      items: [
        {
          title: "Browse Marketplace",
          description: "Discover thousands of products with advanced search and filtering",
          icon: Search,
          details: ["Real-time search", "Category filters", "Price range filtering", "Condition filters"]
        },
        {
          title: "Product Listings",
          description: "Create stunning product listings with multiple images and rich descriptions",
          icon: Package,
          details: ["Multiple image upload", "Rich text descriptions", "Pricing suggestions", "Category management"]
        },
        {
          title: "Smart Search",
          description: "Advanced search with auto-suggestions and real-time results",
          icon: Zap,
          details: ["Auto-complete", "Smart suggestions", "Recent searches", "Trending products"]
        }
      ]
    },
    {
      category: "Shopping Experience",
      icon: ShoppingCart,
      color: "from-green-500 to-teal-600",
      items: [
        {
          title: "Shopping Cart",
          description: "Seamless cart experience with quantity management and checkout",
          icon: ShoppingCart,
          details: ["Quantity controls", "Price calculations", "Shipping estimates", "Promo codes"]
        },
        {
          title: "Favorites System",
          description: "Save and organize your favorite products for easy access",
          icon: Heart,
          details: ["One-click favorites", "Organize collections", "Quick access", "Share favorites"]
        },
        {
          title: "Buy/Sell Workflow",
          description: "Streamlined transaction process with seller approval system",
          icon: DollarSign,
          details: ["48-hour approval", "Instant notifications", "Secure transactions", "Order tracking"]
        }
      ]
    },
    {
      category: "Communication",
      icon: MessageCircle,
      color: "from-orange-500 to-red-600",
      items: [
        {
          title: "Real-time Messaging",
          description: "Chat with buyers and sellers instantly with full-page chat mode",
          icon: MessageCircle,
          details: ["Real-time chat", "Full-page mode", "Message highlighting", "Chat history"]
        },
        {
          title: "Smart Notifications",
          description: "Stay updated with intelligent notifications and quick actions",
          icon: Bell,
          details: ["Real-time alerts", "Quick actions", "Auto-delete options", "Sound notifications"]
        },
        {
          title: "User Profiles",
          description: "Comprehensive user profiles with activity tracking and privacy controls",
          icon: UserCheck,
          details: ["Public profiles", "Activity feeds", "Privacy settings", "Rating system"]
        }
      ]
    },
    {
      category: "Management Tools",
      icon: Settings,
      color: "from-purple-500 to-pink-600",
      items: [
        {
          title: "My Listings",
          description: "Manage your products with advanced controls and analytics",
          icon: Layout,
          details: ["Draft system", "Bulk operations", "Performance analytics", "Status management"]
        },
        {
          title: "My Deals",
          description: "Track all your transactions with detailed order management",
          icon: BarChart3,
          details: ["Order tracking", "Action buttons", "Deal analytics", "Status updates"]
        },
        {
          title: "Admin Panel",
          description: "Comprehensive admin tools for platform management",
          icon: Shield,
          details: ["User management", "Content moderation", "Site settings", "Analytics dashboard"]
        }
      ]
    }
  ];

  const stats = [
    { label: "Active Users", value: "10K+", icon: Users },
    { label: "Products Listed", value: "50K+", icon: Package },
    { label: "Successful Deals", value: "25K+", icon: TrendingUp },
    { label: "User Rating", value: "4.9★", icon: Star }
  ];

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Ultra-Modern Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-100 dark:from-gray-900 dark:via-blue-900 dark:to-purple-900">
        <div className="absolute inset-0 bg-gradient-to-tr from-blue-400/10 via-purple-400/10 to-pink-400/10"></div>
        <div className="absolute top-0 left-0 w-full h-full">
          <div className="absolute top-20 left-20 w-96 h-96 bg-blue-300/20 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
          <div className="absolute top-40 right-20 w-96 h-96 bg-purple-300/20 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-8 left-1/2 w-96 h-96 bg-pink-300/20 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
        </div>
      </div>

      {/* Floating Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-blue-400 rounded-full animate-ping"></div>
        <div className="absolute top-3/4 right-1/4 w-1 h-1 bg-purple-400 rounded-full animate-ping" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-3/4 w-1.5 h-1.5 bg-pink-400 rounded-full animate-ping" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-yellow-400 rounded-full animate-ping" style={{ animationDelay: '3s' }}></div>
      </div>

      <div className="relative z-10">
        {/* Hero Section */}
        <div className="container mx-auto px-4 pt-20 pb-16">
          <div className="text-center mb-16">
            {/* Premium Logo */}
            <div className="relative mb-8">
              <div className="w-24 h-24 mx-auto relative">
                <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 p-1">
                  <div className="w-full h-full rounded-3xl bg-white/20 backdrop-blur-xl flex items-center justify-center group">
                    <Store className="w-12 h-12 text-white drop-shadow-lg group-hover:scale-110 transition-transform duration-300" />
                  </div>
                </div>
                <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 blur-lg opacity-50 animate-pulse"></div>
                <Sparkles className="absolute -top-3 -right-3 w-8 h-8 text-yellow-400 animate-spin" style={{ animationDuration: '3s' }} />
              </div>
            </div>

            {/* Hero Title */}
            <h1 className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 dark:from-white dark:via-blue-100 dark:to-purple-100 mb-6">
              {UI_CONFIG.APP_NAME}
            </h1>
            <p className="text-2xl font-semibold text-gray-600 dark:text-gray-300 mb-4">
              Ultra-Modern Marketplace Platform
            </p>
            <p className="text-lg text-gray-500 dark:text-gray-400 max-w-3xl mx-auto leading-relaxed">
              Experience the future of online commerce with our cutting-edge marketplace featuring 
              real-time messaging, intelligent notifications, advanced search, and seamless transactions.
            </p>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
              <Link
                to="/login"
                className="px-8 py-4 rounded-2xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white font-bold text-lg hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 transition-all duration-300 transform hover:scale-[1.02] hover:shadow-2xl group overflow-hidden inline-flex items-center justify-center space-x-3"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/20 via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <span className="relative">Get Started</span>
                <ArrowRight className="w-5 h-5 relative group-hover:translate-x-1 transition-transform duration-300" />
              </Link>
              <Link
                to="/browse"
                className="px-8 py-4 rounded-2xl bg-white/20 dark:bg-white/10 backdrop-blur-sm border border-white/30 text-gray-700 dark:text-gray-200 font-semibold hover:bg-white/30 dark:hover:bg-white/20 transition-all duration-300 group inline-flex items-center justify-center space-x-3"
              >
                <Eye className="w-5 h-5 text-blue-500" />
                <span>Browse Marketplace</span>
              </Link>
            </div>
          </div>

          {/* Stats Section */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-20">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div key={index} className="cataloro-card-glass p-6 text-center backdrop-blur-2xl border-white/30 group hover:scale-105 transition-transform duration-300">
                  <div className="w-12 h-12 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow duration-300">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-2">
                    {stat.value}
                  </div>
                  <div className="text-sm font-semibold text-gray-600 dark:text-gray-300">
                    {stat.label}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Features Section */}
        <div className="container mx-auto px-4 pb-20">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 dark:from-white dark:via-blue-100 dark:to-purple-100 mb-4">
              Platform Features
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Discover all the powerful features that make our marketplace the most advanced platform for buying and selling.
            </p>
          </div>

          <div className="space-y-20">
            {features.map((category, categoryIndex) => {
              const CategoryIcon = category.icon;
              return (
                <div key={categoryIndex} className="relative">
                  {/* Category Header */}
                  <div className="text-center mb-12">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-xl">
                      <CategoryIcon className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                      {category.category}
                    </h3>
                  </div>

                  {/* Feature Cards */}
                  <div className="grid md:grid-cols-3 gap-8">
                    {category.items.map((feature, featureIndex) => {
                      const FeatureIcon = feature.icon;
                      return (
                        <div key={featureIndex} className="cataloro-card-glass p-8 backdrop-blur-2xl border-white/30 group hover:scale-105 transition-all duration-300">
                          {/* Feature Icon */}
                          <div className={`w-14 h-14 mb-6 rounded-2xl bg-gradient-to-br ${category.color} flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow duration-300`}>
                            <FeatureIcon className="w-7 h-7 text-white" />
                          </div>

                          {/* Feature Content */}
                          <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
                            {feature.title}
                          </h4>
                          <p className="text-gray-600 dark:text-gray-300 mb-6 leading-relaxed">
                            {feature.description}
                          </p>

                          {/* Feature Details */}
                          <div className="space-y-2">
                            {feature.details.map((detail, detailIndex) => (
                              <div key={detailIndex} className="flex items-center space-x-3">
                                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                                <span className="text-sm text-gray-600 dark:text-gray-300">{detail}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Call to Action Section */}
        <div className="container mx-auto px-4 pb-20">
          <div className="cataloro-card-glass p-12 text-center backdrop-blur-2xl border-white/30">
            <div className="max-w-3xl mx-auto">
              <h2 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 dark:from-white dark:via-blue-100 dark:to-purple-100 mb-6">
                Ready to Get Started?
              </h2>
              <p className="text-lg text-gray-600 dark:text-gray-300 mb-8 leading-relaxed">
                Join thousands of users who are already experiencing the future of online commerce. 
                Create your account today and start buying or selling with confidence.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/login"
                  className="px-8 py-4 rounded-2xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white font-bold text-lg hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 transition-all duration-300 transform hover:scale-[1.02] hover:shadow-2xl group overflow-hidden inline-flex items-center justify-center space-x-3"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-white/20 via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <span className="relative">Start Your Journey</span>
                  <ArrowRight className="w-5 h-5 relative group-hover:translate-x-1 transition-transform duration-300" />
                </Link>
                <Link
                  to="/browse"
                  className="px-8 py-4 rounded-2xl bg-white/20 dark:bg-white/10 backdrop-blur-sm border border-white/30 text-gray-700 dark:text-gray-200 font-semibold hover:bg-white/30 dark:hover:bg-white/20 transition-all duration-300 group inline-flex items-center justify-center space-x-3"
                >
                  <Globe className="w-5 h-5 text-purple-500" />
                  <span>Explore Platform</span>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default InfoPage;