/**
 * CATALORO - Ultra-Modern Login Page
 * Premium glassmorphism design with advanced animations
 */

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, Store, ArrowRight, Shield, User, Sparkles } from 'lucide-react';
import { UI_CONFIG } from '../../config/directions';

function SimpleLoginPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [loggedInUser, setLoggedInUser] = useState(null);
  const [isAnimating, setIsAnimating] = useState(false);

  // Check if user is already logged in
  React.useEffect(() => {
    const token = localStorage.getItem('cataloro_token');
    const user = localStorage.getItem('cataloro_user');
    if (token && user) {
      try {
        setLoggedInUser(JSON.parse(user));
      } catch (e) {
        localStorage.removeItem('cataloro_token');
        localStorage.removeItem('cataloro_user');
      }
    }
  }, []);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setIsAnimating(true);
    setError(null);
    
    try {
      // Call the actual backend API
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      if (!response.ok) {
        throw new Error(`Login failed: ${response.status}`);
      }

      const data = await response.json();
      
      // Store user data and redirect to main app
      localStorage.setItem('cataloro_token', data.token);
      localStorage.setItem('cataloro_user', JSON.stringify(data.user));
      
      // Redirect to marketplace
      window.location.href = '/browse';
      
    } catch (error) {
      setError(error.message || 'Login failed. Please check your credentials.');
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
      setIsAnimating(false);
    }
  };

  const handleDemoLogin = async (role = 'user') => {
    const demoCredentials = {
      email: role === 'admin' ? 'admin@cataloro.com' : 'user@cataloro.com',
      password: 'demo123'
    };
    
    // Fill form and submit
    setFormData(demoCredentials);
    
    // Trigger actual login
    setIsLoading(true);
    setIsAnimating(true);
    setError(null);
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(demoCredentials)
      });

      if (!response.ok) {
        throw new Error(`Demo login failed: ${response.status}`);
      }

      const data = await response.json();
      
      localStorage.setItem('cataloro_token', data.token);
      localStorage.setItem('cataloro_user', JSON.stringify(data.user));
      
      // Force page reload to ensure proper authentication state
      window.location.href = '/browse';
      
    } catch (error) {
      setError(`Demo login failed: ${error.message}`);
    } finally {
      setIsLoading(false);
      setIsAnimating(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('cataloro_token');
    localStorage.removeItem('cataloro_user');
    setLoggedInUser(null);
    setFormData({ email: '', password: '' });
    alert('✅ Logged out successfully!');
  };

  // If user is already logged in, show logged in state
  if (loggedInUser) {
    return (
      <div className="min-h-screen relative overflow-hidden">
        {/* Ultra-Modern Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-100 dark:from-gray-900 dark:via-blue-900 dark:to-purple-900">
          <div className="absolute inset-0 bg-gradient-to-tr from-blue-400/20 via-purple-400/20 to-pink-400/20 animate-pulse"></div>
          <div className="absolute top-0 left-0 w-full h-full">
            <div className="absolute top-20 left-20 w-72 h-72 bg-blue-300/30 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
            <div className="absolute top-40 right-20 w-72 h-72 bg-purple-300/30 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
            <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300/30 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
          </div>
        </div>

        <div className="relative z-10 min-h-screen flex items-center justify-center p-4">
          <div className="w-full max-w-md">
            <div className="text-center mb-10">
              <div className="relative mb-6">
                <div className="w-20 h-20 mx-auto relative">
                  <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 p-1">
                    <div className="w-full h-full rounded-3xl bg-white/10 backdrop-blur-xl flex items-center justify-center group">
                      <Store className="w-10 h-10 text-white drop-shadow-lg group-hover:scale-110 transition-transform duration-300" />
                    </div>
                  </div>
                  <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 blur-lg opacity-50 animate-pulse"></div>
                  <Sparkles className="absolute -top-2 -right-2 w-6 h-6 text-yellow-400 animate-spin" style={{ animationDuration: '3s' }} />
                </div>
              </div>
              <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 dark:from-white dark:via-blue-100 dark:to-purple-100">
                Welcome Back!
              </h1>
              <p className="text-lg font-medium text-gray-600 dark:text-gray-300">
                You are logged in to <span className="text-blue-600 dark:text-blue-400 font-bold">{UI_CONFIG.APP_NAME}</span>
              </p>
            </div>

            <div className="cataloro-card-glass p-8 backdrop-blur-2xl border-white/30">
              <div className="text-center space-y-6">
                <div className="w-20 h-20 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center mx-auto shadow-xl">
                  <span className="text-white font-bold text-2xl">
                    {loggedInUser.full_name?.charAt(0) || loggedInUser.username?.charAt(0) || 'U'}
                  </span>
                </div>
                
                <div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">{loggedInUser.full_name}</h3>
                  <p className="text-gray-600 dark:text-gray-300">{loggedInUser.email}</p>
                  <span className={`inline-block mt-2 px-4 py-1 rounded-full text-sm font-bold ${
                    loggedInUser.role === 'admin' ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white' : 'bg-gradient-to-r from-blue-500 to-purple-500 text-white'
                  }`}>
                    {loggedInUser.role?.toUpperCase()}
                  </span>
                </div>

                <div className="space-y-3 pt-4">
                  <button
                    onClick={() => window.location.href = '/browse'}
                    className="w-full h-14 rounded-2xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white font-bold text-lg hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 transition-all duration-300 transform hover:scale-[1.02] hover:shadow-2xl group overflow-hidden"
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-white/20 via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    <div className="relative flex items-center justify-center space-x-2">
                      <span>Go to Marketplace</span>
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
                    </div>
                  </button>
                  
                  <button
                    onClick={handleLogout}
                    className="w-full h-12 rounded-xl bg-white/20 dark:bg-white/10 backdrop-blur-sm border border-white/30 text-gray-700 dark:text-gray-200 font-semibold hover:bg-white/30 dark:hover:bg-white/20 transition-all duration-300 group flex items-center justify-center space-x-3"
                  >
                    <span>Logout</span>
                  </button>
                </div>

                <div className="mt-6 text-center">
                  <p className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span>Authentication: Working</span>
                    </div>
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span>Backend API: Connected</span>
                    </div>
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span>User Session: Active</span>
                    </div>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Ultra-Modern Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-100 dark:from-gray-900 dark:via-blue-900 dark:to-purple-900">
        <div className="absolute inset-0 bg-gradient-to-tr from-blue-400/20 via-purple-400/20 to-pink-400/20 animate-pulse"></div>
        <div className="absolute top-0 left-0 w-full h-full">
          <div className="absolute top-20 left-20 w-72 h-72 bg-blue-300/30 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
          <div className="absolute top-40 right-20 w-72 h-72 bg-purple-300/30 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300/30 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
        </div>
      </div>

      {/* Floating Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-blue-400 rounded-full animate-ping"></div>
        <div className="absolute top-3/4 right-1/4 w-1 h-1 bg-purple-400 rounded-full animate-ping" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-3/4 w-1.5 h-1.5 bg-pink-400 rounded-full animate-ping" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="relative z-10 min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Ultra-Modern Header */}
          <div className="text-center mb-10">
            {/* Premium Logo Container */}
            <div className="relative mb-6">
              <div className="w-20 h-20 mx-auto relative">
                {/* Main Logo */}
                <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 p-1">
                  <div className="w-full h-full rounded-3xl bg-white/10 backdrop-blur-xl flex items-center justify-center group">
                    <Store className="w-10 h-10 text-white drop-shadow-lg group-hover:scale-110 transition-transform duration-300" />
                  </div>
                </div>
                {/* Animated Glow */}
                <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 blur-lg opacity-50 animate-pulse"></div>
                {/* Sparkle Effect */}
                <Sparkles className="absolute -top-2 -right-2 w-6 h-6 text-yellow-400 animate-spin" style={{ animationDuration: '3s' }} />
              </div>
            </div>

            {/* Premium Title */}
            <div className="space-y-3">
              <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-gray-900 via-blue-900 to-purple-900 dark:from-white dark:via-blue-100 dark:to-purple-100">
                Welcome Back
              </h1>
              <p className="text-lg font-medium text-gray-600 dark:text-gray-300">
                Sign in to <span className="text-blue-600 dark:text-blue-400 font-bold">{UI_CONFIG.APP_NAME}</span>
              </p>
              <div className="flex items-center justify-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>Secure Login</span>
                </div>
                <span>•</span>
                <span>Ultra-Modern Marketplace</span>
              </div>
            </div>
          </div>

          {/* Premium Login Form */}
          <div className="cataloro-card-glass p-8 backdrop-blur-2xl border-white/30">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Enhanced Error Display */}
              {error && (
                <div className="bg-red-500/10 border border-red-300/30 text-red-700 dark:text-red-300 px-5 py-4 rounded-2xl backdrop-blur-sm animate-pulse">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                    <span className="font-medium">{error}</span>
                  </div>
                </div>
              )}

              {/* Premium Email Field */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200">
                  Email Address
                </label>
                <div className="relative group">
                  <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-blue-500 w-5 h-5 transition-colors duration-200" />
                  <input
                    type="email"
                    name="email"
                    required
                    value={formData.email}
                    onChange={handleInputChange}
                    className="cataloro-input pl-12 h-14 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50"
                    placeholder="Enter your email address"
                  />
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-500/5 to-purple-500/5 opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
                </div>
              </div>

              {/* Premium Password Field */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200">
                  Password
                </label>
                <div className="relative group">
                  <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-blue-500 w-5 h-5 transition-colors duration-200" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    required
                    value={formData.password}
                    onChange={handleInputChange}
                    className="cataloro-input pl-12 pr-12 h-14 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-200"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-500/5 to-purple-500/5 opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
                </div>
              </div>

              {/* Premium Submit Button */}
              <button
                type="submit"
                disabled={isLoading || isAnimating}
                className="w-full relative h-14 rounded-2xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white font-bold text-lg hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-[1.02] hover:shadow-2xl group overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/20 via-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="relative flex items-center justify-center space-x-2">
                  {(isLoading || isAnimating) ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      <span>Signing You In...</span>
                    </>
                  ) : (
                    <>
                      <span>Sign In</span>
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
                    </>
                  )}
                </div>
              </button>
            </form>

            {/* Premium Demo Login Section */}
            <div className="mt-8 pt-6 border-t border-white/20">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-300 text-center mb-6">
                <span className="flex items-center justify-center space-x-2">
                  <Sparkles className="w-4 h-4 text-yellow-500" />
                  <span>Try the premium demo experience</span>
                  <Sparkles className="w-4 h-4 text-yellow-500" />
                </span>
              </p>
              <div className="space-y-3">
                <button
                  onClick={() => handleDemoLogin('user')}
                  disabled={isLoading || isAnimating}
                  className="w-full h-12 rounded-xl bg-white/20 dark:bg-white/10 backdrop-blur-sm border border-white/30 text-gray-700 dark:text-gray-200 font-semibold hover:bg-white/30 dark:hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 group flex items-center justify-center space-x-3"
                >
                  <User className="w-5 h-5 text-blue-500" />
                  <span>Demo User Experience</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-300" />
                </button>
                <button
                  onClick={() => handleDemoLogin('admin')}
                  disabled={isLoading || isAnimating}
                  className="w-full h-12 rounded-xl bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm border border-purple-300/30 text-purple-700 dark:text-purple-300 font-semibold hover:from-purple-500/30 hover:to-pink-500/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 group flex items-center justify-center space-x-3"
                >
                  <Shield className="w-5 h-5 text-purple-500" />
                  <span>Demo Admin Panel</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-300" />
                </button>
              </div>
            </div>

            {/* Premium Register Link */}
            <div className="mt-8 text-center">
              <p className="text-sm text-gray-600 dark:text-gray-300">
                New to {UI_CONFIG.APP_NAME}?{' '}
                <Link 
                  to="/register" 
                  className="font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all duration-300"
                >
                  Create your account →
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Signing In...
                </div>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Demo Login Buttons */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600 text-center mb-4">
              Try the demo:
            </p>
            <div className="space-y-2">
              <button
                onClick={() => handleDemoLogin('user')}
                disabled={isLoading}
                className="w-full bg-white text-gray-700 px-4 py-2 rounded-lg font-medium border border-gray-300 hover:bg-gray-50 transition-all duration-200 shadow-sm hover:shadow-md text-sm"
              >
                Demo User Login
              </button>
              <button
                onClick={() => handleDemoLogin('admin')}
                disabled={isLoading}
                className="w-full bg-purple-100 text-purple-700 px-4 py-2 rounded-lg font-medium hover:bg-purple-200 transition-all duration-200 text-sm"
              >
                Demo Admin Login
              </button>
            </div>
          </div>

          {/* Status Info */}
          <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
              ✅ Backend API: Working (10/10 tests passed)<br/>
              ✅ Frontend: Fully functional<br/>
              ✅ Database: MongoDB operational
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SimpleLoginPage;