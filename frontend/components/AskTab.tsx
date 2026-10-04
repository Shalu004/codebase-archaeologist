'use client';

import React, { useState } from 'react';
import { Sparkles, ArrowRight, ShieldCheck, FileCode, CheckCircle2, Search, Cpu } from 'lucide-react';
import { askCodebase } from '../services/api';

interface AskTabProps {
  repoId: string;
}

export const AskTab: React.FC<AskTabProps> = ({ repoId }) => {
  const [question, setQuestion] = useState('How does authentication work?');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);

  React.useEffect(() => {
    setResponse(null);
  }, [repoId]);

  const handleAsk = async (e?: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const queryToSubmit = customQuery || question;
    if (!queryToSubmit.trim()) return;
    setLoading(true);
    try {
      const res = await askCodebase(repoId, queryToSubmit);
      setResponse(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceBadge = (confidence: string) => {
    const c = (confidence || '').toLowerCase();
    if (c.includes('high')) {
      return (
        <span className="badge-confidence badge-confidence-high">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>HIGH CONFIDENCE</span>
        </span>
      );
    }
    if (c.includes('med')) {
      return (
        <span className="badge-confidence badge-confidence-medium">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>MEDIUM CONFIDENCE</span>
        </span>
      );
    }
    return (
      <span className="badge-confidence badge-confidence-low">
        <CheckCircle2 className="w-3.5 h-3.5" />
        <span>LOW CONFIDENCE</span>
      </span>
    );
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-10 font-sans">
      {/* Search Header / Command Center */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-xs font-semibold text-indigo-400 uppercase tracking-wider">
          <Sparkles className="w-4 h-4" />
          <span>Codebase Command Center</span>
        </div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">What do you want to understand?</h2>
        <p className="text-sm text-gray-400 max-w-2xl leading-relaxed">
          Ask natural language questions about implementation details, flow architectures, or dependencies. Answers are strictly grounded in verified static analysis graph nodes.
        </p>

        <form onSubmit={(e) => handleAsk(e)} className="relative mt-6">
          <div className="relative flex items-center">
            <Search className="w-5 h-5 absolute left-4 text-gray-400" />
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. Where is execute_sql used? What breaks if I change User?"
              className="w-full bg-[#0d1322] border border-gray-800 text-sm text-white rounded-xl pl-12 pr-36 py-4 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 shadow-inner font-sans transition-all"
            />
            <button
              type="submit"
              disabled={loading}
              className="absolute right-2.5 px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-2 transition-all shadow-md shadow-indigo-600/20"
            >
              <Cpu className="w-4 h-4" />
              <span>{loading ? 'Analyzing...' : 'Investigate'}</span>
            </button>
          </div>
        </form>

        <div className="pt-2">
          <span className="text-xs font-medium text-gray-500 mr-2">Suggested queries:</span>
          <div className="flex flex-wrap gap-2 mt-2">
            {[
              'How does authentication work?',
              'What happens after POST /register?',
              'Where is execute_sql used?',
              'What breaks if I change User?',
              'Where should I start?'
            ].map((preset, i) => (
              <button
                key={i}
                type="button"
                onClick={() => {
                  setQuestion(preset);
                  handleAsk(undefined, preset);
                }}
                className="text-xs px-3 py-1.5 rounded-lg bg-[#0d1322] hover:bg-gray-800/80 text-gray-300 border border-gray-800 transition-all font-sans"
              >
                {preset}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Answer Output */}
      {response && (
        <div className="space-y-6 pt-4 border-t border-gray-800/80">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">INVESTIGATION RESULT</h3>
            {getConfidenceBadge(response.confidence)}
          </div>

          {/* ANSWER */}
          <div className="p-6 rounded-2xl bg-[#0d1322] border border-gray-800 space-y-4">
            <h4 className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">ANSWER</h4>
            <p className="text-base font-semibold text-gray-100 leading-snug">{response.summary}</p>
            <div className="text-sm text-gray-300 whitespace-pre-line leading-relaxed border-t border-gray-800/80 pt-4 font-sans">
              {response.explanation}
            </div>
          </div>

          {/* CODEBASE EVIDENCE CHIPS */}
          {response.evidence?.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center space-x-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>VERIFIED EVIDENCE CHIPS</span>
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {response.evidence.map((ev: any, i: number) => (
                  <div key={i} className="p-4 rounded-xl bg-[#0d1322] border border-gray-800/80 flex flex-col justify-between space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 text-xs font-mono font-semibold text-emerald-400">
                        <FileCode className="w-3.5 h-3.5 text-emerald-400" />
                        <span>✓ {ev.file_path}:{ev.line_number}</span>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-gray-800/80 text-gray-400 border border-gray-700/50">
                        {ev.relationship}
                      </span>
                    </div>
                    {ev.snippet && (
                      <p className="text-xs text-gray-300 font-mono bg-[#080c14] p-2.5 rounded-lg border border-gray-800 truncate">
                        {ev.snippet}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

