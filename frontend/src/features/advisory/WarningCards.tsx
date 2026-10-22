import React, { useEffect, useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import {
  AlertTriangle,
  Bug,
  Droplets,
  CloudRain,
  TrendingDown,
  Info,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
} from 'lucide-react';
import api from '../../api/client';

export interface RiskAlertItem {
  id: string;
  category: string;
  level: 'high' | 'medium' | 'low';
  title: string;
  title_bn?: string;
  title_en?: string;
  description: string;
  description_bn?: string;
  description_en?: string;
  action_bn?: string;
  action_en?: string;
}

export type RiskAlert = RiskAlertItem;

interface WarningCardsProps {
  crop: string;
  region: string;
  variety?: string;
  yieldVal?: number;
  initialAlerts?: RiskAlertItem[];
}

export const WarningCards: React.FC<WarningCardsProps> = ({
  crop,
  region,
  variety = 'HYV',
  yieldVal,
  initialAlerts,
}) => {
  const { t } = useLanguage();
  const [alerts, setAlerts] = useState<RiskAlertItem[]>(initialAlerts || []);
  const [loading, setLoading] = useState<boolean>(!initialAlerts);
  const [error, setError] = useState<boolean>(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const loadAlerts = async () => {
    setLoading(true);
    setError(false);
    try {
      const res = await api.get<RiskAlertItem[]>('/api/risk/alerts', {
        params: { crop, region, variety, yield: yieldVal },
      });
      setAlerts(res.data);
      if (res.data.length > 0) {
        setExpandedId(res.data[0].id);
      }
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialAlerts && initialAlerts.length > 0) {
      setAlerts(initialAlerts);
      setLoading(false);
      setExpandedId(initialAlerts[0].id);
    } else {
      loadAlerts();
    }
  }, [crop, region, variety, yieldVal, initialAlerts]);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'pest':
        return <Bug className="w-4 h-4 text-rose-600" />;
      case 'moisture':
        return <Droplets className="w-4 h-4 text-sky-600" />;
      case 'climate':
        return <CloudRain className="w-4 h-4 text-indigo-600" />;
      case 'yield':
        return <TrendingDown className="w-4 h-4 text-amber-600" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-amber-600" />;
    }
  };

  const getCardStyle = (level: 'high' | 'medium' | 'low') => {
    switch (level) {
      case 'high':
        return {
          borderLeft: 'border-l-4 border-l-red-600',
          bg: 'bg-red-50/60',
          border: 'border-red-200/80',
          titleColor: 'text-red-900',
          badge: 'high' as const,
        };
      case 'medium':
        return {
          borderLeft: 'border-l-4 border-l-amber-500',
          bg: 'bg-amber-50/50',
          border: 'border-amber-200/80',
          titleColor: 'text-amber-950',
          badge: 'medium' as const,
        };
      default:
        return {
          borderLeft: 'border-l-4 border-l-emerald-600',
          bg: 'bg-emerald-50/40',
          border: 'border-emerald-200/80',
          titleColor: 'text-emerald-950',
          badge: 'low' as const,
        };
    }
  };

  if (loading) {
    return (
      <div className="space-y-2.5">
        <div className="h-20 bg-slate-100/80 animate-pulse rounded-xl" />
        <div className="h-16 bg-slate-100/60 animate-pulse rounded-xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-center justify-between">
        <span>{t('ঝুঁকির সতর্কতা লোড করা যায়নি।', 'Failed to load risk warnings.')}</span>
        <button
          onClick={loadAlerts}
          className="px-2.5 py-1 bg-red-600 text-white rounded-lg text-[11px] font-semibold"
        >
          {t('পুনরায় চেষ্টা', 'Retry')}
        </button>
      </div>
    );
  }

  if (alerts.length === 0) {
    return (
      <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 flex items-center gap-2">
        <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
        <span>{t('কোনো গুরুতর ঝুঁকি সতর্কতা নেই। ফসল বৃদ্ধির অবস্থা অনুকূল।', 'No critical risk alerts found. Crop conditions are optimal.')}</span>
      </div>
    );
  }

  return (
    <div className="space-y-2.5">
      {alerts.map((alert) => {
        const style = getCardStyle(alert.level);
        const isExpanded = expandedId === alert.id;
        const title = t(alert.title_bn || alert.title, alert.title_en || alert.title);
        const desc = t(alert.description_bn || alert.description, alert.description_en || alert.description);
        const action = t(alert.action_bn || '', alert.action_en || '');

        return (
          <div
            key={alert.id}
            className={`rounded-xl border ${style.border} ${style.bg} ${style.borderLeft} p-3.5 shadow-sm transition-all duration-200`}
          >
            <div
              className="flex items-start justify-between gap-2 cursor-pointer select-none"
              onClick={() => setExpandedId(isExpanded ? null : alert.id)}
            >
              <div className="flex items-start gap-2.5 flex-1 min-w-0">
                <div className="mt-0.5 p-1 rounded-lg bg-white/80 shadow-xs border border-black/5 flex-shrink-0">
                  {getCategoryIcon(alert.category)}
                </div>
                <div>
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <h4 className={`text-xs font-bold leading-snug ${style.titleColor}`}>
                      {title}
                    </h4>
                    <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-white/80 border border-black/5 text-slate-600">
                      {alert.category}
                    </span>
                  </div>
                  <p className="text-[12px] text-slate-700 leading-relaxed">
                    {desc}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-1 flex-shrink-0 pt-0.5 text-slate-400 hover:text-slate-700">
                {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </div>
            </div>

            {/* Action Item Accordion */}
            {isExpanded && action && (
              <div className="mt-2.5 pt-2.5 border-t border-black/5 flex items-start gap-2 bg-white/60 p-2.5 rounded-lg">
                <Info className="w-3.5 h-3.5 text-emerald-700 flex-shrink-0 mt-0.5" />
                <div className="text-[11px] text-emerald-950 font-medium leading-relaxed">
                  <span className="font-bold text-emerald-900 mr-1">
                    {t('প্রস্তাবিত পদক্ষেপ:', 'Recommended Action:')}
                  </span>
                  {action}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
