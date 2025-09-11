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
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'https://cataloro-repair.preview.emergentagent.com'}/api/menu-settings/user/${userId}`);
      
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
    if (loading) return true; // Show items while loading
    
    const menuItem = menuSettings[menuType]?.[itemKey];
    
    // If no settings found, show by default
    if (!menuItem) return true;
    
    // Check if item is enabled and user has permission
    return menuItem.enabled !== false && 
           menuItem.roles?.includes(menuSettings.user_role);
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