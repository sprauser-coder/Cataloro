/**
 * Advertisement Configuration Utility
 * Handles initialization and management of ads configuration
 */

// Default ads configuration
export const DEFAULT_ADS_CONFIG = {
  adsManager: {
    browsePageAd: {
      active: true,  // Set to true by default for immediate functionality
      image: null,
      description: 'Browse Page Advertisement Space',
      runtime: '1 month',
      width: '300px',
      height: '600px'
    },
    favoriteAd: {
      active: false,
      image: null,
      description: '',
      runtime: '1 month'
    },
    messengerAd: {
      active: false,
      image: null,
      description: '',
      runtime: '1 month'
    },
    footerAd: {
      active: false,
      logo: null,
      companyName: '',
      runtime: '1 month'
    }
  },
  // Ensure hero section is always enabled
  heroSectionEnabled: true,
  featuredProductsEnabled: true,
  categoriesShowcase: true,
  testimonialSection: false,
  footerEnabled: true
};

// Initialize ads configuration in localStorage
export const initializeAdsConfiguration = () => {
  try {
    console.log('🔧 Initializing ads configuration...');
    
    // Check if configuration already exists
    const existingConfig = localStorage.getItem('cataloro_site_config');
    let currentConfig = {};
    
    if (existingConfig) {
      try {
        currentConfig = JSON.parse(existingConfig);
      } catch (error) {
        console.warn('⚠️ Invalid existing config, using defaults:', error);
        currentConfig = {};
      }
    }
    
    // Merge with defaults, preserving existing configuration
    const mergedConfig = {
      ...DEFAULT_ADS_CONFIG,
      ...currentConfig,
      adsManager: {
        ...DEFAULT_ADS_CONFIG.adsManager,
        ...(currentConfig.adsManager || {})
      }
    };
    
    // Ensure hero section is always enabled
    mergedConfig.heroSectionEnabled = true;
    
    // Save the merged configuration
    localStorage.setItem('cataloro_site_config', JSON.stringify(mergedConfig));
    
    console.log('✅ Ads configuration initialized:', mergedConfig);
    
    // Dispatch event to notify components
    window.dispatchEvent(new CustomEvent('adsConfigUpdated', { 
      detail: mergedConfig.adsManager 
    }));
    
    return mergedConfig;
  } catch (error) {
    console.error('❌ Failed to initialize ads configuration:', error);
    return DEFAULT_ADS_CONFIG;
  }
};

// Get current ads configuration
export const getAdsConfiguration = () => {
  try {
    const config = localStorage.getItem('cataloro_site_config');
    if (config) {
      const parsedConfig = JSON.parse(config);
      return parsedConfig.adsManager || DEFAULT_ADS_CONFIG.adsManager;
    }
    return DEFAULT_ADS_CONFIG.adsManager;
  } catch (error) {
    console.error('❌ Failed to get ads configuration:', error);
    return DEFAULT_ADS_CONFIG.adsManager;
  }
};

// Save ads configuration
export const saveAdsConfiguration = (adsConfig) => {
  try {
    const currentConfig = JSON.parse(localStorage.getItem('cataloro_site_config') || '{}');
    const updatedConfig = {
      ...currentConfig,
      adsManager: adsConfig,
      heroSectionEnabled: true // Always ensure hero section is enabled
    };
    
    localStorage.setItem('cataloro_site_config', JSON.stringify(updatedConfig));
    
    // Dispatch event to notify components
    window.dispatchEvent(new CustomEvent('adsConfigUpdated', { 
      detail: adsConfig 
    }));
    
    console.log('✅ Ads configuration saved:', adsConfig);
    return true;
  } catch (error) {
    console.error('❌ Failed to save ads configuration:', error);
    return false;
  }
};

// Load and apply ads configuration on app startup
export const loadAndApplyAdsConfiguration = () => {
  try {
    const config = initializeAdsConfiguration();
    
    // Apply site configuration to DOM if needed
    if (config.heroSectionEnabled === false) {
      // Force enable hero section
      config.heroSectionEnabled = true;
      localStorage.setItem('cataloro_site_config', JSON.stringify(config));
    }
    
    console.log('✅ Ads configuration loaded and applied on startup');
    return config;
  } catch (error) {
    console.warn('⚠️ Could not load ads configuration:', error);
    return initializeAdsConfiguration();
  }
};