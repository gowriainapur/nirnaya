import React from 'react';
import { X, ShieldCheck, AlertTriangle, ExternalLink, BookOpen, Layers } from 'lucide-react';
import { CitationRef } from '../types';

interface SourceDrawerProps {
  citation: CitationRef | null;
  onClose: () => void;
}

export const SourceDrawer: React.FC<SourceDrawerProps> = ({ citation, onClose }) => {
  if (!citation) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end transition-opacity">
      <div className="w-full max-w-lg bg-navy-950 border-l border-cyan-500/30 shadow-2xl h-full flex flex-col p-6 overflow-y-auto">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-1 rounded bg-cyan-500/20 text-cyan-400 font-mono text-xs font-bold border border-cyan-500/40">
              {citation.citation_id}
            </span>
            <span className="text-sm font-bold text-slate-100 font-mono">{citation.rule_ref}</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Authority Tier Tag */}
        <div className="mt-4 flex items-center space-x-2">
          {citation.authority_level === 1 && (
            <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-semibold flex items-center space-x-1.5">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>LEVEL 1 — PRIMARY OFFICIAL GOVERNMENT SOURCE</span>
            </span>
          )}
          {citation.authority_level === 2 && (
            <span className="px-3 py-1 rounded-full bg-violet-500/10 text-violet-400 border border-violet-500/30 text-xs font-mono font-semibold flex items-center space-x-1.5">
              <Layers className="w-3.5 h-3.5" />
              <span>LEVEL 2 — INSTITUTIONAL PRIMARY SOURCE</span>
            </span>
          )}
          {citation.is_synthetic && (
            <span className="px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 text-xs font-mono font-semibold flex items-center space-x-1.5">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>SYNTHETIC / DEMONSTRATION POLICY</span>
            </span>
          )}
        </div>

        {/* Metadata Grid */}
        <div className="mt-6 bg-navy-900/60 border border-slate-800/80 rounded-xl p-4 space-y-3 text-xs">
          <div className="flex justify-between py-1 border-b border-slate-800/60">
            <span className="text-slate-400">Source Document:</span>
            <span className="font-mono text-cyan-300 font-semibold">{citation.source_title}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-800/60">
            <span className="text-slate-400">Statutory Version:</span>
            <span className="font-mono text-slate-200">{citation.source_version}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-800/60">
            <span className="text-slate-400">Document Page / Section:</span>
            <span className="font-mono text-slate-200">Page {citation.page || 'N/A'}</span>
          </div>
          <div className="flex justify-between py-1">
            <span className="text-slate-400">Provenance Status:</span>
            <span className="font-mono text-emerald-400 flex items-center space-x-1">
              <ShieldCheck className="w-3 h-3" />
              <span>Verified Statutory Clause</span>
            </span>
          </div>
        </div>

        {/* Verbatim Statutory Excerpt */}
        <div className="mt-6 flex-1">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-2 flex items-center space-x-1.5">
            <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
            <span>Statutory Clause Excerpt</span>
          </h4>
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs font-mono text-slate-300 leading-relaxed overflow-y-auto max-h-72 whitespace-pre-wrap selection:bg-cyan-500/40">
            {citation.excerpt}
          </div>
        </div>

        <div className="mt-6 pt-4 border-t border-slate-800 text-[11px] text-slate-500 flex items-center justify-between">
          <span>Provenance verified against official DoE / MoF publication.</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-mono text-xs transition-colors"
          >
            Close Drawer
          </button>
        </div>
      </div>
    </div>
  );
};
