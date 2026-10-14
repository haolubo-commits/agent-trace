import { useState, useRef, useCallback } from 'react';

export function useGraphCanvas(initialScale = 0.85) {
  const [transform, setTransform] = useState({ x: 60, y: 120, scale: initialScale });
  const [isDragging, setIsDragging] = useState(false);
  const dragStartRef = useRef({ x: 0, y: 0 });

  const handleMouseDown = useCallback((e) => {
    // Only drag on left click and not clicking on interactive buttons/nodes
    if (e.button !== 0) return;
    if (e.target.closest('.dag-node') || e.target.closest('.control-btn') || e.target.closest('.step-drawer')) {
      return;
    }
    setIsDragging(true);
    dragStartRef.current = {
      x: e.clientX - transform.x,
      y: e.clientY - transform.y
    };
  }, [transform]);

  const handleMouseMove = useCallback((e) => {
    if (!isDragging) return;
    setTransform((prev) => ({
      ...prev,
      x: e.clientX - dragStartRef.current.x,
      y: e.clientY - dragStartRef.current.y
    }));
  }, [isDragging]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleWheel = useCallback((e) => {
    e.preventDefault();
    const zoomFactor = 1.08;
    const delta = e.deltaY < 0 ? zoomFactor : 1 / zoomFactor;

    setTransform((prev) => {
      const nextScale = Math.min(Math.max(prev.scale * delta, 0.25), 2.2);
      return {
        ...prev,
        scale: nextScale
      };
    });
  }, []);

  const zoomIn = useCallback(() => {
    setTransform((prev) => ({ ...prev, scale: Math.min(prev.scale * 1.2, 2.2) }));
  }, []);

  const zoomOut = useCallback(() => {
    setTransform((prev) => ({ ...prev, scale: Math.max(prev.scale / 1.2, 0.25) }));
  }, []);

  const resetView = useCallback(() => {
    setTransform({ x: 60, y: 120, scale: 0.85 });
  }, []);

  return {
    transform,
    isDragging,
    handleMouseDown,
    handleMouseMove,
    handleMouseUp,
    handleWheel,
    zoomIn,
    zoomOut,
    resetView,
    setTransform
  };
}
