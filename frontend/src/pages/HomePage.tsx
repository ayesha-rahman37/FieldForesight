import React from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import {
  BarChart3,
  AlertTriangle,
  Users,
  Sprout,
  CheckCircle2,
  ChevronRight,
  BookOpen,
  Radio,
  ArrowRight,
  TrendingUp,
  MapPin,
  CloudRain,
  Check,
  Phone
} from 'lucide-react';

export const HomePage: React.FC = () => {
  const { t } = useLanguage();
  const { user } = useAuth();

  return (
    <div className="bg-[#FBF9F5] text-slate-800 selection:bg-emerald-300 selection:text-[#011914] flex flex-col min-h-screen font-sans antialiased">
      
      {/* ========================================================================= */}
      {/* 1. HERO SECTION                                                           */}
      {/* ========================================================================= */}
      <section className="relative text-white pt-12 pb-20 lg:pt-16 lg:pb-28 overflow-hidden border-b border-teal-700/70"
        style={{
          backgroundColor: '#00473F',
          backgroundImage: `
            radial-gradient(circle at 65% 15%, rgba(52, 211, 153, 0.16) 0%, transparent 65%),
            linear-gradient(rgba(52, 211, 153, 0.08) 1px, transparent 1px),
            linear-gradient(90deg, rgba(52, 211, 153, 0.08) 1px, transparent 1px)
          `,
          backgroundSize: '100% 100%, 40px 40px, 40px 40px'
        }}
      >
        {/* Ambient background glow */}
        <div className="absolute -top-32 left-1/3 -translate-x-1/2 w-[700px] h-[350px] bg-emerald-400/15 blur-[130px] pointer-events-none rounded-full"></div>
        <div className="max-w-[1720px] mx-auto px-4 sm:px-6 lg:px-12 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-center">
            
            {/* Left Column: 55% Content */}
            <div className="lg:col-span-7 flex flex-col items-start text-left">
              {/* Calibration Pill */}
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#022c22]/90 border border-emerald-400/40 text-emerald-200 mb-6 shadow-sm">
                <span className="text-base">🛰️</span>
                <span className="text-xs sm:text-sm font-bold uppercase tracking-wider text-emerald-200">
                  {t('স্যাটেলাইট ও এআই-চালিত এগ্রিটেক • বাংলাদেশের জন্য ক্যালিব্রেটেড', 'SATELLITE & AI-POWERED AGTECH • CALIBRATED FOR BANGLADESH')}
                </span>
              </div>

              {/* Main Headline */}
              <h1 className="text-4xl sm:text-5xl lg:text-[3.5rem] font-extrabold tracking-tight leading-[1.12] text-white">
                {t('নির্ভুল ফসল পূর্বাভাস,', 'Accurate Crop Prediction,')} <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 via-emerald-100 to-teal-200">
                  {t('আপনার হাতের মুঠোয়', 'at Your Fingertips')}
                </span>
              </h1>

              {/* Subtext */}
              <p className="mt-6 text-base sm:text-lg lg:text-xl text-emerald-100/90 max-w-2xl font-normal leading-relaxed">
                {t(
                  'স্যাটেলাইট ডেটা এবং এআই ব্যবহার করে আপনার ফসলের ফলন সম্পর্কে আগাম ধারণা পান। সঠিক সিদ্ধান্ত নিন, ঝুঁকি কমান এবং আয় বাড়ান।',
                  'Get early insights into your crop yield using satellite data and AI. Make informed decisions, mitigate risks, and increase your income.'
                )}
              </p>

              {/* Action Buttons */}
              <div className="mt-8 flex flex-wrap items-center gap-4">
                <Link
                  to={user ? "/dashboard" : "/signup"}
                  className="min-h-[48px] px-8 py-3.5 rounded-xl bg-white hover:bg-emerald-50 text-[#011914] font-bold text-base tracking-wide shadow-lg shadow-black/20 hover:shadow-xl transition-all flex items-center gap-3 group focus:ring-4 focus:ring-emerald-400/40"
                >
                  <span>{t('শুরু করুন', 'Get Started')}</span>
                  <ChevronRight className="w-5 h-5 text-[#00473F] group-hover:translate-x-1 transition-transform" />
                </Link>
                {!user && (
                  <Link
                    to="/login"
                    className="min-h-[48px] px-7 py-3.5 rounded-xl border-2 border-emerald-400/50 hover:bg-[#022c22]/60 text-emerald-100 font-semibold text-base tracking-wide transition-all flex items-center justify-center focus:ring-4 focus:ring-emerald-400/40"
                  >
                    {t('লগইন', 'Log In')}
                  </Link>
                )}
              </div>

              {/* 3 Trust Stats */}
              <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4 w-full pt-8 border-t border-teal-700/60">
                <div className="flex items-start gap-3 bg-[#022c22]/50 border border-emerald-500/20 rounded-xl p-3.5">
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/20 text-emerald-300 flex items-center justify-center shrink-0">
                    <CheckCircle2 className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-base font-bold text-white">{t('১০,০০০+ জমি বিশ্লেষিত', '10K+ fields analyzed')}</div>
                    <div className="text-xs text-emerald-200/70 mt-0.5">{t('আঞ্চলিক কৃষকদের দ্বারা সংগৃহীত', 'Validated with regional farmers')}</div>
                  </div>
                </div>

                <div className="flex items-start gap-3 bg-[#022c22]/50 border border-emerald-500/20 rounded-xl p-3.5">
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/20 text-emerald-300 flex items-center justify-center shrink-0">
                    <MapPin className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-base font-bold text-white">{t('সমগ্র বাংলাদেশ', 'Bangladesh-wide')}</div>
                    <div className="text-xs text-emerald-200/70 mt-0.5">{t('সকল ৬৪ জেলা ও এগ্রো জোন', 'All 64 districts & agro zones')}</div>
                  </div>
                </div>

                <div className="flex items-start gap-3 bg-[#022c22]/50 border border-emerald-500/20 rounded-xl p-3.5">
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/20 text-emerald-300 flex items-center justify-center shrink-0">
                    <Radio className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-base font-bold text-white">{t('স্যাটেলাইট + আবহাওয়া', 'Satellite + weather')}</div>
                    <div className="text-xs text-emerald-200/70 mt-0.5">{t('সেনটিনেল-২, মডিশ ও ERA5', 'Sentinel-2, MODIS & ERA5')}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: 45% Satellite Map Visual + Floating Mock Card */}
            <div className="lg:col-span-5 relative mt-6 lg:mt-0 flex justify-center">
              <div className="relative w-full max-w-lg rounded-3xl overflow-hidden border-2 border-emerald-400/40 shadow-2xl bg-[#011914] p-2">
                
                {/* Simulated Satellite NDVI Overlay */}
                <div className="relative h-64 sm:h-72 w-full rounded-2xl overflow-hidden bg-emerald-950">
                  <div className="absolute inset-0 bg-gradient-to-tr from-emerald-900 via-teal-800 to-green-700 opacity-90"></div>
                  <div className="absolute inset-0 grid grid-cols-4 grid-rows-3 gap-1 p-2 opacity-60">
                    <div className="rounded bg-emerald-400/30 border border-emerald-300/40"></div>
                    <div className="rounded bg-teal-300/25 border border-teal-300/30 col-span-2"></div>
                    <div className="rounded bg-lime-400/35 border border-lime-300/40"></div>
                    <div className="rounded bg-emerald-500/35 border border-emerald-300/30 col-span-2"></div>
                    <div className="rounded bg-yellow-400/20 border border-yellow-300/30"></div>
                    <div className="rounded bg-emerald-400/40 border border-emerald-300/40"></div>
                    <div className="rounded bg-emerald-300/25 border border-emerald-300/30"></div>
                    <div className="rounded bg-teal-400/30 border border-teal-300/30"></div>
                    <div className="rounded bg-emerald-600/30 border border-emerald-400/40 col-span-2"></div>
                  </div>
                  
                  {/* Radar tags */}
                  <div className="absolute top-3 left-3 bg-black/60 backdrop-blur-md px-3 py-1 rounded-md text-[11px] font-mono text-emerald-300 border border-emerald-500/40 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                    <span>LAT 24.374° N, LON 88.604° E</span>
                  </div>
                  <div className="absolute top-3 right-3 bg-emerald-900/80 backdrop-blur-md px-2.5 py-1 rounded-md text-[11px] font-bold text-white border border-emerald-400/40">
                    NDVI BAND 8A
                  </div>
                </div>

                {/* Floating Mock Prediction Card */}
                <div className="-mt-20 relative mx-2 mb-2 p-5 rounded-2xl shadow-2xl text-left text-white"
                  style={{
                    background: 'rgba(4, 56, 50, 0.88)',
                    backdropFilter: 'blur(16px)',
                    border: '1px solid rgba(52, 211, 153, 0.35)'
                  }}
                >
                  <div className="flex items-center justify-between pb-3 border-b border-emerald-500/25">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">🌾</span>
                      <span className="font-bold text-sm sm:text-base text-white">{t('ধান · রাজশাহী · বোরো মৌসুম', 'Rice · Rajshahi · Boro Season')}</span>
                    </div>
                    <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-950 bg-emerald-300 px-2.5 py-1 rounded-full shadow-sm">
                      <Check className="w-3.5 h-3.5 text-emerald-900" />
                      {t('৯৪% উচ্চ নির্ভুলতা', '94% High Confidence')}
                    </span>
                  </div>

                  <div className="mt-4 flex items-baseline justify-between">
                    <div>
                      <div className="text-xs uppercase font-semibold text-emerald-300 tracking-wider">{t('আনুমানিক ফসলের ফলন', 'Estimated Harvest Yield')}</div>
                      <div className="text-4xl font-extrabold text-white tracking-tight mt-1 flex items-baseline gap-1.5">
                        4.2 <span className="text-xl font-medium text-emerald-200">t/ha</span>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="inline-flex items-center gap-1 text-xs font-bold text-emerald-300 bg-emerald-500/20 border border-emerald-400/30 px-2.5 py-1 rounded-lg">
                        <TrendingUp className="w-3.5 h-3.5" />
                        <span>+14% vs 5-yr regional avg</span>
                      </div>
                      <div className="text-[11px] text-emerald-200/60 mt-1">DAE Historic Benchmark: 3.68 t/ha</div>
                    </div>
                  </div>

                  <div className="mt-3 py-1">
                    <svg className="w-full h-8 text-emerald-400" fill="none" viewBox="0 0 280 40">
                      <path d="M0 32 C 40 28, 70 34, 110 24 C 150 14, 190 22, 230 10 C 255 4, 270 6, 280 4" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"></path>
                      <path d="M0 32 C 40 28, 70 34, 110 24 C 150 14, 190 22, 230 10 C 255 4, 270 6, 280 4 L 280 40 L 0 40 Z" fill="rgba(52, 211, 153, 0.15)"></path>
                    </svg>
                  </div>

                  <div className="mt-3 pt-3 border-t border-emerald-500/25 grid grid-cols-3 gap-2 text-center">
                    <div className="bg-[#022c22]/80 border border-emerald-400/25 rounded-lg py-1.5 px-1">
                      <div className="text-[11px] text-emerald-300/80 font-medium">NDVI Index</div>
                      <div className="text-sm font-bold text-white">0.81</div>
                    </div>
                    <div className="bg-[#022c22]/80 border border-emerald-400/25 rounded-lg py-1.5 px-1">
                      <div className="text-[11px] text-emerald-300/80 font-medium">{t('মাটির আর্দ্রতা', 'Soil Moisture')}</div>
                      <div className="text-sm font-bold text-white">32%</div>
                    </div>
                    <div className="bg-[#022c22]/80 border border-emerald-400/25 rounded-lg py-1.5 px-1">
                      <div className="text-[11px] text-emerald-300/80 font-medium">{t('আবহাওয়া', 'Weather')}</div>
                      <div className="text-sm font-bold text-emerald-300">{t('অনুকূল', 'Favorable')}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 2. FEATURES SECTION                                                       */}
      {/* ========================================================================= */}
      <section className="py-20 lg:py-28 relative"
        style={{
          backgroundColor: '#FBF9F5',
          backgroundImage: `
            linear-gradient(rgba(0, 71, 63, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 71, 63, 0.04) 1px, transparent 1px)
          `,
          backgroundSize: '32px 32px, 32px 32px'
        }}
      >
        <div className="max-w-[1720px] mx-auto px-4 sm:px-6 lg:px-12">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl lg:text-[2.6rem] font-extrabold text-[#00473F] tracking-tight leading-snug">
              {t('যেভাবে FieldForesight আপনাকে সাহায্য করে', 'How FieldForesight Helps You')}
            </h2>
            <p className="mt-3 text-base sm:text-lg text-slate-600 font-medium">
              {t('স্মার্ট কৃষিকাজের জন্য প্রয়োজনীয় সবকিছু এক জায়গায়', 'Everything you need for smart farming in one place')}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 xl:gap-8">
            {/* Card 1 */}
            <div className="bg-white rounded-2xl p-8 border border-stone-200/90 shadow-sm hover:shadow-xl hover:-translate-y-2 transition-all duration-300 flex flex-col justify-between group">
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="w-14 h-14 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700 shadow-sm group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                    <BarChart3 className="w-7 h-7" />
                  </div>
                  <span className="text-xs font-bold text-emerald-800 bg-emerald-100/80 px-3 py-1 rounded-full">
                    Predictive AI
                  </span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3 group-hover:text-emerald-800 transition-colors">
                  {t('ফলন পূর্বাভাস', 'Yield Prediction')}
                </h3>
                <p className="text-base text-slate-600 leading-relaxed font-normal">
                  {t('অত্যাধুনিক এআই দিয়ে ফসলের সম্ভাব্য ফলন জানুন।', 'Know your potential crop yield with advanced AI before seasonal harvesting commences. Calibrated models for local strains.')}
                </p>
              </div>
              <div className="pt-6 mt-6 border-t border-slate-100 flex items-center justify-between text-sm font-semibold text-emerald-700">
                <span>Model XGBoost + SHAP</span>
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </div>
            </div>

            {/* Card 2 */}
            <div className="bg-white rounded-2xl p-8 border border-stone-200/90 shadow-sm hover:shadow-xl hover:-translate-y-2 transition-all duration-300 flex flex-col justify-between group">
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="w-14 h-14 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-600 shadow-sm group-hover:bg-amber-600 group-hover:text-white transition-colors">
                    <AlertTriangle className="w-7 h-7" />
                  </div>
                  <span className="text-xs font-bold text-amber-800 bg-amber-100/90 px-3 py-1 rounded-full">
                    Early Warning
                  </span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3 group-hover:text-amber-800 transition-colors">
                  {t('ঝুঁকি সতর্কতা', 'Risk Alerts')}
                </h3>
                <p className="text-base text-slate-600 leading-relaxed font-normal">
                  {t('আবহাওয়া ও রোগবালাইয়ের আগাম সতর্কতা পান।', 'Get real-time warnings for blast diseases, localized pest outbreaks, unexpected hailstorms, and flash flood threats.')}
                </p>
              </div>
              <div className="pt-6 mt-6 border-t border-slate-100 flex items-center justify-between text-sm font-semibold text-amber-700">
                <span>Climate & Blight Shield</span>
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </div>
            </div>

            {/* Card 3 */}
            <div className="bg-white rounded-2xl p-8 border border-stone-200/90 shadow-sm hover:shadow-xl hover:-translate-y-2 transition-all duration-300 flex flex-col justify-between group">
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="w-14 h-14 rounded-2xl bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-700 shadow-sm group-hover:bg-teal-700 group-hover:text-white transition-colors">
                    <Users className="w-7 h-7" />
                  </div>
                  <span className="text-xs font-bold text-teal-800 bg-teal-100/80 px-3 py-1 rounded-full">
                    Peer Benchmark
                  </span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3 group-hover:text-teal-800 transition-colors">
                  {t('কমিউনিটি ইনসাইটস', 'Community Insights')}
                </h3>
                <p className="text-base text-slate-600 leading-relaxed font-normal">
                  {t('অন্যান্য কৃষকদের অভিজ্ঞতার সাথে আপনার জমির তুলনা করুন।', 'Compare your field with regional peer metrics and localized farmer inputs across upazilas to optimize fertilizer timing.')}
                </p>
              </div>
              <div className="pt-6 mt-6 border-t border-slate-100 flex items-center justify-between text-sm font-semibold text-teal-700">
                <span>District Aggregations</span>
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </div>
            </div>

            {/* Card 4 */}
            <div className="bg-white rounded-2xl p-8 border border-stone-200/90 shadow-sm hover:shadow-xl hover:-translate-y-2 transition-all duration-300 flex flex-col justify-between group">
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="w-14 h-14 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 shadow-sm group-hover:bg-[#022c22] group-hover:text-white transition-colors">
                    <Sprout className="w-7 h-7" />
                  </div>
                  <span className="text-xs font-bold text-emerald-800 bg-emerald-100/90 px-3 py-1 rounded-full">
                    Multispectral NDVI
                  </span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3 group-hover:text-emerald-800 transition-colors">
                  {t('ভেজিটেশন মনিটরিং', 'Vegetation Monitoring')}
                </h3>
                <p className="text-base text-slate-600 leading-relaxed font-normal">
                  {t('স্যাটেলাইট চিত্রের মাধ্যমে ফসলের স্বাস্থ্য পর্যবেক্ষণ করুন।', 'High-frequency multispectral Sentinel-2 NDVI health tracks. Catch chlorophyll and water stress before visible discoloration.')}
                </p>
              </div>
              <div className="pt-6 mt-6 border-t border-slate-100 flex items-center justify-between text-sm font-semibold text-emerald-800">
                <span>5-Day Cadence Revisit</span>
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 3. HOW IT WORKS SECTION                                                   */}
      {/* ========================================================================= */}
      <section className="py-20 lg:py-28 bg-white border-y border-stone-200">
        <div className="max-w-[1720px] mx-auto px-4 sm:px-6 lg:px-12">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 pb-6 border-b border-stone-100">
            <div>
              <span className="text-xs font-bold text-emerald-800 uppercase tracking-widest bg-emerald-50 border border-emerald-200 px-3.5 py-1.5 rounded-full inline-block mb-3">
                SYSTEM PIPELINE
              </span>
              <h2 className="text-3xl sm:text-4xl lg:text-[2.5rem] font-extrabold text-slate-900 tracking-tight">
                {t('এটি কীভাবে কাজ করে?', 'How It Works?')}
              </h2>
              <p className="text-slate-600 mt-2 text-base font-normal max-w-xl">
                {t('তিনটি সহজ ধাপে জমির ডেটা থেকে সরাসরি ফসল ফলনের দিকনির্দেশনা পান।', 'A seamless three-step data journey from field coordinate to actionable harvest guidance.')}
              </p>
            </div>
            <div className="mt-4 md:mt-0">
              <span className="px-4 py-2 text-xs font-semibold rounded-lg bg-stone-100 text-slate-700 border border-stone-200 inline-flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                {t('স্বয়ংক্রিয় এ্যান্ড-টু-এ্যান্ড পাইপলাইন', 'End-to-End Automated Pipeline')}
              </span>
            </div>
          </div>

          <div className="relative grid grid-cols-1 md:grid-cols-3 gap-8 xl:gap-12">
            <div className="hidden md:block absolute top-7 left-[15%] right-[15%] h-1 bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 -z-0"></div>

            {/* Step 1 */}
            <div className="relative bg-[#FBF9F5] rounded-2xl p-7 border border-stone-200/90 shadow-sm hover:border-emerald-600/60 transition-all flex flex-col justify-between z-10 group">
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="w-14 h-14 rounded-2xl bg-[#00473F] text-white font-extrabold text-xl flex items-center justify-center shadow-md ring-4 ring-white">
                    ১
                  </div>
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500 bg-white px-3 py-1 rounded-md border border-stone-200">
                    Input Layer
                  </span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2 group-hover:text-emerald-800 transition-colors">
                  {t('ফসল ও অঞ্চল নির্বাচন করুন', 'Select Crop & Region')}
                </h3>
                <p className="text-base text-slate-600 leading-relaxed font-normal mb-6">
                  {t('আপনার জমি কোথায় এবং কী চাষ করছেন তা জানান।', 'Tell us where your land is located and what you are growing. Choose specific crop strains like BRRI Dhan 28/29, BARI Gom, or Aman hybrids.')}
                </p>
              </div>

              <div className="bg-white rounded-xl p-4 border border-stone-200 shadow-inner space-y-2.5">
                <div className="flex items-center justify-between text-xs font-semibold text-slate-700 pb-2 border-b border-stone-100">
                  <span>District: Rajshahi</span>
                  <span className="text-emerald-700 font-mono">Upazila: Paba</span>
                </div>
                <div className="bg-stone-50 rounded-lg p-2.5 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="text-emerald-700 font-bold">🌾</span>
                    <span className="font-medium text-slate-800">BRRI Dhan 29 (Boro)</span>
                  </div>
                  <span className="text-[11px] font-semibold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded">Selected</span>
                </div>
                <div className="text-[11px] text-slate-400 font-mono text-center">Coordinate: 24.37° N, 88.60° E</div>
              </div>
            </div>

            {/* Step 2 */}
            <div className="relative bg-[#FBF9F5] rounded-2xl p-7 border border-stone-200/90 shadow-sm hover:border-emerald-600/60 transition-all flex flex-col justify-between z-10 group">
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="w-14 h-14 rounded-2xl bg-[#043832] text-white font-extrabold text-xl flex items-center justify-center shadow-md ring-4 ring-white">
                    ২
                  </div>
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500 bg-white px-3 py-1 rounded-md border border-stone-200">
                    Inference Engine
                  </span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2 group-hover:text-emerald-800 transition-colors">
                  {t('পূর্বাভাস পান', 'Get Prediction')}
                </h3>
                <p className="text-base text-slate-600 leading-relaxed font-normal mb-6">
                  {t('এআই মুহূর্তের মধ্যে আপনার ফলনের একটি বৈজ্ঞানিক হিসাব তৈরি করবে।', 'AI instantly generates a scientific estimate of your harvest. FastAPI & XGBoost ML synthesize satellite radar data and soil telemetry in seconds.')}
                </p>
              </div>

              <div className="bg-white rounded-xl p-4 border border-stone-200 shadow-inner space-y-2.5">
                <div className="flex items-center justify-between text-xs font-semibold text-slate-700 pb-2 border-b border-stone-100">
                  <span>ML Model Execution</span>
                  <span className="text-emerald-700 font-mono">Status: 200 OK</span>
                </div>
                <div className="bg-[#011914] text-white rounded-lg p-3 text-xs space-y-1 font-mono">
                  <div className="text-emerald-400">&gt; Loading Sentinel-2 NDVI matrix...</div>
                  <div className="text-teal-300">&gt; ERA5 rainfall accumulation: OK</div>
                  <div className="text-white font-bold">&gt; Yield Predicted: 4.2 t/ha (±0.18)</div>
                </div>
                <div className="text-[11px] text-slate-500 text-center">FastAPI Microservice · Inference &lt; 450ms</div>
              </div>
            </div>

            {/* Step 3 */}
            <div className="relative bg-[#FBF9F5] rounded-2xl p-7 border border-stone-200/90 shadow-sm hover:border-emerald-600/60 transition-all flex flex-col justify-between z-10 group">
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="w-14 h-14 rounded-2xl bg-emerald-700 text-white font-extrabold text-xl flex items-center justify-center shadow-md ring-4 ring-white">
                    ৩
                  </div>
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500 bg-white px-3 py-1 rounded-md border border-stone-200">
                    Actionable Plan
                  </span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2 group-hover:text-emerald-800 transition-colors">
                  {t('বুঝুন ও কাজ করুন', 'Understand & Act')}
                </h3>
                <p className="text-base text-slate-600 leading-relaxed font-normal mb-6">
                  {t('উপদেশ ও সতর্কবার্তা মেনে পরবর্তী পদক্ষেপ গ্রহণ করুন।', 'Receive clear localized advisories, nutrient adjustment warnings, and SMS alerts to proactively safeguard your yield and maximize revenues.')}
                </p>
              </div>

              <div className="bg-white rounded-xl p-4 border border-stone-200 shadow-inner space-y-2.5">
                <div className="flex items-center justify-between text-xs font-semibold text-slate-700 pb-2 border-b border-stone-100">
                  <span>Advisory Action Plan</span>
                  <span className="text-emerald-700 font-semibold">SMS Ready</span>
                </div>
                <div className="bg-emerald-50/80 border border-emerald-200/60 rounded-lg p-2.5 text-xs text-slate-900 space-y-1">
                  <div className="font-bold flex items-center gap-1.5 text-emerald-800">
                    <Check className="w-4 h-4 text-emerald-600" />
                    Optimal Top-dressing Window
                  </div>
                  <p className="text-[12px] text-slate-700">Apply Urea + MOP within next 5 days prior to predicted dry spell.</p>
                </div>
                <div className="text-[11px] text-slate-500 text-center">Bangla SMS pushed to farmer handset</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 4. DATA SOURCES BAND                                                      */}
      {/* ========================================================================= */}
      <section className="bg-[#00473F] text-white py-16 border-b border-[#011914]">
        <div className="max-w-[1720px] mx-auto px-4 sm:px-6 lg:px-12">
          <div className="text-center mb-10">
            <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
              {t('যেসব ডেটার ওপর ভিত্তি করে আমরা কাজ করি', 'Data sources that power our predictions')}
            </h3>
            <p className="text-emerald-200/75 text-sm sm:text-base mt-1">
              {t('স্যাটেলাইট রিমোট সেন্সিং ও আঞ্চলিক কৃষি পর্যবেক্ষণের সমন্বয়', 'Peer-reviewed satellite remote sensing combined with ground-truth agricultural observations')}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-[#022c22]/80 border border-emerald-400/30 rounded-2xl p-6 hover:border-emerald-300 transition-all flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-[#011914] border border-emerald-400/40 text-emerald-300 flex items-center justify-center shrink-0 shadow-inner">
                <Radio className="w-6 h-6" />
              </div>
              <div>
                <div className="font-bold text-white text-base">{t('স্যাটেলাইট চিত্র', 'Satellite Imagery')}</div>
                <div className="text-xs text-emerald-200/80 font-medium mt-1">Sentinel-2 & MODIS multispectral</div>
                <p className="text-xs text-emerald-100/60 mt-2">10m optical resolution + 5-day NDVI revisit tracking</p>
              </div>
            </div>

            <div className="bg-[#022c22]/80 border border-emerald-400/30 rounded-2xl p-6 hover:border-emerald-300 transition-all flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-[#011914] border border-emerald-400/40 text-emerald-300 flex items-center justify-center shrink-0 shadow-inner">
                <CloudRain className="w-6 h-6" />
              </div>
              <div>
                <div className="font-bold text-white text-base">{t('আবহাওয়ার ডেটা', 'Weather Data')}</div>
                <div className="text-xs text-emerald-200/80 font-medium mt-1">ERA5 Climate Grids & Telemetry</div>
                <p className="text-xs text-emerald-100/60 mt-2">Solar radiation, temperature range & rainfall anomalies</p>
              </div>
            </div>

            <div className="bg-[#022c22]/80 border border-emerald-400/30 rounded-2xl p-6 hover:border-emerald-300 transition-all flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-[#011914] border border-emerald-400/40 text-emerald-300 flex items-center justify-center shrink-0 shadow-inner">
                <BookOpen className="w-6 h-6" />
              </div>
              <div>
                <div className="font-bold text-white text-base">{t('ঐতিহাসিক রেকর্ড', 'Historical Records')}</div>
                <div className="text-xs text-emerald-200/80 font-medium mt-1">2012–2024 DAE Archives</div>
                <p className="text-xs text-emerald-100/60 mt-2">12 years of verified district crop cutting experiments</p>
              </div>
            </div>

            <div className="bg-[#022c22]/80 border border-emerald-400/30 rounded-2xl p-6 hover:border-emerald-300 transition-all flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-[#011914] border border-emerald-400/40 text-emerald-300 flex items-center justify-center shrink-0 shadow-inner">
                <Sprout className="w-6 h-6" />
              </div>
              <div>
                <div className="font-bold text-white text-base">{t('মাটির ধরন', 'Soil Types')}</div>
                <div className="text-xs text-emerald-200/80 font-medium mt-1">BARC Soil pH & Texture Maps</div>
                <p className="text-xs text-emerald-100/60 mt-2">Salinity gradients, nitrogen baselines & hydrology indices</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 5. FINAL CTA                                                              */}
      {/* ========================================================================= */}
      <section className="py-20 lg:py-24 bg-[#022c22] text-white relative overflow-hidden">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white leading-tight">
            {t('কয়েক মিনিটে আপনার প্রথম ফলন পূর্বাভাস পান', 'Get your first prediction in minutes')}
          </h2>
          <p className="mt-4 text-base sm:text-lg lg:text-xl text-emerald-100/85 font-normal max-w-2xl mx-auto leading-relaxed">
            {t('আজই ডেটা-ভিত্তিক কৃষিকাজে যুক্ত হোন হাজারো কৃষক ও কৃষি কর্মকর্তার সাথে।', 'Join thousands of farmers and agricultural officers across Bangladesh making data-backed decisions today.')}
          </p>
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to={user ? "/dashboard" : "/signup"}
              className="min-h-[48px] px-8 py-4 rounded-xl bg-white hover:bg-emerald-50 text-[#011914] font-extrabold text-base tracking-wide shadow-xl shadow-black/20 hover:scale-[1.02] transition-all flex items-center gap-2.5"
            >
              <span>{t('এখনই শুরু করুন', 'Get Started Now')}</span>
              <ArrowRight className="w-5 h-5 text-[#00473F]" />
            </Link>
          </div>
          <div className="mt-5 text-xs sm:text-sm text-emerald-200/70 font-medium flex items-center justify-center gap-2">
            <Check className="w-4 h-4 text-emerald-400" />
            <span>{t('কোন ক্রেডিট কার্ডের প্রয়োজন নেই • ক্ষুদ্র কৃষকদের জন্য বিনামূল্যে', 'No credit card required • Free for smallholder farmers')}</span>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 6. GLOBAL FOOTER                                                          */}
      {/* ========================================================================= */}
      <footer className="bg-white border-t border-stone-200 py-8 text-sm text-slate-600 font-medium">
        <div className="max-w-[1720px] mx-auto px-4 sm:px-6 lg:px-12 flex flex-col lg:flex-row items-center justify-between gap-5">
          <div className="text-center lg:text-left text-slate-600 flex items-center gap-2 flex-wrap">
            <span>FieldForesight Platform © {new Date().getFullYear()}. All agricultural models calibrated for Bangladesh agro-ecological zones.</span>
            <span className="inline-flex items-center text-[10px] font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
              AI YIELD V2.4
            </span>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm">
            <Link to="/security" className="hover:text-emerald-800 transition-colors">
              {t('প্রাইভেসি ও নিরাপত্তা', 'Privacy Shield')}
            </Link>
            <span className="text-slate-300">•</span>
            <Link to="/security" className="hover:text-emerald-800 transition-colors">
              {t('এপিআই ডকুমেন্টেশন', 'API Documentation')}
            </Link>
            <span className="text-slate-300">•</span>
            <a href="tel:16123" className="hover:text-emerald-800 text-emerald-800 font-bold transition-colors flex items-center gap-1.5">
              <Phone className="w-4 h-4 text-emerald-700" />
              <span>{t('কৃষক সহায়তা হেল্পলাইন (১৬১২৩)', 'Farmer Support Helpline (16123 toll-free)')}</span>
            </a>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default HomePage;
