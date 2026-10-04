from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class RepositoryCreateGitHub(BaseModel):
    github_url: str = Field(..., description="GitHub repository URL (e.g. https://github.com/user/repo)")
    default_branch: Optional[str] = "main"

class RepositoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    source_type: str
    default_branch: Optional[str] = "main"
    commit_sha: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    file_count: int = 0
    symbol_count: int = 0
    node_count: int = 0
    edge_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FileNode(BaseModel):
    id: str
    name: str
    path: str
    type: str  # 'file' or 'directory'
    size: Optional[int] = 0
    line_count: Optional[int] = 0
    language: Optional[str] = None
    children: Optional[List['FileNode']] = None

class FileTreeResponse(BaseModel):
    tree: List[FileNode]

class FileDetailResponse(BaseModel):
    id: str
    path: str
    language: Optional[str]
    size_bytes: int
    line_count: int
    content: Optional[str] = None
    symbols: List[Dict[str, Any]] = []
