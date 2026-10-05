import React, { useEffect, useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useMinDelay } from '../../hooks/useMinDelay';
import { Skeleton } from '../../components/common/SkeletonLoader';
import { ErrorState } from '../../components/common/ErrorState';
import { getCommunityAggregation } from '../../api/community';
import type { CommunityYieldAggregationResponse } from '../community/types';

interface CommunityComparisonCardProps {
  region: string;
  crop: string;
  predictionValue: number;
}

export const CommunityComparisonCard: React.FC<CommunityComparisonCardProps> = ({
  region,
  crop,
  predictionValue,
}) => {
  const { t } = useLanguage();
  const [data, setData] = useState<CommunityYieldAggregationResponse | null>(null);
  const [rawLoading, setRawLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);

  const loading = useMinDelay(rawLoading, 300);

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
    fetchData();
  }, [region, crop, predictionValue]);

  const districtAvg = data ? data.district_avg_value : 4.25;
  const myPred = data ? data.llm_prediction : predictionValue || 4.25;

  const diffPercent = districtAvg > 0 ? ((myPred - districtAvg) / districtAvg) * 100 : 0;
  const isHigher = myPred > districtAvg;
  const isLower = myPred < districtAvg;

  let pillText = t('জেলার গড়ের সমান', 'On par with district average');
  if (isHigher && diffPercent > 1) {
    pillText = t(`জেলার গড়ের চেয়ে +${diffPercent.toFixed(1)}% বেশি`, `+${diffPercent.toFixed(1)}% vs district avg`);
  } else if (isLower && diffPercent < -1) {
    pillText = t(`জেলার গড়ের চেয়ে ${diffPercent.toFixed(1)}% কম`, `${diffPercent.toFixed(1)}% vs district avg`);
  }

  // Bar height calculation (max scale normalized)
  const maxVal = Math.max(districtAvg, myPred, 5);
  const distBarHeight = Math.min(100, Math.max(30, (districtAvg / maxVal) * 100));
  const predBarHeight = Math.min(100, Math.max(30, (myPred / maxVal) * 100));

  return (
    <div className="bg-[#FBFAF6] border border-[#E5E1D6] rounded-2xl p-6 shadow-[0_1px_2px_rgba(0,0,0,0.04)] w-full">
      {/* Header Row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#E5E1D6]/70">
        <div>
          <div className="flex items-center gap-1.5 mb-1">
            <span className="text-[#0B5D45] text-xs font-bold">📊</span>
            <h3 className="text-xs font-bold uppercase tracking-[0.06em] text-[#4A4A44]">
              {t('কমিউনিটি তুলনা', 'COMMUNITY COMPARISON')}
            </h3>
          </div>
          <p className="text-xs text-slate-500 font-medium">
            {t(`${crop || 'ফসল'} ফলন পরিসংখ্যান - ${region || 'জেলা'}`, `${crop || 'Yield'} statistics - ${region || 'District'}`)}
          </p>

          {/* Status Pill */}
          <div className="mt-2">
            <span className="inline-block bg-[#EAE8DF] text-[#5A5950] border border-[#D8D4C7] text-xs font-semibold px-3 py-1 rounded-full">
              {pillText}
            </span>
          </div>
        </div>

        {/* Right Values Header */}
        <div className="flex items-center gap-6">
          <div className="text-center">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
              {t('জেলার গড়', 'DISTRICT AVG')}
            </span>
            <span className="text-xl sm:text-2xl font-extrabold text-slate-700">
              {districtAvg.toFixed(2)}
            </span>
          </div>

          <div className="text-center">
            <span className="text-[11px] font-bold text-[#0B5D45] uppercase tracking-wider block">
              {t('আপনার পূর্বাভাস', 'YOUR PREDICTION')}
            </span>
            <span className="text-xl sm:text-2xl font-extrabold text-[#0B5D45]">
              {myPred.toFixed(2)}
            </span>
          </div>
        </div>
      </div>

      {/* Chart Section */}
      {loading ? (
        <div className="pt-6 h-44 flex flex-col justify-end items-center">
          <div className="flex items-end gap-16 pb-2 w-full justify-center">
            <div className="flex flex-col items-center gap-2">
              <Skeleton width="48px" height="16px" borderRadius="4px" />
              <Skeleton width="60px" height="90px" borderRadius="12px 12px 0 0" />
            </div>
            <div className="flex flex-col items-center gap-2">
              <Skeleton width="48px" height="16px" borderRadius="4px" />
              <Skeleton width="60px" height="120px" borderRadius="12px 12px 0 0" />
            </div>
          </div>
        </div>
      ) : error ? (
        <div className="pt-6">
          <ErrorState
            featureName={t('কমিউনিটি পরিসংখ্যান', 'Community Statistics')}
            message={t('কমিউনিটি ডেটা লোড করা যায়নি', 'Failed to load community comparison')}
            onRetry={fetchData}
          />
        </div>
      ) : (
        <div className="pt-6">
          {/* Dashed Grid Container */}
          <div className="relative h-44 w-full flex items-end justify-center border-b border-[#E5E1D6]">
            {/* Gridlines */}
            <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-40">
              <div className="border-b border-dashed border-[#D8D4C7] w-full" />
              <div className="border-b border-dashed border-[#D8D4C7] w-full" />
              <div className="border-b border-dashed border-[#D8D4C7] w-full" />
            </div>

            {/* Bars Group */}
            <div className="relative z-10 flex items-end gap-12 sm:gap-20 pb-0">
              {/* Bar 1: District Avg */}
              <div className="flex flex-col items-center gap-1.5">
                <span className="text-xs font-bold text-slate-700 bg-white px-2 py-0.5 rounded border border-[#E5E1D6]">
                  {districtAvg.toFixed(2)}
                </span>
                <div
                  className="w-14 sm:w-16 rounded-t-xl bg-gradient-to-t from-slate-400 to-slate-300 shadow-sm transition-all duration-500"
                  style={{ height: `${distBarHeight}%`, minHeight: '40px' }}
                />
                <span className="text-xs font-semibold text-slate-500 mt-2">
                  {t('জেলার গড়', 'District avg')}
                </span>
              </div>

              {/* Bar 2: Your Prediction */}
              <div className="flex flex-col items-center gap-1.5">
                <span className="text-xs font-extrabold text-[#0B5D45] bg-[#E6EFE6] px-2 py-0.5 rounded border border-[#C5DCBF]">
                  {myPred.toFixed(2)}
                </span>
                <div
                  className="w-14 sm:w-16 rounded-t-xl bg-gradient-to-t from-[#0B5D45] to-[#148363] shadow-md transition-all duration-500"
                  style={{ height: `${predBarHeight}%`, minHeight: '40px' }}
                />
                <span className="text-xs font-bold text-[#0B5D45] mt-2">
                  {t('আপনার পূর্বাভাস', 'Your prediction')}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
