import api from './client';
import type { ScenarioRequest, ScenarioResponse } from '../features/scenario-planner/types';

export const runScenario = async (
  payload: ScenarioRequest,
  signal?: AbortSignal
): Promise<ScenarioResponse> => {
  const response = await api.post<ScenarioResponse>('/api/scenario/', payload, { signal });
  return response.data;
};

export type ScenarioStreamEvent =
  | ({ type: 'result' } & ScenarioResponse)
  | { type: 'done' }
  | { type: 'error'; message: string };

/**
 * Recalculates scenario yield predictions via SSE over POST /api/scenario/stream.
 */
export const streamScenario = async (
  payload: ScenarioRequest,
  onEvent: (event: ScenarioStreamEvent) => void,
  signal?: AbortSignal
): Promise<void> => {
  const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
  const token = localStorage.getItem('access_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${baseURL}/api/scenario/stream`, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
    signal,
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => null);
    const error: any = new Error(errorBody?.detail || `HTTP Error ${res.status}`);
    error.status = res.status;
    error.response = { status: res.status, data: errorBody };
    throw error;
  }

  if (!res.body) {
    throw new Error('No response body from server');
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      const parts = buffer.split('\n\n');
      buffer = parts.pop() ?? '';

      for (const part of parts) {
        const lines = part.split(/\r?\n/);
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data:')) {
            const dataStr = trimmed.slice(5).trim();
            if (dataStr) {
              try {
                const parsed = JSON.parse(dataStr) as ScenarioStreamEvent;
                onEvent(parsed);
              } catch (e) {
                console.error('Failed to parse SSE JSON in streamScenario:', dataStr, e);
              }
            }
          }
        }
      }
    }

    if (buffer.trim()) {
      const lines = buffer.split(/\r?\n/);
      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('data:')) {
          const dataStr = trimmed.slice(5).trim();
          if (dataStr) {
            try {
              const parsed = JSON.parse(dataStr) as ScenarioStreamEvent;
              onEvent(parsed);
            } catch (e) {
              console.error('Failed to parse SSE JSON from trailing buffer:', dataStr, e);
            }
          }
        }
      }
    }
  } catch (err: any) {
    if (signal?.aborted) {
      return;
    }
    throw err;
  }
};
