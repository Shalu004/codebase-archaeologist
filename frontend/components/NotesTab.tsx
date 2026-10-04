'use client';

import React, { useState } from 'react';
import { BookOpen, Download, Copy, Check, Sparkles, FileCode } from 'lucide-react';
import { generateProjectNotes } from '../services/api';

interface NotesTabProps {
  repoId: string;
}

export const NotesTab: React.FC<NotesTabProps> = ({ repoId }) => {
  const [loading, setLoading] = useState(false);
  const [notes, setNotes] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  React.useEffect(() => {
    setNotes(null);
  }, [repoId]);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await generateProjectNotes(repoId);
      setNotes(res.notes_markdown);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!notes) return;
    navigator.clipboard.writeText(notes);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = (format: 'md' | 'txt') => {
    if (!notes) return;
    const blob = new Blob([notes], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `developer_field_guide_${repoId.slice(0, 8)}.${format}`;
    link.click();
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-10 font-sans">
      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 text-xs font-semibold text-indigo-400 uppercase tracking-wider">
          <BookOpen className="w-4 h-4" />
          <span>Developer Field Guide</span>
        </div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-3xl font-extrabold text-white tracking-tight">Automated Onboarding Documentation</h2>
            <p className="text-sm text-gray-400 max-w-2xl leading-relaxed mt-1">
              Synthesizes architecture, APIs, data layers, critical entry points, and domain capabilities into a clean field guide.
            </p>
          </div>
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs flex items-center space-x-2 shadow-lg shadow-indigo-600/20 transition-all self-start md:self-auto"
          >
            <Sparkles className="w-4 h-4 text-amber-300" />
            <span>{loading ? 'Synthesizing Guide...' : 'Generate Field Guide'}</span>
          </button>
        </div>
      </div>

      {/* Generated Guide View */}
      {notes && (
        <div className="space-y-6 pt-4 border-t border-gray-800/80">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">DOCUMENT PREVIEW</span>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleCopy}
                className="px-3.5 py-1.5 rounded-lg bg-[#0d1322] border border-gray-800 text-xs font-medium text-gray-300 hover:text-white flex items-center space-x-1.5 transition-all"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-gray-400" />}
                <span>{copied ? 'Copied' : 'Copy Markdown'}</span>
              </button>
              <button
                onClick={() => handleDownload('md')}
                className="px-3.5 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-xs font-semibold text-indigo-300 hover:bg-indigo-500/20 flex items-center space-x-1.5 transition-all"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export .MD</span>
              </button>
              <button
                onClick={() => handleDownload('txt')}
                className="px-3.5 py-1.5 rounded-lg bg-[#0d1322] border border-gray-800 text-xs font-medium text-gray-300 hover:text-white flex items-center space-x-1.5 transition-all"
              >
                <Download className="w-3.5 h-3.5 text-gray-400" />
                <span>Export .TXT</span>
              </button>
            </div>
          </div>

          <div className="p-8 rounded-2xl bg-[#0d1322] border border-gray-800 text-sm text-gray-200 whitespace-pre-wrap leading-relaxed max-h-[650px] overflow-y-auto font-mono text-xs">
            {notes}
          </div>
        </div>
      )}
    </div>
  );
};

