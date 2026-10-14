# ⚛️ AgentTrace Frontend — Interactive DAG Execution Viewer

> High-performance React & SVG interactive Directed Acyclic Graph (DAG) visualizer for AI agent reasoning steps, tool calls, and token economics.

---

## 🚀 Features

- **Interactive Execution Graph Canvas**:
  - Dynamically renders nodes and smooth cubic bezier edges with auto-computed coordinates from the FastAPI DAG traversal engine.
  - Custom node badges and styling for `thought`, `llm_call`, `tool_call`, `subagent_spawn`, and `user_input`.
  - Latency badges directly mounted on edge midpoint nodes.
  - Fluid pan & zoom controls (scroll wheel, drag canvas, zoom controls, center view).
  - Floating minimap with real-time viewport bounding box.

- **Execution Timeline Replay Simulator**:
  - Step through multi-agent DAG execution step-by-step.
  - Play, Pause, Step Forward/Back, and Speed toggle (1x / 2x / 4x).
  - Active node glowing pulse animation during simulation playback.

- **Step Inspector & Tool Drawer**:
  - Slide-out glassmorphic panel upon selecting any node.
  - In-depth token breakdown (prompt vs completion tokens).
  - Formatted JSON payloads for step inputs and outputs.
  - Nested tool invocation cards with argument dictionaries and returned outputs.

- **Multi-Trace Cockpit**:
  - Switch between active agent sessions from the top bar.
  - Real-time KPI metrics: End-to-End Latency, Total Tokens, Cost ($USD), Total Steps, and Tool Invocations.
  - Zero-friction fallback to realistic mock datasets when backend is offline.

---

## 🛠️ Development & Run

```bash
# Navigate to frontend directory
cd projects/agent-trace/frontend

# Install dependencies
npm install

# Run Vite development server
npm run dev
```

The frontend will start at `http://localhost:5174` and proxy backend requests to `http://localhost:8000`.
