import React from 'react';
import { TrendingUp, Cpu } from 'lucide-react';

export default function Header() {
  return (
    <header className="border-b border-slate-200 bg-white/95 backdrop-blur-md sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-50 border border-blue-200 rounded-lg flex items-center justify-center text-blue-600 shadow-sm">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
                StockSense
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                  ML Trend Prediction
                </span>
              </h1>
            </div>
            <p className="text-xs text-slate-500">
              Machine learning based directional analysis of Indian equities
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3 self-end sm:self-auto text-xs text-slate-600">
          <div className="flex items-center space-x-1.5 bg-slate-100 px-2.5 py-1 rounded-md border border-slate-200 shadow-sm">
            <Cpu className="w-3.5 h-3.5 text-blue-600" />
            <span className="text-slate-700 font-mono font-medium">Trained Classifiers</span>
          </div>
          <div className="flex items-center space-x-1.5 bg-slate-100 px-2.5 py-1 rounded-md border border-slate-200 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-slate-700 font-mono font-medium">NSE Live Feed</span>
          </div>
        </div>
      </div>
    </header>
  );
}
