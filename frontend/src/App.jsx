import React, { useState } from 'react';
import { useTraceData } from './hooks/useTraceData';
import { useGraphCanvas } from './hooks/useGraphCanvas';
import { Header } from './components/Header';
import { MetricsBar } from './components/MetricsBar';
import { GraphCanvas } from './components/GraphCanvas';
import { StepDrawer } from './components/StepDrawer';
import { PlaybackControls } from './components/PlaybackControls';

export function App() {
  const {
    traces,
    activeTraceId,
    graphData,
    loading,
    error,
    selectTrace
  } = useTraceData();

  const canvasHook = useGraphCanvas(0.85);

  const [selectedNode, setSelectedNode] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackStepIndex, setPlaybackStepIndex] = useState(null);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);

  const nodes = graphData?.nodes || [];
  const edges = graphData?.edges || [];
  const trace = graphData?.trace || traces.find((t) => t.trace_id === activeTraceId);

  // Sync playback index with selected node when advancing
  const handleStepIndexChange = (newIndex) => {
    setPlaybackStepIndex(newIndex);
    const targetNode = nodes.find((n) => n.data.step_index === newIndex);
    if (targetNode) {
      setSelectedNode(targetNode);
    }
  };

  const handleResetPlayback = () => {
    setIsPlaying(false);
    setPlaybackStepIndex(0);
    if (nodes.length > 0) {
      const first = nodes.find((n) => n.data.step_index === 0) || nodes[0];
      setSelectedNode(first);
    }
  };

  return (
    <div className="app-container">
      {/* Top Navigation & Session Switcher */}
      <Header
        traces={traces}
        activeTraceId={activeTraceId}
        onSelectTrace={(id) => {
          selectTrace(id);
          setSelectedNode(null);
          setPlaybackStepIndex(null);
          setIsPlaying(false);
        }}
        isLive={!error}
      />

      {/* Metrics & Token Cockpit */}
      <MetricsBar
        trace={trace}
        totalSteps={graphData?.total_steps || nodes.length}
        totalTools={graphData?.total_tools || 0}
      />

      {/* Main Interactive Execution DAG Canvas */}
      <GraphCanvas
        nodes={nodes}
        edges={edges}
        selectedNode={selectedNode}
        onSelectNode={(node) => setSelectedNode(node)}
        playbackStepIndex={playbackStepIndex}
        canvasHook={canvasHook}
      />

      {/* Playback Simulation Toolbar */}
      <PlaybackControls
        isPlaying={isPlaying}
        setIsPlaying={setIsPlaying}
        currentStepIndex={playbackStepIndex ?? 0}
        setCurrentStepIndex={handleStepIndexChange}
        totalSteps={nodes.length}
        speed={playbackSpeed}
        setSpeed={setPlaybackSpeed}
        onReset={handleResetPlayback}
      />

      {/* Step & Tool Inspector Slide-Out Drawer */}
      {selectedNode && (
        <StepDrawer
          selectedNode={selectedNode}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </div>
  );
}

export default App;
