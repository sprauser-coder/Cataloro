/**
 * Users Tab Component - User Management Interface
 * Extracted from AdminPanel.js for better maintainability and performance
 */

import React, { useState } from 'react';
import { 
  Users, 
  CheckCircle, 
  Shield, 
  Ban, 
  Clock,
  Search,
  Plus,
  Edit,
  Trash2,
  X,
  Download
} from 'lucide-react';

// Comprehensive User Edit Modal with all features
const UserEditModal = ({ user, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    first_name: user?.first_name || (user?.full_name ? user.full_name.split(' ')[0] : ''),
    last_name: user?.last_name || (user?.full_name ? user.full_name.split(' ').slice(1).join(' ') : ''),
    username: user?.username || '',
    email: user?.email || '',
    user_role: user?.user_role || user?.role === 'admin' ? 'Admin' : 'User-Buyer', // Migrate legacy role to user_role
    registration_status: user?.registration_status || 'Approved',
    is_active: user?.is_active !== undefined ? user.is_active : true,
    password: '',
    confirmPassword: '',
    is_business: user?.is_business || false,
    company_name: user?.company_name || '',
    country: user?.country || '',
    vat_number: user?.vat_number || ''
  });

  const [errors, setErrors] = useState({});
  const [usernameAvailable, setUsernameAvailable] = useState(null);
  const [checkingUsername, setCheckingUsername] = useState(false);

  const checkUsernameAvailability = async (username) => {
    if (user && user.username === username) {
      // Don't check availability for current user's existing username
      setUsernameAvailable(true);
      return;
    }
    
    setCheckingUsername(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/check-username/${username}`);
      if (response.ok) {
        const data = await response.json();
        setUsernameAvailable(data.available);
      } else {
        setUsernameAvailable(null);
      }
    } catch (error) {
      console.error('Error checking username:', error);
      setUsernameAvailable(null);
    } finally {
      setCheckingUsername(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
    
    // Check username availability when username changes
    if (name === 'username' && value.length >= 3) {
      checkUsernameAvailability(value);
    } else if (name === 'username') {
      setUsernameAvailable(null);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // First Name and Last Name validation (matching registration page)
    if (!formData.first_name.trim()) {
      newErrors.first_name = 'First name is required';
    }
    if (!formData.last_name.trim()) {
      newErrors.last_name = 'Last name is required';
    }

    // Username validation (matching registration page)
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    }
    if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }
    if (usernameAvailable === false) {
      newErrors.username = 'Username is not available';
    }

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    // Password validation - required for new users or if password is being changed
    if (!user && !formData.password) {
      newErrors.password = 'Password is required for new users';
    }
    
    if (formData.password && formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    if (formData.password && formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    // Business validation (matching registration page)
    if (formData.is_business) {
      if (!formData.company_name.trim()) {
        newErrors.company_name = 'Company name is required for business accounts';
      }
      if (!formData.country.trim()) {
        newErrors.country = 'Country is required for business accounts';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    const userData = { 
      ...formData,
      full_name: `${formData.first_name} ${formData.last_name}`.trim() // Compose full name for backend compatibility
    };
    
    // If editing existing user, include ID
    if (user) {
      userData.id = user.id;
    }

    // Remove password fields if they're empty (for updates)
    if (!userData.password) {
      delete userData.password;
      delete userData.confirmPassword;
    } else {
      delete userData.confirmPassword; // Don't send confirmPassword to backend
    }

    onSave(userData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-md mx-4">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {user ? 'Edit User' : 'Create New User'}
          </h3>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* First Name and Last Name */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                First Name *
              </label>
              <input
                type="text"
                value={formData.first_name}
                onChange={handleInputChange}
                name="first_name"
                className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                  errors.first_name ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                }`}
                placeholder="Enter first name"
              />
              {errors.first_name && <p className="text-red-500 text-xs mt-1">{errors.first_name}</p>}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Last Name *
              </label>
              <input
                type="text"
                value={formData.last_name}
                onChange={handleInputChange}
                name="last_name"
                className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                  errors.last_name ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                }`}
                placeholder="Enter last name"
              />
              {errors.last_name && <p className="text-red-500 text-xs mt-1">{errors.last_name}</p>}
            </div>
          </div>

          {/* Username with Availability Check */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Username *
            </label>
            <div className="relative">
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 pr-10 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                  errors.username ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                }`}
                placeholder="Enter username"
              />
              {formData.username.length >= 3 && (
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  {checkingUsername ? (
                    <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                  ) : usernameAvailable === true ? (
                    <Check className="w-5 h-5 text-green-500" />
                  ) : usernameAvailable === false ? (
                    <X className="w-5 h-5 text-red-500" />
                  ) : null}
                </div>
              )}
            </div>
            {formData.username.length >= 3 && usernameAvailable !== null && (
              <div className={`mt-1 text-sm ${usernameAvailable ? 'text-green-600' : 'text-red-600'}`}>
                {usernameAvailable ? 'Username is available' : 'Username is not available'}
              </div>
            )}
            {errors.username && <p className="text-red-500 text-xs mt-1">{errors.username}</p>}
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Email *
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                errors.email ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
              placeholder="Enter email address"
            />
            {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
          </div>

          {/* User Role Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              User Role *
            </label>
            <select
              name="user_role"
              value={formData.user_role}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="User-Buyer">User-Buyer</option>
              <option value="User-Seller">User-Seller</option>
              <option value="Admin-Manager">Admin-Manager</option>
              <option value="Admin">Admin</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Determines user permissions and access level
            </p>
          </div>

          {/* Registration Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Registration Status *
            </label>
            <select
              name="registration_status"
              value={formData.registration_status}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="Approved">Approved</option>
              <option value="Pending">Pending</option>
              <option value="Rejected">Rejected</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Controls user login access and approval status
            </p>
          </div>

          {/* Account Status */}
          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              name="is_active"
              checked={formData.is_active}
              onChange={handleInputChange}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Account Active
            </label>
            <span className="text-xs text-gray-500">
              {formData.is_active ? 'User can access the platform' : 'User account is suspended'}
            </span>
          </div>

          {/* Business Registration Section */}
          <div className="border-t border-gray-200 dark:border-gray-600 pt-6">
            <div className="flex items-center space-x-3 mb-4">
              <input
                type="checkbox"
                id="is_business"
                name="is_business"
                checked={formData.is_business}
                onChange={handleInputChange}
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              />
              <label htmlFor="is_business" className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center">
                <User className="w-4 h-4 mr-2 text-blue-600" />
                Business Account
              </label>
            </div>
            
            {/* Conditional Business Fields */}
            {formData.is_business && (
              <div className="space-y-4 bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-100 flex items-center">
                  <User className="w-4 h-4 mr-2" />
                  Business Information
                </h4>
                
                {/* Company Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Company Name *
                  </label>
                  <input
                    type="text"
                    name="company_name"
                    value={formData.company_name}
                    onChange={handleInputChange}
                    className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      errors.company_name ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                    }`}
                    placeholder="Enter company name"
                  />
                  {errors.company_name && <p className="text-red-500 text-xs mt-1">{errors.company_name}</p>}
                </div>

                {/* Country */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Country *
                  </label>
                  <input
                    type="text"
                    name="country"
                    value={formData.country}
                    onChange={handleInputChange}
                    className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                      errors.country ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                    }`}
                    placeholder="Enter country"
                  />
                  {errors.country && <p className="text-red-500 text-xs mt-1">{errors.country}</p>}
                </div>

                {/* VAT Number */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    VAT Number
                    <span className="text-xs text-gray-500 ml-1">(Optional)</span>
                  </label>
                  <input
                    type="text"
                    name="vat_number"
                    value={formData.vat_number}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    placeholder="Enter VAT number (if applicable)"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Password {user && <span className="text-xs text-gray-500">(leave blank to keep current)</span>}
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                errors.password ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
              placeholder={user ? "Enter new password (optional)" : "Enter password"}
            />
            {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
          </div>

          {/* Confirm Password */}
          {formData.password && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Confirm Password
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
                  errors.confirmPassword ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                }`}
                placeholder="Confirm password"
              />
              {errors.confirmPassword && <p className="text-red-500 text-xs mt-1">{errors.confirmPassword}</p>}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              {user ? 'Update User' : 'Create User'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

function UsersTab({ users, onUpdateUser, showToast }) {
  const [selectedUser, setSelectedUser] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [bulkAction, setBulkAction] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterRegistrationStatus, setFilterRegistrationStatus] = useState('all');

  // RBAC Functions
  const handleApproveUser = async (userId) => {
    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/users/${userId}/approve`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        showToast('User approved successfully', 'success');
        onUpdateUser(); // Refresh users list
      } else {
        showToast('Failed to approve user', 'error');
      }
    } catch (error) {
      showToast('Error approving user', 'error');
      console.error('Approve user error:', error);
    }
  };

  const handleRejectUser = async (userId) => {
    const reason = prompt('Please provide a reason for rejection (optional):');
    if (reason === null) return; // User cancelled

    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/users/${userId}/reject`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason: reason || 'No reason provided' })
      });

      if (response.ok) {
        showToast('User rejected successfully', 'success');
        onUpdateUser(); // Refresh users list
      } else {
        showToast('Failed to reject user', 'error');
      }
    } catch (error) {
      showToast('Error rejecting user', 'error');
      console.error('Reject user error:', error);
    }
  };

  const handleSuspendUser = async (userId) => {
    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/users/${userId}/suspend`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        showToast('User suspended successfully', 'success');
        onUpdateUser(); // Refresh users list
      } else {
        showToast('Failed to suspend user', 'error');
      }
    } catch (error) {
      showToast('Error suspending user', 'error');
      console.error('Suspend user error:', error);
    }
  };

  const handleActivateUser = async (userId) => {
    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/users/${userId}/activate`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        showToast('User activated successfully', 'success');
        onUpdateUser(); // Refresh users list
      } else {
        showToast('Failed to activate user', 'error');
      }
    } catch (error) {
      showToast('Error activating user', 'error');
      console.error('Activate user error:', error);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return;
    }

    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        showToast('User deleted successfully', 'success');
        onUpdateUser(); // Refresh users list
      } else {
        showToast('Failed to delete user', 'error');
      }
    } catch (error) {
      showToast('Error deleting user', 'error');
      console.error('Delete user error:', error);
    }
  };

  const handleUpdateUser = async (userData) => {
    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/users/${userData.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });

      if (response.ok) {
        showToast('User updated successfully', 'success');
        setShowEditModal(false);
        setSelectedUser(null);
        onUpdateUser(); // Refresh users list
      } else {
        showToast('Failed to update user', 'error');
      }
    } catch (error) {
      showToast('Error updating user', 'error');
      console.error('Update user error:', error);
    }
  };

  const handleCreateUser = async (userData) => {
    try {
      const token = localStorage.getItem('cataloro_token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/users`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });

      if (response.ok) {
        showToast('User created successfully', 'success');
        setShowEditModal(false);
        setSelectedUser(null);
        onUpdateUser(); // Refresh users list
      } else {
        const error = await response.json();
        showToast(error.detail || 'Failed to create user', 'error');
      }
    } catch (error) {
      showToast('Error creating user', 'error');
      console.error('Create user error:', error);
    }
  };

  // Filter users based on search and filter criteria
  const filteredUsers = users.filter(user => {
    const matchesSearch = user.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.full_name?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = filterRole === 'all' || 
                       user.user_role === filterRole || 
                       (!user.user_role && user.role === filterRole); // Support legacy role as fallback
    const matchesStatus = filterStatus === 'all' || 
                         (filterStatus === 'active' && user.is_active) ||
                         (filterStatus === 'inactive' && !user.is_active);
    const matchesRegistrationStatus = filterRegistrationStatus === 'all' || 
                                    user.registration_status === filterRegistrationStatus ||
                                    (filterRegistrationStatus === 'Approved' && !user.registration_status); // Backward compatibility
    return matchesSearch && matchesRole && matchesStatus && matchesRegistrationStatus;
  });

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedUsers(filteredUsers.map(u => u.id));
    } else {
      setSelectedUsers([]);
    }
  };

  const handleSelectUser = (userId, checked) => {
    if (checked) {
      setSelectedUsers([...selectedUsers, userId]);
    } else {
      setSelectedUsers(selectedUsers.filter(id => id !== userId));
    }
  };

  const handleUserBulkAction = async (action = null) => {
    const actionToPerform = action || bulkAction;
    if (!actionToPerform || selectedUsers.length === 0) {
      showToast('No action selected or no users selected', 'warning');
      return;
    }

    // Show confirmation for destructive actions
    if (['delete', 'suspend', 'reject'].includes(actionToPerform)) {
      const actionText = actionToPerform === 'delete' ? 'delete' : 
                        actionToPerform === 'suspend' ? 'suspend' : 'reject';
      if (!window.confirm(`Are you sure you want to ${actionText} ${selectedUsers.length} users? This action cannot be undone.`)) {
        return;
      }
    }

    try {
      // Use the new bulk endpoint for all operations
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/users/bulk-action`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          action: actionToPerform,
          user_ids: selectedUsers
        })
      });

      if (response.ok) {
        const result = await response.json();
        const { results } = result;
        
        if (results.success_count > 0) {
          showToast(`Successfully ${actionToPerform}d ${results.success_count} user${results.success_count !== 1 ? 's' : ''}`, 'success');
        }
        
        if (results.failed_count > 0) {
          showToast(`Failed to ${actionToPerform} ${results.failed_count} user${results.failed_count !== 1 ? 's' : ''}`, 'warning');
          console.warn('Bulk action errors:', results.errors);
        }
        
        // Clear selections and refresh
        setSelectedUsers([]);
        setBulkAction('');
        onUpdateUser(); // Refresh user list
      } else {
        const errorData = await response.json().catch(() => ({}));
        showToast(`Failed to perform bulk ${actionToPerform}: ${errorData.detail || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      console.error('Bulk action error:', error);
      showToast(`Error performing bulk ${actionToPerform}`, 'error');
    }
  };

  return (
    <div className="space-y-8">
      {/* Enhanced Users Stats - STANDARDIZED SPACING */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <div className="cataloro-card-glass p-6">
          <div className="flex flex-col items-center justify-center space-y-3 h-full min-h-[140px]">
            <div className="p-4 bg-blue-100/80 dark:bg-blue-900/30 rounded-2xl backdrop-blur-md flex items-center justify-center">
              <Users className="w-8 h-8 text-blue-500" />
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold mb-1 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent flex items-center justify-center">
                {users.length}
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wider">Total Users</div>
            </div>
          </div>
        </div>
        
        <div className="cataloro-card-glass p-6">
          <div className="flex flex-col items-center justify-center space-y-3 h-full min-h-[140px]">
            <div className="p-4 bg-green-100/80 dark:bg-green-900/30 rounded-2xl backdrop-blur-md flex items-center justify-center">
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold mb-1 bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent flex items-center justify-center">
                {users.filter(u => u.registration_status === 'Approved').length}
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wider">Active Users</div>
            </div>
          </div>
        </div>
        
        <div className="cataloro-card-glass p-6">
          <div className="flex flex-col items-center justify-center space-y-3 h-full min-h-[140px]">
            <div className="p-4 bg-purple-100/80 dark:bg-purple-900/30 rounded-2xl backdrop-blur-md flex items-center justify-center">
              <Shield className="w-8 h-8 text-purple-500" />
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold mb-1 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent flex items-center justify-center">
                {users.filter(u => u.user_role === 'Admin' || u.user_role === 'Admin-Manager' || (!u.user_role && u.role === 'admin')).length}
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wider">Admins</div>
            </div>
          </div>
        </div>
        
        <div className="cataloro-card-glass p-6">
          <div className="flex flex-col items-center justify-center space-y-3 h-full min-h-[140px]">
            <div className="p-4 bg-red-100/80 dark:bg-red-900/30 rounded-2xl backdrop-blur-md flex items-center justify-center">
              <Ban className="w-8 h-8 text-red-500" />
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold mb-1 bg-gradient-to-r from-red-600 to-pink-600 bg-clip-text text-transparent flex items-center justify-center">
                {users.filter(u => u.registration_status === 'Rejected' || !u.is_active).length}
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wider">Suspended</div>
            </div>
          </div>
        </div>

        <div className="cataloro-card-glass p-6">
          <div className="flex flex-col items-center justify-center space-y-3 h-full min-h-[140px]">
            <div className="p-4 bg-yellow-100/80 dark:bg-yellow-900/30 rounded-2xl backdrop-blur-md flex items-center justify-center">
              <Clock className="w-8 h-8 text-yellow-500" />
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold mb-1 bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent flex items-center justify-center">
                {users.filter(u => u.registration_status === 'Pending').length}
              </div>
              <div className="text-sm font-medium text-gray-600 dark:text-gray-300 uppercase tracking-wider">Pending</div>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters - STANDARDIZED SPACING */}
      <div className="cataloro-card-glass p-6">
        <div className="flex flex-col xl:flex-row xl:items-center xl:justify-between space-y-6 xl:space-y-0">
          <div className="flex-1 max-w-md">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Search Users</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by name, email, or username..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 cataloro-input w-full"
              />
            </div>
          </div>
          
          <div className="flex items-end space-x-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Filter by Role</label>
              <select
                value={filterRole}
                onChange={(e) => setFilterRole(e.target.value)}
                className="cataloro-input w-auto min-w-[140px]"
              >
                <option value="all">All Roles</option>
                <option value="Admin">Admin</option>
                <option value="Admin-Manager">Admin Manager</option>
                <option value="User-Seller">User Seller</option>
                <option value="User-Buyer">User Buyer</option>
                <option value="admin">Legacy Admin</option>
                <option value="user">Legacy User</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Filter by Status</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="cataloro-input w-auto min-w-[120px]"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Suspended</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Registration Status</label>
              <select
                value={filterRegistrationStatus}
                onChange={(e) => setFilterRegistrationStatus(e.target.value)}
                className="cataloro-input w-auto min-w-[120px]"
              >
                <option value="all">All Status</option>
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Bulk Actions for Users - REDESIGNED */}
      {selectedUsers.length > 0 && (
        <div className="cataloro-card-glass p-6 border-2 border-blue-200 dark:border-blue-800 shadow-xl">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-6 lg:space-y-0">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
                <span className="text-xl font-bold text-gray-900 dark:text-white">
                  {selectedUsers.length} user{selectedUsers.length !== 1 ? 's' : ''} selected
                </span>
                <div className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-sm font-medium rounded-full">
                  Ready for action
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
              {/* Activate Users */}
              <button
                onClick={() => handleUserBulkAction('activate')}
                className="flex items-center justify-center space-x-2 px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-xl font-medium transition-all duration-200 transform hover:scale-105 shadow-lg"
                title="Activate selected users"
              >
                <CheckCircle className="w-4 h-4" />
                <span className="hidden sm:inline">Activate</span>
              </button>

              {/* Suspend Users */}
              <button
                onClick={() => handleUserBulkAction('suspend')}
                className="flex items-center justify-center space-x-2 px-4 py-3 bg-orange-600 hover:bg-orange-700 text-white rounded-xl font-medium transition-all duration-200 transform hover:scale-105 shadow-lg"
                title="Suspend selected users"
              >
                <Ban className="w-4 h-4" />
                <span className="hidden sm:inline">Suspend</span>
              </button>

              {/* Delete Users */}
              <button
                onClick={() => handleUserBulkAction('delete')}
                className="flex items-center justify-center space-x-2 px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl font-medium transition-all duration-200 transform hover:scale-105 shadow-lg"
                title="Delete selected users"
              >
                <Trash2 className="w-4 h-4" />
                <span className="hidden sm:inline">Delete</span>
              </button>

              {/* Approve Users */}
              <button
                onClick={() => handleUserBulkAction('approve')}
                className="flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-all duration-200 transform hover:scale-105 shadow-lg"
                title="Approve pending users"
              >
                <CheckCircle className="w-4 h-4" />
                <span className="hidden sm:inline">Approve</span>
              </button>

              {/* Reject Users */}
              <button
                onClick={() => handleUserBulkAction('reject')}
                className="flex items-center justify-center space-x-2 px-4 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-xl font-medium transition-all duration-200 transform hover:scale-105 shadow-lg"
                title="Reject pending users"
              >
                <X className="w-4 h-4" />
                <span className="hidden sm:inline">Reject</span>
              </button>
            </div>
          </div>
          
          {/* Second Row with Additional Actions */}
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex flex-wrap gap-3 justify-center lg:justify-start">
              {/* Export Users */}
              <button
                onClick={() => {
                  // Simple CSV export functionality
                  const selectedUserData = users.filter(u => selectedUsers.includes(u.id));
                  const csvContent = [
                    ['ID', 'Name', 'Email', 'Role', 'Status', 'Registration Status'].join(','),
                    ...selectedUserData.map(u => [
                      u.id,
                      u.full_name || u.username,
                      u.email,
                      u.user_role || (u.role === 'admin' ? 'Admin' : 'User-Buyer'),
                      u.is_active ? 'Active' : 'Suspended',
                      u.registration_status || 'Approved'
                    ].join(','))
                  ].join('\n');
                  
                  const blob = new Blob([csvContent], { type: 'text/csv' });
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `selected_users_${new Date().toISOString().split('T')[0]}.csv`;
                  a.click();
                  window.URL.revokeObjectURL(url);
                  
                  showToast(`Exported ${selectedUsers.length} users to CSV`, 'success');
                }}
                className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors"
                title="Export selected users to CSV"
              >
                <Download className="w-4 h-4" />
                <span>Export CSV</span>
              </button>

              {/* Clear Selection */}
              <button
                onClick={() => {
                  setSelectedUsers([]);
                  setBulkAction('');
                }}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors"
                title="Clear selection"
              >
                <X className="w-4 h-4" />
                <span>Clear Selection</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create User Button - Moved to Top */}
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">User Management</h3>
        <button
          onClick={() => {
            setSelectedUser(null);
            setShowEditModal(true);
          }}
          className="cataloro-button-primary flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Create New User</span>
        </button>
      </div>

      {/* Users Table - STANDARDIZED SPACING */}
      <div className="cataloro-card-glass overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50/80 dark:bg-gray-800/80 backdrop-blur-md">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  <input
                    type="checkbox"
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    checked={selectedUsers.length === filteredUsers.length && filteredUsers.length > 0}
                    className="admin-checkbox purple-theme"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Role & Badge
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Registration Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Active Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Joined
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {filteredUsers.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      type="checkbox"
                      checked={selectedUsers.includes(user.id)}
                      onChange={(e) => handleSelectUser(user.id, e.target.checked)}
                      className="admin-checkbox purple-theme"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-medium text-sm">
                          {user.full_name?.charAt(0) || user.username?.charAt(0)}
                        </span>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">{user.full_name}</div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">{user.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="space-y-1">
                      {/* Role Badge - Single Field */}
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          user.user_role === 'Admin' || user.user_role === 'Admin-Manager' || (!user.user_role && user.role === 'admin')
                            ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300' 
                            : user.user_role === 'User-Seller'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                            : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                        }`}>
                          {user.user_role || (user.role === 'admin' ? 'Admin' : 'User-Buyer')}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        user.registration_status === 'Approved' || !user.registration_status
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                          : user.registration_status === 'Pending'
                          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                          : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                      }`}>
                        {user.registration_status || 'APPROVED'}
                      </span>
                      {/* Approval Actions */}
                      {user.registration_status === 'Pending' && (
                        <div className="flex space-x-1">
                          <button
                            onClick={() => handleApproveUser(user.id)}
                            className="p-1 text-green-600 hover:text-green-900 hover:bg-green-50 rounded transition-colors"
                            title="Approve User"
                          >
                            <CheckCircle className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => handleRejectUser(user.id)}
                            className="p-1 text-red-600 hover:text-red-900 hover:bg-red-50 rounded transition-colors"
                            title="Reject User"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      user.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                    }`}>
                      {user.is_active ? 'ACTIVE' : 'SUSPENDED'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end space-x-2">
                      <button
                        onClick={() => {
                          setSelectedUser(user);
                          setShowEditModal(true);
                        }}
                        className="p-2 text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                        title="Edit User"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      {user.is_active ? (
                        <button
                          onClick={() => handleSuspendUser(user.id)}
                          className="p-2 text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                          title="Suspend User"
                        >
                          <Ban className="w-4 h-4" />
                        </button>
                      ) : (
                        <button
                          onClick={() => handleActivateUser(user.id)}
                          className="p-2 text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300 hover:bg-green-50 dark:hover:bg-green-900/30 rounded-lg transition-colors"
                          title="Activate User"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => handleDeleteUser(user.id)}
                        className="p-2 text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                        title="Delete User"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* User Edit/Create Modal */}
      {showEditModal && (
        <UserEditModal
          user={selectedUser}
          onClose={() => {
            setShowEditModal(false);
            setSelectedUser(null);
          }}
          onSave={selectedUser ? handleUpdateUser : handleCreateUser}
        />
      )}
    </div>
  );
}

export default UsersTab;