'use client';

import React, { useState } from 'react';
import { X, Github, UploadCloud, FileArchive, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

interface RepoIngestionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmitGitHub: (url: string) => Promise<void>;
  onSubmitZip: (file: File) => Promise<void>;
}

export const RepoIngestionModal: React.FC<RepoIngestionModalProps> = ({
  isOpen,
  onClose,
  onSubmitGitHub,
  onSubmitZip,
}) => {
  const [tab, setTab] = useState<'github' | 'zip'>('github');
  const [githubUrl, setGithubUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleGitHubSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!githubUrl.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await onSubmitGitHub(githubUrl.trim());
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to ingest repository');
    } finally {
      setSubmitting(false);
    }
  };

  const handleZipSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    setSubmitting(true);
    setError(null);
    try {
      await onSubmitZip(selectedFile);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to upload ZIP archive');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg glass-panel rounded-2xl p-6 border border-gray-700/80 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white p-1 rounded-lg hover:bg-gray-800"
        >
          <X className="w-5 h-5" />
        </button>

        <h2 className="text-xl font-bold text-white mb-1">Analyze a Repository</h2>
        <p className="text-xs text-gray-400 mb-6">
          Provide a GitHub repository URL or upload a ZIP package to build an interactive knowledge graph.
        </p>

        {/* Tab switcher */}
        <div className="flex border-b border-gray-800 mb-6">
          <button
            onClick={() => setTab('github')}
            className={`flex items-center space-x-2 pb-3 px-4 font-medium text-sm border-b-2 transition-all ${
              tab === 'github'
                ? 'border-brand-500 text-brand-400'
                : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <Github className="w-4 h-4" />
            <span>GitHub Repository</span>
          </button>
          <button
            onClick={() => setTab('zip')}
            className={`flex items-center space-x-2 pb-3 px-4 font-medium text-sm border-b-2 transition-all ${
              tab === 'zip'
                ? 'border-brand-500 text-brand-400'
                : 'border-transparent text-gray-400 hover:text-gray-200'
            }`}
          >
            <FileArchive className="w-4 h-4" />
            <span>Upload ZIP Archive</span>
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {tab === 'github' ? (
          <form onSubmit={handleGitHubSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                GitHub Repository URL
              </label>
              <input
                type="url"
                required
                placeholder="https://github.com/username/repository"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                className="w-full bg-dark-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-brand-500 font-mono"
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 rounded-xl bg-brand-600 hover:bg-brand-500 font-semibold text-sm text-white flex items-center justify-center space-x-2 shadow-lg shadow-brand-600/25"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Cloning & Analyzing...</span>
                </>
              ) : (
                <span>Analyze Repository</span>
              )}
            </button>
          </form>
        ) : (
          <form onSubmit={handleZipSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                ZIP File Upload
              </label>
              <div className="border-2 border-dashed border-gray-700 hover:border-brand-500 rounded-2xl p-6 text-center cursor-pointer bg-dark-900/50 transition-all">
                <input
                  type="file"
                  accept=".zip"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="hidden"
                  id="zip-upload"
                />
                <label htmlFor="zip-upload" className="cursor-pointer block">
                  <UploadCloud className="w-10 h-10 text-brand-400 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-200">
                    {selectedFile ? selectedFile.name : 'Click or drag & drop ZIP file here'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">Maximum recommended size: 250MB</p>
                </label>
              </div>
            </div>
            <button
              type="submit"
              disabled={submitting || !selectedFile}
              className="w-full py-3 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:opacity-50 font-semibold text-sm text-white flex items-center justify-center space-x-2 shadow-lg shadow-brand-600/25"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Extracting & Parsing...</span>
                </>
              ) : (
                <span>Extract & Analyze ZIP</span>
              )}
            </button>
          </form>
        )}

        {/* TRY AN EXAMPLE REPOSITORY Section */}
        <div className="mt-6 pt-4 border-t border-gray-800">
          <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2">
            Try an Example Repository
          </div>
          <div className="max-w-xs">
            <button
              type="button"
              onClick={() => {
                setGithubUrl('https://github.com/Shalu004/CivicFix');
                setTab('github');
              }}
              className="w-full p-3 rounded-xl bg-slate-900 border border-slate-800 hover:border-indigo-500/50 text-left transition-all group flex items-center justify-between"
            >
              <div>
                <div className="text-xs font-bold text-slate-200 group-hover:text-indigo-300">CivicFix</div>
                <div className="text-[10px] text-slate-500">Example repository</div>
              </div>
              <span className="text-[10px] font-mono text-indigo-400 px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">
                Load Example
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
