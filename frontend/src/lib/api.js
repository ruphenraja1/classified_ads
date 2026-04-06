/**
 * API Configuration
 * Centralized API URL management for both development and production
 */

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * Helper function to construct API endpoints
 * @param {string} path - The API path (e.g., 'v1/lov/')
 * @returns {string} - The full API URL
 */
export const getApiUrl = (path) => {
  return `${API_URL}/${path}`.replace(/\/+/g, '/').replace('://', '###').replace(/\//g, '/').replace('###', '://');
};

/**
 * Helper function to construct LOV endpoints with query parameters
 * @param {string} type - LOV type
 * @param {string} language - Language code
 * @param {string} lic - Optional lic parameter
 * @returns {string} - The full LOV API URL
 */
export const getLovUrl = (type, language, lic = null) => {
  let url = `${API_URL}/v1/lov/?type=${type}&language=${language}`;
  if (lic) {
    url += `&lic=${lic}`;
  }
  return url;
};
