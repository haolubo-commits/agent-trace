"""
Unit tests for Pydantic v2 schemas and validation models.
"""

from datetime import datetime
from app.models.trace import TraceStatus, StepType, TokenUsage
from app.schemas.trace import (
    TraceCreate,
    TraceResponse,
    StepCreate,
    StepResponse,
    ToolCallCreate,
    ToolCallResponse,
    DAGNode,
    DAGEdge,
)


def test_token_usage_initialization():
    usage = TokenUsage(prompt_tokens=150, completion_tokens=50, total_tokens=200)
    assert usage.prompt_tokens == 150
    assert usage.completion_tokens == 50
    assert usage.total_tokens == 200


def test_trace_create_schema():
    payload = {
        "agent_name": "FinancialAnalystAgent",
        "session_id": "sess_market_991",
        "meta_info": {"model": "gpt-4o", "temperature": 0.2},
    }
    trace_in = TraceCreate(**payload)
    assert trace_in.agent_name == "FinancialAnalystAgent"
    assert trace_in.session_id == "sess_market_991"
    assert trace_in.meta_info["model"] == "gpt-4o"


def test_step_create_schema():
    step_in = StepCreate(
        step_type=StepType.THOUGHT,
        name="Reasoning: Evaluate Valuation Metrics",
        inputs={"target": "NVDA", "pe_ratio": 45.2},
        outputs={"action": "INVOKE_TOOL", "tool": "SEC_EDGAR"},
        tokens=TokenUsage(prompt_tokens=240, completion_tokens=60, total_tokens=300),
        latency_ms=120.5,
    )
    assert step_in.step_type == StepType.THOUGHT
    assert step_in.name == "Reasoning: Evaluate Valuation Metrics"
    assert step_in.tokens.total_tokens == 300
    assert step_in.latency_ms == 120.5
    assert step_in.status == TraceStatus.COMPLETED


def test_tool_call_create_schema():
    tool_in = ToolCallCreate(
        tool_name="SearchWeb",
        arguments={"query": "latest SEC 10-K filing NVDA"},
        result={"url": "sec.gov/edgar/...", "revenue": "$35.1B"},
        latency_ms=450.0,
        status="success",
    )
    assert tool_in.tool_name == "SearchWeb"
    assert tool_in.status == "success"
    assert tool_in.latency_ms == 450.0


def test_dag_node_schema():
    node = DAGNode(
        id="step_node_01",
        type="thoughtNode",
        position={"x": 80.0, "y": 140.0},
        data={"name": "Step 1", "tokens": 400},
    )
    assert node.id == "step_node_01"
    assert node.type == "thoughtNode"
    assert node.position["x"] == 80.0
    assert node.position["y"] == 140.0


def test_dag_edge_schema():
    edge = DAGEdge(
        id="e_01_02",
        source="step_node_01",
        target="step_node_02",
        animated=True,
        label="145ms",
    )
    assert edge.source == "step_node_01"
    assert edge.target == "step_node_02"
    assert edge.animated is True
    assert edge.label == "145ms"
