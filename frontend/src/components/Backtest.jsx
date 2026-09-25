import React from 'react';
import { History } from 'lucide-react';

export default function Backtest({ backtest }) {
  if (!backtest) return null;

  const isStrategyProfitable = backtest.strategy_return >= 0;
  const isBuyHoldProfitable = backtest.buy_hold_return >= 0;
  const outperformsBuyHold = backtest.strategy_return > backtest.buy_hold_return;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900 tracking-wide uppercase flex items-center gap-2">
            <History className="w-4 h-4 text-blue-600" />
            Strategy Backtest Simulation
          </h2>
          <p className="text-xs text-slate-500">
            Hold stock when ML predicts UP, hold cash when DOWN (Test Period)
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-[11px] font-mono font-medium px-2.5 py-1 rounded bg-slate-100 text-slate-700 border border-slate-200 shadow-sm">
            Fee: {backtest.transaction_cost_pct}% per switch
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        {/* ML Strategy Return */}
        <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-lg shadow-sm">
          <div className="text-xs text-slate-500 font-medium mb-1">ML Strategy Return</div>
          <div className={`text-2xl font-bold font-mono ${isStrategyProfitable ? 'text-emerald-600' : 'text-rose-600'}`}>
            {isStrategyProfitable ? '+' : ''}{backtest.strategy_return}%
          </div>
          <div className="text-[10px] text-slate-500 mt-1 font-medium">
            {outperformsBuyHold ? 'Outperforms Buy & Hold' : 'Underperforms Benchmark'}
          </div>
        </div>

        {/* Buy & Hold Return */}
        <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-lg shadow-sm">
          <div className="text-xs text-slate-500 font-medium mb-1">Buy & Hold Return</div>
          <div className={`text-2xl font-bold font-mono ${isBuyHoldProfitable ? 'text-emerald-600' : 'text-rose-600'}`}>
            {isBuyHoldProfitable ? '+' : ''}{backtest.buy_hold_return}%
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Passive Benchmark</div>
        </div>

        {/* Max Drawdown */}
        <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-lg shadow-sm">
          <div className="text-xs text-slate-500 font-medium mb-1">Max Drawdown</div>
          <div className="text-2xl font-bold font-mono text-amber-600">
            {backtest.max_drawdown}%
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Peak-to-Trough Decline</div>
        </div>

        {/* Win Rate */}
        <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-lg shadow-sm">
          <div className="text-xs text-slate-500 font-medium mb-1">Trade Win Rate</div>
          <div className="text-2xl font-bold font-mono text-slate-900">
            {backtest.win_rate}%
          </div>
          <div className="text-[10px] text-slate-500 mt-1">
            {backtest.up_signals} UP / {backtest.down_signals} DOWN
          </div>
        </div>
      </div>

      <div className="mt-3.5 flex flex-wrap items-center justify-between text-xs text-slate-500 pt-3 border-t border-slate-100 gap-2">
        <span>Total Test Signals: <span className="font-mono text-slate-700 font-semibold">{backtest.total_signals} sessions</span></span>
        <span className="text-[11px] text-slate-500 italic">Realistic 0.1% transaction cost subtracted per trade switch.</span>
      </div>
    </div>
  );
}
