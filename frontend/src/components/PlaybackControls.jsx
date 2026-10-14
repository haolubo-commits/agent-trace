import React, { useEffect } from 'react';

export function PlaybackControls({
  isPlaying,
  setIsPlaying,
  currentStepIndex,
  setCurrentStepIndex,
  totalSteps,
  speed,
  setSpeed,
  onReset
}) {
  useEffect(() => {
    let timer = null;
    if (isPlaying) {
      const interval = 1200 / speed;
      timer = setInterval(() => {
        setCurrentStepIndex((prev) => {
          if (prev >= totalSteps - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, interval);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isPlaying, speed, totalSteps, setIsPlaying, setCurrentStepIndex]);

  return (
    <div className="playback-bar">
      {/* Reset */}
      <button
        className="control-btn"
        onClick={onReset}
        title="Reset Replay"
        style={{ color: '#94a3b8' }}
      >
        ⏮️
      </button>

      {/* Step Back */}
      <button
        className="control-btn"
        disabled={currentStepIndex <= 0}
        onClick={() => setCurrentStepIndex((prev) => Math.max(0, prev - 1))}
        title="Previous Step"
      >
        ◀
      </button>

      {/* Play / Pause Primary Action */}
      <button
        className="play-action-btn"
        onClick={() => {
          if (currentStepIndex >= totalSteps - 1 && !isPlaying) {
            setCurrentStepIndex(0);
          }
          setIsPlaying(!isPlaying);
        }}
        title={isPlaying ? 'Pause' : 'Play Execution'}
      >
        {isPlaying ? '⏸' : '▶'}
      </button>

      {/* Step Forward */}
      <button
        className="control-btn"
        disabled={currentStepIndex >= totalSteps - 1}
        onClick={() => setCurrentStepIndex((prev) => Math.min(totalSteps - 1, prev + 1))}
        title="Next Step"
      >
        ▶
      </button>

      {/* Step Indicator */}
      <span className="playback-step-info">
        Step {totalSteps > 0 ? currentStepIndex + 1 : 0} of {totalSteps}
      </span>

      {/* Speed Selector */}
      <button
        className="control-btn"
        style={{ width: 'auto', padding: '0 8px', fontSize: '0.75rem', fontWeight: 600, color: '#38bdf8' }}
        onClick={() => {
          const speeds = [1, 2, 4];
          const nextIdx = (speeds.indexOf(speed) + 1) % speeds.length;
          setSpeed(speeds[nextIdx]);
        }}
        title="Replay Speed"
      >
        {speed}x
      </button>
    </div>
  );
}
