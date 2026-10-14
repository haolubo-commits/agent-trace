import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';

export function useTraceData() {
  const [traces, setTraces] = useState([]);
  const [activeTraceId, setActiveTraceId] = useState('');
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load initial trace list
  useEffect(() => {
    let mounted = true;
    async function loadInitial() {
      setLoading(true);
      try {
        const traceList = await apiService.getTraces();
        if (mounted) {
          setTraces(traceList);
          if (traceList.length > 0) {
            setActiveTraceId(traceList[0].trace_id);
          }
        }
      } catch (err) {
        if (mounted) setError(err.message);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    loadInitial();
    return () => { mounted = false; };
  }, []);

  // Load graph when activeTraceId changes
  useEffect(() => {
    if (!activeTraceId) return;
    let mounted = true;

    async function fetchGraph() {
      try {
        const graph = await apiService.getTraceGraph(activeTraceId);
        if (mounted) {
          setGraphData(graph);
        }
      } catch (err) {
        if (mounted) setError(err.message);
      }
    }
    fetchGraph();
    return () => { mounted = false; };
  }, [activeTraceId]);

  const selectTrace = useCallback((traceId) => {
    setActiveTraceId(traceId);
  }, []);

  const refresh = useCallback(async () => {
    if (!activeTraceId) return;
    try {
      const graph = await apiService.getTraceGraph(activeTraceId);
      setGraphData(graph);
    } catch (err) {
      console.error('Refresh failed:', err);
    }
  }, [activeTraceId]);

  return {
    traces,
    activeTraceId,
    graphData,
    loading,
    error,
    selectTrace,
    refresh
  };
}
