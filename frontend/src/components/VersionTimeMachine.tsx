import React, { useState } from 'react';
import { History, ArrowRight, ShieldCheck, Clock } from 'lucide-react';
import { assessProcurement } from '../lib/api';
import { AssessmentResponse } from '../types';

export const VersionTimeMachine: React.FC = () => {
  const [value, setValue] = useState(40000);
  const [item, setItem] = useState('Laboratory equipment and testing apparatus');
  const [historicalRes, setHistoricalRes] = useState<AssessmentResponse | null>(null);
  const [currentRes, setCurrentRes] = useState<AssessmentResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const runComparison = async () => {
    setLoading(true);
    try {
      // Historical: Date in 2023
      const hist = await assessProcurement({
        item_description: item,
        category: 'goods',
        estimated_value_inr: value,
        tax_inclusive: true,
        procurement_date: '2023-05-10',
        gem_status: 'unavailable_verified',
        funding_source: 'institute',
        institution_policy_loaded: true,
        research_purpose: false,
        scientific_equipment: false,
        special_research_eligibility: 'not_eligible',
        is_emergency: false,
        is_proprietary: false,
        is_single_source: false,
        is_rate_contract_item: false,
        contains_installation: false,
        contains_commissioning: false,
        contains_training: false,
        contains_maintenance: false,
        contains_software: false,
        contains_cloud: false,
        contains_integration: false,
        related_recent_purchases: []
      });

      // Current: Date in 2026
      const curr = await assessProcurement({
        item_description: item,
        category: 'goods',
        estimated_value_inr: value,
        tax_inclusive: true,
        procurement_date: '2026-02-15',
        gem_status: 'unavailable_verified',
        funding_source: 'institute',
        institution_policy_loaded: true,
        research_purpose: false,
        scientific_equipment: false,
        special_research_eligibility: 'not_eligible',
        is_emergency: false,
        is_proprietary: false,
        is_single_source: false,
        is_rate_contract_item: false,
        contains_installation: false,
        contains_commissioning: false,
        contains_training: false,
        contains_maintenance: false,
        contains_software: false,
        contains_cloud: false,
        contains_integration: false,
        related_recent_purchases: []
      });

      setHistoricalRes(hist);
      setCurrentRes(curr);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="bg-navy-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl space-y-6">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
          <div className="w-10 h-10 rounded-xl bg-violet-500/20 text-violet-400 flex items-center justify-center border border-violet-500/40">
            <History className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold font-mono text-slate-100">
              Version Time Machine (§51)
            </h2>
            <p className="text-xs text-slate-400">
              Evaluate how the exact same procurement is treated under Historical GFR 2017 vs Current GFR 2017 (Updated 31.01.2026).
            </p>
          </div>
        </div>

        {/* Input Parameters */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="sm:col-span-2 space-y-1.5">
            <label className="text-xs font-mono text-slate-300">Item Description</label>
            <input
              type="text"
              value={item}
              onChange={(e) => setItem(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-navy-950 border border-slate-700 text-sm text-slate-200 font-sans"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-mono text-slate-300">Purchase Value (INR)</label>
            <input
              type="number"
              value={value}
              onChange={(e) => setValue(parseInt(e.target.value) || 0)}
              className="w-full px-3 py-2 rounded-xl bg-navy-950 border border-slate-700 text-sm font-mono text-cyan-300"
            />
          </div>
        </div>

        <button
          onClick={runComparison}
          disabled={loading}
          className="px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-mono text-xs font-bold transition-all flex items-center space-x-2"
        >
          <Clock className="w-4 h-4" />
          <span>{loading ? 'Simulating Version Differences...' : 'Run Time Machine Comparison'}</span>
        </button>

        {/* Side-by-Side Comparison Columns */}
        {historicalRes && currentRes && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-slate-800">
            {/* Historical Card */}
            <div className="p-5 rounded-xl bg-navy-950/90 border border-amber-500/40 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <span className="text-xs font-mono font-bold text-amber-400">HISTORICAL GFR 2017 (Original Baseline)</span>
                <span className="text-[10px] font-mono text-slate-400">As-Of: 10/05/2023</span>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Applicable Route:</span>
                  <span className="font-mono font-bold text-amber-300 uppercase">
                    {historicalRes.decision.procurement_route.replace(/_/g, ' ')}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Statutory Ceiling:</span>
                  <span className="font-mono text-slate-200">
                    Direct: ₹25,000 | Committee: ₹2,50,000
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Rule Reference:</span>
                  <span className="font-mono text-slate-200">GFR 2017 Rule 154/155 (p.34)</span>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-slate-300 leading-relaxed font-sans">
                At ₹{value.toLocaleString('en-IN')}, this procurement exceeded the historical direct purchase limit of ₹25,000 and required a Local Purchase Committee under Rule 155.
              </div>
            </div>

            {/* Current Card */}
            <div className="p-5 rounded-xl bg-navy-950/90 border border-emerald-500/40 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <span className="text-xs font-mono font-bold text-emerald-400">CURRENT GFR 2017 (Updated 31.01.2026)</span>
                <span className="text-[10px] font-mono text-slate-400">As-Of: 15/02/2026</span>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-400">Applicable Route:</span>
                  <span className="font-mono font-bold text-emerald-300 uppercase">
                    {currentRes.decision.procurement_route.replace(/_/g, ' ')}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Statutory Ceiling:</span>
                  <span className="font-mono text-slate-200">
                    Direct: ₹50,000 | Committee: ₹5,00,000
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Rule Reference:</span>
                  <span className="font-mono text-slate-200">GFR 2017 Rule 154/155 (p.36)</span>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-slate-300 leading-relaxed font-sans">
                Under the updated 2026 compilation, the direct purchase threshold is enhanced to ₹50,000. At ₹{value.toLocaleString('en-IN')}, it now qualifies for Direct Purchase under Rule 154!
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
