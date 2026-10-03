import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { PurchaseWizard } from './components/PurchaseWizard';
import { ResultView } from './components/ResultView';
import { VersionTimeMachine } from './components/VersionTimeMachine';
import { WhatIfSimulator } from './components/WhatIfSimulator';
import { PolicyDiff } from './components/PolicyDiff';
import { RetrievalArena } from './components/RetrievalArena';
import { TestLab } from './components/TestLab';
import { AuditTrailView } from './components/AuditTrailView';
import { SourceRegisterView } from './components/SourceRegisterView';
import { AboutView } from './components/AboutView';
import { SourceDrawer } from './components/SourceDrawer';
import { assessProcurement } from './lib/api';
import { ProcurementInput, AssessmentResponse, CitationRef } from './types';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('wizard');
  const [assessment, setAssessment] = useState<AssessmentResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [activeCitation, setActiveCitation] = useState<CitationRef | null>(null);

  const handleAssess = async (input: ProcurementInput) => {
    setLoading(true);
    try {
      const res = await assessProcurement(input);
      setAssessment(res);
      setActiveTab('results');
    } catch (e: any) {
      alert(`Assessment Error: ${e.message || 'Failed to evaluate procurement'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenSourceByRef = (ruleRef: string) => {
    if (assessment && assessment.citations) {
      const cit = assessment.citations.find((c) =>
        c.rule_ref.toLowerCase().includes(ruleRef.toLowerCase()) ||
        ruleRef.toLowerCase().includes(c.rule_ref.toLowerCase())
      ) || assessment.citations[0];
      if (cit) setActiveCitation(cit);
    }
  };

  return (
    <div className="min-h-screen bg-navy-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30">
      {/* Top Navbar */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main View Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'wizard' && (
          <PurchaseWizard onSubmit={handleAssess} isLoading={loading} />
        )}

        {activeTab === 'results' && (
          assessment ? (
            <ResultView
              assessment={assessment}
              onOpenCitation={(c) => setActiveCitation(c)}
              onOpenSourceByRef={handleOpenSourceByRef}
            />
          ) : (
            <div className="text-center py-16 space-y-4">
              <p className="text-sm font-mono text-slate-400">No active procurement evaluation.</p>
              <button
                onClick={() => setActiveTab('wizard')}
                className="px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-navy-950 font-mono text-xs font-bold transition-all"
              >
                Open Assess Wizard
              </button>
            </div>
          )
        )}

        {activeTab === 'timemachine' && <VersionTimeMachine />}
        {activeTab === 'whatif' && <WhatIfSimulator />}
        {activeTab === 'policydiff' && <PolicyDiff />}
        {activeTab === 'retrieval' && <RetrievalArena />}
        {activeTab === 'testlab' && <TestLab />}
        {activeTab === 'audit' && <AuditTrailView />}
        {activeTab === 'sources' && <SourceRegisterView />}
        {activeTab === 'about' && <AboutView />}
      </main>

      {/* Slide-out Source Drawer (§50) */}
      <SourceDrawer
        citation={activeCitation}
        onClose={() => setActiveCitation(null)}
      />

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-navy-950 py-6 text-center text-xs font-mono text-slate-500">
        Procurement Compass v2.0 • GFR 2017 Updated 31.01.2026 • Every Answer Cited • Every Doubt Escalated
      </footer>
    </div>
  );
}

export default App;
