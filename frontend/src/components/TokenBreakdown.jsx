import React from 'react';

export function TokenBreakdown({ tokens = {} }) {
  const prompt = tokens.prompt_tokens || 0;
  const completion = tokens.completion_tokens || 0;
  const total = tokens.total_tokens || prompt + completion || 1;

  const promptPct = Math.round((prompt / total) * 100);
  const completionPct = 100 - promptPct;

  return (
    <div style={{ padding: '8px 12px', background: 'rgba(15, 23, 42, 0.4)', borderRadius: '8px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '4px', color: '#94a3b8' }}>
        <span>Prompt: {prompt.toLocaleString()} ({promptPct}%)</span>
        <span>Completion: {completion.toLocaleString()} ({completionPct}%)</span>
      </div>
      <div style={{ height: '6px', width: '100%', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '3px', overflow: 'hidden', display: 'flex' }}>
        <div style={{ width: `${promptPct}%`, background: '#06b6d4', transition: 'width 0.3s ease' }} />
        <div style={{ width: `${completionPct}%`, background: '#a855f7', transition: 'width 0.3s ease' }} />
      </div>
    </div>
  );
}
