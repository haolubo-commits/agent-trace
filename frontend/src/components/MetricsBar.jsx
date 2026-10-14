import React from 'react';

export function MetricsBar({ trace, totalSteps = 0, totalTools = 0 }) {
  if (!trace) return null;

  const totalTokens = trace.total_tokens?.total_tokens || 0;
  const promptTokens = trace.total_tokens?.prompt_tokens || 0;
  const completionTokens = trace.total_tokens?.completion_tokens || 0;
  const latencySec = (trace.latency_ms / 1000).toFixed(2);
  const cost = (trace.total_cost_usd || 0).toFixed(4);
  const isRunning = trace.status === 'running';

  return (
    <div className="metrics-strip">
      {/* Execution Status */}
      <div className="metric-card">
        <div
          className="metric-icon-box"
          style={{
            backgroundColor: isRunning ? 'rgba(245, 158, 11, 0.15)' : 'rgba(16, 185, 129, 0.15)',
            color: isRunning ? '#f59e0b' : '#10b981'
          }}
        >
          {isRunning ? '⚡' : '✓'}
        </div>
        <div className="metric-data">
          <span className="metric-label">Status</span>
          <span
            className="metric-value"
            style={{
              color: isRunning ? '#f59e0b' : '#10b981',
              textTransform: 'uppercase',
              fontSize: '0.85rem'
            }}
          >
            {trace.status}
          </span>
        </div>
      </div>

      {/* Latency */}
      <div className="metric-card">
        <div className="metric-icon-box" style={{ backgroundColor: 'rgba(6, 182, 212, 0.15)', color: '#06b6d4' }}>
          ⏱️
        </div>
        <div className="metric-data">
          <span className="metric-label">E2E Latency</span>
          <span className="metric-value">{latencySec}s</span>
        </div>
      </div>

      {/* Tokens */}
      <div className="metric-card">
        <div className="metric-icon-box" style={{ backgroundColor: 'rgba(168, 85, 247, 0.15)', color: '#a855f7' }}>
          🧠
        </div>
        <div className="metric-data">
          <span className="metric-label">Total Tokens</span>
          <span className="metric-value">
            {totalTokens.toLocaleString()}{' '}
            <span style={{ fontSize: '0.7rem', color: '#64748b', fontWeight: 400 }}>
              ({promptTokens} in / {completionTokens} out)
            </span>
          </span>
        </div>
      </div>

      {/* Total Cost */}
      <div className="metric-card">
        <div className="metric-icon-box" style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }}>
          💰
        </div>
        <div className="metric-data">
          <span className="metric-label">Cost (USD)</span>
          <span className="metric-value">${cost}</span>
        </div>
      </div>

      {/* Total DAG Nodes / Steps */}
      <div className="metric-card">
        <div className="metric-icon-box" style={{ backgroundColor: 'rgba(59, 130, 246, 0.15)', color: '#3b82f6' }}>
          🕸️
        </div>
        <div className="metric-data">
          <span className="metric-label">Steps in DAG</span>
          <span className="metric-value">{totalSteps}</span>
        </div>
      </div>

      {/* Tool Invocations */}
      <div className="metric-card">
        <div className="metric-icon-box" style={{ backgroundColor: 'rgba(244, 63, 94, 0.15)', color: '#f43f5e' }}>
          ⚙️
        </div>
        <div className="metric-data">
          <span className="metric-label">Tool Calls</span>
          <span className="metric-value">{totalTools}</span>
        </div>
      </div>

      {/* Agent & Model Info */}
      <div className="metric-card" style={{ marginLeft: 'auto', minWidth: 'auto' }}>
        <div className="metric-data" style={{ textAlign: 'right' }}>
          <span className="metric-label">Target Model</span>
          <span className="metric-value" style={{ fontSize: '0.8rem', color: '#06b6d4' }}>
            {trace.meta_info?.model || 'gpt-4o'}
          </span>
        </div>
      </div>
    </div>
  );
}
