import React, { useState, useEffect } from 'react';

const CurrencySelector = ({ selectedCurrency, onCurrencyChange, showLabel = true }) => {
  const [currencies, setCurrencies] = useState([]);
  const [exchangeRates, setExchangeRates] = useState({});
  const [loading, setLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchCurrencies();
    fetchExchangeRates();
  }, []);

  const fetchCurrencies = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/v2/currency/supported`);
      const data = await response.json();
      
      if (data.success) {
        setCurrencies(data.currencies);
      }
    } catch (error) {
      console.error('Failed to fetch currencies:', error);
    }
  };

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
    } finally {
      setLoading(false);
    }
  };

  const selectedCurrencyData = currencies.find(c => c.code === selectedCurrency) || currencies[0];

  const handleCurrencySelect = (currency) => {
    onCurrencyChange(currency.code);
    setIsOpen(false);

    // Save user preference
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
    if (currentUser.id) {
      saveUserPreference(currentUser.id, currency.code);
    }
  };

  const saveUserPreference = async (userId, currencyCode) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      await fetch(`${backendUrl}/v2/currency/user/preference`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          currency_code: currencyCode
        })
      });
    } catch (error) {
      console.error('Failed to save currency preference:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="animate-pulse bg-gray-200 h-8 w-20 rounded"></div>
      </div>
    );
  }

  return (
    <div className="relative">
      {showLabel && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Currency
        </label>
      )}
      
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center justify-between w-full bg-white border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent hover:bg-gray-50"
        >
          <div className="flex items-center">
            <span className="font-medium mr-2">
              {selectedCurrencyData?.symbol || '€'}
            </span>
            <span className="text-gray-700">
              {selectedCurrencyData?.code || 'EUR'}
            </span>
            {exchangeRates[selectedCurrency] && selectedCurrency !== 'EUR' && (
              <span className="ml-2 text-xs text-gray-500">
                ≈{exchangeRates[selectedCurrency].toFixed(4)}
              </span>
            )}
          </div>
          <div className={`transform transition-transform ${isOpen ? 'rotate-180' : ''}`}>
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </button>

        {isOpen && (
          <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
            <div className="py-1">
              {currencies.map((currency) => (
                <button
                  key={currency.code}
                  onClick={() => handleCurrencySelect(currency)}
                  className={`w-full px-3 py-2 text-left hover:bg-gray-100 flex items-center justify-between ${
                    selectedCurrency === currency.code ? 'bg-blue-50 text-blue-700' : 'text-gray-900'
                  }`}
                >
                  <div className="flex items-center">
                    <span className="font-medium mr-3 w-8">
                      {currency.symbol}
                    </span>
                    <div>
                      <span className="font-medium">{currency.code}</span>
                      <span className="ml-2 text-sm text-gray-500">{currency.name}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    {exchangeRates[currency.code] && (
                      <div className="text-sm text-gray-600">
                        {currency.code === 'EUR' ? '1.0000' : exchangeRates[currency.code].toFixed(4)}
                      </div>
                    )}
                    {selectedCurrency === currency.code && (
                      <div className="text-xs text-blue-600">Selected</div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Click outside to close */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default CurrencySelector;