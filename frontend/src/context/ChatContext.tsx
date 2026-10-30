
import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useRef,
  useEffect,
} from 'react';

import {
  streamChat,
} from '../api/chat';

import type {
  ChatMessageItem,
  ChatContextPayload,
  ChatStreamEvent,
} from '../api/chat';


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

const ChatContext = createContext<ChatContextType | undefined>(
  undefined
);


export const ChatProvider: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {

  const [isOpen, setIsOpenState] = useState(false);
  const [messages, setMessages] = useState<ChatMessageItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUnauthorized, setIsUnauthorized] = useState(false);
  const [hasUnread, setHasUnread] = useState(false);

  const [lastFailedMessage, setLastFailedMessage] =
    useState<string | null>(null);

  const [conversationId, setConversationId] =
    useState<string | null>(null);

  const [pageContext, setPageContext] =
    useState<ChatContextPayload>({});

  const abortControllerRef = useRef<AbortController | null>(null);
  const isOpenRef = useRef(isOpen);
  const busyRef = useRef(false);

  useEffect(() => {
    isOpenRef.current = isOpen;
  }, [isOpen]);


  // ==========================================================
  // CHAT WINDOW
  // ==========================================================

  const setIsOpen = useCallback((open: boolean) => {
    setIsOpenState(open);

    if (open) {
      setHasUnread(false);
    }
  }, []);

  const toggleChat = useCallback(() => {
    setIsOpenState((previous) => {
      const next = !previous;

      if (next) {
        setHasUnread(false);
      }

      return next;
    });
  }, []);


  // ==========================================================
  // STOP STREAMING
  // ==========================================================

  const stopConversation = useCallback(() => {

    abortControllerRef.current?.abort();
    abortControllerRef.current = null;

    busyRef.current = false;

    setLoading(false);
    setIsStreaming(false);

    setMessages((previous) =>
      previous.map((message) =>
        message.isPartial
          ? { ...message, isPartial: false }
          : message
      )
    );

  }, []);

  const cancelStream = stopConversation;


  // ==========================================================
  // NEW CHAT
  // ==========================================================

  const startNewChat = useCallback(() => {

    stopConversation();

    setMessages([]);
    setConversationId(null);
    setError(null);
    setIsUnauthorized(false);
    setLastFailedMessage(null);

  }, [stopConversation]);


  // ==========================================================
  // SEND MESSAGE WITH STREAMING
  // ==========================================================

  const sendMessage = useCallback(
    async (content: string) => {

      const trimmed = content.trim();

      if (!trimmed || busyRef.current) {
        return;
      }

      busyRef.current = true;

      const userMsg: ChatMessageItem = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: trimmed,
        timestamp: Date.now(),
      };

      const assistantId = `assistant-${Date.now()}`;

      const assistantMsg: ChatMessageItem = {
        id: assistantId,
        role: 'assistant',
        content: '',
        sources: [],
        tools_used: [],
        trace_steps: [],
        timestamp: Date.now(),
        isPartial: true,
      };

      const currentHistory = [
        ...messages,
        userMsg,
      ];

      setMessages([
        ...currentHistory,
        assistantMsg,
      ]);

      setLoading(true);
      setIsStreaming(true);
      setError(null);
      setIsUnauthorized(false);
      setLastFailedMessage(null);

      const historyPayload = currentHistory
        .slice(-6)
        .map((message) => ({
          role: message.role,
          content: message.content,
        }));

      const activeConvId =
        conversationId ||
        (
          typeof crypto !== 'undefined' &&
          crypto.randomUUID
            ? crypto.randomUUID()
            : `conv-${Date.now()}`
        );

      setConversationId(activeConvId);

      const controller = new AbortController();

      abortControllerRef.current = controller;

      let receivedText = '';
      let receivedSources: string[] = [];
      let receivedTools: string[] = [];
      let receivedTrace: string[] = [];

      let completed = false;

      const updateAssistant = (
        updater: (message: ChatMessageItem) => ChatMessageItem
      ) => {

        setMessages((previous) =>
          previous.map((message) =>
            message.id === assistantId
              ? updater(message)
              : message
          )
        );
      };

      try {

        await streamChat(
          {
            message: trimmed,
            conversation_id: activeConvId,
            history: historyPayload,
            context:
              Object.keys(pageContext).length > 0
                ? pageContext
                : undefined,
          },

          (event: ChatStreamEvent) => {

            // --------------------------------------------
            // TOKEN EVENT
            // --------------------------------------------

            if (event.type === 'token') {

              receivedText += event.text;

              updateAssistant((message) => ({
                ...message,
                content: receivedText,
                isPartial: true,
              }));
            }

            // --------------------------------------------
            // REPLACE EVENT
            // --------------------------------------------

            else if (event.type === 'replace') {

              receivedText = event.text;

              updateAssistant((message) => ({
                ...message,
                content: receivedText,
                isPartial: true,
              }));
            }

            // --------------------------------------------
            // SOURCES EVENT
            // --------------------------------------------

            else if (event.type === 'sources') {

              receivedSources = event.sources || [];

              updateAssistant((message) => ({
                ...message,
                sources: receivedSources,
              }));
            }

            // --------------------------------------------
            // DONE EVENT
            // --------------------------------------------

            else if (event.type === 'done') {

              completed = true;

              if (event.conversation_id) {
                setConversationId(event.conversation_id);
              }

              receivedTools = event.tools_used || [];
              receivedTrace = event.trace_steps || [];

              updateAssistant((message) => ({
                ...message,
                content: receivedText,
                sources: receivedSources,
                tools_used: receivedTools,
                trace_steps: receivedTrace,
                isPartial: false,
                hasError: false,
              }));
            }

            // --------------------------------------------
            // ERROR EVENT
            // --------------------------------------------

            else if (event.type === 'error') {

              throw new Error(event.message);
            }

            if (!isOpenRef.current) {
              setHasUnread(true);
            }
          },

          controller.signal
        );

        if (controller.signal.aborted) {
          return;
        }

        if (!completed) {
          throw new Error(
            'The server ended the stream without a completion event.'
          );
        }

        if (!receivedText.trim()) {
          throw new Error(
            'The server returned an empty response.'
          );
        }

        updateAssistant((message) => ({
          ...message,
          content: receivedText,
          sources: receivedSources,
          tools_used: receivedTools,
          trace_steps: receivedTrace,
          isPartial: false,
          hasError: false,
        }));

        if (!isOpenRef.current) {
          setHasUnread(true);
        }

      } catch (err: unknown) {

        if (
          controller.signal.aborted ||
          (err instanceof Error && err.name === 'AbortError')
        ) {

          updateAssistant((message) => ({
            ...message,
            isPartial: false,
          }));

          return;
        }

        const errorObject = err as {
          status?: number;
          response?: { status?: number };
        };

        const status =
          errorObject.status ||
          errorObject.response?.status;

        if (status === 401) {

          setIsUnauthorized(true);

        } else {

          setError(
            'উত্তর আনতে সমস্যা হয়েছে। আবার চেষ্টা করুন।'
          );

          setLastFailedMessage(trimmed);

          updateAssistant((message) => ({
            ...message,
            content: receivedText || message.content,
            isPartial: false,
            hasError: true,
          }));
        }

      } finally {

        if (abortControllerRef.current === controller) {
          abortControllerRef.current = null;
        }

        busyRef.current = false;

        setLoading(false);
        setIsStreaming(false);
      }
    },

    [
      messages,
      conversationId,
      pageContext,
    ]
  );


  // ==========================================================
  // RETRY
  // ==========================================================

  const retryLastMessage = useCallback(async () => {

    if (!lastFailedMessage) {
      return;
    }

    setError(null);
    setIsUnauthorized(false);

    await sendMessage(lastFailedMessage);

  }, [
    lastFailedMessage,
    sendMessage,
  ]);


  // ==========================================================
  // PROVIDER
  // ==========================================================

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


// ============================================================
// HOOK
// ============================================================

export const useChat = () => {

  const context = useContext(ChatContext);

  if (!context) {
    throw new Error(
      'useChat must be used within a ChatProvider'
    );
  }

  return context;
};
