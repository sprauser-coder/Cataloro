import React, { useState, useEffect } from 'react';
import { ArrowUpDown, RefreshCw, Calculator } from 'lucide-react';
import CurrencySelector from './CurrencySelector';

const CurrencyConverter = ({ 
  initialAmount = 100,
  onConversionChange,
  compact = false 
}) => {
  const [fromCurrency, setFromCurrency] = useState('EUR');
  const [toCurrency, setToCurrency] = useState('USD');
  const [amount, setAmount] = useState(initialAmount);
  const [convertedAmount, setConvertedAmount] = useState(0);
  const [exchangeRates, setExchangeRates] = useState({});
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    fetchExchangeRates();
  }, []);

  useEffect(() => {
    convertCurrency();
  }, [amount, fromCurrency, toCurrency, exchangeRates]);

  const fetchExchangeRates = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/v2/currency/rates`);
      const data = await response.json();
      
      if (data.success) {
        setExchangeRates(data.rates);
        setLastUpdated(new Date());
      }
    } catch (error) {
      console.error('Failed to fetch exchange rates:', error);
    } finally {
      setLoading(false);
    }
  };

  const convertCurrency = async () => {
    if (!amount || !fromCurrency || !toCurrency || fromCurrency === toCurrency) {
      setConvertedAmount(amount);
      return;
    }

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/v2/currency/convert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: parseFloat(amount),
          from_currency: fromCurrency,
          to_currency: toCurrency
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setConvertedAmount(data.conversion.converted_amount);
        
        if (onConversionChange) {
          onConversionChange({
            originalAmount: amount,
            convertedAmount: data.conversion.converted_amount,
            fromCurrency,
            toCurrency,
            exchangeRate: data.conversion.exchange_rate
          });
        }
      }
    } catch (error) {
      console.error('Failed to convert currency:', error);
      // Fallback to client-side calculation if available
      if (exchangeRates[fromCurrency] && exchangeRates[toCurrency]) {
        const rate = exchangeRates[toCurrency] / exchangeRates[fromCurrency];
        setConvertedAmount(amount * rate);
      }
    }
  };

  const swapCurrencies = () => {
    setFromCurrency(toCurrency);
    setToCurrency(fromCurrency);
  };

  const getExchangeRate = () => {
    if (fromCurrency === toCurrency) return 1;
    if (exchangeRates[fromCurrency] && exchangeRates[toCurrency]) {
      return exchangeRates[toCurrency] / exchangeRates[fromCurrency];
    }
    return 0;
  };

  if (compact) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
        <div className="flex items-center space-x-2 mb-3">
          <Calculator className="w-4 h-4 text-blue-500" />
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Quick Converter
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-20 px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            min="0"
            step="0.01"
          />
          
          <CurrencySelector
            selectedCurrency={fromCurrency}
            onCurrencyChange={(currency) => setFromCurrency(currency.code)}
            size="small"
            showFlag={false}
          />
          
          <button
            onClick={swapCurrencies}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
          >
            <ArrowUpDown className="w-4 h-4 text-gray-500" />
          </button>
          
          <CurrencySelector
            selectedCurrency={toCurrency}
            onCurrencyChange={(currency) => setToCurrency(currency.code)}
            size="small"
            showFlag={false}
          />
          
          <div className="text-sm font-medium text-gray-900 dark:text-white">
            {convertedAmount.toFixed(2)}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-600">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
            <Calculator className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Currency Converter
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Real-time exchange rates
            </p>
          </div>
        </div>
        
        <button
          onClick={fetchExchangeRates}
          disabled={loading}
          className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          title="Refresh rates"
        >
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Conversion Form */}
      <div className="space-y-4">
        {/* From Currency */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            From
          </label>
          <div className="flex items-center space-x-3">
            <div className="flex-1">
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full px-4 py-3 text-lg border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="Enter amount"
                min="0"
                step="0.01"
              />
            </div>
            <div className="w-48">
              <CurrencySelector
                selectedCurrency={fromCurrency}
                onCurrencyChange={(currency) => setFromCurrency(currency.code)}
                showFlag={true}
              />
            </div>
          </div>
        </div>

        {/* Swap Button */}
        <div className="flex justify-center">
          <button
            onClick={swapCurrencies}
            className="p-3 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-full transition-colors group"
            title="Swap currencies"
          >
            <ArrowUpDown className="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-gray-800 dark:group-hover:text-gray-200" />
          </button>
        </div>

        {/* To Currency */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            To
          </label>
          <div className="flex items-center space-x-3">
            <div className="flex-1">
              <div className="px-4 py-3 text-lg bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg">
                <span className="font-semibold text-gray-900 dark:text-white">
                  {convertedAmount.toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}
                </span>
              </div>
            </div>
            <div className="w-48">
              <CurrencySelector
                selectedCurrency={toCurrency}
                onCurrencyChange={(currency) => setToCurrency(currency.code)}
                showFlag={true}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Exchange Rate Info */}
      <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-750 rounded-lg">
        <div className="flex items-center justify-between text-sm">
          <div className="text-gray-600 dark:text-gray-400">
            Exchange Rate
          </div>
          <div className="font-medium text-gray-900 dark:text-white">
            1 {fromCurrency} = {getExchangeRate().toFixed(4)} {toCurrency}
          </div>
        </div>
        
        {lastUpdated && (
          <div className="mt-2 text-xs text-gray-500 dark:text-gray-500">
            Last updated: {lastUpdated.toLocaleString()}
          </div>
        )}
      </div>

      {/* Quick Amount Buttons */}
      <div className="mt-4">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Quick amounts
        </label>
        <div className="flex space-x-2">
          {[100, 500, 1000, 5000, 10000].map((quickAmount) => (
            <button
              key={quickAmount}
              onClick={() => setAmount(quickAmount)}
              className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                amount == quickAmount
                  ? 'bg-blue-100 dark:bg-blue-900/30 border-blue-300 dark:border-blue-600 text-blue-700 dark:text-blue-300'
                  : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
              }`}
            >
              {quickAmount.toLocaleString()}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CurrencyConverter;