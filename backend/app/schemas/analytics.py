"""
Analytics schemas for trace aggregation pipelines, token bottlenecks, and tool reliability metrics.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StepTypeBreakdown(BaseModel):
    step_type: str
    count: int
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    avg_latency_ms: float
    max_latency_ms: float


class ToolPerformanceMetrics(BaseModel):
    tool_name: str
    total_invocations: int
    success_count: int
    error_count: int
    error_rate: float
    avg_latency_ms: float
    max_latency_ms: float


class BottleneckInsight(BaseModel):
    bottleneck_type: str  # 'latency' | 'tokens'
    step_id: str
    step_name: str
    step_type: str
    value: float
    unit: str
    percentage_of_total: float
    recommendation: str


class TraceAnalyticsResponse(BaseModel):
    trace_id: str
    agent_name: str
    total_latency_ms: float
    total_tokens: int
    total_cost_usd: float
    step_breakdowns: List[StepTypeBreakdown]
    tool_metrics: List[ToolPerformanceMetrics]
    bottlenecks: List[BottleneckInsight]
