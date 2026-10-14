import React, { useMemo } from 'react';
import { NodeCard } from './NodeCard';
import { Minimap } from './Minimap';

export function GraphCanvas({
  nodes = [],
  edges = [],
  selectedNode,
  onSelectNode,
  playbackStepIndex,
  canvasHook
}) {
  const {
    transform,
    isDragging,
    handleMouseDown,
    handleMouseMove,
    handleMouseUp,
    handleWheel,
    zoomIn,
    zoomOut,
    resetView
  } = canvasHook;

  // Build node lookup map for edge coordinate resolution
  const nodeMap = useMemo(() => {
    const map = new Map();
    nodes.forEach((n) => map.set(n.id, n));
    return map;
  }, [nodes]);

  // Compute curved bezier path coordinates for edges
  const renderedEdges = useMemo(() => {
    const NODE_WIDTH = 260;
    const NODE_HEIGHT = 80;

    return edges.map((edge) => {
      const srcNode = nodeMap.get(edge.source);
      const tgtNode = nodeMap.get(edge.target);
      if (!srcNode || !tgtNode) return null;

      const sx = srcNode.position.x + NODE_WIDTH;
      const sy = srcNode.position.y + NODE_HEIGHT / 2;
      const tx = tgtNode.position.x;
      const ty = tgtNode.position.y + NODE_HEIGHT / 2;

      const dx = Math.max(Math.abs(tx - sx) * 0.5, 40);
      const pathD = `M ${sx} ${sy} C ${sx + dx} ${sy}, ${tx - dx} ${ty}, ${tx} ${ty}`;

      const midX = (sx + tx) / 2;
      const midY = (sy + ty) / 2;

      return {
        ...edge,
        pathD,
        midX,
        midY
      };
    }).filter(Boolean);
  }, [edges, nodeMap]);

  return (
    <div
      className={`canvas-wrapper ${isDragging ? 'is-dragging' : ''}`}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onWheel={handleWheel}
    >
      {/* Background Dot Grid */}
      <div className="dag-grid" />

      {/* Main Transform Container */}
      <div
        style={{
          transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})`,
          transformOrigin: '0 0',
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none'
        }}
      >
        {/* SVG Connectors Layer */}
        <svg
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '4000px',
            height: '2500px',
            overflow: 'visible',
            pointerEvents: 'none'
          }}
        >
          <defs>
            <linearGradient id="edgeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#a855f7" stopOpacity="0.8" />
            </linearGradient>

            <marker
              id="arrowhead"
              markerWidth="8"
              markerHeight="6"
              refX="7"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 8 3, 0 6" fill="#a855f7" />
            </marker>
          </defs>

          {renderedEdges.map((edge) => (
            <g key={edge.id}>
              {/* Subtle background glow path */}
              <path
                d={edge.pathD}
                fill="none"
                stroke="#06b6d4"
                strokeWidth={5}
                strokeOpacity={0.15}
              />
              {/* Primary connector line */}
              <path
                d={edge.pathD}
                fill="none"
                stroke="url(#edgeGradient)"
                strokeWidth={2}
                strokeDasharray={edge.animated ? '6, 4' : 'none'}
                markerEnd="url(#arrowhead)"
              />
              {/* Latency badge on edge midpoint */}
              {edge.label && (
                <g transform={`translate(${edge.midX}, ${edge.midY})`}>
                  <rect
                    x={-24}
                    y={-10}
                    width={48}
                    height={20}
                    rx={10}
                    fill="#0f172a"
                    stroke="rgba(255, 255, 255, 0.15)"
                    strokeWidth={1}
                  />
                  <text
                    x={0}
                    y={3}
                    textAnchor="middle"
                    fill="#94a3b8"
                    fontSize={10}
                    fontFamily="monospace"
                  >
                    {edge.label}
                  </text>
                </g>
              )}
            </g>
          ))}
        </svg>

        {/* Nodes Layer */}
        <div style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'auto' }}>
          {nodes.map((node) => {
            const isSelected = selectedNode?.id === node.id;
            const isActivePlayback = playbackStepIndex !== null && node.data.step_index === playbackStepIndex;

            return (
              <NodeCard
                key={node.id}
                node={node}
                isSelected={isSelected}
                isActivePlayback={isActivePlayback}
                onSelect={onSelectNode}
              />
            );
          })}
        </div>
      </div>

      {/* Canvas Floating Viewport Controls */}
      <div className="canvas-floating-controls">
        <button className="control-btn" onClick={zoomIn} title="Zoom In (+)">
          ➕
        </button>
        <button className="control-btn" onClick={zoomOut} title="Zoom Out (-)">
          ➖
        </button>
        <button className="control-btn" onClick={resetView} title="Center View">
          🎯
        </button>
        <span style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: '#64748b', padding: '0 4px' }}>
          {Math.round(transform.scale * 100)}%
        </span>
      </div>

      {/* Minimap */}
      <Minimap nodes={nodes} transform={transform} />
    </div>
  );
}
