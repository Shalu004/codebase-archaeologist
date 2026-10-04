import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

REPOS_TO_TEST = [
    {"name": "QueryGate", "url": "https://github.com/YASH-YADAV-dynamo/QueryGate"},
    {"name": "kiet-innotech", "url": "https://github.com/something1703/kiet-innotech"},
    {"name": "CivicFix", "url": "https://github.com/Shalu004/CivicFix"},
    {"name": "cors", "url": "https://github.com/expressjs/cors"}
]

def test_01_invalid_github_url_ingestion():
    """Test ingest with invalid / non-existent GitHub URL"""
    response = client.post("/api/repositories", json={
        "github_url": "https://github.com/invalid-user-123456789/nonexistent-repo-999"
    })
    # Must fail fast with 400 Bad Request
    assert response.status_code == 400
    assert "Invalid or inaccessible GitHub repository" in response.json()["detail"]

def test_02_ingest_all_repositories():
    """Ingest and analyze target repositories"""
    for repo in REPOS_TO_TEST:
        res = client.post("/api/repositories", json={"github_url": repo["url"]})
        assert res.status_code in [200, 201], f"Failed to ingest {repo['name']}: {res.text}"
        data = res.json()
        assert "id" in data
        assert data["status"].lower() in ["completed", "analyzing", "queued", "cloning", "parsing", "building_graph", "generating_insights"]

def test_03_querygate_full_user_journey():
    """Test full user journey on QueryGate"""
    list_res = client.get("/api/repositories")
    assert list_res.status_code == 200
    repos = list_res.json()
    qgate = next((r for r in repos if "querygate" in r["name"].lower()), None)
    assert qgate is not None, "QueryGate repository not found in ingested repos"
    repo_id = qgate["id"]

    # 1. Overview Endpoint
    ov_res = client.get(f"/api/repositories/{repo_id}/overview")
    assert ov_res.status_code == 200
    ov_data = ov_res.json()
    assert "project_name" in ov_data
    assert "purpose" in ov_data
    assert "objectives" in ov_data
    assert "target_users" in ov_data

    # 2. Features Endpoint
    feat_res = client.get(f"/api/repositories/{repo_id}/features")
    assert feat_res.status_code == 200
    feats = feat_res.json()
    assert isinstance(feats, list)
    assert len(feats) > 0

    for feat in feats:
        assert "name" in feat
        assert "confidence" in feat

    # 3. Graph Endpoint
    graph_res = client.get(f"/api/repositories/{repo_id}/graph?level=system")
    assert graph_res.status_code == 200
    graph_data = graph_res.json()
    assert "nodes" in graph_data
    assert len(graph_data["nodes"]) > 0

    # 4. Ask Codebase Endpoint (Q1, Q2, Q4)
    ask_res = client.post(f"/api/repositories/{repo_id}/ask", json={"question": "How does SQL execution work?"})
    assert ask_res.status_code == 200
    ask_data = ask_res.json()
    assert "summary" in ask_data
    assert "explanation" in ask_data
    assert "evidence" in ask_data
    assert len(ask_data["evidence"]) > 0, "Evidence citations must be returned for QueryGate"
    for ev in ask_data["evidence"]:
        assert "file_path" in ev and ev["file_path"], "Evidence file_path missing"

    # 5. Trace Feature Endpoint (Q6, Q7)
    trace_res = client.post(f"/api/repositories/{repo_id}/trace", json={"feature_name": "SQL Execution"})
    assert trace_res.status_code == 200
    trace_data = trace_res.json()
    assert "trace_steps" in trace_data

    # 6. Impact Analysis Endpoint (Q8)
    impact_res = client.post(f"/api/repositories/{repo_id}/impact", json={"symbol_name": "execute_sql"})
    assert impact_res.status_code == 200
    impact_data = impact_res.json()
    assert "total_affected_count" in impact_data
    assert "direct_dependents" in impact_data

    # 7. Timeline Endpoint (Q10)
    timeline_res = client.get(f"/api/repositories/{repo_id}/timeline")
    assert timeline_res.status_code == 200
    timeline_data = timeline_res.json()
    assert "timeline" in timeline_data

    # 8. Notes Endpoint (Q9)
    notes_res = client.post(f"/api/repositories/{repo_id}/notes")
    assert notes_res.status_code == 200
    notes_data = notes_res.json()
    assert "notes_markdown" in notes_data
    assert len(notes_data["notes_markdown"]) > 100

def test_04_kiet_innotech_full_user_journey():
    """Test full user journey on kiet-innotech"""
    list_res = client.get("/api/repositories")
    assert list_res.status_code == 200
    repos = list_res.json()
    kiet_repo = next((r for r in repos if "kiet" in r["name"].lower()), None)
    assert kiet_repo is not None
    repo_id = kiet_repo["id"]

    ov_res = client.get(f"/api/repositories/{repo_id}/overview")
    assert ov_res.status_code == 200

    ask_res = client.post(f"/api/repositories/{repo_id}/ask", json={"question": "Where are API routes defined?"})
    assert ask_res.status_code == 200

def test_05_civicfix_full_user_journey():
    """Test full user journey on CivicFix"""
    list_res = client.get("/api/repositories")
    assert list_res.status_code == 200
    repos = list_res.json()
    civic_repo = next((r for r in repos if "civic" in r["name"].lower()), None)
    assert civic_repo is not None
    repo_id = civic_repo["id"]

    ov_res = client.get(f"/api/repositories/{repo_id}/overview")
    assert ov_res.status_code == 200

    impact_res = client.post(f"/api/repositories/{repo_id}/impact", json={"symbol_name": "Issue"})
    assert impact_res.status_code == 200

def test_06_cors_frontend_no_db_repo_user_journey():
    """Test user journey on a repository without database models (expressjs/cors)"""
    list_res = client.get("/api/repositories")
    assert list_res.status_code == 200
    repos = list_res.json()
    cors_repo = next((r for r in repos if "cors" in r["name"].lower()), None)
    assert cors_repo is not None
    repo_id = cors_repo["id"]

    ov_res = client.get(f"/api/repositories/{repo_id}/overview")
    assert ov_res.status_code == 200

    notes_res = client.post(f"/api/repositories/{repo_id}/notes")
    assert notes_res.status_code == 200
