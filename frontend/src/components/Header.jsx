import React from 'react';

export function Header({ traces, activeTraceId, onSelectTrace, isLive }) {
  const activeTrace = traces.find((t) => t.trace_id === activeTraceId);

  return (
    <header className="header">
      <div className="logo-group">
        <div className="logo-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="18" cy="5" r="3" />
            <circle cx="6" cy="12" r="3" />
            <circle cx="18" cy="19" r="3" />
            <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
            <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
          </svg>
        </div>
        <span className="brand-title">AgentTrace</span>
        <span className="brand-badge">DAG OBSERVER</span>
      </div>

      <div className="header-actions">
        {/* Session / Trace Selector */}
        <div className="trace-selector">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
          <select
            className="trace-dropdown"
            value={activeTraceId}
            onChange={(e) => onSelectTrace(e.target.value)}
          >
            {traces.map((trace) => (
              <option key={trace.trace_id} value={trace.trace_id}>
                {trace.agent_name} ({trace.session_id})
              </option>
            ))}
          </select>
        </div>

        {/* Live / Mock Indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: '#94a3b8' }}>
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: isLive ? '#10b981' : '#06b6d4',
              boxShadow: isLive ? '0 0 8px #10b981' : '0 0 8px #06b6d4',
              display: 'inline-block'
            }}
          />
          <span>{isLive ? 'Live Engine' : 'DAG Replay Mode'}</span>
        </div>
      </div>
    </header>
  );
}
