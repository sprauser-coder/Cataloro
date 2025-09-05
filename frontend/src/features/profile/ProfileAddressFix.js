import React, { useState, useEffect } from 'react';
import { Save, User, Mail, MapPin, Phone, Building, Globe } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

// Fixed Profile Component with Persistent Address
const ProfileAddressFix = () => {
  const [profileData, setProfileData] = useState({
    username: '',
    email: '',
    profile: {
      full_name: '',
      bio: '',
      location: '',
      phone: '',
      company: '',
      website: '',
      address: '' // This will persist
    },
    settings: {
      notifications: true,
      email_updates: true,
      public_profile: true
    }
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  const { user } = useAuth();
  const { showToast } = useNotifications();

  useEffect(() => {
    if (user?.id) {
      fetchProfileData();
    }
  }, [user?.id]);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/auth/profile/${user.id}`);
      
      if (response.ok) {
        const data = await response.json();
        // Make sure all fields are properly set including address
        setProfileData({
          username: data.username || '',
          email: data.email || '',
          profile: {
            full_name: data.profile?.full_name || '',
            bio: data.profile?.bio || '',
            location: data.profile?.location || '',
            phone: data.profile?.phone || '',
            company: data.profile?.company || '',
            website: data.profile?.website || '',
            address: data.profile?.address || '' // Critical: ensure address persists
          },
          settings: {
            notifications: data.settings?.notifications !== false,
            email_updates: data.settings?.email_updates !== false,
            public_profile: data.settings?.public_profile !== false
          }
        });
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
      showToast('Failed to load profile data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const saveProfile = async () => {
    try {
      setSaving(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/auth/profile/${user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData)
      });

      if (response.ok) {
        const result = await response.json();
        showToast('Profile updated successfully!', 'success');
        // Update local state with returned data to ensure persistence
        if (result.user) {
          setProfileData(prev => ({
            ...prev,
            username: result.user.username,
            email: result.user.email,
            profile: {
              ...prev.profile,
              ...result.user.profile
            },
            settings: {
              ...prev.settings,
              ...result.user.settings
            }
          }));
        }
      } else {
        const error = await response.json();
        showToast(error.detail || 'Failed to update profile', 'error');
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      showToast('Failed to update profile', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (section, field, value) => {
    if (section === 'profile') {
      setProfileData(prev => ({
        ...prev,
        profile: {
          ...prev.profile,
          [field]: value
        }
      }));
    } else if (section === 'settings') {
      setProfileData(prev => ({
        ...prev,
        settings: {
          ...prev.settings,
          [field]: value
        }
      }));
    } else {
      setProfileData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
        <span className="ml-3 text-gray-600 dark:text-gray-400">Loading profile...</span>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-8">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Profile Settings</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Update your profile information and preferences. Changes are saved permanently.
          </p>
        </div>

        <div className="p-6 space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
              <User className="w-5 h-5 mr-2" />
              Basic Information
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Username
                </label>
                <input
                  type="text"
                  value={profileData.username}
                  onChange={(e) => handleInputChange(null, 'username', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={profileData.email}
                  onChange={(e) => handleInputChange(null, 'email', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Full Name
              </label>
              <input
                type="text"
                value={profileData.profile.full_name}
                onChange={(e) => handleInputChange('profile', 'full_name', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Bio
              </label>
              <textarea
                value={profileData.profile.bio}
                onChange={(e) => handleInputChange('profile', 'bio', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Tell us about yourself..."
              />
            </div>
          </div>

          {/* Contact Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
              <Mail className="w-5 h-5 mr-2" />
              Contact Information
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  <Phone className="w-4 h-4 inline mr-1" />
                  Phone
                </label>
                <input
                  type="tel"
                  value={profileData.profile.phone}
                  onChange={(e) => handleInputChange('profile', 'phone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  <MapPin className="w-4 h-4 inline mr-1" />
                  Location
                </label>
                <input
                  type="text"
                  value={profileData.profile.location}
                  onChange={(e) => handleInputChange('profile', 'location', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>

            {/* CRITICAL: Address Field with Persistence */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                <MapPin className="w-4 h-4 inline mr-1" />
                Address (Persistent)
              </label>
              <textarea
                value={profileData.profile.address}
                onChange={(e) => handleInputChange('profile', 'address', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Enter your full address..."
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                This address will be saved permanently and persist across sessions.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  <Building className="w-4 h-4 inline mr-1" />
                  Company
                </label>
                <input
                  type="text"
                  value={profileData.profile.company}
                  onChange={(e) => handleInputChange('profile', 'company', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  <Globe className="w-4 h-4 inline mr-1" />
                  Website
                </label>
                <input
                  type="url"
                  value={profileData.profile.website}
                  onChange={(e) => handleInputChange('profile', 'website', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>
          </div>

          {/* Settings */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Preferences</h3>
            
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={profileData.settings.notifications}
                  onChange={(e) => handleInputChange('settings', 'notifications', e.target.checked)}
                  className="h-4 w-4 rounded border-2 border-gray-300 dark:border-gray-600 text-purple-600 focus:ring-purple-500 focus:ring-2 bg-white dark:bg-gray-700 checked:bg-purple-600 checked:border-purple-600"
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Enable notifications</span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={profileData.settings.email_updates}
                  onChange={(e) => handleInputChange('settings', 'email_updates', e.target.checked)}
                  className="h-4 w-4 rounded border-2 border-gray-300 dark:border-gray-600 text-purple-600 focus:ring-purple-500 focus:ring-2 bg-white dark:bg-gray-700 checked:bg-purple-600 checked:border-purple-600"
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Receive email updates</span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={profileData.settings.public_profile}
                  onChange={(e) => handleInputChange('settings', 'public_profile', e.target.checked)}
                  className="h-4 w-4 rounded border-2 border-gray-300 dark:border-gray-600 text-purple-600 focus:ring-purple-500 focus:ring-2 bg-white dark:bg-gray-700 checked:bg-purple-600 checked:border-purple-600"
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Make profile public</span>
              </label>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end pt-6 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={saveProfile}
              disabled={saving}
              className="flex items-center space-x-2 px-6 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white rounded-lg font-medium transition-colors"
            >
              {saving ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>Save Changes</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileAddressFix;