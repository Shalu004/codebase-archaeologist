import pytest
from app.db.session import SessionLocal, init_db
from app.services.repo_service import RepositoryService
from app.graph.builder import GraphBuilder
from app.analysis.feature_engine import FeatureDiscoveryEngine
from app.models.entities import NodeModel, FeatureModel

def test_hierarchical_graph_levels():
    init_db()
    db = SessionLocal()
    try:
        service = RepositoryService(db)
        repo = service.create_from_github("https://github.com/something1703/kiet-innotech")
        service.run_analysis(repo.id)

        gb = GraphBuilder(db, repo.id)
        
        # Test Level 1 System View
        sys_g = gb.get_hierarchical_graph(level="system")
        assert len(sys_g["nodes"]) >= 3
        print(f"[TEST PASSED] System view nodes: {len(sys_g['nodes'])}, edges: {len(sys_g['edges'])}")

        # Test Level 2 Module View
        mod_g = gb.get_hierarchical_graph(level="module", target_module="client")
        assert len(mod_g["nodes"]) >= 1
        print(f"[TEST PASSED] Module view nodes: {len(mod_g['nodes'])}")

        # Test Impact Analysis with reverse traversal on actual node
        node = db.query(NodeModel).filter(NodeModel.repository_id == repo.id, NodeModel.node_type != "repository").first()
        assert node is not None
        impact = gb.get_impact_nodes(node.id)
        assert "direct_dependents" in impact
        assert "impact_paths" in impact
        print(f"[TEST PASSED] Impact analysis target: {impact['target']['label']}, total affected: {impact['total']}")

    finally:
        db.close()

def test_feature_discovery_engine():
    init_db()
    db = SessionLocal()
    try:
        service = RepositoryService(db)
        repo = service.create_from_github("https://github.com/something1703/kiet-innotech")
        service.run_analysis(repo.id)

        engine = FeatureDiscoveryEngine(db, repo.id)
        features = engine.discover_features()

        assert len(features) > 0, "Feature Discovery Engine should discover at least 1 feature candidate"
        print(f"\n[FEATURE DISCOVERY ENGINE REPORT] Total features discovered: {len(features)}")
        
        high_conf = [f for f in features if f.confidence == "HIGH"]
        med_conf = [f for f in features if f.confidence == "MEDIUM"]
        low_conf = [f for f in features if f.confidence == "LOW"]

        print(f"Confidence breakdown: HIGH={len(high_conf)}, MEDIUM={len(med_conf)}, LOW={len(low_conf)}")

        for idx, feat in enumerate(features[:5], 1):
            print(f"\n--- Feature Candidate #{idx}: {feat.name} (Confidence: {feat.confidence}) ---")
            print(f"Description: {feat.description}")
            print(f"Entry Points: {feat.entry_points_json}")
            print(f"APIs: {feat.api_routes_json}")
            print(f"Models: {feat.data_models_json}")
            print(f"Flow Steps ({len(feat.flows_json or [])}):")
            for step in feat.flows_json or []:
                print(f"  Step {step['step']} [{step['layer']}]: {step['symbol_name']} in {step['file_path']}:{step['line_number']}")

    finally:
        db.close()
