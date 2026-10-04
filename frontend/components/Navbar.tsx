'use client';

import React from 'react';
import { Compass, FolderGit2, Plus, Sparkles, RefreshCw, ChevronDown, CheckCircle2 } from 'lucide-react';
import { Repository } from '../services/api';

interface NavbarProps {
  repositories: Repository[];
  activeRepo: Repository | null;
  onSelectRepo: (repo: Repository) => void;
  onOpenIngestion: () => void;
  onStartTour: () => void;
  onAnalyzeFixture: () => void;
  loading: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  repositories,
  activeRepo,
  onSelectRepo,
  onOpenIngestion,
  onStartTour,
  onAnalyzeFixture,
  loading
}) => {
  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
      
      {/* Brand logo & identity */}
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 via-blue-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <Compass className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="font-extrabold text-base tracking-tight text-slate-100 font-sans">
              CODEBASE ARCHAEOLOGIST
            </h1>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-500/15 text-indigo-400 border border-indigo-500/30">
              v1.0
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-normal">
            The Google Maps for Any Unfamiliar Codebase
          </p>
        </div>
      </div>

      {/* Command Center Controls */}
      <div className="flex items-center space-x-3">
        
        {/* Repository Control Dropdown */}
        {repositories.length > 0 && (
          <div className="relative">
            <select
              value={activeRepo?.id || ''}
              onChange={(e) => {
                const found = repositories.find(r => r.id === e.target.value);
                if (found) onSelectRepo(found);
              }}
              className="bg-slate-900 border border-slate-800 text-slate-200 text-xs font-medium rounded-xl px-3.5 py-2 pr-8 focus:outline-none focus:border-indigo-500 transition-all appearance-none cursor-pointer"
            >
              {repositories.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.source_type}) • {r.status}
                </option>
              ))}
            </select>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-3 pointer-events-none" />
          </div>
        )}

        {/* Analyze Repository Primary CTA */}
        <button
          onClick={onOpenIngestion}
          className="btn-primary text-xs"
        >
          <Plus className="w-4 h-4" />
          <span>Analyze Repository</span>
        </button>

        {/* Guided Tour Button */}
        {activeRepo && (
          <button
            onClick={onStartTour}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/30 hover:bg-amber-500/20 transition-all flex items-center space-x-1.5"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>5-Min Tour</span>
          </button>
        )}
      </div>

    </header>
  );
};
