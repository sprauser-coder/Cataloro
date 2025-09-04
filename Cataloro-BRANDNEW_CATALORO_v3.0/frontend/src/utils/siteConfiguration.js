/**
 * Site Configuration Utility
 * Handles site-wide configuration application
 */

// Apply site configuration changes to the DOM
export const applySiteConfiguration = (config) => {
  try {
    // Remove any existing configuration styles
    const existingStyle = document.getElementById('cataloro-site-config-styles');
    if (existingStyle) {
      existingStyle.remove();
    }

    // Create new style element
    const style = document.createElement('style');
    style.id = 'cataloro-site-config-styles';
    
    // Generate CSS based on configuration
    const css = `
      /* Site Configuration Styles */
      :root {
        --primary-color: ${config.primaryColor || '#3B82F6'};
        --secondary-color: ${config.secondaryColor || '#8B5CF6'};
        --accent-color: ${config.accentColor || '#10B981'};
      }
      
      /* Footer Configuration */
      ${!config.footerEnabled ? `
      footer {
        display: none !important;
      }
      ` : ''}
      
      /* Custom CSS */
      ${config.customCSS || ''}
    `;
    
    style.textContent = css;
    document.head.appendChild(style);
    
    // Apply footer configuration to localStorage if enabled
    if (config.footerEnabled) {
      const footerConfig = {
        enabled: config.footerEnabled,
        companyInfo: {
          name: config.footerCompanyName || 'Cataloro',
          tagline: config.footerTagline || 'Modern Marketplace for Everyone',
          description: config.footerDescription || 'Discover, buy, and sell amazing products in our trusted marketplace.',
        },
        contact: {
          email: config.footerEmail || 'hello@cataloro.com',
          phone: config.footerPhone || '+1 (555) 123-4567',
          address: config.footerAddress || '123 Marketplace St, Commerce City, CC 12345'
        },
        social: {
          facebook: config.footerFacebook || '',
          twitter: config.footerTwitter || '',
          instagram: config.footerInstagram || '',
          linkedin: config.footerLinkedin || '',
          youtube: config.footerYoutube || ''
        },
        style: {
          backgroundColor: config.footerBackgroundColor || '#1f2937',
          textColor: config.footerTextColor || '#ffffff',
          linkColor: config.footerLinkColor || '#60a5fa',
          borderColor: '#374151'
        }
      };
      
      localStorage.setItem('cataloro_footer_config', JSON.stringify(footerConfig));
    } else {
      localStorage.removeItem('cataloro_footer_config');
    }
    
    console.log('✅ Site configuration applied successfully');
    return true;
  } catch (error) {
    console.error('❌ Error applying site configuration:', error);
    return false;
  }
};

// Load site configuration on app startup
export const loadAndApplySiteConfiguration = () => {
  try {
    const savedConfig = localStorage.getItem('cataloro_site_config');
    if (savedConfig) {
      const parsedConfig = JSON.parse(savedConfig);
      applySiteConfiguration(parsedConfig);
      console.log('✅ Site configuration loaded and applied on startup');
      return true;
    }
    return false;
  } catch (error) {
    console.warn('⚠️ Could not load site configuration:', error);
    return false;
  }
};