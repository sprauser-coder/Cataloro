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
        full_name: formData.full_name,
        password: formData.password
      });
      navigate(APP_ROUTES.BROWSE);
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
                Password
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
                Confirm Password
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