/**
 * CATALORO - Menu Settings Management
 * Admin interface for controlling menu visibility and user permissions
 */

import React, { useState, useEffect } from 'react';
import { 
  Save, 
  RotateCcw, 
  Monitor, 
  Smartphone, 
  Eye, 
  EyeOff,
  Users,
  Settings,
  Shield,
  User,
  UserCheck,
  ShoppingCart,
  Store,
  MessageCircle,
  Package,
  DollarSign,
  Plus,
  Heart,
  BarChart3,
  Globe,
  RefreshCw
} from 'lucide-react';
import { useNotifications } from '../../context/NotificationContext';

const ROLE_COLORS = {
  admin: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
  manager: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  seller: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  buyer: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300'
};

const MENU_ICONS = {
  about: Globe,
  browse: Store,
  create_listing: Plus,
  create: Plus,
  messages: MessageCircle,
  tenders: DollarSign,
  profile: User,
  admin_panel: Shield,
  buy_management: ShoppingCart,
  my_listings: Package,
  listings: Package,
  favorites: Heart,
  admin_drawer: BarChart3
};

const MENU_LABELS = {
  about: 'About',
  browse: 'Browse',
  create_listing: 'Create Listing',
  create: 'Create',
  messages: 'Messages',
  tenders: 'Tenders',
  profile: 'Profile',
  admin_panel: 'Admin Panel',
  buy_management: 'Buy Management',
  my_listings: 'My Listings',
  listings: 'Listings',
  favorites: 'Favorites',
  admin_drawer: 'Admin Drawer'
};

function MenuSettings() {
  const { showToast } = useNotifications();
  const [settings, setSettings] = useState({
    desktop_menu: {},
    mobile_menu: {}
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    loadMenuSettings();
  }, []);

  const loadMenuSettings = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'https://market-guardian.preview.emergentagent.com'}/api/admin/menu-settings`);
      if (response.ok) {
        const data = await response.json();
        setSettings(data);
      } else {
        throw new Error('Failed to load menu settings');
      }
    } catch (error) {
      console.error('Error loading menu settings:', error);
      showToast('Failed to load menu settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  const saveMenuSettings = async () => {
    try {
      setSaving(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'https://market-guardian.preview.emergentagent.com'}/api/admin/menu-settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        showToast('Menu settings saved successfully', 'success');
        setHasChanges(false);
      } else {
        throw new Error('Failed to save menu settings');
      }
    } catch (error) {
      console.error('Error saving menu settings:', error);
      showToast('Failed to save menu settings', 'error');
    } finally {
      setSaving(false);
    }
  };

  const toggleMenuItemEnabled = (menuType, itemKey) => {
    setSettings(prev => ({
      ...prev,
      [menuType]: {
        ...prev[menuType],
        [itemKey]: {
          ...prev[menuType][itemKey],
          enabled: !prev[menuType][itemKey]?.enabled
        }
      }
    }));
    setHasChanges(true);
  };

  const toggleUserRole = (menuType, itemKey, role) => {
    setSettings(prev => {
      const currentRoles = prev[menuType][itemKey]?.roles || [];
      const newRoles = currentRoles.includes(role)
        ? currentRoles.filter(r => r !== role)
        : [...currentRoles, role];

      return {
        ...prev,
        [menuType]: {
          ...prev[menuType],
          [itemKey]: {
            ...prev[menuType][itemKey],
            roles: newRoles
          }
        }
      };
    });
    setHasChanges(true);
  };

  const resetToDefault = () => {
    if (window.confirm('Are you sure you want to reset all menu settings to default? This will overwrite all current settings.')) {
      loadMenuSettings();
      setHasChanges(false);
      showToast('Menu settings reset to default', 'info');
    }
  };

  const renderMenuSection = (menuType, title, icon) => {
    const IconComponent = icon;
    const menuItems = settings[menuType] || {};

    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center mb-6">
          <div className="bg-blue-100 dark:bg-blue-900/30 p-2 rounded-lg mr-3">
            <IconComponent className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
        </div>

        <div className="space-y-4">
          {Object.entries(menuItems).map(([itemKey, itemConfig]) => {
            const ItemIcon = MENU_ICONS[itemKey] || Settings;
            const itemLabel = MENU_LABELS[itemKey] || itemKey;
            const isEnabled = itemConfig?.enabled !== false;
            const userRoles = itemConfig?.roles || [];

            return (
              <div key={itemKey} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <ItemIcon className="w-5 h-5 text-gray-600 dark:text-gray-400 mr-3" />
                    <span className="font-medium text-gray-900 dark:text-white">{itemLabel}</span>
                  </div>
                  
                  <button
                    onClick={() => toggleMenuItemEnabled(menuType, itemKey)}
                    className={`flex items-center px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      isEnabled
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                        : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                    }`}
                  >
                    {isEnabled ? (
                      <>
                        <Eye className="w-4 h-4 mr-1" />
                        Visible
                      </>
                    ) : (
                      <>
                        <EyeOff className="w-4 h-4 mr-1" />
                        Hidden
                      </>
                    )}
                  </button>
                </div>

                <div className="ml-8">
                  <div className="flex items-center mb-2">
                    <Users className="w-4 h-4 text-gray-500 mr-2" />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Allowed User Roles:
                    </span>
                  </div>
                  
                  <div className="flex flex-wrap gap-2">
                    {['admin', 'manager', 'seller', 'buyer'].map(role => (
                      <button
                        key={role}
                        onClick={() => toggleUserRole(menuType, itemKey, role)}
                        className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                          userRoles.includes(role)
                            ? ROLE_COLORS[role]
                            : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                        }`}
                      >
                        {userRoles.includes(role) && <UserCheck className="w-3 h-3 inline mr-1" />}
                        {role.charAt(0).toUpperCase() + role.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Menu Settings</h2>
            <p className="text-gray-600 dark:text-gray-400">Configure menu visibility and user permissions</p>
          </div>
        </div>
        
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Menu Settings</h2>
          <p className="text-gray-600 dark:text-gray-400">Configure menu visibility and user permissions</p>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={resetToDefault}
            className="flex items-center px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg transition-colors"
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset to Default
          </button>
          
          <button
            onClick={saveMenuSettings}
            disabled={!hasChanges || saving}
            className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
              hasChanges && !saving
                ? 'bg-blue-600 text-white'
                : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
            }`}
          >
            {saving ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </>
            )}
          </button>
        </div>
      </div>

      {/* Changes indicator */}
      {hasChanges && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <div className="flex items-center">
            <Settings className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mr-2" />
            <span className="text-yellow-800 dark:text-yellow-200 font-medium">
              You have unsaved changes. Don't forget to save your settings.
            </span>
          </div>
        </div>
      )}

      {/* Menu Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderMenuSection('desktop_menu', 'Desktop Menu', Monitor)}
        {renderMenuSection('mobile_menu', 'Mobile Menu', Smartphone)}
      </div>

      {/* Role Legend */}
      <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-6">
        <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">User Role Legend</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(ROLE_COLORS).map(([role, colorClass]) => (
            <div key={role} className="flex items-center">
              <div className={`px-3 py-1 rounded-full text-xs font-medium ${colorClass} mr-2`}>
                {role.charAt(0).toUpperCase() + role.slice(1)}
              </div>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {role === 'admin' && 'Full system access'}
                {role === 'manager' && 'Management access'}
                {role === 'seller' && 'Can sell items'}
                {role === 'buyer' && 'Can buy items'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default MenuSettings;