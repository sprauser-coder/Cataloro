/**
 * CATALORO - Menu Settings Component
 * Admin interface for managing navigation menu items and custom items
 */

import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { Plus, Edit, Trash2, GripVertical, Eye, EyeOff, Monitor, Smartphone } from 'lucide-react';
import CustomMenuItemForm from './CustomMenuItemForm';
import NotificationToast from '../ui/NotificationToast';

const MenuSettings = () => {
  const [settings, setSettings] = useState({ desktop_menu: {}, mobile_menu: {} });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');
  
  // Custom item form state
  const [showCustomForm, setShowCustomForm] = useState(false);
  const [editingCustomItem, setEditingCustomItem] = useState(null);
  const [editingMenuType, setEditingMenuType] = useState('desktop_menu');
  const [availablePages, setAvailablePages] = useState([]);
  const [availableIcons, setAvailableIcons] = useState([]);

  useEffect(() => {
    loadMenuSettings();
    loadAvailablePages();
    loadAvailableIcons();
  }, []);

  const showToastMessage = (message, type = 'success') => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  const loadMenuSettings = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('cataloro_token');
      const headers = {
        'Content-Type': 'application/json'
      };
      
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/menu-settings`, {
        headers
      });
      
      if (response.ok) {
        const data = await response.json();
        setSettings(data);
      } else if (response.status === 401 || response.status === 403) {
        showToastMessage('Access denied. Admin privileges required.', 'error');
      } else {
        throw new Error(`Failed to load menu settings: ${response.status}`);
      }
    } catch (error) {
      console.error('Error loading menu settings:', error);
      showToastMessage('Failed to load menu settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadAvailablePages = async () => {
    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/available-pages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setAvailablePages(data.available_pages);
      }
    } catch (error) {
      console.error('Error loading available pages:', error);
    }
  };

  const loadAvailableIcons = async () => {
    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/available-icons`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setAvailableIcons(data.available_icons);
      }
    } catch (error) {
      console.error('Error loading available icons:', error);
    }
  };

  const saveMenuSettings = async () => {
    try {
      setSaving(true);
      const token = localStorage.getItem('cataloro_token');
      const headers = {
        'Content-Type': 'application/json'
      };
      
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/menu-settings`, {
        method: 'POST',
        headers,
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        showToastMessage('Menu settings saved successfully', 'success');
        setHasChanges(false);
      } else if (response.status === 401 || response.status === 403) {
        showToastMessage('Access denied. Admin privileges required.', 'error');
      } else {
        throw new Error(`Failed to save menu settings: ${response.status}`);
      }
    } catch (error) {
      console.error('Error saving menu settings:', error);
      showToastMessage('Failed to save menu settings', 'error');
    } finally {
      setSaving(false);
    }
  };

  const toggleItemVisibility = (menuType, itemKey) => {
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

  const toggleRoleAccess = (menuType, itemKey, role) => {
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

  const handleCustomItemSave = (customItem) => {
    setSettings(prev => {
      const menuType = editingMenuType;
      const customItems = prev[menuType]?.custom_items || [];
      
      let updatedCustomItems;
      if (editingCustomItem) {
        // Update existing item
        updatedCustomItems = customItems.map(item => 
          item.id === editingCustomItem.id ? customItem : item
        );
      } else {
        // Add new item
        updatedCustomItems = [...customItems, customItem];
      }
      
      return {
        ...prev,
        [menuType]: {
          ...prev[menuType],
          custom_items: updatedCustomItems
        }
      };
    });
    
    setHasChanges(true);
    setShowCustomForm(false);
    setEditingCustomItem(null);
    showToastMessage(
      editingCustomItem ? 'Custom menu item updated!' : 'Custom menu item added!', 
      'success'
    );
  };

  const deleteCustomItem = (menuType, customItemId) => {
    if (!window.confirm('Are you sure you want to delete this custom menu item?')) return;
    
    setSettings(prev => ({
      ...prev,
      [menuType]: {
        ...prev[menuType],
        custom_items: (prev[menuType]?.custom_items || []).filter(item => item.id !== customItemId)
      }
    }));
    
    setHasChanges(true);
    showToastMessage('Custom menu item deleted', 'success');
  };

  const onDragEnd = (result) => {
    if (!result.destination) return;

    const { source, destination, type } = result;
    
    if (type === 'CUSTOM_ITEMS') {
      const menuType = source.droppableId;
      const customItems = [...(settings[menuType]?.custom_items || [])];
      const [removed] = customItems.splice(source.index, 1);
      customItems.splice(destination.index, 0, removed);

      // Update positions based on new order
      const updatedItems = customItems.map((item, index) => ({
        ...item,
        position: index
      }));

      setSettings(prev => ({
        ...prev,
        [menuType]: {
          ...prev[menuType],
          custom_items: updatedItems
        }
      }));

      setHasChanges(true);
    }
  };

  const renderMenuSection = (menuType, title, icon) => {
    const menuData = settings[menuType] || {};
    const customItems = menuData.custom_items || [];
    
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {icon}
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {title}
              </h3>
            </div>
            <button
              onClick={() => {
                setEditingMenuType(menuType);
                setShowCustomForm(true);
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add Custom Item</span>
            </button>
          </div>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Existing Menu Items */}
          <div>
            <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
              Default Menu Items
            </h4>
            <div className="space-y-3">
              {Object.entries(menuData).map(([key, item]) => {
                if (key === 'custom_items') return null;
                
                return (
                  <div key={key} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {item.label || key}
                      </span>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        item.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {item.enabled ? 'Visible' : 'Hidden'}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => toggleItemVisibility(menuType, key)}
                        className={`p-2 rounded-lg transition-colors ${
                          item.enabled 
                            ? 'text-green-600 hover:bg-green-100' 
                            : 'text-red-600 hover:bg-red-100'
                        }`}
                        title={item.enabled ? 'Hide item' : 'Show item'}
                      >
                        {item.enabled ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                      </button>
                      
                      <div className="flex space-x-1">
                        {['admin', 'manager', 'seller', 'buyer'].map(role => (
                          <button
                            key={role}
                            onClick={() => toggleRoleAccess(menuType, key, role)}
                            className={`px-2 py-1 text-xs rounded ${
                              (item.roles || []).includes(role)
                                ? 'bg-gray-300 text-gray-700'
                                : 'bg-gray-200 text-gray-600'
                            }`}
                            title={`Toggle ${role} access`}
                          >
                            {role.charAt(0).toUpperCase()}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Custom Menu Items */}
          {customItems.length > 0 && (
            <div>
              <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
                Custom Menu Items
              </h4>
              <DragDropContext onDragEnd={onDragEnd}>
                <Droppable droppableId={menuType} type="CUSTOM_ITEMS">
                  {(provided) => (
                    <div
                      {...provided.droppableProps}
                      ref={provided.innerRef}
                      className="space-y-3"
                    >
                      {customItems.map((item, index) => (
                        <Draggable key={item.id} draggableId={item.id} index={index}>
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              className={`p-4 bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500 rounded-lg ${
                                snapshot.isDragging ? 'shadow-lg' : ''
                              }`}
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                  <div {...provided.dragHandleProps} className="text-gray-400 hover:text-gray-600 cursor-move">
                                    <GripVertical className="w-4 h-4" />
                                  </div>
                                  <div>
                                    <div className="flex items-center space-x-2">
                                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                                        {item.label}
                                      </span>
                                      <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded">
                                        {item.type === 'custom_url' ? 'External' : 'Internal'}
                                      </span>
                                      <span className={`px-2 py-1 text-xs rounded-full ${
                                        item.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                      }`}>
                                        {item.enabled ? 'Visible' : 'Hidden'}
                                      </span>
                                    </div>
                                    <div className="text-xs text-gray-500 mt-1">
                                      {item.url} | Position: {item.position || 0}
                                    </div>
                                  </div>
                                </div>
                                
                                <div className="flex items-center space-x-2">
                                  <button
                                    onClick={() => {
                                      setEditingCustomItem(item);
                                      setEditingMenuType(menuType);
                                      setShowCustomForm(true);
                                    }}
                                    className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors"
                                    title="Edit item"
                                  >
                                    <Edit className="w-4 h-4" />
                                  </button>
                                  
                                  <button
                                    onClick={() => deleteCustomItem(menuType, item.id)}
                                    className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                                    title="Delete item"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                </div>
                              </div>
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>
              </DragDropContext>
            </div>
          )}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-600 dark:text-gray-400">Loading menu settings...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Menu Settings</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage navigation menu items and add custom links
          </p>
        </div>
        
        {hasChanges && (
          <div className="flex space-x-3">
            <button
              onClick={() => {
                setSettings({ desktop_menu: {}, mobile_menu: {} });
                setHasChanges(false);
                loadMenuSettings();
              }}
              className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
            >
              Reset Changes
            </button>
            <button
              onClick={saveMenuSettings}
              disabled={saving}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        )}
      </div>

      {/* Menu Sections */}
      <div className="space-y-8">
        {renderMenuSection('desktop_menu', 'Desktop Menu', <Monitor className="w-5 h-5 text-gray-600" />)}
        {renderMenuSection('mobile_menu', 'Mobile Menu', <Smartphone className="w-5 h-5 text-gray-600" />)}
      </div>

      {/* Custom Menu Item Form */}
      <CustomMenuItemForm
        isOpen={showCustomForm}
        onClose={() => {
          setShowCustomForm(false);
          setEditingCustomItem(null);
        }}
        onSave={handleCustomItemSave}
        editingItem={editingCustomItem}
        availablePages={availablePages}
        availableIcons={availableIcons}
      />

      {/* Toast Notification */}
      <NotificationToast
        show={showToast}
        message={toastMessage}
        type={toastType}
        onClose={() => setShowToast(false)}
      />
    </div>
  );
};

export default MenuSettings;