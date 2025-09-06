/**
 * CATALORO - Ultra-Modern Login Page
 * Premium glassmorphism design with advanced animations
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, Store, ArrowRight, Shield, User, Sparkles } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { APP_ROUTES, UI_CONFIG } from '../../config/directions';

function LoginPage() {
  const { login, isLoading, error, clearError } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  // Clear errors when component mounts
  useEffect(() => {
    clearError();
  }, [clearError]);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    clearError(); // Clear errors on input change
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsAnimating(true);
    try {
      await login(formData.email, formData.password);
      navigate(APP_ROUTES.BROWSE);
    } catch (error) {
      console.error('Login failed:', error);
      setIsAnimating(false);
    }
  };

  const handleDemoLogin = async (role = 'user') => {
    const demoCredentials = {
      email: role === 'admin' ? 'admin@cataloro.com' : 'user@cataloro.com',
      password: 'demo123'
    };
    
    setIsAnimating(true);
    try {
      const response = await login(demoCredentials.email, demoCredentials.password);
      
      // Check if user is admin and redirect accordingly
      if (response?.user?.role === 'admin' || response?.user?.email === 'admin@cataloro.com') {
        navigate(APP_ROUTES.ADMIN_PANEL);
      } else {
        navigate(APP_ROUTES.BROWSE);
      }
    } catch (error) {
      console.error('Demo login failed:', error);
      setIsAnimating(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Ultra-Modern Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-100 dark:from-gray-900 dark:via-blue-900 dark:to-purple-900">
        <div className="absolute inset-0 bg-gradient-to-tr from-blue-400/20 via-purple-400/20 to-pink-400/20 animate-pulse"></div>
        <div className="absolute top-0 left-0 w-full h-full">
          {/* Background decorative elements - simplified */}
          <div className="absolute top-20 left-20 w-72 h-72 bg-blue-300/30 rounded-full mix-blend-multiply opacity-70"></div>
          <div className="absolute top-40 right-20 w-72 h-72 bg-purple-300/30 rounded-full mix-blend-multiply opacity-70"></div>
          <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300/30 rounded-full mix-blend-multiply opacity-70"></div>
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
                  <div className="w-full h-full rounded-3xl bg-white/10 flex items-center justify-center">
                    <Store className="w-10 h-10 text-white drop-shadow-lg" />
                  </div>
                </div>
                {/* Animated Glow */}
                <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 opacity-50"></div>
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
          <div className="cataloro-card-glass p-8 border-white/30">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Enhanced Error Display */}
              {error && (
                <div className="bg-red-500/10 border border-red-300/30 text-red-700 dark:text-red-300 px-5 py-4 rounded-2xl">
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
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-blue-500 w-5 h-5" />
                  <input
                    type="email"
                    name="email"
                    required
                    value={formData.email}
                    onChange={handleInputChange}
                    className="cataloro-input pl-12 h-14 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500/50"
                    placeholder="Enter your email address"
                  />
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-500/5 to-purple-500/5 opacity-0 group-focus-within:opacity-100 pointer-events-none"></div>
                </div>
              </div>

              {/* Premium Password Field */}
              <div className="space-y-2">
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-200">
                  Password
                </label>
                <div className="relative group">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-blue-500 w-5 h-5" />
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
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-500/5 to-purple-500/5 opacity-0 group-focus-within:opacity-100 pointer-events-none"></div>
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
                  to={APP_ROUTES.REGISTER} 
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

export default LoginPage;