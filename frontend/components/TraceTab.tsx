'use client';

import React, { useState } from 'react';
import { Compass, Play, CheckCircle2, FileCode, ArrowDown, Layers, Terminal } from 'lucide-react';
import { traceFeature } from '../services/api';

interface TraceTabProps {
  repoId: string;
}

export const TraceTab: React.FC<TraceTabProps> = ({ repoId }) => {
  const [query, setQuery] = useState('What happens when I click Login?');
  const [loading, setLoading] = useState(false);
  const [traceResult, setTraceResult] = useState<any>(null);
  const [activeStepIndex, setActiveStepIndex] = useState<number | null>(0);

  React.useEffect(() => {
    setTraceResult(null);
  }, [repoId]);

  const handleTrace = async (e?: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const q = customQuery || query;
    if (!q.trim()) return;
    setLoading(true);
    try {
      const res = await traceFeature(repoId, q);
      setTraceResult(res);
      setActiveStepIndex(0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-10 font-sans">
      {/* Search & Header */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-xs font-semibold text-cyan-400 uppercase tracking-wider">
          <Compass className="w-4 h-4" />
          <span>Execution Flow Journey</span>
        </div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Trace a feature end-to-end</h2>
        <p className="text-sm text-gray-400 max-w-2xl leading-relaxed">
          Follow execution paths step-by-step: User Action → UI Handler → API Route → Service Logic → Database Entity.
        </p>

        <form onSubmit={(e) => handleTrace(e)} className="relative mt-6">
          <div className="relative flex items-center">
            <Terminal className="w-5 h-5 absolute left-4 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. What happens when I click Login? How is SQL executed?"
              className="w-full bg-[#0d1322] border border-gray-800 text-sm text-white rounded-xl pl-12 pr-36 py-4 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 shadow-inner font-sans transition-all"
            />
            <button
              type="submit"
              disabled={loading}
              className="absolute right-2.5 px-5 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center space-x-2 transition-all shadow-md shadow-cyan-600/20"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{loading ? 'Tracing...' : 'Trace Journey'}</span>
            </button>
          </div>
        </form>

        <div className="pt-2">
          <span className="text-xs font-medium text-gray-500 mr-2">Preset traces:</span>
          <div className="flex flex-wrap gap-2 mt-2">
            {[
              'What happens when I click Login?',
              'How does user registration work?',
              'How is execute_sql processed?'
            ].map((preset, i) => (
              <button
                key={i}
                type="button"
                onClick={() => {
                  setQuery(preset);
                  handleTrace(undefined, preset);
                }}
                className="text-xs px-3 py-1.5 rounded-lg bg-[#0d1322] hover:bg-gray-800/80 text-gray-300 border border-gray-800 transition-all font-sans"
              >
                {preset}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Trace Results Journey */}
      {traceResult && (
        <div className="space-y-8 pt-4 border-t border-gray-800/80">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">EXECUTION JOURNEY PIPELINE</h3>
            <span className="badge-confidence badge-confidence-high">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>VERIFIED FLOW · {traceResult.confidence}</span>
            </span>
          </div>

          <div className="relative pl-6 border-l-2 border-cyan-500/30 space-y-8">
            {traceResult.trace_steps?.map((step: any, idx: number) => {
              const isSelected = activeStepIndex === idx;
              return (
                <div key={idx} className="relative group">
                  {/* Step Connector Dot */}
                  <div className={`absolute -left-[31px] top-1.5 w-4 h-4 rounded-full border-2 transition-all ${
                    isSelected
                      ? 'bg-cyan-400 border-cyan-300 ring-4 ring-cyan-500/20'
                      : 'bg-[#080c14] border-gray-600 group-hover:border-cyan-400'
                  }`} />

                  {/* Step Card */}
                  <div
                    onClick={() => setActiveStepIndex(idx)}
                    className={`p-6 rounded-2xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-[#0d1322] border-cyan-500/50 shadow-lg shadow-cyan-950/30'
                        : 'bg-[#0d1322]/50 border-gray-800 hover:border-gray-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <span className="px-2.5 py-1 rounded-md text-[10px] font-bold bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 uppercase tracking-wider">
                          STAGE {step.step_number} · {step.layer}
                        </span>
                        <h4 className="text-base font-extrabold text-white font-mono">{step.symbol_name}</h4>
                      </div>
                      <span className="text-xs font-mono text-emerald-400 font-medium">
                        ✓ {step.file_path}:{step.line_number}
                      </span>
                    </div>

                    <p className="text-sm text-gray-300 leading-relaxed font-sans">{step.explanation}</p>

                    {step.code_snippet && (
                      <div className="mt-4 pt-3 border-t border-gray-800/80">
                        <div className="flex items-center space-x-2 text-[11px] font-mono text-gray-400 mb-2">
                          <FileCode className="w-3.5 h-3.5 text-cyan-400" />
                          <span>Code Evidence Snippet</span>
                        </div>
                        <pre className="p-4 rounded-xl bg-[#080c14] text-xs font-mono text-gray-300 border border-gray-800/80 overflow-x-auto leading-relaxed">
                          {step.code_snippet}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

