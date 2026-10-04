import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class RepositoryModel(Base):
    __tablename__ = "repositories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(1024), nullable=True)
    source_type = Column(String(50), nullable=False, default="github")  # github, zip
    local_path = Column(String(1024), nullable=False)
    default_branch = Column(String(255), nullable=True, default="main")
    commit_sha = Column(String(64), nullable=True)
    status = Column(String(50), nullable=False, default="QUEUED")  # QUEUED, SCANNING, PARSING, GRAPH_BUILDING, READY, FAILED
    error_message = Column(Text, nullable=True)
    file_count = Column(Integer, default=0)
    symbol_count = Column(Integer, default=0)
    node_count = Column(Integer, default=0)
    edge_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    files = relationship("FileModel", back_populates="repository", cascade="all, delete-orphan")
    symbols = relationship("SymbolModel", back_populates="repository", cascade="all, delete-orphan")
    nodes = relationship("NodeModel", back_populates="repository", cascade="all, delete-orphan")
    edges = relationship("EdgeModel", back_populates="repository", cascade="all, delete-orphan")
    routes = relationship("RouteModel", back_populates="repository", cascade="all, delete-orphan")
    api_calls = relationship("ApiCallModel", back_populates="repository", cascade="all, delete-orphan")
    db_models = relationship("DBModelEntity", back_populates="repository", cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRunModel", back_populates="repository", cascade="all, delete-orphan")
    git_commits = relationship("GitCommitModel", back_populates="repository", cascade="all, delete-orphan")
    features = relationship("FeatureModel", back_populates="repository", cascade="all, delete-orphan")

class FileModel(Base):
    __tablename__ = "files"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    relative_path = Column(String(1024), nullable=False, index=True)
    extension = Column(String(50), nullable=True)
    language = Column(String(50), nullable=True)
    size_bytes = Column(Integer, default=0)
    line_count = Column(Integer, default=0)
    file_hash = Column(String(64), nullable=True)
    is_entry_point = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    repository = relationship("RepositoryModel", back_populates="files")
    symbols = relationship("SymbolModel", back_populates="file", cascade="all, delete-orphan")

class SymbolModel(Base):
    __tablename__ = "symbols"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    file_id = Column(String(36), ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String(1024), nullable=False)
    symbol_type = Column(String(50), nullable=False)  # function, class, method, component, route, model, export, import, variable
    name = Column(String(255), nullable=False, index=True)
    container_name = Column(String(255), nullable=True)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    start_column = Column(Integer, default=0)
    end_column = Column(Integer, default=0)
    docstring = Column(Text, nullable=True)
    source_code = Column(Text, nullable=True)
    extra_metadata = Column(JSON, nullable=True)

    repository = relationship("RepositoryModel", back_populates="symbols")
    file = relationship("FileModel", back_populates="symbols")

class NodeModel(Base):
    __tablename__ = "nodes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    node_type = Column(String(50), nullable=False)  # repository, directory, file, function, class, method, component, route, model, api
    label = Column(String(255), nullable=False, index=True)
    file_path = Column(String(1024), nullable=True)
    symbol_id = Column(String(36), nullable=True)
    metadata_json = Column(JSON, nullable=True)

    repository = relationship("RepositoryModel", back_populates="nodes")

class EdgeModel(Base):
    __tablename__ = "edges"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(String(36), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id = Column(String(36), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    edge_type = Column(String(50), nullable=False)  # CONTAINS, IMPORTS, EXPORTS, CALLS, DEFINES, USES, ROUTES_TO, DEPENDS_ON, RENDERS, ACCESSES, RELATED_TO
    weight = Column(Float, default=1.0)
    confidence = Column(String(20), default="HIGH")  # HIGH, MEDIUM, LOW, POSSIBLE
    evidence_json = Column(JSON, nullable=True)

    repository = relationship("RepositoryModel", back_populates="edges")

class RouteModel(Base):
    __tablename__ = "routes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    path = Column(String(512), nullable=False)
    method = Column(String(20), nullable=False, default="GET")
    handler_symbol_id = Column(String(36), nullable=True)
    file_path = Column(String(1024), nullable=False)
    line_number = Column(Integer, default=1)

    repository = relationship("RepositoryModel", back_populates="routes")

class ApiCallModel(Base):
    __tablename__ = "api_calls"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String(1024), nullable=False)
    line_number = Column(Integer, default=1)
    endpoint = Column(String(512), nullable=False)
    method = Column(String(20), nullable=False, default="GET")
    caller_symbol_id = Column(String(36), nullable=True)

    repository = relationship("RepositoryModel", back_populates="api_calls")

class DBModelEntity(Base):
    __tablename__ = "db_models"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    file_path = Column(String(1024), nullable=False)
    line_number = Column(Integer, default=1)
    fields_json = Column(JSON, nullable=True)
    model_type = Column(String(50), default="prisma")  # prisma, sequelize, typeorm, mongoose, custom

    repository = relationship("RepositoryModel", back_populates="db_models")

class AnalysisRunModel(Base):
    __tablename__ = "analysis_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="RUNNING")
    current_step = Column(String(255), nullable=True)
    step_progress = Column(Integer, default=0)
    error_log = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    repository = relationship("RepositoryModel", back_populates="analysis_runs")

class GitCommitModel(Base):
    __tablename__ = "git_commits"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    commit_hash = Column(String(64), nullable=False, index=True)
    author_name = Column(String(255), nullable=True)
    author_email = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    parents_json = Column(JSON, nullable=True)

    repository = relationship("RepositoryModel", back_populates="git_commits")
    changes = relationship("GitChangeModel", back_populates="commit", cascade="all, delete-orphan")

class GitChangeModel(Base):
    __tablename__ = "git_changes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    commit_id = Column(String(36), ForeignKey("git_commits.id", ondelete="CASCADE"), nullable=False, index=True)
    change_type = Column(String(20), nullable=False)  # ADD, MODIFY, DELETE
    file_path = Column(String(1024), nullable=False)
    old_path = Column(String(1024), nullable=True)
    lines_added = Column(Integer, default=0)
    lines_deleted = Column(Integer, default=0)

    commit = relationship("GitCommitModel", back_populates="changes")

class FeatureModel(Base):
    __tablename__ = "features"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    repository_id = Column(String(36), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    confidence = Column(String(20), default="HIGH")  # HIGH, MEDIUM, LOW
    entry_points_json = Column(JSON, nullable=True)  # List[str]
    files_json = Column(JSON, nullable=True)  # List[str]
    symbols_json = Column(JSON, nullable=True)  # List[str]
    api_routes_json = Column(JSON, nullable=True)  # List[str]
    data_models_json = Column(JSON, nullable=True)  # List[str]
    components_json = Column(JSON, nullable=True)  # List[str]
    flows_json = Column(JSON, nullable=True)  # List[Dict[str, Any]]
    evidence_json = Column(JSON, nullable=True)  # List[Dict[str, Any]]
    created_at = Column(DateTime, default=datetime.utcnow)

    repository = relationship("RepositoryModel", back_populates="features")

