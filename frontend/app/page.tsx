'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Compass, Map, FileCode, Network, Route, AlertTriangle, MessageSquare, Clock, FileText, Plus, RefreshCw, FolderGit2,
  Loader2, CheckCircle2, AlertCircle, Cpu, Layers, GitBranch
} from 'lucide-react';
import {
  fetchRepositories, fetchRepository, fetchOverview, analyzeFixtureRepo, createGitHubRepo, uploadZipRepo, Repository
} from '../services/api';
import { Navbar } from '../components/Navbar';
import { RepoIngestionModal } from '../components/RepoIngestionModal';
import { GuidedTourModal } from '../components/GuidedTourModal';
import { OverviewTab } from '../components/OverviewTab';
import { ArchitectureTab } from '../components/ArchitectureTab';
import { FileExplorerTab } from '../components/FileExplorerTab';
import { FeatureMapTab } from '../components/FeatureMapTab';
import { TraceTab } from '../components/TraceTab';
import { ImpactTab } from '../components/ImpactTab';
import { AskTab } from '../components/AskTab';
import { HistoryTab } from '../components/HistoryTab';
import { NotesTab } from '../components/NotesTab';
import { Footer } from '../components/Footer';

const PENDING_STATUSES = ['QUEUED', 'CLONING', 'SCANNING', 'PARSING', 'BUILDING_GRAPH', 'GENERATING_INSIGHTS'];

export default function Dashboard() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [activeRepo, setActiveRepo] = useState<Repository | null>(null);
  const [overview, setOverview] = useState<any>(null);

  const [activeTab, setActiveTab] = useState<string>('overview');
  const [ingestionOpen, setIngestionOpen] = useState(false);
  const [tourOpen, setTourOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadRepos = useCallback(async () => {
    try {
      const repos = await fetchRepositories();
      setRepositories(repos);
      if (repos.length > 0 && !activeRepo) {
        setActiveRepo(repos[0]);
      }
    } catch (err) {
      console.error(err);
    }
  }, [activeRepo]);

  useEffect(() => {
    loadRepos();
  }, [loadRepos]);

  // Polling repository status when analysis is in progress
  useEffect(() => {
    if (!activeRepo) return;

    const isPending = PENDING_STATUSES.includes(activeRepo.status);
    if (!isPending) return;

    const interval = setInterval(async () => {
      try {
        const updated = await fetchRepository(activeRepo.id);
        setActiveRepo(updated);
        setRepositories(prev => prev.map(r => (r.id === updated.id ? updated : r)));
        if (!PENDING_STATUSES.includes(updated.status)) {
          clearInterval(interval);
        }
      } catch (err) {
        console.error(err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [activeRepo]);

  // Load overview whenever active repo is ready/completed
  useEffect(() => {
    setOverview(null);
    if (activeRepo && (activeRepo.status === 'COMPLETED' || activeRepo.status === 'READY')) {
      fetchOverview(activeRepo.id)
        .then(data => setOverview(data))
        .catch(err => console.error(err));
    }
  }, [activeRepo?.id]);

  const handleAnalyzeGitHub = async (url: string) => {
    setLoading(true);
    try {
      const repo = await createGitHubRepo(url);
      setRepositories(prev => [repo, ...prev]);
      setActiveRepo(repo);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadZip = async (file: File) => {
    setLoading(true);
    try {
      const repo = await uploadZipRepo(file);
      setRepositories(prev => [repo, ...prev]);
      setActiveRepo(repo);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeFixture = async () => {
    setLoading(true);
    try {
      const repo = await analyzeFixtureRepo('CivicFix');
      setRepositories(prev => [repo, ...prev]);
      setActiveRepo(repo);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const navItems = [
    { id: 'overview', label: 'Overview', icon: Compass },
    { id: 'architecture', label: 'Architecture Map', icon: Map },
    { id: 'files', label: 'File Explorer', icon: FileCode },
    { id: 'features', label: 'Feature Map', icon: Network },
    { id: 'trace', label: 'Trace This', icon: Route },
    { id: 'impact', label: 'Impact Analysis', icon: AlertTriangle },
    { id: 'ask', label: 'Ask Codebase', icon: MessageSquare },
    { id: 'history', label: 'Project History', icon: Clock },
    { id: 'notes', label: 'Project Notes', icon: FileText },
  ];

  const getStepStatus = (currentStatus: string, stepName: string) => {
    const steps = ['QUEUED', 'CLONING', 'SCANNING', 'PARSING', 'BUILDING_GRAPH', 'GENERATING_INSIGHTS', 'COMPLETED'];
    const currentIdx = steps.indexOf(currentStatus === 'READY' ? 'COMPLETED' : currentStatus);
    const stepIdx = steps.indexOf(stepName);

    if (currentIdx > stepIdx) return 'completed';
    if (currentIdx === stepIdx) return 'active';
    return 'upcoming';
  };

  return (
    <div className="min-h-screen bg-dark-900 text-gray-100 flex flex-col font-sans selection:bg-brand-500 selection:text-white">
      <Navbar
        repositories={repositories}
        activeRepo={activeRepo}
        onSelectRepo={setActiveRepo}
        onOpenIngestion={() => setIngestionOpen(true)}
        onStartTour={() => setTourOpen(true)}
        onAnalyzeFixture={handleAnalyzeFixture}
        loading={loading}
      />

      {activeRepo ? (
        <div className="flex-1 flex flex-col">
          {/* Sub Navigation Bar - disabled while analysis pending */}
          <div className="bg-dark-800/60 border-b border-gray-800 px-6 flex items-center space-x-1 overflow-x-auto">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              const isPending = PENDING_STATUSES.includes(activeRepo.status) || activeRepo.status === 'FAILED';
              return (
                <button
                  key={item.id}
                  disabled={isPending}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 py-3 px-4 text-xs font-semibold border-b-2 transition-all whitespace-nowrap ${
                    isPending ? 'opacity-40 cursor-not-allowed border-transparent text-gray-500' :
                    isActive
                      ? 'border-brand-500 text-brand-400 bg-brand-500/10'
                      : 'border-transparent text-gray-400 hover:text-gray-200 hover:bg-gray-800/40'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive && !isPending ? 'text-brand-400' : 'text-gray-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>

          <main className="flex-1 overflow-y-auto">
            {/* 1. ANALYSIS PENDING / IN-PROGRESS SCREEN */}
            {PENDING_STATUSES.includes(activeRepo.status) && (
              <div className="p-12 max-w-3xl mx-auto space-y-8 text-center">
                <div className="w-16 h-16 rounded-2xl bg-brand-600/20 border border-brand-500/40 flex items-center justify-center mx-auto text-brand-400">
                  <Loader2 className="w-8 h-8 animate-spin text-brand-400" />
                </div>

                <div>
                  <div className="inline-block px-3 py-1 rounded-full text-xs font-bold font-mono bg-brand-500/20 text-brand-300 border border-brand-500/30 uppercase mb-3">
                    STATUS: {activeRepo.status}
                  </div>
                  <h2 className="text-2xl font-extrabold text-white tracking-tight mb-2">
                    Analyzing Repository Codebase: {activeRepo.name}
                  </h2>
                  <p className="text-xs text-gray-400 font-mono">
                    Executing AST parsing, working directory scanning, and NetworkX dependency graph construction...
                  </p>
                </div>

                {/* Progress Steps List */}
                <div className="glass-panel rounded-2xl p-6 border border-gray-800 text-left space-y-4">
                  {[
                    { id: 'CLONING', label: 'Cloning / Extracting Repository Sources' },
                    { id: 'SCANNING', label: 'Scanning Files & Working Directory' },
                    { id: 'PARSING', label: 'Tree-sitter AST Parsing (JS/TS/TSX/Routes/Models)' },
                    { id: 'BUILDING_GRAPH', label: 'Building Code Network Graph & Relationships' },
                    { id: 'GENERATING_INSIGHTS', label: 'Finalizing Fact-Grounded Insights' }
                  ].map((step) => {
                    const st = getStepStatus(activeRepo.status, step.id);
                    return (
                      <div key={step.id} className="flex items-center space-x-3 text-xs font-mono">
                        {st === 'completed' ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                        ) : st === 'active' ? (
                          <Loader2 className="w-4 h-4 text-brand-400 animate-spin flex-shrink-0" />
                        ) : (
                          <span className="w-4 h-4 rounded-full border border-gray-700 flex-shrink-0" />
                        )}
                        <span className={st === 'completed' ? 'text-gray-300 font-semibold' : st === 'active' ? 'text-brand-300 font-bold' : 'text-gray-600'}>
                          {step.label}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* 2. ANALYSIS FAILED SCREEN */}
            {activeRepo.status === 'FAILED' && (
              <div className="p-12 max-w-2xl mx-auto space-y-6 text-center">
                <div className="w-16 h-16 rounded-2xl bg-red-500/20 border border-red-500/40 flex items-center justify-center mx-auto text-red-400">
                  <AlertCircle className="w-8 h-8" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white tracking-tight mb-2">
                    Analysis Failed
                  </h2>
                  <p className="text-xs text-red-400 font-mono bg-dark-900 p-4 rounded-xl border border-red-500/30 text-left overflow-x-auto">
                    {activeRepo.error_message || 'Repository could not be ingested or analyzed.'}
                  </p>
                </div>
                <button
                  onClick={() => setIngestionOpen(true)}
                  className="px-6 py-3 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs inline-flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Try Another Repository</span>
                </button>
              </div>
            )}

            {/* 3. READY / COMPLETED TAB CONTENT */}
            {(activeRepo.status === 'COMPLETED' || activeRepo.status === 'READY') && (
              <>
                {activeTab === 'overview' && <OverviewTab overview={overview} repo={activeRepo} />}
                {activeTab === 'architecture' && <ArchitectureTab repoId={activeRepo.id} />}
                {activeTab === 'files' && <FileExplorerTab repoId={activeRepo.id} />}
                {activeTab === 'features' && <FeatureMapTab repoId={activeRepo.id} overview={overview} />}
                {activeTab === 'trace' && <TraceTab repoId={activeRepo.id} />}
                {activeTab === 'impact' && <ImpactTab repoId={activeRepo.id} />}
                {activeTab === 'ask' && <AskTab repoId={activeRepo.id} />}
                {activeTab === 'history' && <HistoryTab repoId={activeRepo.id} />}
                {activeTab === 'notes' && <NotesTab repoId={activeRepo.id} />}
              </>
            )}
          </main>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="max-w-xl text-center space-y-6">
            <div className="w-20 h-20 rounded-3xl bg-gradient-to-tr from-brand-600 via-indigo-500 to-cyan-400 flex items-center justify-center mx-auto shadow-2xl shadow-brand-500/30">
              <Compass className="w-10 h-10 text-white" />
            </div>

            <h2 className="text-3xl font-extrabold text-white tracking-tight">
              Welcome to Codebase Archaeologist
            </h2>
            <p className="text-sm text-gray-400 leading-relaxed">
              Transform any unfamiliar GitHub repository or local codebase into an interactive, factual knowledge map with architecture visualization, feature flow tracing, and impact analysis.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
              <button
                onClick={handleAnalyzeFixture}
                disabled={loading}
                className="px-6 py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-dark-900 font-bold text-sm flex items-center justify-center space-x-2 shadow-lg shadow-emerald-500/20"
              >
                {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <FolderGit2 className="w-4 h-4" />}
                <span>Analyze Demo: CivicFix</span>
              </button>

              <button
                onClick={() => setIngestionOpen(true)}
                className="px-6 py-3.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-bold text-sm flex items-center justify-center space-x-2 shadow-lg shadow-brand-600/20"
              >
                <Plus className="w-4 h-4" />
                <span>Analyze Custom Repository</span>
              </button>
            </div>
          </div>
        </div>
      )}

      <RepoIngestionModal
        isOpen={ingestionOpen}
        onClose={() => setIngestionOpen(false)}
        onSubmitGitHub={handleAnalyzeGitHub}
        onSubmitZip={handleUploadZip}
      />

      <GuidedTourModal
        isOpen={tourOpen}
        onClose={() => setTourOpen(false)}
        overview={overview}
        onSelectTab={setActiveTab}
      />

      <Footer activeRepo={activeRepo} activeTab={activeTab} />
    </div>
  );
}
