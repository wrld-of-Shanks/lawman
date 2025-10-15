// API Configuration
const config = {
  // Use environment variable if available, otherwise default to localhost for development
  // Updated to use Render backend deployment
  API_BASE_URL: process.env.REACT_APP_API_URL || 'https://specter-backend1.onrender.com',
  
  // For translation service (if needed)
  TRANSLATE_API_URL: process.env.REACT_APP_TRANSLATE_URL || 'http://localhost:8000',
};

// Debug logging
console.log('API_BASE_URL:', config.API_BASE_URL);
console.log('Environment:', process.env.NODE_ENV);

export default config;
