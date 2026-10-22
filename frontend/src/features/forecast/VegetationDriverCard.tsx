import React, { useEffect, useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useMinDelay } from '../../hooks/useMinDelay';
import { Skeleton } from '../../components/common/SkeletonLoader';
import { ErrorState } from '../../components/common/ErrorState';
import { getNDVI } from '../../api/ndvi';
import { getExplainability } from '../../api/explainability';
import type { NDVIResponse } from '../vegetation-health/types';
import type { ExplainabilityResponse } from '../explainability/types';

interface VegetationDriverCardProps {
  region: string;
  crop?: string;
  predictionId: number | null;
  rainfallAdj?: number;
  tempAdj?: number;
}

export const VegetationDriverCard: React.FC<VegetationDriverCardProps> = ({
  region,
  crop = 'Wheat',
  predictionId,
  rainfallAdj = 0,
  tempAdj = 0,
}) => {
  const { t } = useLanguage();

  const [ndviData, setNdviData] = useState<NDVIResponse | null>(null);
  const [rawNdviLoading, setRawNdviLoading] = useState(true);
  const [ndviError, setNdviError] = useState(false);

  const [explainData, setExplainData] = useState<ExplainabilityResponse | null>(null);
  const [rawExplainLoading, setRawExplainLoading] = useState(true);
  const [explainError, setExplainError] = useState(false);

  const ndviLoading = useMinDelay(rawNdviLoading, 250);
  const explainLoading = useMinDelay(rawExplainLoading, 250);

  const fetchNDVI = async () => {
    if (!region) {
      setRawNdviLoading(false);
      return;
    }
    setRawNdviLoading(true);
    setNdviError(false);
    try {
      const res = await getNDVI(region);
      setNdviData(res);
    } catch {
      setNdviError(true);
    } finally {
      setRawNdviLoading(false);
    }
  };

  const fetchExplainability = async () => {
    if (!predictionId) {
      setRawExplainLoading(false);
      return;
    }
    setRawExplainLoading(true);
    setExplainError(false);
    try {
      const res = await getExplainability(predictionId);
      setExplainData(res);
    } catch {
      setExplainError(true);
    } finally {
      setRawExplainLoading(false);
    }
  };

  useEffect(() => {
    void fetchNDVI();
  }, [region]);

  useEffect(() => {
    if (predictionId) {
      void fetchExplainability();
    }
  }, [predictionId]);

  const ndviValue = ndviData?.ndvi_value ?? 0.26;
  const normalizedNdvi = Math.min(1, Math.max(0.12, ndviValue));
  const radius = 23;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - normalizedNdvi * circumference;

  let ringColor = '#D97706'; // Amber for Moderate
  let badgeClass = 'bg-amber-50 border-amber-200 text-amber-800';
  let statusLabel = t('মাঝারি', 'Moderate');
  let statusDesc = t(
    `${crop} ফসলের মাঝারি ক্যানোপি ঘনত্ব।`,
    `Normal canopy density for mid-vegetative ${crop.toLowerCase()}.`
  );

  if (ndviData) {
    const sLower = ndviData.vegetation_status.toLowerCase();
    if (sLower.includes('healthy') || sLower.includes('ভাল') || sLower.includes('উত্তম')) {
      ringColor = '#059669';
      badgeClass = 'bg-emerald-50 border-emerald-200 text-emerald-800';
      statusLabel = t('উত্তম', 'Healthy');
      statusDesc = t(
        `${crop} ফসলের শক্তিশালী ও সুস্থ ক্যানোপি ঘনত্ব।`,
        `Strong canopy vigor for mid-vegetative ${crop.toLowerCase()}.`
      );
    } else if (sLower.includes('poor') || sLower.includes('খারাপ')) {
      ringColor = '#DC2626';
      badgeClass = 'bg-red-50 border-red-200 text-red-700';
      statusLabel = t('দুর্বল', 'Poor');
      statusDesc = t(
        `${crop} ফসলের ক্যানোপি ঘনত্ব গড়ের নিচে।`,
        `Low canopy density detected for ${crop.toLowerCase()}.`
      );
    }
  }

  const driverContributions = explainData?.contributions ?? {
    rainfall: 34.6,
    soil: 16.9,
    temperature: 48.5,
  };

  // Dynamically weight driver attribution when rainfall or temperature sliders are adjusted
  const rawRainWeight = Math.max(
    5,
    Number(driverContributions.rainfall ?? 34.6) * (1 + Math.abs(rainfallAdj) / 60)
  );
  const rawSoilWeight = Math.max(5, Number(driverContributions.soil ?? 16.9));
  const rawTempWeight = Math.max(
    5,
    Number(driverContributions.temperature ?? 48.5) * (1 + Math.abs(tempAdj) / 6)
  );
  const weightSum = rawRainWeight + rawSoilWeight + rawTempWeight;

  const formattedDrivers = [
    {
      key: 'rainfall',
      label: t('বৃষ্টিপাতের প্রভাব', 'Rainfall Impact'),
      val: (rawRainWeight / weightSum) * 100,
      barClass: 'bg-blue-600',
    },
    {
      key: 'soil',
      label: t('মাটি ও এনডিভিআই অবস্থা', 'Soil & NDVI Status'),
      val: (rawSoilWeight / weightSum) * 100,
      barClass: 'bg-[#047857]',
    },
    {
      key: 'temperature',
      label: t('তাপমাত্রার প্রভাব', 'Temperature Stress'),
      val: (rawTempWeight / weightSum) * 100,
      barClass: 'bg-amber-600',
    },
  ];

  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs">
      {/* 1. VEGETATION HEALTH */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-[11px] font-bold uppercase tracking-[0.06em] text-slate-600">
          {t('ভেজিটেশন হেলথ', 'VEGETATION HEALTH')}
        </h3>
        <span className="text-[10px] font-medium text-slate-400">Sentinel-2</span>
      </div>

      {ndviLoading ? (
        <div className="flex items-center gap-3.5 p-3.5 rounded-xl bg-slate-50 border border-slate-100">
          <Skeleton width="56px" height="56px" borderRadius="9999px" className="shrink-0" />
          <div className="space-y-2 flex-1">
            <Skeleton width="70px" height="16px" borderRadius="6px" />
            <Skeleton width="120px" height="12px" borderRadius="4px" />
          </div>
        </div>
      ) : ndviError ? (
        <ErrorState
          message={t('ভেজিটেশন লোড করা যায়নি', 'Failed to load vegetation data')}
          featureName={t('ভেজিটেশন হেলথ', 'Vegetation Health')}
          onRetry={fetchNDVI}
        />
      ) : (
        <div className="p-3.5 rounded-xl bg-slate-50/90 border border-slate-200/70 flex items-center gap-3.5">
          {/* Circular Gauge */}
          <div className="relative w-14 h-14 shrink-0">
            <svg width="56" height="56" viewBox="0 0 56 56">
              <circle cx="28" cy="28" r={radius} fill="none" stroke="#E2E8F0" strokeWidth="5" />
              <circle
                cx="28"
                cy="28"
                r={radius}
                fill="none"
                stroke={ringColor}
                strokeWidth="5"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                transform="rotate(-90 28 28)"
                style={{ transition: 'stroke-dashoffset 0.8s ease' }}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center text-xs font-extrabold text-slate-900">
              {ndviValue.toFixed(2)}
            </div>
          </div>

          {/* Right Info */}
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${badgeClass}`}>
                {statusLabel}
              </span>
              <span className="text-[10px] font-medium text-slate-400">NDVI Index</span>
            </div>
            <p className="text-[11px] text-slate-700 font-medium leading-snug mt-1">
              {statusDesc}
            </p>
          </div>
        </div>
      )}

      {/* 2. DRIVER ATTRIBUTION */}
      <div className="mt-5">
        <h4 className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-3">
          {t('ড্রাইভার অ্যাট্রিবিউশন', 'DRIVER ATTRIBUTION')}
        </h4>

        {explainLoading && predictionId ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-1.5">
                <div className="flex justify-between">
                  <Skeleton width="90px" height="12px" borderRadius="4px" />
                  <Skeleton width="36px" height="12px" borderRadius="4px" />
                </div>
                <Skeleton width="100%" height="6px" borderRadius="9999px" />
              </div>
            ))}
          </div>
        ) : explainError && predictionId ? (
          <ErrorState
            message={t('ড্রাইভার অ্যাট্রিবিউশন লোড করা যায়নি', 'Failed to load driver attribution')}
            featureName={t('ড্রাইভার অ্যাট্রিবিউশন', 'Driver Attribution')}
            onRetry={fetchExplainability}
          />
        ) : (
          <div className="space-y-3">
            {formattedDrivers.map((driver) => (
              <div key={driver.key}>
                <div className="flex items-center justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span>{driver.label}</span>
                  <span className="font-bold text-slate-900">{driver.val.toFixed(1)}%</span>
                </div>
                <div className="h-1.5 w-full rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${driver.barClass} transition-all duration-500`}
                    style={{ width: `${Math.min(100, Math.max(4, driver.val))}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
