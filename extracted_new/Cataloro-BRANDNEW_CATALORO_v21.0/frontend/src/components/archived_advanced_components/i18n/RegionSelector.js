import React, { useState, useEffect } from 'react';
import { MapPin, ChevronDown, Check, DollarSign, Shield } from 'lucide-react';

const RegionSelector = ({ 
  selectedRegion = 'US', 
  onRegionChange,
  showCurrency = true,
  showCompliance = false,
  size = 'medium',
  position = 'bottom-left',
  className = ''
}) => {
  const [regions, setRegions] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSupportedRegions();
  }, []);

  const fetchSupportedRegions = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/v2/phase6/i18n/regions`);
      
      if (response.ok) {
        const data = await response.json();
        setRegions(data.regions || []);
      }
    } catch (error) {
      console.error('Failed to fetch regions:', error);
      // Fallback regions
      setRegions([
        { code: 'US', name: 'United States', currency: 'USD', tax_rate: 8.25, compliance_requirements: ['CCPA', 'SOX'] },
        { code: 'GB', name: 'United Kingdom', currency: 'GBP', tax_rate: 20.0, compliance_requirements: ['GDPR'] },
        { code: 'DE', name: 'Germany', currency: 'EUR', tax_rate: 19.0, compliance_requirements: ['GDPR'] },
        { code: 'FR', name: 'France', currency: 'EUR', tax_rate: 20.0, compliance_requirements: ['GDPR'] }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleRegionSelect = (region) => {
    setIsOpen(false);
    if (onRegionChange) {
      onRegionChange(region);
    }
    
    // Store in localStorage
    localStorage.setItem('preferred_region', region.code);
  };

  const selectedRegionData = regions.find(r => r.code === selectedRegion) || regions[0];

  const getSizeClasses = () => {
    switch (size) {
      case 'small':
        return {
          button: 'px-2 py-1 text-sm',
          dropdown: 'w-64',
          text: 'text-sm'
        };
      case 'large':
        return {
          button: 'px-4 py-3 text-lg',
          dropdown: 'w-80',
          text: 'text-lg'
        };
      default:
        return {
          button: 'px-3 py-2 text-base',
          dropdown: 'w-72',
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

  const getCurrencySymbol = (currency) => {
    const symbols = {
      'USD': '$',
      'EUR': '€',
      'GBP': '£',
      'JPY': '¥',
      'CAD': 'C$',
      'AUD': 'A$',
      'CHF': 'CHF',
      'CNY': '¥',
      'BRL': 'R$'
    };
    return symbols[currency] || currency;
  };

  const sizeClasses = getSizeClasses();
  const positionClasses = getPositionClasses();

  if (loading || !selectedRegionData) {
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
          <MapPin className="w-4 h-4 text-gray-500" />
          <span className={`font-medium text-gray-900 dark:text-white ${sizeClasses.text}`}>
            {selectedRegionData.name}
          </span>
          {showCurrency && (
            <span className={`text-gray-600 dark:text-gray-400 ${sizeClasses.text}`}>
              ({getCurrencySymbol(selectedRegionData.currency)})
            </span>
          )}
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
                Select Region
              </div>
              
              {regions.map((region) => (
                <button
                  key={region.code}
                  onClick={() => handleRegionSelect(region)}
                  className={`
                    w-full flex items-start space-x-3 px-3 py-3 rounded-md
                    hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors
                    ${selectedRegion === region.code 
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300' 
                      : 'text-gray-900 dark:text-white'
                    }
                  `}
                >
                  <div className="flex-1 text-left">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{region.name}</span>
                      {selectedRegion === region.code && (
                        <Check className="w-4 h-4 text-blue-500" />
                      )}
                    </div>
                    
                    <div className="mt-1 space-y-1">
                      {showCurrency && (
                        <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
                          <DollarSign className="w-3 h-3" />
                          <span>Currency: {region.currency} ({getCurrencySymbol(region.currency)})</span>
                          <span>• Tax: {region.tax_rate}%</span>
                        </div>
                      )}
                      
                      {showCompliance && region.compliance_requirements && region.compliance_requirements.length > 0 && (
                        <div className="flex items-start space-x-2 text-xs text-gray-600 dark:text-gray-400">
                          <Shield className="w-3 h-3 mt-0.5" />
                          <div>
                            <span>Compliance: </span>
                            <span>{region.compliance_requirements.slice(0, 2).join(', ')}</span>
                            {region.compliance_requirements.length > 2 && (
                              <span> +{region.compliance_requirements.length - 2} more</span>
                            )}
                          </div>
                        </div>
                      )}
                      
                      {region.supported_languages && (
                        <div className="text-xs text-gray-600 dark:text-gray-400">
                          Languages: {region.supported_languages.join(', ')}
                        </div>
                      )}
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

export default RegionSelector;