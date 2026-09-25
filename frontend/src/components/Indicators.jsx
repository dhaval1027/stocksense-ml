import React from 'react';
import { Gauge } from 'lucide-react';

export default function Indicators({ indicators }) {
  if (!indicators) return null;

  const getRsiColor = (rsi) => {
    if (rsi >= 70) return 'text-rose-700 bg-rose-50 border-rose-200';
    if (rsi <= 30) return 'text-emerald-700 bg-emerald-50 border-emerald-200';
    return 'text-blue-700 bg-blue-50 border-blue-200';
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900 tracking-wide uppercase flex items-center gap-2">
            <Gauge className="w-4 h-4 text-blue-600" />
            Technical Indicators
          </h2>
          <p className="text-xs text-slate-500">Calculated from recent market OHLCV data</p>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        {/* RSI 14 */}
        <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-lg shadow-sm">
          <div className="text-xs text-slate-500 font-medium flex items-center justify-between mb-1">
            <span>RSI (14)</span>
            <span className={`text-[10px] px-1.5 py-0.5 rounded border font-semibold ${getRsiColor(indicators.rsi)}`}>
              {indicators.rsi_status}
            </span>
          </div>
          <div className="text-xl font-bold font-mono text-slate-900">
            {indicators.rsi}
          </div>
          <div className="w-full bg-slate-200 h-1.5 rounded-full mt-2 overflow-hidden">
            <div
              className={`h-full ${indicators.rsi >= 70 ? 'bg-rose-500' : indicators.rsi <= 30 ? 'bg-emerald-500' : 'bg-blue-600'}`}
              style={{ width: `${Math.min(Math.max(indicators.rsi, 0), 100)}%` }}
            />
          </div>
        </div>

        {/* MACD */}
        <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-lg shadow-sm">
          <div className="text-xs text-slate-500 font-medium flex items-center justify-between mb-1">
            <span>MACD</span>
            <span className={`text-[10px] font-mono font-semibold ${indicators.macd_hist >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
              Hist: {indicators.macd_hist > 0 ? '+' : ''}{indicators.macd_hist}
            </span>
          </div>
          <div className="text-xl font-bold font-mono text-slate-900">
            {indicators.macd}
          </div>
          <div className="text-[11px] text-slate-500 mt-1 font-mono">
            Signal: {indicators.macd_signal}
          </div>
        </div>

        {/* SMA 20 */}
        <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-lg shadow-sm">
          <div className="text-xs text-slate-500 font-medium flex items-center justify-between mb-1">
            <span>SMA 20</span>
            <span className="text-[10px] text-slate-400 font-medium">20-day</span>
          </div>
          <div className="text-xl font-bold font-mono text-slate-900">
            ₹{indicators.sma20?.toFixed(2)}
          </div>
          <div className="text-[11px] text-slate-500 mt-1 font-mono">
            SMA 50: ₹{indicators.sma50?.toFixed(2)}
          </div>
        </div>

        {/* Volatility */}
        <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-lg shadow-sm">
          <div className="text-xs text-slate-500 font-medium flex items-center justify-between mb-1">
            <span>Volatility</span>
            <span className="text-[10px] text-slate-400 font-medium">Annualized</span>
          </div>
          <div className="text-xl font-bold font-mono text-slate-900">
            {indicators.volatility}%
          </div>
          <div className="text-[11px] text-slate-500 mt-1 font-mono truncate">
            BB: [{indicators.bb_lower?.toFixed(0)} - {indicators.bb_upper?.toFixed(0)}]
          </div>
        </div>
      </div>
    </div>
  );
}
