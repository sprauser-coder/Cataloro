import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Bell, Heart, Search, User } from 'lucide-react';

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [siteSettings, setSiteSettings] = useState({
    site_name: 'Cataloro',
    header_logo_url: '',
    primary_color: '#8b5cf6'
  });

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/20 bg-gradient-to-r from-purple-600 via-purple-700 to-indigo-800 backdrop-blur-md">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/20 backdrop-blur-sm">
              {siteSettings.header_logo_url ? (
                <img 
                  src={siteSettings.header_logo_url} 
                  alt={siteSettings.site_name}
                  className="h-8 w-8 object-contain"
                />
              ) : (
                <div className="text-2xl">📦</div>
              )}
            </div>
            <span className="text-xl font-light text-white tracking-tight">
              {siteSettings.site_name}
            </span>
          </Link>

          {/* Navigation */}
          {user ? (
            <div className="flex items-center space-x-1">
              <nav className="hidden md:flex items-center space-x-1">
                <Link 
                  to="/browse" 
                  className="px-4 py-2 text-purple-100 hover:text-white hover:bg-purple-500/20 rounded-xl backdrop-blur-sm transition-all duration-300 font-light"
                >
                  Browse
                </Link>
                <Link 
                  to="/sell" 
                  className="px-4 py-2 text-purple-100 hover:text-white hover:bg-purple-500/20 rounded-xl backdrop-blur-sm transition-all duration-300 font-light"
                >
                  Sell
                </Link>
                <Link 
                  to="/orders" 
                  className="px-4 py-2 text-purple-100 hover:text-white hover:bg-purple-500/20 rounded-xl backdrop-blur-sm transition-all duration-300 font-light"
                >
                  My Orders
                </Link>
                {user?.role === 'admin' && (
                  <Link 
                    to="/admin" 
                    className="px-4 py-2 text-red-300 hover:text-red-200 hover:bg-red-500/10 rounded-xl backdrop-blur-sm transition-all duration-300 font-light border border-red-400/30"
                  >
                    Admin Panel
                  </Link>
                )}
              </nav>

              {/* User Actions */}
              <div className="flex items-center space-x-3 ml-4">
                <Link to="/favorites" className="p-2 text-purple-100 hover:text-white hover:bg-purple-500/20 rounded-xl transition-colors">
                  <Heart className="h-5 w-5" />
                </Link>
                
                <div className="p-2 text-purple-100 hover:text-white hover:bg-purple-500/20 rounded-xl transition-colors cursor-pointer">
                  <Bell className="h-5 w-5" />
                </div>

                <Link to="/profile" className="flex items-center space-x-2 hover:bg-purple-500/20 rounded-xl px-3 py-2 transition-colors">
                  <Avatar className="h-8 w-8 ring-2 ring-white/30">
                    <AvatarImage src={user?.avatar_url} />
                    <AvatarFallback className="bg-purple-500 text-white text-sm">
                      {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                    </AvatarFallback>
                  </Avatar>
                  <span className="hidden md:block text-sm text-purple-100 font-light">
                    {user?.full_name || user?.email}
                  </span>
                </Link>

                <Button 
                  onClick={handleLogout}
                  variant="ghost" 
                  size="sm"
                  className="text-purple-100 hover:text-white hover:bg-purple-500/20 font-light"
                >
                  Logout
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <Link to="/auth">
                <Button variant="ghost" className="text-purple-100 hover:text-white hover:bg-purple-500/20 font-light">
                  Sign In
                </Button>
              </Link>
              <Link to="/auth">
                <Button className="bg-white text-purple-700 hover:bg-purple-50 font-light">
                  Get Started
                </Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;