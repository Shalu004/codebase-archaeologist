'use client';

import React from 'react';
import Link from 'next/link';
import { ExternalLink } from 'lucide-react';
import { Repository } from '../services/api';

interface FooterProps {
  activeRepo: Repository | null;
  activeTab?: string;
}

export const Footer: React.FC<FooterProps> = ({ activeRepo, activeTab = 'overview' }) => {
  const githubUrl = activeRepo?.url;

  const handleReportIssue = () => {
    const repoName = activeRepo?.name || 'No repo selected';
    const subject = encodeURIComponent('Codebase Archaeologist — Issue Report');
    const body = encodeURIComponent(
      `Repository: ${repoName}\nCurrent page: ${activeTab}\n\nIssue description:\n\nSteps to reproduce:\n`
    );
    const gmailUrl = `https://mail.google.com/mail/?view=cm&fs=1&to=mushaluthakur785@gmail.com&su=${subject}&body=${body}`;
    window.open(gmailUrl, '_blank');
  };

  return (
    <footer className="border-t border-slate-800/80 bg-slate-950/80 py-6 px-6 mt-auto text-slate-400 font-sans">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-center md:text-left">
        <div>
          <div className="flex items-center justify-center md:justify-start space-x-2">
            <span className="font-extrabold text-sm text-slate-200 tracking-tight font-sans">
              CODEBASE ARCHAEOLOGIST
            </span>
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              v1.0
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            The Google Maps for Any Unfamiliar Codebase — Understand architecture · Trace features · Analyze impact
          </p>
        </div>

        <div className="flex items-center space-x-6 text-xs text-slate-400 font-medium">
          {githubUrl ? (
            <a
              href={githubUrl}
              target="_blank"
              rel="noreferrer"
              className="hover:text-slate-200 transition-colors inline-flex items-center space-x-1"
            >
              <span>GitHub</span>
              <ExternalLink className="w-3 h-3 opacity-70" />
            </a>
          ) : (
            <span className="opacity-40 cursor-not-allowed text-slate-500" title="GitHub unavailable">
              GitHub ↗
            </span>
          )}

          <Link
            href="/docs"
            target="_blank"
            className="hover:text-slate-200 transition-colors inline-flex items-center space-x-1"
          >
            <span>Docs</span>
            <ExternalLink className="w-3 h-3 opacity-70" />
          </Link>

          <button
            onClick={handleReportIssue}
            className="hover:text-slate-200 transition-colors inline-flex items-center space-x-1"
          >
            <span>Report Issue</span>
            <ExternalLink className="w-3 h-3 opacity-70" />
          </button>
        </div>

        <div className="text-[11px] text-slate-400 font-sans">
          Built with ❤️ for all the curious minds
        </div>
      </div>
    </footer>
  );
};
