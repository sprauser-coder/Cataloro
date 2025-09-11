/**
 * CATALORO - Custom Menu Item Form Component
 * Form for adding/editing custom menu items
 */

import React, { useState, useEffect } from 'react';
import { X, Plus, ExternalLink, Monitor } from 'lucide-react';

const CustomMenuItemForm = ({ 
  isOpen, 
  onClose, 
  onSave, 
  editingItem = null,
  availablePages = [],
  availableIcons = []
}) => {
  const [formData, setFormData] = useState({
    id: '',
    label: '',
    url: '',
    icon: 'Star',
    roles: ['admin', 'manager', 'seller', 'buyer'],
    target: '_self',
    position: 0,
    type: 'existing_page',
    enabled: true
  });

  const [isLoadingPages, setIsLoadingPages] = useState(false);
  const [isLoadingIcons, setIsLoadingIcons] = useState(false);

  useEffect(() => {
    if (editingItem) {
      setFormData({ ...editingItem });
    } else {
      setFormData({
        id: `custom_${Date.now()}`,
        label: '',
        url: '',
        icon: 'Star',
        roles: ['admin', 'manager', 'seller', 'buyer'],
        target: '_self',
        position: 0,
        type: 'existing_page',
        enabled: true
      });
    }
  }, [editingItem, isOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.label || !formData.url) {
      alert('Please fill in all required fields');
      return;
    }
    onSave(formData);
  };

  const handleRoleToggle = (role) => {
    setFormData(prev => ({
      ...prev,
      roles: prev.roles.includes(role)
        ? prev.roles.filter(r => r !== role)
        : [...prev.roles, role]
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            {editingItem ? 'Edit Menu Item' : 'Add New Menu Item'}
          </h3>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Item Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Item Type
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center space-x-2">
                <input
                  type="radio"
                  name="type"
                  value="existing_page"
                  checked={formData.type === 'existing_page'}
                  onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value, url: '' }))}
                  className="text-blue-600"
                />
                <Monitor className="w-4 h-4" />
                <span className="text-sm text-gray-700 dark:text-gray-300">Existing App Page</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="radio"
                  name="type"
                  value="custom_url"
                  checked={formData.type === 'custom_url'}
                  onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value, url: '' }))}
                  className="text-blue-600"
                />
                <ExternalLink className="w-4 h-4" />
                <span className="text-sm text-gray-700 dark:text-gray-300">Custom URL</span>
              </label>
            </div>
          </div>

          {/* Label */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Display Label *
            </label>
            <input
              type="text"
              required
              value={formData.label}
              onChange={(e) => setFormData(prev => ({ ...prev, label: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              placeholder="e.g., Help Center, Documentation"
            />
          </div>

          {/* URL/Page Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {formData.type === 'existing_page' ? 'Select Page' : 'URL'} *
            </label>
            {formData.type === 'existing_page' ? (
              <select
                required
                value={formData.url}
                onChange={(e) => {
                  const selectedPage = availablePages.find(p => p.path === e.target.value);
                  setFormData(prev => ({
                    ...prev,
                    url: e.target.value,
                    label: prev.label || selectedPage?.label || '',
                    icon: prev.icon || selectedPage?.icon || 'Star'
                  }));
                }}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="">Select a page...</option>
                {availablePages.map(page => (
                  <option key={page.path} value={page.path}>
                    {page.label} ({page.path})
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="url"
                required
                value={formData.url}
                onChange={(e) => setFormData(prev => ({ ...prev, url: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="https://example.com or /internal-path"
              />
            )}
          </div>

          {/* Icon Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Icon
            </label>
            <select
              value={formData.icon}
              onChange={(e) => setFormData(prev => ({ ...prev, icon: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            >
              {availableIcons.map(icon => (
                <option key={icon} value={icon}>{icon}</option>
              ))}
            </select>
          </div>

          {/* Target */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Open Link
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center space-x-2">
                <input
                  type="radio"
                  name="target"
                  value="_self"
                  checked={formData.target === '_self'}
                  onChange={(e) => setFormData(prev => ({ ...prev, target: e.target.value }))}
                  className="text-blue-600"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">Same Window</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="radio"
                  name="target"
                  value="_blank"
                  checked={formData.target === '_blank'}
                  onChange={(e) => setFormData(prev => ({ ...prev, target: e.target.value }))}
                  className="text-blue-600"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">New Window/Tab</span>
              </label>
            </div>
          </div>

          {/* Position */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Position (Order)
            </label>
            <input
              type="number"
              min="0"
              value={formData.position}
              onChange={(e) => setFormData(prev => ({ ...prev, position: parseInt(e.target.value) || 0 }))}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              placeholder="0 = first, higher number = later in menu"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Lower numbers appear first in the menu. You can also drag-and-drop to reorder.
            </p>
          </div>

          {/* Role Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Visible to Roles
            </label>
            <div className="grid grid-cols-2 gap-3">
              {['admin', 'manager', 'seller', 'buyer'].map(role => (
                <label key={role} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.roles.includes(role)}
                    onChange={() => handleRoleToggle(role)}
                    className="text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">
                    {role}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Enabled Toggle */}
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="enabled"
              checked={formData.enabled}
              onChange={(e) => setFormData(prev => ({ ...prev, enabled: e.target.checked }))}
              className="text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="enabled" className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Enabled (visible in navigation)
            </label>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              {editingItem ? 'Update Item' : 'Add Item'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CustomMenuItemForm;