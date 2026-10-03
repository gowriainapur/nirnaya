import React, { useState } from 'react';
import { Cpu, RefreshCw, Sliders, ArrowRight } from 'lucide-react';
import { simulateWhatIf } from '../lib/api';
import { ProcurementInput } from '../types';

export const WhatIfSimulator: React.FC = () => {
  const [val, setVal] = useState(48000);
  const [gemStatus, setGemStatus] = useState<'unavailable_verified' | 'available_verified'>('unavailable_verified');
  const [researchEligible, setResearchEligible] = useState<'not_eligible' | 'eligible'>('not_eligible');
  const [isEmergency, setIsEmergency] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const runSimulation = async () => {
    setLoading(true);
    const baseInput: ProcurementInput = {
      item_description: 'Precision analytical instrument',
      category: 'goods',
      estimated_value_inr: val,
      tax_inclusive: true,
      procurement_date: '2026-02-15',
      gem_status: gemStatus,
      funding_source: 'institute',
      institution_policy_loaded: true,
      research_purpose: researchEligible === 'eligible',
      scientific_equipment: researchEligible === 'eligible',
      special_research_eligibility: researchEligible,
      is_emergency: isEmergency,
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
    };

    const variations = {
      estimated_value_inr: val > 50000 ? 45000 : 52000,
      gem_status: gemStatus === 'unavailable_verified' ? 'available_verified' : 'unavailable_verified',
      special_research_eligibility: researchEligible === 'eligible' ? 'not_eligible' : 'eligible',
      is_emergency: !isEmergency
    };

    try {
      const data = await simulateWhatIf(baseInput, variations);
      setResults(data.results || []);
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
          <div className="w-10 h-10 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center border border-cyan-500/40">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold font-mono text-slate-100">
              Deterministic What-If Simulator (§52)
            </h2>
            <p className="text-xs text-slate-400">
              Dynamically manipulate purchase parameters and observe immediate deterministic route adjustments.
            </p>
          </div>
        </div>

        {/* Live Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="space-y-1.5">
            <label className="text-xs font-mono text-slate-300">Purchase Value (INR)</label>
            <input
              type="number"
              value={val}
              onChange={(e) => setVal(parseInt(e.target.value) || 0)}
              className="w-full px-3 py-2 rounded-xl bg-navy-950 border border-slate-700 text-sm font-mono text-cyan-300"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-mono text-slate-300">GeM Status</label>
            <select
              value={gemStatus}
              onChange={(e) => setGemStatus(e.target.value as any)}
              className="w-full px-3 py-2 rounded-xl bg-navy-950 border border-slate-700 text-sm text-slate-200"
            >
              <option value="unavailable_verified">Unavailable on GeM (Verified)</option>
              <option value="available_verified">Available on GeM (Rule 149)</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-mono text-slate-300">Research Eligibility</label>
            <select
              value={researchEligible}
              onChange={(e) => setResearchEligible(e.target.value as any)}
              className="w-full px-3 py-2 rounded-xl bg-navy-950 border border-slate-700 text-sm text-slate-200"
            >
              <option value="not_eligible">Standard Purchase (Standard limits)</option>
              <option value="eligible">Eligible Research (₹2L / ₹25L)</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-mono text-slate-300">Emergency Route</label>
            <button
              onClick={() => setIsEmergency(!isEmergency)}
              className={`w-full px-3 py-2 rounded-xl border text-xs font-mono font-semibold transition-all ${
                isEmergency
                  ? 'bg-crimson-500/20 text-crimson-400 border-crimson-500/40'
                  : 'bg-navy-950 text-slate-400 border-slate-700'
              }`}
            >
              {isEmergency ? 'Emergency Declared (ESCALATE)' : 'Normal Routine'}
            </button>
          </div>
        </div>

        <button
          onClick={runSimulation}
          disabled={loading}
          className="px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-navy-950 font-mono text-xs font-bold transition-all flex items-center space-x-2"
        >
          <Sliders className="w-4 h-4" />
          <span>{loading ? 'Evaluating Variations...' : 'Simulate Controlled Variations'}</span>
        </button>

        {/* Results Matrix */}
        {results.length > 0 && (
          <div className="space-y-3 pt-4 border-t border-slate-800">
            <h4 className="text-xs font-mono uppercase tracking-wider text-slate-300">
              Deterministic Simulation Matrix
            </h4>
            <div className="overflow-x-auto">
              <table className="w-full text-xs font-mono text-left border border-slate-800 rounded-xl overflow-hidden">
                <thead className="bg-navy-950 text-slate-400 border-b border-slate-800">
                  <tr>
                    <th className="p-3">Scenario</th>
                    <th className="p-3">Parameter Varied</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Evaluated Route</th>
                    <th className="p-3">Threshold Upper</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 bg-navy-900/40">
                  {results.map((r, idx) => (
                    <tr key={idx} className={idx === 0 ? 'bg-cyan-500/5' : ''}>
                      <td className="p-3 font-semibold text-slate-200">
                        {r.scenario} {idx === 0 && <span className="text-[10px] text-cyan-400">(Base)</span>}
                      </td>
                      <td className="p-3 text-slate-400">{r.changed_parameter} {r.value ? `(${r.value})` : ''}</td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] ${
                          r.status === 'COMPLETE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                          r.status === 'NEEDS_INFO' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                          'bg-crimson-500/10 text-crimson-400 border border-crimson-500/30'
                        }`}>
                          {r.status}
                        </span>
                      </td>
                      <td className="p-3 font-bold text-cyan-300">{r.route.replace(/_/g, ' ')}</td>
                      <td className="p-3 text-slate-300">
                        {r.threshold_upper ? `₹${r.threshold_upper.toLocaleString('en-IN')}` : 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
