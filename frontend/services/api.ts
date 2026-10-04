const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface Repository {
  id: string;
  name: string;
  description?: string;
  url?: string;
  source_type: string;
  status: string;
  error_message?: string;
  file_count: number;
  symbol_count: number;
  node_count: number;
  edge_count: number;
  created_at: string;
}

export async function fetchRepositories(): Promise<Repository[]> {
  const res = await fetch(`${API_BASE}/repositories`);
  if (!res.ok) throw new Error('Failed to fetch repositories');
  return res.json();
}

export async function fetchRepository(id: string): Promise<Repository> {
  const res = await fetch(`${API_BASE}/repositories/${id}`);
  if (!res.ok) throw new Error('Failed to fetch repository');
  return res.json();
}

export async function createGitHubRepo(githubUrl: string): Promise<Repository> {
  const res = await fetch(`${API_BASE}/repositories`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ github_url: githubUrl }),
  });
  if (!res.ok) throw new Error('Failed to ingest GitHub repository');
  return res.json();
}

export async function uploadZipRepo(file: File): Promise<Repository> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/repositories/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to upload ZIP repository');
  return res.json();
}

export async function analyzeFixtureRepo(name: string = 'CivicFix'): Promise<Repository> {
  const res = await fetch(`${API_BASE}/repositories/analyze-fixture?name=${encodeURIComponent(name)}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to analyze fixture repository');
  return res.json();
}

export async function fetchFileTree(repoId: string) {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/tree`);
  if (!res.ok) throw new Error('Failed to fetch file tree');
  return res.json();
}

export async function fetchFileContent(repoId: string, path: string) {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/file-content?path=${encodeURIComponent(path)}`);
  if (!res.ok) throw new Error('Failed to fetch file content');
  return res.json();
}

export async function fetchCodeGraph(repoId: string, level: string = 'system', targetModule?: string) {
  let url = `${API_BASE}/repositories/${repoId}/graph?level=${encodeURIComponent(level)}`;
  if (targetModule) {
    url += `&target_module=${encodeURIComponent(targetModule)}`;
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch graph');
  return res.json();
}

export async function searchSymbols(repoId: string, query: string) {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/search-symbols?query=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error('Failed to search symbols');
  return res.json();
}

export async function fetchNodeDetail(repoId: string, nodeId: string) {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/nodes/${nodeId}`);
  if (!res.ok) throw new Error('Failed to fetch node detail');
  return res.json();
}

export async function analyzeImpact(repoId: string, payload: { node_id?: string; file_path?: string; symbol_name?: string }) {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/impact`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to analyze impact');
  return res.json();
}

export async function traceFeature(repoId: string, query: string) {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/trace`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ feature_description: query }),
  });
  if (!res.ok) throw new Error('Failed to trace feature');
  return res.json();
}

export async function askCodebase(repoId: string, question: string) {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error('Failed to query codebase AI');
  return res.json();
}

export async function fetchOverview(repoId: string) {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/overview`);
  if (!res.ok) throw new Error('Failed to fetch overview');
  return res.json();
}

export async function generateProjectNotes(repoId: string) {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/notes`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to generate notes');
  return res.json();
}

export async function fetchTimeline(repoId: string) {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/timeline`);
  if (!res.ok) throw new Error('Failed to fetch timeline');
  return res.json();
}

export async function fetchDiscoveredFeatures(repoId: string) {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/features`);
  if (!res.ok) throw new Error('Failed to fetch discovered features');
  return res.json();
}

export async function fetchFeatureDetail(repoId: string, featureId: string) {
  const res = await fetch(`${API_BASE}/repositories/${repoId}/features/${encodeURIComponent(featureId)}`);
  if (!res.ok) throw new Error('Failed to fetch feature detail');
  return res.json();
}
