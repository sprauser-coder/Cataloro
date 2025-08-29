/**
 * CATALORO - Profile Page
 * User profile settings and management (dummy implementation for now)
 */

import React, { useState } from 'react';
import { User, Mail, Phone, MapPin, Camera, Save, Edit } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';

function ProfilePage() {
  const { user } = useAuth();
  const { showToast } = useNotifications();
  const [isEditing, setIsEditing] = useState(false);
  
  const [profileData, setProfileData] = useState({
    full_name: user?.full_name || '',
    username: user?.username || '',
    email: user?.email || '',
    phone: '',
    address: '',
    bio: '',
    avatar_url: ''
  });

  const handleInputChange = (e) => {
    setProfileData({
      ...profileData,
      [e.target.name]: e.target.value
    });
  };

  const handleSaveProfile = () => {
    // TODO: Implement profile update API call
    setIsEditing(false);
    showToast('Profile updated successfully', 'success');
  };

  const handleAvatarUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // TODO: Implement avatar upload
      showToast('Avatar upload feature coming soon', 'info');
    }
  };

  return (
    <div className="fade-in">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Profile Settings</h1>
            <p className="text-gray-600">Manage your account information and preferences</p>
          </div>
          
          <button
            onClick={() => isEditing ? handleSaveProfile() : setIsEditing(true)}
            className="cataloro-button-primary flex items-center"
          >
            {isEditing ? (
              <>
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </>
            ) : (
              <>
                <Edit className="w-4 h-4 mr-2" />
                Edit Profile
              </>
            )}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Profile Card */}
        <div className="lg:col-span-1">
          <div className="cataloro-card p-6 text-center">
            {/* Avatar */}
            <div className="relative inline-block mb-4">
              <div className="w-32 h-32 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto">
                <span className="text-white font-bold text-4xl">
                  {profileData.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                </span>
              </div>
              
              {isEditing && (
                <label className="absolute bottom-0 right-0 bg-white rounded-full p-2 shadow-lg cursor-pointer hover:bg-gray-50">
                  <Camera className="w-4 h-4 text-gray-600" />
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarUpload}
                    className="hidden"
                  />
                </label>
              )}
            </div>

            <h3 className="text-xl font-bold text-gray-900 mb-1">
              {profileData.full_name || 'User Name'}
            </h3>
            <p className="text-gray-600 mb-2">@{profileData.username}</p>
            
            {user?.role && (
              <span className="inline-block bg-blue-100 text-blue-600 px-3 py-1 rounded-full text-sm font-medium">
                {user.role.toUpperCase()}
              </span>
            )}

            {/* Stats */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-lg font-bold text-gray-900">12</div>
                  <div className="text-sm text-gray-600">Listings</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-gray-900">8</div>
                  <div className="text-sm text-gray-600">Deals</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-gray-900">4.9</div>
                  <div className="text-sm text-gray-600">Rating</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Profile Details */}
        <div className="lg:col-span-2">
          <div className="cataloro-card p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Account Information</h2>
            
            <form className="space-y-6">
              {/* Full Name */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <User className="w-4 h-4 inline mr-2" />
                    Full Name
                  </label>
                  <input
                    type="text"
                    name="full_name"
                    value={profileData.full_name}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className={`cataloro-input ${!isEditing ? 'bg-gray-50 cursor-not-allowed' : ''}`}
                    placeholder="Enter your full name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <User className="w-4 h-4 inline mr-2" />
                    Username
                  </label>
                  <input
                    type="text"
                    name="username"
                    value={profileData.username}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className={`cataloro-input ${!isEditing ? 'bg-gray-50 cursor-not-allowed' : ''}`}
                    placeholder="Choose a username"
                  />
                </div>
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Mail className="w-4 h-4 inline mr-2" />
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={profileData.email}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  className={`cataloro-input ${!isEditing ? 'bg-gray-50 cursor-not-allowed' : ''}`}
                  placeholder="Enter your email"
                />
              </div>

              {/* Phone */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Phone className="w-4 h-4 inline mr-2" />
                  Phone Number
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={profileData.phone}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  className={`cataloro-input ${!isEditing ? 'bg-gray-50 cursor-not-allowed' : ''}`}
                  placeholder="Enter your phone number"
                />
              </div>

              {/* Address */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <MapPin className="w-4 h-4 inline mr-2" />
                  Address
                </label>
                <input
                  type="text"
                  name="address"
                  value={profileData.address}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  className={`cataloro-input ${!isEditing ? 'bg-gray-50 cursor-not-allowed' : ''}`}
                  placeholder="Enter your address"
                />
              </div>

              {/* Bio */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bio
                </label>
                <textarea
                  name="bio"
                  rows={4}
                  value={profileData.bio}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  className={`cataloro-input ${!isEditing ? 'bg-gray-50 cursor-not-allowed' : ''}`}
                  placeholder="Tell us about yourself..."
                />
              </div>
            </form>
          </div>

          {/* Security Section */}
          <div className="cataloro-card p-6 mt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Security</h2>
            
            <div className="space-y-4">
              <button className="cataloro-button-secondary w-full sm:w-auto">
                Change Password
              </button>
              <button className="cataloro-button-secondary w-full sm:w-auto">
                Two-Factor Authentication
              </button>
            </div>
          </div>

          {/* Preferences Section */}
          <div className="cataloro-card p-6 mt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Preferences</h2>
            
            <div className="space-y-4">
              <label className="flex items-center">
                <input type="checkbox" className="mr-3" defaultChecked />
                <span className="text-gray-700">Email notifications for new messages</span>
              </label>
              
              <label className="flex items-center">
                <input type="checkbox" className="mr-3" defaultChecked />
                <span className="text-gray-700">SMS notifications for deals</span>
              </label>
              
              <label className="flex items-center">
                <input type="checkbox" className="mr-3" />
                <span className="text-gray-700">Marketing emails</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProfilePage;