import React, { useState, useEffect } from 'react';
import { GitCompare, ArrowRight, ShieldCheck } from 'lucide-react';
import { comparePolicies } from '../lib/api';

export const PolicyDiff: React.FC = () => {
  const [diffData, setDiffData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadDiff = async () => {
      setLoading(true);
      try {
        const data = await comparePolicies('gfr_2017_historical_original', 'gfr_2017_updated_31_01_2026');
        setDiffData(data.comparison || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    loadDiff();
  }, []);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="bg-navy-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl space-y-6">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center border border-cyan-500/40">
            <GitCompare className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold font-mono text-slate-100">
              Policy Diff & Threshold Evolution (§57)
            </h2>
            <p className="text-xs text-slate-400">
              Auditable comparison of statutory procurement thresholds and procedures between Historical GFR and 2026 Update.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto border border-slate-800 rounded-xl overflow-hidden">
          <table className="w-full text-xs font-mono text-left">
            <thead className="bg-navy-950 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="p-3.5">Statutory Parameter</th>
                <th className="p-3.5">GFR 2017 Original</th>
                <th className="p-3.5">GFR 2017 (Updated 31.01.2026)</th>
                <th className="p-3.5">Delta / Evolution</th>
                <th className="p-3.5">Change Classification</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 bg-navy-900/40">
              {diffData.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-800/20">
                  <td className="p-3.5 font-semibold text-slate-200">{row.parameter}</td>
                  <td className="p-3.5 text-amber-300/90">
                    <div>{row.ruleset_a_value}</div>
                    <div className="text-[10px] text-slate-500">{row.ruleset_a_ref}</div>
                  </td>
                  <td className="p-3.5 text-emerald-300 font-bold">
                    <div>{row.ruleset_b_value}</div>
                    <div className="text-[10px] text-slate-400">{row.ruleset_b_ref}</div>
                  </td>
                  <td className="p-3.5 text-cyan-300 font-semibold">{row.delta}</td>
                  <td className="p-3.5">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                      {row.change_type}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
