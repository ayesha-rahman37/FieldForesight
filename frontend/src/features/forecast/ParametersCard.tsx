import React, { useEffect, useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { Play, ShieldCheck, Clock } from 'lucide-react';
import api from '../../api/client';

export interface VarietyItem {
  id: number;
  crop: string;
  variety_code: string;
  name_en: string;
  name_bn: string;
  variety_type: string;
  yield_coefficient: number;
  potential_yield_min?: number;
  potential_yield_max?: number;
  maturity_days?: number;
  season?: string;
  stress_tolerance?: string;
  description_bn?: string;
  description_en?: string;
  is_recommended: boolean;
}

interface ParametersCardProps {
  crops: string[];
  regions: string[];
  selectedCrop: string;
  selectedRegion: string;
  selectedVariety: string;
  onCropChange: (crop: string) => void;
  onRegionChange: (region: string) => void;
  onVarietyChange: (variety: string) => void;
  onRunForecast: () => void;
  loading: boolean;
}

const ChevronDown = () => (
  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3.5 text-slate-400">
    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
      <path d="M19 9l-7 7-7-7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  </div>
);

export const ParametersCard: React.FC<ParametersCardProps> = ({
  crops,
  regions,
  selectedCrop,
  selectedRegion,
  selectedVariety,
  onCropChange,
  onRegionChange,
  onVarietyChange,
  onRunForecast,
  loading,
}) => {
  const { t } = useLanguage();
  const [varieties, setVarieties] = useState<VarietyItem[]>([]);
  const [loadingVarieties, setLoadingVarieties] = useState<boolean>(false);

  // Fetch varieties dynamically whenever selectedCrop changes
  useEffect(() => {
    let active = true;
    if (!selectedCrop) {
      setVarieties([]);
      return;
    }

    setLoadingVarieties(true);
    api
      .get<VarietyItem[]>('/api/varieties', { params: { crop: selectedCrop } })
      .then((res) => {
        if (active) {
          setVarieties(res.data);
          // If current variety is not in the list, set default
          if (res.data.length > 0) {
            const hasMatch = res.data.some(
              (v) => v.variety_code === selectedVariety || v.name_en === selectedVariety
            );
            if (!hasMatch) {
              const defaultVariety = res.data[0].variety_code;
              onVarietyChange(defaultVariety);
            }
          }
        }
      })
      .catch((err) => {
        console.warn('Failed to fetch dynamic varieties, fallback to defaults:', err);
      })
      .finally(() => {
        if (active) setLoadingVarieties(false);
      });

    return () => {
      active = false;
    };
  }, [selectedCrop]);

  const activeVarietyInfo = varieties.find(
    (v) => v.variety_code === selectedVariety || v.name_en === selectedVariety
  );

  return (
    <div className="bg-[#FBFAF6] border border-[#E5E1D6] rounded-2xl p-6 shadow-[0_1px_2px_rgba(0,0,0,0.04)] flex flex-col justify-between h-full">
      <div>
        {/* Card Header */}
        <div className="flex items-center gap-1.5 mb-5">
          <span className="text-slate-500 font-bold text-sm">–</span>
          <h3 className="text-xs font-bold uppercase tracking-[0.06em] text-[#4A4A44]">
            {t('প্যারামিটারস ও জাত নির্বাচন', 'PARAMETERS & VARIETY SELECTION')}
          </h3>
        </div>

        {/* Input Controls */}
        <div className="space-y-4">
          {/* Crop Selection */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[#4A4A44] mb-1.5">
              {t('কৃষি ফসল', 'AGRICULTURAL CROP')}
            </label>
            <div className="relative">
              <select
                className="w-full h-[44px] pl-3.5 pr-10 rounded-xl border border-[#E5E1D6] bg-[#F1EEE6] text-[#1F1F1B] text-sm font-semibold focus:ring-2 focus:ring-[#0B5D45] focus:border-[#0B5D45] transition cursor-pointer appearance-none"
                value={selectedCrop}
                onChange={(e) => onCropChange(e.target.value)}
              >
                <option value="">{t('ফসল নির্বাচন করুন', 'Select Crop')}</option>
                {crops.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
              <ChevronDown />
            </div>
          </div>

          {/* Division & District */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[#4A4A44] mb-1.5">
              {t('বিভাগ ও জেলা', 'DIVISION & DISTRICT')}
            </label>
            <div className="relative">
              <select
                className="w-full h-[44px] pl-3.5 pr-10 rounded-xl border border-[#E5E1D6] bg-[#F1EEE6] text-[#1F1F1B] text-sm font-semibold focus:ring-2 focus:ring-[#0B5D45] focus:border-[#0B5D45] transition cursor-pointer appearance-none"
                value={selectedRegion}
                onChange={(e) => onRegionChange(e.target.value)}
              >
                <option value="">{t('জেলা নির্বাচন করুন', 'Select District')}</option>
                {regions.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
              <ChevronDown />
            </div>
          </div>

          {/* Seed Variety Selector UI */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-[11px] font-bold uppercase tracking-wider text-[#4A4A44]">
                {t('অনুমোদিত বীজের জাত (BRRI / BARI)', 'CERTIFIED SEED VARIETY')}
              </label>
              {loadingVarieties && (
                <span className="text-[10px] text-emerald-700 animate-pulse font-medium">
                  {t('লোড হচ্ছে...', 'loading...')}
                </span>
              )}
            </div>
            <div className="relative">
              <select
                className="w-full h-[44px] pl-3.5 pr-10 rounded-xl border border-[#E5E1D6] bg-[#F1EEE6] text-[#1F1F1B] text-sm font-semibold focus:ring-2 focus:ring-[#0B5D45] focus:border-[#0B5D45] transition cursor-pointer appearance-none"
                value={selectedVariety}
                onChange={(e) => onVarietyChange(e.target.value)}
              >
                {varieties.length > 0 ? (
                  varieties.map((v) => (
                    <option key={v.variety_code} value={v.variety_code}>
                      {t(v.name_bn, v.name_en)} ({v.variety_type})
                    </option>
                  ))
                ) : (
                  <>
                    <option value="HYV">{t('উচ্চ ফলনশীল (HYV Standard)', 'High Yielding (HYV Standard)')}</option>
                    <option value="Local">{t('স্থানীয় দেশি জাত (Local Cultivar)', 'Local Native Cultivar')}</option>
                  </>
                )}
              </select>
              <ChevronDown />
            </div>

            {/* Selected Variety Trait Preview Badge */}
            {activeVarietyInfo && (
              <div className="mt-2 p-2 rounded-lg bg-[#EAE7DC]/60 border border-[#DDD8CA] text-[11px] text-slate-700 space-y-1">
                <div className="flex items-center justify-between gap-1 flex-wrap">
                  <span className="font-bold text-[#004741]">
                    {t(activeVarietyInfo.name_bn, activeVarietyInfo.name_en)}
                  </span>
                  <span className="px-1.5 py-0.2 rounded bg-white text-[10px] font-semibold text-emerald-800 border border-emerald-200">
                    {activeVarietyInfo.variety_type}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-[10px] text-slate-600 flex-wrap">
                  {activeVarietyInfo.maturity_days && (
                    <span className="inline-flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-500" />
                      {t(`জীবনকাল: ${activeVarietyInfo.maturity_days} দিন`, `Maturity: ${activeVarietyInfo.maturity_days}d`)}
                    </span>
                  )}
                  {activeVarietyInfo.stress_tolerance && activeVarietyInfo.stress_tolerance !== 'Standard' && (
                    <span className="inline-flex items-center gap-0.5 font-semibold text-blue-700">
                      <ShieldCheck className="w-3 h-3 text-blue-600" />
                      {activeVarietyInfo.stress_tolerance}
                    </span>
                  )}
                  {activeVarietyInfo.yield_coefficient && (
                    <span className="text-emerald-700 font-mono">
                      ×{activeVarietyInfo.yield_coefficient.toFixed(2)} coeff
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Button & Telemetry Note */}
      <div className="mt-6 pt-2">
        <button
          type="button"
          disabled={!selectedCrop || !selectedRegion || loading}
          onClick={onRunForecast}
          className="w-full h-[48px] bg-[#0B5D45] hover:bg-[#084936] disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl text-[13px] font-semibold tracking-wider uppercase flex items-center justify-center gap-2 shadow-md hover:shadow-lg transition-all active:scale-[0.99]"
        >
          <Play className="w-4 h-4 fill-white text-white" />
          <span>{loading ? t('চলছে...', 'RUNNING...') : t('পূর্বাভাস ও ঝুঁকি বিশ্লেষণ', 'RUN FORECAST & ADVISORY')}</span>
        </button>

        {/* Telemetry Chips under button */}
        <div className="mt-3 text-[10px] text-slate-500 font-medium text-center flex flex-wrap justify-center gap-1.5">
          <span className="bg-[#F1EEE6] border border-[#E5E1D6] px-2 py-0.5 rounded-full">Groq Llama 3.3</span>
          <span className="bg-[#F1EEE6] border border-[#E5E1D6] px-2 py-0.5 rounded-full">BRRI / BARI Certified</span>
          <span className="bg-[#E6EFE6] text-[#0B5D45] border border-[#C5DCBF] px-2 py-0.5 rounded-full font-semibold">
            MODIS NDVI & Risk Alert
          </span>
        </div>
      </div>
    </div>
  );
};
