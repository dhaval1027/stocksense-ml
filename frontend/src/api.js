import axios from 'axios';

// Use relative URL so Vite proxy forwards to backend, with fallback for direct API
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchStocks = async () => {
  try {
    const response = await client.get('/stocks');
    if (response.data && response.data.success) {
      return response.data.data;
    }
    throw new Error(response.data.error || 'Failed to load stocks');
  } catch (error) {
    console.error('Error fetching stocks:', error);
    // Return default supported stocks if backend is still starting
    return [
      { ticker: 'RELIANCE.NS', name: 'Reliance Industries', exchange: 'NSE' },
      { ticker: 'TCS.NS', name: 'Tata Consultancy Services', exchange: 'NSE' },
      { ticker: 'HDFCBANK.NS', name: 'HDFC Bank', exchange: 'NSE' },
    ];
  }
};

export const analyzeStock = async (ticker) => {
  try {
    const response = await client.get(`/analyze/${ticker}`);
    if (response.data && response.data.success) {
      return response.data.data;
    }
    throw new Error(response.data.error || `Failed to analyze ${ticker}`);
  } catch (error) {
    console.error(`Error analyzing ${ticker}:`, error);
    const msg = error.response?.data?.detail || error.response?.data?.error || error.message;
    throw new Error(msg || 'Network or server error during stock analysis');
  }
};
