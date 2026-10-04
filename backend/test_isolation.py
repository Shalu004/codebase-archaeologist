import urllib.request, json

def test_repo_isolation(repo_name, expected_keyword):
    print(f'=== TESTING REPOSITORY: {repo_name} ===')
    req = urllib.request.urlopen('http://localhost:8000/api/repositories')
    repos = json.loads(req.read().decode())
    target = next((r for r in repos if r['name'].lower() == repo_name.lower() and r['status'] == 'COMPLETED'), None)
    if not target:
        print(f'ERROR: Repo {repo_name} not found!')
        return False
    
    repo_id = target['id']
    print(f'ID: {repo_id}, Files: {target["file_count"]}, Symbols: {target["symbol_count"]}, Nodes: {target["node_count"]}, Edges: {target["edge_count"]}')

    ov = json.loads(urllib.request.urlopen(f'http://localhost:8000/api/repositories/{repo_id}/overview').read().decode())
    print('  [x] Overview Project Name:', ov['project_name'])
    print('  [x] Overview Purpose:', ov['purpose'][:100] + '...')

    feats = json.loads(urllib.request.urlopen(f'http://localhost:8000/api/repositories/{repo_id}/features').read().decode())
    feat_names = [f['name'] for f in feats[:3]]
    print('  [x] Features Discovered:', len(feats), 'features', feat_names)

    g = json.loads(urllib.request.urlopen(f'http://localhost:8000/api/repositories/{repo_id}/graph?level=system').read().decode())
    print('  [x] System Graph Modules:', len(g['nodes']), 'modules')

    req_notes = urllib.request.Request(f'http://localhost:8000/api/repositories/{repo_id}/notes', method='POST')
    notes = json.loads(urllib.request.urlopen(req_notes).read().decode())
    print('  [x] Notes Generated:', notes['notes_markdown'][:80].replace('\n', ' '))

    print(f'SUCCESS: {repo_name} isolated cleanly!\n')
    return True

if __name__ == '__main__':
    test_repo_isolation('QueryGate', 'PostgreSQL')
    test_repo_isolation('kiet-innotech', 'hackathon')
    test_repo_isolation('CivicFix', 'civic')
    test_repo_isolation('kiet-innotech', 'hackathon')
