'use client';

import React from 'react';
import Link from 'next/link';
import { Compass, ArrowLeft, ShieldCheck, Layers, GitBranch, Terminal, HelpCircle, AlertCircle, FileCode, CheckCircle2 } from 'lucide-react';

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 font-sans selection:bg-indigo-500 selection:text-white flex flex-col">
      {/* Header */}
      <header className="h-16 border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 via-blue-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Compass className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="font-extrabold text-base tracking-tight text-slate-100 font-sans">
                CODEBASE ARCHAEOLOGIST
              </h1>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-500/15 text-indigo-400 border border-indigo-500/30">
                v1.0 Docs
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-normal">
              The Google Maps for Any Unfamiliar Codebase
            </p>
          </div>
        </div>

        <Link
          href="/"
          className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-indigo-500/50 text-slate-200 text-xs font-semibold flex items-center space-x-2 transition-all"
        >
          <ArrowLeft className="w-4 h-4 text-indigo-400" />
          <span>Back to Application</span>
        </Link>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-4xl mx-auto px-6 py-12 space-y-12">
        
        {/* Hero Section */}
        <div className="glass-panel p-8 border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950/30 rounded-2xl space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-xs font-semibold font-mono">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>OFFICIAL PRODUCT DOCUMENTATION</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            What is Codebase Archaeologist?
          </h1>
          <p className="text-slate-300 text-base leading-relaxed">
            Codebase Archaeologist is an automated knowledge extraction and exploration platform for software repositories. It acts as <strong>"The Google Maps for Any Unfamiliar Codebase"</strong> — turning complex, unfamiliar repositories into interactive visual knowledge maps, execution flow journeys, and blast-radius impact scanners.
          </p>
        </div>

        {/* Section 1: What It Does */}
        <section className="space-y-6">
          <div className="flex items-center space-x-2 text-xs font-semibold text-indigo-400 uppercase tracking-wider">
            <Layers className="w-4 h-4" />
            <span>Core System Capabilities</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">What Codebase Archaeologist Does</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { title: "1. Repository Ingestion", desc: "Clones public GitHub repositories or ingests uploaded local ZIP source archives." },
              { title: "2. Static Code Analysis", desc: "Scans repository directories, filters non-source assets, and computes directory structures." },
              { title: "3. AST & Symbol Extraction", desc: "Parses source code using Tree-sitter AST parsers across JS, TS, TSX, Python, and SQL." },
              { title: "4. Dependency Graph Construction", desc: "Builds NetworkX call graphs, route maps, data model mappings, and import dependencies." },
              { title: "5. Feature Discovery", desc: "Groups related controllers, routes, and entities into high-level functional capabilities." },
              { title: "6. Feature Flow Reconstruction", desc: "Maps execution journeys from UI triggers -> API endpoints -> services -> database queries." },
              { title: "7. Evidence-Grounded Q&A", desc: "Answers technical questions grounded strictly in verified source symbol citations." },
              { title: "8. Reverse Impact Analysis", desc: "Calculates total blast radius and upstream breakages before making code changes." },
              { title: "9. Git History Analysis", desc: "Tracks architectural shifts, commit milestones, and contributor activity timelines." },
              { title: "10. Developer Onboarding", desc: "Generates automated Field Guides, entry point recommendations, and quickstarts." }
            ].map((item, idx) => (
              <div key={idx} className="p-5 rounded-xl bg-[#0d1322] border border-slate-800 space-y-2">
                <h3 className="text-sm font-bold text-slate-100">{item.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Section 2: How to Use It */}
        <section className="space-y-6">
          <div className="flex items-center space-x-2 text-xs font-semibold text-cyan-400 uppercase tracking-wider">
            <Terminal className="w-4 h-4" />
            <span>Developer User Journey</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">How to Use Codebase Archaeologist</h2>

          <div className="space-y-3 font-mono text-xs">
            {[
              "1. Ingest Repository: Provide a GitHub URL or drag-and-drop a ZIP archive via '+ Analyze Repository'.",
              "2. Automatic Analysis: Wait for scanner, AST parser, and graph engine execution to complete.",
              "3. Explore Overview: Review project purpose, scanned file counts, tech stack, and primary entry points.",
              "4. Inspect Feature Map: Browse discovered system capabilities and click to inspect call layers.",
              "5. Navigate Architecture Map: Zoom between System, Module, and File/Symbol interactive graph levels.",
              "6. Trace Execution Flows: Follow step-by-step journeys from UI actions down to database models.",
              "7. Query Codebase AI: Ask questions grounded in source code evidence chips.",
              "8. Run Impact Analysis: Select target symbols to calculate exact upstream blast radius before editing code."
            ].map((step, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-[#0d1322] border border-slate-800 text-slate-300">
                {step}
              </div>
            ))}
          </div>
        </section>

        {/* Section 3: Evidence & Confidence */}
        <section className="space-y-6">
          <div className="flex items-center space-x-2 text-xs font-semibold text-emerald-400 uppercase tracking-wider">
            <CheckCircle2 className="w-4 h-4" />
            <span>Fact-Grounded Analysis</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Evidence & Confidence Ratings</h2>
          <p className="text-xs text-slate-300 leading-relaxed">
            Every insight, feature card, and Q&A answer is verified against concrete source code evidence (file paths, line numbers, and symbol definitions).
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-5 rounded-xl bg-[#0d1322] border border-slate-800 space-y-2">
              <span className="badge-confidence badge-confidence-high inline-flex">HIGH CONFIDENCE</span>
              <p className="text-xs text-slate-400 leading-relaxed">
                Directly verified by AST symbol definitions, explicit import statements, and active route decorators.
              </p>
            </div>
            <div className="p-5 rounded-xl bg-[#0d1322] border border-slate-800 space-y-2">
              <span className="badge-confidence badge-confidence-medium inline-flex">MEDIUM CONFIDENCE</span>
              <p className="text-xs text-slate-400 leading-relaxed">
                Derived from token similarity, structural heuristics, or naming convention call matching.
              </p>
            </div>
            <div className="p-5 rounded-xl bg-[#0d1322] border border-slate-800 space-y-2">
              <span className="badge-confidence badge-confidence-low inline-flex">LOW CONFIDENCE</span>
              <p className="text-xs text-slate-400 leading-relaxed">
                Inferred fallback data when source files are sparse or structural citations are limited.
              </p>
            </div>
          </div>
        </section>

        {/* Section 4: Limitations */}
        <section className="space-y-6">
          <div className="flex items-center space-x-2 text-xs font-semibold text-amber-400 uppercase tracking-wider">
            <AlertCircle className="w-4 h-4" />
            <span>Static Analysis Boundaries</span>
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">System Limitations</h2>
          
          <div className="p-6 rounded-2xl bg-[#0d1322] border border-slate-800 text-xs text-slate-300 leading-relaxed space-y-3">
            <p>Static code analysis produces deterministic, grounded representations of code structure. However, static parsers may not fully resolve:</p>
            <ul className="list-disc pl-5 space-y-1 text-slate-400 font-mono">
              <li>Dynamic runtime imports (e.g. `import(variable)`)</li>
              <li>Runtime reflection or dynamic string evaluation (`eval()`)</li>
              <li>External microservice calls over un-annotated HTTP endpoints</li>
              <li>Code files outside the uploaded repository context</li>
            </ul>
          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/80 py-6 px-6 mt-auto text-slate-400 font-sans text-center text-xs">
        Built with ❤️ for all the curious minds
      </footer>
    </div>
  );
}
