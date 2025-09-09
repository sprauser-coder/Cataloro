/**
 * CATALORO - Mobile Hero Section Component
 * Simplified mobile hero with background styling support
 */

import React, { useState, useEffect } from 'react';
import { Search, Filter, Zap, TrendingUp } from 'lucide-react';
import MobileSearchBar from '../layout/MobileSearchBar';

function MobileHeroSection({ 
  onSearch, 
  onFilterToggle, 
  quickStats = {},
  className = "" 
}) {
  const [heroContent, setHeroContent] = useState({
    title: 'Find Catalysts',
    description: 'Discover quality catalytic converters',
    search_placeholder: 'Search catalysts...',
    height: 200, // Reduced height for mobile
    background_type: 'gradient',
    background_gradient_from: '#3f6ec7',
    background_gradient_to: '#ec4899',
    background_color: '#3B82F6',
    background_image: '',
    gradient_opacity: 0.8,
    background_size: 'cover',
    background_repeat: 'no-repeat',
    background_position: 'center',
    display_mode: 'full_width'
  });

  // Load hero content from localStorage
  useEffect(() => {
    const loadHeroContent = () => {
      const savedHeroContent = localStorage.getItem('cataloro_hero_content');
      if (savedHeroContent) {
        try {
          const parsed = JSON.parse(savedHeroContent);
          setHeroContent(prev => ({
            ...prev,
            ...parsed,
            height: Math.min(parsed.height || 200, 250) // Cap mobile height
          }));
        } catch (error) {
          console.error('Error parsing hero content:', error);
        }
      }
    };

    loadHeroContent();

    // Listen for hero content updates
    const handleHeroUpdate = (event) => {
      if (event.detail) {
        setHeroContent(prev => ({
          ...prev,
          ...event.detail,
          height: Math.min(event.detail.height || 200, 250) // Cap mobile height
        }));
      }
    };

    window.addEventListener('heroContentUpdated', handleHeroUpdate);
    return () => window.removeEventListener('heroContentUpdated', handleHeroUpdate);
  }, []);

  // Generate mobile hero background style
  const getMobileHeroBackgroundStyle = () => {
    const hexToRgba = (hex, opacity) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      if (!result) return hex;
      const r = parseInt(result[1], 16);
      const g = parseInt(result[2], 16);
      const b = parseInt(result[3], 16);
      return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    };

    const gradientOpacity = heroContent.gradient_opacity || 0.8;
    
    const baseStyle = {
      height: `${heroContent.height}px`,
      minHeight: '220px', // Increased minimum height to prevent text cutoff
      maxHeight: '280px', // Slightly increased max height
      marginTop: '-1rem',
      marginBottom: '1rem',
      marginLeft: 'calc(-50vw + 50%)',
      marginRight: 'calc(-50vw + 50%)'
    };

    // Add background image styling properties for image and image-gradient types
    if (heroContent.background_type === 'image' || heroContent.background_type === 'image-gradient') {
      baseStyle.backgroundSize = heroContent.background_size || 'cover';
      baseStyle.backgroundPosition = heroContent.background_position || 'center';
      baseStyle.backgroundRepeat = heroContent.background_repeat || 'no-repeat';
    }

    switch (heroContent.background_type) {
      case 'gradient':
        return {
          ...baseStyle,
          backgroundImage: `linear-gradient(to right, ${heroContent.background_gradient_from || '#3f6ec7'}, ${heroContent.background_gradient_to || '#ec4899'})`
        };
      case 'solid':
        return {
          ...baseStyle,
          backgroundColor: heroContent.background_color || '#3B82F6'
        };
      case 'image':
        return {
          ...baseStyle,
          backgroundImage: heroContent.background_image 
            ? `linear-gradient(rgba(0,0,0,${gradientOpacity * 0.5}), rgba(0,0,0,${gradientOpacity * 0.5})), url(${heroContent.background_image})`
            : 'linear-gradient(to right, #3f6ec7, #a855f7, #ec4899)'
        };
      case 'image-gradient':
        const gradientFromRgba = hexToRgba(heroContent.background_gradient_from || '#3f6ec7', gradientOpacity);
        const gradientToRgba = hexToRgba(heroContent.background_gradient_to || '#ec4899', gradientOpacity);
        
        return {
          ...baseStyle,
          backgroundImage: heroContent.background_image 
            ? `linear-gradient(to right, ${gradientFromRgba}, ${gradientToRgba}), url(${heroContent.background_image})`
            : `linear-gradient(to right, ${heroContent.background_gradient_from || '#3f6ec7'}, ${heroContent.background_gradient_to || '#ec4899'})`
        };
      default:
        return {
          ...baseStyle,
          backgroundImage: 'linear-gradient(to right, #3f6ec7, #a855f7, #ec4899)'
        };
    }
  };

  return (
    <div className={`lg:hidden ${className}`}>
      {/* Mobile Hero Section */}
      <div 
        className="hero-section relative text-white overflow-hidden w-screen"
        style={getMobileHeroBackgroundStyle()}
      >
        <div className="absolute inset-0 bg-black/20"></div>
        
        <div className="relative z-10 flex flex-col justify-center h-full px-6 py-6 max-w-7xl mx-auto">
          {/* Hero Image - displayed over text if image_url exists */}
          {heroContent.image_url && (
            <div className="mb-3 flex justify-center">
              <img 
                src={heroContent.image_url} 
                alt="Hero" 
                className="max-h-14 max-w-28 object-contain" 
              />
            </div>
          )}
          
          {/* Title and Description - Better spacing for mobile */}
          <div className="text-center mb-5">
            <h1 className="text-2xl md:text-3xl font-bold mb-3 leading-tight">
              {heroContent.title || 'Find Catalysts'}
            </h1>
            <p className="text-base opacity-95 max-w-xs mx-auto leading-relaxed">
              {heroContent.description || 'Discover quality catalytic converters'}
            </p>
          </div>
          
          {/* Mobile Search Bar */}
          <div className="mb-4">
            <MobileSearchBar
              onSearch={onSearch}
              placeholder={heroContent.search_placeholder || 'Search catalysts...'}
            />
          </div>

          {/* Quick Actions Row */}
          <div className="flex justify-center space-x-3">
            <button
              onClick={onFilterToggle}
              className="flex items-center space-x-2 px-4 py-2 bg-white/20 backdrop-blur-sm text-white rounded-lg hover:bg-white/30 transition-colors"
            >
              <Filter className="w-4 h-4" />
              <span className="text-sm">Filters</span>
            </button>
            
            {quickStats.hotDeals > 0 && (
              <div className="flex items-center space-x-2 px-4 py-2 bg-red-500/80 backdrop-blur-sm text-white rounded-lg">
                <Zap className="w-4 h-4" />
                <span className="text-sm">{quickStats.hotDeals} Hot Deals</span>
              </div>
            )}
            
            {quickStats.trending > 0 && (
              <div className="flex items-center space-x-2 px-4 py-2 bg-green-500/80 backdrop-blur-sm text-white rounded-lg">
                <TrendingUp className="w-4 h-4" />
                <span className="text-sm">Trending</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Stats Bar - Optional */}
      {Object.keys(quickStats).length > 0 && (
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
          <div className="flex justify-around text-center">
            {quickStats.totalListings && (
              <div>
                <p className="text-lg font-bold text-gray-900 dark:text-white">
                  {quickStats.totalListings}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Total</p>
              </div>
            )}
            {quickStats.newToday && (
              <div>
                <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
                  {quickStats.newToday}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">New Today</p>
              </div>
            )}
            {quickStats.hotDeals && (
              <div>
                <p className="text-lg font-bold text-red-600 dark:text-red-400">
                  {quickStats.hotDeals}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Hot Deals</p>
              </div>
            )}
            {quickStats.avgPrice && (
              <div>
                <p className="text-lg font-bold text-green-600 dark:text-green-400">
                  €{quickStats.avgPrice}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Avg Price</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default MobileHeroSection;