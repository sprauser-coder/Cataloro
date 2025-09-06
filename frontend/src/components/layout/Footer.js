/**
 * CATALORO - Modern Footer Component
 * Editable footer that can be customized through site administration
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Facebook, 
  Twitter, 
  Instagram, 
  Linkedin, 
  Youtube,
  Mail,
  Phone,
  MapPin,
  Heart,
  Store
} from 'lucide-react';

// Hook to get ads configuration
function useAdsConfig() {
  const [adsConfig, setAdsConfig] = useState(null);
  
  useEffect(() => {
    const loadAdsConfig = () => {
      try {
        const savedConfig = localStorage.getItem('cataloro_site_config');
        if (savedConfig) {
          const config = JSON.parse(savedConfig);
          setAdsConfig(config.adsManager || null);
        }
      } catch (error) {
        console.warn('Could not load ads configuration');
      }
    };

    // Load initially
    loadAdsConfig();

    // Listen for ads config updates
    const handleAdsConfigUpdate = () => {
      loadAdsConfig();
    };

    window.addEventListener('adsConfigUpdated', handleAdsConfigUpdate);
    window.addEventListener('storage', handleAdsConfigUpdate);

    return () => {
      window.removeEventListener('adsConfigUpdated', handleAdsConfigUpdate);
      window.removeEventListener('storage', handleAdsConfigUpdate);
    };
  }, []);
  
  return adsConfig;
}

function Footer() {
  const [siteBranding, setSiteBranding] = useState({});
  const adsConfig = useAdsConfig();

  useEffect(() => {
    // Load site branding data to get the dark mode logo
    const loadBrandingData = () => {
      try {
        const brandingData = localStorage.getItem('cataloro_site_branding');
        if (brandingData) {
          const parsedBranding = JSON.parse(brandingData);
          setSiteBranding(parsedBranding);
        }
      } catch (error) {
        console.error('Error loading branding data in footer:', error);
      }
    };

    // Load initially
    loadBrandingData();

    // Listen for branding updates
    const handleBrandingUpdate = () => {
      loadBrandingData();
    };

    window.addEventListener('brandingUpdated', handleBrandingUpdate);
    window.addEventListener('storage', handleBrandingUpdate);

    return () => {
      window.removeEventListener('brandingUpdated', handleBrandingUpdate);
      window.removeEventListener('storage', handleBrandingUpdate);
    };
  }, []);

  // Get footer configuration from localStorage (set by site admin)
  const getFooterConfig = () => {
    try {
      const savedConfig = localStorage.getItem('cataloro_footer_config');
      const defaultConfig = getDefaultFooterConfig();
      
      if (!savedConfig) {
        return defaultConfig;
      }
      
      const parsedConfig = JSON.parse(savedConfig);
      
      // Merge with defaults to ensure all properties exist
      return {
        ...defaultConfig,
        ...parsedConfig,
        companyInfo: { ...defaultConfig.companyInfo, ...parsedConfig.companyInfo },
        contact: { ...defaultConfig.contact, ...parsedConfig.contact },
        social: { ...defaultConfig.social, ...parsedConfig.social },
        links: { 
          ...defaultConfig.links, 
          ...parsedConfig.links,
          about: parsedConfig.links?.about || defaultConfig.links.about,
          marketplace: parsedConfig.links?.marketplace || defaultConfig.links.marketplace,
          support: parsedConfig.links?.support || defaultConfig.links.support,
          legal: parsedConfig.links?.legal || defaultConfig.links.legal
        },
        style: { ...defaultConfig.style, ...parsedConfig.style }
      };
    } catch (error) {
      console.error('Error parsing footer config:', error);
      return getDefaultFooterConfig();
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
        { label: 'Categories', url: '/categories' },
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

  const config = getFooterConfig();

  if (!config.enabled) {
    return null;
  }

  const footerStyle = {
    backgroundColor: config.style.backgroundColor,
    color: config.style.textColor,
    borderColor: config.style.borderColor
  };

  const linkStyle = {
    color: config.style.linkColor
  };

  return (
    <footer style={footerStyle} className="bg-gray-900 text-white border-t">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main Footer Content */}
        <div className="py-12">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            
            {/* Company Information - WITH DARK MODE LOGO */}
            <div className="lg:col-span-1">
              <div className="flex items-center space-x-3 mb-4">
                {/* Show Dark Mode Logo if available, otherwise show default company info */}
                {siteBranding.logo_dark_url && siteBranding.logo_dark_url !== 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==' ? (
                  // Display Dark Mode Logo
                  <div className="flex flex-col space-y-2">
                    <img 
                      src={siteBranding.logo_dark_url}
                      alt={siteBranding.site_name || config.companyInfo.name}
                      className="h-12 max-w-[200px] object-contain"
                      onError={(e) => {
                        // Fallback to default if logo fails to load
                        e.target.style.display = 'none';
                        e.target.parentElement.nextElementSibling.style.display = 'flex';
                      }}
                    />
                  </div>
                ) : siteBranding.logo_light_url && siteBranding.logo_light_url !== 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==' ? (
                  // Fallback to Light Mode Logo if Dark Mode Logo not available
                  <div className="flex flex-col space-y-2">
                    <img 
                      src={siteBranding.logo_light_url}
                      alt={siteBranding.site_name || config.companyInfo.name}
                      className="h-12 max-w-[200px] object-contain"
                      onError={(e) => {
                        // Fallback to default if logo fails to load
                        e.target.style.display = 'none';
                        e.target.parentElement.nextElementSibling.style.display = 'flex';
                      }}
                    />
                  </div>
                ) : (
                  // Fallback to default company branding
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
                      <Store className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                        {siteBranding.site_name || config.companyInfo.name}
                      </h3>
                      <p className="text-sm text-gray-400">{siteBranding.site_description || config.companyInfo.tagline}</p>
                    </div>
                  </div>
                )}
                
                {/* Hidden fallback (shown if logo fails to load) */}
                <div className="items-center space-x-3" style={{ display: 'none' }}>
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
                    <Store className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                      {siteBranding.site_name || config.companyInfo.name}
                    </h3>
                    <p className="text-sm text-gray-400">{siteBranding.site_description || config.companyInfo.tagline}</p>
                  </div>
                </div>
              </div>
              <p className="text-gray-300 text-sm mb-6 leading-relaxed">
                {config.companyInfo.description}
              </p>
              
              {/* Contact Information */}
              <div className="space-y-3">
                <div className="flex items-center space-x-3 text-sm">
                  <Mail className="w-4 h-4 text-blue-400" />
                  <a href={`mailto:${config.contact.email}`} style={linkStyle} className="hover:text-blue-300">
                    {config.contact.email}
                  </a>
                </div>
                <div className="flex items-center space-x-3 text-sm">
                  <Phone className="w-4 h-4 text-blue-400" />
                  <a href={`tel:${config.contact.phone}`} style={linkStyle} className="hover:text-blue-300">
                    {config.contact.phone}
                  </a>
                </div>
                <div className="flex items-center space-x-3 text-sm">
                  <MapPin className="w-4 h-4 text-blue-400" />
                  <span className="text-gray-300">{config.contact.address}</span>
                </div>
                
                {/* Footer Advertisement - Right below address */}
                {adsConfig?.footerAd?.active && adsConfig.footerAd.logo && adsConfig.footerAd.companyName && (
                  <div 
                    className={`flex items-center space-x-3 text-sm text-gray-400 mt-4 pt-4 border-t border-gray-700 ${adsConfig.footerAd.url ? 'cursor-pointer hover:text-gray-300 transition-colors' : ''}`}
                    onClick={() => {
                      if (adsConfig.footerAd.url) {
                        // Track footer ad click using utility function
                        try {
                          // Import the tracking function dynamically
                          import('../../utils/adsConfiguration').then(({ trackAdClick }) => {
                            trackAdClick('footerAd');
                          });
                        } catch (error) {
                          console.warn('Could not track ad click:', error);
                        }
                        console.log('Footer ad clicked:', adsConfig.footerAd.url);
                        window.open(adsConfig.footerAd.url, '_blank');
                      }
                    }}
                  >
                    <span>In cooperation with</span>
                    <img 
                      src={adsConfig.footerAd.logo} 
                      alt={adsConfig.footerAd.companyName}
                      className="w-12 h-12 object-contain" // Made bigger: was w-6 h-6, now w-12 h-12
                    />
                    <span className="font-medium text-gray-300">{adsConfig.footerAd.companyName}</span>
                  </div>
                )}
              </div>
            </div>

            {/* About Links */}
            <div>
              <h4 className="text-lg font-semibold mb-4">About</h4>
              <ul className="space-y-3">
                {(config.links?.about || []).map((link, index) => (
                  <li key={index}>
                    <Link 
                      to={link.url} 
                      style={linkStyle}
                      className="text-sm hover:text-blue-300"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Marketplace Links */}
            <div>
              <h4 className="text-lg font-semibold mb-4">Marketplace</h4>
              <ul className="space-y-3">
                {(config.links?.marketplace || []).map((link, index) => (
                  <li key={index}>
                    <Link 
                      to={link.url} 
                      style={linkStyle}
                      className="text-sm hover:text-blue-300"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            {/* Support & Legal Links */}
            <div>
              <h4 className="text-lg font-semibold mb-4">Support</h4>
              <ul className="space-y-3 mb-6">
                {(config.links?.support || []).map((link, index) => (
                  <li key={index}>
                    <Link 
                      to={link.url} 
                      style={linkStyle}
                      className="text-sm hover:text-blue-300"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
              
              <h5 className="text-md font-semibold mb-3">Legal</h5>
              <ul className="space-y-2">
                {(config.links?.legal || []).map((link, index) => (
                  <li key={index}>
                    <Link 
                      to={link.url} 
                      style={linkStyle}
                      className="text-xs hover:text-blue-300"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Social Media & Copyright */}
        <div style={{ borderColor: config.style.borderColor }} className="border-t py-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            
            {/* Social Media Links */}
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-400">Follow us:</span>
              <div className="flex space-x-3">
                {config.social.facebook && (
                  <a 
                    href={config.social.facebook} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-blue-400"
                  >
                    <Facebook className="w-5 h-5" />
                  </a>
                )}
                {config.social.twitter && (
                  <a 
                    href={config.social.twitter} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-blue-400"
                  >
                    <Twitter className="w-5 h-5" />
                  </a>
                )}
                {config.social.instagram && (
                  <a 
                    href={config.social.instagram} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-pink-400"
                  >
                    <Instagram className="w-5 h-5" />
                  </a>
                )}
                {config.social.linkedin && (
                  <a 
                    href={config.social.linkedin} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-blue-400"
                  >
                    <Linkedin className="w-5 h-5" />
                  </a>
                )}
                {config.social.youtube && (
                  <a 
                    href={config.social.youtube} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-red-400"
                  >
                    <Youtube className="w-5 h-5" />
                  </a>
                )}
              </div>
            </div>

            {/* Copyright */}
            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <span>© 2025 {config.companyInfo.name}. Made with</span>
              <Heart className="w-4 h-4 text-red-400" />
              <span>for amazing marketplace experiences.</span>
            </div>


          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;