// API Configuration
const config = {
  // Use environment variable if available, otherwise default to Render backend for production
  // For production deployment, set REACT_APP_API_URL environment variable in Netlify if needed
  API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',

  // For translation service (if needed)
  TRANSLATE_API_URL: process.env.REACT_APP_TRANSLATE_URL || 'http://localhost:8000',
};

// Debug logging
console.log('API_BASE_URL:', config.API_BASE_URL);
console.log('Environment:', process.env.NODE_ENV);
console.log('REACT_APP_API_URL env var:', process.env.REACT_APP_API_URL);

export default config;
