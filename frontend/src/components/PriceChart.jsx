import React, { useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { Activity } from 'lucide-react';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const closeItem = payload.find(p => p.dataKey === 'close');
    const smaItem = payload.find(p => p.dataKey === 'sma20');

    return (
      <div className="bg-white border border-slate-200 p-3 rounded-lg shadow-md text-xs space-y-1 font-mono">
        <div className="text-slate-500 font-sans font-medium border-b border-slate-100 pb-1 mb-1">
          {label}
        </div>
        {closeItem && (
          <div className="flex items-center justify-between gap-4">
            <span className="text-blue-600 flex items-center gap-1.5 font-medium">
              <span className="w-2 h-2 rounded-full bg-blue-600"></span>
              Close Price:
            </span>
            <span className="font-semibold text-slate-900">₹{closeItem.value.toFixed(2)}</span>
          </div>
        )}
        {smaItem && smaItem.value && (
          <div className="flex items-center justify-between gap-4">
            <span className="text-amber-600 flex items-center gap-1.5 font-medium">
              <span className="w-2 h-2 rounded-full bg-amber-500"></span>
              SMA 20:
            </span>
            <span className="font-semibold text-slate-900">₹{smaItem.value.toFixed(2)}</span>
          </div>
        )}
      </div>
    );
  }
  return null;
};

export default function PriceChart({ chartData, data, ticker }) {
  const [showSMA, setShowSMA] = useState(true);
  const actualData = chartData || data || [];

  if (!actualData || actualData.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-8 text-center text-slate-400">
        No price history available.
      </div>
    );
  }

  // Calculate dynamic min/max for clean Y-axis domain
  const prices = actualData.map(d => d.close);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const padding = (maxPrice - minPrice) * 0.05 || 10;
  const yDomain = [Math.floor(minPrice - padding), Math.ceil(maxPrice + padding)];

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900 tracking-wide uppercase flex items-center gap-2">
            <Activity className="w-4 h-4 text-blue-600" />
            Price History & Trend (Past 12 Months)
          </h2>
          <p className="text-xs text-slate-500">Daily Close and 20-day Simple Moving Average</p>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <button
            onClick={() => setShowSMA(!showSMA)}
            className={`px-2.5 py-1 rounded-md border font-medium transition-colors ${
              showSMA
                ? 'bg-amber-50 border-amber-300 text-amber-800'
                : 'bg-slate-100 border-slate-300 text-slate-600 hover:text-slate-900'
            }`}
          >
            SMA 20 {showSMA ? 'ON' : 'OFF'}
          </button>
        </div>
      </div>

      <div className="h-72 sm:h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={actualData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={{ stroke: '#E2E8F0' }}
              tick={{ fill: '#64748B', fontSize: 11 }}
              tickFormatter={(str) => {
                const parts = str.split('-');
                return parts.length === 3 ? `${parts[1]}/${parts[0].slice(2)}` : str;
              }}
              minTickGap={40}
            />
            <YAxis
              domain={yDomain}
              tickLine={false}
              axisLine={{ stroke: '#E2E8F0' }}
              tick={{ fill: '#64748B', fontSize: 11 }}
              tickFormatter={(v) => `₹${v}`}
              width={65}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="close"
              name="Close Price"
              stroke="#2563EB"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, stroke: '#3B82F6', strokeWidth: 2, fill: '#1D4ED8' }}
            />
            {showSMA && (
              <Line
                type="monotone"
                dataKey="sma20"
                name="SMA 20"
                stroke="#D97706"
                strokeWidth={1.5}
                strokeDasharray="4 4"
                dot={false}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
