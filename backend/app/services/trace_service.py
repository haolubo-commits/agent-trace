"""
Trace Service: Business logic for managing agent execution trace sessions in MongoDB.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import get_database
from app.models.trace import TraceModel, TraceStatus, TokenUsage
from app.schemas.trace import TraceCreate, TraceUpdate, TraceResponse


class TraceService:
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self.db = db if db is not None else get_database()

    def _get_collection(self):
        if self.db is None:
            raise RuntimeError("MongoDB connection not initialized. Please ensure MongoDB is running.")
        return self.db["traces"]

    async def create_trace(self, trace_in: TraceCreate) -> TraceResponse:
        """Initializes a new trace session for an autonomous agent run."""
        col = self._get_collection()
        trace_id = f"tr_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        trace_doc = {
            "trace_id": trace_id,
            "agent_name": trace_in.agent_name,
            "session_id": trace_in.session_id,
            "status": TraceStatus.RUNNING.value,
            "total_tokens": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "cached_tokens": 0,
                "total_tokens": 0
            },
            "latency_ms": 0.0,
            "total_cost_usd": 0.0,
            "start_time": now,
            "end_time": None,
            "meta_info": trace_in.meta_info
        }

        await col.insert_one(trace_doc)
        trace_doc.pop("_id", None)
        return TraceResponse(**trace_doc)

    async def get_trace(self, trace_id: str) -> Optional[TraceResponse]:
        """Fetches a trace by unique trace_id."""
        col = self._get_collection()
        doc = await col.find_one({"trace_id": trace_id}, {"_id": 0})
        if not doc:
            return None
        return TraceResponse(**doc)

    async def list_traces(
        self,
        status: Optional[TraceStatus] = None,
        session_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[TraceResponse]:
        """Retrieves a paginated list of traces matching optional status/session filters."""
        col = self._get_collection()
        query: Dict[str, Any] = {}
        if status:
            query["status"] = status.value
        if session_id:
            query["session_id"] = session_id

        cursor = col.find(query, {"_id": 0}).sort("start_time", -1).skip(skip).limit(limit)
        traces = []
        async for doc in cursor:
            traces.append(TraceResponse(**doc))
        return traces

    async def update_trace(self, trace_id: str, update_in: TraceUpdate) -> Optional[TraceResponse]:
        """Updates trace status, metrics, or metadata."""
        col = self._get_collection()
        update_data = update_in.model_dump(exclude_unset=True)

        if not update_data:
            return await self.get_trace(trace_id)

        # Convert Enum if present
        if "status" in update_data and isinstance(update_data["status"], TraceStatus):
            update_data["status"] = update_data["status"].value

        # Auto-set end_time if completed or failed and not explicitly provided
        if update_data.get("status") in [TraceStatus.COMPLETED.value, TraceStatus.FAILED.value, TraceStatus.CANCELLED.value]:
            if "end_time" not in update_data or update_data["end_time"] is None:
                update_data["end_time"] = datetime.utcnow()

        result = await col.find_one_and_update(
            {"trace_id": trace_id},
            {"$set": update_data},
            projection={"_id": 0},
            return_document=True
        )
        if not result:
            return None
        return TraceResponse(**result)

    async def increment_metrics(
        self,
        trace_id: str,
        tokens: TokenUsage,
        latency_ms: float = 0.0,
        cost_usd: float = 0.0
    ) -> Optional[TraceResponse]:
        """Atomically increments token counters, latency, and estimated cost for a trace."""
        col = self._get_collection()
        inc_fields = {
            "total_tokens.prompt_tokens": tokens.prompt_tokens,
            "total_tokens.completion_tokens": tokens.completion_tokens,
            "total_tokens.cached_tokens": tokens.cached_tokens,
            "total_tokens.total_tokens": tokens.total_tokens,
            "latency_ms": latency_ms,
            "total_cost_usd": cost_usd
        }

        result = await col.find_one_and_update(
            {"trace_id": trace_id},
            {"$inc": inc_fields},
            projection={"_id": 0},
            return_document=True
        )
        if not result:
            return None
        return TraceResponse(**result)

    async def delete_trace(self, trace_id: str) -> bool:
        """Deletes a trace and cascades deletion to associated steps and tool calls."""
        if self.db is None:
            raise RuntimeError("MongoDB connection not initialized.")

        traces_col = self.db["traces"]
        steps_col = self.db["steps"]
        tools_col = self.db["tool_calls"]

        result = await traces_col.delete_one({"trace_id": trace_id})
        if result.deleted_count > 0:
            await steps_col.delete_many({"trace_id": trace_id})
            await tools_col.delete_many({"trace_id": trace_id})
            return True
        return False
