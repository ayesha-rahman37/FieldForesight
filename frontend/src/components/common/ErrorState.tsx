import React from 'react';
import { AlertCircle, RotateCcw, Home } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
  onNavigateHome?: () => void;
  featureName?: string;
  compact?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  message,
  onRetry,
  onNavigateHome,
  featureName,
  compact = false,
  className = '',
  style,
}) => {
  const { t } = useLanguage();

  const defaultMsg = featureName
    ? t(`${featureName} অংশটি এখন লোড করা যাচ্ছে না`, `This section could not be loaded right now`)
    : t('এই অংশটি এখন লোড করা যাচ্ছে না', 'This section could not be loaded right now');

  const displayMessage = message || defaultMsg;

  if (compact) {
    return (
      <div
        className={`py-3 px-4 bg-amber-50/70 border border-amber-200/80 rounded-xl flex items-center justify-between gap-3 text-xs ${className}`}
        style={style}
      >
        <div className="flex items-center gap-2 min-w-0">
          <AlertCircle className="w-4 h-4 text-amber-700 shrink-0" />
          <span className="font-medium text-slate-700 truncate">{displayMessage}</span>
        </div>

        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center gap-1.5 font-bold text-[#004741] hover:text-emerald-800 hover:underline shrink-0 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>{t('আবার চেষ্টা করুন', 'Try again')}</span>
          </button>
        )}
      </div>
    );
  }

  return (
    <div
      className={`p-5 sm:p-6 bg-slate-50/80 border border-slate-200/90 rounded-2xl flex flex-col items-center justify-center text-center shadow-2xs ${className}`}
      style={style}
    >
      <div className="w-10 h-10 rounded-full bg-amber-100/70 text-amber-800 flex items-center justify-center mb-3">
        <AlertCircle className="w-5 h-5 text-amber-700" />
      </div>

      <h4 className="text-sm font-bold text-slate-800 mb-1">
        {displayMessage}
      </h4>

      <p className="text-xs text-slate-500 max-w-sm mb-4 leading-relaxed">
        {t(
          'চিন্তার কিছু নেই, আপনার ডেটা সুরক্ষিত রয়েছে। অনুগ্রহ করে পুনরায় চেষ্টা করুন।',
          'Your data is secure. Please try again or return to the dashboard.'
        )}
      </p>

      <div className="flex items-center gap-2.5 flex-wrap justify-center">
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-[#004741] hover:bg-emerald-900 text-white text-xs font-semibold rounded-xl shadow-xs transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>{t('আবার চেষ্টা করুন', 'Try again')}</span>
          </button>
        )}

        {onNavigateHome && (
          <button
            type="button"
            onClick={onNavigateHome}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 text-xs font-semibold rounded-xl shadow-2xs transition-colors cursor-pointer"
          >
            <Home className="w-3.5 h-3.5 text-slate-500" />
            <span>{t('ড্যাশবোর্ডে ফিরে যান', 'Back to Dashboard')}</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorState;
