from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class FeatureStep(BaseModel):
    step: int
    layer: str
    file_path: str
    symbol_name: str
    line_number: int
    snippet: Optional[str] = None
    explanation: Optional[str] = None

class FeatureEvidence(BaseModel):
    file_path: str
    line_number: int
    symbol_name: Optional[str] = None
    snippet: Optional[str] = None
    relationship: str

class FeatureResponse(BaseModel):
    id: str
    repository_id: str
    name: str
    description: str
    confidence: str
    entry_points: List[str]
    files: List[str]
    symbols: List[str]
    api_routes: List[str]
    data_models: List[str]
    components: List[str]
    flows: List[FeatureStep]
    evidence: List[FeatureEvidence]
