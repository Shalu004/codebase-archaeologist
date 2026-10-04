import os
import re
from typing import List, Dict, Any, Optional, Set
from sqlalchemy.orm import Session
from app.models.entities import (
    RepositoryModel, FileModel, SymbolModel, NodeModel, EdgeModel,
    RouteModel, ApiCallModel, DBModelEntity, FeatureModel
)

class FeatureDiscoveryEngine:
    def __init__(self, db: Session, repository_id: str):
        self.db = db
        self.repository_id = repository_id

    def discover_features(self) -> List[FeatureModel]:
        """
        Discovers evidence-backed feature candidates from source code, AST symbols, API calls, routes, MCP tools, and DB models.
        """
        # Clear old features for this repository
        self.db.query(FeatureModel).filter(FeatureModel.repository_id == self.repository_id).delete()
        self.db.commit()

        repo = self.db.query(RepositoryModel).filter(RepositoryModel.id == self.repository_id).first()
        if not repo or repo.file_count == 0:
            return []

        files = self.db.query(FileModel).filter(FileModel.repository_id == self.repository_id).all()
        symbols = self.db.query(SymbolModel).filter(SymbolModel.repository_id == self.repository_id).all()
        routes = self.db.query(RouteModel).filter(RouteModel.repository_id == self.repository_id).all()
        api_calls = self.db.query(ApiCallModel).filter(ApiCallModel.repository_id == self.repository_id).all()
        db_models = self.db.query(DBModelEntity).filter(DBModelEntity.repository_id == self.repository_id).all()

        domain_tokens: Set[str] = set()

        # Extract tokens from routes
        for r in routes:
            parts = [p.lower() for p in re.split(r'[/_.-]', r.path) if p and p.lower() not in ('api', 'v1', 'v2', 'route')]
            for p in parts:
                if len(p) > 2 and not p.isdigit():
                    domain_tokens.add(p)

        # Extract tokens from DB entities
        for m in db_models:
            m_name = m.name.lower()
            if len(m_name) > 2:
                domain_tokens.add(m_name)

        # Extract tokens from files & symbols (including tools, security, db, session, http, mcp)
        for f in files:
            path_lower = f.relative_path.lower()
            parts = [p.lower() for p in re.split(r'[/_.-]', f.relative_path) if p]
            for p in parts:
                if p in ('tools', 'security', 'db', 'executor', 'validator', 'pii', 'pipeline', 'session', 'rate-limit', 'connection', 'mcp', 'server', 'http', 'analytics', 'schema'):
                    domain_tokens.add(p)
                elif len(p) > 3 and p not in ('index', 'page', 'route', 'service', 'controller', 'component', 'ts', 'tsx', 'js', 'jsx', 'json'):
                    domain_tokens.add(p)

        # Consolidate candidate feature groups
        feature_configs = [
            {
                "id": "sql-execution",
                "name": "SQL Execution Pipeline",
                "tokens": ["execute", "query", "pipeline", "executor"],
                "file_keywords": ["execute-sql", "query", "executor"],
                "symbol_keywords": ["executeSqlPipeline", "executeQuery", "query"],
                "desc": "Validates, executes, caches, and masks PII for database queries."
            },
            {
                "id": "sql-safety",
                "name": "SQL Safety & Validation Engine",
                "tokens": ["security", "validator", "validation", "safety"],
                "file_keywords": ["security", "validator", "sanitizer"],
                "symbol_keywords": ["validateSql", "tickRateLimit", "block"],
                "desc": "Parses SQL AST, enforces read-only mode, blocks DDL mutations, and validates table permissions."
            },
            {
                "id": "pii-protection",
                "name": "PII Protection & Data Masking",
                "tokens": ["pii", "mask", "masking"],
                "file_keywords": ["pii", "detector", "masker"],
                "symbol_keywords": ["maskIfPii", "detectPii", "piiRisk"],
                "desc": "Scans result columns for sensitive PII data and automatically masks sensitive values."
            },
            {
                "id": "mcp-interface",
                "name": "MCP Server Interface & Tools",
                "tokens": ["mcp", "tool", "tools", "registry"],
                "file_keywords": ["server", "tools", "registry", "mcp"],
                "symbol_keywords": ["createMcpServer", "runTool", "getToolByName", "dispatchMcp"],
                "desc": "Exposes model context protocol (MCP) endpoints and registers executable database tools."
            },
            {
                "id": "db-connection",
                "name": "Database Connection Management",
                "tokens": ["connection", "connector", "store", "pool"],
                "file_keywords": ["connection", "connector", "store", "db"],
                "symbol_keywords": ["getOrCreatePool", "ConnectionStore", "resolveDatabaseUrl"],
                "desc": "Manages connection pools, JWT connection tokens, and dynamic database credentials."
            },
            {
                "id": "schema-inspection",
                "name": "Schema Inspection Tools",
                "tokens": ["schema", "table", "tables", "sample"],
                "file_keywords": ["schema", "tables", "sample"],
                "symbol_keywords": ["getTables", "getSchema", "sampleRows"],
                "desc": "Provides database metadata, table lists, schema inspection, and sample data."
            },
            {
                "id": "session-rate-limiting",
                "name": "Session & Rate Limiting Engine",
                "tokens": ["session", "rate-limit", "limiter"],
                "file_keywords": ["session", "rate-limit", "limiter", "manager"],
                "symbol_keywords": ["getRateLimit", "tickRateLimit", "resolveSessionForTool"],
                "desc": "Manages active user sessions, per-session caches, and rate-limiting limits."
            }
        ]

        feature_models: List[FeatureModel] = []
        processed_feature_ids: Set[str] = set()

        for config in feature_configs:
            matching_files = [
                f for f in files 
                if any(kw in f.relative_path.lower() for kw in config["file_keywords"])
            ]
            matching_symbols = [
                s for s in symbols 
                if any(kw in s.name.lower() or kw in s.file_path.lower() for kw in config["symbol_keywords"])
            ]
            matching_routes = [
                r for r in routes 
                if any(kw in r.path.lower() or kw in r.file_path.lower() for kw in config["tokens"])
            ]
            matching_models = [
                m for m in db_models 
                if any(kw in m.name.lower() or kw in m.file_path.lower() for kw in config["tokens"])
            ]

            if not matching_files and not matching_symbols:
                continue

            processed_feature_ids.add(config["id"])

            # Build evidence flow steps
            flows: List[Dict[str, Any]] = []
            step_num = 1

            # Step 1: Entry Point (MCP Tool or Route)
            entry_sym = next((s for s in matching_symbols if 'tool' in s.name.lower() or 'server' in s.file_path.lower() or 'mcp' in s.file_path.lower()), matching_symbols[0] if matching_symbols else None)
            if entry_sym:
                flows.append({
                    "step": step_num,
                    "layer": "MCP_TOOL",
                    "file_path": entry_sym.file_path,
                    "symbol_name": entry_sym.name,
                    "line_number": entry_sym.start_line,
                    "snippet": entry_sym.source_code[:150] if entry_sym.source_code else f"MCP entrypoint {entry_sym.name}()",
                    "explanation": f"MCP Client invokes tool or request entry point {entry_sym.name}."
                })
                step_num += 1

            # Step 2: Validation / Core Logic
            val_sym = next((s for s in symbols if 'validate' in s.name.lower() or 'check' in s.name.lower() or 'ensure' in s.name.lower()), None)
            if val_sym and val_sym.file_path != (entry_sym.file_path if entry_sym else ""):
                flows.append({
                    "step": step_num,
                    "layer": "VALIDATION",
                    "file_path": val_sym.file_path,
                    "symbol_name": val_sym.name,
                    "line_number": val_sym.start_line,
                    "snippet": val_sym.source_code[:150] if val_sym.source_code else f"validateSql()",
                    "explanation": "Security engine validates SQL AST, permissions, and safety rules."
                })
                step_num += 1

            # Step 3: Database Execution Layer
            db_sym = next((s for s in symbols if 'execute' in s.name.lower() or 'pool' in s.name.lower() or 'query' in s.name.lower()), None)
            if db_sym and db_sym.file_path != (entry_sym.file_path if entry_sym else ""):
                flows.append({
                    "step": step_num,
                    "layer": "DATABASE_EXECUTION",
                    "file_path": db_sym.file_path,
                    "symbol_name": db_sym.name,
                    "line_number": db_sym.start_line,
                    "snippet": db_sym.source_code[:150] if db_sym.source_code else f"executeQuery()",
                    "explanation": "Database executor dispatches query to PostgreSQL connection pool."
                })
                step_num += 1

            # Step 4: Masking / Result Formatting
            mask_sym = next((s for s in symbols if 'pii' in s.name.lower() or 'mask' in s.name.lower()), None)
            if mask_sym:
                flows.append({
                    "step": step_num,
                    "layer": "DATA_PROTECTION",
                    "file_path": mask_sym.file_path,
                    "symbol_name": mask_sym.name,
                    "line_number": mask_sym.start_line,
                    "snippet": mask_sym.source_code[:150] if mask_sym.source_code else f"maskIfPii()",
                    "explanation": "PII engine masks sensitive columns before returning payload to MCP client."
                })
                step_num += 1

            confidence = "HIGH" if len(flows) >= 3 else ("MEDIUM" if len(flows) >= 2 else "LOW")

            evidence = []
            for f_item in flows:
                evidence.append({
                    "file_path": f_item["file_path"],
                    "line_number": f_item["line_number"],
                    "symbol_name": f_item["symbol_name"],
                    "snippet": f_item["snippet"],
                    "relationship": f"DEFINES_{f_item['layer']}"
                })

            for m_sym in matching_symbols[:5]:
                if not any(e["symbol_name"] == m_sym.name for e in evidence):
                    evidence.append({
                        "file_path": m_sym.file_path,
                        "line_number": m_sym.start_line,
                        "symbol_name": m_sym.name,
                        "snippet": m_sym.source_code[:120] if m_sym.source_code else f"Symbol {m_sym.name}",
                        "relationship": "IMPLEMENTS_SYMBOL"
                    })

            feat_obj = FeatureModel(
                repository_id=self.repository_id,
                name=config["name"],
                description=config["desc"],
                confidence=confidence,
                entry_points_json=[f.relative_path for f in matching_files if f.is_entry_point or 'server' in f.relative_path.lower() or 'index' in f.relative_path.lower()][:3],
                files_json=list(set(f.relative_path for f in matching_files))[:15],
                symbols_json=list(set(s.name for s in matching_symbols))[:15],
                api_routes_json=list(set(f"{r.method} {r.path}" for r in matching_routes))[:10],
                data_models_json=list(set(m.name for m in matching_models))[:5],
                components_json=[s.name for s in matching_symbols if s.symbol_type == 'component'][:10],
                flows_json=flows,
                evidence_json=evidence[:15]
            )

            self.db.add(feat_obj)
            feature_models.append(feat_obj)

        self.db.commit()
        return feature_models
