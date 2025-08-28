// Image URL helper function for production deployment
export const getImageUrl = (imageUrl) => {
  if (!imageUrl) return '';
  if (imageUrl.startsWith('http')) return imageUrl;
  if (imageUrl.startsWith('/uploads/')) {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://217.154.0.82';
    return `${backendUrl}${imageUrl}`;
  }
  return imageUrl;
};

// Format error messages
export const formatErrorMessage = (error, fallbackMessage) => {
  try {
    if (!error?.response?.data?.detail) {
      return fallbackMessage;
    }
    
    const detail = error.response.data.detail;
    
    if (Array.isArray(detail)) {
      const errorMessages = detail.map(err => {
        if (typeof err === 'string') {
          return err;
        }
        const message = typeof err.msg === 'string' ? err.msg : 'Validation error';
        return `${err.loc ? err.loc.join('.') + ': ' : ''}${message}`;
      });
      return errorMessages.join(', ');
    } else if (typeof detail === 'string') {
      return detail;
    } else if (detail?.msg) {
      return detail.msg;
    }
    
    return fallbackMessage;
  } catch (processingError) {
    return fallbackMessage;
  }
};

// Format currency
export const formatCurrency = (amount, currency = '€') => {
  if (amount === null || amount === undefined) return `${currency}0.00`;
  return `${currency}${parseFloat(amount).toFixed(2)}`;
};

// Format date
export const formatDate = (date) => {
  return new Date(date).toLocaleDateString();
};

// Generate unique ID
export const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};