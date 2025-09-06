/**
 * CATALORO - Register Page
 * User registration with modern design
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, User, Building, Globe, Check, X, AlertCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { APP_ROUTES, UI_CONFIG } from '../../config/directions';

function RegisterPage() {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    account_type: 'buyer', // Default to buyer
    is_business: false,
    company_name: '',
    country: '',
    vat_number: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [usernameAvailable, setUsernameAvailable] = useState(null);
  const [checkingUsername, setCheckingUsername] = useState(false);
  const { register, isAuthenticated, isLoading, error, clearError } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate(APP_ROUTES.BROWSE);
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    return () => clearError();
  }, [clearError]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
    clearError();
    
    // Check username availability when username changes
    if (name === 'username' && value.length >= 3) {
      checkUsernameAvailability(value);
    } else if (name === 'username') {
      setUsernameAvailable(null);
    }
  };

  const checkUsernameAvailability = async (username) => {
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

  const validateForm = () => {
    if (!formData.first_name.trim()) {
      return 'First name is required';
    }
    if (!formData.last_name.trim()) {
      return 'Last name is required';
    }
    if (!formData.username.trim()) {
      return 'Username is required';
    }
    if (formData.username.length < 3) {
      return 'Username must be at least 3 characters';
    }
    if (usernameAvailable === false) {
      return 'Username is not available';
    }
    if (!formData.email.trim()) {
      return 'Email is required';
    }
    if (formData.password !== formData.confirmPassword) {
      return 'Passwords do not match';
    }
    if (formData.password.length < 6) {
      return 'Password must be at least 6 characters';
    }
    if (formData.is_business) {
      if (!formData.company_name.trim()) {
        return 'Company name is required for business accounts';
      }
      if (!formData.country.trim()) {
        return 'Country is required for business accounts';
      }
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationError = validateForm();
    if (validationError) {
      // This would show via the error state
      return;
    }

    try {
      await register({
        username: formData.username,
        email: formData.email,
        first_name: formData.first_name,
        last_name: formData.last_name,
        full_name: `${formData.first_name} ${formData.last_name}`.trim(),
        password: formData.password,
        account_type: formData.account_type, // Pass account type to backend
        is_business: formData.is_business,
        company_name: formData.is_business ? formData.company_name : '',
        country: formData.is_business ? formData.country : '',
        vat_number: formData.is_business ? formData.vat_number : ''
      });
      // Show pending approval message instead of navigating
      alert('Registration submitted successfully! Your account is pending admin approval. You will be notified once approved.');
      navigate(APP_ROUTES.LOGIN);
    } catch (error) {
      console.error('Registration failed:', error);
    }
  };

  const validationError = validateForm();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-2xl">C</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Join {UI_CONFIG.APP_NAME}</h1>
          <p className="text-gray-600">Create your marketplace account</p>
        </div>

        {/* Registration Form */}
        <div className="cataloro-card p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error Display */}
            {(error || validationError) && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error || validationError}
              </div>
            )}

            {/* First Name and Last Name Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  First Name *
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    name="first_name"
                    required
                    value={formData.first_name}
                    onChange={handleInputChange}
                    className="cataloro-input pl-10"
                    placeholder="Enter your first name"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Last Name *
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    name="last_name"
                    required
                    value={formData.last_name}
                    onChange={handleInputChange}
                    className="cataloro-input pl-10"
                    placeholder="Enter your last name"
                  />
                </div>
              </div>
            </div>

            {/* Username Field with Availability Check */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Username *
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  name="username"
                  required
                  value={formData.username}
                  onChange={handleInputChange}
                  className="cataloro-input pl-10 pr-10"
                  placeholder="Choose a username"
                />
                {formData.username.length >= 3 && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    {checkingUsername ? (
                      <AlertCircle className="w-5 h-5 text-gray-400 animate-spin" />
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
            </div>

            {/* Email Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address *
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="email"
                  name="email"
                  required
                  value={formData.email}
                  onChange={handleInputChange}
                  className="cataloro-input pl-10"
                  placeholder="Enter your email"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password *
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  className="cataloro-input pl-10 pr-10"
                  placeholder="Create a password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Confirm Password Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password *
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  name="confirmPassword"
                  required
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="cataloro-input pl-10 pr-10"
                  placeholder="Confirm your password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Account Type Selection */}
            <div className="space-y-4">
              <div className="border-t border-gray-200 pt-6">
                <label className="block text-sm font-medium text-gray-700 mb-4">
                  Account Type *
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Buyer Account */}
                  <div 
                    className={`relative p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                      formData.account_type === 'buyer' 
                        ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setFormData({...formData, account_type: 'buyer'})}
                  >
                    <div className="flex items-center space-x-3">
                      <input
                        type="radio"
                        name="account_type"
                        value="buyer"
                        checked={formData.account_type === 'buyer'}
                        onChange={handleInputChange}
                        className="w-4 h-4 text-blue-600"
                      />
                      <div>
                        <div className="font-medium text-gray-900">Buyer Account</div>
                        <div className="text-sm text-gray-500">Browse and bid on listings</div>
                      </div>
                    </div>
                    {formData.account_type === 'buyer' && (
                      <div className="absolute top-2 right-2">
                        <Check className="w-5 h-5 text-blue-600" />
                      </div>
                    )}
                  </div>

                  {/* Seller Account */}
                  <div 
                    className={`relative p-4 border-2 rounded-lg cursor-pointer transition-all duration-200 ${
                      formData.account_type === 'seller' 
                        ? 'border-green-500 bg-green-50 ring-2 ring-green-200' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setFormData({...formData, account_type: 'seller'})}
                  >
                    <div className="flex items-center space-x-3">
                      <input
                        type="radio"
                        name="account_type"
                        value="seller"
                        checked={formData.account_type === 'seller'}
                        onChange={handleInputChange}
                        className="w-4 h-4 text-green-600"
                      />
                      <div>
                        <div className="font-medium text-gray-900">Seller Account</div>
                        <div className="text-sm text-gray-500">Create and manage listings</div>
                      </div>
                    </div>
                    {formData.account_type === 'seller' && (
                      <div className="absolute top-2 right-2">
                        <Check className="w-5 h-5 text-green-600" />
                      </div>
                    )}
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  You can switch between buying and selling after account approval. Both account types are free.
                </p>
              </div>
            </div>

            {/* Business Registration Section */}
            <div className="space-y-4">
              <div className="border-t border-gray-200 pt-6">
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="is_business"
                    name="is_business"
                    checked={formData.is_business}
                    onChange={handleInputChange}
                    className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                  />
                  <label htmlFor="is_business" className="text-sm font-medium text-gray-700 flex items-center">
                    <Building className="w-4 h-4 mr-2 text-blue-600" />
                    Register as Business
                  </label>
                </div>
                <p className="text-xs text-gray-500 ml-7 mt-1">
                  Check this box if you're registering for your company or business
                </p>
              </div>

              {/* Conditional Business Fields */}
              {formData.is_business && (
                <div className="space-y-4 bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                  <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-100 flex items-center">
                    <Building className="w-4 h-4 mr-2" />
                    Business Information
                  </h4>
                  
                  {/* Company Name */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Company Name *
                    </label>
                    <div className="relative">
                      <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                      <input
                        type="text"
                        name="company_name"
                        required={formData.is_business}
                        value={formData.company_name}
                        onChange={handleInputChange}
                        className="cataloro-input pl-10"
                        placeholder="Enter your company name"
                      />
                    </div>
                  </div>

                  {/* Country */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Country *
                    </label>
                    <div className="relative">
                      <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                      <input
                        type="text"
                        name="country"
                        required={formData.is_business}
                        value={formData.country}
                        onChange={handleInputChange}
                        className="cataloro-input pl-10"
                        placeholder="Enter your country"
                      />
                    </div>
                  </div>

                  {/* VAT Number */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      VAT Number
                      <span className="text-xs text-gray-500 ml-1">(Optional)</span>
                    </label>
                    <div className="relative">
                      <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                      <input
                        type="text"
                        name="vat_number"
                        value={formData.vat_number}
                        onChange={handleInputChange}
                        className="cataloro-input pl-10"
                        placeholder="Enter your VAT number (if applicable)"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || validationError}
              className="w-full cataloro-button-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="spinner mr-2"></div>
                  Creating Account...
                </div>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link to={APP_ROUTES.LOGIN} className="text-blue-600 hover:text-blue-700 font-medium">
                Sign in here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;