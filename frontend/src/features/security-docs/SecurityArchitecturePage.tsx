import React from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../../context/LanguageContext';

export const SecurityArchitecturePage: React.FC = () => {
  const { t } = useLanguage();

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6 text-slate-800 font-sans antialiased pt-4 pb-12">
      {/* Page Title & Lead */}

      {/* Page Title & Lead */}
      <section aria-label="Page Header" className="space-y-1.5">
        <div className="inline-flex items-center space-x-1.5 text-xs font-semibold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200/60">
          <svg className="w-3.5 h-3.5 text-emerald-600 shrink-0" width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          </svg>
          <span>{t('গভর্ন্যান্স ও বিশ্বাস', 'Governance & Trust')}</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 font-display">
          {t('নিরাপত্তা ও সিস্টেম আর্কিটেকচার', 'Security & System Architecture')}
        </h1>
        <p className="text-sm sm:text-base text-slate-600">
          {t('ফিল্ডফোরসাইট প্ল্যাটফর্মের প্রযুক্তিগত নকশা, উপাত্ত সুরক্ষা এবং আপনার তথ্যের মালিকানা সম্পর্কিত নীতিমালা।', 'Technical design, data protection standards, and data ownership policies of FieldForesight.')}
        </p>
      </section>

      {/* SECTION 1: How it Works & System Workflow */}
      <article className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 sm:p-7 space-y-6">
        <div className="space-y-2">
          <h2 className="text-base font-bold text-slate-900 tracking-tight flex items-center space-x-2 font-display">
            <span className="w-2 h-2 rounded-full bg-emerald-600"></span>
            <span>{t('কীভাবে কাজ করে', 'How it Works')}</span>
          </h2>
          <p className="text-sm text-slate-600 leading-relaxed max-w-3xl">
            {t('ফিল্ডফোরসাইট একটি এআই-চালিত কৃষি পূর্বাভাস ব্যবস্থা। এটি স্যাটেলাইট ডেটা, আবহাওয়ার তথ্য এবং ফসলের ইতিহাস বিশ্লেষণ করে কৃষকদের সঠিক সিদ্ধান্ত নিতে সাহায্য করে।', 'FieldForesight is an AI-driven agricultural prediction platform. It analyzes satellite data, weather parameters, and historical yield patterns to help farmers make data-driven decisions.')}
          </p>
        </div>

        <hr className="border-slate-100" />

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              {t('সিস্টেম প্রবাহ', 'System Workflow')}
            </h3>
            <span className="text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
              {t('সম্পূর্ণ প্রসেসিং পাইপলাইন', 'End-to-End Pipeline')}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 relative">
            {/* Step 1: Frontend */}
            <div className="group relative bg-slate-50/70 hover:bg-white rounded-xl p-4 border border-slate-200/80 hover:border-emerald-300 hover:shadow-md transition-all duration-200 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="w-7 h-7 rounded-full bg-emerald-900 text-white font-bold text-xs flex items-center justify-center ring-4 ring-emerald-50 shadow-sm">
                    1
                  </span>
                  <span className="text-[10px] font-mono font-medium text-slate-400 bg-white px-1.5 py-0.5 rounded border border-slate-200">
                    Client
                  </span>
                </div>
                <h4 className="text-sm font-semibold text-slate-900 mb-1">{t('ফ্রন্টএন্ড', 'Frontend')}</h4>
                <p className="text-xs text-slate-500 leading-normal">
                  {t('কৃষকের ইনপুট সংগ্রহ ও ইউজার ইন্টারফেস', 'Farmer input collection & UI')}
                </p>
              </div>
              <div className="mt-4 pt-2 border-t border-slate-200/50 flex items-center text-[11px] font-medium text-emerald-800">
                <span>React / Responsive UI</span>
              </div>
            </div>

            {/* Step 2: API Gateway */}
            <div className="group relative bg-slate-50/70 hover:bg-white rounded-xl p-4 border border-slate-200/80 hover:border-emerald-300 hover:shadow-md transition-all duration-200 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="w-7 h-7 rounded-full bg-emerald-900 text-white font-bold text-xs flex items-center justify-center ring-4 ring-emerald-50 shadow-sm">
                    2
                  </span>
                  <span className="text-[10px] font-mono font-medium text-slate-400 bg-white px-1.5 py-0.5 rounded border border-slate-200">
                    Gateway
                  </span>
                </div>
                <h4 className="text-sm font-semibold text-slate-900 mb-1">{t('এপিআই গেটওয়ে', 'API Gateway')}</h4>
                <p className="text-xs text-slate-500 leading-normal">
                  {t('নিরাপদ FastAPI সার্ভার ও অথেন্টিকেশন', 'Secure FastAPI server & authentication')}
                </p>
              </div>
              <div className="mt-4 pt-2 border-t border-slate-200/50 flex items-center text-[11px] font-medium text-emerald-800">
                <span>TLS / OAuth2 Bearer</span>
              </div>
            </div>

            {/* Step 3: AI Model */}
            <div className="group relative bg-slate-50/70 hover:bg-white rounded-xl p-4 border border-slate-200/80 hover:border-emerald-300 hover:shadow-md transition-all duration-200 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="w-7 h-7 rounded-full bg-emerald-900 text-white font-bold text-xs flex items-center justify-center ring-4 ring-emerald-50 shadow-sm">
                    3
                  </span>
                  <span className="text-[10px] font-mono font-medium text-slate-400 bg-white px-1.5 py-0.5 rounded border border-slate-200">
                    Inference
                  </span>
                </div>
                <h4 className="text-sm font-semibold text-slate-900 mb-1">{t('এআই মডেল', 'AI Model')}</h4>
                <p className="text-xs text-slate-500 leading-normal">
                  {t('ফলন গণনা ও ব্যাখ্যা তৈরি', 'Yield inference & explainability generation')}
                </p>
              </div>
              <div className="mt-4 pt-2 border-t border-slate-200/50 flex items-center text-[11px] font-medium text-emerald-800">
                <span>XGBoost + SHAP Tree</span>
              </div>
            </div>

            {/* Step 4: Response */}
            <div className="group relative bg-slate-50/70 hover:bg-white rounded-xl p-4 border border-slate-200/80 hover:border-emerald-300 hover:shadow-md transition-all duration-200 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="w-7 h-7 rounded-full bg-emerald-900 text-white font-bold text-xs flex items-center justify-center ring-4 ring-emerald-50 shadow-sm">
                    4
                  </span>
                  <span className="text-[10px] font-mono font-medium text-slate-400 bg-white px-1.5 py-0.5 rounded border border-slate-200">
                    Delivery
                  </span>
                </div>
                <h4 className="text-sm font-semibold text-slate-900 mb-1">{t('ফলাফল প্রদান', 'Response')}</h4>
                <p className="text-xs text-slate-500 leading-normal">
                  {t('সহজ ভাষায় কৃষকের কাছে উপস্থাপন', 'Clear result representation for farmers')}
                </p>
              </div>
              <div className="mt-4 pt-2 border-t border-slate-200/50 flex items-center text-[11px] font-medium text-emerald-800">
                <span>Localized Visuals / SMS</span>
              </div>
            </div>
          </div>
        </div>
      </article>

      {/* SECTION 2: Security Specifications */}
      <article className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 sm:p-7 space-y-5">
        <div className="space-y-1">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <h2 className="text-base font-bold text-slate-900 tracking-tight flex items-center space-x-2 font-display">
              <span className="w-2 h-2 rounded-full bg-emerald-600"></span>
              <span>{t('নিরাপত্তা', 'Security')}</span>
            </h2>
            <span className="inline-flex items-center space-x-1 text-[11px] font-medium bg-emerald-50 text-emerald-800 border border-emerald-200/70 px-2.5 py-0.5 rounded-full">
              <svg className="w-3 h-3 text-emerald-600 shrink-0" width="12" height="12" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" clipRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" />
              </svg>
              <span>{t('AES-256 এনক্রিপশন প্রয়োগকৃত', 'AES-256 Storage Enforced')}</span>
            </span>
          </div>
          <p className="text-sm text-slate-600 leading-relaxed">
            {t('আমরা আধুনিক অথেন্টিকেশন ও এনক্রিপশন প্রোটোকল ব্যবহার করে অ্যাকাউন্ট ও তথ্যের সুরক্ষাকে সর্বোচ্চ অগ্রাধিকার দিই।', 'We prioritize user account and data protection using industry-standard authentication and encryption.')}
          </p>
        </div>

        {/* Security Item 1: JWT Token Security */}
        <div className="border border-slate-200/80 rounded-xl p-4 bg-slate-50/50 hover:bg-slate-50 transition-colors flex items-start space-x-3.5">
          <div className="p-2 bg-emerald-100/70 text-emerald-800 rounded-lg shrink-0 mt-0.5">
            <svg className="w-4 h-4 shrink-0" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <div className="space-y-1 w-full">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <h4 className="text-sm font-semibold text-slate-900">{t('JWT টোকেন নিরাপত্তা', 'JWT Token Security')}</h4>
              <span className="text-[10px] font-mono font-medium text-emerald-800 bg-emerald-100/80 px-2 py-0.5 rounded-full">{t('২৪ ঘণ্টা মেয়াদ', '24h Expiry')}</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              {t('প্রতিটি সুরক্ষিত এপিআই অনুরোধের জন্য Bearer Access Tokens আবশ্যক যা ২৪ ঘণ্টা পর স্বয়ংক্রিয়ভাবে মোছ যায়।', 'All protected API requests require Bearer Access Tokens that expire after 24 hours.')}
            </p>
          </div>
        </div>

        {/* Security Item 2: Password Hashing */}
        <div className="border border-slate-200/80 rounded-xl p-4 bg-slate-50/50 hover:bg-slate-50 transition-colors flex items-start space-x-3.5">
          <div className="p-2 bg-emerald-100/70 text-emerald-800 rounded-lg shrink-0 mt-0.5">
            <svg className="w-4 h-4 shrink-0" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <div className="space-y-1 w-full">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <h4 className="text-sm font-semibold text-slate-900">{t('পাসওয়ার্ড হ্যাশিং', 'Password Hashing')}</h4>
              <span className="text-[10px] font-mono font-medium text-emerald-800 bg-emerald-100/80 px-2 py-0.5 rounded-full">{t('জিরো প্লেনটেক্সট', 'Zero Plaintext')}</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              {t('পাসওয়ার্ড সরাসরি প্লেইনটেক্সটে সংরক্ষণ করা হয় না; সল্টেড পাসওয়ার্ড হ্যাশিং কঠোরভাবে প্রয়োগ করা হয়।', 'Passwords are never stored in plaintext; salted password hashing is strictly enforced.')}
            </p>
          </div>
        </div>

        {/* Security Item 3: Data Purpose */}
        <div className="border border-slate-200/80 rounded-xl p-4 bg-slate-50/50 hover:bg-slate-50 transition-colors flex items-start space-x-3.5">
          <div className="p-2 bg-emerald-100/70 text-emerald-800 rounded-lg shrink-0 mt-0.5">
            <svg className="w-4 h-4 shrink-0" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <div className="space-y-1 w-full">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <h4 className="text-sm font-semibold text-slate-900">{t('ডেটা ব্যবহারের উদ্দেশ্য', 'Data Purpose')}</h4>
              <span className="text-[10px] font-mono font-medium text-emerald-800 bg-emerald-100/80 px-2 py-0.5 rounded-full">{t('ফেয়ার ইউজ নীতি', 'Fair Use Principle')}</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              {t('কেবল পূর্বাভাস উন্নত করা এবং কৃষকদের ব্যক্তিগত সুবিধা দিতেই তথ্য ব্যবহার করা হয়।', 'Data is strictly gathered to improve prediction accuracy and personalize farmer experience.')}
            </p>
          </div>
        </div>
      </article>

      {/* SECTION 3: Data Ownership */}
      <article className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 sm:p-7 space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <h2 className="text-base font-bold text-slate-900 tracking-tight flex items-center space-x-2 font-display">
            <span className="w-2 h-2 rounded-full bg-emerald-600"></span>
            <span>{t('ডেটা মালিকানা', 'Data Ownership')}</span>
          </h2>
          <span className="inline-flex items-center space-x-1.5 text-xs font-semibold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200">
            <svg className="w-3.5 h-3.5 text-emerald-600 shrink-0" width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
            </svg>
            <span>{t('কৃষকের পূর্ণ অধিকার নিশ্চয়তা', 'Farmer-First Sovereign Guarantee')}</span>
          </span>
        </div>
        <div className="space-y-2 text-sm text-slate-600 leading-relaxed">
          <p>
            {t('আপনার খামার ও ফসলের তথ্যের একমাত্র মালিক আপনি। ফিল্ডফোরসাইট আপনার কোনো ব্যক্তিগত তথ্য তৃতীয় পক্ষের কাছে বিক্রি বা হস্তান্তর করে না।', 'You maintain complete ownership of your farm data. FieldForesight never sells or shares your personal details with third parties.')}
          </p>
          <p>
            {t('আপনি যেকোনো সময় আপনার তথ্য দেখতে বা মুছে ফেলার অনুরোধ করতে পারবেন।', 'You can modify your preferences or request data removal at any time.')}
          </p>
        </div>

        {/* Trust Indicator Box */}
        <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 flex-wrap gap-3">
          <div className="flex items-center space-x-2 text-emerald-700">
            <svg className="w-4 h-4 text-emerald-600 shrink-0" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
            </svg>
            <span className="font-medium">{t('আপনার অ্যাকাউন্ট সেটিংস থেকে সরাসরি ডেটা ডিলিট করার ব্যবস্থা রয়েছে', 'Self-service data removal directly accessible through your account preferences')}</span>
          </div>
          <Link to="/dashboard?tab=my-data" className="font-semibold text-emerald-700 hover:text-emerald-800 hover:underline shrink-0">
            {t('ডেটা সেটিংস পরিচালনা করুন →', 'Manage Preferences →')}
          </Link>
        </div>
      </article>
    </div>
  );
};

