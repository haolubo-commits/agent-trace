"""
MongoDB data models for AgentTrace.
Represents traces, DAG execution steps, tool call records, and token metrics.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class TraceStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepType(str, Enum):
    THOUGHT = "thought"
    LLM_CALL = "llm_call"
    TOOL_CALL = "tool_call"
    SUBAGENT_SPAWN = "subagent_spawn"
    USER_INPUT = "user_input"


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    total_tokens: int = 0


class ToolCallModel(BaseModel):
    tool_call_id: str
    step_id: str
    trace_id: str
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None
    latency_ms: float = 0.0
    status: str = "success"  # success, error
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StepModel(BaseModel):
    step_id: str
    trace_id: str
    parent_step_id: Optional[str] = None
    step_index: int
    step_type: StepType
    name: str
    status: TraceStatus = TraceStatus.COMPLETED
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    tokens: TokenUsage = Field(default_factory=TokenUsage)
    latency_ms: float = 0.0
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    meta_info: Dict[str, Any] = Field(default_factory=dict)


class TraceModel(BaseModel):
    trace_id: str
    agent_name: str
    session_id: str
    status: TraceStatus = TraceStatus.RUNNING
    total_tokens: TokenUsage = Field(default_factory=TokenUsage)
    latency_ms: float = 0.0
    total_cost_usd: float = 0.0
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    meta_info: Dict[str, Any] = Field(default_factory=dict)
