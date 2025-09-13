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
    // During loading, hide items to prevent showing disabled items
    if (loading) return false;
    
    const menuSection = menuSettings[menuType];
    
    // If no menu section found, fallback to minimal default behavior
    // This happens when user is not logged in or API completely fails
    if (!menuSection) {
      // For unauthenticated users, show only browse
      const publicItems = ['browse'];
      // For authenticated users, show minimal set + new menu items
      const authenticatedItems = ['browse', 'buy', 'sell'];
      return user ? authenticatedItems.includes(itemKey) : publicItems.includes(itemKey);
    }
    
    const menuItem = menuSection[itemKey];
    
    // If item is not in the settings, show default items for new menu items only
    // This provides fallback for new menu items like buy/sell that might not be in backend settings yet
    if (!menuItem) {
      // Only show new items (buy/sell) that might not be configured yet
      // Traditional items should be explicitly configured in admin settings
      const newMenuItems = ['buy', 'sell'];
      return newMenuItems.includes(itemKey);
    }
    
    // Check if item is explicitly enabled
    // Use 'enabled' property from backend API
    return menuItem.enabled === true;
  };

  const getVisibleMenuItems = (menuType, allItems) => {
    // During loading, hide items to prevent showing disabled items
    if (loading) return [];
    
    return allItems.filter(item => {
      const itemKey = item.key || item.id || item.path?.replace('/', '');
      return isMenuItemVisible(menuType, itemKey);
    });
  };

  const getCustomMenuItems = (menuType) => {
    if (loading) return [];
    
    const customItems = menuSettings[menuType]?.custom_items || [];
    return customItems
      .filter(item => item.enabled !== false)
      .sort((a, b) => (a.position || 0) - (b.position || 0));
  };

  return {
    menuSettings,
    loading,
    isMenuItemVisible,
    getVisibleMenuItems,
    getCustomMenuItems,
    refreshSettings: () => user?.id && fetchUserMenuSettings(user.id)
  };
}

export default useMenuSettings;