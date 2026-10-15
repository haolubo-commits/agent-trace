"""
Analytics Service: High-performance MongoDB aggregation pipelines for AI agent observability.
Calculates token bottlenecks, P95/avg tool latencies, and step distribution.
"""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import get_database
from app.schemas.analytics import (
    TraceAnalyticsResponse,
    StepTypeBreakdown,
    ToolPerformanceMetrics,
    BottleneckInsight,
)
from app.services.trace_service import TraceService
from app.services.step_service import StepService


class AnalyticsService:
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self.db = db if db is not None else get_database()
        self.trace_service = TraceService(self.db)
        self.step_service = StepService(self.db)

    async def get_trace_analytics(self, trace_id: str) -> Optional[TraceAnalyticsResponse]:
        """
        Executes aggregation pipelines across steps and tool calls for a given trace.
        """
        trace = await self.trace_service.get_trace(trace_id)
        if not trace:
            return None

        # 1. MongoDB Aggregation Pipeline: Step Type Distribution & Token Breakdown
        step_pipeline = [
            {"$match": {"trace_id": trace_id}},
            {
                "$group": {
                    "_id": "$step_type",
                    "count": {"$sum": 1},
                    "total_tokens": {"$sum": "$tokens.total_tokens"},
                    "prompt_tokens": {"$sum": "$tokens.prompt_tokens"},
                    "completion_tokens": {"$sum": "$tokens.completion_tokens"},
                    "avg_latency_ms": {"$avg": "$latency_ms"},
                    "max_latency_ms": {"$max": "$latency_ms"},
                }
            },
            {"$sort": {"total_tokens": -1}},
        ]

        step_breakdowns: List[StepTypeBreakdown] = []
        if self.db is not None:
            cursor = self.db.steps.aggregate(step_pipeline)
            async for doc in cursor:
                step_breakdowns.append(
                    StepTypeBreakdown(
                        step_type=doc["_id"],
                        count=doc["count"],
                        total_tokens=doc["total_tokens"],
                        prompt_tokens=doc["prompt_tokens"],
                        completion_tokens=doc["completion_tokens"],
                        avg_latency_ms=round(doc.get("avg_latency_ms", 0.0), 2),
                        max_latency_ms=round(doc.get("max_latency_ms", 0.0), 2),
                    )
                )

        # 2. MongoDB Aggregation Pipeline: Tool Invocation Reliability & Latency
        tool_pipeline = [
            {"$match": {"trace_id": trace_id}},
            {
                "$group": {
                    "_id": "$tool_name",
                    "total_invocations": {"$sum": 1},
                    "error_count": {
                        "$sum": {
                            "$cond": [{"$ne": ["$status", "success"]}, 1, 0]
                        }
                    },
                    "avg_latency_ms": {"$avg": "$latency_ms"},
                    "max_latency_ms": {"$max": "$latency_ms"},
                }
            },
            {"$sort": {"total_invocations": -1}},
        ]

        tool_metrics: List[ToolPerformanceMetrics] = []
        if self.db is not None:
            cursor = self.db.tool_calls.aggregate(tool_pipeline)
            async for doc in cursor:
                total = doc["total_invocations"]
                errors = doc["error_count"]
                successes = total - errors
                err_rate = round((errors / total) * 100, 2) if total > 0 else 0.0

                tool_metrics.append(
                    ToolPerformanceMetrics(
                        tool_name=doc["_id"],
                        total_invocations=total,
                        success_count=successes,
                        error_count=errors,
                        error_rate=err_rate,
                        avg_latency_ms=round(doc.get("avg_latency_ms", 0.0), 2),
                        max_latency_ms=round(doc.get("max_latency_ms", 0.0), 2),
                    )
                )

        # 3. Bottleneck Analysis: Find the highest-latency and highest-token steps
        bottlenecks: List[BottleneckInsight] = []
        steps = await self.step_service.get_steps_by_trace(trace_id)

        if steps:
            total_tokens = trace.total_tokens.total_tokens or sum(s.tokens.total_tokens for s in steps)
            total_latency = trace.latency_ms or sum(s.latency_ms for s in steps)

            # Max token consumer
            max_token_step = max(steps, key=lambda s: s.tokens.total_tokens)
            if max_token_step.tokens.total_tokens > 0 and total_tokens > 0:
                pct = round((max_token_step.tokens.total_tokens / total_tokens) * 100, 1)
                bottlenecks.append(
                    BottleneckInsight(
                        bottleneck_type="tokens",
                        step_id=max_token_step.step_id,
                        step_name=max_token_step.name,
                        step_type=max_token_step.step_type.value,
                        value=float(max_token_step.tokens.total_tokens),
                        unit="tokens",
                        percentage_of_total=pct,
                        recommendation=(
                            f"Step '{max_token_step.name}' accounts for {pct}% of total tokens. "
                            "Consider semantic context pruning or prompt compaction."
                        ),
                    )
                )

            # Max latency consumer
            max_latency_step = max(steps, key=lambda s: s.latency_ms)
            if max_latency_step.latency_ms > 0 and total_latency > 0:
                pct = round((max_latency_step.latency_ms / total_latency) * 100, 1)
                bottlenecks.append(
                    BottleneckInsight(
                        bottleneck_type="latency",
                        step_id=max_latency_step.step_id,
                        step_name=max_latency_step.name,
                        step_type=max_latency_step.step_type.value,
                        value=round(max_latency_step.latency_ms, 2),
                        unit="ms",
                        percentage_of_total=pct,
                        recommendation=(
                            f"Step '{max_latency_step.name}' took {max_latency_step.latency_ms:.0f}ms ({pct}% of trace duration). "
                            "Check tool IO timeouts or evaluate asynchronous concurrent dispatch."
                        ),
                    )
                )

        return TraceAnalyticsResponse(
            trace_id=trace.trace_id,
            agent_name=trace.agent_name,
            total_latency_ms=round(trace.latency_ms, 2),
            total_tokens=trace.total_tokens.total_tokens,
            total_cost_usd=round(trace.total_cost_usd, 4),
            step_breakdowns=step_breakdowns,
            tool_metrics=tool_metrics,
            bottlenecks=bottlenecks,
        )
