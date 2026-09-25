import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import StockSelector from './components/StockSelector';
import SummaryCards from './components/SummaryCards';
import PriceChart from './components/PriceChart';
import Indicators from './components/Indicators';
import ModelMetrics from './components/ModelMetrics';
import Backtest from './components/Backtest';
import { fetchStocks, analyzeStock, getActiveApiUrl, setActiveApiUrl } from './api';
import { AlertCircle, RefreshCw, Server, Check, Edit2, X } from 'lucide-react';

export default function App() {
  const [stocks, setStocks] = useState([
    { ticker: 'RELIANCE.NS', name: 'Reliance Industries', exchange: 'NSE' },
    { ticker: 'TCS.NS', name: 'Tata Consultancy Services', exchange: 'NSE' },
    { ticker: 'HDFCBANK.NS', name: 'HDFC Bank', exchange: 'NSE' },
  ]);
  const [selectedTicker, setSelectedTicker] = useState('RELIANCE.NS');
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showConfig, setShowConfig] = useState(false);
  const [customUrl, setCustomUrl] = useState(getActiveApiUrl() || '');
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Load stocks list on initial mount
  useEffect(() => {
    async function initStocks() {
      try {
        const stockList = await fetchStocks();
        if (stockList && stockList.length > 0) {
          setStocks(stockList);
        }
      } catch (err) {
        console.warn('Using default stock list');
      }
    }
    initStocks();
  }, []);

  // Fetch analysis for selected stock
  const loadStockData = async (ticker) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await analyzeStock(ticker);
      setData(result);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Failed to fetch analysis data.');
    } finally {
      setIsLoading(false);
    }
  };

  // Initial load and ticker change
  useEffect(() => {
    loadStockData(selectedTicker);
  }, [selectedTicker]);

  const handleSelectTicker = (newTicker) => {
    setSelectedTicker(newTicker);
  };

  const handleAnalyze = () => {
    loadStockData(selectedTicker);
  };

  const handleSaveApiUrl = (e) => {
    e.preventDefault();
    setActiveApiUrl(customUrl);
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2000);
    setShowConfig(false);
    loadStockData(selectedTicker);
  };

  const activeUrl = getActiveApiUrl();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* 1. Header */}
      <Header />

      {/* Main Single Page Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-5">
        {/* Backend Connection Status Bar */}
        <div className="flex flex-wrap items-center justify-between bg-white border border-slate-200 px-4 py-2.5 rounded-xl text-xs shadow-sm gap-2">
          <div className="flex items-center space-x-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="font-semibold text-slate-700">Model Engine:</span>
            <span className="font-mono text-slate-500 truncate max-w-xs sm:max-w-md">
              {activeUrl ? `Connected: ${activeUrl}` : 'Production Pre-Trained Engine (NSE Live Data)'}
            </span>
          </div>

          <button
            onClick={() => setShowConfig(!showConfig)}
            className="inline-flex items-center space-x-1 font-medium text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-2.5 py-1 rounded-md transition-colors"
          >
            <Server className="w-3.5 h-3.5" />
            <span>{showConfig ? 'Close Settings' : 'Configure Backend URL'}</span>
          </button>
        </div>

        {/* Backend URL Input Modal/Bar */}
        {showConfig && (
          <form onSubmit={handleSaveApiUrl} className="bg-white border border-blue-200 rounded-xl p-4 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                <Server className="w-4 h-4 text-blue-600" />
                Connect Live Render Backend URL
              </h3>
              <button type="button" onClick={() => setShowConfig(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>
            <p className="text-xs text-slate-500">
              Paste your Render Web Service URL below (e.g. <code className="bg-slate-100 px-1 py-0.5 rounded text-blue-700">https://your-service.onrender.com</code>).
            </p>
            <div className="flex flex-col sm:flex-row gap-2">
              <input
                type="text"
                value={customUrl}
                onChange={(e) => setCustomUrl(e.target.value)}
                placeholder="https://your-backend-name.onrender.com"
                className="flex-1 bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs font-mono focus:border-blue-600 focus:ring-1 focus:ring-blue-600 outline-none"
              />
              <button
                type="submit"
                className="inline-flex items-center justify-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Save & Connect</span>
              </button>
            </div>
          </form>
        )}

        {/* 2. Stock Selector & Analyze Button */}
        <StockSelector
          stocks={stocks}
          selectedTicker={selectedTicker}
          onSelectTicker={handleSelectTicker}
          onAnalyze={handleAnalyze}
          isLoading={isLoading}
        />

        {/* Error Banner */}
        {error && (
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-rose-800 text-sm flex items-center justify-between shadow-sm">
            <div className="flex items-center space-x-3">
              <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-600" />
              <span className="font-medium">{error}</span>
            </div>
            <button
              onClick={handleAnalyze}
              className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-rose-100 hover:bg-rose-200 text-xs font-semibold text-rose-800 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry</span>
            </button>
          </div>
        )}

        {/* Dashboard Content */}
        {data && (
          <div className="space-y-5 animate-in fade-in duration-300">
            {/* 3. Summary Cards */}
            <SummaryCards data={data} />

            {/* 4. Interactive Price & SMA Chart */}
            <PriceChart data={data.chart_data} ticker={data.ticker} />

            {/* 5. Technical Indicators Grid */}
            <Indicators indicators={data.indicators} />

            {/* 6. ML Model Performance Metrics */}
            <ModelMetrics metrics={data.metrics} />

            {/* 7. Strategy Backtest Simulation */}
            <Backtest backtest={data.backtest} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-xs text-slate-500 font-medium">
          Educational project only. ML predictions are probabilistic and do not constitute financial advice or guarantee future returns.
        </div>
      </footer>
    </div>
  );
}
