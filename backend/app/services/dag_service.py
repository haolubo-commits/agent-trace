"""
DAG Service: Directed Acyclic Graph traversal and layout engine for React Flow visualization.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict, deque
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.mongodb import get_database
from app.models.trace import StepType, TraceStatus
from app.schemas.trace import DAGGraphResponse, DAGNode, DAGEdge, TraceResponse, StepResponse, ToolCallResponse
from app.services.trace_service import TraceService
from app.services.step_service import StepService
from app.services.tool_service import ToolService


class DAGService:
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        self.db = db if db is not None else get_database()
        self.trace_service = TraceService(self.db)
        self.step_service = StepService(self.db)
        self.tool_service = ToolService(self.db)

    def _map_step_type_to_node_type(self, step_type: str) -> str:
        """Maps internal step enum to specialized React Flow custom node identifiers."""
        mapping = {
            StepType.THOUGHT.value: "thoughtNode",
            StepType.LLM_CALL.value: "llmNode",
            StepType.TOOL_CALL.value: "toolNode",
            StepType.SUBAGENT_SPAWN.value: "subagentNode",
            StepType.USER_INPUT.value: "inputNode",
        }
        return mapping.get(step_type, "customNode")

    async def build_dag_graph(self, trace_id: str) -> Optional[DAGGraphResponse]:
        """
        Traverses trace execution steps and tool calls to construct a hierarchical
        React Flow Directed Acyclic Graph (DAG) with auto-computed coordinates.
        """
        trace = await self.trace_service.get_trace(trace_id)
        if not trace:
            return None

        steps: List[StepResponse] = await self.step_service.get_steps_by_trace(trace_id)
        tools: List[ToolCallResponse] = await self.tool_service.get_tools_by_trace(trace_id)

        # Group tools by step_id
        tools_by_step: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for tool in tools:
            tools_by_step[tool.step_id].append(tool.model_dump())

        # Step lookup map
        step_map: Dict[str, StepResponse] = {s.step_id: s for s in steps}

        # Build adjacency graph
        children_map: Dict[str, List[str]] = defaultdict(list)
        parent_map: Dict[str, str] = {}
        roots: List[str] = []

        for step in steps:
            p_id = step.parent_step_id
            if p_id and p_id in step_map:
                children_map[p_id].append(step.step_id)
                parent_map[step.step_id] = p_id
            else:
                roots.append(step.step_id)

        # Compute depth/level for each node using BFS
        depth_map: Dict[str, int] = {}
        queue = deque([(root_id, 0) for root_id in roots])
        visited = set()

        while queue:
            node_id, depth = queue.popleft()
            if node_id in visited:
                continue
            visited.add(node_id)
            depth_map[node_id] = depth

            for child_id in children_map.get(node_id, []):
                if child_id not in visited:
                    queue.append((child_id, depth + 1))

        # Any unvisited step gets depth 0
        for step in steps:
            if step.step_id not in depth_map:
                depth_map[step.step_id] = 0

        # Group node IDs by depth for layout calculation
        level_groups: Dict[int, List[str]] = defaultdict(list)
        for step in steps:
            level = depth_map[step.step_id]
            level_groups[level].append(step.step_id)

        # Assign (x, y) coordinates
        # Left-to-right DAG layout: x advances with level, y advances per sibling
        positions: Dict[str, Dict[str, float]] = {}
        HORIZONTAL_SPACING = 320.0
        VERTICAL_SPACING = 160.0

        for level, node_ids in level_groups.items():
            num_nodes = len(node_ids)
            total_height = (num_nodes - 1) * VERTICAL_SPACING
            start_y = 60.0 - (total_height / 2.0)

            for idx, node_id in enumerate(node_ids):
                positions[node_id] = {
                    "x": 80.0 + (level * HORIZONTAL_SPACING),
                    "y": start_y + (idx * VERTICAL_SPACING)
                }

        # Assemble DAG Nodes
        dag_nodes: List[DAGNode] = []
        for step in steps:
            node_type = self._map_step_type_to_node_type(step.step_type.value)
            step_tools = tools_by_step.get(step.step_id, [])

            dag_nodes.append(DAGNode(
                id=step.step_id,
                type=node_type,
                position=positions.get(step.step_id, {"x": 0.0, "y": 0.0}),
                data={
                    "step_id": step.step_id,
                    "name": step.name,
                    "step_type": step.step_type.value,
                    "status": step.status.value,
                    "step_index": step.step_index,
                    "latency_ms": step.latency_ms,
                    "tokens": step.tokens.model_dump(),
                    "inputs": step.inputs,
                    "outputs": step.outputs,
                    "error_message": step.error_message,
                    "tools": step_tools,
                    "has_error": bool(step.error_message),
                    "tool_count": len(step_tools)
                }
            ))

        # Assemble DAG Edges
        dag_edges: List[DAGEdge] = []
        for step in steps:
            if step.parent_step_id and step.parent_step_id in step_map:
                is_animated = (step.status == TraceStatus.RUNNING)
                latency_label = f"{step.latency_ms:.0f}ms" if step.latency_ms > 0 else None

                dag_edges.append(DAGEdge(
                    id=f"e_{step.parent_step_id}_{step.step_id}",
                    source=step.parent_step_id,
                    target=step.step_id,
                    animated=is_animated,
                    label=latency_label
                ))

        return DAGGraphResponse(
            trace=trace,
            nodes=dag_nodes,
            edges=dag_edges,
            total_steps=len(steps),
            total_tools=len(tools)
        )
