import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import StockSelector from './components/StockSelector';
import SummaryCards from './components/SummaryCards';
import PriceChart from './components/PriceChart';
import Indicators from './components/Indicators';
import ModelMetrics from './components/ModelMetrics';
import Backtest from './components/Backtest';
import { fetchStocks, analyzeStock } from './api';
import { AlertCircle, RefreshCw } from 'lucide-react';

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
      setError(err.message || 'Failed to fetch analysis data. Please ensure backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    loadStockData(selectedTicker);
  }, [selectedTicker]);

  const handleSelectTicker = (newTicker) => {
    setSelectedTicker(newTicker);
  };

  const handleAnalyze = () => {
    loadStockData(selectedTicker);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* 1. Header */}
      <Header />

      {/* Main Single Page Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-5">
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
          <div className={`space-y-5 transition-opacity duration-200 ${isLoading ? 'opacity-60' : 'opacity-100'}`}>
            {/* 3. Summary Information Cards */}
            <SummaryCards data={data} />

            {/* 4. Interactive Price History Chart */}
            <PriceChart chartData={data.chart_data} ticker={data.ticker} />

            {/* 5. Technical Indicators */}
            <Indicators indicators={data.indicators} />

            {/* 6. Model Performance */}
            <ModelMetrics metrics={data.metrics} />

            {/* 7. Strategy Backtest */}
            <Backtest backtest={data.backtest} />
          </div>
        )}

        {/* Initial loading placeholder if no data yet */}
        {!data && isLoading && (
          <div className="bg-white border border-slate-200 rounded-xl p-16 text-center space-y-3 shadow-sm">
            <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-slate-600 text-sm font-medium">Analyzing market data and loading trained model...</p>
          </div>
        )}
      </main>

      {/* 8. Educational Disclaimer Footer */}
      <footer className="border-t border-slate-200 bg-white py-5 px-4 text-center">
        <p className="text-xs text-slate-500 max-w-3xl mx-auto">
          Educational project only. ML predictions are probabilistic and do not constitute financial advice or guarantee future returns.
        </p>
      </footer>
    </div>
  );
}
