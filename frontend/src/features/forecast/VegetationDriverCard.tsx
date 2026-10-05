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
  predictionId: number | null;
}

export const VegetationDriverCard: React.FC<VegetationDriverCardProps> = ({
  region,
  predictionId,
}) => {
  const { t } = useLanguage();

  // Vegetation Health State
  const [ndviData, setNdviData] = useState<NDVIResponse | null>(null);
  const [rawNdviLoading, setRawNdviLoading] = useState(true);
  const [ndviError, setNdviError] = useState(false);

  // Driver Attribution State
  const [explainData, setExplainData] = useState<ExplainabilityResponse | null>(null);
  const [rawExplainLoading, setRawExplainLoading] = useState(true);
  const [explainError, setExplainError] = useState(false);

  const ndviLoading = useMinDelay(rawNdviLoading, 300);
  const explainLoading = useMinDelay(rawExplainLoading, 300);

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
    fetchNDVI();
  }, [region]);

  useEffect(() => {
    if (predictionId) {
      fetchExplainability();
    }
  }, [predictionId]);

  // Compute ring parameters
  const ndviValue = ndviData?.ndvi_value ?? 0.65;
  const normalizedNdvi = Math.max(0, (ndviValue + 1) / 2);
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - normalizedNdvi * circumference;

  let ringColor = '#E5A93C'; // Moderate amber default
  let statusBg = '#FDF4E3';
  let statusBorder = '#F3DBAF';
  let statusText = '#B47818';
  let statusLabel = t('মাঝারি', 'Moderate');
  let statusDesc = t('মাঝারি ভেজিটেশন', 'Moderate vegetation');

  if (ndviData) {
    const sLower = ndviData.vegetation_status.toLowerCase();
    if (sLower.includes('healthy') || sLower.includes('ভাল') || sLower.includes('উত্তম') || sLower.includes('good')) {
      ringColor = '#0B5D45';
      statusBg = '#E6EFE6';
      statusBorder = '#C5DCBF';
      statusText = '#0B5D45';
      statusLabel = t('উত্তম', 'Healthy');
      statusDesc = t('উত্তম ভেজিটেশন', 'Healthy vegetation');
    } else if (sLower.includes('poor') || sLower.includes('খারাপ')) {
      ringColor = '#C62828';
      statusBg = '#F8E9E4';
      statusBorder = '#F3C7BE';
      statusText = '#C62828';
      statusLabel = t('দুর্বল', 'Poor');
      statusDesc = t('দুর্বল ভেজিটেশন', 'Poor vegetation');
    }
  }

  // Driver Attribution factors mapping
  const driverContributions = explainData?.contributions ?? {
    rainfall: 40,
    soil: 35,
    temperature: 25,
  };

  const formattedDrivers = [
    { key: 'Rainfall', label: t('বৃষ্টিপাত', 'RAINFALL'), val: Number(driverContributions.rainfall || driverContributions.Rainfall || 40) },
    { key: 'Soil', label: t('মাটির গুণমান ও এনডিভিআই', 'SOIL & NDVI'), val: Number(driverContributions.soil || driverContributions.Soil || 35) },
    { key: 'Temperature', label: t('তাপমাত্রা', 'TEMPERATURE'), val: Number(driverContributions.temperature || driverContributions.Temperature || 25) },
  ];

  return (
    <div className="bg-[#FBFAF6] border border-[#E5E1D6] rounded-2xl p-6 shadow-[0_1px_2px_rgba(0,0,0,0.04)] flex flex-col justify-between h-full space-y-5">
      {/* 1. VEGETATION HEALTH SECTION */}
      <div>
        <h3 className="text-xs font-bold uppercase tracking-[0.06em] text-[#4A4A44] mb-3">
          {t('ভেজিটেশন হেলথ', 'VEGETATION HEALTH')}
        </h3>

        {ndviLoading ? (
          <div className="flex items-center gap-4 py-1">
            <Skeleton width="72px" height="72px" borderRadius="9999px" className="shrink-0" />
            <div className="space-y-2 flex-1">
              <Skeleton width="60px" height="18px" borderRadius="12px" />
              <Skeleton width="110px" height="14px" borderRadius="4px" />
              <Skeleton width="90px" height="12px" borderRadius="4px" />
            </div>
          </div>
        ) : ndviError ? (
          <ErrorState
            message={t('ভেজিটেশন লোড করা যায়নি', 'Failed to load vegetation data')}
            featureName={t('ভেজিটেশন হেলথ', 'Vegetation Health')}
            onRetry={fetchNDVI}
          />
        ) : (
          <div className="flex items-center gap-4">
            {/* Ring */}
            <div className="relative w-[72px] h-[72px] shrink-0">
              <svg width="72" height="72" viewBox="0 0 72 72">
                <circle cx="36" cy="36" r={radius} fill="none" stroke="#E5E1D6" strokeWidth="6" />
                <circle
                  cx="36" cy="36" r={radius}
                  fill="none" stroke={ringColor} strokeWidth="6"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  strokeLinecap="round"
                  transform="rotate(-90 36 36)"
                  style={{ transition: 'stroke-dashoffset 0.8s ease' }}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center text-sm font-bold text-[#1F1F1B]">
                {ndviValue.toFixed(2)}
              </div>
            </div>

            {/* Status Pills */}
            <div className="space-y-0.5">
              <span
                className="inline-block text-[11px] font-bold px-2.5 py-0.5 rounded-full border mb-1"
                style={{ backgroundColor: statusBg, borderColor: statusBorder, color: statusText }}
              >
                {statusLabel}
              </span>
              <div className="text-xs font-semibold text-[#1F1F1B]">{statusDesc}</div>
              <div className="text-[11px] text-slate-400 font-medium">NDVI · Sentinel-2</div>
            </div>
          </div>
        )}
      </div>

      <hr className="border-[#E5E1D6]/70 my-2" />

      {/* 2. DRIVER ATTRIBUTION SECTION */}
      <div>
        <h3 className="text-xs font-bold uppercase tracking-[0.06em] text-[#4A4A44] mb-3">
          {t('ড্রাইভার অ্যাট্রিবিউশন', 'DRIVER ATTRIBUTION')}
        </h3>

        {explainLoading && predictionId ? (
          <div className="space-y-3 py-1">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-1.5">
                <div className="flex justify-between">
                  <Skeleton width="80px" height="12px" borderRadius="4px" />
                  <Skeleton width="36px" height="12px" borderRadius="4px" />
                </div>
                <Skeleton width="100%" height="8px" borderRadius="9999px" />
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
          <div className="space-y-2.5">
            {formattedDrivers.map((driver) => (
              <div key={driver.key}>
                <div className="flex items-center justify-between text-[11px] font-bold text-[#4A4A44] uppercase mb-1">
                  <span>{driver.label}</span>
                  <span>{driver.val.toFixed(1)}%</span>
                </div>
                <div className="h-2 w-full rounded-full bg-[#D9DDD0] overflow-hidden">
                  <div
                    className="h-full rounded-full bg-[#0B5D45] transition-all duration-500"
                    style={{ width: `${Math.min(100, Math.max(0, driver.val))}%` }}
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
