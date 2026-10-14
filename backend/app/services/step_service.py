"""
Step Service: Business logic for ingesting and managing agent execution steps.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import get_database
from app.models.trace import StepType, TraceStatus
from app.schemas.trace import StepCreate, StepResponse
from app.services.trace_service import TraceService


class StepService:
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self.db = db if db is not None else get_database()
        self.trace_service = TraceService(self.db)

    def _get_collection(self):
        if self.db is None:
            raise RuntimeError("MongoDB connection not initialized. Please ensure MongoDB is running.")
        return self.db["steps"]

    async def add_step(self, trace_id: str, step_in: StepCreate) -> StepResponse:
        """
        Appends an execution step to a trace DAG and updates trace aggregate statistics.
        """
        col = self._get_collection()
        step_id = f"stp_{uuid.uuid4().hex[:10]}"
        now = datetime.utcnow()

        # Compute next step_index
        count = await col.count_documents({"trace_id": trace_id})
        step_index = count + 1

        step_doc = {
            "step_id": step_id,
            "trace_id": trace_id,
            "parent_step_id": step_in.parent_step_id,
            "step_index": step_index,
            "step_type": step_in.step_type.value,
            "name": step_in.name,
            "status": step_in.status.value,
            "inputs": step_in.inputs,
            "outputs": step_in.outputs,
            "tokens": step_in.tokens.model_dump(),
            "latency_ms": step_in.latency_ms,
            "error_message": step_in.error_message,
            "created_at": now,
            "meta_info": step_in.meta_info
        }

        await col.insert_one(step_doc)

        # Estimate token cost: ~$0.005 / 1k prompt, $0.015 / 1k completion
        estimated_cost = (
            (step_in.tokens.prompt_tokens * 0.000005) +
            (step_in.tokens.completion_tokens * 0.000015)
        )

        # Increment metrics on parent trace
        await self.trace_service.increment_metrics(
            trace_id=trace_id,
            tokens=step_in.tokens,
            latency_ms=step_in.latency_ms,
            cost_usd=round(estimated_cost, 6)
        )

        step_doc.pop("_id", None)
        return StepResponse(**step_doc)

    async def get_steps_by_trace(self, trace_id: str) -> List[StepResponse]:
        """Fetches all steps for a given trace, sorted by execution sequence."""
        col = self._get_collection()
        cursor = col.find({"trace_id": trace_id}, {"_id": 0}).sort("step_index", 1)
        steps = []
        async for doc in cursor:
            steps.append(StepResponse(**doc))
        return steps

    async def get_step_by_id(self, step_id: str) -> Optional[StepResponse]:
        """Fetches a specific execution step by its step_id."""
        col = self._get_collection()
        doc = await col.find_one({"step_id": step_id}, {"_id": 0})
        if not doc:
            return None
        return StepResponse(**doc)

    async def update_step(self, step_id: str, update_data: Dict[str, Any]) -> Optional[StepResponse]:
        """Updates execution step outputs, error state, or latency upon completion."""
        col = self._get_collection()
        result = await col.find_one_and_update(
            {"step_id": step_id},
            {"$set": update_data},
            projection={"_id": 0},
            return_document=True
        )
        if not result:
            return None
        return StepResponse(**result)
