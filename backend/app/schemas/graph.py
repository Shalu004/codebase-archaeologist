from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class GraphNode(BaseModel):
    id: str
    type: str  # repository, directory, file, function, class, method, component, route, model, api
    label: str
    file_path: Optional[str] = None
    symbol_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str  # CONTAINS, IMPORTS, EXPORTS, CALLS, DEFINES, USES, ROUTES_TO, DEPENDS_ON, RENDERS, ACCESSES, RELATED_TO
    confidence: str = "HIGH"  # HIGH, MEDIUM, LOW, POSSIBLE
    label: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class ImpactAnalysisRequest(BaseModel):
    node_id: Optional[str] = None
    file_path: Optional[str] = None
    symbol_name: Optional[str] = None

class ImpactAnalysisResponse(BaseModel):
    target: Dict[str, Any]
    affected_files: List[Dict[str, Any]]
    affected_symbols: List[Dict[str, Any]]
    affected_routes: List[Dict[str, Any]]
    affected_models: List[Dict[str, Any]]
    impact_graph: GraphResponse
    total_affected_count: int

class TraceRequest(BaseModel):
    feature_description: Optional[str] = "What happens when I click Login?"
    start_node_id: Optional[str] = None
    endpoint: Optional[str] = None

class TraceStep(BaseModel):
    step_number: int
    layer: str  # FRONTEND, API, ROUTE, CONTROLLER, SERVICE, DATABASE
    file_path: str
    symbol_name: str
    code_snippet: Optional[str] = None
    line_number: Optional[int] = None
    confidence: str = "HIGH"
    explanation: Optional[str] = None

class TraceResponse(BaseModel):
    query: str
    trace_steps: List[TraceStep]
    trace_graph: GraphResponse
    confidence: str
