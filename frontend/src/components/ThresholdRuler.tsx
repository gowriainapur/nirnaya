import React from 'react';
import { ThresholdBand } from '../types';

interface ThresholdRulerProps {
  currentValue: number | null;
  thresholdBand: ThresholdBand | null;
  route: string;
}

export const ThresholdRuler: React.FC<ThresholdRulerProps> = ({
  currentValue,
  thresholdBand,
  route
}) => {
  const val = currentValue || 0;
  
  // Standard bands: 0 to 25 Lakhs (or custom maximum)
  const maxScale = 2500000;
  const pct = Math.min(100, Math.max(0, (val / maxScale) * 100));

  const markers = [
    { label: '₹0', value: 0, pct: 0 },
    { label: '₹50K (Rule 154)', value: 50000, pct: (50000 / maxScale) * 100 },
    { label: '₹5L (Rule 155)', value: 500000, pct: (500000 / maxScale) * 100 },
    { label: '₹25L (LTE/Open)', value: 2500000, pct: 100 }
  ];

  return (
    <div className="bg-navy-900/80 border border-slate-800 rounded-xl p-5 shadow-inner">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-mono uppercase tracking-wider text-cyan-400 font-semibold">
            Dynamic Threshold Scale
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
            {thresholdBand?.rule_ref || 'Rule Baseline'}
          </span>
        </div>
        <div className="text-sm font-mono text-slate-200">
          Evaluated Value: <span className="text-cyan-400 font-bold">₹{val.toLocaleString('en-IN')}</span>
        </div>
      </div>

      {/* Progress Bar Container */}
      <div className="relative w-full h-4 bg-slate-950 rounded-full overflow-hidden border border-slate-800 my-6">
        {/* Tier Color Zones */}
        <div className="absolute inset-0 flex">
          <div className="h-full bg-emerald-500/20 border-r border-emerald-500/40" style={{ width: `${(50000 / maxScale) * 100}%` }}></div>
          <div className="h-full bg-cyan-500/20 border-r border-cyan-500/40" style={{ width: `${((500000 - 50000) / maxScale) * 100}%` }}></div>
          <div className="h-full bg-violet-500/20 border-r border-violet-500/40" style={{ width: `${((2500000 - 500000) / maxScale) * 100}%` }}></div>
        </div>

        {/* Current Value Indicator Bar */}
        <div
          className="h-full bg-gradient-to-r from-cyan-500 via-cyan-400 to-amber-400 transition-all duration-500 rounded-full"
          style={{ width: `${pct}%` }}
        ></div>

        {/* Value Pin */}
        <div
          className="absolute top-0 bottom-0 w-1 bg-amber-300 shadow-[0_0_8px_rgba(245,158,11,0.8)] z-10"
          style={{ left: `${pct}%` }}
        ></div>
      </div>

      {/* Marker Labels */}
      <div className="relative w-full flex justify-between text-[11px] font-mono text-slate-400">
        {markers.map((m, idx) => (
          <div key={idx} className="flex flex-col items-center">
            <span className="w-0.5 h-2 bg-slate-700 mb-1"></span>
            <span className={val >= m.value ? 'text-cyan-300 font-medium' : 'text-slate-500'}>
              {m.label}
            </span>
          </div>
        ))}
      </div>

      {/* Applicable Band Banner */}
      {thresholdBand && (
        <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-300">
          <div>
            Active Band: <span className="font-mono text-cyan-300 font-semibold">₹{thresholdBand.lower.toLocaleString('en-IN')} – {thresholdBand.upper ? `₹${thresholdBand.upper.toLocaleString('en-IN')}` : 'Above'}</span>
          </div>
          <div className="font-mono text-[11px] text-slate-400">
            Source: {thresholdBand.source_doc} (p.{thresholdBand.page || 'N/A'})
          </div>
        </div>
      )}
    </div>
  );
};
