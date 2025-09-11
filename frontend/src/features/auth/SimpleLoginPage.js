/**
 * CATALORO - Ultra-Modern Login Page with Liquid Glass Optics
 * Advanced glassmorphism design with animated backgrounds and admin logo
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, Store, ArrowRight, User, UserPlus, Sparkles, Zap } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

function SimpleLoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [activeTab, setActiveTab] = useState('login'); // 'login' or 'register'
  const [logoUrl, setLogoUrl] = useState(null);
  
  // Login form state
  const [loginData, setLoginData] = useState({
    email: '',
    password: ''
  });
  
  // Registration form state
  const [registerData, setRegisterData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: ''
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch admin logo and check if user is already logged in
  useEffect(() => {
    const fetchLogo = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'https://marketplace-debug-3.preview.emergentagent.com/api'}/admin/logo`);
        if (response.ok) {
          const data = await response.json();
          if (data.logo_url) {
            setLogoUrl(data.logo_url);
          }
        }
      } catch (error) {
        console.log('No admin logo found, using default');
      }
    };

    // Check if user is already logged in
    const token = localStorage.getItem('cataloro_token');
    const user = localStorage.getItem('cataloro_user');
    if (token && user) {
      try {
        const userData = JSON.parse(user);
        if (userData.role === 'admin') {
          navigate('/admin');
        } else {
          navigate('/browse');
        }
      } catch (e) {
        localStorage.removeItem('cataloro_token');
        localStorage.removeItem('cataloro_user');
      }
    }

    fetchLogo();
  }, [navigate]);

  const handleLoginChange = (e) => {
    setLoginData({
      ...loginData,
      [e.target.name]: e.target.value
    });
    setError(null);
  };

  const handleRegisterChange = (e) => {
    setRegisterData({
      ...registerData,
      [e.target.name]: e.target.value
    });
    setError(null);
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    try {
      // Call the actual backend API
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: loginData.email,
          password: loginData.password
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
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    // Validation
    if (registerData.password !== registerData.confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    if (registerData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL || 'https://marketplace-debug-3.preview.emergentagent.com/api'}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: registerData.username,
          email: registerData.email,
          password: registerData.password,
          first_name: registerData.firstName,
          last_name: registerData.lastName,
          full_name: `${registerData.firstName} ${registerData.lastName}`.trim()
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Registration failed: ${response.status}`);
      }

      const data = await response.json();
      
      // Auto-login after successful registration
      localStorage.setItem('cataloro_token', data.token);
      localStorage.setItem('cataloro_user', JSON.stringify(data.user));
      
      // Redirect to marketplace
      window.location.href = '/browse';
      
    } catch (error) {
      setError(error.message || 'Registration failed. Please try again.');
      console.error('Registration error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Ultra-Modern Animated Background */}
      <div className="absolute inset-0">
        {/* Primary gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/80 via-purple-900/80 to-pink-900/80"></div>
        
        {/* Animated liquid shapes */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden">
          <div className="absolute -top-40 -left-40 w-80 h-80 bg-gradient-to-r from-cyan-400/30 to-blue-500/30 rounded-full blur-3xl animate-blob"></div>
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-r from-purple-400/30 to-pink-500/30 rounded-full blur-3xl animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-40 left-1/2 transform -translate-x-1/2 w-80 h-80 bg-gradient-to-r from-emerald-400/30 to-cyan-500/30 rounded-full blur-3xl animate-blob animation-delay-4000"></div>
        </div>
        
        {/* Floating particles */}
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
          <div className="absolute top-1/3 right-1/4 w-1 h-1 bg-purple-400 rounded-full animate-ping animation-delay-1000"></div>
          <div className="absolute bottom-1/3 left-1/3 w-1.5 h-1.5 bg-pink-400 rounded-full animate-pulse animation-delay-2000"></div>
          <div className="absolute top-2/3 right-1/3 w-1 h-1 bg-emerald-400 rounded-full animate-ping animation-delay-3000"></div>
        </div>
        
        {/* Grid pattern overlay */}
        <div className="absolute inset-0 opacity-30">
          <div className="w-2 h-2 bg-white/5 rounded-full absolute top-10 left-10"></div>
          <div className="w-1 h-1 bg-white/5 rounded-full absolute top-20 left-32"></div>
          <div className="w-1.5 h-1.5 bg-white/5 rounded-full absolute top-32 left-16"></div>
          <div className="w-1 h-1 bg-white/5 rounded-full absolute top-40 left-48"></div>
        </div>
      </div>
      
      <div className="relative min-h-screen flex items-center justify-center p-4 z-10">
        <div className="w-full max-w-md">
          {/* Logo and Header */}
          <div className="text-center mb-8">
            <div className="mb-6 relative">
              {logoUrl ? (
                <div className="relative">
                  <div className="w-20 h-20 mx-auto bg-white/10 backdrop-blur-xl rounded-3xl border border-white/20 flex items-center justify-center p-2">
                    <img 
                      src={logoUrl} 
                      alt="Company Logo" 
                      className="max-w-full max-h-full object-contain"
                    />
                  </div>
                  {/* Glowing effect */}
                  <div className="absolute inset-0 w-20 h-20 mx-auto bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-3xl blur-xl animate-pulse"></div>
                  <Sparkles className="absolute -top-2 -right-2 w-6 h-6 text-cyan-400 animate-spin" style={{ animationDuration: '3s' }} />
                </div>
              ) : (
                <div className="relative">
                  <div className="w-20 h-20 mx-auto bg-gradient-to-br from-cyan-500/20 to-purple-500/20 backdrop-blur-xl rounded-3xl border border-white/20 flex items-center justify-center">
                    <Store className="w-10 h-10 text-white drop-shadow-lg" />
                  </div>
                  {/* Glowing effect */}
                  <div className="absolute inset-0 w-20 h-20 mx-auto bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-3xl blur-xl animate-pulse"></div>
                  <Sparkles className="absolute -top-2 -right-2 w-6 h-6 text-cyan-400 animate-spin" style={{ animationDuration: '3s' }} />
                </div>
              )}
            </div>
            <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-cyan-200 to-purple-200 mb-2">
              Welcome to Cataloro
            </h1>
            <p className="text-gray-300/80 text-lg">
              Your premium marketplace experience
            </p>
          </div>

          {/* Ultra-Modern Glass Card */}
          <div className="relative">
            {/* Glass morphism background */}
            <div className="absolute inset-0 bg-white/5 backdrop-blur-2xl rounded-3xl border border-white/10"></div>
            
            {/* Inner glow effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-purple-500/5 rounded-3xl"></div>
            
            {/* Content */}
            <div className="relative p-8">
              {/* Liquid Tab Selector */}
              <div className="flex mb-8 relative">
                <div className="absolute inset-0 bg-white/5 rounded-2xl"></div>
                <button
                  type="button"
                  onClick={() => setActiveTab('login')}
                  className={`relative flex-1 py-4 px-6 text-center font-semibold rounded-xl transition-all duration-500 ${
                    activeTab === 'login'
                      ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-white shadow-lg transform scale-105'
                      : 'text-gray-300/70'
                  }`}
                >
                  <User className="w-5 h-5 inline mr-2" />
                  Sign In
                  {activeTab === 'login' && (
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-xl blur-lg"></div>
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('register')}
                  className={`relative flex-1 py-4 px-6 text-center font-semibold rounded-xl transition-all duration-500 ${
                    activeTab === 'register'
                      ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-white shadow-lg transform scale-105'
                      : 'text-gray-300/70'
                  }`}
                >
                  <UserPlus className="w-5 h-5 inline mr-2" />
                  Sign Up
                  {activeTab === 'register' && (
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-xl blur-lg"></div>
                  )}
                </button>
              </div>

              {/* Error Message */}
              {error && (
                <div className="mb-6 p-4 bg-red-500/10 backdrop-blur-sm border border-red-500/20 rounded-2xl">
                  <p className="text-red-300 text-sm font-medium">{error}</p>
                </div>
              )}

              {/* Login Form */}
              {activeTab === 'login' && (
                <form onSubmit={handleLoginSubmit} className="space-y-6">
                  <div>
                    <label className="block text-sm font-semibold text-gray-200 mb-3">
                      Email Address
                    </label>
                    <div className="relative group">
                      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-2xl blur-lg group-focus-within:blur-xl transition-all duration-300"></div>
                      <div className="relative">
                        <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 z-10" />
                        <input
                          type="email"
                          name="email"
                          value={loginData.email}
                          onChange={handleLoginChange}
                          required
                          className="w-full pl-12 pr-4 py-4 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 text-white placeholder-gray-400 transition-all duration-300"
                          placeholder="Enter your email"
                        />
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-200 mb-3">
                      Password
                    </label>
                    <div className="relative group">
                      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-2xl blur-lg group-focus-within:blur-xl transition-all duration-300"></div>
                      <div className="relative">
                        <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 z-10" />
                        <input
                          type={showPassword ? 'text' : 'password'}
                          name="password"
                          value={loginData.password}
                          onChange={handleLoginChange}
                          required
                          className="w-full pl-12 pr-14 py-4 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 text-white placeholder-gray-400 transition-all duration-300"
                          placeholder="Enter your password"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 z-10"
                        >
                          {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                      </div>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="relative w-full py-4 px-6 bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-semibold rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden group"
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-600 to-purple-600 opacity-0 group-active:opacity-100 transition-opacity duration-200"></div>
                    <div className="relative flex items-center justify-center">
                      {isLoading ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                          Signing In...
                        </>
                      ) : (
                        <>
                          Sign In
                          <ArrowRight className="w-5 h-5 ml-3" />
                        </>
                      )}
                    </div>
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-2xl blur-xl"></div>
                  </button>
                </form>
              )}

              {/* Registration Form */}
              {activeTab === 'register' && (
                <form onSubmit={handleRegisterSubmit} className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-200 mb-3">
                        First Name
                      </label>
                      <div className="relative group">
                        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-2xl blur-lg group-focus-within:blur-xl transition-all duration-300"></div>
                        <div className="relative">
                          <User className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 z-10" />
                          <input
                            type="text"
                            name="firstName"
                            value={registerData.firstName}
                            onChange={handleRegisterChange}
                            required
                            className="w-full pl-12 pr-4 py-4 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 text-white placeholder-gray-400 transition-all duration-300"
                            placeholder="First name"
                          />
                        </div>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-200 mb-3">
                        Last Name
                      </label>
                      <div className="relative group">
                        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-2xl blur-lg group-focus-within:blur-xl transition-all duration-300"></div>
                        <div className="relative">
                          <User className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 z-10" />
                          <input
                            type="text"
                            name="lastName"
                            value={registerData.lastName}
                            onChange={handleRegisterChange}
                            required
                            className="w-full pl-12 pr-4 py-4 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 text-white placeholder-gray-400 transition-all duration-300"
                            placeholder="Last name"
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-200 mb-3">
                      Username
                    </label>
                    <div className="relative group">
                      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-2xl blur-lg group-focus-within:blur-xl transition-all duration-300"></div>
                      <div className="relative">
                        <User className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 z-10" />
                        <input
                          type="text"
                          name="username"
                          value={registerData.username}
                          onChange={handleRegisterChange}
                          required
                          className="w-full pl-12 pr-4 py-4 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 text-white placeholder-gray-400 transition-all duration-300"
                          placeholder="Choose a username"
                        />
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-200 mb-3">
                      Email Address
                    </label>
                    <div className="relative group">
                      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-2xl blur-lg group-focus-within:blur-xl transition-all duration-300"></div>
                      <div className="relative">
                        <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 z-10" />
                        <input
                          type="email"
                          name="email"
                          value={registerData.email}
                          onChange={handleRegisterChange}
                          required
                          className="w-full pl-12 pr-4 py-4 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 text-white placeholder-gray-400 transition-all duration-300"
                          placeholder="Enter your email"
                        />
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-200 mb-3">
                      Password
                    </label>
                    <div className="relative group">
                      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-2xl blur-lg group-focus-within:blur-xl transition-all duration-300"></div>
                      <div className="relative">
                        <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 z-10" />
                        <input
                          type={showPassword ? 'text' : 'password'}
                          name="password"
                          value={registerData.password}
                          onChange={handleRegisterChange}
                          required
                          minLength={6}
                          className="w-full pl-12 pr-14 py-4 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 text-white placeholder-gray-400 transition-all duration-300"
                          placeholder="Create a password (min 6 characters)"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 z-10"
                        >
                          {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-200 mb-3">
                      Confirm Password
                    </label>
                    <div className="relative group">
                      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-2xl blur-lg group-focus-within:blur-xl transition-all duration-300"></div>
                      <div className="relative">
                        <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 z-10" />
                        <input
                          type={showPassword ? 'text' : 'password'}
                          name="confirmPassword"
                          value={registerData.confirmPassword}
                          onChange={handleRegisterChange}
                          required
                          className="w-full pl-12 pr-4 py-4 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20 text-white placeholder-gray-400 transition-all duration-300"
                          placeholder="Confirm your password"
                        />
                      </div>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="relative w-full py-4 px-6 bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-semibold rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden group"
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-600 to-purple-600 opacity-0 group-active:opacity-100 transition-opacity duration-200"></div>
                    <div className="relative flex items-center justify-center">
                      {isLoading ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                          Creating Account...
                        </>
                      ) : (
                        <>
                          Create Account
                          <UserPlus className="w-5 h-5 ml-3" />
                        </>
                      )}
                    </div>
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-2xl blur-xl"></div>
                  </button>
                </form>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="text-center mt-8">
            <p className="text-sm text-gray-400/60">
              © 2024 Cataloro. Premium marketplace experience.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SimpleLoginPage;