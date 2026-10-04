'use client';

import React, { useState, useEffect } from 'react';
import { GitCommit, Calendar, User, FileDiff, History } from 'lucide-react';
import { fetchTimeline } from '../services/api';

interface HistoryTabProps {
  repoId: string;
}

export const HistoryTab: React.FC<HistoryTabProps> = ({ repoId }) => {
  const [timeline, setTimeline] = useState<any[]>([]);
  const [hasGit, setHasGit] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTimeline() {
      try {
        const res = await fetchTimeline(repoId);
        setTimeline(res.timeline || []);
        setHasGit(res.has_git);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadTimeline();
  }, [repoId]);

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-10 font-sans">
      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-xs font-semibold text-purple-400 uppercase tracking-wider">
          <History className="w-4 h-4" />
          <span>Archaeological Timeline</span>
        </div>
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Project Architectural Evolution</h2>
        <p className="text-sm text-gray-400 max-w-2xl leading-relaxed">
          Chronological milestone timeline tracing structural changes, feature additions, and codebase shifts.
        </p>
      </div>

      {loading ? (
        <div className="text-xs text-gray-500 font-mono">Extracting commit timeline...</div>
      ) : (
        <div className="space-y-8 pt-4 border-t border-gray-800/80">
          <div className="flex items-center justify-between text-xs font-semibold text-gray-500 uppercase tracking-wider">
            <span>PAST</span>
            <span>NOW</span>
          </div>

          <div className="relative pl-6 border-l-2 border-purple-500/30 space-y-6">
            {timeline.map((item: any, idx: number) => (
              <div key={idx} className="relative group">
                {/* Timeline Dot */}
                <div className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full border-2 bg-[#080c14] border-purple-400 group-hover:bg-purple-400 transition-colors" />

                <div className="p-5 rounded-2xl bg-[#0d1322] border border-gray-800 hover:border-gray-700 transition-all space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-extrabold text-base text-white tracking-tight">{item.title}</h3>
                    <span className="text-xs font-sans text-gray-400 flex items-center space-x-1.5">
                      <Calendar className="w-3.5 h-3.5 text-gray-500" />
                      <span>{item.date}</span>
                    </span>
                  </div>

                  <p className="text-xs text-gray-300 leading-relaxed font-sans">{item.summary}</p>

                  <div className="flex items-center space-x-4 pt-3 border-t border-gray-800/80 text-[11px] text-gray-400">
                    <span className="flex items-center space-x-1 font-sans">
                      <User className="w-3 h-3 text-indigo-400" />
                      <span>{item.author}</span>
                    </span>
                    <span className="flex items-center space-x-1 font-sans">
                      <FileDiff className="w-3 h-3 text-cyan-400" />
                      <span>{item.changed_files_count} files changed</span>
                    </span>
                    <span className="px-2 py-0.5 rounded bg-[#080c14] border border-gray-800 text-gray-400 font-mono text-[10px]">
                      {item.commit_hash?.slice(0, 7)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

