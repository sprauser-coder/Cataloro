/**
 * CATALORO - Advanced Content Management System
 * Enhanced CMS with comprehensive content editing, SEO, and media management
 */

import React, { useState, useEffect } from 'react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import { 
  Save, 
  Eye, 
  RefreshCw, 
  Edit3, 
  FileText, 
  Settings, 
  Sparkles,
  AlertCircle,
  CheckCircle,
  Layout,
  Type,
  Image,
  Link,
  BarChart3,
  Plus,
  Minus,
  ArrowUp,
  ArrowDown,
  Globe,
  Search,
  Tag,
  Palette,
  Monitor,
  Smartphone,
  Upload,
  X,
  Copy,
  ExternalLink,
  Zap,
  Target,
  Users,
  TrendingUp
} from 'lucide-react';

function ContentManagementSystem() {
  const [contentSections, setContentSections] = useState({
    seo: {
      title: 'Cataloro - Ultra-Modern Marketplace Platform',
      description: 'Experience the future of online commerce with cutting-edge marketplace featuring real-time messaging, intelligent notifications, and seamless transactions.',
      keywords: 'marketplace, ecommerce, online shopping, buy sell, real-time messaging',
      ogImage: '',
      canonicalUrl: '/info'
    },
    hero: {
      title: 'Cataloro',
      subtitle: 'Ultra-Modern Marketplace Platform',
      description: 'Experience the future of online commerce with our cutting-edge marketplace featuring real-time messaging, intelligent notifications, advanced search, and seamless transactions.',
      primaryButtonText: 'Get Started',
      primaryButtonLink: '/login',
      secondaryButtonText: 'Browse Marketplace',
      secondaryButtonLink: '/browse',
      backgroundStyle: 'gradient',
      showLogo: true,
      logoAnimation: true
    },
    stats: [
      { label: 'Active Users', value: '10K+', icon: 'users', color: 'blue' },
      { label: 'Products Listed', value: '50K+', icon: 'package', color: 'green' },
      { label: 'Successful Deals', value: '25K+', icon: 'trending', color: 'purple' },
      { label: 'User Rating', value: '4.9★', icon: 'star', color: 'yellow' }
    ],
    features: {
      title: 'Platform Features',
      description: 'Discover all the powerful features that make our marketplace the most advanced platform for buying and selling.',
      showIcons: true,
      categories: [
        {
          id: 'marketplace-core',
          name: 'Marketplace Core',
          description: 'Essential marketplace functionality with advanced search and product management.',
          icon: 'store',
          color: 'blue-purple',
          features: [
            'Real-time search with auto-suggestions',
            'Advanced filtering and categorization',
            'Smart product recommendations',
            'Price comparison tools'
          ]
        },
        {
          id: 'shopping-experience',
          name: 'Shopping Experience', 
          description: 'Seamless shopping with cart management, favorites, and secure transactions.',
          icon: 'shopping-cart',
          color: 'green-teal',
          features: [
            'One-click shopping cart',
            'Wishlist and favorites system',
            'Secure payment processing',
            '48-hour approval system'
          ]
        },
        {
          id: 'communication',
          name: 'Communication',
          description: 'Real-time messaging, notifications, and user profile management.',
          icon: 'message-circle',
          color: 'orange-red',
          features: [
            'Real-time chat system',
            'Smart notifications',
            'User verification system',
            'Review and rating system'
          ]
        },
        {
          id: 'management-tools',
          name: 'Management Tools',
          description: 'Comprehensive admin and user management tools with analytics.',
          icon: 'settings',
          color: 'purple-pink',
          features: [
            'Advanced analytics dashboard',
            'Inventory management',
            'Bulk operations',
            'Performance insights'
          ]
        }
      ]
    },
    testimonials: {
      enabled: true,
      title: 'What Our Users Say',
      description: 'Join thousands of satisfied users who trust Cataloro for their marketplace needs.',
      items: [
        {
          id: '1',
          name: 'Sarah Johnson',
          role: 'Power Seller',
          avatar: '',
          content: 'Cataloro has transformed how I sell online. The real-time messaging and advanced analytics have boosted my sales by 300%!',
          rating: 5
        },
        {
          id: '2', 
          name: 'Mike Chen',
          role: 'Regular Buyer',
          avatar: '',
          content: 'The search functionality is incredible. I can find exactly what Im looking for in seconds. Best marketplace experience ever!',
          rating: 5
        },
        {
          id: '3',
          name: 'Emily Rodriguez',
          role: 'Business Owner',
          avatar: '',
          content: 'The admin tools and inventory management features have streamlined our entire operation. Highly recommended!',
          rating: 5
        }
      ]
    },
    cta: {
      title: 'Ready to Get Started?',
      description: 'Join thousands of users who are already experiencing the future of online commerce. Create your account today and start buying or selling with confidence.',
      primaryButtonText: 'Start Your Journey',
      primaryButtonLink: '/login',
      secondaryButtonText: 'Explore Platform',
      secondaryButtonLink: '/browse',
      backgroundStyle: 'gradient',
      showStats: true
    },
    footer: {
      companyDescription: 'Cataloro is the future of online commerce, providing cutting-edge marketplace solutions for modern buyers and sellers.',
      socialLinks: {
        twitter: '',
        facebook: '',
        instagram: '',
        linkedin: ''
      },
      footerLinks: [
        { title: 'About', url: '/info' },
        { title: 'Contact', url: '/contact' },
        { title: 'Privacy', url: '/privacy' },
        { title: 'Terms', url: '/terms' }
      ]
    }
  });

  const [activeSection, setActiveSection] = useState('seo');
  const [isLoading, setSaveLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);
  const [previewMode, setPreviewMode] = useState(false);
  const [previewDevice, setPreviewDevice] = useState('desktop');
  const [uploadingImage, setUploadingImage] = useState(false);

  // Enhanced Quill editor configuration
  const quillModules = {
    toolbar: [
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      ['bold', 'italic', 'underline', 'strike', 'blockquote'],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }, { 'indent': '-1'}, { 'indent': '+1' }],
      [{ 'align': [] }],
      ['link', 'image', 'video'],
      ['code-block'],
      ['clean']
    ],
  };

  const quillFormats = [
    'header', 'bold', 'italic', 'underline', 'strike', 'blockquote',
    'color', 'background', 'list', 'bullet', 'indent', 'align',
    'link', 'image', 'video', 'code-block'
  ];

  // Save content to backend
  const saveContent = async () => {
    setSaveLoading(true);
    setSaveStatus(null);
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/content`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('cataloro_token')}`
        },
        body: JSON.stringify({
          ...contentSections,
          lastUpdated: new Date().toISOString(),
          version: Date.now()
        })
      });

      if (response.ok) {
        setSaveStatus('success');
        setTimeout(() => setSaveStatus(null), 3000);
      } else {
        throw new Error('Failed to save content');
      }
    } catch (error) {
      console.error('Save error:', error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(null), 3000);
    } finally {
      setSaveLoading(false);
    }
  };

  // Load content from backend
  const loadContent = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/content`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('cataloro_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setContentSections(prev => ({ ...prev, ...data }));
      }
    } catch (error) {
      console.error('Load error:', error);
    }
  };

  // Auto-save functionality
  useEffect(() => {
    const autoSaveInterval = setInterval(() => {
      if (contentSections) {
        localStorage.setItem('cataloro_cms_draft', JSON.stringify(contentSections));
      }
    }, 30000); // Auto-save every 30 seconds

    return () => clearInterval(autoSaveInterval);
  }, [contentSections]);

  useEffect(() => {
    loadContent();
    
    // Load draft from localStorage if available
    const draft = localStorage.getItem('cataloro_cms_draft');
    if (draft) {
      try {
        const draftData = JSON.parse(draft);
        setContentSections(prev => ({ ...prev, ...draftData }));
      } catch (error) {
        console.error('Error loading draft:', error);
      }
    }
  }, []);

  // Update functions for different sections
  const updateSEOContent = (field, value) => {
    setContentSections(prev => ({
      ...prev,
      seo: { ...prev.seo, [field]: value }
    }));
  };

  const updateHeroContent = (field, value) => {
    setContentSections(prev => ({
      ...prev,
      hero: { ...prev.hero, [field]: value }
    }));
  };

  const updateStatContent = (index, field, value) => {
    setContentSections(prev => ({
      ...prev,
      stats: prev.stats.map((stat, i) => 
        i === index ? { ...stat, [field]: value } : stat
      )
    }));
  };

  const addStat = () => {
    setContentSections(prev => ({
      ...prev,
      stats: [...prev.stats, { label: 'New Stat', value: '0', icon: 'zap', color: 'blue' }]
    }));
  };

  const removeStat = (index) => {
    setContentSections(prev => ({
      ...prev,
      stats: prev.stats.filter((_, i) => i !== index)
    }));
  };

  const updateFeaturesContent = (field, value) => {
    setContentSections(prev => ({
      ...prev,
      features: { ...prev.features, [field]: value }
    }));
  };

  const updateFeatureCategory = (categoryId, field, value) => {
    setContentSections(prev => ({
      ...prev,
      features: {
        ...prev.features,
        categories: prev.features.categories.map(cat =>
          cat.id === categoryId ? { ...cat, [field]: value } : cat
        )
      }
    }));
  };

  const addFeatureCategory = () => {
    const newId = `category-${Date.now()}`;
    setContentSections(prev => ({
      ...prev,
      features: {
        ...prev.features,
        categories: [...prev.features.categories, {
          id: newId,
          name: 'New Category',
          description: 'Category description',
          icon: 'zap',
          color: 'blue-purple',
          features: ['Feature 1', 'Feature 2']
        }]
      }
    }));
  };

  const removeFeatureCategory = (categoryId) => {
    setContentSections(prev => ({
      ...prev,
      features: {
        ...prev.features,
        categories: prev.features.categories.filter(cat => cat.id !== categoryId)
      }
    }));
  };

  const updateTestimonials = (field, value) => {
    setContentSections(prev => ({
      ...prev,
      testimonials: { ...prev.testimonials, [field]: value }
    }));
  };

  const updateTestimonialItem = (id, field, value) => {
    setContentSections(prev => ({
      ...prev,
      testimonials: {
        ...prev.testimonials,
        items: prev.testimonials.items.map(item =>
          item.id === id ? { ...item, [field]: value } : item
        )
      }
    }));
  };

  const addTestimonial = () => {
    const newId = `testimonial-${Date.now()}`;
    setContentSections(prev => ({
      ...prev,
      testimonials: {
        ...prev.testimonials,
        items: [...prev.testimonials.items, {
          id: newId,
          name: 'New User',
          role: 'Customer',
          avatar: '',
          content: 'Great experience with Cataloro!',
          rating: 5
        }]
      }
    }));
  };

  const removeTestimonial = (id) => {
    setContentSections(prev => ({
      ...prev,
      testimonials: {
        ...prev.testimonials,
        items: prev.testimonials.items.filter(item => item.id !== id)
      }
    }));
  };

  const updateCTAContent = (field, value) => {
    setContentSections(prev => ({
      ...prev,
      cta: { ...prev.cta, [field]: value }
    }));
  };

  const updateFooterContent = (field, value) => {
    setContentSections(prev => ({
      ...prev,
      footer: { ...prev.footer, [field]: value }
    }));
  };

  // Image upload handler
  const handleImageUpload = async (file, section, field) => {
    setUploadingImage(true);
    try {
      const formData = new FormData();
      formData.append('image', file);
      formData.append('section', section);
      formData.append('field', field);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/upload-image`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('cataloro_token')}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        // Update the appropriate field with the image URL
        if (section === 'seo') {
          updateSEOContent(field, data.imageUrl);
        }
        // Add more sections as needed
      }
    } catch (error) {
      console.error('Image upload error:', error);
    } finally {
      setUploadingImage(false);
    }
  };

  const sections = [
    { id: 'seo', name: 'SEO & Meta', icon: Search },
    { id: 'hero', name: 'Hero Section', icon: Layout },
    { id: 'stats', name: 'Statistics', icon: BarChart3 },
    { id: 'features', name: 'Features', icon: Settings },
    { id: 'testimonials', name: 'Testimonials', icon: Users },
    { id: 'cta', name: 'Call to Action', icon: Target },
    { id: 'footer', name: 'Footer', icon: Globe }
  ];

  return (
    <div className="space-y-8">
      {/* Enhanced Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center space-x-3">
            <Edit3 className="w-8 h-8 text-blue-600" />
            <span>Advanced Content Management</span>
          </h2>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            Comprehensive content management with SEO, media, and advanced editing capabilities
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {/* Auto-save indicator */}
          <div className="text-xs text-gray-500 dark:text-gray-400">
            Auto-save: Active
          </div>

          {/* Save Status */}
          {saveStatus && (
            <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
              saveStatus === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {saveStatus === 'success' ? 
                <CheckCircle className="w-4 h-4" /> : 
                <AlertCircle className="w-4 h-4" />
              }
              <span className="text-sm font-medium">
                {saveStatus === 'success' ? 'Content saved!' : 'Save failed'}
              </span>
            </div>
          )}

          {/* Preview Device Toggle */}
          <div className="flex items-center space-x-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setPreviewDevice('desktop')}
              className={`p-2 rounded transition-colors ${
                previewDevice === 'desktop' ? 'bg-white dark:bg-gray-700 shadow' : ''
              }`}
            >
              <Monitor className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPreviewDevice('mobile')}
              className={`p-2 rounded transition-colors ${
                previewDevice === 'mobile' ? 'bg-white dark:bg-gray-700 shadow' : ''
              }`}
            >
              <Smartphone className="w-4 h-4" />
            </button>
          </div>

          {/* Action Buttons */}
          <button
            onClick={() => setPreviewMode(!previewMode)}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200"
          >
            <Eye className="w-4 h-4" />
            <span>{previewMode ? 'Edit Mode' : 'Preview'}</span>
          </button>

          <button
            onClick={() => window.open('/info', '_blank')}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/70 transition-colors duration-200"
          >
            <ExternalLink className="w-4 h-4" />
            <span>Live Preview</span>
          </button>

          <button
            onClick={loadContent}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Reload</span>
          </button>

          <button
            onClick={saveContent}
            disabled={isLoading}
            className="flex items-center space-x-2 px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            <Save className="w-4 h-4" />
            <span>{isLoading ? 'Saving...' : 'Save Changes'}</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Enhanced Section Navigation */}
        <div className="lg:col-span-1">
          <div className="cataloro-card-glass p-6 backdrop-blur-2xl border-white/30 sticky top-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
              <FileText className="w-5 h-5 text-blue-600" />
              <span>Content Sections</span>
            </h3>
            <div className="space-y-2">
              {sections.map((section) => {
                const Icon = section.icon;
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                      activeSection === section.id
                        ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 scale-105'
                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="font-medium">{section.name}</span>
                  </button>
                );
              })}
            </div>

            {/* Quick Actions */}
            <div className="mt-6 pt-6 border-t border-white/20">
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Quick Actions</h4>
              <div className="space-y-2">
                <button
                  onClick={() => window.open('/info', '_blank')}
                  className="w-full flex items-center space-x-2 px-3 py-2 text-sm bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                >
                  <ExternalLink className="w-3 h-3" />
                  <span>View Live Site</span>
                </button>
                <button
                  onClick={() => {
                    const draft = JSON.stringify(contentSections, null, 2);
                    navigator.clipboard.writeText(draft);
                    alert('Content copied to clipboard!');
                  }}
                  className="w-full flex items-center space-x-2 px-3 py-2 text-sm bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                >
                  <Copy className="w-3 h-3" />
                  <span>Copy Content</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Content Editor */}
        <div className="lg:col-span-3">
          <div className="cataloro-card-glass p-8 backdrop-blur-2xl border-white/30 min-h-[600px]">
            {/* SEO & Meta Section Editor */}
            {activeSection === 'seo' && (
              <div className="space-y-6">
                <div className="flex items-center space-x-3 mb-6">
                  <Search className="w-6 h-6 text-blue-600" />
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">SEO & Meta Tags</h3>
                </div>

                <div className="grid grid-cols-1 gap-6">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                      Page Title (SEO)
                    </label>
                    <input
                      type="text"
                      value={contentSections.seo.title}
                      onChange={(e) => updateSEOContent('title', e.target.value)}
                      className="cataloro-input"
                      placeholder="Cataloro - Ultra-Modern Marketplace Platform"
                    />
                    <p className="text-xs text-gray-500 mt-1">Max 60 characters recommended. Current: {contentSections.seo.title.length}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                      Meta Description
                    </label>
                    <textarea
                      value={contentSections.seo.description}
                      onChange={(e) => updateSEOContent('description', e.target.value)}
                      className="cataloro-input h-24 resize-none"
                      placeholder="Experience the future of online commerce..."
                    />
                    <p className="text-xs text-gray-500 mt-1">Max 160 characters recommended. Current: {contentSections.seo.description.length}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                      Keywords (comma-separated)
                    </label>
                    <input
                      type="text"
                      value={contentSections.seo.keywords}
                      onChange={(e) => updateSEOContent('keywords', e.target.value)}
                      className="cataloro-input"
                      placeholder="marketplace, ecommerce, online shopping, buy sell"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                        Open Graph Image URL
                      </label>
                      <div className="flex space-x-2">
                        <input
                          type="text"
                          value={contentSections.seo.ogImage}
                          onChange={(e) => updateSEOContent('ogImage', e.target.value)}
                          className="cataloro-input flex-1"
                          placeholder="https://example.com/og-image.jpg"
                        />
                        <button
                          onClick={() => document.getElementById('og-image-upload').click()}
                          className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                          disabled={uploadingImage}
                        >
                          <Upload className="w-4 h-4" />
                        </button>
                        <input
                          id="og-image-upload"
                          type="file"
                          accept="image/*"
                          onChange={(e) => e.target.files[0] && handleImageUpload(e.target.files[0], 'seo', 'ogImage')}
                          className="hidden"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                        Canonical URL
                      </label>
                      <input
                        type="text"
                        value={contentSections.seo.canonicalUrl}
                        onChange={(e) => updateSEOContent('canonicalUrl', e.target.value)}
                        className="cataloro-input"
                        placeholder="/info"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Enhanced Hero Section Editor */}
            {activeSection === 'hero' && (
              <div className="space-y-6">
                <div className="flex items-center space-x-3 mb-6">
                  <Layout className="w-6 h-6 text-blue-600" />
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">Hero Section</h3>
                </div>

                <div className="grid grid-cols-1 gap-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                        Main Title
                      </label>
                      <input
                        type="text"
                        value={contentSections.hero.title}
                        onChange={(e) => updateHeroContent('title', e.target.value)}
                        className="cataloro-input"
                        placeholder="Cataloro"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                        Subtitle
                      </label>
                      <input
                        type="text"
                        value={contentSections.hero.subtitle}
                        onChange={(e) => updateHeroContent('subtitle', e.target.value)}
                        className="cataloro-input"
                        placeholder="Ultra-Modern Marketplace Platform"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                      Description
                    </label>
                    <ReactQuill
                      value={contentSections.hero.description}
                      onChange={(value) => updateHeroContent('description', value)}
                      modules={quillModules}
                      formats={quillFormats}
                      theme="snow"
                      className="bg-white dark:bg-gray-800 rounded-lg"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                        Primary Button
                      </label>
                      <div className="space-y-2">
                        <input
                          type="text"
                          value={contentSections.hero.primaryButtonText}
                          onChange={(e) => updateHeroContent('primaryButtonText', e.target.value)}
                          className="cataloro-input"
                          placeholder="Get Started"
                        />
                        <input
                          type="text"
                          value={contentSections.hero.primaryButtonLink}
                          onChange={(e) => updateHeroContent('primaryButtonLink', e.target.value)}
                          className="cataloro-input"
                          placeholder="/login"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                        Secondary Button
                      </label>
                      <div className="space-y-2">
                        <input
                          type="text"
                          value={contentSections.hero.secondaryButtonText}
                          onChange={(e) => updateHeroContent('secondaryButtonText', e.target.value)}
                          className="cataloro-input"
                          placeholder="Browse Marketplace"
                        />
                        <input
                          type="text"
                          value={contentSections.hero.secondaryButtonLink}
                          onChange={(e) => updateHeroContent('secondaryButtonLink', e.target.value)}
                          className="cataloro-input"
                          placeholder="/browse"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                        Background Style
                      </label>
                      <select
                        value={contentSections.hero.backgroundStyle}
                        onChange={(e) => updateHeroContent('backgroundStyle', e.target.value)}
                        className="cataloro-input"
                      >
                        <option value="gradient">Gradient</option>
                        <option value="solid">Solid Color</option>
                        <option value="image">Background Image</option>
                      </select>
                    </div>
                    <div className="flex items-center space-x-4">
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={contentSections.hero.showLogo}
                          onChange={(e) => updateHeroContent('showLogo', e.target.checked)}
                          className="rounded border-gray-300"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300">Show Logo</span>
                      </label>
                    </div>
                    <div className="flex items-center space-x-4">
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={contentSections.hero.logoAnimation}
                          onChange={(e) => updateHeroContent('logoAnimation', e.target.checked)}
                          className="rounded border-gray-300"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300">Logo Animation</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Enhanced Statistics Section Editor */}
            {activeSection === 'stats' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center space-x-3">
                    <BarChart3 className="w-6 h-6 text-blue-600" />
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">Statistics Section</h3>
                  </div>
                  <button
                    onClick={addStat}
                    className="flex items-center space-x-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Add Stat</span>
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {contentSections.stats.map((stat, index) => (
                    <div key={index} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg relative">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-semibold text-gray-900 dark:text-white">
                          Statistic {index + 1}
                        </h4>
                        {contentSections.stats.length > 1 && (
                          <button
                            onClick={() => removeStat(index)}
                            className="p-1 text-red-500 hover:text-red-700 transition-colors"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                      <div className="space-y-3">
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="block text-xs font-medium text-gray-700 dark:text-gray-200 mb-1">
                              Value
                            </label>
                            <input
                              type="text"
                              value={stat.value}
                              onChange={(e) => updateStatContent(index, 'value', e.target.value)}
                              className="cataloro-input text-sm"
                              placeholder="10K+"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 dark:text-gray-200 mb-1">
                              Label
                            </label>
                            <input
                              type="text"
                              value={stat.label}
                              onChange={(e) => updateStatContent(index, 'label', e.target.value)}
                              className="cataloro-input text-sm"
                              placeholder="Active Users"
                            />
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="block text-xs font-medium text-gray-700 dark:text-gray-200 mb-1">
                              Icon
                            </label>
                            <select
                              value={stat.icon}
                              onChange={(e) => updateStatContent(index, 'icon', e.target.value)}
                              className="cataloro-input text-sm"
                            >
                              <option value="users">Users</option>
                              <option value="package">Package</option>
                              <option value="trending">Trending</option>
                              <option value="star">Star</option>
                              <option value="zap">Zap</option>
                              <option value="target">Target</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 dark:text-gray-200 mb-1">
                              Color
                            </label>
                            <select
                              value={stat.color}
                              onChange={(e) => updateStatContent(index, 'color', e.target.value)}
                              className="cataloro-input text-sm"
                            >
                              <option value="blue">Blue</option>
                              <option value="green">Green</option>
                              <option value="purple">Purple</option>
                              <option value="yellow">Yellow</option>
                              <option value="red">Red</option>
                              <option value="pink">Pink</option>
                            </select>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ContentManagementSystem;