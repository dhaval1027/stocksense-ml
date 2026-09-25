import React from 'react';
import { Award, ShieldCheck } from 'lucide-react';

export default function ModelMetrics({ metrics }) {
  if (!metrics) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4">
        <div>
          <h2 className="text-sm font-bold text-slate-900 tracking-wide uppercase flex items-center gap-2">
            <Award className="w-4 h-4 text-blue-600" />
            Model Performance (Untouched Test Set)
          </h2>
          <p className="text-xs text-slate-500">
            Chronological holdout evaluation ({metrics.test_samples} trading days)
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-500 font-medium">Selected Model:</span>
          <span className="px-2.5 py-1 text-xs font-semibold rounded-md bg-blue-50 text-blue-700 border border-blue-200 shadow-sm">
            {metrics.selected_model}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        {/* Accuracy */}
        <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-lg text-center shadow-sm">
          <div className="text-xs text-slate-500 font-medium mb-1">Accuracy</div>
          <div className="text-2xl font-bold font-mono text-slate-900">
            {metrics.accuracy}%
          </div>
          <div className="text-[10px] text-slate-400 mt-1">Correct / Total</div>
        </div>

        {/* Precision */}
        <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-lg text-center shadow-sm">
          <div className="text-xs text-slate-500 font-medium mb-1">Precision</div>
          <div className="text-2xl font-bold font-mono text-slate-900">
            {metrics.precision}%
          </div>
          <div className="text-[10px] text-slate-400 mt-1">True UP / Pred UP</div>
        </div>

        {/* Recall */}
        <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-lg text-center shadow-sm">
          <div className="text-xs text-slate-500 font-medium mb-1">Recall</div>
          <div className="text-2xl font-bold font-mono text-slate-900">
            {metrics.recall}%
          </div>
          <div className="text-[10px] text-slate-400 mt-1">True UP / Actual UP</div>
        </div>

        {/* F1 Score */}
        <div className="bg-slate-50 border border-slate-200 p-3.5 rounded-lg text-center shadow-sm">
          <div className="text-xs text-slate-500 font-medium mb-1">Macro F1 Score</div>
          <div className="text-2xl font-bold font-mono text-emerald-600">
            {metrics.f1_macro || metrics.f1}%
          </div>
          <div className="text-[10px] text-slate-400 mt-1">Balanced UP & DOWN</div>
        </div>
      </div>

      <div className="mt-3.5 flex flex-wrap items-center justify-between text-xs text-slate-500 pt-3 border-t border-slate-100 gap-2">
        <span className="flex items-center gap-1.5 font-medium">
          <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
          Zero Data Leakage: Decision threshold ({metrics.threshold || '0.50'}) selected strictly on validation fold.
        </span>
        <span className="font-mono text-slate-700 font-semibold">
          ROC-AUC: {metrics.roc_auc} • Binary F1: {metrics.f1}%
        </span>
      </div>
    </div>
  );
}
