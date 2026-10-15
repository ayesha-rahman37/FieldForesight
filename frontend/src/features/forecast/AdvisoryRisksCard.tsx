import React, { useEffect, useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { Lightbulb, Sparkles, ShieldAlert } from 'lucide-react';
import api from '../../api/client';
import { RiskLevelBadge, type RiskLevel } from '../advisory/RiskLevelBadge';
import { WarningCards, type RiskAlertItem } from '../advisory/WarningCards';
import { BanglaAdvisorySection } from '../advisory/BanglaAdvisorySection';

interface AdvisoryRisksCardProps {
  crop: string;
  region: string;
  yieldVal: number;
  variety?: string;
  predictionId?: number | null;
  lowerBound?: number;
  upperBound?: number;
}

interface AdvisoryResponse {
  id?: number;
  crop: string;
  region: string;
  variety: string;
  predicted_yield: number;
  risk_level: RiskLevel;
  risk_score: number;
  advisory_text: string;
  action_items: string[];
  precaution_alert?: string;
  warning_alerts?: RiskAlertItem[];
  llm_provider: string;
  llm_model?: string;
}

export const AdvisoryRisksCard: React.FC<AdvisoryRisksCardProps> = ({
  crop,
  region,
  yieldVal,
  variety = 'HYV',
  predictionId,
  lowerBound,
  upperBound,
}) => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState<'advisory' | 'warnings'>('advisory');
  const [advisory, setAdvisory] = useState<AdvisoryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    setError(false);
    try {
      const res = await api.post<AdvisoryResponse>('/api/advisory/generate', {
        crop,
        region,
        variety,
        predicted_yield: yieldVal,
        lower_bound: lowerBound,
        upper_bound: upperBound,
        prediction_id: predictionId || undefined,
      });
      setAdvisory(res.data);
    } catch {
      // Fallback GET
      try {
        const getRes = await api.get<AdvisoryResponse>('/api/advisory/generate', {
          params: {
            crop,
            region,
            variety,
            yield: yieldVal,
            prediction_id: predictionId || undefined,
          },
        });
        setAdvisory(getRes.data);
      } catch {
        setError(true);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [crop, region, yieldVal, variety, predictionId]);

  return (
    <div className="bg-[#FBFAF6] border border-[#E5E1D6] rounded-2xl p-6 shadow-[0_1px_2px_rgba(0,0,0,0.04)] flex flex-col justify-between h-full space-y-4">
      <div>
        {/* Header with Risk Level Badge */}
        <div className="flex items-center justify-between flex-wrap gap-2 mb-4">
          <div className="flex items-center gap-1.5">
            <span className="text-amber-700 text-xs font-bold">⚠</span>
            <h3 className="text-xs font-bold uppercase tracking-[0.06em] text-[#4A4A44]">
              {t('ঝুঁকি মূল্যায়ন ও বাংলা পরামর্শ', 'RISK EVALUATION & ADVISORY')}
            </h3>
          </div>

          {advisory && (
            <RiskLevelBadge
              level={advisory.risk_level}
              score={advisory.risk_score}
              size="sm"
            />
          )}
        </div>

        {/* View Switcher Tabs */}
        <div className="flex rounded-xl bg-[#EFECE3] p-1 mb-4 text-xs font-semibold">
          <button
            type="button"
            onClick={() => setActiveTab('advisory')}
            className={`flex-1 py-1.5 px-3 rounded-lg transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'advisory'
                ? 'bg-white text-[#004741] shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Lightbulb className="w-3.5 h-3.5 text-emerald-600" />
            <span>{t('কৃষি পরামর্শ (AI Advisory)', 'AI Advisory')}</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('warnings')}
            className={`flex-1 py-1.5 px-3 rounded-lg transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'warnings'
                ? 'bg-white text-[#004741] shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
            <span>
              {t('সতর্কতা কার্ড', 'Warning Cards')}
              {advisory?.warning_alerts && (
                <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] bg-amber-100 text-amber-900 font-bold">
                  {advisory.warning_alerts.length}
                </span>
              )}
            </span>
          </button>
        </div>

        {/* Tab Content */}
        {loading ? (
          <div className="space-y-3 animate-pulse">
            <div className="h-20 bg-slate-100 rounded-xl" />
            <div className="h-20 bg-slate-100 rounded-xl" />
          </div>
        ) : error ? (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-xs flex items-center justify-between">
            <span className="text-red-700">
              {t('পরামর্শ ও ঝুঁকি উপাত্ত লোড করতে ত্রুটি।', 'Failed to load advisory data.')}
            </span>
            <button
              onClick={loadData}
              className="px-2.5 py-1 bg-red-600 text-white rounded-lg text-[11px] font-semibold"
            >
              {t('পুনরায় চেষ্টা', 'Retry')}
            </button>
          </div>
        ) : activeTab === 'advisory' ? (
          <BanglaAdvisorySection
            crop={crop}
            region={region}
            yieldVal={yieldVal}
            variety={variety}
            predictionId={predictionId}
          />
        ) : (
          <WarningCards
            crop={crop}
            region={region}
            variety={variety}
            yieldVal={yieldVal}
            initialAlerts={advisory?.warning_alerts}
          />
        )}
      </div>

      {/* Footer Info */}
      <div className="pt-2 border-t border-[#E5E1D6]/70 flex items-center justify-between text-[11px] text-slate-500">
        <span className="flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-emerald-600" />
          <span>{advisory?.llm_provider === 'groq' ? 'Groq Llama-3.3-70B' : 'BARC Rules'}</span>
        </span>
        <span>
          {t('মডেল রেজাল্ট ভিত্তিক ক্যালিব্রেটেড', 'Calibrated on prediction output')}
        </span>
      </div>
    </div>
  );
};
