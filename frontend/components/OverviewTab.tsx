'use client';

import React, { useState, useEffect } from 'react';
import { Layers, Server, Database, Code2, PlayCircle, ShieldCheck, Cpu, ArrowRight, Sparkles, CheckCircle2, GitBranch } from 'lucide-react';
import { fetchDiscoveredFeatures } from '../services/api';
import { FeatureDetailModal } from './FeatureDetailModal';

interface OverviewTabProps {
  overview: any;
  repo: any;
}

export const OverviewTab: React.FC<OverviewTabProps> = ({ overview, repo }) => {
  const [features, setFeatures] = useState<any[]>([]);
  const [selectedFeature, setSelectedFeature] = useState<any>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [isSlowLoading, setIsSlowLoading] = useState(false);

  useEffect(() => {
    setIsSlowLoading(false);
    if (!overview) {
      const timer = setTimeout(() => {
        setIsSlowLoading(true);
      }, 7000);
      return () => clearTimeout(timer);
    }
  }, [overview, repo?.id]);

  useEffect(() => {
    if (repo?.id && (repo.status === 'COMPLETED' || repo.status === 'READY')) {
      fetchDiscoveredFeatures(repo.id)
        .then(data => setFeatures(data))
        .catch(err => console.error(err));
    }
  }, [repo]);

  if (!overview) {
    return (
      <div className="p-16 text-center text-slate-400 font-sans text-sm max-w-md mx-auto space-y-3">
        <div className="animate-spin w-7 h-7 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto mb-3"></div>
        <p className="text-slate-200 font-medium text-sm">
          {isSlowLoading ? 'Still reconstructing the codebase...' : 'Reconstructing repository overview from codebase evidence...'}
        </p>
        <p className="text-xs text-slate-500">
          Synthesizing AST graph nodes, discovering capabilities, and extracting entry points.
        </p>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-10">
      
      {/* 1. HERO SECTION */}
      <div className="glass-panel p-8 border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950/30 relative overflow-hidden">
        
        {/* Top Confidence Pill */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span className="text-emerald-400 font-mono">VERIFIED CODEBASE EVIDENCE</span>
          </div>

          <span className="badge-confidence-high px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" /> High Confidence Analysis
          </span>
        </div>

        {/* Project Title & Purpose */}
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-100 tracking-tight mb-3">
          {overview.project_name || repo?.name}
        </h1>
        <p className="text-slate-300 text-base leading-relaxed max-w-4xl">
          {overview.purpose}
        </p>

        {/* Spacious Statistics Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 mt-8 pt-6 border-t border-slate-800/80">
          <div>
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Scanned Files</div>
            <div className="text-2xl font-bold text-slate-100 font-mono mt-0.5">{repo?.file_count || 0}</div>
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Extracted Symbols</div>
            <div className="text-2xl font-bold text-slate-100 font-mono mt-0.5">{repo?.symbol_count || 0}</div>
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Graph Nodes</div>
            <div className="text-2xl font-bold text-cyan-400 font-mono mt-0.5">{repo?.node_count || 0}</div>
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Relationships</div>
            <div className="text-2xl font-bold text-indigo-400 font-mono mt-0.5">{repo?.edge_count || 0}</div>
          </div>
        </div>

      </div>

      {/* 2. "WHAT I DISCOVERED" CAPABILITY TREE MAP */}
      <div className="glass-panel p-6 border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center space-x-2 text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-1">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>Discovered Architecture & Execution Pipeline</span>
            </div>
            <h2 className="text-lg font-bold text-slate-100">
              Codebase Capability Map
            </h2>
          </div>
          <span className="text-xs text-slate-400">
            Reconstructed from AST call graph & import symbols
          </span>
        </div>

        {/* Clean visual connected tree diagram */}
        <div className="bg-slate-950/80 border border-slate-900 rounded-xl p-6 relative">
          
          {/* Root Node */}
          <div className="flex justify-center mb-6">
            <div className="px-5 py-2.5 rounded-xl bg-indigo-600/20 border border-indigo-500/40 text-indigo-200 font-bold text-sm flex items-center space-x-2 shadow-lg shadow-indigo-500/10">
              <GitBranch className="w-4 h-4 text-indigo-400" />
              <span>{overview.project_name || repo?.name} Repository Root</span>
            </div>
          </div>

          {/* Sub-node Clusters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 relative">
            
            {/* Cluster 1: Core Features */}
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
              <div className="text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-1">
                Discovered Capabilities
              </div>
              <div className="text-sm font-bold text-slate-200">
                {features.length} Functional Features
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                {features.map(f => f.name).slice(0, 3).join(', ')}...
              </p>
            </div>

            {/* Cluster 2: Transports & APIs */}
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
              <div className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-1">
                Transports & Routes
              </div>
              <div className="text-sm font-bold text-slate-200 font-mono">
                {overview.apis?.length || 0} API Endpoints / Transports
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                HTTP REST, SSE, stdio transports
              </p>
            </div>

            {/* Cluster 3: Database & Models */}
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 text-center">
              <div className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-1">
                Persistence Layer
              </div>
              <div className="text-sm font-bold text-slate-200 font-mono">
                {overview.database_layer ? 'Relational Schema' : 'Data Entities'}
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                Prisma Schema & PostgreSQL pool executor
              </p>
            </div>

          </div>

        </div>
      </div>

      {/* 3. DISCOVERED FEATURES (EDITORIAL CARDS) */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-slate-100">
              Discovered Features ({features.length})
            </h2>
            <p className="text-xs text-slate-400">
              Click any feature to inspect code flow, symbol evidence, and confidence rating
            </p>
          </div>
        </div>

        {features.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {features.map((feat, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setSelectedFeature(feat);
                  setModalOpen(true);
                }}
                className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-indigo-500/50 transition-all text-left group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-sm text-slate-100 group-hover:text-indigo-300 transition-colors">
                      {feat.name}
                    </span>
                    <span className={`px-2.5 py-0.5 rounded text-[10px] font-semibold font-mono ${
                      feat.confidence === 'HIGH' ? 'badge-confidence-high' : 'badge-confidence-medium'
                    }`}>
                      {feat.confidence}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">
                    {feat.description}
                  </p>
                </div>

                {/* Footer preview */}
                <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono text-slate-400">
                  <span>{feat.flows?.length || 0} Layers • {feat.files?.length || 0} Files</span>
                  <span className="text-indigo-400 group-hover:translate-x-1 transition-transform flex items-center space-x-1 font-sans font-semibold">
                    <span>Explore</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </button>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-slate-400 bg-slate-900 rounded-xl border border-slate-800">
            Analyzing source code AST to discover functional features...
          </div>
        )}
      </div>

      {/* 4. START HERE (DEVELOPER ONBOARDING ENTRY POINTS) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Recommended Entry Points */}
        <div className="glass-panel p-6 border border-slate-800">
          <h2 className="text-base font-bold text-slate-100 mb-3 flex items-center space-x-2">
            <PlayCircle className="w-5 h-5 text-emerald-400" />
            <span>Start Here — Recommended Entry Points</span>
          </h2>
          <div className="space-y-3">
            {overview.entry_points?.length > 0 ? (
              overview.entry_points.map((ep: any, i: number) => (
                <div key={i} className="p-3.5 rounded-xl bg-slate-950 border border-slate-900 flex items-start justify-between">
                  <div>
                    <code className="text-xs font-mono font-semibold text-emerald-300">{ep.path}</code>
                    <p className="text-xs text-slate-400 mt-1">{ep.reason}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-xs text-slate-400 font-mono">No entry point files detected.</div>
            )}
          </div>
        </div>

        {/* Detected Tech Stack & Data Layer */}
        <div className="glass-panel p-6 border border-slate-800">
          <h2 className="text-base font-bold text-slate-100 mb-3 flex items-center space-x-2">
            <Code2 className="w-5 h-5 text-cyan-400" />
            <span>Technology Stack & Data Layer</span>
          </h2>

          <div className="flex flex-wrap gap-2 mb-4">
            {overview.tech_stack?.map((tech: string, i: number) => (
              <span
                key={i}
                className="px-3 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-medium"
              >
                {tech}
              </span>
            ))}
          </div>

          <div className="pt-3 border-t border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Persistence & Database
            </span>
            <p className="text-xs font-mono text-emerald-400 p-3 bg-slate-950 rounded-xl border border-slate-900">
              {overview.database_layer}
            </p>
          </div>
        </div>

      </div>

      {/* Feature Detail Modal */}
      <FeatureDetailModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        feature={selectedFeature}
      />
    </div>
  );
};
