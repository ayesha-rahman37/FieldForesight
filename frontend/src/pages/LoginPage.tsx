import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { useComingSoon } from '../context/ComingSoonContext';
import { loginUser } from '../api/auth';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const { language, toggleLanguage, t } = useLanguage();
  const { openComingSoon } = useComingSoon();
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Scroll to top on mount
    window.scrollTo(0, 0);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await loginUser(username.trim(), password);
      await login(res.access_token);
      if (rememberMe) {
        localStorage.setItem('remember_me', '1');
      } else {
        localStorage.removeItem('remember_me');
      }
      navigate('/dashboard');
    } catch (err: unknown) {
      const detail =
        err &&
        typeof err === 'object' &&
        'response' in err &&
        err.response &&
        typeof err.response === 'object' &&
        'data' in err.response &&
        err.response.data &&
        typeof err.response.data === 'object' &&
        'detail' in err.response.data
          ? String((err.response.data as { detail: unknown }).detail)
          : t('লগইন ব্যর্থ হয়েছে। ইউজারনেম এবং পাসওয়ার্ড পরীক্ষা করুন।', 'Login failed. Please check your username and password.');
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen text-slate-800 bg-grid-pattern flex flex-col justify-between selection:bg-emerald-200 selection:text-emerald-950"
      style={{ fontFamily: '"Plus Jakarta Sans", sans-serif', backgroundColor: '#F8F9F5' }}
    >
      <style>{`
        .bg-grid-pattern {
          background-size: 32px 32px;
          background-image:
            linear-gradient(to right, rgba(6, 78, 59, 0.04) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(6, 78, 59, 0.04) 1px, transparent 1px);
        }
        .btn-glow:hover {
          box-shadow: 0 10px 25px -5px rgba(6, 95, 70, 0.35);
        }
      `}</style>

      <header className="w-full bg-white/80 backdrop-blur-md border-b border-emerald-900/10 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link className="flex items-center gap-3 group" to="/">
              <div className="w-11 h-11 rounded-xl flex items-center justify-center text-white shadow-md shadow-emerald-950/20 group-hover:scale-105 transition-transform duration-200" style={{ background: 'linear-gradient(135deg, #022c22 0%, #047857 100%)' }}>
                <svg
                  className="w-6 h-6 stroke-white stroke-[2.2] fill-none shrink-0"
                  width="24"
                  height="24"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  viewBox="0 0 24 24"
                >
                  <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" />
                  <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
                </svg>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xl font-bold tracking-tight text-emerald-950">FieldForesight</span>
                  <span className="hidden sm:inline-block px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-emerald-100 text-emerald-800 rounded-full border border-emerald-200">
                    AI Yield V2.4
                  </span>
                </div>
                <p className="text-xs font-medium text-slate-500 tracking-wide">{t('স্মার্ট কৃষি ফলন পূর্বাভাস', 'Intelligent Harvest Prediction')}</p>
              </div>
            </Link>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <Link className="hover:text-emerald-800 transition-colors" to="/">
              {t('হোম', 'Home')}
            </Link>
            <Link className="hover:text-emerald-800 transition-colors" to="/dashboard">
              {t('ফলন ইনসাইটস', 'Yield Insights')}
            </Link>
            <Link className="hover:text-emerald-800 transition-colors" to="/security">
              {t('নিরাপত্তা ও ডকুমেন্টস', 'Security & Docs')}
            </Link>
          </nav>

          <div className="flex items-center gap-3 sm:gap-4">
            <button
              type="button"
              onClick={toggleLanguage}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-emerald-950 bg-white hover:bg-slate-100 border border-slate-200 rounded-lg shadow-sm transition cursor-pointer"
            >
              <svg className="w-4 h-4 text-emerald-700 shrink-0" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="1.8"
                />
              </svg>
              <span>{language === 'bn' ? 'English' : 'বাংলা'}</span>
            </button>
            <Link
              className="px-5 py-2 text-sm font-semibold text-emerald-950 hover:text-emerald-700 transition"
              to="/signup"
            >
              {t('একাউন্ট তৈরি করুন', 'Create Account')}
            </Link>
            <button type="button" className="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100">
              <svg className="w-6 h-6 shrink-0" width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M4 6h16M4 12h16m-7 6h7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12 w-full flex items-center justify-center">
        <div className="w-full bg-white rounded-3xl shadow-xl shadow-slate-200/70 border border-slate-100 overflow-hidden grid grid-cols-1 lg:grid-cols-12 min-h-[720px]">
          <section className="lg:col-span-5 p-8 sm:p-12 text-white relative flex flex-col justify-between overflow-hidden" style={{ background: 'linear-gradient(135deg, #011914 0%, #064e3b 50%, #047857 100%)' }}>
            <div className="absolute -right-20 -top-20 w-80 h-80 rounded-full bg-emerald-500/10 blur-3xl pointer-events-none" />
            <div className="absolute -left-20 -bottom-20 w-80 h-80 rounded-full bg-emerald-400/15 blur-2xl pointer-events-none" />
            <div className="absolute inset-0 bg-[radial-gradient(#10b981_1px,transparent_1px)] [background-size:24px_24px] opacity-10 pointer-events-none" />

            <div className="relative z-10">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-emerald-200 text-xs font-semibold mb-6">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                {t('বাংলাদেশের ১,২০০+ কৃষককে সহায়তা করা হচ্ছে', 'Empowering 1,200+ Farmers in Bangladesh')}
              </div>
              <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight leading-tight text-white">
                {t('সর্বোচ্চ ফসল উৎপাদনের জন্য প্রিসিশন এগ্রিটেক।', 'Precision AgTech for maximum crop yield.')}
              </h1>
              <p className="mt-4 text-emerald-100/90 text-sm leading-relaxed font-normal">
                {t('উপগ্রহ চিত্র, স্থানীয় আবহাওয়া সেন্সর এবং আঞ্চলিক মাটির উপাত্ত ব্যবহার করে কাটার আগেই ফসলের উৎপাদন অনুমান করুন।', 'Harness satellite imagery, hyper-local microclimate sensors, and regional soil datasets to predict crop performance weeks before harvest.')}
              </p>
            </div>

            <div className="relative z-10 my-8 space-y-4">
              <div className="bg-white/10 backdrop-blur-md border border-white/20 p-4 rounded-2xl flex items-center justify-between transition duration-200 hover:bg-white/15">
                <div className="flex items-center gap-3.5">
                  <div className="w-10 h-10 rounded-xl bg-emerald-400/20 border border-emerald-300/30 flex items-center justify-center text-emerald-300">
                    <svg className="w-5 h-5 shrink-0" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                      />
                    </svg>
                  </div>
                  <div>
                    <div className="text-xs text-emerald-200 font-medium">{t('বোরো ধান ও গম মডেল', 'Boro Rice & Wheat Model')}</div>
                    <div className="text-base font-bold text-white tracking-wide">{t('৯৮.৪% সঠিকতা', '98.4% Accuracy')}</div>
                  </div>
                </div>
                <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-emerald-500/30 text-emerald-200 border border-emerald-400/30">
                  {t('যাচাইকৃত', 'Verified')}
                </span>
              </div>

              <div className="bg-white/10 backdrop-blur-md border border-white/20 p-4 rounded-2xl flex items-center justify-between transition duration-200 hover:bg-white/15">
                <div className="flex items-center gap-3.5">
                  <div className="w-10 h-10 rounded-xl bg-amber-400/20 border border-amber-300/30 flex items-center justify-center text-amber-300">
                    <svg className="w-5 h-5 shrink-0" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        d="M13 10V3L4 14h7v7l9-11h-7z"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                      />
                    </svg>
                  </div>
                  <div>
                    <div className="text-xs text-emerald-200 font-medium">{t('আঞ্চলিক কভারেজ', 'Regional Coverage')}</div>
                    <div className="text-base font-bold text-white tracking-wide">{t('৬৪টি জেলা প্রস্তুত', '64 Districts Ready')}</div>
                  </div>
                </div>
                <div className="flex -space-x-1 overflow-hidden">
                  <span className="inline-block h-6 w-6 rounded-full ring-2 ring-emerald-900 bg-emerald-600 text-[10px] font-bold text-center leading-6 text-white">
                    DH
                  </span>
                  <span className="inline-block h-6 w-6 rounded-full ring-2 ring-emerald-900 bg-teal-600 text-[10px] font-bold text-center leading-6 text-white">
                    RJ
                  </span>
                  <span className="inline-block h-6 w-6 rounded-full ring-2 ring-emerald-900 bg-emerald-700 text-[10px] font-bold text-center leading-6 text-white">
                    RN
                  </span>
                </div>
              </div>
            </div>

            <div className="relative z-10 pt-4 border-t border-emerald-800/60">
              <p className="text-xs italic text-emerald-100/90 leading-normal">
                {t('"ফিল্ডফোরসাইট আমাদের ধান কাটার তারিখ ১৪ দিন আগেই অনুমান করতে সাহায্য করেছে, যার ফলে কোনো খাদ্যশস্য নষ্ট হয়নি।"', '"FieldForesight helped us forecast our paddy harvesting date 14 days in advance with zero grain spoilage."')}
              </p>
              <div className="mt-2 text-xs font-semibold text-emerald-300">{t('— মোঃ রফিকুল ইসলাম, কৃষক, বগুড়া', '— Md. Rafiqul Islam, Farmer, Bogura')}</div>
            </div>
          </section>

          <section className="lg:col-span-7 p-6 sm:p-10 lg:p-12 flex flex-col justify-center bg-white">
            <div className="max-w-md mx-auto w-full">
              <div className="text-center sm:text-left mb-8">
                <div className="inline-flex lg:hidden mb-4 w-12 h-12 rounded-2xl text-white items-center justify-center shadow-md" style={{ background: 'linear-gradient(135deg, #022c22 0%, #047857 100%)' }}>
                  <svg
                    className="w-6 h-6 stroke-white stroke-[2.2] fill-none shrink-0"
                    width="24"
                    height="24"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    viewBox="0 0 24 24"
                  >
                    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" />
                    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
                  </svg>
                </div>
                <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">{t('স্বাগতম!', 'Welcome back!')}</h2>
                <p className="mt-2 text-sm text-slate-500">
                  {t('আপনার খামারের ফলন পূর্বাভাস এবং স্যাটেলাইট তথ্য দেখতে সাইন ইন করুন।', 'Sign in to access your farm yield forecasts and satellite insights.')}
                </p>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-rose-50 text-rose-600 text-sm rounded-xl border border-rose-100 font-medium">
                  {error}
                </div>
              )}

              <div className="mb-6">
                <button
                  type="button"
                  className="w-full flex items-center justify-center gap-3 py-2.5 px-4 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 bg-white hover:bg-slate-50 transition shadow-sm cursor-pointer"
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
                  {t('গুগল দিয়ে প্রবেশ করুন', 'Continue with Google')}
                </button>
                <div className="relative flex items-center justify-center my-6">
                  <div className="border-t border-slate-200 w-full" />
                  <span className="bg-white px-3 text-xs text-slate-400 uppercase tracking-wider font-medium">
                    {t('অথবা ইউজারনেম / ইমেইল দিয়ে সাইন ইন করুন', 'Or sign in with username / email')}
                  </span>
                  <div className="border-t border-slate-200 w-full" />
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label
                    className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5"
                    htmlFor="username_or_email"
                  >
                    {t('ইউজারনেম অথবা ইমেইল', 'Username or Email')} <span className="text-rose-500">*</span>
                  </label>
                  <div className="relative rounded-xl shadow-sm">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                      <svg className="w-5 h-5 shrink-0" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="1.8"
                        />
                      </svg>
                    </div>
                    <input
                      className="block w-full pl-11 pr-4 py-2.5 text-sm bg-slate-50/50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-brand-700 focus:border-brand-700 transition placeholder:text-slate-400"
                      id="username_or_email"
                      name="username_or_email"
                      placeholder={t('আপনার ইউজারনেম বা ইমেইল দিন', 'Enter your username or email')}
                      required
                      type="text"
                      value={username}
                      onChange={(e) => {
                        setUsername(e.target.value);
                        setError(null);
                      }}
                      autoComplete="username"
                    />
                  </div>
                </div>

                <div>
                  <label
                    className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5"
                    htmlFor="password"
                  >
                    {t('পাসওয়ার্ড', 'Password')} <span className="text-rose-500">*</span>
                  </label>
                  <div className="relative rounded-xl shadow-sm">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                      <svg className="w-5 h-5 shrink-0" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="1.8"
                        />
                      </svg>
                    </div>
                    <input
                      className="block w-full pl-11 pr-11 py-2.5 text-sm bg-slate-50/50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-brand-700 focus:border-brand-700 transition placeholder:text-slate-400"
                      id="password"
                      name="password"
                      placeholder={t('আপনার পাসওয়ার্ড দিন', 'Enter your password')}
                      required
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => {
                        setPassword(e.target.value);
                        setError(null);
                      }}
                      autoComplete="current-password"
                    />
                    <button
                      type="button"
                      aria-label="Toggle password visibility"
                      onClick={() => setShowPassword((s) => !s)}
                      className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600 transition cursor-pointer"
                    >
                      <svg className="w-5 h-5 shrink-0" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        {showPassword ? (
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="1.8"
                            d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                          />
                        ) : (
                          <>
                            <path
                              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth="1.8"
                            />
                            <path
                              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth="1.8"
                            />
                          </>
                        )}
                      </svg>
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <div className="flex items-center">
                    <input
                      className="h-4 w-4 rounded border-slate-300 text-brand-800 focus:ring-brand-700"
                      id="remember_me"
                      name="remember_me"
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                    />
                    <label className="ml-2 block text-xs text-slate-600 leading-tight cursor-pointer" htmlFor="remember_me">
                      {t('৩০ দিনের জন্য মনে রাখুন', 'Remember me for 30 days')}
                    </label>
                  </div>
                  <button
                    type="button"
                    onClick={() => openComingSoon(t('পাসওয়ার্ড পুনরুদ্ধার', 'Password Recovery'))}
                    className="text-xs font-semibold text-brand-800 hover:text-brand-950 hover:underline transition cursor-pointer"
                  >
                    {t('পাসওয়ার্ড ভুলে গেছেন?', 'Forgot password?')}
                  </button>
                </div>

                <div className="pt-2">
                  <button
                    className="w-full py-3 px-4 rounded-xl text-white font-semibold text-sm bg-gradient-to-r from-brand-900 to-brand-800 hover:from-brand-950 hover:to-brand-900 shadow-md shadow-brand-950/20 transition-all duration-200 flex items-center justify-center gap-2 group btn-glow cursor-pointer disabled:opacity-70 disabled:cursor-not-allowed"
                    type="submit"
                    disabled={loading}
                  >
                    <span>{loading ? t('সাইন ইন করা হচ্ছে...', 'Signing in...') : t('সাইন ইন', 'Sign In')}</span>
                    {!loading && (
                      <svg
                        className="w-4 h-4 text-emerald-300 group-hover:translate-x-1 transition-transform shrink-0"
                        width="16"
                        height="16"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          d="M14 5l7 7m0 0l-7 7m7-7H3"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2.2"
                        />
                      </svg>
                    )}
                  </button>
                </div>
              </form>

              <p className="mt-8 text-center text-xs text-slate-500">
                {t('একাউন্ট নেই?', "Don't have an account?")}{' '}
                <Link className="font-bold text-brand-800 hover:text-brand-950 hover:underline transition" to="/signup">
                  {t('একাউন্ট তৈরি করুন', 'Create an account')}
                </Link>
              </p>
            </div>
          </section>
        </div>
      </main>

      <footer className="w-full py-6 border-t border-slate-200/70 text-slate-500 text-xs mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-brand-950">{t('ফিল্ডফোরসাইট প্ল্যাটফর্ম', 'FieldForesight Platform')}</span>
            <span>{t('© ২০২৫। বাংলাদেশের সকল কৃষি-বাস্তুতন্ত্র অঞ্চলের জন্য মডেল প্রস্তুত।', '© 2025. All agricultural models calibrated for Bangladesh agro-ecological zones.')}</span>
          </div>
          <div className="flex items-center gap-6">
            <Link className="hover:text-brand-900 transition" to="/security">
              {t('প্রাইভেসি শিল্ড', 'Privacy Shield')}
            </Link>
            <Link className="hover:text-brand-900 transition" to="/security">
              {t('এপিআই ডকুমেন্টস', 'API Documentation')}
            </Link>
            <button
              type="button"
              onClick={() => openComingSoon(t('কৃষক সহায়তা হেল্পলাইন', 'Farmer Support Helpline'))}
              className="hover:text-brand-900 transition cursor-pointer"
            >
              {t('কৃষক সহায়তা হেল্পলাইন', 'Farmer Support Helpline')}
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};
