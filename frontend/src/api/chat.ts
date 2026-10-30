
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
  history?: Array<{
    role: 'user' | 'assistant';
    content: string;
  }>;
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
  | { type: 'replace'; text: string }
  | { type: 'sources'; sources: string[] }
  | {
      type: 'done';
      conversation_id?: string;
      tools_used?: string[];
      trace_steps?: string[];
    }
  | { type: 'error'; message: string };

export const sendChatMessage = async (
  payload: SendChatRequest,
  signal?: AbortSignal
): Promise<SendChatResponse> => {
  const endpoint = payload.agent_mode
    ? '/api/chat/agent'
    : '/api/chat';

  const response = await api.post<SendChatResponse>(
    endpoint,
    payload,
    { signal }
  );

  return response.data;
};

export const getGraphStatus = async (): Promise<{
  status: string;
  uri?: string;
}> => {
  try {
    const response = await api.get('/api/chat/graph/status');
    return response.data;
  } catch {
    return { status: 'disconnected' };
  }
};

function processSSEBlock(
  block: string,
  onEvent: (event: ChatStreamEvent) => void
): void {

  const dataLines = block
    .split(/\r?\n/)
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice(5).replace(/^ /, ''));

  if (!dataLines.length) return;

  const data = dataLines.join('\n').trim();

  if (!data || data === '[DONE]') return;

  try {
    const event = JSON.parse(data) as ChatStreamEvent;
    onEvent(event);
  } catch (error) {
    console.error('Invalid chat SSE event:', data, error);
  }
}

export const streamChat = async (
  payload: SendChatRequest,
  onEvent: (event: ChatStreamEvent) => void,
  signal?: AbortSignal
): Promise<void> => {

  const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

  const token = localStorage.getItem('access_token');

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'text/event-stream',
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(
    `${baseURL}/api/chat/stream`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
      signal,
    }
  );

  if (!response.ok) {

    const body = await response.json().catch(() => null);

    const error = new Error(
      body?.detail || `Chat request failed: HTTP ${response.status}`
    ) as Error & {
      status?: number;
      response?: unknown;
    };

    error.status = response.status;

    error.response = {
      status: response.status,
      data: body,
    };

    throw error;
  }

  if (!response.body) {
    throw new Error('The server returned an empty response stream.');
  }

  const reader = response.body.getReader();

  const decoder = new TextDecoder('utf-8');

  let buffer = '';

  try {

    while (true) {

      const { value, done } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, {
        stream: true,
      });

      const blocks = buffer.split(/\r?\n\r?\n/);

      buffer = blocks.pop() ?? '';

      for (const block of blocks) {
        processSSEBlock(block, onEvent);
      }
    }

    // Flush remaining UTF-8 characters.
    buffer += decoder.decode();

    if (buffer.trim()) {
      processSSEBlock(buffer, onEvent);
    }

  } catch (error) {

    if (signal?.aborted) return;

    throw error;

  } finally {

    reader.releaseLock();
  }
};
