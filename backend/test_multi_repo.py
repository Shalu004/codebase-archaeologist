import os
import sys

sys.path.insert(0, os.path.abspath("."))

from app.db.session import SessionLocal, init_db
from app.services.repo_service import RepositoryService
from app.models.entities import RepositoryModel, FileModel, SymbolModel, FeatureModel
from app.ai.llm_service import AIService

def clean_dict(obj):
    if not obj:
        return {}
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    return dict(obj)

def run():
    init_db()
    db = SessionLocal()
    try:
        repos = db.query(RepositoryModel).filter(RepositoryModel.status == "COMPLETED").all()
        print(f"=== MULTI-REPOSITORY VALIDATION ===")
        print(f"Total Completed Repositories in DB: {len(repos)}")

        seen_names = set()
        unique_repos = []
        for r in repos:
            if r.name not in seen_names:
                seen_names.add(r.name)
                unique_repos.append(r)

        ai = AIService()

        for repo in unique_repos[:3]:
            print(f"\n--------------------------------------------------")
            print(f"Repository: {repo.name} ({repo.source_type})")
            print(f"ID: {repo.id}")
            print(f"Files: {repo.file_count}, Symbols: {repo.symbol_count}, Nodes: {repo.node_count}, Edges: {repo.edge_count}")

            files = [clean_dict(f) for f in db.query(FileModel).filter(FileModel.repository_id == repo.id).all()]
            symbols = [clean_dict(s) for s in db.query(SymbolModel).filter(SymbolModel.repository_id == repo.id).all()]
            features = db.query(FeatureModel).filter(FeatureModel.repository_id == repo.id).all()

            print(f"Discovered Features ({len(features)}):")
            for feat in features[:5]:
                print(f"  - {feat.name} ({feat.confidence}): {feat.description[:80]}...")

            ov = ai.generate_overview(repo.name, files, symbols, [], [], None)
            print(f"Purpose Overview: {ov.get('purpose')[:120]}...")

    finally:
        db.close()

if __name__ == "__main__":
    run()
