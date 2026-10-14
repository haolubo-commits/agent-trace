import React from 'react';

export function Minimap({ nodes = [], transform }) {
  if (nodes.length === 0) return null;

  // Compute bounding box of all nodes
  const xs = nodes.map((n) => n.position.x);
  const ys = nodes.map((n) => n.position.y);
  const minX = Math.min(...xs) - 40;
  const maxX = Math.max(...xs) + 300;
  const minY = Math.min(...ys) - 40;
  const maxY = Math.max(...ys) + 200;

  const width = Math.max(maxX - minX, 600);
  const height = Math.max(maxY - minY, 400);

  // Scaled coordinates inside 180x120 container
  const mapW = 180;
  const mapH = 120;
  const scaleX = mapW / width;
  const scaleY = mapH / height;

  return (
    <div className="minimap-container">
      <svg width={mapW} height={mapH} style={{ background: '#090d16' }}>
        {/* Draw node dots */}
        {nodes.map((node) => {
          const nx = (node.position.x - minX) * scaleX;
          const ny = (node.position.y - minY) * scaleY;
          return (
            <rect
              key={node.id}
              x={nx}
              y={ny}
              width={16}
              height={8}
              rx={2}
              fill="#06b6d4"
              opacity={0.8}
            />
          );
        })}

        {/* Viewport boundary indicator */}
        <rect
          x={Math.max(0, (-transform.x - minX) * scaleX * 0.5)}
          y={Math.max(0, (-transform.y - minY) * scaleY * 0.5)}
          width={Math.min(mapW, (window.innerWidth / transform.scale) * scaleX * 0.5)}
          height={Math.min(mapH, (window.innerHeight / transform.scale) * scaleY * 0.5)}
          fill="none"
          stroke="#a855f7"
          strokeWidth={1.5}
          strokeDasharray="3 3"
        />
      </svg>
    </div>
  );
}
