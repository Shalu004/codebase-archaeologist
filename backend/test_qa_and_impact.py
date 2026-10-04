import os
import sys

sys.path.insert(0, os.path.abspath("."))

from app.db.session import SessionLocal
from app.models.entities import (
    RepositoryModel, FileModel, SymbolModel, RouteModel, DBModelEntity, NodeModel, FeatureModel
)
from app.graph.builder import GraphBuilder
from app.git.analyzer import GitAnalyzer
from app.ai.llm_service import AIService

def clean_dict(obj):
    if not obj:
        return {}
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    return dict(obj)

def run():
    db = SessionLocal()
    try:
        repo = db.query(RepositoryModel).filter(RepositoryModel.name == "QueryGate").first()
        if not repo:
            print("QueryGate repo not found in DB!")
            return

        print(f"Loaded QueryGate repo ID: {repo.id}")

        files = [clean_dict(f) for f in db.query(FileModel).filter(FileModel.repository_id == repo.id).all()]
        symbols = [clean_dict(s) for s in db.query(SymbolModel).filter(SymbolModel.repository_id == repo.id).all()]
        routes = [clean_dict(r) for r in db.query(RouteModel).filter(RouteModel.repository_id == repo.id).all()]
        models = [clean_dict(m) for m in db.query(DBModelEntity).filter(DBModelEntity.repository_id == repo.id).all()]
        nodes = [clean_dict(n) for n in db.query(NodeModel).filter(NodeModel.repository_id == repo.id).all()]
        features = [clean_dict(f) for f in db.query(FeatureModel).filter(FeatureModel.repository_id == repo.id).all()]

        ai = AIService()

        questions = [
            "What is QueryGate and what problem does it solve?",
            "What are the main features of QueryGate?",
            "How does a database connection work?",
            "How does QueryGate execute SQL?",
            "How does QueryGate validate or restrict SQL?",
            "How does the MCP interface expose database functionality?",
            "Where is database schema information retrieved?",
            "Where is execute_sql implemented?",
            "What could be affected if execute_sql is changed?",
            "How has QueryGate evolved according to Git history?"
        ]

        print("\n==================================================")
        print("STEP 8: TEST ASK CODEBASE QUESTIONS")
        print("==================================================")

        for idx, q in enumerate(questions, 1):
            res = ai.ask_question(q, files, symbols, routes, models, nodes, features)
            print(f"\n--- Question {idx}: {q} ---")
            print(f"Summary: {res['summary']}")
            print(f"Confidence: {res['confidence']}")
            print("Evidence Citations:")
            for ev in res['evidence'][:3]:
                print(f"  * {ev['file_path']}:{ev.get('line_number', 1)} - {ev['symbol_name']}")

        print("\n==================================================")
        print("STEP 10: IMPACT ANALYSIS FOR execute_sql")
        print("==================================================")

        gb = GraphBuilder(db, repo.id)
        exec_node = db.query(NodeModel).filter(
            NodeModel.repository_id == repo.id,
            NodeModel.label.ilike("%executeSqlPipeline%")
        ).first()

        if not exec_node:
            exec_node = db.query(NodeModel).filter(
                NodeModel.repository_id == repo.id,
                NodeModel.file_path.ilike("%execute-sql%")
            ).first()

        if exec_node:
            impact = gb.get_impact_nodes(exec_node.id)
            print(f"Target Node: {impact['target']['label']} ({impact['target']['file_path']})")
            print(f"Direct Dependents: {len(impact['direct_dependents'])}")
            print(f"Indirect Dependents: {len(impact['indirect_dependents'])}")
            print(f"Affected Files: {impact['affected_files']}")
            print(f"Affected Symbols: {impact['affected_symbols']}")
            print(f"Impact Paths Count: {len(impact['impact_paths'])}")

        print("\n==================================================")
        print("STEP 11: GIT HISTORY ANALYSIS")
        print("==================================================")

        git_analyzer = GitAnalyzer(repo.local_path)
        commits = git_analyzer.get_commit_history(limit=10)
        print(f"Total Commits Retrieved: {len(commits)}")
        for c in commits[:5]:
            print(f"  * [{c['commit_hash'][:7]}] {c['message']} (Author: {c['author_name']}, Date: {c['timestamp']})")

    finally:
        db.close()

if __name__ == "__main__":
    run()
