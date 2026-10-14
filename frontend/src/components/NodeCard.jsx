import React from 'react';

const NODE_THEMES = {
  inputNode: {
    badge: 'INPUT',
    color: '#10b981',
    bg: 'rgba(16, 185, 129, 0.12)',
    border: 'rgba(16, 185, 129, 0.3)',
    icon: '📥'
  },
  thoughtNode: {
    badge: 'THOUGHT',
    color: '#a855f7',
    bg: 'rgba(168, 85, 247, 0.12)',
    border: 'rgba(168, 85, 247, 0.3)',
    icon: '🧠'
  },
  toolNode: {
    badge: 'TOOL CALL',
    color: '#f43f5e',
    bg: 'rgba(244, 63, 94, 0.12)',
    border: 'rgba(244, 63, 94, 0.3)',
    icon: '⚙️'
  },
  subagentNode: {
    badge: 'SUBAGENT',
    color: '#06b6d4',
    bg: 'rgba(6, 182, 212, 0.12)',
    border: 'rgba(6, 182, 212, 0.3)',
    icon: '🌐'
  },
  llmNode: {
    badge: 'LLM GENERATION',
    color: '#3b82f6',
    bg: 'rgba(59, 130, 246, 0.12)',
    border: 'rgba(59, 130, 246, 0.3)',
    icon: '🤖'
  },
  customNode: {
    badge: 'STEP',
    color: '#94a3b8',
    bg: 'rgba(148, 163, 184, 0.12)',
    border: 'rgba(148, 163, 184, 0.3)',
    icon: '⚡'
  }
};

export function NodeCard({ node, isSelected, isActivePlayback, onSelect }) {
  const theme = NODE_THEMES[node.type] || NODE_THEMES.customNode;
  const { data } = node;
  const tokens = data.tokens?.total_tokens || 0;
  const latency = data.latency_ms ? `${data.latency_ms.toFixed(0)}ms` : '0ms';

  return (
    <div
      className={`dag-node ${isSelected ? 'selected' : ''} ${isActivePlayback ? 'is-active-playback' : ''}`}
      style={{
        left: `${node.position.x}px`,
        top: `${node.position.y}px`
      }}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(node);
      }}
    >
      <div className="node-header">
        <span
          className="node-type-badge"
          style={{
            backgroundColor: theme.bg,
            color: theme.color,
            border: `1px solid ${theme.border}`
          }}
        >
          <span>{theme.icon}</span>
          <span>{theme.badge}</span>
        </span>

        {/* Status Dot */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: data.status === 'completed' ? '#10b981' : data.status === 'failed' ? '#f43f5e' : '#f59e0b'
            }}
          />
          <span style={{ fontSize: '0.68rem', color: '#64748b', textTransform: 'uppercase' }}>
            #{data.step_index ?? 0}
          </span>
        </div>
      </div>

      <div className="node-name" title={data.name}>
        {data.name}
      </div>

      <div className="node-footer">
        <span>⏱️ {latency}</span>
        {tokens > 0 && <span>🧠 {tokens} tok</span>}
        {data.tool_count > 0 && (
          <span style={{ color: '#f43f5e' }}>
            ⚙️ {data.tool_count} {data.tool_count === 1 ? 'call' : 'calls'}
          </span>
        )}
      </div>
    </div>
  );
}
