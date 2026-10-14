/**
 * Realistic Mock Datasets for AgentTrace execution DAG visualization.
 * Provides fallback data for standalone frontend development and demo showcases.
 */

export const MOCK_TRACES = [
  {
    trace_id: "trc_alpha_market_8921",
    agent_name: "FinancialAnalysisAgent",
    session_id: "sess_user_wealth_401",
    status: "completed",
    total_tokens: {
      prompt_tokens: 3840,
      completion_tokens: 920,
      total_tokens: 4760
    },
    latency_ms: 1845.2,
    total_cost_usd: 0.0428,
    start_time: "2026-10-14T09:12:00.000Z",
    end_time: "2026-10-14T09:12:01.845Z",
    meta_info: {
      model: "claude-3-7-sonnet",
      temperature: 0.2,
      max_iterations: 8
    }
  },
  {
    trace_id: "trc_beta_code_review_3102",
    agent_name: "AutonomousCodeReviewer",
    session_id: "sess_pr_audit_109",
    status: "running",
    total_tokens: {
      prompt_tokens: 6120,
      completion_tokens: 1450,
      total_tokens: 7570
    },
    latency_ms: 3210.5,
    total_cost_usd: 0.0681,
    start_time: "2026-10-14T09:45:10.000Z",
    end_time: null,
    meta_info: {
      model: "gpt-4o",
      repo: "enterprise-core-engine",
      pr_id: "#482"
    }
  }
];

export const MOCK_DAG_GRAPHS = {
  trc_alpha_market_8921: {
    trace: MOCK_TRACES[0],
    total_steps: 6,
    total_tools: 3,
    nodes: [
      {
        id: "step_01_input",
        type: "inputNode",
        position: { x: 80, y: 160 },
        data: {
          step_id: "step_01_input",
          name: "User Request: Analyze Q3 Tech Semiconductor Margins",
          step_type: "user_input",
          status: "completed",
          step_index: 0,
          latency_ms: 12.0,
          tokens: { prompt_tokens: 45, completion_tokens: 0, total_tokens: 45 },
          inputs: { prompt: "Compare gross margins of NVDA vs TSM in Q3 2026 filings and summarize risks." },
          outputs: { validated: true, query_intent: "FINANCIAL_COMPARISON" },
          error_message: null,
          tools: [],
          tool_count: 0
        }
      },
      {
        id: "step_02_thought",
        type: "thoughtNode",
        position: { x: 400, y: 160 },
        data: {
          step_id: "step_02_thought",
          name: "Reasoning: Plan SEC EDGAR & Market Retrieval",
          step_type: "thought",
          status: "completed",
          step_index: 1,
          latency_ms: 145.0,
          tokens: { prompt_tokens: 320, completion_tokens: 95, total_tokens: 415 },
          inputs: { context: "Q3 2026 NVDA and TSM financial statements required" },
          outputs: {
            strategy: "Query 10-Q filing filings via EdgarAPI, then compute ratio with PythonRepl tool.",
            required_tools: ["SearchWeb", "PythonRepl"]
          },
          error_message: null,
          tools: [],
          tool_count: 0
        }
      },
      {
        id: "step_03_tool_search",
        type: "toolNode",
        position: { x: 720, y: 80 },
        data: {
          step_id: "step_03_tool_search",
          name: "Tool: SearchWeb(NVDA Q3 10-Q margins)",
          step_type: "tool_call",
          status: "completed",
          step_index: 2,
          latency_ms: 480.0,
          tokens: { prompt_tokens: 580, completion_tokens: 120, total_tokens: 700 },
          inputs: { query: "NVDA Q3 2026 gross margins GAAP non-GAAP" },
          outputs: { revenue: "$35.1B", gross_margin: "74.6%", data_source: "SEC EDGAR" },
          error_message: null,
          tools: [
            {
              tool_name: "SearchWeb",
              arguments: { query: "NVDA Q3 2026 gross margin" },
              result: { gross_margin: "74.6%", operating_income: "$21.8B" },
              latency_ms: 480.0,
              status: "success"
            }
          ],
          tool_count: 1
        }
      },
      {
        id: "step_04_tool_repl",
        type: "toolNode",
        position: { x: 720, y: 240 },
        data: {
          step_id: "step_04_tool_repl",
          name: "Tool: PythonRepl(calc_spread)",
          step_type: "tool_call",
          status: "completed",
          step_index: 3,
          latency_ms: 190.0,
          tokens: { prompt_tokens: 410, completion_tokens: 85, total_tokens: 495 },
          inputs: { code: "nvda_margin = 0.746\ntsm_margin = 0.578\nspread_bps = (nvda_margin - tsm_margin) * 10000" },
          outputs: { spread_basis_points: 1680, delta_percentage: "+16.8%" },
          error_message: null,
          tools: [
            {
              tool_name: "PythonRepl",
              arguments: { script: "delta = (0.746 - 0.578) * 10000; return delta" },
              result: { result: 1680.0, stdout: "Spread: 1680 bps" },
              latency_ms: 190.0,
              status: "success"
            }
          ],
          tool_count: 1
        }
      },
      {
        id: "step_05_subagent",
        type: "subagentNode",
        position: { x: 1040, y: 80 },
        data: {
          step_id: "step_05_subagent",
          name: "Subagent: RiskSynthesisWorker",
          step_type: "subagent_spawn",
          status: "completed",
          step_index: 4,
          latency_ms: 540.0,
          tokens: { prompt_tokens: 1100, completion_tokens: 310, total_tokens: 1410 },
          inputs: { task: "Evaluate geopolitical supply chain and packaging bottlenecks" },
          outputs: { risks: ["CoWoS packaging allocation constraints", "Taiwan fab concentration"] },
          error_message: null,
          tools: [
            {
              tool_name: "SupplyChainIndex",
              arguments: { ticker: "TSM", metric: "lead_time_weeks" },
              result: { lead_time: 26, stress_index: "ELEVATED" },
              latency_ms: 220.0,
              status: "success"
            }
          ],
          tool_count: 1
        }
      },
      {
        id: "step_06_llm_synth",
        type: "llmNode",
        position: { x: 1360, y: 160 },
        data: {
          step_id: "step_06_llm_synth",
          name: "LLM: Final Executive Synthesis",
          step_type: "llm_call",
          status: "completed",
          step_index: 5,
          latency_ms: 478.2,
          tokens: { prompt_tokens: 1385, completion_tokens: 310, total_tokens: 1695 },
          inputs: { full_context: "Merged findings from SEC filings, REPL spread calculations, and risk agent" },
          outputs: {
            executive_summary: "NVDA maintains a robust 1,680 bps margin premium over foundry partner TSM...",
            recommendation: "MONITOR_COWOS_CAPACITY"
          },
          error_message: null,
          tools: [],
          tool_count: 0
        }
      }
    ],
    edges: [
      { id: "e1_2", source: "step_01_input", target: "step_02_thought", animated: false, label: "12ms" },
      { id: "e2_3", source: "step_02_thought", target: "step_03_tool_search", animated: false, label: "145ms" },
      { id: "e2_4", source: "step_02_thought", target: "step_04_tool_repl", animated: false, label: "145ms" },
      { id: "e3_5", source: "step_03_tool_search", target: "step_05_subagent", animated: false, label: "480ms" },
      { id: "e4_6", source: "step_04_tool_repl", target: "step_06_llm_synth", animated: false, label: "190ms" },
      { id: "e5_6", source: "step_05_subagent", target: "step_06_llm_synth", animated: false, label: "540ms" }
    ]
  },
  trc_beta_code_review_3102: {
    trace: MOCK_TRACES[1],
    total_steps: 4,
    total_tools: 2,
    nodes: [
      {
        id: "step_b1_input",
        type: "inputNode",
        position: { x: 80, y: 140 },
        data: {
          step_id: "step_b1_input",
          name: "Git Webhook: PR #482 Opened",
          step_type: "user_input",
          status: "completed",
          step_index: 0,
          latency_ms: 18.0,
          tokens: { prompt_tokens: 80, completion_tokens: 0, total_tokens: 80 },
          inputs: { diff_url: "github.com/org/repo/pull/482.diff", author: "lead-dev" },
          outputs: { changed_files: 14, additions: 420, deletions: 85 },
          error_message: null,
          tools: [],
          tool_count: 0
        }
      },
      {
        id: "step_b2_thought",
        type: "thoughtNode",
        position: { x: 400, y: 140 },
        data: {
          step_id: "step_b2_thought",
          name: "Reasoning: Identify Security & Memory Leak Vectors",
          step_type: "thought",
          status: "completed",
          step_index: 1,
          latency_ms: 220.0,
          tokens: { prompt_tokens: 1840, completion_tokens: 310, total_tokens: 2150 },
          inputs: { ast_tree: "Python AST parsed, 3 async database connection pools altered" },
          outputs: { critical_audit_target: "Connection leakage inside generator loop" },
          error_message: null,
          tools: [],
          tool_count: 0
        }
      },
      {
        id: "step_b3_tool_ast",
        type: "toolNode",
        position: { x: 720, y: 140 },
        data: {
          step_id: "step_b3_tool_ast",
          name: "Tool: BanditStaticAnalysis(security_scan)",
          step_type: "tool_call",
          status: "completed",
          step_index: 2,
          latency_ms: 1420.0,
          tokens: { prompt_tokens: 2200, completion_tokens: 440, total_tokens: 2640 },
          inputs: { engine: "bandit", confidence: "HIGH", severity: "MEDIUM_PLUS" },
          outputs: { issues_detected: 0, warnings: 1 },
          error_message: null,
          tools: [
            {
              tool_name: "BanditStaticAnalysis",
              arguments: { target_dir: "backend/services" },
              result: { passed: true, issues_count: 0 },
              latency_ms: 1420.0,
              status: "success"
            }
          ],
          tool_count: 1
        }
      },
      {
        id: "step_b4_llm_eval",
        type: "llmNode",
        position: { x: 1040, y: 140 },
        data: {
          step_id: "step_b4_llm_eval",
          name: "LLM: Streaming PR Review Comments",
          step_type: "llm_call",
          status: "running",
          step_index: 3,
          latency_ms: 1552.5,
          tokens: { prompt_tokens: 2000, completion_tokens: 700, total_tokens: 2700 },
          inputs: { rules: "OWASP Top 10 + Concurrency Safety" },
          outputs: { status: "generating_markdown_comments" },
          error_message: null,
          tools: [],
          tool_count: 0
        }
      }
    ],
    edges: [
      { id: "eb1_2", source: "step_b1_input", target: "step_b2_thought", animated: false, label: "18ms" },
      { id: "eb2_3", source: "step_b2_thought", target: "step_b3_tool_ast", animated: false, label: "220ms" },
      { id: "eb3_4", source: "step_b3_tool_ast", target: "step_b4_llm_eval", animated: true, label: "streaming" }
    ]
  }
};
