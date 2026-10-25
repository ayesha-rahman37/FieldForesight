import React, { useEffect, useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import {
  AlertTriangle,
  ClipboardCheck,
  Volume2,
  VolumeX,
  Check,
  AlertCircle,
} from 'lucide-react';
import api from '../../api/client';
import { type RiskLevel } from '../advisory/RiskLevelBadge';
import { type RiskAlertItem } from '../advisory/WarningCards';
import { ErrorState } from '../../components/common/ErrorState';

interface AdvisoryRisksCardProps {
  crop: string;
  region: string;
  yieldVal: number;
  variety?: string;
  predictionId?: number | null;
  lowerBound?: number;
  upperBound?: number;
  rainfallAdj?: number;
  tempAdj?: number;
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
  rainfallAdj = 0,
  tempAdj = 0,
}) => {
  const { t } = useLanguage();
  const [advisory, setAdvisory] = useState<AdvisoryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);
  const [speaking, setSpeaking] = useState<boolean>(false);
  const [completedItems, setCompletedItems] = useState<Record<number, boolean>>({});

  const loadData = async () => {
    setLoading(true);
    setError(false);
    setCompletedItems({});
    try {
      const res = await api.post<AdvisoryResponse>('/api/advisory/generate', {
        crop,
        region,
        variety,
        predicted_yield: yieldVal,
        lower_bound: lowerBound,
        upper_bound: upperBound,
        prediction_id: predictionId || undefined,
        rainfall_adjustment_percent: rainfallAdj,
        temperature_adjustment_percent: tempAdj * 10,
      });
      setAdvisory(res.data);
    } catch {
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
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
    }
  }, [crop, region, yieldVal, variety, predictionId, rainfallAdj, tempAdj]);

  const toggleActionItem = (index: number) => {
    setCompletedItems((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const handleSpeak = () => {
    if (!('speechSynthesis' in window) || !advisory) return;

    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }

    const textToRead = `${advisory.advisory_text}. করণীয় পদক্ষেপসমূহ: ${advisory.action_items.join('. ')}`;
    const utterance = new SpeechSynthesisUtterance(textToRead);
    utterance.lang = 'bn-BD';
    utterance.rate = 0.95;

    const voices = window.speechSynthesis.getVoices();
    const bnVoice = voices.find((v) => v.lang.includes('bn') || v.lang.includes('BD'));
    if (bnVoice) {
      utterance.voice = bnVoice;
    }

    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);

    setSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  const riskLevel = advisory?.risk_level || 'medium';
  const riskScore = advisory?.risk_score !== undefined ? Math.round(advisory.risk_score) : 45;
  const warningCount = advisory?.warning_alerts?.length ?? 1;
  const actionItems = advisory?.action_items ?? [];
  const doneCount = Object.values(completedItems).filter(Boolean).length;

  const riskBadgeStyle =
    riskLevel === 'high'
      ? 'bg-red-50 border-red-200 text-red-700'
      : riskLevel === 'low'
      ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
      : 'bg-amber-50 border-amber-200 text-amber-800';

  const riskDotColor =
    riskLevel === 'high'
      ? 'bg-red-500'
      : riskLevel === 'low'
      ? 'bg-emerald-500'
      : 'bg-amber-500';

  const precautionText =
    advisory?.precaution_alert ||
    advisory?.warning_alerts?.[0]?.action_bn ||
    'আগামী ৭২ ঘণ্টার মধ্যে হালকা সেচ দিলে ফলনের গুণগত মান বৃদ্ধি পাবে।';

  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs">
      {/* Header */}
      <div className="flex items-center gap-2">
        <AlertTriangle className="w-4 h-4 text-amber-600" />
        <h3 className="text-[11px] font-bold uppercase tracking-[0.06em] text-slate-800">
          {t('ঝুঁকি মূল্যায়ন ও বাংলা পরামর্শ', 'RISK EVALUATION & ADVISORY')}
        </h3>
      </div>

      {/* Risk & Warning Pills Row */}
      <div className="mt-2.5 mb-4 flex items-center gap-2 flex-wrap">
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase border ${riskBadgeStyle}`}
        >
          <span className={`w-1.5 h-1.5 rounded-full ${riskDotColor}`} />
          {riskLevel.toUpperCase()} RISK {riskScore}%
        </span>

        <a
          href="#field-warnings-section"
          className="px-2.5 py-0.5 rounded-md bg-slate-100 hover:bg-slate-200/70 border border-slate-200 text-slate-600 text-[11px] font-semibold transition inline-flex items-center gap-1 cursor-pointer"
          title={t('ডানপাশে সতর্কতা দেখুন', 'View warnings on the right')}
        >
          <span>{warningCount} {warningCount === 1 ? 'Warning' : 'Warnings'}</span>
          <span className="text-[10px] text-slate-400">→</span>
        </a>
      </div>

      {loading ? (
        <div className="space-y-3 animate-pulse">
          <div className="h-28 bg-slate-100 rounded-xl" />
          <div className="h-12 bg-slate-100 rounded-xl" />
          <div className="h-12 bg-slate-100 rounded-xl" />
        </div>
      ) : error || !advisory ? (
        <ErrorState
          featureName={t('কৃষি পরামর্শ ও ঝুঁকি', 'Advisory and Risk')}
          onRetry={() => void loadData()}
        />
      ) : (
        <>
          {/* Green Tinted Agricultural Advisory Box */}
          <div className="bg-emerald-50/55 border border-emerald-200/90 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#047857] text-white flex items-center justify-center shrink-0 mt-0.5 shadow-xs">
                <ClipboardCheck className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <h4 className="text-xs font-bold text-slate-900">
                    {t('কৃষি পরামর্শ ও করণীয়', 'Agricultural Advisory & Actions')}
                  </h4>
                  <span className="px-2 py-0.5 rounded bg-emerald-100 border border-emerald-300/80 text-emerald-900 text-[10px] font-bold">
                    {advisory.llm_provider === 'groq' ? 'Groq Llama 3.3' : 'BARC Expert Rule'}
                  </span>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed mt-1.5 font-medium">
                  {advisory.advisory_text}
                </p>
              </div>
            </div>

            <div className="mt-3.5 pt-2.5 border-t border-emerald-200/60 flex items-center justify-between gap-2 flex-wrap">
              <button
                type="button"
                onClick={handleSpeak}
                className={`px-3 py-1 rounded-full border text-[11px] font-bold inline-flex items-center gap-1.5 transition ${
                  speaking
                    ? 'bg-rose-50 border-rose-300 text-rose-700'
                    : 'bg-white hover:bg-emerald-50 border-emerald-300 text-emerald-800'
                }`}
              >
                {speaking ? (
                  <VolumeX className="w-3.5 h-3.5 text-rose-600 animate-pulse" />
                ) : (
                  <Volume2 className="w-3.5 h-3.5 text-emerald-700" />
                )}
                <span>{speaking ? t('থামান (Stop)', 'Stop (থামান)') : 'Listen (শুনুন)'}</span>
              </button>

              <span className="text-[11px] text-emerald-800/80 font-medium inline-flex items-center gap-1">
                <Check className="w-3.5 h-3.5 text-emerald-600" />
                {t('মডেল রেজাল্ট ভিত্তিক ক্যালিব্রেটেড', 'Calibrated on prediction output')}
              </span>
            </div>
          </div>

          {/* Farmer Action Checklist */}
          {actionItems.length > 0 && (
            <div className="mt-5">
              <div className="flex items-center justify-between mb-2.5">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-700">
                  {t('কৃষকের করণীয় তালিকা', 'FARMER ACTION CHECKLIST')}
                </span>
                <span className="px-2 py-0.5 rounded bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-bold">
                  {doneCount} / {actionItems.length} done
                </span>
              </div>

              <div className="space-y-2">
                {actionItems.map((item, idx) => {
                  const isChecked = !!completedItems[idx];
                  return (
                    <div
                      key={idx}
                      onClick={() => toggleActionItem(idx)}
                      className={`p-3 rounded-xl border flex items-start gap-2.5 cursor-pointer select-none transition ${
                        isChecked
                          ? 'bg-emerald-50/50 border-emerald-200 text-emerald-900'
                          : 'bg-white hover:border-slate-300 border-slate-200 text-slate-800'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => {}}
                        className="mt-0.5 h-3.5 w-3.5 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500 cursor-pointer"
                      />
                      <span
                        className={`text-xs leading-relaxed flex-1 ${
                          isChecked ? 'line-through text-slate-400' : 'text-slate-700 font-medium'
                        }`}
                      >
                        {item}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Precaution Alert Banner */}
          <div className="mt-4 p-3 rounded-xl bg-amber-50/90 border border-amber-300/90 flex items-center gap-2 text-xs text-amber-950">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
            <span className="leading-snug">
              <strong className="font-bold">পরামর্শ: </strong>
              <span>{precautionText.replace(/^পরামর্শ:\s*/, '')}</span>
            </span>
          </div>
        </>
      )}
    </div>
  );
};
