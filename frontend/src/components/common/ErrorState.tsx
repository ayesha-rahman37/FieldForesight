import React from 'react';
import { AlertTriangle, RotateCw } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
  featureName?: string;
  className?: string;
  style?: React.CSSProperties;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  message,
  onRetry,
  featureName,
  className = '',
  style,
}) => {
  const { t } = useLanguage();

  const displayMessage = featureName
    ? `${t(`${featureName} লোড করা যায়নি`, `Failed to load ${featureName}`)}: ${message}`
    : message;

  return (
    <div
      className={`py-3 px-4 bg-amber-50/70 border border-amber-200/80 rounded-xl flex items-center justify-between gap-3 text-xs ${className}`}
      style={style}
    >
      <div className="flex items-center gap-2 min-w-0">
        <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0" />
        <span className="font-medium text-slate-700 truncate">{displayMessage}</span>
      </div>

      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="inline-flex items-center gap-1.5 font-bold text-[#0B5D45] hover:underline shrink-0 cursor-pointer"
        >
          <RotateCw className="w-3.5 h-3.5" />
          <span>{t('আবার চেষ্টা করুন', 'Try again')}</span>
        </button>
      )}
    </div>
  );
};
