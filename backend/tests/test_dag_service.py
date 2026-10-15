"""
Unit tests for DAG graph traversal, node type mappings, and coordinate computation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.models.trace import StepType, TraceStatus, TokenUsage
from app.schemas.trace import StepResponse, TraceResponse
from app.services.dag_service import DAGService
from datetime import datetime


def test_map_step_type_to_node_type():
    dag_service = DAGService(db=None)

    assert dag_service._map_step_type_to_node_type("thought") == "thoughtNode"
    assert dag_service._map_step_type_to_node_type("llm_call") == "llmNode"
    assert dag_service._map_step_type_to_node_type("tool_call") == "toolNode"
    assert dag_service._map_step_type_to_node_type("subagent_spawn") == "subagentNode"
    assert dag_service._map_step_type_to_node_type("user_input") == "inputNode"
    assert dag_service._map_step_type_to_node_type("unknown") == "customNode"


@pytest.mark.asyncio
async def test_build_dag_graph_structure():
    mock_db = MagicMock()
    dag_service = DAGService(db=mock_db)

    # Mock trace response
    trace = TraceResponse(
        trace_id="trc_test_01",
        agent_name="TestAgent",
        session_id="sess_100",
        status=TraceStatus.COMPLETED,
        total_tokens=TokenUsage(prompt_tokens=500, completion_tokens=100, total_tokens=600),
        latency_ms=1200.0,
        total_cost_usd=0.015,
        start_time=datetime.utcnow(),
        meta_info={},
    )
    dag_service.trace_service.get_trace = AsyncMock(return_value=trace)

    # Mock steps: step1 -> step2 (child) -> step3 (child)
    step1 = StepResponse(
        step_id="step_1",
        trace_id="trc_test_01",
        parent_step_id=None,
        step_index=0,
        step_type=StepType.USER_INPUT,
        name="User Input Prompt",
        status=TraceStatus.COMPLETED,
        inputs={"q": "Hello"},
        outputs={"ack": True},
        tokens=TokenUsage(prompt_tokens=20, completion_tokens=0, total_tokens=20),
        latency_ms=10.0,
        created_at=datetime.utcnow(),
        meta_info={},
    )
    step2 = StepResponse(
        step_id="step_2",
        trace_id="trc_test_01",
        parent_step_id="step_1",
        step_index=1,
        step_type=StepType.THOUGHT,
        name="Reasoning Strategy",
        status=TraceStatus.COMPLETED,
        inputs={},
        outputs={},
        tokens=TokenUsage(prompt_tokens=180, completion_tokens=50, total_tokens=230),
        latency_ms=150.0,
        created_at=datetime.utcnow(),
        meta_info={},
    )
    step3 = StepResponse(
        step_id="step_3",
        trace_id="trc_test_01",
        parent_step_id="step_2",
        step_index=2,
        step_type=StepType.TOOL_CALL,
        name="Tool: SearchWeb",
        status=TraceStatus.COMPLETED,
        inputs={"query": "test"},
        outputs={"results": 3},
        tokens=TokenUsage(prompt_tokens=300, completion_tokens=50, total_tokens=350),
        latency_ms=450.0,
        created_at=datetime.utcnow(),
        meta_info={},
    )

    dag_service.step_service.get_steps_by_trace = AsyncMock(return_value=[step1, step2, step3])
    dag_service.tool_service.get_tools_by_trace = AsyncMock(return_value=[])

    graph = await dag_service.build_dag_graph("trc_test_01")

    assert graph is not None
    assert graph.total_steps == 3
    assert len(graph.nodes) == 3
    assert len(graph.edges) == 2

    # Verify edge connectivity
    edge_pairs = [(e.source, e.target) for e in graph.edges]
    assert ("step_1", "step_2") in edge_pairs
    assert ("step_2", "step_3") in edge_pairs

    # Verify positions: level advances horizontally
    node_x = {n.id: n.position["x"] for n in graph.nodes}
    assert node_x["step_1"] < node_x["step_2"] < node_x["step_3"]
