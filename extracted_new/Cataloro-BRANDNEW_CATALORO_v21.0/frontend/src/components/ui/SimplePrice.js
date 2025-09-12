/**
 * Simple Price Component - Replacement for MultiCurrencyPrice
 */

import React from 'react';

const SimplePrice = ({ basePrice, baseCurrency = 'EUR', className = '' }) => {
  const formatPrice = (price) => {
    if (typeof price !== 'number') return '€0.00';
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: baseCurrency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price);
  };

  return (
    <div className={`text-2xl font-bold text-gray-900 dark:text-white ${className}`}>
      {formatPrice(basePrice)}
    </div>
  );
};

export default SimplePrice;