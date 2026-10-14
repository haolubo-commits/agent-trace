"""
Traces API Endpoints: Ingestion, session querying, DAG graph retrieval, and trace lifecycles.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from app.models.trace import TraceStatus
from app.schemas.trace import TraceCreate, TraceUpdate, TraceResponse, DAGGraphResponse
from app.services.trace_service import TraceService
from app.services.dag_service import DAGService

router = APIRouter()


@router.post("/", response_model=TraceResponse, status_code=status.HTTP_201_CREATED)
async def create_trace(trace_in: TraceCreate):
    """
    Initializes a new autonomous agent trace session.
    """
    service = TraceService()
    return await service.create_trace(trace_in)


@router.get("/", response_model=List[TraceResponse])
async def list_traces(
    status: Optional[TraceStatus] = Query(None, description="Filter traces by status"),
    session_id: Optional[str] = Query(None, description="Filter traces by user session ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Lists agent execution traces with pagination and status filters.
    """
    service = TraceService()
    return await service.list_traces(status=status, session_id=session_id, skip=skip, limit=limit)


@router.get("/{trace_id}", response_model=TraceResponse)
async def get_trace(trace_id: str):
    """
    Retrieves execution summary and metrics for a specific agent trace.
    """
    service = TraceService()
    trace = await service.get_trace(trace_id)
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace with ID '{trace_id}' not found."
        )
    return trace


@router.patch("/{trace_id}", response_model=TraceResponse)
async def update_trace(trace_id: str, update_in: TraceUpdate):
    """
    Updates status, completion timestamp, cost, or metadata of an existing trace.
    """
    service = TraceService()
    updated = await service.update_trace(trace_id, update_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace with ID '{trace_id}' not found."
        )
    return updated


@router.delete("/{trace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trace(trace_id: str):
    """
    Cascading delete for a trace and all associated steps and tool execution records.
    """
    service = TraceService()
    deleted = await service.delete_trace(trace_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace with ID '{trace_id}' not found."
        )


@router.get("/{trace_id}/graph", response_model=DAGGraphResponse)
async def get_trace_dag_graph(trace_id: str):
    """
    Traverses the execution graph and returns a structured Directed Acyclic Graph (DAG)
    compatible with React Flow, including pre-computed node layout positions.
    """
    dag_service = DAGService()
    graph = await dag_service.build_dag_graph(trace_id)
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace with ID '{trace_id}' not found."
        )
    return graph
