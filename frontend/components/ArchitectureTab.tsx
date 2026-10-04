'use client';

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  MarkerType
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Search, Layers, ChevronRight, RefreshCw, Eye, X, Home, Compass } from 'lucide-react';
import { fetchCodeGraph, fetchNodeDetail, fetchFileContent } from '../services/api';

interface ArchitectureTabProps {
  repoId: string;
}

export const ArchitectureTab: React.FC<ArchitectureTabProps> = ({ repoId }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [loading, setLoading] = useState(true);
  
  const [level, setLevel] = useState<'system' | 'module' | 'file'>('system');
  const [targetModule, setTargetModule] = useState<string | null>(null);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [nodeTypeFilter, setNodeTypeFilter] = useState('ALL');

  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [nodeDetail, setNodeDetail] = useState<any>(null);
  const [fileCodeSnippet, setFileCodeSnippet] = useState<string | null>(null);

  const loadGraph = useCallback(async (currentLevel: 'system' | 'module' | 'file', moduleTarget?: string | null) => {
    setLoading(true);
    try {
      const data = await fetchCodeGraph(repoId, currentLevel, moduleTarget || undefined);
      
      const rawNodes = data.nodes || [];
      const rawEdges = data.edges || [];

      const formattedNodes: Node[] = rawNodes.map((n: any, idx: number) => {
        const row = Math.floor(idx / 4);
        const col = idx % 4;
        
        let bgColor = '#0d1322';
        let borderColor = '#374151';
        let textColor = '#F3F4F6';

        if (n.type === 'module') {
          bgColor = '#111827';
          borderColor = '#6366F1';
        } else if (n.type === 'submodule') {
          bgColor = '#064E3B';
          borderColor = '#10B981';
        } else if (n.type === 'file') {
          bgColor = '#0d1322';
          borderColor = '#1F2937';
        } else if (n.type === 'route') {
          bgColor = '#4C1D95';
          borderColor = '#8B5CF6';
        } else if (n.type === 'model') {
          bgColor = '#78350F';
          borderColor = '#F59E0B';
        }

        const subCountText = n.data?.file_count ? ` (${n.data.file_count} files)` : '';

        return {
          id: n.id,
          type: 'default',
          position: { x: col * 260 + 40, y: row * 140 + 40 },
          data: { label: `${n.label}${subCountText}`, raw: n },
          style: {
            background: bgColor,
            color: textColor,
            border: `1px solid ${borderColor}`,
            borderRadius: '10px',
            padding: '12px 16px',
            fontSize: '12px',
            fontFamily: 'JetBrains Mono, monospace',
            fontWeight: 600,
            width: 220,
            boxShadow: '0 8px 16px rgba(0, 0, 0, 0.4)'
          },
        };
      });

      const formattedEdges: Edge[] = rawEdges.map((e: any) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.type !== 'CONTAINS' ? e.type : undefined,
        animated: e.type === 'CALLS' || e.type === 'ROUTES_TO',
        style: { stroke: e.type === 'CALLS' ? '#6366F1' : e.type === 'ACCESSES' ? '#F59E0B' : '#4B5563', strokeWidth: 1.5 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#6366F1' },
      }));

      setNodes(formattedNodes);
      setEdges(formattedEdges);
    } catch (err) {
      console.error('Failed to load code graph:', err);
    } finally {
      setLoading(false);
    }
  }, [repoId, setNodes, setEdges]);

  useEffect(() => {
    setLevel('system');
    setTargetModule(null);
    setSelectedNodeId(null);
    setNodeDetail(null);
    setFileCodeSnippet(null);
  }, [repoId]);

  useEffect(() => {
    loadGraph(level, targetModule);
  }, [level, targetModule, loadGraph]);

  const handleLevelSwitch = (newLevel: 'system' | 'module' | 'file') => {
    setLevel(newLevel);
    if (newLevel === 'system') {
      setTargetModule(null);
    }
  };

  const onNodeClick = async (_: any, node: Node) => {
    setSelectedNodeId(node.id);
    setNodeDetail(null);
    setFileCodeSnippet(null);

    const rawNode = (node.data as any)?.raw;

    if (level === 'system' && rawNode?.data?.module_name) {
      setTargetModule(rawNode.data.module_name);
      setLevel('module');
      return;
    }

    if (level === 'module') {
      setLevel('file');
      return;
    }

    try {
      const detail = await fetchNodeDetail(repoId, node.id);
      setNodeDetail(detail);
      if (detail.file_path) {
        const fc = await fetchFileContent(repoId, detail.file_path);
        setFileCodeSnippet(fc.content);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const filteredNodes = useMemo(() => {
    return nodes.filter(n => {
      const labelStr = String((n.data as any)?.label || '');
      const matchesSearch = labelStr.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesType = nodeTypeFilter === 'ALL' || labelStr.toLowerCase().includes(nodeTypeFilter.toLowerCase());
      return matchesSearch && matchesType;
    });
  }, [nodes, searchTerm, nodeTypeFilter]);

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col relative bg-[#080c14] font-sans">
      {/* Top Controls & Breadcrumbs Bar */}
      <div className="z-10 px-6 py-3.5 bg-[#0d1322] border-b border-gray-800/80 flex flex-wrap items-center justify-between gap-4">
        {/* Breadcrumb Path */}
        <div className="flex items-center space-x-2 text-xs text-gray-300">
          <button
            onClick={() => handleLevelSwitch('system')}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#080c14] border border-gray-800 hover:bg-gray-800/80 hover:text-white transition-all font-medium"
          >
            <Home className="w-3.5 h-3.5 text-indigo-400" />
            <span>SYSTEM LEVEL</span>
          </button>

          {targetModule && (
            <>
              <ChevronRight className="w-3.5 h-3.5 text-gray-600" />
              <button
                onClick={() => handleLevelSwitch('module')}
                className="px-3 py-1.5 rounded-lg bg-[#080c14] border border-gray-800 text-indigo-300 hover:bg-gray-800/80 font-mono text-xs font-semibold"
              >
                MODULE: {targetModule}
              </button>
            </>
          )}

          {level === 'file' && (
            <>
              <ChevronRight className="w-3.5 h-3.5 text-gray-600" />
              <span className="px-3 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 font-mono text-xs font-semibold">
                SYMBOL GRAPH
              </span>
            </>
          )}
        </div>

        {/* Level Selector Buttons */}
        <div className="flex items-center space-x-1 bg-[#080c14] p-1 rounded-xl border border-gray-800 text-xs font-semibold">
          <button
            onClick={() => handleLevelSwitch('system')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              level === 'system' ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-400 hover:text-white'
            }`}
          >
            SYSTEM
          </button>
          <button
            onClick={() => handleLevelSwitch('module')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              level === 'module' ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-400 hover:text-white'
            }`}
          >
            MODULE
          </button>
          <button
            onClick={() => handleLevelSwitch('file')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              level === 'file' ? 'bg-indigo-600 text-white shadow-md' : 'text-gray-400 hover:text-white'
            }`}
          >
            FILE & SYMBOL
          </button>
        </div>

        {/* Search & Filters */}
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search architecture..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-[#080c14] border border-gray-800 text-xs text-white rounded-lg pl-9 pr-3 py-2 focus:outline-none focus:border-indigo-500 w-44 font-sans"
            />
          </div>

          <button
            onClick={() => loadGraph(level, targetModule)}
            className="p-2 rounded-lg bg-[#080c14] border border-gray-800 text-gray-400 hover:text-white hover:bg-gray-800"
            title="Refresh Graph"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Interactive Graph View */}
      <div className="flex-1 h-full relative bg-[#080c14]">
        {loading ? (
          <div className="h-full flex items-center justify-center text-gray-400 font-sans text-sm">
            <div className="flex items-center space-x-3">
              <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
              <span>Constructing Architectural Map ({level.toUpperCase()})...</span>
            </div>
          </div>
        ) : (
          <ReactFlow
            nodes={filteredNodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            fitView
          >
            <Controls />
            <MiniMap style={{ background: '#0d1322', borderRadius: '12px' }} nodeColor="#6366F1" />
            <Background color="#1e293b" gap={28} size={1} />
          </ReactFlow>
        )}

        {/* Floating Inspector Panel */}
        {selectedNodeId && (
          <div className="absolute right-6 top-6 bottom-6 w-96 bg-[#0d1322] border border-gray-800 rounded-2xl p-6 overflow-y-auto z-20 flex flex-col justify-between shadow-2xl space-y-4">
            <div>
              <div className="flex items-center justify-between border-b border-gray-800 pb-3 mb-4">
                <h3 className="font-extrabold text-sm text-white flex items-center space-x-2">
                  <Compass className="w-4 h-4 text-indigo-400" />
                  <span>Node Inspector</span>
                </h3>
                <button
                  onClick={() => setSelectedNodeId(null)}
                  className="text-gray-400 hover:text-white p-1 rounded-md hover:bg-gray-800"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {nodeDetail ? (
                <div className="space-y-4">
                  <div>
                    <label className="text-xs text-gray-400 font-medium uppercase tracking-wider block mb-1">NODE SYMBOL</label>
                    <p className="text-sm font-semibold text-white font-mono">{nodeDetail.label}</p>
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 font-medium uppercase tracking-wider block mb-1">NODE TYPE</label>
                    <span className="px-2.5 py-0.5 rounded text-xs font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                      {nodeDetail.type}
                    </span>
                  </div>
                  {nodeDetail.file_path && (
                    <div>
                      <label className="text-xs text-gray-400 font-medium uppercase tracking-wider block mb-1">SOURCE PATH</label>
                      <p className="text-xs text-emerald-400 font-mono bg-[#080c14] p-2.5 rounded-lg border border-gray-800 break-all">
                        {nodeDetail.file_path}
                      </p>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-3 pt-2">
                    <div className="p-3 bg-[#080c14] rounded-xl border border-gray-800 text-center">
                      <div className="text-[10px] text-gray-400 uppercase font-semibold">Incoming Edges</div>
                      <div className="text-xl font-bold text-indigo-400 font-mono">{nodeDetail.incoming_connections_count}</div>
                    </div>
                    <div className="p-3 bg-[#080c14] rounded-xl border border-gray-800 text-center">
                      <div className="text-[10px] text-gray-400 uppercase font-semibold">Outgoing Edges</div>
                      <div className="text-xl font-bold text-cyan-400 font-mono">{nodeDetail.outgoing_connections_count}</div>
                    </div>
                  </div>

                  {fileCodeSnippet && (
                    <div className="mt-4 space-y-1.5">
                      <label className="text-xs text-gray-400 font-medium uppercase tracking-wider block">SOURCE CODE PREVIEW</label>
                      <pre className="p-3.5 rounded-xl bg-[#080c14] text-xs font-mono text-gray-300 max-h-56 overflow-y-auto border border-gray-800 leading-relaxed">
                        {fileCodeSnippet.slice(0, 1000)}
                      </pre>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-xs text-gray-400 font-mono">Fetching node metadata...</div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

