/**
 * CATALORO - Edit Side Menu Dashboard with Drag-and-Drop
 * Advanced menu management with reordering and customization
 */

import React, { useState, useEffect } from 'react';
import { 
  Menu,
  GripVertical,
  Plus,
  Edit3,
  Trash2,
  Eye,
  EyeOff,
  Save,
  RotateCcw,
  Settings,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Home,
  Package,
  Users,
  MessageCircle,
  Heart,
  User,
  ShoppingCart,
  BarChart3,
  Shield,
  Target,
  Database,
  Building,
  Zap,
  Globe,
  DollarSign,
  Star,
  Bell,
  Search,
  Filter,
  Download,
  Upload,
  Palette,
  BookOpen,
  Layers,
  GitBranch,
  Monitor,
  Smartphone,
  Code,
  Server,
  Wifi,
  Lock,
  Mail,
  Calendar,
  Camera,
  Image,
  Video,
  Music,
  FileText,
  Folder,
  Archive,
  Link,
  Tag,
  Flag,
  Award,
  Trophy,
  Crown,
  Gem,
  Rocket,
  Lightning,
  Fire,
  Sun,
  Moon,
  Cloud,
  Umbrella,
  Mountain,
  Store
} from 'lucide-react';
import { useNotifications } from '../../context/NotificationContext';
import usePermissions from '../../hooks/usePermissions';
import { APP_ROUTES } from '../../config/directions';

// Available icons for menu items
const availableIcons = {
  Home, Package, Users, MessageCircle, Heart, User, ShoppingCart, BarChart3, Shield, Target,
  Database, Building, Zap, Globe, DollarSign, Star, Bell, Search, Filter, Download, Upload,
  Palette, BookOpen, Layers, GitBranch, Monitor, Smartphone, Code, Server, Wifi, Lock,
  Mail, Calendar, Camera, Image, Video, Music, FileText, Folder, Archive, Link, Tag,
  Flag, Award, Trophy, Crown, Gem, Rocket, Lightning, Fire, Sun, Moon, Cloud, Umbrella, Mountain
};

// Default menu structure
const defaultMenuItems = [
  { id: 'browse', label: 'Browse', icon: 'Package', path: '/browse', visible: true, type: 'page' },
  { id: 'messages', label: 'Messages', icon: 'MessageCircle', path: '/messages', visible: true, type: 'page' },
  { id: 'favorites', label: 'Favorites', icon: 'Heart', path: '/favorites', visible: true, type: 'page' },
  { id: 'profile', label: 'Profile', icon: 'User', path: '/profile', visible: true, type: 'page' },
  { id: 'inventory', label: 'Inventory', icon: 'ShoppingCart', path: '/inventory', visible: true, type: 'page' },
  { id: 'deals', label: 'Deals', icon: 'DollarSign', path: '/deals', visible: true, type: 'page' },
  { id: 'notifications', label: 'Notifications', icon: 'Bell', path: '/notifications', visible: true, type: 'page' }
];

function EditSideMenuDashboard() {
  const { showToast } = useNotifications();
  const [menuItems, setMenuItems] = useState(defaultMenuItems);
  const [draggedItem, setDraggedItem] = useState(null);
  const [dragOverIndex, setDragOverIndex] = useState(null);
  const [editingItem, setEditingItem] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [selectedIcon, setSelectedIcon] = useState('Package');
  const [expandedSections, setExpandedSections] = useState({
    visible: true,
    hidden: false,
    custom: false
  });

  useEffect(() => {
    loadMenuConfiguration();
  }, []);

  const loadMenuConfiguration = () => {
    try {
      const savedMenu = localStorage.getItem('cataloro_side_menu');
      if (savedMenu) {
        const parsedMenu = JSON.parse(savedMenu);
        setMenuItems(parsedMenu);
      }
    } catch (error) {
      console.error('Failed to load menu configuration:', error);
      showToast('Failed to load menu configuration', 'error');
    }
  };

  const saveMenuConfiguration = () => {
    try {
      localStorage.setItem('cataloro_side_menu', JSON.stringify(menuItems));
      setHasChanges(false);
      showToast('Menu configuration saved successfully!', 'success');
      
      // Trigger event for other components to update
      window.dispatchEvent(new CustomEvent('menuConfigUpdated', {
        detail: menuItems
      }));
    } catch (error) {
      console.error('Failed to save menu configuration:', error);
      showToast('Failed to save menu configuration', 'error');
    }
  };

  const resetToDefault = () => {
    if (window.confirm('Are you sure you want to reset the menu to default configuration? This will undo all customizations.')) {
      setMenuItems(defaultMenuItems);
      setHasChanges(true);
      showToast('Menu reset to default configuration', 'info');
    }
  };

  // Drag and Drop Functions
  const handleDragStart = (e, item, index) => {
    setDraggedItem(item);
    e.dataTransfer.effectAllowed = 'move';
    e.target.style.opacity = '0.5';
  };

  const handleDragEnd = (e) => {
    e.target.style.opacity = '1';
    setDraggedItem(null);
    setDragOverIndex(null);
  };

  const handleDragOver = (e, index) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverIndex(index);
  };

  const handleDrop = (e, dropIndex) => {
    e.preventDefault();
    
    if (!draggedItem) return;
    
    const dragIndex = menuItems.findIndex(item => item.id === draggedItem.id);
    if (dragIndex === dropIndex) return;
    
    const newMenuItems = [...menuItems];
    const [removed] = newMenuItems.splice(dragIndex, 1);
    newMenuItems.splice(dropIndex, 0, removed);
    
    setMenuItems(newMenuItems);
    setHasChanges(true);
    setDragOverIndex(null);
  };

  const toggleVisibility = (itemId) => {
    setMenuItems(items =>
      items.map(item =>
        item.id === itemId ? { ...item, visible: !item.visible } : item
      )
    );
    setHasChanges(true);
  };

  const deleteMenuItem = (itemId) => {
    if (window.confirm('Are you sure you want to delete this menu item?')) {
      setMenuItems(items => items.filter(item => item.id !== itemId));
      setHasChanges(true);
      showToast('Menu item deleted', 'info');
    }
  };

  const addMenuItem = (newItem) => {
    const menuItem = {
      id: `custom_${Date.now()}`,
      label: newItem.label,
      icon: newItem.icon,
      path: newItem.path,
      visible: true,
      type: 'custom'
    };
    
    setMenuItems(items => [...items, menuItem]);
    setHasChanges(true);
    setShowAddModal(false);
    showToast('Menu item added successfully', 'success');
  };

  const updateMenuItem = (itemId, updates) => {
    setMenuItems(items =>
      items.map(item =>
        item.id === itemId ? { ...item, ...updates } : item
      )
    );
    setHasChanges(true);
    setEditingItem(null);
  };

  const getIconComponent = (iconName) => {
    const IconComponent = availableIcons[iconName] || Package;
    return IconComponent;
  };

  const visibleItems = menuItems.filter(item => item.visible);
  const hiddenItems = menuItems.filter(item => !item.visible);
  const customItems = menuItems.filter(item => item.type === 'custom');

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2 flex items-center">
              <Menu className="w-8 h-8 mr-3" />
              Edit Side Menu
            </h1>
            <p className="text-indigo-100">Customize navigation menu with drag-and-drop functionality</p>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="bg-white/20 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold">{visibleItems.length}</div>
              <div className="text-sm text-indigo-100">Visible</div>
            </div>
            <div className="bg-white/20 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold">{hiddenItems.length}</div>
              <div className="text-sm text-indigo-100">Hidden</div>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Add Item</span>
          </button>
          
          <button
            onClick={resetToDefault}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center space-x-2"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset to Default</span>
          </button>
        </div>
        
        <div className="flex items-center space-x-4">
          {hasChanges && (
            <span className="text-sm text-amber-600 dark:text-amber-400 flex items-center">
              <Settings className="w-4 h-4 mr-1" />
              Unsaved changes
            </span>
          )}
          
          <button
            onClick={saveMenuConfiguration}
            disabled={!hasChanges}
            className={`px-6 py-2 rounded-lg font-medium transition-all duration-200 ${
              hasChanges
                ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg hover:shadow-xl'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            } flex items-center space-x-2`}
          >
            <Save className="w-4 h-4" />
            <span>Save Changes</span>
          </button>
        </div>
      </div>

      {/* Menu Sections */}
      <div className="space-y-6">
        {/* Visible Items */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setExpandedSections(prev => ({ ...prev, visible: !prev.visible }))}
            className="w-full p-4 flex items-center justify-between text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <Eye className="w-5 h-5 text-green-600" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Visible Menu Items ({visibleItems.length})
              </h2>
            </div>
            {expandedSections.visible ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </button>
          
          {expandedSections.visible && (
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
              {visibleItems.map((item, index) => {
                const IconComponent = getIconComponent(item.icon);
                
                return (
                  <div
                    key={item.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, item, index)}
                    onDragEnd={handleDragEnd}
                    onDragOver={(e) => handleDragOver(e, index)}
                    onDrop={(e) => handleDrop(e, index)}
                    className={`flex items-center space-x-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg cursor-move transition-all duration-200 ${
                      dragOverIndex === index ? 'border-2 border-blue-500 border-dashed' : 'border border-transparent'
                    } hover:shadow-md`}
                  >
                    <GripVertical className="w-4 h-4 text-gray-400" />
                    <IconComponent className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    
                    <div className="flex-1">
                      <span className="font-medium text-gray-900 dark:text-white">{item.label}</span>
                      <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">{item.path}</span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setEditingItem(item)}
                        className="p-1 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                        title="Edit item"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      
                      <button
                        onClick={() => toggleVisibility(item.id)}
                        className="p-1 text-amber-600 hover:text-amber-800 dark:text-amber-400 dark:hover:text-amber-300"
                        title="Hide item"
                      >
                        <EyeOff className="w-4 h-4" />
                      </button>
                      
                      {item.type === 'custom' && (
                        <button
                          onClick={() => deleteMenuItem(item.id)}
                          className="p-1 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                          title="Delete item"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
              
              {visibleItems.length === 0 && (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  <Eye className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No visible menu items</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Hidden Items */}
        {hiddenItems.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setExpandedSections(prev => ({ ...prev, hidden: !prev.hidden }))}
              className="w-full p-4 flex items-center justify-between text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <EyeOff className="w-5 h-5 text-gray-500" />
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Hidden Menu Items ({hiddenItems.length})
                </h2>
              </div>
              {expandedSections.hidden ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </button>
            
            {expandedSections.hidden && (
              <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
                {hiddenItems.map((item) => {
                  const IconComponent = getIconComponent(item.icon);
                  
                  return (
                    <div
                      key={item.id}
                      className="flex items-center space-x-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg opacity-60"
                    >
                      <IconComponent className="w-5 h-5 text-gray-400" />
                      
                      <div className="flex-1">
                        <span className="font-medium text-gray-700 dark:text-gray-300">{item.label}</span>
                        <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">{item.path}</span>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => setEditingItem(item)}
                          className="p-1 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                          title="Edit item"
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>
                        
                        <button
                          onClick={() => toggleVisibility(item.id)}
                          className="p-1 text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300"
                          title="Show item"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        
                        {item.type === 'custom' && (
                          <button
                            onClick={() => deleteMenuItem(item.id)}
                            className="p-1 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                            title="Delete item"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Add New Item Modal */}
      {showAddModal && (
        <AddMenuItemModal
          onClose={() => setShowAddModal(false)}
          onAdd={addMenuItem}
          availableIcons={availableIcons}
        />
      )}

      {/* Edit Item Modal */}
      {editingItem && (
        <EditMenuItemModal
          item={editingItem}
          onClose={() => setEditingItem(null)}
          onUpdate={updateMenuItem}
          availableIcons={availableIcons}
        />
      )}
    </div>
  );
}

// Add Menu Item Modal
function AddMenuItemModal({ onClose, onAdd, availableIcons }) {
  const [formData, setFormData] = useState({
    label: '',
    icon: 'Package',
    path: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.label.trim() || !formData.path.trim()) {
      return;
    }
    
    onAdd(formData);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md mx-4 shadow-2xl">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Add New Menu Item</h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Label
            </label>
            <input
              type="text"
              value={formData.label}
              onChange={(e) => setFormData(prev => ({ ...prev, label: e.target.value }))}
              placeholder="Menu item label"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Path
            </label>
            <input
              type="text"
              value={formData.path}
              onChange={(e) => setFormData(prev => ({ ...prev, path: e.target.value }))}
              placeholder="/custom-page"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Icon
            </label>
            <select
              value={formData.icon}
              onChange={(e) => setFormData(prev => ({ ...prev, icon: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              {Object.keys(availableIcons).map(iconName => (
                <option key={iconName} value={iconName}>{iconName}</option>
              ))}
            </select>
          </div>
          
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Add Item
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Edit Menu Item Modal
function EditMenuItemModal({ item, onClose, onUpdate, availableIcons }) {
  const [formData, setFormData] = useState({
    label: item.label,
    icon: item.icon,
    path: item.path
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.label.trim() || !formData.path.trim()) {
      return;
    }
    
    onUpdate(item.id, formData);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-full max-w-md mx-4 shadow-2xl">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Edit Menu Item</h3>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Label
            </label>
            <input
              type="text"
              value={formData.label}
              onChange={(e) => setFormData(prev => ({ ...prev, label: e.target.value }))}
              placeholder="Menu item label"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Path
            </label>
            <input
              type="text"
              value={formData.path}
              onChange={(e) => setFormData(prev => ({ ...prev, path: e.target.value }))}
              placeholder="/custom-page"
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Icon
            </label>
            <select
              value={formData.icon}
              onChange={(e) => setFormData(prev => ({ ...prev, icon: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              {Object.keys(availableIcons).map(iconName => (
                <option key={iconName} value={iconName}>{iconName}</option>
              ))}
            </select>
          </div>
          
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Update Item
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EditSideMenuDashboard;