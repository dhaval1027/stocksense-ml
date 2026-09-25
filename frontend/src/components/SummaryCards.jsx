import React from 'react';
import { ArrowUpRight, ArrowDownRight, TrendingUp, TrendingDown, Target } from 'lucide-react';

export default function SummaryCards({ data }) {
  if (!data) return null;

  const isUp = data.prediction === 'UP';
  const isChangePositive = data.daily_change_pct >= 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* 1. Current Price Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm relative overflow-hidden">
        <div className="flex items-center justify-between text-xs text-slate-500 font-semibold mb-1.5 uppercase tracking-wider">
          <span>Current Price</span>
          <span className="text-slate-400 font-mono">NSE • INR</span>
        </div>
        <div className="flex items-baseline space-x-2">
          <span className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 font-mono">
            ₹{data.current_price?.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
        </div>
        <div className="mt-2 text-xs text-slate-500">
          Prev Close: <span className="font-mono text-slate-700 font-medium">₹{data.previous_close?.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
        </div>
      </div>

      {/* 2. Today's Change Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm relative overflow-hidden">
        <div className="flex items-center justify-between text-xs text-slate-500 font-semibold mb-1.5 uppercase tracking-wider">
          <span>Today's Change</span>
          <span className="text-slate-400 font-mono">Last Session</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`p-1.5 rounded-lg ${isChangePositive ? 'bg-emerald-50 text-emerald-600 border border-emerald-200' : 'bg-rose-50 text-rose-600 border border-rose-200'}`}>
            {isChangePositive ? (
              <ArrowUpRight className="w-5 h-5" />
            ) : (
              <ArrowDownRight className="w-5 h-5" />
            )}
          </div>
          <span
            className={`text-2xl sm:text-3xl font-bold tracking-tight font-mono ${
              isChangePositive ? 'text-emerald-600' : 'text-rose-600'
            }`}
          >
            {isChangePositive ? '+' : ''}{data.daily_change_pct?.toFixed(2)}%
          </span>
        </div>
        <div className="mt-2 text-xs text-slate-500">
          As of: <span className="font-mono text-slate-700 font-medium">{data.prediction_date}</span>
        </div>
      </div>

      {/* 3. ML Prediction Card */}
      <div className={`border rounded-xl p-5 shadow-sm relative overflow-hidden ${
        isUp 
          ? 'bg-emerald-50/70 border-emerald-300' 
          : 'bg-rose-50/70 border-rose-300'
      }`}>
        <div className="flex items-center justify-between text-xs font-semibold mb-1.5">
          <span className={`flex items-center gap-1.5 uppercase tracking-wider ${isUp ? 'text-emerald-800' : 'text-rose-800'}`}>
            <Target className="w-3.5 h-3.5 text-blue-600" />
            Next Trading Day Direction
          </span>
          <span className="text-xs font-mono text-slate-600 bg-white/70 px-2 py-0.5 rounded border border-slate-200">
            {data.selected_model}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className={`p-2 rounded-lg ${isUp ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
              {isUp ? (
                <TrendingUp className="w-7 h-7" />
              ) : (
                <TrendingDown className="w-7 h-7" />
              )}
            </div>
            <span
              className={`text-3xl font-extrabold tracking-tight font-mono ${
                isUp ? 'text-emerald-700' : 'text-rose-700'
              }`}
            >
              {isUp ? '↑ UP' : '↓ DOWN'}
            </span>
          </div>

          <div className="text-right">
            <div className="text-xs text-slate-600 font-medium">Model Confidence</div>
            <div className={`text-xl font-bold font-mono ${isUp ? 'text-emerald-800' : 'text-rose-800'}`}>
              {data.probability}%
            </div>
          </div>
        </div>

        <div className="mt-2.5 text-[11px] text-slate-600 flex items-center justify-between border-t border-slate-200/80 pt-2">
          <span>Ensemble Calibrated Confidence</span>
          <span className="font-mono text-slate-700 font-medium">P({data.prediction}) = {data.probability}%</span>
        </div>
      </div>
    </div>
  );
}
