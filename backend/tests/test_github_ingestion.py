import os
import pytest
from app.db.session import SessionLocal, init_db
from app.services.repo_service import RepositoryService
from app.models.entities import RepositoryModel

# Initialize database tables
init_db()

def test_github_ingestion_kiet_innotech():
    db = SessionLocal()
    try:
        service = RepositoryService(db)
        # 1. Ingest kiet-innotech repository
        repo = service.create_from_github("https://github.com/something1703/kiet-innotech", "main")
        assert repo.status == "QUEUED"

        # 2. Run analysis pipeline
        service.run_analysis(repo.id)
        db.refresh(repo)

        # 3. Verify factual stats from static analysis & AST parsing
        assert repo.status == "COMPLETED"
        assert repo.file_count > 0
        assert repo.symbol_count > 0
        assert repo.node_count > 0
        assert repo.edge_count > 0
        assert repo.commit_sha is not None
        assert len(repo.commit_sha) > 5

        print(f"\n[TEST PASSED] kiet-innotech analysis: files={repo.file_count}, symbols={repo.symbol_count}, nodes={repo.node_count}, edges={repo.edge_count}")
    finally:
        db.close()

def test_github_ingestion_invalid_repository_fails():
    db = SessionLocal()
    try:
        service = RepositoryService(db)
        # Ingest invalid non-existent repository must raise ValueError during validation
        with pytest.raises(ValueError) as excinfo:
            service.create_from_github("https://github.com/invalid-nonexistent-user-12345/nonexistent-repo-99999", "main")
        
        assert "Invalid or inaccessible GitHub repository" in str(excinfo.value)
        print("\n[TEST PASSED] Invalid GitHub ingestion correctly raised ValueError on URL validation")
    finally:
        db.close()

