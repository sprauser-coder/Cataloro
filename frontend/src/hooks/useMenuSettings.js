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
      const url = `${process.env.REACT_APP_BACKEND_URL}/api/menu-settings/user/${userId}`;
      console.log('🔄 Fetching menu settings for user:', userId, 'URL:', url);
      
      const response = await fetch(url);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Menu settings fetched successfully:', data);
        setMenuSettings(data);
      } else {
        console.log('❌ Menu settings API failed:', response.status, response.statusText);
        // Use default settings if API fails
        setMenuSettings({
          desktop_menu: {},
          mobile_menu: {},
          user_role: user?.role || 'buyer'
        });
      }
    } catch (error) {
      console.error('❌ Error fetching menu settings:', error);
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
    if (loading) {
      console.log(`🔄 Menu loading - hiding ${itemKey}`);
      return false;
    }
    
    const menuSection = menuSettings[menuType];
    
    // If no menu section found, fallback to default behavior
    // This happens when user is not logged in or API fails
    if (!menuSection) {
      console.log(`❌ No menu section for ${menuType} - ${itemKey} fallback to public items`);
      // For unauthenticated users, hide all items except basic ones
      const publicItems = ['browse', 'about'];
      return publicItems.includes(itemKey);
    }
    
    const menuItem = menuSection[itemKey];
    
    // If item is not in the settings, hide it 
    // The backend should return all available items for the user's role
    if (!menuItem) {
      console.log(`❌ No menu item data for ${menuType}.${itemKey} - hiding`);
      return false;
    }
    
    // Check if item is explicitly enabled
    // Use 'enabled' property from backend API
    const isVisible = menuItem.enabled === true;
    console.log(`🔍 Menu visibility check: ${menuType}.${itemKey} = ${isVisible}`, {
      enabled: menuItem.enabled,
      menuItem: menuItem
    });
    
    return isVisible;
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