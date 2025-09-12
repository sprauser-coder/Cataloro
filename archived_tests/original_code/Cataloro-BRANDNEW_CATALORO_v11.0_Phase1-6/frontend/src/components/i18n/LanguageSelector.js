import React, { useState, useEffect } from 'react';
import { Globe, ChevronDown, Check } from 'lucide-react';

const LanguageSelector = ({ 
  selectedLanguage = 'en', 
  onLanguageChange,
  showNativeName = true,
  size = 'medium',
  position = 'bottom-left',
  className = ''
}) => {
  const [languages, setLanguages] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSupportedLanguages();
  }, []);

  const fetchSupportedLanguages = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/v2/phase6/i18n/languages`);
      
      if (response.ok) {
        const data = await response.json();
        setLanguages(data.languages || []);
      }
    } catch (error) {
      console.error('Failed to fetch languages:', error);
      // Fallback languages
      setLanguages([
        { code: 'en', name: 'English', native_name: 'English', completion_percentage: 100 },
        { code: 'es', name: 'Spanish', native_name: 'Español', completion_percentage: 95 },
        { code: 'fr', name: 'French', native_name: 'Français', completion_percentage: 90 },
        { code: 'de', name: 'German', native_name: 'Deutsch', completion_percentage: 85 }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleLanguageSelect = (language) => {
    setIsOpen(false);
    if (onLanguageChange) {
      onLanguageChange(language);
    }
    
    // Store in localStorage
    localStorage.setItem('preferred_language', language.code);
  };

  const selectedLanguageData = languages.find(l => l.code === selectedLanguage) || languages[0];

  const getSizeClasses = () => {
    switch (size) {
      case 'small':
        return {
          button: 'px-2 py-1 text-sm',
          dropdown: 'w-48',
          text: 'text-sm'
        };
      case 'large':
        return {
          button: 'px-4 py-3 text-lg',
          dropdown: 'w-72',
          text: 'text-lg'
        };
      default:
        return {
          button: 'px-3 py-2 text-base',
          dropdown: 'w-60',
          text: 'text-base'
        };
    }
  };

  const getPositionClasses = () => {
    switch (position) {
      case 'top-left':
        return 'bottom-full left-0 mb-1';
      case 'top-right':
        return 'bottom-full right-0 mb-1';
      case 'bottom-right':
        return 'top-full right-0 mt-1';
      default:
        return 'top-full left-0 mt-1';
    }
  };

  const sizeClasses = getSizeClasses();
  const positionClasses = getPositionClasses();

  if (loading || !selectedLanguageData) {
    return (
      <div className={`inline-flex items-center ${sizeClasses.button} bg-gray-100 dark:bg-gray-700 rounded-lg ${className}`}>
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
        <span className="ml-2 text-gray-600 dark:text-gray-400">Loading...</span>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          inline-flex items-center justify-between ${sizeClasses.button}
          bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600
          rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          transition-colors duration-200
        `}
      >
        <div className="flex items-center space-x-2">
          <Globe className="w-4 h-4 text-gray-500" />
          <span className={`font-medium text-gray-900 dark:text-white ${sizeClasses.text}`}>
            {showNativeName ? selectedLanguageData.native_name : selectedLanguageData.name}
          </span>
        </div>
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className={`absolute ${positionClasses} ${sizeClasses.dropdown} bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-600 z-20 max-h-80 overflow-y-auto`}>
            <div className="p-2">
              <div className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider px-3 py-2">
                Select Language
              </div>
              
              {languages.map((language) => (
                <button
                  key={language.code}
                  onClick={() => handleLanguageSelect(language)}
                  className={`
                    w-full flex items-center justify-between px-3 py-2 rounded-md
                    hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors
                    ${selectedLanguage === language.code 
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300' 
                      : 'text-gray-900 dark:text-white'
                    }
                  `}
                >
                  <div className="flex-1 text-left">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">
                        {showNativeName ? language.native_name : language.name}
                      </span>
                      {selectedLanguage === language.code && (
                        <Check className="w-4 h-4 text-blue-500" />
                      )}
                    </div>
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-xs text-gray-600 dark:text-gray-400">
                        {showNativeName ? language.name : language.native_name}
                      </span>
                      <div className="flex items-center space-x-2">
                        <div className="w-12 bg-gray-200 dark:bg-gray-600 rounded-full h-1">
                          <div 
                            className="bg-green-500 h-1 rounded-full"
                            style={{ width: `${language.completion_percentage}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-500 dark:text-gray-500">
                          {language.completion_percentage.toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default LanguageSelector;