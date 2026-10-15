"""
Unit tests for AnalyticsService and performance bottleneck discovery.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.models.trace import StepType, TraceStatus, TokenUsage
from app.schemas.trace import TraceResponse, StepResponse
from app.schemas.analytics import StepTypeBreakdown, ToolPerformanceMetrics, BottleneckInsight
from app.services.analytics_service import AnalyticsService


@pytest.mark.asyncio
async def test_analytics_bottleneck_detection():
    mock_db = MagicMock()
    # Mock empty cursor for aggregate pipelines
    mock_cursor = MagicMock()
    mock_cursor.__aiter__.return_value = []
    mock_db.steps.aggregate.return_value = mock_cursor
    mock_db.tool_calls.aggregate.return_value = mock_cursor

    service = AnalyticsService(db=mock_db)

    trace = TraceResponse(
        trace_id="trc_perf_01",
        agent_name="ObservabilityAgent",
        session_id="sess_perf_1",
        status=TraceStatus.COMPLETED,
        total_tokens=TokenUsage(prompt_tokens=2000, completion_tokens=1000, total_tokens=3000),
        latency_ms=5000.0,
        total_cost_usd=0.045,
        start_time=datetime.utcnow(),
        meta_info={},
    )
    service.trace_service.get_trace = AsyncMock(return_value=trace)

    step_fast = StepResponse(
        step_id="step_fast",
        trace_id="trc_perf_01",
        step_index=0,
        step_type=StepType.THOUGHT,
        name="Quick Thought",
        status=TraceStatus.COMPLETED,
        inputs={},
        outputs={},
        tokens=TokenUsage(prompt_tokens=100, completion_tokens=20, total_tokens=120),
        latency_ms=50.0,
        created_at=datetime.utcnow(),
        meta_info={},
    )
    step_heavy = StepResponse(
        step_id="step_heavy",
        trace_id="trc_perf_01",
        step_index=1,
        step_type=StepType.LLM_CALL,
        name="Massive Context Generation",
        status=TraceStatus.COMPLETED,
        inputs={},
        outputs={},
        tokens=TokenUsage(prompt_tokens=1900, completion_tokens=980, total_tokens=2880),
        latency_ms=4950.0,
        created_at=datetime.utcnow(),
        meta_info={},
    )

    service.step_service.get_steps_by_trace = AsyncMock(return_value=[step_fast, step_heavy])

    analytics = await service.get_trace_analytics("trc_perf_01")

    assert analytics is not None
    assert analytics.trace_id == "trc_perf_01"
    assert analytics.total_latency_ms == 5000.0

    # Bottleneck assertions
    assert len(analytics.bottlenecks) == 2
    types = [b.bottleneck_type for b in analytics.bottlenecks]
    assert "tokens" in types
    assert "latency" in types

    token_b = next(b for b in analytics.bottlenecks if b.bottleneck_type == "tokens")
    assert token_b.step_id == "step_heavy"
    assert token_b.percentage_of_total == 96.0

    latency_b = next(b for b in analytics.bottlenecks if b.bottleneck_type == "latency")
    assert latency_b.step_id == "step_heavy"
    assert latency_b.percentage_of_total == 99.0
