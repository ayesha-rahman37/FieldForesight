import React from 'react';
import { useLanguage } from '../../context/LanguageContext';

interface ProjectedYieldCardProps {
  predictedYield: number;
  lowerBound: number;
  upperBound: number;
  region: string;
}

export const ProjectedYieldCard: React.FC<ProjectedYieldCardProps> = ({
  predictedYield,
  lowerBound,
  upperBound,
  region,
}) => {
  const { t } = useLanguage();

  const formattedRegion = region ? region.toUpperCase() : 'REGIONAL';

  // Calculate percentage position of predictedYield between lowerBound and upperBound for the range slider
  const rangeSpan = upperBound - lowerBound;
  const thumbPercent = rangeSpan > 0 ? Math.min(100, Math.max(0, ((predictedYield - lowerBound) / rangeSpan) * 100)) : 50;

  return (
    <div className="bg-[#FBFAF6] border border-[#E5E1D6] rounded-2xl p-6 shadow-[0_1px_2px_rgba(0,0,0,0.04)] flex flex-col justify-between h-full">
      {/* Header */}
      <div>
        <h3 className="text-xs font-bold uppercase tracking-[0.06em] text-[#4A4A44]">
          {t(`পূর্বাভাসকৃত ফলন · ${region} জেলা`, `PROJECTED YIELD · ${formattedRegion} DISTRICT`)}
        </h3>

        {/* Hero Number Display */}
        <div className="mt-6 flex items-baseline gap-2">
          <span className="text-[88px] sm:text-[108px] lg:text-[116px] font-extrabold text-[#1F1F1B] leading-none tracking-[-0.03em]">
            {predictedYield.toFixed(2)}
          </span>
          <span className="text-xl sm:text-2xl font-normal text-slate-500 pb-2">
            t/ha
          </span>
        </div>
      </div>

      {/* Confidence Range Section */}
      <div className="mt-8 pt-4">
        <div className="flex items-center justify-between text-xs font-bold uppercase tracking-[0.06em]">
          <span className="text-[#4A4A44]">{t('আত্মবিশ্বাসের পরিসীমা', 'CONFIDENCE RANGE')}</span>
          <span className="text-[#0B5D45]">{t('উচ্চ নির্ভরযোগ্যতা', 'HIGH RELIABILITY')}</span>
        </div>

        {/* Custom Range Track Bar */}
        <div className="relative my-3">
          <div className="h-2.5 w-full bg-[#E5E1D6] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-[#80B9A5] via-[#4A8B7C] to-[#0B5D45]"
              style={{ width: '100%' }}
            />
          </div>
          {/* Thumb marker */}
          <div
            className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-5 h-5 rounded-full bg-white border-2 border-[#0B5D45] shadow-md transition-all duration-300"
            style={{ left: `${thumbPercent}%` }}
          />
        </div>

        {/* Min & Max Labels */}
        <div className="flex items-center justify-between text-xs font-medium text-slate-500">
          <span>{lowerBound.toFixed(2)} {t('সর্বনিম্ন', 'minimum')}</span>
          <span>{upperBound.toFixed(2)} {t('সর্বোচ্চ', 'maximum')}</span>
        </div>
      </div>
    </div>
  );
};
