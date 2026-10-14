"""
Seed Demo Trace: Generates a realistic multi-step autonomous agent execution DAG in MongoDB.
"""

import asyncio
from datetime import datetime
from app.db.mongodb import connect_to_mongo, close_mongo_connection, get_database
from app.models.trace import StepType, TraceStatus, TokenUsage
from app.schemas.trace import TraceCreate, StepCreate, ToolCallCreate
from app.services.trace_service import TraceService
from app.services.step_service import StepService
from app.services.tool_service import ToolService
from app.services.dag_service import DAGService


async def seed():
    print("Connecting to MongoDB...")
    await connect_to_mongo()
    db = get_database()
    if db is None:
        print("Failed to connect to MongoDB.")
        return

    trace_svc = TraceService(db)
    step_svc = StepService(db)
    tool_svc = ToolService(db)
    dag_svc = DAGService(db)

    print("Creating sample AgentTrace session...")
    trace = await trace_svc.create_trace(TraceCreate(
        agent_name="MarketIntelligenceAgent-v2",
        session_id="sess_alpha_2026",
        meta_info={"environment": "production", "model": "gemini-1.5-pro", "orchestrator": "langgraph"}
    ))
    trace_id = trace.trace_id
    print(f"Created trace: {trace_id}")

    # Step 1: User Request / Initial Thought
    s1 = await step_svc.add_step(trace_id, StepCreate(
        step_type=StepType.THOUGHT,
        name="Analyze Financial Query & Plan Steps",
        status=TraceStatus.COMPLETED,
        inputs={"user_prompt": "Analyze semiconductor AI revenue growth and generate summary."},
        outputs={"plan": ["Search quarterly filings", "Parse revenue table", "Calculate YoY metric"]},
        latency_ms=115.0
    ))

    # Step 2: LLM Planning Call
    s2 = await step_svc.add_step(trace_id, StepCreate(
        parent_step_id=s1.step_id,
        step_type=StepType.LLM_CALL,
        name="LLM: Function & Tool Calling Router",
        status=TraceStatus.COMPLETED,
        inputs={"system_prompt": "You are a financial research assistant.", "temperature": 0.2},
        outputs={"selected_tools": ["search_web", "sec_filing_parser"]},
        tokens=TokenUsage(prompt_tokens=520, completion_tokens=140, total_tokens=660),
        latency_ms=480.0
    ))

    # Step 3: Tool Execution - Web Search (Branch A)
    s3 = await step_svc.add_step(trace_id, StepCreate(
        parent_step_id=s2.step_id,
        step_type=StepType.TOOL_CALL,
        name="Tool: Web Search Intelligence",
        status=TraceStatus.COMPLETED,
        inputs={"query": "Semiconductor Q3 AI accelerator revenue report"},
        outputs={"snippets_found": 4},
        latency_ms=310.0
    ))
    await tool_svc.record_tool_call(trace_id, s3.step_id, ToolCallCreate(
        tool_name="SearchWeb",
        arguments={"query": "Semiconductor Q3 AI datacenter revenue 2026"},
        result={"status": 200, "top_url": "https://sec.gov/edgar/data/market-summary.html"},
        latency_ms=290.0,
        status="success"
    ))

    # Step 4: Subagent Spawn - SEC Filing Deep Search (Branch B)
    s4 = await step_svc.add_step(trace_id, StepCreate(
        parent_step_id=s2.step_id,
        step_type=StepType.SUBAGENT_SPAWN,
        name="Subagent: SECFilingParserWorker",
        status=TraceStatus.COMPLETED,
        inputs={"target_form": "10-Q", "fiscal_year": "2026"},
        outputs={"parsed_tables": 3, "datacenter_segment_b": 18.2},
        tokens=TokenUsage(prompt_tokens=1100, completion_tokens=320, total_tokens=1420),
        latency_ms=920.0
    ))

    # Step 5: Calculation Tool
    s5 = await step_svc.add_step(trace_id, StepCreate(
        parent_step_id=s3.step_id,
        step_type=StepType.TOOL_CALL,
        name="Tool: Python REPL YoY Computation",
        status=TraceStatus.COMPLETED,
        inputs={"code": "growth = ((18.2 - 14.5) / 14.5) * 100; round(growth, 2)"},
        outputs={"growth_rate": "25.52%"},
        latency_ms=85.0
    ))
    await tool_svc.record_tool_call(trace_id, s5.step_id, ToolCallCreate(
        tool_name="PythonRepl",
        arguments={"code": "((18.2 - 14.5) / 14.5) * 100"},
        result={"output": 25.51724},
        latency_ms=75.0,
        status="success"
    ))

    # Step 6: Synthesis Thought
    s6 = await step_svc.add_step(trace_id, StepCreate(
        parent_step_id=s4.step_id,
        step_type=StepType.THOUGHT,
        name="Synthesize Branch Findings",
        status=TraceStatus.COMPLETED,
        inputs={"branch_a": s5.step_id, "branch_b": s4.step_id},
        outputs={"ready_for_final_response": True},
        latency_ms=90.0
    ))

    # Step 7: Final LLM Synthesis
    s7 = await step_svc.add_step(trace_id, StepCreate(
        parent_step_id=s6.step_id,
        step_type=StepType.LLM_CALL,
        name="LLM: Final Executive Briefing Generator",
        status=TraceStatus.COMPLETED,
        inputs={"context_tokens": 1620},
        outputs={"summary": "Datacenter revenue reached $18.2B, a 25.52% YoY surge driven by accelerator demand."},
        tokens=TokenUsage(prompt_tokens=1620, completion_tokens=410, total_tokens=2030),
        latency_ms=640.0
    ))

    # Mark trace completed
    await trace_svc.update_trace(trace_id, TraceCreate(
        agent_name=trace.agent_name,
        session_id=trace.session_id,
        meta_info={"completed": True}
    ))

    # Retrieve and verify DAG graph
    dag = await dag_svc.build_dag_graph(trace_id)
    print("\n✓ Seed completed successfully!")
    print(f"Trace ID     : {trace_id}")
    print(f"Total Nodes  : {len(dag.nodes)}")
    print(f"Total Edges  : {len(dag.edges)}")
    print(f"Total Tools  : {dag.total_tools}")

    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(seed())
