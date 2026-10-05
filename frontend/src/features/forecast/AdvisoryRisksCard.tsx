import React, { useEffect, useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { AlertTriangle, Lightbulb } from 'lucide-react';
import api from '../../api/client';

interface AdvisoryRisksCardProps {
  crop: string;
  region: string;
  yieldVal: number;
}

interface RiskAlert {
  id: string;
  level: 'high' | 'medium' | 'low';
  title: string;
  description: string;
}

interface AdvisoryResponse {
  advisory_text: string;
  action_items: string[];
}

export const AdvisoryRisksCard: React.FC<AdvisoryRisksCardProps> = ({
  crop,
  region,
  yieldVal,
}) => {
  const { t } = useLanguage();
  const [alerts, setAlerts] = useState<RiskAlert[]>([]);
  const [advisory, setAdvisory] = useState<AdvisoryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);

  const loadData = async () => {
    setLoading(true);
    setError(false);
    try {
      const [alertRes, advRes] = await Promise.allSettled([
        api.get<RiskAlert[]>('/api/risk/alerts', { params: { crop, region } }),
        api.get<AdvisoryResponse>('/api/advisory/generate', { params: { crop, region, yield: yieldVal } }),
      ]);

      if (alertRes.status === 'fulfilled') setAlerts(alertRes.value.data);
      if (advRes.status === 'fulfilled') setAdvisory(advRes.value.data);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [crop, region, yieldVal]);

  const primaryAlert = alerts[0] || {
    title: t('কীটপতঙ্গ সতর্কতা', 'PEST ALERT'),
    description: t(
      'পার্শ্ববর্তী জেলাগুলিতে হালকা মরিচা রোগের ঝুঁকি দেখা গেছে। প্রতিদিন ফসলের পাতা পর্যবেক্ষণ করুন।',
      'Mild rust risk detected in adjacent districts. Monitor crop leaves daily.'
    ),
  };

  const guidanceText = advisory?.advisory_text || t(
    'পরবর্তী ৭২ ঘণ্টার মধ্যে জমিতে সার দেওয়ার সেরা সময় শুরু হচ্ছে।',
    'Top-dressing fertilizer window begins within the next 72 hours.'
  );

  return (
    <div className="bg-[#FBFAF6] border border-[#E5E1D6] rounded-2xl p-6 shadow-[0_1px_2px_rgba(0,0,0,0.04)] flex flex-col justify-between h-full space-y-4">
      <div>
        {/* Header */}
        <div className="flex items-center gap-1.5 mb-4">
          <span className="text-amber-700 text-xs font-bold">⚠</span>
          <h3 className="text-xs font-bold uppercase tracking-[0.06em] text-[#4A4A44]">
            {t('পরামর্শ ও ঝুঁকি', 'ADVISORY & RISKS')}
          </h3>
        </div>

        {loading ? (
          <div className="space-y-3 animate-pulse">
            <div className="h-16 bg-[#F8E9E4] rounded-xl" />
            <div className="h-16 bg-[#E6EFE6] rounded-xl" />
          </div>
        ) : error ? (
          <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs flex items-center justify-between">
            <span className="text-red-700">{t('পরামর্শ লোড করতে ত্রুটি', 'Failed to load advisory')}</span>
            <button
              onClick={loadData}
              className="px-2 py-0.5 bg-red-600 text-white rounded text-[11px] font-semibold"
            >
              {t('পুনরায় চেষ্টা', 'Retry')}
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {/* Pest Alert Card */}
            <div className="bg-[#F8E9E4] border border-[#F3C7BE] border-l-4 border-l-[#C62828] rounded-xl p-3.5 space-y-1">
              <div className="flex items-center gap-1.5 text-[#C62828] text-[11px] font-bold uppercase">
                <AlertTriangle className="w-3.5 h-3.5 text-[#C62828]" />
                <span>{primaryAlert.title}</span>
              </div>
              <p className="text-xs text-[#5C2320] leading-snug">
                {primaryAlert.description}
              </p>
            </div>

            {/* Field Guidance Card */}
            <div className="bg-[#E6EFE6] border border-[#C5DCBF] border-l-4 border-l-[#0B5D45] rounded-xl p-3.5 space-y-1">
              <div className="flex items-center gap-1.5 text-[#0B5D45] text-[11px] font-bold uppercase">
                <Lightbulb className="w-3.5 h-3.5 text-[#0B5D45]" />
                <span>{t('মাঠের নির্দেশিকা', 'FIELD GUIDANCE')}</span>
              </div>
              <p className="text-xs text-[#1E4337] leading-snug">
                {guidanceText}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
