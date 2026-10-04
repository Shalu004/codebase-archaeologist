from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AskRequest(BaseModel):
    question: str
    context_node_id: Optional[str] = None
    file_path: Optional[str] = None

class EvidenceItem(BaseModel):
    file_path: str
    line_number: Optional[int] = None
    symbol_name: Optional[str] = None
    snippet: Optional[str] = None
    relationship: Optional[str] = None

class AskResponse(BaseModel):
    question: str
    summary: str
    explanation: str
    evidence: List[EvidenceItem]
    confidence: str  # HIGH, MEDIUM, LOW, POSSIBLE

class OverviewResponse(BaseModel):
    project_name: str
    purpose: str
    objectives: List[str]
    target_users: str
    tech_stack: List[str]
    architecture: str
    major_modules: List[Dict[str, str]]
    entry_points: List[Dict[str, Any]]
    database_layer: Optional[str]
    apis: List[Dict[str, Any]]
    feature_connections: List[Dict[str, Any]]

class OnboardingResponse(BaseModel):
    prerequisites: List[str]
    installation: List[str]
    environment_vars: List[str]
    how_to_run: List[str]
    architecture_overview: str
    important_directories: List[Dict[str, str]]
    important_files: List[Dict[str, str]]
    recommended_reading_order: List[str]
    common_pitfalls: List[str]
