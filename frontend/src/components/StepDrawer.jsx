import React from 'react';

export function StepDrawer({ selectedNode, onClose }) {
  if (!selectedNode) return null;

  const { data } = selectedNode;
  const promptTokens = data.tokens?.prompt_tokens || 0;
  const completionTokens = data.tokens?.completion_tokens || 0;
  const totalTokens = data.tokens?.total_tokens || 0;

  return (
    <aside className="step-drawer">
      <div className="drawer-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '1rem', fontWeight: 700, color: '#f1f5f9' }}>
            Step #{data.step_index ?? 0} Details
          </span>
          <span
            style={{
              fontSize: '0.7rem',
              padding: '2px 8px',
              borderRadius: '9999px',
              backgroundColor: data.status === 'completed' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
              color: data.status === 'completed' ? '#10b981' : '#f59e0b',
              fontWeight: 600,
              textTransform: 'uppercase'
            }}
          >
            {data.status}
          </span>
        </div>

        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#94a3b8',
            cursor: 'pointer',
            fontSize: '1.2rem',
            padding: '4px'
          }}
          title="Close Drawer"
        >
          ✕
        </button>
      </div>

      <div className="drawer-content">
        {/* Step Title & Type */}
        <div>
          <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>
            Step Name & Action
          </span>
          <p style={{ fontSize: '0.95rem', fontWeight: 600, color: '#f1f5f9', marginTop: '4px' }}>
            {data.name}
          </p>
        </div>

        {/* Token Metrics */}
        <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.8rem' }}>
            <span style={{ color: '#94a3b8' }}>Prompt Tokens</span>
            <span style={{ fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>{promptTokens}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.8rem' }}>
            <span style={{ color: '#94a3b8' }}>Completion Tokens</span>
            <span style={{ fontFamily: 'var(--font-mono)', color: '#a855f7' }}>{completionTokens}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '8px', fontSize: '0.85rem', fontWeight: 600 }}>
            <span style={{ color: '#f1f5f9' }}>Total Tokens</span>
            <span style={{ fontFamily: 'var(--font-mono)', color: '#10b981' }}>{totalTokens}</span>
          </div>
        </div>

        {/* Latency */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Execution Latency</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: '#f1f5f9', fontWeight: 600 }}>
            {data.latency_ms?.toFixed(2)} ms
          </span>
        </div>

        {/* Tool Invocations if any */}
        {data.tools && data.tools.length > 0 && (
          <div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>
              Tool Calls ({data.tools.length})
            </span>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '6px' }}>
              {data.tools.map((tool, idx) => (
                <div
                  key={idx}
                  style={{
                    background: 'rgba(244, 63, 94, 0.05)',
                    border: '1px solid rgba(244, 63, 94, 0.2)',
                    borderRadius: '8px',
                    padding: '10px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 600, color: '#f43f5e', marginBottom: '4px' }}>
                    <span>⚙️ {tool.tool_name}</span>
                    <span>{tool.latency_ms?.toFixed(0)} ms</span>
                  </div>
                  <div className="code-block" style={{ marginTop: '6px', fontSize: '0.72rem' }}>
                    {JSON.stringify({ arguments: tool.arguments, result: tool.result }, null, 2)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Inputs */}
        <div>
          <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>
            Inputs / Context Payload
          </span>
          <div className="code-block" style={{ marginTop: '6px' }}>
            {JSON.stringify(data.inputs || {}, null, 2)}
          </div>
        </div>

        {/* Outputs */}
        <div>
          <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>
            Outputs / State Delta
          </span>
          <div className="code-block" style={{ marginTop: '6px', color: '#a7f3d0' }}>
            {JSON.stringify(data.outputs || {}, null, 2)}
          </div>
        </div>

        {/* Error message if present */}
        {data.error_message && (
          <div style={{ background: 'rgba(244, 63, 94, 0.1)', border: '1px solid #f43f5e', borderRadius: '8px', padding: '12px' }}>
            <span style={{ color: '#f43f5e', fontWeight: 600, fontSize: '0.8rem' }}>Execution Error</span>
            <p style={{ color: '#fecdd3', fontSize: '0.8rem', marginTop: '4px', fontFamily: 'var(--font-mono)' }}>
              {data.error_message}
            </p>
          </div>
        )}
      </div>
    </aside>
  );
}
