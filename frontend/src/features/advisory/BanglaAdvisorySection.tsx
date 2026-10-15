import React, { useEffect, useState } from 'react';
import { ErrorState } from '../../components/common/ErrorState';
import { useLanguage } from '../../context/LanguageContext';
import {
  Volume2,
  VolumeX,
  Copy,
  Check,
  Sparkles,
  CheckSquare,
  Square,
  AlertCircle,
} from 'lucide-react';
import api from '../../api/client';
import { RiskLevelBadge, type RiskLevel } from './RiskLevelBadge';

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
  llm_provider: string;
  llm_model?: string;
}

interface BanglaAdvisorySectionProps {
  crop: string;
  region: string;
  yieldVal: number;
  variety?: string;
  predictionId?: number | null;
  onAdvisoryLoaded?: (data: AdvisoryResponse) => void;
}

export const BanglaAdvisorySection: React.FC<BanglaAdvisorySectionProps> = ({
  crop,
  region,
  yieldVal,
  variety = 'HYV',
  predictionId,
  onAdvisoryLoaded,
}) => {
  const { t } = useLanguage();
  const [data, setData] = useState<AdvisoryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const [speaking, setSpeaking] = useState<boolean>(false);
  const [completedItems, setCompletedItems] = useState<{ [index: number]: boolean }>({});

  const loadAdvisory = async () => {
    setLoading(true);
    setError(false);
    try {
      const res = await api.post<AdvisoryResponse>('/api/advisory/generate', {
        crop,
        region,
        variety,
        predicted_yield: yieldVal,
        prediction_id: predictionId || undefined,
      });
      setData(res.data);
      if (onAdvisoryLoaded) {
        onAdvisoryLoaded(res.data);
      }
    } catch {
      // Fallback to GET endpoint
      try {
        const getRes = await api.get<AdvisoryResponse>('/api/advisory/generate', {
          params: { crop, region, variety, yield: yieldVal, prediction_id: predictionId || undefined },
        });
        setData(getRes.data);
        if (onAdvisoryLoaded) {
          onAdvisoryLoaded(getRes.data);
        }
      } catch {
        setError(true);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdvisory();
    // Stop speech if params change
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
    }
  }, [crop, region, yieldVal, variety, predictionId]);

  const toggleActionItem = (index: number) => {
    setCompletedItems((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const handleCopy = () => {
    if (!data) return;
    const fullText = `${data.advisory_text}\n\nকরণীয়:\n${data.action_items.map((item, i) => `${i + 1}. ${item}`).join('\n')}`;
    navigator.clipboard.writeText(fullText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleSpeak = () => {
    if (!('speechSynthesis' in window) || !data) return;

    if (speaking) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
      return;
    }

    const textToRead = `${data.advisory_text}. করণীয় পদক্ষেপসমূহ: ${data.action_items.join('. ')}`;
    const utterance = new SpeechSynthesisUtterance(textToRead);
    utterance.lang = 'bn-BD';
    utterance.rate = 0.95;

    // Pick a Bengali voice if browser has one installed
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

  if (loading) {
    return (
      <div className="bg-[#FBFAF6] border border-[#E5E1D6] rounded-2xl p-6 shadow-sm space-y-4 animate-pulse">
        <div className="flex items-center justify-between">
          <div className="h-6 w-40 bg-slate-200 rounded-lg" />
          <div className="h-6 w-24 bg-slate-200 rounded-full" />
        </div>
        <div className="h-16 bg-slate-200/70 rounded-xl" />
        <div className="space-y-2">
          <div className="h-8 bg-slate-200/50 rounded-lg" />
          <div className="h-8 bg-slate-200/50 rounded-lg" />
          <div className="h-8 bg-slate-200/50 rounded-lg" />
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <ErrorState
        message={t('পরামর্শ লোড করা যায়নি। পুনরায় চেষ্টা করুন।', 'Failed to load advisory. Please retry.')}
        onRetry={loadAdvisory}
      />
    );
  }

  return (
    <div className="bg-[#FBFAF6] border border-[#E5E1D6] rounded-2xl p-6 shadow-[0_1px_2px_rgba(0,0,0,0.04)] space-y-5 transition-all">
      {/* Header Banner */}
      <div className="flex items-center justify-between flex-wrap gap-3 pb-3 border-b border-[#E5E1D6]">
        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-xl bg-[#004741] text-white flex items-center justify-center text-lg shadow-sm">
            🧑‍🌾
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-[#004741] leading-tight">
                {t('বাংলা কৃষি পরামর্শ ও করণীয়', 'Agricultural Advisory & Actions')}
              </h3>
              <span className="hidden sm:inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
                <Sparkles className="w-3 h-3 text-emerald-600" />
                {data.llm_provider === 'groq' ? 'Groq Llama 3.3 AI' : 'BARC Expert Rule'}
              </span>
            </div>
            <p className="text-[11px] text-[#5A6E69] font-medium">
              {t(
                `${region} অঞ্চলে ${variety} জাতের জন্য স্থানীয় নির্দেশিকা`,
                `Localized advisory for ${variety} in ${region}`
              )}
            </p>
          </div>
        </div>

        {/* Right Header Actions */}
        <div className="flex items-center gap-2">
          <RiskLevelBadge level={data.risk_level} score={data.risk_score} size="sm" />

          {/* Voice Speak Button */}
          <button
            type="button"
            onClick={handleSpeak}
            title={speaking ? t('পড়া থামান', 'Stop Reading') : t('বাংলায় শুনুন', 'Listen in Bengali')}
            className={`p-2 rounded-xl border text-xs font-semibold flex items-center gap-1.5 transition-all ${
              speaking
                ? 'bg-rose-50 text-rose-700 border-rose-200 ring-2 ring-rose-400'
                : 'bg-white hover:bg-slate-50 text-[#004741] border-[#E5E1D6] shadow-xs'
            }`}
          >
            {speaking ? <VolumeX className="w-4 h-4 text-rose-600 animate-pulse" /> : <Volume2 className="w-4 h-4 text-[#0B5D45]" />}
            <span className="hidden md:inline">{speaking ? t('থামান', 'Stop') : t('শুনুন', 'Listen')}</span>
          </button>

          {/* Copy Button */}
          <button
            type="button"
            onClick={handleCopy}
            title={t('পরামর্শ কপি করুন', 'Copy advisory')}
            className="p-2 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-[#E5E1D6] shadow-xs transition-all"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4 text-slate-600" />}
          </button>
        </div>
      </div>

      {/* Main Advisory Box */}
      <div className="p-4 rounded-xl bg-[#F4F1EA] border border-[#E2DDD2] text-[#1F2925] relative">
        <div className="flex items-start gap-3">
          <span className="text-xl select-none">📢</span>
          <p className="text-[14px] sm:text-[15px] leading-relaxed font-normal text-slate-800">
            {data.advisory_text}
          </p>
        </div>
      </div>

      {/* Action Items Interactive Checklist */}
      {data.action_items && data.action_items.length > 0 && (
        <div className="space-y-2.5">
          <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-[#4A4A44]">
            <span>{t('কৃষকের করণীয় অ্যাকশন তালিকা:', 'Farmer Action Checklist:')}</span>
            <span className="text-[11px] font-normal lowercase text-slate-500">
              {Object.values(completedItems).filter(Boolean).length} / {data.action_items.length} {t('সম্পন্ন', 'done')}
            </span>
          </div>

          <div className="space-y-2">
            {data.action_items.map((item, index) => {
              const isChecked = !!completedItems[index];
              return (
                <div
                  key={index}
                  onClick={() => toggleActionItem(index)}
                  className={`flex items-start gap-3 p-3 rounded-xl border transition-all cursor-pointer select-none ${
                    isChecked
                      ? 'bg-emerald-50/70 border-emerald-200/80 text-emerald-900'
                      : 'bg-white hover:bg-slate-50/80 border-[#E5E1D6] text-slate-800'
                  }`}
                >
                  <div className="mt-0.5 text-emerald-700 flex-shrink-0">
                    {isChecked ? (
                      <CheckSquare className="w-4 h-4 text-emerald-600" />
                    ) : (
                      <Square className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                  <span
                    className={`text-xs sm:text-[13px] leading-snug flex-1 ${
                      isChecked ? 'line-through text-emerald-800/80' : 'text-slate-800 font-medium'
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

      {/* Precaution Alert Pill if present */}
      {data.precaution_alert && (
        <div className="p-3 rounded-xl bg-amber-50/80 border border-amber-200 text-amber-900 text-xs flex items-center gap-2.5">
          <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
          <span className="font-medium leading-snug">{data.precaution_alert}</span>
        </div>
      )}
    </div>
  );
};
