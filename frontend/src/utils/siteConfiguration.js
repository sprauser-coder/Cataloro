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
      
      /* Hero Section Control - ALWAYS ENABLED */
      /* Hero section is essential for the marketplace experience */
      ${false ? `
      .hero-section {
        display: none !important;
      }
      ` : ''}
      
      /* Featured Products Control */
      ${!config.featuredProductsEnabled ? `
      .featured-products-section {
        display: none !important;
      }
      ` : ''}
      
      /* Categories Showcase Control */
      ${!config.categoriesShowcase ? `
      .categories-showcase {
        display: none !important;
      }
      ` : ''}
      
      /* Newsletter Signup Control */
      ${!config.newsletterSignup ? `
      .newsletter-section {
        display: none !important;
      }
      ` : ''}
      
      /* Wishlist/Favorites Control */
      ${!config.wishlistEnabled ? `
      .wishlist-button,
      .favorites-button,
      .add-to-favorites {
        display: none !important;
      }
      ` : ''}
      
      /* Product Reviews Control */
      ${!config.productReviews ? `
      .reviews-section,
      .product-reviews,
      .review-button {
        display: none !important;
      }
      ` : ''}
      
      /* Compare Feature Control */
      ${!config.compareFeature ? `
      .compare-button,
      .product-compare {
        display: none !important;
      }
      ` : ''}
      
      /* Advanced Filters Control */
      ${!config.advancedFilters ? `
      .advanced-filters,
      .filter-panel {
        display: none !important;
      }
      ` : ''}
      
      /* Search Bar Prominence */
      ${config.searchBarProminent ? `
      .search-bar-container {
        transform: scale(1.1);
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
        border: 2px solid var(--primary-color);
      }
      ` : ''}
      
      /* Compact Mode */
      ${config.compactMode ? `
      .product-card {
        padding: 0.5rem !important;
      }
      .hero-section {
        min-height: 200px !important;
      }
      .page-padding {
        padding: 1rem !important;
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
    
    // Store feature flags for application logic
    const featureFlags = {
      heroSectionEnabled: config.heroSectionEnabled !== false,
      featuredProductsEnabled: config.featuredProductsEnabled !== false,
      categoriesShowcase: config.categoriesShowcase !== false,
      testimonialSection: config.testimonialSection !== false,
      newsletterSignup: config.newsletterSignup !== false,
      searchBarProminent: config.searchBarProminent || false,
      userRegistration: config.userRegistration !== false,
      guestBrowsing: config.guestBrowsing !== false,
      productReviews: config.productReviews !== false,
      wishlistEnabled: config.wishlistEnabled !== false,
      compareFeature: config.compareFeature || false,
      advancedFilters: config.advancedFilters !== false,
      bulkOperations: config.bulkOperations || false,
      productVariations: config.productVariations || false,
      inventoryTracking: config.inventoryTracking || false,
      compactMode: config.compactMode || false,
      animationsEnabled: config.animationsEnabled !== false
    };
    
    localStorage.setItem('cataloro_feature_flags', JSON.stringify(featureFlags));
    window.dispatchEvent(new CustomEvent('featureFlagsUpdated', { detail: featureFlags }));
    
    console.log('✅ Site configuration applied successfully', featureFlags);
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