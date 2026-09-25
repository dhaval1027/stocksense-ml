import React from 'react';
import { Play, Loader2, ChevronDown } from 'lucide-react';

export default function StockSelector({
  stocks,
  selectedTicker,
  onSelectTicker,
  onAnalyze,
  isLoading
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 w-full sm:w-auto">
          <label htmlFor="stock-select" className="text-sm font-semibold text-slate-700 flex items-center gap-2">
            <span>Select Stock</span>
          </label>

          <div className="relative min-w-[280px]">
            <select
              id="stock-select"
              value={selectedTicker}
              onChange={(e) => onSelectTicker(e.target.value)}
              disabled={isLoading}
              className="w-full appearance-none bg-slate-50 border border-slate-300 hover:border-slate-400 focus:border-blue-600 focus:ring-2 focus:ring-blue-100 rounded-lg px-4 py-2.5 text-sm font-medium text-slate-900 transition-colors cursor-pointer disabled:opacity-50 pr-10 shadow-sm"
            >
              {stocks.map((s) => (
                <option key={s.ticker} value={s.ticker}>
                  {s.name} ({s.ticker})
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-500">
              <ChevronDown className="w-4 h-4" />
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onAnalyze}
            disabled={isLoading}
            className="w-full sm:w-auto inline-flex items-center justify-center px-5 py-2.5 rounded-lg text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 active:bg-blue-800 transition-all duration-150 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>Analyzing market data...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Analyze</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
