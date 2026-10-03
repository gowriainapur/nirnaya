import React, { useState, useEffect } from 'react';
import { Database, ShieldCheck, AlertTriangle, ExternalLink } from 'lucide-react';
import { fetchSources } from '../lib/api';
import { SourceDocument } from '../types';

export const SourceRegisterView: React.FC = () => {
  const [sources, setSources] = useState<SourceDocument[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const data = await fetchSources();
        setSources(data || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="bg-navy-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl space-y-6">
        <div className="flex items-center space-x-3 border-b border-slate-800 pb-4">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center border border-cyan-500/40">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold font-mono text-slate-100">
              Authoritative Source Register (§6, §25, §67)
            </h2>
            <p className="text-xs text-slate-400">
              Complete catalog of ingested statutory procurement rules, manuals, OMs, and demonstration policies.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto border border-slate-800 rounded-xl overflow-hidden">
          <table className="w-full text-xs font-mono text-left">
            <thead className="bg-navy-950 text-slate-400 border-b border-slate-800">
              <tr>
                <th className="p-3">Document Title</th>
                <th className="p-3">Issuer</th>
                <th className="p-3 text-center">Authority Level</th>
                <th className="p-3">Version / Date</th>
                <th className="p-3">Status</th>
                <th className="p-3 text-center">Synthetic?</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 bg-navy-900/40">
              {sources.map((s, idx) => (
                <tr key={idx} className="hover:bg-slate-800/20">
                  <td className="p-3 font-semibold text-slate-200">
                    <div>{s.title}</div>
                    <div className="text-[10px] text-slate-500 font-mono mt-0.5">{s.doc_id}</div>
                  </td>
                  <td className="p-3 text-slate-400">{s.issuer}</td>
                  <td className="p-3 text-center">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 font-bold">
                      Level {s.authority_level}
                    </span>
                  </td>
                  <td className="p-3 text-slate-300">
                    <div>{s.version}</div>
                    <div className="text-[10px] text-slate-500">{s.publication_date}</div>
                  </td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      s.verified ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                      'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                    }`}>
                      {s.verified ? 'VERIFIED' : 'DEMO OVERLAY'}
                    </span>
                  </td>
                  <td className="p-3 text-center">
                    {s.is_synthetic ? (
                      <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-bold border border-amber-500/40">
                        SYNTHETIC
                      </span>
                    ) : (
                      <span className="text-slate-500">NO</span>
                    )}
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
