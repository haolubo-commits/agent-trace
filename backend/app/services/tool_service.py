"""
Tool Service: Business logic for recording and retrieving tool call executions.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import get_database
from app.schemas.trace import ToolCallCreate, ToolCallResponse


class ToolService:
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self.db = db if db is not None else get_database()

    def _get_collection(self):
        if self.db is None:
            raise RuntimeError("MongoDB connection not initialized. Please ensure MongoDB is running.")
        return self.db["tool_calls"]

    async def record_tool_call(
        self,
        trace_id: str,
        step_id: str,
        tool_in: ToolCallCreate
    ) -> ToolCallResponse:
        """Records a tool execution invocation belonging to a specific trace step."""
        col = self._get_collection()
        tool_call_id = f"call_{uuid.uuid4().hex[:10]}"
        now = datetime.utcnow()

        tool_doc = {
            "tool_call_id": tool_call_id,
            "step_id": step_id,
            "trace_id": trace_id,
            "tool_name": tool_in.tool_name,
            "arguments": tool_in.arguments,
            "result": tool_in.result,
            "latency_ms": tool_in.latency_ms,
            "status": tool_in.status,
            "error_message": tool_in.error_message,
            "timestamp": now
        }

        await col.insert_one(tool_doc)
        tool_doc.pop("_id", None)
        return ToolCallResponse(**tool_doc)

    async def get_tools_by_step(self, step_id: str) -> List[ToolCallResponse]:
        """Fetches all tool invocations that occurred inside a particular execution step."""
        col = self._get_collection()
        cursor = col.find({"step_id": step_id}, {"_id": 0}).sort("timestamp", 1)
        tools = []
        async for doc in cursor:
            tools.append(ToolCallResponse(**doc))
        return tools

    async def get_tools_by_trace(self, trace_id: str) -> List[ToolCallResponse]:
        """Fetches all tool invocations for an entire agent trace."""
        col = self._get_collection()
        cursor = col.find({"trace_id": trace_id}, {"_id": 0}).sort("timestamp", 1)
        tools = []
        async for doc in cursor:
            tools.append(ToolCallResponse(**doc))
        return tools
