"""
Steps API Endpoints: Step ingestion, execution hierarchy, and step details.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from app.schemas.trace import StepCreate, StepResponse
from app.services.step_service import StepService
from app.services.trace_service import TraceService

router = APIRouter()


@router.post("/{trace_id}/steps", response_model=StepResponse, status_code=status.HTTP_201_CREATED)
async def add_trace_step(trace_id: str, step_in: StepCreate):
    """
    Appends a new execution step (thought, llm_call, tool_call, subagent_spawn)
    to an active trace DAG. Automatically recomputes parent trace metrics.
    """
    trace_service = TraceService()
    trace = await trace_service.get_trace(trace_id)
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent trace '{trace_id}' not found."
        )

    # Validate parent_step_id if provided
    step_service = StepService()
    if step_in.parent_step_id:
        parent_step = await step_service.get_step_by_id(step_in.parent_step_id)
        if not parent_step or parent_step.trace_id != trace_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parent step '{step_in.parent_step_id}' does not exist in this trace."
            )

    return await step_service.add_step(trace_id, step_in)


@router.get("/{trace_id}/steps", response_model=List[StepResponse])
async def list_trace_steps(trace_id: str):
    """
    Lists all execution steps in sequential order for a specific trace.
    """
    step_service = StepService()
    return await step_service.get_steps_by_trace(trace_id)


@router.get("/step/{step_id}", response_model=StepResponse)
async def get_step_detail(step_id: str):
    """
    Retrieves detailed payload, inputs, outputs, and token usage for a single step.
    """
    step_service = StepService()
    step = await step_service.get_step_by_id(step_id)
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Step with ID '{step_id}' not found."
        )
    return step
