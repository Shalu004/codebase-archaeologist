'use client';

import React from 'react';
import { X, Layers, Code, ArrowRight, ShieldCheck, FileText, Route, Database, CheckCircle2 } from 'lucide-react';

interface FeatureStep {
  step: number;
  layer: string;
  file_path: string;
  symbol_name: string;
  line_number: number;
  snippet?: string;
  explanation?: string;
}

interface FeatureEvidence {
  file_path: string;
  line_number: number;
  symbol_name?: string;
  snippet?: string;
  relationship: string;
}

interface FeatureDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  feature: any;
}

export const FeatureDetailModal: React.FC<FeatureDetailModalProps> = ({ isOpen, onClose, feature }) => {
  if (!isOpen || !feature) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 font-sans">
      <div className="w-full max-w-4xl max-h-[90vh] rounded-2xl bg-[#0d1322] border border-gray-800 flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-gray-800 flex items-center justify-between bg-[#080c14]">
          <div>
            <div className="flex items-center space-x-3 mb-1.5">
              <span className={`px-2.5 py-0.5 rounded text-xs font-semibold uppercase font-sans border ${
                feature.confidence === 'HIGH' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' :
                feature.confidence === 'MEDIUM' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' :
                'bg-gray-500/10 text-gray-300 border-gray-500/30'
              }`}>
                {feature.confidence} CONFIDENCE
              </span>
              <span className="text-xs font-sans text-gray-400">DISCOVERED FEATURE CODE</span>
            </div>
            <h2 className="text-2xl font-extrabold text-white tracking-tight">{feature.name}</h2>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-gray-800/80 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 bg-[#080c14]">
          {/* Description */}
          <div className="p-5 rounded-xl bg-[#0d1322] border border-gray-800">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1.5">Functional Summary</h3>
            <p className="text-sm text-gray-200 leading-relaxed font-sans">{feature.description}</p>
          </div>

          {/* Execution Flow Pipeline */}
          {feature.flows?.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center space-x-2">
                <Route className="w-4 h-4 text-cyan-400" />
                <span>Feature Execution Chain Flow</span>
              </h3>

              <div className="space-y-3">
                {feature.flows.map((step: FeatureStep, idx: number) => (
                  <div key={idx} className="p-4 rounded-xl bg-[#0d1322] border border-gray-800/80 flex items-start space-x-4">
                    <div className="w-7 h-7 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center font-bold text-xs text-indigo-300 font-mono">
                      {step.step}
                    </div>

                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider font-sans">
                          {step.layer} LAYER
                        </span>
                        <code className="text-xs text-emerald-400 font-mono">✓ {step.file_path}:{step.line_number}</code>
                      </div>
                      <h4 className="text-sm font-extrabold text-white font-mono">{step.symbol_name}</h4>
                      {step.explanation && <p className="text-xs text-gray-300 mt-1 font-sans">{step.explanation}</p>}

                      {step.snippet && (
                        <pre className="mt-3 p-3 rounded-lg bg-[#080c14] border border-gray-800 text-xs font-mono text-gray-300 overflow-x-auto leading-relaxed">
                          {step.snippet}
                        </pre>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Files, APIs & Symbols Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* APIs Involved */}
            <div className="p-4 rounded-xl bg-[#0d1322] border border-gray-800">
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center space-x-2">
                <Route className="w-4 h-4 text-indigo-400" />
                <span>APIs Involved ({feature.api_routes?.length || 0})</span>
              </h4>
              <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1 font-mono text-xs">
                {feature.api_routes?.map((api: string, idx: number) => (
                  <div key={idx} className="p-2 rounded-lg bg-[#080c14] border border-gray-800 text-indigo-300">
                    {api}
                  </div>
                ))}
              </div>
            </div>

            {/* Data Models */}
            <div className="p-4 rounded-xl bg-[#0d1322] border border-gray-800">
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center space-x-2">
                <Database className="w-4 h-4 text-amber-400" />
                <span>Database Models ({feature.data_models?.length || 0})</span>
              </h4>
              <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1 font-mono text-xs">
                {feature.data_models?.map((model: string, idx: number) => (
                  <div key={idx} className="p-2 rounded-lg bg-[#080c14] border border-gray-800 text-amber-300">
                    {model}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Source Evidence */}
          {feature.evidence?.length > 0 && (
            <div className="p-4 rounded-xl bg-[#0d1322] border border-gray-800">
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Parsed Source Code Evidence</span>
              </h4>
              <div className="space-y-2">
                {feature.evidence.map((ev: FeatureEvidence, idx: number) => (
                  <div key={idx} className="p-3 rounded-lg bg-[#080c14] border border-gray-800 text-xs font-mono flex items-start justify-between">
                    <div>
                      <span className="text-emerald-400 font-semibold">✓ {ev.file_path}:{ev.line_number}</span>
                      {ev.snippet && <p className="text-gray-300 text-[11px] mt-1">{ev.snippet}</p>}
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] bg-gray-800 text-gray-400 border border-gray-700/50">
                      {ev.relationship}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

