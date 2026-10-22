import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Skeleton } from '../../components/common/SkeletonLoader';
import { ErrorState } from '../../components/common/ErrorState';
import { useMinDelay } from '../../hooks/useMinDelay';
import { fetchMyData, deleteData, type MyDataResponse } from '../../api/dataOwnership';
import { useLanguage } from '../../context/LanguageContext';
import { useAuth } from '../../context/AuthContext';
import { ExplainabilityPanel } from '../explainability/ExplainabilityPanel';
import {
  UserCircle,
  BarChart3,
  Sliders,
  Trash2,
  X,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Info,
  Calendar,
  RefreshCw,
} from 'lucide-react';

export const MyDataPanel: React.FC = () => {
  const { t } = useLanguage();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [data, setData] = useState<MyDataResponse | null>(null);
  const [rawLoading, setRawLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);
  const [deleting, setDeleting] = useState<string | null>(null);

  // Active Drawers / Modals
  const [activeDrawer, setActiveDrawer] = useState<'profile' | 'predictions' | 'preferences' | null>(null);
  const [deleteModalType, setDeleteModalType] = useState<'profile' | 'prediction_history' | 'preferences' | null>(null);

  // Profile deletion username verification
  const [typedConfirmUsername, setTypedConfirmUsername] = useState<string>('');

  // Selected prediction for explainability preview
  const [selectedExplainId, setSelectedExplainId] = useState<number | null>(null);

  // Toast feedback state
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ message, type });
    setTimeout(() => {
      setToast(null);
    }, 3500);
  };

  const loading = useMinDelay(rawLoading, 250);

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
    void loadData();
  }, []);

  const handleExecuteDelete = async (dataType: 'profile' | 'prediction_history' | 'preferences') => {
    setDeleting(dataType);
    try {
      await deleteData(dataType);
      setDeleteModalType(null);
      setTypedConfirmUsername('');

      if (dataType === 'profile') {
        showToast(t('মুছে ফেলা হয়েছে', 'Deleted successfully'), 'success');
        logout();
        navigate('/');
        return;
      }

      if (dataType === 'prediction_history' || dataType === 'preferences') {
        // Clear active session forecast from localStorage
        try {
          localStorage.removeItem('fieldforesight_active_forecast');
        } catch {
          // Ignore
        }
      }

      // Refresh real counts from backend — never optimistic!
      await loadData();
      showToast(t('মুছে ফেলা হয়েছে', 'Deleted successfully'), 'success');
    } catch {
      showToast(t('মুছতে পারিনি, আবার চেষ্টা করুন', 'Failed to delete, please try again'), 'error');
    } finally {
      setDeleting(null);
    }
  };

  const profileUsername = data?.profile?.username || user?.username || '';
  const isProfileDeleteDisabled =
    typedConfirmUsername.trim() !== profileUsername.trim() || deleting === 'profile';

  const predictionCount =
    data?.prediction_count !== undefined
      ? data.prediction_count
      : (data?.prediction_history?.length ?? 0);

  const hasPreferences = Boolean(
    data?.saved_preference &&
      (data.saved_preference.last_crop || data.saved_preference.last_region)
  );
  const preferencesCount = hasPreferences ? 1 : 0;

  if (loading) {
    return (
      <div className="w-full max-w-4xl mx-auto bg-white rounded-2xl border border-[#E5E7EB] shadow-xs p-6 sm:p-8 space-y-6">
        <div className="space-y-2 pb-4 border-b border-[#E5E7EB]">
          <Skeleton width="180px" height="24px" borderRadius="8px" />
          <Skeleton width="340px" height="14px" borderRadius="6px" />
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center justify-between p-4 rounded-xl border border-[#E5E7EB] gap-4">
              <div className="flex items-center space-x-4 flex-1">
                <Skeleton width="48px" height="48px" borderRadius="12px" className="shrink-0" />
                <div className="space-y-2 flex-1">
                  <Skeleton width="140px" height="16px" borderRadius="6px" />
                  <Skeleton width="220px" height="12px" borderRadius="6px" />
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
          message={t('ডেটা লোড করতে সমস্যা হয়েছে।', 'Failed to load telemetry data.')}
          onRetry={() => void loadData()}
        />
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto bg-white rounded-2xl border border-[#E5E7EB] shadow-xs overflow-hidden relative">
      {/* Floating Toast Notification */}
      {toast && (
        <div className="fixed top-5 right-5 z-50 animate-in fade-in slide-in-from-top-4 duration-200">
          <div
            className={`flex items-center gap-2.5 px-4 py-3 rounded-xl shadow-lg border text-xs font-semibold ${
              toast.type === 'success'
                ? 'bg-emerald-950 text-emerald-100 border-emerald-800'
                : 'bg-rose-950 text-rose-100 border-rose-800'
            }`}
          >
            {toast.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            )}
            <span>{toast.message}</span>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="px-6 sm:px-8 pt-7 pb-5 border-b border-[#E5E7EB] bg-[#FAF9F5]">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-3">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#004741]">
              {t('আমার ডেটা নিয়ন্ত্রণ', 'My Data Control')}
            </h1>
            <span className="text-xs font-mono font-bold bg-[#E6F0ED] text-[#004741] px-2.5 py-1 rounded-md border border-[#C2DFD6]">
              {t('টেলিমেট্রি স্টোরেজ', 'Telemetry Storage')}
            </span>
          </div>
          <button
            type="button"
            onClick={() => void loadData()}
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition"
            title={t('পুনরায় লোড করুন', 'Refresh')}
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
        <p className="text-xs sm:text-sm text-slate-600 mt-1.5 font-normal">
          {t(
            'আপনার কৃষি টেলিমেট্রি রেকর্ড এবং ক্লাউড পছন্দ পরিচালনা, পরিদর্শন বা স্থায়ীভাবে মুছে ফেলুন।',
            'Manage, inspect, or wipe your agricultural telemetry records and cloud preferences.'
          )}
        </p>
      </div>

      {/* Three Primary Cards */}
      <div className="p-6 sm:p-8 space-y-4">
        {/* Card 1: Profile Data */}
        <div className="group flex flex-col sm:flex-row sm:items-center justify-between p-4 sm:p-5 rounded-xl border border-[#E5E7EB] bg-white hover:border-[#004741]/40 hover:shadow-xs transition gap-4">
          <div
            className="flex items-center space-x-4 flex-1 cursor-pointer"
            onClick={() => setActiveDrawer('profile')}
          >
            <div className="w-12 h-12 rounded-xl bg-[#E6F0ED] border border-[#C2DFD6] flex items-center justify-center text-[#004741] group-hover:scale-105 transition shrink-0">
              <UserCircle className="w-6 h-6" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <h2 className="text-sm sm:text-base font-bold text-slate-900 group-hover:text-[#004741] transition">
                  {t('প্রোফাইল ডেটা', 'Profile Data')}
                </h2>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-[#004741] group-hover:translate-x-0.5 transition" />
              </div>
              <p className="text-xs text-slate-500 mt-0.5 truncate">
                {t('আপনার নাম, ইমেইল এবং অ্যাকাউন্ট তথ্য', 'Your username, email, role, and registered account telemetry')}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setDeleteModalType('profile')}
            className="flex items-center justify-center space-x-1.5 text-xs font-bold text-rose-700 bg-rose-50 border border-rose-200 hover:bg-rose-100 px-3.5 py-2 rounded-lg transition active:scale-95 cursor-pointer self-end sm:self-center shrink-0"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>{t('মুছুন', 'Delete')}</span>
          </button>
        </div>

        {/* Card 2: Prediction History */}
        <div className="group flex flex-col sm:flex-row sm:items-center justify-between p-4 sm:p-5 rounded-xl border border-[#E5E7EB] bg-white hover:border-[#004741]/40 hover:shadow-xs transition gap-4">
          <div
            className="flex items-center space-x-4 flex-1 cursor-pointer"
            onClick={() => setActiveDrawer('predictions')}
          >
            <div className="w-12 h-12 rounded-xl bg-[#E6F0ED] border border-[#C2DFD6] flex items-center justify-center text-[#004741] group-hover:scale-105 transition shrink-0">
              <BarChart3 className="w-6 h-6" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2.5">
                <h2 className="text-sm sm:text-base font-bold text-slate-900 group-hover:text-[#004741] transition">
                  {t('পূর্বাভাস ইতিহাস', 'Prediction History')}
                </h2>
                <span className="inline-flex items-center justify-center text-[11px] font-bold font-mono bg-[#E6F0ED] text-[#004741] border border-[#C2DFD6] px-2 py-0.5 rounded-full">
                  {predictionCount}
                </span>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-[#004741] group-hover:translate-x-0.5 transition" />
              </div>
              <p className="text-xs text-slate-500 mt-0.5 truncate">
                {t('আপনার আগের করা পূর্বাভাসগুলো', 'Historical yield forecasts, bounds, and confidence evaluations')}
              </p>
            </div>
          </div>
          <button
            type="button"
            disabled={predictionCount === 0}
            onClick={() => setDeleteModalType('prediction_history')}
            className="flex items-center justify-center space-x-1.5 text-xs font-bold text-rose-700 bg-rose-50 border border-rose-200 hover:bg-rose-100 disabled:opacity-50 disabled:cursor-not-allowed px-3.5 py-2 rounded-lg transition active:scale-95 cursor-pointer self-end sm:self-center shrink-0"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>{t('মুছুন', 'Delete')}</span>
          </button>
        </div>

        {/* Card 3: Saved Preferences */}
        <div className="group flex flex-col sm:flex-row sm:items-center justify-between p-4 sm:p-5 rounded-xl border border-[#E5E7EB] bg-white hover:border-[#004741]/40 hover:shadow-xs transition gap-4">
          <div
            className="flex items-center space-x-4 flex-1 cursor-pointer"
            onClick={() => setActiveDrawer('preferences')}
          >
            <div className="w-12 h-12 rounded-xl bg-[#E6F0ED] border border-[#C2DFD6] flex items-center justify-center text-[#004741] group-hover:scale-105 transition shrink-0">
              <Sliders className="w-6 h-6" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2.5">
                <h2 className="text-sm sm:text-base font-bold text-slate-900 group-hover:text-[#004741] transition">
                  {t('সংরক্ষিত পছন্দসমূহ', 'Saved Preferences')}
                </h2>
                <span className="inline-flex items-center justify-center text-[11px] font-bold font-mono bg-[#E6F0ED] text-[#004741] border border-[#C2DFD6] px-2 py-0.5 rounded-full">
                  {preferencesCount}
                </span>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-[#004741] group-hover:translate-x-0.5 transition" />
              </div>
              <p className="text-xs text-slate-500 mt-0.5 truncate">
                {t('আপনার নির্বাচিত ফসল ও অঞ্চল', 'Your preferred crop and district selections for automatic loading')}
              </p>
            </div>
          </div>
          <button
            type="button"
            disabled={!hasPreferences}
            onClick={() => setDeleteModalType('preferences')}
            className="flex items-center justify-center space-x-1.5 text-xs font-bold text-rose-700 bg-rose-50 border border-rose-200 hover:bg-rose-100 disabled:opacity-50 disabled:cursor-not-allowed px-3.5 py-2 rounded-lg transition active:scale-95 cursor-pointer self-end sm:self-center shrink-0"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>{t('মুছুন', 'Delete')}</span>
          </button>
        </div>
      </div>

      {/* Footer Note */}
      <div className="px-6 sm:px-8 py-4 bg-[#FAF9F5] border-t border-[#E5E7EB] flex items-center justify-between text-xs text-slate-600 gap-2">
        <div className="flex items-center space-x-2 text-slate-600">
          <Info className="w-4 h-4 text-slate-500 shrink-0" />
          <span className="font-medium">
            {t(
              'ডেটা মোছা স্থায়ী এবং সিঙ্ক করা ডিভাইস জুড়ে পূর্বাবস্থায় ফেরানো যাবে না।',
              'Data deletion is permanent and cannot be undone across synced devices.'
            )}
          </span>
        </div>
      </div>

      {/* ============================================================ */}
      {/* DRAWER / MODAL: Card 1 (Profile Data)                        */}
      {/* ============================================================ */}
      {activeDrawer === 'profile' && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full border border-[#E5E7EB] shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="px-6 py-4 bg-[#FAF9F5] border-b border-[#E5E7EB] flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <UserCircle className="w-5 h-5 text-[#004741]" />
                <h3 className="text-base font-bold text-slate-900">
                  {t('প্রোফাইল ডেটা বিবরণ', 'Profile Data Details')}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setActiveDrawer(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4 text-xs">
              <div className="space-y-3 bg-slate-50 p-4 rounded-xl border border-slate-200">
                <div className="flex justify-between py-1 border-b border-slate-200/60">
                  <span className="text-slate-500">{t('ব্যবহারকারী নাম (Username):', 'Username:')}</span>
                  <span className="font-bold text-slate-900">{data.profile.username || 'N/A'}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-200/60">
                  <span className="text-slate-500">{t('ইমেইল ঠিকানা (Email):', 'Email:')}</span>
                  <span className="font-bold text-slate-900">{data.profile.email || 'N/A'}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-200/60">
                  <span className="text-slate-500">{t('ভূমিকা (Role):', 'Role:')}</span>
                  <span className="font-bold uppercase tracking-wider text-[#004741]">{data.profile.role || 'farmer'}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">{t('অ্যাকাউন্ট তৈরির তারিখ:', 'Account Created Date:')}</span>
                  <span className="font-bold text-slate-900">{data.profile.created_at || t('অজানা', 'Unknown')}</span>
                </div>
              </div>

              {/* Stored Reason Note */}
              <div className="p-3 bg-emerald-50/70 border border-emerald-200/80 rounded-xl flex items-start gap-2.5 text-emerald-950">
                <Info className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5" />
                <div className="leading-relaxed">
                  <span className="font-bold">{t('কেন রাখা হয়েছে: ', 'Why it is kept: ')}</span>
                  <span>{t('লগইন ও অ্যাকাউন্ট চিনতে', 'Strictly to authenticate and identify your account session.')}</span>
                </div>
              </div>
            </div>

            <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex justify-between items-center">
              <button
                type="button"
                onClick={() => {
                  setActiveDrawer(null);
                  setDeleteModalType('profile');
                }}
                className="text-xs font-bold text-rose-600 hover:text-rose-800 hover:underline flex items-center gap-1"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>{t('অ্যাকাউন্ট মুছুন', 'Delete Account')}</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveDrawer(null)}
                className="px-4 py-2 bg-slate-200 hover:bg-slate-300 rounded-lg text-xs font-bold text-slate-700"
              >
                {t('বন্ধ করুন', 'Close')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* DRAWER / MODAL: Card 2 (Prediction History List)             */}
      {/* ============================================================ */}
      {activeDrawer === 'predictions' && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-3xl w-full border border-[#E5E7EB] shadow-2xl overflow-hidden max-h-[85vh] flex flex-col animate-in fade-in zoom-in-95 duration-150">
            <div className="px-6 py-4 bg-[#FAF9F5] border-b border-[#E5E7EB] flex items-center justify-between shrink-0">
              <div className="flex items-center gap-2.5">
                <BarChart3 className="w-5 h-5 text-[#004741]" />
                <h3 className="text-base font-bold text-slate-900">
                  {t('পূর্বাভাস ইতিহাস তালিকা', 'Prediction History Records')} ({predictionCount})
                </h3>
              </div>
              <button
                type="button"
                onClick={() => {
                  setActiveDrawer(null);
                  setSelectedExplainId(null);
                }}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-3 flex-1 text-xs">
              {data.prediction_history.length === 0 ? (
                <div className="py-12 text-center space-y-3">
                  <p className="text-slate-600 font-medium">
                    {t('এখনো কোনো পূর্বাভাস নেই। প্রথম পূর্বাভাস দেখতে Dashboard-এ যান।', 'No predictions recorded yet. Go to Dashboard to generate your first forecast.')}
                  </p>
                  <Link
                    to="/dashboard"
                    className="inline-flex items-center gap-1.5 px-4 py-2 bg-[#004741] text-white text-xs font-bold rounded-lg hover:bg-[#003833] transition"
                  >
                    <span>{t('ড্যাশবোর্ডে যান', 'Go to Dashboard')}</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              ) : (
                data.prediction_history.map((row) => (
                  <div
                    key={row.prediction_id}
                    className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/70 hover:bg-white hover:border-emerald-300 transition space-y-2"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="flex items-center gap-2.5 flex-wrap">
                        <span className="font-bold text-slate-900 text-sm">{row.crop}</span>
                        <span className="text-slate-400">•</span>
                        <span className="text-slate-700 font-medium">{row.region}</span>
                        <span className="px-2 py-0.5 rounded bg-emerald-100 text-[#004741] font-bold text-[10px]">
                          {row.variety}
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="font-extrabold text-sm text-[#004741]">
                          {row.yield_predicted}
                        </span>
                        {row.lower_bound !== undefined && row.upper_bound !== undefined && (
                          <span className="text-[11px] text-slate-500 font-mono">
                            [{row.lower_bound?.toFixed(2)} - {row.upper_bound?.toFixed(2)} t/ha]
                          </span>
                        )}
                        <button
                          type="button"
                          onClick={() => {
                            const pid = Number(row.prediction_id);
                            setSelectedExplainId(selectedExplainId === pid ? null : pid);
                          }}
                          className="px-2.5 py-1 text-[11px] font-bold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-md transition"
                        >
                          {selectedExplainId === Number(row.prediction_id)
                            ? t('সংক্ষেপ করুন', 'Close Details')
                            : t('বিস্তারিত', 'Details')}
                        </button>
                      </div>
                    </div>
                    <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
                      <Calendar className="w-3 h-3" />
                      <span>{row.date || t('সম্প্রতি', 'Recently')}</span>
                    </div>

                    {/* Inline Explainability Panel when toggled */}
                    {selectedExplainId === Number(row.prediction_id) && (
                      <div className="mt-3 pt-3 border-t border-slate-200">
                        <ExplainabilityPanel predictionId={Number(row.prediction_id)} />
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex justify-end">
              <button
                type="button"
                onClick={() => {
                  setActiveDrawer(null);
                  setSelectedExplainId(null);
                }}
                className="px-4 py-2 bg-slate-200 hover:bg-slate-300 rounded-lg text-xs font-bold text-slate-700"
              >
                {t('বন্ধ করুন', 'Close')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* DRAWER / MODAL: Card 3 (Saved Preferences)                   */}
      {/* ============================================================ */}
      {activeDrawer === 'preferences' && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full border border-[#E5E7EB] shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="px-6 py-4 bg-[#FAF9F5] border-b border-[#E5E7EB] flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <Sliders className="w-5 h-5 text-[#004741]" />
                <h3 className="text-base font-bold text-slate-900">
                  {t('সংরক্ষিত পছন্দসমূহ', 'Saved Preferences')}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setActiveDrawer(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4 text-xs">
              {!hasPreferences ? (
                <div className="py-8 text-center text-slate-500 font-medium">
                  {t('কোনো পছন্দ সংরক্ষিত নেই', 'No preferences saved.')}
                </div>
              ) : (
                <div className="space-y-3 bg-slate-50 p-4 rounded-xl border border-slate-200">
                  <div className="flex justify-between py-1 border-b border-slate-200/60">
                    <span className="text-slate-500">{t('পছন্দের ফসল (Saved Crop):', 'Saved Crop:')}</span>
                    <span className="font-bold text-slate-900">{data.saved_preference?.last_crop || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-200/60">
                    <span className="text-slate-500">{t('পছন্দের জেলা (Saved Region):', 'Saved Region:')}</span>
                    <span className="font-bold text-slate-900">{data.saved_preference?.last_region || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-500">{t('সর্বশেষ আপডেট:', 'Last Updated:')}</span>
                    <span className="font-bold text-slate-900">{data.saved_preference?.updated_at || t('সম্প্রতি', 'Recently')}</span>
                  </div>
                </div>
              )}

              <div className="p-3 bg-emerald-50/70 border border-emerald-200/80 rounded-xl flex items-start gap-2.5 text-emerald-950">
                <Info className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5" />
                <div className="leading-relaxed">
                  {t('এটা ড্যাশবোর্ড খোলার সময় স্বয়ংক্রিয়ভাবে নির্বাচন করা হয়', 'This is automatically selected when opening the dashboard.')}
                </div>
              </div>
            </div>

            <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex justify-end">
              <button
                type="button"
                onClick={() => setActiveDrawer(null)}
                className="px-4 py-2 bg-slate-200 hover:bg-slate-300 rounded-lg text-xs font-bold text-slate-700"
              >
                {t('বন্ধ করুন', 'Close')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* CONFIRMATION MODALS                                          */}
      {/* ============================================================ */}

      {/* Profile Delete Modal */}
      {deleteModalType === 'profile' && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full border border-rose-200 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="p-6 space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-rose-100 text-rose-700 flex items-center justify-center mx-auto">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div className="text-center space-y-2">
                <h3 className="text-base font-bold text-slate-900">
                  {t('অ্যাকাউন্ট স্থায়ীভাবে মুছে ফেলা', 'Permanently Delete Account')}
                </h3>
                <p className="text-xs text-rose-700 font-semibold leading-relaxed">
                  {t(
                    'এটি আপনার অ্যাকাউন্ট স্থায়ীভাবে মুছে দেবে, Prediction History ও Preferences সহ। ফিরিয়ে আনা যাবে না।',
                    'This will permanently delete your account, including all Prediction History and Preferences. This action cannot be undone.'
                  )}
                </p>
              </div>

              <div className="space-y-1.5 pt-2">
                <label className="block text-xs font-bold text-slate-700">
                  {t('নিশ্চিত করতে আপনার ব্যবহারকারী নাম টাইপ করুন:', 'Type your username to confirm:')}{' '}
                  <span className="font-mono text-emerald-800 font-extrabold">{profileUsername}</span>
                </label>
                <input
                  type="text"
                  value={typedConfirmUsername}
                  onChange={(e) => setTypedConfirmUsername(e.target.value)}
                  placeholder={profileUsername}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-mono focus:ring-2 focus:ring-rose-500 focus:border-rose-500 outline-none"
                />
              </div>
            </div>

            <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex justify-end gap-2.5">
              <button
                type="button"
                onClick={() => {
                  setDeleteModalType(null);
                  setTypedConfirmUsername('');
                }}
                className="px-4 py-2 bg-white border border-slate-200 hover:bg-slate-100 rounded-lg text-xs font-bold text-slate-700"
              >
                {t('বাতিল', 'Cancel')}
              </button>
              <button
                type="button"
                disabled={isProfileDeleteDisabled}
                onClick={() => handleExecuteDelete('profile')}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-700 disabled:opacity-40 disabled:cursor-not-allowed rounded-lg text-xs font-bold text-white shadow-xs transition"
              >
                {deleting === 'profile' ? t('মুছা হচ্ছে...', 'Deleting...') : t('স্থায়ীভাবে মুছুন', 'Delete Permanently')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Prediction History Delete Modal */}
      {deleteModalType === 'prediction_history' && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full border border-rose-200 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="p-6 space-y-4 text-center">
              <div className="w-12 h-12 rounded-2xl bg-rose-100 text-rose-700 flex items-center justify-center mx-auto">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div className="space-y-2">
                <h3 className="text-base font-bold text-slate-900">
                  {t('পূর্বাভাস ইতিহাস মুছে ফেলুন', 'Delete Prediction History')}
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed font-medium">
                  {t(
                    `সব ${predictionCount}টি পূর্বাভাস ও সংশ্লিষ্ট ডেটা স্থায়ীভাবে মুছে যাবে। এটি Community ও Explainability-র cache-ও পরিষ্কার করবে।`,
                    `All ${predictionCount} prediction history records will be deleted. This will also clear associated Community and Explainability caches.`
                  )}
                </p>
              </div>
            </div>

            <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex justify-end gap-2.5">
              <button
                type="button"
                onClick={() => setDeleteModalType(null)}
                className="px-4 py-2 bg-white border border-slate-200 hover:bg-slate-100 rounded-lg text-xs font-bold text-slate-700"
              >
                {t('বাতিল', 'Cancel')}
              </button>
              <button
                type="button"
                disabled={deleting === 'prediction_history'}
                onClick={() => handleExecuteDelete('prediction_history')}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-700 disabled:opacity-40 rounded-lg text-xs font-bold text-white shadow-xs transition"
              >
                {deleting === 'prediction_history' ? t('মুছা হচ্ছে...', 'Deleting...') : t('মুছে ফেলুন', 'Confirm Delete')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Preferences Delete Modal */}
      {deleteModalType === 'preferences' && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full border border-rose-200 shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="p-6 space-y-4 text-center">
              <div className="w-12 h-12 rounded-2xl bg-rose-100 text-rose-700 flex items-center justify-center mx-auto">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div className="space-y-2">
                <h3 className="text-base font-bold text-slate-900">
                  {t('পছন্দসমূহ মুছে ফেলুন', 'Delete Preferences')}
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed font-medium">
                  {t(
                    'সংরক্ষিত ফসল ও জেলার পছন্দসমূহ মুছে ফেলা হবে। পরবর্তী বার ড্যাশবোর্ডে খালি নির্বাচন দেখাবে।',
                    'Saved crop and region preferences will be deleted. On your next visit, the dashboard will open with empty selectors.'
                  )}
                </p>
              </div>
            </div>

            <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex justify-end gap-2.5">
              <button
                type="button"
                onClick={() => setDeleteModalType(null)}
                className="px-4 py-2 bg-white border border-slate-200 hover:bg-slate-100 rounded-lg text-xs font-bold text-slate-700"
              >
                {t('বাতিল', 'Cancel')}
              </button>
              <button
                type="button"
                disabled={deleting === 'preferences'}
                onClick={() => handleExecuteDelete('preferences')}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-700 disabled:opacity-40 rounded-lg text-xs font-bold text-white shadow-xs transition"
              >
                {deleting === 'preferences' ? t('মুছা হচ্ছে...', 'Deleting...') : t('মুছে ফেলুন', 'Confirm Delete')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
