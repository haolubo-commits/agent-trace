/**
 * AgentTrace API Service Layer
 * Connects to FastAPI backend (/api/v1) with seamless fallback to realistic mock datasets.
 */

import { MOCK_TRACES, MOCK_DAG_GRAPHS } from './mockData';

const BASE_URL = '/api/v1';

export const apiService = {
  /**
   * Fetches the list of all recorded agent traces.
   */
  async getTraces() {
    try {
      const res = await fetch(`${BASE_URL}/traces/?limit=50`, {
        headers: { 'Accept': 'application/json' },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return data && data.length > 0 ? data : MOCK_TRACES;
    } catch (err) {
      console.warn('Backend unavailable, using mock trace list:', err.message);
      return MOCK_TRACES;
    }
  },

  /**
   * Fetches the full React Flow DAG graph representation for a given trace.
   */
  async getTraceGraph(traceId) {
    try {
      const res = await fetch(`${BASE_URL}/traces/${traceId}/graph`, {
        headers: { 'Accept': 'application/json' },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.warn(`Backend unavailable, using mock graph for ${traceId}:`, err.message);
      return MOCK_DAG_GRAPHS[traceId] || MOCK_DAG_GRAPHS['trc_alpha_market_8921'];
    }
  },

  /**
   * Fetches single trace metadata.
   */
  async getTraceById(traceId) {
    try {
      const res = await fetch(`${BASE_URL}/traces/${traceId}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      const fallback = MOCK_TRACES.find((t) => t.trace_id === traceId);
      return fallback || MOCK_TRACES[0];
    }
  }
};
