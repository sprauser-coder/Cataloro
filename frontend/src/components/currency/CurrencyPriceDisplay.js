import React, { useState, useEffect } from 'react';
import { DollarSign, RefreshCw } from 'lucide-react';

const CurrencyPriceDisplay = ({ price, baseCurrency = 'EUR', className = '' }) => {
  const [selectedCurrency, setSelectedCurrency] = useState(baseCurrency);
  const [convertedPrice, setConvertedPrice] = useState(price);
  const [exchangeRates, setExchangeRates] = useState({});
  const [supportedCurrencies, setSupportedCurrencies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCurrencyData();
  }, []);

  useEffect(() => {
    convertPrice();
  }, [selectedCurrency, price, exchangeRates]);

  const fetchCurrencyData = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      
      // Fetch supported currencies and exchange rates
      const [currenciesRes, ratesRes] = await Promise.all([
        fetch(`${backendUrl}/api/v2/advanced/currency/supported`),
        fetch(`${backendUrl}/api/v2/advanced/currency/rates`)
      ]);

      const [currenciesData, ratesData] = await Promise.all([
        currenciesRes.json(),
        ratesRes.json()
      ]);

      if (currenciesData.success) {
        setSupportedCurrencies(currenciesData.currencies);
      }

      if (ratesData.success) {
        setExchangeRates(ratesData.rates);
      }
    } catch (error) {
      console.error('Failed to fetch currency data:', error);
      // Fallback data
      setSupportedCurrencies([
        { code: 'EUR', name: 'Euro', symbol: '€', is_base: true },
        { code: 'USD', name: 'US Dollar', symbol: '$' },
        { code: 'GBP', name: 'British Pound', symbol: '£' },
        { code: 'CHF', name: 'Swiss Franc', symbol: 'CHF' }
      ]);
      setExchangeRates({
        'USD': 1.08, 'GBP': 0.85, 'CHF': 0.95, 'JPY': 160.0
      });
    } finally {
      setLoading(false);
    }
  };

  const convertPrice = () => {
    if (selectedCurrency === baseCurrency) {
      setConvertedPrice(price);
      return;
    }

    const rate = exchangeRates[selectedCurrency];
    if (rate) {
      setConvertedPrice(price * rate);
    } else {
      setConvertedPrice(price);
    }
  };

  const getCurrentCurrency = () => {
    return supportedCurrencies.find(c => c.code === selectedCurrency) || 
           supportedCurrencies.find(c => c.is_base) || 
           { code: 'EUR', symbol: '€' };
  };

  const formatPrice = (amount) => {
    const currency = getCurrentCurrency();
    return `${currency.symbol}${amount.toFixed(2)}`;
  };

  if (loading) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <RefreshCw className="w-4 h-4 animate-spin text-gray-400" />
        <span className="text-gray-600">Loading price...</span>
      </div>
    );
  }

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      {/* Price Display */}
      <div className="text-2xl font-bold text-gray-900 dark:text-white">
        {formatPrice(convertedPrice)}
      </div>

      {/* Currency Selector */}
      <div className="relative">
        <select
          value={selectedCurrency}
          onChange={(e) => setSelectedCurrency(e.target.value)}
          className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {supportedCurrencies.map((currency) => (
            <option key={currency.code} value={currency.code}>
              {currency.code} ({currency.symbol})
            </option>
          ))}
        </select>
      </div>

      {/* Base Currency Reference */}
      {selectedCurrency !== baseCurrency && (
        <div className="text-sm text-gray-500 dark:text-gray-400">
          ({formatPrice(price)} {baseCurrency})
        </div>
      )}
    </div>
  );
};

export default CurrencyPriceDisplay;