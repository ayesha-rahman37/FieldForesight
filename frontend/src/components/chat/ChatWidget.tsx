import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { MessageSquare, LogIn } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useChat } from '../../context/ChatContext';
import { ErrorBoundary } from '../common/ErrorBoundary';
import { ChatPanel } from './ChatPanel';

export const ChatWidget: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { token } = useAuth();
  const { isOpen, setIsOpen, toggleChat, hasUnread } = useChat();

  const [showLoginPrompt, setShowLoginPrompt] = useState(false);
  const promptRef = useRef<HTMLDivElement>(null);

  // Do NOT render on /login and /signup
  const isAuthPage =
    location.pathname === '/login' || location.pathname === '/signup';

  const isLandingPage = location.pathname === '/';
  const isLoggedIn = Boolean(token);

  // Handle Escape key to close panel/prompt
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (isOpen) setIsOpen(false);
        if (showLoginPrompt) setShowLoginPrompt(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, showLoginPrompt, setIsOpen]);

  // Close login prompt if clicked outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (promptRef.current && !promptRef.current.contains(e.target as Node)) {
        setShowLoginPrompt(false);
      }
    };
    if (showLoginPrompt) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showLoginPrompt]);

  if (isAuthPage) {
    return null;
  }

  const handleButtonClick = () => {
    if (isLandingPage && !isLoggedIn) {
      setShowLoginPrompt(true);
      return;
    }
    toggleChat();
  };

  return (
    <>
      {/* Unauthenticated Login Prompt on Landing Page */}
      {showLoginPrompt && !isLoggedIn && (
        <div
          ref={promptRef}
          className="fixed bottom-24 right-6 z-50 w-72 p-4 bg-white rounded-2xl shadow-xl border border-[#E5E1D6] animate-in fade-in slide-in-from-bottom-2 duration-200"
        >
          <div className="flex items-center gap-3 mb-2.5">
            <div className="w-8 h-8 rounded-full bg-[#E6EFE6] text-[#004741] flex items-center justify-center">
              <LogIn className="w-4 h-4" />
            </div>
            <div>
              <h4 className="font-semibold text-sm text-[#1F1F1B]">কৃষি সহকারী</h4>
              <p className="text-xs text-[#717568]">চ্যাট করতে লগইন করুন</p>
            </div>
          </div>
          <button
            onClick={() => {
              setShowLoginPrompt(false);
              navigate('/login');
            }}
            className="w-full py-2 px-4 bg-[#004741] text-[#F0EDE4] text-sm font-semibold rounded-xl hover:bg-[#084936] transition-colors cursor-pointer"
          >
            লগইন
          </button>
        </div>
      )}

      {/* Floating Trigger Button */}
      <button
        onClick={handleButtonClick}
        aria-label="কৃষি সহকারী চ্যাট"
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-[#004741] text-[#F0EDE4] shadow-lg hover:shadow-xl transition-all duration-200 hover:-translate-y-0.5 flex items-center justify-center cursor-pointer ${
          isOpen ? 'scale-0 opacity-0 pointer-events-none' : 'scale-100 opacity-100'
        }`}
      >
        <MessageSquare className="w-6 h-6" />
        {/* Unread dot badge */}
        {hasUnread && !isOpen && (
          <span className="absolute top-1 right-1 w-3.5 h-3.5 bg-amber-400 border-2 border-[#004741] rounded-full animate-pulse" />
        )}
      </button>

      {/* Chat Panel */}
      <ErrorBoundary featureName="কৃষি সহকারী চ্যাট">
        <ChatPanel isOpen={isOpen} onClose={() => setIsOpen(false)} />
      </ErrorBoundary>
    </>
  );
};

export default ChatWidget;
