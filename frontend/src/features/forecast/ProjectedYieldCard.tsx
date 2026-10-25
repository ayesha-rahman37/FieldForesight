import React from 'react';
import { useLanguage } from '../../context/LanguageContext';

interface ProjectedYieldCardProps {
  predictedYield: number;
  lowerBound: number;
  upperBound: number;
  region: string;
  baselineDelta?: number;
}

export const ProjectedYieldCard: React.FC<ProjectedYieldCardProps> = ({
  predictedYield,
  lowerBound,
  upperBound,
  region,
  baselineDelta = 0,
}) => {
  const { t } = useLanguage();

  const formattedRegion = region ? region.toUpperCase() : 'DHAKA';

  const rangeSpan = upperBound - lowerBound;
  const thumbPercent =
    rangeSpan > 0
      ? Math.min(92, Math.max(8, ((predictedYield - lowerBound) / rangeSpan) * 100))
      : 50;

  const deltaLabel =
    Math.abs(baselineDelta) < 0.005
      ? '+0.00 baseline'
      : `${baselineDelta > 0 ? '+' : ''}${baselineDelta.toFixed(2)} simulated`;

  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs">
      {/* Header Row */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <h3 className="text-[11px] font-bold uppercase tracking-[0.06em] text-slate-600">
          {t(`পূর্বাভাসকৃত ফলন · ${region} জেলা`, `PROJECTED YIELD · ${formattedRegion} DISTRICT`)}
        </h3>
        <span className="px-2.5 py-0.5 rounded-md bg-emerald-50 border border-emerald-200 text-emerald-700 text-[10px] font-bold uppercase tracking-wider">
          {t('উচ্চ নির্ভরযোগ্যতা', 'HIGH RELIABILITY')}
        </span>
      </div>

      {/* Hero Number Display */}
      <div className="mt-3 flex items-baseline gap-2.5 flex-wrap">
        <span className="text-5xl sm:text-[52px] font-black text-slate-900 leading-none tracking-tight">
          {predictedYield.toFixed(2)}
        </span>
        <span className="text-lg font-bold text-slate-500">t/ha</span>
        <span
          className={`px-2 py-0.5 rounded-md text-xs font-bold border ${
            baselineDelta < -0.005
              ? 'bg-amber-50 border-amber-200 text-amber-800'
              : 'bg-emerald-50 border-emerald-200 text-emerald-700'
          }`}
        >
          {deltaLabel}
        </span>
      </div>

      {/* Subtitle */}
      <p className="text-xs text-slate-500 mt-2.5 leading-relaxed">
        {t(
          'অনুমোদিত বীজের ক্ষমতা এবং বর্তমান জলবায়ু সূচকের ভিত্তিতে প্রাক্কলিত উৎপাদন।',
          'Estimated output based on certified seed vigor & current climate anomaly index.'
        )}
      </p>

      {/* Confidence Range Section */}
      <div className="mt-6 pt-2">
        <div className="flex items-center justify-between text-xs mb-2">
          <span className="font-bold text-slate-700">
            {t('আত্মবিশ্বাসের পরিসীমা', 'Confidence Range')}
          </span>
          <span className="text-slate-500">
            <span>{t('প্রত্যাশিত মধ্যমান:', 'Median Expected:')} </span>
            <strong className="font-bold text-slate-900">{predictedYield.toFixed(2)} t/ha</strong>
          </span>
        </div>

        {/* Custom Range Track Bar */}
        <div className="relative my-2.5 h-2.5 w-full bg-slate-100 rounded-full flex items-center justify-center">
          <div className="w-3/5 h-2 rounded-full bg-emerald-300/80" />
          <div
            className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-3.5 h-3.5 rounded-full bg-[#047857] border-2 border-white shadow-sm transition-all duration-300"
            style={{ left: `${thumbPercent}%` }}
          />
        </div>

        {/* Min, Mean & Max Labels */}
        <div className="flex items-center justify-between text-[11px] font-medium text-slate-400 mt-1.5">
          <span>{lowerBound.toFixed(2)} min</span>
          <span className="text-[10px] font-extrabold uppercase tracking-wider text-emerald-700">
            AGRO-ECOLOGICAL MEAN
          </span>
          <span>{upperBound.toFixed(2)} max</span>
        </div>
      </div>
    </div>
  );
};
