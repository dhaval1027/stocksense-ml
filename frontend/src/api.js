import axios from 'axios';

// Normalize VITE_API_BASE_URL: strip trailing slashes
const rawBase = 'https://stocksense-ml-dcvi.onrender.com/api';

// Create primary client
const client = axios.create({
  baseURL: rawBase || '/api',
  timeout: 60000, // 60 seconds for Render free tier cold-starts
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchStocks = async () => {
  try {
    // Try primary endpoint
    let response;
    try {
      response = await client.get('/stocks');
    } catch (e) {
      // If base was raw domain without /api, try /api/stocks
      if (rawBase && !rawBase.endsWith('/api')) {
        response = await axios.get(`${rawBase}/api/stocks`, { timeout: 60000 });
      } else {
        throw e;
      }
    }

    if (response.data && response.data.success) {
      return response.data.data;
    }
    throw new Error(response.data.error || 'Failed to load stocks');
  } catch (error) {
    console.error('Error fetching stocks from backend:', error);
    // Return standard supported stocks so UI always stays operational
    return [
      { ticker: 'RELIANCE.NS', name: 'Reliance Industries', exchange: 'NSE' },
      { ticker: 'TCS.NS', name: 'Tata Consultancy Services', exchange: 'NSE' },
      { ticker: 'HDFCBANK.NS', name: 'HDFC Bank', exchange: 'NSE' },
    ];
  }
};

export const analyzeStock = async (ticker) => {
  try {
    let response;
    try {
      response = await client.get(`/analyze/${ticker}`);
    } catch (err) {
      // If primary failed with 404 and rawBase did not include /api, try with /api prefix
      if (err.response?.status === 404 && rawBase && !rawBase.endsWith('/api')) {
        response = await axios.get(`${rawBase}/api/analyze/${ticker}`, { timeout: 60000 });
      } else {
        throw err;
      }
    }

    if (response.data && response.data.success) {
      return response.data.data;
    }
    throw new Error(response.data.error || `Failed to analyze ${ticker}`);
  } catch (error) {
    console.error(`Error analyzing ${ticker}:`, error);

    // Extract clean human-readable error string (prevent [object Object])
    let msg = 'Failed to fetch analysis data. Backend may be waking up.';
    if (error.response?.data) {
      const data = error.response.data;
      if (typeof data.detail === 'string') {
        msg = data.detail;
      } else if (Array.isArray(data.detail)) {
        msg = data.detail.map(d => (typeof d === 'string' ? d : d.msg || JSON.stringify(d))).join(', ');
      } else if (typeof data.error === 'string') {
        msg = data.error;
      } else if (typeof data === 'string') {
        msg = data;
      } else {
        msg = JSON.stringify(data);
      }
    } else if (error.message && typeof error.message === 'string') {
      msg = error.message;
    }

    throw new Error(msg);
  }
};
