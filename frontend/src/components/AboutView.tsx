import React, { useState, useEffect } from 'react';
import { Info, ShieldAlert, CheckCircle, Scale, Database } from 'lucide-react';
import { fetchHealth } from '../lib/api';

export const AboutView: React.FC = () => {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(console.error);
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-navy-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl space-y-6">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center border border-cyan-500/40">
            <Info className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold font-mono text-slate-100">
              About Procurement Compass (§66)
            </h2>
            <p className="text-xs text-slate-400">
              Institutional Procurement Decision-Support System • JIG26_30
            </p>
          </div>
        </div>

        {/* Mandatory Statutory Notice */}
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs font-mono leading-relaxed space-y-2">
          <div className="flex items-center space-x-2 font-bold uppercase tracking-wider text-amber-300">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            <span>Mandatory Decision-Support Notice</span>
          </div>
          <p>• Procurement Compass is <strong>decision-support software</strong>.</p>
          <p>• It <strong>does not approve purchases</strong>.</p>
          <p>• It <strong>does not replace the Competent Authority</strong>.</p>
          <p>• It <strong>does not provide legal or financial advice</strong>.</p>
          <p>• Central Government rules and institutional policies may differ. Always verify the applicable institutional policy and delegation of financial powers.</p>
        </div>

        {/* Corpus Metadata Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
          <div className="p-4 rounded-xl bg-navy-950 border border-slate-800">
            <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
              Active Ruleset
            </span>
            <div className="text-sm font-bold font-mono text-cyan-300">
              {health?.current_ruleset || 'gfr_2017_updated_31_01_2026'}
            </div>
            <span className="text-[10px] text-slate-500 block mt-0.5">Updated through 31.01.2026</span>
          </div>

          <div className="p-4 rounded-xl bg-navy-950 border border-slate-800">
            <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
              Statutory Sources
            </span>
            <div className="text-sm font-bold font-mono text-emerald-400">
              {health?.sources_count || 9} Ingested Documents
            </div>
            <span className="text-[10px] text-slate-500 block mt-0.5">
              {health?.policy_chunks_count || 18} Verified Clause Chunks
            </span>
          </div>

          <div className="p-4 rounded-xl bg-navy-950 border border-slate-800">
            <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
              Test Coverage
            </span>
            <div className="text-sm font-bold font-mono text-slate-200">
              28 Golden Scenarios
            </div>
            <span className="text-[10px] text-slate-500 block mt-0.5">40 Labelled Query Benchmarks</span>
          </div>
        </div>

        {/* Core Principles */}
        <div className="p-5 rounded-xl bg-navy-950 border border-slate-800 space-y-3 text-xs text-slate-300 leading-relaxed font-sans">
          <div className="font-mono font-bold text-slate-100 flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-cyan-400" />
            <span>Core Engineering Principles</span>
          </div>
          <p>
            <strong>The LLM Never Decides:</strong> In accordance with Section 2 of the specification, the LLM is purely an explanation layer. All threshold classifications, routing determinations, and conflict detections are 100% deterministic.
          </p>
          <p>
            <strong>Evidence-First Provenance:</strong> Every factual statement must cite a statutory clause. Monetary figures are machine-checked by an amount validator ensuring zero hallucinated values.
          </p>
          <p>
            <strong>Controlled Escalation:</strong> When critical information is missing or when policies conflict, the system halts with <code>NEEDS_INFO</code> or <code>ESCALATE</code> rather than guessing.
          </p>
        </div>
      </div>
    </div>
  );
};
