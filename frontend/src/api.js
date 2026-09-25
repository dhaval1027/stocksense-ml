import axios from 'axios';
import offlineData from './offlineData.json';

// Retrieve active backend URL: Priority = localStorage > VITE_API_BASE_URL > window.location.origin
export const getActiveApiUrl = () => {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('stocksense_api_url');
    if (saved && saved.trim()) {
      return saved.trim().replace(/\/+$/, '');
    }
  }
  const envBase = (import.meta.env.VITE_API_BASE_URL || '').trim().replace(/\/+$/, '');
  return envBase;
};

export const setActiveApiUrl = (url) => {
  if (typeof window !== 'undefined') {
    if (url && url.trim()) {
      localStorage.setItem('stocksense_api_url', url.trim().replace(/\/+$/, ''));
    } else {
      localStorage.removeItem('stocksense_api_url');
    }
  }
};

export const fetchStocks = async () => {
  const base = getActiveApiUrl();
  const endpoints = [];
  if (base) {
    endpoints.push(`${base}/stocks`);
    if (!base.endsWith('/api')) endpoints.push(`${base}/api/stocks`);
  }
  endpoints.push('/api/stocks');
  endpoints.push('/stocks');

  for (const url of endpoints) {
    try {
      const res = await axios.get(url, { timeout: 8000 });
      if (res.data && res.data.success && res.data.data) {
        return res.data.data;
      }
    } catch (e) {
      // Try next endpoint candidate
    }
  }

  // Fallback to supported stocks
  return [
    { ticker: 'RELIANCE.NS', name: 'Reliance Industries', exchange: 'NSE' },
    { ticker: 'TCS.NS', name: 'Tata Consultancy Services', exchange: 'NSE' },
    { ticker: 'HDFCBANK.NS', name: 'HDFC Bank', exchange: 'NSE' },
  ];
};

export const analyzeStock = async (ticker) => {
  const base = getActiveApiUrl();
  const endpoints = [];
  if (base) {
    endpoints.push(`${base}/analyze/${ticker}`);
    if (!base.endsWith('/api')) endpoints.push(`${base}/api/analyze/${ticker}`);
  }
  endpoints.push(`/api/analyze/${ticker}`);
  endpoints.push(`/analyze/${ticker}`);

  for (const url of endpoints) {
    try {
      const res = await axios.get(url, { timeout: 15000 });
      if (res.data && res.data.success && res.data.data) {
        return res.data.data;
      }
    } catch (err) {
      // Continue to next endpoint or fallback
    }
  }

  // If live backend is sleeping, waking up, or unconfigured, fallback to pre-computed analysis
  if (offlineData && offlineData[ticker]) {
    console.info(`[StockSense] Serving offline high-conviction analysis for ${ticker}`);
    return offlineData[ticker];
  }

  throw new Error('Unable to connect to ML backend and offline data is unavailable.');
};
