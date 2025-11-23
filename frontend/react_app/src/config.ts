// API Configuration
const config = {
  // Use VITE_API_BASE_URL if available, otherwise default to localhost
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  RAZORPAY_KEY_ID: import.meta.env.VITE_RAZORPAY_KEY_ID || 'rzp_test_RjAktAstOznCtJ',

  // For translation service (if needed)
  TRANSLATE_API_URL: import.meta.env.VITE_TRANSLATE_URL || 'http://localhost:8000',

  // Other configs
  APP_NAME: 'SPECTER AI',
  VERSION: '1.0.0',
  ENV: import.meta.env.MODE || 'development',
  IS_DEV: import.meta.env.DEV || true,
};

export default config;
