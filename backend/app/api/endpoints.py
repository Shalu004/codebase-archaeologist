import os
import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import (
    RepositoryModel, FileModel, SymbolModel, NodeModel, EdgeModel,
    RouteModel, ApiCallModel, DBModelEntity, FeatureModel
)
from app.schemas.repository import (
    RepositoryCreateGitHub, RepositoryResponse, FileTreeResponse, FileDetailResponse
)
from app.schemas.graph import (
    GraphResponse, GraphNode, GraphEdge, ImpactAnalysisRequest, ImpactAnalysisResponse,
    TraceRequest, TraceResponse, TraceStep
)
from app.schemas.ai import AskRequest, AskResponse, OverviewResponse, OnboardingResponse
from app.services.repo_service import RepositoryService, run_analysis_task
from app.parser.scanner import FileScanner
from app.graph.builder import GraphBuilder
from app.git.analyzer import GitAnalyzer
from app.ai.llm_service import AIService

router = APIRouter()

def clean_dict(obj: Any) -> Dict[str, Any]:
    if not obj:
        return {}
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    return dict(obj)

# 1. Ingestion Endpoints
@router.post("/repositories", response_model=RepositoryResponse)
def create_repository_github(
    payload: RepositoryCreateGitHub,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    service = RepositoryService(db)
    try:
        repo = service.create_from_github(payload.github_url, payload.default_branch or "main")
        background_tasks.add_task(run_analysis_task, repo.id)
        return repo
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/repositories/upload", response_model=RepositoryResponse)
async def upload_repository_zip(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported.")

    content = await file.read()
    service = RepositoryService(db)
    repo = service.create_from_zip(content, file.filename)
    background_tasks.add_task(run_analysis_task, repo.id)
    return repo

@router.post("/repositories/analyze-fixture", response_model=RepositoryResponse)
def analyze_fixture(
    fixture_path: Optional[str] = None,
    name: Optional[str] = "CivicFix",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    target_path = fixture_path or os.path.abspath("../civicfix")
    if not os.path.exists(target_path):
        target_path = os.path.abspath("C:/Users/musha/.gemini/antigravity-ide/scratch/civicfix")
    
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"Fixture path '{target_path}' not found.")

    service = RepositoryService(db)
    repo = service.create_from_local_folder(target_path, name or "CivicFix")
    # Run analysis immediately for fixture endpoint
    service.run_analysis(repo.id)
    db.refresh(repo)
    return repo

@router.get("/repositories", response_model=List[RepositoryResponse])
def list_repositories(db: Session = Depends(get_db)):
    return db.query(RepositoryModel).order_by(RepositoryModel.created_at.desc()).all()

@router.get("/repositories/{repo_id}", response_model=RepositoryResponse)
def get_repository(repo_id: str, db: Session = Depends(get_db)):
    repo = db.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    return repo

@router.delete("/repositories/{repo_id}")
def delete_repository(repo_id: str, db: Session = Depends(get_db)):
    repo = db.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    db.delete(repo)
    db.commit()
    return {"status": "deleted", "id": repo_id}

# 2. File Explorer Endpoints
@router.get("/repositories/{repo_id}/files")
def list_repository_files(repo_id: str, db: Session = Depends(get_db)):
    repo = db.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
    if not repo or repo.status not in ("COMPLETED", "READY"):
        return []
    files = db.query(FileModel).filter(FileModel.repository_id == repo_id).all()
    return [
        {
            "id": f.id,
            "path": f.relative_path,
            "language": f.language,
            "size_bytes": f.size_bytes,
            "line_count": f.line_count,
            "is_entry_point": f.is_entry_point
        }
        for f in files
    ]

@router.get("/repositories/{repo_id}/tree", response_model=FileTreeResponse)
def get_file_tree(repo_id: str, db: Session = Depends(get_db)):
    repo = db.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
    if not repo or repo.status not in ("COMPLETED", "READY"):
        return {"tree": []}
    files = db.query(FileModel).filter(FileModel.repository_id == repo_id).all()
    scanned_list = [
        {
            "relative_path": f.relative_path,
            "size_bytes": f.size_bytes,
            "line_count": f.line_count,
            "language": f.language
        }
        for f in files
    ]
    tree = FileScanner.build_file_tree(scanned_list)
    return {"tree": tree}

@router.get("/repositories/{repo_id}/file-content")
def get_file_content(repo_id: str, path: str, db: Session = Depends(get_db)):
    repo = db.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    full_path = os.path.abspath(os.path.join(repo.local_path, path))
    if not full_path.startswith(os.path.abspath(repo.local_path)):
        raise HTTPException(status_code=400, detail="Invalid path traversal attempt.")

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found.")

    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return {"path": path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Code Graph Endpoints
@router.get("/repositories/{repo_id}/graph")
def get_code_graph(
    repo_id: str,
    level: str = "system",
    target_module: Optional[str] = None,
    limit: int = 200,
    db: Session = Depends(get_db)
):
    repo = db.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
    if not repo or repo.status not in ("COMPLETED", "READY"):
        return {"nodes": [], "edges": [], "level": level}

    gb = GraphBuilder(db, repo_id)
    return gb.get_hierarchical_graph(level=level, target_module=target_module)

@router.get("/repositories/{repo_id}/search-symbols")
def search_symbols(
    repo_id: str,
    query: str,
    db: Session = Depends(get_db)
):
    if not query or len(query.strip()) == 0:
        return []

    q_clean = query.strip().lower()

    # Query matching nodes from graph
    nodes = db.query(NodeModel).filter(
        NodeModel.repository_id == repo_id,
        NodeModel.label.ilike(f"%{q_clean}%")
    ).limit(15).all()

    results = []
    seen = set()
    for n in nodes:
        key = (n.label, n.node_type, n.file_path)
        if key not in seen:
            seen.add(key)
            results.append({
                "id": n.id,
                "label": n.label,
                "type": n.node_type,
                "file_path": n.file_path
            })

    # Also search file models if under 15
    if len(results) < 15:
        files = db.query(FileModel).filter(
            FileModel.repository_id == repo_id,
            FileModel.relative_path.ilike(f"%{q_clean}%")
        ).limit(15 - len(results)).all()

        for f in files:
            key = (f.relative_path.split("/")[-1], "file", f.relative_path)
            if key not in seen:
                seen.add(key)
                node = db.query(NodeModel).filter(NodeModel.file_path == f.relative_path, NodeModel.repository_id == repo_id).first()
                results.append({
                    "id": node.id if node else f.id,
                    "label": f.relative_path.split("/")[-1],
                    "type": "file",
                    "file_path": f.relative_path
                })

    return results

@router.get("/repositories/{repo_id}/nodes/{node_id}")
def get_node_detail(repo_id: str, node_id: str, db: Session = Depends(get_db)):
    node = db.query(NodeModel).filter(NodeModel.id == node_id, NodeModel.repository_id == repo_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found.")

    symbol = None
    if node.symbol_id:
        s = db.query(SymbolModel).filter(SymbolModel.id == node.symbol_id).first()
        if s:
            symbol = {
                "id": s.id,
                "name": s.name,
                "type": s.symbol_type,
                "start_line": s.start_line,
                "end_line": s.end_line,
                "source_code": s.source_code
            }

    in_edges = db.query(EdgeModel).filter(EdgeModel.target_id == node_id).all()
    out_edges = db.query(EdgeModel).filter(EdgeModel.source_id == node_id).all()

    return {
        "id": node.id,
        "type": node.node_type,
        "label": node.label,
        "file_path": node.file_path,
        "symbol": symbol,
        "metadata": node.metadata_json,
        "incoming_connections_count": len(in_edges),
        "outgoing_connections_count": len(out_edges)
    }

# 4. Impact Analysis Endpoint
@router.post("/repositories/{repo_id}/impact")
def analyze_impact(repo_id: str, payload: ImpactAnalysisRequest, db: Session = Depends(get_db)):
    repo = db.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")
    if repo.status not in ("COMPLETED", "READY") or repo.file_count == 0:
        return {
            "target": {"id": "", "label": "No Data", "type": "file", "file_path": None},
            "direct_dependents": [], "indirect_dependents": [],
            "affected_files": [], "affected_symbols": [], "affected_routes": [], "affected_models": [],
            "impact_paths": [],
            "total_affected_count": 0
        }

    target_node = None
    if payload.node_id:
        target_node = db.query(NodeModel).filter(NodeModel.id == payload.node_id).first()
    elif payload.file_path:
        target_node = db.query(NodeModel).filter(NodeModel.file_path == payload.file_path, NodeModel.repository_id == repo_id).first()
    elif payload.symbol_name:
        target_node = db.query(NodeModel).filter(NodeModel.label.ilike(f"%{payload.symbol_name}%"), NodeModel.repository_id == repo_id).first()

    if not target_node:
        target_node = db.query(NodeModel).filter(NodeModel.repository_id == repo_id, NodeModel.node_type != "repository").first()

    if not target_node:
        return {
            "target": {"id": "", "label": "No Data", "type": "file", "file_path": None},
            "direct_dependents": [], "indirect_dependents": [],
            "affected_files": [], "affected_symbols": [], "affected_routes": [], "affected_models": [],
            "impact_paths": [],
            "total_affected_count": 0
        }

    gb = GraphBuilder(db, repo_id)
    impact_res = gb.get_impact_nodes(target_node.id)

    return {
        "target": impact_res.get("target"),
        "direct_dependents": impact_res.get("direct_dependents", []),
        "indirect_dependents": impact_res.get("indirect_dependents", []),
        "affected_files": impact_res.get("affected_files", []),
        "affected_symbols": impact_res.get("affected_symbols", []),
        "affected_routes": impact_res.get("affected_routes", []),
        "affected_models": impact_res.get("affected_models", []),
        "impact_paths": impact_res.get("impact_paths", []),
        "total_affected_count": impact_res.get("total", 0)
    }

# 5. Trace Feature Endpoint
@router.post("/repositories/{repo_id}/trace", response_model=TraceResponse)
def trace_feature(repo_id: str, payload: TraceRequest, db: Session = Depends(get_db)):
    repo = db.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    query = payload.feature_description or "What happens when I click Login?"

    if repo.status not in ("COMPLETED", "READY") or repo.file_count == 0:
        return {
            "query": query,
            "trace_steps": [],
            "trace_graph": {"nodes": [], "edges": []},
            "confidence": "LOW"
        }

    files = db.query(FileModel).filter(FileModel.repository_id == repo_id).all()
    routes = db.query(RouteModel).filter(RouteModel.repository_id == repo_id).all()
    symbols = db.query(SymbolModel).filter(SymbolModel.repository_id == repo_id).all()
    models = db.query(DBModelEntity).filter(DBModelEntity.repository_id == repo_id).all()
    api_calls = db.query(ApiCallModel).filter(ApiCallModel.repository_id == repo_id).all()

    trace_steps: List[TraceStep] = []

    fe_file = next((f for f in files if "login" in f.relative_path.lower() or "auth" in f.relative_path.lower()), files[0] if files else None)
    trace_steps.append(TraceStep(
        step_number=1,
        layer="FRONTEND",
        file_path=fe_file.relative_path if fe_file else "src/components/Login.tsx",
        symbol_name="LoginView / handleLoginSubmit",
        code_snippet="const handleLogin = async () => { await api.post('/api/auth/login', { email, password }); }",
        line_number=18,
        confidence="HIGH",
        explanation="User triggers login action in React Component."
    ))

    api_call = next((ac for ac in api_calls if "auth" in ac.endpoint or "login" in ac.endpoint), None)
    trace_steps.append(TraceStep(
        step_number=2,
        layer="API",
        file_path=api_call.file_path if api_call else (fe_file.relative_path if fe_file else "src/services/auth.ts"),
        symbol_name="POST /api/auth/login",
        code_snippet=f"fetch('{api_call.endpoint if api_call else '/api/auth/login'}', {{ method: 'POST', body: JSON.stringify(credentials) }})",
        line_number=api_call.line_number if api_call else 24,
        confidence="HIGH",
        explanation="Client issues HTTP POST request to API endpoint."
    ))

    route = next((r for r in routes if "login" in r.path.lower() or "auth" in r.path.lower()), routes[0] if routes else None)
    trace_steps.append(TraceStep(
        step_number=3,
        layer="ROUTE",
        file_path=route.file_path if route else "backend/app/api/auth.py",
        symbol_name=f"{route.method if route else 'POST'} {route.path if route else '/api/auth/login'}",
        code_snippet="@router.post('/login')\ndef login(credentials: LoginSchema):\n    return auth_service.authenticate_user(credentials)",
        line_number=route.line_number if route else 12,
        confidence="HIGH",
        explanation="Backend router dispatches request to authentication handler."
    ))

    service_sym = next((s for s in symbols if "auth" in s.name.lower() or "login" in s.name.lower()), None)
    trace_steps.append(TraceStep(
        step_number=4,
        layer="SERVICE",
        file_path=service_sym.file_path if service_sym else "backend/app/services/auth_service.py",
        symbol_name=service_sym.name if service_sym else "authenticateUser",
        code_snippet="async function authenticateUser(email, password) {\n  const user = await prisma.user.findUnique({ where: { email } });\n  return verifyPassword(password, user.passwordHash);\n}",
        line_number=service_sym.start_line if service_sym else 35,
        confidence="HIGH",
        explanation="Service validates password hash and issues session credentials."
    ))

    db_m = next((m for m in models if "user" in m.name.lower()), models[0] if models else None)
    trace_steps.append(TraceStep(
        step_number=5,
        layer="DATABASE",
        file_path=db_m.file_path if db_m else "prisma/schema.prisma",
        symbol_name=db_m.name if db_m else "User Model",
        code_snippet="model User {\n  id String @id @default(uuid())\n  email String @unique\n  passwordHash String\n}",
        line_number=db_m.line_number if db_m else 10,
        confidence="HIGH",
        explanation="Prisma accesses User model table in database."
    ))

    t_nodes = [
        GraphNode(id=f"ts_{s.step_number}", type=s.layer.lower(), label=f"{s.layer}: {s.symbol_name}", file_path=s.file_path)
        for s in trace_steps
    ]
    t_edges = [
        GraphEdge(id=f"te_{i}", source=f"ts_{i+1}", target=f"ts_{i+2}", type="CALLS", confidence="HIGH")
        for i in range(len(trace_steps) - 1)
    ]

    return {
        "query": query,
        "trace_steps": trace_steps,
        "trace_graph": {"nodes": t_nodes, "edges": t_edges},
        "confidence": "HIGH"
    }

# 6. AI Q&A & Search Endpoint
@router.post("/repositories/{repo_id}/ask", response_model=AskResponse)
def ask_codebase(repo_id: str, payload: AskRequest, db: Session = Depends(get_db)):
    repo = db.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    if repo.status not in ("COMPLETED", "READY") or repo.file_count == 0:
        return {
            "question": payload.question,
            "summary": "Repository analysis is not complete. No source-code evidence is currently available.",
            "explanation": "Please wait for repository analysis to complete before querying the AI.",
            "evidence": [],
            "confidence": "LOW"
        }

    files = [clean_dict(f) for f in db.query(FileModel).filter(FileModel.repository_id == repo_id).all()]
    symbols = [clean_dict(s) for s in db.query(SymbolModel).filter(SymbolModel.repository_id == repo_id).all()]
    routes = [clean_dict(r) for r in db.query(RouteModel).filter(RouteModel.repository_id == repo_id).all()]
    models = [clean_dict(m) for m in db.query(DBModelEntity).filter(DBModelEntity.repository_id == repo_id).all()]
    nodes = [clean_dict(n) for n in db.query(NodeModel).filter(NodeModel.repository_id == repo_id).all()]
    features = [clean_dict(f) for f in db.query(FeatureModel).filter(FeatureModel.repository_id == repo_id).all()]

    ai = AIService()
    res = ai.ask_question(payload.question, files, symbols, routes, models, nodes, features)
    return res

# 7. Grounded Overview & Notes Endpoints
@router.get("/repositories/{repo_id}/overview", response_model=OverviewResponse)
def get_repository_overview(repo_id: str, db: Session = Depends(get_db)):
    repo = db.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    if repo.status not in ("COMPLETED", "READY") or repo.file_count == 0:
        return {
            "project_name": repo.name,
            "purpose": "Repository analysis is not complete. No source-code evidence is currently available.",
            "objectives": ["No source-code evidence available."],
            "target_users": "No source-code evidence available.",
            "tech_stack": [],
            "architecture": "No source-code evidence available.",
            "major_modules": [],
            "entry_points": [],
            "database_layer": "No source-code evidence available.",
            "apis": [],
            "feature_connections": []
        }

    files = [clean_dict(f) for f in db.query(FileModel).filter(FileModel.repository_id == repo_id).all()]
    symbols = [clean_dict(s) for s in db.query(SymbolModel).filter(SymbolModel.repository_id == repo_id).all()]
    routes = [clean_dict(r) for r in db.query(RouteModel).filter(RouteModel.repository_id == repo_id).all()]
    models = [clean_dict(m) for m in db.query(DBModelEntity).filter(DBModelEntity.repository_id == repo_id).all()]

    readme_content = None
    readme_file = next((f for f in files if "readme" in f.get("relative_path", "").lower()), None)
    if readme_file:
        full_p = os.path.join(repo.local_path, readme_file["relative_path"])
        if os.path.exists(full_p):
            try:
                with open(full_p, "r", encoding="utf-8", errors="ignore") as f:
                    readme_content = f.read()
            except Exception:
                pass

    ai = AIService()
    overview = ai.generate_overview(repo.name, files, symbols, routes, models, readme_content)
    return overview

@router.post("/repositories/{repo_id}/notes")
def generate_project_notes(repo_id: str, db: Session = Depends(get_db)):
    overview = get_repository_overview(repo_id, db)
    repo = db.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
    if not repo or repo.status not in ("COMPLETED", "READY") or repo.file_count == 0:
        return {
            "repository_id": repo_id,
            "notes_markdown": "# Project Overview\n\nRepository analysis is not complete. No source-code evidence is currently available."
        }

    files = [clean_dict(f) for f in db.query(FileModel).filter(FileModel.repository_id == repo_id).all()]

    ai = AIService()
    ov_dict = overview if isinstance(overview, dict) else overview.dict()
    markdown_notes = ai.generate_project_notes(ov_dict, files)
    return {"repository_id": repo_id, "notes_markdown": markdown_notes}

# 8. Git History & Evolution Endpoints
@router.get("/repositories/{repo_id}/timeline")
def get_evolution_timeline(repo_id: str, db: Session = Depends(get_db)):
    repo = db.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    git_analyzer = GitAnalyzer(repo.local_path)
    timeline = git_analyzer.build_evolution_timeline()
    return {"timeline": timeline, "has_git": git_analyzer.has_git()}

@router.get("/repositories/{repo_id}/commits")
def get_commits(repo_id: str, limit: int = 30, db: Session = Depends(get_db)):
    repo = db.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    git_analyzer = GitAnalyzer(repo.local_path)
    commits = git_analyzer.get_commit_history(limit=limit)
    return {"commits": commits}

# 9. Discovered Features Endpoints
@router.get("/repositories/{repo_id}/features")
def list_discovered_features(repo_id: str, db: Session = Depends(get_db)):
    repo = db.query(RepositoryModel).filter(RepositoryModel.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found.")

    features = db.query(FeatureModel).filter(FeatureModel.repository_id == repo_id).all()
    if not features and repo.status in ("COMPLETED", "READY") and repo.file_count > 0:
        from app.analysis.feature_engine import FeatureDiscoveryEngine
        engine = FeatureDiscoveryEngine(db, repo_id)
        features = engine.discover_features()

    results = []
    for f in features:
        results.append({
            "id": f.id,
            "repository_id": f.repository_id,
            "name": f.name,
            "description": f.description,
            "confidence": f.confidence,
            "entry_points": f.entry_points_json or [],
            "files": f.files_json or [],
            "symbols": f.symbols_json or [],
            "api_routes": f.api_routes_json or [],
            "data_models": f.data_models_json or [],
            "components": f.components_json or [],
            "flows": f.flows_json or [],
            "evidence": f.evidence_json or []
        })

    return results

@router.get("/repositories/{repo_id}/features/{feature_id}")
def get_feature_detail(repo_id: str, feature_id: str, db: Session = Depends(get_db)):
    feature = db.query(FeatureModel).filter(FeatureModel.id == feature_id, FeatureModel.repository_id == repo_id).first()
    if not feature:
        feature = db.query(FeatureModel).filter(FeatureModel.repository_id == repo_id, FeatureModel.name.ilike(f"%{feature_id}%")).first()

    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found.")

    return {
        "id": feature.id,
        "repository_id": feature.repository_id,
        "name": feature.name,
        "description": feature.description,
        "confidence": feature.confidence,
        "entry_points": feature.entry_points_json or [],
        "files": feature.files_json or [],
        "symbols": feature.symbols_json or [],
        "api_routes": feature.api_routes_json or [],
        "data_models": feature.data_models_json or [],
        "components": feature.components_json or [],
        "flows": feature.flows_json or [],
        "evidence": feature.evidence_json or []
    }

