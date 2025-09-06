/**
 * Global Ad Expiration Service
 * Manages ad expiration checking and event execution in the background
 * Runs independently of whether the admin panel is active or not
 */

import { getTimeRemaining, isAdExpired } from '../utils/adsConfiguration';

class AdsExpirationService {
  constructor() {
    this.intervalId = null;
    this.isRunning = false;
    this.checkInterval = 60000; // Check every minute
    this.processedExpirations = new Set(); // Track processed expirations to prevent duplicates
  }

  /**
   * Start the global expiration monitoring service
   */
  start() {
    if (this.isRunning) {
      console.log('🔄 Ads expiration service already running');
      return;
    }

    console.log('🚀 Starting global ads expiration service');
    this.isRunning = true;
    
    // Check immediately on start
    this.checkExpirations();
    
    // Set up periodic checking
    this.intervalId = setInterval(() => {
      this.checkExpirations();
    }, this.checkInterval);
  }

  /**
   * Stop the expiration monitoring service
   */
  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.isRunning = false;
    console.log('🛑 Stopped global ads expiration service');
  }

  /**
   * Check all active ads for expiration and execute events
   */
  async checkExpirations() {
    try {
      const currentConfig = JSON.parse(localStorage.getItem('cataloro_site_config') || '{}');
      const adsManager = currentConfig.adsManager || {};

      console.log('🔍 Checking ad expirations...');

      for (const [adType, adConfig] of Object.entries(adsManager)) {
        if (adConfig.active && adConfig.expirationDate) {
          const isExpired = isAdExpired(adConfig);
          const expirationKey = `${adType}_${adConfig.expirationDate}`;

          if (isExpired && !this.processedExpirations.has(expirationKey)) {
            console.log(`⏰ Ad ${adType} has expired - executing events`);
            
            // Mark this expiration as processed
            this.processedExpirations.add(expirationKey);
            
            // Execute expiration events
            await this.executeExpirationEvents(adType, adConfig, currentConfig);
          }
        }
      }
    } catch (error) {
      console.error('❌ Error checking ad expirations:', error);
    }
  }

  /**
   * Execute expiration events for an expired ad
   */
  async executeExpirationEvents(adType, adConfig, currentConfig) {
    const expirationEvents = adConfig.expirationEvents || [];
    
    console.log(`🔔 Executing expiration events for ${adType}:`, expirationEvents);

    for (const event of expirationEvents) {
      try {
        await this.executeEvent(event, adType, adConfig, currentConfig);
      } catch (error) {
        console.error(`❌ Error executing expiration event ${event} for ${adType}:`, error);
      }
    }
  }

  /**
   * Execute a specific expiration event
   */
  async executeEvent(event, adType, adConfig, currentConfig) {
    switch (event) {
      case 'notify':
        await this.executeNotifyEvent(adType, adConfig);
        break;
        
      case 'deactivate':
        this.executeDeactivateEvent(adType, adConfig, currentConfig);
        break;
        
      case 'reset':
        this.executeResetEvent(adType, adConfig, currentConfig);
        break;
        
      default:
        console.warn(`❓ Unknown expiration event: ${event}`);
    }
  }

  /**
   * Execute notification event
   */
  async executeNotifyEvent(adType, adConfig) {
    console.log(`📧 Sending notifications for expired ad: ${adType}`);
    
    const notificationMethods = adConfig.notificationMethods || ['notificationCenter'];
    
    // Handle notification center notifications
    if (notificationMethods.includes('notificationCenter')) {
      const selectedUsers = adConfig.notificationUsers || [];
      console.log(`🔔 Sending notification center alerts to ${selectedUsers.length} users`);
      
      if (selectedUsers.length > 0) {
        // Send notifications to each selected user via backend API
        const notificationPromises = selectedUsers.map(async (user) => {
          try {
            const adDescription = adConfig.description || adType;
            const pageLocation = this.getPageLocationName(adType);
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${user.id}/notifications`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                title: '⏰ Advertisement Expired',
                message: `"${adDescription}" on ${pageLocation} has expired and been processed according to your settings`,
                type: 'warning'
              })
            });
            
            if (response.ok) {
              console.log(`✅ Expiration notification sent to user ${user.email} (${user.id})`);
              return { success: true, user: user.email };
            } else {
              console.error(`❌ Failed to send expiration notification to user ${user.email}`);
              return { success: false, user: user.email, error: 'HTTP Error' };
            }
          } catch (error) {
            console.error(`❌ Error sending expiration notification to user ${user.email}:`, error);
            return { success: false, user: user.email, error: error.message };
          }
        });
        
        try {
          const results = await Promise.all(notificationPromises);
          const successCount = results.filter(r => r.success).length;
          console.log(`📊 Expiration notifications: ${successCount}/${selectedUsers.length} sent successfully`);
        } catch (error) {
          console.error('❌ Error in batch expiration notification sending:', error);
        }
      }
    }

    // Handle other notification methods (email, browser push) if needed
    if (notificationMethods.includes('email')) {
      console.log('📧 Email notifications would be sent here');
      // TODO: Implement email notification logic
    }

    if (notificationMethods.includes('browserPush')) {
      console.log('🔔 Browser push notifications would be sent here');
      // TODO: Implement browser push notification logic
    }
  }

  /**
   * Execute deactivate event
   */
  executeDeactivateEvent(adType, adConfig, currentConfig) {
    console.log(`🔄 Deactivating expired ad: ${adType}`);
    
    // Update the ad configuration
    currentConfig.adsManager[adType].active = false;
    
    // Save to localStorage
    localStorage.setItem('cataloro_site_config', JSON.stringify(currentConfig));
    
    // Dispatch update event for UI components
    window.dispatchEvent(new CustomEvent('adsConfigUpdated', { 
      detail: currentConfig.adsManager 
    }));
    
    console.log(`✅ Ad ${adType} has been deactivated`);
  }

  /**
   * Execute reset event
   */
  executeResetEvent(adType, adConfig, currentConfig) {
    console.log(`🔄 Auto-resetting duration for ad: ${adType}`);
    
    const now = new Date().toISOString();
    const originalRuntime = adConfig.runtime;
    const newExpirationDate = this.calculateExpirationDate(now, originalRuntime);
    
    // Update the ad configuration
    currentConfig.adsManager[adType].startDate = now;
    currentConfig.adsManager[adType].expirationDate = newExpirationDate;
    currentConfig.adsManager[adType].active = true;
    
    // Save to localStorage
    localStorage.setItem('cataloro_site_config', JSON.stringify(currentConfig));
    
    // Remove this expiration from processed set so it can expire again
    const oldExpirationKey = `${adType}_${adConfig.expirationDate}`;
    this.processedExpirations.delete(oldExpirationKey);
    
    // Send restart notifications if configured
    this.sendRestartNotifications(adType, currentConfig.adsManager[adType], originalRuntime, newExpirationDate);
    
    // Dispatch update event for UI components
    window.dispatchEvent(new CustomEvent('adsConfigUpdated', { 
      detail: currentConfig.adsManager 
    }));
    
    console.log(`✅ Ad ${adType} has been automatically reset until ${new Date(newExpirationDate).toLocaleString()}`);
  }

  /**
   * Send restart notifications for reset ads
   */
  async sendRestartNotifications(adType, adConfig, originalRuntime, newExpirationDate) {
    const selectedUsers = adConfig.notificationUsers || [];
    const notificationMethods = adConfig.notificationMethods || [];
    
    if (notificationMethods.includes('notificationCenter') && selectedUsers.length > 0) {
      console.log(`🔄 Sending ad restart notifications to ${selectedUsers.length} users (auto-reset)`);
      
      const restartPromises = selectedUsers.map(async (user) => {
        try {
          const adDescription = adConfig.description || adType;
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/user/${user.id}/notifications`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              title: '🔄 Advertisement Restarted',
              message: `Advertisement "${adDescription}" has automatically restarted with a new ${originalRuntime} duration until ${new Date(newExpirationDate).toLocaleString()}`,
              type: 'info'
            })
          });
          
          if (response.ok) {
            console.log(`✅ Ad restart notification sent to user ${user.email} (${user.id})`);
            return { success: true, user: user.email };
          } else {
            console.error(`❌ Failed to send ad restart notification to user ${user.email}`);
            return { success: false, user: user.email, error: 'HTTP Error' };
          }
        } catch (error) {
          console.error(`❌ Error sending ad restart notification to user ${user.email}:`, error);
          return { success: false, user: user.email, error: error.message };
        }
      });
      
      try {
        const results = await Promise.all(restartPromises);
        const successCount = results.filter(r => r.success).length;
        console.log(`📊 Ad restart notifications: ${successCount}/${selectedUsers.length} sent successfully`);
      } catch (error) {
        console.error('❌ Error in batch restart notification sending:', error);
      }
    }
  }

  /**
   * Calculate expiration date from start date and runtime
   */
  calculateExpirationDate(startDate, runtime) {
    const start = new Date(startDate);
    
    // Parse runtime format (e.g., "2 weeks", "1 month", "3 days")
    const [amount, unit] = runtime.split(' ');
    const numAmount = parseInt(amount);
    
    switch (unit.toLowerCase()) {
      case 'minute':
      case 'minutes':
        return new Date(start.getTime() + numAmount * 60 * 1000).toISOString();
      case 'hour':
      case 'hours':
        return new Date(start.getTime() + numAmount * 60 * 60 * 1000).toISOString();
      case 'day':
      case 'days':
        return new Date(start.getTime() + numAmount * 24 * 60 * 60 * 1000).toISOString();
      case 'week':
      case 'weeks':
        return new Date(start.getTime() + numAmount * 7 * 24 * 60 * 60 * 1000).toISOString();
      case 'month':
      case 'months':
        const newDate = new Date(start);
        newDate.setMonth(newDate.getMonth() + numAmount);
        return newDate.toISOString();
      default:
        console.warn(`Unknown runtime unit: ${unit}, defaulting to 1 month`);
        const defaultDate = new Date(start);
        defaultDate.setMonth(defaultDate.getMonth() + 1);
        return defaultDate.toISOString();
    }
  }

  /**
   * Clean up processed expirations older than 24 hours
   */
  cleanupProcessedExpirations() {
    // This could be enhanced to remove old entries from processedExpirations
    // For now, we keep it simple
    console.log('🧹 Cleaning up old expiration records');
  }
}

// Create singleton instance
const adsExpirationService = new AdsExpirationService();

export default adsExpirationService;