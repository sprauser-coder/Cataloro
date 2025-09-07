import React, { useState, useEffect } from 'react';
import { DollarSign, Eye, EyeOff, Globe } from 'lucide-react';

const MultiCurrencyPrice = ({ 
  basePrice, 
  baseCurrency = 'EUR',
  showAlternativePrices = true,
  primaryCurrency = null,
  compact = false,
  className = ''
}) => {
  const [exchangeRates, setExchangeRates] = useState({});
  const [loading, setLoading] = useState(true);
  const [showAllCurrencies, setShowAllCurrencies] = useState(false);
  const [userPreferredCurrency, setUserPreferredCurrency] = useState(null);

  // Popular currencies to display
  const popularCurrencies = ['USD', 'GBP', 'CHF', 'CAD', 'JPY'];

  useEffect(() => {
    fetchExchangeRates();
    loadUserPreference();
  }, []);

  const fetchExchangeRates = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/v2/currency/rates`);
      const data = await response.json();
      
      if (data.success) {
        setExchangeRates(data.rates);
      }
    } catch (error) {
      console.error('Failed to fetch exchange rates:', error);
      // Fallback rates for common currencies
      setExchangeRates({
        'EUR': 1.0,
        'USD': 1.17,
        'GBP': 0.868,
        'CHF': 1.05,
        'CAD': 1.48,
        'JPY': 130.5
      });
    } finally {
      setLoading(false);
    }
  };

  const loadUserPreference = () => {
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
    const savedCurrency = localStorage.getItem('preferred_currency');
    
    if (primaryCurrency) {
      setUserPreferredCurrency(primaryCurrency);
    } else if (savedCurrency) {
      setUserPreferredCurrency(savedCurrency);
    }
  };

  const convertPrice = (price, fromCurrency, toCurrency) => {
    if (fromCurrency === toCurrency) return price;
    
    const fromRate = exchangeRates[fromCurrency] || 1;
    const toRate = exchangeRates[toCurrency] || 1;
    
    // Convert to EUR first, then to target currency
    const eurPrice = price / fromRate;
    return eurPrice * toRate;
  };

  const formatPrice = (price, currency) => {
    const symbols = {
      'EUR': '€',
      'USD': '$',
      'GBP': '£',
      'CHF': 'CHF',
      'CAD': 'C$',
      'JPY': '¥',
      'AUD': 'A$',
      'SEK': 'kr',
      'NOK': 'kr',
      'DKK': 'kr'
    };

    const symbol = symbols[currency] || currency;
    const formattedPrice = price.toLocaleString(undefined, {
      minimumFractionDigits: currency === 'JPY' ? 0 : 2,
      maximumFractionDigits: currency === 'JPY' ? 0 : 2
    });

    return `${symbol}${formattedPrice}`;
  };

  const getDisplayCurrency = () => {
    return userPreferredCurrency || baseCurrency;
  };

  const getPrimaryPrice = () => {
    const displayCurrency = getDisplayCurrency();
    const convertedPrice = convertPrice(basePrice, baseCurrency, displayCurrency);
    return {
      price: convertedPrice,
      currency: displayCurrency,
      formatted: formatPrice(convertedPrice, displayCurrency)
    };
  };

  const getAlternativePrices = () => {
    const displayCurrency = getDisplayCurrency();
    const currenciesToShow = showAllCurrencies 
      ? Object.keys(exchangeRates).filter(c => c !== displayCurrency)
      : popularCurrencies.filter(c => c !== displayCurrency);

    return currenciesToShow.map(currency => {
      const convertedPrice = convertPrice(basePrice, baseCurrency, currency);
      return {
        currency,
        price: convertedPrice,
        formatted: formatPrice(convertedPrice, currency)
      };
    }).slice(0, showAllCurrencies ? 10 : 3);
  };

  if (loading) {
    return (
      <div className={`${compact ? 'text-sm' : 'text-lg'} ${className}`}>
        <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-6 w-20 rounded"></div>
      </div>
    );
  }

  const primaryPrice = getPrimaryPrice();
  const alternativePrices = getAlternativePrices();

  if (compact) {
    return (
      <div className={`${className}`}>
        <div className="flex items-center space-x-2">
          <span className="text-lg font-bold text-gray-900 dark:text-white">
            {primaryPrice.formatted}
          </span>
          {showAlternativePrices && alternativePrices.length > 0 && (
            <div className="text-sm text-gray-500 dark:text-gray-400">
              ≈ {alternativePrices[0].formatted}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      {/* Primary Price */}
      <div className="flex items-center space-x-2 mb-2">
        <span className="text-2xl font-bold text-gray-900 dark:text-white">
          {primaryPrice.formatted}
        </span>
        {userPreferredCurrency && userPreferredCurrency !== baseCurrency && (
          <span className="text-sm bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-1 rounded">
            Preferred
          </span>
        )}
      </div>

      {/* Alternative Prices */}
      {showAlternativePrices && alternativePrices.length > 0 && (
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Globe className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Other currencies:
            </span>
            <button
              onClick={() => setShowAllCurrencies(!showAllCurrencies)}
              className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 flex items-center space-x-1"
            >
              {showAllCurrencies ? (
                <>
                  <EyeOff className="w-3 h-3" />
                  <span>Show less</span>
                </>
              ) : (
                <>
                  <Eye className="w-3 h-3" />
                  <span>Show all</span>
                </>
              )}
            </button>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {alternativePrices.map(({ currency, formatted }) => (
              <span
                key={currency}
                className="text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-1 rounded"
              >
                {formatted}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Base Currency Note */}
      {baseCurrency !== getDisplayCurrency() && (
        <div className="mt-2 text-xs text-gray-500 dark:text-gray-500">
          Original price: {formatPrice(basePrice, baseCurrency)} {baseCurrency}
        </div>
      )}
    </div>
  );
};

export default MultiCurrencyPrice;