import os
import shutil
import zipfile
import tempfile
import logging
import git
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.entities import (
    RepositoryModel, FileModel, SymbolModel, RouteModel, ApiCallModel, DBModelEntity, AnalysisRunModel
)
from app.parser.scanner import FileScanner
from app.parser.ast_parser import CodeASTParser
from app.graph.builder import GraphBuilder
from app.git.analyzer import GitAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("codebase_archaeologist")

class RepositoryService:
    def __init__(self, db: Session):
        self.db = db

    def validate_github_url(self, github_url: str) -> bool:
        """Verify that the GitHub repository exists and is publicly accessible"""
        try:
            g = git.cmd.Git()
            # Perform quick remote head inspection (timeout handling)
            g.ls_remote(github_url, heads=True)
            return True
        except Exception as e:
            logger.warning(f"[INGEST] Invalid or inaccessible GitHub repository URL: {github_url} error={str(e)}")
            return False

    def create_from_github(self, github_url: str, default_branch: str = "main") -> RepositoryModel:
        if not self.validate_github_url(github_url):
            raise ValueError(f"Invalid or inaccessible GitHub repository URL: '{github_url}'")

        clean_url = github_url.rstrip("/").replace(".git", "")
        repo_name = clean_url.split("/")[-1] or "repository"

        repo = RepositoryModel(
            name=repo_name,
            url=github_url,
            source_type="github",
            local_path="",
            default_branch=default_branch,
            status="QUEUED"
        )
        self.db.add(repo)
        self.db.commit()
        self.db.refresh(repo)

        storage_dir = os.path.abspath(os.path.join(settings.REPO_STORAGE_DIR, repo.id))
        repo.local_path = storage_dir
        self.db.commit()

        logger.info(f"[INGEST] GitHub URL validated & received: {github_url} (Repo ID: {repo.id})")
        return repo


    def create_from_zip(self, zip_file_bytes: bytes, filename: str) -> RepositoryModel:
        repo_name = os.path.splitext(filename)[0] or "zip_repository"

        repo = RepositoryModel(
            name=repo_name,
            url=None,
            source_type="zip",
            local_path="",
            status="QUEUED"
        )
        self.db.add(repo)
        self.db.commit()
        self.db.refresh(repo)

        storage_dir = os.path.abspath(os.path.join(settings.REPO_STORAGE_DIR, repo.id))
        os.makedirs(storage_dir, exist_ok=True)
        repo.local_path = storage_dir

        zip_path = os.path.join(storage_dir, "upload.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_file_bytes)

        self._safe_extract_zip(zip_path, storage_dir)
        self.db.commit()

        logger.info(f"[INGEST] ZIP archive received and extracted: {filename} (Repo ID: {repo.id})")
        return repo

    def create_from_local_folder(self, folder_path: str, name: str) -> RepositoryModel:
        repo = RepositoryModel(
            name=name,
            url=None,
            source_type="local",
            local_path=os.path.abspath(folder_path),
            status="QUEUED"
        )
        self.db.add(repo)
        self.db.commit()
        self.db.refresh(repo)
        return repo

    def run_analysis(self, repository_id: str):
        """Asynchronous analysis pipeline with explicit lifecycle states and zero-data sanity checks"""
        repo = self.db.query(RepositoryModel).filter(RepositoryModel.id == repository_id).first()
        if not repo:
            logger.error(f"[ANALYSIS] Repository ID {repository_id} not found.")
            return

        analysis_run = AnalysisRunModel(
            repository_id=repo.id,
            status="RUNNING",
            current_step="INITIALIZING",
            step_progress=5
        )
        self.db.add(analysis_run)
        self.db.commit()

        try:
            # Stage 1: GitHub Clone Ingestion
            if repo.source_type == "github":
                repo.status = "CLONING"
                analysis_run.current_step = "CLONING_REPOSITORY"
                analysis_run.step_progress = 15
                self.db.commit()

                if not os.path.exists(os.path.join(repo.local_path, ".git")):
                    if os.path.exists(repo.local_path):
                        shutil.rmtree(repo.local_path, ignore_errors=True)
                    os.makedirs(os.path.dirname(repo.local_path), exist_ok=True)

                    logger.info(f"[INGEST] Repository clone started url={repo.url} path={repo.local_path}")
                    try:
                        cloned = git.Repo.clone_from(repo.url, repo.local_path, depth=50)
                        try:
                            branch_name = cloned.active_branch.name
                        except Exception:
                            branch_name = "HEAD"
                        commit_sha = cloned.head.commit.hexsha
                        repo.default_branch = branch_name
                        repo.commit_sha = commit_sha
                        self.db.commit()
                        logger.info(f"[INGEST] Repository clone completed path={repo.local_path} commit_sha={commit_sha} branch={branch_name}")
                    except Exception as e:
                        err_text = f"Failed to clone GitHub repository '{repo.url}': {str(e)}"
                        logger.error(f"[INGEST] FAILED: {err_text}")
                        repo.status = "FAILED"
                        repo.error_message = err_text
                        analysis_run.status = "FAILED"
                        analysis_run.error_log = err_text
                        self.db.commit()
                        return

            # Stage 2: File Scanner & Working Directory Inspection
            repo.status = "SCANNING"
            analysis_run.current_step = "SCANNING_FILES"
            analysis_run.step_progress = 30
            self.db.commit()

            logger.info(f"[SCAN] Scanning repository path={repo.local_path}")
            scanner = FileScanner(repo.local_path)
            scanned_files = scanner.scan()

            logger.info(f"[SCAN] files_found={len(scanned_files)} at path={repo.local_path}")

            # SANITY CHECK: Verify actual analyzable files exist on disk!
            if len(scanned_files) == 0:
                err_text = "Repository was obtained but no analyzable source files were found."
                logger.error(f"[SCAN] FAILED: {err_text}")
                repo.status = "FAILED"
                repo.error_message = err_text
                analysis_run.status = "FAILED"
                analysis_run.error_log = err_text
                self.db.commit()
                return

            # Clear existing analysis metadata for clean re-runs
            self.db.query(FileModel).filter(FileModel.repository_id == repo.id).delete()
            self.db.query(SymbolModel).filter(SymbolModel.repository_id == repo.id).delete()
            self.db.query(RouteModel).filter(RouteModel.repository_id == repo.id).delete()
            self.db.query(ApiCallModel).filter(ApiCallModel.repository_id == repo.id).delete()
            self.db.query(DBModelEntity).filter(DBModelEntity.repository_id == repo.id).delete()
            self.db.commit()

            file_records: Dict[str, FileModel] = {}
            for sf in scanned_files:
                f_record = FileModel(
                    repository_id=repo.id,
                    relative_path=sf["relative_path"],
                    extension=sf["extension"],
                    language=sf["language"],
                    size_bytes=sf["size_bytes"],
                    line_count=sf["line_count"],
                    file_hash=sf["file_hash"],
                    is_entry_point=sf["is_entry_point"]
                )
                self.db.add(f_record)
                self.db.flush()
                file_records[sf["relative_path"]] = f_record

            repo.file_count = len(file_records)
            self.db.commit()

            # Stage 3: AST Parsing
            repo.status = "PARSING"
            analysis_run.current_step = "PARSING_AST"
            analysis_run.step_progress = 60
            self.db.commit()

            parser = CodeASTParser()
            symbol_count = 0
            parsed_files_count = 0

            for sf in scanned_files:
                parse_res = parser.parse_file(sf["relative_path"], sf["content"])
                parsed_files_count += 1
                f_record = file_records.get(sf["relative_path"])

                for sym in parse_res["symbols"]:
                    s_entity = SymbolModel(
                        repository_id=repo.id,
                        file_id=f_record.id if f_record else "",
                        file_path=sym["file_path"],
                        symbol_type=sym["symbol_type"],
                        name=sym["name"],
                        container_name=sym["container_name"],
                        start_line=sym["start_line"],
                        end_line=sym["end_line"],
                        start_column=sym["start_column"],
                        end_column=sym["end_column"],
                        source_code=sym["source_code"],
                        extra_metadata=sym["extra_metadata"]
                    )
                    self.db.add(s_entity)
                    symbol_count += 1

                for r in parse_res["routes"]:
                    r_entity = RouteModel(
                        repository_id=repo.id,
                        path=r["path"],
                        method=r["method"],
                        file_path=r["file_path"],
                        line_number=r["line"]
                    )
                    self.db.add(r_entity)

                for ac in parse_res["api_calls"]:
                    ac_entity = ApiCallModel(
                        repository_id=repo.id,
                        endpoint=ac["endpoint"],
                        method=ac["method"],
                        file_path=ac["file_path"],
                        line_number=ac["line"]
                    )
                    self.db.add(ac_entity)

                for db_m in parse_res["db_models"]:
                    db_entity = DBModelEntity(
                        repository_id=repo.id,
                        name=db_m["name"],
                        model_type=db_m["model_type"],
                        file_path=db_m["file_path"],
                        line_number=db_m["line"]
                    )
                    self.db.add(db_entity)

            repo.symbol_count = symbol_count
            self.db.commit()
            logger.info(f"[PARSER] files_parsed={parsed_files_count} symbols_extracted={symbol_count}")

            # Stage 4: Code Graph Building
            repo.status = "BUILDING_GRAPH"
            analysis_run.current_step = "BUILDING_GRAPH"
            analysis_run.step_progress = 85
            self.db.commit()

            gb = GraphBuilder(self.db, repo.id)
            node_cnt, edge_cnt = gb.build_graph()
            logger.info(f"[GRAPH] nodes_created={node_cnt} edges_created={edge_cnt}")

            # Stage 5: Feature Discovery & Generating Insights
            repo.status = "GENERATING_INSIGHTS"
            analysis_run.current_step = "GENERATING_INSIGHTS"
            analysis_run.step_progress = 95
            self.db.commit()

            from app.analysis.feature_engine import FeatureDiscoveryEngine
            feature_engine = FeatureDiscoveryEngine(self.db, repo.id)
            features = feature_engine.discover_features()
            logger.info(f"[FEATURE_ENGINE] Discovered {len(features)} features for repo={repo.name}")

            # Mark Completed
            repo.status = "COMPLETED"
            repo.node_count = node_cnt
            repo.edge_count = edge_cnt
            analysis_run.status = "COMPLETED"
            analysis_run.current_step = "COMPLETED"
            analysis_run.step_progress = 100
            self.db.commit()

            logger.info(f"[ANALYSIS] Analysis completed for repo={repo.id} ({repo.name}) status=COMPLETED files={repo.file_count} symbols={symbol_count} nodes={node_cnt} edges={edge_cnt}")

        except Exception as e:
            err_text = f"Analysis failed: {str(e)}"
            logger.error(f"[ANALYSIS] FAILED: {err_text}")
            repo.status = "FAILED"
            repo.error_message = err_text
            analysis_run.status = "FAILED"
            analysis_run.error_log = err_text
            self.db.commit()

    def _safe_extract_zip(self, zip_path: str, extract_to: str):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                target_path = os.path.abspath(os.path.join(extract_to, member.filename))
                if not target_path.startswith(os.path.abspath(extract_to)):
                    raise ValueError(f"Path traversal detected in zip file: {member.filename}")
            zip_ref.extractall(extract_to)

def run_analysis_task(repository_id: str):
    """Background task wrapper with isolated database session"""
    db = SessionLocal()
    try:
        service = RepositoryService(db)
        service.run_analysis(repository_id)
    finally:
        db.close()
