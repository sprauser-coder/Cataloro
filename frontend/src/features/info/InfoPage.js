/**
 * CATALORO - Dynamic Info/Functionality Page
 * Powered by Advanced CMS - All content managed through admin panel
 */

import React, { useState, useEffect } from 'react';
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
  UserCheck,
  Target,
  Loader
} from 'lucide-react';
import { UI_CONFIG } from '../../config/directions';

// Icon mapping for dynamic icon rendering
const iconMap = {
  'users': Users,
  'package': Package,
  'trending': TrendingUp,
  'star': Star,
  'zap': Zap,
  'target': Target,
  'store': Store,
  'shopping-cart': ShoppingCart,
  'message-circle': MessageCircle,
  'settings': Settings,
  'shield': Shield,
  'search': Search,
  'heart': Heart,
  'bell': Bell,
  'bar-chart': BarChart3
};

// Color scheme mapping
const colorSchemes = {
  'blue': 'from-blue-500 to-blue-600',
  'green': 'from-green-500 to-green-600',
  'purple': 'from-purple-500 to-purple-600',
  'yellow': 'from-yellow-500 to-yellow-600',
  'red': 'from-red-500 to-red-600',
  'pink': 'from-pink-500 to-pink-600',
  'blue-purple': 'from-blue-500 to-purple-600',
  'green-teal': 'from-green-500 to-teal-600',
  'orange-red': 'from-orange-500 to-red-600',
  'purple-pink': 'from-purple-500 to-pink-600'
};

function InfoPage() {
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load CMS content from backend
  useEffect(() => {
    const loadContent = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/content`);
        
        if (response.ok) {
          const data = await response.json();
          setContent(data);
          
          // Update SEO meta tags dynamically
          if (data.seo) {
            document.title = data.seo.title || 'Cataloro - Ultra-Modern Marketplace Platform';
            
            // Update meta description
            let metaDescription = document.querySelector('meta[name="description"]');
            if (!metaDescription) {
              metaDescription = document.createElement('meta');
              metaDescription.name = 'description';
              document.head.appendChild(metaDescription);
            }
            metaDescription.content = data.seo.description || 'Experience the future of online commerce';
            
            // Update meta keywords
            let metaKeywords = document.querySelector('meta[name="keywords"]');
            if (!metaKeywords) {
              metaKeywords = document.createElement('meta');
              metaKeywords.name = 'keywords';
              document.head.appendChild(metaKeywords);
            }
            metaKeywords.content = Array.isArray(data.seo.keywords) ? data.seo.keywords.join(', ') : data.seo.keywords || '';
            
            // Update Open Graph tags
            if (data.seo.ogImage) {
              let ogImage = document.querySelector('meta[property="og:image"]');
              if (!ogImage) {
                ogImage = document.createElement('meta');
                ogImage.setAttribute('property', 'og:image');
                document.head.appendChild(ogImage);
              }
              ogImage.content = data.seo.ogImage;
            }
            
            // Update canonical URL
            if (data.seo.canonicalUrl) {
              let canonical = document.querySelector('link[rel="canonical"]');
              if (!canonical) {
                canonical = document.createElement('link');
                canonical.rel = 'canonical';
                document.head.appendChild(canonical);
              }
              canonical.href = window.location.origin + data.seo.canonicalUrl;
            }
          }
        } else {
          throw new Error('Failed to load content');
        }
      } catch (error) {
        console.error('Error loading CMS content:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    loadContent();
  }, []);

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-100">
        <div className="text-center">
          <Loader className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-lg text-gray-600">Loading content...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-100">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Shield className="w-8 h-8 text-red-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Content Loading Error</h2>
          <p className="text-gray-600 mb-4">Unable to load page content from CMS</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Fallback content if CMS data is incomplete
  const safeContent = {
    hero: content?.hero || {
      title: UI_CONFIG.APP_NAME,
      subtitle: 'Ultra-Modern Marketplace Platform',
      description: 'Experience the future of online commerce with our cutting-edge marketplace.',
      primaryButtonText: 'Get Started',
      primaryButtonLink: '/login',
      secondaryButtonText: 'Browse Marketplace',
      secondaryButtonLink: '/browse',
      showLogo: true,
      logoAnimation: true
    },
    stats: content?.stats || [
      { label: 'Active Users', value: '10K+', icon: 'users', color: 'blue' },
      { label: 'Products Listed', value: '50K+', icon: 'package', color: 'green' },
      { label: 'Successful Deals', value: '25K+', icon: 'trending', color: 'purple' },
      { label: 'User Rating', value: '4.9★', icon: 'star', color: 'yellow' }
    ],
    features: content?.features || {
      title: 'Platform Features',
      description: 'Discover all the powerful features that make our marketplace advanced.',
      categories: []
    },
    testimonials: content?.testimonials || { enabled: false, items: [] },
    cta: content?.cta || {
      title: 'Ready to Get Started?',
      description: 'Join thousands of users experiencing the future of online commerce.',
      primaryButtonText: 'Start Your Journey',
      primaryButtonLink: '/login',
      secondaryButtonText: 'Explore Platform',
      secondaryButtonLink: '/browse'
    },
    footer: content?.footer || {
      companyDescription: 'Cataloro is the future of online commerce.',
      socialLinks: {},
      footerLinks: []
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Dynamic Animated Background */}
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
        {/* Dynamic Hero Section */}
        <div className="container mx-auto px-4 pt-20 pb-16">
          <div className="text-center mb-16">
            {/* Dynamic Logo */}
            {safeContent.hero.showLogo && (
              <div className="relative mb-8">
                <div className="w-24 h-24 mx-auto relative">
                  <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 p-1">
                    <div className="w-full h-full rounded-3xl bg-white/20 backdrop-blur-xl flex items-center justify-center group">
                      <Store className={`w-12 h-12 text-white drop-shadow-lg ${safeContent.hero.logoAnimation ? 'group-hover:scale-110 transition-transform duration-300' : ''}`} />
                    </div>
                  </div>
                  <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 blur-lg opacity-50 animate-pulse"></div>
                  {safeContent.hero.logoAnimation && (
                    <Sparkles className="absolute -top-3 -right-3 w-8 h-8 text-yellow-400 animate-spin" style={{ animationDuration: '3s' }} />
                  )}
                </div>
              </div>
            )}

            {/* Dynamic Hero Title */}
            <h1 className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 dark:from-white dark:via-blue-100 dark:to-purple-100 mb-6">
              {safeContent.hero.title}
            </h1>
            <p className="text-2xl font-semibold text-gray-600 dark:text-gray-300 mb-4">
              {safeContent.hero.subtitle}
            </p>
            <div 
              className="text-lg text-gray-500 dark:text-gray-400 max-w-3xl mx-auto leading-relaxed"
              dangerouslySetInnerHTML={{ __html: safeContent.hero.description }}
            />

            {/* Dynamic Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
              <Link
                to={safeContent.hero.primaryButtonLink || '/login'}
                className="px-8 py-4 rounded-2xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white font-bold text-lg hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 transition-all duration-300 transform hover:scale-[1.02] hover:shadow-2xl group overflow-hidden inline-flex items-center justify-center space-x-3"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/20 via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <span className="relative">{safeContent.hero.primaryButtonText}</span>
                <ArrowRight className="w-5 h-5 relative group-hover:translate-x-1 transition-transform duration-300" />
              </Link>
              <Link
                to={safeContent.hero.secondaryButtonLink || '/browse'}
                className="px-8 py-4 rounded-2xl bg-white/20 dark:bg-white/10 backdrop-blur-sm border border-white/30 text-gray-700 dark:text-gray-200 font-semibold hover:bg-white/30 dark:hover:bg-white/20 transition-all duration-300 group inline-flex items-center justify-center space-x-3"
              >
                <Eye className="w-5 h-5 text-blue-500" />
                <span>{safeContent.hero.secondaryButtonText}</span>
              </Link>
            </div>
          </div>

          {/* Dynamic Stats Section */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-20">
            {safeContent.stats.map((stat, index) => {
              const IconComponent = iconMap[stat.icon] || Star;
              const colorClass = colorSchemes[stat.color] || 'from-blue-500 to-purple-600';
              
              return (
                <div key={index} className="cataloro-card-glass p-6 text-center backdrop-blur-2xl border-white/30 group hover:scale-105 transition-transform duration-300">
                  <div className={`w-12 h-12 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${colorClass} flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow duration-300`}>
                    <IconComponent className="w-6 h-6 text-white" />
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

        {/* Dynamic Features Section */}
        {safeContent.features.categories && safeContent.features.categories.length > 0 && (
          <div className="container mx-auto px-4 pb-20">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 dark:from-white dark:via-blue-100 dark:to-purple-100 mb-4">
                {safeContent.features.title}
              </h2>
              <div 
                className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto"
                dangerouslySetInnerHTML={{ __html: safeContent.features.description }}
              />
            </div>

            <div className="space-y-20">
              {safeContent.features.categories.map((category, categoryIndex) => {
                const CategoryIcon = iconMap[category.icon] || Settings;
                const colorClass = colorSchemes[category.color] || 'from-blue-500 to-purple-600';
                
                return (
                  <div key={categoryIndex} className="relative">
                    {/* Category Header */}
                    <div className="text-center mb-12">
                      <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${colorClass} flex items-center justify-center shadow-xl`}>
                        <CategoryIcon className="w-8 h-8 text-white" />
                      </div>
                      <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                        {category.name}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-300">
                        {category.description}
                      </p>
                    </div>

                    {/* Feature Items */}
                    {category.features && category.features.length > 0 && (
                      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {category.features.map((feature, featureIndex) => (
                          <div key={featureIndex} className="cataloro-card-glass p-6 backdrop-blur-2xl border-white/30 group hover:scale-105 transition-all duration-300">
                            <div className="flex items-center space-x-3">
                              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                              <span className="text-gray-700 dark:text-gray-300">{feature}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Dynamic Testimonials Section */}
        {safeContent.testimonials.enabled && safeContent.testimonials.items && safeContent.testimonials.items.length > 0 && (
          <div className="container mx-auto px-4 pb-20">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 dark:from-white dark:via-blue-100 dark:to-purple-100 mb-4">
                {safeContent.testimonials.title}
              </h2>
              <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                {safeContent.testimonials.description}
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {safeContent.testimonials.items.map((testimonial, index) => (
                <div key={index} className="cataloro-card-glass p-8 backdrop-blur-2xl border-white/30 group hover:scale-105 transition-all duration-300">
                  <div className="text-center mb-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
                      <span className="text-white font-bold text-xl">
                        {testimonial.name.charAt(0)}
                      </span>
                    </div>
                    <h4 className="text-lg font-bold text-gray-900 dark:text-white">{testimonial.name}</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-300">{testimonial.role}</p>
                    <div className="flex items-center justify-center mt-2">
                      {[...Array(5)].map((_, i) => (
                        <Star key={i} className={`w-4 h-4 ${i < testimonial.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} />
                      ))}
                    </div>
                  </div>
                  <p className="text-gray-700 dark:text-gray-300 italic text-center">
                    "{testimonial.content}"
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Dynamic Call to Action Section */}
        <div className="container mx-auto px-4 pb-20">
          <div className="cataloro-card-glass p-12 text-center backdrop-blur-2xl border-white/30">
            <div className="max-w-3xl mx-auto">
              <h2 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 dark:from-white dark:via-blue-100 dark:to-purple-100 mb-6">
                {safeContent.cta.title}
              </h2>
              <div 
                className="text-lg text-gray-600 dark:text-gray-300 mb-8 leading-relaxed"
                dangerouslySetInnerHTML={{ __html: safeContent.cta.description }}
              />

              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to={safeContent.cta.primaryButtonLink || '/login'}
                  className="px-8 py-4 rounded-2xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white font-bold text-lg hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 transition-all duration-300 transform hover:scale-[1.02] hover:shadow-2xl group overflow-hidden inline-flex items-center justify-center space-x-3"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-white/20 via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  <span className="relative">{safeContent.cta.primaryButtonText}</span>
                  <ArrowRight className="w-5 h-5 relative group-hover:translate-x-1 transition-transform duration-300" />
                </Link>
                <Link
                  to={safeContent.cta.secondaryButtonLink || '/browse'}
                  className="px-8 py-4 rounded-2xl bg-white/20 dark:bg-white/10 backdrop-blur-sm border border-white/30 text-gray-700 dark:text-gray-200 font-semibold hover:bg-white/30 dark:hover:bg-white/20 transition-all duration-300 group inline-flex items-center justify-center space-x-3"
                >
                  <Globe className="w-5 h-5 text-purple-500" />
                  <span>{safeContent.cta.secondaryButtonText}</span>
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