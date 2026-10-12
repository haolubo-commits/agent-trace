"""
Pydantic v2 schemas for API requests, responses, and React Flow DAG representations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.trace import TraceStatus, StepType, TokenUsage


class TraceCreate(BaseModel):
    agent_name: str = Field(..., max_length=120)
    session_id: str = Field(..., max_length=120)
    meta_info: Dict[str, Any] = Field(default_factory=dict)


class TraceUpdate(BaseModel):
    status: Optional[TraceStatus] = None
    end_time: Optional[datetime] = None
    total_cost_usd: Optional[float] = None
    meta_info: Optional[Dict[str, Any]] = None


class TraceResponse(BaseModel):
    trace_id: str
    agent_name: str
    session_id: str
    status: TraceStatus
    total_tokens: TokenUsage
    latency_ms: float
    total_cost_usd: float
    start_time: datetime
    end_time: Optional[datetime] = None
    meta_info: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class StepCreate(BaseModel):
    parent_step_id: Optional[str] = None
    step_type: StepType
    name: str = Field(..., max_length=200)
    status: TraceStatus = TraceStatus.COMPLETED
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    tokens: TokenUsage = Field(default_factory=TokenUsage)
    latency_ms: float = 0.0
    error_message: Optional[str] = None
    meta_info: Dict[str, Any] = Field(default_factory=dict)


class StepResponse(BaseModel):
    step_id: str
    trace_id: str
    parent_step_id: Optional[str] = None
    step_index: int
    step_type: StepType
    name: str
    status: TraceStatus
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    tokens: TokenUsage
    latency_ms: float
    error_message: Optional[str] = None
    created_at: datetime
    meta_info: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class ToolCallCreate(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None
    latency_ms: float = 0.0
    status: str = "success"
    error_message: Optional[str] = None


class ToolCallResponse(BaseModel):
    tool_call_id: str
    step_id: str
    trace_id: str
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Any] = None
    latency_ms: float
    status: str
    error_message: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# React Flow DAG Graph Structures
class DAGNode(BaseModel):
    id: str
    type: str  # custom node type for React Flow: thoughtNode, toolNode, llmNode
    data: Dict[str, Any]
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0})


class DAGEdge(BaseModel):
    id: str
    source: str
    target: str
    animated: bool = False
    label: Optional[str] = None


class DAGGraphResponse(BaseModel):
    trace: TraceResponse
    nodes: List[DAGNode]
    edges: List[DAGEdge]
    total_steps: int
    total_tools: int
