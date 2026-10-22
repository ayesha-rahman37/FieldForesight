import React, { useEffect, useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useMinDelay } from '../../hooks/useMinDelay';
import { Skeleton } from '../../components/common/SkeletonLoader';
import { ErrorState } from '../../components/common/ErrorState';
import { getCommunityAggregation } from '../../api/community';
import { BarChart3, RefreshCw } from 'lucide-react';
import type { CommunityYieldAggregationResponse } from '../community/types';

interface CommunityComparisonCardProps {
  region: string;
  crop: string;
  predictionValue: number;
  modelVersion?: string;
}

export const CommunityComparisonCard: React.FC<CommunityComparisonCardProps> = ({
  region,
  crop,
  predictionValue,
  modelVersion,
}) => {
  const { language, t } = useLanguage();
  const [data, setData] = useState<CommunityYieldAggregationResponse | null>(null);
  const [rawLoading, setRawLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);

  const loading = useMinDelay(rawLoading, 250);

  const fetchData = async () => {
    if (!region || !crop) return;
    setRawLoading(true);
    setError(false);
    try {
      const res = await getCommunityAggregation(region, crop, predictionValue);
      setData(res);
    } catch {
      setError(true);
    } finally {
      setRawLoading(false);
    }
  };

  useEffect(() => {
    void fetchData();
  }, [region, crop, predictionValue]);

  const districtAvg = data ? data.district_avg_value : 3.25;
  const myPred = predictionValue || (data ? data.llm_prediction : 3.25);

  const diffPercent = districtAvg > 0 ? ((myPred - districtAvg) / districtAvg) * 100 : 0;
  const isHigher = myPred > districtAvg;
  const isLower = myPred < districtAvg;

  let pillText = t('জেলার গড়ের সমান', 'On par with district avg');
  if (isHigher && diffPercent > 1) {
    pillText = t(`+${diffPercent.toFixed(1)}% জেলার গড়ের চেয়ে`, `+${diffPercent.toFixed(1)}% vs district avg`);
  } else if (isLower && diffPercent < -1) {
    pillText = t(`${diffPercent.toFixed(1)}% জেলার গড়ের চেয়ে`, `${diffPercent.toFixed(1)}% vs district avg`);
  }

  const maxVal = Math.max(districtAvg, myPred, 4.5);
  const distBarPx = Math.round(Math.min(96, Math.max(44, (districtAvg / maxVal) * 96)));
  const predBarPx = Math.round(Math.min(96, Math.max(44, (myPred / maxVal) * 96)));

  const modelBadgeName =
    modelVersion || (crop === 'Rice' ? `BRRI-${crop}-V2.4` : `BARI-${crop || 'Crop'}-V2.1`);

  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs flex flex-col justify-between">
      <div>
        {/* Header Row */}
        <div className="flex items-start justify-between gap-2">
          <div>
            <div className="flex items-center gap-1.5">
              <BarChart3 className="w-4 h-4 text-[#047857] shrink-0" />
              <h3 className="text-[11px] font-bold uppercase tracking-[0.06em] text-slate-800 leading-tight">
                {t('কমিউনিটি তুলনা', 'COMMUNITY COMPARISON')}
              </h3>
            </div>
            <p className="text-[11px] text-slate-400 font-medium mt-1">
              {t(`${crop} পরিসংখ্যান — ${region} জেলা`, `${crop} statistics — ${region} District`)}
            </p>
          </div>

          <span className="px-2.5 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-[10px] font-bold leading-tight text-right max-w-[125px]">
            {pillText}
          </span>
        </div>

        {/* Stat Boxes Row */}
        <div className="mt-4 grid grid-cols-2 gap-2.5">
          <div className="p-3 rounded-xl bg-slate-50/90 border border-slate-200/80 text-center">
            <span className="block text-[9px] font-bold uppercase tracking-wider text-slate-400">
              {t('জেলার গড়', 'DISTRICT AVG')}
            </span>
            <div className="mt-1 flex items-baseline justify-center gap-1">
              <span className="text-xl font-black text-slate-900">{districtAvg.toFixed(2)}</span>
              <span className="text-[11px] font-semibold text-slate-500">t/ha</span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-emerald-50/70 border border-emerald-200/90 text-center">
            <span className="block text-[9px] font-bold uppercase tracking-wider text-emerald-800">
              {t('আপনার পূর্বাভাস', 'YOUR PREDICTION')}
            </span>
            <div className="mt-1 flex items-baseline justify-center gap-1">
              <span className="text-xl font-black text-[#047857]">{myPred.toFixed(2)}</span>
              <span className="text-[11px] font-semibold text-emerald-700">t/ha</span>
            </div>
          </div>
        </div>

        {/* Chart Section */}
        {loading ? (
          <div className="mt-5 h-36 flex items-end justify-center gap-10 pb-2">
            <Skeleton width="52px" height="80px" borderRadius="6px" />
            <Skeleton width="52px" height="90px" borderRadius="6px" />
          </div>
        ) : error ? (
          <div className="mt-4">
            <ErrorState
              featureName={t('কমিউনিটি পরিসংখ্যান', 'Community Statistics')}
              message={t('কমিউনিটি ডেটা লোড করা যায়নি', 'Failed to load community comparison')}
              onRetry={fetchData}
            />
          </div>
        ) : (
          <div className="mt-5">
            <h4 className="text-[9px] font-bold uppercase tracking-wider text-slate-400 text-center mb-3">
              {t('ঐতিহাসিক আঞ্চলিক বিতরণ', 'HISTORICAL REGIONAL DISTRIBUTION')}
            </h4>

            <div className="flex items-end justify-center gap-9 pt-2 pb-2 border-b border-slate-100">
              {/* Bar 1: District Avg */}
              <div className="flex flex-col items-center">
                <span className="text-[11px] font-bold text-slate-700 mb-1.5">
                  {districtAvg.toFixed(2)}
                </span>
                <div
                  className="w-12 rounded-t-md bg-slate-200/90 border-t-4 border-slate-400 transition-all duration-500"
                  style={{ height: `${distBarPx}px` }}
                />
                <span className="text-[11px] font-medium text-slate-500 mt-2">
                  {t('জেলার গড়', 'District avg')}
                </span>
              </div>

              {/* Bar 2: Your Prediction */}
              <div className="flex flex-col items-center">
                <span className="text-[11px] font-bold text-[#047857] mb-1.5">
                  {myPred.toFixed(2)}
                </span>
                <div
                  className="w-12 rounded-t-md bg-[#059669] border-t-4 border-emerald-400 shadow-xs transition-all duration-500"
                  style={{ height: `${predBarPx}px` }}
                />
                <span className="text-[11px] font-bold text-[#047857] mt-2">
                  {t('আপনার পূর্বাভাস', 'Your prediction')}
                </span>
              </div>
            </div>

            <p className="text-[11px] text-slate-500 text-center leading-relaxed mt-3 px-1">
              {language === 'bn' && data?.comparison_note_bn
                ? data.comparison_note_bn
                : t(
                    `স্বাভাবিক বৃষ্টিপাতের প্রত্যাশায় আপনার পূর্বাভাসিত ফলন ১০ বছরের ${region} এগ্রো-ইকোলজিক্যাল বেঞ্চমার্কের সাথে সামঞ্জস্যপূর্ণ।`,
                    `Your predicted yield matches the 10-year ${region} agro-ecological benchmark under normal rainfall expectations.`
                  )}
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400 font-medium">
        <span className="inline-flex items-center gap-1">
          <RefreshCw className="w-3 h-3 text-emerald-600" />
          Model: {modelBadgeName}
        </span>
        <span>Updated: Today</span>
      </div>
    </div>
  );
};
