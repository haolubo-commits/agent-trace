"""
Aggregated v1 API Router for AgentTrace.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import traces, steps, tools

api_router = APIRouter()

api_router.include_router(traces.router, prefix="/traces", tags=["Traces"])
api_router.include_router(steps.router, prefix="/traces", tags=["Steps"])
api_router.include_router(tools.router, prefix="/traces", tags=["Tools"])
