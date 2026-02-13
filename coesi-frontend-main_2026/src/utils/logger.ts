/**
 * Centralized logging utility
 * Automatically disables verbose logs in production
 * Only error logs are shown in production
 */

const isDevelopment = process.env.NODE_ENV === 'development';

// Log levels
export const logger = {
  // Debug logs - only in development
  debug: (...args: any[]) => {
    if (isDevelopment) {
      console.log(...args);
    }
  },

  // Info logs - only in development
  info: (...args: any[]) => {
    if (isDevelopment) {
      console.info(...args);
    }
  },

  // Warnings - always shown (useful for production)
  warn: (...args: any[]) => {
    console.warn(...args);
  },

  // Errors - always shown (critical for production)
  error: (...args: any[]) => {
    console.error(...args);
  },

  // Log - alias for debug (for backward compatibility)
  log: (...args: any[]) => {
    if (isDevelopment) {
      console.log(...args);
    }
  }
};


