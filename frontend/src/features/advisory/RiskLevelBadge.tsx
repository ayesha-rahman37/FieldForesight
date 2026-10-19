import React from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { AlertTriangle, ShieldCheck, AlertCircle } from 'lucide-react';

export type RiskLevel = 'high' | 'medium' | 'low';

interface RiskLevelBadgeProps {
  level: RiskLevel;
  score?: number;
  showScore?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const RiskLevelBadge: React.FC<RiskLevelBadgeProps> = ({
  level,
  score,
  showScore = true,
  size = 'md',
  className = '',
}) => {
  const { t } = useLanguage();

  const config = {
    high: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-700',
      ring: 'ring-red-400/30',
      pulseDot: 'bg-red-500',
      icon: AlertCircle,
      labelBn: 'উচ্চ ঝুঁকি',
      labelEn: 'High Risk',
    },
    medium: {
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      text: 'text-amber-800',
      ring: 'ring-amber-400/30',
      pulseDot: 'bg-amber-500',
      icon: AlertTriangle,
      labelBn: 'মাঝারি ঝুঁকি',
      labelEn: 'Medium Risk',
    },
    low: {
      bg: 'bg-emerald-50',
      border: 'border-emerald-200',
      text: 'text-emerald-800',
      ring: 'ring-emerald-400/30',
      pulseDot: 'bg-emerald-500',
      icon: ShieldCheck,
      labelBn: 'কম / স্বাভাবিক ঝুঁকি',
      labelEn: 'Low Risk',
    },
  }[level] || {
    bg: 'bg-slate-50',
    border: 'border-slate-200',
    text: 'text-slate-700',
    ring: 'ring-slate-400/30',
    pulseDot: 'bg-slate-400',
    icon: ShieldCheck,
    labelBn: 'স্বাভাবিক',
    labelEn: 'Normal',
  };

  const Icon = config.icon;

  const sizeClasses = {
    sm: 'text-[11px] px-2 py-0.5 gap-1.5',
    md: 'text-xs px-2.5 py-1 gap-2',
    lg: 'text-sm px-3.5 py-1.5 gap-2.5',
  }[size];

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  }[size];

  return (
    <div
      className={`inline-flex items-center rounded-full font-bold uppercase tracking-wider border shadow-sm transition-all ${config.bg} ${config.border} ${config.text} ${sizeClasses} ${className}`}
    >
      <span className="relative flex h-2 w-2">
        <span
          className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${config.pulseDot}`}
        />
        <span className={`relative inline-flex rounded-full h-2 w-2 ${config.pulseDot}`} />
      </span>

      <Icon className={iconSizes} />

      <span>{t(config.labelBn, config.labelEn)}</span>

      {showScore && score !== undefined && (
        <span
          className={`ml-0.5 px-1.5 py-0.2 rounded-full font-mono text-[10px] font-semibold bg-white/70 border border-black/5`}
        >
          {Math.round(score)}%
        </span>
      )}
    </div>
  );
};
