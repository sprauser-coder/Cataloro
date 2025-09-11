/**
 * CATALORO - Menu Settings Hook
 * Custom hook for fetching and managing menu visibility settings
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

export function useMenuSettings() {
  const { user } = useAuth();
  const [menuSettings, setMenuSettings] = useState({
    desktop_menu: {},
    mobile_menu: {},
    user_role: 'buyer'
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.id) {
      fetchUserMenuSettings(user.id);
    } else {
      setLoading(false);
    }
  }, [user]);

  const fetchUserMenuSettings = async (userId) => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/menu-settings/user/${userId}`);
      
      if (response.ok) {
        const data = await response.json();
        setMenuSettings(data);
      } else {
        // Use default settings if API fails
        setMenuSettings({
          desktop_menu: {},
          mobile_menu: {},
          user_role: user?.role || 'buyer'
        });
      }
    } catch (error) {
      console.error('Error fetching menu settings:', error);
      // Use default settings on error
      setMenuSettings({
        desktop_menu: {},
        mobile_menu: {},
        user_role: user?.role || 'buyer'
      });
    } finally {
      setLoading(false);
    }
  };

  const isMenuItemVisible = (menuType, itemKey) => {
    if (loading) {
      console.log(`🔄 Menu loading, showing ${itemKey} by default`);
      return true; // Show items while loading
    }
    
    const menuSection = menuSettings[menuType];
    
    // If no menu section found, don't show anything
    if (!menuSection) {
      console.log(`❌ No menu section found for ${menuType}, hiding ${itemKey}`);
      return false;
    }
    
    const menuItem = menuSection[itemKey];
    
    // If item is not in the filtered settings from backend, it should be hidden
    if (!menuItem) {
      console.log(`❌ Item ${itemKey} not in filtered settings for ${menuType}, hiding`);
      return false;
    }
    
    // Item exists in settings, so it's enabled and user has permission
    console.log(`✅ Item ${itemKey} found in ${menuType} settings, showing`);
    return true;
  };

  const getVisibleMenuItems = (menuType, allItems) => {
    if (loading) return allItems; // Show all items while loading
    
    return allItems.filter(item => {
      const itemKey = item.key || item.id || item.path?.replace('/', '');
      return isMenuItemVisible(menuType, itemKey);
    });
  };

  return {
    menuSettings,
    loading,
    isMenuItemVisible,
    getVisibleMenuItems,
    refreshSettings: () => user?.id && fetchUserMenuSettings(user.id)
  };
}

export default useMenuSettings;