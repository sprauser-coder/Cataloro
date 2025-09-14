/**
 * CATALORO - Currency Formatting Utilities
 * German locale formatting for Euro amounts
 */

/**
 * Formats a number to German Euro format (1.234,00€)
 * @param {number} amount - The amount to format
 * @param {boolean} showCurrency - Whether to show the € symbol (default: true)
 * @returns {string} - Formatted string in German format
 */
export const formatEuro = (amount, showCurrency = true) => {
  // Handle null, undefined, or invalid numbers
  if (amount === null || amount === undefined || isNaN(amount)) {
    return showCurrency ? '0,00€' : '0,00';
  }

  // Convert to number if it's a string
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
  
  // Format with German locale (1.234,56 format)
  const formatted = new Intl.NumberFormat('de-DE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(numAmount);

  return showCurrency ? `${formatted}€` : formatted;
};

/**
 * Formats a number to German format without currency symbol (1.234,00)
 * @param {number} amount - The amount to format
 * @returns {string} - Formatted string in German format without €
 */
export const formatGermanNumber = (amount) => {
  return formatEuro(amount, false);
};

/**
 * Legacy function name for backwards compatibility
 * @deprecated Use formatEuro instead
 */
export const formatCurrency = formatEuro;

export default formatEuro;