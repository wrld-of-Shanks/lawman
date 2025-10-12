// API Configuration
const config = {
  // Use environment variable if available, otherwise default to localhost for development
  API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8002',
  
  // For translation service (if needed)
  TRANSLATE_API_URL: process.env.REACT_APP_TRANSLATE_URL || 'http://localhost:8000',
};

export default config;
