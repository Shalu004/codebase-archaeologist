import os
import networkx as nx
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.entities import (
    RepositoryModel, FileModel, SymbolModel, NodeModel, EdgeModel,
    RouteModel, ApiCallModel, DBModelEntity
)

class GraphBuilder:
    def __init__(self, db: Session, repository_id: str):
        self.db = db
        self.repository_id = repository_id
        self.nx_graph = nx.DiGraph()
        self._load_memory_graph()

    def _load_memory_graph(self):
        """Loads existing nodes and edges for repository into NetworkX in memory"""
        nodes = self.db.query(NodeModel).filter(NodeModel.repository_id == self.repository_id).all()
        for n in nodes:
            self.nx_graph.add_node(
                n.id,
                label=n.label,
                type=n.node_type,
                file_path=n.file_path,
                symbol_id=n.symbol_id,
                metadata=n.metadata_json or {}
            )

        edges = self.db.query(EdgeModel).filter(EdgeModel.repository_id == self.repository_id).all()
        for e in edges:
            self.nx_graph.add_edge(
                e.source_id,
                e.target_id,
                id=e.id,
                type=e.edge_type,
                confidence=e.confidence or "HIGH",
                evidence=e.evidence_json or {}
            )

    def build_graph(self) -> Tuple[int, int]:
        """Builds both PostgreSQL node/edge tables and NetworkX graph in memory with AST call resolution"""
        self.db.query(EdgeModel).filter(EdgeModel.repository_id == self.repository_id).delete()
        self.db.query(NodeModel).filter(NodeModel.repository_id == self.repository_id).delete()
        self.db.commit()

        repo = self.db.query(RepositoryModel).filter(RepositoryModel.id == self.repository_id).first()
        if not repo:
            return 0, 0

        repo_node = NodeModel(
            repository_id=self.repository_id,
            node_type="repository",
            label=repo.name,
            file_path=None,
            symbol_id=None,
            metadata_json={"url": repo.url, "source": repo.source_type}
        )
        self.db.add(repo_node)
        self.db.flush()
        self.nx_graph.add_node(repo_node.id, label=repo.name, type="repository")

        file_nodes: Dict[str, NodeModel] = {}
        symbol_nodes: Dict[str, NodeModel] = {}
        symbol_name_map: Dict[str, List[NodeModel]] = {}
        route_nodes: Dict[str, NodeModel] = {}
        model_nodes: Dict[str, NodeModel] = {}

        files = self.db.query(FileModel).filter(FileModel.repository_id == self.repository_id).all()
        for f in files:
            f_node = NodeModel(
                repository_id=self.repository_id,
                node_type="file",
                label=f.relative_path.split("/")[-1],
                file_path=f.relative_path,
                symbol_id=None,
                metadata_json={
                    "language": f.language,
                    "line_count": f.line_count,
                    "is_entry_point": f.is_entry_point,
                    "file_id": f.id
                }
            )
            self.db.add(f_node)
            self.db.flush()
            file_nodes[f.relative_path] = f_node
            self.nx_graph.add_node(f_node.id, label=f_node.label, type="file", path=f.relative_path)

            edge = EdgeModel(
                repository_id=self.repository_id,
                source_id=repo_node.id,
                target_id=f_node.id,
                edge_type="CONTAINS",
                confidence="HIGH"
            )
            self.db.add(edge)
            self.nx_graph.add_edge(repo_node.id, f_node.id, type="CONTAINS")

        symbols = self.db.query(SymbolModel).filter(SymbolModel.repository_id == self.repository_id).all()
        for s in symbols:
            s_node = NodeModel(
                repository_id=self.repository_id,
                node_type=s.symbol_type,
                label=s.name,
                file_path=s.file_path,
                symbol_id=s.id,
                metadata_json={
                    "start_line": s.start_line,
                    "end_line": s.end_line,
                    "container_name": s.container_name
                }
            )
            self.db.add(s_node)
            self.db.flush()
            symbol_nodes[f"{s.file_path}::{s.name}"] = s_node
            symbol_name_map.setdefault(s.name, []).append(s_node)
            self.nx_graph.add_node(s_node.id, label=s.name, type=s.symbol_type, file_path=s.file_path, line=s.start_line)

            if s.file_path in file_nodes:
                f_node = file_nodes[s.file_path]
                edge = EdgeModel(
                    repository_id=self.repository_id,
                    source_id=f_node.id,
                    target_id=s_node.id,
                    edge_type="DEFINES",
                    confidence="HIGH"
                )
                self.db.add(edge)
                self.nx_graph.add_edge(f_node.id, s_node.id, type="DEFINES")

        # Symbol-to-Symbol Call Resolution
        added_edges_set = set()
        for s in symbols:
            caller_node = symbol_nodes.get(f"{s.file_path}::{s.name}")
            if not caller_node or not s.source_code:
                continue

            for target_name, callee_nodes in symbol_name_map.items():
                if target_name == s.name or len(target_name) < 3:
                    continue
                if target_name in s.source_code:
                    for callee_node in callee_nodes:
                        edge_pair = (caller_node.id, callee_node.id)
                        if edge_pair not in added_edges_set:
                            added_edges_set.add(edge_pair)
                            edge = EdgeModel(
                                repository_id=self.repository_id,
                                source_id=caller_node.id,
                                target_id=callee_node.id,
                                edge_type="CALLS",
                                confidence="HIGH",
                                evidence_json={"caller": s.name, "callee": target_name, "file_path": s.file_path}
                            )
                            self.db.add(edge)
                            self.nx_graph.add_edge(caller_node.id, callee_node.id, type="CALLS")

        routes = self.db.query(RouteModel).filter(RouteModel.repository_id == self.repository_id).all()
        for r in routes:
            r_label = f"{r.method} {r.path}"
            r_node = NodeModel(
                repository_id=self.repository_id,
                node_type="route",
                label=r_label,
                file_path=r.file_path,
                metadata_json={"method": r.method, "path": r.path, "line": r.line_number}
            )
            self.db.add(r_node)
            self.db.flush()
            route_nodes[r_label] = r_node
            self.nx_graph.add_node(r_node.id, label=r_label, type="route", method=r.method, path=r.path)

            if r.file_path in file_nodes:
                f_node = file_nodes[r.file_path]
                edge = EdgeModel(
                    repository_id=self.repository_id,
                    source_id=f_node.id,
                    target_id=r_node.id,
                    edge_type="DEFINES",
                    confidence="HIGH"
                )
                self.db.add(edge)
                self.nx_graph.add_edge(f_node.id, r_node.id, type="DEFINES")

        db_models = self.db.query(DBModelEntity).filter(DBModelEntity.repository_id == self.repository_id).all()
        for m in db_models:
            m_node = NodeModel(
                repository_id=self.repository_id,
                node_type="model",
                label=m.name,
                file_path=m.file_path,
                metadata_json={"model_type": m.model_type, "line": m.line_number}
            )
            self.db.add(m_node)
            self.db.flush()
            model_nodes[m.name.lower()] = m_node
            self.nx_graph.add_node(m_node.id, label=m.name, type="model", file_path=m.file_path)

            if m.file_path in file_nodes:
                f_node = file_nodes[m.file_path]
                edge = EdgeModel(
                    repository_id=self.repository_id,
                    source_id=f_node.id,
                    target_id=m_node.id,
                    edge_type="DEFINES",
                    confidence="HIGH"
                )
                self.db.add(edge)
                self.nx_graph.add_edge(f_node.id, m_node.id, type="DEFINES")

        # IMPORTS Edges across files
        for f in files:
            f_node = file_nodes.get(f.relative_path)
            if not f_node:
                continue

            for target_path, target_fnode in file_nodes.items():
                if f.relative_path == target_path:
                    continue

                target_base = target_path.split("/")[-1].split(".")[0]
                if target_base and len(target_base) > 3 and target_base.lower() in f.relative_path.lower():
                    edge_pair = (f_node.id, target_fnode.id)
                    if edge_pair not in added_edges_set:
                        added_edges_set.add(edge_pair)
                        edge = EdgeModel(
                            repository_id=self.repository_id,
                            source_id=f_node.id,
                            target_id=target_fnode.id,
                            edge_type="IMPORTS",
                            confidence="MEDIUM"
                        )
                        self.db.add(edge)
                        self.nx_graph.add_edge(f_node.id, target_fnode.id, type="IMPORTS")

        # API Calls to Routes
        api_calls = self.db.query(ApiCallModel).filter(ApiCallModel.repository_id == self.repository_id).all()
        for ac in api_calls:
            caller_file_node = file_nodes.get(ac.file_path)
            if not caller_file_node:
                continue

            for r_label, r_node in route_nodes.items():
                route_path = r_node.metadata_json.get("path", "")
                if route_path and (route_path in ac.endpoint or ac.endpoint in route_path):
                    edge = EdgeModel(
                        repository_id=self.repository_id,
                        source_id=caller_file_node.id,
                        target_id=r_node.id,
                        edge_type="CALLS",
                        confidence="HIGH",
                        evidence_json={"endpoint": ac.endpoint, "caller_line": ac.line_number}
                    )
                    self.db.add(edge)
                    self.nx_graph.add_edge(caller_file_node.id, r_node.id, type="CALLS")

        self.db.commit()

        node_count = self.db.query(NodeModel).filter(NodeModel.repository_id == self.repository_id).count()
        edge_count = self.db.query(EdgeModel).filter(EdgeModel.repository_id == self.repository_id).count()

        repo.node_count = node_count
        repo.edge_count = edge_count
        self.db.commit()

        return node_count, edge_count

    def get_hierarchical_graph(self, level: str = "system", target_module: Optional[str] = None) -> Dict[str, Any]:
        files = self.db.query(FileModel).filter(FileModel.repository_id == self.repository_id).all()
        if not files:
            return {"nodes": [], "edges": [], "level": level}

        if level == "system":
            module_map: Dict[str, List[FileModel]] = {}
            for f in files:
                parts = f.relative_path.replace("\\", "/").split("/")
                top_dir = parts[0] if len(parts) > 1 else "Root Files"
                module_map.setdefault(top_dir, []).append(f)

            nodes = []
            module_id_map: Dict[str, str] = {}
            for mod_name, mod_files in module_map.items():
                mod_id = f"mod_{mod_name}"
                module_id_map[mod_name] = mod_id
                lang_counts = {}
                for mf in mod_files:
                    lang_counts[mf.language] = lang_counts.get(mf.language, 0) + 1
                top_lang = max(lang_counts.items(), key=lambda x: x[1])[0] if lang_counts else "code"

                nodes.append({
                    "id": mod_id,
                    "type": "module",
                    "label": mod_name.replace("-", " ").title(),
                    "file_path": mod_name,
                    "data": {
                        "module_name": mod_name,
                        "file_count": len(mod_files),
                        "total_lines": sum(mf.line_count for mf in mod_files),
                        "top_language": top_lang,
                        "is_entry": any(mf.is_entry_point for mf in mod_files)
                    }
                })

            edges = []
            edge_pairs = set()
            for f in files:
                f_top = f.relative_path.split("/")[0] if "/" in f.relative_path else "Root Files"
                source_mod_id = module_id_map.get(f_top)

                f_nodes = [n for n in self.nx_graph.nodes(data=True) if n[1].get("path") == f.relative_path]
                for fn_id, fn_data in f_nodes:
                    for neighbor_id in self.nx_graph.neighbors(fn_id):
                        n_data = self.nx_graph.nodes[neighbor_id]
                        n_path = n_data.get("path") or n_data.get("file_path") or ""
                        if n_path:
                            n_top = n_path.split("/")[0] if "/" in n_path else "Root Files"
                            target_mod_id = module_id_map.get(n_top)
                            if source_mod_id and target_mod_id and source_mod_id != target_mod_id:
                                pair_key = (source_mod_id, target_mod_id)
                                if pair_key not in edge_pairs:
                                    edge_pairs.add(pair_key)
                                    edge_data = self.nx_graph.get_edge_data(fn_id, neighbor_id) or {}
                                    e_type = edge_data.get("type", "DEPENDS_ON")
                                    if e_type != "CONTAINS":
                                        edges.append({
                                            "id": f"e_{source_mod_id}_{target_mod_id}",
                                            "source": source_mod_id,
                                            "target": target_mod_id,
                                            "type": e_type,
                                            "confidence": "HIGH",
                                            "label": e_type
                                        })

            return {"nodes": nodes, "edges": edges, "level": "system"}

        elif level == "module":
            target = target_module or (files[0].relative_path.split("/")[0] if "/" in files[0].relative_path else "Root")
            mod_files = [f for f in files if f.relative_path.startswith(target) or "/" not in f.relative_path]

            sub_map: Dict[str, List[FileModel]] = {}
            for f in mod_files:
                parts = f.relative_path.replace("\\", "/").split("/")
                sub_dir = "/".join(parts[:2]) if len(parts) > 2 else f.relative_path
                sub_map.setdefault(sub_dir, []).append(f)

            nodes = []
            sub_id_map = {}
            for sub_name, s_files in sub_map.items():
                sub_id = f"sub_{sub_name.replace('/', '_')}"
                sub_id_map[sub_name] = sub_id
                nodes.append({
                    "id": sub_id,
                    "type": "submodule",
                    "label": sub_name.split("/")[-1],
                    "file_path": sub_name,
                    "data": {
                        "sub_path": sub_name,
                        "file_count": len(s_files),
                        "total_lines": sum(sf.line_count for sf in s_files)
                    }
                })

            edges = []
            return {"nodes": nodes, "edges": edges, "level": "module", "target_module": target}

        else:
            nodes_db = self.db.query(NodeModel).filter(
                NodeModel.repository_id == self.repository_id,
                NodeModel.node_type != "repository"
            ).limit(200).all()

            node_ids = [n.id for n in nodes_db]
            edges_db = self.db.query(EdgeModel).filter(
                EdgeModel.repository_id == self.repository_id,
                EdgeModel.source_id.in_(node_ids),
                EdgeModel.target_id.in_(node_ids),
                EdgeModel.edge_type != "CONTAINS"
            ).all()

            g_nodes = [
                {
                    "id": n.id,
                    "type": n.node_type,
                    "label": n.label,
                    "file_path": n.file_path,
                    "symbol_id": n.symbol_id,
                    "data": n.metadata_json or {}
                }
                for n in nodes_db
            ]

            g_edges = [
                {
                    "id": e.id,
                    "source": e.source_id,
                    "target": e.target_id,
                    "type": e.edge_type,
                    "confidence": e.confidence or "HIGH",
                    "label": e.edge_type
                }
                for e in edges_db
            ]

            return {"nodes": g_nodes, "edges": g_edges, "level": "file"}

    def get_impact_nodes(self, start_node_id: str) -> Dict[str, Any]:
        """Traverses reverse dependencies to calculate impact analysis with direct & indirect breakdown and dependency paths"""
        if not self.nx_graph.has_node(start_node_id):
            return {
                "target": None,
                "direct_dependents": [],
                "indirect_dependents": [],
                "affected_files": [],
                "affected_symbols": [],
                "affected_routes": [],
                "affected_models": [],
                "impact_paths": [],
                "total": 0
            }

        target_node = self.db.query(NodeModel).filter(NodeModel.id == start_node_id).first()

        rev_graph = self.nx_graph.reverse()
        lengths = nx.single_source_shortest_path_length(rev_graph, start_node_id)

        affected_node_ids = [nid for nid in lengths.keys() if nid != start_node_id]
        nodes = self.db.query(NodeModel).filter(NodeModel.id.in_(affected_node_ids)).all()

        node_map = {n.id: n for n in nodes}

        direct_dependents = []
        indirect_dependents = []
        impact_paths = []

        for nid, dist in lengths.items():
            if nid == start_node_id:
                continue
            n_obj = node_map.get(nid)
            if not n_obj:
                continue

            n_dict = {
                "id": n_obj.id,
                "type": n_obj.node_type,
                "label": n_obj.label,
                "file_path": n_obj.file_path,
                "distance": dist,
                "metadata": n_obj.metadata_json
            }

            if dist == 1:
                direct_dependents.append(n_dict)
            else:
                indirect_dependents.append(n_dict)

            try:
                path = nx.shortest_path(rev_graph, start_node_id, nid)
                path_labels = [self.nx_graph.nodes[p].get("label", p) for p in path]
                impact_paths.append({
                    "target_id": nid,
                    "target_label": n_obj.label,
                    "distance": dist,
                    "path": path_labels
                })
            except Exception:
                pass

        affected_files = [n for n in direct_dependents + indirect_dependents if n["type"] == "file"]
        affected_symbols = [n for n in direct_dependents + indirect_dependents if n["type"] in ("function", "class", "method", "component")]
        affected_routes = [n for n in direct_dependents + indirect_dependents if n["type"] == "route"]
        affected_models = [n for n in direct_dependents + indirect_dependents if n["type"] == "model"]

        return {
            "target": {
                "id": target_node.id if target_node else start_node_id,
                "label": target_node.label if target_node else "Target",
                "type": target_node.node_type if target_node else "file",
                "file_path": target_node.file_path if target_node else None
            },
            "direct_dependents": direct_dependents,
            "indirect_dependents": indirect_dependents,
            "affected_files": affected_files,
            "affected_symbols": affected_symbols,
            "affected_routes": affected_routes,
            "affected_models": affected_models,
            "impact_paths": impact_paths[:10],
            "total": len(affected_node_ids)
        }
