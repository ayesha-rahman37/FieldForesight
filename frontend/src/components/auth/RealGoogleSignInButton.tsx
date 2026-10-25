import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import { translateAuthError } from '../../utils/emailValidator';

interface RealGoogleSignInButtonProps {
  onError?: (errMessage: string) => void;
  className?: string;
}

// Module-level singletons to ensure Google GSI initialize() is called strictly once across the entire application lifecycle
let globalInitializedClientId: string | null = null;
let globalCredentialHandler: ((response: any) => void) | null = null;

export const RealGoogleSignInButton: React.FC<RealGoogleSignInButtonProps> = ({ onError, className }) => {
  const { loginWithGoogle } = useAuth();
  const { language } = useLanguage();
  const navigate = useNavigate();
  const location = useLocation();

  const googleBtnContainerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(false);
  const [isGsiReady, setIsGsiReady] = useState(false);

  const clientId =
    (import.meta as any).env?.VITE_GOOGLE_CLIENT_ID ||
    '1001242793973-jcoqddl819ecd1omlsidhcm5b2rpolju.apps.googleusercontent.com';

  const callbackRef = useRef({ loginWithGoogle, onError, navigate, location, language });
  useEffect(() => {
    callbackRef.current = { loginWithGoogle, onError, navigate, location, language };
  }, [loginWithGoogle, onError, navigate, location, language]);

  const onCredentialResponse = useCallback(async (response: any) => {
    const { loginWithGoogle: loginFn, onError: errFn, navigate: navFn, location: loc, language: lang } =
      callbackRef.current;

    if (!response || !response.credential) {
      const msg = lang === 'bn' ? 'গুগল অথেনটিকেশন ব্যর্থ হয়েছে।' : 'Google authentication failed.';
      errFn?.(msg);
      return;
    }

    setLoading(true);
    try {
      await loginFn(response.credential);
      const params = new URLSearchParams(loc.search);
      const redirect = params.get('redirect') || '/dashboard';
      navFn(redirect);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      const translated = translateAuthError(detail, lang as 'bn' | 'en');
      errFn?.(translated || (lang === 'bn' ? 'লগইন ব্যর্থ হয়েছে।' : 'Login failed.'));
    } finally {
      setLoading(false);
    }
  }, []);

  // Sync latest credential handler
  useEffect(() => {
    globalCredentialHandler = onCredentialResponse;
  }, [onCredentialResponse]);

  useEffect(() => {
    let checkInterval: any = null;
    let attempts = 0;

    const setupButton = () => {
      attempts++;
      const google = (window as any).google;
      if (!google || !google.accounts || !google.accounts.id) return false;

      try {
        // 1. Initialize strictly once per clientId
        if (globalInitializedClientId !== clientId) {
          google.accounts.id.initialize({
            client_id: clientId,
            callback: (resp: any) => {
              if (globalCredentialHandler) {
                globalCredentialHandler(resp);
              }
            },
            auto_select: false,
            cancel_on_tap_outside: true,
          });
          globalInitializedClientId = clientId;
        }

        // 2. Render Google official button in dedicated empty container
        if (googleBtnContainerRef.current) {
          const parentWidth = googleBtnContainerRef.current.parentElement?.offsetWidth || 360;
          const clampedWidth = Math.min(Math.max(parentWidth, 200), 400);

          googleBtnContainerRef.current.innerHTML = '';
          google.accounts.id.renderButton(googleBtnContainerRef.current, {
            type: 'standard',
            theme: 'outline',
            size: 'large',
            text: 'continue_with',
            shape: 'rectangular',
            logo_alignment: 'left',
            width: clampedWidth,
            locale: language === 'bn' ? 'bn' : 'en',
          });

          // Check if Google inserted the iframe button
          setTimeout(() => {
            if (googleBtnContainerRef.current && googleBtnContainerRef.current.children.length > 0) {
              setIsGsiReady(true);
            }
          }, 150);
        }
        return true;
      } catch (err) {
        console.error('Failed to initialize Google Identity Services:', err);
        return false;
      }
    };

    if (!setupButton()) {
      checkInterval = setInterval(() => {
        if (setupButton() || attempts > 20) {
          clearInterval(checkInterval);
        }
      }, 300);
    }

    return () => {
      if (checkInterval) clearInterval(checkInterval);
    };
  }, [clientId, language]);

  const handleFallbackClick = () => {
    const msg =
      language === 'bn'
        ? 'গুগল ক্লাউড কনসোলে এই অরিজিন (http://localhost:5173) সক্রিয় হতে ২-৫ মিনিট সময় লাগতে পারে। অনুগ্রহ করে কিছুক্ষণ পর পেজটি রিফ্রেশ (Ctrl+F5) করুন।'
        : 'Google Cloud settings for origin http://localhost:5173 may take 2-5 minutes to take effect. Please refresh the page (Ctrl+F5) in a moment.';
    onError?.(msg);
  };

  return (
    <div className={`w-full flex flex-col items-center justify-center ${className || ''}`}>
      {loading && (
        <div className="mb-2 text-xs text-slate-500 flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin" />
          <span>{language === 'bn' ? 'গুগল অ্যাকাউন্ট যাচাই করা হচ্ছে...' : 'Verifying Google Account...'}</span>
        </div>
      )}

      {/* Fallback button shown only until Google GSI finishes rendering the iframe */}
      {!isGsiReady && !loading && (
        <button
          type="button"
          onClick={handleFallbackClick}
          className="w-full max-w-[400px] flex items-center justify-center gap-3 py-2.5 px-4 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 bg-white hover:bg-slate-50 transition shadow-sm cursor-pointer"
        >
          <svg className="w-5 h-5 shrink-0" width="20" height="20" viewBox="0 0 24 24">
            <path
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              fill="#4285F4"
            />
            <path
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              fill="#34A853"
            />
            <path
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              fill="#FBBC05"
            />
            <path
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              fill="#EA4335"
            />
          </svg>
          <span>{language === 'bn' ? 'গুগল দিয়ে চালিয়ে যান' : 'Continue with Google'}</span>
        </button>
      )}

      {/* Dedicated isolated container for Google's official iframe button */}
      <div
        ref={googleBtnContainerRef}
        className={`w-full flex justify-center min-h-[44px] ${!isGsiReady || loading ? 'hidden' : ''}`}
        style={{ minHeight: '44px' }}
      />
    </div>
  );
};
