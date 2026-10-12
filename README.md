# 🕸️ AgentTrace — AI Agent Observability & Tool Execution DAG

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB%20Motor-47A248.svg?style=flat&logo=mongodb)](https://www.mongodb.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?style=flat&logo=python)](https://python.org)
[![React Flow](https://img.shields.io/badge/Graph-React%20Flow-ff0072.svg?style=flat)](https://reactflow.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **AgentTrace** is a high-performance observability and execution graph visualizer for autonomous AI agents. It models multi-agent workflows, tool calls, reasoning steps, and token economics as an interactive **Directed Acyclic Graph (DAG)** backed by MongoDB's document store.

---

## 🏗️ Architecture & Execution DAG

```mermaid
graph TD
    AgentSession[Agent Run Session] --> Step1["Thought: Analyze Query (P50: 120ms)"]
    Step1 --> Step2["LLM Call: Function Selection (Tokens: 512)"]
    Step2 --> ToolA["Tool: SearchWeb(query='latest filings')"]
    Step2 --> ToolB["Tool: PythonRepl(code='calc_ratio()')"]
    ToolA --> Step3["Subagent Spawn: ResearchSummarizer"]
    ToolB --> Step4["State Aggregator & Response Synthesis"]
    Step3 --> Step4
    Step4 --> MongoStore[("MongoDB (Traces, Steps, ToolCalls)")]

    MongoStore --> AggAPI[FastAPI Aggregation Engine]
    AggAPI --> ReactFlowUI[React Flow Visual DAG Viewer]
```

---

## 🌟 Key Features (4-Day Sprint Roadmap)

- [x] **Day 1: Scaffolding & Architecture**: MongoDB schema design, asynchronous Motor connection lifecycle, Pydantic v2 execution graph models, and configuration.
- [ ] **Day 2: Trace Ingestion & DAG Traversal APIs**: Streaming step ingestion endpoints, tool execution logging, DAG topological tree builder, and trace status management.
- [ ] **Day 3: Interactive React Flow DAG Viewer**: Node-based graph canvas, step timeline inspector, token cost break-down, and tool payload drawers.
- [ ] **Day 4: Aggregation Pipelines, Tests & Docker**: MongoDB analytics pipelines (token bottlenecks, error rates, p95 latencies), Pytest integration suites, and Docker Compose environment.

---

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- MongoDB 6.0+ (local instance or Docker container)

### Setup
```bash
# Clone the repository
git clone https://github.com/haolubo-commits/agent-trace.git
cd agent-trace/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the API server
uvicorn app.main:app --reload --port 8000
```

---

## 📑 API Endpoints Preview

- `GET /health` — Service uptime and MongoDB connection health status.
- `POST /api/v1/traces/` — Initialize new agent execution trace session.
- `POST /api/v1/traces/{trace_id}/steps/` — Append step or tool execution node to trace DAG.
- `GET /api/v1/traces/{trace_id}/graph` — Retrieve full DAG hierarchy with node dependencies and metrics.
