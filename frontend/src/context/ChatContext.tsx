import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react';
import axios from 'axios';
import { sendChatMessage } from '../api/chat';
import type { ChatMessageItem, ChatContextPayload } from '../api/chat';

interface ChatContextType {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  toggleChat: () => void;
  messages: ChatMessageItem[];
  loading: boolean;
  isStreaming: boolean;
  cancelStream: () => void;
  stopConversation: () => void;
  error: string | null;
  isUnauthorized: boolean;
  hasUnread: boolean;
  lastFailedMessage: string | null;
  pageContext: ChatContextPayload;
  setPageContext: (ctx: ChatContextPayload) => void;
  conversationId: string | null;
  sendMessage: (content: string) => Promise<void>;
  retryLastMessage: () => Promise<void>;
  startNewChat: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isOpen, setIsOpenState] = useState(false);
  const [messages, setMessages] = useState<ChatMessageItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUnauthorized, setIsUnauthorized] = useState(false);
  const [hasUnread, setHasUnread] = useState(false);
  const [lastFailedMessage, setLastFailedMessage] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [pageContext, setPageContext] = useState<ChatContextPayload>({});

  const abortControllerRef = useRef<AbortController | null>(null);
  const isOpenRef = useRef(isOpen);

  useEffect(() => {
    isOpenRef.current = isOpen;
  }, [isOpen]);

  const setIsOpen = useCallback((open: boolean) => {
    setIsOpenState(open);
    if (open) {
      setHasUnread(false);
    }
  }, []);

  const toggleChat = useCallback(() => {
    setIsOpenState((prev) => {
      const next = !prev;
      if (next) {
        setHasUnread(false);
      }
      return next;
    });
  }, []);

  const stopConversation = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
    setLoading(false);
    setError(null);
  }, []);

  const cancelStream = stopConversation;

  const startNewChat = useCallback(() => {
    stopConversation();
    setMessages([]);
    setConversationId(null);
    setError(null);
    setIsUnauthorized(false);
    setLastFailedMessage(null);
  }, [stopConversation]);

  const sendMessage = useCallback(
    async (content: string) => {
      const trimmed = content.trim();
      if (!trimmed || loading || isStreaming) return;

      const userMsg: ChatMessageItem = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: trimmed,
        timestamp: Date.now(),
      };

      const currentHistory = [...messages, userMsg];
      setMessages(currentHistory);
      setLoading(true);
      setError(null);
      setIsUnauthorized(false);
      setLastFailedMessage(null);

      const historyPayload = currentHistory.slice(-6).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const activeConvId =
        conversationId ||
        (typeof crypto !== 'undefined' && crypto.randomUUID
          ? crypto.randomUUID()
          : `conv-${Date.now()}`);

      if (!conversationId) {
        setConversationId(activeConvId);
      }

      // Initialize AbortController for user cancellation
      const controller = new AbortController();
      abortControllerRef.current = controller;

      // Send message to Agricultural AI Orchestrator
      try {
        const res = await sendChatMessage(
          {
            message: trimmed,
            conversation_id: activeConvId,
            history: historyPayload,
            context: Object.keys(pageContext).length > 0 ? pageContext : undefined,
          },
          controller.signal
        );

        if (res.conversation_id) {
          setConversationId(res.conversation_id);
        }

        const assistantMsg: ChatMessageItem = {
          id: `asst-${Date.now()}`,
          role: 'assistant',
          content: res.reply,
          sources: [],
          timestamp: Date.now(),
        };

        setMessages((prev) => [...prev, assistantMsg]);

        if (!isOpenRef.current) {
          setHasUnread(true);
        }
      } catch (err: unknown) {
        if (axios.isCancel(err) || (err instanceof Error && err.name === 'CanceledError')) {
          // User intentionally stopped the conversation
          return;
        }
        if (axios.isAxiosError(err) && err.response?.status === 401) {
          setIsUnauthorized(true);
        } else {
          setError('উত্তর আনা যায়নি');
          setLastFailedMessage(trimmed);
        }
      } finally {
        setLoading(false);
        abortControllerRef.current = null;
      }
    },
    [loading, isStreaming, messages, conversationId, pageContext]
  );

  const retryLastMessage = useCallback(async () => {
    if (!lastFailedMessage) return;
    setError(null);
    setIsUnauthorized(false);
    await sendMessage(lastFailedMessage);
  }, [lastFailedMessage, sendMessage]);

  return (
    <ChatContext.Provider
      value={{
        isOpen,
        setIsOpen,
        toggleChat,
        messages,
        loading,
        isStreaming,
        cancelStream,
        stopConversation,
        error,
        isUnauthorized,
        hasUnread,
        lastFailedMessage,
        pageContext,
        setPageContext,
        conversationId,
        sendMessage,
        retryLastMessage,
        startNewChat,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
