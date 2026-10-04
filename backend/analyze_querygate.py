import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath("."))

from app.db.session import SessionLocal, init_db
from app.services.repo_service import RepositoryService
from app.models.entities import (
    RepositoryModel, FileModel, SymbolModel, RouteModel, ApiCallModel, DBModelEntity, FeatureModel, NodeModel, EdgeModel
)
from app.graph.builder import GraphBuilder
from app.git.analyzer import GitAnalyzer
from app.analysis.feature_engine import FeatureDiscoveryEngine
from app.ai.llm_service import AIService

def run():
    init_db()
    db = SessionLocal()
    try:
        service = RepositoryService(db)
        querygate_path = os.path.abspath("C:/Users/musha/.gemini/antigravity-ide/scratch/querygate-repo")
        
        # Check if already ingested
        existing = db.query(RepositoryModel).filter(RepositoryModel.name == "QueryGate").first()
        if existing:
            db.delete(existing)
            db.commit()

        print("=== STEP 1 & 2: INGESTING QUERYGATE ===")
        repo = service.create_from_local_folder(querygate_path, "QueryGate")
        print(f"Created repository record ID={repo.id}, path={repo.local_path}")
        
        print("Running full analysis pipeline...")
        service.run_analysis(repo.id)
        db.refresh(repo)

        print("\n=== STEP 3: VERIFY INGESTION COUNTS ===")
        print(f"Status: {repo.status}")
        print(f"Scanned Files Count: {repo.file_count}")
        print(f"Extracted Symbols Count: {repo.symbol_count}")
        print(f"Graph Nodes Count: {repo.node_count}")
        print(f"Graph Edges Count: {repo.edge_count}")

        files = db.query(FileModel).filter(FileModel.repository_id == repo.id).all()
        symbols = db.query(SymbolModel).filter(SymbolModel.repository_id == repo.id).all()
        routes = db.query(RouteModel).filter(RouteModel.repository_id == repo.id).all()
        api_calls = db.query(ApiCallModel).filter(ApiCallModel.repository_id == repo.id).all()
        db_entities = db.query(DBModelEntity).filter(DBModelEntity.repository_id == repo.id).all()
        features = db.query(FeatureModel).filter(FeatureModel.repository_id == repo.id).all()

        print(f"Detected Routes: {len(routes)}")
        print(f"Detected API Calls: {len(api_calls)}")
        print(f"Detected Database Entities: {len(db_entities)}")
        print(f"Discovered Features: {len(features)}")

        # Print some file examples
        print("\nSample Scanned Files:")
        for f in files[:10]:
            print(f"  - {f.relative_path} ({f.language}, {f.line_count} lines)")

        # Print database entities
        print("\nSample Database Entities:")
        for db_e in db_entities:
            print(f"  - {db_e.name} ({db_e.model_type}) in {db_e.file_path}:{db_e.line_number}")

        # Print routes
        print("\nSample Routes / API Endpoints:")
        for r in routes:
            print(f"  - {r.method} {r.path} in {r.file_path}:{r.line_number}")

        # Print MCP / Tool related symbols
        print("\nSample MCP/Tool-related Symbols:")
        mcp_syms = [s for s in symbols if 'mcp' in s.name.lower() or 'tool' in s.name.lower() or 'sql' in s.name.lower() or 'execute' in s.name.lower()]
        for s in mcp_syms[:15]:
            print(f"  - {s.name} ({s.symbol_type}) in {s.file_path}:{s.start_line}")

        print("\n=== STEP 4 & 5: DISCOVERED FEATURES ===")
        for f in features:
            print(f"\nFeature: {f.name}")
            print(f"  Confidence: {f.confidence}")
            print(f"  Description: {f.description}")
            print(f"  Files: {f.files_json}")
            print(f"  Symbols: {f.symbols_json}")
            print(f"  Flows: {f.flows_json}")
            print(f"  Evidence: {f.evidence_json}")

    finally:
        db.close()

if __name__ == "__main__":
    run()
