import React from 'react';
import { ArrowRight, CheckCircle2, AlertCircle, HelpCircle, FileText } from 'lucide-react';
import { DecisionObject } from '../types';

interface DecisionPathGraphProps {
  decision: DecisionObject;
  onOpenSource?: (ruleRef: string) => void;
}

export const DecisionPathGraph: React.FC<DecisionPathGraphProps> = ({
  decision,
  onOpenSource
}) => {
  const steps = [
    {
      title: 'Classification',
      value: decision.procurement_classification.category,
      subtitle: decision.procurement_classification.subtype || 'Primary category',
      status: decision.procurement_classification.classification_status === 'resolved' ? 'success' : 'warn',
      ruleRef: decision.procurement_classification.supporting_clauses[0] || 'Classification Manual'
    },
    {
      title: 'As-Of Ruleset',
      value: decision.ruleset_used === 'gfr_2017_updated_31_01_2026' ? 'GFR 2026' : 'Historical GFR',
      subtitle: 'Date-aware resolution',
      status: 'success',
      ruleRef: 'Effective Date Resolution'
    },
    {
      title: 'GeM Status',
      value: decision.gem_assessment.status.replace('_', ' ').toUpperCase(),
      subtitle: 'Rule 149 applicability',
      status: decision.gem_assessment.status === 'unavailable_verified' || decision.gem_assessment.status === 'available_verified' ? 'success' : 'warn',
      ruleRef: 'Rule 149'
    },
    {
      title: 'Applicable Route',
      value: decision.procurement_route.replace(/_/g, ' ').toUpperCase(),
      subtitle: decision.threshold_band ? `Up to ₹${(decision.threshold_band.upper || 0).toLocaleString('en-IN')}` : 'Procedural route',
      status: decision.status === 'COMPLETE' ? 'success' : decision.status === 'NEEDS_INFO' ? 'warn' : 'error',
      ruleRef: decision.threshold_band?.rule_ref || decision.applied_rules[0]?.rule_ref || 'Statutory Rule'
    },
    {
      title: 'Authority',
      value: decision.approval_authority.status === 'explicit' ? decision.approval_authority.value || 'Explicit' : 'Delegation Needed',
      subtitle: decision.approval_authority.status === 'explicit' ? 'Institutional Delegation' : 'Verification Required',
      status: decision.approval_authority.status === 'explicit' ? 'success' : 'warn',
      ruleRef: 'Schedule B Delegation'
    }
  ];

  return (
    <div className="bg-navy-900/80 border border-slate-800 rounded-xl p-5 shadow-inner">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-xs font-mono uppercase tracking-wider text-cyan-400 font-semibold flex items-center space-x-2">
          <span>Deterministic Decision Trace Graph</span>
        </h4>
        <span className="text-[11px] text-slate-400 font-mono">5 Evaluation Nodes</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {steps.map((step, idx) => (
          <div key={idx} className="relative group">
            <div className={`h-full p-3.5 rounded-lg border bg-navy-950/80 transition-all ${
              step.status === 'success' ? 'border-emerald-500/40 hover:border-emerald-400' :
              step.status === 'warn' ? 'border-amber-500/40 hover:border-amber-400' :
              'border-crimson-500/40 hover:border-crimson-400'
            }`}>
              <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 mb-1">
                <span>NODE 0{idx + 1}</span>
                {step.status === 'success' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                {step.status === 'warn' && <HelpCircle className="w-3.5 h-3.5 text-amber-400" />}
                {step.status === 'error' && <AlertCircle className="w-3.5 h-3.5 text-crimson-400" />}
              </div>
              <div className="text-[11px] font-semibold text-slate-300">{step.title}</div>
              <div className="text-xs font-mono font-bold text-cyan-300 mt-1 truncate" title={step.value}>
                {step.value}
              </div>
              <div className="text-[10px] text-slate-400 truncate mt-0.5">{step.subtitle}</div>

              <div
                onClick={() => onOpenSource && onOpenSource(step.ruleRef)}
                className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[9px] font-mono text-cyan-400/80 hover:text-cyan-300 cursor-pointer"
              >
                <span className="truncate">{step.ruleRef}</span>
                <FileText className="w-3 h-3 ml-1 shrink-0" />
              </div>
            </div>

            {idx < steps.length - 1 && (
              <div className="hidden lg:block absolute -right-2 top-1/2 -translate-y-1/2 z-10 pointer-events-none">
                <ArrowRight className="w-4 h-4 text-slate-600" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
