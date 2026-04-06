/**
 * API Configuration
 * Centralized API URL management for both development and production
 */

export const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? `${window.location.origin}/api` : 'http://localhost:8000/api');

/**
 * Helper function to construct API endpoints
 * @param {string} path - The API path (e.g., 'v1/lov/')
 * @returns {string} - The full API URL
 */
export const getApiUrl = (path) => {
  const base = API_URL.replace(/\/+$|^\s+|\s+$/g, '');
  const normalizedPath = path.replace(/^\/+/, '');
  return `${base}/${normalizedPath}`;
};

/**
 * Helper function to construct LOV endpoints with query parameters
 * @param {string} type - LOV type
 * @param {string} language - Language code
 * @param {string} lic - Optional lic parameter
 * @returns {string} - The full LOV API URL
 */
export const getLovUrl = (type, language, lic = null) => {
  let url = getApiUrl(`v1/lov/?type=${encodeURIComponent(type)}&language=${encodeURIComponent(language)}`);
  if (lic) {
    url += `&lic=${encodeURIComponent(lic)}`;
  }
  return url;
};
