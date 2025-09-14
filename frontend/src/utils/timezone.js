/**
 * CATALORO - Timezone Utility Functions
 * Consistent timezone handling across the application
 */

// Get user's timezone preference from localStorage or default to browser timezone
export const getUserTimezone = () => {
  const userData = localStorage.getItem('cataloro_user');
  if (userData) {
    try {
      const user = JSON.parse(userData);
      return user.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone;
    } catch (e) {
      console.warn('Error parsing user data for timezone:', e);
    }
  }
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
};

// Convert UTC date to user's timezone for display
export const formatDateInUserTimezone = (utcDate, userTimezone = null) => {
  if (!utcDate) return null;
  
  const timezone = userTimezone || getUserTimezone();
  const date = new Date(utcDate);
  
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: timezone,
    timeZoneName: 'short'
  }).format(date);
};

// Convert date to UTC for storage (backend expects UTC)
export const convertToUTC = (localDate) => {
  if (!localDate) return null;
  return new Date(localDate).toISOString();
};

// Parse date with timezone handling for partner listings
export const parsePartnerDate = (dateString, userTimezone = null) => {
  if (!dateString) return null;
  
  let parsedDate;
  try {
    // Handle different date formats from backend
    if (dateString.includes('Z') || dateString.includes('+')) {
      // Already has timezone info (UTC)
      parsedDate = new Date(dateString);
    } else {
      // Assume UTC if no timezone specified
      parsedDate = new Date(dateString + 'Z');
    }
  } catch (e) {
    // Fallback parsing
    parsedDate = new Date(dateString);
  }
  
  return parsedDate;
};

// Calculate time remaining for partner listings (always consistent regardless of user timezone)
export const calculateTimeRemaining = (publicAtString) => {
  if (!publicAtString) return { expired: true, timeRemaining: 0 };
  
  const publicDate = parsePartnerDate(publicAtString);
  const now = new Date();
  const timeRemaining = publicDate - now;
  
  return {
    expired: timeRemaining <= 0,
    timeRemaining: Math.max(0, timeRemaining),
    hoursRemaining: Math.floor(timeRemaining / (1000 * 60 * 60)),
    minutesRemaining: Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60))
  };
};

// Format time remaining text for partner badges
export const formatPartnerTimeRemaining = (publicAtString) => {
  const { expired, hoursRemaining, minutesRemaining } = calculateTimeRemaining(publicAtString);
  
  if (expired) return null;
  
  if (hoursRemaining > 0) {
    return `${hoursRemaining}h ${minutesRemaining}m left`;
  } else if (minutesRemaining > 0) {
    return `${minutesRemaining}m left`;
  } else {
    return 'Ending soon';
  }
};

// Get timezone offset for display
export const getTimezoneDisplay = (timezone = null) => {
  const tz = timezone || getUserTimezone();
  const now = new Date();
  const offsetMinutes = -now.getTimezoneOffset();
  const offsetHours = Math.floor(Math.abs(offsetMinutes) / 60);
  const offsetMins = Math.abs(offsetMinutes) % 60;
  const sign = offsetMinutes >= 0 ? '+' : '-';
  
  return `${tz} (GMT${sign}${offsetHours}${offsetMins > 0 ? ':' + offsetMins.toString().padStart(2, '0') : ''})`;
};

// List of common timezones with user-friendly names
export const COMMON_TIMEZONES = [
  { value: 'Europe/London', label: 'London (GMT+0/+1)', region: 'Europe' },
  { value: 'Europe/Berlin', label: 'Berlin (GMT+1/+2)', region: 'Europe' },
  { value: 'Europe/Paris', label: 'Paris (GMT+1/+2)', region: 'Europe' },
  { value: 'Europe/Madrid', label: 'Madrid (GMT+1/+2)', region: 'Europe' },
  { value: 'Europe/Rome', label: 'Rome (GMT+1/+2)', region: 'Europe' },
  { value: 'Europe/Amsterdam', label: 'Amsterdam (GMT+1/+2)', region: 'Europe' },
  { value: 'America/New_York', label: 'New York (EST/EDT)', region: 'Americas' },
  { value: 'America/Chicago', label: 'Chicago (CST/CDT)', region: 'Americas' },
  { value: 'America/Los_Angeles', label: 'Los Angeles (PST/PDT)', region: 'Americas' },
  { value: 'Asia/Tokyo', label: 'Tokyo (JST)', region: 'Asia Pacific' },
  { value: 'Asia/Shanghai', label: 'Shanghai (CST)', region: 'Asia Pacific' },
  { value: 'Asia/Dubai', label: 'Dubai (GST)', region: 'Asia Pacific' },
  { value: 'Australia/Sydney', label: 'Sydney (AEST/AEDT)', region: 'Asia Pacific' }
];