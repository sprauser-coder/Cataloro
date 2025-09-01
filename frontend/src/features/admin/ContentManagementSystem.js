/**
 * CATALORO - Content Management System
 * Rich text editor for managing info page content
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
  BarChart3
} from 'lucide-react';

function ContentManagementSystem() {
  const [contentSections, setContentSections] = useState({
    hero: {
      title: 'Cataloro',
      subtitle: 'Ultra-Modern Marketplace Platform',
      description: 'Experience the future of online commerce with our cutting-edge marketplace featuring real-time messaging, intelligent notifications, advanced search, and seamless transactions.',
      primaryButtonText: 'Get Started',
      secondaryButtonText: 'Browse Marketplace'
    },
    stats: [
      { label: 'Active Users', value: '10K+' },
      { label: 'Products Listed', value: '50K+' },
      { label: 'Successful Deals', value: '25K+' },
      { label: 'User Rating', value: '4.9★' }
    ],
    features: {
      title: 'Platform Features',
      description: 'Discover all the powerful features that make our marketplace the most advanced platform for buying and selling.',
      categories: [
        {
          name: 'Marketplace Core',
          description: 'Essential marketplace functionality with advanced search and product management.'
        },
        {
          name: 'Shopping Experience', 
          description: 'Seamless shopping with cart management, favorites, and secure transactions.'
        },
        {
          name: 'Communication',
          description: 'Real-time messaging, notifications, and user profile management.'
        },
        {
          name: 'Management Tools',
          description: 'Comprehensive admin and user management tools with analytics.'
        }
      ]
    },
    cta: {
      title: 'Ready to Get Started?',
      description: 'Join thousands of users who are already experiencing the future of online commerce. Create your account today and start buying or selling with confidence.',
      primaryButtonText: 'Start Your Journey',
      secondaryButtonText: 'Explore Platform'
    }
  });

  const [activeSection, setActiveSection] = useState('hero');
  const [isLoading, setSaveLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);
  const [previewMode, setPreviewMode] = useState(false);

  // Quill editor configuration
  const quillModules = {
    toolbar: [
      [{ 'header': [1, 2, 3, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      [{ 'align': [] }],
      ['link', 'image'],
      ['clean']
    ],
  };

  const quillFormats = [
    'header', 'bold', 'italic', 'underline', 'strike',
    'color', 'background', 'list', 'bullet', 'align',
    'link', 'image'
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
        body: JSON.stringify(contentSections)
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
        setContentSections(data);
      }
    } catch (error) {
      console.error('Load error:', error);
    }
  };

  useEffect(() => {
    loadContent();
  }, []);

  const updateHeroContent = (field, value) => {
    setContentSections(prev => ({
      ...prev,
      hero: {
        ...prev.hero,
        [field]: value
      }
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

  const updateFeaturesContent = (field, value) => {
    setContentSections(prev => ({
      ...prev,
      features: {
        ...prev.features,
        [field]: value
      }
    }));
  };

  const updateCTAContent = (field, value) => {
    setContentSections(prev => ({
      ...prev,
      cta: {
        ...prev.cta,
        [field]: value
      }
    }));
  };

  const sections = [
    { id: 'hero', name: 'Hero Section', icon: Layout },
    { id: 'stats', name: 'Statistics', icon: BarChart3 },
    { id: 'features', name: 'Features', icon: Settings },
    { id: 'cta', name: 'Call to Action', icon: Sparkles }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center space-x-3">
            <Edit3 className="w-8 h-8 text-blue-600" />
            <span>Content Management System</span>
          </h2>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            Manage the content of your info page with rich text editing capabilities
          </p>
        </div>

        <div className="flex items-center space-x-3">
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

          {/* Action Buttons */}
          <button
            onClick={() => setPreviewMode(!previewMode)}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200"
          >
            <Eye className="w-4 h-4" />
            <span>{previewMode ? 'Edit Mode' : 'Preview'}</span>
          </button>

          <button
            onClick={loadContent}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/70 transition-colors duration-200"
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
        {/* Section Navigation */}
        <div className="lg:col-span-1">
          <div className="cataloro-card-glass p-6 backdrop-blur-2xl border-white/30">
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
                        ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300'
                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="font-medium">{section.name}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Content Editor */}
        <div className="lg:col-span-3">
          <div className="cataloro-card-glass p-8 backdrop-blur-2xl border-white/30">
            {/* Hero Section Editor */}
            {activeSection === 'hero' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center space-x-2">
                  <Layout className="w-5 h-5 text-blue-600" />
                  <span>Hero Section</span>
                </h3>

                <div className="grid grid-cols-1 gap-6">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                      Main Title
                    </label>
                    <input
                      type="text"
                      value={contentSections.hero.title}
                      onChange={(e) => updateHeroContent('title', e.target.value)}
                      className="cataloro-input"
                      placeholder="Enter main title"
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
                      placeholder="Enter subtitle"
                    />
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
                        Primary Button Text
                      </label>
                      <input
                        type="text"
                        value={contentSections.hero.primaryButtonText}
                        onChange={(e) => updateHeroContent('primaryButtonText', e.target.value)}
                        className="cataloro-input"
                        placeholder="Primary button text"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                        Secondary Button Text
                      </label>
                      <input
                        type="text"
                        value={contentSections.hero.secondaryButtonText}
                        onChange={(e) => updateHeroContent('secondaryButtonText', e.target.value)}
                        className="cataloro-input"
                        placeholder="Secondary button text"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Statistics Section Editor */}
            {activeSection === 'stats' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5 text-blue-600" />
                  <span>Statistics Section</span>
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {contentSections.stats.map((stat, index) => (
                    <div key={index} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                      <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
                        Statistic {index + 1}
                      </h4>
                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
                            Value
                          </label>
                          <input
                            type="text"
                            value={stat.value}
                            onChange={(e) => updateStatContent(index, 'value', e.target.value)}
                            className="cataloro-input"
                            placeholder="e.g., 10K+"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
                            Label
                          </label>
                          <input
                            type="text"
                            value={stat.label}
                            onChange={(e) => updateStatContent(index, 'label', e.target.value)}
                            className="cataloro-input"
                            placeholder="e.g., Active Users"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Features Section Editor */}
            {activeSection === 'features' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center space-x-2">
                  <Settings className="w-5 h-5 text-blue-600" />
                  <span>Features Section</span>
                </h3>

                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                      Section Title
                    </label>
                    <input
                      type="text"
                      value={contentSections.features.title}
                      onChange={(e) => updateFeaturesContent('title', e.target.value)}
                      className="cataloro-input"
                      placeholder="Section title"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                      Section Description
                    </label>
                    <ReactQuill
                      value={contentSections.features.description}
                      onChange={(value) => updateFeaturesContent('description', value)}
                      modules={quillModules}
                      formats={quillFormats}
                      theme="snow"
                      className="bg-white dark:bg-gray-800 rounded-lg"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* CTA Section Editor */}
            {activeSection === 'cta' && (
              <div className="space-y-6">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-blue-600" />
                  <span>Call to Action Section</span>
                </h3>

                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                      CTA Title
                    </label>
                    <input
                      type="text"
                      value={contentSections.cta.title}
                      onChange={(e) => updateCTAContent('title', e.target.value)}
                      className="cataloro-input"
                      placeholder="Call to action title"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                      CTA Description
                    </label>
                    <ReactQuill
                      value={contentSections.cta.description}
                      onChange={(value) => updateCTAContent('description', value)}
                      modules={quillModules}
                      formats={quillFormats}
                      theme="snow"
                      className="bg-white dark:bg-gray-800 rounded-lg"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                        Primary Button Text
                      </label>
                      <input
                        type="text"
                        value={contentSections.cta.primaryButtonText}
                        onChange={(e) => updateCTAContent('primaryButtonText', e.target.value)}
                        className="cataloro-input"
                        placeholder="Primary button text"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">
                        Secondary Button Text
                      </label>
                      <input
                        type="text"
                        value={contentSections.cta.secondaryButtonText}
                        onChange={(e) => updateCTAContent('secondaryButtonText', e.target.value)}
                        className="cataloro-input"
                        placeholder="Secondary button text"
                      />
                    </div>
                  </div>
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