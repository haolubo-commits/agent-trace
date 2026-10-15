"""
Analytics API Endpoints: Aggregate trace performance, token breakdowns, and bottleneck discovery.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.analytics import TraceAnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/{trace_id}/analytics", response_model=TraceAnalyticsResponse)
async def get_trace_analytics(trace_id: str):
    """
    Retrieves deep analytics for a trace: MongoDB aggregation pipelines calculate
    step-type token breakdowns, tool failure rates, and execution bottlenecks.
    """
    service = AnalyticsService()
    analytics = await service.get_trace_analytics(trace_id)
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace with ID '{trace_id}' not found."
        )
    return analytics
