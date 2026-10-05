import React, { useEffect, useState } from 'react';
import { Skeleton } from '../../components/common/SkeletonLoader';
import { ErrorState } from '../../components/common/ErrorState';
import { useMinDelay } from '../../hooks/useMinDelay';
import { fetchMyData, deleteData } from '../../api/dataOwnership';
import type { MyDataResponse } from '../../api/dataOwnership';
import { useLanguage } from '../../context/LanguageContext';

export const MyDataPanel: React.FC = () => {
  const { t } = useLanguage();
  const [data, setData] = useState<MyDataResponse | null>(null);
  const [rawLoading, setRawLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);
  const [deleting, setDeleting] = useState<string | null>(null);

  const loading = useMinDelay(rawLoading, 300);

  const loadData = async () => {
    setRawLoading(true);
    setError(false);
    try {
      const res = await fetchMyData();
      setData(res);
    } catch {
      setError(true);
    } finally {
      setRawLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDelete = async (dataType: 'profile' | 'prediction_history' | 'preferences') => {
    if (!window.confirm(t('আপনি কি নিশ্চিত যে আপনি এই ডেটা মুছতে চান?', 'Are you sure you want to delete this data?'))) {
      return;
    }
    setDeleting(dataType);
    try {
      await deleteData(dataType);
      await loadData();
    } catch {
      alert(t('ডেটা মুছতে সমস্যা হয়েছে।', 'Failed to delete data.'));
    } finally {
      setDeleting(null);
    }
  };

  if (loading) {
    return (
      <div className="w-full max-w-4xl mx-auto bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden p-6 sm:p-8 space-y-6">
        <div className="space-y-2 pb-4 border-b border-slate-100">
          <Skeleton width="180px" height="24px" borderRadius="6px" />
          <Skeleton width="300px" height="14px" borderRadius="4px" />
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center justify-between p-4 rounded-xl border border-slate-200 gap-4">
              <div className="flex items-center space-x-4 flex-1">
                <Skeleton width="48px" height="48px" borderRadius="12px" className="shrink-0" />
                <div className="space-y-2 flex-1">
                  <Skeleton width="140px" height="16px" borderRadius="4px" />
                  <Skeleton width="220px" height="12px" borderRadius="4px" />
                </div>
              </div>
              <Skeleton width="80px" height="36px" borderRadius="8px" className="shrink-0" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="w-full max-w-4xl mx-auto">
        <ErrorState
          featureName={t('আমার ডেটা নিয়ন্ত্রণ', 'My Data Control')}
          message={t('ডেটা লোড করতে সমস্যা হয়েছে।', 'Failed to load data.')}
          onRetry={loadData}
        />
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden" data-purpose="data-control-card">
      {/* Card Header */}
      <div className="px-6 sm:px-8 pt-8 pb-5 border-b border-slate-100">
        <div className="flex items-center space-x-3">
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 font-display">
            {t('আমার ডেটা নিয়ন্ত্রণ', 'My Data Control')}
          </h1>
          <span className="text-xs font-mono font-medium bg-slate-100 text-slate-700 px-2.5 py-1 rounded-md border border-slate-200">
            {t('টেলিমেট্রি স্টোরেজ', 'Telemetry Storage')}
          </span>
        </div>
        <p className="text-xs sm:text-sm text-slate-500 mt-1.5 font-normal">
          {t('আপনার কৃষি টেলিমেট্রি রেকর্ড এবং ক্লাউড পছন্দ পরিচালনা, পরিদর্শন বা মুছে ফেলুন।', 'Manage, inspect, or wipe your agricultural telemetry records and cloud preferences.')}
        </p>
      </div>

      {/* Action Items Rows */}
      <div className="p-6 sm:p-8 space-y-4">
        {/* Row 1: Profile Data */}
        <div className="group flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl border border-slate-200/90 bg-white hover:border-emerald-300 hover:shadow-sm transition gap-4" data-purpose="data-row-profile">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-600 group-hover:bg-emerald-50 group-hover:text-emerald-700 transition shrink-0">
              <svg className="w-5 h-5 shrink-0" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">{t('প্রোফাইল ডেটা', 'Profile Data')}</h2>
              <p className="text-xs text-slate-500 mt-0.5">{t('আপনার নাম, ইমেইল এবং অ্যাকাউন্ট তথ্য', 'Your name, email and account info')}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => handleDelete('profile')}
            disabled={deleting === 'profile'}
            className="flex items-center justify-center space-x-1.5 text-xs font-semibold text-rose-600 bg-rose-50/70 border border-rose-200 hover:bg-rose-100 px-3.5 py-2 rounded-lg transition active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer self-end sm:self-center"
          >
            <svg className="w-3.5 h-3.5 shrink-0" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <span>{deleting === 'profile' ? t('মুছা হচ্ছে...', 'Deleting...') : t('মুছুন', 'Delete')}</span>
          </button>
        </div>

        {/* Row 2: Prediction History */}
        <div className="group flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl border border-slate-200/90 bg-white hover:border-emerald-300 hover:shadow-sm transition gap-4" data-purpose="data-row-prediction">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-600 group-hover:bg-emerald-50 group-hover:text-emerald-700 transition shrink-0">
              <svg className="w-5 h-5 shrink-0" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base font-semibold text-slate-900">{t('পূর্বাভাস ইতিহাস', 'Prediction History')}</h2>
                <span className="inline-flex items-center justify-center text-[11px] font-semibold font-mono bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full">
                  {data.prediction_history.length}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">{t('আপনার আগের করা পূর্বাভাসগুলো', 'Your previous predictions')}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => handleDelete('prediction_history')}
            disabled={deleting === 'prediction_history' || data.prediction_history.length === 0}
            className="flex items-center justify-center space-x-1.5 text-xs font-semibold text-rose-600 bg-rose-50/70 border border-rose-200 hover:bg-rose-100 px-3.5 py-2 rounded-lg transition active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer self-end sm:self-center"
          >
            <svg className="w-3.5 h-3.5 shrink-0" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <span>{deleting === 'prediction_history' ? t('মুছা হচ্ছে...', 'Deleting...') : t('মুছুন', 'Delete')}</span>
          </button>
        </div>

        {/* Row 3: Saved Preferences */}
        <div className="group flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl border border-slate-200/90 bg-white hover:border-emerald-300 hover:shadow-sm transition gap-4" data-purpose="data-row-preferences">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-600 group-hover:bg-emerald-50 group-hover:text-emerald-700 transition shrink-0">
              <svg className="w-5 h-5 shrink-0" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base font-semibold text-slate-900">{t('সংরক্ষিত পছন্দসমূহ', 'Saved Preferences')}</h2>
                <span className="inline-flex items-center justify-center text-[11px] font-semibold font-mono bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full">
                  {data.saved_preference ? 1 : 0}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">{t('আপনার নির্বাচিত ফসল ও অঞ্চল', 'Your selected crop and region')}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => handleDelete('preferences')}
            disabled={deleting === 'preferences' || !data.saved_preference}
            className="flex items-center justify-center space-x-1.5 text-xs font-semibold text-rose-600 bg-rose-50/70 border border-rose-200 hover:bg-rose-100 px-3.5 py-2 rounded-lg transition active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer self-end sm:self-center"
          >
            <svg className="w-3.5 h-3.5 shrink-0" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <span>{deleting === 'preferences' ? t('মুছা হচ্ছে...', 'Deleting...') : t('মুছুন', 'Delete')}</span>
          </button>
        </div>
      </div>

      {/* Card Internal Footer Disclaimer */}
      <div className="px-6 sm:px-8 py-4 bg-slate-50/70 border-t border-slate-100 flex flex-wrap items-center justify-between text-xs text-slate-500 gap-2" data-purpose="retention-notice">
        <div className="flex items-center space-x-2 text-amber-700">
          <svg className="w-4 h-4 text-amber-600 flex-shrink-0" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span className="font-medium text-slate-600">
            {t('ডেটা মোছা স্থায়ী এবং সিঙ্ক করা ডিভাইস জুড়ে পূর্বাবস্থায় ফেরানো যাবে না।', 'Data deletion is permanent and cannot be undone across synced devices.')}
          </span>
        </div>
        <span className="font-mono text-[11px] text-slate-400 uppercase tracking-wider">
          {t('AES-256 এনক্রিপশন প্রয়োগকৃত', 'AES-256 Storage Enforced')}
        </span>
      </div>
    </div>
  );
};
