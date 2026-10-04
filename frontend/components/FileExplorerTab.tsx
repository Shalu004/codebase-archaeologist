'use client';

import React, { useState, useEffect } from 'react';
import { Folder, FileText, ChevronRight, ChevronDown, Code2 } from 'lucide-react';
import { fetchFileTree, fetchFileContent } from '../services/api';

interface FileExplorerTabProps {
  repoId: string;
}

export const FileExplorerTab: React.FC<FileExplorerTabProps> = ({ repoId }) => {
  const [tree, setTree] = useState<any[]>([]);
  const [selectedFilePath, setSelectedFilePath] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setTree([]);
    setSelectedFilePath(null);
    setFileContent(null);
    setLoading(true);
    async function loadTree() {
      try {
        const data = await fetchFileTree(repoId);
        setTree(data.tree || []);
        if (data.tree && data.tree.length > 0) {
          const findFirstFile = (nodes: any[]): string | null => {
            for (const n of nodes) {
              if (n.type === 'file') return n.path;
              if (n.children) {
                const childFile = findFirstFile(n.children);
                if (childFile) return childFile;
              }
            }
            return null;
          };
          const firstPath = findFirstFile(data.tree);
          if (firstPath) handleSelectFile(firstPath);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadTree();
  }, [repoId]);

  const handleSelectFile = async (path: string) => {
    setSelectedFilePath(path);
    try {
      const res = await fetchFileContent(repoId, path);
      setFileContent(res.content);
    } catch (err) {
      setFileContent('Error loading file content.');
    }
  };

  const TreeNode: React.FC<{ node: any }> = ({ node }) => {
    const [open, setOpen] = useState(true);

    if (node.type === 'directory') {
      return (
        <div className="ml-2">
          <div
            onClick={() => setOpen(!open)}
            className="flex items-center space-x-1.5 py-1 px-2 hover:bg-gray-800/50 rounded-lg cursor-pointer text-xs font-mono text-gray-300 transition-colors"
          >
            {open ? <ChevronDown className="w-3.5 h-3.5 text-gray-500" /> : <ChevronRight className="w-3.5 h-3.5 text-gray-500" />}
            <Folder className="w-3.5 h-3.5 text-indigo-400" />
            <span>{node.name}</span>
          </div>
          {open && node.children && (
            <div className="border-l border-gray-800/80 ml-2">
              {node.children.map((child: any) => (
                <TreeNode key={child.id} node={child} />
              ))}
            </div>
          )}
        </div>
      );
    }

    return (
      <div
        onClick={() => handleSelectFile(node.path)}
        className={`flex items-center space-x-2 py-1 px-2 ml-4 rounded-lg cursor-pointer text-xs font-mono transition-colors ${
          selectedFilePath === node.path
            ? 'bg-indigo-500/20 text-indigo-300 font-semibold border-l-2 border-indigo-400'
            : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/40'
        }`}
      >
        <FileText className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
        <span className="truncate">{node.name}</span>
      </div>
    );
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex font-sans bg-[#080c14]">
      {/* File Tree Sidebar */}
      <div className="w-80 h-full bg-[#0d1322] border-r border-gray-800/80 p-4 overflow-y-auto">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">
          SOURCE TREE EXPLORER
        </h3>
        {loading ? (
          <div className="text-xs text-gray-500 font-mono">Scanning file tree...</div>
        ) : (
          <div className="space-y-1">
            {tree.map((node) => (
              <TreeNode key={node.id} node={node} />
            ))}
          </div>
        )}
      </div>

      {/* Code Preview Viewer */}
      <div className="flex-1 h-full bg-[#080c14] flex flex-col">
        {selectedFilePath ? (
          <>
            <div className="h-12 border-b border-gray-800 px-6 flex items-center justify-between bg-[#0d1322]">
              <div className="flex items-center space-x-2 text-xs font-mono text-gray-200">
                <Code2 className="w-4 h-4 text-indigo-400" />
                <span className="font-semibold text-emerald-400">{selectedFilePath}</span>
              </div>
            </div>

            <div className="flex-1 overflow-auto p-6 bg-[#080c14]">
              <pre className="text-xs font-mono text-gray-200 leading-relaxed">
                {fileContent?.split('\n').map((line, idx) => (
                  <div key={idx} className="flex hover:bg-gray-800/40 px-2 py-0.5 rounded">
                    <span className="w-10 text-gray-600 select-none text-right pr-4 flex-shrink-0">{idx + 1}</span>
                    <span className="whitespace-pre">{line}</span>
                  </div>
                ))}
              </pre>
            </div>
          </>
        ) : (
          <div className="h-full flex items-center justify-center text-gray-500 text-xs font-sans">
            Select a file from the tree to preview source code.
          </div>
        )}
      </div>
    </div>
  );
};

