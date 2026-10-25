import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  X,
  ArrowLeft,
  Send,
  Square,
  RotateCcw,
  Sparkles,
  AlertCircle,
} from 'lucide-react';
import { useChat } from '../../context/ChatContext';

export interface ChatPanelProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  isOpen: propIsOpen,
  onClose: propOnClose,
}) => {
  const navigate = useNavigate();
  const chatContext = useChat();

  const isOpen = propIsOpen !== undefined ? propIsOpen : chatContext.isOpen;
  const handleClose = propOnClose || (() => chatContext.setIsOpen(false));

  const {
    messages,
    loading,
    isStreaming,
    stopConversation,
    error,
    isUnauthorized,
    pageContext,
    sendMessage,
    retryLastMessage,
    startNewChat,
  } = chatContext;

  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom on new messages or loading state
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, loading, isStreaming, error, isUnauthorized, isOpen]);

  // Focus textarea when panel opens
  useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => {
        textareaRef.current?.focus();
      }, 260);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  const handleSend = () => {
    const text = input.trim();
    if (!text || loading || isStreaming) return;
    sendMessage(text);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestionChips = [
    'রংপুরে ব্রি ধান ২৮ চাষে ফলন ও ব্লাস্ট দমন পরামর্শ চাই',
    'আলুর নাবি ধসা রোগ প্রতিরোধ ও লক্ষণ কী?',
    'দিনাজপুরে সাম্প্রতিক আবহাওয়া ও দুর্যোগ সতর্কতা কেমন?',
  ];

  const contextText = [
    pageContext.crop && `ফসল: ${pageContext.crop}`,
    pageContext.region && `অঞ্চল: ${pageContext.region}`,
    pageContext.predicted_yield !== undefined &&
      pageContext.predicted_yield !== null &&
      `পূর্বাভাস: ${pageContext.predicted_yield} টন/হেক্টর`,
  ]
    .filter(Boolean)
    .join(' • ');

  return (
    <div
      className={`fixed z-50 transition-all duration-250 ease-out bg-white flex flex-col shadow-2xl border border-[#E5E1D6] 
        /* Mobile: full screen */
        inset-0 w-full h-full rounded-none
        /* Desktop: 380px wide card with 16px radius */
        sm:inset-auto sm:bottom-6 sm:right-6 sm:w-[380px] sm:h-[600px] sm:max-h-[calc(100vh-3rem)] sm:rounded-[16px]
        ${
          isOpen
            ? 'translate-x-0 opacity-100'
            : 'translate-x-full opacity-0 pointer-events-none'
        }
      `}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-[#004741] text-[#F0EDE4] sm:rounded-t-[16px] select-none">
        <div className="flex items-center gap-2.5">
          {/* Back button on mobile */}
          <button
            onClick={handleClose}
            className="sm:hidden p-1.5 -ml-1 text-[#F0EDE4] hover:bg-white/10 rounded-lg transition-colors cursor-pointer"
            aria-label="বন্ধ করুন"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-[#F0EDE4]" />
          </div>
          <div>
            <h3 className="font-semibold text-base leading-tight">কৃষি সহকারী</h3>
            <p className="text-xs text-[#F0EDE4]/80">AI চালিত</p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={startNewChat}
            title="নতুন চ্যাট"
            className="p-1.5 text-xs flex items-center gap-1 text-[#F0EDE4]/90 hover:text-[#F0EDE4] hover:bg-white/10 rounded-lg transition-colors cursor-pointer"
          >
            <RotateCcw className="w-4 h-4" />
            <span className="text-xs hidden sm:inline">নতুন চ্যাট</span>
          </button>
          {/* Close button on desktop */}
          <button
            onClick={handleClose}
            className="hidden sm:flex p-1.5 text-[#F0EDE4]/90 hover:text-[#F0EDE4] hover:bg-white/10 rounded-lg transition-colors cursor-pointer"
            aria-label="বন্ধ করুন"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Permanent Disclaimer Strip */}
      <div className="px-3 py-1.5 bg-[#FDF4E3] border-b border-[#F3DBAF] text-[#B47818] text-[12px] leading-snug font-medium text-center">
        এটা AI সহকারী। কীটনাশক বা সারের মাত্রার জন্য স্থানীয় কৃষি কর্মকর্তার পরামর্শ নিন।
      </div>

      {/* Page Context Chip */}
      {contextText && (
        <div className="px-3 py-1 bg-[#F4F1EA] text-[#004741] text-xs font-medium border-b border-[#E5E1D6] flex items-center justify-between">
          <span className="truncate">
            <span className="font-semibold">প্রসঙ্গ:</span> {contextText}
          </span>
        </div>
      )}

      {/* Message List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-[#FBFAF6]">
        {/* Empty State */}
        {messages.length === 0 && !loading && (
          <div className="h-full flex flex-col justify-center items-center text-center p-2">
            <div className="w-12 h-12 rounded-full bg-[#E6EFE6] text-[#004741] flex items-center justify-center mb-3">
              <Sparkles className="w-6 h-6" />
            </div>
            <h4 className="font-semibold text-[#1F1F1B] text-base mb-1">
              স্বাগতম! কীভাবে সাহায্য করতে পারি?
            </h4>
            <p className="text-sm text-[#717568] max-w-[280px] mb-4">
              ফসলের সেচ, রোগবালাই, সার প্রয়োগ বা এলাকার ঝুঁকি সম্পর্কে সরাসরি প্রশ্ন করুন।
            </p>
            <div className="w-full space-y-2">
              {suggestionChips.map((chip, idx) => (
                <button
                  key={idx}
                  onClick={() => sendMessage(chip)}
                  className="w-full text-left p-2.5 bg-white hover:bg-[#F0EDE4] border border-[#E5E1D6] rounded-xl text-sm text-[#004741] font-medium transition-colors cursor-pointer"
                >
                  💡 {chip}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Render Messages */}
        {messages.map((msg) => {
          const isUser = msg.role === 'user';
          return (
            <div
              key={msg.id}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-[85%] px-3.5 py-2.5 rounded-2xl text-[16px] leading-relaxed break-words whitespace-pre-wrap ${
                  isUser
                    ? 'bg-[#004741] text-[#F0EDE4] rounded-br-sm'
                    : 'bg-white text-[#1F1F1B] border border-[#E5E1D6] rounded-bl-sm shadow-sm'
                }`}
              >
                {msg.content}
              </div>
            </div>
          );
        })}

        {/* Loading Typing Indicator with Inline Stop Button */}
        {loading && (
          <div className="flex items-center gap-2">
            <div className="bg-white border border-[#E5E1D6] px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#004741] animate-bounce [animation-delay:-0.3s]" />
              <span className="w-2 h-2 rounded-full bg-[#004741] animate-bounce [animation-delay:-0.15s]" />
              <span className="w-2 h-2 rounded-full bg-[#004741] animate-bounce" />
            </div>
            <button
              type="button"
              onClick={stopConversation}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white hover:bg-rose-50 text-rose-700 border border-rose-200 text-xs font-semibold shadow-2xs transition-colors cursor-pointer"
              title="কথোপকথন থামান"
            >
              <Square className="w-3 h-3 fill-current" />
              <span>থামান</span>
            </button>
          </div>
        )}

        {/* Unauthorized (401) Inline Banner */}
        {isUnauthorized && (
          <div className="p-3 bg-[#FDF4E3] border border-[#F3DBAF] rounded-xl flex items-center justify-between text-xs text-[#B47818]">
            <span>চ্যাট করতে লগইন করুন</span>
            <button
              onClick={() => navigate('/login')}
              className="px-3 py-1 bg-[#004741] text-[#F0EDE4] rounded-lg font-medium hover:bg-[#084936] transition-colors cursor-pointer"
            >
              লগইন
            </button>
          </div>
        )}

        {/* Compact Inline Error */}
        {error && !loading && !isStreaming && (
          <div className="flex items-center gap-1.5 text-xs text-[#C62828] px-2 py-1 bg-[#F8E9E4] rounded-lg self-start border border-[#F3C7BE]">
            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
            <span>{error}</span>
            <button
              onClick={retryLastMessage}
              className="underline font-semibold ml-1 text-[#C62828] hover:opacity-80 cursor-pointer"
            >
              আবার চেষ্টা করুন
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-3 border-t border-[#E5E1D6] bg-white sm:rounded-b-[16px]">
        <div className="relative border border-[#E5E1D6] rounded-xl focus-within:border-[#004741] focus-within:ring-1 focus-within:ring-[#004741] transition-all bg-[#FBFAF6]">
          <textarea
            ref={textareaRef}
            rows={2}
            maxLength={500}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="কৃষি বিষয়ক যেকোনো প্রশ্ন লিখুন..."
            className="w-full resize-none p-2.5 pr-12 text-[15px] bg-transparent text-[#1F1F1B] placeholder-[#717568] focus:outline-none"
          />
          {loading || isStreaming ? (
            <button
              type="button"
              onClick={stopConversation}
              aria-label="কথোপকথন থামান"
              title="কথোপকথন থামান"
              className="absolute right-2 bottom-2 p-1.5 rounded-lg bg-[#C62828] text-white hover:bg-[#B71C1C] transition-colors cursor-pointer shadow-xs"
            >
              <Square className="w-4 h-4 fill-current" />
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSend}
              disabled={!input.trim()}
              aria-label="বার্তা পাঠান"
              className="absolute right-2 bottom-2 p-1.5 rounded-lg bg-[#004741] text-[#F0EDE4] disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[#084936] transition-colors cursor-pointer"
            >
              <Send className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Character counter (shows when >= 400 characters) */}
        <div className="flex justify-between items-center mt-1 px-1 text-[11px] text-[#717568]">
          <span>Enter চাপলে পাঠানো হবে, Shift+Enter নতুন লাইন</span>
          {input.length >= 400 && (
            <span className={input.length >= 490 ? 'text-[#C62828] font-bold' : ''}>
              {input.length}/500
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatPanel;

