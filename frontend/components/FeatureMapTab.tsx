'use client';

import React, { useState, useEffect } from 'react';
import { Layers, ArrowRight, CheckCircle2, ShieldCheck, Cpu, Code2, Sparkles } from 'lucide-react';
import { fetchDiscoveredFeatures } from '../services/api';
import { FeatureDetailModal } from './FeatureDetailModal';

interface FeatureMapTabProps {
  repoId: string;
  overview?: any;
}

export const FeatureMapTab: React.FC<FeatureMapTabProps> = ({ repoId }) => {
  const [features, setFeatures] = useState<any[]>([]);
  const [selectedFeature, setSelectedFeature] = useState<any>(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    setFeatures([]);
    setSelectedFeature(null);
    if (repoId) {
      fetchDiscoveredFeatures(repoId)
        .then(data => setFeatures(data))
        .catch(err => console.error(err));
    }
  }, [repoId]);

  const getConfidenceBadge = (confidence: string) => {
    const c = (confidence || '').toLowerCase();
    if (c.includes('high')) {
      return (
        <span className="badge-confidence badge-confidence-high font-sans">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>High confidence</span>
        </span>
      );
    }
    if (c.includes('med')) {
      return (
        <span className="badge-confidence badge-confidence-medium font-sans">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Medium confidence</span>
        </span>
      );
    }
    return (
      <span className="badge-confidence badge-confidence-low font-sans">
        <CheckCircle2 className="w-3.5 h-3.5" />
        <span>Inferred</span>
      </span>
    );
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-10 font-sans">
      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-xs font-semibold text-indigo-400 uppercase tracking-wider">
          <Layers className="w-4 h-4" />
          <span>Capability Intelligence Map</span>
        </div>
        <div className="flex items-baseline justify-between">
          <h2 className="text-3xl font-extrabold text-white tracking-tight">System Feature Capabilities</h2>
          <span className="text-xs font-mono font-medium text-gray-400">{features.length} Discovered Systems</span>
        </div>
        <p className="text-sm text-gray-400 max-w-2xl leading-relaxed">
          Spatial reconstruction of what this software can do, synthesized from static analysis of route handlers, call graphs, and DB schema types.
        </p>
      </div>

      {/* Feature Map Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {features.map((feat: any, idx: number) => (
          <div
            key={idx}
            className="p-6 rounded-2xl bg-[#0d1322] border border-gray-800 hover:border-gray-700 transition-all flex flex-col justify-between space-y-6 group hover:-translate-y-0.5 hover:shadow-xl hover:shadow-indigo-950/20"
          >
            <div className="space-y-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 group-hover:scale-105 transition-transform">
                    <Cpu className="w-4 h-4" />
                  </div>
                  <h3 className="text-lg font-extrabold text-white tracking-tight">{feat.name}</h3>
                </div>
                {getConfidenceBadge(feat.confidence)}
              </div>

              <p className="text-xs text-gray-300 leading-relaxed font-sans">{feat.description}</p>

              {/* Execution Flow Pipeline preview */}
              {feat.flows?.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-gray-800/80">
                  <div className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
                    Flow Preview ({feat.flows.length} layers)
                  </div>
                  <div className="flex flex-wrap items-center gap-2 text-xs">
                    {feat.flows.map((step: any, sIdx: number) => (
                      <React.Fragment key={sIdx}>
                        <span className="font-mono text-xs px-2.5 py-1 rounded-md bg-[#080c14] border border-gray-800 text-gray-300">
                          {step.symbol_name}
                        </span>
                        {sIdx < feat.flows.length - 1 && (
                          <ArrowRight className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
                        )}
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="pt-4 border-t border-gray-800/80 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-3 text-gray-400 font-mono text-[11px]">
                {feat.api_routes?.length > 0 && <span>{feat.api_routes.length} APIs</span>}
                {feat.data_models?.length > 0 && <span>{feat.data_models.length} Models</span>}
              </div>

              <button
                onClick={() => {
                  setSelectedFeature(feat);
                  setModalOpen(true);
                }}
                className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center space-x-1 group-hover:translate-x-1 transition-transform"
              >
                <span>Explore</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>

      <FeatureDetailModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        feature={selectedFeature}
      />
    </div>
  );
};

