/**
 * CATALORO - Ultra-Modern Stylish Info Page
 * Powered by Advanced CMS with Image Management
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
  Loader,
  Play,
  Award,
  Lightbulb,
  Rocket,
  Clock,
  Mail,
  Phone,
  MapPin,
  Quote
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
  'bar-chart': BarChart3,
  'award': Award,
  'lightbulb': Lightbulb,
  'rocket': Rocket,
  'clock': Clock
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
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="text-center">
          <Loader className="w-12 h-12 text-purple-400 animate-spin mx-auto mb-4" />
          <p className="text-lg text-white">Loading content...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Shield className="w-8 h-8 text-red-400" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Content Loading Error</h2>
          <p className="text-gray-300 mb-4">Unable to load page content from CMS</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Fallback content with stock images
  const safeContent = {
    hero: content?.hero || {
      title: 'Cataloro',
      subtitle: 'The Future of Online Marketplace',
      description: 'Experience next-generation commerce with our ultra-modern platform featuring intelligent matching, real-time communication, and seamless transactions.',
      primaryButtonText: 'Start Trading Now',
      primaryButtonLink: '/login',
      secondaryButtonText: 'Explore Features',
      secondaryButtonLink: '/browse',
      backgroundImage: 'https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=1920&h=1080&fit=crop&crop=center',
      showVideo: false,
      videoUrl: 'https://player.vimeo.com/video/123456789'
    },
    stats: content?.stats || [
      { label: 'Active Users', value: '25K+', icon: 'users', color: 'blue' },
      { label: 'Products Listed', value: '150K+', icon: 'package', color: 'green' },
      { label: 'Successful Deals', value: '75K+', icon: 'trending', color: 'purple' },
      { label: 'User Satisfaction', value: '4.9★', icon: 'star', color: 'yellow' }
    ],
    features: content?.features || {
      title: 'Advanced Platform Features',
      description: 'Discover the comprehensive suite of tools that make Cataloro the most advanced marketplace platform.',
      backgroundImage: 'https://images.unsplash.com/photo-1551434678-e076c223a692?w=1920&h=1080&fit=crop&crop=center',
      categories: []
    },
    testimonials: content?.testimonials || { 
      enabled: true, 
      title: 'What Our Users Say',
      description: 'Join thousands of satisfied users who trust Cataloro for their marketplace needs.',
      backgroundImage: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1920&h=1080&fit=crop&crop=center',
      items: [] 
    },
    about: content?.about || {
      enabled: true,
      title: 'About Cataloro',
      subtitle: 'Revolutionizing Digital Commerce',
      description: 'Founded with the vision to transform online trading, we combine cutting-edge technology with user-centric design to create the ultimate marketplace experience.',
      image: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&h=600&fit=crop&crop=center',
      features: [
        'AI-Powered Matching',
        'Real-time Communication',
        'Advanced Security',
        'Global Reach'
      ]
    },
    team: content?.team || {
      enabled: true,
      title: 'Meet Our Team',
      description: 'Passionate experts dedicated to revolutionizing digital commerce.',
      backgroundImage: 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1920&h=1080&fit=crop&crop=center',
      members: []
    },
    cta: content?.cta || {
      title: 'Ready to Transform Your Trading?',
      description: 'Join thousands of users experiencing the future of online commerce.',
      primaryButtonText: 'Start Your Journey',
      primaryButtonLink: '/login',
      secondaryButtonText: 'Explore Platform',
      secondaryButtonLink: '/browse',
      backgroundImage: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1920&h=1080&fit=crop&crop=center'
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section with Parallax Background */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Dynamic Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-fixed"
          style={{ 
            backgroundImage: `url(${safeContent.hero.backgroundImage})`,
            filter: 'brightness(0.4)'
          }}
        />
        
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-black/70 via-purple-900/50 to-black/70" />
        
        {/* Floating Particles */}
        <div className="absolute inset-0">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute w-2 h-2 bg-white/20 rounded-full animate-pulse"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${3 + Math.random() * 4}s`
              }}
            />
          ))}
        </div>

        {/* Hero Content */}
        <div className="relative z-10 max-w-6xl mx-auto px-4 text-center">
          <div className="mb-8">
            <div className="inline-flex items-center space-x-2 bg-white/10 backdrop-blur-md rounded-full px-6 py-3 mb-6">
              <Sparkles className="w-5 h-5 text-yellow-400" />
              <span className="text-white font-medium">The Future is Here</span>
            </div>
            
            <h1 className="text-7xl md:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-purple-200 to-pink-200 mb-6 leading-tight">
              {safeContent.hero.title}
            </h1>
            
            <h2 className="text-3xl md:text-4xl font-bold text-purple-200 mb-8">
              {safeContent.hero.subtitle}
            </h2>
            
            <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-12 leading-relaxed">
              {safeContent.hero.description}
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-16">
            <Link
              to={safeContent.hero.primaryButtonLink}
              className="group relative px-10 py-5 rounded-2xl bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold text-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-300 transform hover:scale-105 shadow-2xl hover:shadow-purple-500/25"
            >
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative flex items-center justify-center space-x-3">
                <span>{safeContent.hero.primaryButtonText}</span>
                <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform duration-300" />
              </div>
            </Link>
            
            <Link
              to={safeContent.hero.secondaryButtonLink}
              className="group px-10 py-5 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 text-white font-bold text-lg hover:bg-white/20 transition-all duration-300 transform hover:scale-105"
            >
              <div className="flex items-center justify-center space-x-3">
                <Play className="w-6 h-6" />
                <span>{safeContent.hero.secondaryButtonText}</span>
              </div>
            </Link>
          </div>

          {/* Scroll Indicator */}
          <div className="animate-bounce">
            <div className="w-6 h-10 border-2 border-white/30 rounded-full flex justify-center">
              <div className="w-1 h-3 bg-white rounded-full mt-2 animate-pulse" />
            </div>
          </div>
        </div>
      </section>

      {/* Modern Stats Section */}
      <section className="relative py-20 bg-white overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-gray-50 to-white" />
        
        <div className="relative z-10 max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {safeContent.stats.map((stat, index) => {
              const IconComponent = iconMap[stat.icon] || Star;
              const colorClass = colorSchemes[stat.color] || 'from-purple-500 to-pink-600';
              
              return (
                <div key={index} className="group text-center">
                  <div className="relative mb-6">
                    <div className={`w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br ${colorClass} flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-500 transform group-hover:scale-110 group-hover:-rotate-6`}>
                      <IconComponent className="w-10 h-10 text-white" />
                    </div>
                  </div>
                  
                  <div className="text-4xl font-black text-gray-900 mb-2 group-hover:text-purple-600 transition-colors duration-300">
                    {stat.value}
                  </div>
                  
                  <div className="text-lg font-semibold text-gray-600 group-hover:text-gray-900 transition-colors duration-300">
                    {stat.label}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* About Section with Side Image */}
      {safeContent.about.enabled && (
        <section className="py-20 bg-gradient-to-br from-slate-900 to-purple-900">
          <div className="max-w-7xl mx-auto px-4">
            <div className="grid lg:grid-cols-2 gap-16 items-center">
              {/* Text Content */}
              <div className="space-y-8">
                <div>
                  <div className="inline-flex items-center space-x-2 bg-purple-500/20 rounded-full px-4 py-2 mb-6">
                    <Award className="w-5 h-5 text-purple-400" />
                    <span className="text-purple-300 font-medium">About Us</span>
                  </div>
                  
                  <h2 className="text-5xl font-black text-white mb-6">
                    {safeContent.about.title}
                  </h2>
                  
                  <h3 className="text-2xl font-bold text-purple-300 mb-8">
                    {safeContent.about.subtitle}
                  </h3>
                  
                  <p className="text-xl text-gray-300 leading-relaxed mb-8">
                    {safeContent.about.description}
                  </p>
                </div>

                {/* Feature Grid */}
                <div className="grid grid-cols-2 gap-6">
                  {safeContent.about.features.map((feature, index) => (
                    <div key={index} className="flex items-center space-x-3 p-4 rounded-xl bg-white/5 backdrop-blur-sm">
                      <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0" />
                      <span className="text-white font-medium">{feature}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Image */}
              <div className="relative">
                <div className="relative overflow-hidden rounded-3xl shadow-2xl transform rotate-3 hover:rotate-0 transition-transform duration-500">
                  <img
                    src={safeContent.about.image}
                    alt="About Cataloro"
                    className="w-full h-96 object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-purple-900/50 to-transparent" />
                </div>
                
                {/* Floating Badge */}
                <div className="absolute -top-6 -right-6 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-2xl p-4 shadow-xl">
                  <div className="text-center">
                    <div className="text-2xl font-black text-white">4.9★</div>
                    <div className="text-sm text-white font-medium">Rating</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Features Section with Background Image */}
      <section className="relative py-24 overflow-hidden">
        {/* Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-fixed"
          style={{ 
            backgroundImage: `url(${safeContent.features.backgroundImage})`,
            filter: 'brightness(0.1)'
          }}
        />
        
        {/* Overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-black/80 via-purple-900/70 to-black/80" />

        <div className="relative z-10 max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-black text-white mb-8">
              {safeContent.features.title}
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              {safeContent.features.description}
            </p>
          </div>

          {/* Features Grid */}
          {safeContent.features.categories && safeContent.features.categories.length > 0 && (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {safeContent.features.categories.slice(0, 6).map((category, index) => {
                const CategoryIcon = iconMap[category.icon] || Settings;
                const colorClass = colorSchemes[category.color] || 'from-purple-500 to-pink-600';
                
                return (
                  <div key={index} className="group">
                    <div className="bg-white/10 backdrop-blur-md rounded-3xl p-8 border border-white/20 hover:bg-white/20 transition-all duration-500 transform hover:scale-105 hover:-translate-y-2">
                      <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${colorClass} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                        <CategoryIcon className="w-8 h-8 text-white" />
                      </div>
                      
                      <h3 className="text-2xl font-bold text-white mb-4">
                        {category.name}
                      </h3>
                      
                      <p className="text-gray-300 mb-6">
                        {category.description}
                      </p>

                      {/* Feature List */}
                      {category.features && category.features.slice(0, 3).map((feature, featureIndex) => (
                        <div key={featureIndex} className="flex items-center space-x-3 mb-3">
                          <div className="w-2 h-2 bg-purple-400 rounded-full" />
                          <span className="text-gray-300 text-sm">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </section>

      {/* Testimonials Section */}
      {safeContent.testimonials.enabled && safeContent.testimonials.items && safeContent.testimonials.items.length > 0 && (
        <section className="relative py-24 bg-gradient-to-br from-white to-gray-100">
          <div className="max-w-7xl mx-auto px-4">
            <div className="text-center mb-16">
              <h2 className="text-5xl font-black text-gray-900 mb-8">
                {safeContent.testimonials.title}
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                {safeContent.testimonials.description}
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {safeContent.testimonials.items.slice(0, 3).map((testimonial, index) => (
                <div key={index} className="group">
                  <div className="bg-white rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:scale-105 border-l-4 border-purple-500">
                    <div className="mb-6">
                      <Quote className="w-12 h-12 text-purple-500 opacity-50" />
                    </div>
                    
                    <p className="text-gray-700 text-lg mb-8 italic">
                      "{testimonial.content}"
                    </p>
                    
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold text-lg">
                          {testimonial.name.charAt(0)}
                        </span>
                      </div>
                      
                      <div>
                        <div className="font-bold text-gray-900">{testimonial.name}</div>
                        <div className="text-gray-600">{testimonial.role}</div>
                        <div className="flex items-center mt-1">
                          {[...Array(5)].map((_, i) => (
                            <Star key={i} className={`w-4 h-4 ${i < testimonial.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} />
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Final CTA Section */}
      <section className="relative py-24 overflow-hidden">
        {/* Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-fixed"
          style={{ 
            backgroundImage: `url(${safeContent.cta.backgroundImage})`,
            filter: 'brightness(0.3)'
          }}
        />
        
        {/* Animated Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-purple-900/90 via-pink-900/70 to-purple-900/90" />

        <div className="relative z-10 max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-6xl font-black text-white mb-8">
            {safeContent.cta.title}
          </h2>
          
          <p className="text-2xl text-gray-300 mb-12 leading-relaxed">
            {safeContent.cta.description}
          </p>

          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <Link
              to={safeContent.cta.primaryButtonLink}
              className="group relative px-12 py-6 rounded-2xl bg-gradient-to-r from-white to-gray-100 text-gray-900 font-bold text-xl hover:from-gray-100 hover:to-white transition-all duration-300 transform hover:scale-105 shadow-2xl"
            >
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-purple-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="relative flex items-center justify-center space-x-3">
                <span>{safeContent.cta.primaryButtonText}</span>
                <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform duration-300" />
              </div>
            </Link>
            
            <Link
              to={safeContent.cta.secondaryButtonLink}
              className="group px-12 py-6 rounded-2xl bg-white/10 backdrop-blur-md border-2 border-white/30 text-white font-bold text-xl hover:bg-white/20 transition-all duration-300 transform hover:scale-105"
            >
              <div className="flex items-center justify-center space-x-3">
                <Globe className="w-6 h-6" />
                <span>{safeContent.cta.secondaryButtonText}</span>
              </div>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

export default InfoPage;