import React, { useState, useEffect } from 'react';
import { Globe, ChevronDown, Check } from 'lucide-react';

const LanguageSwitcher = ({ className = '' }) => {
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [supportedLanguages, setSupportedLanguages] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLanguages();
    // Load saved language preference
    const savedLanguage = localStorage.getItem('selectedLanguage') || 'en';
    setCurrentLanguage(savedLanguage);
  }, []);

  const fetchLanguages = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/v2/advanced/i18n/languages`);
      const data = await response.json();
      
      if (data.success) {
        setSupportedLanguages(data.languages.filter(lang => lang.enabled));
      } else {
        // Fallback languages
        setSupportedLanguages([
          { code: 'en', name: 'English', native_name: 'English', enabled: true },
          { code: 'de', name: 'German', native_name: 'Deutsch', enabled: true },
          { code: 'fr', name: 'French', native_name: 'Français', enabled: true },
          { code: 'es', name: 'Spanish', native_name: 'Español', enabled: true }
        ]);
      }
    } catch (error) {
      console.error('Failed to fetch languages:', error);
      // Fallback languages
      setSupportedLanguages([
        { code: 'en', name: 'English', native_name: 'English', enabled: true },
        { code: 'de', name: 'German', native_name: 'Deutsch', enabled: true },
        { code: 'fr', name: 'French', native_name: 'Français', enabled: true },
        { code: 'es', name: 'Spanish', native_name: 'Español', enabled: true }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const changeLanguage = (languageCode) => {
    setCurrentLanguage(languageCode);
    localStorage.setItem('selectedLanguage', languageCode);
    setIsOpen(false);
    
    // Apply language change to document
    document.documentElement.lang = languageCode;
    
    // Trigger a custom event for other components to listen to
    window.dispatchEvent(new CustomEvent('languageChange', { 
      detail: { language: languageCode } 
    }));
    
    // For demo purposes, show a toast notification
    console.log(`Language changed to: ${languageCode}`);
  };

  const getCurrentLanguage = () => {
    return supportedLanguages.find(lang => lang.code === currentLanguage) || 
           supportedLanguages[0] || 
           { code: 'en', name: 'English', native_name: 'English' };
  };

  const getFlagEmoji = (languageCode) => {
    const flags = {
      'en': '🇺🇸',
      'de': '🇩🇪', 
      'fr': '🇫🇷',
      'es': '🇪🇸',
      'it': '🇮🇹',
      'pt': '🇵🇹',
      'nl': '🇳🇱',
      'da': '🇩🇰',
      'sv': '🇸🇪',
      'no': '🇳🇴',
      'fi': '🇫🇮',
      'pl': '🇵🇱'
    };
    return flags[languageCode] || '🌐';
  };

  if (loading) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <Globe className="w-4 h-4 animate-spin text-gray-400" />
      </div>
    );
  }

  const currentLang = getCurrentLanguage();

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
      >
        <span className="text-lg">{getFlagEmoji(currentLang.code)}</span>
        <span className="hidden md:inline">{currentLang.native_name}</span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown */}
          <div className="absolute right-0 top-full mt-2 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg z-20">
            <div className="py-2">
              {supportedLanguages.map((language) => (
                <button
                  key={language.code}
                  onClick={() => changeLanguage(language.code)}
                  className="w-full flex items-center justify-between px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{getFlagEmoji(language.code)}</span>
                    <div className="text-left">
                      <div className="font-medium">{language.native_name}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{language.name}</div>
                    </div>
                  </div>
                  {currentLanguage === language.code && (
                    <Check className="w-4 h-4 text-blue-600" />
                  )}
                </button>
              ))}
            </div>

            {/* Language Notice */}
            <div className="border-t border-gray-200 dark:border-gray-600 px-4 py-3">
              <div className="text-xs text-gray-500 dark:text-gray-400">
                🌍 Translation powered by AI
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default LanguageSwitcher;