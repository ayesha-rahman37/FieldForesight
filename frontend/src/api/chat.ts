import api from './client';

export interface ChatContextPayload {
  crop?: string;
  region?: string;
  predicted_yield?: number | null;
}

export interface ChatMessageItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  tools_used?: string[];
  trace_steps?: string[];
  timestamp: number;
  isPartial?: boolean;
  hasError?: boolean;
}

export interface SendChatRequest {
  message: string;
  conversation_id?: string;
  history?: Array<{ role: 'user' | 'assistant'; content: string }>;
  context?: ChatContextPayload;
  agent_mode?: boolean;
}

export interface SendChatResponse {
  reply: string;
  conversation_id?: string;
  sources?: string[];
  tools_used?: string[];
  trace_steps?: string[];
}

export type ChatStreamEvent =
  | { type: 'token'; text: string }
  | { type: 'sources'; sources: string[] }
  | { type: 'done' }
  | { type: 'error'; message: string };

/**
 * Sends a message to the AI Chat API (non-streaming full reply).
 */
export const sendChatMessage = async (
  payload: SendChatRequest,
  signal?: AbortSignal
): Promise<SendChatResponse> => {
  const endpoint = payload.agent_mode ? '/api/chat/agent' : '/api/chat';
  const response = await api.post<SendChatResponse>(endpoint, payload, { signal });
  return response.data;
};

/**
 * Checks connectivity status of Neo4j Graph Database.
 */
export const getGraphStatus = async (): Promise<{ status: string; uri?: string }> => {
  try {
    const res = await api.get('/api/chat/graph/status');
    return res.data;
  } catch {
    return { status: 'disconnected' };
  }
};

/**
 * Sends a message to the AI Chat API and streams tokens via SSE over POST.
 */
export const streamChat = async (
  payload: SendChatRequest,
  onEvent: (event: ChatStreamEvent) => void,
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

  const res = await fetch(`${baseURL}/api/chat/stream`, {
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
                const parsed = JSON.parse(dataStr) as ChatStreamEvent;
                onEvent(parsed);
              } catch (e) {
                console.error('Failed to parse SSE JSON:', dataStr, e);
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
              const parsed = JSON.parse(dataStr) as ChatStreamEvent;
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
