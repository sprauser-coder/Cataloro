/**
 * CATALORO - Ads Management Component
 * Complete ads management with inactive-by-default functionality
 */

import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Play, 
  Pause, 
  Target, 
  ExternalLink,
  Eye,
  MousePointer,
  Calendar,
  Users,
  Activity,
  BarChart3
} from 'lucide-react';
import { ENV_CONFIG } from '../../config/directions';

function AdsManagement({ showToast }) {
  const [ads, setAds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingAd, setEditingAd] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    content: '',
    image_url: '',
    link_url: '',
    target_audience: 'all',
    placement: 'banner'
  });

  useEffect(() => {
    fetchAds();
  }, []);

  const fetchAds = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${ENV_CONFIG.API_BASE_URL}/admin/ads`);
      if (response.ok) {
        const adsData = await response.json();
        setAds(adsData);
      } else {
        throw new Error('Failed to fetch ads');
      }
    } catch (error) {
      console.error('Error fetching ads:', error);
      showToast('Failed to load ads', 'error');
    } finally {
      setLoading(false);
    }
  };

  const createAd = async () => {
    try {
      const response = await fetch(`${ENV_CONFIG.API_BASE_URL}/admin/ads`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        showToast('Ad created successfully (inactive by default)', 'success');
        setShowCreateModal(false);
        resetForm();
        fetchAds();
      } else {
        throw new Error('Failed to create ad');
      }
    } catch (error) {
      console.error('Error creating ad:', error);
      showToast('Failed to create ad', 'error');
    }
  };

  const updateAd = async () => {
    try {
      const response = await fetch(`${ENV_CONFIG.API_BASE_URL}/admin/ads/${editingAd.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        showToast('Ad updated successfully', 'success');
        setEditingAd(null);
        resetForm();
        fetchAds();
      } else {
        throw new Error('Failed to update ad');
      }
    } catch (error) {
      console.error('Error updating ad:', error);
      showToast('Failed to update ad', 'error');
    }
  };

  const toggleAdStatus = async (ad) => {
    try {
      const endpoint = ad.is_active ? 'deactivate' : 'activate';
      const response = await fetch(`${ENV_CONFIG.API_BASE_URL}/admin/ads/${ad.id}/${endpoint}`, {
        method: 'PUT'
      });

      if (response.ok) {
        const action = ad.is_active ? 'deactivated' : 'activated';
        showToast(`Ad ${action} successfully`, 'success');
        fetchAds();
      } else {
        throw new Error(`Failed to toggle ad status`);
      }
    } catch (error) {
      console.error('Error toggling ad status:', error);
      showToast('Failed to update ad status', 'error');
    }
  };

  const deleteAd = async (adId) => {
    if (!window.confirm('Are you sure you want to delete this ad?')) {
      return;
    }

    try {
      const response = await fetch(`${ENV_CONFIG.API_BASE_URL}/admin/ads/${adId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        showToast('Ad deleted successfully', 'success');
        fetchAds();
      } else {
        throw new Error('Failed to delete ad');
      }
    } catch (error) {
      console.error('Error deleting ad:', error);
      showToast('Failed to delete ad', 'error');
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      content: '',
      image_url: '',
      link_url: '',
      target_audience: 'all',
      placement: 'banner'
    });
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      showToast('Please select a valid image file', 'error');
      return;
    }

    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      showToast('Image size must be less than 5MB', 'error');
      return;
    }

    try {
      const formDataUpload = new FormData();
      formDataUpload.append('image', file);
      formDataUpload.append('section', 'ads');
      formDataUpload.append('field', 'ad_image');

      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${ENV_CONFIG.API_BASE_URL}/api/admin/upload-image`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formDataUpload
      });

      if (response.ok) {
        const result = await response.json();
        setFormData(prev => ({ ...prev, image_url: result.image_url }));
        showToast('Image uploaded successfully', 'success');
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Error uploading image:', error);
      showToast('Failed to upload image. Please try again.', 'error');
    }
  };

  const openEditModal = (ad) => {
    setEditingAd(ad);
    setFormData({
      title: ad.title || '',
      description: ad.description || '',
      content: ad.content || '',
      image_url: ad.image_url || '',
      link_url: ad.link_url || '',
      target_audience: ad.target_audience || 'all',
      placement: ad.placement || 'banner'
    });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading ads...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Ads Management</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage advertisements (ads are inactive by default)
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Create Ad</span>
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <Target className="w-8 h-8 text-blue-600 mr-3" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Ads</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{ads.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <Play className="w-8 h-8 text-green-600 mr-3" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Ads</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {ads.filter(ad => ad.is_active).length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <Pause className="w-8 h-8 text-orange-600 mr-3" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Inactive Ads</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {ads.filter(ad => !ad.is_active).length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <div className="flex items-center">
            <MousePointer className="w-8 h-8 text-purple-600 mr-3" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Clicks</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {ads.reduce((sum, ad) => sum + (ad.click_count || 0), 0)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Ads Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Ad Details
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Analytics
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {ads.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center">
                    <div className="text-gray-500 dark:text-gray-400">
                      <Target className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p className="text-lg font-medium mb-2">No ads created yet</p>
                      <p className="text-sm">Create your first ad to get started</p>
                    </div>
                  </td>
                </tr>
              ) : (
                ads.map((ad) => (
                  <tr key={ad.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        {ad.image_url && (
                          <img
                            src={ad.image_url}
                            alt={ad.title}
                            className="w-10 h-10 rounded-lg object-cover mr-3"
                          />
                        )}
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {ad.title}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {ad.placement} • {ad.target_audience}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        ad.is_active
                          ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                      }`}>
                        {ad.is_active ? (
                          <>
                            <Play className="w-3 h-3 mr-1" />
                            Active
                          </>
                        ) : (
                          <>
                            <Pause className="w-3 h-3 mr-1" />
                            Inactive
                          </>
                        )}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                        <div className="flex items-center">
                          <Eye className="w-4 h-4 mr-1" />
                          {ad.impression_count || 0}
                        </div>
                        <div className="flex items-center">
                          <MousePointer className="w-4 h-4 mr-1" />
                          {ad.click_count || 0}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                      {formatDate(ad.created_at)}
                    </td>
                    <td className="px-6 py-4 text-right text-sm font-medium">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => toggleAdStatus(ad)}
                          className={`p-2 rounded-lg transition-colors ${
                            ad.is_active
                              ? 'text-orange-600 hover:bg-orange-100 dark:hover:bg-orange-900'
                              : 'text-green-600 hover:bg-green-100 dark:hover:bg-green-900'
                          }`}
                          title={ad.is_active ? 'Deactivate Ad' : 'Activate Ad'}
                        >
                          {ad.is_active ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        </button>
                        <button
                          onClick={() => openEditModal(ad)}
                          className="p-2 text-blue-600 hover:bg-blue-100 dark:hover:bg-blue-900 rounded-lg transition-colors"
                          title="Edit Ad"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => deleteAd(ad.id)}
                          className="p-2 text-red-600 hover:bg-red-100 dark:hover:bg-red-900 rounded-lg transition-colors"
                          title="Delete Ad"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create/Edit Ad Modal */}
      {(showCreateModal || editingAd) && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div className="fixed inset-0 bg-black opacity-50"></div>
            <div className="relative bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                {editingAd ? 'Edit Ad' : 'Create New Ad'}
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Title
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    placeholder="Enter ad title"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows="3"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    placeholder="Enter ad description"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Image
                  </label>
                  <div className="space-y-3">
                    {/* Upload Option */}
                    <div>
                      <label className="text-sm text-gray-600 dark:text-gray-400 mb-1 block">
                        Upload Image File
                      </label>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageUpload}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                    
                    {/* OR Divider */}
                    <div className="flex items-center">
                      <div className="flex-1 border-t border-gray-300 dark:border-gray-600"></div>
                      <span className="px-3 text-sm text-gray-500 dark:text-gray-400">OR</span>
                      <div className="flex-1 border-t border-gray-300 dark:border-gray-600"></div>
                    </div>
                    
                    {/* URL Option */}
                    <div>
                      <label className="text-sm text-gray-600 dark:text-gray-400 mb-1 block">
                        Image URL
                      </label>
                      <input
                        type="url"
                        value={formData.image_url}
                        onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                        placeholder="https://example.com/image.jpg"
                      />
                    </div>
                    
                    {/* Image Preview */}
                    {formData.image_url && (
                      <div className="mt-3">
                        <label className="text-sm text-gray-600 dark:text-gray-400 mb-1 block">Preview</label>
                        <img 
                          src={formData.image_url} 
                          alt="Ad Preview" 
                          className="w-full max-w-xs h-32 object-cover rounded-lg border border-gray-200 dark:border-gray-600"
                          onError={(e) => {
                            e.target.style.display = 'none';
                          }}
                        />
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Link URL
                  </label>
                  <input
                    type="url"
                    value={formData.link_url}
                    onChange={(e) => setFormData({ ...formData, link_url: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    placeholder="https://example.com"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Placement
                    </label>
                    <select
                      value={formData.placement}
                      onChange={(e) => setFormData({ ...formData, placement: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    >
                      <option value="banner">Banner</option>
                      <option value="sidebar">Sidebar</option>
                      <option value="popup">Popup</option>
                      <option value="inline">Inline</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Target Audience
                    </label>
                    <select
                      value={formData.target_audience}
                      onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    >
                      <option value="all">All Users</option>
                      <option value="buyers">Buyers</option>
                      <option value="sellers">Sellers</option>
                      <option value="admins">Admins</option>
                    </select>
                  </div>
                </div>

                {!editingAd && (
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg p-3">
                    <p className="text-sm text-yellow-800 dark:text-yellow-200">
                      ⚠️ Note: New ads are created as inactive by default and require manual activation.
                    </p>
                  </div>
                )}
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    setEditingAd(null);
                    resetForm();
                  }}
                  className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={editingAd ? updateAd : createAd}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {editingAd ? 'Update Ad' : 'Create Ad'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdsManagement;