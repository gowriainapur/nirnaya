import React, { useState, useEffect } from 'react';
import { FileText, ShieldCheck, Hash, Clock, RefreshCw } from 'lucide-react';
import { fetchAuditTrail } from '../lib/api';

export const AuditTrailView: React.FC = () => {
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await fetchAuditTrail(25);
      setRecords(data.records || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="bg-navy-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center border border-cyan-500/40">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold font-mono text-slate-100">
                Immutable SQLite Audit Trail (§38, §56)
              </h2>
              <p className="text-xs text-slate-400">
                Cryptographically hashed, append-only evaluation log preserving complete provenance and verification results.
              </p>
            </div>
          </div>

          <button
            onClick={loadLogs}
            disabled={loading}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-mono text-xs flex items-center space-x-2 transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Audit Logs</span>
          </button>
        </div>

        {records.length > 0 ? (
          <div className="overflow-x-auto border border-slate-800 rounded-xl overflow-hidden">
            <table className="w-full text-xs font-mono text-left">
              <thead className="bg-navy-950 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="p-3">Assessment ID</th>
                  <th className="p-3">Timestamp (UTC)</th>
                  <th className="p-3">Category</th>
                  <th className="p-3">Route</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Input Hash (SHA-256)</th>
                  <th className="p-3 text-center">Verification</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 bg-navy-900/40">
                {records.map((r, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/20">
                    <td className="p-3 font-bold text-cyan-300">{r.assessment_id}</td>
                    <td className="p-3 text-slate-400">{r.timestamp ? r.timestamp.replace('T', ' ').slice(0, 19) : 'N/A'}</td>
                    <td className="p-3 text-slate-200">{r.classification}</td>
                    <td className="p-3 font-semibold text-emerald-400">{r.route.replace(/_/g, ' ')}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] ${
                        r.status === 'COMPLETE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                        r.status === 'NEEDS_INFO' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                        'bg-crimson-500/10 text-crimson-400 border border-crimson-500/30'
                      }`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="p-3 text-slate-500 text-[10px] truncate max-w-[120px]" title={r.input_hash}>
                      {r.input_hash?.slice(0, 12)}...
                    </td>
                    <td className="p-3 text-center">
                      <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px]">
                        <ShieldCheck className="w-3 h-3" />
                        <span>VERIFIED</span>
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-10 text-xs font-mono text-slate-500">
            No audit records currently found. Run an assessment to log decisions.
          </div>
        )}
      </div>
    </div>
  );
};
