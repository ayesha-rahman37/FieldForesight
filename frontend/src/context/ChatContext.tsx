import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react';
import axios from 'axios';
import { sendChatMessage, streamChat } from '../api/chat';
import type { ChatMessageItem, ChatContextPayload } from '../api/chat';
import { CONFIG } from '../config';

interface ChatContextType {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  toggleChat: () => void;
  messages: ChatMessageItem[];
  loading: boolean;
  isStreaming: boolean;
  cancelStream: () => void;
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

  const cancelStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
    setLoading(false);
  }, []);

  const startNewChat = useCallback(() => {
    cancelStream();
    setMessages([]);
    setConversationId(null);
    setError(null);
    setIsUnauthorized(false);
    setLastFailedMessage(null);
  }, [cancelStream]);

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

      if (CONFIG.CHAT_STREAMING) {
        const controller = new AbortController();
        abortControllerRef.current = controller;
        setIsStreaming(true);

        let assistantMsgId: string | null = null;
        let accumulatedContent = '';

        try {
          await streamChat(
            {
              message: trimmed,
              conversation_id: activeConvId,
              history: historyPayload,
              context: Object.keys(pageContext).length > 0 ? pageContext : undefined,
            },
            (event) => {
              if (event.type === 'token') {
                if (!assistantMsgId) {
                  // First token received: create the assistant message bubble
                  assistantMsgId = `asst-${Date.now()}`;
                  accumulatedContent = event.text;
                  const newAsstMsg: ChatMessageItem = {
                    id: assistantMsgId,
                    role: 'assistant',
                    content: accumulatedContent,
                    timestamp: Date.now(),
                  };
                  setMessages((prev) => [...prev, newAsstMsg]);
                  setLoading(false); // Stop typing indicator
                  if (!isOpenRef.current) {
                    setHasUnread(true);
                  }
                } else {
                  accumulatedContent += event.text;
                  setMessages((prev) =>
                    prev.map((m) =>
                      m.id === assistantMsgId
                        ? { ...m, content: accumulatedContent }
                        : m
                    )
                  );
                }
              } else if (event.type === 'sources') {
                if (assistantMsgId) {
                  const sources = event.sources;
                  setMessages((prev) =>
                    prev.map((m) =>
                      m.id === assistantMsgId ? { ...m, sources } : m
                    )
                  );
                }
              } else if (event.type === 'error') {
                setError(event.message || 'উত্তর সম্পূর্ণ হয়নি');
                setLastFailedMessage(trimmed);
                if (assistantMsgId) {
                  setMessages((prev) =>
                    prev.map((m) =>
                      m.id === assistantMsgId
                        ? { ...m, isPartial: true, hasError: true }
                        : m
                    )
                  );
                }
              } else if (event.type === 'done') {
                if (!isOpenRef.current) {
                  setHasUnread(true);
                }
              }
            },
            controller.signal
          );
        } catch (err: any) {
          if (controller.signal.aborted) {
            // Cancelled by user
            if (assistantMsgId) {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsgId ? { ...m, isPartial: true } : m
                )
              );
            }
          } else if (err?.status === 401 || err?.response?.status === 401) {
            setIsUnauthorized(true);
          } else {
            // Midstream error or network drop
            if (assistantMsgId) {
              setError('উত্তর সম্পূর্ণ হয়নি');
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsgId
                    ? { ...m, isPartial: true, hasError: true }
                    : m
                )
              );
            } else {
              setError('উত্তর আনা যায়নি');
            }
            setLastFailedMessage(trimmed);
          }
        } finally {
          setIsStreaming(false);
          setLoading(false);
          abortControllerRef.current = null;
        }
      } else {
        // Non-streaming fallback
        try {
          const res = await sendChatMessage({
            message: trimmed,
            conversation_id: activeConvId,
            history: historyPayload,
            context: Object.keys(pageContext).length > 0 ? pageContext : undefined,
          });

          if (res.conversation_id) {
            setConversationId(res.conversation_id);
          }

          const assistantMsg: ChatMessageItem = {
            id: `asst-${Date.now()}`,
            role: 'assistant',
            content: res.reply,
            sources: res.sources,
            timestamp: Date.now(),
          };

          setMessages((prev) => [...prev, assistantMsg]);

          if (!isOpenRef.current) {
            setHasUnread(true);
          }
        } catch (err: unknown) {
          if (axios.isAxiosError(err) && err.response?.status === 401) {
            setIsUnauthorized(true);
          } else {
            setError('উত্তর আনা যায়নি');
            setLastFailedMessage(trimmed);
          }
        } finally {
          setLoading(false);
        }
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
