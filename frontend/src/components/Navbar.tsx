import React from 'react';
import { Compass, ShieldCheck, Cpu, History, GitCompare, Database, TestTube, FileText, Info } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const navItems = [
    { id: 'wizard', label: 'Assess Wizard', icon: Compass },
    { id: 'results', label: 'Assessment Results', icon: ShieldCheck },
    { id: 'timemachine', label: 'Version Time Machine', icon: History },
    { id: 'whatif', label: 'What-If Simulator', icon: Cpu },
    { id: 'policydiff', label: 'Policy Diff', icon: GitCompare },
    { id: 'retrieval', label: 'Retrieval Arena', icon: Database },
    { id: 'testlab', label: 'Test Lab (28 Cases)', icon: TestTube },
    { id: 'audit', label: 'Audit Trail', icon: FileText },
    { id: 'sources', label: 'Source Register', icon: FileText },
    { id: 'about', label: 'About & Disclaimer', icon: Info },
  ];

  return (
    <header className="sticky top-0 z-50 bg-navy-950/90 backdrop-blur-md border-b border-cyan-500/20 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('wizard')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-violet-600 flex items-center justify-center shadow-cyan-500/30 shadow-md">
              <Compass className="w-6 h-6 text-navy-950" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-wider text-slate-100 font-mono">PROCUREMENT COMPASS</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-mono">v2.0</span>
              </div>
              <p className="text-[11px] text-slate-400 font-sans">Institutional Procurement Decision-Support System</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="hidden md:flex items-center space-x-2 px-3 py-1 rounded-lg bg-navy-900 border border-slate-800 text-xs font-mono text-slate-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>GFR 2017 (Updated 31.01.2026)</span>
            </div>
          </div>
        </div>

        {/* Scrollable Subnav Tabs */}
        <nav className="flex space-x-1 overflow-x-auto py-2 border-t border-slate-800/60 no-scrollbar">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-navy-900/60'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
