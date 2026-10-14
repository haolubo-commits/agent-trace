"""
Tools API Endpoints: Logging tool executions, arguments, returns, and execution latencies.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from app.schemas.trace import ToolCallCreate, ToolCallResponse
from app.services.tool_service import ToolService
from app.services.step_service import StepService

router = APIRouter()


@router.post("/{trace_id}/steps/{step_id}/tools", response_model=ToolCallResponse, status_code=status.HTTP_201_CREATED)
async def record_tool_call(trace_id: str, step_id: str, tool_in: ToolCallCreate):
    """
    Logs an external tool execution (e.g. Python REPL, Web Search, Database query)
    associated with an execution step node.
    """
    step_service = StepService()
    step = await step_service.get_step_by_id(step_id)
    if not step or step.trace_id != trace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Step '{step_id}' not found under trace '{trace_id}'."
        )

    tool_service = ToolService()
    return await tool_service.record_tool_call(trace_id, step_id, tool_in)


@router.get("/{trace_id}/steps/{step_id}/tools", response_model=List[ToolCallResponse])
async def list_step_tools(trace_id: str, step_id: str):
    """
    Lists all tool execution logs invoked within a specific step.
    """
    tool_service = ToolService()
    return await tool_service.get_tools_by_step(step_id)


@router.get("/{trace_id}/tools", response_model=List[ToolCallResponse])
async def list_trace_tools(trace_id: str):
    """
    Lists all tool execution records across the entire trace run.
    """
    tool_service = ToolService()
    return await tool_service.get_tools_by_trace(trace_id)
