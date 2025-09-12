/**
 * CATALORO - Footer Management Component
 * Allows admin to configure the footer content dynamically
 */

import React, { useState, useEffect } from 'react';
import { 
  Save, 
  Plus, 
  Trash2, 
  ExternalLink,
  Facebook,
  Twitter,
  Instagram,
  Linkedin,
  Youtube,
  Eye,
  EyeOff
} from 'lucide-react';

function FooterManagement({ showToast }) {
  const [footerConfig, setFooterConfig] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Load footer configuration from localStorage
  useEffect(() => {
    loadFooterConfig();
  }, []);

  const loadFooterConfig = () => {
    try {
      const savedConfig = localStorage.getItem('cataloro_footer_config');
      if (savedConfig) {
        setFooterConfig(JSON.parse(savedConfig));
      } else {
        // Set default configuration
        setFooterConfig(getDefaultFooterConfig());
      }
    } catch (error) {
      console.error('Error loading footer config:', error);
      setFooterConfig(getDefaultFooterConfig());
    } finally {
      setIsLoading(false);
    }
  };

  const getDefaultFooterConfig = () => ({
    enabled: true,
    companyInfo: {
      name: 'Cataloro',
      tagline: 'Modern Marketplace for Everyone',
      description: 'Discover, buy, and sell amazing products in our trusted marketplace. Connect with sellers worldwide and find exactly what you\'re looking for.',
      logo: '/logo.png'
    },
    contact: {
      email: 'hello@cataloro.com',
      phone: '+1 (555) 123-4567',
      address: '123 Marketplace St, Commerce City, CC 12345'
    },
    social: {
      facebook: 'https://facebook.com/cataloro',
      twitter: 'https://twitter.com/cataloro',
      instagram: 'https://instagram.com/cataloro',
      linkedin: 'https://linkedin.com/company/cataloro',
      youtube: 'https://youtube.com/cataloro'
    },
    links: {
      about: [
        { label: 'About Us', url: '/about' },
        { label: 'Our Story', url: '/story' },
        { label: 'Careers', url: '/careers' },
        { label: 'Press', url: '/press' }
      ],
      marketplace: [
        { label: 'Browse Products', url: '/browse' },
        { label: 'Sell on Cataloro', url: '/sell' },
        { label: 'Seller Center', url: '/seller' }
      ],
      support: [
        { label: 'Help Center', url: '/help' },
        { label: 'Contact Support', url: '/support' },
        { label: 'Community', url: '/community' },
        { label: 'Safety', url: '/safety' }
      ],
      legal: [
        { label: 'Privacy Policy', url: '/privacy' },
        { label: 'Terms of Service', url: '/terms' },
        { label: 'Cookie Policy', url: '/cookies' },
        { label: 'Seller Agreement', url: '/seller-terms' }
      ]
    },
    style: {
      backgroundColor: '#1f2937',
      textColor: '#ffffff',
      linkColor: '#60a5fa',
      borderColor: '#374151'
    }
  });

  const handleBasicInfoChange = (field, value) => {
    setFooterConfig(prev => ({
      ...prev,
      companyInfo: {
        ...prev.companyInfo,
        [field]: value
      }
    }));
  };

  const handleContactChange = (field, value) => {
    setFooterConfig(prev => ({
      ...prev,
      contact: {
        ...prev.contact,
        [field]: value
      }
    }));
  };

  const handleSocialChange = (platform, value) => {
    setFooterConfig(prev => ({
      ...prev,
      social: {
        ...prev.social,
        [platform]: value
      }
    }));
  };

  const handleStyleChange = (field, value) => {
    setFooterConfig(prev => ({
      ...prev,
      style: {
        ...prev.style,
        [field]: value
      }
    }));
  };

  const handleLinkChange = (section, index, field, value) => {
    setFooterConfig(prev => ({
      ...prev,
      links: {
        ...prev.links,
        [section]: prev.links[section].map((link, i) => 
          i === index ? { ...link, [field]: value } : link
        )
      }
    }));
  };

  const addLink = (section) => {
    setFooterConfig(prev => ({
      ...prev,
      links: {
        ...prev.links,
        [section]: [...(prev.links?.[section] || []), { label: '', url: '' }]
      }
    }));
  };

  const removeLink = (section, index) => {
    setFooterConfig(prev => ({
      ...prev,
      links: {
        ...prev.links,
        [section]: (prev.links?.[section] || []).filter((_, i) => i !== index)
      }
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Save to localStorage
      localStorage.setItem('cataloro_footer_config', JSON.stringify(footerConfig));
      
      // Dispatch event to notify footer component
      window.dispatchEvent(new CustomEvent('footerConfigUpdated', { 
        detail: footerConfig 
      }));

      showToast('Footer configuration saved successfully!', 'success');
    } catch (error) {
      console.error('Error saving footer config:', error);
      showToast('Failed to save footer configuration', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const handleToggleEnabled = () => {
    setFooterConfig(prev => ({
      ...prev,
      enabled: !prev.enabled
    }));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Enable/Disable Footer */}
      <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div>
          <h4 className="font-medium text-gray-900 dark:text-white">Footer Display</h4>
          <p className="text-sm text-gray-600 dark:text-gray-400">Show or hide the footer on your site</p>
        </div>
        <button
          onClick={handleToggleEnabled}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
            footerConfig.enabled 
              ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
              : 'bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-400'
          }`}
        >
          {footerConfig.enabled ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          <span>{footerConfig.enabled ? 'Enabled' : 'Disabled'}</span>
        </button>
      </div>

      {footerConfig && footerConfig.enabled && (
        <>
          {/* Company Information */}
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900 dark:text-white">Company Information</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Company Name
                </label>
                <input
                  type="text"
                  value={footerConfig.companyInfo?.name || ''}
                  onChange={(e) => handleBasicInfoChange('name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Enter company name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Tagline
                </label>
                <input
                  type="text"
                  value={footerConfig.companyInfo?.tagline || ''}
                  onChange={(e) => handleBasicInfoChange('tagline', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Enter company tagline"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Description
              </label>
              <textarea
                rows={3}
                value={footerConfig.companyInfo?.description || ''}
                onChange={(e) => handleBasicInfoChange('description', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Enter company description"
              />
            </div>
          </div>

          {/* Contact Information */}
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900 dark:text-white">Contact Information</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={footerConfig.contact?.email || ''}
                  onChange={(e) => handleContactChange('email', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="contact@example.com"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Phone
                </label>
                <input
                  type="text"
                  value={footerConfig.contact?.phone || ''}
                  onChange={(e) => handleContactChange('phone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="+1 (555) 123-4567"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Address
                </label>
                <input
                  type="text"
                  value={footerConfig.contact?.address || ''}
                  onChange={(e) => handleContactChange('address', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="123 Main St, City, State 12345"
                />
              </div>
            </div>
          </div>

          {/* Social Media Links */}
          <div className="space-y-4">
            <h4 className="font-medium text-gray-900 dark:text-white">Social Media Links</h4>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { key: 'facebook', label: 'Facebook', icon: Facebook },
                { key: 'twitter', label: 'Twitter', icon: Twitter },
                { key: 'instagram', label: 'Instagram', icon: Instagram },
                { key: 'linkedin', label: 'LinkedIn', icon: Linkedin },
                { key: 'youtube', label: 'YouTube', icon: Youtube }
              ].map(({ key, label, icon: Icon }) => (
                <div key={key} className="flex items-center space-x-3">
                  <Icon className="w-5 h-5 text-gray-500" />
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      {label}
                    </label>
                    <input
                      type="url"
                      value={footerConfig.social?.[key] || ''}
                      onChange={(e) => handleSocialChange(key, e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder={`https://${key}.com/yourcompany`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Footer Links Sections */}
          {footerConfig && footerConfig.links && ['about', 'marketplace', 'support', 'legal'].map((section) => (
            <div key={section} className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium text-gray-900 dark:text-white capitalize">
                  {section} Links
                </h4>
                <button
                  onClick={() => addLink(section)}
                  className="flex items-center space-x-2 px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Link</span>
                </button>
              </div>

              <div className="space-y-3">
                {(footerConfig.links[section] || []).map((link, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className="flex-1 grid grid-cols-2 gap-3">
                      <input
                        type="text"
                        value={link.label || ''}
                        onChange={(e) => handleLinkChange(section, index, 'label', e.target.value)}
                        className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        placeholder="Link Label"
                      />
                      <input
                        type="text"
                        value={link.url || ''}
                        onChange={(e) => handleLinkChange(section, index, 'url', e.target.value)}
                        className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        placeholder="/path or https://example.com"
                      />
                    </div>
                    <button
                      onClick={() => removeLink(section, index)}
                      className="p-2 text-red-600 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Style Configuration */}
          {footerConfig && footerConfig.style && (
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900 dark:text-white">Footer Styling</h4>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Background Color
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="color"
                      value={footerConfig.style.backgroundColor || '#1f2937'}
                      onChange={(e) => handleStyleChange('backgroundColor', e.target.value)}
                      className="w-10 h-10 rounded-lg border border-gray-300 dark:border-gray-600"
                    />
                    <input
                      type="text"
                      value={footerConfig.style.backgroundColor || '#1f2937'}
                      onChange={(e) => handleStyleChange('backgroundColor', e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Text Color
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="color"
                      value={footerConfig.style.textColor || '#ffffff'}
                      onChange={(e) => handleStyleChange('textColor', e.target.value)}
                      className="w-10 h-10 rounded-lg border border-gray-300 dark:border-gray-600"
                    />
                    <input
                      type="text"
                      value={footerConfig.style.textColor || '#ffffff'}
                      onChange={(e) => handleStyleChange('textColor', e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Link Color
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="color"
                      value={footerConfig.style.linkColor || '#60a5fa'}
                      onChange={(e) => handleStyleChange('linkColor', e.target.value)}
                      className="w-10 h-10 rounded-lg border border-gray-300 dark:border-gray-600"
                    />
                    <input
                      type="text"
                      value={footerConfig.style.linkColor || '#60a5fa'}
                      onChange={(e) => handleStyleChange('linkColor', e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Border Color
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="color"
                      value={footerConfig.style.borderColor || '#374151'}
                      onChange={(e) => handleStyleChange('borderColor', e.target.value)}
                      className="w-10 h-10 rounded-lg border border-gray-300 dark:border-gray-600"
                    />
                    <input
                      type="text"
                      value={footerConfig.style.borderColor || '#374151'}
                      onChange={(e) => handleStyleChange('borderColor', e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${
            isSaving
              ? 'bg-gray-400 text-white cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          <Save className="w-4 h-4" />
          <span>{isSaving ? 'Saving...' : 'Save Footer Configuration'}</span>
        </button>
      </div>
    </div>
  );
}

export default FooterManagement;