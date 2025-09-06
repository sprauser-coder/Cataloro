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
      height: '600px',
      url: '', // Link URL for the ad
      clicks: 0, // Click counter
      startDate: null, // When the ad was activated
      expirationDate: null, // When the ad expires
      expirationEvents: ['deactivate'] // Default: just deactivate when expired
    },
    favoriteAd: {
      active: false,
      image: null,
      description: '',
      runtime: '1 month',
      width: '100%',
      height: '200px',
      url: '',
      clicks: 0,
      startDate: null,
      expirationDate: null,
      expirationEvents: ['deactivate'],
      notificationMethods: ['notificationCenter'],
      notificationUsers: []
    },
    messengerAd: {
      active: false,
      image: null,
      description: '',
      runtime: '1 month',
      width: '250px',
      height: '400px',
      url: '',
      clicks: 0,
      startDate: null,
      expirationDate: null,
      expirationEvents: ['deactivate'],
      notificationMethods: ['notificationCenter'],
      notificationUsers: []
    },
    footerAd: {
      active: false,
      logo: null,
      companyName: '',
      runtime: '1 month',
      url: '',
      clicks: 0,
      startDate: null,
      expirationDate: null,
      expirationEvents: ['deactivate']
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

// Track ad click
export const trackAdClick = (adType) => {
  try {
    const currentConfig = JSON.parse(localStorage.getItem('cataloro_site_config') || '{}');
    
    if (currentConfig.adsManager && currentConfig.adsManager[adType]) {
      // Increment click count
      currentConfig.adsManager[adType].clicks = (currentConfig.adsManager[adType].clicks || 0) + 1;
      
      // Save updated configuration
      localStorage.setItem('cataloro_site_config', JSON.stringify(currentConfig));
      
      // Dispatch event to notify components
      window.dispatchEvent(new CustomEvent('adClicked', { 
        detail: { adType, clicks: currentConfig.adsManager[adType].clicks }
      }));
      
      console.log(`🔗 Ad click tracked: ${adType} (Total clicks: ${currentConfig.adsManager[adType].clicks})`);
      return currentConfig.adsManager[adType].clicks;
    }
  } catch (error) {
    console.error('❌ Failed to track ad click:', error);
  }
  return 0;
};

// Calculate expiration date based on runtime
export const calculateExpirationDate = (startDate, runtime) => {
  if (!startDate) return null;
  
  const start = new Date(startDate);
  const expiration = new Date(start);
  
  // Handle custom runtime format: custom_XdYhZm
  if (runtime && runtime.startsWith('custom_')) {
    const customPattern = /custom_(\d+)d_(\d+)h_(\d+)m/;
    const match = runtime.match(customPattern);
    
    if (match) {
      const days = parseInt(match[1]) || 0;
      const hours = parseInt(match[2]) || 0;
      const minutes = parseInt(match[3]) || 0;
      
      expiration.setDate(expiration.getDate() + days);
      expiration.setHours(expiration.getHours() + hours);
      expiration.setMinutes(expiration.getMinutes() + minutes);
      
      console.log(`🕒 Custom runtime calculated: ${days}d ${hours}h ${minutes}m`);
      return expiration.toISOString();
    }
  }
  
  // Handle predefined runtime options
  switch (runtime) {
    case '1 month':
      expiration.setMonth(expiration.getMonth() + 1);
      break;
    case '3 months':
      expiration.setMonth(expiration.getMonth() + 3);
      break;
    case '12 months':
    case '1 year':
      expiration.setFullYear(expiration.getFullYear() + 1);
      break;
    default:
      expiration.setMonth(expiration.getMonth() + 1); // Default to 1 month
  }
  
  return expiration.toISOString();
};

// Check if ad is expired
export const isAdExpired = (adConfig) => {
  if (!adConfig.expirationDate) return false;
  return new Date() > new Date(adConfig.expirationDate);
};

// Get time remaining for ad
export const getTimeRemaining = (expirationDate) => {
  if (!expirationDate) return null;
  
  const now = new Date();
  const expiration = new Date(expirationDate);
  const diff = expiration - now;
  
  if (diff <= 0) return { expired: true };
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);
  
  return { days, hours, minutes, seconds, expired: false };
};

// Activate ad with start date and expiration
export const activateAd = (adType, adConfig) => {
  try {
    const currentConfig = JSON.parse(localStorage.getItem('cataloro_site_config') || '{}');
    
    if (!currentConfig.adsManager) currentConfig.adsManager = {};
    if (!currentConfig.adsManager[adType]) currentConfig.adsManager[adType] = {};
    
    const now = new Date().toISOString();
    const expirationDate = calculateExpirationDate(now, adConfig.runtime || '1 month');
    
    currentConfig.adsManager[adType] = {
      ...currentConfig.adsManager[adType],
      ...adConfig,
      active: true,
      startDate: now,
      expirationDate: expirationDate
    };
    
    localStorage.setItem('cataloro_site_config', JSON.stringify(currentConfig));
    
    // Dispatch event to notify components
    window.dispatchEvent(new CustomEvent('adsConfigUpdated', { 
      detail: currentConfig.adsManager 
    }));
    
    console.log(`🕒 Ad activated: ${adType} (Expires: ${expirationDate})`);
    return true;
  } catch (error) {
    console.error('❌ Failed to activate ad:', error);
    return false;
  }
};

// Execute expiration events
export const executeExpirationEvents = (adType, adConfig) => {
  const events = adConfig.expirationEvents || [];
  
  console.log(`🔔 Executing expiration events for ${adType}:`, events);
  
  events.forEach(event => {
    switch (event) {
      case 'notify':
        // Send notification to admin
        console.log(`📧 Sending admin notification for expired ad: ${adType}`);
        // Dispatch custom event for notification
        window.dispatchEvent(new CustomEvent('adExpiredNotification', {
          detail: { adType, adConfig, message: `Advertisement "${adType}" has expired` }
        }));
        break;
        
      case 'deactivate':
        console.log(`❌ Deactivating expired ad: ${adType}`);
        // This will be handled by the existing deactivation logic
        break;
        
      case 'reset':
        console.log(`🔄 Resetting duration for ad: ${adType}`);
        try {
          const currentConfig = JSON.parse(localStorage.getItem('cataloro_site_config') || '{}');
          if (currentConfig.adsManager && currentConfig.adsManager[adType]) {
            const now = new Date().toISOString();
            const originalRuntime = currentConfig.adsManager[adType].runtime;
            const newExpirationDate = calculateExpirationDate(now, originalRuntime);
            
            // Reset start and expiration dates
            currentConfig.adsManager[adType].startDate = now;
            currentConfig.adsManager[adType].expirationDate = newExpirationDate;
            currentConfig.adsManager[adType].active = true; // Ensure it stays active
            
            localStorage.setItem('cataloro_site_config', JSON.stringify(currentConfig));
            
            // Dispatch update event
            window.dispatchEvent(new CustomEvent('adsConfigUpdated', { 
              detail: currentConfig.adsManager 
            }));
            
            console.log(`🔄 Ad duration reset for ${adType} until:`, newExpirationDate);
          }
        } catch (error) {
          console.error(`Error resetting ad duration for ${adType}:`, error);
        }
        break;
        
      default:
        console.warn(`Unknown expiration event: ${event}`);
    }
  });
};

// Deactivate expired ads (enhanced with event handling) - Only runs automatically, not on manual admin actions
export const deactivateExpiredAds = (skipManualOverride = false) => {
  try {
    const currentConfig = JSON.parse(localStorage.getItem('cataloro_site_config') || '{}');
    
    if (!currentConfig.adsManager) return;
    
    let hasChanges = false;
    
    Object.keys(currentConfig.adsManager).forEach(adType => {
      const adConfig = currentConfig.adsManager[adType];
      
      // Only process ads that are active and expired
      if (adConfig.active && isAdExpired(adConfig)) {
        
        // Check if this is a manual admin action - if so, skip automatic processing
        if (skipManualOverride) {
          console.log(`🔧 Skipping automatic expiration for ${adType} - manual admin control active`);
          return;
        }
        
        // Execute expiration events before making decisions
        executeExpirationEvents(adType, adConfig);
        
        // Check configured events
        const hasResetEvent = adConfig.expirationEvents?.includes('reset');
        const hasDeactivateEvent = adConfig.expirationEvents?.includes('deactivate');
        
        if (hasResetEvent && !hasDeactivateEvent) {
          // Reset event will handle reactivation, don't deactivate
          console.log(`🔄 Ad ${adType} expired but configured for reset - automatic reactivation handled`);
        } else if (hasDeactivateEvent || (!hasResetEvent && !hasDeactivateEvent)) {
          // Deactivate the ad (explicit deactivate event or default behavior)
          currentConfig.adsManager[adType].active = false;
          hasChanges = true;
          console.log(`🕒 Ad expired and automatically deactivated: ${adType} (can be manually reactivated by admin)`);
        }
      }
    });
    
    if (hasChanges) {
      localStorage.setItem('cataloro_site_config', JSON.stringify(currentConfig));
      
      // Dispatch event to notify components
      window.dispatchEvent(new CustomEvent('adsConfigUpdated', { 
        detail: currentConfig.adsManager 
      }));
    }
    
    return hasChanges;
  } catch (error) {
    console.error('❌ Failed to deactivate expired ads:', error);
    return false;
  }
};