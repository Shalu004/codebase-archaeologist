'use client';

import React, { useState } from 'react';
import { X, Sparkles, ArrowRight, ArrowLeft, CheckCircle2, Compass } from 'lucide-react';

interface GuidedTourModalProps {
  isOpen: boolean;
  onClose: () => void;
  overview: any;
  onSelectTab: (tab: string) => void;
}

export const GuidedTourModal: React.FC<GuidedTourModalProps> = ({
  isOpen,
  onClose,
  overview,
  onSelectTab,
}) => {
  const [stepIndex, setStepIndex] = useState(0);

  if (!isOpen) return null;

  const tourSteps = [
    {
      title: "1. What This Repository Does",
      subtitle: "Project Purpose & Core Problem",
      content: overview?.purpose || "Full-stack modern software application featuring client UI views and REST APIs.",
      actionTab: "overview"
    },
    {
      title: "2. Architectural Layering",
      subtitle: "System Separation of Concerns",
      content: overview?.architecture || "Client React Components -> HTTP REST Controllers -> Application Business Logic -> Prisma Database Layer.",
      actionTab: "architecture"
    },
    {
      title: "3. Recommended Entry Points",
      subtitle: "Where Should a New Developer Start?",
      content: `Primary entry point files detected:\n${overview?.entry_points?.map((e: any) => `• ${e.path}`).join('\n') || '• src/index.tsx'}`,
      actionTab: "files"
    },
    {
      title: "4. Feature Flow Tracing",
      subtitle: "What Happens When a User Clicks Login?",
      content: "Trace end-to-end execution path across Frontend Component → API Call → Router → Service → Database Model.",
      actionTab: "trace"
    },
    {
      title: "5. Impact Analysis Capabilities",
      subtitle: "Prevent Regression & Unintended Side Effects",
      content: "Use reverse dependency graph calculations to immediately check what breaks before changing database models or core functions.",
      actionTab: "impact"
    },
    {
      title: "6. Grounded Natural Language AI Q&A",
      subtitle: "Ask Facts About the Codebase",
      content: "Query anything about the repository and receive answers grounded strictly in retrieved file lines and AST symbols.",
      actionTab: "ask"
    }
  ];

  const currentStep = tourSteps[stepIndex];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div className="w-full max-w-xl glass-panel rounded-2xl p-6 border border-amber-500/30 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white p-1 rounded-lg hover:bg-gray-800"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-2 text-xs font-bold text-amber-400 uppercase tracking-wider mb-2">
          <Sparkles className="w-4 h-4 text-amber-400" />
          <span>5-Minute Guided Repository Tour</span>
        </div>

        <h2 className="text-xl font-extrabold text-white mb-1">{currentStep.title}</h2>
        <p className="text-xs text-amber-300 font-medium mb-6">{currentStep.subtitle}</p>

        <div className="p-4 rounded-xl bg-dark-900 border border-gray-800 text-xs font-mono text-gray-300 whitespace-pre-line leading-relaxed mb-6">
          {currentStep.content}
        </div>

        {/* Navigation controls */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-800">
          <div className="flex space-x-1">
            {tourSteps.map((_, i) => (
              <span
                key={i}
                className={`w-2 h-2 rounded-full transition-all ${
                  i === stepIndex ? 'bg-amber-400 w-5' : 'bg-gray-700'
                }`}
              />
            ))}
          </div>

          <div className="flex items-center space-x-2">
            {stepIndex > 0 && (
              <button
                onClick={() => setStepIndex(stepIndex - 1)}
                className="px-4 py-2 rounded-xl bg-dark-900 border border-gray-700 text-xs font-semibold text-gray-300 hover:text-white flex items-center space-x-1"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Previous</span>
              </button>
            )}

            {stepIndex < tourSteps.length - 1 ? (
              <button
                onClick={() => {
                  onSelectTab(currentStep.actionTab);
                  setStepIndex(stepIndex + 1);
                }}
                className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-dark-900 font-bold text-xs flex items-center space-x-1 shadow-lg shadow-amber-500/20"
              >
                <span>Next Step</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            ) : (
              <button
                onClick={() => {
                  onSelectTab('overview');
                  onClose();
                }}
                className="px-5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-dark-900 font-bold text-xs flex items-center space-x-1 shadow-lg shadow-emerald-500/20"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Complete Tour</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
