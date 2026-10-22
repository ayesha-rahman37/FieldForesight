import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import {
  Sprout,
  Shield,
  UserCircle,
  Database,
  LogOut,
  ChevronDown,
  Menu,
  X,
  BookOpen,
  Lock
} from 'lucide-react';

export const TopNavbar: React.FC = () => {
  const { user, logout } = useAuth();
  const { toggleLanguage, t, language } = useLanguage();
  const location = useLocation();
  const navigate = useNavigate();

  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [helpDropdownOpen, setHelpDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [visible, setVisible] = useState(true);
  const [liveTime, setLiveTime] = useState<string>('');

  const lastScrollY = useRef(0);

  // Auto-close menus on route change
  useEffect(() => {
    setDropdownOpen(false);
    setHelpDropdownOpen(false);
    setMobileMenuOpen(false);
  }, [location.pathname, location.search]);

  // Live clock for Sentinel-2 status badge
  useEffect(() => {
    const updateTime = () => setLiveTime(new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', second: '2-digit' }));
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Hide on scroll down, show on scroll up
  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      if (currentScrollY > lastScrollY.current && currentScrollY > 60) {
        setVisible(false);
      } else {
        setVisible(true);
      }
      lastScrollY.current = currentScrollY;
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const searchParams = new URLSearchParams(location.search);
  const currentTab = searchParams.get('tab');

  const isHomeActive = location.pathname === '/';
  const isDashboardActive = location.pathname === '/dashboard' && (!currentTab || currentTab === 'overview');
  const isMyDataActive = location.pathname === '/dashboard' && currentTab === 'my-data';
  const isYieldInsightsActive = location.pathname === '/yield-insights';
  const isSecurityActive = location.pathname === '/security';

  const linkClass = (active: boolean) =>
    `h-[34px] min-h-[44px] md:min-h-0 px-3.5 text-xs font-medium rounded-lg transition-all flex items-center gap-1.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 ${
      active
        ? 'bg-emerald-900/70 text-white font-semibold border border-emerald-400/50 shadow-xs'
        : 'text-white/80 hover:text-white hover:bg-white/5'
    }`;

  return (
    <header
      className={`w-full bg-[#064E3B] border-b border-white/[0.08] sticky top-0 z-50 transition-transform duration-300 ease-in-out ${
        visible ? 'translate-y-0' : '-translate-y-full'
      }`}
    >
      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 h-[54px] flex items-center justify-between gap-4">
        
        {/* LEFT: Logo Mark + "FieldForesight" Title + Sentinel-2 Status Pill */}
        <div className="flex items-center gap-4">
          <Link
            to={user ? "/dashboard" : "/"}
            className="flex items-center gap-2.5 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 rounded-lg p-0.5"
          >
            <div className="w-8 h-8 rounded-lg bg-emerald-800/80 border border-emerald-400/40 flex items-center justify-center transition-transform group-hover:scale-105">
              <Sprout className="w-4 h-4 text-emerald-300" />
            </div>
            <span className="text-white font-bold text-base tracking-tight">
              Field<span className="text-emerald-300 font-semibold">Foresight</span>
            </span>
          </Link>

          <div className="hidden lg:inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#033527] border border-emerald-500/25 text-[11px] font-medium text-emerald-200">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Sentinel-2 Multispectral Synced</span>
            <span className="text-emerald-500/60">|</span>
            <span className="text-emerald-300/80">Dhaka {liveTime}</span>
          </div>
        </div>

        {/* CENTER: Navigation Links */}
        <nav className="hidden md:flex items-center gap-1" aria-label="Main Navigation">
          <Link to="/" className={linkClass(isHomeActive)}>
            {t('হোম', 'Home')}
          </Link>

          <Link to={user ? "/dashboard" : "/login"} className={linkClass(isDashboardActive)}>
            {t('ড্যাশবোর্ড', 'Dashboard')}
          </Link>

          {user && (
            <Link to="/dashboard?tab=my-data" className={linkClass(isMyDataActive)}>
              {t('আমার ডেটা', 'My Data')}
            </Link>
          )}

          <Link to="/yield-insights" className={linkClass(isYieldInsightsActive)}>
            {t('ফলন ইনসাইট', 'Yield Insights')}
          </Link>

          {/* Help & Docs Dropdown */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setHelpDropdownOpen(!helpDropdownOpen)}
              className={`h-[36px] px-3.5 text-sm font-medium rounded-lg transition-all flex items-center gap-1.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 ${
                isSecurityActive ? 'bg-white/10 text-white font-semibold' : 'text-white/75 hover:text-white'
              }`}
            >
              <span>{t('সহায়তা ও ডকুমেন্টস', 'Help & Docs')}</span>
              <ChevronDown className={`w-3.5 h-3.5 transition-transform ${helpDropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {helpDropdownOpen && (
              <div className="absolute top-[calc(100%+8px)] left-0 bg-[#022c22] border border-emerald-400/30 rounded-xl p-1.5 shadow-xl min-w-[210px] z-50 space-y-1">
                <Link
                  to="/security"
                  className="flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-emerald-100 hover:bg-emerald-800/60 rounded-lg transition-colors"
                >
                  <Shield className="w-4 h-4 text-emerald-400" />
                  <span>{t('নিরাপত্তা ও আর্কিটেকচার', 'Security & Architecture')}</span>
                </Link>
                <Link
                  to="/security"
                  className="flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-emerald-100 hover:bg-emerald-800/60 rounded-lg transition-colors"
                >
                  <BookOpen className="w-4 h-4 text-emerald-400" />
                  <span>{t('এপিআই ডকুমেন্টেশন', 'API Documentation')}</span>
                </Link>
                <Link
                  to="/security"
                  className="flex items-center gap-2.5 px-3 py-2 text-xs font-semibold text-emerald-100 hover:bg-emerald-800/60 rounded-lg transition-colors"
                >
                  <Lock className="w-4 h-4 text-emerald-400" />
                  <span>{t('প্রাইভেসি ও ডাটা সুরক্ষা', 'Privacy Shield')}</span>
                </Link>
              </div>
            )}
          </div>
        </nav>

        {/* RIGHT: Segmented Language Switcher + User Profile / Auth */}
        <div className="hidden md:flex items-center gap-3">
          {/* Compact Segmented Language Switcher "বাংলা | EN" */}
          <div className="h-7 bg-[#033527] border border-emerald-500/30 p-0.5 inline-flex items-center rounded-md text-[11px] font-bold shadow-inner">
            <button
              type="button"
              onClick={() => language !== 'bn' && toggleLanguage()}
              className={`h-full px-2.5 rounded transition-all ${
                language === 'bn'
                  ? 'bg-emerald-500 text-white font-bold shadow-xs'
                  : 'text-emerald-200/75 hover:text-white'
              }`}
            >
              বাংলা
            </button>
            <button
              type="button"
              onClick={() => language !== 'en' && toggleLanguage()}
              className={`h-full px-2.5 rounded transition-all ${
                language === 'en'
                  ? 'bg-emerald-500 text-white font-bold shadow-xs'
                  : 'text-emerald-200/75 hover:text-white'
              }`}
            >
              EN
            </button>
          </div>

          {/* (3) 32px User Avatar with Dropdown / Logged Out Action Buttons */}
          {!user ? (
            <div className="flex items-center gap-2">
              <Link
                to="/login"
                className="h-8 px-3.5 text-xs font-semibold text-emerald-100 hover:text-white transition-colors flex items-center justify-center"
              >
                {t('লগইন', 'Login')}
              </Link>
              <Link
                to="/signup"
                className="h-8 px-4 text-xs font-bold text-[#011914] bg-white hover:bg-emerald-100 rounded-lg shadow transition-all flex items-center justify-center"
              >
                {t('নিবন্ধন', 'Sign up')}
              </Link>
            </div>
          ) : (
            <div className="relative">
              <button
                type="button"
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="flex items-center gap-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 rounded-full"
                aria-label="User menu"
              >
                <div className="w-8 h-8 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center ring-2 ring-emerald-500/30 shadow-sm">
                  {user.username.charAt(0).toUpperCase()}
                </div>
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 top-[calc(100%+8px)] bg-white rounded-xl p-2 shadow-2xl min-w-[200px] border border-stone-200 flex flex-col gap-1 z-50">
                  <div className="px-3 py-2 border-b border-stone-100">
                    <p className="text-xs font-bold text-[#00473F]">{user.username}</p>
                    <p className="text-[10px] text-slate-500 font-medium">{user.email || user.role || 'Farmer Account'}</p>
                  </div>
                  <button
                    onClick={() => navigate('/dashboard?tab=profile')}
                    className="flex items-center gap-2.5 w-full px-3 py-2 text-left text-[#00473F] text-xs font-semibold hover:bg-stone-100 rounded-lg transition-colors"
                  >
                    <UserCircle className="w-4 h-4 text-emerald-700" />
                    <span>{t('প্রোফাইল', 'Profile')}</span>
                  </button>
                  <button
                    onClick={() => navigate('/dashboard?tab=my-data')}
                    className="flex items-center gap-2.5 w-full px-3 py-2 text-left text-[#00473F] text-xs font-semibold hover:bg-stone-100 rounded-lg transition-colors"
                  >
                    <Database className="w-4 h-4 text-emerald-700" />
                    <span>{t('আমার ডেটা', 'My Data')}</span>
                  </button>
                  <button
                    onClick={() => navigate('/security')}
                    className="flex items-center gap-2.5 w-full px-3 py-2 text-left text-[#00473F] text-xs font-semibold hover:bg-stone-100 rounded-lg transition-colors"
                  >
                    <Shield className="w-4 h-4 text-emerald-700" />
                    <span>{t('নিরাপত্তা ও নকশা', 'Security & Docs')}</span>
                  </button>
                  <div className="h-[1px] bg-stone-200 my-1" />
                  <button
                    onClick={() => { logout(); navigate('/'); }}
                    className="flex items-center gap-2.5 w-full px-3 py-2 text-left text-red-600 text-xs font-bold hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <LogOut className="w-4 h-4 text-red-600" />
                    <span>{t('লগআউট', 'Logout')}</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* MOBILE MENU TOGGLE BUTTON (<768px) */}
        <div className="flex items-center gap-3 md:hidden">
          {/* Mobile Status Dot */}
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />

          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="w-10 h-10 flex items-center justify-center text-white/90 hover:text-white rounded-lg focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
            aria-label="Toggle Navigation"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

      </div>

      {/* MOBILE SLIDE-DOWN DRAWER MENU */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-[#022c22] border-b border-emerald-500/30 px-6 py-5 space-y-4 animate-in slide-in-from-top duration-200">
          <nav className="flex flex-col gap-2">
            <Link to="/" className="min-h-[44px] flex items-center px-4 rounded-xl text-base font-medium text-white/90 hover:bg-white/10">
              {t('হোম', 'Home')}
            </Link>
            <Link to={user ? "/dashboard" : "/login"} className="min-h-[44px] flex items-center px-4 rounded-xl text-base font-medium text-white/90 hover:bg-white/10">
              {t('ড্যাশবোর্ড', 'Dashboard')}
            </Link>
            {user && (
              <Link to="/dashboard?tab=my-data" className="min-h-[44px] flex items-center px-4 rounded-xl text-base font-medium text-white/90 hover:bg-white/10">
                {t('আমার ডেটা', 'My Data')}
              </Link>
            )}
            <Link to="/yield-insights" className="min-h-[44px] flex items-center px-4 rounded-xl text-base font-medium text-white/90 hover:bg-white/10">
              {t('ফলন ইনসাইট', 'Yield Insights')}
            </Link>
            <Link to="/security" className="min-h-[44px] flex items-center px-4 rounded-xl text-base font-medium text-white/90 hover:bg-white/10">
              {t('নিরাপত্তা ও আর্কিটেকচার', 'Security & Docs')}
            </Link>
          </nav>

          <div className="pt-4 border-t border-emerald-700/50 flex items-center justify-between">
            {/* Segmented language switcher in mobile drawer */}
            <div className="h-9 bg-[#00473F] border border-emerald-400/40 p-0.5 inline-flex items-center rounded-full text-xs font-bold">
              <button
                type="button"
                onClick={() => language !== 'bn' && toggleLanguage()}
                className={`h-full px-3 rounded-full transition-all ${
                  language === 'bn' ? 'bg-white/20 text-white font-bold' : 'text-emerald-300/70'
                }`}
              >
                বাংলা
              </button>
              <span className="text-emerald-400/40 text-[10px] px-1">|</span>
              <button
                type="button"
                onClick={() => language !== 'en' && toggleLanguage()}
                className={`h-full px-3 rounded-full transition-all ${
                  language === 'en' ? 'bg-white/20 text-white font-bold' : 'text-emerald-300/70'
                }`}
              >
                EN
              </button>
            </div>

            {!user ? (
              <div className="flex items-center gap-2">
                <Link to="/login" className="min-h-[44px] px-4 text-sm font-semibold text-white">
                  {t('লগইন', 'Login')}
                </Link>
                <Link to="/signup" className="min-h-[44px] px-4 text-sm font-bold text-[#011914] bg-white rounded-xl flex items-center">
                  {t('নিবন্ধন', 'Sign up')}
                </Link>
              </div>
            ) : (
              <button
                onClick={() => { logout(); navigate('/'); }}
                className="min-h-[44px] px-4 text-sm font-semibold text-red-300 hover:text-red-100"
              >
                {t('লগআউট', 'Logout')}
              </button>
            )}
          </div>
        </div>
      )}
    </header>
  );
};

export default TopNavbar;
