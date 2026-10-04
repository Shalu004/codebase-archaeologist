'use client';

import React, { useState, useEffect, useRef } from 'react';
import { ShieldAlert, Search, ArrowRight, CornerDownRight, AlertCircle, CheckCircle2, Flame, Layers } from 'lucide-react';
import { analyzeImpact, searchSymbols } from '../services/api';

interface ImpactTabProps {
  repoId: string;
}

export const ImpactTab: React.FC<ImpactTabProps> = ({ repoId }) => {
  const [targetQuery, setTargetQuery] = useState('User');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedTargetNode, setSelectedTargetNode] = useState<any>(null);
  
  const [loading, setLoading] = useState(false);
  const [impactData, setImpactData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'direct' | 'indirect' | 'paths'>('direct');

  const dropdownRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    setImpactData(null);
    setSelectedTargetNode(null);
  }, [repoId]);

  useEffect(() => {
    const fetchMatches = async () => {
      if (!targetQuery || targetQuery.trim().length === 0) {
        setSearchResults([]);
        return;
      }
      try {
        const matches = await searchSymbols(repoId, targetQuery);
        setSearchResults(matches);
      } catch (err) {
        console.error(err);
      }
    };

    const timer = setTimeout(fetchMatches, 200);
    return () => clearTimeout(timer);
  }, [targetQuery, repoId]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectTarget = (item: any) => {
    setSelectedTargetNode(item);
    setTargetQuery(item.label);
    setShowDropdown(false);
    runAnalysis(item.id, item.label, item.file_path);
  };

  const handleAnalyzeSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!targetQuery.trim()) return;
    runAnalysis(selectedTargetNode?.id, targetQuery, selectedTargetNode?.file_path);
  };

  const runAnalysis = async (nodeId?: string, symbol_name?: string, file_path?: string) => {
    setLoading(true);
    try {
      const payload: any = {};
      if (nodeId) payload.node_id = nodeId;
      else if (symbol_name) payload.symbol_name = symbol_name;
      else if (file_path) payload.file_path = file_path;

      const res = await analyzeImpact(repoId, payload);
      setImpactData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityBadge = (count: number) => {
    if (count > 10) {
      return (
        <span className="badge-confidence badge-confidence-low">
          <Flame className="w-3.5 h-3.5 text-rose-400" />
          <span>HIGH SEVERITY</span>
        </span>
      );
    }
    if (count > 3) {
      return (
        <span className="badge-confidence badge-confidence-medium">
          <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
          <span>MEDIUM SEVERITY</span>
        </span>
      );
    }
    return (
      <span className="badge-confidence badge-confidence-high">
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
        <span>LOW SEVERITY</span>
      </span>
    );
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-10 font-sans">
      {/* Search Header */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-xs font-semibold text-amber-400 uppercase tracking-wider">
          <ShieldAlert className="w-4 h-4" />
          <span>Reverse Dependency Scanner</span>
        </div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">What breaks if I touch this?</h2>
        <p className="text-sm text-gray-400 max-w-2xl leading-relaxed">
          Select any function, class, model, or file to calculate the exact blast radius across upstream call sites and features.
        </p>

        <form onSubmit={handleAnalyzeSubmit} className="relative mt-6" ref={dropdownRef}>
          <div className="relative flex items-center">
            <Search className="w-5 h-5 absolute left-4 text-gray-400" />
            <input
              type="text"
              value={targetQuery}
              onChange={(e) => {
                setTargetQuery(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
              placeholder="Search symbol or path (e.g. execute_sql, User, auth.ts)..."
              className="w-full bg-[#0d1322] border border-gray-800 text-sm text-white rounded-xl pl-12 pr-36 py-4 focus:outline-none focus:border-amber-500/80 focus:ring-1 focus:ring-amber-500/50 shadow-inner font-mono transition-all"
            />
            <button
              type="submit"
              disabled={loading}
              className="absolute right-2.5 px-5 py-2.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold flex items-center space-x-2 transition-all shadow-md shadow-amber-600/20"
            >
              <span>{loading ? 'Scanning...' : 'Analyze Impact'}</span>
            </button>
          </div>

          {/* Autocomplete Dropdown */}
          {showDropdown && searchResults.length > 0 && (
            <div className="absolute left-0 right-0 top-full mt-2 bg-[#0d1322] border border-gray-800 rounded-xl shadow-2xl z-30 max-h-60 overflow-y-auto">
              {searchResults.map((item, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelectTarget(item)}
                  className="w-full px-4 py-3 text-left text-xs font-mono hover:bg-gray-800/80 flex items-center justify-between border-b border-gray-800/50 last:border-0"
                >
                  <div>
                    <span className="font-semibold text-white">{item.label}</span>
                    {item.file_path && <span className="text-gray-400 text-[11px] block mt-0.5">{item.file_path}</span>}
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-500/20 text-indigo-300 uppercase">
                    {item.type}
                  </span>
                </button>
              ))}
            </div>
          )}
        </form>
      </div>

      {/* Impact Output */}
      {impactData && (
        <div className="space-y-8 pt-4 border-t border-gray-800/80">
          {/* Target Box */}
          <div className="p-6 rounded-2xl bg-[#0d1322] border border-amber-500/30 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-1">
              <span className="text-[11px] font-semibold text-amber-400 uppercase tracking-wider">CHANGE TARGET</span>
              <h3 className="text-2xl font-extrabold text-white font-mono">
                {impactData.target?.label || targetQuery}
              </h3>
              {impactData.target?.file_path && (
                <p className="text-xs text-gray-400 font-mono">{impactData.target.file_path}</p>
              )}
            </div>

            <div className="flex items-center space-x-6 border-t md:border-t-0 md:border-l border-gray-800 pt-4 md:pt-0 md:pl-6">
              <div>
                <span className="text-[11px] font-medium text-gray-400 block">Calculated Blast Radius</span>
                <span className="text-3xl font-extrabold text-amber-300 font-mono">
                  {impactData.total_affected_count} <span className="text-xs font-sans text-gray-400">nodes</span>
                </span>
              </div>
              <div>{getSeverityBadge(impactData.total_affected_count)}</div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center space-x-4 border-b border-gray-800/80 text-xs font-semibold">
            <button
              onClick={() => setActiveTab('direct')}
              className={`pb-3 border-b-2 transition-all ${
                activeTab === 'direct'
                  ? 'border-amber-400 text-amber-300'
                  : 'border-transparent text-gray-400 hover:text-gray-200'
              }`}
            >
              DIRECTLY AFFECTED ({impactData.direct_dependents?.length || 0})
            </button>
            <button
              onClick={() => setActiveTab('indirect')}
              className={`pb-3 border-b-2 transition-all ${
                activeTab === 'indirect'
                  ? 'border-indigo-400 text-indigo-300'
                  : 'border-transparent text-gray-400 hover:text-gray-200'
              }`}
            >
              INDIRECTLY AFFECTED ({impactData.indirect_dependents?.length || 0})
            </button>
            <button
              onClick={() => setActiveTab('paths')}
              className={`pb-3 border-b-2 transition-all ${
                activeTab === 'paths'
                  ? 'border-cyan-400 text-cyan-300'
                  : 'border-transparent text-gray-400 hover:text-gray-200'
              }`}
            >
              IMPACT PATHS ({impactData.impact_paths?.length || 0})
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === 'direct' && (
            <div className="space-y-3">
              {impactData.direct_dependents?.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {impactData.direct_dependents.map((item: any, idx: number) => (
                    <div key={idx} className="p-4 rounded-xl bg-[#0d1322] border border-gray-800 flex items-start justify-between space-x-3">
                      <div className="space-y-1">
                        <div className="text-xs font-mono font-semibold text-gray-100">{item.label}</div>
                        {item.file_path && <div className="text-[11px] text-gray-400 font-mono">{item.file_path}</div>}
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30 uppercase">
                        {item.type}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center bg-[#0d1322] rounded-xl text-xs text-gray-400 font-sans border border-gray-800">
                  No direct dependencies will be affected by this change.
                </div>
              )}
            </div>
          )}

          {activeTab === 'indirect' && (
            <div className="space-y-3">
              {impactData.indirect_dependents?.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {impactData.indirect_dependents.map((item: any, idx: number) => (
                    <div key={idx} className="p-4 rounded-xl bg-[#0d1322] border border-gray-800 flex items-start justify-between space-x-3">
                      <div className="space-y-1">
                        <div className="text-xs font-mono font-semibold text-gray-100">{item.label}</div>
                        {item.file_path && <div className="text-[11px] text-gray-400 font-mono">{item.file_path}</div>}
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
                        Distance: {item.distance}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center bg-[#0d1322] rounded-xl text-xs text-gray-400 font-sans border border-gray-800">
                  No indirect downstream breakages detected.
                </div>
              )}
            </div>
          )}

          {activeTab === 'paths' && (
            <div className="space-y-4">
              {impactData.impact_paths?.length > 0 ? (
                impactData.impact_paths.map((p: any, idx: number) => (
                  <div key={idx} className="p-4 rounded-xl bg-[#0d1322] border border-gray-800 space-y-3">
                    <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center justify-between">
                      <span>Breakage Propagation to <span className="font-mono text-cyan-300">{p.target_label}</span></span>
                      <span className="text-[10px] font-mono text-gray-500">Distance {p.distance}</span>
                    </div>
                    <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
                      {p.path.map((step: string, sIdx: number) => (
                        <React.Fragment key={sIdx}>
                          <span className="px-3 py-1.5 rounded-lg bg-[#080c14] text-gray-200 border border-gray-800 font-medium">
                            {step}
                          </span>
                          {sIdx < p.path.length - 1 && (
                            <ArrowRight className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center bg-[#0d1322] rounded-xl text-xs text-gray-400 font-sans border border-gray-800">
                  No multi-step impact propagation chains identified.
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

